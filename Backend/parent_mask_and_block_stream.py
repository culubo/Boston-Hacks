#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, json, time, signal, argparse, subprocess, pickle, threading
from typing import List, Dict, Any, Optional, Tuple
import importlib.util

# ----------------- Model utils -----------------

def load_model(pkl_path: str):
    with open(pkl_path, "rb") as f:
        return pickle.load(f)

def ensure_features_module(features_path: str):
    """
    Load a standalone features.py (or point directly to the file) as module 'features'
    so unpickling can import it. Safe to call multiple times.
    """
    # If a directory is passed, append features.py
    if os.path.isdir(features_path):
        candidate = os.path.join(features_path, "features.py")
    else:
        candidate = features_path  # allow full file path

    if not os.path.exists(candidate):
        raise FileNotFoundError(f"features.py not found at: {candidate}")

    # Already loaded?
    if "features" in sys.modules:
        return

    spec = importlib.util.spec_from_file_location("features", candidate)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to create spec for features from {candidate}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.modules["features"] = mod  # register under the expected name

def predict_sensitive_map(model, words: List[str], prob_threshold: float = 0.5) -> List[bool]:
    if not words:
        return []
    uniq, order = {}, []
    for w in words:
        if w not in uniq:
            uniq[w] = None
            order.append(w)
    results: Dict[str,bool] = {}
    used_proba = False
    if hasattr(model, "predict_proba"):
        try:
            probs = model.predict_proba(order)
            pos_col = 1 if probs.shape[1] == 2 else int(probs.shape[1]-1)
            for w, row in zip(order, probs):
                results[w] = float(row[pos_col]) >= prob_threshold
            used_proba = True
        except Exception:
            pass
    if not used_proba:
        if hasattr(model, "predict"):
            try:
                preds = model.predict(order)
                for w, y in zip(order, preds):
                    results[w] = str(y).strip().lower() in {"1","true","yes","positive","pos","sensitive"}
            except Exception:
                for w in order: results[w] = False
        else:
            for w in order: results[w] = False
    return [results[w] for w in words]

def max_xy_from_items(items: List[Dict[str,Any]]) -> Tuple[int,int]:
    mx = my = 0.0
    for it in items:
        try:
            x2 = float(it["bottom_right"][0]); y2 = float(it["bottom_right"][1])
        except Exception:
            continue
        if x2 > mx: mx = x2
        if y2 > my: my = y2
    return int(mx), int(my)

# ----------------- OBS child (your script) -----------------

class OBSStdinProcess:
    def __init__(self, script_path: str, host: str, port: int, password: str,
                 scene: Optional[str], canvas_w: int, canvas_h: int,
                 overlay_prefix="MASK", max_boxes=50, fps=90, extra_args=None):
        self.script_path = script_path
        self.host = host; self.port = port; self.password = password
        self.scene = scene; self.canvas_w = canvas_w; self.canvas_h = canvas_h
        self.overlay_prefix = overlay_prefix; self.max_boxes = max_boxes; self.fps = fps
        self.extra_args = extra_args or []
        self.proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()

    def start(self):
        args = [sys.executable, self.script_path,
                "--mode","stdin",
                "--obs-host", self.host, "--obs-port", str(self.port),
                "--obs-password", self.password,
                "--overlay-prefix", self.overlay_prefix,
                "--max-boxes", str(self.max_boxes),
                "--canvas-w", str(self.canvas_w), "--canvas-h", str(self.canvas_h),
                "--fps", str(self.fps)]
        if self.scene: args += ["--scene", self.scene]
        args += self.extra_args
        self.proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1)
        threading.Thread(target=self._drain_stderr, daemon=True).start()

    def _drain_stderr(self):
        if not self.proc or not self.proc.stderr: return
        for line in self.proc.stderr:
            sys.stderr.write(f"[obs-mask] {line}"); sys.stderr.flush()

    def send_boxes(self, boxes):
        if not self.proc or not self.proc.stdin: return
        payload = [{"x1":float(x1),"y1":float(y1),"x2":float(x2),"y2":float(y2)} for (x1,y1,x2,y2) in boxes]
        line = json.dumps(payload, separators=(",",":")) + "\n"
        with self._lock:
            try:
                self.proc.stdin.write(line); self.proc.stdin.flush()
            except BrokenPipeError:
                pass

    def stop(self):
        if not self.proc: return
        try:
            self.proc.terminate()
            try: self.proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired: self.proc.kill()
        except Exception:
            pass

# ----------------- fastscreenocr server client -----------------

class FastScreenOCRServer:
    def __init__(self, cmd_path: str, langs_env: Optional[str] = None):
        self.cmd_path = cmd_path
        self.langs_env = langs_env
        self.proc: Optional[subprocess.Popen] = None
        self._lock = threading.Lock()

    def start(self):
        env = os.environ.copy()
        if self.langs_env:
            env["FASTSCREENOCR_LANGS"] = self.langs_env
        self.proc = subprocess.Popen([self.cmd_path, "--server"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1, env=env)
        threading.Thread(target=self._drain_stderr, daemon=True).start()

    def _drain_stderr(self):
        if not self.proc or not self.proc.stderr: return
        for line in self.proc.stderr:
            sys.stderr.write(f"[ocr] {line}"); sys.stderr.flush()

    def capture_once(self, timeout: float = 2.5) -> Optional[List[Dict[str,Any]]]:
        if not self.proc or not self.proc.stdin or not self.proc.stdout:
            return None
        with self._lock:
            try:
                self.proc.stdin.write("CAPTURE\n"); self.proc.stdin.flush()
            except BrokenPipeError:
                return None
        # Read one JSON line (compact)
        start = time.perf_counter()
        buff = ""
        while True:
            if not self.proc: return None
            ch = self.proc.stdout.read(1)
            if ch == "" and self.proc.poll() is not None:
                return None  # process died
            if ch == "\n":
                break
            buff += ch
            if time.perf_counter() - start > timeout:
                return None
        try:
            return json.loads(buff)  # Expect list of items
        except Exception:
            return None

    def stop(self):
        if not self.proc: return
        try:
            if self.proc.stdin:
                try:
                    self.proc.stdin.write("quit\n"); self.proc.stdin.flush()
                except Exception:
                    pass
            self.proc.terminate()
            try: self.proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired: self.proc.kill()
        except Exception:
            pass

# ----------------- Orchestration -----------------

def run_parent_stream(
    fastscreenocr_path: str,
    model_path: str,
    obs_script_path: str,
    obs_host="localhost",
    obs_port=4455,
    obs_password="V7s23mQOACBp6Yvq",
    scene: Optional[str]=None,
    canvas_w: int=2560,
    canvas_h: int=1440,
    display_w: Optional[int]=None,
    display_h: Optional[int]=None,
    fps: int=5,
    prob_threshold: float=0.5,
    max_boxes: int=50,
    overlay_prefix="MASK",
    langs_env: Optional[str]="en-US",
):

    model = load_model(model_path)

    obs_proc = OBSStdinProcess(obs_script_path, obs_host, obs_port, obs_password,
                               scene, canvas_w, canvas_h,
                               overlay_prefix=overlay_prefix,
                               max_boxes=max_boxes, fps=max(1,fps))
    obs_proc.start()

    ocr = FastScreenOCRServer(fastscreenocr_path, langs_env=langs_env)
    ocr.start()

    def cleanup(*_):
        ocr.stop(); obs_proc.stop(); sys.exit(0)
    try:
        signal.signal(signal.SIGINT, cleanup)
    except Exception:
        pass

    period = 1.0 / max(1,fps)
    last_wh: Optional[Tuple[int,int]] = (display_w, display_h) if (display_w and display_h) else None

    while True:
        t0 = time.perf_counter()
        items = ocr.capture_once()
        if items is None:
            sys.stderr.write("[parent] OCR server returned no data; attempting to continue...\n")
            boxes_to_block = []
        else:
            if not last_wh:
                est = max_xy_from_items(items)
                if est[0] > 0 and est[1] > 0:
                    last_wh = est
            cap_w = display_w or (last_wh[0] if last_wh else canvas_w)
            cap_h = display_h or (last_wh[1] if last_wh else canvas_h)

            sx = float(canvas_w)/float(cap_w)
            sy = float(canvas_h)/float(cap_h)

            words, raw_boxes = [], []
            for it in items:
                w = it.get("word"); tl = it.get("top_left"); br = it.get("bottom_right")
                if not w or not isinstance(tl, list) or not isinstance(br, list): continue
                words.append(w)
                raw_boxes.append((float(tl[0]), float(tl[1]), float(br[0]), float(br[1])))

            flags = predict_sensitive_map(model, words, prob_threshold=prob_threshold)
            boxes_to_block = []
            for flag, (x1,y1,x2,y2) in zip(flags, raw_boxes):
                if flag:
                    boxes_to_block.append((x1*sx, y1*sy, x2*sx, y2*sy))
            if len(boxes_to_block) > max_boxes:
                boxes_to_block = boxes_to_block[:max_boxes]

        obs_proc.send_boxes(boxes_to_block)

        dt = time.perf_counter() - t0
        sleep_left = period - dt
        if sleep_left > 0:
            time.sleep(sleep_left)

def main():
    ap = argparse.ArgumentParser(description="Parent: warm OCR server → PKL classifier → OBS masks")
    ap.add_argument("--fastscreenocr", default="./fastscreenocr", help="Path to OCR binary")
    ap.add_argument("--model-pkl", default="/Users/mwatk/Documents/Boston-Hacks/Backend/ML_Model/final_model.pkl", help="Path to trained .pkl model (trusted)")
    ap.add_argument("--obs-script", required=True, help="Path to OBS masker script")
    ap.add_argument("--obs-host", default="localhost")
    ap.add_argument("--obs-port", type=int, default=4455)
    ap.add_argument("--obs-password", default="V7s23mQOACBp6Yvq")
    ap.add_argument("--scene", default=None)
    ap.add_argument("--canvas-w", type=int, default=2560)
    ap.add_argument("--canvas-h", type=int, default=1440)
    ap.add_argument("--display-w", type=int, default=None)
    ap.add_argument("--display-h", type=int, default=None)
    ap.add_argument("--fps", type=int, default=5)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--max-boxes", type=int, default=50)
    ap.add_argument("--overlay-prefix", default="MASK")
    ap.add_argument("--langs", default="en-US", help="FASTSCREENOCR_LANGS value")
    ap.add_argument("--features-path",default="/Users/mwatk/Documents/Boston-Hacks/Backend/ML_Model",help="Directory or file path to features.py")
    args = ap.parse_args()

    ensure_features_module(args.features_path)
    run_parent_stream(
        fastscreenocr_path=args.fastscreenocr,
        model_path=args.model_pkl,
        obs_script_path=args.obs_script,
        obs_host=args.obs_host,
        obs_port=args.obs_port,
        obs_password=args.obs_password,
        scene=args.scene,
        canvas_w=args.canvas_w,
        canvas_h=args.canvas_h,
        display_w=args.display_w,
        display_h=args.display_h,
        fps=args.fps,
        prob_threshold=args.threshold,
        max_boxes=args.max_boxes,
        overlay_prefix=args.overlay_prefix,
        langs_env=args.langs,
    )

if __name__ == "__main__":
    main()

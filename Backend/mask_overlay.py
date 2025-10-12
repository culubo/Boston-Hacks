#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, json, time, argparse, threading, random, signal
from dataclasses import dataclass
from typing import List, Optional

# pip install obsws-python pynput
import obsws_python as obs
from obsws_python.error import OBSSDKRequestError
from pynput import keyboard

@dataclass
class Box:
    x1: float
    y1: float
    x2: float
    y2: float

    def clamp(self, w: int, h: int):
        self.x1 = max(0, min(self.x1, w))
        self.x2 = max(0, min(self.x2, w))
        self.y1 = max(0, min(self.y1, h))
        self.y2 = max(0, min(self.y2, h))

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

class OBSMasks:
    def __init__(self, cl: obs.ReqClient, scene: Optional[str], overlay_prefix: str,
                 canvas_w: int, canvas_h: int, max_masks: int = 50):
        self.cl = cl
        self.scene = scene or self._get_program_scene()
        self.prefix = overlay_prefix
        self.canvas_w = canvas_w
        self.canvas_h = canvas_h
        self.max_masks = max_masks
        self.mask_names: List[str] = []
        self.mask_ids: List[int] = []
        self.panic_name = f"{self.prefix}_PANIC"
        self.panic_id: Optional[int] = None

        self._ensure_pool(self.max_masks)
        self._ensure_panic()

    def _get_program_scene(self) -> str:
        resp = self.cl.get_current_program_scene()
        # obsws-python maps fields to snake_case
        return resp.current_program_scene_name

    def _get_scene_items(self):
        # Always return a fresh list of scene items (SDK may return objects or dicts)
        return self.cl.get_scene_item_list(self.scene).scene_items

    def _list_items_map(self):
        """Return {name: sceneItemId} for current scene."""
        return {
            self._item_name(it): self._item_id(it)
            for it in self._get_scene_items()
            if self._item_name(it) is not None and self._item_id(it) is not None
        }


    def _move_to_top(self, scene_item_id: int):
        # Find the current highest index and place this item above it,
        # but never exceed OBS's maximum index (8191).
        items = self._get_scene_items()
        max_idx = -1
        for it in items:
            idx = self._item_index(it)
            if isinstance(idx, int):
                max_idx = max(max_idx, idx)
        new_index = min(8191, max_idx + 1)
        self.cl.set_scene_item_index(self.scene, scene_item_id, new_index)

    def _item_name(self, it):
        if isinstance(it, dict):
            return it.get("sourceName") or it.get("inputName") or it.get("source_name")
        return getattr(it, "source_name", None)

    def _item_id(self, it):
        if isinstance(it, dict):
            return it.get("sceneItemId") or it.get("scene_item_id")
        return getattr(it, "scene_item_id", None)
        
    def _item_index(self, it):
        if isinstance(it, dict):
            return it.get("sceneItemIndex") or it.get("scene_item_index")
        return getattr(it, "scene_item_index", None)


    def _create_color_source(self, name: str, w: int = 10, h: int = 10):
        # Try modern then legacy color source kinds
        for kind in ("color_source_v3", "color_source"):
            try:
                # create_input(sceneName, inputName, inputKind, inputSettings, sceneItemEnabled=False)
                self.cl.create_input(
                    self.scene,
                    name,
                    kind,
                    {
                        "width": int(max(1, w)),
                        "height": int(max(1, h)),
                        "color": 0xFF000000,  # opaque black (RGBA)
                    },
                    False,
                )
                return True
            except OBSSDKRequestError:
                continue
        raise RuntimeError("Failed to create Color Source (tried color_source_v3 and color_source)")

    def _ensure_pool(self, n: int):
        """Ensure we have exactly n color sources reserved for masks, named f'{prefix}_{i}'."""
        existing = self._list_items_map()

        # Collect current pool members (strictly by prefix_)
        pool_names = [name for name in existing.keys() if name.startswith(f"{self.prefix}_") and  name != self.panic_name]
        pool_names.sort()  # stable ordering

        # Create more if needed
        i = 0
        while len(pool_names) < n:
            # find next unused name in sequence
            while f"{self.prefix}_{i}" in existing:
                i += 1
            name = f"{self.prefix}_{i}"
            self._create_color_source(name, 10, 10)  # tiny; will be resized per box
            existing = self._list_items_map()        # refresh IDs after creation
            pool_names.append(name)
            i += 1

        # Record the pool and push to top, keep them initially disabled
        self.mask_names = pool_names[:n]
        self.mask_ids = [existing[name] for name in self.mask_names]
        for sid in self.mask_ids:
            self._move_to_top(sid)
            self.cl.set_scene_item_enabled(self.scene, sid, False)


    def _ensure_panic(self):
        existing = self._list_items_map()

        if self.panic_name not in existing:
            self._create_color_source(self.panic_name, self.canvas_w, self.canvas_h)
            existing = self._list_items_map()

        self.panic_id = existing[self.panic_name]
        self._move_to_top(self.panic_id)
        # Make sure panic starts disabled
        self.cl.set_scene_item_enabled(self.scene, self.panic_id, False)

    def apply_boxes(self, boxes: List[Box]):
        for b in boxes:
            b.clamp(self.canvas_w, self.canvas_h)

        for i, name in enumerate(self.mask_names):
            sid = self.mask_ids[i]
            if i < len(boxes) and boxes[i].width > 0 and boxes[i].height > 0:
                b = boxes[i]

                # set_input_settings(inputName, inputSettings, overlay=True)
                self.cl.set_input_settings(
                    name,
                    {
                        "width": int(b.width),
                        "height": int(b.height),
                        "color": 0xFF000000,  # opaque black
                    },
                    True,
                )

                # set_scene_item_transform(sceneName, sceneItemId, sceneItemTransform)
                self.cl.set_scene_item_transform(
                    self.scene,
                    sid,
                    {
                        "positionX": float(b.x1),
                        "positionY": float(b.y1),
                        "alignment": 5,
                        "boundsType": "OBS_BOUNDS_NONE",
                    },
                )

                # set_scene_item_enabled(sceneName, sceneItemId, sceneItemEnabled)
                self.cl.set_scene_item_enabled(self.scene, sid, True)
            else:
                self.cl.set_scene_item_enabled(self.scene, sid, False)

    def set_panic(self, on: bool):
        if self.panic_id is None:
            return

        if on:
            # Hide all individual masks while PANIC is up
            for sid in self.mask_ids:
                self.cl.set_scene_item_enabled(self.scene, sid, False)

        # set_input_settings(inputName, inputSettings, overlay=True)
        self.cl.set_input_settings(
            self.panic_name,
            {
                "width": int(self.canvas_w),
                "height": int(self.canvas_h),
                "color": 0xFF000000,  # opaque black
            },
            True,
        )

        self.cl.set_scene_item_enabled(self.scene, self.panic_id, bool(on))

class FrameFeed:
    def __init__(self):
        self.latest_boxes: List[Box] = []
        self.lock = threading.Lock()
        self.running = True

    def update(self, boxes: List[Box]):
        with self.lock:
            self.latest_boxes = boxes

    def snapshot(self) -> List[Box]:
        with self.lock:
            return list(self.latest_boxes)

    def stop(self):
        self.running = False

def parse_boxes(line: str) -> List[Box]:
    arr = json.loads(line)
    out = []
    for r in arr:
        x1, y1, x2, y2 = float(r["x1"]), float(r["y1"]), float(r["x2"]), float(r["y2"])
        out.append(Box(x1, y1, x2, y2))
    return out

def stdin_reader(feed: FrameFeed):
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            boxes = parse_boxes(line)
            feed.update(boxes)
        except Exception:
            continue

def gen_random_boxes(w, h, count, min_size=80, max_size=260):
    boxes = []
    for _ in range(count):
        ww = random.randint(min_size, max_size)
        hh = random.randint(min_size, max_size)
        x1 = random.randint(0, max(0, w - ww))
        y1 = random.randint(0, max(0, h - hh))
        boxes.append(Box(x1, y1, x1 + ww, y1 + hh))
    return boxes

def random_feeder(feed: FrameFeed, w: int, h: int, count: int, fps: int):
    interval = 1.0 / max(1, fps)
    while feed.running:
        feed.update(gen_random_boxes(w, h, count))
        time.sleep(interval)

def bouncing_feeder(feed: FrameFeed, w: int, h: int, count: int, size=180, speed=8, fps: int = 60):
    import math
    interval = 1.0 / max(1, fps)
    balls = []
    for _ in range(count):
        x = random.randint(0, max(0, w - size))
        y = random.randint(0, max(0, h - size))
        a = random.random() * math.tau
        balls.append([x, y, size, size, speed * math.cos(a), speed * math.sin(a)])
    while feed.running:
        boxes = []
        for b in balls:
            b[0] += b[4]; b[1] += b[5]
            if b[0] < 0 or b[0] + b[2] > w: b[4] *= -1; b[0] = max(0, min(b[0], w - b[2]))
            if b[1] < 0 or b[1] + b[3] > h: b[5] *= -1; b[1] = max(0, min(b[1], h - b[3]))
            boxes.append(Box(b[0], b[1], b[0] + b[2], b[1] + b[3]))
        feed.update(boxes)
        time.sleep(interval)

class PanicHotkey:
    def __init__(self, toggle_fn, combo="ctrl+alt+m"):
        self.toggle_fn = toggle_fn
        self.combo = combo
        self.is_down = set()
        self.enabled = True
        self._parse_combo()

    def _parse_combo(self):
        parts = self.combo.lower().split("+")
        self.need = set(parts)

    def start(self):
        def on_press(key):
            if not self.enabled: return
            try:
                name = key.char.lower()
            except Exception:
                name = str(key).lower().replace("key.", "")
            self.is_down.add(name)
            if self.need.issubset(self.is_down):
                self.toggle_fn()
        def on_release(key):
            try:
                name = key.char.lower()
            except Exception:
                name = str(key).lower().replace("key.", "")
            self.is_down.discard(name)
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True
        listener.start()

def main():
    ap = argparse.ArgumentParser(description="OBS black-box masker (per-frame).")
    ap.add_argument("--obs-host", default="localhost")
    ap.add_argument("--obs-port", type=int, default=4455)
    ap.add_argument("--obs-password", default="V7s23mQOACBp6Yvq")
    ap.add_argument("--scene", default=None, help="Target scene (default: current Program scene)")
    ap.add_argument("--overlay-prefix", default="MASK", help="Prefix for generated color sources")
    ap.add_argument("--max-boxes", type=int, default=50, help="Pool size for color sources")
    ap.add_argument("--canvas-w", type=int, default=2560, help="Scene canvas width (px)")
    ap.add_argument("--canvas-h", type=int, default=1440, help="Scene canvas height (px)")
    ap.add_argument("--fps", type=int, default=90, help="Update rate")
    ap.add_argument("--mode", choices=["stdin", "random", "bounce"], default="bounce")
    ap.add_argument("--random-count", type=int, default=15, help="Boxes for test modes")
    ap.add_argument("--panic-hotkey", default="ctrl+alt+m", help="Global hotkey to toggle full blackout")
    args = ap.parse_args()

    cl = obs.ReqClient(host=args.obs_host, port=args.obs_port, password=args.obs_password, timeout=3)

    try:
        vs = cl.get_video_settings()
        base_w, base_h = vs.base_width, vs.base_height
    except Exception:
        base_w, base_h = args.canvas_w, args.canvas_h

    if args.canvas_w != 2560 or args.canvas_h != 1440:
        base_w, base_h = args.canvas_w, args.canvas_h

    overlay = OBSMasks(cl, args.scene, args.overlay_prefix, base_w, base_h, args.max_boxes)

    feed = FrameFeed()

    panic_state = {"on": False}
    def toggle_panic():
        panic_state["on"] = not panic_state["on"]
        overlay.set_panic(panic_state["on"])

    PanicHotkey(toggle_panic, combo=args.panic_hotkey).start()

    def on_usr1(signum, frame):
        toggle_panic()
    try:
        signal.signal(signal.SIGUSR1, on_usr1)
    except Exception:
        pass

    if args.mode == "stdin":
        t = threading.Thread(target=stdin_reader, args=(feed,), daemon=True)
    elif args.mode == "random":
        t = threading.Thread(target=random_feeder, args=(feed, base_w, base_h, args.random_count, args.fps), daemon=True)
    elif args.mode == "bounce":
        t = threading.Thread(target=bouncing_feeder, args=(feed, base_w, base_h, args.random_count, 180, 10, args.fps), daemon=True)
    t.start()

    frame_interval = 1.0 / max(1, args.fps)
    try:
        while True:
            if not panic_state["on"]:
                boxes = feed.snapshot()
                if boxes:                  # <-- only apply if non-empty
                    overlay.apply_boxes(boxes)
                # else: do nothing; don't force-hide masks
            time.sleep(frame_interval)
    except KeyboardInterrupt:
        feed.stop()

if __name__ == "__main__":
    main()

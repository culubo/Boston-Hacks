from fastapi import FastAPI
from fastapi.responses import JSONResponse
import subprocess

app = FastAPI()

@app.post("/block")
def block_screen():
    try:
        subprocess.Popen([
            "python3", "parent_mask_and_block_stream.py",
            "--fastscreenocr", "./fastscreenocr",
            "--obs-script", "mask_overlay.py",
            "--model-pkl", "/Users/mwatk/Documents/Boston-Hacks/Backend/ML_Model/final_model.pkl",
            "--features-path", "/Users/mwatk/Documents/Boston-Hacks/Backend/ML_Model",
            "--fps", "5",
            "--canvas-w", "2560", "--canvas-h", "1440",
            "--display-w", "2560", "--display-h", "1440",
            "--langs", "en-US"
        ])
        return JSONResponse({"status": "started"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

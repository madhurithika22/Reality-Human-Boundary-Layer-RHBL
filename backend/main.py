from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import threading
import time
import shutil
from logic import SentinelEngine
from database import save_log
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SentinelEngine()

# GLOBAL STATE
VIDEO_SOURCE = 1  # Default Camera Index
camera = None

current_stats = {
    "layer": "human",
    "score": 0.0,
    "confidence_interval": [0.0, 0.0],
    "quality": 0.0,
    "violated_rules": [],
    "prompt": "INITIALIZING...",
    "rppg_wave": [],
    "checks": {}
}

def get_camera():
    global camera, VIDEO_SOURCE
    if camera is not None and camera.isOpened():
        return camera
    print(f"Opening Source: {VIDEO_SOURCE}")
    camera = cv2.VideoCapture(VIDEO_SOURCE, cv2.CAP_DSHOW if isinstance(VIDEO_SOURCE, int) else None)
    return camera

def db_worker():
    while True:
        time.sleep(1.0)
        # Check if score > 0.0 (Float comparison)
        if current_stats.get("score", 0.0) > 0.01:
            save_log(current_stats)

threading.Thread(target=db_worker, daemon=True).start()

def generate_frames():
    global camera, VIDEO_SOURCE
    
    while True:
        cap = get_camera()
        success, frame = cap.read()
        
        if not success:
            if isinstance(VIDEO_SOURCE, str): # Loop video
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                cap.release()
                camera = None 
                time.sleep(1)
                continue
        
        try:
            if isinstance(VIDEO_SOURCE, int):
                frame = cv2.flip(frame, 1)

            processed_frame, stats_dict = engine.process_frame(frame)
            
            global current_stats
            current_stats = stats_dict

            ret, buffer = cv2.imencode('.jpg', processed_frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"Frame Error: {e}")
            continue

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/stats")
def get_stats():
    return current_stats

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    global VIDEO_SOURCE, camera, engine
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    if camera: camera.release()
    camera = None
    VIDEO_SOURCE = file_location
    engine = SentinelEngine() # Reset state
    return {"status": "Source switched"}

@app.post("/reset_camera")
def reset_camera():
    global VIDEO_SOURCE, camera, engine
    if camera: camera.release()
    camera = None
    VIDEO_SOURCE = 1
    engine = SentinelEngine()
    return {"status": "Reset to webcam"}
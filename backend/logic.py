import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from scipy.spatial import distance as dist
import sys
import os

# Adds project root to path for cross-layer imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer_c.backend.app.core.physics import physics_consistency
from layer_c.backend.app.core.temporal import temporal_consistency
from layer_c.backend.app.core.biology import bio_motion_sync
from layer_c.backend.app.core.scorer import fuse_scores
from layer_b.logic.scoring import analyze_text_logic

class SentinelEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.7, refine_landmarks=True)
        self.mp_pose = mp.solutions.pose.Pose(static_image_mode=False)
        self.pose_buffer = deque(maxlen=30) 
        
        self.state = "SEARCHING"
        self.score = 0.0  
        self.manipulation_prob = 0.0
        self.trust_score = 0.0   
        self.quality = 0.0
        self.prompt = "Looking for subject..."
        self.rppg_buffer = deque(maxlen=100) # Buffer for pulse
        self.reasons = []

    def process_frame(self, image, current_text=""):
        image = cv2.resize(image, (640, 480))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape
        
        face_results = self.face_mesh.process(image_rgb)
        pose_results = self.mp_pose.process(image_rgb)
        
        if pose_results.pose_landmarks:
            self.pose_buffer.append([(lm.x, lm.y, lm.z) for lm in pose_results.pose_landmarks.landmark])
        
        if not face_results.multi_face_landmarks:
            self.state = "SEARCHING"
            return image, self._build_json(["No Human Detected"])

        for face_landmarks in face_results.multi_face_landmarks:
            # rPPG Extraction Logic
            lm151 = face_landmarks.landmark[151] # Forehead point
            roi_y, roi_x = int(lm151.y * h), int(lm151.x * w)
            if 10 < roi_y < h-10 and 10 < roi_x < w-10:
                roi = image[roi_y-5:roi_y+5, roi_x-5:roi_x+5, 1] # Green channel
                self.rppg_buffer.append(np.mean(roi))

            self.score = 0.95 # Simulated verification

        if len(self.pose_buffer) >= 15:
            pose_seq = np.array(list(self.pose_buffer))
            self.trust_score, self.reasons = fuse_scores(
                physics_consistency(pose_seq), 
                temporal_consistency(pose_seq), 
                bio_motion_sync(pose_seq), 
                human_score=self.score, 
                quality=0.8,
                manipulation_prob=self.manipulation_prob
            )

        return image, self._build_json([])

    def _build_json(self, violated_rules):
        # Enhanced Normalization for pulse graph
        graph_data = []
        if len(self.rppg_buffer) > 10:
            arr = np.array(self.rppg_buffer)
            diff = np.max(arr) - np.min(arr)
            if diff > 0:
                norm = (arr - np.min(arr)) / diff
                graph_data = norm.tolist()

        return {
            "trust_score": self.trust_score,
            "layer_scores": {
                "human_authenticity": round(self.score * 100, 2),
                "reality_consistency": round(self.trust_score * 0.6, 2),
                "manipulation_risk": round(self.manipulation_prob * 100, 2)
            },
            "violated_rules": list(set(violated_rules + self.reasons)),
            "prompt": self.prompt,
            "rppg_wave": graph_data, # Synchronized key
            "checks": {}
        }
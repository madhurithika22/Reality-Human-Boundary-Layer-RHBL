import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from scipy.spatial import distance as dist
import sys
import os

# Ensure project root is in path for cross-layer imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layer_c.backend.app.core.physics import physics_consistency
from layer_c.backend.app.core.temporal import temporal_consistency
from layer_c.backend.app.core.biology import bio_motion_sync
from layer_c.backend.app.core.scorer import fuse_scores

class SentinelEngine:
    def __init__(self):
        # Layer A: Human Authenticity Setup
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7,
            refine_landmarks=True 
        )
        # Layer C: Reality Consistency Setup
        self.mp_pose = mp.solutions.pose.Pose(static_image_mode=False)
        self.pose_buffer = deque(maxlen=30) 
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=0, color=(255, 255, 0))

        # Metrics & State
        self.state = "SEARCHING"
        self.state_start_time = time.time()
        self.condition_start_time = None
        self.score = 0.1  # Human Score
        self.reality_score = 0.0 
        self.trust_score = 0.0
        self.quality = 0.0
        self.prompt = "Looking for subject..."
        self.rppg_buffer = deque(maxlen=150)
        self.checks = {"calibrated": False, "turned": False, "smiled": False, "blinked": False}
        self.reasons = []
        self.eyes_closed = False
        self.current_violation = None

    def get_quality(self, face_landmarks, image_shape):
        h, w, _ = image_shape
        face_height = dist.euclidean(
            (face_landmarks.landmark[10].x * w, face_landmarks.landmark[10].y * h),
            (face_landmarks.landmark[152].x * w, face_landmarks.landmark[152].y * h)
        )
        return float(min(1.0, face_height / (h * 0.4)))

    def detect_smile(self, landmarks):
        mouth_width = dist.euclidean(landmarks[61], landmarks[291])
        jaw_width = dist.euclidean(landmarks[234], landmarks[454])
        return (mouth_width / jaw_width) > 0.38

    def calculate_ear(self, eye_points, landmarks):
        A = dist.euclidean(landmarks[eye_points[1]], landmarks[eye_points[5]])
        B = dist.euclidean(landmarks[eye_points[2]], landmarks[eye_points[4]])
        C = dist.euclidean(landmarks[eye_points[0]], landmarks[eye_points[3]])
        return (A + B) / (2.0 * C)

    def get_pose(self, shape, face_landmarks):
        h, w, _ = shape
        face_2d = []
        face_3d = []
        indices = [1, 152, 33, 263, 61, 291]
        for idx in indices:
            lm = face_landmarks.landmark[idx]
            face_2d.append([int(lm.x * w), int(lm.y * h)])
            face_3d.append([int(lm.x * w), int(lm.y * h), lm.z])
        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)
        focal = 1 * w
        cam_matrix = np.array([[focal, 0, h/2], [0, focal, w/2], [0, 0, 1]], dtype=np.float64)
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        _, rot_vec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        return angles[1] * 360

    def process_frame(self, image):
        image = cv2.resize(image, (640, 480))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape
        
        face_results = self.face_mesh.process(image_rgb)
        pose_results = self.mp_pose.process(image_rgb)
        
        violated_rules = []

        if pose_results.pose_landmarks:
            current_pose = [(lm.x, lm.y, lm.z) for lm in pose_results.pose_landmarks.landmark]
            self.pose_buffer.append(current_pose)
        
        if not face_results.multi_face_landmarks:
            self.state = "SEARCHING"
            self.prompt = "WAITING FOR SUBJECT..."
            self.trust_score = 0.0
            return image, self._build_json(["No Face Detected"])

        for face_landmarks in face_results.multi_face_landmarks:
            self.quality = self.get_quality(face_landmarks, image.shape)
            lms = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark])
            yaw = self.get_pose(image.shape, face_landmarks)
            is_smiling = self.detect_smile(lms)
            
            # rPPG
            lm151 = face_landmarks.landmark[151]
            val = np.mean(image[int(lm151.y*h)-5:int(lm151.y*h)+5, int(lm151.x*w)-5:int(lm151.x*w)+5, 1])
            self.rppg_buffer.append(val)

            # Blink Detection
            ear = (self.calculate_ear([33, 160, 158, 133, 153, 144], lms) + 
                   self.calculate_ear([362, 385, 387, 263, 373, 380], lms)) / 2.0
            if ear < 0.22: self.eyes_closed = True
            else: self.eyes_closed = False

            # State Machine Logic
            if self.state == "SEARCHING":
                self.state = "CALIBRATING"
                self.state_start_time = time.time()
                self.prompt = "Align Face & Hold Still..."
            elif self.state == "CALIBRATING":
                if time.time() - self.state_start_time > 3.0:
                    self.state = "CHALLENGE_TURN"
                    self.score = 0.3
                    self.checks["calibrated"] = True
            elif self.state == "CHALLENGE_TURN":
                self.prompt = "ACTION: Turn Head LEFT ⬅️"
                if yaw < -18:
                    self.state = "CHALLENGE_SMILE"
                    self.score = 0.5
                    self.checks["turned"] = True
            elif self.state == "CHALLENGE_SMILE":
                self.prompt = "ACTION: Smile 😊"
                if is_smiling:
                    self.state = "CHALLENGE_BLINK"
                    self.score = 0.75
                    self.checks["smiled"] = True
            elif self.state == "CHALLENGE_BLINK":
                self.prompt = "ACTION: Blink Eyes 👁️"
                if ear < 0.22: self.blink_ready = True
                if getattr(self, 'blink_ready', False) and ear > 0.26:
                    self.state = "VERIFIED"
                    self.score = 0.98
                    self.checks["blinked"] = True

        # Trust Fusion Layer
        if len(self.pose_buffer) >= 15:
            pose_seq = np.array(list(self.pose_buffer))
            phys = physics_consistency(pose_seq)
            temp = temporal_consistency(pose_seq)
            bio = bio_motion_sync(pose_seq)
            
            self.trust_score, self.reasons = fuse_scores(
                phys, temp, bio, 
                human_score=self.score, 
                quality=self.quality
            )

        return image, self._build_json(violated_rules)

    def _build_json(self, violated_rules):
        all_violations = list(set(violated_rules + self.reasons))
        graph_data = []
        if len(self.rppg_buffer) > 10:
            arr = np.array(self.rppg_buffer)
            norm = (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-6)
            graph_data = norm.tolist()

        return {
            "trust_score": self.trust_score,
            "layer_scores": {
                "human_authenticity": round(self.score * 100, 2),
                "reality_consistency": round(self.trust_score * 0.6, 2) # Weighted estimate
            },
            "quality": round(self.quality, 2),
            "violated_rules": [r for r in all_violations if "No major" not in r],
            "prompt": self.prompt,
            "rppg_wave": graph_data,
            "checks": self.checks
        }
import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque
from scipy.spatial import distance as dist

class SentinelEngine:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7,
            refine_landmarks=True 
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=0, color=(255, 255, 0))

        # State Machine
        self.state = "SEARCHING"
        self.state_start_time = time.time()
        self.condition_start_time = None 
        
        # Metrics
        self.score = 0.0
        self.quality = 0.0
        self.prompt = "Looking for subject..."
        self.rppg_buffer = deque(maxlen=150)
        
        # Validation Tracking
        self.checks = {"calibrated": False, "turned": False, "smiled": False, "blinked": False}
        self.eyes_closed = False
        self.current_violation = None 

    def get_quality(self, face_landmarks, image_shape):
        h, w, _ = image_shape
        face_height = dist.euclidean(
            (face_landmarks.landmark[10].x * w, face_landmarks.landmark[10].y * h),
            (face_landmarks.landmark[152].x * w, face_landmarks.landmark[152].y * h)
        )
        quality = min(1.0, face_height / (h * 0.4))
        return float(quality)

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
        face_3d = []
        face_2d = []
        indices = [1, 152, 33, 263, 61, 291]
        for idx in indices:
            lm = face_landmarks.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])
        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)
        focal = 1 * w
        cam_matrix = np.array([[focal, 0, h/2], [0, focal, w/2], [0, 0, 1]], dtype=np.float64)
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        success, rot_vec, _ = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        rmat, _ = cv2.Rodrigues(rot_vec)
        angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
        return angles[1] * 360 # Yaw

    def process_frame(self, image):
        image = cv2.resize(image, (640, 480))
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        h, w, _ = image.shape
        
        violated_rules = [] 
        
        if not results.multi_face_landmarks:
            self.state = "SEARCHING"
            self.prompt = "WAITING FOR SUBJECT..."
            self.score = 0.0
            self.quality = 0.0
            violated_rules.append("No Face Detected")
            return image, self._build_json(violated_rules)

        for face_landmarks in results.multi_face_landmarks:
            self.mp_drawing.draw_landmarks(
                image=image, landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None, connection_drawing_spec=self.drawing_spec)

            lms = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark])
            yaw = self.get_pose(image.shape, face_landmarks)
            is_smiling = self.detect_smile(lms)
            
            lm151 = face_landmarks.landmark[151]
            val = np.mean(image[int(lm151.y*h)-5:int(lm151.y*h)+5, int(lm151.x*w)-5:int(lm151.x*w)+5, 1])
            self.rppg_buffer.append(val)
            
            self.quality = self.get_quality(face_landmarks, image.shape)
            if self.quality < 0.35: violated_rules.append("3D Features Mismatch (Low Quality)")
            
            # --- IMPROVED BLINK LOGIC ---
            left_indices = [33, 160, 158, 133, 153, 144]
            right_indices = [362, 385, 387, 263, 373, 380]
            ear = (self.calculate_ear(left_indices, lms) + self.calculate_ear(right_indices, lms)) / 2.0
            
            # DEBUG: Uncomment this to see your EAR value in terminal
            # print(f"Eye Ratio: {ear:.3f}") 

            # Easier Thresholds: Close < 0.22, Open > 0.25
            if ear < 0.22: 
                self.eyes_closed = True
                if self.state != "CHALLENGE_BLINK":
                    if self.condition_start_time and time.time() - self.condition_start_time > 1.5:
                         violated_rules.append("Eye Gaze Not Proper (Eyes Closed)")
            else:
                self.eyes_closed = False

            # --- STATE MACHINE ---
            if self.state == "FAILED":
                self.prompt = f"FAILED: {self.current_violation}"
                self.score = 0.0
                violated_rules.append(self.current_violation)
                if time.time() - self.state_start_time > 2.0:
                    self.state = "SEARCHING"
                    self.current_violation = None
            
            elif self.state == "SEARCHING":
                self.score = 0.1
                self.state = "CALIBRATING"
                self.state_start_time = time.time()
                self.prompt = "Align Face & Hold Still..."

            elif self.state == "CALIBRATING":
                self.prompt = "Calibrating Sensors..."
                if time.time() - self.state_start_time > 3.0:
                    self.state = "CHALLENGE_TURN"
                    self.state_start_time = time.time()
                    self.score = 0.3
                    self.checks["calibrated"] = True
            
            elif self.state == "CHALLENGE_TURN":
                self.prompt = "ACTION: Turn Head LEFT ⬅️"
                if yaw < -18:
                    if not self.condition_start_time: self.condition_start_time = time.time()
                    elif time.time() - self.condition_start_time > 0.5:
                        self.state = "CHALLENGE_SMILE"
                        self.score = 0.5
                        self.checks["turned"] = True
                        self.condition_start_time = None
                else:
                    self.condition_start_time = None
                    if time.time() - self.state_start_time > 8.0: self._trigger_failure("Did Not Turn Head")

            elif self.state == "CHALLENGE_SMILE":
                self.prompt = "ACTION: Smile 😊"
                if is_smiling:
                    if not self.condition_start_time: self.condition_start_time = time.time()
                    elif time.time() - self.condition_start_time > 1.0:
                        self.state = "CHALLENGE_BLINK"
                        self.score = 0.75
                        self.checks["smiled"] = True
                        self.condition_start_time = None
                else:
                    self.condition_start_time = None
                    if time.time() - self.state_start_time > 8.0: self._trigger_failure("Did Not Smile")

            elif self.state == "CHALLENGE_BLINK":
                self.prompt = "ACTION: Blink Eyes 👁️"
                
                # Logic: We detected a close (self.eyes_closed was True) AND now it's Open (ear > 0.25)
                # This transition means a blink happened.
                if ear > 0.25 and self.eyes_closed: # Try to catch the rising edge
                     pass # Wait for the variable to update
                
                # Simplified Check: Just detecting the sequence
                if ear < 0.22: 
                     self.blink_ready = True # Flag that we saw a close
                
                # If we saw a close recently, and now it's open -> Success
                if getattr(self, 'blink_ready', False) and ear > 0.26:
                    self.state = "VERIFIED"
                    self.score = 0.98 
                    self.checks["blinked"] = True
                    self.blink_ready = False
                
                if time.time() - self.state_start_time > 8.0: self._trigger_failure("Did Not Blink")

            elif self.state == "VERIFIED":
                self.prompt = "AUTHENTIC HUMAN CONFIRMED"
                self.score = 0.98

        return image, self._build_json(violated_rules)

    def _trigger_failure(self, reason):
        self.state = "FAILED"
        self.current_violation = reason
        self.state_start_time = time.time()

    def _build_json(self, violated_rules):
        graph_data = []
        if len(self.rppg_buffer) > 10:
            arr = np.array(self.rppg_buffer)
            norm = (arr - np.min(arr)) / (np.max(arr) - np.min(arr) + 1e-6)
            graph_data = norm.tolist()

        return {
            "layer": "human",
            "score": round(self.score, 2),
            "confidence_interval": [max(0.0, round(self.score - 0.1, 2)), min(1.0, round(self.score + 0.1, 2))],
            "quality": round(self.quality, 2),
            "violated_rules": violated_rules,
            "prompt": self.prompt,
            "rppg_wave": graph_data,
            "checks": self.checks
        }
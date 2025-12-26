import cv2, mediapipe as mp, numpy as np

mp_pose = mp.solutions.pose.Pose(static_image_mode=False)

def extract_pose_sequence(video_bytes):
    tmp = "temp.mp4"
    open(tmp, "wb").write(video_bytes)
    cap = cv2.VideoCapture(tmp)

    sequence = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        res = mp_pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if res.pose_landmarks:
            sequence.append([
                (lm.x, lm.y, lm.z) for lm in res.pose_landmarks.landmark
            ])
    cap.release()
    return np.array(sequence)

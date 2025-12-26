import numpy as np

def temporal_consistency(pose_sequence):
    if pose_sequence is None or len(pose_sequence) < 3:
        return 0.0

    acceleration = np.diff(pose_sequence, n=2, axis=0)
    spikes = np.linalg.norm(acceleration, axis=2) > 5.0

    score = 1.0 - np.mean(spikes)
    return float(round(score, 3))

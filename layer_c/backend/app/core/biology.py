import numpy as np


def bio_motion_sync(pose_sequence):
    """
    Checks biological plausibility between head and torso motion
    Returns score in [0,1]
    """
    if pose_sequence is None or len(pose_sequence) < 3:
        return 0.0

    head = pose_sequence[:, 0]     # nose
    torso = pose_sequence[:, 23]   # hip

    head_motion = np.linalg.norm(np.diff(head, axis=0), axis=1)
    torso_motion = np.linalg.norm(np.diff(torso, axis=0), axis=1)

    if np.std(head_motion) == 0 or np.std(torso_motion) == 0:
        return 0.0

    corr = np.corrcoef(head_motion, torso_motion)[0, 1]
    return float(round(max(corr, 0.0), 3))

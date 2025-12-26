import numpy as np

MAX_JOINT_VELOCITY = 3.5  # realistic human motion limit


def physics_consistency(pose_sequence):
    """
    Checks whether joint motion obeys basic physical constraints.
    Returns a score in [0,1]
    """
    if pose_sequence is None or len(pose_sequence) < 2:
        return 0.0

    # Velocity = frame-to-frame displacement
    velocities = np.linalg.norm(
        np.diff(pose_sequence, axis=0),
        axis=2
    )

    # Detect physically impossible jumps
    violations = velocities > MAX_JOINT_VELOCITY

    score = 1.0 - np.mean(violations)
    return float(round(score, 3))

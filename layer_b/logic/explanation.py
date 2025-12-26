def generate_explanation(patterns):
    if not patterns:
        return "No psychological manipulation detected."
    return "Detected manipulation via " + ", ".join(patterns)

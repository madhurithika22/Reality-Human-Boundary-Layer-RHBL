from layer_b.logic.pattern_rules import detect_patterns

def analyze_text_logic(text: str):
    patterns = detect_patterns(text)

    # Ensure list (not set / None)
    if not patterns:
        patterns = []

    score = min(len(patterns) * 0.3, 1.0)

    explanation = (
        f"Detected manipulation via {', '.join(patterns)}"
        if patterns else
        "No manipulation patterns detected"
    )

    return float(score), patterns, explanation

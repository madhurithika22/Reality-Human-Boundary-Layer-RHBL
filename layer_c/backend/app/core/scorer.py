def fuse_scores(physics, temporal, biology):
    """
    Fuse Layer-C signals into a single Reality Consistency Score.
    Returns (score_0_to_100, explanation_list)
    """

    score = (0.4 * physics) + (0.3 * temporal) + (0.3 * biology)
    score_100 = round(score * 100, 2)

    explanation = []
    if physics < 0.7:
        explanation.append("Physics consistency violation detected")
    if temporal < 0.7:
        explanation.append("Temporal discontinuity detected")
    if biology < 0.6:
        explanation.append("Biological motion inconsistency detected")

    if not explanation:
        explanation.append("No major reality violations detected")

    return score_100, explanation

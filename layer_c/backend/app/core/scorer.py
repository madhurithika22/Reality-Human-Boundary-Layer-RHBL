# A:\reality_engine\Reality-Human-Boundary-Layer-RHBL\layer_c\backend\app\core\scorer.py

def fuse_scores(physics, temporal, biology, human_score=0.0, quality=0.0, manipulation_prob=0.0):
    """
    Fuses all Layer-A and Layer-C signals into a single Trust Score.
    """
    if quality < 0.35:
        return 0.0, ["Refused: Poor environment quality for verification."]

    # Reality Consistency Score
    reality_score = (0.4 * physics) + (0.3 * temporal) + (0.3 * biology)
    
    # Final Trust Fusion
    final_score = (human_score * 0.4) + (reality_score * 0.4) + ((1 - manipulation_prob) * 0.2)
    
    explanation = []
    if physics < 0.7: explanation.append("Physics consistency violation detected")
    if human_score < 0.6: explanation.append("Low human authenticity signals")

    return round(final_score * 100, 2), explanation
# In backend/logic.py
def _build_json(self, violated_rules):
    # Ensure fuse_scores is called to get final trust data
    # trust_score, explanation = fuse_scores(...) 

    return {
        "trust_score": getattr(self, 'trust_score', 0), # Matches stats.trust_score
        "layer_scores": {
            "human_authenticity": round(self.score * 100, 2),
            "reality_consistency": getattr(self, 'reality_score', 0)
        },
        "quality": round(self.quality, 2),
        "violated_rules": list(set(violated_rules + getattr(self, 'reasons', []))),
        "prompt": self.prompt,
        "rppg_wave": self._get_normalized_rppg(),
        "checks": self.checks
    }
from fastapi import APIRouter, UploadFile, File
from app.core.skeleton import extract_pose_sequence
from app.core.physics import physics_consistency
from app.core.temporal import temporal_consistency
from app.core.biology import bio_motion_sync
from app.core.scorer import fuse_scores

router = APIRouter(prefix="/analyze", tags=["Reality Validation"])

@router.post("/video")
async def analyze_video(file: UploadFile = File(...)):
    pose_seq = extract_pose_sequence(await file.read())

    physics = physics_consistency(pose_seq)
    temporal = temporal_consistency(pose_seq)
    biology = bio_motion_sync(pose_seq)

    score, explanation = fuse_scores(physics, temporal, biology)

    return {
        "reality_score": score,
        "components": {
            "physics": physics,
            "temporal": temporal,
            "biological": biology
        },
        "explanation": explanation
    }

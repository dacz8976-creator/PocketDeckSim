import json
from pathlib import Path

root = Path(__file__).parent
frames = sorted((root / "frames_1s").glob("f_*.jpg"))
dense = sorted((root / "dense").glob("*.jpg"))
starts = {"a": 20.0, "b": 99.0, "c": 140.0}
index = {
    "source_basename": "20261009_195029000_iOS.MP4",
    "source_sha256": "8b069aade34fbba5615a4f500ab0aa5a150ae8c823be6aa23ca18d5f0a9ddc48",
    "timestamp_note": "Times are nominal source-local elapsed seconds from ffmpeg fps extraction. The 1 fps samples are identified by their second bin; dense samples are at one-third-second steps. Cite an approximate time for animation events.",
    "dimensions_note": "Overview and dense frames are 585 x 1266, scaled from the 1170 x 2532 source. Intake frames retain native source resolution. A separate verifier is retaining a small native-resolution consequential proof set.",
    "overview": [{"path": str(p.relative_to(root)).replace('\\', '/'), "nominal_seconds": int(p.stem[2:]) - 1} for p in frames],
    "dense": [{"path": str(p.relative_to(root)).replace('\\', '/'), "nominal_seconds": round(starts[p.stem[0]] + (int(p.stem[2:]) - 1) / 3, 3)} for p in dense],
    "intake_original": [
        {"path": "intake_frames/0_0.000s.jpg", "seconds": 0.0},
        {"path": "intake_frames/1_20.000s.jpg", "seconds": 20.0},
        {"path": "intake_frames/2_95.488s.jpg", "seconds": 95.488},
        {"path": "intake_frames/3_189.976s.jpg", "seconds": 189.976}
    ]
}
(root / "FRAME_INDEX.json").write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")

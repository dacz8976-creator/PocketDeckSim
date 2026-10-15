"""Append the approved archival disposition without changing partial battle scope."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parent.parent
for video, reviewer in [("20260926_211809000_iOS.MP4", "/root/older_211809"), ("20260926_212155000_iOS.MP4", "/root/older_212155")]:
    packet = BATCH / Path(video).stem
    summary = json.loads((packet / "SUMMARY.json").read_text(encoding="utf-8-sig"))
    lead = json.loads((packet / "LEAD_ACCEPTANCE.json").read_text(encoding="utf-8-sig"))
    receipt = packet / "ARCHIVE_REGISTRATION_RESULT.json"
    assert not receipt.exists()
    command = [sys.executable, str(ROOT / "Review_Log/review_log.py"), "record", "--video", video,
               "--reviewer", reviewer, "--status", "partial", "--scope", lead["scope"],
               "--recording-time", summary["source_creation_utc"],
               "--notes", lead["notes"] + " Owner explicitly approved completed-excerpt archive/offload on2026-10-14; missing-opening notes and partial-battle status preserved. Source now Reviewed with matching before/after SHA; OneDrive release waits for sync."]
    for name in ["REVIEW.md", "COVERAGE.md", "LEAD_ACCEPTANCE.json", "LEAD_ARCHIVE_EXCEPTION.json", "MOVE_RECEIPT." + video + ".json", "independent_sol/CHECK_RESULT.json"]:
        command.extend(["--evidence", str((packet / name).relative_to(ROOT))])
    command.extend(["--evidence", str((BATCH / "OWNER_EXCERPT_ARCHIVE_APPROVAL.json").relative_to(ROOT))])
    result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", capture_output=True)
    receipt.write_text(json.dumps({"registered_utc": datetime.now(timezone.utc).isoformat(), "exit_code": result.returncode,
                                 "stdout": result.stdout, "stderr": result.stderr, "command": command}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"video": video, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}))
    if result.returncode:
        raise SystemExit(result.returncode)

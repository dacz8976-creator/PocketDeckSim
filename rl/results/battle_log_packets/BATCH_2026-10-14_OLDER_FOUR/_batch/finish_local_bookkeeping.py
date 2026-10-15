"""Record approved browser retry outcome and prepared external handoff."""
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
status = {
    "recorded_utc": datetime.now(timezone.utc).isoformat(),
    "artifact_url": "https://claude.ai/artifact/GHSfGSCzNiWNj8SFPXV3R1",
    "owner_authorized_retry_and_verified_saves": True,
    "owner_answer": "Approve browser retry and verified saves",
    "initial_auto_review_rejection": "Earlier Computer Use stop after browser URL verification failed was cited; explicit fresh retry approval requested and granted",
    "fresh_browser_inventory": "Succeeded after approval; one returned Chrome window, Pause Games title",
    "initial_capture": "Returned null accessibility and wallpaper; no usable browser contents",
    "initial_activation_error": "GetCursorPos failed: Access is denied. (0x80070005)",
    "bounded_recovery": "Fresh list_windows and uniquely returned Chrome selection; one activation/state recovery attempt",
    "recovery_error": "computer-use request timed out: get_window_state",
    "browser_inputs_after_recovery_failure": 0,
    "current_live_source_filename_duplicate_check": False,
    "external_entries_written_this_turn": 0,
    "current_totals_verified": False,
    "status": "prepared_pending_browser_availability",
    "next_step": "When browser control is available, check source filename duplicates, save only absent prepared results, reload and verify entries/totals; user authorization persists",
    "candidates": ["20260926_211809000_iOS.MP4", "20260926_212155000_iOS.MP4"],
    "computer_sources_excluded": ["20261002_011527000_iOS.MP4", "20261002_012229000_iOS.MP4"],
}
(BATCH / "EXTERNAL_STATUS.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
candidate_path = BATCH / "LADDER_CANDIDATES.json"
before = BATCH / "LADDER_CANDIDATES.before_approved_retry.json"
assert not before.exists()
before.write_bytes(candidate_path.read_bytes())
candidates = json.loads(candidate_path.read_text(encoding="utf-8"))
candidates["status"] = status["status"]
candidates["browser_block"] = "Fresh retry authorized and inventory succeeded; Chrome activation access denied and one bounded recovery timed out; no live duplicate check/save"
candidates["owner_authorized_browser_retry"] = True
candidates["external_status_receipt"] = "EXTERNAL_STATUS.json"
candidate_path.write_text(json.dumps(candidates, indent=2) + "\n", encoding="utf-8")
for video in status["candidates"]:
    packet = BATCH / Path(video).stem
    per_source = {**status, "source_filename": video, "prepared_result": next(row for row in candidates["candidates"] if row["source_filename"] == video)}
    (packet / "EXTERNAL_SAVE_STATUS.json").write_text(json.dumps(per_source, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"prepared_ladder_candidates": 2, "external_entries_saved": 0, "retry_authorized": True, "current_block": "Browser control failed"}))

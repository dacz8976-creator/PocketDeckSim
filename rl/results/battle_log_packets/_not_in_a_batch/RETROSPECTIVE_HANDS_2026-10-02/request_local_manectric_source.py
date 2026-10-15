"""Ask OneDrive to deliver exactly one authorized source; no movie data reads."""
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[1]
FOLDER = BATCH / "20260909_023151000"
source = ROOT / "Reviewed" / "20260909_023151000_iOS.MP4"
assert source.resolve().is_relative_to((ROOT / "Reviewed").resolve())
prior = json.loads((FOLDER / "ROOT_SOURCE_VERIFICATION.json").read_text(encoding="utf-8-sig"))
assert prior["status"] == "source_access_error" and prior["attempt_number"] == 2
spec = importlib.util.spec_from_file_location("cloud_metadata", ROOT / "Recording_QA" / "free_reviewed_video_space.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
before = module.metadata(source)
assert before["cloud_placeholder"] and before["in_sync"]
receipt_path = FOLDER / "LOCAL_DELIVERY_REQUEST.json"
assert not receipt_path.exists(), "Do not repeat the same pin request automatically."
command = ["attrib.exe", "+P", "-U", str(source)]
run = subprocess.run(command, capture_output=True, text=True)
receipt = {
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "source": source.name,
    "current_path": str(source),
    "scope": "Download one selected review recording through OneDrive; restore online-only after acceptance.",
    "documentation": "https://learn.microsoft.com/en-us/sharepoint/files-on-demand-windows",
    "before": before,
    "command": command,
    "exit_code": run.returncode,
    "stdout": run.stdout,
    "stderr": run.stderr,
    "after_request": module.metadata(source),
    "movie_content_reads": 0,
    "previous_failed_reads": 2,
    "content_identity_verified": False,
}
receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
print(json.dumps(receipt))
if run.returncode:
    raise SystemExit(run.returncode)

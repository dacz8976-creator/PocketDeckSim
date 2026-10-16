"""Write current readable intake state without reading media contents."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_NEWER_LADDER_FOUR'
names = ['20261014_232438000_iOS.MP4','20261014_233402000_iOS.MP4','20261014_234511000_iOS.MP4','20261014_234728000_iOS.MP4']
sources = []
for name in names:
    packet = BATCH / Path(name).stem
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8'))
    availability = json.loads((packet / 'AVAILABILITY.json').read_text(encoding='utf-8'))
    assert availability['readable'] and availability['stable_size_mtime'] and availability['sha256_bound']
    sources.append({k: source[k] for k in ['video_basename','bytes','duration_seconds','sha256','source_creation_utc']})
now = datetime.now(timezone.utc).isoformat()
status = {'checked_utc': now, 'requested_games': 4, 'reviewable_sources': 4, 'registered_in_progress': 4, 'reviewed_games': 0, 'review_and_archive_complete': False, 'owner_authorization': 'Yes, include all six', 'availability_resolution': 'All four downloaded locally during final availability checkpoint. Readability, stable size/mtime, duration and source SHA256 verified; prior bounded retry receipts retained.', 'retry_automation': {'id':'retry-four-ladder-uploads','status':'PAUSED','reason':'All sources available; processing directly in the active thread'}, 'source_rows': sources, 'older_backlog_reopened': False}
(BATCH / 'SOURCE_INVENTORY.json').write_text(json.dumps(sources, indent=2) + '\n', encoding='utf-8')
(BATCH / 'BATCH_STATUS.json').write_text(json.dumps(status, indent=2) + '\n', encoding='utf-8')
(BATCH / 'README.md').write_text('# October 14 newer ladder sources\n\nAll four owner-authorized sources are now readable, stable and SHA256-bound. Each has an append-only in-progress assignment. Full source review, independent acceptance, lead reconciliation, completion registration, archival and live Ladder Log readback remain in progress. The first three workers are active; 234728 waits for a bounded worker slot.\n\nThe original two requested recordings are complete and saved in BATCH_2026-10-14_LATE_LADDER_TWO. No older backlog was reopened. Prior hydration timeout receipts describe the earlier source state. The temporary later-retry heartbeat is paused because all four sources became available in this active thread.\n\nSee SOURCE_INVENTORY.json, BATCH_STATUS.json and per-source packets.\n', encoding='utf-8')
print(json.dumps({'sources_ready':len(sources),'registered_in_progress':len(sources)}))

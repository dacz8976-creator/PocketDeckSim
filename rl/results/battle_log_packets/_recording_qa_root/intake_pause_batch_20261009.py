"""Source-bound intake for only the owner's newly requested October 9 uploads."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import intake_pause_batch_20261006 as prior

ROOT = Path(__file__).resolve().parent.parent
prior.BATCH = ROOT / 'Recording_QA/BATCH_2026-10-09_NEW_PAUSE_GAMES'
prior.BATCH.mkdir(exist_ok=True)
context = prior.BATCH / 'OWNER_CONTEXT.json'
if not context.exists():
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    assigned = {r['Video'] for r in rows}
    selected = sorted(p.name for p in ROOT.glob('20261010_*.MP4') if p.name not in assigned)
    prior.save(context, {
        'requested_utc': datetime.now(timezone.utc).isoformat(),
        'owner_request': 'Uploaded new videos to be processed. I believe all the newest ones are against humans and should be logged in the pause logs',
        'selected_sources': selected,
        'excluded_existing_assignments': [r for r in rows if r['Video'].startswith('20261009') and r['Status'] == 'In progress'],
        'requested_log': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
        'classification_rule': 'Visible Auto option, even OFF, means computer; no external human entry.',
        'scope': 'Only these newly requested sources. Full review, Pause Games supplement, independent acceptance, verified external log and archive.',
        'lead_only_shared_writes': True})
    prior.save(prior.BATCH / 'INDEX_BEFORE.json', rows)
selected = json.loads(context.read_text(encoding='utf-8'))['selected_sources']
print(json.dumps({'frozen_selection': selected}), flush=True)
for name in selected:
    prior.intake(name)

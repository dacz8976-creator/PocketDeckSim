"""Intake only the three new sources requested October 11, 2026."""
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import intake_pause_batch_20261006 as prior

ROOT = Path(__file__).resolve().parent.parent
prior.BATCH = ROOT / 'Recording_QA/BATCH_2026-10-11_NEW_PAUSE_GAMES'
prior.BATCH.mkdir(exist_ok=True)
context = prior.BATCH / 'OWNER_CONTEXT.json'
if not context.exists():
    rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
    assigned = {r['Video'] for r in rows}
    selected = sorted(p.name for p in ROOT.glob('20261012_*.MP4') if p.name not in assigned)
    prior.save(context, {
        'requested_utc': datetime.now(timezone.utc).isoformat(),
        'owner_request': 'Uploaded some new pause game logs for review',
        'selected_sources': selected,
        'requested_log': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
        'classification_rule': 'Visible Auto option, even OFF, means computer; exclude from both external human logs.',
        'scope': 'Only these newly uploaded sources. Full review, mandatory Pause Games supplement, independent acceptance, verified external logging and archival.',
        'lead_only_shared_writes': True})
    prior.save(prior.BATCH / 'INDEX_BEFORE.json', rows)
selected = json.loads(context.read_text(encoding='utf-8'))['selected_sources']
print(json.dumps({'frozen_selection': selected}), flush=True)
for name in selected:
    prior.intake(name)

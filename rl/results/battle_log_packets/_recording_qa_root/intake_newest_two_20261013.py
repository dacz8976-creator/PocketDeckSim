"""Lead intake restricted to the two latest owner-requested uploads."""
import argparse
import csv
from datetime import datetime, timezone
import intake_pause_batch_20261006 as base

NAMES = ['20261013_022530000_iOS.MP4', '20261013_030351000_iOS.MP4']
parser = argparse.ArgumentParser()
parser.add_argument('--video', choices=NAMES)
parser.add_argument('--initialize-only', action='store_true')
args = parser.parse_args()
base.BATCH = base.ROOT / 'Recording_QA/BATCH_2026-10-13_NEWEST_TWO'
base.BATCH.mkdir(exist_ok=True)
if not (base.BATCH / 'OWNER_CONTEXT.json').exists():
    base.save(base.BATCH / 'OWNER_CONTEXT.json', {
        'requested_utc': datetime.now(timezone.utc).isoformat(),
        'owner_request': 'Uploaded two more videos; Give it a try now.',
        'selected_sources': NAMES,
        'selection_basis': 'The two newest root uploads by LastWriteTime, both later than the previous completed six-source batch.',
        'scope': 'Only these two newly requested sources. Whole-source review, mandatory Pause Games supplement when eligible, separate independent checks, lead acceptance, registration, verified external save and safe archival.',
        'requested_log': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
        'classification_rule': 'Any Auto option, even OFF, means computer; exclude computer games from both human logs.',
        'lead_only_shared_writes': True,
        'prior_batch': 'BATCH_2026-10-12_ADDITIONAL_TWO',
        'other_root_uploads': 'Outside this two-source request; do not resume older uploads or backlog.'})
    base.save(base.BATCH / 'INDEX_BEFORE.json', list(csv.DictReader((base.ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
if not args.initialize_only:
    for name in ([args.video] if args.video else NAMES):
        base.intake(name)

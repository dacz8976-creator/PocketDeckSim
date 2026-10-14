"""Bind only the two later uploads requested by the owner; serialized reads."""
import csv
import argparse
from datetime import datetime, timezone
import intake_pause_batch_20261006 as base

names = ['20261012_225319000_iOS.MP4', '20261012_230258000_iOS.MP4']
parser = argparse.ArgumentParser()
parser.add_argument('--video', choices=names)
args = parser.parse_args()
base.BATCH = base.ROOT / 'Recording_QA/BATCH_2026-10-12_ADDITIONAL_TWO'
base.BATCH.mkdir(exist_ok=True)
context = base.BATCH / 'OWNER_CONTEXT.json'
if not context.exists():
    base.save(context, {
        'requested_utc': datetime.now(timezone.utc).isoformat(),
        'owner_request': 'Yes please finish. There are actually two more videos as well.',
        'selected_sources': names,
        'requested_log': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
        'scope': 'Only the two newly added uploads. Complete full-source review, future Pause Games protocol, independent checks, safe archive and verified external save if eligible.',
        'classification_rule': 'Any visible Auto control, even OFF, means computer. Exclude computer games from both human logs.',
        'lead_only_shared_writes': True,
        'prior_batch': 'BATCH_2026-10-12_NEW_LONG_VIDEOS',
        'external_message_authorization': 'Owner explicitly approved finishing the prepared Pause Games import and requested these two further reviews in the same workflow.',
    })
    base.save(base.BATCH / 'INDEX_BEFORE.json', list(csv.DictReader((base.ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
for name in ([args.video] if args.video else names):
    base.intake(name)

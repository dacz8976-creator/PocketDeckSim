"""Bind only the new long source authorized on October 12. Serial media reads."""
import csv
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
import intake_pause_batch_20261006 as base

parser = argparse.ArgumentParser()
parser.add_argument('--video', choices=['20261012_010706000_iOS.MP4', '20261012_203719000_iOS.MP4', '20261012_210041000_iOS.MP4', '20261012_210823000_iOS.MP4'], default='20261012_010706000_iOS.MP4')
args = parser.parse_args()

base.BATCH = base.ROOT / 'Recording_QA/BATCH_2026-10-12_NEW_LONG_VIDEOS'
base.BATCH.mkdir(exist_ok=True)
context = base.BATCH / 'OWNER_CONTEXT.json'
if not context.exists():
    base.save(context, {
        'requested_utc': datetime.now(timezone.utc).isoformat(),
        'owner_request': 'Process the two newest fairly long videos; prior access issues should be resolved.',
        'selected_sources': ['20261012_010706000_iOS.MP4'],
        'second_source': None,
        'second_source_status': 'Awaiting filename: only one new root upload is visible; October 11 sources are completed.',
        'scope': 'Only the two newly requested long sources, with whole-file coverage and all contained games. Do not reopen accepted recordings or older backlog.',
        'classification_rule': 'Visible Auto option even OFF means computer and excludes external human logs. Confirm Pause Games versus ladder from filmed context.',
        'lead_only_shared_writes': True,
    })
    base.save(base.BATCH / 'INDEX_BEFORE.json', list(csv.DictReader((base.ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
base.intake(args.video)

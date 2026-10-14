"""Lead intake of the six October 13 UTC uploads explicitly requested next."""
import argparse
import csv
from datetime import datetime, timezone
import intake_pause_batch_20261006 as base

NAMES = ['20261013_010003000_iOS.MP4', '20261013_010837000_iOS.MP4',
         '20261013_014423000_iOS.MP4', '20261013_015011000_iOS.MP4',
         '20261013_015659000_iOS.MP4', '20261013_020824000_iOS.MP4']
parser = argparse.ArgumentParser()
parser.add_argument('--video', choices=NAMES)
parser.add_argument('--initialize-only', action='store_true')
args = parser.parse_args()
base.BATCH = base.ROOT / 'Recording_QA/BATCH_2026-10-13_REMAINING_SIX'
base.BATCH.mkdir(exist_ok=True)
if not (base.BATCH / 'OWNER_CONTEXT.json').exists():
    base.save(base.BATCH / 'OWNER_CONTEXT.json', {
        'requested_utc': datetime.now(timezone.utc).isoformat(),
        'owner_request': 'Finish the six remaining October 13 videos; all should now be downloaded.',
        'selected_sources': NAMES,
        'scope': 'Exactly these six unreviewed October 13 UTC filenames. Entire recordings and all games, individual packets, independent acceptance, lead registration, external logging when eligible and safe archive. Continue established Pause Games routing. Completed newest pair is excluded.',
        'requested_log': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
        'classification_rule': 'Any visible Auto option, even OFF, identifies computer and excludes both human logs.',
        'lead_only_shared_writes': True,
        'prior_completed_pair': 'BATCH_2026-10-13_NEWEST_TWO',
        'initial_availability': 'All six fully allocated, in-sync pinned cloud files; no download recovery needed.'})
    base.save(base.BATCH / 'INDEX_BEFORE.json', list(csv.DictReader((base.ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline=''))))
    (base.BATCH / 'README.md').write_text('# Six remaining October 13 UTC recordings\n\nAll six sources are downloaded and in sync. Full reviews, individual game packets, separate independent acceptance, live logging and archival are in progress. The already completed newest pair is excluded. Source filenames are preserved; actual local match dates will be qualified from metadata and footage.\n', encoding='utf-8')
if not args.initialize_only:
    for name in ([args.video] if args.video else NAMES):
        base.intake(name)

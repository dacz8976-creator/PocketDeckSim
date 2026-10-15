"""Lead-only current batch status, preserving the initial dated descriptions."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
for name in ['README.md', 'REVIEW_ROLES.json']:
    previous = BATCH / (name + '.before_review_progress')
    if not previous.exists():
        shutil.copy2(BATCH / name, previous)
roles = json.loads((BATCH / 'REVIEW_ROLES.json').read_text(encoding='utf-8-sig'))
roles['updated_utc'] = datetime.now(timezone.utc).isoformat()
for entry in roles['sources']:
    stem = Path(entry['source']).stem
    suffix = '225319' if '225319' in stem else '230258'
    entry.update(primary_worker='/root/later_' + suffix,
                 independent_worker='/root/check_later_' + suffix,
                 primary_model='gpt-6.1-sol', primary_effort='high',
                 independent_model='gpt-6.1-sol', independent_effort='high',
                 source_download_pending=False)
    entry['current_status'] = ('accepted_registered_archived_and_live_verified'
                               if suffix == '225319' else 'full_review_and_independent_checks_in_progress')
(BATCH / 'REVIEW_ROLES.json').write_text(json.dumps(roles, indent=2) + '\n', encoding='utf-8')
(BATCH / 'README.md').write_text('''# Two further October 12 recordings

Both source downloads are complete and hash-bound. The first, 20261012_225319000_iOS.MP4, has a complete nine-turn review, separate independent acceptance, lead acceptance, immutable registration and hash-verified archival. Its owner-concession loss versus Job is saved in Pause Games and verified after reload at 44 games, 25 wins, 19 losses and 15 concession wins. All prior 43 entries are unchanged. Storage release verification is pending.

The second, 20261012_230258000_iOS.MP4, is undergoing its full review and separate independent source checks. Its registration, archival and external save remain pending.

Download attempts and two graceful OneDrive recovery records are retained. No older paused recording is included. The earlier four-source batch is complete locally and online. LIVE_BASELINE.json preserves its fresh 43-game baseline. LIVE_DECK_SNAPSHOT.json preserves the exact 20-card Darkness list; each new source establishes its own filmed deck match.
''', encoding='utf-8')
print('Current batch progress and actual reviewer roles saved.')

"""Reconcile this pass without treating blocked downloads as reviewed media."""
import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
RUN = ROOT / 'Recording_QA/RESUME_2026-10-15_FIVE'
DONE = ['20261016_024253000_iOS.MP4', '20261016_030833000_iOS.MP4']
TAG = 'two_available'

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def digest(path):
    assert path.suffix.lower() not in ['.mp4', '.mov', '.mkv']
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--mirror', action='store_true')
args = parser.parse_args()
context = load(RUN / 'OWNER_CONTEXT.json')
if args.mirror:
    status = load(RUN / ('RESUME_STATUS.' + TAG + '.json'))
    assert status['completed_this_pass'] == DONE
    boss = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder')
    folders = [ROOT / 'Recording_QA/BATCH_2026-10-15_NIGHT_LADDER_FOUR',
               ROOT / 'Recording_QA/BATCH_2026-10-15_FINAL_LADDER_TWO', RUN]
    copies = []
    for folder in folders:
        for path in sorted(p for p in folder.rglob('*') if p.is_file() and p.name != 'MIRROR_RECEIPT.' + TAG + '.json'):
            target = boss / folder.name / path.relative_to(folder)
            sha = digest(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert digest(target) == sha, target
            else:
                shutil.copy2(path, target)
            assert digest(target) == sha
            copies.append({'source': str(path), 'destination': str(target), 'sha256': sha, 'bytes': path.stat().st_size})
    folder = ROOT / 'Recording_QA/LOCAL_DOWNLOAD_RESUME_20261015'
    for path in sorted(p for p in folder.rglob('*') if p.is_file()):
        target = boss / RUN.name / 'local_download_receipts' / path.relative_to(folder)
        target.parent.mkdir(parents=True, exist_ok=True)
        sha = digest(path)
        if target.exists():
            assert digest(target) == sha, target
        else:
            shutil.copy2(path, target)
        assert digest(target) == sha
        copies.append({'source': str(path), 'destination': str(target), 'sha256': sha, 'bytes': path.stat().st_size})
    receipt = RUN / ('MIRROR_RECEIPT.' + TAG + '.json')
    save(receipt, {'created_utc': datetime.now(timezone.utc).isoformat(), 'all_hashes_verified': True,
        'videos_copied': 0, 'complete_new_reviews': 2, 'unreadable_sources_pending': 3,
        'file_count': len(copies), 'files': copies})
    target = boss / RUN.name / receipt.name
    shutil.copy2(receipt, target)
    assert digest(receipt) == digest(target)
    print(json.dumps({'mirrored_files': len(copies), 'all_hashes_verified': True}))
    raise SystemExit(0)

live = load(RUN / ('LIVE_SAVE_VERIFICATION.' + TAG + '.json'))
assert live['fresh_reload_verified'] and live['all_exact_rows_verified']
assert live['verified_entry_count'] == 2 and live['prior_source_notes_preserved_exactly_once'] == 29
assert live['verified_totals'] == {'wins': 13, 'losses': 18, 'games': 31}
assert (RUN / ('LADDER_SAVED_PROOF.' + TAG + '.png')).is_file()
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
current = {row['Video']: row for row in rows}
baseline = load(RUN / 'INDEX_BEFORE.json')
unrelated = [row for row in baseline if row['Video'] not in context['selected_sources']]
assert all(current[row['Video']] == row for row in unrelated)
locations = load(ROOT / 'MEDIA_LOCATIONS.json')['moved']
states = []
for name in context['selected_sources']:
    packet = Path(context['packets'][name])
    if name not in DONE:
        assert not (packet / 'SOURCE.json').exists()
        assert name not in current
        cloud = metadata(ROOT / name)
        states.append({'source': name, 'review_complete': False, 'external_saved': False,
            'cloud_metadata': cloud, 'sha256': None, 'duration_seconds': None,
            'remaining': 'Local OneDrive download/readability, source binding, full review, independent acceptance, live log/readback, archive.',
            'blocker': 'Cloud-file access denied; full normal local read also failed. No source identity or review claim.'})
        continue
    source = load(packet / 'SOURCE.json')
    assert load(packet / 'LEAD_ACCEPTANCE.json')['accepted']
    assert load(packet / 'independent_sol/CHECK_RESULT.json')['accepted']
    assert load(packet / 'REGISTRATION_RESULT.json')['exit_code'] == 0
    assert load(packet / 'EXTERNAL_SAVE_STATUS.json')['fresh_reload_verified']
    for rel, sha in load(packet / 'REVIEW_PACKET_HASHES.json')['files'].items():
        assert digest(packet / rel) == sha, rel
    receipt = load(packet / ('MOVE_RECEIPT.' + name + '.json'))
    assert receipt['identity_match'] and receipt['sha256_before'] == receipt['sha256_after'] == source['sha256']
    archive = ROOT / 'Reviewed' / name
    assert archive.is_file() and archive.stat().st_size == source['bytes'] and not (ROOT / name).exists()
    assert current[name]['Status'] == 'Reviewed' and current[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
    location = next(e for e in locations if e['filename'] == name)
    assert Path(location['current_path']).resolve() == archive.resolve() and location['sha256'] == source['sha256']
    cloud = metadata(archive)
    entry = load(packet / 'LADDER_ENTRY.json')
    states.append({'source': name, 'review_complete': True, 'independently_accepted': True, 'registered': True,
        'archived': True, 'external_saved': True, 'fresh_reload_verified': True, 'sha256': source['sha256'],
        'result': entry['result'], 'opponent': entry['opponent'], 'cloud_metadata': cloud,
        'storage_complete': cloud['in_sync'] and cloud['online_only'] and cloud['allocated_bytes'] == 0})
pending = [n for n in context['selected_sources'] if n not in DONE]
status = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'selected_sources_count': 5,
    'completed_this_pass': DONE, 'already_completed_prior_source': context['already_completed_prior_source'],
    'combined_six_sources_complete': False, 'review_pending': pending, 'download_pending': pending,
    'states': states, 'live_verified_totals': live['verified_totals'], 'deck01_totals': live['deck01_totals'],
    'unrelated_index_rows_preserved': len(unrelated), 'prior_current_season_notes_preserved': 29,
    'chrome_downloads_used_this_pass': False, 'videos_deleted': 0,
    'storage_pending': [s['source'] for s in states if s['review_complete'] and not s['storage_complete']],
    'pending_question': 'Owner asked whether OneDrive tray shows paused sync or an error; no response yet.'}
save(RUN / ('RESUME_STATUS.' + TAG + '.json'), status)
with (RUN / ('README.' + TAG + '.md')).open('x', encoding='utf-8') as f:
    f.write('# Local OneDrive continuation\n\n')
    f.write('Two more recordings are completely reviewed, independently and lead accepted, registered, hash-verified in Reviewed, and saved exactly once in the live Ladder Log after reload.\n\n')
    f.write('- 20261016_024253000_iOS.MP4: win3-2 versus 暗黑掌門人; first,19turns,540damage. Heavy Helmet preserves Kingambit10HP before final180damage.\n')
    f.write('- 20261016_030833000_iOS.MP4: loss versus アヤカ; second,10turns. Last observed score0-2; ending cause unshown.\n\n')
    f.write('Season totals verified13wins,18losses,31games. Deck01:5wins,2losses. All29prior current-season notes and unrelated index rows are preserved.\n\n')
    f.write('The previously completed020517win remains intact, so three of the six requested recordings are complete. Pending:015753,020806,031512. Local OneDrive downloads were allowed sustained attempts; two files became fully readable. The remaining three returned Windows cloud-file access denied, and a normal full local read also failed. They have no SHA256/duration/review claim. Originals remain preserved, pinned for download. No Chrome download was used in this pass.\n\n')
    f.write('Accepted videos were not deleted. Local cache release was requested; final metadata is in RESUME_STATUS.two_available.json. Historical pending-download checkpoints remain intact.\n')
print(json.dumps({'completed_this_pass': 2, 'download_pending': 3, 'live_totals': live['verified_totals'],
    'storage_pending': status['storage_pending']}))

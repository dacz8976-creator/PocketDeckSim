"""Verify the accepted short game and preserve the three download blockers."""
import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-15_NIGHT_LADDER_FOUR'
NAMES = ['20261016_015753000_iOS.MP4', '20261016_020517000_iOS.MP4',
         '20261016_020806000_iOS.MP4', '20261016_024253000_iOS.MP4']
DONE = NAMES[1]

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
if args.mirror:
    checkpoint = BATCH / 'CHECKPOINT_020517.json'
    assert load(checkpoint)['completed_sources'] == [DONE]
    target_root = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder') / BATCH.name
    target_root.mkdir(parents=True, exist_ok=True)
    paths = sorted(p for p in BATCH.rglob('*') if p.is_file() and p.name != 'MIRROR_CHECKPOINT_020517.json')
    copied = []
    for path in paths:
        sha = digest(path)
        rel = path.relative_to(BATCH)
        target = target_root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert digest(target) == sha, target
        else:
            shutil.copy2(path, target)
        assert digest(target) == sha
        copied.append({'path': rel.as_posix(), 'sha256': sha, 'bytes': path.stat().st_size})
    receipt_path = BATCH / 'MIRROR_CHECKPOINT_020517.json'
    save(receipt_path, {'created_utc': datetime.now(timezone.utc).isoformat(), 'source': str(BATCH),
        'destination': str(target_root), 'all_hashes_verified': True, 'videos_copied': 0,
        'batch_complete': False, 'files': copied, 'file_count': len(copied)})
    shutil.copy2(receipt_path, target_root / receipt_path.name)
    assert digest(receipt_path) == digest(target_root / receipt_path.name)
    print(json.dumps({'mirrored_files': len(copied), 'all_hashes_verified': True, 'batch_complete': False}))
    raise SystemExit(0)

packet = BATCH / Path(DONE).stem
source = load(packet / 'SOURCE.json')
assert load(packet / 'LEAD_ACCEPTANCE.json')['accepted']
assert load(packet / 'independent_sol/CHECK_RESULT.json')['accepted']
assert load(packet / 'REGISTRATION_RESULT.json')['exit_code'] == 0
for rel, sha in load(packet / 'REVIEW_PACKET_HASHES.json')['files'].items():
    assert digest(packet / rel) == sha, rel
move = load(packet / ('MOVE_RECEIPT.' + DONE + '.json'))
assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
archived = ROOT / 'Reviewed' / DONE
assert archived.is_file() and not (ROOT / DONE).exists() and archived.stat().st_size == source['bytes']
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    current = {row['Video']: row for row in csv.DictReader(f)}
assert current[DONE]['Status'] == 'Reviewed'
assert current[DONE]['Location'].replace('\\', '/') == 'Reviewed/' + DONE
baseline = load(BATCH / 'INDEX_BEFORE.json')
assert all(current[row['Video']] == row for row in baseline if row['Video'] not in NAMES)
location = next(e for e in load(ROOT / 'MEDIA_LOCATIONS.json')['moved'] if e['filename'] == DONE)
assert Path(location['current_path']).resolve() == archived.resolve() and location['sha256'] == source['sha256']
live = load(BATCH / 'LIVE_SAVE_VERIFICATION_020517.json')
assert live['fresh_reload_verified'] and live['all_exact_rows_verified']
assert live['verified_entry_count'] == 1 and live['prior_source_notes_preserved_exactly_once'] == 28
assert live['verified_totals'] == {'wins': 12, 'losses': 17, 'games': 29}
states = []
for name in NAMES:
    done = name == DONE
    cloud = metadata(archived if done else ROOT / name)
    states.append({'source_filename': name, 'review_complete': done, 'independently_accepted': done,
        'lead_accepted': done, 'registered_complete': done, 'archived': done,
        'external_saved_and_reloaded': done, 'source_sha256': source['sha256'] if done else None,
        'duration_seconds': source['duration_seconds'] if done else None, 'cloud_metadata': cloud,
        'storage_complete': done and cloud['in_sync'] and cloud['online_only'] and cloud['allocated_bytes'] == 0,
        'remaining': 'OneDrive cache release pending' if done else 'Download readable bytes, verify identity/duration, full review, independent acceptance, live log/readback and archive'})
save(BATCH / 'CHECKPOINT_020517.json', {'checked_utc': datetime.now(timezone.utc).isoformat(),
    'requested_sources': NAMES, 'requested_count': 4, 'batch_complete': False, 'completed_sources': [DONE],
    'pending_sources': [n for n in NAMES if n != DONE], 'states': states,
    'live_totals': live['verified_totals'], 'prior_entries_preserved': 28,
    'original_media_read_during_checkpoint': False, 'videos_deleted': 0,
    'blockers': ['OneDrive client exits and bounded hydration attempts timed out for three sources.',
        'Browser download attempted on OneDrive but no readable file was found locally.',
        'Chrome internal Downloads URL denied by URL security policy; further download-control access rejected by automatic approval review.',
        'User approval to return to normal OneDrive download buttons requested; awaiting response.']})
with (BATCH / 'CHECKPOINT_020517.md').open('x', encoding='utf-8') as f:
    f.write('# Four new ladder videos: checkpoint\n\n')
    f.write('One of four recordings is complete. 20261016_020517000_iOS.MP4 is a ranked win versus つちのこ by explicit opponent concession at0-0. Went second,4turns,0damage, no owner attacks. Full review, separate independent acceptance, lead acceptance, completion registration and hash-verified archive are saved. The source is preserved in Reviewed.\n\n')
    f.write('The live Ladder Log contains the source exactly once, verified after reload. Season totals are12wins,17losses,29games. Deck01 is4wins,1loss. All28 earlier current-season notes remain unchanged.\n\n')
    f.write('The other three sources remain pending unreadable downloads. No hash, duration or visual-review claim is made for them. Original cloud placeholders are preserved. Normal OneDrive browser download controls await owner approval after automatic approval review blocked further download-control access.\n\n')
    f.write('Local cache release for the completed source was requested but remains pending. No videos were deleted. CHECKPOINT_020517.json contains exact per-source state and remaining work.\n')
print(json.dumps({'completed': 1, 'download_pending': 3, 'live_totals': live['verified_totals']}))

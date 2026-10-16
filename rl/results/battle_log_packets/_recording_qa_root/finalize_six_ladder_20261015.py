"""Verify all six requested results, source archives and final local reports."""
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
GROUPS = {
    'BATCH_2026-10-15_NIGHT_LADDER_FOUR': ['20261016_015753000_iOS.MP4', '20261016_020517000_iOS.MP4', '20261016_020806000_iOS.MP4', '20261016_024253000_iOS.MP4'],
    'BATCH_2026-10-15_FINAL_LADDER_TWO': ['20261016_030833000_iOS.MP4', '20261016_031512000_iOS.MP4'],
}

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
    assert load(RUN / 'SIX_GAME_COMPLETION.json')['review_and_ladder_logging_complete']
    boss = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder')
    folders = [ROOT / 'Recording_QA' / key for key in GROUPS] + [RUN]
    copies = []
    for folder in folders:
        for path in sorted(p for p in folder.rglob('*') if p.is_file() and p.name != 'MIRROR_RECEIPT.all_six.json'):
            sha = digest(path)
            target = boss / folder.name / path.relative_to(folder)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                assert digest(target) == sha, target
            else:
                shutil.copy2(path, target)
            assert digest(target) == sha
            copies.append({'source': str(path), 'destination': str(target), 'sha256': sha, 'bytes': path.stat().st_size})
    receipt = RUN / 'MIRROR_RECEIPT.all_six.json'
    save(receipt, {'created_utc': datetime.now(timezone.utc).isoformat(), 'all_hashes_verified': True,
        'file_count': len(copies), 'videos_copied': 0, 'completed_source_count': 6, 'files': copies})
    shutil.copy2(receipt, boss / RUN.name / receipt.name)
    assert digest(receipt) == digest(boss / RUN.name / receipt.name)
    print(json.dumps({'mirrored_files': len(copies), 'all_hashes_verified': True}))
    raise SystemExit(0)

live = load(RUN / 'LIVE_SAVE_VERIFICATION.all_five.json')
assert live['fresh_reload_verified'] and live['all_exact_rows_verified'] and live['verified_entry_count'] == 5
assert live['prior_source_notes_preserved_exactly_once'] == 29 and live['verified_totals']['games'] == 34
assert (RUN / 'LADDER_SAVED_PROOF.all_five.png').is_file()
assert load(RUN / 'DOWNLOAD_RESOLUTION.json')['download_blockers_resolved']
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as f:
    current = {row['Video']: row for row in csv.DictReader(f)}
baseline = load(RUN / 'INDEX_BEFORE.json')
selected = {name for names in GROUPS.values() for name in names}
unrelated = [row for row in baseline if row['Video'] not in selected]
assert all(current[row['Video']] == row for row in unrelated)
locations = load(ROOT / 'MEDIA_LOCATIONS.json')['moved']
raw = (RUN / 'LADDER_RELOAD.all_five.txt').read_text(encoding='utf-8')
states = []
for group, names in GROUPS.items():
    for name in names:
        packet = ROOT / 'Recording_QA' / group / Path(name).stem
        source = load(packet / 'SOURCE.json')
        primary = load(packet / 'SUMMARY.json')
        acceptance = load(packet / 'LEAD_ACCEPTANCE.json')
        check = load(packet / 'independent_sol/CHECK_RESULT.json')
        registration = load(packet / 'REGISTRATION_RESULT.json')
        assert source['video_basename'] == primary['source_filename'] == check['source_filename'] == name
        assert source['sha256'] == primary['source_sha256'] == check['source_sha256']
        assert acceptance['accepted'] and acceptance['archive_eligible'] and check['accepted']
        assert primary['battle_complete'] and primary['match_count'] == 1 and registration['exit_code'] == 0
        assert check['frozen_manifest_sha256'] == digest(packet / 'REVIEW_PACKET_HASHES.json')
        raw_files = load(packet / 'REVIEW_PACKET_HASHES.json')['files']
        primary_hashes = {item['path']: item['sha256'] for item in raw_files} if isinstance(raw_files, list) else raw_files
        assert len(primary_hashes) == len(raw_files)
        for rel, sha in primary_hashes.items():
            evidence_path = (packet / rel).resolve()
            assert evidence_path.is_relative_to(packet.resolve()) and digest(evidence_path) == sha, rel
        event = load(Path(registration['stdout'].strip()))
        assert event['status'] == 'full_battle_review_complete' and event['video_sha256'] == source['sha256']
        move = load(packet / ('MOVE_RECEIPT.' + name + '.json'))
        assert move['identity_match'] and move['sha256_before'] == move['sha256_after'] == source['sha256']
        archive = ROOT / 'Reviewed' / name
        assert archive.is_file() and archive.stat().st_size == source['bytes'] and not (ROOT / name).exists()
        assert current[name]['Status'] == 'Reviewed' and current[name]['Location'].replace('\\', '/') == 'Reviewed/' + name
        match = [e for e in locations if e['filename'] == name]
        assert len(match) == 1 and Path(match[0]['current_path']).resolve() == archive.resolve()
        assert match[0]['sha256'] == source['sha256']
        entry = load(packet / 'LADDER_ENTRY.json')
        assert load(packet / 'EXTERNAL_SAVE_STATUS.json')['fresh_reload_verified']
        assert raw.count(name) == 1 and raw.count(entry['note']) == 1
        cloud = metadata(archive)
        states.append({'source': name, 'group': group, 'source_sha256': source['sha256'],
            'result': entry['result'], 'opponent': entry['opponent'], 'review_complete': True,
            'independently_accepted': True, 'registered': True, 'archived': True,
            'external_saved_and_reloaded': True, 'cloud_metadata': cloud,
            'storage_complete': cloud['in_sync'] and cloud['online_only'] and cloud['allocated_bytes'] == 0})
now = datetime.now(timezone.utc).isoformat()
storage_pending = [s['source'] for s in states if not s['storage_complete']]
status = {'checked_utc': now, 'requested_games': 6, 'review_and_ladder_logging_complete': True,
    'all_source_archives_verified': True, 'download_pending': [], 'review_pending': [], 'external_pending': [],
    'live_verified_current_season': live['verified_totals'], 'deck01_totals': live['deck01_totals'],
    'sources': states, 'storage_pending': storage_pending, 'videos_deleted': 0,
    'original_media_read_during_final_verification': False, 'unrelated_index_rows_preserved': len(unrelated),
    'prior_29_current_season_notes_preserved': True, 'transient_download_error_cause': 'unconfirmed',
    'download_resolution': 'DOWNLOAD_RESOLUTION.json', 'live_proof': live['proof_image']}
save(RUN / 'SIX_GAME_COMPLETION.json', status)
for group, names in GROUPS.items():
    save(ROOT / 'Recording_QA' / group / 'BATCH_COMPLETION.json', {
        'checked_utc': now, 'requested_games': len(names), 'review_and_ladder_logging_complete': True,
        'archive_complete': True, 'sources': [s for s in states if s['source'] in names],
        'review_pending': [], 'external_pending': [], 'storage_pending': [n for n in storage_pending if n in names],
        'combined_live_verification': str(RUN / 'LIVE_SAVE_VERIFICATION.all_five.json')})
report = '# Six requested ladder videos complete\n\n'
report += 'All six sources have full reviews, separate independent acceptance, lead acceptance, completion registration, hash-verified archives and reload-verified Ladder Log entries. Earlier pending-download checkpoints are historical; DOWNLOAD_RESOLUTION.json supersedes their blockers.\n\n'
for state in states:
    report += f"- {state['source']}: {state['result']} versus {state['opponent']}.\n"
report += f"\nVerified season total: {live['verified_totals']['wins']} wins, {live['verified_totals']['losses']} losses, 34 games. Deck 01: {live['deck01_totals']['wins']} wins and {live['deck01_totals']['losses']} losses. All 29 earlier current-season entries remain unchanged, including 020517.\n\n"
report += 'All original media are preserved in Reviewed. Frozen SOURCE paths retain the review-time location; MEDIA_LOCATIONS.json and move receipts resolve current paths. No videos were deleted. Exact decks, hidden information and any source-specific limits remain qualified in the individual reviews.\n\n'
report += 'The formerly incomplete downloads became readable during checks. The temporary cloud-file access error cause remains unconfirmed; no pause, restart or browser download is established as necessary.\n\n'
report += ('Local OneDrive space release remains pending for: ' + ', '.join(storage_pending) + '.\n' if storage_pending else 'All six originals are in sync and online-only with zero local allocated bytes.\n')
with (RUN / 'COMPLETE_SIX_GAMES.md').open('x', encoding='utf-8') as f:
    f.write(report)
print(json.dumps({'completed_sources': 6, 'live_totals': live['verified_totals'], 'storage_pending': storage_pending}))

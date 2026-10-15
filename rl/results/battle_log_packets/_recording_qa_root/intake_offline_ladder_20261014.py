"""Preserve complete Downloads sources while OneDrive is unavailable."""
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'
DOWNLOADS = Path('C:/Users/dacz8/Downloads')
NAMES = ['20261014_160506000_iOS.MP4', '20261014_161324000_iOS.MP4',
         '20261014_163325000_iOS.MP4', '20261014_164328000_iOS.MP4']
PROBE = 'C:/Program Files/MiniTool Screen Recorder/FFmpeg/ffprobe.exe'
CLI = ROOT / 'Review_Log/review_log.py'


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


# Meaningful CLI checks use disposable fixture roots, never the owner index.
with tempfile.TemporaryDirectory(prefix='ladder-offline-cli-', dir=ROOT / 'Recording_QA') as temporary:
    trial = Path(temporary)
    assert trial.resolve().is_relative_to((ROOT / 'Recording_QA').resolve())
    alternate = trial / 'local/video.MP4'
    alternate.parent.mkdir()
    alternate.write_bytes(b'offline fixture identity')
    test_root = trial / 'log'
    test_root.mkdir()
    common = [sys.executable, '-X', 'utf8', str(CLI), '--root', str(test_root), 'record',
              '--reviewer', 'offline-cli-check', '--status', 'in_progress', '--scope', 'Fixture only']
    good = subprocess.run(common + ['--video', 'video.MP4', '--source-path', str(alternate)], capture_output=True, text=True)
    assert good.returncode == 0, good.stderr
    event = json.loads(Path(good.stdout.strip()).read_text(encoding='utf-8'))
    assert event['video_sha256'] == digest(alternate) and event['video_path_at_record'] == str(alternate.resolve())
    assert event['video_location_at_record'] == 'offline_local'
    event_count = len(list((test_root / 'Review_Log/events').glob('*.json')))
    bad = subprocess.run(common + ['--video', 'different.MP4', '--source-path', str(alternate)], capture_output=True, text=True)
    assert bad.returncode != 0 and len(list((test_root / 'Review_Log/events').glob('*.json'))) == event_count
    legacy = test_root / 'legacy.MP4'
    legacy.write_bytes(b'legacy fixture identity')
    ordinary = subprocess.run(common + ['--video', legacy.name], capture_output=True, text=True)
    assert ordinary.returncode == 0, ordinary.stderr
    assert json.loads(Path(ordinary.stdout.strip()).read_text())['video_location_at_record'] == 'main'

BATCH.mkdir(exist_ok=True)
inbox = ROOT / 'Offline_Inbox'
inbox.mkdir(exist_ok=True)
archive = ROOT / 'Offline_Reviewed'
archive.mkdir(exist_ok=True)
assignment = ROOT / 'Recording_QA/BATCH_2026-10-14_LADDER_RESUME_FIVE/REVIEW_ASSIGNMENT.md'
if not (BATCH / 'REVIEW_ASSIGNMENT.md').exists():
    shutil.copy2(assignment, BATCH / 'REVIEW_ASSIGNMENT.md')
index = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
if not (BATCH / 'OWNER_CONTEXT.json').exists():
    save(BATCH / 'INDEX_BEFORE.json', index)
    save(BATCH / 'OWNER_CONTEXT.json', {'utc': datetime.now(timezone.utc).isoformat(),
         'owner_instruction': 'Newest videos downloaded into Downloads. Save work locally in Battle Logs while OneDrive is down; reconcile with OneDrive later.',
         'selected_sources': NAMES, 'expected_routing': 'Same Ladder Log and three-item note contract as previous six games.',
         'canonical_cloud_sources_unverified': True, 'downloads_originals_must_be_preserved': True,
         'archive_location': str(archive), 'boss_folder_mirror': 'Deferred by owner offline staging instruction',
         'source_copy_and_cloud_reconciliation': 'Local source identity verified now. Existing cloud placeholders are preserved and unverified until sync returns.'})
    save(BATCH / 'OFFLINE_CLI_CHECKS.json', {'passed': True, 'checks': ['Explicit source path hashes correct local bytes and records real location',
         'Mismatched basename rejected without event mutation', 'Normal main-file registration still works'], 'real_index_used_for_checks': False})
inventory = []
for name in NAMES:
    packet = BATCH / Path(name).stem
    packet.mkdir(exist_ok=True)
    if (packet / 'SOURCE.json').exists():
        inventory.append(json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig')))
        continue
    original = DOWNLOADS / name
    assert original.is_file(), f'Not downloaded yet: {original}'
    assert not any(r['Video'] == name for r in index), f'Existing index assignment: {name}'
    local = inbox / name
    assert not local.exists() and not (archive / name).exists(), f'Collision: {name}'
    before = original.stat()
    expected_cloud_size = (ROOT / name).stat().st_size
    assert before.st_size == expected_cloud_size and before.st_size > 0
    original_hash = digest(original)
    after = original.stat()
    assert (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    shutil.copy2(original, local)
    assert digest(local) == original_hash
    probe = json.loads(subprocess.run([PROBE, '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(local)],
                                     capture_output=True, text=True, check=True, timeout=45).stdout)
    save(packet / 'PROBE.json', probe)
    save(packet / 'COPY_RECEIPT.json', {'copied_utc': datetime.now(timezone.utc).isoformat(), 'from': str(original), 'to': str(local),
         'bytes': before.st_size, 'sha256_original': original_hash, 'sha256_local_copy': original_hash,
         'identity_match': True, 'original_preserved': True, 'canonical_cloud_copy_not_read': True,
         'canonical_cloud_logical_size_matches': True})
    reviewer = '/root/offline_ladder_' + name[9:15]
    registered = subprocess.run([sys.executable, '-X', 'utf8', str(CLI), 'record', '--video', name, '--source-path', str(local),
          '--reviewer', reviewer, '--status', 'in_progress', '--scope', 'Full new ladder recording: setup, every turn, result and exact note fields.',
          '--notes', 'Owner authorized local Downloads copies while OneDrive is down. Local staging copy verified identical; existing cloud placeholder remains unverified. No older backlog.'],
          capture_output=True, text=True, encoding='utf-8', timeout=90)
    assert registered.returncode == 0, registered.stderr
    event = json.loads(Path(registered.stdout.strip()).read_text(encoding='utf-8'))
    assert event['video_sha256'] == original_hash
    save(packet / 'ASSIGNMENT_REGISTRATION.json', {'exit_code': 0, 'stdout': registered.stdout, 'stderr': registered.stderr})
    binding = {'video_basename': name, 'sha256': original_hash, 'bytes': before.st_size,
         'duration_seconds': float(probe['format']['duration']), 'source_path_at_review': str(local),
         'download_original': str(original), 'canonical_cloud_placeholder': str(ROOT / name),
         'canonical_cloud_copy_verified': False, 'source_creation_utc': probe['format'].get('tags', {}).get('creation_time'),
         'bound_utc': event['logged_at_utc'], 'identity_provenance': event['identity_provenance'], 'recording_relationships': [],
         'packet': str(packet)}
    save(packet / 'SOURCE.json', binding)
    save(packet / 'ASSIGNMENT.json', {'reviewer': reviewer, 'model': 'gpt-6.1-sol', 'reasoning_effort': 'high',
         'source_sha256': original_hash, 'assignment_event': event['event_id'], 'scope': 'Entire ordinary ladder battle; no Pause Games supplement.',
         'shared_write_authority': False, 'external_write_authority': False})
    inventory.append(binding)
    save(BATCH / 'SOURCE_INVENTORY.json', inventory)
    print(json.dumps({k: binding[k] for k in ['video_basename', 'sha256', 'bytes', 'duration_seconds', 'source_creation_utc', 'packet']}), flush=True)

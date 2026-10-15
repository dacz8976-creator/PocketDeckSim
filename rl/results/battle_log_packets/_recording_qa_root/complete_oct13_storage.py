"""Reconcile final cloud metadata and mirror only changed administrative files."""
import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / 'Recording_QA/BATCH_2026-10-13_REMAINING_SIX'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--mirror', action='store_true')
args = parser.parse_args()
changed = ['FINAL_STORAGE_CHECK.json', 'BATCH_COMPLETION_CHECK.json', 'README.md', 'REVIEW_ROLES.json']
storage = read(B / 'FINAL_STORAGE_CHECK.json')
assert storage['complete'] and storage['online_only'] == storage['videos'] == 6
assert all(e['after']['in_sync'] and e['after']['online_only'] and e['after']['allocated_bytes'] == 0 for e in storage['entries'])
assert all(e['source_contents_read'] is False for e in storage['entries'])

if not args.mirror:
    by_name = {e['video']: e['after'] for e in storage['entries']}
    check = read(B / 'BATCH_COMPLETION_CHECK.json')
    assert check['all_requested_local_reviews_complete'] and not check['external_saved']
    assert set(by_name) == {e['source'] for e in check['sources']}
    check['storage_checked_utc'] = storage['created_at_utc']
    check['storage_complete'] = True
    check['storage_online_only_count'] = 6
    check['storage_allocated_bytes'] = 0
    check['storage_receipt'] = 'FINAL_STORAGE_CHECK.json'
    check['storage_pending_reason'] = None
    for entry in check['sources']:
        entry['storage_online_only'] = True
        entry['storage_in_sync'] = True
        entry['storage_allocated_bytes'] = 0
    save(B / 'BATCH_COMPLETION_CHECK.json', check)
    roles = read(B / 'REVIEW_ROLES.json')
    roles['storage_updated_utc'] = storage['created_at_utc']
    for entry in roles['sources']:
        entry['status'] = 'accepted_registered_archived_external_pending_online_only'
    save(B / 'REVIEW_ROLES.json', roles)
    text = (B / 'README.md').read_text(encoding='utf-8')
    begin = text.index('OneDrive has not confirmed sync for every archived original.')
    end = text.index('\n', begin)
    text = text[:begin] + 'All six originals are in sync, online only and use zero local allocated video bytes.' + text[end:]
    text = text.replace('STORAGE_PENDING.json and the per-source', 'FINAL_STORAGE_CHECK.json and the per-source')
    text = text.replace('Written reviews and retained evidence are intended for the required Pocket Deck Lab/Boss Folder mirror; MIRROR_RECEIPT.json confirms its completion separately.', 'Written reviews and retained evidence are copied to the required Pocket Deck Lab/Boss Folder mirror. MIRROR_RECEIPT.json confirms matching copies.')
    (B / 'README.md').write_text(text, encoding='utf-8')
    print(json.dumps({'storage_complete': True, 'online_only': 6, 'allocated_bytes': 0, 'external_saved': False}))
else:
    receipt_path = B / 'MIRROR_RECEIPT.json'
    receipt = read(receipt_path)
    D = Path(receipt['destination']).resolve()
    boss = Path('C:/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder').resolve()
    assert D.parent == boss and D.name == B.name and D.is_dir()
    entries = {e['path']: e for e in receipt['files']}
    for name in changed:
        source = B / name
        destination = D / name
        shutil.copy2(source, destination)
        sha = digest(source)
        assert digest(destination) == sha
        entries[name] = {'path': name, 'bytes': source.stat().st_size, 'sha256': sha}
    all_paths = {p.relative_to(B).as_posix() for p in B.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name != 'MIRROR_RECEIPT.json'}
    assert all_paths == set(entries)
    receipt['updated_utc'] = datetime.now(timezone.utc).isoformat()
    receipt['incremental_update'] = {'changed_files': changed, 'copy_hashes_match': True, 'source_video_contents_read': False}
    receipt['file_count'] = len(entries)
    receipt['files'] = sorted(entries.values(), key=lambda e: e['path'])
    save(receipt_path, receipt)
    shutil.copy2(receipt_path, D / receipt_path.name)
    assert digest(receipt_path) == digest(D / receipt_path.name)
    print(json.dumps({'mirrored_files': len(entries), 'changed_files_verified': len(changed), 'copy_hashes_match': True}))

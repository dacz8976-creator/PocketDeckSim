import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BATCH = Path(__file__).resolve().parent

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def check(name):
    packet = BATCH / name
    receipt_dir = packet / 'independent_sol'
    receipt_dir.mkdir(exist_ok=True)
    frozen = packet / 'REVIEW_PACKET_HASHES.json'
    manifest = json.loads(frozen.read_text(encoding='utf-8-sig'))
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
    original = ROOT / source['video_basename']
    before = original.stat()
    source_hash = sha(original)
    after = original.stat()
    checked = []
    problems = []
    for entry in manifest['files']:
        p = packet / entry['path']
        actual = {'path': entry['path'], 'sha256': sha(p), 'bytes': p.stat().st_size}
        if 'dimensions' in entry:
            with Image.open(p) as im:
                actual['dimensions'] = list(im.size)
        actual['matches_frozen'] = all(actual[k] == entry[k] for k in ('sha256', 'bytes'))
        if 'dimensions' in entry:
            actual['matches_frozen'] &= actual['dimensions'] == entry['dimensions']
        if not actual['matches_frozen']:
            problems.append(entry['path'])
        checked.append(actual)
    evidence_manifest_checks = None
    ep = packet / 'EVIDENCE_MANIFEST.json'
    if ep.exists():
        em = json.loads(ep.read_text(encoding='utf-8-sig'))
        paths = {x['path']: x for x in checked}
        evidence_manifest_checks = []
        for entry in em['native_evidence']:
            p = packet / entry['path']
            with Image.open(p) as im:
                dims = list(im.size)
            valid = (entry['source_sha256'] == source_hash and dims == entry['dimensions']
                     and entry['path'] in paths and paths[entry['path']]['matches_frozen'])
            evidence_manifest_checks.append({'path': entry['path'], 'matches': valid})
            if not valid:
                problems.append('evidence_manifest:' + entry['path'])
    identity_ok = (before.st_size == after.st_size == source['bytes']
                   and before.st_mtime_ns == after.st_mtime_ns
                   and source_hash == source['sha256'] == manifest['source_sha256'])
    if not identity_ok:
        problems.append('source identity')
    record = {'checked_utc': datetime.now(timezone.utc).isoformat(),
              'source_path': str(original), 'source_sha256': source_hash,
              'source_bytes': after.st_size, 'source_stable_during_hash': before.st_mtime_ns == after.st_mtime_ns,
              'source_identity_matches': identity_ok,
              'frozen_manifest_path': str(frozen), 'frozen_manifest_sha256': sha(frozen),
              'evidence_manifest_sha256': sha(ep) if ep.exists() else None,
              'files_checked': checked, 'evidence_manifest_checks': evidence_manifest_checks,
              'all_frozen_entries_match': not problems, 'problems': problems}
    initial = receipt_dir / 'INTEGRITY_INITIAL.json'
    target = receipt_dir / ('INTEGRITY_FINAL.json' if initial.exists() else 'INTEGRITY_INITIAL.json')
    if target.exists():
        raise RuntimeError('Refusing to overwrite receipt: ' + str(target))
    target.write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(name, len(checked), 'frozen files; identity:', identity_ok, 'problems:', problems)

for name in ('20260926_211809000_iOS', '20260926_212155000_iOS'):
    check(name)

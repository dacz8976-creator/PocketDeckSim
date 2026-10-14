"""Preserve a same-session Camera Roll source while staging one review copy."""
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAMERA = Path(r'C:\Users\dacz8\OneDrive\Pictures\Camera Roll 1\2026\09')
BATCH = ROOT / 'Recording_QA' / 'BATCH_2026-09-30_EVENING'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('video', choices=['20261001_024952000_iOS.MP4', '20261001_030109000_iOS.MP4'])
    args = parser.parse_args()
    source = CAMERA / args.video
    destination = ROOT / args.video
    if destination.exists():
        raise SystemExit('Destination already exists; no overwrite performed')
    temp = BATCH / (args.video + '.copying')
    before = source.stat()
    digest = hashlib.sha256()
    with source.open('rb') as original, temp.open('xb') as output:
        while chunk := original.read(8 * 1024 * 1024):
            digest.update(chunk)
            output.write(chunk)
        output.flush()
        os.fsync(output.fileno())
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns) or temp.stat().st_size != before.st_size:
        raise RuntimeError('Source changed or copy size disagrees; staged copy retained without finalizing')
    with temp.open('rb') as check:
        copied_hash = hashlib.file_digest(check, 'sha256').hexdigest()
    if copied_hash != digest.hexdigest():
        raise RuntimeError('Copy digest mismatch')
    # Windows rename refuses an existing destination, including a concurrent sync arrival.
    temp.rename(destination)
    receipt = {'schema': 'battle-review-source-copy/v1', 'video': args.video, 'original_path': str(source), 'review_source_path': str(destination), 'bytes': before.st_size, 'source_sha256_read_during_copy': digest.hexdigest(), 'staged_copy_sha256': copied_hash, 'identity_match': True, 'original_preserved': True, 'independent_gameplay_observations': 1, 'copied_utc': datetime.now(timezone.utc).isoformat()}
    (BATCH / ('SOURCE_COPY.' + args.video + '.json')).write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt), flush=True)

if __name__ == '__main__':
    main()

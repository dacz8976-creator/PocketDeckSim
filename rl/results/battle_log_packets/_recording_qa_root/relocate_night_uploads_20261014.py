"""Move the two owner-identified misplaced uploads into the review inbox."""
import csv, json, shutil
from datetime import datetime, timezone
from pathlib import Path
from free_reviewed_video_space import metadata

ROOT = Path(__file__).resolve().parent.parent
ONEDRIVE = Path('C:/Users/dacz8/OneDrive').resolve()
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_NIGHT_LADDER_FOUR'
NAMES = ['20261015_021533000_iOS.MP4', '20261015_022206000_iOS.MP4']
rows = list(csv.DictReader((ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
assert not any(row['Video'] in NAMES for row in rows)
for name in NAMES:
    source = (ONEDRIVE / name).resolve()
    dest = (ROOT / name).resolve()
    assert source.parent == ONEDRIVE and dest.parent == ROOT.resolve()
    assert source.drive == dest.drive and source.is_file() and not dest.exists()
    assert not (ROOT / 'Reviewed' / name).exists()
    before = source.stat()
    assert before.st_ino != 0
    state_before = metadata(source)
    source.rename(dest)
    after = dest.stat()
    assert not source.exists()
    assert (before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns)
    packet = BATCH / Path(name).stem
    packet.mkdir(exist_ok=True)
    receipt = {'moved_utc':datetime.now(timezone.utc).isoformat(), 'source_filename':name, 'original_misplaced_path':str(source), 'current_path':str(dest), 'operation':'Same-volume atomic rename into Battle Logs', 'file_id_before':before.st_ino, 'file_id_after':after.st_ino, 'bytes_before':before.st_size, 'bytes_after':after.st_size, 'mtime_ns_before':before.st_mtime_ns, 'mtime_ns_after':after.st_mtime_ns, 'file_identity_and_metadata_unchanged':True, 'metadata_before':state_before, 'metadata_after':metadata(dest), 'content_sha256':None, 'hash_limit':'Content hash not claimed by relocation; readable source SHA256 must be established by intake before review.', 'destination_collision':False}
    (packet / 'INTAKE_RELOCATION_RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'moved':name, 'file_identity_and_metadata_unchanged':True}), flush=True)
context_path = BATCH / 'OWNER_CONTEXT.json'
shutil.copy2(context_path, BATCH / 'OWNER_CONTEXT.before_relocation.json')
context = json.loads(context_path.read_text(encoding='utf-8'))
context['selected_sources'].extend(NAMES)
context['remaining_source_names_unresolved'] = 0
context['relocation_authorization'] = 'Owner supplied screenshot of the two missing uploads in the OneDrive main folder and said they were accidentally placed there.'
context_path.write_text(json.dumps(context, indent=2) + '\n', encoding='utf-8')

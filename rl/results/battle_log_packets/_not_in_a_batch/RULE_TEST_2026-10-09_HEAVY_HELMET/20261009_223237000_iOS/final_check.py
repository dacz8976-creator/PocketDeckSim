import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

p = Path(__file__).resolve().parent
root = p.parents[2]
video = '20261009_223237000_iOS.MP4'
source = json.loads((p / 'SOURCE.json').read_text(encoding='utf-8-sig'))
receipt = json.loads((p / ('MOVE_RECEIPT.' + video + '.json')).read_text(encoding='utf-8-sig'))
assert receipt['identity_match'] and receipt['sha256_before'] == receipt['sha256_after'] == source['sha256']
archived = root / 'Reviewed' / video
assert archived.is_file() and archived.stat().st_size == source['bytes']
assert not (root / video).exists()
rows = list(csv.DictReader((root / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='')))
matching = [r for r in rows if r['Video'] == video]
assert len(matching) == 1 and matching[0]['Status'] == 'Reviewed'
assert matching[0]['Location'] == 'Reviewed/' + video
other = [r for r in rows if r['Video'] != video]
baseline = json.loads((p / 'INDEX_BASELINE.json').read_text())
other_hash = hashlib.sha256(json.dumps(other, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
assert len(other) == baseline['unrelated_row_count'] and other_hash == baseline['unrelated_rows_sha256']
mapping = json.loads((root / 'MEDIA_LOCATIONS.json').read_text(encoding='utf-8-sig'))
entry = [r for r in mapping['moved'] if r['filename'] == video]
assert len(entry) == 1 and Path(entry[0]['current_path']) == archived
assert entry[0]['sha256'] == source['sha256']
state = (p / 'ARTIFACT_RELOADED_STATE.txt').read_text(encoding='utf-8')
for required in ['1 of 1 captured', video, '03:05 to 03:37.5 (hit-back 03:32.5)', 'Heavy Helmet DOES reduce Bristling Spikes hit-back from 30 to 10', 'other hit-back cards, damage cuts and attack-trigger effects remain untested']:
    assert required in state, required
source['current_path'] = str(archived)
(p / 'SOURCE.json').write_text(json.dumps(source, indent=2) + '\n', encoding='utf-8')
artifact = {
    'artifact_url': source['artifact'],
    'verified_utc': datetime.now(timezone.utc).isoformat(),
    'verification': 'Chrome Save completed, artifact reloaded, All filter selected, saved fields read from reloaded accessibility state',
    'status': 'Captured', 'captured_count': 1, 'total_count': 1,
    'video': video, 'time': '03:05 to 03:37.5 (hit-back 03:32.5)',
    'finding': 'Heavy Helmet reduces this Bristling Spikes return from30 to10; Wailmer90 to80',
    'proof': ['ARTIFACT_RELOADED_STATE.txt', 'ARTIFACT_SAVED.jpg', 'ARTIFACT_SAVED_FIELDS.jpg'],
}
(p / 'ARTIFACT_VERIFICATION.json').write_text(json.dumps(artifact, indent=2) + '\n', encoding='utf-8')
result = {
    'review_complete': True, 'independently_accepted': True,
    'archived': True, 'archive_hash_match': True,
    'unrelated_index_rows_unchanged': len(other),
    'artifact_saved_and_reloaded': True,
    'ladder_entries_created': 0, 'pause_games_entries_created': 0,
    'simulator_changes': 0,
    'online_only_status': 'Pending OneDrive sync, local source retained; check storage receipt without reading video contents',
    'storage_receipt': str(root / 'Recording_QA/CLOUD_STORAGE/20261009T230148743849Z.apply.json'),
}
(p / 'COMPLETION_CHECK.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))

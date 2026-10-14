"""Verify selected movie storage from Windows metadata without reading movie bytes."""
import argparse
import csv
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--partial', action='store_true')
args = parser.parse_args()
inventory = json.loads((B / 'INVENTORY.json').read_text(encoding='utf-8-sig'))
spec = importlib.util.spec_from_file_location('storage_metadata', ROOT / 'Recording_QA' / 'free_reviewed_video_space.py')
storage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(storage)
with (ROOT / 'BATTLE_REVIEW_INDEX.csv').open(encoding='utf-8-sig', newline='') as file:
    index = list(csv.DictReader(file))
entries = []
errors = []
for game in inventory['recordings']:
    source = game['source']
    matches = [row for row in index if row['Video'] == source]
    path = ROOT / 'Reviewed' / source
    if len(matches) != 1 or matches[0]['Status'] != 'Reviewed' or matches[0]['Location'].replace('\\', '/') != 'Reviewed/' + source:
        errors.append(source + ': completed archive index entry missing or nonunique')
    if path.resolve() != Path(game['location']).resolve():
        errors.append(source + ': archive path differs from selected inventory')
    state = storage.metadata(path)
    expected_size = game['logical_bytes']
    size_match = state['logical_bytes'] == expected_size
    if not size_match:
        errors.append(source + ': logical file size differs from frozen inventory')
    lead_path = B / source.split('_iOS')[0] / 'LEAD_ACCEPTANCE.json'
    lead = json.loads(lead_path.read_text(encoding='utf-8-sig')) if lead_path.is_file() else {}
    accepted = lead.get('shared_registration') == 'complete'
    if not args.partial and not accepted:
        errors.append(source + ': independent acceptance and registration unfinished')
    if not args.partial and not state['online_only']:
        errors.append(source + ': source movie still has local allocation')
    entries.append({'source': source, 'path': str(path), 'accepted_registered': accepted,
                    'frozen_logical_bytes': expected_size, 'logical_size_matches': size_match, **state})
receipt = {'schema': 'retrospective-storage-verification-v1',
           'checked_at_utc': datetime.now(timezone.utc).isoformat(),
           'partial_check': args.partial, 'method': 'Windows cloud-placeholder and allocated-size metadata only',
           'movie_content_reads': 0, 'files_deleted': 0, 'movie_mutations': 0,
           'online_only_verified': [e['source'] for e in entries if e['online_only']],
           'allocated_bytes_after': sum(e['allocated_bytes'] for e in entries),
           'all_sources_in_reviewed': not any('archive' in error for error in errors),
           'all_logical_sizes_match_inventory': all(e['logical_size_matches'] for e in entries),
           'entries': entries, 'errors': errors, 'passed': not errors}
(B / 'STORAGE_VERIFICATION.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print(json.dumps({k: receipt[k] for k in ['partial_check', 'allocated_bytes_after', 'passed', 'errors']} |
                 {'sources': len(entries), 'online_only': len(receipt['online_only_verified'])}))
raise SystemExit(0 if receipt['passed'] else 1)

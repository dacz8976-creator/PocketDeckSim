import json
from pathlib import Path

batch = Path(__file__).resolve().parent
root = batch.parent.parent
status = json.loads((batch / 'BATCH_STATUS.json').read_text(encoding='utf-8-sig'))
results = status['results']
accepted = [r for r in results if r['status'] == 'accepted_registered_archived']
blocked = [r for r in results if r['status'] == 'source_access_blocked']
assert len(accepted) == 5 and len(blocked) == 3
copy_receipt = json.loads((batch / 'BOSS_FOLDER_COPY_RECEIPT.json').read_text(encoding='utf-8-sig'))
assert len(copy_receipt['packets']) == 5
source_bindings = [json.loads((Path(r['packet']) / 'SOURCE.json').read_text(encoding='utf-8-sig')) for r in accepted]
(batch / 'INTAKE.json').write_text(json.dumps(source_bindings, indent=2) + '\n', encoding='utf-8')
lines = [
    'October 9 new upload batch',
    '',
    'Five recordings completed: full visual review, separate independent verification, lead acceptance, completion registration, and archive with before/after identity verification.',
    'All five show the computer Auto control and are excluded from the human Ladder and Pause Games logs.',
    '',
    'Completed recordings:',
]
for item in accepted:
    outcome = item['outcome']
    result = outcome.get('result', outcome.get('owner_result', outcome.get('owner_outcome', 'See review')))
    owner_points = outcome.get('owner_points', 'see review')
    opponent_points = outcome.get('opponent_points', outcome.get('computer_points', 'see review'))
    lines.append(f"- {item['video']}: {result}, owner {owner_points} points, computer {opponent_points} points.")
lines += [
    '',
    'Three uploads remain pending because OneDrive did not provide readable source contents:',
    *[f"- {item['video']}" for item in blocked],
    'Make these files available on this device in OneDrive before review can proceed. Their modes and outcomes are unknown. No corruption has been established. The original files were retained in the intake folder.',
    '',
    f"All {status['existing_index_rows_unchanged']} existing index entries are unchanged. The older paused backlog was not restarted.",
    'Archived recordings are preserved in Reviewed. Online-only handling was checked after archival; available receipts show pending sync and local contents retained, so no reclaimed space is claimed.',
    'Review packets and their evidence were copied to the Boss Folder campaign new-uploads-2026-10-09, with every copied file verified by SHA-256.',
    f"Verified packet files: {sum(p['verified_file_count'] for p in copy_receipt['packets'])}.",
    '',
    'Detailed status: BATCH_STATUS.json',
    'Boss Folder copy evidence: BOSS_FOLDER_COPY_RECEIPT.json',
]
(batch / 'BATCH_SUMMARY.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))

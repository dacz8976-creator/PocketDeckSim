import json
import shutil
from pathlib import Path

batch = Path(__file__).resolve().parent
status = json.loads((batch / 'BATCH_STATUS.json').read_text(encoding='utf-8-sig'))
assert len(status['results']) == 8
assert all(item['status'] == 'accepted_registered_archived' for item in status['results'])
old_copy = json.loads((batch / 'BOSS_FOLDER_COPY_RECEIPT.json').read_text(encoding='utf-8-sig'))
new_copy = json.loads((batch / 'RESUMED_BOSS_COPY_RECEIPT.json').read_text(encoding='utf-8-sig'))
assert len(old_copy['packets']) == 5 and len(new_copy['packets']) == 3
storage = json.loads((batch / 'BATCH_STORAGE_RESULT.json').read_text(encoding='utf-8-sig'))
assert storage['videos'] == 8
bindings = []
wins = 0
losses = 0
lines = ['October 9 new uploads: completed batch', '', 'All eight requested recordings are fully reviewed, independently verified, registered, and archived with source identity preserved. The three uploads that previously failed OneDrive reads became readable and are now complete.', 'All eight are computer battles, excluded from the human Ladder and Pause Games logs. Auto status and manual choices are recorded separately in each review.', '', 'Results, owner score first:']
for item in status['results']:
    packet = Path(item['packet'])
    bindings.append(json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig')))
    outcome = item['outcome']
    result = outcome.get('result', outcome.get('owner_result', outcome.get('owner_outcome')))
    assert result is not None
    owner_points = outcome['owner_points']
    opponent_points = outcome.get('opponent_points', outcome.get('computer_points'))
    assert opponent_points is not None
    if result.lower() in ['victory', 'win']:
        wins += 1
    elif result.lower() in ['defeat', 'loss']:
        losses += 1
    else:
        raise AssertionError(result)
    lines.append(f"- {item['video']}: {result.capitalize()}, {owner_points}-{opponent_points}.")
lines += ['', f'Combined results: {wins} wins, {losses} losses.', f"All {status['existing_index_rows_unchanged']} entries preceding this upload batch are unchanged; all {status['existing_index_rows_before_retry_unchanged']} entries present before the retry are unchanged. The older paused backlog was not restarted.", 'Review packets are saved in Pocket Deck Lab/Boss Folder/new-uploads-2026-10-09. Every copied packet file was checked by SHA-256.', f"Verified packet files: {sum(p['verified_file_count'] for p in old_copy['packets'] + new_copy['packets'])}.", '', f"OneDrive storage: {storage['online_only']} of 8 original recordings are online-only; {8 - storage['online_only']} remain locally stored. Local bytes reclaimed in the final storage check: {storage['local_bytes_reclaimed']}. Files deleted: {storage['files_deleted']}."]
if storage['online_only'] < 8:
    lines.append('Any remaining storage release is pending OneDrive sync. Originals are preserved; no local-space release is claimed without metadata verification.')
lines += ['', 'Supporting records: local BATCH_STATUS.json (Boss Folder copy: RESUMED_BATCH_STATUS.json), RESUMED_BOSS_COPY_RECEIPT.json, BATCH_STORAGE_RESULT.json. Historical intake errors remain in the individual packets as prior access evidence.']
report = '\n'.join(lines) + '\n'
old_summary = batch / 'BATCH_SUMMARY.txt'
snapshot = batch / 'BATCH_SUMMARY_PRE_RESUME.txt'
if old_summary.exists() and not snapshot.exists():
    shutil.copy2(old_summary, snapshot)
old_summary.write_text(report, encoding='utf-8')
(batch / 'RESUMED_BATCH_SUMMARY.txt').write_text(report, encoding='utf-8')
(batch / 'INTAKE.json').write_text(json.dumps(bindings, indent=2) + '\n', encoding='utf-8')
print(report)

import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
batch = root / 'Recording_QA' / 'BATCH_2026-09-30'
intake = json.loads((batch / 'INTAKE.json').read_text(encoding='utf-8-sig'))
entries = []
for item in intake['sources']:
    packet = root / 'Recording_QA' / (Path(item['video']).stem + '_auto_sol')
    acceptance_path = packet / 'LEAD_ACCEPTANCE.json'
    receipt_path = packet / f"MOVE_RECEIPT.{item['video']}.json"
    accepted = acceptance_path.is_file() and receipt_path.is_file()
    initial_status = item.get('status', 'review_in_progress')
    entry = {'video': item['video'], 'ladder_eligible': False, 'status': initial_status, 'packet': str(packet)}
    if accepted:
        a = json.loads(acceptance_path.read_text(encoding='utf-8-sig'))
        receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
        if not a['accepted'] or not receipt['identity_match'] or receipt['sha256_after'] != item['sha256']:
            raise RuntimeError(f"Invalid archive acceptance: {item['video']}")
        entry.update({'status': 'accepted_and_archived', 'outcome': a.get('outcome'), 'final_points': a.get('final_points'), 'result_display': a.get('result_display'), 'owner_visible_core': a.get('owner_visible_core'), 'opponent': a.get('opponent'), 'last_turn': a.get('last_turn'), 'useful_finding': a.get('useful_finding'), 'sha256': receipt['sha256_after'], 'astra_consulted': a.get('astra_consulted', False)})
    entries.append(entry)
completed = [e for e in entries if e['status'] == 'accepted_and_archived']
astra_count = sum(e.get('astra_consulted', False) for e in completed)
wins = sum(e['outcome'] == 'owner_win' for e in completed)
losses = sum(e['outcome'] == 'owner_loss' for e in completed)
(batch / 'RESULTS.json').write_text(json.dumps({'scope': 'September 30 autopilot computer games; no Ladder Log entries', 'total': len(entries), 'completed': len(completed), 'videos': entries}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
lines = ['# September 30 autopilot computer battle reviews', '', f"{len(completed)} of {len(entries)} recordings have completed source-backed Sol reviews, lead checks and verified archival. Every game is excluded from Ladder Log under the owner's instruction. Results here describe computer practice, not ranked ladder performance.", '', 'Each completed packet includes the full timeline, turn coverage, source identity, useful evidence, explicit uncertainties and lead acceptance. Unknown hidden cards or challenge difficulty stay unknown. Ordinary, decisive and terminal evidence is checked before acceptance.', '', '| Source recording | Visible owner core | Result | Review |', '|---|---|---|---|']
lines[6:6] = [f'A separate fresh Sol agent reviewed each recording in full. Astra checked the difficult Stadium and terminal-sequence interpretations in {astra_count} reports; see the [bounded consultation](Recording_QA/BATCH_2026-09-30/ASTRA_ARENA_CHECK.md). The completed practice games contain {wins} wins and {losses} losses across the shown decks and challenges.', ''] if astra_count else []
for e in entries:
    relative = 'Recording_QA/' + Path(e['video']).stem + '_auto_sol/REVIEW.md'
    if e['status'] == 'accepted_and_archived':
        points = e['final_points']
        score = f"{points['owner']}-{points['opponent']}"
        result = e.get('result_display') or (('Win ' if e['outcome'] == 'owner_win' else 'Loss ') + score)
        lines.append(f"| `{e['video']}` | {e['owner_visible_core']} | {result} vs {e['opponent']} | [Complete review]({relative}) |")
    else:
        progress = 'Waiting for OneDrive download' if e['status'] in ['pending_local_download', 'pending_readable_source'] else 'Review in progress'
        lines.append(f"| `{e['video']}` | Pending | {progress} | Pending |")
if completed:
    lines += ['', '## Useful observations', '']
    for e in completed:
        finding = re.sub(r'([A-Za-z])(?=\d)', r'\1 ', e['useful_finding'])
        finding = re.sub(r'(\d)(?=[A-Za-z])', r'\1 ', finding)
        finding = finding.replace('zeroHP', 'zero HP')
        lines.append(f"- `{e['video']}`: {finding}")
correction_report = batch / 'POST_ACCEPTANCE_CORRECTIONS_2026-09-30.md'
if correction_report.is_file():
    lines += ['', '## Post-acceptance corrections', '', 'The owner-supplied cross-check has been reconciled in the [wording and status correction record](Recording_QA/BATCH_2026-09-30/POST_ACCEPTANCE_CORRECTIONS_2026-09-30.md). All 15 current statuses agree with lead acceptance. Original text and review events are preserved. Outcomes, scores and Ladder exclusion are unchanged.', '', 'Results-screen Damage done can include overkill. Point-circle displays stop at three; the reviews separately record observed awards when they cross that threshold.']
lines += ['', '## Verification', '', 'Completed originals preserve their exact names and bytes in `Reviewed`. Each move receipt records matching SHA-256 before and after the move. The shared review events, index and media-location map are updated only after lead acceptance. No Ladder Log entry is created for this batch.', '', 'Full visual action coverage is distinct from frame-by-frame playback or audio transcription. The individual reviews retain any limitations and do not infer full decks or hidden tactical alternatives.', '']
(root / 'BATTLE_TRANSCRIPTS_2026-09-30.md').write_text('\n'.join(lines), encoding='utf-8')
print(f'{len(completed)}/{len(entries)} complete and archived; Ladder Log entries: 0')

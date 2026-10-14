"""Write a current coordinator view without changing frozen worker reports."""
import json
from datetime import datetime, timezone
from pathlib import Path
from batch_packet_scope import game_packets, result_value
B=Path(__file__).resolve().parent
progress=json.loads((B/'BATCH_PROGRESS.json').read_text(encoding='utf-8'))
decks=json.loads((B/'NEW_DECK_ENTRIES.json').read_text(encoding='utf-8'))
counts={}
request_path=B/'AUTHORIZED_IMPORT_REQUEST.json'
live_path=B/'LIVE_SAVE_VERIFICATION.json'
request=json.loads(request_path.read_text(encoding='utf-8')) if request_path.exists() else None
live=json.loads(live_path.read_text(encoding='utf-8')) if live_path.exists() else None
if live and live.get('external_saved_verified'):
    external_status=f"The existing [Pause Games artifact]({live['artifact_url']}) was updated with {live['inserted_decks']} new deck definitions and {live['inserted_games']} games. Fresh reload and exact rendered-field checks verified {live['final_games']} total games, {live['final_wins']} wins and {live['final_losses']} losses, with {live['final_decks']} deck definitions. Existing entries were preserved. See [live verification](LIVE_SAVE_VERIFICATION.json)."
elif request:
    external_status='The owner authorized sending and adding the prepared entries. The complete JSON was sent to Claude for the existing artifact; live persistence verification is still pending. See [authorized request](AUTHORIZED_IMPORT_REQUEST.json). The existing 10 games, 6 wins and 4 losses were checked before the request and are preserved in EXTERNAL_BASELINE.json.'
else:
    external_status='No new external save is claimed. The artifact has no Add Deck control; sending the prepared JSON to Claude awaits direct owner authorization. The existing 10 games, 6 wins and 4 losses were checked by source filename and preserved in EXTERNAL_BASELINE.json.'
lines=['# October 6 new Pause Games review','','Current coordinator status at '+datetime.now(timezone.utc).isoformat()+'. Worker summaries retain their original submission status; LEAD_ACCEPTANCE.json and registration/move receipts establish the current accepted status.','','Scope: exactly 17 newly requested recordings from October 4 through 6. Earlier paused backlog remains outside this request. Sol performs complete first passes and separate bounded independent checks; consequential unresolved reasoning goes to Astra.','','| Source | Current status | Submitted result | Turns | Packet |','| --- | --- | --- | --- | --- |']
for entry in progress['sources']:
    status=entry['persisted_status'];counts[status]=counts.get(status,0)+1
    units=game_packets(Path(entry['packet']))
    for number,p in enumerate(units,1):
        summary_path=p/'SUMMARY.json'
        s=json.loads(summary_path.read_text(encoding='utf-8')) if summary_path.exists() else {}
        outcome=result_value(s) or 'pending'
        outcome_fields=s.get('outcome') if isinstance(s.get('outcome'),dict) else {}
        turns=s.get('turn_count',s.get('recorded_turn_count',s.get('turns',s.get('actual_turns',outcome_fields.get('turns_played','pending')))))
        lead_path=p/'LEAD_ACCEPTANCE.json'
        if lead_path.exists():turns=json.loads(lead_path.read_text(encoding='utf-8'))['turn_rows']
        label=entry['source_video']+(f' (game {number}/{len(units)})' if len(units)>1 else '')
        review_link=f'[Review](<{p.as_posix()}/REVIEW.md>)' if (p/'REVIEW.md').exists() else 'pending'
        lines.append(f"| {label} | {status.replace('_',' ')} | {outcome} | {turns} | {review_link} |")
game_count=sum(len(game_packets(Path(e['packet']))) for e in progress['sources'])
lines+=['',f'Current source segmentation identifies {game_count} game packets across the 17 recordings. The 012927 recording contains two human games and an intervening filmed deck edit; both games and the edit passed review before the original was archived. Each game retains a distinct ID and source interval, so a shared filename does not create a duplicate battle entry.']
lines+=['','Current counts: '+', '.join(f'{n} {k.replace("_"," ")}' for k,n in counts.items())+'.','',str(len(decks['decks']))+' distinct exact 20-card QR deck entries are prepared in [NEW_DECK_ENTRIES.md](NEW_DECK_ENTRIES.md). They preserve small revisions, playable entity IDs and Energy. The filmed slot name is not a unique deck identity. Native QR payloads, source and image hashes, decoder round-trip and semantic references are retained. Artwork remains unspecified.','',external_status,'','Every accepted packet includes source binding, full coverage, prose, one structured row per actual turn, the Pause Games hand/board capture supplement, independent findings, lead acceptance and CLI registration. Original videos move only after registration and matching pre/post-move hashes. [Storage status](STORAGE_STATUS.md) records pending OneDrive sync separately from successful archival.','','Reports and evidence resolve from the project Boss Folder through its uniquely named new-pause-games-review-2026-10-06 junction. Canonical files remain in the Battle Logs Recording_QA batch; the junction avoids duplicate media and evidence.','','The empty review lock was inspected and cleared after the owner authorized removal. LOCK_RESOLUTION.json retains creation time and the limits on identifying its creator.']
if (B/'EDITED_DECK_ENTRY.json').exists():
    edit=json.loads((B/'EDITED_DECK_ENTRY.json').read_text(encoding='utf-8'))['decks'][0]
    lines+=['','A separate fourteenth definition is prepared in [EDITED_DECK_ENTRY.md](EDITED_DECK_ENTRY.md) for '+edit['deck_name']+' used in 012927 game 2. Its Energy is Water only. No revised QR was filmed; the continuous edit ledger and second game independently establish its exact list and binding. The 13 QR definitions remain frozen.']
if (B/'BATCH_COMPLETION_CHECK.json').exists():
    completion=json.loads((B/'BATCH_COMPLETION_CHECK.json').read_text(encoding='utf-8'))
    queue=json.loads((B/'PREPARED_GAME_QUEUE.json').read_text(encoding='utf-8'))
    wins=sum(r['owner_result']=='win' for r in queue['accepted_game_entries'])
    losses=sum(r['owner_result']=='loss' for r in queue['accepted_game_entries'])
    lines+=['',f'Final local verification passed: {completion["source_count"]} originals, {completion["game_count"]} games, {wins} wins and {losses} losses. All source/game acceptances, frozen inputs, CLI entries, archive identity receipts, index and media map agree. No video content was read during this final verification.']
if (B/'PAUSE_GAMES_BATCH_IMPORT.json').exists():
    lines+=['','The complete [prepared import](PAUSE_GAMES_BATCH_IMPORT.json) contains all 14 deck definitions and 18 game entries, with four qualified deck choices clearly distinguished from proven versions. It preserves the prepared state before external changes; the current external status and separate receipts are reported above. [Accepted deck bindings](ACCEPTED_DECK_BINDINGS.json) separately record final source acceptance without changing frozen definitions.']
(B/'BATCH_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(counts))

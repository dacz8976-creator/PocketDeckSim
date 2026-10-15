import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
decision = {
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'owner_choice': 'Local batch and index only (Recommended)',
    'owner_rule': 'The pause log is for games against other humans. No games where the auto pilot mode is shown, should be logged there',
    'classification_rule': 'Any visible Auto option, even OFF, identifies a computer battle. Process locally; exclude from human Pause Games and ladder results.',
    'actual_destination': 'local_review_batch_and_BATTLE_REVIEW_INDEX',
    'batch_path': str(BATCH),
    'online_game_entry_requested': False,
    'human_pause_games_eligible': False,
    'ranked_ladder_eligible': False,
    'capture_protocol': 'PAUSE_GAMES_REVIEW_PROTOCOL.md explicitly requested for this local computer comparison.',
    'deck_snapshot_source_url': 'https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd',
    'prior_intake_routing_limit': 'Root initially assigned the Pause Games URL as a tentative destination. Preserved SOURCE/ASSIGNMENT or frozen first passes may retain that URL. This direct owner routing decision supersedes those destination fields; the URL remains valid only as the exact deck-list source.',
    'external_writes_for_this_batch': 0,
    'scope': 'All eight new October2 Draft A computer comparison games.'
}
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
save(BATCH/'LOG_ROUTING.json', decision)
context_path = BATCH/'OWNER_CONTEXT.json'
context = json.loads(context_path.read_text(encoding='utf-8-sig'))
context.update({'requested_destination':'local_review_batch_and_BATTLE_REVIEW_INDEX', 'online_game_entry_requested':False, 'human_pause_games_eligible':False, 'deck_snapshot_source_url':decision['deck_snapshot_source_url'], 'routing_decision':str(BATCH/'LOG_ROUTING.json')})
save(context_path,context)
for packet in BATCH.glob('20261002_*_sol'):
    save(packet/'ROUTING.json', {**decision, 'packet_path':str(packet)})
note = BATCH/'BATCH_NOTE.md'
text = note.read_text(encoding='utf-8')
text = text.replace('All are computer battles and excluded from ladder totals.', 'All are computer battles, saved in this local batch and BATTLE_REVIEW_INDEX. They are excluded from both the human Pause Games log and ladder totals, per Dustin’s explicit routing instruction.')
note.write_text(text, encoding='utf-8')
print('Local-only routing recorded for all eight games; no external game entries written.')

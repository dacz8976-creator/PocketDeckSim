"""Prepare readable, source-qualified notes after external saving."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
bundle = json.loads((B/'PAUSE_GAMES_BATCH_IMPORT.json').read_text(encoding='utf-8'))
queue = json.loads((B/'PREPARED_GAME_QUEUE.json').read_text(encoding='utf-8'))
detail = {
    ('20261004_213625000_iOS.MP4',1): 'Loss 2-3; Defeat results at 459s.',
    ('20261004_214518000_iOS.MP4',1): 'Setup-only win 0-0, zero turns and zero damage. Connection warning at about 45s, Victory at 49s and results at 55s. The termination cause is unknown; no explicit concession was observed. Opponent Pokemon were not revealed.',
    ('20261004_214731000_iOS.MP4',1): 'Win 3-0; 200 damage; final results at 374s.',
    ('20261004_215749000_iOS.MP4',1): 'Win by explicit opponent concession at 244s; Victory at 256s. Earned points 1-0.',
    ('20261005_003547000_iOS.MP4',1): 'Loss 0-3; 240 damage; Defeat results at 557s.',
    ('20261005_031138000_iOS.MP4',1): 'Win by explicit opponent concession at 214s; Victory results at 225s. Earned points 2-0; 180 damage.',
    ('20261005_032023000_iOS.MP4',1): 'Loss 0-3; 180 damage; Defeat results at 476s. Exact matchmaking mode remains uncertain.',
    ('20261005_032857000_iOS.MP4',1): 'Loss with earned points 0-2 after the last owner Pokemon was knocked out and both Active and Bench were empty. Defeat results at 304s; 220 damage.',
    ('20261005_033529000_iOS.MP4',1): 'Loss 1-3; 270 damage; Defeat results at 390s.',
    ('20261005_034229000_iOS.MP4',1): 'Loss 0-3; 110 damage; Defeat results at 374s.',
    ('20261005_034953000_iOS.MP4',1): 'Win by explicit opponent concession at 390s; Victory results at 409s. Earned points 2-1; 460 damage.',
    ('20261005_123812000_iOS.MP4',1): 'Loss by owner concession at 325s; Defeat at 327s and results at 336s. Last earned points 1-2.',
    ('20261005_124532000_iOS.MP4',1): 'Loss 0-3; 70 damage; Defeat results at 339.7s. Individual identities within one combined hidden draw remain unknown.',
    ('20261005_183108000_iOS.MP4',1): 'Loss 2-3; 470 damage; Defeat results at 402s. During the buffered opponent turn 6, the net board change and hand counts are visible, but hidden draw identity and the order of the two Pokemon plays are unknown.',
    ('20261006_012140000_iOS.MP4',1): 'Win by explicit opponent concession at 204s; Victory results at 214.8s. Earned points 2-0; 160 damage.',
    ('20261006_012927000_iOS.MP4',1): 'Loss 0-3; Defeat results at 407s. This is the first match, before the filmed deck edit.',
    ('20261006_012927000_iOS.MP4',2): 'Win by explicit opponent concession at 710s; Victory at 718s. Earned points 0-0 and zero damage. This is the second match, after the filmed deck edit.',
    ('20261006_020518000_iOS.MP4',1): "Win 3-2. Hitmonchan ex's Quick Straight knocked out Copperajah for the third point; Victory versus Adgbag is confirmed. Opponent May searches and shuffled cards remain hidden.",
}
rows = []
for game, row in zip(bundle['game_documents'],queue['accepted_game_entries']):
    assert game['game_id'] == row['game_id']
    key=(row['source_video'],row['game_number_in_source'])
    assert key in detail
    if not row['exact_game_deck_binding']:
        binding='Exact 20-card game list is unverified. The selected deck is a qualified earlier QR candidate; only the visible core is proven for this game.'
    elif row['exact_deck_evidence_type']=='continuous_filmed_edit':
        binding='Exact 20-card Water-only revision is established by the continuous filmed edit and saved list. No revised QR was filmed.'
    else:
        binding='Exact 20-card list and Energy are bound to the filmed QR and this game; artwork and rarity are not established by the QR.'
    packet=Path(row['packet']).relative_to(B).as_posix()
    note=(f"Source: {row['source_video']}. Game {row['game_number_in_source']} of {row['game_count_in_source']}; game ID: {row['game_id']}. "
          f"Opponent: {row['opponent']}. {detail[key]} Went {row['went']}; {row['turn_count']} recorded turns. {binding} "
          f"Full review and structured hand, turn and board evidence: Recording_QA/BATCH_2026-10-06_NEW_PAUSE_GAMES/{packet}/ "
          '(REVIEW.md, TURN_LEDGER.json, TURN_EVIDENCE.json, DECK_USED.json, PAUSE_GAME.json). '
          'All times are source-local seconds. Hidden cards and unrecorded actions remain unknown. Owner ratings were not supplied.')
    assert len(note)<=1500 and '\u2014' not in note
    rows.append({'game_id':game['game_id'],'source_video':game['source_video'],'game_number_in_source':game['game_number_in_source'],
                 'previous_note_sha256':hashlib.sha256(game['fields']['note'].encode('utf-8')).hexdigest(),'note':note})
out={'prepared_utc':datetime.now(timezone.utc).isoformat(),'artifact_url':bundle['existing_artifact'],
     'operation':'Update note fields only for these 18 newly imported game IDs; preserve all other fields and the 10 pre-existing games.',
     'games':rows,'qualified_game_ids':[g['game_id'] for g in bundle['game_documents'] if not g['exact_game_deck_binding']],
     'ui_clarity':'Label exact_game_deck_binding === false games as Exact deck list unverified in Recent games and give the count of these games in each deck summary. Do not treat missing flags on older games as false.'}
(B/'FINAL_GAME_NOTES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'notes':len(rows),'qualified':len(out['qualified_game_ids']),'maximum_length':max(len(r['note']) for r in rows)}))

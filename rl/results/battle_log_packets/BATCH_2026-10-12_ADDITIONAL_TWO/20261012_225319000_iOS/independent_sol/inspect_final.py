from pathlib import Path
import json
p=Path(__file__).resolve().parent.parent
for name in ['PAUSE_GAME.json','DECK_USED.json']:
 j=json.loads((p/name).read_text(encoding='utf-8-sig'));print(name,json.dumps(j,ensure_ascii=False))
j=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8-sig'))
for t in j['turns']:
 print('\nTURN',t['turn_number'],t['who_played'],'start',t.get('timing'))
 print('acting hand',json.dumps(t.get('hand_at_start'),ensure_ascii=False))
 for play in t['plays_in_order']: print('PLAY',play['order'],play['kind'],play['card_name'],play.get('target'),play.get('timestamp_seconds'),play['result'],play['energy'],play.get('evidence_ids'))
 if t['who_played']=='owner':
  print('HANDS',t['owner_hand_start'],t['owner_hand_end']);print('FAN',t['opponent_hand_at_owner_turn_start'])
 for bkey in ['board_at_start','board_after']:
  b=t.get(bkey,t.get('starting_board' if bkey=='board_at_start' else 'board_after'))
  print('BOARD',bkey,json.dumps(b,ensure_ascii=False))
 print('DRAWSEARCH',json.dumps(t.get('draws_and_searches'),ensure_ascii=False))
 print('LIMITS',t.get('limits'))

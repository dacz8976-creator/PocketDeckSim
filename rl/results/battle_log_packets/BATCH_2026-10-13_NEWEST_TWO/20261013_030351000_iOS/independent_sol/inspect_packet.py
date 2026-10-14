import json,hashlib
from pathlib import Path
p=Path(__file__).resolve().parent.parent
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'))
evidence=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
print('Ledger keys',list(ledger)); print('Evidence keys',list(evidence))
for t in ledger['turns']:
 print('\nTURN',t['turn_number'],t.get('timing'))
 print('START',json.dumps(t.get('owner_hand_start'),ensure_ascii=False))
 print('DRAW',json.dumps(t.get('draws_and_searches'),ensure_ascii=False))
 print('END',json.dumps(t.get('owner_hand_end'),ensure_ascii=False))
 print('FAN',json.dumps(t.get('opponent_hand_at_owner_turn_start'),ensure_ascii=False))
 if t['turn_number']==11:
  print('PLAYS',json.dumps(t.get('plays_in_order'),ensure_ascii=False))
 print('EZ',json.dumps({k:t.get(k,{}).get('energy_zones') for k in ['starting_board','board_after']},ensure_ascii=False))

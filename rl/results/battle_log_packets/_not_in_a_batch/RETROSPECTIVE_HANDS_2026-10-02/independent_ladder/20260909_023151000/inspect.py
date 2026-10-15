exec(open(__file__.replace('inspect.py','check.py'),encoding='utf-8').read().split('hashes=[]')[0])
L=read('TURN_LEDGER.json')
for t in L['turns']:
 print('TURN',t['turn_number'],t['who_played'])
 print('plays',json.dumps([{k:p.get(k) for k in ['order','card_name','target','energy','result','prompt_text','response','limit_reason']} for p in t['plays_in_order']],ensure_ascii=False))
 for k in ['board_at_start','board_after']:
  b=t[k]
  print(k,b['phase'],'stadium',b['stadium'])
  for side in ['owner','opponent']:
   v=b[side]; a=v['active']; z=v['energy_zone']
   print(side,[(a or {}).get('name'),(a or {}).get('hp_now'),(a or {}).get('attached_energy')],[(x['name'],x['hp_now'],x['attached_energy']) for x in v['bench_in_position_order']],z['this_turn'],z.get('derived_after_generation'),v['points'])
 print('automatic',json.dumps(t['automatic_events_in_order'],ensure_ascii=False))

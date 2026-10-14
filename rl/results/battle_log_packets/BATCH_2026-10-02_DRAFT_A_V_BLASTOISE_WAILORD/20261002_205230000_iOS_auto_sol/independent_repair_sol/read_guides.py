import pathlib,json
B=pathlib.Path(__file__).resolve().parents[2]
for g in ['20261002_205230000_iOS_auto_sol','20261002_205731000_iOS_auto_sol','20261002_210612000_iOS_auto_sol']:
 p=B/g; d=json.loads((p/'GUIDE_UPDATE_SUPPLEMENT.json').read_text()); i=json.loads((p/'SEEN_CARD_INVENTORY.json').read_text()); print(g)
 for k,v in d.items():
  if k not in ['source_evidence','fresh_owner_turn_boards','owner_turns','physical_evolution_histories']: print(k,json.dumps(v,ensure_ascii=False))
 rows=d.get('fresh_owner_turn_boards',d.get('owner_turns'))
 print('FIRST_ROW',json.dumps(rows[0],ensure_ascii=False))
 print('histories',json.dumps(d.get('physical_evolution_histories'),ensure_ascii=False))
 for c in i['cards']: print('card',json.dumps({k:v for k,v in c.items() if k not in ['occurrences','evidence_occurrences']},ensure_ascii=False))
 print('rows_keys',[list(r.keys()) for r in rows]); print('inventoryfirst',json.dumps(i['cards'][0],ensure_ascii=False))

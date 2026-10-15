import json
from pathlib import Path
p=Path(r'Recording_QA\BATCH_2026-10-06_NEW_PAUSE_GAMES\20261004_213625000_iOS')
f=p/'TURN_LEDGER.json';d=json.loads(f.read_text());r=d['turns'][-1];r['board_after']['opponent']['board_effects']=[{'name':None,'source':None,'observed':'Residual blue immunity badge is still displayed on Vespiquen ex through the terminal animation after Ogerpon was discarded.','expiry':None,'status':'terminal_UI_clearance_not_shown','evidence_ids':['F0446.00']}];r['limits'].append('No following playable turn is recorded to establish clearance of the residual immunity badge after source Ogerpon leaves. Does not affect terminalKO/result.')
f.write_text(json.dumps(d,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
f=p/'WORKER_QA.json';q=json.loads(f.read_text());q['structural_pass']=True;q['structural_validator']='../validate_packet.py';f.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

import json,hashlib,re,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
p=Path(__file__).resolve().parent
def read(n):return json.loads((p/n).read_text(encoding='utf-8'))
def save(n,x):(p/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def normalize(s):
 s=re.sub(r'(?<=[a-zA-Z])(?=(?:HP|KO)\b)', ' ',s)
 s=re.sub(r'(?<=\d)(?=(?:HP|Fighting|Darkness|weakness|extra|hidden|card|Energy|Research|Copycat|Mesagoza|IcePop|normal|evolution|plus|Active|weak|Damage|Dark|F\b|s\b|turns?\b|cards?\b))',' ',s)
 s=re.sub(r'(?<=(?:HP))(?=\d)',' ',s)
 for a,b in {'plus20weakness':'plus 20 weakness','plus20extra':'plus 20 extra','point1':'point 1','point2':'point 2','Tails;':'Tails;','8:57..9:03':'8:57 to 9:03','13turns':'13 turns','20-card':'20-card','140 plus20':'140 plus 20','Pulse90':'Pulse 90','Pulse140':'Pulse 140','Fist10':'Fist 10','Hit30':'Hit 30','Spin20':'Spin 20','Spin40':'Spin 40','normaldraw':'normal draw','Researchdraws':'Research draws','20extra':'20 extra','draws2':'draws 2','draw2':'draw 2','heal20':'heal 20','discard1':'discard 1','to180':'to 180','gives2':'gives 2'}.items():s=s.replace(a,b)
 return s
textfields={'result','description','basis','limit_reason','restriction','phase','hand_arithmetic','damage_results','limits','capture_limits','candidate_suitability','timestamp_basis','deck_source','match_date_basis','game_version_binding_basis','log_list_version'}
def fix(v,key=None):
 if isinstance(v,dict):return {k:fix(i,k) for k,i in v.items()}
 if isinstance(v,list):return [fix(i,key) for i in v]
 if isinstance(v,str) and key in textfields:return normalize(v)
 return v
names=['SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
for n in names:save(n,fix(read(n)))
l=read('TURN_LEDGER.json');t3=l['turns'][2];t3['plays_in_order'][0].update(timestamp_seconds=76.5,evidence_ids=['N0076_50'],basis='Completed left Glimmora evolution shown by native76.5;74.5 is selection/inspection, not a claimed committed play instant',commit_window_seconds=[74.5,76.5]);t3['timing']['first_voluntary_move_seconds']=76.5;t3['timing']['first_move_timing_basis']='Commit occurs between selected card at74.5 and completed board at76.5; timestamp is observed completion anchor'
l['turns'][12]['plays_in_order'][-1].update(timestamp_seconds=385,evidence_ids=['N0384_00','N0386_00'],nested_events_in_order=['Concede menu383.5','confirmation384','acceptance occurs between384 and386','Defeat386']);l['turns'][12]['timing']['end_after_resolution_seconds']=386
save('TURN_LEDGER.json',l)
g=read('PAUSE_GAME.json');g['outcome']={'result':'loss','method':'owner concession','points_at_concession':{'owner':0,'opponent':2},'turns_played':13,'evidence_ids':['N0383_50','N0384_00','N0386_00','N0403_00']};g['limits']=g['capture_limits'];save('PAUSE_GAME.json',g)
s=read('SUMMARY.json');s['terminal_evidence'].update(concede_menu_seconds=383.5,confirmation_seconds=384,defeat_seconds=386,result_opponent_seconds=403);s['terminal_statistics_available']=False;s['turn_count_basis']='13 recorded turn rows and filmed banners;403s result identifies opponent and Defeat but does not show terminal statistic table';save('SUMMARY.json',s)
q=read('QR_DECODE.json');q['payload']=q.get('payload',q.get('decoded_payload'));save('QR_DECODE.json',q)
for n in ['REVIEW.md','COVERAGE.md']:
 s=(p/n).read_text();s=s.replace('at385-386s','between 384 and 386 s').replace('at385-386 s','between 384 and 386 s').replace('confirms concession at385-386','confirms concession between 384 and 386').replace('Defeat follows and results identify','Defeat at 386 s follows, and the result title identifies').replace('Reviewer: remaining_015659, Sol/high','Reviewer: remaining_015659, Sol/high')
 s=normalize(s);s=s.replace('all13','all 13').replace('All13','All 13').replace('One game.','One game.').replace('Entire404.623333 s','Entire 404.623333 s').replace('reviewed: QR/deck, matchmaking, setup,13','reviewed: QR/deck, matchmaking, setup, 13').replace('no Pokémon ex','no Pokémon ex').replace('Turn13','Turn 13').replace('Hand4','Hand 4').replace('leaves5cards','leaves 5 cards').replace('leaves4','leaves 4').replace('list20','list 20').replace('20-card','20-card').replace('HP60','HP 60').replace('point2','point 2')
 s=s.replace('evolve60HP','evolve 60 HP').replace('bench50HP','bench 50 HP').replace('bench60HP','bench 60 HP').replace('bench70HP','bench 70 HP').replace('bench80HP','bench 80 HP').replace('second80HP','second 80 HP').replace('to90HP','to 90 HP').replace('to110HP','to 110 HP')
 s+='\nTiming clarification: T3 native 74.5 s shows selected Glimmora inspection. The left evolution is committed between that view and the completed board at 76.5 s. Ledger play 1 uses the completed 76.5 s anchor, without calling the inspection a committed play. The result title at 403 s shows Defeat versus GaboDobleT; the source ends before a full statistics table. Turn count and damage are supported by gameplay, not that result title.\n'
 (p/n).write_text(s,encoding='utf-8')
validator=p.parent.parent/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r=subprocess.run([sys.executable,'-X','utf8',str(validator),str(p)],capture_output=True,text=True,encoding='utf-8');print(r.stdout);assert r.returncode==0,r.stderr
save('STRUCTURAL_VALIDATION.json',json.loads(r.stdout))
source=read('SOURCE.json'); eight=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
save('REVIEW_PACKET_HASHES.json',{'source_video':source['video_basename'],'source_sha256':source['sha256'],'frozen_utc':datetime.now(timezone.utc).isoformat(),'review_components':{n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in eight},'scope':'Eight actual primary components frozen for separate source-bound acceptance','visual_acceptance':False})
print('Eight files frozen. Stop primary edits during independent acceptance.')

from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).parent
S=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
summary={
 'source_filename':S['video_basename'],'source_sha256':S['sha256'],
 'source_bytes':S['bytes'],'source_duration_seconds':S['duration_seconds'],
 'recording_creation_utc':S['source_creation_utc'],'match_date':'2026-10-14',
 'reviewer':'/root/newer_234728','existing_claim':'/root/evening_234728',
 'model':'gpt-6.1-sol','reasoning_effort':'high',
 'primary_review_complete':True,'independent_acceptance_pending':True,
 'battle_complete':True,'match_count':1,
 'mode':'ranked ladder','rank_visible':'Ultra Ball Rank 4 (both players)',
 'auto_option_seen':False,'manual_interaction_seen':True,
 'owner':'Dacz8976','opponent':'カビゴンです',
 'deck':{'name':'Deck 13-A','main_attacker':'Alolan Ninetales ex','energy':['Water'],'visible_core':['Alolan Vulpix','Alolan Ninetales ex',"Team Rocket's Rattata","Team Rocket's Raticate ex"],'complete_20_card_list_established':False},
 'opponent_visible_core':['Mega Rayquaza ex','Dratini','Dragonair','Gouging Fire'],
 'result':'win','result_method':'opponent concession',
 'score':{'owner':2,'opponent':2,'meaning':'actual points before concession; no fabricated third point'},
 'going_order':'1st','exact_three_item_note_prefix':'1st | Alolan Ninetales ex T3 | opp 0 pts',
 'first_main_attack':{'pokemon':'Alolan Ninetales ex','attack':'Binding Snow','own_turn':3,'global_turn':5,'seconds_approx':176,'opponent_points_before':0,'damage':80,'target':'Dragonair','target_hp_before':80,'knockout':True},
 'supporting_attacks':[],
 'global_turns_observed':11,'owner_turns_started':6,'opponent_turns_started':5,
 'point_progression':[{'seconds_approx':184,'score':'1-0','event':'Dragonair KO'},{'seconds_approx':350,'score':'2-0','event':'Gouging Fire KO'},{'seconds_approx':386,'score':'2-2','event':'Alolan Ninetales ex KO'},{'seconds_approx':398,'score':'2-2','event':'Opponent conceded'}],
 'decisive_native_evidence':['evidence/f_0002.00.jpg','evidence/f_0018.00.jpg','evidence/f_0022.00.jpg','evidence/f_0042.00.jpg','evidence/f_0176.00.jpg','evidence/f_0178.00.jpg','evidence/f_0184.00.jpg','evidence/f_0350.00.jpg','evidence/f_0376.00.jpg','evidence/f_0380.00.jpg','evidence/f_0382.00.jpg','evidence/f_0386.00.jpg','evidence/f_0392.00.jpg','evidence/f_0393.00.jpg','evidence/f_0398.00.jpg','evidence/f_0407.00.jpg'],
 'external_log_written':False,'source_moved':False,
 'limits':['Final detailed statistics table is not shown; score 2-2 is from the preconcession board and global turn 11 from the visible banner at 393 seconds.','Full opponent hand and both exact 20-card lists are not established.','No post-concession continuation or guaranteed tactical outcome is inferred.','Primary visual review uses targeted native stills and state reconciliation, not exact simulator replay.']
}
unc={
 'source_filename':S['video_basename'],'source_sha256':S['sha256'],
 'unreviewed_intervals':[],'material_outcome_ambiguity':False,
 'uncertainties':[
  {'topic':'Final statistics','status':'not_shown','detail':'The recording ends on the Victory/Card of the Game page before a final detailed statistics table. Score 2-2 is read from the preconcession board; global turn 11 is from the visible banner at 393 seconds.'},
  {'topic':'Complete deck lists','status':'not_established','detail':'Selected deck name, Water Energy, 20/20 count and visible core are established. The lower deck grid and hidden opponent deck are not exhaustively shown.'},
  {'topic':'Hidden information and intent','status':'unknown','detail':'Opponent hand, unrevealed draws, reasons for long waits and concession, and unplayed alternatives are unknown.'},
  {'topic':'Exact event subsecond timing','status':'bounded','detail':'Times identify retained source-local frames and short action windows; no frame-by-frame transcript claimed.'},
  {'topic':'Counterfactual play','status':'not_established','detail':'The footage ends after explicit opponent concession at actual points 2-2. No guaranteed follow-up win or optimal next turn is claimed.'},
  {'topic':'Acceptance','status':'pending_independent_lead_check','detail':'Independent evidence check, shared completion event, external log and archive are lead responsibilities.'}
 ]
}
for name,obj in [('SUMMARY.json',summary),('UNCERTAINTIES.json',unc)]:
 (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
names=['SOURCE.json','REVIEW.md','SUMMARY.json','COVERAGE.md','UNCERTAINTIES.json']
paths=[P/n for n in names]+sorted((P/'evidence').glob('*.jpg'))
files={str(p.relative_to(P)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
manifest={'source_filename':S['video_basename'],'source_sha256':S['sha256'],'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'primary_review_frozen':True,'files':files}
(P/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
bad=[n for n,h in files.items() if hashlib.sha256((P/n).read_bytes()).hexdigest()!=h]
assert not bad,bad
print(json.dumps({'frozen_files':len(files),'native_frames':len(list((P/'evidence').glob('f_*.jpg'))),'hash_verification':'all_match','prefix':summary['exact_three_item_note_prefix'],'result':summary['result_method'],'score':summary['score']}))

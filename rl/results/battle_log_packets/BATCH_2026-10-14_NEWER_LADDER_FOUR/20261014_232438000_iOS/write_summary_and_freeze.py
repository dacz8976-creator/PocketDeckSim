from pathlib import Path
import json,hashlib,datetime
P=Path(__file__).parent
source=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
summary={
 'video_basename':source['video_basename'],'source_sha256':source['sha256'],'source_bytes':source['bytes'],'duration_seconds':source['duration_seconds'],
 'reviewer':'/root/newer_232438 continuing /root/evening_232438','assignment_event':'7d9bf3b5-1dc0-4e18-8a0c-12947dff814b','model':'gpt-6.1-sol','reasoning_effort':'high',
 'review_scope':'Full available recording, setup through complete result; primary review pending independent acceptance',
 'match_count':1,'battle_complete':True,'available_recording_fully_reviewed':True,'independent_acceptance':False,
 'match_date_local':'2026-10-14','source_creation_utc':'2026-10-14T23:24:38Z',
 'owner':'Dacz8976','opponent':'ててら','deck_label':'Deck 13-A','deck_core':['Alolan Vulpix','Alolan Ninetales ex','Team Rocket\u2019s Rattata','Team Rocket\u2019s Raticate ex'],
 'deck_list_complete':False,'opponent_visible_core':['Caterpie (Quick Growth)','Metapod (Ram30)','Butterfree (Sunny Wind60, heal20)'],
 'mode':'ladder by owner default; exact ranked queue/tier unestablished','auto_option_seen':False,'auto_enabled':None,'mega_form_seen':False,
 'turn_order':'first','global_turns':10,'owner_turns':5,'result':'loss','concession':False,'score':{'owner':0,'opponent':3,'basis':'result screen352s'},'damage_done':230,
 'main_attacker':'Alolan Ninetales ex','firstmainattack':{'attacked':False,'owner_own_turn':None,'global_turn':None,'opponent_points_before':None,'display':'Alolan Ninetales ex no attack; opp N/A'},
 'exact_three_item_note_prefix':'1st | Alolan Ninetales ex no attack | opp N/A',
 'supporting_attacks':[
 {'pokemon':'Alolan Vulpix','attack':'Gnaw','damage':20,'owner_own_turn':2,'global_turn':3,'time_seconds':[136,140],'opponent_points_before':0},
 {'pokemon':'Team Rocket\u2019s Raticate ex','attack':'Boost Dash','damage':70,'owner_own_turn':3,'global_turn':5,'time_seconds':[188,192],'opponent_points_before':1},
 {'pokemon':'Team Rocket\u2019s Raticate ex','attack':'Boost Dash','damage':70,'owner_own_turn':4,'global_turn':7,'time_seconds':[234,240],'opponent_points_before':2},
 {'pokemon':'Team Rocket\u2019s Raticate ex','attack':'Boost Dash','damage':70,'owner_own_turn':5,'global_turn':9,'time_seconds':[314,318],'opponent_points_before':2}],
 'point_progression':[{'time_seconds':170,'owner':0,'opponent':1,'event':'Sunny Wind knocks out first Vulpix'},{'time_seconds':218,'owner':0,'opponent':2,'event':'Sunny Wind knocks out second Vulpix after Sabrina'},{'time_seconds':352,'owner':0,'opponent':3,'event':'Giovanni Sunny Wind80 knocks out Raticate ex; result screen capped at3'}],
 'decisive_evidence':['evidence/t0330.00.jpg','evidence/t0334.00.jpg','evidence/t0338.00.jpg','evidence/t0344.00.jpg','evidence/t0352.00.jpg'],
 'important_observations':['Caterpie Quick Growth evolves at end of owner turn1','Thieving Incisors moves opponent Grass Energy to Raticate ex','Elegant Cape on basic Vulpix confers no Stage1 HP bonus','Four Lucky Ice Pop uses heal Butterfree80 total','Giovanni boosts final Sunny Wind60 to80 against Active ex'],
 'limitations_file':'UNCERTAINTIES.json','coverage_file':'COVERAGE.md','report_file':'REVIEW.md'}
unc={
 'source_sha256':source['sha256'],'unreviewed_intervals':[],
 'items':[
 {'topic':'Hidden information','status':'unknown','detail':'No full20-card owner or opponent list reconstructed; concealed cards and deck order remain unknown.'},
 {'topic':'Ranked queue/tier','status':'unknown','detail':'Owner ladder default applies. Exact queue or rank not visible.'},
 {'topic':'Opponent bench Energy','status':'bounded','detail':'Rear Butterfree130 has two Grass by290s. Some exact later attachment instants are not transcribed; active-attacker damage does not depend on them.'},
 {'topic':'Lucky Ice Pop first coin frame','status':'bounded','detail':'Four20-HP heals and repeated item use are visible. Heads at268/276 and final Tails284 retained. First successful-return coin exact result frame is not separately isolated; do not claim physical copy count.'}],
 'material_outcome_uncertainty':False,'main_attacker_ambiguity':False,'lead_acceptance_pending':True}
for name,obj in [('SUMMARY.json',summary),('UNCERTAINTIES.json',unc)]: (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files=[P/n for n in ['SOURCE.json','REVIEW.md','SUMMARY.json','COVERAGE.md','UNCERTAINTIES.json']]+sorted((P/'evidence').glob('*.jpg'))+sorted(P.glob('overview_*.jpg'))+sorted(P.glob('detail_*.jpg'))+[P/'clarification.jpg']
entries=[{'path':str(f.relative_to(P)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]
manifest={'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':source['sha256'],'model':'gpt-6.1-sol','reasoning_effort':'high','scope':'Immutable primary review and retained evidence; independent checker appends separate files','files':entries}
(P/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files_frozen':len(entries),'native_frames':len(list((P/'evidence').glob('*.jpg'))),'packet':str(P),'main_attacker_note':summary['exact_three_item_note_prefix']}))

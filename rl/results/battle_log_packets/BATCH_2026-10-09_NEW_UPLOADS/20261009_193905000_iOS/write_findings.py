import json
from pathlib import Path
p=Path(__file__).parent
s=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
d={
 'schema_version':1,'reviewer':'/root/review_193905','review_role':'first-pass Sol worker; inherited model/effort not independently exposed','review_date_utc':'2026-10-10','status':'first_pass_complete_pending_independent_acceptance',
 'source':{'filename':s['video_basename'],'sha256':s['sha256'],'bytes':s['bytes'],'duration_seconds':s['duration_seconds'],'width':1170,'height':2532,'source_identity_provenance':'lead intake verified SHA-256; in_progress event 58ec8e67-c335-4c61-b595-5c6e989e88ba'},
 'classification':{'computer_battle':True,'visible_ai_label':True,'queue_title':'Mega Charizard X ex Deck (Deluxe Pack: Mega)','selected_owner_deck_name':'Draft A: Shark Tempo','auto_enabled':True,'auto_mode_changes_observed':False,'choices_attributable_to_owner_manual_play':False,'eligible_ladder_log':False,'eligible_pause_games':False},
 'scope':{'matches':1,'turns':7,'opening_and_setup_reviewed':True,'all_turns_reviewed':True,'ending_reviewed':True,'source_intervals_reviewed':[[0,176.924377]],'unreviewed_turns':[],'linked_continuation_required':False},
 'outcome':{'winner':'Dacz8976','result':'Victory','owner_points':3,'opponent_points':1,'terminal_ko_seconds':[159,165],'third_point_seconds':[166,168],'victory_frame':'frames/action_160.jpg','victory_source_seconds':175.005,'card_of_game':'Alolan Ninetales ex','card_of_game_frame':'frames/action_161.jpg','card_of_game_source_seconds':176.005},
 'point_progression':[{'owner':0,'opponent':0},{'owner':0,'opponent':1,'ko':'Carvanha','seconds':[64,69]},{'owner':1,'opponent':1,'ko':'Torkoal 1','seconds':[96,103]},{'owner':2,'opponent':1,'ko':'Torkoal 2','seconds':[124,131]},{'owner':3,'opponent':1,'ko':'Charmander 1','seconds':[161,168]}],
 'mechanics_findings':[
 {'observation':'Misty gives 1 head then 1 tail, attaching first Water; normal Water attaches afterward','seconds':[84.8,94],'evidence':['frames/dense_163.jpg','frames/dense_187.jpg','frames/action_087.jpg','frames/action_088.jpg','frames/action_093.jpg']},
 {'observation':'AI turn 2 plays Copycat, not Research; five face-down redraws match owner five-card hand','seconds':[48.208,53.61],'evidence':['frames/dense_080.jpg','frames/dense_083.jpg','frames/dense_104.jpg']},
 {'observation':'AI turn 4 plays Research, draws hidden cards and attaches Fire to Bench Charmander; no attack','seconds':[110.2,114],'evidence':['frames/dense_205.jpg','frames/dense_208.jpg','frames/dense_220.jpg','frames/action_107.jpg']},
 {'observation':'Turn 6 Flame Patch takes Fire from discard and attaches to Active despite Binding Snow Energy Zone restriction; normal attachment goes to Bench','seconds':[140.835,149],'evidence':['frames/dense_293.jpg','frames/dense_303.jpg','frames/action_139.jpg']},
 {'observation':'All three Binding Snow knockouts receive Water weakness +20; final attack explicitly displays100','seconds':[94.8,165],'evidence':['frames/action_092.jpg','frames/action_118.jpg','frames/action_151.jpg']}
 ],
 'final_visible_state':{'owner_active':'Alolan Ninetales ex','owner_active_hp':120,'owner_active_attached_water':3,'owner_bench':[],'owner_hand':['Irida','Mega Sharpedo ex','Cyrus','Alolan Ninetales ex (alternate artwork)','Lucky Ice Pop','Alolan Vulpix (second artwork)'],'opponent_bench':[{'pokemon':'Charmander (second)','hp':70,'attached_fire':1}],'stadium':'Rainbow Cave','healing_observed':False,'tools_observed':False,'abilities_observed':False,'retreats_or_voluntary_switches_observed':False,'special_conditions_observed':False},
 'uncertainties':[
 'No exact20-card list; hidden deck and printing IDs unknown.',
 'Opponent normal draws, Research draws and Copycat redraw identities remain hidden.',
 'AI Poke Ball result is face-down; second Torkoal benched afterward is likely result, not explicit face-up reveal.',
 'Phone notification partly covers opponent fan on turn4; no exact fan count asserted there.',
 'Turn7 Energy Zone glow and next-generated label do not establish fourth attachment; readable Ninetales count remains3.',
 'Deck-title Mega Charizard X ex never enters play; title is matchup identity, not board evidence.'
 ],
 'evidence':{'action_frame_count':161,'targeted_dense_frame_count':348,'coarse_frame_count':35,'reused_intake_frame_count':4,'native_resolution':[1170,2532],'indexes':['FRAME_INDEX.json','DENSE_FRAME_INDEX.json'],'reports':['REVIEW.md','COVERAGE.md'],'dense_windows_seconds':[[22,24.5],[26,29],[32,36],[40,46],[48,58],[78,91],[108,120],[133,147],[154,159]]},
 'acceptance':{'independent_check_pending':True,'lead_acceptance_pending':True,'review_registration_performed_by_worker':False,'video_move_performed_by_worker':False,'external_log_mutation_performed':False,'simulator_edits_performed':False}
}
(p/'FINDINGS.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print('FINDINGS saved')

from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
P=Path(__file__).parent
s=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
unc=[
    {'topic':'Hidden information','limitation':'Opponent unrevealed hand/deck and exact full lists are unknown. Visible versions are identified by attacks and HP. No hidden card identities inferred.'},
    {'topic':'Attack time precision','limitation':'First Grass Knot commits between native278 and279 seconds and its named animation is visible at280; review uses approximately279 seconds, rather than claiming a frame-exact start.'},
    {'topic':'Review sampling','limitation':'Full visual review used coarse discovery plus targeted native samples, not a frame-by-frame transcript. All visible turns, meaningful actions and the terminal sequence are accounted for.'}
]
summary={
 'reviewer':'/root/ladder_142546','model':'gpt-6.1-sol','reasoning_effort':'high',
 'review_date':'2026-10-14','source_filename':s['video_basename'],'source_sha256':s['sha256'],
 'source_creation_utc':s['source_creation_utc'],'match_date_local':'2026-10-14',
 'battle_complete':True,'primary_review_complete':True,'independent_acceptance':False,'lead_acceptance':False,
 'recording_duration_seconds':s['duration_seconds'],'match_count':1,
 'owner_identifier':'Dacz8976','opponent_identifier':'まいちゃん',
 'identifier_evidence':['native/t0042.0.jpg','native/t0299.8.jpg'],
 'owner_visible_deck_core':['Spinarak','Ariados (Trap Territory/Pierce,90 HP)','Cottonee','Whimsicott ex (Grass Knot,140 HP)','Teal Mask Ogerpon ex (Soothing Wind/Energized Leaves,130 HP)'],
 'opponent_visible_deck_core':['Magikarp (Leap Out,30 HP)','Mantyke (Splashy Toss,30 HP)','Carvanha (Sharp Fang,50 HP)','Mega Sharpedo ex (Turbo Shark,190 HP)'],
 'deck_selected_label':'Deck 12','deck_selection_evidence':['native/t0007.0.jpg','native/t0010.0.jpg'],
 'outcome':'win','terminal_score':{'owner':3,'opponent':0},'terminal_timestamp_seconds':299.8,
 'terminal_evidence_paths':['native/t0281.0.jpg','native/t0282.0.jpg','native/t0287.0.jpg','native/t0299.8.jpg'],
 'terminal_reason':'Whimsicott ex Grass Knot deals160 and knocks out Mega Sharpedo ex; +3 award completes the owner point track. Victory confirms3-0.',
 'first_or_second':'first','first_or_second_evidence_timestamps_seconds':[33,36,299.8],
 'first_or_second_evidence_paths':['native/t0033.0.jpg','native/t0036.0.jpg','native/t0299.8.jpg'],
 'first_main_attacker_attack':{'pokemon':'Whimsicott ex','attack_name':'Grass Knot','own_turn_number':4,'global_displayed_turn':7,'source_time_seconds':279,'source_time_window_seconds':[278,280],'opponent_points_before_attack':0,'owner_points_before_attack':1,'damage':160,'evidence_paths':['native/t0227.0.jpg','native/t0277.0.jpg','native/t0278.0.jpg','native/t0279.0.jpg','native/t0280.0.jpg','native/t0281.0.jpg']},
 'main_attacker_interpretation':'Whimsicott ex is the deck finisher and Card of the Game. Ariados supports through two early Pierce attacks and retreat-cost abilities; its earlier attack is separately recorded, not substituted.',
 'earlier_supporting_attack':{'pokemon':'Ariados','attack_name':'Pierce','own_turn_number':2,'global_displayed_turn':3,'source_time_seconds':129,'opponent_points_before_attack':0,'damage':30,'target':'Mantyke','result':'knockout; owner first point','evidence_paths':['native/t0094.0.jpg','native/t0126.0.jpg','native/t0129.0.jpg','native/t0132.0.jpg','native/t0135.0.jpg']},
 'recommended_ladder_section':'deck 12 (Ariados / Whimsicott / Ogerpon)',
 'exact_three_item_note_prefix':'1st | Whimsicott ex T4 | opp 0 pts',
 'recommended_note':'1st | Whimsicott ex T4 | opp 0 pts. Ariados took Mantyke for1, then softened Carvanha. Two Ariados plus two Goo-zooka set Grass Knot160 to KO Mega Sharpedo ex for the win. Source: 20261014_142546000_iOS.MP4.',
 'mode':{'classification':'ladder human match','rank_visible':'Ultra Ball Rank4 for both players','rank_evidence':['native/t0029.0.jpg'],'auto_option_seen':False,'basis':'Owner ladder designation plus ranked introduction; no Auto contradiction in reviewed footage.'},
 'score_progression':[{'time_seconds':40,'owner':0,'opponent':0},{'time_seconds':135,'owner':1,'opponent':0},{'time_seconds':299.8,'owner':3,'opponent':0}],
 'damage_reconciliation':{'owner_attacks':[30,30,160],'owner_total':220,'result_screen_total':220,'opponent_attacks':[70]},
 'explicit_uncertainties':unc
}
(P/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(P/'UNCERTAINTIES.json').write_text(json.dumps({'source_filename':s['video_basename'],'blocking_uncertainties':[],'uncertainties':unc},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files={}
for f in sorted(P.rglob('*')):
    if f.is_file() and (f.suffix in ('.jpg','.json','.md')) and f.name!='REVIEW_PACKET_HASHES.json' and 'independent_sol' not in f.parts:
        files[f.relative_to(P).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
manifest={'source_filename':s['video_basename'],'source_sha256':s['sha256'],'reviewer':summary['reviewer'],'frozen_utc':datetime.now(timezone.utc).isoformat(),'files':files}
(P/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'frozen_files':len(files),'manifest_sha256':hashlib.sha256((P/'REVIEW_PACKET_HASHES.json').read_bytes()).hexdigest(),'native_frames':sum(1 for x in files if x.startswith('native/t'))},indent=2))

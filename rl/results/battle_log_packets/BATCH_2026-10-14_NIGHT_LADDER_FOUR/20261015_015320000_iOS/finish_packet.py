from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
P=Path(__file__).parent
SOURCE=json.loads((P/'SOURCE.json').read_text(encoding='utf-8-sig'))
def write(name,data):
    (P/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
write('SUMMARY.json',{
 'source_filename':'20261015_015320000_iOS.MP4','source_sha256':SOURCE['sha256'],
 'source_bytes':858013310,'duration_seconds':463.635,
 'reviewer':'/root/night_015320','model':'gpt-6.1-sol','reasoning_effort':'high',
 'review_scope':'Complete supplied recording including setup, all 11 global turns and terminal results',
 'battle_complete':True,'review_complete':True,'match_count':1,
 'independent_acceptance':'pending lead-assigned fresh checker',
 'match_date_local':'2026-10-14','timezone':'America/Chicago','recording_creation_utc':'2026-10-15T01:53:20Z',
 'mode':'ranked ladder','mode_evidence':['evidence/t0004.00.jpg','evidence/t0020.00.jpg'],
 'rank_visible':'Master Ball Rank','owner_queue_points_visible':758,
 'auto_option_seen':False,'auto_enabled_observed':False,
 'auto_limit':'No Auto option visible across reviewed setup/gameplay/result footage; no Auto operation observed.',
 'owner':'Dacz8976','opponent':'脳筋',
 'deck_label':'Deck 13-A','deck_core':['Alolan Vulpix','Alolan Ninetales ex','Team Rocket\'s Rattata','Team Rocket\'s Raticate ex'],
 'main_attacker':'Alolan Ninetales ex','owner_energy_types_visible':['Water'],
 'opponent_core':['Mega Rayquaza ex','Pichu','Gouging Fire','Dratini','Dragonair'],
 'result':'loss','termination':'opponent Mega Burst 200 KOs caped Alolan Ninetales ex',
 'score':{'owner':2,'opponent':3,'basis':'displayed terminal three-slot point indicators','pre_terminal_owner':2,'pre_terminal_opponent':2,'not_a_concession':True},
 'turn_order':'2nd','global_turns':11,'owner_turns':5,'opponent_turns':6,
 'first_main_attack':{'pokemon':'Alolan Ninetales ex','attack':'Binding Snow','owner_turn':4,'global_turn':8,'opponent_points_before_attack':2,'start_seconds_approx':319,'damage_seconds':320,'damage':80,'opponent_active':'Mega Rayquaza ex','hp_before':160,'hp_after':80,'evidence':['evidence/t0312.00.jpg','evidence/t0318.00.jpg','evidence/t0320.00.jpg','evidence/t0322.00.jpg']},
 'earlier_supporting_attacks':[{'pokemon':'Team Rocket\'s Rattata','attack':'Ambush','owner_turn':1,'coin':'tails','damage':20,'seconds':110},{'pokemon':'Team Rocket\'s Rattata','attack':'Ambush','owner_turn':2,'coin':'tails','damage_nominal':20,'remaining_hp_removed':10,'seconds':173},{'pokemon':'Alolan Vulpix','attack':'Gnaw','owner_turn':3,'damage':20,'seconds':262}],
 'exact_three_item_note_prefix':'2nd | MAIN Alolan Ninetales ex T4 | opp 2 pts',
 'decisive_evidence':['evidence/t0229.00.jpg','evidence/t0300.00.jpg','evidence/t0312.00.jpg','evidence/t0320.00.jpg','evidence/t0442.00.jpg','evidence/t0447.00.jpg','evidence/t0448.00.jpg','evidence/t0452.00.jpg','evidence/t0462.00.jpg'],
 'external_log_eligibility':'Ranked human-ladder evidence; lead owns duplicate check and any external entry',
 'external_logs_written_by_reviewer':False,'shared_log_or_index_written_by_reviewer':False,'source_moved_by_reviewer':False,
 'limits':['Full 20-card lists and hidden cards unknown','Dragonair small ability body text not transcribed; name and observed Energy changes retained','Individual attachment timings may be bounded by adjacent frames rather than exact instant','Displayed final score 2-3 retained without inventing fourth point']
})
write('UNCERTAINTIES.json',{
 'source_filename':'20261015_015320000_iOS.MP4','source_sha256':SOURCE['sha256'],
 'unreviewed_intervals':[],'unreviewed_turns':[],
 'material_unresolved_facts':[],
 'limits':[
 {'topic':'Full deck contents','detail':'Opening page displays part of Deck13-A; no complete 20-card snapshot. Hidden opponent cards and exact counts are unknown.'},
 {'topic':'Dragonair ability body text','times_seconds':[284,285,414,418],'detail':'Dragonair, 80 HP, Dragon\'s Blessing and Draconic Whip40 are readable. Small complete ability body is not transcribed. Ability activations and Rayquaza Lightning gains are observed; no generalized rules claim is made.'},
 {'topic':'Opponent attachment instants','detail':'Meaningful before/after Energy states and final transfers are reconciled. Some exact attachment instants are bounded by adjacent source frames.'},
 {'topic':'Final score','times_seconds':[447,448,452],'detail':'Owner2/opponent2 before terminal Ninetales ex knockout. Three-slot terminal display shows owner2/opponent3. No numeric fourth point is displayed or invented.'},
 {'topic':'Mode and Auto','detail':'Ranked Master Ball queue is visible. No Auto option is seen; absence claim is limited to reviewed footage.'},
 {'topic':'Strategic intent','detail':'No owner thought process, guaranteed alternate win or opponent hidden-card possession is inferred.'}
 ],'review_complete':True,'battle_complete':True,'independent_acceptance_pending':True
})
# Retain the complete four-second navigation coverage plus specifically cited
# original-resolution action frames; remove only our uncited extraction extras.
prose=(P/'REVIEW.md').read_text(encoding='utf-8')+(P/'COVERAGE.md').read_text(encoding='utf-8')
cited=set(re.findall(r't\d{4}\.\d{2}\.jpg',prose))
cited.update(f't{t:07.2f}.jpg' for t in range(0,461,4));cited.add('t0462.00.jpg')
for f in (P/'evidence').glob('t*.jpg'):
    if f.name not in cited:f.unlink()
# Keep compact overview plus focused action sheets, discard redundant tall sheets.
keep_sheets={'sheet_0000.00_0136.00.jpg','sheet_0144.00_0280.00.jpg','sheet_0288.00_0462.00.jpg','sheet_0004.00_0172.00.jpg','sheet_0180.00_0460.00.jpg','sheet_0046.00_0154.00.jpg','sheet_0198.00_0322.00.jpg','sheet_0334.00_0450.00.jpg','sheet_0018.00_0177.00.jpg'}
for f in P.glob('sheet_*.jpg'):
    if f.name not in keep_sheets:f.unlink()
missing=[x for x in re.findall(r't\d{4}\.\d{2}\.jpg',prose) if not (P/'evidence'/x).is_file()]
assert not missing,missing
tohash=['SOURCE.json','PROBE.json','ASSIGNMENT.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']
tohash+=sorted(str(f.relative_to(P)).replace('\\','/') for f in (P/'evidence').glob('*.jpg'))
tohash+=sorted(f.name for f in P.glob('sheet_*.jpg'))
tohash+=['dragonair_crop.png','tool_discard_crop.png']
files={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in tohash}
write('REVIEW_PACKET_HASHES.json',{'source_filename':'20261015_015320000_iOS.MP4','source_sha256':SOURCE['sha256'],'frozen_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root/night_015320','primary_edit_freeze':True,'files':files})
manifest=json.loads((P/'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256((P/n).read_bytes()).hexdigest()==h for n,h in manifest['files'].items())
write('HASH_VERIFICATION.json',{'verified_utc':datetime.now(timezone.utc).isoformat(),'files_checked':len(files),'all_match':True,'native_frame_count':len(list((P/'evidence').glob('*.jpg'))),'native_dimensions':[1170,2532],'review_packet_hashes_sha256':hashlib.sha256((P/'REVIEW_PACKET_HASHES.json').read_bytes()).hexdigest()})
print(json.dumps({'files_checked':len(files),'all_match':True,'native_frames':len(list((P/'evidence').glob('*.jpg'))),'packet':str(P)}))

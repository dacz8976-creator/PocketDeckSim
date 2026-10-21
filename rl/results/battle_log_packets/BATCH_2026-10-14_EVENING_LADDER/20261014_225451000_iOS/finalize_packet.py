from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
p=Path(__file__).parent
r=p/'REVIEW.md'
s=r.read_text(encoding='utf-8')
s=s.replace('Plays Elemental Switch at 146, transferring the single Lightning from benched 100-HP Rotom to Active 40-HP Rotom. Active now has two Lightning, Bench none. The zone Energy is left unused.', 'Attaches the turn\'s zone Lightning to benched 100-HP Rotom by 144, then plays Elemental Switch at 146, transferring that Lightning to Active 40-HP Rotom. Active now has two Lightning, Bench none, and the zone is empty.')
s=s.replace('`details/t0139.00.jpg`, `details/t0146.00.jpg`', '`details/t0139.00.jpg`, `details/t0144.00.jpg`, `details/t0146.00.jpg`')
r.write_text(s,encoding='utf-8')
c=p/'COVERAGE.md'
s=c.read_text(encoding='utf-8').replace('no-target Poké Ball, X Speed with no retreat, Elemental Switch, Junk Spark90.', 'no-target Poké Ball, X Speed with no retreat, zone Lightning to Bench, Elemental Switch, Junk Spark90.')
s=s.replace('then Sabrina promotes it and Elemental Switch supplies second from the now-benched other Rotom on global5.', 'then Sabrina promotes it. On global5 zone Lightning attaches to the now-benched other Rotom and Elemental Switch transfers that second Lightning to Active.')
c.write_text(s,encoding='utf-8')
summary={
 'source_filename':'20261014_225451000_iOS.MP4',
 'source_sha256':'42d70079e0c431c59af4c4c1475494fc718a4499e5bc73f8bcf6ea8bacde7582',
 'reviewer':'/root/evening_225451', 'review_date':'2026-10-14',
 'battle_complete':True,'match_count':1,'full_source_review_complete':True,
 'mode':{'classification':'human_ranked_ladder','auto_option_seen':False,'queue_evidence':'details/t0004.00.jpg','queue_label':'Season B4b SP, Ultra Ball Rank 4'},
 'deck':{'label':'Deck 13-A','core':['Alolan Vulpix','Alolan Ninetales ex','Team Rocket\'s Rattata','Team Rocket\'s Raticate ex'],'main_attacker':'Alolan Ninetales ex','complete_20_card_list_known':False,'evidence':'details/t0000.00.jpg'},
 'opponent':{'name':'ろっき','core':['Rotom ex'],'visible_pokemon_count':2,'evidence':'details/t0012.00.jpg'},
 'result':'win','result_method':'opponent_concession','score':{'owner':0,'opponent':0},
 'order':'second','global_turns_played':6,'damage_done':100,
 'first_main_attack':{'attacker':'Alolan Ninetales ex','attack':'Binding Snow','own_turn':2,'global_turn':4,'time_seconds':116,'opponent_points_before_attack':0,'damage':80,'evidence':['details/t0114.00.jpg','details/t0116.00.jpg','details/t0118.00.jpg','details/t0121.00.jpg']},
 'exact_three_item_note_prefix':'2nd | Alolan Ninetales ex T2 | opp 0 pts',
 'match_date':'2026-10-14','concession_time_seconds':161,
 'key_evidence_paths':{'deck':'details/t0000.00.jpg','ranked_queue':'details/t0004.00.jpg','first_main_attack':'details/t0116.00.jpg','before_first_attack':'details/t0114.00.jpg','global_turn_after_first_attack':'details/t0121.00.jpg','concession':'details/t0162.00.jpg','result_order_score':'details/t0171.30.jpg','opponent_energy_route_before_transfer':'details/t0144.00.jpg','opponent_attack':'details/t0152.00.jpg'},
 'uncertainties_file':'UNCERTAINTIES.json','coverage_file':'COVERAGE.md','review_file':'REVIEW.md','lead_acceptance':'pending_separate_lead_check','external_log_updated':False
}
(p/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
uncertainties={
 'reviewer':'/root/evening_225451','source_filename':summary['source_filename'],
 'material_outcome_uncertainties':[],
 'limits':[
 {'topic':'hidden_cards','detail':'Unrevealed opponent draws, hand and remaining deck are unknown.'},
 {'topic':'full_owner_list','detail':'Only editor visible upper core and gameplay trainers are identified, not every card in 20-card deck.'},
 {'topic':'timing','detail':'Action times are source-local approximate samples, generally within one or two seconds; first named Binding Snow at116.'},
 {'topic':'concession_reason','detail':'Opponent concession is explicit, its motivation is not recorded.'},
 {'topic':'sampling','detail':'End-to-end phases and meaningful actions checked through coarse orientation plus dense targeted native states; no claim of viewing every animation frame.'}
 ],'unreviewed_intervals':[],'missing_battle_ending':False
}
(p/'UNCERTAINTIES.json').write_text(json.dumps(uncertainties,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
files={}
for f in sorted(p.rglob('*')):
 if f.is_file() and f.name!='REVIEW_PACKET_HASHES.json':
  files[f.relative_to(p).as_posix()]=hashlib.sha256(f.read_bytes()).hexdigest()
manifest={'source_filename':summary['source_filename'],'source_sha256':summary['source_sha256'],'reviewer':summary['reviewer'],'frozen_utc':datetime.now(timezone.utc).isoformat(),'files':files}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files_hashed':len(files),'summary':summary['exact_three_item_note_prefix'],'packet':str(p)},ensure_ascii=False))

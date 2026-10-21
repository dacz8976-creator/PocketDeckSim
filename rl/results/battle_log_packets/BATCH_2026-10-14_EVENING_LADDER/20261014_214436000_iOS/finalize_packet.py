import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
p=Path(__file__).parent
source=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
summary={
 'source_filename':source['video_basename'], 'source_sha256':source['sha256'],
 'source_bytes':source['bytes'],'duration_seconds':source['duration_seconds'],
 'reviewer':'/root/evening_214436','model':'gpt-6.1-sol','reasoning_effort':'high',
 'review_date':'2026-10-14','match_date':'2026-10-14',
 'review_status':'primary_full_review_complete_pending_lead_acceptance',
 'battle_complete':True,'match_count':1,'all_visible_turns_reviewed':True,'global_turn_count':11,
 'mode':{'classification':'ranked_human','auto_option_seen':False,'auto_made_choices':False,
         'queue_label':'Season B4b SP; Ultra Ball Rank 4','evidence':['native/t0005.00.jpg','native/t0013.00.jpg']},
 'deck':{'visible_label':'Deck 13-A','visible_core':['Alolan Vulpix','Alolan Ninetales ex',"Team Rocket's Rattata","Team Rocket's Raticate ex"],
         'exact_20_card_list_verified':False,'main_attacker':'Alolan Ninetales ex',
         'other_visible_cards':['Ilima','Poke Ball','Field Blower','Soothing Shore',"Professor's Research",'Cyrus','Elegant Cape','Copycat','Sabrina'],
         'limits':"Team Rocket's Raticate ex is drawn/inspected, never played; no full list invented."},
 'opponent':{'name':'N.N','level':60,'visible_core':['Eevee','Espeon','Swablu','Mega Altaria ex','Darkrai','Igglybuff'],
             'notes':'Two non-ex Darkrai with Bad Dreams are visible.'},
 'result':'loss',
 'score':{'owner':1,'opponent':3,'convention':'final_display','visible_opponent_point_awards':[2,2],
          'note':'The terminal display caps opposing points at3; two +2 awards are visible.'},
 'order':{'owner':'second','evidence':'native/t0379.00.jpg'},
 'first_main_attack':{'pokemon':'Alolan Ninetales ex','attack':'Binding Snow','own_turn_number':3,'global_turn_number':6,
                      'source_time_seconds':205,'selection_source_time_seconds':203,'damage_source_time_seconds':207,
                      'opponent_points_before_attack':0,'damage':80,'target':'Igglybuff','knockout':True,
                      'evidence':['native/t0203.00.jpg','native/t0205.00.jpg','native/t0207.00.jpg','native/t0213.00.jpg','orientation/dense_sheet_012.jpg']},
 'exact_three_item_note_prefix':'2nd | Alolan Ninetales ex T3 | opp 0 pts',
 'note':"2nd | Alolan Ninetales ex T3 | opp 0 pts. Lost vs N.N. Double Darkrai Bad Dreams knocked out the first Ninetales after a tails sleep check; Mega Altaria ex then finished the second with130. Final displayed1-3,11 turns,160 damage.",
 'outcome_evidence':['native/t0364.00.jpg','native/t0365.00.jpg','native/t0371.00.jpg','native/t0379.00.jpg'],
 'decisive_sequence_evidence':['native/t0228.00.jpg','native/t0233.00.jpg','native/t0237.00.jpg','native/t0245.00.jpg','native/t0265.00.jpg','orientation/dense_sheet_017.jpg'],
 'packet_files':['SOURCE.json','REVIEW.md','COVERAGE.md','UNCERTAINTIES.json'],
 'evidence_paths':[str(p/'native'),str(p/'orientation')],
 'lead_acceptance_pending':True,'external_log_saved':False,'shared_registration_by_worker':False,'source_moved_by_worker':False,
 'uncertainties':['Exact full deck lists and hidden opponent draws/search return identities remain unknown.'],
}
(p/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
files={str(f.relative_to(p)).replace('\\','/'):hashlib.sha256(f.read_bytes()).hexdigest()
       for f in sorted(p.rglob('*')) if f.is_file() and f.name!='REVIEW_PACKET_HASHES.json'}
manifest={'source_filename':source['video_basename'],'source_sha256':source['sha256'],
          'frozen_utc':datetime.now(timezone.utc).isoformat(),'algorithm':'SHA256','files':files}
(p/'REVIEW_PACKET_HASHES.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files_frozen':len(files),'summary':str(p/'SUMMARY.json'),'review':str(p/'REVIEW.md')}))

"""Apply bounded independently evidenced corrections; retain prior drafts."""
import copy,json,shutil
from pathlib import Path
from PIL import Image
b=Path(__file__).resolve().parent;p=b/'20261010_015452000_iOS'
files=['DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json','REVIEW.md','COVERAGE.md']
for name in files:
 f=p/name;backup=p/(f.stem+'.before_independent_repairs'+f.suffix)
 if not backup.exists():shutil.copy2(f,backup)
deck=json.loads((p/'DECK_USED.json').read_text(encoding='utf-8'))
deck['conflicts_with_filmed_cards']=[]
deck['filmed_deck']['continuity_basis']='QR0s; edit screen3s shows Water; unsaved edit exit warning4s and continued deck screen6/8s also show Water; immediate matchmaking12s and same visible core. No Energy change is established.'
(p/'DECK_USED.json').write_text(json.dumps(deck,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
e=json.loads((p/'TURN_EVIDENCE.json').read_text(encoding='utf-8'))
for sec,observation in [(83,'Opponent turn2 normal draw settled: four visible card backs; faces hidden.'),(89,'Research has resolved by this view: five visible card backs; two drawn faces hidden.')]:
 src=p/f'independent_sol/source_check/t{sec:07.2f}.jpg'; dst=p/f'turn_evidence/t{sec:07.2f}.jpg'
 assert src.is_file();shutil.copy2(src,dst)
 with Image.open(dst) as im:
  w,h=im.size
  bottom=dst.with_name(dst.stem+'_bottom.jpg');top=dst.with_name(dst.stem+'_top.jpg')
  im.crop((0,2025,w,h)).save(bottom,quality=95);im.crop((0,0,w,600)).save(top,quality=95)
 frame=copy.deepcopy(e['frames'][0]);frame.update(evidence_id=f'f{sec:07.2f}',role='independent_repair_event',turn_number=2,who_played='opponent',
  requested_source_seconds=float(sec),full_frame_path=str(dst.relative_to(p)),before_first_play=sec==83,unzoomed=True,observation=observation)
 frame['bottom_crop']={'path':str(bottom.relative_to(p)),'pixel_bounds_x0_y0_x1_y1':[0,2025,w,h]}
 frame['top_crop']={'path':str(top.relative_to(p)),'pixel_bounds_x0_y0_x1_y1':[0,0,w,600]}
 assert not any(x['evidence_id']==frame['evidence_id'] for x in e['frames']);e['frames'].append(frame)
(p/'TURN_EVIDENCE.json').write_text(json.dumps(e,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
ledger=json.loads((p/'TURN_LEDGER.json').read_text(encoding='utf-8'));t=ledger['turns'][1]
t['timing']['draw_animation_end_seconds']=83
t['timing']['draw_end_precision']='Normal draw is settled by native83s; exact animation endpoint not measured.'
t['hand_at_start']['evidence_ids']=['f0083.00']
normal,research=t['draws_and_searches'];normal.update(timestamp_seconds=83,evidence_ids=['f0083.00'],limit_reason='Settled normaldraw at83s; exact endpoint not measured.')
normal['cards_in_reveal_order'][0].update(timestamp_seconds=83,evidence_ids=['f0083.00'])
research.update(timestamp_seconds=None,evidence_ids=['f0087.00','f0089.00'],observed_interval_seconds=[87,89],limit_reason='Research played by87; fivebacks at89. Hidden card faces and individual reveal times unavailable.')
for c in research['cards_in_reveal_order']:
 c.update(reveal_position=None,timestamp_seconds=None,evidence_ids=['f0087.00','f0089.00'],limit_reason='Two hidden draws resolved87–89; individual reveal ordering/time unavailable.')
t['turn_evidence_ids']+=['f0083.00','f0089.00']
(p/'TURN_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
f=p/'REVIEW.md';text=f.read_text(encoding='utf-8').replace('3s unsaved deck edit New deck13 briefly showsDarkness;4s Go Back Without Saving accepted;6/8s restored deck showsWater.','3s edit screen New deck13 shows Water;4s Go Back Without Saving warning and subsequent continued deck screen6/8s establish exit from the unsaved edit. No Energy change is shown.')
text=text.replace('Hidden normal draw; Professor\'s Research87 draws2hidden cards;','Hidden normal draw settled by83s; Professor\'s Research played by87, two hidden draws resolved by89s;')
text+='\nLead independent corrections: Native3/6/8 all show Water; no Darkness edit is established. Turn2 normal draw is settled by83s with four card backs, before Research removes one card by87s and its two hidden draws produce five backs by89s. The exact draw animation endpoint and hidden reveal ordering remain unavailable. Independent retained native83/89 and derived crops are now cited in the ledger.\n'
f.write_text(text,encoding='utf-8')
f=p/'COVERAGE.md';text=f.read_text(encoding='utf-8').replace('unsaved-edit warning, restoredWater configuration.','unsaved-edit exit warning, Water configuration throughout visible deck screens.');f.write_text(text,encoding='utf-8')
print('Bounded deck-edit and turn2 evidence corrections applied.')

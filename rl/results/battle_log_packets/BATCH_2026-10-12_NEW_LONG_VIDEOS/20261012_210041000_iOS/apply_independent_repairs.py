"""Source-grounded repairs after the rejected independent check; packet only."""
import json,hashlib,subprocess
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
P=Path(__file__).resolve().parent
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
def get(n):return json.loads((P/n).read_text(encoding='utf-8'))
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def eid(t):return 'N'+f'{t:07.2f}'.replace('.','_')
S=get('SOURCE.json');V=S['video_basename'];SHA=S['sha256'];L=get('TURN_LEDGER.json');E=get('TURN_EVIDENCE.json')

# R1: native241s shows the full readable Glimmet face, unlike240s.
copycat=next(x for x in L['turns'][7]['draws_and_searches'] if x['caused_by']=='Copycat')
copycat['cards_in_reveal_order'][0].update(timestamp_seconds=241,evidence_ids=[eid(241)],basis='Native individual Glimmet face at241s, after draw animation and before Poké Ball reveal')
copycat['timestamp_seconds']=241
copycat['evidence_ids']=[eid(t) for t in [241,242,243,244,245]]
copyplay=L['turns'][7]['plays_in_order'][0]
copyplay['nested_events_in_order']=[{'kind':'individual_named_draw_reveal','card_name':c['name'],'reveal_position':c['reveal_position'],'timestamp_seconds':c['timestamp_seconds'],'evidence_ids':c['evidence_ids']} for c in copycat['cards_in_reveal_order']]

# R2: neither turn1 opponent search exposes its acquired card face.
t1=L['turns'][0]
t1['timing']['first_voluntary_move_seconds']=79
t1['plays_in_order'][0].update(timestamp_seconds=79,evidence_ids=[eid(79),eid(80.6),eid(81)],result='Poké Ball puts one face-down Basic Pokémon into the opponent hand. The searched name is hidden; the later Riolu bench play is separate.')
t1['plays_in_order'][3].update(timestamp_seconds=92.4,evidence_ids=[eid(92.4),eid(93.8),eid(94.2)],result='Serena puts one face-down Mega Evolution Pokémon ex into the opponent hand. The acquired name is not shown; later Mega Lucario ex evolution does not identify this searched card.')
for x in t1['draws_and_searches']:
 if x['kind']!='search':continue
 isball=x['caused_by']=='Poké Ball'
 ts=80.6 if isball else 94.2
 ev=[eid(t) for t in ([79,80.6,81] if isball else[92.4,93.8,94.2,95.8])]
 reason=('Opponent Poké Ball acquisition is added face-down. Dense native78-84.2s inspection shows no acquired card face; the later named Riolu play is not proof of its acquisition source.' if isball else'Opponent Serena acquisition is added face-down. Dense native90.8-95.8s inspection shows Serena and the card back, no searched Mega Pokémon face. Later Mega Lucario ex evolution does not prove the search identity.')
 x.update(timestamp_seconds=ts,evidence_ids=ev,hand_count_before=4 if isball else 2,hand_count_after=5 if isball else 3,limit_reason=reason)
 x['cards_in_reveal_order']=[{'name':None,'category_from_filmed_trainer_text':'Basic Pokémon' if isball else'Mega Evolution Pokémon ex','reveal_position':1,'source_video':V,'timestamp_seconds':ts,'evidence_ids':ev,'basis':'One observed face-down addition after the named Trainer resolves','limit_reason':reason}]
t1['limits'].append('Poké Ball and Serena search acquisitions are hidden faces. Their names cannot be assigned from later bench/evolution plays.')

# R3: preserve approximate play time, explicitly link the filmed effect.
x=L['turns'][10]['plays_in_order'][1]
x['evidence_ids']=[eid(354)]
x['observed_effect_seconds']=354
x['nested_events_in_order']=[{'result':'X Speed is visible atop discard; Retreat Cost is1 less banner is displayed.','source_video':V,'timestamp_seconds':354,'evidence_ids':[eid(354)],'basis':'Named discarded card and visible effect banner'}]
x['limit_reason']='Approximate play time351s is distinct from the observed effect frame354s; exact tap time is not measured.'
L['turns'][10]['plays_in_order'][2]['evidence_ids']=[eid(358),eid(362)]
save('TURN_LEDGER.json',L)

# Catalog all newly retained frames and their native crops without changing old IDs.
ids={f['evidence_id'] for f in E['frames']}
for f in sorted((P/'turn_evidence').glob('t*.jpg')):
 if '_' in f.stem:continue
 t=float(f.stem[1:]);id=eid(t)
 if id in ids:continue
 im=Image.open(f);w,h=im.size;b=f.with_name(f.stem+'_bottom.jpg');top=f.with_name(f.stem+'_top.jpg')
 im.crop((0,2025,w,h)).save(b,quality=94);im.crop((0,0,w,770)).save(top,quality=94)
 role='independent_repair_named_reveal' if t==241 else'independent_repair_dense_source_inspection'
 obs='Full readable individual Glimmet reveal from Copycat.' if t==241 else'Bounded native inspection of face-down opponent Trainer acquisition.' if t<100 else'Bounded native inspection locating the individual Copycat reveal.'
 E['frames'].append({'evidence_id':id,'role':role,'turn_number':1 if t<100 else 8,'who_played':'opponent' if t<100 else'owner','source_video':V,'source_sha256':SHA,'draw_animation_end_seconds':None,'requested_source_seconds':t,'actual_frame_seconds_if_measured':None,'offset_after_draw_seconds':None,'full_frame_path':str(f.relative_to(P)).replace('\\','/'),'native_dimensions':{'width':w,'height':h},'bottom_crop':{'path':str(b.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,2025,w,h]},'top_crop':{'path':str(top.relative_to(P)).replace('\\','/'),'pixel_bounds_x0_y0_x1_y1':[0,0,w,770]},'selected_for_start_hand':False,'before_first_play':False,'unzoomed':False if t==241 else None,'hand_spread':False if t==241 else None,'observation':obs,'suitability_or_limit':'241s is a reveal, not pre-play start-hand evidence.' if t==241 else'Searched card identity stays null where the opponent acquisition remains face-down.' if t<100 else'Only a visibly readable card face is used to name a draw.'})
for f in E['frames']:
 if f['evidence_id']==eid(240):f['observation']='Copycat draw animation only; no Glimmet face and no owner hand in this frame. Individual Glimmet reveal is retained at241s.'
 if f['evidence_id']==eid(96):f['observation']='Stable Riolu board with Serena on opponent discard top; this is not a Mega Lucario ex reveal.'
 if f['evidence_id']==eid(354):f['observation']='X Speed atop discard and Retreat Cost is1 less banner; source-bound effect evidence for approximate351s play.'
E['independent_repair_notes']=['R1: Glimmet individual Copycat reveal bound to native241s, not240s.','R2: Turn1 Poké Ball and Serena produce face-down additions; searched names remain null. Later Riolu play and Mega Lucario ex evolution remain separately observed.','R3: X Speed play links354s named effect, with approximate351s play time retained separately.']
save('TURN_EVIDENCE.json',E)

limit={'id':'L5','topic':'Turn1 opponent search acquisitions','reason':'Poké Ball adds one face-down Basic Pokémon and Serena adds one face-down Mega Evolution Pokémon ex. Bounded dense native source inspection confirms no named acquired face is exposed. Later bench/evolution identities do not prove which search acquired them.','evidence':['TURN_LEDGER.json','TURN_EVIDENCE.json']}
U=get('UNCERTAINTIES.json');U['unresolved_facts'].append(limit);save('UNCERTAINTIES.json',U)
for n in ['PAUSE_GAME.json','SUMMARY.json']:
 d=get(n);d['limits' if n=='PAUSE_GAME.json' else'limitations'].append(limit);save(n,d)

# Replace only the affected narrative details, preserving all other accepted observations.
rp=P/'REVIEW.md';txt=rp.read_text(encoding='utf-8')
txt=txt.replace('Search obtains Riolu with Punch; opponent search reveal then bench placement establishes identity.','Put one face-down Basic Pokémon into the opponent hand. The searched name is hidden; Riolu with Punch is observed separately when benched at85s.')
txt=txt.replace('Search obtains Mega Lucario ex, publicly revealed at96.','Put one face-down Mega Evolution Pokémon ex into the opponent hand. No acquired name is exposed; the later Mega Lucario ex evolution does not identify this search acquisition.')
txt=txt.replace('Glimmet240s','Glimmet241s').replace('Glimmet 240s','Glimmet 241s')
txt=txt.replace('Reduce Active retreat cost by1 for this turn.','Reduce Active retreat cost by1 for this turn; native354s shows X Speed atop discard and the effect banner, separate from approximate351s play time.')
txt+='\nIndependent-check repairs: the individual Copycat Glimmet reveal is at241s. Turn1 Poké Ball and Serena acquisitions remain unnamed face-down cards; their triggers and one-card additions are observed, while later Riolu bench and Mega Lucario ex evolution are separate facts. X Speed links354s effect evidence. No independent acceptance is claimed by this repair.\n'
rp.write_text(txt,encoding='utf-8')
cp=P/'COVERAGE.md';cp.write_text(cp.read_text(encoding='utf-8')+'\nIndependent repair inspection: bounded native78-84.2s and90.8-95.8s Trainer/acquisition windows, plus240.2-241.8s Copycat reveal window. Poké Ball and Serena acquisition faces remain hidden; Glimmet individual face is readable at241s. Existing354s frame establishes the X Speed effect.\n',encoding='utf-8')

# Readable natural-language spacing, without altering IDs, hashes or paths.
import re
def walk(v):
 if isinstance(v,dict):return {k:walk(x) for k,x in v.items()}
 if isinstance(v,list):return [walk(x) for x in v]
 if isinstance(v,str):return re.sub(r'\b(at|by|native|approximate|turn|Turn)(?=\d)',r'\1 ',v)
 return v
for n in ['SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','TURN_LEDGER.json','TURN_EVIDENCE.json']:save(n,walk(get(n)))
for n in ['REVIEW.md','COVERAGE.md']:
 p=P/n;p.write_text(walk(p.read_text(encoding='utf-8')),encoding='utf-8')
py=r'C:/Users/dacz8/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
validator=P.parent.parent/'BATCH_2026-10-11_NEW_PAUSE_GAMES/validate_packet.py'
r=subprocess.run([py,'-X','utf8',str(validator),str(P)],capture_output=True,text=True,encoding='utf-8',check=False)
(P/'INDEPENDENT_REPAIR_VALIDATION.json').write_text(r.stdout,encoding='utf-8')
if r.returncode:raise RuntimeError(r.stdout+r.stderr)
hashes={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in names}
save('INDEPENDENT_REPAIR_HASHES.json',{'repaired_at_utc':datetime.now(timezone.utc).isoformat(),'source_video':V,'source_sha256':SHA,'eight_repaired_input_sha256':hashes,'independent_acceptance':False,'required_recheck':['R1 native241s Glimmet face','R2 hidden turn1 searches and no inferred acquisitions','R3 X Speed354s effect link']})
(P/'INDEPENDENT_REPAIR_MEMO.md').write_text('''# Independent repair memo

The rejected eight-file revision was preserved before editing in `before_independent_repairs_20261012T233320_842111Z`, with all eight hashes matching the checker freeze. The previous rejection and audit are unchanged.

- R1: bounded240.2-241.8s native extraction locates a readable individual Glimmet face at241.00s. The first Copycat card timestamp/reference and prose now use N0241_00. N0240_00 is explicitly only draw animation.
- R2: bounded90.8-95.8s native inspection shows Serena's face, then a face-down addition. The searched name is null; Mega Lucario ex's later evolution is separate. The copied Riolu-search basis is removed. The same hidden-face distinction was applied to turn1 Poké Ball after bounded78-84.2s inspection: one Basic is acquired face-down and Riolu is separately observed benched. No identity is derived from that later play.
- R3: approximate X Speed play time351s remains separate from the named effect at354s. N0354_00 is linked directly, and retreat links N0358_00/N0362_00.

All eight files remain consistent, with the added hidden-search limit in summary, uncertainties and Pause Game. The unchanged deck snapshot keeps its provenance. Structural validation passes with14 rows and no issues; it is not semantic acceptance. New eight-file hashes are in INDEPENDENT_REPAIR_HASHES.json. No shared registration, source move, external write or lead acceptance was performed. Ready for targeted independent recheck.
''',encoding='utf-8')
print(r.stdout)

from pathlib import Path
import json, hashlib, datetime
out=Path(__file__).parent
packet=out.parent.parent/'20260908_190031000'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
ledger=read(packet/'TURN_LEDGER.json')
ev=read(packet/'TURN_EVIDENCE.json')
expected=[(['Small Balloon','Copycat',"Professor's Research",'Poké Ball'],48),(['Copycat','Mega Altaria ex','Training Area'],102),(['Copycat','Mega Altaria ex','Training Area'],130),(['Copycat'],165.5)]
errors=[]
for r,(names,time) in zip(ledger['turns'],expected):
 h=r['owner_hand_end']
 if [c['name'] for c in h['cards_left_to_right']]!=names or h['count']!=len(names) or h['status']!='observed' or h['requested_source_seconds']!=time: errors.append('Ending hand mismatch turn '+str(r['turn_number']))
 def refs(x):
  result=set()
  if isinstance(x,dict):
   for k,v in x.items():
    if k in ('evidence_ids','turn_evidence_ids'): result.update(v or [])
    else: result.update(refs(v))
  elif isinstance(x,list):
   for v in x:result.update(refs(v))
  return result
 nested=refs({k:v for k,v in r.items() if k!='turn_evidence_ids'})
 if not nested.issubset(set(r['turn_evidence_ids'])): errors.append('Missing nested reference turn '+str(r['turn_number']))
expected_piles=[[],['pile_2_owner'],['pile_3_opponent'],['pile_4_owner','pile_4_opponent']]
for r,piles in zip(ledger['turns'],expected_piles):
 if r['discard_snapshot_ids']!=piles:errors.append('Pile binding mismatch')
if not ledger['turns'][0].get('discard_snapshot_limit'):errors.append('Turn1 missing unassigned-pile qualification')
q=ledger['turns'][2]['plays_in_order'][2]
if q['evidence_ids']!=['t0116.50','t0120.00','t0126.00'] or 'preceding' not in q['timestamp_basis'] or 'unmeasured' not in q['basis']:errors.append('Quick-Grow qualification mismatch')
text=(packet/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8-sig')
quick=[line for line in text.splitlines() if line.startswith('3. item: Quick-Grow')]
if not quick or not all(s in quick[0] for s in ['t0116.50 preceding','t0120.00/t0126.00 resolved']):errors.append('Readable Quick-Grow reference mismatch')
original=read(out/'BINDING_CHECK.json')
for item in original['image_files']:
 if hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()!=item['sha256']:errors.append('Evidence image changed: '+item['path'])
files=[]
for p in sorted(packet.glob('*')):
 if p.is_file() and p.suffix in ('.json','.md'):
  if p.suffix=='.json':read(p)
  else:p.read_text(encoding='utf-8-sig')
  files.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'read_encoding':'utf-8-sig'})
verdict='needs_repair' if errors else 'accepted_with_recording_limits'
result={'verdict':verdict,'source':'20260908_190031000_iOS.MP4','source_sha256':'2f68b969662a26fd6a79844ad00d7a3eb97ebde0bf790a25c273ff34d7d8cbf5','reviewer':'Sol independent different producer','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Recheck four ending hands, Quick-Grow preceding versus resolved references, and turn/discard serialization bindings only. Original independent needs_repair report preserved.','repairs_passed':['All four ending owner hands now observed with exact checked names/counts/native48/102/130/165.5.','Quick-Grow116.5 preceding state distinguished from120/126 evolution/recovery and resolved discard; exact input/PTS unmeasured. Readable references agree.','Every turn evidence union covers existing nested references; periodic pile2/3/4 IDs assigned. Turn1 has no snapshot assigned with explicit limit.','All129 previously bound evidence images unchanged; all current submitted JSON read using utf-8-sig and current raw byte SHA retained.'],'errors':errors,'limits_inherited_from':'SOURCE_CHECKS.json','metrics':{'new_original_video_reads':0,'new_extractions':0,'new_image_submissions':0,'original_image_submissions':30,'original_locator_samples_screened':168},'current_packet_files':files}
(out/'SOURCE_CHECKS_REPAIR_ACCEPTANCE.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'REPAIR_ACCEPTANCE.md').write_text('# Independent repair acceptance\n\nVerdict: '+verdict+'\n\nThe four ending owner hands are now directly recorded: turn1 Small Balloon, Copycat, Professor\'s Research, Poké Ball (4) at native48; turn2 Copycat, Mega Altaria ex, Training Area (3) at102; turn3 the same three at130; turn4 Copycat (1) at165.5. These match the images inspected in the original independent check.\n\nQuick-Grow now distinguishes native116.5 as the preceding Bulbasaur state and native120/126 as the resolved Ivysaur, recovery and closed Item discard. The readable action references agree. Exact input time and decoded PTS remain unmeasured.\n\nThe turn reference unions cover existing nested evidence. Periodic discard IDs now bind to their existing turn2/3/4 snapshots. Turn1 has no assigned snapshot with an explicit limit; full concealed piles remain unknown.\n\nAll43 native frames and86 crops retain their original byte hashes. Current packet files were read explicitly as utf-8-sig and bound in SOURCE_CHECKS_REPAIR_ACCEPTANCE.json. The original needs_repair reports remain separate. This repair check required no additional video reads, extraction or image submissions; original bounded inspection used30 native/crop submissions and all168 reduced locator samples. Previously reported recording, mode and hidden-information limits still apply. No new outcome audit was performed.\n',encoding='utf-8')
report=[]
for name in ['SOURCE_CHECKS_REPAIR_ACCEPTANCE.json','REPAIR_ACCEPTANCE.md']:
 p=out/name;p.read_text(encoding='utf-8-sig');report.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'read_encoding':'utf-8-sig'})
(out/'REPAIR_BINDING.json').write_text(json.dumps({'verdict':verdict,'reports':report,'packet_files':files},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'verdict':verdict,'errors':errors,'packet_files':len(files)}))

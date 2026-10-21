import json,pathlib,hashlib,datetime,collections
from PIL import Image,ImageChops
P=pathlib.Path(__file__).resolve().parent.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
S=read(P/'SOURCE.json');names=['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
catalog=pathlib.Path(r'C:\Users\dacz8\Projects\Pocket Deck Lab\s216_card_catalog_v1.json');aliases=read(catalog)['aliases']
by=collections.defaultdict(list)
for a in aliases:
 kind,num=a['entity_key'].split(':');by[f'{kind}:{int(num)}'].append(a)
qr=read(P/'qr_intake/QR_DECODE_0001.00.json');edited=read(P.parent/'EDITED_DECK_ENTRY.json')['decks'][0]
supp=[P/'DECK_EDIT_LEDGER.json',P/'CORRECTION_LEDGER.json',P/'RELATED_GAME_PACKETS.json',P/'HANDOFF.md',P/'RECORDING_METADATA.json',P.parent/'EDITED_DECK_ENTRY.json',P/'qr_intake/QR_DECODE_0001.00.json',P/'qr_intake/t0001.00.png',catalog]
for sub in ['', 'game_02']:
 q=P/sub;e=read(q/'TURN_EVIDENCE.json');l=read(q/'TURN_LEDGER.json');errs=[];frames=e['frames'];ids={f['evidence_id'] for f in frames};maes=[];checked=[]
 for f in frames:
  fp=q/f['full_frame_path'];im=Image.open(fp).convert('RGB');w,h=im.size
  if (w,h)!=(1170,2532):errs.append([f['evidence_id'],'native size',im.size])
  if f['source_video']!=S['video_basename'] or f['source_sha256']!=S['sha256']:errs.append([f['evidence_id'],'source binding'])
  for role in ['bottom_crop','top_crop']:
   c=f[role];bounds=c['pixel_bounds_x0_y0_x1_y1'];ci=Image.open(q/c['path']).convert('RGB');x0,y0,x1,y1=bounds
   if not(0<=x0<x1<=w and 0<=y0<y1<=h) or ci.size!=(x1-x0,y1-y0):errs.append([f['evidence_id'],role,'bounds'])
   if role=='bottom_crop' and bounds!=[0,2025,1170,2532]:errs.append([f['evidence_id'],'bottom fifth'])
   if len(checked)<24 or f['selected_for_start_hand']:
    diff=ImageChops.difference(im.crop(bounds),ci)
    if diff.getbbox():errs.append([f['evidence_id'],role,'crop pixels mismatch'])
    maes.append(0 if not diff.getbbox() else 1)
  checked.append(f['evidence_id'])
 def refs(obj):
  if isinstance(obj,dict):
   for k,v in obj.items():
    if k.endswith('evidence_ids') and isinstance(v,list):
     for x in v:
      parentids={f['evidence_id'] for f in read(P/'TURN_EVIDENCE.json')['frames']} if sub and k=='source_proof_evidence_ids' else set()
      if isinstance(x,str) and x.startswith('f') and x not in ids and x not in parentids:errs.append(['reference',k,x])
    else:refs(v)
  elif isinstance(obj,list):
   for v in obj:refs(v)
 for n in ['TURN_LEDGER.json','PAUSE_GAME.json','DECK_USED.json']:refs(read(q/n))
 for n in ['SOURCE.json','SUMMARY.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json']:
  d=read(q/n)
  if d.get('is_template'):errs.append([n,'template'])
 deck=read(q/'DECK_USED.json')
 if not sub:
  slots=deck['source_cards_in_qr_order'];counts=deck['source_counts_by_semantic_entity']
  got=collections.Counter((r['entity_kind'],r['semantic_entity_id']) for r in slots)
  expected=collections.Counter({(r['entity_kind'],r['entity_id']):r['count'] for r in qr['cards']})
  exact=got==expected and len(slots)==20 and sum(r['count'] for r in counts)==20
 else:
  counts=deck['source_counts_by_name_and_variant'];exact=sum(r['count'] for r in counts)==20 and sum(c['count'] for c in edited['cards_in_display_order'])==20 and len(edited['card_slots'])==20
 semantic=[]
 for c in edited['cards_in_display_order']:
  key=f"{c['entity_kind']}:{c['entity_id']}";rows=by[key];func={a['functional_id'] for a in rows}
  ok=bool(rows) and func=={c['functional_id']} and c.get('printing') is None
  semantic.append({'entity_key':key,'count':c['count'],'functional_match':ok,'aliases':sorted({a['raw_name'] for a in rows})})
  if not ok:errs.append(['edited semantic',key])
 out={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frames':len(frames),'crops':len(frames)*2,'all_files_decode_and_bounds_pass':not any('size' in str(v) or 'bounds' in str(v) for v in errs),'source_media_rehashed':False,'native_dimensions':[1170,2532],'reference_and_source_binding_errors':errs,'crop_pixel_comparisons':len(maes),'all_compared_crop_pixels_equal':not any(maes),'ledger_turn_count':len(l['turns']),'turn_numbers':[r['turn_number'] for r in l['turns']],'exact20_arithmetic_and_qr_or_edited_counts_pass':exact,'catalog_sha256':sha(catalog),'edited_semantic_mapping':semantic,'checked_input_sha256':{n:sha(q/n) for n in names},'checked_supplemental_sha256':{str(f.resolve()):sha(f) for f in supp},'limit':'Structural decoding, crop binding and count checks are separate from source visual acceptance.'}
 (q/'independent_sol'/'STRUCTURAL_CHECK.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8');print(sub,len(frames),'frames','errors',errs,'exact20',exact)

import json,shutil
from pathlib import Path
from datetime import datetime,timezone

B=Path(__file__).resolve().parent
P=B/'20260908_190031000'
backup=P/'before_independent_field_repair'
files=['TURN_LEDGER.json','REVIEW_SUPPLEMENT.md','UNCERTAINTIES.json']
if not backup.exists():
    backup.mkdir()
    for f in files:shutil.copy2(P/f,backup/f)
else:
    assert not (P/'FIELD_REPAIR_RECEIPT.json').exists(), 'Completed repair already exists'
    for f in files:shutil.copy2(backup/f,P/f)
hands={1:(48,['Small Balloon','Copycat',"Professor's Research",'Poké Ball']),
 2:(102,['Copycat','Mega Altaria ex','Training Area']),
 3:(130,['Copycat','Mega Altaria ex','Training Area']),
 4:(165.5,['Copycat'])}
ledger=json.loads((P/'TURN_LEDGER.json').read_text(encoding='utf-8-sig'))
for row in ledger['turns']:
    time,names=hands[row['turn_number']]
    eid=f't{time:07.2f}'
    row['owner_hand_end']={'cards_left_to_right':[{'position':i+1,'name':name,
      'basis':'native full-width ending hand','evidence_ids':[eid],'limit_reason':None} for i,name in enumerate(names)],
      'count':len(names),'basis':'Direct native ending fan at cited boundary.',
      'evidence_ids':[eid],'status':'observed','limit_reason':None,
      'source_video':'20260908_190031000_iOS.MP4','requested_source_seconds':time,
      'actual_frame_seconds_if_measured':None}
    row['turn_evidence_ids']=sorted(set((row.get('turn_evidence_ids') or [])+[eid]))
    if row['turn_number']==3:
        play=next(p for p in row['plays_in_order'] if p.get('card_name')=='Quick-Grow Extract')
        play['evidence_ids']=['t0116.50','t0120.00','t0126.00']
        play['basis']='Native116.5 is preceding Bulbasaur state. Native120 shows evolution/recovery; native126 corroborates Ivysaur and closed Quick-Grow discard. Inherited exact input anchor remains unmeasured.'
        play['timestamp_basis']='116.5 is preceding-state requested seek, not a measured resolved-action instant.'
        play['limit_reason']='Evolution and recovery directly supported by120/126; exact Item input time not certified.'
(P/'TURN_LEDGER.json').write_text(json.dumps(ledger,indent=2,ensure_ascii=False),encoding='utf-8')
text=(P/'REVIEW_SUPPLEMENT.md').read_text(encoding='utf-8-sig')
text+='\nIndependent field repair: ending owner hands are now populated in all four turn rows from native48 (four cards),102 (three),130 (three) and165.5 (one Copycat). Quick-Grow uses native116.5 only as its preceding-state anchor, with evolution/recovery supported by120 and the resolved Ivysaur/closed Item discard corroborated by126. Exact input time remains unmeasured.\n'
(P/'REVIEW_SUPPLEMENT.md').write_text(text,encoding='utf-8')
u=json.loads((P/'UNCERTAINTIES.json').read_text(encoding='utf-8-sig'))
u['quick_grow_timing_qualification']='116.5 precedes Quick-Grow resolution;120/126 support the resolved evolution/recovery and discard. Exact input time is unmeasured.'
(P/'UNCERTAINTIES.json').write_text(json.dumps(u,indent=2,ensure_ascii=False),encoding='utf-8')
(P/'FIELD_REPAIR_RECEIPT.json').write_text(json.dumps({'schema':'bounded-independent-field-repair-v1',
 'utc':datetime.now(timezone.utc).isoformat(),'source':'20260908_190031000_iOS.MP4',
 'changed_files':files,'prior_versions':str(backup),'new_source_reads':0,'new_frames':0,
 'independent_recheck_pending':True,'old_packet_unchanged':True},indent=2),encoding='utf-8')
print('Populated four ending hands and qualified Quick-Grow evidence; recheck pending.')

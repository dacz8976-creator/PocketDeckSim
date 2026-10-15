"""Apply two source-checked, independently requested corrections; preserve first pass."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

B = Path(__file__).resolve().parent
P = B/'20261002_210612000_iOS_auto_sol'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,o): p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

original = read(P/'SUBMISSION.json')
assert sha(P/'SUBMISSION.json') == '9489c54b6a89b2387ab1a988555385358a6ab5f4d097ce70562577a44637bd5b'
assert not (P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json').exists()
for name,expected in original['files'].items():
    assert sha(P/name) == expected, name
raw=P/'worker_submission'
raw.mkdir(exist_ok=False)
for name in list(original['files'])+['SUBMISSION.json']:
    target=raw/name;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(P/name,target)
    assert sha(target)==sha(P/name)

ledger=read(P/'TURN_LEDGER.json')
t8=ledger['turns'][7]['board_after']
assert t8['evidence_ids']==['F0124.50']
assert len(t8['opponent']['board_effects'])==1
t8['opponent']['board_effects']=[]
t8['turn_number_displayed']=9
t8['turn_number_displayed_limit']=None
t8['phase']='T8-to-T9 handoff: Current Turn 9 banner shown; opponent-turn Binding Snow restriction expired; owner Energy generation pending'
t8['effect_expiry_provenance']={'effect':'Binding Snow','status':'expired','target':'opponent player Active position during T8 only','evidence_ids':['F0123.50','F0124.50','F0128.20'],'basis':'Printed next-opponent-turn duration; native F0124.50 already shows Current Turn 9 and no blocked icon. Restriction remains at T8 start and during retreat.'}

t3=ledger['turns'][2]
mon=t3['board_after']['owner']['active']
assert mon['hp_now']==mon['hp_max']==180 and mon['damage']==0
assert mon['attribute_provenance']['name_hp_position']==['F0049.40']
mon['attribute_provenance']['name_hp_position']=['F0049.40','F0052.00']
mon['attribute_provenance']['resolved_hp']={'hp_now':180,'hp_max':180,'evidence_ids':['F0052.00'],'basis':'Settled HP after uninterrupted Cape animation; composite endpoint provenance, later than before-end hand anchor.'}
mon['attribute_provenance']['transient_hp_animation']={'displayed_hp':170,'evidence_ids':['F0049.40'],'basis':'Intermediate count-up after Elegant Cape; not the resolved effective HP.'}
mon['evidence_ids']=['F0049.40','F0052.00']
mon['hp_max_basis']='Elegant Cape +30 from printed150; native F0049.40 transient170, F0052.00 settled180 through continuous footage'
mon['limit_reason']='Composite resolved endpoint: before-end hand, position and Energy at F0049.40; settled HP180 confirmed at F0052.00 after the Cape count-up. These are distinct observations.'
tool=t3['plays_in_order'][3]
assert tool['card_name']=='Elegant Cape'
tool['result']='Elegant Cape increases effective maximum/current HP150 to180; F0049.40 shows transient170 during count-up, F0052.00 confirms settled180'
tool['evidence_ids']=['F0048.90','F0049.40','F0052.00']
save(P/'TURN_LEDGER.json',ledger)

review=(P/'REVIEW.md').read_text(encoding='utf-8-sig')
before='4. tool Elegant Cape, target O-V1: Effective maximum/current HP 150 -> 180 (F0048.90).'
assert review.count(before)==1
after='4. tool Elegant Cape, target O-V1: Effective maximum/current HP 150 -> 180. F0048.90 shows attachment; the before-end hand at F0049.40 shows the intermediate HP count-up at 170. F0052.00 confirms settled 180 HP, Cape and one Water through uninterrupted footage. The resolved endpoint therefore uses composite HP provenance.'
review=review.replace(before,after)
(P/'REVIEW.md').write_text(review,encoding='utf-8')

changed=[n for n,s in original['files'].items() if sha(P/n)!=s]
assert set(changed)=={'TURN_LEDGER.json','REVIEW.md'}
receipt={'repaired_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'/root','model_attribution':'root coordinator; no Astra review claimed','source_video':original['source_video'],'source_sha256':original['source_sha256'],'original_submission_sha256':sha(P/'SUBMISSION.json'),'original_files_preserved':{n:sha(raw/n) for n in original['files']},'independent_findings_sha256':sha(P/'independent_sol/CHECK_RESULT.json'),'corrected_items':['R1: expired player-level Binding Snow at observed T8-to-T9 handoff','R2: Cape transient170 versus settled180 HP provenance'],'lead_independently_inspected_images':['turn_evidence/t0049.40.jpg','turn_evidence/t0052.00.jpg','turn_evidence/t0124.50.jpg'],'changed_files':{n:{'before':original['files'][n],'after':sha(P/n)} for n in changed},'pending':'Same independent Sol must confirm effective files before acceptance; latest guide supplement remains separate.'}
save(P/'REPAIR_RECEIPT.json',receipt)
effective=dict(original)
effective.update({'submitted_utc':receipt['repaired_utc'],'review_status':'repaired_pending_independent_recheck','original_submission_manifest':'worker_submission/SUBMISSION.json','original_submission_manifest_sha256':sha(raw/'SUBMISSION.json'),'repair_receipt':'REPAIR_RECEIPT.json','files':{n:sha(P/n) for n in original['files']}})
effective['files']['REPAIR_RECEIPT.json']=sha(P/'REPAIR_RECEIPT.json')
save(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json',effective)
print(json.dumps({'changed':changed,'originals_preserved':len(original['files']),'effective_manifest_sha256':sha(P/'SUBMISSION_AFTER_INDEPENDENT_REPAIR.json')}))

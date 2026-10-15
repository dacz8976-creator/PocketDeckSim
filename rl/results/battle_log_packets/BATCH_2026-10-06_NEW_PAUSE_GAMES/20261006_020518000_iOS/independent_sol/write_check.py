import base64, collections, hashlib, json, sys
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent/'qr_dependencies'))
import zxingcpp

p=Path(__file__).resolve().parent.parent
out=p/'independent_sol'
def read(f): return json.loads(f.read_text(encoding='utf-8'))
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def save(name,obj): (out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
integrity=read(out/'INPUT_INTEGRITY.json')
qr=read(p/'qr_intake/QR_DECODE_0002.00.json')
code=zxingcpp.read_barcodes(Image.open(p/'qr_intake/t0002.00.png'))[0].text
assert code==qr['payload']
b=base64.b64decode(code); i=0; groups=[]
for kind in ['trainer','pokemon']:
    n=b[i];i+=1; ids=[]
    for _ in range(n):
        v=int.from_bytes(b[i:i+3],'big'); i+=3
        ids.append(v-10000000 if kind=='trainer' else v)
    groups.append(ids)
n=b[i];i+=1;energy=list(b[i:i+n]);i+=n
assert i==len(b) and len(groups[0])+len(groups[1])==20 and energy==[6]
catpath=Path(qr['dependencies']['catalog']);cat=read(catpath)
mapping={}
for kind,ids in zip(['trainer','pokemon'],groups):
    for entity in set(ids):
        aliases=[a for a in cat['aliases'] if a['entity_key'].split(':')[0]==kind and int(a['entity_key'].split(':')[1])==entity]
        mapping[f'{kind}:{entity}']={'names':sorted(set(a['raw_name'] for a in aliases)), 'variants':sorted(set(a['deckgym_id'] for a in aliases)), 'count':ids.count(entity)}
deck=read(p/'DECK_USED.json')
for slot in deck['filmed_qr']['cards_in_payload_order']:
    item=mapping[f"{slot['entity_kind']}:{slot['entity_id']}"]
    assert slot['name'] in item['names'] and sorted(slot['printing_aliases'])==item['variants']
save('QR_RECHECK.json',{'checked_at_utc':datetime.now(timezone.utc).isoformat(),'native_image_payload_match':True,'payload_ascii_sha256':hashlib.sha256(code.encode('ascii')).hexdigest(),'trainer_ids':groups[0],'pokemon_ids':groups[1],'energy_types':energy,'card_count':20,'semantic_entity_mapping':mapping,'limits':['Community-derived pinned catalog supplies entity mapping; QR does not encode artwork or rarity. Matching live log deck version remains absent, separately from exact filmed semantic list.']})
full='0028.00 0059.50 0070.00 0072.00 0075.00 0079.00 0084.00 0093.00 0179.00 0181.00 0376.00 0378.00 0380.00 0388.00 0408.50 0418.00 0429.00 0344.00 0345.00 0350.00 0353.00 0360.00 0061.50 0064.50 0095.50 0097.50 0100.50 0159.50 0161.50 0164.50 0199.50 0202.50 0265.40 0267.40 0270.40 0333.50 0335.60 0338.60 0433.50 0435.50 0438.50 0486.50 0488.50 0491.50 0571.50 0573.50 0576.50 0490.00 0493.00 0495.00 0577.00 0578.00 0579.00 0582.00 0591.00 0594.00 0004.00 0007.00 0012.00 0024.00 0139.00 0194.00 0261.00 0330.00 0366.00'.split()
starts='0094.50 0158.30 0197.50 0264.00 0332.80 0433.00 0485.60 0570.00'.split()
ends='0062.00 0109.00 0161.50 0216.50 0281.00 0353.00 0440.00 0505.50 0573.00'.split()
viewed=[f'turn_evidence/t{t}.jpg' for t in full]+[f'turn_evidence/t{t}_{s}.png' for t in starts for s in ['bottom','top']]+[f'turn_evidence/t{t}_bottom.png' for t in ends]+['qr_intake/t0002.00.png']
save('VIEWED_EVIDENCE.json',{'reviewer':'independent_sol','scope':'Fresh bounded acceptance review of retained native evidence, beyond special targets; not a substitute full first pass.','viewed_native_paths':sorted(set(viewed)),'ordinary_anchors':{'opening_before_active':28,'first_owner_decision':[59.5,61.5,64.5],'ordinary_opponent_T2':[70,72,75,79,84,93],'ordinary_T6':[179,181],'ordinary_T12':[376,378,380,388,408.5,418,429]},'all_27_scheduled_candidates_visually_inspected':True,'all_nine_owner_start_hands_and_before_end_crops_inspected':True,'all_native_crops_and_bounds_verified_by_pixel_equality':True,'integrity_receipt':'INPUT_INTEGRITY.json'})
supplement={f:sha(p/f) for f in sorted(set(viewed))}
for f in ['qr_intake/QR_DECODE_0002.00.json','../LIVE_DECK_SNAPSHOT.json','../NEW_DECK_ENTRIES.json','../QR_INTAKE_CATALOG.json']:
    supplement[f]=sha(p/f)
for k in ['codec','reader','catalog']: supplement[qr['dependencies'][k]]=sha(Path(qr['dependencies'][k]))
repairs=[
 {'id':'R1','files':['TURN_LEDGER.json'],'issue':'Generic per-play input_and_resolution_distinction overstates scheduled pre-action citations as first public input/presentation. T2 72s still current Metal before transfer (75s attached); T12 376s still two Metal/current Metal, 378s three attached but May not yet presented (380s); T13 435.5s current Energy still unselected, 438.5s Energy is held in target selection and not yet attached; T17 570s is pre-attachment while 571.5s shows transfer.','required_repair':'Use cited interval anchors and source-local onset/resolution windows or qualify timestamp as pre-action reference; do not claim remote tap or first public input from these frames. Preserve verified attachment/play order and subsequent resolved states.'},
 {'id':'R2','files':['TURN_EVIDENCE.json'],'issue':'Capture suitability metadata does not consistently describe the retained pixels. f0161_50 has enlarged Active/attack-retreat overlay but unzoomed=true. f0100_50 is coin resolution, not completed Ice Pop discard. f0438_50 shows held Energy/target selection, not completed attachment. f0435_50 is hand selection/current Energy still available, not yet Energy target selection. f0095_50/f0097_50/f0199_50/f0488_50/f0491_50/f0576_50 are normal-scale battlefield/effect/resolution views with no enlarged-card zoom despite unzoomed=false.','required_repair':'Correct zoom flags independently of before-first-play and hand usefulness; describe overlays, coin/heal effects and target selection accurately. Keep late or occluded candidates rejected as intact pre-play hand even where unzoomed=true. Qualify the 161.5s before-end hand as attack-selection overlay, not intact unzoomed battlefield.'}
]
receipt={'schema':'pause-games/independent-sol-acceptance-v1','reviewer':'independent_sol','game_id':p.name,'checked_at_utc':datetime.now(timezone.utc).isoformat(),'result':'rejected','accepted':False,'source_video':'20261006_020518000_iOS.MP4','source_sha256':qr['source_sha256'],'duration_seconds':616.08966,'checked_input_sha256':integrity['checked_input_sha256'],'supplemental_checked_input_sha256':supplement,'source_backed_findings':['Opening five and ordinary first owner decision agree; End Turn retains four without attachment/evolution/attack.','Full ordinary opponent T2 agrees: Metal to Tinkatink, Research hidden two draws, Cufant bench left, Lunge Out 20.','Ordinary T6 Copperajah evolution precedes second Metal on Stakataka.','Ordinary T12 third Copperajah Metal precedes May hidden two draws/two returns, Tinkatink/Cufant bench, Heavy Impact 80.','All nine owner start hands, end hands and opponent fan counts support ledger identities/counts; all 27 scheduled draw-offset candidate pixels were inspected.','Both boards and current versus next Energy Zones remain separated. Tools and Stadium use observed none with basis, not unexplained null.','All six non-null displayed-turn numbers 4/7/9/11/12/13 are readable in cited native transition frames; concluded phase is separately encoded.','Wally Colorless attachment then normal Fighting, one-Fighting retreat payment/retained one, Bedrock KO and point agree.','Research named reveal order Poké Ball then Timburr and subsequent Ball search Hitmonchan ex agree.','Terminal frames separately establish Copperajah HP 0 at577, empty Active578, discard preview579, third point582, Victory591/594; human Event Adgbag, owner first, 17-turn 3-2 win.','Native QR independently decodes to same exact20 semantic entities and Fighting, including distinct Conkeldurr A3/B4 and Sandslash B2/A1. Matching live log list/version absence and artwork limits remain qualified.'],'integrity':{'frame_count':292,'image_count':876,'native_crop_pixel_equality_and_bounds_passed':True,'unresolved_evidence_references':[]},'remaining_repairs':repairs,'limits':['No redundant full replay or source-media reopening. Full first pass remains separate.','Hidden opponent draws/May returns, unopened discard piles, QR artwork and missing matching live log deck version stay unknown or qualified.','Native seeks supply requested source-local anchors, not measured exact PTS.'],'external_changes_made':False,'canonical_edits_made':False}
save('CHECK_RESULT_REJECTED_R1_R2.json',receipt)
save('CHECK_RESULT.json',receipt)
print('Wrote rejected independent receipt, viewed evidence and QR recheck. Repairs R1/R2; native dimensions/crops/source bindings passed.')

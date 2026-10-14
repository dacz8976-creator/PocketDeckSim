import hashlib, json, shutil
from pathlib import Path
from datetime import datetime, timezone

p=Path(__file__).resolve().parent.parent
out=p/'independent_sol'
freeze=json.loads((p/'REVIEW_PACKET_HASHES.json').read_text(encoding='utf-8-sig'))
checked={n:hashlib.sha256((p/n).read_bytes()).hexdigest() for n in freeze['files']}
stable=checked==freeze['files']
if not stable:
    raise SystemExit('Frozen eight changed during independent check. Refuse to record mismatched inputs.')
rejected=out/'rejected_8_v1'
rejected.mkdir(exist_ok=False)
for name in [*checked,'REVIEW_PACKET_HASHES.json']:
    shutil.copy2(p/name,rejected/name)
result={
 'schema':'pause_games_independent_source_check_v1',
 'checked_utc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'/root/check_remaining_010837',
 'model_effort':'Sol/high',
 'scope':'Separate bounded source acceptance of all eight frozen packet files. Opening, ordinary owner first move, individual Research/Copycat/search arrivals, selected consequential mechanics, Energy targets and terminal sequence. Not a duplicate full visual pass.',
 'source_video':freeze['source_video'],
 'source_sha256':freeze['source_sha256'],
 'checked_input_sha256':checked,
 'all_eight_stable':stable,
 'accepted':False,
 'structural_validation':{'structural_pass':True,'turn_rows':15,'issues':[], 'visual_acceptance_separate':True},
 'rejected_bytes_preserved':'independent_sol/rejected_8_v1',
 'required_repairs':[
  {'id':'R1','files':['REVIEW.md','TURN_LEDGER.json','TURN_EVIDENCE.json'], 'detail':'Turn 1 Research reveal order is inverted and first arrival anchor unsupported. Native68 has only settled Glimmora/Muk/Copycat. Native69 shows Rare Candy arrival; native70 shows Glimmet arrival while Rare Candy is already in hand. Record Rare Candy then Glimmet with corresponding native evidence. Reconcile prose/result wording and any linked timing.'},
  {'id':'R2','files':['REVIEW.md','TURN_LEDGER.json','TURN_EVIDENCE.json'], 'detail':'Turn 5 first voluntary move is Alolan Muk evolution, not Glimmet Bench. Native201 has Kingambit/Glimmet/Muk3. Native202 lifts Muk toward Grimer; 204 shows evolution;205/206 Muk settled110 with suppression banner while Glimmet remains in hand.208 then lifts Glimmet to Bench.210 endingKingambit1. Update play numbers, timestamps, evidence, intermediate hand counts and prose.'},
  {'id':'R3','files':['REVIEW.md','TURN_LEDGER.json','TURN_EVIDENCE.json'], 'detail':'Owner Energy destinations and propagated boards require reconciliation from Turn5 onward. Native214 shows Darkness1 on Pawniard, not Muk. Native274/275 shows Glimmet1,Kingambit1,Muk0 before Turn9 normal draw. Native297 shows Darkness attachment onto Kingambit;303 endingKingambit2,Glimmet1,Muk0. Frozen account instead claims T5Muk,T7Kingambit,T9Glimmet and wrong intermediate boards. Recheck T7 andT11 targets against existing native frames, repair all affected start/end boards, Energy Zones and prose. This does not require changing correctly observed final theft/180/timeout outcome.'},
 ],
 'targeted_observations':[
  {'check':'opening five','status':'supported','seconds':[32],'observed':'Glimmora, Pawniard, Alolan Muk, Professor Research, Copycat, left to right before Active placement. Pawniard selected in recorded setup.'},
  {'check':'ordinary T5','status':'repair_required','seconds':[201,202,204,205,206,208,210,214],'observed':'Three-card start and one-card Kingambit end reconcile; first move Muk then Glimmet, with Pawniard receiving Darkness.'},
  {'check':'Research arrivals','status':'repair_required','seconds':[66,67,68,69,70,73],'observed':'Research displayed66; no arrivals yet68; RareCandy69 then Glimmet70. Ending4 Glimmora/Muk/Copycat/RareCandy supported73.'},
  {'check':'Copycat and search','status':'supported','seconds':[144,145,146,148,152,157],'observed':'Individual central arrivals PokeBall144,Kingambit145,Glimmet146; three-card settled hand148; AlolanGrimer search arrival152; endingKingambit/Glimmet2 at157.'},
  {'check':'Seal of Antiquity','status':'supported','seconds':[60],'observed':'Literal card text prohibits attack without Regirock/Regice/Registeel Bench, not Energy attachment.'},
  {'check':'Glimmora point denial','status':'supported','seconds':[189,194],'observed':'Coin face and explicit opponent-unable-to-get-points banner support denied point after knockout. Kingambit damage counts knockouts, independently of awarded points.'},
  {'check':'Lucky Ice Pop','status':'supported_with_energy_repair','seconds':[274,275,276,277,280,283,286,294,295,296,297,303],'observed':'First heal20->40 and heads return, second40->60 and tails discard. Ending0 owner cards. Glimmet already has Darkness at turn start; later T9 attachment goesKingambit. FirstPop-before-secondPop-before-attachment order is not rejected.'},
  {'check':'Thieving Incisors/mixedEnergy','status':'supported','seconds':[397,400,402,428],'observed':'Raticate starts2Metal, ability banner400, then Darkness1+Metal2 at402/428 and Glimmet loses itsDarkness. Muk Basic suppression does not suppress Stage1 Raticate.'},
  {'check':'Overlord180','status':'supported','seconds':[434],'observed':'Displayed180 damage to120HP Raticateex, Kingambit140HP withHeavyHelmet. Packet distinguishes3ownerKnockouts from2opponentpoints.'},
  {'check':'terminal outcome','status':'supported','seconds':[481,530,535,538,550,553],'observed':'2-2 points during waiting-for-opponent-return, time-limit3, ownerturn transition without attack, Ilima arrival538, +3 points animation capped atowner3/opponent2, Victory553. Timeout win, not visible concession or terminalKO.'},
  {'check':'exact20deck','status':'supported_historical_only','observed':'Deck slots/counts match retained exact20 QR semantic contents with Darkness. Historical log provenance is explicit. Fresh live access/save/readback remains root pending, intentionally not certified by this checker.'},
 ],
 'limits':['Bounded independent check does not independently repeat the whole battle coverage pass.','Source hash is frozen intake identity; native evidence refers to that source. No duplicate original rehash needed for this check.','Source metadata converts to2026-10-12Chicago; fresh live external artifact is pending and outside this checker scope.']
}
(out/'CHECK_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'accepted':False,'stable':stable,'result':str(out/'CHECK_RESULT.json'),'preserved':str(rejected)}))

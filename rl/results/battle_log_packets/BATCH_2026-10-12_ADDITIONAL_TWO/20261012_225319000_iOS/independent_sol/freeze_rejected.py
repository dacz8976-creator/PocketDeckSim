from pathlib import Path
import hashlib,json,datetime
p=Path(__file__).resolve().parent.parent
out=p/'independent_sol'; copies=out/'rejected_inputs_t6';copies.mkdir(exist_ok=True)
names=['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json','PAUSE_GAME.json','DECK_USED.json','TURN_LEDGER.json','TURN_EVIDENCE.json']
h={}
for n in names:
 b=(p/n).read_bytes();(copies/n).write_bytes(b);h[n]=hashlib.sha256(b).hexdigest()
receipt={'status':'rejected','checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checker':'/root/check_later_225319','source_video':'20261012_225319000_iOS.MP4','source_sha256':json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))['sha256'],'checked_input_sha256':h,'frozen_copy_directory':'independent_sol/rejected_inputs_t6','reason':'Early T6 account omitted Darkness attachment before retreat, wrongly claimed zero payment and unused current Energy. Native bounded4fps335-340 independently contradicts it. No acceptance issued.','source_check_notes':'independent_sol/SOURCE_CHECK_NOTES.md','correction_evidence':'independent_sol/T6_CORRECTION.md'}
(out/'CHECK_RESULT.rejected_t6.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))

import json,datetime
from pathlib import Path
B=Path(__file__).parent
p=B/'SOURCE_VERIFICATION.json'
d=json.loads(p.read_text(encoding='utf-8-sig'))
d.update(status='verification_failed_cloud_delivery_timeout',actual_sha256=None,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),error='Get-FileHash returned: The cloud operation was not completed before the time-out period expired.',exec_session=26878,retry_started=False,limits='No matching hash was produced. Original source not reread. Cached status must be checked and recovery coordinated by lead before further source reads.')
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
question={'status':'open_waiting_exact_source_comparison','source_sha256':d['expected_sha256'],'prior_binding':'PREPROCESS_LOG.md explicitly binds native frames to exact SHA, but decodedPTS not measured in prior manifest. Filename times are presently provisional.','observations':[{'evidence_id':'R0500.00','observation':'Drapion shows two Darkness symbols; Mega Absol shows blue attached Tool and two Darkness; old prose T13 inherits Drapion one Darkness and omits Tool.'},{'evidence_id':'R0522.00','observation':'Card-back animation unlike overview source522 LuckyIcePop preview; timing alignment needs current exact source.'},{'evidence_id':'R0672.00','observation':'Cape Raticate still visibly carries Psychic/Darkness symbols after old prose T15 retreat-payment claim. Requires close current-source transaction comparison.'}], 'conclusion':'Do not silently overwrite accepted facts or call discrepancies errors. New fields remain incomplete pending exact-source/native timing and action reconciliation.'}
(B/'RETAINED_NATIVE_QUESTION.json').write_text(json.dumps(question,indent=2),encoding='utf-8')

import json
from pathlib import Path
B=Path(__file__).parent
p=B/'EXTRACTION_PLAN.json';d=json.loads(p.read_text())
d['new_native_cap']=52
d['timing_comparison_checkpoint']={'status':'approved_by_lead','additional_native_count':2,'seconds':[500,522],'purpose':'Compare current measuredPTS images to prior native labels and reduced overview phases. Current500/522 match prior native images; overview phase differs.'}
for s in [500,522]:d['rows'].append(dict(turn_number=13 if s==500 else 14,requested_source_seconds=float(s),purpose='Bounded timestamp/provenance comparison',status='extracted',actual_frame_seconds_if_measured=500.012 if s==500 else 522.007))
d['planned_new_native_count']=52
p.write_text(json.dumps(d,indent=2),encoding='utf-8')
s=B/'SOURCE_REFERENCE.json';d=json.loads(s.read_text());d.update(current_source_verification='SOURCE_VERIFICATION.json',verification_status='verified_sha256_match',current_original_hash_attempts=2,current_original_successful_hashes=1,current_original_hash_reads=2,failed_attempt_receipt='SOURCE_VERIFICATION_ATTEMPT_1.json');s.write_text(json.dumps(d,indent=2),encoding='utf-8')

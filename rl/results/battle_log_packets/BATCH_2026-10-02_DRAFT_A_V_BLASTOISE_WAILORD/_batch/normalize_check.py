import argparse,json
from pathlib import Path
from validate_packet import BATCH,local,read,sha
p=argparse.ArgumentParser();p.add_argument('packet');p.add_argument('check');a=p.parse_args()
packet=Path(a.packet).resolve();assert packet.parent==BATCH
original=local(packet,a.check);c=read(original)
for standard,alias in [('checked_submission_manifest','checked_submission_path'),('checked_submission_manifest_sha256','checked_submission_sha256'),('checked_submission_files','checked_files_sha256')]:
 assert alias in c
 if standard in c:assert c[standard]==c[alias]
 else:c[standard]=c[alias]
manifest=local(packet,c['checked_submission_manifest']);assert sha(manifest)==c['checked_submission_manifest_sha256']
assert read(manifest)['files']==c['checked_submission_files']
for name,h in c['checked_submission_files'].items():assert sha(local(packet,name))==h
c['format_normalization']={'by':'/root','scope':'Three unambiguous field aliases only; independent conclusions unchanged','original_check':a.check,'original_check_sha256':sha(original)}
output=original.with_name(original.stem+'_NORMALIZED.json');assert not output.exists()
output.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(str(output.relative_to(packet)))

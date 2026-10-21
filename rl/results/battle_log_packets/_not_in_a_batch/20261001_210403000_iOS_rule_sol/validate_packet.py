from pathlib import Path
import json,re
from PIL import Image
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_210403000_iOS_rule_sol')
for n in ['SOURCE.json','REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
 f=p/n;print(n,f.stat().st_size)
for n in ['REVIEW.md','COVERAGE.md']:
 s=(p/n).read_text(encoding='utf-8-sig');assert '\u2014' not in s
checks=json.loads((p/'SUMMARY.json').read_text())['independent_check_times']
missing=[]
for c in checks:
 for t in c['seconds']:
  f=p/'native'/f't{t:07.2f}.jpg'
  if not f.exists():missing.append(str(f))
  else:
   with Image.open(f) as im: im.verify()
print('Missing exact handoff frames:',missing)
assert not missing
print('All handoff frames decoded and verified')
print('Overview sheets',len(list((p/'overview').glob('sheet_*.jpg'))))
print('Native exact frames',len(list((p/'native').glob('t*.jpg'))))
print('Source identity retained',json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))['sha256'])
(p/'WORKING_NOTES.md').write_text('Working notes were provisional and are superseded by REVIEW.md, COVERAGE.md, SUMMARY.json and UNCERTAINTIES.json. The final report corrects early overview card-name and inspection-versus-play interpretations using native frames.\n',encoding='utf-8')

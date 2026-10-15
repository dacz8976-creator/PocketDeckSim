from pathlib import Path
import json,re
p=Path('Recording_QA/20261001_205658000_iOS_rule_sol')
for n in ['SOURCE.json','SUMMARY.json','UNCERTAINTIES.json']: json.loads((p/n).read_text(encoding='utf-8-sig'))
missing=[]
for n in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
 s=(p/n).read_text(encoding='utf-8')
 if '\u2014' in s: raise SystemExit('Em dash found '+n)
 for f in re.findall(r'native/t[0-9]+\.[0-9]+\.jpg',s):
  if not (p/f).exists(): missing.append(f)
print('Missing native references:',sorted(set(missing)))
print('Native frame count:',len(list((p/'native').glob('*.jpg'))))
print('Packet bytes:',sum(f.stat().st_size for f in p.rglob('*') if f.is_file()))

from pathlib import Path
import re,json
p=Path(__file__).parent
src=json.loads((p/'SOURCE.json').read_text(encoding='utf-8'))
for name in ['REVIEW.md','COVERAGE.md']:
 s=(p/name).read_text(encoding='utf-8')
 # Repair any accidental identifier spacing without changing actual provenance.
 s=re.sub(r'`7326[^`]*`','`'+src['sha256']+'`',s)
 s=s.replace('Dacz 8976','Dacz8976').replace('dueHPcap','due to the HP cap').replace('withBalloon','with Balloon').replace('showMilotic','show Milotic')
 s=re.sub(r'HP([0-9])',r'HP, \1',s)
 s=re.sub(r',(?=[A-Za-z0-9])',', ',s)
 s=re.sub(r':(?=[A-Z0-9])',': ',s)
 # Undo colon spacing in the timestamp, and preserve the immutable exact hash.
 s=s.replace('`2026-10-12T00: 44: 35Z`','`2026-10-12T00:44:35Z`').replace('19: 44: 35','19:44:35')
 s=s.replace('`2026-10-12 T00:44:35 Z`','`2026-10-12T00:44:35Z`')
 (p/name).write_text(s,encoding='utf-8')
print('Prose spacing cleaned; exact source identifiers preserved')

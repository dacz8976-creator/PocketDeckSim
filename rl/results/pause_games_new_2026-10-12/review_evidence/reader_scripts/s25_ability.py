import sys, re
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
for p in POS:
    for s in p['his_plan']:
        if s.startswith('Ability') or s.startswith('UseStadium'):
            print(p['id'], repr(s), 'normalises' if re.match(r'^Ability(:[^@]+)?@\d+$', s) else 'NOT normalised')

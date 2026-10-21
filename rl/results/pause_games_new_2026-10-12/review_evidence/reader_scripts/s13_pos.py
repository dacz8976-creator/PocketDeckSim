import sys, json
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
for pid in sys.argv[1:]:
    p = POSBY[pid]
    q = dict(p)
    print(json.dumps(q, ensure_ascii=False)[:4000])
    print()

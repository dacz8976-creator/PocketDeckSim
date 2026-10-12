import sys, json
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
for pid in ['KW-261005_034953000-t02', 'KW-261005_034953000-t14', 'KW-261005_034953000-t16', 'KW-261005_031138000-t02', 'KW-261005_031138000-t04', 'KW-261005_031138000-t06',
            'KW-261006_012927000-t02', 'KW-261010_012303000-t11', 'KW-261005_032023000-t12', 'KW-261006_020518000-t11', 'KW-261010_013009000-t15', 'KW-261006_012927000-t06']:
    p = POSBY[pid]
    print(pid, '| hand', p['me']['hand'], '| board', [(b['card'], b['hp'], b.get('behind')) for b in p['me']['board']], '| plan', p['his_plan'], '| turn_effects', p['turn_effects'], '| opp', [(b['card'], b['hp']) for b in p['opp']['board']])

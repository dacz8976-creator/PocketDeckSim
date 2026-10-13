import sys, json, re
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
# usage: s15_grep.py GAMESUFFIX REGEX : every turn / field path whose string value matches
g = [x for x in GAMES if short_of(x).endswith(sys.argv[1])][0]
rx = re.compile(sys.argv[2], re.I)


def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + '.' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + f'[{i}]')
    else:
        yield path, o


for t in led(g)['turns']:
    for path, v in walk(t):
        if isinstance(v, str) and rx.search(v.replace('’', "'")):
            print(f"t{t['turn_number']:02d} {str(t.get('who_played'))[:5]} {path[:90]} = {v[:160]}")

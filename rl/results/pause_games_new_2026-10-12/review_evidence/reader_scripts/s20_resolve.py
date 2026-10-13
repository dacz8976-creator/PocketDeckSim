import sys, json, collections, re
sys.dont_write_bytecode = True
sys.path.insert(0, '/mnt/c/Users/dacz8/AppData/Local/Temp/claude/pp_review')
from common import *
from conv import C
orig = C['resolve']
LOG = []


def wrapped(items, text, name_hint=None):
    r = orig(items, text, name_hint)
    LOG.append(([(it['name'], it.get('bench_position'), sorted(it.get('ids', ()))) for it in items], text, r))
    return r


C['resolve'] = wrapped
bad = []
for g in GAMES:
    try:
        LOG.clear()
        pos, skip, dk = C['convert_game'](g)
    except Exception as e:
        continue
    for items, text, r in LOG:
        if r is None or text is None:
            continue
        tl = str(text).replace('’', "'").lower()
        names = [n.lower() for n, _, _ in items]
        rn = names[r]
        mentioned = [n for n in set(names) if n in tl]
        # the resolved Pokemon's name is absent from the text while another board name is in it
        if mentioned and rn not in tl and not any(rn in m or m in rn for m in mentioned):
            bad.append((short_of(g), text, r, items[r], mentioned, items))
        # bench slot mentioned but resolved to a different slot
        m = re.search(r'bench\s*(?:position\s*|slot\s*)?(\d)', tl)
        if m and r != 0 and items[r][1] is not None and items[r][1] != int(m.group(1)):
            bad.append((short_of(g), text, r, items[r], 'slot', items))
        for w, k in (('left', 1), ('middle', 2), ('center', 2), ('right', 3)):
            if re.search(r'\b' + w + r'\b', tl) and 'bench' in tl and r != 0 and items[r][1] is not None and items[r][1] != k:
                bad.append((short_of(g), text, r, items[r], 'word ' + w, items))
print('resolve calls checked; suspicious:', len(bad))
for x in bad:
    print('  ', x)

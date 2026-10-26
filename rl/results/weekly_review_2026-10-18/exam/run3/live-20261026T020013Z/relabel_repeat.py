#!/usr/bin/env python3
"""The sensitivity repeat is a SEPARATE judge invocation (after the primary run), so judge.py stamps its rows `repeat: 0` like the primary's. This
copies them with `repeat: 1`. judge.py sets that field after the call (`r['repeat'] = k`); it is not part of the prompt, the reply or any hash, so
nothing else changes. usage: relabel_repeat.py IN OUT"""
import json, sys

src, dst = sys.argv[1:3]
n = 0
with open(src, encoding='utf-8') as f, open(dst, 'w', encoding='utf-8') as g:
    for line in f:
        if not line.strip():
            continue
        r = json.loads(line)
        assert r.get('bot') == 'judge' and r.get('repeat') == 0, (r.get('bot'), r.get('repeat'))
        r['repeat'] = 1  # nothing else is touched (the run manifest records the relabel)
        g.write(json.dumps(r, ensure_ascii=False) + '\n')
        n += 1
print(f'{n} rows relabelled to repeat 1')

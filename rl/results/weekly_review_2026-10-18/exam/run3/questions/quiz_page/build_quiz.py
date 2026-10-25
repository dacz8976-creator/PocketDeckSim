import json, hashlib, sys
src, tpl, out = sys.argv[1], sys.argv[2], sys.argv[3]
raw = open(src, 'rb').read()
print('source sha256', hashlib.sha256(raw).hexdigest())
d = json.loads(raw.decode('utf-8'))
assert len(d['questions']) == 23 and all('video' in q for q in d['questions'])
blob = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
t = open(tpl, encoding='utf-8').read()
assert t.count('/*__DATA__*/null') == 1
if len(sys.argv) > 4:
    cards = open(sys.argv[4], encoding='utf-8').read().replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    assert t.count('/*__CARDS__*/null') == 1
    t = t.replace('/*__CARDS__*/null', cards)
    print('cards embedded', len(cards), 'chars, sha256', hashlib.sha256(open(sys.argv[4], 'rb').read()).hexdigest())
open(out, 'w', encoding='utf-8', newline='\n').write(t.replace('/*__DATA__*/null', blob))
print('wrote', out, len(blob), 'chars of data')
test = out.replace('.html', '_localtest.html')
open(test, 'w', encoding='utf-8', newline='\n').write('<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n' + t.replace('/*__DATA__*/null', blob))

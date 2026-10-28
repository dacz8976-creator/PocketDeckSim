"""Split each Gemini review answer in a game folder into REVIEW.md, OPPONENT.json and UNCERTAINTIES.md (next to response.txt)."""
import os, re, sys
g = sys.argv[1]
def unfence(x):
    m = re.search(r'```(?:json)?\s*(.*?)```', x, flags=re.S)
    return (m.group(1) if m else x).strip()
for run in ('review_high', 'review_default'):
    p = os.path.join(g, run, 'response.txt')
    if not os.path.exists(p):
        continue
    t = open(p, encoding='utf-8').read()
    parts = re.split(r'^`?=== (REVIEW\.md|OPPONENT\.json|UNCERTAINTIES\.md) ===`?\s*$', t, flags=re.M)
    got = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    for name in ('REVIEW.md', 'OPPONENT.json', 'UNCERTAINTIES.md'):
        body = got.get(name, '(section missing)')
        open(os.path.join(g, run, name), 'w', encoding='utf-8').write((unfence(body) if name.endswith('.json') else body) + '\n')
    print(os.path.basename(g), run, 'sections:', sorted(got))

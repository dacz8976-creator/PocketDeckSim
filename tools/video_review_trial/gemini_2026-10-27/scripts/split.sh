#!/bin/bash
# usage: split.sh gN  -> the Gemini outputs, split into files, in the scorer's folder (with placeholder score files)
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/b816037a-8268-412e-9510-8518f9b17037/scratchpad/gscore/$1
G=/home/dacz8976/gemini_video/$1
mkdir -p $S/gemini $S/score
python3 - "$G" "$S" <<'EOF'
import sys, re, os
g, s = sys.argv[1], sys.argv[2]
t = open(f'{g}/out_review/response.txt', encoding='utf-8').read()
parts = re.split(r'^`?=== (REVIEW\.md|OPPONENT\.json|UNCERTAINTIES\.md) ===`?\s*$', t, flags=re.M)
got = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
def unfence(x):
    m = re.search(r'```(?:json)?\s*(.*?)```', x, flags=re.S)
    return (m.group(1) if m else x).strip()
open(f'{s}/gemini/REVIEW.md', 'w', encoding='utf-8').write(got.get('REVIEW.md', '(section missing)') + '\n')
open(f'{s}/gemini/OPPONENT_review.json', 'w', encoding='utf-8').write(unfence(got.get('OPPONENT.json', '{}')) + '\n')
open(f'{s}/gemini/UNCERTAINTIES.md', 'w', encoding='utf-8').write(got.get('UNCERTAINTIES.md', '(section missing)') + '\n')
f = open(f'{g}/out_field/response.txt', encoding='utf-8').read()
open(f'{s}/gemini/OPPONENT_field.json', 'w', encoding='utf-8').write(unfence(f) + '\n')
for n in ('SCORE.md', 'score.json'):
    open(f'{s}/score/{n}', 'w').write('PLACEHOLDER\n')
print(os.path.basename(g), 'sections:', sorted(got), {n: os.path.getsize(f'{s}/gemini/{n}') for n in os.listdir(f'{s}/gemini')})
EOF

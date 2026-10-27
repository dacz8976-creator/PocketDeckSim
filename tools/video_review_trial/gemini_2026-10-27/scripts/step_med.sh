#!/bin/bash
# cheaper variant: the review pass at 2 fps with the DEFAULT media resolution, for g1-g3; outputs split for scoring
cd /home/dacz8976/gemini_video || exit 1
S=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/b816037a-8268-412e-9510-8518f9b17037/scratchpad/gscore
for G in g2 g1 g3; do
  python3 -I gemini_video.py --video $G/video.mp4 --brief $G/REVIEW.md --out $G/out_review_med --fps 2 | tail -1
  mkdir -p $S/$G/med/gemini $S/$G/med/score
  python3 - "$G/out_review_med/response.txt" "$S/$G/med" <<'EOF'
import sys, re
t = open(sys.argv[1], encoding='utf-8').read(); s = sys.argv[2]
parts = re.split(r'^`?=== (REVIEW\.md|OPPONENT\.json|UNCERTAINTIES\.md) ===`?\s*$', t, flags=re.M)
got = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
def unfence(x):
    m = re.search(r'```(?:json)?\s*(.*?)```', x, flags=re.S)
    return (m.group(1) if m else x).strip()
open(f'{s}/gemini/REVIEW.md', 'w', encoding='utf-8').write(got.get('REVIEW.md', '(section missing)') + '\n')
open(f'{s}/gemini/OPPONENT_review.json', 'w', encoding='utf-8').write(unfence(got.get('OPPONENT.json', '{}')) + '\n')
open(f'{s}/gemini/UNCERTAINTIES.md', 'w', encoding='utf-8').write(got.get('UNCERTAINTIES.md', '(section missing)') + '\n')
for n in ('SCORE.md', 'score.json'):
    open(f'{s}/score/{n}', 'w').write('PLACEHOLDER\n')
print('sections', sorted(got))
EOF
done
python3 -c "import json; l=json.load(open('ledger.json')); print('ledger', round(l['accrued_usd'],4))"

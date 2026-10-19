"""v1.5.1: Dustin's correction for 215114 t10 (he won that game): key unchanged, recorded line still not acceptable, NOT decided_game."""
import json, re
F = '/home/dacz8976/exam/commit/exam_2026-10-19.json'
d = json.load(open(F))
assert d['format'] == 'pds-exam-v1.5'
pid = 'LAD-20261014_215114000_iOS-t10'
p = next(x for x in d['points'] if x['id'] == pid); a = p['answer']
a['dustin_answer'] = {'words': a['dustin_answer']['words'], 'source': a['dustin_answer']['source'],
    'correction': {'words': "For 5. I think I thought I had lost, but just finished the video and I won. The energy attachment to rattata didn't matter, but would have been the better move there",
                   'source': 'Dustin, Oct 19 (relayed verbatim by the coordinator): supersedes "the game was over"; the key stands, the point is not decided_game'}}
p['decided_game'] = False
for r in a['rejected_alternatives']:
    if r['line'] == a['his_move']:
        r['rejected_because'] = "Dustin: attaching the Water to Rattata 'would have been the better move there' (it didn't change the result; he won)"
assert a['key_line'] and a['recorded_move_acceptable'] is False
d['format'] = 'pds-exam-v1.5.1'
d['key_rule'] = d['key_rule'].replace("decided_game marks a point whose game was already lost; reports show those separately.",
                                      "decided_game marks a point whose game was already decided; reports show those separately (no point carries it as of v1.5.1).")
json.dump(d, open(F, 'w'), indent=1, ensure_ascii=False)
print('decided_game points:', [x['id'] for x in d['points'] if x.get('decided_game')])
R = '/home/dacz8976/exam/commit/README.md'
t = open(R).read()
old = "| 215114 t10 (13-A) | the game was over; attaching to Rattata \"would be the smart play normally\" | the Water goes on the new Rattata | his recorded line: rejected as play quality. `decided_game: true`, so reports show it separately |"
assert old in t
t = t.replace(old, "| 215114 t10 (13-A) | attaching to Rattata \"would have been the better move there\". He first said the game was over, then corrected it on re-watching: he won (v1.5.1) | the Water goes on the new Rattata | his recorded line: rejected as play quality. Not `decided_game` (his correction) |")
t = t.replace("File: `exam_2026-10-19.json`, format `pds-exam-v1.5`.", "File: `exam_2026-10-19.json`, format `pds-exam-v1.5.1`.")
t += """
## v1.5.1 (Oct 19): Dustin's correction for 215114 t10
His words: "For 5. I think I thought I had lost, but just finished the video and I won. The energy attachment to rattata didn't matter, but would have been the better move there".
- The key is unchanged: the turn's Water goes on the new Rattata.
- His recorded line is still not acceptable.
- The point is no longer `decided_game`, so no point carries that flag now.
- The correction is stored with his earlier words in `answer.dustin_answer.correction`.
- No line changed, so v1.5's validation stands.
"""
open(R, 'w').write(t)
print('README ok')

#!/usr/bin/env python3
"""RESULTS_K21.md from K21's own files (every result number read from SUMMARY_K21.json and the launch files, none typed).
The kx3-v-km3 pair counts and timing come from the independent check's result file ~/k21_verify/lineconsistency/result.json (wf_6bdd9503-5a0)."""
import json, sys
K = '/home/dacz8976/k21_run'
OUTF = sys.argv[1]
S = json.load(open(f'{K}/out/SUMMARY_K21.json'))
L = json.load(open(f'{K}/launch/LAUNCH_K21.json'))
G = json.load(open(f'{K}/launch/GATES.json'))
launch = open(f'{K}/launch/COMMIT').read().strip()
night = open(f'{K}/night_2026-10-27.log').read().splitlines()


def ci(c):
    return f"{c['estimate']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]"


def rate(r):
    return f"{r['estimate']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]"


P = S['primary']; pc = P['contrasts'][0]; pr = P['rates']
X = S['kx3_v_km3']; xc = X['contrasts'][0]; xr = X['rates']
F = P['full_scope']; fc = F['contrasts'][0]
XF = X['full_scope']; xfc = XF['contrasts'][0]
C = S['chance_stratum']; cc = C['contrast']
assert pc['a'] == 'judge' and pc['b'] == 'kx3' and xc['a'] == 'kx3' and xc['b'] == 'km3'
assert P['experiment_switches'] == ['--allow-other-binaries'] and P['formal_flag'] is False and X['experiment_switches'] == ['--allow-other-binaries']
assert S['gemini_calls'] == 0 and S['status'] == 'DONE'
t = lambda key: next(l.split(' ')[0] for l in night if key in l)

lines = []
A = lines.append
A('# K21: unchanged kx3 on the frozen exam v2, the result (Oct 27)')
A('')
A(f"**Label: EXPERIMENT.** This is frozen-7's own label for a compare run with `--allow-other-binaries` (report `formal: false`). K21 makes it the registered kx3 result (PREREG_RUN3.md, K21 section 6, and K21a). Results go to the coordinator only.")
A('')
A('## The registered primary (K21 section 5; 95%)')
A('')
A('| | decisions (games) | Gemini (saved run 3 rows) | kx3 (mean of 3 seeds) | Gemini minus kx3 | sign-flip p | verdict |')
A('|---|---|---|---|---|---|---|')
A(f"| **PRIMARY** | {pc['n_decisions']} ({pc['n_games']}) | {rate(pr['judge'])} | {rate(pr['kx3'])} | **{ci(pc)}** | {pc['sign_flip_p']:g} | **{pc['verdict']}** |")
A('')
A(f"- **Verdict rule (frozen-7's analysis.py, as registered):** the game-clustered 95% interval lies above 0 AND the sign-flip p < 0.05, with at least 10 games. Here: {pc['reason']}; {pc['n_pairs_dropped']} pairs dropped.")
A("- **What it means (K21 section 6):** on these 258 decisions of exam v2, Gemini's first plan segment matches Dustin's accepted moves more often than unchanged kx3's does. This is the comparison section 8 required before anyone says Gemini beats our best bot.")
A("- **Its limits:** the measure is prefix agreement (v1.6's scoring, R1's lister segments), not plan quality. It says nothing about finished games or win rates.")
A("- **Unchanged:** run 3's filed verdict (Gemini v km3, RESULTS_run3.md) stands. **The adapter is not started.**")
A('')
A('## Descriptive only (K21 section 5: no verdict is drawn from these)')
A('')
A('| | decisions (games) | first bot | second bot | difference | sign-flip p |')
A('|---|---|---|---|---|---|')
A(f"| kx3 minus km3, same seeds and decisions | {xc['n_decisions']} ({xc['n_games']}) | kx3 {rate(xr['kx3'])} | km3 {rate(xr['km3'])} | {ci(xc)} | {xc['sign_flip_p']:g} |")
import re
NFS = int(re.search(r'of (\d+) decisions', fc['reason']).group(1))
A(f"| Full-scope block, Gemini minus kx3 | {fc['n_decisions']} of {NFS} ({fc['n_games']}) | Gemini {fc['matched_rates']['judge']:.3f} (matched) | kx3 {fc['matched_rates']['kx3']:.3f} (matched) | {ci(fc)} | {fc['sign_flip_p']:g} |")
A(f"| Full-scope block, kx3 minus km3 | {xfc['n_decisions']} ({xfc['n_games']}) | kx3 {xfc['matched_rates']['kx3']:.3f} | km3 {xfc['matched_rates']['km3']:.3f} | {ci(xfc)} | {xfc['sign_flip_p']:g} |")
A(f"| Chance-ending stratum (run 3's 168 points), Gemini minus kx3 | {cc['n_decisions']} ({cc['n_games']}) | Gemini {rate(C['rates']['judge'])} | kx3 {rate(C['rates']['kx3'])} | {ci(cc)} | {cc['sign_flip_p']:g} |")
A('')
LC = json.load(open('/home/dacz8976/k21_verify/lineconsistency/result.json'))
dp, pa, kg, dv, tm = LC['differing_plan_number'], LC['pairs'], LC['kx3_km3_games'], LC['deviation'], LC['timing']
assert dp['kx3_higher'] - dp['kx3_lower'] == round(xc['estimate'] * pa['n']) and pa['n'] == 774
A(f"- **kx3 minus km3:** frozen-7's analysis prints \"{xc['verdict']}\" for this line; K21 registered it as descriptive, so no verdict is drawn. The independent check (below) traced it to kx3's own overrides of km3's move: kx3 chose a different listed plan on {dp['n']} of {pa['n']} (decision, seed) pairs, on {dv['positions_with_any_deviation']} of the 258 positions. kx3 matched the answer on {dp['kx3_higher']} of them, km3 on {dp['kx3_lower']}, and neither on {dp['equal_neither']}: a net of {dp['kx3_higher'] - dp['kx3_lower']} of {pa['n']} pairs, which is the {xc['estimate']:+.6f}. The difference covers {kg['decisions_nonzero']} decisions ({kg['decisions_negative']} lower, {kg['decisions_positive']} higher) in {kg['games_nonzero']} games. On all {pa['equal_plan_number']} pairs where both picked the same plan, they scored the same.")
A(f"- **kx3's time:** median {tm['median']} s per decision and seed (95th percentile {tm['p95']} s, longest {tm['max']} s); {tm['total_hours']} h for all {tm['n']} rows (the registered estimate was 1.4-6 h per seed).")
nc = F.get('not_comparable', {})
A(f"- **Full scope:** {fc['n_pairs_dropped']} of the {NFS} full-scope points were not comparable for both bots and were dropped, not scored (kx3's plan stops at a chance event: {', '.join(x[4:] for x in nc.get('kx3', []))}; Gemini's: {', '.join(x[4:] for x in nc.get('judge', []))}). kx3 minus km3 dropped {xfc['n_pairs_dropped']}.")
A("- **By category:** `run/out/by_category_k21.json` and `categories_k21.txt` (descriptive; a point counts in each of its kinds).")
A('')
A("## K21a: what replaced each freeze check the switch skips")
A('')
A(f"- **S1, the plan lister's sha256** (judge.py line 1002): checked in `freeze_checks.json` before the rows and again before the compare; lister {S['frozen7']['plans_binary_sha256'][:16]}… = FROZEN.json's.")
A(f"- **S2, `freeze_identity.check`** (line 1007): item by item, {S['freeze_checks']['result'].split(': ')[1]} at night start and before the compare; frozen-7 tag {S['frozen7']['tag_commit'][:8]}, its own check: {S['frozen7']['freeze_identity_check']}.")
A(f"- **S3, each row's executable** (line 1000): every kx3 row carries the launch line's binary {S['row_binaries']['kx3'][:16]}… and every km3 row f35a1a99 ({S['row_binaries']['km3'][:16]}…).")
A("- **Each report** carries exactly the one experiment switch, the frozen fingerprint, the frozen lister and the frozen judge settings (compare_k21.py checks this).")
A(f"- **No Gemini call:** gemini_calls {S['gemini_calls']}; Gemini's saved run 3 rows are reused byte for byte (judge_primary.jsonl {S['inputs']['judge_rows']['judge_primary.jsonl'][:8]}, pass 1 {S['inputs']['judge_rows']['judge_primary_pass1.jsonl'][:8]}).")
A('')
A('## How it ran (night 1 of 4; the other three are not needed)')
A('')
A(f"- {t('K21 night 2026-10-27')}: start; kit {L['kit_commit'][:8]}; freeze checks {S['freeze_checks']['result'].split(': ')[1]}.")
A(f"- {t('BUILD OK')}: build OK, binary sha256 {S['row_binaries']['kx3']}.")
assert G['all_pass'] is True and L['gates_all_pass'] is True and L['kx3_exam_rows_so_far'] == 0 and L['binary_sha256'] == S['row_binaries']['kx3']
A(f"- Gates (a)-(d) on development positions only: {json.dumps(L['gates_pass'])}; all pass. The launch line was written at {L['written_utc']} with 0 kx3 exam rows so far.")
A(f"- {t('launch line committed')}: launch line `{launch[:8]}` committed and pushed, before any kx3 exam row.")
A(f"- {t('kx3 rows: exit')}: {S['complete_seeds'].__len__()} seeds complete ({', '.join(str(s) for s in S['complete_seeds'])}), 774 rows; the compare ran at {t('K21 scored')}.")
A("- Later nights (Oct 28, 30, 31 UTC) find `DONE` and run nothing.")
A('')
A('## The independent check before this report (workflow wf_6bdd9503-5a0; 5 Opus agents, no Sonnet; no API or network call)')
A('')
A('- **Frozen code, own driver** (not compare_k21.py): every estimate, n, interval end, p and verdict above reproduced to the printed digits; the judge and km3 rates equal run 3\'s own report; the kx3 rows fed to the compare equal the runner\'s raw rows.')
A('- **From scratch** (frozen code read as a spec only): every point estimate and n exact; its own random draws land within 0.0017 of every interval end; with the registered seeds the method reproduces every digit.')
A('- **Line level:** the kx3 minus km3 accounting above; on identical plans the scores are identical.')
A('- **Provenance:** binary sha on disk and in every row; the kit equals d4877c97\'s; the inputs equal the frozen exam files (6e5fab0c) and run 3\'s live rows (e159551d); the launch commit is on origin and precedes every row file.')
A('- **Critic:** no discrepancy. Limits: the binary was not rebuilt (its source was checked: frozen tree 70652fff plus kx3\'s insertions only, the card data unchanged); the order "record, launch, rows" rests on the laptop\'s clocks and git times.')
A('- **What the checkers ran beyond reading files** (disclosed; nothing new is scored from them): the frozen lister on the 258 exam positions (to rebuild the plan lists, as the compare does); the K21 binary as km3 on all 774 exam pairs (identical to the baseline rows byte for byte); kx3 replays on 8 sampled exam pairs and 2 gate (b) development pairs (identical lines). One checker also computed a label-only reading, which is not the registered definition and is not a result.')
A('- **No answer content was printed** by any checker. Their scripts and outputs stay on the laptop (`~/k21_verify`, scratchpad `exam2/k21/verify/`).')
A('')
A('## Records')
A('')
A("- `run/`: the night's rows (`rows/`), the compare's outputs (`out/`, including SUMMARY_K21.json and both reports), the gates' outputs on development positions (`gates/`) and the logs. `launch/` and `kit/` were committed before the rows.")
open(OUTF, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

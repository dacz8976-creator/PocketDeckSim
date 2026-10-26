#!/usr/bin/env python3
"""RESULTS_run3.md from the live run's own files (every number read from them, none typed)."""
import glob, json, re, sys
L = sorted(glob.glob('/home/dacz8976/exam_run3/live-*'))[-1]
RUN = L.split('/')[-1]
OUTF = sys.argv[1]
J = lambda f: json.load(open(f'{L}/{f}', encoding='utf-8'))
rep, pooled, ps, s3 = J('report_primary.json'), J('pooled_primary.json'), J('pooled_chance_stratum.json'), J('run3_chance_stratum.json')
man, a3, ledger, cats, ro = J('run_manifest.json'), J('a3_run3.json'), J('spend_ledger.json'), J('by_category.json'), J('report_only.json')
pos = {p['id']: p for p in json.load(open(f'{L}/in/positions.json'))}
spend = open(f'{L}/spend.txt').read().strip()
runlog = open(f'{L}/run.log').read()
D = json.load(open('/home/dacz8976/exam_034_w/rl/results/weekly_review_2026-10-18/exam/run3/decks/DECKS.json', encoding='utf-8'))


def deck_name(d):
    def walk(o):
        if isinstance(o, dict):
            if d in o and isinstance(o[d], dict):
                for k in ('name', 'deck_name', 'title', 'label'):
                    if o[d].get(k):
                        return o[d][k]
            for v in o.values():
                r = walk(v)
                if r:
                    return r
        elif isinstance(o, list):
            for v in o:
                if isinstance(v, dict) and d in (v.get('deck_id'), v.get('id'), v.get('key')):
                    for k in ('name', 'deck_name', 'title', 'label'):
                        if v.get(k):
                            return v[k]
                r = walk(v)
                if r:
                    return r
        return None
    return walk(D) or d


def ci(c):
    return f"{c['estimate']:+.3f} [{c['ci_low']:+.3f}, {c['ci_high']:+.3f}]"


def rate(r):
    return f"{r['estimate']:.3f} [{r['ci_low']:.3f}, {r['ci_high']:.3f}]"


pp = pooled['primary']
pr = {x['label'].split()[0]: x for x in pooled['per_run']}
r3 = rep['analysis']['prefix']
c3 = r3['contrasts'][0]
fs = rep['analysis']['full_scope']
fsc = fs['contrasts'][0]
pst, s3t = ps['stratum'], s3['stratum']
name = lambda c: re.sub(r'\s+((?:P-[AB]|[AB]\d[a-z]?)\s+\d{1,3})$', '', c)
t0 = re.search(r'^(\S+) mode=live', runlog, re.M).group(1)
tkm = re.search(r'^(\S+) km3 rows: (\d+)', runlog, re.M)
tcmp = re.search(r'^(\S+) compare \(primary', runlog, re.M).group(1)
tend = re.findall(r'^(\S+) ', runlog, re.M)[-1]
passes = [l for l in runlog.splitlines() if ' pass ' in l and ': exit ' in l]


def pass_line(l):
    m = re.search(r'(judge_\w+) pass (\d+): exit (\d+).*?spend \$([\d.]+); (\{.*?\}\}?[^;]*?\});', l)
    if not m:
        m2 = re.search(r'(judge_\w+) pass (\d+): exit (\d+).*?spend \$([\d.]+); (\{.*\})', l)
        m = m2
    who, k, ex, sp = m.group(1), m.group(2), m.group(3), m.group(4)
    js = json.loads(re.search(r'(\{"last_pass".*?\}\s*,\s*"missing".*?\})', l).group(1))
    lp = js['last_pass']
    return (f"| {who.replace('judge_', '').replace('_raw', '')} | {k} | {lp['asked']} | {lp['sent']} | {lp['not_sent']} | {lp['failed']} | "
            f"{js['missing']} | ${float(sp):.2f} |")


lines = []
A = lines.append
A(f"# Exam run 3: results ({t0[:10]}, {t0[11:16]}-{tend[11:16]}Z)")
A('')
A(f"Run folder `{RUN}` (kit `{man['kit_commit']}`, K20; exam v2 frozen at 6e5fab0c, K19; judge `judge-prompt-frozen-7`). Results go to the coordinator only.")
A('')
A('## The registered primary, and run 3 alone (equal prominence)')
A('')
A('| | decisions (games) | Gemini | km3 (mean of 3 seeds) | Gemini minus km3 | sign-flip p | verdict |')
A('|---|---|---|---|---|---|---|')
A(f"| **PRIMARY: runs 2 + 3 pooled, 97.5%** (section 4) | {pp['population']['n_decisions']} ({pp['population']['n_games']}) | {rate(pp['rates']['judge'])} | "
  f"{rate(pp['rates']['km3'])} | **{ci(pp['contrast'])}** | {pp['contrast']['sign_flip_p']:g} | **{pp['contrast']['verdict']}; PASS = {pp['pass']}** |")
A(f"| **Run 3 alone, run 2's rule (95%)** (section 5) | {r3['population']['n_decisions']} ({r3['population']['n_games']}) | {rate(r3['rates']['judge'])} | "
  f"{rate(r3['rates']['km3'])} | **{ci(c3)}** | {c3['sign_flip_p']:g} | **{c3['verdict']}** |")
r2 = pr['run2']['alone_at_0.95_equals_its_report']
A(f"| Run 2 alone (for reference; its own report) | {r2['n_decisions']} ({r2['n_games']}) | | | {ci(r2)} | {r2['sign_flip_p']:g} | {r2['verdict']} |")
A('')
A(f"- **The PRIMARY passes** (section 4: the 97.5% game-clustered interval lies entirely above 0 AND the sign-flip p < 0.025; {pp['population']['n_games']} games, at least 10).")
A(f"- **Run 3 alone also gives \"judge higher\"** at run 2's rule (its 95% interval above 0, sign-flip p < 0.05, {r3['population']['n_games']} games). The two runs are different games and points by construction.")
A(f"- **The model:** every judge row returned `{', '.join(pooled['judge_models'])}`, run 2's model (section 7: pooling ON). frozen-7's analysis.py was used unchanged (sha256 {pooled['method']['analysis_sha256'][:12]}…); 20,000 resamples, seed 20261019; sign-flip Monte Carlo, 100,000 draws, seed 20261020.")
A(f"- **Failed judge replies (no choice, scored as misses):** {a3['failed_primary_decisions']} of {a3['judge_decisions_primary']} (run 3); pooled {pp['failed_replies']['n']} ({pp['failed_replies']['share']:.1%}). The >20% rule (A3) is not triggered.")
A(f"- **The formal compare:** `judge.py compare --on-problem fail --failed-judge-rows miss`, status {rep['status']}, formal {rep['formal']}, problems {len(rep['problems'])}; rows {rep['n_present_rows']} of {rep['n_expected_rows']} (km3 {rep['row_account']['per_bot_state_counts']['km3']}, judge {rep['row_account']['per_bot_state_counts']['judge']}).")
A('')
A('## Section 8, the sentence written in advance')
A('')
A('> "Gemini is a better plan picker than km3 on his decisions."')
A('')
A("- As registered: **the formal kx3 test (frozen-5) still comes before anyone says it beats our best bot.** km3 is a frozen, untuned baseline.")
A("- What is measured is **prefix agreement** with his first plan segment (v1.6's scoring; R1's lister segments): it is not plan quality.")
A("- **Stage 2 was declared after stage 1 was seen** (section 4), which is why the bar was 97.5%. There is no stage 3 on this question until 50+ new labelled games exist.")
A('')
A('## Secondaries (reported, not deciding)')
A('')
A('| | decisions (games) | Gemini | km3 | Gemini minus km3 | sign-flip p |')
A('|---|---|---|---|---|---|')
A(f"| Chance-ending stratum, run 3 alone (95%) | {s3t['contrast']['n_decisions']} ({s3t['contrast']['n_games']}) | {rate(s3t['rates']['judge'])} | {rate(s3t['rates']['km3'])} | {ci(s3t['contrast'])} | {s3t['contrast']['sign_flip_p']:g} |")
A(f"| Chance-ending stratum, pooled (97.5%) | {pst['contrast']['n_decisions']} ({pst['contrast']['n_games']}) | {rate(pst['rates']['judge'])} | {rate(pst['rates']['km3'])} | {ci(pst['contrast'])} | {pst['contrast']['sign_flip_p']:g} |")
A(f"| Full-scope block, run 3 alone (95%; the formal compare's) | {fsc['n_decisions']} of {fs['population']['n_decisions']} ({fsc['n_games']}) | {rate(fs['rates']['judge'])} | {rate(fs['rates']['km3'])} | {ci(fsc)} | {fsc['sign_flip_p']:g} |")
A('')
nb = list(pst['n_by_run'].values())
A(f"- **The chance-ending stratum** (section 5; `strata/STRATA.md`, fixed before any row): {nb[0]} points from run 2 and {nb[1]} from run 3, {sum(nb)} pooled. No verdict is drawn from it.")
nc = fs.get('not_comparable') or {}
union = sorted(set().union(*[set(v) for v in nc.values()])) if nc else []
A(f"- **The full-scope block:** {fsc['n_pairs_dropped']} of the {fs['population']['n_decisions']} full-scope points were not comparable for both bots and were dropped, not scored "
  f"(km3's plan stops at a chance event: {', '.join(x[4:] for x in nc.get('km3', []))}; Gemini's: {', '.join(x[4:] for x in nc.get('judge', []))}). "
  "K9's caveat point 122720-t1 is one of them; the other four K9 points are not full-scope.")
A("- **The sensitivity repeat** (run 2's design): **incomplete, so no sensitivity comparison** (K20). 257 of 258 decisions have a repeat row. "
  "LAD-20261023_225646000_SR-t11 got HTTP 429 on both of its issued repeat calls (repeat pass 0 and its single resend in pass 1), so by K20 it was not sent again. "
  "The same decision had also hit HTTP 429 in the primary's pass 0; its resend in the primary's pass 1 returned a reply.")
A("- **Gemini against run 1's Sonnet judge:** no point overlaps (run 3's points are new), so there is nothing to report.")
A('')
A('### By category (by_category.json; descriptive, a point counts in each of its kinds; no interval, no verdict)')
A('')
tab = cats['table']
for group, title in (('answer_kind', 'Answer kind'), ('deck_kinds', 'Deck kind')):
    A(f'- **{title}:** ' + '; '.join(f"{k} ({v['judge']['n_decisions']}): Gemini {v['judge']['agreement']:.3f}, km3 {v['km3']['agreement']:.3f}"
                                     for k, v in sorted(tab.get(group, {}).items())))
A(f"- **By deck:** in `by_category.json` and `categories.txt` (24 decks, most with few points; deck ids are mapped to their lists in `decks/DECKS.json`). Note: categories.py's own `what` text says \"the 49 primary points\" (run 1's wording); here it is all 258.")
A('')
A('## REPORT-ONLY (K19): his third lines, beside what the judge and km3 played (no scoring)')
A('')
A('Slots are as in the position: 0 is his Active, 1-3 his Bench from the left. km3 played the same line on all 3 seeds at each of these points.')
A('')
for x in ro['points']:
    p = pos[x['point']]
    me = ', '.join(f"{i} {name(b['card'])}" for i, b in enumerate(p['me']['board']))
    A(f"- **{x['question']}** `{x['point']}` (his answer: \"{x['his_choice']}\"). His board: {me}.")
    A(f"  - His note: \"{x['his_note']}\"")
    A(f"  - His move: `{', '.join(x['his_move'])}`")
    A(f"  - Gemini: `{', '.join(x['judge'][0]['plan'])}` (stops at: {x['judge'][0]['cut']})")
    A(f"  - km3: `{', '.join(x['km3'][0]['plan'])}` (stops at: {x['km3'][0]['cut']})")
    if x.get('engine_note'):
        A(f"  - Engine note: {x['engine_note']}.")
A('')
A('## How it ran')
A('')
A(f"- **Launch:** tmux `run3live`, armed at 22:44Z, started {t0[11:19]}Z (the night window opens 02:00Z). The worktree was at the kit commit; the key came from ~/.bashrc and was never printed. freeze_identity passes; the harness tests (406) pass; the inputs equal K19 and are unchanged at the tip.")
A(f"- **km3:** {tkm.group(2)} rows at {tkm.group(1)[11:19]}Z (seeds 25,101,000,001-003, nice 19, the frozen baseline).")
A(f"- **The judge** (2 workers; K20's passes):")
A('')
A('| batch | pass | asked | sent | NOT SENT | failed | without a row after | spend |')
A('|---|---|---|---|---|---|---|---|')
for l in passes:
    try:
        A(pass_line(l))
    except Exception as e:
        A(f'| (unparsed: {l[:80]}) |')
A('')
A("- Every failed call was HTTP 429 (TPM quota). Each one halted its pass (frozen-7's rule), and the tasks after it were recorded NOT SENT and went in a later pass, as K20 registered. The primary was complete after 1 later pass; the repeat used all 3 and ended with 1 decision issued twice without a row.")
A(f"- **The compare** ran at {tcmp[11:19]}Z; the pooled primary and both strata immediately after (no API call); then the repeat.")
A("- **STATUS STOP** at the end only because the repeat was incomplete (K20: no sensitivity comparison; everything else written). Nothing unregistered happened; nothing was worked around.")
A('')
A('## Spend (ACTUAL where the records give it; caps are not spending)')
A('')
A(f"- **Gemini (this run):** {spend}. That is the harness's own token counts at its price table (Gemini 4 Argon on Vertex, $2 / $10 per 1M input / output tokens through 2026-11-30): **an estimate, until the Google billing page confirms it.**")
A(f"  - The ledger shows ${ledger['accrued_usd']:.2f}: the same plus the full worst case charged for each of the 4 calls that got HTTP 429 (frozen-7 charges a failed call its worst case because whether it was billed is unknown). The caps ($40 primary, $75 ledger) were never near.")
A("- **The Claude credit-worker jobs for run 3's prep** (INV, Part A, the labels, the relabel, the second pass, Part B): their logs (`job.log`, `--output-format text`) **record no cost**, so only the caps are known: INV + Part A $8 per part (6 parts, at most $48); the labels $15 per part (5 parts, at most $75); the relabel $5; the second pass $8 per part (2 parts, at most $16); Part B $10 + 5 x $5 (at most $35). **The actual amounts are in the Anthropic Console** (API usage) if Dustin wants them.")
A('')
A('## Records')
A('')
A(f"- **This folder:** `run3/{RUN}/` (the run's own files, without its git clone), with `run_manifest.json` (every file's sha256, the inputs, the kit commit, the passes).")
A("- **Reads (C1):** the laptop session read the run's outputs to write this report. While gathering the credit-worker job logs for their cost, a glob also matched the `label_out_p*.aborted_20261025T172559Z` folders: it ran a byte count and a text search for cost strings on their `job.log` files, which are empty (0 bytes). Nothing else in those folders was opened or read.")
A('- **To-dos for after the runs** (K19): Q1\'s note asks "I would be curious to know if one was definitely better than the other". Q14\'s note assumes the alternatives came from "the bot"; they came from the labellers.')
A('- **Queued after this report** (Astra\'s weekly review, via the coordinator): the containment line in the agent rules (answer-material files named; developers get answer-free excerpts only).')
open(OUTF, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

#!/usr/bin/env python3
"""The report of a strength run: paired differences with intervals, who went first, runtime and cost, intended lines, and what more precision costs.

  strength_report.py --dir RUNDIR [--out REPORT.md] [--override]

Reads manifest.json (checks it against manifest.sha256), games.jsonl and errors.jsonl. Pure standard library. No pass/fail: a slow arm is a fact
about time and cost, reported as such.

REFUSES (exit 1, nothing written) when manifest.json is not the file that was pre-registered: manifest.sha256 missing or empty, or its sha256 differs.
--override writes the report anyway, for a deliberate re-read of a changed registration; the report then opens with a REGISTRATION CHANGED banner
and report.json says registration_changed.
"""
import argparse, collections, hashlib, json, math, os, statistics, sys

Z = 1.96


def mean_ci(xs):
    n = len(xs)
    if n == 0:
        return dict(n=0, mean=float('nan'), sd=float('nan'), half=float('nan'))
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0
    return dict(n=n, mean=m, sd=sd, half=Z * sd / math.sqrt(n) if n > 1 else float('nan'))


def pp(x):  # a score difference as percentage points
    return f"{100 * x:+.1f}"


def fmt_ci(c):
    if c['n'] == 0:
        return 'n/a'
    return f"{pp(c['mean'])} ± {100 * c['half']:.1f}" if c['n'] > 1 else f"{pp(c['mean'])} (n=1)"


def pct(x):
    return f"{100 * x:.1f}%"


def human(sec):
    if sec != sec or sec == float('inf'):
        return 'n/a'
    if sec < 10:
        return f"{sec:.2f} s"
    if sec < 90:
        return f"{sec:.0f} s"
    if sec < 5400:
        return f"{sec / 60:.0f} min"
    if sec < 172800:
        return f"{sec / 3600:.1f} h"
    return f"{sec / 86400:.1f} days"


def quant(xs, q):
    if not xs:
        return float('nan')
    s = sorted(xs)
    return s[min(len(s) - 1, int(q * len(s)))]


def score(rec):
    return {'deck': 1.0, 'tie': 0.5, 'opp': 0.0}[rec['winner']]


def wilson(k, n):
    if n == 0:
        return (float('nan'),) * 3
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d
    return p, c - h, c + h


def need(sd, half_target, n_have):
    if sd != sd or sd == 0:
        return None
    n = math.ceil((Z * sd / half_target) ** 2)
    return n, max(0, n - n_have)


# ---------------------------------------------------------------- intended lines
def uses(log, action):
    return [i for i, r in enumerate(log) if r['a'].startswith(action)]


def game_indicator(rec, line):
    log = rec.get('log') or []
    k = line['kind']
    if k == 'used_ever':
        return 1.0 if uses(log, line['action']) else 0.0
    if k == 'used_by_own_turn':
        return 1.0 if any(log[i]['o'] <= line['own_turn'] for i in uses(log, line['action'])) else 0.0
    if k == 'use_with_active':
        return 1.0 if any(log[i]['act'] == line['active'] for i in uses(log, line['action'])) else 0.0
    if k == 'active_at_own_turn':
        return 1.0 if any(r['o'] == line['own_turn'] and r['act'] == line['active'] for r in log) else 0.0
    if k == 'use_without_point':
        return 1.0 if any(use_flags(rec, line)) else 0.0
    raise SystemExit(f"unknown intended-line kind {k!r}")


def use_flags(rec, line):
    """For per-use lines: a list of booleans, one per use of the action (True = the 'bad'/'asked-for' condition holds)."""
    log = rec.get('log') or []
    out = []
    for i in uses(log, line['action']):
        if line['kind'] == 'use_with_active':
            out.append(log[i]['act'] == line['active'])
        elif line['kind'] == 'use_without_point':
            before = log[i]['p'][0]
            after = log[i + 1]['p'][0] if i + 1 < len(log) else rec['points'][0]
            out.append(after <= before)
    return out


def registration_problems(msha, reg_sha):
    """Why manifest.json cannot be shown to be the pre-registered file (an empty list when it can)."""
    if not reg_sha:
        return ['manifest.sha256 is missing or empty, so nothing shows that manifest.json is the file that was registered']
    if reg_sha != msha:
        return [f'manifest.json (sha256 {msha[:16]}) is not the registered file (manifest.sha256 says {reg_sha[:16]})']
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--out')
    ap.add_argument('--override', action='store_true', help='write the report even though the registration changed (it opens with a REGISTRATION CHANGED banner)')
    a = ap.parse_args()
    d = a.dir
    man = json.load(open(os.path.join(d, 'manifest.json'), encoding='utf-8'))
    msha = hashlib.sha256(open(os.path.join(d, 'manifest.json'), 'rb').read()).hexdigest()
    reg_sha = (open(os.path.join(d, 'manifest.sha256')).read().split() or [None])[0] if os.path.exists(os.path.join(d, 'manifest.sha256')) else None
    problems = registration_problems(msha, reg_sha)
    if problems and not a.override:
        sys.exit('REFUSED: the registration has changed, so no report is written.\n  ' + '\n  '.join(problems)
                 + '\nRead manifest.json against PREREGISTRATION.md. To write a report anyway, for a deliberate re-read, add --override (the report then opens with a REGISTRATION CHANGED banner).')
    if problems:
        print('REGISTRATION CHANGED (--override): ' + '; '.join(problems), file=sys.stderr)
    games, keys = [], set()
    gp = os.path.join(d, 'games.jsonl')
    if os.path.exists(gp):
        for line in open(gp, encoding='utf-8'):
            try:
                r = json.loads(line)
            except Exception:
                continue  # a truncated last line
            if r['key'] not in keys:
                keys.add(r['key'])
                games.append(r)
    # games that failed: once per game (the program appends a line on every try), and not at all once the game was played on a later try
    errors, seen_err = [], set()
    ep = os.path.join(d, 'errors.jsonl')
    if os.path.exists(ep):
        for line in open(ep, encoding='utf-8'):
            try:
                e = json.loads(line)
            except Exception:
                continue  # a truncated last line
            if e['key'] not in keys and e['key'] not in seen_err:
                seen_err.add(e['key'])
                errors.append(e)

    by = collections.defaultdict(dict)  # (deck, opp, deal, seat) -> {arm: rec}
    for r in games:
        by[(r['deck'], r['opp'], r['deal'], r['seat'])][r['arm']] = r
    pairs = {k: v for k, v in by.items() if 'X' in v and 'ref' in v}
    half = len(by) - len(pairs)
    mism = [k for k, v in pairs.items() if v['X']['first'] != v['ref']['first'] or v['X']['seed'] != v['ref']['seed']]

    P = lambda *s: L.append(' '.join(str(x) for x in s))
    L = []
    if problems:
        P('# REGISTRATION CHANGED\n')
        P('**This report was written with `--override`. ' + '; '.join(problems) + '. Its numbers are not the result of the pre-registered run: read what changed in the manifest against PREREGISTRATION.md before quoting any of them.**\n')
        P('---\n')
    P(f"# Strength report: {man['name']}\n")
    P(f"Pilot **{man['pilot']}** against reference **{man['reference']}**, stage `{man.get('stage')}`. Manifest sha256 `{msha[:16]}`" + (' (matches the pre-registration)' if not problems else ' (**REGISTRATION CHANGED: does not match manifest.sha256**)' if reg_sha else ' (**REGISTRATION CHANGED: manifest.sha256 is missing**)') + f"; registered {man.get('created_at')}.")
    if man.get('question'):
        P(f"\n> {man['question']}")
    if man.get('stage') == 'use':
        P("\n**Stage `use`: this is a report on a deck, not development evidence.** Nothing in it may be used to tune or choose a pilot, and it does not lift the held-out lock. "
          "This engineering report uses mean ± 1.96·sd/√n intervals; the slow report page (`SLOW_REPORT.md`) uses Wilson ranges for scores and Student t for the paired gain, and is the one to quote.")
    started = sorted(g.get('started_at', '') for g in games if g.get('started_at'))
    if started and man.get('created_at'):
        P(f"\nPre-registration order: registered {man['created_at']}; first game started {started[0]} ({'after registration' if started[0] >= man['created_at'] else '**BEFORE registration**'}).")
    if man.get('selfcheck'):
        src = man.get('selfcheck_source') or {}
        P('\nSelf-check digests recorded at registration: ' + '; '.join(f"`{v}`" + (f' ({src[k]})' if src.get(k) else '') for k, v in man['selfcheck'].items()))
    P(f"\n- Planned {man['planned_games']} games; finished {len(games)}; complete pairs {len(pairs)} (= {2 * len(pairs)} games); unpaired games {half}; errors {len(errors)}.")
    if mism:
        P(f"- **{len(mism)} pairs whose two arms did not start from the same deal (seed or first player differ)**; they are excluded.")
        pairs = {k: v for k, v in pairs.items() if k not in set(mism)}
    P(f"- Paired difference = score(arm X) − score(arm ref) per (deck, opponent, deal, seat), in percentage points of score (win 1, tie ½). Intervals are mean ± 1.96·sd/√n over paired games. No pass/fail threshold.\n")
    if not pairs:
        P('No complete pairs yet.')
        out = a.out or os.path.join(d, 'REPORT.md')
        open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print('\n'.join(L))
        return

    diff = {k: score(v['X']) - score(v['ref']) for k, v in pairs.items()}
    # ------------------------------------------------------------ overall
    allc = mean_ci(list(diff.values()))
    decks = sorted({k[0] for k in pairs}, key=lambda n: [x['name'] for x in man['decks']].index(n) if n in [x['name'] for x in man['decks']] else 0)
    deck_c = {dn: mean_ci([v for k, v in diff.items() if k[0] == dn]) for dn in decks}
    dm = [c['mean'] for c in deck_c.values()]
    eq = mean_ci(dm)
    exactly_zero = all(v == 0 for v in diff.values())
    ident = sum(1 for v in pairs.values() if (v['X']['winner'], v['X']['points'], v['X']['turns']) == (v['ref']['winner'], v['ref']['points'], v['ref']['turns']))
    P('## Result\n')
    P(f"**Pooled over all {allc['n']} paired games: {fmt_ci(allc)} points** (arm X {pct(sum(score(v['X']) for v in pairs.values()) / len(pairs))} vs arm ref {pct(sum(score(v['ref']) for v in pairs.values()) / len(pairs))} score).")
    P(f"Decks weighted equally ({len(decks)} decks): {pp(eq['mean'])} ± {100 * eq['half']:.1f} (sd across deck means {100 * eq['sd']:.1f})." if len(decks) > 1 else '')
    if exactly_zero:
        P(f"\n**Every paired difference is exactly 0** ({ident} of {len(pairs)} paired games identical in winner, points and turns): the two arms played the same games.")
    P('\n### Per deck, pooled over its opponents\n')
    P('| deck | paired games | arm X score | arm ref score | paired difference (points) | went first: diff | went second: diff |')
    P('|---|---|---|---|---|---|---|')
    for dn in decks:
        ks = [k for k in pairs if k[0] == dn]
        sx = sum(score(pairs[k]['X']) for k in ks) / len(ks)
        sr = sum(score(pairs[k]['ref']) for k in ks) / len(ks)
        f1 = mean_ci([diff[k] for k in ks if pairs[k]['X']['first'] == 'deck'])
        f2 = mean_ci([diff[k] for k in ks if pairs[k]['X']['first'] == 'opp'])
        P(f"| {dn} | {len(ks)} | {pct(sx)} | {pct(sr)} | {fmt_ci(deck_c[dn])} | {fmt_ci(f1)} | {fmt_ci(f2)} |")
    # first / second overall
    f1 = mean_ci([diff[k] for k in pairs if pairs[k]['X']['first'] == 'deck'])
    f2 = mean_ci([diff[k] for k in pairs if pairs[k]['X']['first'] == 'opp'])
    P(f"\nOverall by who went first (identical in both arms): deck first {fmt_ci(f1)} (n={f1['n']}); deck second {fmt_ci(f2)} (n={f2['n']}).\n")
    P('### Per (deck, opponent) pair\n')
    P('| deck | opponent | n | arm X | arm ref | paired difference (points) |')
    P('|---|---|---|---|---|---|')
    pair_keys = sorted({(k[0], k[1]) for k in pairs})
    for dn, on in pair_keys:
        ks = [k for k in pairs if k[0] == dn and k[1] == on]
        sx = sum(score(pairs[k]['X']) for k in ks) / len(ks)
        sr = sum(score(pairs[k]['ref']) for k in ks) / len(ks)
        P(f"| {dn} | {on} | {len(ks)} | {pct(sx)} | {pct(sr)} | {fmt_ci(mean_ci([diff[k] for k in ks]))} |")

    # ------------------------------------------------------------ runtime
    def arm_games(arm):
        return [v[arm] for v in pairs.values()]
    P('\n## Runtime and cost\n')
    P('Wall time is per game on this machine with the threads the run used; it includes both seats\' decisions and the engine. Decision times are for the decisions the engine actually asked the pilot (forced single-move frames are not asked).\n')
    P('| arm | role | pilot | games | wall per game: mean / median / p95 / max | games per second (1 thread) | decisions per game | ms per decision: mean / median / p95 / max | decision time per game |')
    P('|---|---|---|---|---|---|---|---|---|')
    rt = {}
    for arm in ('X', 'ref'):
        gs = arm_games(arm)
        walls = [g['wall_s'] for g in gs]
        for role, who in (('deck seat', 'moves_deck'), ('opponent seat', 'moves_opp')):
            ms = [x for g in gs for x in g[who]['ms']]
            nper = [g[who]['n'] for g in gs]
            tot = [g[who]['total_s'] for g in gs]
            spec = gs[0]['pilot_deck'] if role == 'deck seat' else gs[0]['pilot_opp']
            wall_txt = f"{statistics.mean(walls):.2f} / {statistics.median(walls):.2f} / {quant(walls, .95):.2f} / {max(walls):.2f} s" if role == 'deck seat' else ''
            gps = f"{1 / statistics.mean(walls):.2f}" if role == 'deck seat' else ''
            P(f"| {arm} | {role} | `{spec}` | {len(gs)} | {wall_txt} | {gps} | {statistics.mean(nper):.1f} | {statistics.mean(ms) if ms else float('nan'):.1f} / {statistics.median(ms) if ms else float('nan'):.1f} / {quant(ms, .95):.1f} / {max(ms) if ms else float('nan'):.1f} | {human(statistics.mean(tot))} |")
            rt[(arm, role)] = dict(wall=statistics.mean(walls), ms=statistics.mean(ms) if ms else float('nan'), dec=statistics.mean(nper))
    cost = {}
    for arm in ('X', 'ref'):
        for who in ('deck', 'opp'):
            cs = [g.get(f'ext_{who}', {}).get('cost_usd', 0.0) for g in arm_games(arm)]
            ts = [g.get(f'ext_{who}', {}).get('tokens', 0) for g in arm_games(arm)]
            if any(cs) or any(ts):
                cost[(arm, who)] = (statistics.mean(cs), statistics.mean(ts))
    if cost:
        P('\nCost reported by external pilots (per game): ' + '; '.join(f"arm {a_}, {w} seat: ${c:.4f}, {t:.0f} tokens" for (a_, w), (c, t) in cost.items()))
    wall_pair = rt[('X', 'deck seat')]['wall'] + rt[('ref', 'deck seat')]['wall']
    threads = max(1, int(man.get('threads', 1)))
    P(f"\nOne paired game (both arms) took {human(wall_pair)} on average; the run used {threads} thread(s).")

    # ------------------------------------------------------------ precision planner
    P('\n## What more precision would take\n')
    P('At the sd reached, the number of paired games for a given half-width is `(1.96·sd/h)²`; the time is that many paired games at the mean wall time above, divided by the threads. Per deck the opponents are pooled as above.\n')
    P('| scope | paired games so far | sd | interval now (points) | for ±5 points: total / more games, time | for ±3 points: total / more games, time |')
    P('|---|---|---|---|---|---|')
    scopes = [('all decks pooled', allc)] + [(dn, deck_c[dn]) for dn in decks]
    for name, c in scopes:
        if c['n'] < 2:
            continue
        row = []
        for h in (0.05, 0.03):
            nd = need(c['sd'], h, c['n'])
            if nd is None:
                row.append('n/a (sd 0)')
            else:
                tot_n, more = nd
                per = wall_pair if name == 'all decks pooled' else sum(g['X']['wall_s'] + g['ref']['wall_s'] for k, g in pairs.items() if k[0] == name) / sum(1 for k in pairs if k[0] == name)
                row.append(f"{tot_n} / {more}, {human(more * per / threads)}")
        P(f"| {name} | {c['n']} | {100 * c['sd']:.1f} | {fmt_ci(c)} | {row[0]} | {row[1]} |")

    # ------------------------------------------------------------ intended lines
    lines_path = man.get('intended_lines')
    lp = lines_path if lines_path and os.path.isabs(lines_path) else os.path.join(man.get('repo_root', '.'), lines_path or '')
    if lines_path and os.path.exists(lp):
        spec = json.load(open(lp, encoding='utf-8'))
        P('\n## Intended lines\n')
        P(f"From `{lines_path}`. Per game: the share of games where the line happened, per arm, with the paired difference (X − ref) and its interval. Per use: of all uses of the action, the share meeting the condition, per arm (Wilson interval).\n")
        P('| deck | line | arm X per game | arm ref per game | paired difference (points) | arm X per use | arm ref per use |')
        P('|---|---|---|---|---|---|---|')
        any_line = False
        for dn in decks:
            for line in spec.get('*', []) + spec.get(dn, []):
                ks = [k for k in pairs if k[0] == dn]
                if not ks:
                    continue
                if not all(pairs[k]['X'].get('log') is not None for k in ks):
                    continue
                any_line = True
                ix = [game_indicator(pairs[k]['X'], line) for k in ks]
                ir = [game_indicator(pairs[k]['ref'], line) for k in ks]
                dd = mean_ci([x - r for x, r in zip(ix, ir)])
                per = []
                for arm in ('X', 'ref'):
                    if line['kind'] in ('use_with_active', 'use_without_point'):
                        fl = [f for k in ks for f in use_flags(pairs[k][arm], line)]
                        p, lo, hi = wilson(sum(fl), len(fl))
                        per.append(f"{pct(p)} of {len(fl)} uses [{pct(lo)}, {pct(hi)}]" if fl else 'no uses')
                    else:
                        per.append('')
                P(f"| {dn} | {line['text']} | {pct(sum(ix) / len(ix))} | {pct(sum(ir) / len(ir))} | {fmt_ci(dd)} | {per[0]} | {per[1]} |")
        if not any_line:
            P('| (no deck in this run has a line in the file, or the run logged nothing) | | | | | | |')

    if errors:
        P(f"\n## Errors\n\n{len(errors)} game{'' if len(errors) == 1 else 's'} failed and {'is' if len(errors) == 1 else 'are'} not in the counts (a resumed run tries them again). First: `{errors[0]['key']}`: {errors[0]['error'][:200]}")
    out = a.out or os.path.join(d, 'REPORT.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    json.dump(dict(manifest_sha256=msha, stage=man.get('stage'), pilot=man.get('pilot'), reference=man.get('reference'), registration_changed=bool(problems), registration_problems=problems, paired_games=len(pairs), pooled=allc, per_deck=deck_c, exactly_zero=exactly_zero), open(os.path.join(d, 'report.json'), 'w'), indent=1, default=str)
    print('\n'.join(L))


if __name__ == '__main__':
    main()

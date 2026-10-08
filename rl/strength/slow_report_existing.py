#!/usr/bin/env python3
"""A slow-report page for one deck built from games that were ALREADY played: existing development evidence, not a fresh test.

  slow_report_existing.py --deck 03-wailord-indeedee-wall --dev rl/results/strength_2026-10-03_kx3_dev --tool rl/results/strength_2026-10-06_kx3_tools_gate3 --out DIR

Reads (and never changes) two registered strength runs and writes DIR/SLOW_REPORT_EXISTING.md:
  * --dev: the kx3 development run, whose kx3 build must be the pinned one (slow_report_pin.json): question 1, how the deck does with kx3 and whether that is
    better than with km3 (the run's own km3 baseline games on the same deals);
  * --tool: gate 3 of the Tool tie-break, a different, candidate build played on the development run's own deals: question 2, whether the rule changes what kx3
    does with this deck (decisions changed and results changed are counted separately, from the games).
Reporting rule (Astra, adopted Oct 7): state the question first, then the size, written "N kx3 games + N cheap km3 baseline games", say which games each range
refers to, and never dismiss a wide interval: say what it can and cannot answer. The page is labelled existing development evidence, is not the km3 floor check,
and has no pass or fail line. It shares its arithmetic (Wilson ranges, the t interval) with slow_report.py.
"""
import sys
sys.dont_write_bytecode = True
import argparse, hashlib, json, math, os, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slow_report as SR  # noqa: E402

SC = SR.SCORE
KIND = 'existing development evidence, not a fresh test'


def say_factory(tag):
    def say(msg):
        print(f'[{tag}; {KIND}] {msg}', flush=True)
    return say


def load_run(path):
    man, msha = SR.load_registered(os.path.abspath(path))
    return man, msha, {g['key']: g for g in SR.load_games(os.path.abspath(path))}


def facts(g):
    """What makes two games the same game: deal, first player, result, points, turns, plies, decision counts and every logged decision (timings aside)."""
    return (g['seed'], g['first'], g['winner'], g['points'], g['turns'], g['plies'], g['moves_deck']['n'], g['moves_opp']['n'],
            [{k: v for k, v in d.items() if k != 'ms'} for d in (g.get('log') or [])])


def decisions(g):
    return [{k: v for k, v in d.items() if k != 'ms'} for d in (g.get('log') or [])]


def rel(path):
    """The repo-relative spelling of a results folder (from rl/results on), wherever the checkout sits; any other path as given."""
    p = os.path.abspath(path).replace(os.sep, '/')
    i = p.rfind('/rl/results/')
    return p[i + 1:] if i >= 0 else p


def file_sha(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def first_started(games):
    s = sorted(g.get('started_at', '') for g in games.values() if g.get('started_at'))
    return s[0] if s else None


def registered_first(games, man):
    """True when the first game started at or after the registration time; None when the games carry no start time (it cannot be checked)."""
    s = first_started(games)
    return None if s is None else s >= man['created_at']


def build(deck, dev_dir, tool_dir, pin):
    dman, dmsha, dall = load_run(dev_dir)
    tman, tmsha, tall = load_run(tool_dir)
    if dman.get('stage') != 'dev':
        SR.die(f'REFUSED: {dev_dir} is not a development run (stage {dman.get("stage")!r})')
    if dman.get('pilot') != pin['pilot'] or dman.get('program_sha256') != pin['program_sha256']:
        SR.die(f'REFUSED: {dev_dir} was not played by the pinned build ({pin["pilot_label"]}, program sha256 {pin["program_sha256"][:12]}); this page is for the pinned build only')
    if not str(tman.get('pilot', '')).endswith('_tools'):
        SR.die(f'REFUSED: {tool_dir} is not a run of the Tool tie-break build (its pilot is {tman.get("pilot")!r})')
    if tman.get('stage') != 'dev':
        SR.die(f'REFUSED: {tool_dir} is not a development run (stage {tman.get("stage")!r})')
    dg = {k: g for k, g in dall.items() if g['deck'] == deck}
    tg = {k: g for k, g in tall.items() if g['deck'] == deck}
    for label, d in (('the development run', dg), ('the gate-3 run', tg)):
        if not any(g['arm'] == 'X' for g in d.values()):
            SR.die(f'REFUSED: deck {deck} has no kx3 games in {label}')
    stray = [k for k in tg if k not in dg]
    if stray:
        SR.die(f'REFUSED: {stray[0]} is not a development-run deal, so the gate-3 games cannot be paired with the development run ({len(stray)} such games)')
    panel = [o['name'] for o in dman['opponents']]
    want = len(panel) * dman['deals'] * len(dman['seats'])
    per_list = dman['deals'] * len(dman['seats'])
    for label, d in (('the development run', dg), ('the gate-3 run', tg)):
        for arm, who in (('X', 'kx3'), ('ref', 'baseline')):
            have = sum(1 for g in d.values() if g['arm'] == arm)
            if have != want:
                SR.die(f'REFUSED: {label} has {have} of the {want} {who} games planned for {deck}, so a page that states the full design would not describe it. Nothing was written.')
            for opp in panel:  # every list has its deals x seats games, so "each row" below is true of each row
                n_opp = sum(1 for g in d.values() if g['arm'] == arm and g['opp'] == opp)
                if n_opp != per_list:
                    SR.die(f'REFUSED: {label} has {n_opp} {who} games for {deck} against {opp} where {per_list} are planned, so the rows of the table would not all describe the same design. Nothing was written.')
    # the pairing is only readable if the gate-3 run replays the same deals: the km3 baseline replays exactly, and every kx3 game starts from its development-run deal
    ref_bad = sum(1 for k, g in tg.items() if g['arm'] == 'ref' and facts(g) != facts(dg[k]))
    if ref_bad:
        SR.die(f'THE PAIRING IS VOID: {ref_bad} of the {want} {pin["reference"]} baseline games in the gate-3 run do not replay the development run, so the build does not reproduce '
               'the development run and on-minus-off cannot be read against it. Nothing was written.')
    deal_bad = sum(1 for k, g in tg.items() if g['arm'] == 'X' and (g['seed'], g['first']) != (dg[k]['seed'], dg[k]['first']))
    if deal_bad:
        SR.die(f'THE PAIRING IS VOID: {deal_bad} of the {want} {pin["pilot"]} games in the gate-3 run did not start from the development run\'s deal (seed or first player differ), so on-minus-off '
               'would compare different games. Nothing was written.')
    pooled_pairs = sum(1 for g in tall.values() if g['arm'] == 'X')  # what gate 3 pooled on its own page: every kx3 game of the run, all of its decks
    pooled_decks = len({g['deck'] for g in tall.values()})
    return dict(deck=deck, dev_dir=dev_dir, tool_dir=tool_dir, dman=dman, dmsha=dmsha, tman=tman, tmsha=tmsha, dg=dg, tg=tg, panel=panel, pin=pin, ref_same=want,
                pooled_pairs=pooled_pairs, pooled_decks=pooled_decks)


def mean_half(xs):
    n = len(xs)
    m = statistics.mean(xs)
    sd = statistics.stdev(xs) if n > 1 else 0.0
    return n, m, sd, (SR.t_crit(n - 1) * sd / math.sqrt(n) if n > 1 else float('nan'))


def page(b):
    deck, dg, tg, panel, pin = b['deck'], b['dg'], b['tg'], b['panel'], b['pin']
    pilot, ref = pin['pilot'], pin['reference']
    headline = SR.headline_of(pin, deck)
    k = len(panel)
    deals, seats = b['dman']['deals'], len(b['dman']['seats'])
    xd = {key: g for key, g in dg.items() if g['arm'] == 'X'}
    rd = {key: g for key, g in dg.items() if g['arm'] == 'ref'}
    xs = [SC[g['winner']] for g in xd.values()]
    rs = [SC[g['winner']] for g in rd.values()]
    n = len(xs)
    L = []
    P = L.append
    P(f'# Slow report from existing games: {deck}\n')
    reg_before = [registered_first(g_, m_) for g_, m_ in ((dg, b['dman']), (b['tg'], b['tman']))]
    P(f'**Existing development evidence, not a fresh test.** Nothing was played for this page: it reads games that were already played, by the {pilot} development run '
      f'({b["dman"]["created_at"][:10]}) and by gate 3 of the Tool tie-break ({b["tman"]["created_at"][:10]}), ' +
      (f"both registered before the first of this deck's games (only {deck}'s games were read, so that is all that was checked)." if all(r is True for r in reg_before) else
       '**but not both were registered before their games: see "Where these games come from".**' if False in reg_before else
       '**but the order of registration and games could not be confirmed for both (a game has no start time): see "Where these games come from".**') + '\n')
    P(f'**{headline}** ({k} public lists: {", ".join(panel)}). This is not the km3 floor check, which has its own page and its own result and is not changed by anything here; there is no pass or fail line.\n')

    # ------------------------------------------------------------------------------------------------ question 1
    P(f'## Question 1: how does {deck} do with {pilot}, and is that better than with {ref}?\n')
    kg = SR.kg
    size = f'{kg(n, pilot)} + {kg(len(rs), ref, True)}'
    P(f'Size: {size} ({SR.plural(deals, "deal")} x {seats} seats against each of the {k} public lists; the baseline games are the same deals with {ref} on the deck). '
      f'Source: the development run.\n')
    p, lo, hi = SR.wilson_range(xs)
    P(f'- With {pilot}, {deck} scored **{SR.pct1(p)}** over the {kg(n, pilot)}: probably between {SR.pct1(lo)} and {SR.pct1(hi)} '
      f'(95% interval; this range refers to the {kg(n, pilot)}). A win counts 1, a tie 1/2, a loss 0.')
    pr = sum(rs) / len(rs)
    P(f'- With {ref}, on the same deals, it scored {SR.pct1(pr)} over the {kg(len(rs), ref, True)}.')
    d = [SC[g['winner']] - SC[rd[key[: -len('X')] + 'ref']['winner']] for key, g in xd.items() if key[: -len('X')] + 'ref' in rd]
    gn, gm, gsd, gh = mean_half(d)
    paired_games = f'{SR.plural(gn, "paired game")}, each a deal and seat played by both pilots: {kg(gn, pilot)} + {kg(gn, ref, True)}'
    if gn < 2:
        P(f'- The gain: {pilot} scored **{SR.signed_points(gm)} points** compared with {ref} on the same deals; with one paired game no range can be given.')
    elif gsd == 0:
        P(f'- The gain: {pilot} scored **{SR.signed_points(gm)} points** compared with {ref} on the same deals; every one of the {gn} paired games gave the same difference, so no spread can be estimated from them.')
    else:
        P(f'- The gain: {pilot} scored **{SR.signed_points(gm)} points** compared with {ref} on the same deals, {SR.range_points(gm, gh)} '
          f'(95% interval). That range refers to the {paired_games}.')
    walls = [g['wall_s'] for g in xd.values()]
    P(f'- Time: {pilot} took {SR.fmt_s(statistics.mean(walls))} a game on average on this deck (about {SR.human_time(statistics.mean(walls))}; slowest {SR.fmt_s(max(walls))}), '
      f'{b["dman"].get("threads", 2)} games at a time; the {ref} baseline games took {SR.fmt_s(statistics.mean(g["wall_s"] for g in rd.values()))} each.\n')
    gain_note = SR.gain_range_note(pilot, ref, gn, gm, gh) + ' ' if gn >= 2 and gsd > 0 else ''
    gain_scale = f" (the gain's range is {SR.range_width_points(gm, gh):.1f} points wide)" if gn >= 2 and gsd > 0 else ''
    P(f'What the {n}-game range can tell and cannot tell: it can tell whether {pilot} plays this deck near, clearly above or clearly below an even score against these {k} lists '
      f'({SR.pct1(lo)} to {SR.pct1(hi)} here), and it can tell a large gain over {ref} from none at all{gain_scale}. {gain_note}'
      f'It cannot tell a gain of a point or two from a gain of ten: {n} games decide only that much, and a wide range is a statement of how much {n} games decide, not an answer of "nothing". '
      f'More deals narrow it (the cost table in the slow-report plan gives the hours).\n')

    P('## Against each public list\n')
    P(f'| opponent ({ref}) | {pilot} games | score | 95% range |')
    P('|---|---|---|---|')
    for opp in panel:
        s = [SC[g['winner']] for g in xd.values() if g['opp'] == opp]
        if not s:
            P(f'| {opp} | 0 | n/a | n/a |')
            continue
        pp, l1, h1 = SR.wilson_range(s)
        P(f'| {opp} | {len(s)} | {SR.pct1(pp)} | {SR.pct1(l1)} to {SR.pct1(h1)} |')
    per = len([1 for g in xd.values() if g['opp'] == panel[0]])
    P(f"\nEach row's range refers to the {per} {pilot} games against that list; with so few games it can separate a very easy or very hard list from an even one, "
      f'not two similar lists from each other.\n')

    # ------------------------------------------------------------------------------------------------ question 2
    P(f'## Question 2: does the Tool tie-break change what {pilot} does with this deck?\n')
    pairs = []
    ref_same = b['ref_same']  # build() has already refused (VOID) unless every baseline game and every kx3 deal replays
    for key, g in sorted(b['tg'].items()):
        if g['arm'] == 'X':
            off = dg[key]
            pairs.append((SC[g['winner']] - SC[off['winner']], decisions(g) != decisions(off), g['winner'] != off['winner'],
                          (g['points'] != off['points'] or g['turns'] != off['turns']), facts(g) != facts(off), SC[g['winner']], SC[off['winner']], key))
    m = len(pairs)
    tool_pilot = b['tman']['pilot']
    P(f'Existing development evidence too: gate 3 of the Tool tie-break (`{rel(b["tool_dir"])}`), a candidate build ({tool_pilot}, program sha256 `{str(b["tman"]["program_sha256"])[:12]}`, '
      f'**not the pinned build**), played on the development run\'s own deals.\n')
    P(f'Size: {kg(m, pilot)} with the Tool tie-break on + the {m} existing {pilot} games with it off, paired by deal and seat ({m} paired games; '
      f'and {kg(ref_same, ref, True)}, which the gate-3 build replays exactly).\n')
    P(f'Build check: {ref_same} of the {ref_same} {ref} baseline games in the gate-3 run replay the development run exactly (same deals, same moves, same results), and all {m} {pilot} games '
      f'in the gate-3 run start from the development run\'s own deal (same seed, same first player), so the two runs are the same deals played by the same {ref}.\n')
    dec = sum(1 for x in pairs if x[1])
    win = sum(1 for x in pairs if x[2])
    pts = sum(1 for x in pairs if x[3])
    any_ = sum(1 for x in pairs if x[4])
    P(f'- {dec} of the {m} pairs had a logged decision that differed (the rule acted).')
    P(f'- {win} of the {m} pairs had a different winner.')
    P(f'- {pts} of the {m} pairs ended with different points or a different number of turns.')
    if any_ != dec:
        P(f'- {any_} of the {m} pairs differed in some way at all (gate 3\'s own count: any logged decision, the points, the turns, the number of plies).')
    diffs = [x[0] for x in pairs]
    dn, dm, dsd, dh = mean_half(diffs)
    if dsd == 0 and dm == 0:
        P(f'- On minus off: **{SR.signed_points(dm)} points**: every one of the {dn} on-minus-off differences was exactly 0, so no spread can be estimated from them '
          f'(this refers to the {dn} paired games played with the Tool tie-break on and off).')
    elif dn < 2 or dsd == 0:
        P(f'- On minus off: **{SR.signed_points(dm)} points** over the {dn} paired games played with the Tool tie-break on and off; no spread can be estimated from them.')
    else:
        P(f'- On minus off: **{SR.signed_points(dm)} points**, {SR.range_points(dm, dh)} (95% interval; this range refers to the {dn} paired games played with the Tool tie-break on and off).')
    on_km = [x[5] - SC[rd[x[7][: -len('X')] + 'ref']['winner']] for x in pairs]
    off_km = [x[6] - SC[rd[x[7][: -len('X')] + 'ref']['winner']] for x in pairs]
    n1, m1, s1, h1_ = mean_half(on_km)
    n2, m2, s2, h2_ = mean_half(off_km)
    def with_spread(mean, sd, half, which):
        # a range only where the paired differences vary; where every one of them is the same there is no spread to estimate from them
        return (f'{which} {SR.signed_points(mean)} points ({SR.range_points(mean, half)})' if n1 >= 2 and sd > 0
                else f'{which} {SR.signed_points(mean)} points (no spread to give: every difference is the same)')
    P(f'- For context, {pilot} minus {ref} on the same deals: {with_spread(m1, s1, h1_, "with the Tool tie-break on")}, {with_spread(m2, s2, h2_, "off")}; '
      f'each range refers to the {n1} paired games.\n')
    wp, wlo, whi = SR.wilson_range([1.0 if x[2] else 0.0 for x in pairs])
    if win == 0:
        share = (f'no winner changed in {m} pairs, so the share of deals whose winner the rule changes is probably no more than about {100 * whi:.1f} in 100 '
                 f'(95% Wilson bound on {win} of {m})')
    else:
        share = (f'{win} of {m} winners changed, which puts the share of deals whose winner the rule changes between about {100 * wlo:.1f} and {100 * whi:.1f} in 100 '
                 f'(95% Wilson range on {win} of {m})')
    tail = (f'and a rule that acts in {dec} of {m} games but changes no winner has not been shown to be harmless or useful: whether it would ever change a result on a deck like this is '
            'a question for more deals.' if win == 0 else f'and {"the one changed winner is" if win == 1 else f"the {win} changed winners are"} what the on-minus-off figure above counts, for or against the rule; '
            f'{"one is" if win == 1 else "they are"} too few to say more.')
    P(f'What this can tell and cannot tell: it can tell what the rule did on these {m} paired games ({dec} had a changed decision, {win} a changed winner), and it can put a bound on how often it changes a winner: {share}. '
      f"It cannot tell what the rule does on other deals or other decks (gate 3 pooled {b['pooled_pairs']} paired games, {kg(b['pooled_pairs'], pilot)} with the rule on against the same deals with it off, "
      f"over {b['pooled_decks']} deck{'' if b['pooled_decks'] == 1 else 's'} on its own page), {tail}\n")

    # ------------------------------------------------------------------------------------------------ provenance
    P('## Where these games come from\n')
    for label, d_, man, msha, games in (('Development run', b['dev_dir'], b['dman'], b['dmsha'], dg), ('Gate 3 of the Tool tie-break', b['tool_dir'], b['tman'], b['tmsha'], tg)):
        gp = os.path.join(os.path.abspath(d_), 'games.jsonl')
        started = first_started(games)
        before = registered_first(games, man)
        P(f"- {label}: `{rel(d_)}`; stage {man['stage']}; pilot `{man['pilot']}` against `{man['reference']}`; program `{man.get('program')}` sha256 `{str(man.get('program_sha256'))[:12]}`; "
          f"manifest sha256 `{msha[:16]}` (matches manifest.sha256); registered {man['created_at']}, first {deck} game started {started or 'at a time that is not recorded'}"
          + (" (registered before the first of this deck's games)" if before else ' (**NOT registered before the games**)' if before is False else ' (**order of registration and games not confirmed**)')
          + f"; games.jsonl sha256 `{file_sha(gp)[:12]}`; only deck {deck} was read ({len(games)} games).")
    P(f"- The pinned build for fresh reports is `{pin['program']}` sha256 `{pin['program_sha256'][:12]}` ({pin['pilot_label']}); the development run was played by that build.")
    P(f'- Seeds {b["dman"]["seed_base"]} + p x {b["dman"]["pair_stride"]} + i; the gate-3 run used the same deals.\n')

    P('## What this page does not say\n')
    P(f'It is not a fresh test: nothing here was played for the question asked, so it cannot show how the deck would do with new deals. It is not the km3 floor check (km3 on both sides, '
      f'with its own floor line and its own result); the two answer different questions and neither changes the other. It is not a ranking against other decks, it says nothing about decks outside '
      f'the {k} public lists or about the ladder, and there is no pass or fail line: whether {deck} is worth playing is a call for the player. The {k} lists count equally, and '
      f'{pilot} is better informed here than it would be against a person, because its opponent is always one of the {k} lists and always plays like the {ref} it imagines when it looks ahead.\n')
    return '\n'.join(L).rstrip() + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='A slow-report page for one deck from existing games (see the module docstring).')
    ap.add_argument('--deck', required=True)
    ap.add_argument('--dev', required=True, help='the kx3 development run directory')
    ap.add_argument('--tool', required=True, help='the gate-3 (Tool tie-break) run directory')
    ap.add_argument('--out', required=True, help='directory for SLOW_REPORT_EXISTING.md')
    ap.add_argument('--pin', default=SR.DEFAULT_PIN)
    a = ap.parse_args(argv)
    pin = SR.load_pin(a.pin)
    say = say_factory(SR.headline_of(pin, a.deck))
    try:
        b = build(a.deck, a.dev, a.tool, pin)
        text = page(b)
    except SystemExit as e:
        if isinstance(e.code, str) and not e.code.startswith('['):
            raise SystemExit(f'[{SR.headline_of(pin, a.deck)}; {KIND}] {e.code}') from None
        raise
    os.makedirs(a.out, exist_ok=True)
    path = os.path.join(a.out, 'SLOW_REPORT_EXISTING.md')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
    say(f'SLOW_REPORT_EXISTING.md written in {a.out}')
    for line in text.splitlines():
        if line.startswith('- ') and ('scored' in line or 'On minus off' in line or 'different winner' in line or 'logged decision' in line or 'The gain' in line):
            say(line[2:].replace('**', '').replace('`', ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())

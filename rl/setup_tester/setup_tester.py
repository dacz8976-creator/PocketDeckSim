#!/usr/bin/env python3
"""Setup tester (rl/setup_tester/SPEC.md): for one deck and many versions of it, how often the cards let the deck carry
out its opening plan, on the same deals for every version. Standard library only; no engine program; cards only through
lib/card.py. It does not say who wins and does not search for the best list.

    python3 rl/setup_tester/setup_tester.py --versions FILE [--deals 100000] [--clock-deals 20000] [--workers 1]
                                            [--clocks his,his_seat,bot,fast,medium,slow] [--out DIR] [--name NAME]
    python3 rl/setup_tester/setup_tester.py --first-run        the SPEC's first run (his list beside deck 01)

The versions file (JSON): {"base": path, "versions": {name: path-or-diff} or [path-or-diff, ...], "swap_pool": [...],
"plan": path}. A diff is a list such as ["-1 Copycat B1 225", "+1 Juliana B3a 071"].
"""
import argparse
import collections
import hashlib
import importlib.util
import io
import json
import math
import multiprocessing
import os
import random
import re
import sys
import time
from operator import mul

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'lib'))

import consistency as cl     # noqa: E402
import deck_check            # noqa: E402
import st_clock as clk       # noqa: E402
import st_exact as ex        # noqa: E402
import st_sim as sim         # noqa: E402
from st_rng import Stream    # noqa: E402

Z = 1.96
SEED_BASE = sim.SEED_BASE
MAX_VERSIONS = 100
CLOCK_NAMES = ['his', 'his_seat', 'bot', 'fast', 'medium', 'slow']
CLOCK_LABEL = {'his': 'C-his', 'his_seat': 'C-his, seat-matched', 'bot': 'C-bot', 'fast': 'C-fixed fast',
               'medium': 'C-fixed medium', 'slow': 'C-fixed slow'}
HIS_LIST = 'rl/results/pause_games_new_2026-10-13/decks/KW261012_203719000.txt'
DECK01 = 'decks/dustin/01-muk-glimmora-kingambit-regigigas.txt'
HIS_ID, DECK01_ID = '73dfed58d1d6', '35d98d0dcaf2'


# ------------------------------------------------------------------------------------------------ decks and versions
def default_plan_path():
    return sim.DEFAULT_PLAN


def _id_of_text(text):
    p = os.path.join(ROOT, 'rl', 'results', 'ladder_validation', 'make_predictions.py')
    try:
        spec = importlib.util.spec_from_file_location('make_predictions', p)
        m = importlib.util.module_from_spec(spec)
        sys.modules.setdefault('make_predictions', m)
        spec.loader.exec_module(m)
        return m.card_list_sha256(text)[:12]
    except Exception:                                   # the id is a label; the run does not depend on it
        return None


def card_list_id(cards):
    c = collections.Counter((k.name, k.id) for k in cards)
    text = 'Energy: Darkness\n' + ''.join(f'{n} {nm} {cid}\n' for (nm, cid), n in sorted(c.items()))
    return _id_of_text(text)


def _cid(s):
    return cl.resolve(s)


def parse_diff(line):
    m = re.fullmatch(r'\s*([+-])(\d+)\s+(.+?)\s+(\S+ \S+)\s*', line)
    if not m:
        raise SystemExit(f'cannot read diff line {line!r}: expected "-1 Name SET NNN" or "+1 Name SET NNN"')
    return (1 if m.group(1) == '+' else -1) * int(m.group(2)), m.group(3), m.group(4)


def build_cards(path, diff=None):
    """The deck at `path` (a list of 20 cl.Card) with the diff applied; the result must pass lib/deck_check.py.
    Pick lists by card-list id, never by file name (SPEC "Inputs")."""
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    types, cards = cl.read_deck(full)
    count = collections.OrderedDict()
    for c in cards:
        count[c.id] = count.get(c.id, 0) + 1
    byid = {c.id: c for c in cards}
    for line in diff or []:
        n, name, cid = parse_diff(line)
        card = _cid(cid)
        if card is None:
            raise SystemExit(f'unknown card id {cid!r} in diff line {line!r}')
        if card.name.lower() != name.lower():
            raise SystemExit(f'diff line {line!r}: {cid} is {card.name!r}, not {name!r} (lib/card.py)')
        byid[card.id] = card
        count[card.id] = count.get(card.id, 0) + n
        if count[card.id] < 0:
            raise SystemExit(f'diff line {line!r} removes a card the list does not have')
    out = []
    for cid, n in count.items():
        out += [byid[cid]] * n
    rows = [(n, byid[cid].name, cid) for cid, n in count.items() if n > 0]
    bad = [m for sev, m in deck_check.check(os.path.basename(path), rows) if sev == 'ERROR']
    if bad:
        raise SystemExit('version fails lib/deck_check.py: ' + '; '.join(bad))
    return out


# ------------------------------------------------------------------------------------------------ measures
def measure_ids(cfg):
    ids = ['K1.t0'] + [f'K1.t{t}' for t in range(1, 6)] + [f'K2.t{t}' for t in range(2, 7)] \
        + [f'K6.t{t}' for t in range(3, 6)]
    ids += [f'G3.{nm}.t{t}' for nm in cfg['key_pokemon'] for t in range(1, 6)]
    ids += [f'G4.s1.t{t}' for t in range(2, 6)] + [f'G4.s2.t{t}' for t in range(2, 6)]
    ids += ['G5.any3'] + [f'G6.t{t}' for t in range(2, 6)]
    return ids


def setup_values(tr, cfg, cost):
    """One deal's setup measures, in measure_ids order, plus G5's count (a value measure)."""
    turns, key = tr['turns'], cfg['key_pokemon']
    main, pawn = cfg['main_attacker'], cfg['pawniard']
    v = [1 if pawn in tr['setup']['roots'] else 0]
    v += [1 if pawn in turns[t - 1]['roots'] else 0 for t in range(1, 6)]
    v += [1 if main in turns[t - 1]['in_play'] else 0 for t in range(2, 7)]
    v += [1 if (cfg['muk'] in turns[t - 1]['in_play'] and cfg['muk_partner'] in turns[t - 1]['in_play']) else 0
          for t in range(3, 6)]
    for nm in key:
        v += [1 if nm in turns[t - 1]['in_play'] else 0 for t in range(1, 6)]
    v += [1 if any(s >= 1 for s in turns[t - 1]['stages']) else 0 for t in range(2, 6)]
    v += [1 if any(s == 2 for s in turns[t - 1]['stages']) else 0 for t in range(2, 6)]
    empties = [1 if turns[t - 1]['empty'] else 0 for t in range(1, 6)]
    v += [1 if any(empties[:3]) else 0]
    v += [1 if turns[t - 1]['kg_energy'] >= cost else 0 for t in range(2, 6)]
    return v, sum(empties)


def clock_ids(horizon):
    return [f'K3.by{x}' for x in range(2, horizon + 1)] + ['K3.never', 'K3.k0', 'K3.k1', 'K3.k2', 'K3.k3p',
                                                          'K4', 'K5']


def clock_values(tr, cfg):
    """One deal's clock measures: 1 yes, 0 no, 2 undecided (the record could not say). SPEC "Opponent clock"."""
    H, T, und, first = tr['horizon'], tr['first_attack_turn'], tr['und_own'], tr['first']
    thr = 140 if cfg['blade_target'] <= 2 else 180
    out = []

    def event(Tev, X):
        if Tev is not None and Tev <= X and (und is None or Tev < und):
            return 1
        return 0 if (und is None or X < und) else 2

    by = [event(T, X) for X in range(2, H + 1)]
    out += by
    last = by[-1]
    out.append({1: 0, 0: 1, 2: 2}[last])
    kk = tr['blades'][0]['k'] if tr['blades'] else None
    for want in (0, 1, 2, 3):
        if kk is not None and (und is None or T < und):
            out.append(1 if (min(kk, 3) == want) else 0)
        else:
            out.append(0 if (und is None or H < und) else 2)
    big = next((b['turn'] for b in tr['blades'] if b['damage'] >= thr), None)
    out.append(event(big, H))
    j, uj = tr['pawniard_lost_j'], tr['und_j']
    if j is not None and (uj is None or j < uj):
        out.append(1)
    else:
        out.append(0 if uj is None or uj > H else 2)
    return out


def make_clock(name, root):
    if name == 'his':
        return clk.load_his(root)
    if name == 'his_seat':
        return clk.load_his(root, seat_matched=True)
    if name == 'bot':
        return clk.load_bot(root)
    return clk.FIXED[name]


def run_one(base_path, diff, n_deals, seed_base=SEED_BASE, clocks=None, clock_deals=20000, keep_vectors=False,
            cfg_over=None, plan=None, label=None, cards=None):
    """One version, every measure. Returns {'measures': ..., 'vectors': ... (if kept), 'label', 'list_id', ...}."""
    t0 = time.time()
    clocks = CLOCK_NAMES if clocks is None else clocks
    cfg = sim.load_cfg(plan, **(cfg_over or {}))
    base_cards = build_cards(base_path)
    cards = cards or build_cards(base_path, diff)
    ver = sim.Version(cards, base_cards, label or ' '.join(diff or []) or 'base')
    cost = cfg['attacker_cost']
    ids = measure_ids(cfg)
    vec = {m: bytearray(n_deals) for m in ids}
    g5 = bytearray(n_deals)
    for i in range(n_deals):
        tr = sim.play_deal(ver, i, i % 2 == 0, cfg, seed_base=seed_base)
        v, n5 = setup_values(tr, cfg, cost)
        for m, x in zip(ids, v):
            if x:
                vec[m][i] = 1
        g5[i] = n5
    vectors = {m: bytes(b) for m, b in vec.items()}
    vectors['G5.n5'] = bytes(g5)
    cv = {}
    for cname in clocks:
        c = make_clock(cname, ROOT)
        cids = clock_ids(cfg['horizon'])
        cvec = {m: bytearray(clock_deals) for m in cids}
        for i in range(clock_deals):
            tr = sim.play_deal(ver, i, i % 2 == 0, cfg, clock=c, seed_base=seed_base)
            for m, x in zip(cids, clock_values(tr, cfg)):
                if x:
                    cvec[m][i] = x
        for m in cids:
            vectors[f'{cname}|{m}'] = bytes(cvec[m])
    res = {'label': ver.label, 'list_id': card_list_id(cards), 'n_deals': n_deals, 'clock_deals': clock_deals,
           'clocks': list(clocks), 'measures': tally(vectors, n_deals, clock_deals), 'seconds': round(time.time() - t0, 1)}
    if keep_vectors:
        res['vectors'] = vectors
    return res


# ------------------------------------------------------------------------------------------------ tallies and statistics
def seat_mask(n, parity):
    """An int with byte i = 1 where deal i is going first (parity 0) or second (parity 1)."""
    pat = b'\x01\x00' if parity == 0 else b'\x00\x01'
    return int.from_bytes((pat * ((n + 1) // 2))[:n], 'little')


_T_YES = bytes(1 if i == 1 else 0 for i in range(256))
_T_UND = bytes(1 if i == 2 else 0 for i in range(256))


def _ints(b):
    return (int.from_bytes(b.translate(_T_YES), 'little'), int.from_bytes(b.translate(_T_UND), 'little'))


def tally(vectors, n_deals, clock_deals):
    out = {}
    for m, b in vectors.items():
        n = len(b)
        yes, und = _ints(b)
        row = {}
        for name, mask in (('first', seat_mask(n, 0)), ('second', seat_mask(n, 1)), ('pooled', (1 << (8 * n)) - 1)):
            nn = (mask & int.from_bytes(b'\x01' * n, 'little')).bit_count()
            if m == 'G5.n5':
                sel = b[0::2] if name == 'first' else b[1::2] if name == 'second' else b
                row[name] = {'x': sum(sel), 'n': len(sel)}
            else:
                row[name] = {'x': (yes & mask).bit_count(), 'n': nn}
                if '|' in m:
                    row[name]['und'] = (und & mask).bit_count()
        out[m] = row
    return out


def rate(res, m, seat='pooled'):
    r = res['measures'][m][seat]
    return r['x'] / r['n']


def wilson(x, n):
    """95% Wilson score interval for x of n, as fractions."""
    if n == 0:
        return (float('nan'), float('nan'))
    p = x / n
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z / den * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def paired(diffs):
    """Mean of the per-deal differences and its 95% normal interval: mean +- 1.96 x sd / sqrt(n), sd with n - 1.
    Copied from rl/results/draft_A_v_fire_2026-10-02/analyze.py (that file imports decks/screen/floor.py)."""
    n = len(diffs)
    if n < 2:
        return (sum(diffs) / n if n else float('nan'), float('nan'), float('nan'), float('nan'))
    m = sum(diffs) / n
    sd = math.sqrt(sum((d - m) ** 2 for d in diffs) / (n - 1))
    h = Z * sd / math.sqrt(n)
    return (m, m - h, m + h, sd)


def pair_stats(va, vb, m, seat):
    """Paired difference (version minus base) of one measure on the same deals, in one seat."""
    a, b = va[m], vb[m]
    n = len(a)
    ya, yb = _ints(a)[0], _ints(b)[0]
    mask = {'first': seat_mask(n, 0), 'second': seat_mask(n, 1), 'pooled': int.from_bytes(b'\x01' * n, 'little')}[seat]
    ya &= mask
    yb &= mask
    nn = mask.bit_count()
    one = mask
    up = (ya & (yb ^ one)).bit_count()
    dn = (yb & (ya ^ one)).bit_count()
    mean = (up - dn) / nn
    var = (up * (1 - mean) ** 2 + dn * (-1 - mean) ** 2 + (nn - up - dn) * mean * mean) / (nn - 1)
    h = Z * math.sqrt(var / nn)
    return mean, mean - h, mean + h


def mean_pair_stats(va, vb, m, seat):
    a, b = va[m], vb[m]
    sl = {'first': slice(0, None, 2), 'second': slice(1, None, 2), 'pooled': slice(None)}[seat]
    d = [x - y for x, y in zip(a[sl], b[sl])]
    mean, lo, hi, _ = paired(d)
    return mean, lo, hi


def game_masks(clock, n):
    """Per recorded game: an int with byte i = 1 where deal i drew that game (the draw is keyed by the deal alone)."""
    pick = [bytearray(n) for _ in clock.games]
    for i in range(n):
        pick[clock.timeline(i, i % 2 == 0).game][i] = 1
    return [int.from_bytes(bytes(p), 'little') for p in pick]


def boot_counts(G, resamples=1000, seed=24_700_000_000):
    """Fixed bootstrap resamples over G recorded games: a list of per-game draw counts per resample."""
    s = Stream(seed + G, 'bootstrap')
    out = []
    for _ in range(resamples):
        c = [0] * G
        for _ in range(G):
            c[s.below(G)] += 1
        out.append(c)
    return out


def bootstrap(counts, xs, ns, lo_q=0.025, hi_q=0.975):
    """Percentile range of sum(c*x)/sum(c*n) over the resamples; the per-game tallies are reweighted, nothing
    is re-simulated."""
    ests = []
    for c in counts:
        den = sum(map(mul, c, ns))
        if den:
            ests.append(sum(map(mul, c, xs)) / den)
    ests.sort()
    if not ests:
        return (float('nan'), float('nan'))
    return ests[int(lo_q * (len(ests) - 1))], ests[int(round(hi_q * (len(ests) - 1)))]


def game_tallies(yes_int, gmasks, mask):
    return [(yes_int & g & mask).bit_count() for g in gmasks]


# ------------------------------------------------------------------------------------------------ the versions file
def load_versions(vf, cfg):
    """[(name, path-or-None, diff)] from the versions file; swap_pool adds one-card swaps of non-plan cards."""
    base = vf['base']
    out = []
    v = vf.get('versions', [])
    items = v.items() if isinstance(v, dict) else [(None, x) for x in v]
    for name, x in items:
        if isinstance(x, str):
            out.append((name or os.path.splitext(os.path.basename(x))[0], x, None))
        else:
            out.append((name or ' '.join(x), base, list(x)))
    pool = vf.get('swap_pool') or []
    if pool:
        base_cards = build_cards(base)
        key = set(cfg['key_pokemon'])
        removable = sorted({c.id: c for c in base_cards if c.kind == 'T' or c.name not in key}.values(),
                           key=lambda c: c.id)
        for p in pool:
            m = re.fullmatch(r'(.+?)\s+(\S+ \S+)', p.strip())
            card = _cid(m.group(2))
            for rm in removable:
                if rm.id == card.id:
                    continue
                diff = [f'-1 {rm.name} {rm.id}', f'+1 {card.name} {card.id}']
                try:
                    build_cards(base, diff)
                except SystemExit:
                    continue                                    # an illegal swap (a third copy) is skipped
                out.append((' '.join(diff), base, diff))
    if len(out) > MAX_VERSIONS:
        raise SystemExit(f'{len(out)} versions: the limit is {MAX_VERSIONS} per run')
    return out


def run_versions(vf, n_deals, clock_deals, clocks, workers=1, order=None, base_path=None, seed_base=SEED_BASE,
                 cfg_over=None, keep_vectors=False):
    """Every version in the file (the base first). `order` lists the version names to run, in that order; the results do
    not depend on it."""
    plan = vf.get('plan')
    cfg = sim.load_cfg(plan, **(cfg_over or {}))
    base = base_path or vf['base']
    vs = {n: (p, d) for n, p, d in load_versions(dict(vf, base=base), cfg)}
    names = order or list(vs)
    jobs = [('base', base, None)] + [(n, vs[n][0] or base, vs[n][1]) for n in names]
    kw = dict(seed_base=seed_base, clocks=clocks, clock_deals=clock_deals, cfg_over=cfg_over, plan=plan,
              keep_vectors=keep_vectors)
    if workers > 1:
        with multiprocessing.Pool(workers) as pool:
            rs = pool.starmap(_job, [(j, n_deals, kw) for j in jobs])
    else:
        rs = [_job(j, n_deals, kw) for j in jobs]
    return {'versions': {j[0]: r for j, r in zip(jobs, rs)}, 'base_name': 'base'}


def _job(job, n_deals, kw):
    name, path, diff = job
    r = run_one(path, diff, n_deals, label=name, **kw)
    r['name'] = name
    return r


# ------------------------------------------------------------------------------------------------ SPEC tests 6 and 7
def compare_consistency(path, n):
    """Kingambit in play by own turn 2-5 going first, against lib/consistency.py's solitaire model on the same list.
    Every gap is explained by a named difference in the script, measured by switching that part of the script off
    (same deals); a gap is not a failure."""
    base = build_cards(path)
    ver = sim.Version(base, base, 'consistency')

    def run(**over):
        cfg = sim.load_cfg(**over)
        got = [0] * 6
        for i in range(0, 2 * n, 2):                       # going first only
            tr = sim.play_deal(ver, i, True, cfg, seed_base=SEED_BASE)
            for t in range(2, 6):
                got[t] += 'Kingambit' in tr['turns'][t - 1]['in_play']
        return [x / n for x in got]

    full = run()
    nomesa = run(mesagoza_coin='tails')
    nocopy = run(mesagoza_coin='tails', copycat_rule='never')
    cfg = sim.load_cfg()
    plan = cl.Plan(path, ['Darkness'], base, main=cfg['main_attacker'])
    note = plan.effect_notes.get('Mesagoza', '')
    sol = cl.solitaire(plan, n, 20_000_000_000)
    acc = sol[(True, 'normal')]
    rows = []
    for t in range(2, 6):
        c = acc['stage2'][t] / acc['n']
        gap = full[t] - c
        mesa = full[t] - nomesa[t]
        rest = nomesa[t] - c
        why = (f"{100 * mesa:+.1f} points of the {100 * gap:+.1f} gap is Mesagoza: lib/consistency.py's note on it is "
               f"'{note}', so the solitaire model never uses it, while this script plays it and flips each turn "
               f"(measured by forcing the coin to tails); the remaining {100 * rest:+.1f} is Copycat and Supporter "
               f"policy: the script plays Copycat when the hand holds no Kingambit or Rare Candy and is smaller than the "
               f"opponent's, the solitaire model only when it holds no card the plan needs (with Copycat never played "
               f"the script is {100 * (nocopy[t] - c):+.1f} from it)")
        rows.append({'turn': t, 'tester': full[t], 'consistency': c, 'gap': gap, 'tester_no_mesagoza': nomesa[t],
                     'tester_no_mesagoza_no_copycat': nocopy[t], 'explained': why})
    return rows


def compare_bots(root, n):
    """K3 (first own turn Kingambit attacks, C-bot clock, no filter on k) beside the first Overlord's Blade turn in the
    64 deck-01 games. A gap is printed, not a failure."""
    turns = clk.bot_first_blade_turns(root)
    base = build_cards(DECK01)
    cfg = sim.load_cfg()
    ver = sim.Version(base, base, 'deck01')
    bot = clk.load_bot(root)
    cnt = collections.Counter()
    for i in range(n):
        tr = sim.play_deal(ver, i, i % 2 == 0, cfg, clock=bot, seed_base=SEED_BASE)
        cnt[tr['first_attack_turn']] += 1
    return {'games': len(turns), 'bot_first_blade': dict(collections.Counter(turns)),
            'sim_k3': {k: v / n for k, v in sorted(cnt.items(), key=lambda kv: (kv[0] is None, kv[0] or 0))}}



def comparison_sections(root, n):
    """SPEC tests 6 and 7 as printed sections of a run's RESULTS.md (a gap is printed, not a failure)."""
    L = ['## Against lib/consistency.py on deck 01 (SPEC test 6)', '',
         'Kingambit in play by own turn t, going first, deck 01, no clock. Gaps are explained by named differences in '
         'the script; a gap is not a failure.', '', '| Own turn | this tester | lib/consistency.py solitaire | gap | named difference |',
         '|---|---|---|---|---|']
    for r in compare_consistency(DECK01, n):
        L.append(f'| {r["turn"]} | {100 * r["tester"]:.1f}% | {100 * r["consistency"]:.1f}% | '
                 f'{100 * r["gap"]:+.1f} | {r["explained"]} |')
    L.append('')
    b = compare_bots(root, n)
    L += ['## Against the bots (SPEC test 7)', '',
          f'Deck 01, C-bot clock, {n:,} deals: the share of deals whose first Overlord\'s Blade is on own turn t, beside '
          f'the first Overlord\'s Blade turn in the {b["games"]} recorded games (km3 and kx3 against km3 on the 8 '
          'panel lists, replay_b). A gap is printed, not a failure: the tester plays a fixed script and the bots do not.',
          '', '| First Blade on own turn | this tester | the 64 bot games |', '|---|---|---|']
    turns = sorted({k for k in b['sim_k3']} | set(b['bot_first_blade']), key=lambda k: (k is None, k or 0))
    for t in turns:
        L.append(f'| {"never in the horizon" if t is None else t} | {100 * b["sim_k3"].get(t, 0):.1f}% | '
                 f'{b["bot_first_blade"].get(t, 0)} of {b["games"]} ({100 * b["bot_first_blade"].get(t, 0) / b["games"]:.0f}%) |')
    L.append('')
    return L


SENS = [('lead order: Pawniard first', {'lead_order': ['Pawniard', 'Glimmet', 'Alolan Grimer', 'Regigigas']}),
        ('promote order: Regigigas first', {'promote_order': ['Regigigas', 'Glimmet', 'Alolan Grimer', 'Glimora'.replace('Glimora', 'Glimmora'),
                                                           'Alolan Muk', 'Bisharp', 'Pawniard', 'Kingambit']}),
        ('Copycat whenever no Kingambit or Rare Candy is in hand', {'copycat_rule': 'always'}),
        ('Blade target 3 (the 180 line)', {'blade_target': 3}),
        ('Poke Ball over names, not cards', {'poke_ball_over': 'names'}),
        ('opponent hand 2 (Copycat)', {'opp_hand': 2}),
        ('opponent hand 6 (Copycat)', {'opp_hand': 6})]


def sensitivity(base_path, n_deals, clock_deals, clocks, plan=None, workers=1):
    """The base list under one alternative of each choice Dustin confirms (SPEC "Dustin confirms five choices"), on the
    same deals. Returns RESULTS.md lines."""
    jobs = [('default', {})] + SENS
    kw = dict(clocks=clocks, clock_deals=clock_deals, plan=plan, keep_vectors=True)
    if workers > 1:
        with multiprocessing.Pool(workers) as pool:
            rs = pool.starmap(_sens_job, [(base_path, n_deals, ov, kw) for _, ov in jobs])
    else:
        rs = [_sens_job(base_path, n_deals, ov, kw) for _, ov in jobs]
    cfg = sim.load_cfg(plan)
    d0 = rs[0]
    L = ['## How much each confirmable choice matters (on the base list)', '',
         'One alternative of each value Dustin confirms, run once on the base list on the same deals. Pooled, '
         'paired differences from the default (percentage points; the range is +-1.96 sd/sqrt(n); a "*" marks a range '
         'that excludes 0 and a difference of at least 1 point). Only measures a choice can touch are listed.', '']
    ids = ['K1.t1', 'K1.t3', 'K2.t2', 'K2.t3', 'K2.t4', 'K2.t5', 'K6.t4', 'G5.any3', 'G6.t3', 'G6.t5']
    L.append('| Alternative | ' + ' | '.join(ids) + ' |')
    L.append('|---|' + '---|' * len(ids))
    for (name, _), r in zip(jobs[1:], rs[1:]):
        cells = []
        for m in ids:
            d, lo, hi = pair_stats(r['vectors'], d0['vectors'], m, 'pooled')
            cells.append(f'{100 * d:+.1f}' + ('*' if (lo > 0 or hi < 0) and abs(d) >= 0.01 else ''))
        L.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    L.append('')
    cl_ids = ['K3.by3', 'K3.by5', 'K3.never', 'K4', 'K5']
    for c in clocks:
        if c not in ('his', 'bot', 'fast'):
            continue
        L.append(f'Clock measures under {CLOCK_LABEL[c]}, difference from the default (pooled points, undecided as no):')
        L.append('')
        L.append('| Alternative | ' + ' | '.join(cl_ids) + ' |')
        L.append('|---|' + '---|' * len(cl_ids))
        for (name, _), r in zip(jobs[1:], rs[1:]):
            cells = []
            for m in cl_ids:
                a, b = _ints(r['vectors'][f'{c}|{m}'])[0], _ints(d0['vectors'][f'{c}|{m}'])[0]
                mask = int.from_bytes(b'\x01' * r['clock_deals'], 'little')
                d, lo, hi = paired_diff_bits(a, b, mask)
                cells.append(f'{100 * d:+.1f}' + ('*' if (lo > 0 or hi < 0) and abs(d) >= 0.01 else ''))
            L.append(f'| {name} | ' + ' | '.join(cells) + ' |')
        L.append('')
    return L


def _sens_job(base_path, n_deals, over, kw):
    return run_one(base_path, None, n_deals, cfg_over=over, **kw)


# ------------------------------------------------------------------------------------------------ the report
def pct(x, n):
    lo, hi = wilson(x, n)
    return f'{100 * x / n:.1f}% ({100 * lo:.1f}-{100 * hi:.1f})'


MEASURE_NAMES = {
    'K1': 'Pawniard line in play (end of own turn t)', 'K2': 'Kingambit in play', 'K6': 'Muk and Regigigas both in play',
    'G4.s1': 'a Stage 1 or Stage 2 in play', 'G4.s2': 'a Stage 2 in play', 'G6': 'Kingambit with [DD] attached',
    'G5.any3': 'an empty own turn among turns 1-3'}


def measure_label(m, cfg):
    if m.startswith('G3.'):
        _, nm, t = m.split('.')
        return f'G3 {nm} in play, own turn {t[1:]}'
    head, _, t = m.rpartition('.')
    if head in MEASURE_NAMES and t.startswith('t'):
        return f'{head} {MEASURE_NAMES[head]}, own turn {t[1:]}' if t != 't0' else f'{head} Pawniard in play at setup'
    return f'{m} {MEASURE_NAMES.get(m, "")}'.strip()


def build_report(out_dir, deck_name, runs, args, cfg, record, extra=None):
    """results.json and RESULTS.md. `runs` is run_versions' result (with vectors)."""
    versions = runs['versions']
    base = versions['base']
    bv = base['vectors']
    clocks = base['clocks']
    ids = measure_ids(cfg)
    res_json = {'record': record, 'versions': {}}
    L = []
    L.append(f'# Setup tester: {deck_name}')
    L.append('')
    L.append('Not a ranking and not a ladder forecast: it shows what the cards allow under a written script (SPEC.md), on '
             'the same deals for every version. It does not say who wins.')
    L.append('')
    # exact part for every version
    for name, r in versions.items():
        cards = r['cards']
        ev = exact_block(cards, cfg)
        r['exact'] = ev
    gm = {c: game_masks(make_clock(c, ROOT), base['clock_deals']) for c in clocks}
    bc = {c: boot_counts(len(make_clock(c, ROOT).games)) for c in clocks}
    for name, r in versions.items():
        vv = r['vectors']
        L.append(f'## {name}' + (f' (card-list id {r["list_id"]})' if r.get('list_id') else ''))
        L.append('')
        if name != 'base':
            L.append(f'Changes: {r.get("diff") or r.get("path")}')
            L.append('')
        L.append('Exact, no simulation (SPEC "Exact part"):')
        L.append('')
        L.extend(exact_lines(r['exact']))
        L.append('')
        L.append(f'Simulated, no knock-outs; {r["n_deals"]:,} deals (deal i uses seed {SEED_BASE:,} + i; even i going first). '
                 'Wilson 95% ranges.')
        L.append('')
        L.append('| Measure | going first | going second | pooled |')
        L.append('|---|---|---|---|')
        rj = {}
        for m in ids:
            row = r['measures'][m]
            L.append(f'| {measure_label(m, cfg)} | ' + ' | '.join(pct(row[s]['x'], row[s]['n']) for s in
                                                              ('first', 'second', 'pooled')) + ' |')
            rj[m] = {s: dict(row[s], wilson=[round(v, 5) for v in wilson(row[s]['x'], row[s]['n'])])
                     for s in ('first', 'second', 'pooled')}
        row = r['measures']['G5.n5']
        L.append('| G5 mean empty own turns in turns 1-5 | ' + ' | '.join(
            f'{row[s]["x"] / row[s]["n"]:.3f}' for s in ('first', 'second', 'pooled')) + ' |')
        rj['G5.n5'] = row
        L.append('')
        cj = {}
        for c in clocks:
            L.extend(clock_table(c, r, base if name != 'base' else None, gm[c], bc[c], cfg, cj))
        diffs = []
        pj = {}
        if name != 'base':
            L.append('Paired against the base, same deals (mean per-deal difference, percentage points, +-1.96 sd/sqrt(n); '
                     '"flag" when the range excludes 0 and the difference is at least 1 point):')
            L.append('')
            L.append('| Measure | going first | going second | pooled |')
            L.append('|---|---|---|---|')
            for m in ids:
                cells, flag = [], False
                for s in ('first', 'second', 'pooled'):
                    d, lo, hi = pair_stats(vv, bv, m, s)
                    pj.setdefault(m, {})[s] = [d, lo, hi]
                    f = (lo > 0 or hi < 0) and abs(d) >= 0.01
                    cells.append(f'{100 * d:+.1f} ({100 * lo:+.1f} to {100 * hi:+.1f})' + (' FLAG' if f else ''))
                    flag |= f
                    if s == 'pooled' and f:
                        diffs.append((m, d))
                if flag:
                    L.append(f'| {measure_label(m, cfg)} | ' + ' | '.join(cells) + ' |')
            d, lo, hi = mean_pair_stats(vv, bv, 'G5.n5', 'pooled')
            L.append(f'| G5 mean empty own turns (turns 1-5) | pooled {d:+.3f} ({lo:+.3f} to {hi:+.3f}) | | |')
            L.append('')
            L.append('Only flagged rows are shown above; the full differences are in results.json.')
            L.append('')
            L.extend(summary(name, r, diffs, cfg, runs))
        res_json['versions'][name] = {'label': r['label'], 'list_id': r.get('list_id'), 'diff': r.get('diff'),
                                      'exact': r['exact'], 'setup': rj, 'clock': cj, 'paired_vs_base': pj, 'seconds': r['seconds']}
    L.extend(extra or [])
    L.append('## The run record')
    L.append('')
    for k, v in record.items():
        L.append(f'- **{k}**: {v}')
    L.append('')
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'RESULTS.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')
    with open(os.path.join(out_dir, 'results.json'), 'w', encoding='utf-8') as f:
        json.dump(res_json, f, indent=1, sort_keys=True)
    return res_json


def exact_block(cards, cfg):
    out = {'p0': ex.p0(sum(c.is_basic for c in cards))}
    out['basics_in_hand'] = {k: v for k, v in ex.basics_in_hand(cards).items() if k}
    out['forced_active'] = ex.forced_active(cards)
    keys = [nm for nm in cfg['key_pokemon'] if any(c.name == nm for c in cards)] + sorted(
        {c.name for c in cards if c.kind == 'T' and sim.KIND.get(c.name) in ('candy', 'juliana', 'lisia', 'pokeball')})
    out['in_hand'] = {nm: ex.in_hand(cards, nm) for nm in keys}
    out['seen_by_turn'] = {nm: {t: ex.seen_prob(cards, [nm], ex.cards_seen(t)) for t in range(1, 6)} for nm in keys}
    trio = ['Pawniard', 'Kingambit', 'Rare Candy']
    if all(any(c.name == nm for c in cards) for nm in trio):
        out['trio_seen'] = {n: ex.seen_prob(cards, trio, n) for n in (7, 8)}
    return out


def exact_lines(e):
    L = [f'- P0 (no Basic in the first 5 cards): {e["p0"]:.5f}. Basics in the opening hand: ' +
         ', '.join(f'{k}: {v:.3f}' for k, v in e['basics_in_hand'].items() if k < 3) +
         f', 3 or more: {sum(v for k, v in e["basics_in_hand"].items() if k >= 3):.3f}.',
         '- Chance of being the only Basic (forced Active): ' + ', '.join(
             f'{k} {v:.5f}' for k, v in sorted(e['forced_active'].items())) + '.',
         '- In the opening hand: ' + ', '.join(f'{k} {v:.4f}' for k, v in e['in_hand'].items()) + '.']
    if 'trio_seen' in e:
        L.append(f'- Pawniard, Kingambit and Rare Candy all seen in 7 cards: {e["trio_seen"][7]:.5f}; in 8 cards: '
                 f'{e["trio_seen"][8]:.5f}.')
    L.append('- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): ' + '; '.join(
        f'{nm}: ' + '/'.join(f'{100 * p:.0f}' for p in d.values()) + '%' for nm, d in e['seen_by_turn'].items()) + '.')
    L.append('- Energy by own turn N: N-1 going first, N going second. Kingambit\'s earliest attack: own turn 2 going '
             'second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.')
    return L


def clock_table(c, r, base, gm, counts, cfg, cj):
    """One clock's table for one version, with bootstrap ranges where the clock is recorded."""
    clock = make_clock(c, ROOT)
    n = r['clock_deals']
    vv = r['vectors']
    bv = base['vectors'] if base else None
    games = len(clock.games)
    L = [f'Clock measures under {CLOCK_LABEL[c]} ({n:,} deals, {games} recorded game(s) sampled by the deal alone). '
         'Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is '
         'more than one (SPEC "Width"). Undecided = the record stops before the measure is decided.', '',
         '| Measure | going first | going second | pooled |', '|---|---|---|---|']
    mask = {'first': seat_mask(n, 0), 'second': seat_mask(n, 1), 'pooled': int.from_bytes(b'\x01' * n, 'little')}
    cj[c] = {}
    for m in clock_ids(cfg['horizon']):
        b = vv[f'{c}|{m}']
        yes, und = _ints(b)
        cells = []
        for s in ('first', 'second', 'pooled'):
            nn = mask[s].bit_count()
            x0 = (yes & mask[s]).bit_count()
            x1 = x0 + (und & mask[s]).bit_count()
            rng = ''
            entry = {'x_no': x0, 'x_yes': x1, 'n': nn, 'wilson': list(wilson(x0, nn))}
            if games > 1:
                xs = game_tallies(yes, gm, mask[s])
                ns = [(g & mask[s]).bit_count() for g in gm]
                lo, hi = bootstrap(counts, xs, ns)
                rng = f' [{100 * lo:.0f}-{100 * hi:.0f}]'
                entry['boot'] = [lo, hi]
            else:
                lo, hi = wilson(x0, nn)
                rng = f' [{100 * lo:.0f}-{100 * hi:.0f}, Wilson]'
            same = x0 == x1
            cells.append(f'{100 * x0 / nn:.1f}%' + ('' if same else f' / {100 * x1 / nn:.1f}%') + rng)
            cj[c].setdefault(m, {})[s] = entry
        L.append(f'| {m} | ' + ' | '.join(cells) + ' |')
    L.append('')
    if bv is not None:
        flagged = []
        for m in clock_ids(cfg['horizon']):
            key = f'{c}|{m}'
            a_yes, b_yes = _ints(vv[key])[0], _ints(bv[key])[0]
            for s in ('pooled',):
                xs_a = game_tallies(a_yes, gm, mask[s])
                xs_b = game_tallies(b_yes, gm, mask[s])
                ns = [(g & mask[s]).bit_count() for g in gm]
                d = (sum(xs_a) - sum(xs_b)) / sum(ns)
                if games > 1:
                    lo, hi = bootstrap(counts, [p - q for p, q in zip(xs_a, xs_b)], ns)
                else:
                    pd = paired_diff_bits(a_yes, b_yes, mask[s])
                    lo, hi = pd[1], pd[2]
                    d = pd[0]
                if (lo > 0 or hi < 0) and abs(d) >= 0.01:
                    flagged.append(f'{m}: {100 * d:+.1f} points ({100 * lo:+.1f} to {100 * hi:+.1f})')
                cj[c][m].setdefault('diff', {})[s] = [d, lo, hi]
        L.append(f'Flagged differences from the base under {CLOCK_LABEL[c]} (pooled; bootstrap range over the recorded '
                 'games, undecided counted as no): ' + ('; '.join(flagged) if flagged else 'none') + '.')
        L.append('')
    return L


def paired_diff_bits(a, b, mask):
    one = mask
    nn = mask.bit_count()
    a &= mask
    b &= mask
    up = (a & (b ^ one)).bit_count()
    dn = (b & (a ^ one)).bit_count()
    mean = (up - dn) / nn
    var = (up * (1 - mean) ** 2 + dn * (-1 - mean) ** 2 + (nn - up - dn) * mean * mean) / (nn - 1)
    h = Z * math.sqrt(var / nn)
    return mean, mean - h, mean + h


NOT_PLAYED = {'ilima', 'other'}


def summary(name, r, diffs, cfg, runs):
    """A plain summary: what the version gains, what it gives up (flagged losses only), the clock used, and 'not valued
    here' for every changed card the script never plays."""
    L = [f'**Plain summary, {name}.**', '']
    good = lambda m, d: d < 0 if m.startswith('G5') else d > 0      # an empty turn is the bad thing
    gains = [(m, d) for m, d in diffs if good(m, d)]
    losses = [(m, d) for m, d in diffs if not good(m, d)]
    L.append('Gains (flagged, pooled): ' + ('; '.join(f'{measure_label(m, cfg)} {100 * d:+.1f} points'
                                                      for m, d in gains[:10]) or 'none flagged') + '.')
    L.append('Gives up (flagged, pooled): ' + ('; '.join(f'{measure_label(m, cfg)} {100 * d:+.1f} points'
                                                         for m, d in losses[:10]) or 'none flagged') + '.')
    nv = []
    for c in r.get('changed_cards', []):
        k = sim.KIND.get(c.name) if c.kind == 'T' else None
        if c.kind == 'T' and (k is None or k in NOT_PLAYED):
            nv.append(c.name)
        if c.kind == 'P' and c.name not in cfg['key_pokemon'] and not c.is_basic and c.name != 'Bisharp':
            nv.append(c.name)
    L.append('Not valued here (changed cards the script never plays: they count as blanks): ' +
             (', '.join(sorted(set(nv))) or 'none') + '.')
    L.append('Clocks used: ' + ', '.join(CLOCK_LABEL[c] for c in r['clocks']) + ' (Copycat draws 4 under every clock).')
    L.append('')
    return L


# ------------------------------------------------------------------------------------------------ the command line
def sha256_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def code_sha():
    h = hashlib.sha256()
    for f in sorted(os.listdir(HERE)):
        if f.endswith('.py') or f == 'plans':
            p = os.path.join(HERE, f)
            if os.path.isfile(p):
                h.update(f.encode() + open(p, 'rb').read())
    h.update(open(sim.DEFAULT_PLAN, 'rb').read())
    return h.hexdigest()


def speed_line(runs):
    deals = sum(r['n_deals'] + r['clock_deals'] * len(r['clocks']) for r in runs['versions'].values())
    secs = sum(r['seconds'] for r in runs['versions'].values())
    return f'{deals / secs:,.0f} deals per second per process ({deals:,} deals in {secs:.0f} s of version time)'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--versions')
    ap.add_argument('--first-run', action='store_true')
    ap.add_argument('--deals', type=int, default=100_000)
    ap.add_argument('--clock-deals', type=int, default=20_000)
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--clocks', default=','.join(CLOCK_NAMES))
    ap.add_argument('--out')
    ap.add_argument('--name', default='kingambit')
    ap.add_argument('--plan')
    ap.add_argument('--set', action='append', default=[], help='plan override KEY=VALUE (JSON value)')
    a = ap.parse_args(argv)
    over = {}
    for kv in a.set:
        k, _, v = kv.partition('=')
        over[k] = json.loads(v)
    if a.first_run:
        vf = {'base': HIS_LIST, 'versions': {'deck01': DECK01}, 'plan': a.plan}
    else:
        vf = json.load(open(a.versions, encoding='utf-8'))
        if a.plan:
            vf['plan'] = a.plan
    t0 = time.time()
    clocks = [c for c in a.clocks.split(',') if c]
    cfg = sim.load_cfg(vf.get('plan'), **over)
    runs = run_versions(vf, a.deals, a.clock_deals, clocks, a.workers, cfg_over=over, keep_vectors=True)
    base_cards = build_cards(vf['base'])
    vs = {n: (p, d) for n, p, d in load_versions(vf, cfg)}
    for name, r in runs['versions'].items():
        if name == 'base':
            r['cards'], r['diff'], r['changed_cards'] = base_cards, None, []
            r['path'] = vf['base']
        else:
            p, d = vs[name]
            r['cards'] = build_cards(p or vf['base'], d)
            r['diff'], r['path'] = d, p
            old = collections.Counter(c.id for c in build_cards(vf['base']))
            new = collections.Counter(c.id for c in r['cards'])
            r['changed_cards'] = [cl.resolve(i) for i in set(old) ^ set(new) | {i for i in old if old[i] != new[i]}]
    out = a.out or os.path.join(HERE, 'runs', time.strftime('%Y-%m-%d') + '_' + a.name)
    base_id = runs['versions']['base'].get('list_id')
    record = {'code sha256': code_sha(), 'engine commit': 'pinned rules-switch-2 engine, main 70319c3d (engine '
                                                           'unchanged since c045ede); no engine program is run',
              'seeds': f'{SEED_BASE:,} + deal index i (deal i is the same in every version and under every clock); '
                       f'{a.deals:,} deals with no knock-outs, {a.clock_deals:,} deals per clock',
              'clock sources': f'C-his: {clk.HIS_POS} (12 Kingambit games); C-bot: {clk.BOT_GAMES} (64 deck-01 rows); '
                               'C-fixed: fast, medium, slow (SPEC)',
              'base list': f'{vf["base"]} (card-list id {base_id})', 'plan config': vf.get('plan') or sim.DEFAULT_PLAN,
              'plan overrides': over or 'none', 'wall time': f'{time.time() - t0:.0f} s, {a.workers} process(es)',
              'speed': speed_line(runs)}
    extra = []
    if a.first_run:
        extra += comparison_sections(ROOT, a.clock_deals)
        extra += sensitivity(vf['base'], a.deals, a.clock_deals, clocks, vf.get('plan'), a.workers)
        record['wall time'] = f'{time.time() - t0:.0f} s, {a.workers} process(es) (comparisons and the choice runs included)'
    build_report(out, a.name, runs, a, cfg, record, extra)
    print(f'wrote {out}/RESULTS.md and results.json in {time.time() - t0:.0f} s')
    return 0


if __name__ == '__main__':
    sys.exit(main())

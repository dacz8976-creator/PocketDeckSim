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
import subprocess
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
CLOCK_NAMES = ['his', 'his_seat', 'bot', 'fast', 'medium', 'slow', 'ref190', 'ref220']
RULINGS = {'R1': 'glimmora_turn=attacked_once', 'R2': 'never_evolve_active_grimer; P3_by_cause',
           'R3': 'slow=180hp_k3_turns_3_5_7; 220hp_reference_horizon_10', 'by': 'coordinator, Oct 15'}
CLOCK_LABEL = {'his': 'C-his', 'his_seat': 'C-his, seat-matched', 'bot': 'C-bot', 'fast': 'C-fixed fast',
               'medium': 'C-fixed medium', 'slow': 'C-fixed slow', 'ref190': 'C-fixed reference (fast pace, 190-HP Mega ex)',
               'ref220': 'C-fixed reference (slow pace, 220-HP Mega ex, 10 own turns)'}
HIS_LIST = 'rl/results/pause_games_new_2026-10-13/decks/KW261012_203719000.txt'
DECK01 = 'decks/dustin/01-muk-glimmora-kingambit-regigigas.txt'
HIS_ID, DECK01_ID = '73dfed58d1d6', '35d98d0dcaf2'


# ------------------------------------------------------------------------------------------------ decks and versions
def default_plan_path():
    return sim.DEFAULT_PLAN


def _make_predictions():
    p = os.path.join(ROOT, 'rl', 'results', 'ladder_validation', 'make_predictions.py')
    spec = importlib.util.spec_from_file_location('make_predictions', p)
    m = importlib.util.module_from_spec(spec)
    sys.modules.setdefault('make_predictions', m)
    spec.loader.exec_module(m)
    return m


def deck_lines(cards, energy='Energy: Darkness'):
    """A list as deck-file lines: the Energy line, then '<count> <name> <id>' with names from lib/card.py."""
    c = collections.Counter((k.name, k.id) for k in cards)
    return [energy] + [f'{n} {nm} {cid}' for (nm, cid), n in sorted(c.items())]


def list_sha256(lines):
    """make_predictions.card_list_sha256 of the deck-file lines (the journal's card-list hash)."""
    return _make_predictions().card_list_sha256('\n'.join(lines) + '\n')


def base_energy(path):
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    with open(full, encoding='utf-8') as f:
        return next((l.strip() for l in f if l.lower().startswith('energy:')), 'Energy: Darkness')


def card_list_id(cards, energy='Energy: Darkness'):
    return list_sha256(deck_lines(cards, energy))[:12]


def refuse_new_ex(base_cards, cards):
    """A version that adds an ex is refused until the script handles one: the script plays no ex card (Alolan Muk ex A3
    111, for example, is not Alolan Muk) and a fallen Muk ex is worth 2 points (TESTER_FIX_BRIEF C7)."""
    have = {c.id for c in base_cards}
    new = sorted({c.name for c in cards if c.kind == 'P' and c.ex and c.id not in have})
    if new:
        raise SystemExit('version adds an ex the script does not handle yet: ' + ', '.join(new))


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
    ids = ['P1', 'K1.t0'] + [f'K1.t{t}' for t in range(1, 6)] + [f'K2.t{t}' for t in range(2, 7)] \
        + [f'K6.t{t}' for t in range(3, 6)]
    ids += [f'G3.{nm}.t{t}' for nm in cfg['key_pokemon'] for t in range(1, 6)]
    ids += [f'G4.s1.t{t}' for t in range(2, 6)] + [f'G4.s2.t{t}' for t in range(2, 6)]
    ids += ['G5.any3'] + [f'G6.t{t}' for t in range(2, 6)]
    return ids


def setup_values(tr, cfg, cost):
    """One deal's setup measures, in measure_ids order, plus G5's count (a value measure)."""
    turns, key = tr['turns'], cfg['key_pokemon']
    main, pawn = cfg['main_attacker'], cfg['pawniard']
    v = [1 if tr['setup']['in_play'][0] == cfg['p1_lead'] else 0, 1 if pawn in tr['setup']['roots'] else 0]
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


P_IDS = ['P2.any', 'P2.both', 'P2.g1', 'P2.g2', 'P3.pawn_lead', 'P3.pawn_promo', 'P3.grimer_muk', 'P4.ko', 'P4.win', 'P4.late1',
         'P4.late2p', 'P4.never', 'P4.nomoment', 'P5.ko', 'P5.win']


GIVEN_MOMENT = ['P4.ko', 'P4.win', 'P4.late1', 'P4.late2p', 'P4.never']     # the lines a deal can have once the moment came


def K_IDS(horizon):
    return [m for m in clock_ids(horizon) if m not in P_IDS]


def clock_horizon(clock, cfg):
    return getattr(clock, 'horizon', None) or cfg['horizon']


def clock_ids(horizon):
    return P_IDS + [f'K3.by{x}' for x in range(2, horizon + 1)] + ['K3.never', 'K3.k0', 'K3.k1', 'K3.k2', 'K3.k3p',
                                                          'K4', 'K5']


def clock_values(tr, cfg):
    """One deal's clock measures: 1 yes, 0 no, 2 undecided (the record could not say). SPEC "Opponent clock"."""
    H, T, und, first = tr['horizon'], tr['first_attack_turn'], tr['und_own'], tr['first']
    thr = 140 if cfg['blade_target'] <= 2 else 180
    out = []

    def event(Tev, X, later=True):
        # `later` False: the line cannot happen after the record stops, so it is decided "no" rather than undecided
        if Tev is not None and Tev <= X and (und is None or Tev < und):
            return 1
        return 0 if (und is None or X < und or not later) else 2

    # the P-lines (SPEC_AMENDMENT_1)
    gt = sorted(x for x in tr['glimmora_turns'] if x is not None)
    lines = tr['glimmora_lines'] + [None, None]
    p3, cl_ = tr['p3'], tr['can_later'] or {}
    out += [event(gt[0] if gt else None, H, cl_.get('P2.any', True)),
            event(gt[1] if len(gt) > 1 else None, H, cl_.get('P2.both', True)),
            event(lines[0], H, cl_.get('P2.g1', True)), event(lines[1], H, cl_.get('P2.g2', True)),
            event(p3.get('pawn_lead'), H, cl_.get('P3.pawn_lead', True)),
            event(p3.get('pawn_promo'), H, cl_.get('P3.pawn_promo', True)),
            event(p3.get('grimer_muk'), H, cl_.get('P3.grimer_muk', True))]
    p4 = tr['p4']
    keys = ['P4.ko', 'P4.win', 'P4.late1', 'P4.late2p', 'P4.never', 'P4.nomoment', 'P5.ko', 'P5.win']
    v = dict.fromkeys(keys, 0)
    if p4 is not None:
        W, R, win = p4['W'], p4['R'], p4['pts'] >= 3
        closed = und is None or H < und              # the record covers the whole deal
        if W is None or (und is not None and W >= und):
            if W is None and closed:
                v['P4.nomoment'] = 1
            elif not closed or W is not None:
                v = dict.fromkeys(keys, 2)
        else:
            v['P4.ko'] = 1 if R == W else 0
            v['P4.win'] = 1 if R == W and win else 0
            if R is not None and (und is None or R < und):
                v['P4.late1'], v['P4.late2p'] = int(R == W + 1), int(R >= W + 2)
                v['P5.ko'], v['P5.win'] = 1, int(win)
            elif closed:
                v['P4.never'] = 1
            else:
                v.update({k: 2 for k in ('P4.late1', 'P4.late2p', 'P4.never', 'P5.ko', 'P5.win')})
    out += [v[k] for k in keys]

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
    refuse_new_ex(base_cards, cards)
    ver = sim.Version(cards, base_cards, label or ' '.join(diff or []) or 'base')
    cost = cfg['attacker_cost']
    ids = measure_ids(cfg)
    vec = {m: bytearray(n_deals) for m in ids}
    g5 = bytearray(n_deals)
    cc = [0, 0]                                   # Copycat decisions, and where valuation and fallback rule disagree
    for i in range(n_deals):
        tr = sim.play_deal(ver, i, i % 2 == 0, cfg, seed_base=seed_base)
        cc[0] += tr['copycat']['decisions']
        cc[1] += tr['copycat']['disagree']
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
        cids = clock_ids(clock_horizon(c, cfg))
        cvec = {m: bytearray(clock_deals) for m in cids}
        for i in range(clock_deals):
            tr = sim.play_deal(ver, i, i % 2 == 0, cfg, clock=c, seed_base=seed_base)
            cc[0] += tr['copycat']['decisions']
            cc[1] += tr['copycat']['disagree']
            for m, x in zip(cids, clock_values(tr, cfg)):
                if x:
                    cvec[m][i] = x
        for m in cids:
            vectors[f'{cname}|{m}'] = bytes(cvec[m])
    res = {'label': ver.label, 'list_id': card_list_id(cards, base_energy(base_path)), 'n_deals': n_deals,
           'copycat_decisions': cc[0], 'copycat_disagree': cc[1], 'clock_deals': clock_deals,
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
                 cfg_over=None, keep_vectors=False, fallback=False):
    """Every version in the file (the base first). `order` lists the version names to run, in that order; the results do
    not depend on it. With `fallback`, each version also runs under Copycat's fallback rule (r['fallback'])."""
    plan = vf.get('plan')
    cfg = sim.load_cfg(plan, **(cfg_over or {}))
    base = base_path or vf['base']
    vs = {n: (p, d) for n, p, d in load_versions(dict(vf, base=base), cfg)}
    names = order or list(vs)
    jobs = [('base', base, None)] + [(n, vs[n][0] or base, vs[n][1]) for n in names]
    base_cards = build_cards(base)
    for j in jobs[1:]:
        refuse_new_ex(base_cards, build_cards(j[1], j[2]))          # before any work is dispatched
    kw = dict(seed_base=seed_base, clocks=clocks, clock_deals=clock_deals, cfg_over=cfg_over, plan=plan,
              keep_vectors=keep_vectors, fallback=fallback)
    if workers > 1:
        with multiprocessing.Pool(workers) as pool:
            rs = pool.starmap(_job, [(j, n_deals, kw) for j in jobs])
    else:
        rs = [_job(j, n_deals, kw) for j in jobs]
    return {'versions': {j[0]: r for j, r in zip(jobs, rs)}, 'base_name': 'base'}


def _job(job, n_deals, kw):
    name, path, diff = job
    kw = dict(kw)
    fallback = kw.pop('fallback', False)
    r = run_one(path, diff, n_deals, label=name, **kw)
    if fallback:                                    # the same deals under Dustin's own gap rule, approximated
        r['fallback'] = run_one(path, diff, n_deals, label=name,
                                **dict(kw, cfg_over=dict(kw.get('cfg_over') or {}, copycat_rule='fallback')))
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
    nocopy = run(mesagoza_coin='tails', copycat_n=0)
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
               f"policy: the script plays Copycat by the N/M rule (fewer than N still-needed plan cards in hand and the "
               f"opponent's hand at least M larger than ours), the solitaire model only when it holds no card the plan "
               f"needs (with Copycat never played the script is {100 * (nocopy[t] - c):+.1f} from it); it also holds "
               f"Pawniard only by the T-now trigger here and puts Energy on the Pawniard line first")
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


SENS = [('T-now: Pawniard benched as soon as drawn, one Bench slot kept for it (the old default)',
         {'pawniard_bench': 'now'}),
        ('T-late: Pawniard benched one own turn after T-first-KO', {'pawniard_bench': 'late'}),
        ('T-pieces: Pawniard benched when Kingambit and Rare Candy are both in hand', {'pawniard_bench': 'pieces'}),
        ('lead order: Pawniard first (P1 is still "Regigigas leads")',
         {'lead_order': ['Pawniard', 'Regigigas', 'Glimmet', 'Alolan Grimer']}),
        ('Poke Ball over names, not cards', {'poke_ball_over': 'names'}),
        ('Copycat: the fallback rule (his 2 v 8), approximated', {'copycat_rule': 'fallback'}),
        ('Copycat never played', {'copycat_rule': 'never'}),
        ('Energy order: the Pawniard line before an Active Glimmora', {'glimmora_energy_first': False}),
        ('promotion order: Regigigas first',
         {'promote_order': ['Regigigas', 'Glimmora', 'Glimmet', 'Bisharp', 'Kingambit', 'Alolan Grimer', 'Alolan Muk',
                            'Pawniard']}),
        ("opponent's hand 2 (Copycat's draw under every clock but C-his)", {'opp_hand': 2}),
        ("opponent's hand 6 (Copycat's draw under every clock but C-his)", {'opp_hand': 6})]

CHOICE_IDS = ['P2.any', 'P2.both', 'P3.pawn_lead', 'P3.pawn_promo', 'P3.grimer_muk', 'P4.ko', 'P4.win', 'P5.ko', 'P5.win',
              'K3.never']


def sensitivity(base_path, n_deals, clock_deals, clocks, plan=None, workers=1):
    """The base list under the alternatives of the choices still open (bench trigger, lead order, Poke Ball, Copycat's
    fallback rule and never, the Energy order, the promotion order, the opponent's hand), on the same deals. Run in every
    --versions run. Returns RESULTS.md lines."""
    jobs = [('default', {})] + SENS
    kw = dict(clocks=clocks, clock_deals=clock_deals, plan=plan, keep_vectors=True)
    if workers > 1:
        with multiprocessing.Pool(workers) as pool:
            rs = pool.starmap(_sens_job, [(base_path, n_deals, ov, kw) for _, ov in jobs])
    else:
        rs = [_sens_job(base_path, n_deals, ov, kw) for _, ov in jobs]
    d0 = rs[0]
    L = ['## How much each open choice matters (on the base list)', '',
         'Each alternative is run once on the base list on the same deals, against the default config (T-first-KO, '
         'Copycat by his valuation, approximated, the Pawniard line after an Active Glimmora\'s Energy, the promotion '
         'order of the plan file). Pooled differences in percentage points, with "*" for a range that excludes 0 and a '
         'difference of at least 1 point. Ranges: the per-game bootstrap over the recorded games under C-his and C-bot '
         '(a bootstrap over the recorded games, 1,000 resamples), the paired test on the same deals under C-fixed and for '
         'the setup measures. These runs are on the base only; nothing here is a version.', '']
    ids = ['P1', 'K1.t1', 'K1.t3', 'K2.t3', 'K2.t5', 'G5.any3', 'G6.t3']
    L += ['Setup measures with no knock-outs (Pawniard is benched at once under T-first-KO and T-late there, so the '
          'bench-trigger rows differ only on T-now and T-pieces):', '']
    L.append('| Alternative | ' + ' | '.join(ids) + ' |')
    L.append('|---|' + '---|' * len(ids))
    for (name, _), r in zip(jobs[1:], rs[1:]):
        cells = []
        for m in ids:
            d, lo, hi = pair_stats(r['vectors'], d0['vectors'], m, 'pooled')
            cells.append(f'{100 * d:+.1f}' + ('*' if (lo > 0 or hi < 0) and abs(d) >= 0.01 else ''))
        L.append(f'| {name} | ' + ' | '.join(cells) + ' |')
    L.append('')
    for c in clocks:
        clock = make_clock(c, ROOT)
        n = d0['clock_deals']
        mask = int.from_bytes(b'\x01' * n, 'little')
        gm = game_masks(clock, n) if len(clock.games) > 1 else None
        counts = boot_counts(len(clock.games)) if gm else None
        L.append(f'Plan lines under {CLOCK_LABEL[c]}, difference from the default (pooled points, undecided as no):')
        L.append('')
        L.append('| Alternative | ' + ' | '.join(CHOICE_IDS) + ' |')
        L.append('|---|' + '---|' * len(CHOICE_IDS))
        for (name, _), r in zip(jobs[1:], rs[1:]):
            cells = []
            for m in CHOICE_IDS:
                a, b = _ints(r['vectors'][f'{c}|{m}'])[0], _ints(d0['vectors'][f'{c}|{m}'])[0]
                d, lo, hi = clock_diff(len(clock.games), a, b, mask, gm, counts)
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


CLOCK_MEASURE_NAMES = {
    'P2.any': 'P2 at least one Glimmora had its turn', 'P2.both': 'P2 both Glimmora had their turn',
    'P2.g1': 'P2 the first Glimmora placed had its turn', 'P2.g2': 'P2 the second Glimmora placed had its turn',
    'P3': 'P3 plan broken in front: Muk or Pawniard Active at any point',
    'P3.opening': 'P3, cause: the opening (still the starting Active)',
    'P3.promo': 'P3, cause: promoted, nothing else left',
    'P4.ko': 'P4 ready at the winning moment: Knocks out their strongest',
    'P4.win': 'P4 ready at the winning moment: Wins outright (a lower bound)',
    'P4.late1': 'P4 not ready, ready 1 turn late', 'P4.late2p': 'P4 not ready, ready 2 or more turns late',
    'P4.never': 'P4 the moment came and Kingambit was never ready in the deal',
    'P4.nomoment': 'P4 the winning moment never came in the deal (the Blade never reaches their strongest)',
    'P5.ko': 'P5 plan reached in time: Knocks out their strongest',
    'P5.win': 'P5 plan reached in time: Wins outright (a lower bound)'}


def measure_label(m, cfg):
    if m in CLOCK_MEASURE_NAMES:
        return CLOCK_MEASURE_NAMES[m]
    if m == 'P1':
        return 'P1 Regigigas leads (the Active at the start of the game; exact above)'
    if m.startswith('G3.'):
        _, nm, t = m.split('.')
        return f'G3 {nm} in play, own turn {t[1:]}'
    head, _, t = m.rpartition('.')
    if head in MEASURE_NAMES and t.startswith('t'):
        return f'{head} {MEASURE_NAMES[head]}, own turn {t[1:]}' if t != 't0' else f'{head} Pawniard in play at setup'
    return f'{m} {MEASURE_NAMES.get(m, "")}'.strip()


def copycat_text(cfg):
    return ("**Copycat is played by his valuation, approximated** (Dustin, Oct 15: \"an updated approximate valuation of card "
            "values, based on what I have in play, what cards are left in the deck, how many cards I have, they have, and "
            "whether a shuffle and new hand is likely to be more valuable to winning than keeping my current hand\"): it "
            "is played when the expected value of a fresh hand beats the current hand's value under the value table "
            f"below. A fresh hand is the opponent's hand count of cards from deck plus hand reshuffled, estimated from "
            f"{cfg['copycat_samples']} sampled hands per decision drawn from the tester's own seed block. The value table "
            "is written from the plan's own needs, with no tuned constants; Dustin can correct a value.")


def copycat_table_lines(cfg):
    fb = cfg['copycat_fallback']
    L = ['## Copycat value table (his rule, approximated)', '',
         'Each card in a hand is worth the value of the first row whose conditions all hold (the last row of a card always '
         f'holds). A card not listed is worth {cfg["copycat_default_value"]}. Conditions are read at the moment of the '
         'decision, for the hand being valued: pawniard_due = a Pawniard-line Pokémon is in play or the bench trigger is '
         'open; kingambit_held / kingambit_needed = Kingambit in that hand / none in play; no_pawniard_line_in_play; '
         'pawniard_in_play; bisharp_line_missing = no Bisharp or Kingambit in play; glimmora_lines_lt2 = fewer than two '
         'Glimmet lines in play; glimmet_waits = a Glimmet in play; muk_needed = no Muk in play; grimer_in_play; '
         'regigigas_missing; kingambit_in_deck; bench_room; no_stadium. Ilima, Lucky Ice Pop and Heavy Helmet act on '
         'damage, which the tester does not model, so they are worth the default.', '',
         '| Card | rows: when (all of these) = value |', '|---|---|']
    for card, rows in cfg['copycat_values'].items():
        L.append(f'| {card} | ' + '; '.join(
            (' and '.join(r['when']) if r['when'] else 'otherwise') + f' = {r["value"]}' for r in rows) + ' |')
    L += ['', f'**The fallback rule (his rule, approximated)**: no must-keep card in hand ({", ".join(fb["must_keep"])}): '
          f'Copycat on a gap of {fb["gap"]} or more between the opponent\'s hand and ours without the Copycat; a must-keep '
          f'card in hand: only on a gap of {fb["gap_must_keep"]} or more (his 2 v 8). It runs on the base and on every '
          'version beside the valuation; the two disagree at the rates below.', '']
    return L


def p_flag_set(vv, bv, clocks, gm, bc, cfg):
    """The flagged P-line differences of one version against the base: {(clock or 'setup', measure, '+' or '-')}."""
    out = set()
    d, lo, hi = pair_stats(vv, bv, 'P1', 'pooled')
    if is_flag(d, lo, hi):
        out.add(('setup', 'P1', '+' if d > 0 else '-'))
    for c in clocks:
        clock = make_clock(c, ROOT)
        n = len(vv[f'{c}|{P_IDS[0]}'])
        mask = int.from_bytes(b'\x01' * n, 'little')
        for m in P_IDS:
            d, lo, hi = clock_diff(len(clock.games), _ints(vv[f'{c}|{m}'])[0], _ints(bv[f'{c}|{m}'])[0], mask, gm[c], bc[c])
            if is_flag(d, lo, hi):
                out.add((c, m, '+' if d > 0 else '-'))
    return out


def rate_text(x, n):
    return f'{x:,} of {n:,} Copycat decisions ({100 * x / n:.1f}%)' if n else 'no Copycat decision'


def build_report(out_dir, deck_name, runs, args, cfg, record, extra=None, run=None, run_info=None):
    """results.json (v2) and RESULTS.md. `runs` is run_versions' result (with vectors)."""
    versions = runs['versions']
    base = versions['base']
    bv = base['vectors']
    clocks = base['clocks']
    ids = measure_ids(cfg)
    res_json = {'schema': 'setup-tester results v2', 'run': run or {}, 'run_info': run_info or {}, 'versions': {}}
    mode = cfg['pawniard_bench']
    gm = {c: game_masks(make_clock(c, ROOT), base['clock_deals']) for c in clocks}
    bc = {c: boot_counts(len(make_clock(c, ROOT).games)) for c in clocks}
    # the Copycat rule check: where the valuation and the fallback rule disagree, and whether a verdict changes
    pf = {name: p_flag_set(r['vectors'], bv, clocks, gm, bc, cfg) for name, r in versions.items() if name != 'base'}
    pf_fb = {name: p_flag_set(r['fallback']['vectors'], base['fallback']['vectors'], clocks, gm, bc, cfg)
             for name, r in versions.items() if name != 'base'}
    changed = {name: sorted(pf[name] ^ pf_fb[name]) for name in pf if pf[name] != pf_fb[name]}
    L = [f'# Setup tester: {deck_name}', '',
         'Not a ranking and not a ladder forecast: it shows what the cards allow under a written script (SPEC.md), on '
         'the same deals for every version. It does not say who wins.',
         '**Plan config follows SPEC_AMENDMENT_1 (Dustin, Oct 15) and the coordinator\'s rulings R1-R3 (Oct 15):** '
         f'Regigigas leads; Pawniard is held until the bench trigger ({mode}; default first_ko = our first turn after one '
         'of ours was knocked out, a spot free); Grimer and Muk are benched, and an Active Alolan Grimer is never '
         'evolved into Muk (R2); a Glimmora has had its turn when it attacked at least once (R1); Energy goes to Kingambit '
         'up to [DD], then an Active Glimmora with no [D], then the Pawniard line up to [DD], then Regigigas while Muk is '
         'in play (R1; the other order runs as a choices row). The lines that lead are P1-P5, P3 by cause (R2); the old G '
         'and K lines stay below "descriptive (speed is not the goal)". The slow pace is knockouts on their turns 3, 5 and '
         '7 against a 180-HP Mega ex; the 220-HP Mega is a reference row with 10 own turns (R3). The no-knock-out runs have '
         'no knock-out to trigger first_ko, so Pawniard is benched at once (trigger "at_once") and no Bench slot is '
         'reserved; the old T-now reserved one.',
         copycat_text(cfg)]
    dec = f'base: {rate_text(base["copycat_disagree"], base["copycat_decisions"])}'
    L.append(f'**His rule, approximated, as a check:** the fallback rule runs on the base and on every version. The two '
             f'disagree at {dec}.')
    if changed:
        L.append('**WARNING, the Copycat rule changes a verdict:** ' + '; '.join(
            f'{n}: ' + ', '.join(f'{c} {m} {s} only under the {"valuation" if (c, m, s) in pf[n] else "fallback rule"}'
                                 for c, m, s in diffs) for n, diffs in changed.items()) +
             '. The laptop shows Dustin one such hand.')
    else:
        L.append('No flagged P-line difference from the base changes between the valuation and the fallback rule.')
    L.append('**PROPOSED, not yet confirmed by Dustin:** the plan lines, the lead and promotion orders, the Copycat value '
             'table, and the assumed strongest Pokémon of C-fixed. Nothing here is to be reported to him as settled until '
             'he confirms or rewrites each.')
    L.append('')
    L.extend(copycat_table_lines(cfg))
    for name, r in versions.items():
        r['exact'] = exact_block(r['cards'], cfg)
    for name, r in versions.items():
        vv = r['vectors']
        L.append(f'## {name}' + (f' (card-list id {r["list_id"]})' if r.get('list_id') else ''))
        L.append('')
        if name != 'base':
            L.append(f'Changes: {r.get("diff") or r.get("path")}')
            L.append('')
        L.append(f'Copycat decisions with a Copycat in hand: {r["copycat_decisions"]:,}; the valuation and the fallback rule '
                 f'disagree at {rate_text(r["copycat_disagree"], r["copycat_decisions"])}.')
        L.append('')
        L.append('Exact, no simulation (SPEC "Exact part"):')
        L.append('')
        L.extend(exact_lines(r['exact']))
        L.append('')
        L.append('### Plan lines: does the deck line up with Dustin\'s plan?')
        L.append('')
        L.append(f'Simulated, no knock-outs; {r["n_deals"]:,} deals (deal i uses seed {SEED_BASE:,} + i; even i going first). '
                 'Wilson 95% ranges.')
        L.append('')
        L.append('| Measure | going first | going second | pooled |')
        L.append('|---|---|---|---|')
        rj = {}

        def setup_rows(sel):
            for m in sel:
                row = r['measures'][m]
                L.append(f'| {measure_label(m, cfg)} | ' + ' | '.join(pct(row[s]['x'], row[s]['n']) for s in SEATS) + ' |')
                rj[m] = {s: dict(row[s], wilson=[round(v, 5) for v in wilson(row[s]['x'], row[s]['n'])]) for s in SEATS}
        setup_rows(['P1'])
        L.append('')
        cj, flags = {}, {}
        for c in clocks:
            L.extend(clock_table(c, r, base if name != 'base' else None, gm[c], bc[c], cfg, cj, P_IDS, flags=flags))
        L.append('#### descriptive (speed is not the goal)')
        L.append('')
        L.append('The old G and K lines, kept for reference. Kingambit\'s speed is not the yardstick for this deck.')
        L.append('')
        L.append('| Measure | going first | going second | pooled |')
        L.append('|---|---|---|---|')
        for m in ids[1:]:
            row = r['measures'][m]
            L.append(f'| {measure_label(m, cfg)} | ' + ' | '.join(pct(row[s]['x'], row[s]['n']) for s in SEATS) + ' |')
            rj[m] = {s: dict(row[s], wilson=[round(v, 5) for v in wilson(row[s]['x'], row[s]['n'])]) for s in SEATS}
        row = r['measures']['G5.n5']
        L.append('| G5 mean empty own turns in turns 1-5 | ' + ' | '.join(
            f'{row[s]["x"] / row[s]["n"]:.3f}' for s in SEATS) + ' |')
        rj['G5.n5'] = row
        L.append('')
        for c in clocks:
            L.extend(clock_table(c, r, base if name != 'base' else None, gm[c], bc[c], cfg, cj,
                                 K_IDS(clock_horizon(make_clock(c, ROOT), cfg)), plan_lines=False, flags=flags))
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
                for s in SEATS:
                    d, lo, hi = pair_stats(vv, bv, m, s)
                    pj.setdefault(m, {})[s] = [d, lo, hi]
                    f = is_flag(d, lo, hi)
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
            L.extend(summary(name, r, flags, diffs, cfg))
        else:
            L.extend(['**Plain summary, base.**', ''] + NOT_MODELLED + [''])
        res_json['versions'][name] = {
            'label': r['label'], 'path': r.get('rel_path'), 'diff': r.get('diff'), 'list': r['list'],
            'card_list_sha256': r['card_list_sha256'], 'list_id': r['list_id'],
            'p1_exact': r['exact']['lead'][cfg['p1_lead']], 'exact': r['exact'], 'setup': rj, 'clock': cj,
            'paired_vs_base': pj,
            'copycat': {'decisions': r['copycat_decisions'], 'disagree': r['copycat_disagree'],
                        'fallback_decisions': r['fallback']['copycat_decisions']},
            'p_flags': sorted(pf.get(name, [])), 'p_flags_fallback': sorted(pf_fb.get(name, []))}
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
    out['lead'] = ex.lead_chance(cards, cfg['lead_order'])
    out['basics_in_hand'] = {k: v for k, v in ex.basics_in_hand(cards).items() if k}
    out['lead_order'] = list(cfg['lead_order'])
    out['forced_active'] = ex.forced_active(cards)
    keys = [nm for nm in cfg['key_pokemon'] if any(c.name == nm for c in cards)] + sorted(
        {c.name for c in cards if c.kind == 'T' and sim.KIND.get(c.name) in ('candy', 'juliana', 'lisia', 'pokeball')})
    out['in_hand'] = {nm: ex.in_hand(cards, nm) for nm in keys}
    out['seen_by_turn'] = {nm: {t: ex.seen_prob(cards, [nm], ex.cards_seen(t)) for t in range(1, 6)} for nm in keys}
    trio = ['Pawniard', 'Kingambit', 'Rare Candy']
    if all(any(c.name == nm for c in cards) for nm in trio):
        out['trio_seen'] = {n: ex.seen_prob(cards, trio, n) for n in (7, 8)}
    return out


def sim_lead(e):
    return list(e.get('lead_order', []))


def exact_lines(e):
    L = [f'- P0 (no Basic in the first 5 cards): {e["p0"]:.5f}. Basics in the opening hand: ' +
         ', '.join(f'{k}: {v:.3f}' for k, v in e['basics_in_hand'].items() if k < 3) +
         f', 3 or more: {sum(v for k, v in e["basics_in_hand"].items() if k >= 3):.3f}.',
         '- Chance of being the only Basic (forced Active): ' + ', '.join(
             f'{k} {v:.5f}' for k, v in sorted(e['forced_active'].items())) + '.',
         '- Chance each Pokémon is the starting Active (lead order ' + ', '.join(sim_lead(e)) + '): ' + ', '.join(
             f'{k} {v:.5f}' for k, v in sorted(e['lead'].items())) + ' (P1 is the Regigigas figure).',
         '- In the opening hand: ' + ', '.join(f'{k} {v:.4f}' for k, v in e['in_hand'].items()) + '.']
    if 'trio_seen' in e:
        L.append(f'- Pawniard, Kingambit and Rare Candy all seen in 7 cards: {e["trio_seen"][7]:.5f}; in 8 cards: '
                 f'{e["trio_seen"][8]:.5f}.')
    L.append('- Seen by own turn 1-5 by natural draws (5 + N cards, both seats): ' + '; '.join(
        f'{nm}: ' + '/'.join(f'{100 * p:.0f}' for p in d.values()) + '%' for nm, d in e['seen_by_turn'].items()) + '.')
    L.append('- Energy by own turn N: N-1 going first, N going second. Kingambit\'s earliest attack: own turn 2 going '
             'second or 3 going first with Rare Candy; own turn 3 through Bisharp in either seat.')
    return L


def clock_diff(games, a_yes, b_yes, mask, gm, counts):
    """(difference, low, high) of one measure, version a minus base b, under one clock: the per-game bootstrap over the
    recorded games when there are two or more (SPEC "Width"), else the paired test on the same deals (C-fixed)."""
    if games > 1:
        xs_a, xs_b = game_tallies(a_yes, gm, mask), game_tallies(b_yes, gm, mask)
        ns = [(g & mask).bit_count() for g in gm]
        lo, hi = bootstrap(counts, [p - q for p, q in zip(xs_a, xs_b)], ns)
        return (sum(xs_a) - sum(xs_b)) / sum(ns), lo, hi
    return paired_diff_bits(a_yes, b_yes, mask)


def is_flag(d, lo, hi):
    return (lo > 0 or hi < 0) and abs(d) >= 0.01


SEATS = ('first', 'second', 'pooled')


def zero_by_construction(clock, cfg):
    """The P4 and P5 lines a fixed pace makes 0 by its own rule, by seat: when the pace never delivers the knock-outs the
    Blade needs against the assumed strongest Pokémon within the horizon (HP 60 + 40 k), every line but "no moment"; when
    that Pokémon is worth fewer than 3 points, the two "wins outright" lines (a 2-point Pokémon cannot win from zero)."""
    if not isinstance(clock, clk.Fixed) or clock.hp is None:
        return {}
    H = clock_horizon(clock, cfg)
    kneed = max(0, -(-(clock.hp - 60) // 40))
    out = {}
    for seat, first in (('first', True), ('second', False)):
        kmax = sum(clock.ko(j) for j in range(1, (H - 1 if first else H) + 1))
        for m in ('P4.ko', 'P4.win', 'P4.late1', 'P4.late2p', 'P4.never', 'P5.ko', 'P5.win'):
            if kmax < kneed or (m.endswith('win') and clock.pts < 3):
                out.setdefault(m, []).append(seat)
    return out


def given_moment_table(c, vv, mask, gm, counts, games, cj):
    """P4 once the moment came (C4): the share of the deals where it came, beside the "of all deals" rows above."""
    yes = {m: _ints(vv[f'{c}|{m}'])[0] for m in GIVEN_MOMENT}
    came = 0
    for m in GIVEN_MOMENT:
        came |= yes[m]
    L = ['P4 given the moment came (of the deals in which the Blade reached their strongest Pokémon; undecided deals left '
         'out):', '', '| P4 line, given the moment came | going first | going second | pooled |', '|---|---|---|---|']
    for m in GIVEN_MOMENT:
        cells = []
        for s in SEATS:
            mm = came & mask[s]
            nn = mm.bit_count()
            if not nn:
                cells.append('the moment never came')
                continue
            x = (yes[m] & mask[s]).bit_count()
            entry = {'x': x, 'n': nn}
            if games > 1:
                ns = [(g & mm).bit_count() for g in gm]
                lo, hi = bootstrap(counts, game_tallies(yes[m], gm, mask[s]), ns)
                entry['boot'] = [lo, hi]
                rng = f' [{100 * lo:.0f}-{100 * hi:.0f}]'
            else:
                lo, hi = wilson(x, nn)
                entry['wilson'] = [lo, hi]
                rng = f' [{100 * lo:.0f}-{100 * hi:.0f}, Wilson]'
            cells.append(f'{100 * x / nn:.1f}% of {nn}{rng}')
            cj[c].setdefault('given_moment', {}).setdefault(m, {})[s] = entry
        L.append(f'| {measure_label(m, None)} | ' + ' | '.join(cells) + ' |')
    L.append('')
    return L


def clock_table(c, r, base, gm, counts, cfg, cj, ids, plan_lines=True, flags=None):
    """One clock's table for one version, with bootstrap ranges where the clock is recorded. `flags` collects the
    flagged differences from the base: flags[c]['p' or 'k'] = [(measure, difference, low, high)]."""
    clock = make_clock(c, ROOT)
    n = r['clock_deals']
    vv = r['vectors']
    bv = base['vectors'] if base else None
    games = len(clock.games)
    L = [f'{"Plan lines" if plan_lines else "Clock measures"} under {CLOCK_LABEL[c]} ({n:,} deals, {games} recorded '
         'game(s) sampled by the deal alone). '
         'Cells: undecided counted as no, then as yes, with the bootstrap range over the recorded games when there is '
         'more than one (SPEC "Width"). Undecided = the record stops before the measure is decided and the line can '
         'still happen after it.', '']
    if plan_lines:
        L += [strongest_line(c, clock), '',
              'P4 "Knocks out their strongest" is the HP condition alone; "Wins outright" adds enough points from zero '
              '(their Pokémon\'s points at least 3). Any points we score before the Blade (Glimmora\'s Venomous Hit '
              'knockouts, for example) are not modelled, so "wins outright" is a lower bound. P5 is Kingambit ready at '
              'the moment or later, before the opponent\'s third point.', '']
        zb = zero_by_construction(clock, cfg)
        if isinstance(clock, clk.Fixed):
            L += ['Zero by construction at this pace: ' + ('; '.join(f'{m} ({", ".join(s)})' for m, s in zb.items())
                                                           if zb else 'none') + '.', '']
    L += ['| Measure | going first | going second | pooled |', '|---|---|---|---|']
    mask = {'first': seat_mask(n, 0), 'second': seat_mask(n, 1), 'pooled': int.from_bytes(b'\x01' * n, 'little')}
    cj.setdefault(c, {})
    for m in ids:
        b = vv[f'{c}|{m}']
        yes, und = _ints(b)
        cells = []
        for s in SEATS:
            nn = mask[s].bit_count()
            x0 = (yes & mask[s]).bit_count()
            x1 = x0 + (und & mask[s]).bit_count()
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
            cells.append(f'{100 * x0 / nn:.1f}%' + ('' if x0 == x1 else f' / {100 * x1 / nn:.1f}%') + rng)
            cj[c].setdefault(m, {})[s] = entry
        L.append(f'| {measure_label(m, cfg) if plan_lines else m} | ' + ' | '.join(cells) + ' |')
    L.append('')
    if plan_lines:
        L.extend(given_moment_table(c, vv, mask, gm, counts, games, cj))
    if bv is not None:
        flagged = []
        for m in ids:
            key = f'{c}|{m}'
            a_yes, b_yes = _ints(vv[key])[0], _ints(bv[key])[0]
            d, lo, hi = clock_diff(games, a_yes, b_yes, mask['pooled'], gm, counts)
            if is_flag(d, lo, hi):
                flagged.append((m, d, lo, hi))
            cj[c][m].setdefault('diff', {})['pooled'] = [d, lo, hi]
        if flags is not None:
            flags.setdefault(c, {})['p' if plan_lines else 'k'] = flagged
        L.append(f'Flagged differences from the base under {CLOCK_LABEL[c]} (pooled; '
                 f'{"bootstrap over the recorded games" if games > 1 else "paired test on the same deals"}, undecided '
                 'counted as no): ' + ('; '.join(f'{m}: {100 * d:+.1f} points ({100 * lo:+.1f} to {100 * hi:+.1f})'
                                                 for m, d, lo, hi in flagged) if flagged else 'none') + '.')
        L.append('')
    return L


def strongest_line(c, clock):
    """The opponent's strongest Pokémon the clock carries (SPEC_AMENDMENT_1), for every plan-line table."""
    def one(hp, pts):
        return f'{hp}-HP {"Mega ex" if pts == 3 else "ex" if pts == 2 else "non-ex"}, {pts} point{"s" if pts > 1 else ""}'
    if isinstance(clock, clk.Fixed):
        return (f'Strongest Pokémon assumed for this pace: a {one(clock.hp, clock.pts)} (the Blade needs 60 + 40k >= '
                f'{clock.hp}, k = {-(-(clock.hp - 60) // 40)}).')
    cnt = collections.Counter(g['strongest'] for g in clock.games)
    txt = ', '.join(f'{one(*k)} in {v} game(s)' for k, v in sorted(cnt.items(), reverse=True))
    if c == 'bot':
        return (f'Strongest Pokémon (FLAGGED: the logs do not show the opponent\'s HP, so this is the biggest Pokémon '
                f'in the panel list of that game): {txt}.')
    return f'Strongest Pokémon (per recorded game, the highest-HP Pokémon seen in play on his opponent\'s board): {txt}.'


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
ACTS_ON_DAMAGE = ['Ilima', 'Lucky Ice Pop', 'Heavy Helmet']
NOT_MODELLED = [
    '**Not modelled** (stated in every summary): Ilima\'s pull-back, the Pops\' heals and the Helmet all act on damage, and '
    'the tester\'s clocks count knockouts, not damage, so they are "not valued here" (blanks). That is a real limit for '
    'this plan: Regigigas walling, and Glimmora surviving long enough for its turn, depend on them. Only his games or a bot '
    'that plays the plan can measure those. Also not modelled: our own attacks and any points we score before the Blade, '
    'retreats, and disruption (SPEC "It cannot represent").']


def drop_evolution_falls(diffs, cfg):
    """G3 "in play" falls that come only from evolving (Pawniard to Bisharp, Glimmet to Glimmora, ...) are not losses:
    the Pokémon's card name is no longer the top card. Dropped from the summary (TESTER_FIX_BRIEF C1)."""
    names = cl.db()['name']
    evolves = {names[nm].frm for nm in cfg['key_pokemon'] if nm in names and names[nm].frm}
    return [(m, d) for m, d in diffs if not (m.startswith('G3.') and d < 0 and m.split('.')[1] in evolves)]


def summary(name, r, flags, diffs, cfg):
    """A plain summary: it leads with the flagged P-line differences per clock (the per-game bootstrap for C-his and
    C-bot, the paired test for C-fixed); G and K changes go under "descriptive (no knockouts)"; then 'not valued here'
    for every changed card the script never plays and the clocks used."""
    L = [f'**Plain summary, {name}.**', '',
         'Plan-line differences from the base (flagged: the range excludes 0 and the difference is at least 1 point; '
         'undecided counted as no):', '']
    p1 = [(m, d) for m, d in diffs if m == 'P1']
    L.append('- P1 setup (paired test on the same deals): ' + (f'{100 * p1[0][1]:+.1f} points' if p1 else 'none flagged'))
    for c in r['clocks']:
        clock = make_clock(c, ROOT)
        how = 'per-game bootstrap' if len(clock.games) > 1 else 'paired test'
        fl = flags.get(c, {}).get('p', [])
        L.append(f'- {CLOCK_LABEL[c]} ({how}): ' + ('; '.join(
            f'{measure_label(m, cfg)} {100 * d:+.1f} points ({100 * lo:+.1f} to {100 * hi:+.1f})' for m, d, lo, hi in fl)
            if fl else 'none flagged'))
    L += ['', '**descriptive (no knockouts)**: the old G and K lines; Kingambit\'s speed is not the aim for this deck. '
          'G3 falls that come only from evolving are left out.', '']
    rest = drop_evolution_falls([(m, d) for m, d in diffs if m != 'P1'], cfg)
    good = lambda m, d: d < 0 if m.startswith('G5') else d > 0      # an empty turn is the bad thing
    gains = [(m, d) for m, d in rest if good(m, d)]
    losses = [(m, d) for m, d in rest if not good(m, d)]
    L.append('Gains (flagged, pooled): ' + ('; '.join(f'{measure_label(m, cfg)} {100 * d:+.1f} points'
                                                      for m, d in gains[:10]) or 'none flagged') + '.')
    L.append('Gives up (flagged, pooled): ' + ('; '.join(f'{measure_label(m, cfg)} {100 * d:+.1f} points'
                                                         for m, d in losses[:10]) or 'none flagged') + '.')
    kfl = [(c, flags.get(c, {}).get('k', [])) for c in r['clocks']]
    kfl = [f'{CLOCK_LABEL[c]}: ' + '; '.join(f'{m} {100 * d:+.1f}' for m, d, lo, hi in f) for c, f in kfl if f]
    L.append('K3-K5 under the clocks (flagged, pooled): ' + ('; '.join(kfl) or 'none flagged') + '.')
    nv = []
    for c in r.get('changed_cards', []):
        k = sim.KIND.get(c.name) if c.kind == 'T' else None
        if c.kind == 'T' and (k is None or k in NOT_PLAYED):
            nv.append(c.name)
        if c.kind == 'P' and c.name not in cfg['key_pokemon'] and not c.is_basic and c.name != 'Bisharp':
            nv.append(c.name)
    L.append('Not valued here (changed cards the script never plays: they count as blanks): ' +
             (', '.join(sorted(set(nv))) or 'none') + '.')
    L.append('Clocks used: ' + ', '.join(CLOCK_LABEL[c] for c in r['clocks']) + ' (Copycat draws the opponent\'s hand: '
             'the recorded one under C-his, otherwise 4).')
    L.append('')
    L.extend(NOT_MODELLED)
    L.append('')
    return L


# ------------------------------------------------------------------------------------------------ the command line
def sha256_file(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def code_sha(plan=None):
    """The tester's code (every .py file here) and the plan file the run actually used."""
    h = hashlib.sha256()
    for f in sorted(os.listdir(HERE)):
        if f.endswith('.py'):
            with open(os.path.join(HERE, f), 'rb') as fh:
                h.update(f.encode() + fh.read())
    with open(plan or sim.DEFAULT_PLAN, 'rb') as fh:
        h.update(fh.read())
    return h.hexdigest()


def rel(p):
    """A repo-relative path (never /home/...) for anything under the repo; other paths are named by their base name."""
    full = os.path.abspath(p if os.path.isabs(p) else os.path.join(ROOT, p))
    r = os.path.relpath(full, ROOT)
    return os.path.basename(full) if r.startswith('..') else r


def git_state():
    """(HEAD, whether rl/setup_tester/ has no uncommitted edits to tracked files) when the run starts."""
    try:
        head = subprocess.run(['git', '-C', ROOT, 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout
        dirty = subprocess.run(['git', '-C', ROOT, 'status', '--porcelain', '--untracked-files=no', '--',
                                'rl/setup_tester'], capture_output=True, text=True, check=True).stdout
        return head.strip(), dirty.strip() == ''
    except (OSError, subprocess.CalledProcessError):
        return None, False


def clock_info(c, cfg):
    clock = make_clock(c, ROOT)
    fixed = isinstance(clock, clk.Fixed)
    src = None if fixed else (clk.BOT_GAMES if c == 'bot' else clk.HIS_POS)
    if fixed:
        strongest = [{'hp': clock.hp, 'points': clock.pts, 'assumed': True}]
    else:
        cnt = collections.Counter(g['strongest'] for g in clock.games if g.get('strongest'))
        strongest = [{'hp': hp, 'points': pts, 'games': n} for (hp, pts), n in sorted(cnt.items(), reverse=True)]
    flag = None
    if c == 'bot':
        flag = ('FLAGGED: the logs do not show the opponent\'s HP, so this is the biggest Pokémon in the panel list of '
                'that game')
    return {'label': CLOCK_LABEL[c], 'kind': 'fixed' if fixed else 'recorded', 'games': None if fixed else len(clock.games),
            'horizon': clock_horizon(clock, cfg), 'source': src if src else 'set pace (SPEC; R3 for slow)',
            'source_sha256': sha256_file(os.path.join(ROOT, src)) if src else None,
            'range_method': 'Wilson 95%' if fixed else 'bootstrap, 1,000 resamples over the recorded games',
            'strongest': strongest, 'strongest_source': strongest_line(c, clock), 'strongest_flag': flag,
            'zero_by_construction': zero_by_construction(clock, cfg)}


def not_played_names(cards, cfg):
    """Cards in the run's lists that the script never plays (the summary's 'not valued here' rule)."""
    out = set()
    for c in cards:
        k = sim.KIND.get(c.name) if c.kind == 'T' else None
        if c.kind == 'T' and (k is None or k in NOT_PLAYED):
            out.add(c.name)
        if c.kind == 'P' and c.name not in cfg['key_pokemon'] and not c.is_basic and c.name != 'Bisharp':
            out.add(c.name)
    return sorted(out)


def speed_line(runs):
    deals = secs = 0
    for r in runs['versions'].values():
        for x in (r, r['fallback']):
            deals += x['n_deals'] + x['clock_deals'] * len(x['clocks'])
            secs += x['seconds']
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
        with open(a.versions, encoding='utf-8') as f:
            vf = json.load(f)
        if a.plan:
            vf['plan'] = a.plan
    t0 = time.time()
    tester_commit, tree_clean = git_state()
    clocks = [c for c in a.clocks.split(',') if c]
    cfg = sim.load_cfg(vf.get('plan'), **over)
    runs = run_versions(vf, a.deals, a.clock_deals, clocks, a.workers, cfg_over=over, keep_vectors=True, fallback=True)
    base_cards = build_cards(vf['base'])
    energy = base_energy(vf['base'])
    vs = {n: (p, d) for n, p, d in load_versions(vf, cfg)}
    for name, r in runs['versions'].items():
        if name == 'base':
            r['cards'], r['diff'], r['changed_cards'] = base_cards, None, []
            r['path'] = vf['base']
            r['rel_path'] = rel(vf['base'])
        else:
            p, d = vs[name]
            r['cards'] = build_cards(p or vf['base'], d)
            r['diff'], r['path'] = d, p
            r['rel_path'] = rel(p) if p else None
            old = collections.Counter(c.id for c in build_cards(vf['base']))
            new = collections.Counter(c.id for c in r['cards'])
            r['changed_cards'] = [cl.resolve(i) for i in sorted(set(old) ^ set(new) | {i for i in old if old[i] != new[i]})]
        r['list'] = deck_lines(r['cards'], energy)
        r['card_list_sha256'] = list_sha256(r['list'])
        r['list_id'] = r['card_list_sha256'][:12]
    out = a.out or os.path.join(HERE, 'runs', time.strftime('%Y-%m-%d') + '_' + a.name)
    plan_used = vf.get('plan') or sim.DEFAULT_PLAN
    plan_full = plan_used if os.path.isabs(plan_used) else os.path.join(ROOT, plan_used)
    trig = 'at_once' if cfg['pawniard_bench'] in ('first_ko', 'late') else cfg['pawniard_bench']
    all_cards = [c for r in runs['versions'].values() for c in r['cards']]
    run = {'code_sha256': code_sha(plan_full), 'tester_commit': tester_commit, 'tree_clean': tree_clean,
           'plan_path': rel(plan_full), 'plan_sha256': sha256_file(plan_full), 'rules_commit': '70319c3d',
           'engine_note': 'no engine program is run', 'seed_base': SEED_BASE,
           'deal_rule': 'deal i uses seed_base + i; even i going first', 'deals_no_knockout': a.deals,
           'deals_per_clock': a.clock_deals, 'config': cfg, 'setup_bench_trigger': trig,
           'setup_bench_reserved': cfg['pawniard_bench'] == 'now', 'bench_trigger_under_clocks': cfg['pawniard_bench'],
           'copycat': {'rule': cfg['copycat_rule'], 'label': 'his rule, approximated', 'value_table': cfg['copycat_values'],
                       'default_value': cfg['copycat_default_value'], 'fallback': cfg['copycat_fallback'],
                       'samples': cfg['copycat_samples'],
                       'disagreement': {n: {'decisions': r['copycat_decisions'], 'disagree': r['copycat_disagree']}
                                        for n, r in runs['versions'].items()}},
           'copycat_opp_hand': f'recorded hand under C-his and C-his seat-matched, else {cfg["opp_hand"]}',
           'undecided_rule': 'v2: undecided only if it can still happen', 'rulings': RULINGS,
           'not_played_by_script': not_played_names(all_cards, cfg), 'acts_on_damage': ACTS_ON_DAMAGE,
           'overrides': over, 'clocks': {c: clock_info(c, cfg) for c in clocks}}
    record = {'code sha256': run['code_sha256'], 'engine commit': 'pinned rules-switch-2 engine, main 70319c3d (engine '
                                                                  'unchanged since c045ede); no engine program is run',
              'rulings': '; '.join(f'{k}: {v}' for k, v in RULINGS.items()),
              'seeds': f'{SEED_BASE:,} + deal index i (deal i is the same in every version and under every clock); '
                       f'{a.deals:,} deals with no knock-outs, {a.clock_deals:,} deals per clock',
              'clock sources': f'C-his: {clk.HIS_POS} (12 Kingambit games); C-bot: {clk.BOT_GAMES} (64 deck-01 rows); '
                               'C-fixed: fast, medium, slow, and the 190- and 220-HP references (SPEC, R3)',
              'base list': f'{rel(vf["base"])} (card-list id {runs["versions"]["base"]["list_id"]})',
              'plan config': run['plan_path'], 'plan overrides': over or 'none'}
    extra = []
    if a.first_run:
        extra += comparison_sections(ROOT, a.clock_deals)
    extra += sensitivity(vf['base'], a.deals, a.clock_deals, clocks, vf.get('plan'), a.workers)
    wall = f'{time.time() - t0:.0f} s, {a.workers} process(es)'
    record['wall time'] = wall + ' (every version under both Copycat rules, and the choice runs, included)'
    record['speed'] = speed_line(runs)
    run_info = {'wall_time_s': round(time.time() - t0, 1), 'workers': a.workers, 'speed': speed_line(runs),
                'seconds': {n: round(r['seconds'], 1) for n, r in runs['versions'].items()},
                'seconds_fallback_rule': {n: round(r['fallback']['seconds'], 1) for n, r in runs['versions'].items()}}
    build_report(out, a.name, runs, a, cfg, record, extra, run, run_info)
    print(f'wrote {out}/RESULTS.md and results.json in {time.time() - t0:.0f} s; {record["speed"]}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

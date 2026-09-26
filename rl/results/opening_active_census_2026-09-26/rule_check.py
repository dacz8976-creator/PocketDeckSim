"""The rule check behind "0 contradictions in 220 informative games" (README sections 2 and 5; Fable's review of
the koa draft, item M4). Plain Python: no engine, no game, no seed.

Reads
- census.json (this folder): the Altaria list's Basics with the inputs of kp3's setup score (HP, knockout points,
  Retreat, online_at_setup) and the pre-set switch weights;
- ../altaria_network_divergence_2026-09-26/decisions.jsonl (B2c): one record per network decision in 400
  Altaria v Lucario games, with kp3's probe choice at the same position.

The setup rule, short form (README section 2; census.py setup_value without the bench-HP term, which in hands of
three or fewer Basics is the same for every opening and in these lists never reverses the order):
    score = 500 x online_at_setup + HP / knockout points - Retreat,
ties to the id that sorts last as a string (byte order; observation.rs 37-39 and expectiminimax_player.rs 340-350).
The network's order is the same score with switch A (+w_a) and switch B (-w_b) at census.json's weights.

Known Basics in a game's opening hand (nothing is drawn during setup, so every Basic placed or picked at a setup
decision was in the opening hand):
- the network's opening Active and the Basics it benched at setup (net_detail, turn 0);
- kp3's opening pick (kp3_detail at the opening decision);
- kp3's later setup picks (kp3_detail at the network's later turn-0 decisions, each a Basic still in that hand).

kp3 check: a game is informative when a known Basic other than kp3's pick is known; a contradiction is a known
Basic that outranks kp3's pick under the kp3 order. Counted without and with kp3's later setup picks.
Network fit: the network's opening outranks every known Basic under the network's order; counted with three sets
of known Basics (the network's placements; plus kp3's opening pick; plus kp3's later setup picks).

Usage:
    python rule_check.py                 prints the check and writes it to rule_check_output.txt
    python rule_check.py --write-census  also adds validation -> <Altaria study> -> rule_check to census.json,
                                         and refuses unless removing the block gives back the old bytes exactly
"""
import io
import json
import math
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
CENSUS = os.path.join(HERE, 'census.json')
DECISIONS = os.path.join(ROOT, 'rl', 'results', 'altaria_network_divergence_2026-09-26', 'decisions.jsonl')
STUDY = 'altaria (kp3 probe, B2c Sept 26)'
ONLINE_WEIGHT = 500.0  # ValueFunctionParams::baseline().active_pokemon_online_score (census.py ONLINE_WEIGHT)


def order(basics, bonus):
    """Names from best to worst opening under the short rule plus `bonus`; ties to the id sorting last."""
    scored = [(ONLINE_WEIGHT * b['online_at_setup'] + b['hp'] / b['ko_points'] - b['retreat'] + bonus(b), b['id'],
               b['name'], b) for b in basics]
    scored.sort(key=lambda t: (t[0], t[1].encode('utf-8')), reverse=True)
    return [(name, round(s, 2), cid) for s, cid, name, _ in scored]


def load_games():
    games = {}
    with io.open(DECISIONS, encoding='utf-8') as f:
        for line in f:
            r = json.loads(line)
            if r.get('turn') != 0:
                continue
            games.setdefault(r['i'], []).append(r)
    return games


def serialise(obj):
    # census.py writes json.dump(indent=1, ensure_ascii=False) through a text-mode file on Windows: CRLF, no final newline
    return json.dumps(obj, indent=1, ensure_ascii=False).replace('\n', '\r\n').encode('utf-8')


def main():
    raw = open(CENSUS, 'rb').read()
    census = json.loads(raw.decode('utf-8'))
    alt = next(e for e in census['lists'] if e['list'] == 'decks/research/altaria.txt')
    names = {b['name'] for b in alt['basics']}
    w_a, w_b = census['weights']['switch_a'], census['weights']['switch_b']
    kp3_order = order(alt['basics'], lambda b: 0.0)
    net_order = order(alt['basics'], lambda b: (w_a if (b['switch_a'] and b['evolves_in_list_to']) else 0.0)
                      - (w_b if b['switch_b'] else 0.0))
    kp3_rank = {n: i for i, (n, _, _) in enumerate(kp3_order)}
    net_rank = {n: i for i, (n, _, _) in enumerate(net_order)}

    games = load_games()
    rows = []
    for i in sorted(games):
        recs = sorted(games[i], key=lambda r: r['decision'])
        opening = [r for r in recs if r['context'].get('own_active') is None]
        if not opening:
            continue
        o = opening[0]
        assert len(opening) == 1, i
        assert o['net_detail']['kind'] == 'place' and o['net_detail']['slot'] == 'active', i
        assert o['kp3_detail']['kind'] == 'place' and o['kp3_detail']['slot'] == 'active', i
        later = [r for r in recs if r['context'].get('own_active') is not None]
        net_bench = [r['net_detail']['name'] for r in later if r['net_detail'].get('kind') == 'place']
        kp3_later = [r['kp3_detail']['name'] for r in later if r['kp3_detail'].get('kind') == 'place']
        row = {'i': i, 'seed': o['seed'], 'net': o['net_detail']['name'], 'kp3': o['kp3_detail']['name'],
               'net_bench': net_bench, 'kp3_later': kp3_later}
        assert {row['net'], row['kp3'], *net_bench, *kp3_later} <= names, i
        rows.append(row)

    def kp3_check(with_later):
        informative, contra = 0, []
        for r in rows:
            known = {r['net'], *r['net_bench']} | (set(r['kp3_later']) if with_later else set())
            others = known - {r['kp3']}
            if others:
                informative += 1
                if any(kp3_rank[b] < kp3_rank[r['kp3']] for b in others):
                    contra.append(r['i'])
        return informative, contra

    def net_fit(with_kp3_open, with_kp3_later):
        fit, exc = 0, {}
        for r in rows:
            known = {r['net'], *r['net_bench']}
            if with_kp3_open:
                known.add(r['kp3'])
            if with_kp3_later:
                known |= set(r['kp3_later'])
            above = sorted((b for b in known if net_rank[b] < net_rank[r['net']]), key=net_rank.get)
            if above:
                exc.setdefault(f"{r['net']} opened, {above[0]} known", []).append(r['i'])
            else:
                fit += 1
        return fit, exc

    inf_wo, con_wo = kp3_check(False)
    inf_w, con_w = kp3_check(True)
    fits = {
        "the network's placements only": net_fit(False, False),
        "the network's placements and kp3's opening pick": net_fit(True, False),
        "the network's placements and every kp3 setup pick": net_fit(True, True),
    }
    kp3_opens = Counter(r['kp3'] for r in rows)
    net_opens = Counter(r['net'] for r in rows)
    differ = sum(r['net'] != r['kp3'] for r in rows)

    exp = {k.rsplit(' ', 2)[0]: p for k, p in alt['kp3_opens_two_plus_basic_cards'].items()}
    counts = []
    for n, _, _ in kp3_order:
        p = exp.get(n, 0.0)
        sd = math.sqrt(400 * p * (1 - p)) if 0 < p < 1 else float('nan')
        counts.append((n, kp3_opens.get(n, 0), round(400 * p, 1), round((kp3_opens.get(n, 0) - 400 * p) / sd, 2)))

    out = []
    out.append('Rule check: kp3\'s opening Active in B2c\'s Altaria records against the census\'s setup rule')
    out.append(f"census.json: {os.path.relpath(CENSUS, ROOT).replace(os.sep, '/')}; "
               f"records: {os.path.relpath(DECISIONS, ROOT).replace(os.sep, '/')}")
    out.append('')
    out.append('kp3 order (500 x online + HP / KO points - Retreat; ties to the id sorting last as a string):')
    out.append('  ' + ' > '.join(f'{n} {s:g} ({c})' for n, s, c in kp3_order))
    out.append(f'network order (same score with switch A +{w_a:g} and switch B -{w_b:g}):')
    out.append('  ' + ' > '.join(f'{n} {s:g} ({c})' for n, s, c in net_order))
    out.append('')
    out.append(f'opening decisions (games with two or more Place moves offered at the opening): {len(rows)} of 400 games')
    out.append('kp3 opens (seen / predicted over 400 games / binomial z over 400 games): '
               + ', '.join(f'{n} {o} / {e} / {z:+.2f}' for n, o, e, z in counts))
    out.append('network opens: ' + ', '.join(f'{n} {c}' for n, c in net_opens.most_common()))
    out.append(f'openings that differ (network v kp3 probe): {differ}')
    out.append('')
    out.append('kp3 check (a known Basic that outranks kp3\'s pick is a contradiction):')
    out.append(f'  known = the network\'s placements:                        {inf_wo} informative games, '
               f'{len(con_wo)} contradictions {con_wo}')
    out.append(f'  known = the network\'s placements + kp3\'s later setup picks: {inf_w} informative games, '
               f'{len(con_w)} contradictions {con_w}')
    out.append('')
    out.append('network fit (the network\'s opening outranks every known Basic under the network order):')
    for label, (fit, exc) in fits.items():
        n_exc = sum(len(v) for v in exc.values())
        out.append(f'  {label}: {fit} fit, {n_exc} exceptions')
        for k, v in sorted(exc.items()):
            out.append(f'    {k}: {len(v)} (games {", ".join(map(str, v))})')
    text = '\n'.join(out)
    print(text)
    with io.open(os.path.join(HERE, 'rule_check_output.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text + '\n')

    block = {
        'script': 'rule_check.py (output rule_check_output.txt)',
        'rule': '500 x online_at_setup + HP / knockout points - Retreat; ties to the id that sorts last as a string (byte order)',
        'kp3_order': [n for n, _, _ in kp3_order],
        'network_order_A_plus_B': [n for n, _, _ in net_order],
        'opening_decisions': len(rows),
        'kp3_check': {
            'known_network_placements': {'informative_games': inf_wo, 'contradictions': len(con_wo),
                                         'contradiction_games': con_wo},
            'known_network_placements_and_kp3_later_setup_picks': {'informative_games': inf_w,
                                                                   'contradictions': len(con_w),
                                                                   'contradiction_games': con_w},
        },
        'network_fit': {label: {'fit': fit, 'exceptions': {k: v for k, v in sorted(exc.items())}}
                        for label, (fit, exc) in fits.items()},
        'openings_that_differ': differ,
    }

    if '--write-census' in sys.argv:
        assert serialise(census) == raw, 'census.json does not re-serialise to its own bytes; not written'
        study = census['validation'][STUDY]
        study.pop('rule_check', None)
        base = serialise(census)
        study['rule_check'] = block
        new = serialise(census)
        check = json.loads(new.decode('utf-8'))
        del check['validation'][STUDY]['rule_check']
        assert serialise(check) == base, 'removing the block does not give back the old bytes; not written'
        with open(CENSUS, 'wb') as f:
            f.write(new)
        print(f'\ncensus.json: validation -> "{STUDY}" -> rule_check written; with the block removed the file '
              f're-serialises to the bytes it had before ({len(base)} bytes), checked')


if __name__ == '__main__':
    main()

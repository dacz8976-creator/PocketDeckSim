"""Ladder Field: one row per ranked game about the opponent's deck, for the Ladder Field dashboard.

Inputs:
  games.json        make_games.py's list: the Ladder Log's games, each linked to its Codex review
  extract/out_*.jsonl  one record per reviewed game, written by extraction jobs that follow EXTRACT_BRIEF.md
  database.json     the engine's card database (Pokémon types, for the inferred Energy of unreviewed games)
Output:
  ladder_field_rows.json  rows for the dashboard (no opponent player names, no notes)

usage: ladder_field.py <games.json> <extract_dir> <database.json> <out.json>
"""
import json, glob, os, sys, re, datetime, collections

ENERGY = ['Grass', 'Fire', 'Water', 'Lightning', 'Psychic', 'Fighting', 'Darkness', 'Metal']
PLANS = {'basic_aggro': 'Basic attackers', 'evolution_setup': 'Evolution setup', 'status_control': 'Status and control',
         'spread_bench': 'Bench damage', 'stall_wall': 'Healing and walls', 'unclear': 'Unclear'}
SEASONS = [  # (label, start UTC inclusive); a game belongs to the last season that started before it
    ('Before Oct 14', datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)),
    ('B4b season', datetime.datetime(2026, 10, 14, 6, 0, tzinfo=datetime.timezone.utc)),
    ('Dual Fusion', datetime.datetime(2026, 10, 29, 1, 0, tzinfo=datetime.timezone.utc)),
]

def chicago(t):
    # Central time: CDT (UTC-5) until 2026-11-01 07:00Z, CST (UTC-6) after
    off = -5 if t < datetime.datetime(2026, 11, 1, 7, 0, tzinfo=datetime.timezone.utc) else -6
    return t + datetime.timedelta(hours=off)

def key(name):
    return re.sub(r'[^a-z0-9]+', ' ', str(name).replace('’', "'").lower()).strip()

def load_types(dbp):
    db = json.load(open(dbp, encoding='utf-8'))
    types, stages, weak = (collections.defaultdict(collections.Counter) for _ in range(3))
    canon = {}
    for e in db:
        p = e.get('Pokemon')
        if not p:
            continue
        k = key(p['name'])
        types[k][p.get('energy_type')] += 1
        stages[k][p.get('stage')] += 1
        weak[k][p.get('weakness') or 'None'] += 1
        canon.setdefault(k, p['name'])
    top = lambda d: {k: c.most_common(1)[0][0] for k, c in d.items()}
    return top(types), canon, top(stages), top(weak)

def main():
    gp, exd, dbp, out = sys.argv[1:5]
    games = json.load(open(gp, encoding='utf-8'))
    ptype, canon, pstage, pweak = load_types(dbp)
    names_by_len = sorted(canon, key=len, reverse=True)
    ex = {}
    for f in sorted(glob.glob(os.path.join(exd, 'out_*.jsonl'))):
        for line in open(f, encoding='utf-8'):
            line = line.strip()
            if line:
                r = json.loads(line)
                ex[r['game_key']] = r

    def canonical(n):
        return canon.get(key(n), str(n).strip()) if n else None

    def types_of(names):
        ts = []
        for n in names:
            t = ptype.get(key(n))
            if t and t != 'Colorless' and t in ENERGY and t not in ts:
                ts.append(t)
        return ts

    def parse_opp_text(text):
        t = re.sub(r'\([^)]*\)', ' ', str(text or ''))
        t = re.sub(r'(?i)full list unknown|video[- ]visible core|visible core|unknown', ' ', t)
        found = []
        for part in re.split(r'[/,;+]| and ', t):
            k = key(part)
            if not k:
                continue
            hit = next((n for n in names_by_len if n == k), None) or next((n for n in names_by_len if re.search(r'\b' + re.escape(n) + r'\b', k)), None)
            if hit and canon[hit] not in found:
                found.append(canon[hit])
        return found

    rows, missing = [], []
    for g in games:
        t = datetime.datetime.fromisoformat(g['utc']) if g.get('utc') else None
        ct = chicago(t) if t else None
        season = [s for s, start in SEASONS if t and t >= start][-1] if t else 'unknown'
        week = (ct.date() - datetime.timedelta(days=ct.weekday())) if ct else None
        r = ex.get(g['game_key'])
        if g['reviews'] and not r:
            missing.append(g['game_key'])
        if r:
            seen = [canonical(n) for n in r.get('opp_pokemon_seen') or []]
            main_ = canonical(r.get('opp_main_attacker'))
            partner = canonical(r.get('opp_partner'))
            energy = [e for e in (r.get('opp_energy_seen') or []) if e in ENERGY]
            src = 'attached' if energy else 'inferred'
            if not energy:
                energy = types_of([n for n in (main_, partner) if n]) or types_of(seen)
            plan = r.get('plan') if r.get('plan') in PLANS else 'unclear'
            # Basic v evolution is the card's own stage (the reviews' readers split on Basic Mega ex)
            if plan in ('basic_aggro', 'evolution_setup') and main_ and pstage.get(key(main_)) is not None:
                plan = 'basic_aggro' if pstage[key(main_)] == 0 else 'evolution_setup'
            conf, went, end, turns, remark = r.get('confidence'), r.get('went_first'), r.get('end'), r.get('turns'), r.get('remark')
        else:
            seen = parse_opp_text(g.get('opp'))
            exs = [n for n in seen if re.search(r'\bex\b', n)]
            main_ = (exs or seen or [None])[0]
            partner = next((n for n in seen if n != main_), None)
            energy, src = types_of([n for n in (main_, partner) if n]) or types_of(seen), 'inferred'
            plan, conf, went, end, turns, remark = 'unclear', 'low', 'unknown', 'unknown', None, 'No video review; from the Ladder Log entry only.'
        rows.append({
            'n': g['n'],
            'date': ct.strftime('%Y-%m-%d') if ct else None,
            'week': week.isoformat() if week else None,
            'season': season,
            'my_deck': g.get('deck_name') or g.get('deck_id'),
            'my_deck_id': g.get('deck_id'),
            'result': g.get('result'),
            'win': 1 if g.get('result') == 'W' else 0,
            'opp_core': main_ or 'Not seen',
            'opp_partner': partner or '',
            'opp_pair': (main_ + (' / ' + partner if partner else '')) if main_ else 'Not seen',
            # the main attacker's own type and Weakness (Dragon and Colorless kept: Weakness follows the card, not the Energy)
            'opp_type': (ptype.get(key(main_)) or 'Unknown') if main_ else 'Not seen',
            'opp_weak': (pweak.get(key(main_)) or 'Unknown') if main_ else 'Not seen',
            'opp_energy': ', '.join(energy),
            'energy_source': src,
            'plan': PLANS[plan],
            'went_first': went or 'unknown',
            'end': end or 'unknown',
            'turns': turns,
            'confidence': conf or 'low',
            'opp_seen': ', '.join(n for n in seen if n),
            'remark': (remark or '')[:160],
            'reviewed': bool(r),
        })
    json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    c = collections.Counter
    print('rows', len(rows), '| reviewed', sum(r['reviewed'] for r in rows), '| missing extraction', missing)
    print('seasons', c(r['season'] for r in rows))
    print('energy source', c(r['energy_source'] for r in rows), '| empty energy', sum(1 for r in rows if not r['opp_energy']))
    e = c(x for r in rows for x in r['opp_energy'].split(', ') if x)
    print('energy (games showing each):', e.most_common())
    print('plans', c(r['plan'] for r in rows).most_common())
    print('top cores', c(r['opp_core'] for r in rows).most_common(15))
    print('confidence', c(r['confidence'] for r in rows))

if __name__ == '__main__':
    main()

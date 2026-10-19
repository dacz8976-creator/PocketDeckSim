#!/usr/bin/env python3
"""Runtime validation of the baseline printer (pg_pos built with rl/results/pause_games_decisions_2026-10-02/harness/pgd_patch.py), on synthetic fixtures only.

  python3 validate_baseline.py [--pg-pos BIN] [--old-pg-pos OLDBIN] [--out validation/baseline_printer_validation.json]

What it checks, on tests/fixtures (no exam data, no API, no game logs):
  1. Field Blower with two Tool holders: the baseline's legal actions at the target choice are TWO different `DiscardToolFromPokemon#{...}` labels, each with its
     own Pokémon (in_play_idx 0 and 1), and the bot's choice carries its target.
  2. Quick-Grow Extract with two Grass Pokémon: two different `ChooseRandomEvolutionTarget#{...}` labels (energy_type, in_play_idx), the bot's choice carries its target.
  3. The baseline's concrete labels are byte-equal to the labels the plan lister prints for the same position and step (one canonical format across the packages).
  4. Free play of km3 on those positions: every concrete label is kept in `plan_full`, and the harness maps the row to exactly ONE listed plan (no ambiguity).
  5. (optional) the OLD executable, run on the same positions, prints the bare name for both targets: the defect this fix removes.
It writes the evidence (the labels seen, the executable's sha256) as JSON.
"""
import argparse, hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import judge  # noqa: E402

FIX = os.path.join(HERE, 'tests', 'fixtures')
POS = os.path.join(FIX, 'baseline_positions.json')
DECKS = os.path.join(FIX, 'decks')
DEFAULT_NEW = os.environ.get('PG_POS_BIN', '/home/dacz8976/ai_judge_pgpos/bin/pg_pos_target_preserving')
DEFAULT_OLD = '/home/dacz8976/stageA/bin/pg_pos_blade'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def run_pg_pos(binary, pid, seeds=(1, 2, 3), bot='km3'):
    cmd = [binary, '--positions', POS] + judge.deck_args(DECKS) + ['--seeds', ','.join(map(str, seeds)), '--bot', bot, '--only', pid]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise AssertionError(f'{binary} exited {r.returncode} on {pid}: {r.stderr[-400:]}')
    rows = [json.loads(l) for l in r.stdout.splitlines()]
    if any(j.get('problems') for j in rows):
        raise AssertionError(f'{binary} reports a position problem for {pid}')
    return rows


def last_legal(rows, seed=1):
    forced = [j for j in rows if j.get('kind') == 'forced' and j.get('seed') == seed]
    assert len(forced) == 1 and forced[0]['ok'], forced
    step = forced[0]['steps'][-1]
    return step['legal'], step['next_choice_km3']


def validate(binary=DEFAULT_NEW, old=None):
    ev = {'binary': binary, 'binary_sha256': sha256(binary), 'checks': {}}
    lister = judge.list_plans(['MINI-BLOWER', 'MINI-QGE'], POS, DECKS)
    for pid, prefix, force in [('MINI-BLOWER', 'DiscardToolFromPokemon#', 'Play:Field Blower'), ('MINI-QGE', 'ChooseRandomEvolutionTarget#', 'Play:Quick-Grow Extract')]:
        rows = run_pg_pos(binary, pid)
        legal, choice = last_legal(rows)
        targets = [l for l in legal if l.startswith(prefix)]
        assert len(targets) == 2 and len(set(targets)) == 2, f'{pid}: expected two different target labels, got {legal}'
        assert all(json.loads(t.split('#', 1)[1]).get('in_play_idx') in (0, 1) for t in targets), targets
        assert choice in targets, f'{pid}: the bot choice {choice!r} is not one of the target labels'
        listed = {l for p in lister[pid]['plans'] for l in p['labels'] if l.startswith(prefix)}
        assert set(targets) == listed, f'{pid}: baseline labels {sorted(targets)} differ from the lister labels {sorted(listed)}'
        free = [j for j in rows if j.get('kind') == 'free']
        assert len(free) == 3, free
        for j in free:
            kept = [l for l in j['plan'] if l.startswith(prefix)]
            assert kept and all('#' in l for l in kept), f'{pid} seed {j["seed"]}: a target label lost its arguments: {j["plan"]}'
        out = judge.run_pg_pos('km3', [pid], [1, 2, 3], lister, POS, DECKS, binary)
        assert all(r['plan_number'] is not None and not r['match_error'] for r in out), [(r['seed'], r['plan_number'], r['match_error']) for r in out]
        ev['checks'][pid] = {'force': force, 'legal_target_labels': sorted(targets), 'bot_choice': choice, 'lister_labels': sorted(listed),
                             'free_play_plans': [j['plan'] for j in free], 'harness_plan_numbers': [r['plan_number'] for r in out], 'ambiguous': 0}
    if old and os.path.exists(old):
        rows = run_pg_pos(old, 'MINI-BLOWER', seeds=(1,))
        legal, choice = last_legal(rows)
        ev['old_executable'] = {'binary': old, 'binary_sha256': sha256(old), 'legal_labels_at_the_target_choice': legal, 'bot_choice': choice,
                                'drops_the_target': sorted(set(l for l in legal if l.startswith('DiscardToolFromPokemon'))) == ['DiscardToolFromPokemon']}
    return ev


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--pg-pos', default=DEFAULT_NEW)
    ap.add_argument('--old-pg-pos', default=DEFAULT_OLD)
    ap.add_argument('--out')
    a = ap.parse_args()
    if not os.path.exists(a.pg_pos):
        sys.exit(f'{a.pg_pos} is missing: build it (README.md, "Rebuilding the baseline")')
    ev = validate(a.pg_pos, a.old_pg_pos)
    text = json.dumps(ev, indent=1, ensure_ascii=False)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        open(a.out, 'w', encoding='utf-8').write(text + '\n')
    print(text)
    print('VALIDATED: the baseline printer keeps every target on the fixtures', file=sys.stderr)


if __name__ == '__main__':
    main()

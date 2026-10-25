#!/usr/bin/env python3
"""The builders' check for exam v2 positions (PREREG_RUN3 section 2; addendum 5, G1 and G5): one game's build record at a time, the same
checks validate_v2.py makes before the freeze, plus the candidate list. Never builds or asks a bot: pg_legal_v14 --legal-only only.

  check_game.py GAME [GAME ...] [--only POINT_ID] [--show] [--all]
    GAME: a game id (20261016_184635000_SR) or a build file (~/exam_v2/build/g/g<game>.py, which defines POS = [P(...), ...])
    --show: print every step's legal list (to find a label), and the engine's summary of the position
    --all: every build file in ~/exam_v2/build/g/

For each position it checks:
  1. the id is LAD-<game>-t<turn count> and is a candidate (~/exam_v2/select/selection.json), once;
  2. kind is None (v2's answer kind comes from the labels), and the candidate view passes (no answer field, no evaluative word in the
     free-text facts, none of his move's labels or the builder's notes in any candidate-visible text: v2_helpers.candidate_view);
  3. shipped: pg_legal_v14 on the candidate view with his move forced: no position problem, every forced label matched up to the tool's
     stop, and the tool stops at the end of the line, the end of the turn, game over, or a hidden draw or coin;
  4. after a hidden draw or coin: validate_v2's verification variant (the build's draws put in the hand up front, the chance actions
     removed, the coin patch applied): no problem, every remaining label matched.
It prints OK or FIX per position, and exits 1 if any position needs a fix."""
import argparse, copy, glob, importlib.util, json, os, subprocess, sys

E2 = os.path.expanduser('~/exam_v2')
sys.path.insert(0, os.path.join(E2, 'build'))
from v2_helpers import (RANDOM_EVOLUTION_PLAYS, AnswerLeak, Uncertain, candidate_view, chance_steps, cut,  # noqa: E402
                        tool_steps, tool_stop_agrees)
# pg_legal_v14 stops that are not chance actions and that end the tool's check before his line ends (Oct 25 build): the rest of the line is
# not checked by the tool; each is reported as a TOOL NOTE, never as OK silently. ReturnPokemonToHand: a card entering his hand (Parasol Lady).
NON_CHANCE_TOOL_STOPS = ('ReturnPokemonToHand',)
NOTES_SEEN = []
BIN = os.path.expanduser('~/exam/bin/pg_legal_v14')
with open(f'{E2}/bin/decks.args') as f:
    ARGS = f.read().split()
CANDS = {c['point_id'] for c in json.load(open(f'{E2}/select/selection.json', encoding='utf-8'))['candidates']}
CLEAN_STOPS = ('end of line', "the turn is over", 'game over')


def load(path):
    sp = importlib.util.spec_from_file_location('g_' + os.path.basename(path)[:-3], path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return list(getattr(m, 'POS', []))


def run(qs, tmp, show=False):
    with open(tmp, 'w') as f:
        json.dump(qs, f, ensure_ascii=False)
    try:
        r = subprocess.run([BIN, '--positions', tmp, '--legal-only'] + ARGS, capture_output=True, text=True)
    finally:
        os.remove(tmp)
    if 'PGDUMP' in r.stderr:
        sys.exit('a search ran: stop')
    if r.returncode:
        sys.exit('pg_legal_v14 failed (a card name or a field it cannot read? Its message names examples/pg_pos.rs, the source it is '
                 'built from in legal-only mode; no bot runs):\n' + r.stderr[-2500:])
    out = {}
    for line in r.stdout.splitlines():
        j = json.loads(line)
        out.setdefault(j['id'], {})[j['kind']] = j
    return out


def variant(built, line, pos):
    """validate_v2.py's after-chance variant, unchanged in meaning: (variant position, remaining line, notes) or (None, None, why)."""
    try:
        ch = set(chance_steps(line, pos))
    except Uncertain as e:
        return None, None, f'the chance steps cannot be followed ({e})'
    if not ch:
        return None, None, 'no chance step in the line'
    draws, vp = built.get('_draws') or {}, built.get('_vpatch')
    orig = built['force']
    pool = []
    for i in sorted(draws, key=int):
        lab = orig[int(i)]
        pool.append(['UseStadium' if lab == 'Play:Mesagoza' else lab, draws[i], False])
    v = copy.deepcopy(pos)
    hand = list(v['me']['hand'])
    keep, note = [], []
    for k, lab in enumerate(line):
        if k not in ch:
            keep.append(lab)
            continue
        base = lab.split('{')[0]
        hit = next((e for e in pool if not e[2] and (e[0] == lab or e[0] == base or (base.startswith('ChooseRandom') and e[0].startswith(RANDOM_EVOLUTION_PLAYS)))), None)
        if lab.startswith('ChooseRandom'):
            continue
        if hit is None:
            if lab == 'UseStadium':
                note.append('Mesagoza coin assumed tails (no record)')
                continue
            return None, None, f'no draws record for {lab} (force index {k}): give draws={{{k}: [cards drawn or found]}}'
        hit[2] = True
        if lab.startswith('Play:'):
            name = lab.split(':', 1)[1]
            h = next((c for c in hand if c.startswith(name)), None)
            if h:
                hand.remove(h)
        for c in hit[1]:
            if c.startswith('-'):
                if c[1:] in hand:
                    hand.remove(c[1:])
                else:
                    note.append(f'draws removes {c[1:]}, which is not in the hand')
            else:
                hand.append(c)
    v['me']['hand'] = hand
    v['force'] = keep
    v['id'] = pos['id'] + '|v'
    if vp:
        try:
            vp(v)
        except Exception as e:
            return None, None, f'the coin patch (vpatch) failed: {e}'
    return v, keep, '; '.join(note)


def steps_report(o, show):
    steps = o['legal']['steps']
    matched, unmatched = tool_steps(steps, o['legal']['stopped'])
    lines = []
    if show:
        for s in steps:
            lines.append(f"      step {s['step']}: forced {s.get('forced')!r} matched {s.get('matched')!r}; legal {s.get('legal')}")
    if unmatched:
        s = unmatched[0]
        lines.append(f"      UNMATCHED at step {s['step']}: {s['forced']!r}; legal there: {s.get('legal')}")
    return len(matched), unmatched, lines


def check_file(path, args, seen):
    try:
        pos_list = load(path)
    except Exception as e:
        print(f'{os.path.basename(path)}: cannot load: {type(e).__name__}: {e}')
        return 1
    if args.only:
        pos_list = [p for p in pos_list if p.get('id') == args.only]
    bad = 0
    views, built_of = [], {}
    for b in pos_list:
        pid = b.get('id')
        probs = []
        if pid != f"LAD-{b.get('game')}-t{b.get('turn_count')}":
            probs.append(f"id is not LAD-<game>-t<turn_count> ({b.get('game')}, {b.get('turn_count')})")
        if pid not in CANDS and not args.test_any_id:
            probs.append('not a candidate point (select/selection.json)')
        if pid in seen:
            probs.append(f'built twice ({seen[pid]})')
        seen[pid] = os.path.basename(path)
        if b.get('kind') is not None:
            probs.append('kind must be None (the labels give the answer kind)')
        try:
            view = candidate_view(b)
        except (AnswerLeak, Exception) as e:
            probs.append(f'candidate view refused: {e}')
            view = None
        if probs:
            print(f'{pid}: FIX\n' + '\n'.join(f'   - {x}' for x in probs))
            bad += 1
            continue
        q = dict(copy.deepcopy(view), force=list(b['force']))
        views.append(q)
        built_of[pid] = b
    if not views:
        return bad
    tmp = os.path.join(E2, 'build', 'scratch', 'tmp', f'check_{os.getpid()}.json')
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    out = run(views, tmp)
    vq, vmeta = [], {}
    results = {}
    for q in views:
        pid = q['id']
        b = built_of[pid]
        o = out[pid]
        probs, info = [], []
        if o['position']['problems']:
            probs.append(f"position problems: {o['position']['problems']}")
        n, unmatched, lines = steps_report(o, args.show)
        stopped = o['legal']['stopped']
        info.append(f'shipped: {n}/{len(q["force"])} matched, stopped: {stopped}')
        info += lines
        chance_stop = stopped.startswith('hidden')
        tool_note = None
        if unmatched or stopped.startswith('unmatched'):
            probs.append('his move does not apply: a forced label is not legal there (see UNMATCHED)')
        elif not chance_stop and not stopped.startswith(CLEAN_STOPS):
            probs.append(f'the tool stopped at {stopped!r}, not at the end of the line or turn or a hidden draw or coin')
        elif not chance_stop and n < len(q['force']) and not (n == len(q['force']) - 1 and q['force'][-1] == 'EndTurn'):
            if stopped.startswith('the turn is over') and n and not q['force'][n - 1].startswith(('Attack:', 'EndTurn')):
                tool_note = (f'the opponent chooses after label {n} ({q["force"][n - 1]}); the tool stops there, and the rest of the line '
                             f'({len(q["force"]) - n} labels) is not checked by the tool')
            else:
                probs.append(f'only {n} of {len(q["force"])} labels applied before {stopped!r}: the line runs past the end of the turn?')
        elif chance_stop and n == len(q['force']):
            info.append('the tool stops at the last label (a hidden effect of it); nothing of his move comes after')
            chance_stop = False  # nothing to check after it
        elif chance_stop and stopped.split(' at ', 1)[-1].startswith(NON_CHANCE_TOOL_STOPS):
            tool_note = (f'the tool stops at a non-chance step ({stopped.split(" at ", 1)[-1]}); the rest of the line '
                         f'({len(q["force"]) - n} labels) is not checked by the tool')
            chance_stop = False
        if tool_note:
            info.append('TOOL NOTE: ' + tool_note)
            NOTES_SEEN.append((pid, tool_note))
        try:
            seg = cut(q['force'], q)
            agrees = tool_stop_agrees(q['force'], seg, q, n, chance_stop, bool(unmatched))
            info.append(f'first segment (cut): {len(seg)} labels; tool stop agrees: {agrees} (report only)')
        except Uncertain as e:
            info.append(f'cut() cannot follow this line: {e} (report only; the lister gives its segment)')
        if args.show:
            info.append(f"      engine summary: {json.dumps(o['position'].get('summary'), ensure_ascii=False)[:1500]}")
        if chance_stop and not probs:
            v, keep, note = variant(b, q['force'], q)
            if v is None:
                probs.append(f'after-chance variant: {note}')
            else:
                vq.append(v)
                vmeta[v['id']] = (pid, keep, note)
        results[pid] = (probs, info)
    if vq:
        out2 = run(vq, tmp)
        for vid, (pid, keep, note) in vmeta.items():
            o = out2[vid]
            probs, info = results[pid]
            if o['position']['problems']:
                probs.append(f"variant position problems: {o['position']['problems']}")
            n, unmatched, lines = steps_report(o, args.show)
            st = o['legal']['stopped']
            info.append(f'after-chance variant: {n}/{len(keep)} matched, stopped: {st}' + (f'; {note}' if note else ''))
            info += lines
            amb = unmatched and unmatched[0]['forced'].startswith('Place:') and \
                sum(1 for l in unmatched[0].get('legal') or [] if l.startswith(unmatched[0]['forced'] + '(')) >= 2
            if amb:
                note = (f"in the after-chance variant only, {unmatched[0]['forced']} names two cards (a drawn card shares the name), so the "
                        f"tool lists only long forms there; the shipped run matched it; the rest of the variant is not checked by the tool")
                info.append('TOOL NOTE: ' + note)
                NOTES_SEEN.append((pid, note))
            elif unmatched or st.startswith('unmatched'):
                probs.append('after-chance variant: a label does not apply (see UNMATCHED): the draws, the coin patch or the label is wrong')
            elif st.startswith('hidden') and n == len(keep):
                info.append('     the variant stops at its last label (a hidden effect of it); nothing of his move comes after')
            elif st.startswith('hidden'):
                probs.append(f'after-chance variant stops again at {st!r}: a chance step without a draws record?')
    for q in views:
        probs, info = results[q['id']]
        print(f"{q['id']}: {'FIX' if probs else 'OK'}")
        for x in probs:
            print(f'   - {x}')
        for x in info:
            print(f'     {x}')
        bad += bool(probs)
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('games', nargs='*')
    ap.add_argument('--only')
    ap.add_argument('--show', action='store_true')
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--test-any-id', action='store_true', help=argparse.SUPPRESS)  # the tool's own tests only
    a = ap.parse_args()
    files = sorted(glob.glob(f'{E2}/build/g/g*.py')) if a.all else [
        g if g.endswith('.py') else f'{E2}/build/g/g{g}.py' for g in a.games]
    if not files:
        sys.exit('no build file given')
    seen, bad = {}, 0
    for f in files:
        if not os.path.exists(f):
            print(f'{f}: no such build file')
            bad += 1
            continue
        bad += check_file(f, a, seen)
    if a.all:
        missing = sorted(CANDS - set(seen))
        print(f'built: {len(seen)} of {len(CANDS)} candidates; not built: {len(missing)}')
        print(f'tool notes (OK, the rest of the line not checked by the tool): {len(NOTES_SEEN)}')
        for pid, n in NOTES_SEEN:
            print(f'   {pid}: {n}')
    print('ALL OK' if not bad else f'{bad} position(s) or file(s) need a fix')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

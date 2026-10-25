#!/usr/bin/env python3
"""Stage exam v2's labelling job (jobs/LABEL_JOB.md; PREREG_RUN3 addendum 5, G5 and G6) in parts, from the build records.

  stage_label.py RUN3_DIR EXAM_V2_DIR [--parts 5] [--out-prefix label]

- The points: every candidate (select/selection.json) built in ~/exam_v2/build/g/*.py, minus the G1 drops (build/drops/<point id>.txt).
  A candidate with no build record stops the run, as does a build record that is not a candidate.
- The parts: the build batches (build/batches.json) taken in order, two batches per part when --parts is 5; whole games, by time.
- label_in_p<k>/ (read-only), per part:
  - positions.json: build/v2_helpers.label_view of each point (the candidate view plus his_move); checked again here for the builder's
    notes, approximate_reason, kind, _draws and _vpatch;
  - legal.jsonl: pg_legal_v14's legal list at each step of his move (--legal-only, the candidate view with his move forced);
  - selection.json: point id, game, global turn, clip, the review file;
  - sources/<game>/: REVIEW.md, UNCERTAINTIES.json, LADDER_ENTRY.json (where present) and, for a battle in several clips, its clip folders
    and CLIPS.json, copied from the hash-checked usability staging (inv_in_p*/sources), hashes checked again;
  - decks/<deck>.txt for the part's decks; DECK_KINDS_FOR.txt: the decks this part gives deck_kinds for (each deck in exactly one part, the
    one holding most of its points);
  - CARDS.md: the card text of every card in the part's decks and positions (the frozen database, b5e68fc8): the workers have no shell;
  - ADJUDICATION_RULES.md, RULES_FOR_AGENTS.md, FILES.txt.
- jobs/LABEL_JOB_PROMPT_p<k>.txt: LABEL_JOB.md's prompt with this part's folders (absolute), CARDS.md for card text, the deck-kinds file, the
  question cap and the linked-battle line. Empty label_out_p<k>/.
- LABEL_STAGING.json: points per part, every staged file's sha256, the prompts' sha256. Refuses to overwrite."""
import argparse, collections, glob, hashlib, importlib.util, json, os, re, shutil, stat, subprocess, sys

E2_ABS = '/home/dacz8976/exam_v2'
sys.path.insert(0, os.path.join(E2_ABS, 'build'))
import v2_helpers as H  # noqa: E402

BIN = os.path.expanduser('~/exam/bin/pg_legal_v14')
SRC_KEEP = ('REVIEW.md', 'UNCERTAINTIES.json', 'LADDER_ENTRY.json')


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_build(e2, pattern='g*.py'):
    built = {}
    for fn in sorted(glob.glob(f'{e2}/build/g/{pattern}')):
        sp = importlib.util.spec_from_file_location('g', fn)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for q in getattr(m, 'POS', []):
            if q['id'] in built:
                sys.exit(f"{q['id']} is built twice: stop")
            built[q['id']] = q
    return built


def readonly(top):
    for d, _, fs in os.walk(top):
        for f in fs:
            p = os.path.join(d, f)
            os.chmod(p, os.stat(p).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    for d, _, _ in sorted(os.walk(top), key=lambda t: -len(t[0])):
        os.chmod(d, os.stat(d).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def card_text(db, name_id):
    sid = ' '.join(name_id.split()[-2:])
    c = db.get(sid)
    if c is None:
        return f'- {name_id}: not in the database'
    if 'hp' in c:
        s = (f"- **{c['name']} {c['id']}**: Pokémon, stage {c['stage']}, HP {c['hp']}, {c['energy_type']}; weakness {c.get('weakness')}; "
             f"retreat {len(c.get('retreat_cost') or [])}" + (f"; evolves from {c['evolves_from']}" if c.get('evolves_from') else ''))
        if c.get('ability'):
            s += f"\n  - Ability {c['ability'].get('title')}: {c['ability'].get('effect')}"
        for a in c.get('attacks') or []:
            s += f"\n  - Attack {a['title']} [{', '.join(a.get('energy_required') or [])}] {a.get('fixed_damage')}: {a.get('effect') or ''}"
        return s
    return f"- **{c['name']} {c['id']}**: {c.get('trainer_card_type')}. {c.get('effect')}"


def cards_in(pos):
    out = set()
    for side in ('me', 'opp'):
        s = pos[side]
        for b in s.get('board') or []:
            out.add(b['card'])
            out.update(b.get('behind') or [])
            out.update(b.get('tools') or [])
        out.update(s.get('hand') or [])
        out.update(s.get('discard') or [])
    if pos.get('stadium'):
        out.add(pos['stadium']['card'])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run3')
    ap.add_argument('exam_v2')
    ap.add_argument('--parts', type=int, default=5)
    ap.add_argument('--questions-per-part', type=int, default=6)  # v1.6's cap per part (addendum 8, K7)
    ap.add_argument('--dry', help='stage into this folder instead (a test; no prompts, no record)')
    ap.add_argument('--dry-build-glob', default='g*.py', help='with --dry: the build files to read')
    a = ap.parse_args()
    e2 = a.exam_v2
    base = a.dry or e2
    sel = {c['point_id']: c for c in json.load(open(f'{e2}/select/selection.json', encoding='utf-8'))['candidates']}
    built = load_build(e2, a.dry_build_glob if a.dry else 'g*.py')
    drops = {os.path.basename(p)[:-4] for p in glob.glob(f'{e2}/build/drops/*.txt')}
    if not a.dry:
        missing = sorted(set(sel) - set(built))
        if missing:
            sys.exit(f'{len(missing)} candidates have no build record (first: {missing[:3]}): stop')
    foreign = sorted(set(built) - set(sel))
    if foreign:
        sys.exit(f'build records that are not candidates: {foreign[:5]}: stop')
    batches = json.load(open(f'{e2}/build/batches.json', encoding='utf-8'))['batches']
    per = -(-len(batches) // a.parts)
    parts = [batches[i:i + per] for i in range(0, len(batches), per)]
    for k in range(1, len(parts) + 1):
        for d in (f'label_in_p{k}', f'label_out_p{k}'):
            if os.path.exists(os.path.join(base, d)):
                sys.exit(f'{d} exists already: stop')
    db = {v['id']: v for e in json.load(open(f'{e2}/bin/frozen_db_b5e68fc8.json', encoding='utf-8')) for v in e.values()}
    with open(f'{e2}/bin/decks.args') as f:
        args = f.read().split()
    # each deck's deck_kinds come from exactly one part: the one holding most of its points (ties: the earlier part)
    deck_pts = collections.defaultdict(collections.Counter)
    for k, bs in enumerate(parts, 1):
        for b in bs:
            for g in b['games']:
                deck_pts[g['deck']][k] += sum(1 for p in g['points'] if p['point_id'] in built and p['point_id'] not in drops)
    kinds_part = {d: max(sorted(c), key=lambda k: c[k]) for d, c in deck_pts.items()}
    prompt = open(f'{a.run3}/jobs/LABEL_JOB.md', encoding='utf-8').read().split('---- the prompt (LABEL_JOB_PROMPT.txt) ----', 1)[1].strip() + '\n'
    record = {'what': 'exam v2 labelling staging (stage_label.py)', 'drops_excluded': sorted(drops), 'parts': []}
    for k, bs in enumerate(parts, 1):
        lin = os.path.join(base, f'label_in_p{k}')
        os.makedirs(os.path.join(lin, 'sources'))
        os.makedirs(os.path.join(lin, 'decks'))
        os.makedirs(os.path.join(base, f'label_out_p{k}'))
        games = [g for b in bs for g in b['games']]
        pids = [p['point_id'] for g in games for p in g['points'] if p['point_id'] in built and p['point_id'] not in drops]
        views, selrows, files = [], [], {}
        cards = set()
        for pid in pids:
            b = built[pid]
            v = H.label_view(b)
            for bad in ('notes', 'approximate_reason', 'kind', '_draws', '_vpatch'):
                if bad in json.dumps(list(v.keys())):
                    sys.exit(f'{pid}: {bad} in the label view: stop')
            views.append(v)
            c = sel[pid]
            src = c['folder']
            review = 'REVIEW.md' if c['clips_in_game'] == 1 else \
                next(x for x in sorted(os.listdir(src)) if x.startswith('clip01_')) + '/REVIEW.md'
            selrows.append({'point_id': pid, 'game': c['game'], 'global_turn': c['global_turn'], 'clip': c['clip'],
                            'review': f"sources/{c['game']}/{review}"})
            cards |= cards_in(v)
        # the games' sources, from the usability staging (already hash-checked against the snapshot record); hashes checked again
        staging = json.load(open(f'{e2}/STAGING.json', encoding='utf-8'))
        rec = {}
        for p in staging['parts']:
            for rel, h in p['files'].items():
                rec[(p['part'], rel)] = h
        for g in games:
            src = g['folder']
            ipart = int(re.search(r'inv_in_p(\d+)', src).group(1))
            for d, _, fs in os.walk(src):
                for f in fs:
                    relg = os.path.relpath(os.path.join(d, f), src)
                    if os.path.basename(relg) not in SRC_KEEP + ('CLIPS.json',):
                        continue
                    s = os.path.join(d, f)
                    rel_staged = os.path.join('sources', g['game'], relg)
                    h = sha(s)
                    if f != 'CLIPS.json' and rec.get((ipart, rel_staged)) != h:
                        sys.exit(f'{s}: its hash is not the usability staging record\'s: stop')
                    dst = os.path.join(lin, rel_staged)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(s, dst)
                    files[rel_staged] = h
        decks = sorted({g['deck'] for g in games})
        for d in decks:
            shutil.copyfile(f'{e2}/decks/{d}.txt', os.path.join(lin, 'decks', f'{d}.txt'))
            for line in open(f'{e2}/decks/{d}.txt', encoding='utf-8'):
                if line[:1].isdigit():
                    cards.add(line.split(None, 1)[1].strip())
        with open(os.path.join(lin, 'DECK_KINDS_FOR.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(d for d in decks if kinds_part[d] == k) + '\n')
        with open(os.path.join(lin, 'CARDS.md'), 'w', encoding='utf-8') as f:
            f.write('# Card text (the frozen database, sha256 b5e68fc8...): every card in this part\'s decks and positions\n\n'
                    + '\n'.join(card_text(db, c) for c in sorted(cards)) + '\n')
        with open(os.path.join(lin, 'positions.json'), 'w', encoding='utf-8') as f:
            json.dump(views, f, indent=1, ensure_ascii=False)
        with open(os.path.join(lin, 'selection.json'), 'w', encoding='utf-8') as f:
            json.dump({'what': f'exam v2 points, labelling part {k} of {len(parts)}', 'points': selrows}, f, indent=1, ensure_ascii=False)
        # the legal lists along his move (pg_legal_v14 --legal-only on the candidate view with his move forced)
        qs = [dict(H.candidate_view(built[pid]), force=list(built[pid]['force'])) for pid in pids]
        out_lines = []
        if qs:
            tmp = os.path.join(e2, 'build', 'scratch', 'tmp', f'label_{os.getpid()}.json')
            os.makedirs(os.path.dirname(tmp), exist_ok=True)
            with open(tmp, 'w') as f:
                json.dump(qs, f, ensure_ascii=False)
            r = subprocess.run([BIN, '--positions', tmp, '--legal-only'] + args, capture_output=True, text=True)
            os.remove(tmp)
            if r.returncode or 'PGDUMP' in r.stderr:
                sys.exit('pg_legal_v14 failed or searched: ' + r.stderr[-1500:])
            out_lines = [l for l in r.stdout.splitlines() if json.loads(l)['kind'] == 'legal']
            if len(out_lines) != len(qs):
                sys.exit(f'part {k}: {len(out_lines)} legal lines for {len(qs)} points: stop')
        with open(os.path.join(lin, 'legal.jsonl'), 'w', encoding='utf-8') as f:
            f.write(''.join(l + '\n' for l in out_lines))
        shutil.copyfile(f'{a.run3}/jobs/ADJUDICATION_RULES.md', os.path.join(lin, 'ADJUDICATION_RULES.md'))
        shutil.copyfile(f'{e2}/inv_in_p1/RULES_FOR_AGENTS.md', os.path.join(lin, 'RULES_FOR_AGENTS.md'))
        listed = sorted(os.path.relpath(os.path.join(d, f), lin) for d, _, fs in os.walk(lin) for f in fs)
        with open(os.path.join(lin, 'FILES.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(listed) + '\n')
        allfiles = {os.path.relpath(os.path.join(d, f), lin): sha(os.path.join(d, f)) for d, _, fs in os.walk(lin) for f in fs}
        L, LO = f'{E2_ABS}/label_in_p{k}/', f'{E2_ABS}/label_out_p{k}/'
        p = (prompt
             .replace('/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md', L + 'RULES_FOR_AGENTS.md')
             .replace('  - /home/dacz8976/exam_v2/label_in/;\n  - RULES_FOR_AGENTS.md (path above);\n'
                      '  - card text, through `python3 lib/card.py <name or id>` run in /home/dacz8976/pincand.\n',
                      f'  - {L} (its RULES_FOR_AGENTS.md included). Its files are listed in `{L}FILES.txt`, one path per line, relative '
                      f'to {L}: you have no search, listing or shell tool, so take every path from that list.\n'
                      f'  - Card text: `{L}CARDS.md` (every card in this part\'s decks and positions, from the database the engine uses).\n')
             .replace('/home/dacz8976/exam_v2/label_out/', LO)
             .replace('- Look cards up with lib/card.py, never from memory.', f'- Look cards up in `{L}CARDS.md`, never from memory.')
             .replace('`label_in/', '`' + L).replace('`label_out/', '`' + LO)
             .replace('read the clips in order as one game. Its count continues across clips and never restarts.',
                      'read the clips in order as one game. Its count continues across clips and never restarts.\n'
                      "- A linked battle's `CLIPS.json` says whether its clips' folders carry ONE review of the whole battle; if they do, "
                      'read that review once.')
             .replace('(at most 6 in the whole exam)', f"(at most {a.questions_per_part} in this part (each part is about v1.6's size, "
                      "and v1.6 allowed 6))")
             .replace('**For each deck** in `' + L + 'decks/`', '**For each deck named in** `' + L + 'DECK_KINDS_FOR.txt` (and only those)'))
        for must in (L + 'FILES.txt', L + 'CARDS.md', 'DECK_KINDS_FOR.txt', f'at most {a.questions_per_part} in this part', LO + 'labels.json'):
            if must not in p:
                sys.exit(f'part {k}: the prompt edit did not take ({must!r}): the doc changed: stop')
        for bad in ('lib/card.py', '/mnt/c/', 'label_in/', 'label_out/'):
            if re.search(r'(?<![_\w])' + re.escape(bad), p.replace(L, '').replace(LO, '')):
                sys.exit(f'part {k}: the prompt still names {bad}: stop')
        if not a.dry:
            os.makedirs(os.path.join(e2, 'jobs'), exist_ok=True)
            with open(os.path.join(e2, 'jobs', f'LABEL_JOB_PROMPT_p{k}.txt'), 'w', encoding='utf-8') as f:
                f.write(p)
        readonly(lin)
        record['parts'].append({'part': k, 'batches': [b['batch'] for b in bs], 'games': [g['game'] for g in games], 'points': pids,
                                'decks': decks, 'deck_kinds_for': [d for d in decks if kinds_part[d] == k], 'files': allfiles,
                                'prompt_sha256': None if a.dry else sha(os.path.join(e2, 'jobs', f'LABEL_JOB_PROMPT_p{k}.txt'))})
        print(f'part {k}: batches {[b["batch"] for b in bs]}, {len(games)} games, {len(pids)} points, {len(decks)} decks '
              f'({len(record["parts"][-1]["deck_kinds_for"])} for deck_kinds), {len(cards)} cards in CARDS.md')
    if not a.dry:
        with open(os.path.join(e2, 'LABEL_STAGING.json'), 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=1, ensure_ascii=False)
    print(f'{sum(len(p["points"]) for p in record["parts"])} points in {len(parts)} parts; {len(drops)} G1 drops left out')


if __name__ == '__main__':
    main()

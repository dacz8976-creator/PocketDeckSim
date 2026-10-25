#!/usr/bin/env python3
"""Stage the two label fix jobs of the coordinator's note 044 (the advisor's audit of the answer key), before the freeze:
  A. RELINK: a fresh re-label of the 3 games recorded in two clips (their first-pass labels were probably made from the position alone,
     because their reviews sat only in clip folders): ~/exam_v2/label_in_relink/, each game's review the clip reviews MERGED in order, the one
     global turn count stated. Its labels replace the first pass's for those points.
  C. SECOND PASS: a fresh, independent alternatives pass over parts 3 and 5 (5/48 and 0/51 accepted, against 6-10 per part elsewhere and
     v1.6's 16/51): the same inputs (label_in_p3, label_in_p5, read-only), a prompt for the second pass; the game relabelled by A is skipped.
     Merge (decided before any output): the UNION of the two passes' acceptable lines, each passing the lister and pg_legal checks.

  stage_fixjobs.py RUN3_DIR EXAM_V2_DIR

Question caps (each part at most 6 in all, addendum 8 K7; the first pass used p1 3, p2 2, p3 1, p4 4, p5 5; note 044 D adds one in p1, p3, p4):
  A: at most 1 about part 2's two games, at most 1 about part 3's game; C p3: at most 3; C p5: at most 1.
Record: ~/exam_v2/FIXJOBS_STAGING.json. Refuses to overwrite."""
import glob, hashlib, importlib.util, json, os, shutil, subprocess, sys

RUN3, E2 = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(E2, 'build'))
sys.path.insert(0, '/home/dacz8976/df0tools')
import v2_helpers as H  # noqa: E402
import stage_label as SL  # noqa: E402  (card_text, cards_in, readonly, load_build)

RELINK_GAMES = {'20261021_020059000_SR': 2, '20261021_032324000_SR': 2, '20261022_004518000_SR': 3}
E2_ABS = '/home/dacz8976/exam_v2'


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    for d in ('label_in_relink', 'label_out_relink', 'label2_out_p3', 'label2_out_p5'):
        if os.path.exists(f'{E2}/{d}'):
            sys.exit(f'{d} exists already: stop')
    built = SL.load_build(E2)
    drops = {os.path.basename(p)[:-4] for p in glob.glob(f'{E2}/build/drops/*.txt')}
    sel = {c['point_id']: c for c in json.load(open(f'{E2}/select/selection.json', encoding='utf-8'))['candidates']}
    db = {v['id']: v for e in json.load(open(f'{E2}/bin/frozen_db_b5e68fc8.json', encoding='utf-8')) for v in e.values()}
    args = open(f'{E2}/bin/decks.args').read().split()
    # ---- A: the relink job
    R = f'{E2}/label_in_relink'
    pids = sorted(p for p in built if p not in drops and sel[p]['game'] in RELINK_GAMES)
    os.makedirs(f'{R}/sources')
    os.makedirs(f'{R}/decks')
    views, rows, cards = [], [], set()
    for pid in pids:
        v = H.label_view(built[pid])
        views.append(v)
        c = sel[pid]
        rows.append({'point_id': pid, 'game': c['game'], 'global_turn': c['global_turn'], 'clip': c['clip'], 'part': RELINK_GAMES[c['game']],
                     'review': f"sources/{c['game']}/REVIEW.md"})
        cards |= SL.cards_in(v)
    for g in RELINK_GAMES:
        src = sel[next(p for p in pids if sel[p]['game'] == g)]['folder']
        clips = json.load(open(f'{src}/CLIPS.json', encoding='utf-8'))
        n = len(clips['clips'])
        head = [f'# REVIEW of game {g}: ONE battle recorded in {n} clips, merged for this job', '',
                f'Below are the {n} clip folders\' REVIEW.md files, in recording order, each copied byte for byte. They are the SAME review of '
                'the whole battle (they differ at most in a line naming their own source), so read it once. The battle has ONE global turn '
                'count; the point ids (LAD-<game>-t<global turn>) use it, and the review gives each turn by that count.',
                'The review may name the clips its own way (Source1/Source2, Clip07/Clip08, ...); the clip numbers here follow the recording '
                'order (CLIPS.json: start times).', '']
        os.makedirs(f'{R}/sources/{g}')
        blob = ('\n'.join(head) + '\n').encode('utf-8')
        for c in clips['clips']:
            blob += f"\n## Clip {c['clip']} of {n} in recording order ({c['folder']}, start {c['start_utc']})\n\n".encode('utf-8')
            blob += open(f"{src}/{c['folder']}/REVIEW.md", 'rb').read()
            for f in ('UNCERTAINTIES.json', 'LADDER_ENTRY.json'):
                if os.path.exists(f"{src}/{c['folder']}/{f}"):
                    shutil.copyfile(f"{src}/{c['folder']}/{f}", f"{R}/sources/{g}/clip{c['clip']:02d}_{f}")
        open(f'{R}/sources/{g}/REVIEW.md', 'wb').write(blob)
        shutil.copyfile(f'{src}/CLIPS.json', f'{R}/sources/{g}/CLIPS.json')
    decks = sorted({built[p]['deck'] for p in pids})
    for d in decks:
        shutil.copyfile(f'{E2}/decks/{d}.txt', f'{R}/decks/{d}.txt')
        for line in open(f'{E2}/decks/{d}.txt', encoding='utf-8'):
            if line[:1].isdigit():
                cards.add(line.split(None, 1)[1].strip())
    open(f'{R}/CARDS.md', 'w', encoding='utf-8').write('# Card text (the frozen database, sha256 b5e68fc8...): every card in this job\'s decks and positions\n\n'
                                                       + '\n'.join(SL.card_text(db, c) for c in sorted(cards)) + '\n')
    json.dump(views, open(f'{R}/positions.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump({'what': 'exam v2: the points of the three games recorded in two clips, re-labelled (note 044 A)', 'points': rows},
              open(f'{R}/selection.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    qs = [dict(H.candidate_view(built[p]), force=list(built[p]['force'])) for p in pids]
    tmp = f'{E2}/build/scratch/tmp/relink_{os.getpid()}.json'
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    json.dump(qs, open(tmp, 'w'), ensure_ascii=False)
    r = subprocess.run([os.path.expanduser('~/exam/bin/pg_legal_v14'), '--positions', tmp, '--legal-only'] + args, capture_output=True, text=True)
    os.remove(tmp)
    if r.returncode or 'PGDUMP' in r.stderr:
        sys.exit('pg_legal_v14: ' + r.stderr[-800:])
    legal = [l for l in r.stdout.splitlines() if json.loads(l)['kind'] == 'legal']
    assert len(legal) == len(pids)
    open(f'{R}/legal.jsonl', 'w', encoding='utf-8').write(''.join(l + '\n' for l in legal))
    shutil.copyfile(f'{RUN3}/jobs/ADJUDICATION_RULES.md', f'{R}/ADJUDICATION_RULES.md')
    shutil.copyfile(f'{E2}/inv_in_p1/RULES_FOR_AGENTS.md', f'{R}/RULES_FOR_AGENTS.md')
    listed = sorted(os.path.relpath(os.path.join(d, f), R) for d, _, fs in os.walk(R) for f in fs)
    open(f'{R}/FILES.txt', 'w', encoding='utf-8').write('\n'.join(listed) + '\n')
    os.makedirs(f'{E2}/label_out_relink')
    base = open(f'{E2}/jobs/LABEL_JOB_PROMPT_p2.txt', encoding='utf-8').read()
    L2, LR, LRO = f'{E2_ABS}/label_in_p2/', f'{E2_ABS}/label_in_relink/', f'{E2_ABS}/label_out_relink/'
    pa = (base.replace(L2, LR).replace(f'{E2_ABS}/label_out_p2/', LRO)
          .replace("(at most 6 in this part (each part is about v1.6's size, and v1.6 allowed 6))",
                   '(at most 1 about the two games 20261021_020059000_SR and 20261021_032324000_SR together, and at most 1 about '
                   '20261022_004518000_SR)')
          .replace('**For each deck named in** `' + LR + 'DECK_KINDS_FOR.txt` (and only those): `deck_kinds` (several allowed) with a one-line reason each, '
                   'from the list and the card text.', "**Decks:** their `deck_kinds` are already given; write `\"decks\": {}`.")
          .replace('## The job: label exam v2\'s points by ADJUDICATION_RULES.md, exactly',
                   "## The job: label exam v2's points by ADJUDICATION_RULES.md, exactly\n"
                   'These are the points of three games, each ONE battle recorded in two clips. Each game\'s `sources/<game>/REVIEW.md` here '
                   'holds its two clip reviews in recording order; they are the SAME review of the whole battle (they differ at most in the line '
                   'naming their source), so read it once, whole, before labelling the game\'s points, and find each point by its global turn.'))
    for must in (LR + 'FILES.txt', LRO + 'labels.json', 'at most 1 about the two games', '"decks": {}', 'SAME review of the whole battle'):
        if must not in pa:
            sys.exit(f'relink prompt edit did not take: {must!r}: stop')
    if 'label_in_p' in pa or 'label_out_p' in pa:
        sys.exit('relink prompt still names a part folder: stop')
    open(f'{E2}/jobs/LABEL_RELINK_PROMPT.txt', 'w', encoding='utf-8').write(pa)
    SL.readonly(R)
    # ---- C: the second alternatives pass on parts 3 and 5 (the same inputs; a new prompt and out-folder)
    caps = {3: 3, 5: 1}
    for k in (3, 5):
        base = open(f'{E2}/jobs/LABEL_JOB_PROMPT_p{k}.txt', encoding='utf-8').read()
        LI, LO, LO2 = f'{E2_ABS}/label_in_p{k}/', f'{E2_ABS}/label_out_p{k}/', f'{E2_ABS}/label2_out_p{k}/'
        skip = [g for g, part in RELINK_GAMES.items() if part == k]
        pc = (base.replace(LO, LO2)
              .replace("(at most 6 in this part (each part is about v1.6's size, and v1.6 allowed 6))",
                       f"(at most {caps[k]} in this pass)")
              .replace('**For each deck named in** `' + LI + 'DECK_KINDS_FOR.txt` (and only those): `deck_kinds` (several allowed) with a one-line reason each, '
                       'from the list and the card text.', "**Decks:** their `deck_kinds` are already given; write `\"decks\": {}`.")
              .replace('## The job: label exam v2\'s points by ADJUDICATION_RULES.md, exactly',
                       "## The job: label exam v2's points by ADJUDICATION_RULES.md, exactly\n"
                       f'This is a SECOND, independent labelling pass over part {k}, made to judge the acceptable alternatives independently: '
                       'another worker labelled these points before you, and you don\'t see that work. Look at every point afresh: list genuinely '
                       'comparable whole-turn lines a strong player with the same plan could choose; none is fine.\n'
                       '- **A tool note:** the root legal list (step 0 of `legal.jsonl`) holds only the actions legal at the start of the turn. '
                       'Retreat is missing from it when something earlier in the turn makes it legal (an Energy attach, X Speed, Small Balloon, '
                       'evolving an Asleep or Paralyzed Active); such lines are still legal. The first action of each line must be in the root list.'
                       + (f"\n- **Skip** the points of game {', '.join(skip)}: they are re-labelled separately; leave them out of labels.json." if skip else '')))
        for must in (LO2 + 'labels.json', f'at most {caps[k]} in this pass', 'SECOND, independent labelling pass', 'Retreat is missing from it'):
            if must not in pc:
                sys.exit(f'second-pass prompt p{k}: edit did not take: {must!r}: stop')
        if LO in pc:
            sys.exit(f'second-pass prompt p{k} still names the first pass\'s out-folder: stop')
        open(f'{E2}/jobs/LABEL2_PROMPT_p{k}.txt', 'w', encoding='utf-8').write(pc)
        os.makedirs(f'{E2}/label2_out_p{k}')
    rec = {'what': "note 044's label fix jobs (stage_fixjobs.py)", 'relink': {'games': RELINK_GAMES, 'points': pids,
           'files': {os.path.relpath(os.path.join(d, f), R): sha(os.path.join(d, f)) for d, _, fs in os.walk(R) for f in fs}},
           'second_pass': {'parts': [3, 5], 'inputs': ['label_in_p3', 'label_in_p5'], 'caps': caps, 'skipped_games': [g for g, p in RELINK_GAMES.items() if p == 3]},
           'prompts': {os.path.basename(p): sha(p) for p in [f'{E2}/jobs/LABEL_RELINK_PROMPT.txt', f'{E2}/jobs/LABEL2_PROMPT_p3.txt', f'{E2}/jobs/LABEL2_PROMPT_p5.txt']}}
    json.dump(rec, open(f'{E2}/FIXJOBS_STAGING.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'relink: {len(pids)} points from 3 games; decks {decks}; cards {len(cards)}')
    print('second pass: parts 3 and 5 on their first-pass inputs; caps', caps)


if __name__ == '__main__':
    main()

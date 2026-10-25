#!/usr/bin/env python3
"""Stage the selection check's Part B (jobs/SELCHECK_JOB.md; PREREG_RUN3 section 3, addendum 5 G3), blind to the answers, as
  - ONE main job (items 1-4: the window, the two codings, no picking, the mix): ~/exam_v2/selcheck_in/;
  - FIVE facts jobs (item 5, the free-text facts, one per labelling part): ~/exam_v2/selcheck_facts_in_p<k>/.
The split keeps each session within reach (the free-text check reads 258 points beside about 1 MB of reviews); items 1-4 need no review
text (Part A reported no turn-list problem).

  stage_partb.py RUN3_DIR EXAM_V2_DIR

selcheck_in/ (read-only): PREREG_EXCERPT.md (sections 1-2, addendum 1, D1-D2, E1, E2, E7, G1, G3, G6, G8, G9; and, added for v2's own record,
addendum 6's H2-H4 (the window as closed) and addendum 8's K1 (the reading of G3)); INV_BRIEF.md, A_BRIEF.md (v1.6's); window.json (the
snapshot record) and BATTLE_REVIEW_INDEX.csv (copied; any row naming a .MOV left out); inventory.json (the first coding, merged, keyed by point
id); coding.json (Part A, merged); selection.json (every turn both codings call usable, and each one's build status); build_drops/,
lister_drops/ (problem types and step counts only); labels_summary.json (per point: answer kind, deck, how the key's first segment ends;
no line); run2_mix.json (run 2's aggregate); RULES_FOR_AGENTS.md; FILES.txt.
selcheck_facts_in_p<k>/ (read-only): position_facts.json (per point: ONLY opp_ambiguous, turn_effects, stadium, each board Pokemon's effects),
sources/<game>/ (REVIEW.md, and clip folders + CLIPS.json for a linked battle), FACTS_RULES.md (G5 and G13 item 6, verbatim),
RULES_FOR_AGENTS.md, FILES.txt.
Prompts: jobs/SELCHECK_JOB_PROMPT.txt (SELCHECK_JOB.md's Part B prompt; item 5 handed to the facts jobs) and jobs/SELCHECK_FACTS_PROMPT_p<k>.txt.
Record: ~/exam_v2/SELCHECK_STAGING.json. Refuses to overwrite."""
import csv, collections, glob, hashlib, json, os, re, shutil, stat, sys

E2_ABS = '/home/dacz8976/exam_v2'


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def readonly(top):
    for d, _, fs in os.walk(top):
        for f in fs:
            p = os.path.join(d, f)
            os.chmod(p, os.stat(p).st_mode & ~0o222)
    for d, _, _ in sorted(os.walk(top), key=lambda t: -len(t[0])):
        os.chmod(d, os.stat(d).st_mode & ~0o222)


def span(lines, start, stops):
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith(stops))
    return '\n'.join(lines[i:j]).strip()


def files_list(base):
    listed = sorted(os.path.relpath(os.path.join(d, f), base) for d, _, fs in os.walk(base) for f in fs)
    with open(os.path.join(base, 'FILES.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(listed) + '\n')


def main():
    global ASM
    run3, e2 = sys.argv[1], sys.argv[2]
    ASM = sys.argv[3] if len(sys.argv) > 3 else f'{e2}/assembly'  # the assembly folder whose draft and lister report Part B checks
    main_in = f'{e2}/selcheck_in'
    parts = [f'{e2}/selcheck_facts_in_p{k}' for k in range(1, 6)]
    for d in [main_in, f'{e2}/selcheck_out'] + parts + [f'{e2}/selcheck_facts_out_p{k}' for k in range(1, 6)]:
        if os.path.exists(d):
            sys.exit(f'{d} exists already: stop')
    pre = open(f'{run3}/PREREG_RUN3.md', encoding='utf-8').read().splitlines()
    ex = ['# PREREG_RUN3 excerpt for the selection check, Part B (verbatim; nothing else of the pre-registration is given)', '']
    for title, start, stops in [
            ('Section 1', '## 1. ', ('## 2. ',)), ('Section 2', '## 2. ', ('## 3. ',)),
            ('Addendum 1', '## Addendum 1', ('## Addendum 2',)),
            ('Addendum 3, D1', '**D1.', ('**D2.',)), ('Addendum 3, D2', '**D2.', ('**D3.',)),
            ('Addendum 4, E1', '**E1.', ('**E2.',)), ('Addendum 4, E2', '**E2.', ('**E3.',)), ('Addendum 4, E7', '**E7.', ('## Addendum 5',)),
            ('Addendum 5, G1', '**G1.', ('**G2.',)), ('Addendum 5, G3', '**G3.', ('**G4.',)), ('Addendum 5, G6', '**G6.', ('**G7.',)),
            ('Addendum 5, G8', '**G8.', ('**G9.',)), ('Addendum 5, G9', '**G9.', ('**G10.',)),
            ('Addendum 6, H2-H4 (the window as closed)', '**H2.', ('**H5.',)),
            ('Addendum 8, K1 (the usable set: how G3 was read)', '**K1.', ('**K2.',))]:
        ex += [f'## {title}', '', span(pre, start, stops), '']
    facts_rules = ['# The free-text facts rule (verbatim from PREREG_RUN3 addendum 5)', '', '## G5', '', span(pre, '**G5.', ('**G6.',)), '',
                   '## G13, item 6', '', span(pre, '6. **Free-text position facts**', ('## Addendum 6',)), '']
    os.makedirs(main_in)
    open(f'{main_in}/PREREG_EXCERPT.md', 'w', encoding='utf-8').write('\n'.join(ex) + '\n')
    for f in ('INV_BRIEF.md', 'A_BRIEF.md'):
        shutil.copyfile(f'{run3}/../build/{f}', f'{main_in}/{f}')
    shutil.copyfile(f'{run3}/window.json', f'{main_in}/window.json')
    idx = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/BATTLE_REVIEW_INDEX.csv'
    with open(idx, encoding='utf-8-sig', newline='') as fi, open(f'{main_in}/BATTLE_REVIEW_INDEX.csv', 'w', encoding='utf-8', newline='') as fo:
        rd = csv.DictReader(fi)
        wr = csv.DictWriter(fo, fieldnames=rd.fieldnames)
        wr.writeheader()
        mov = 0
        for r in rd:
            if '.mov' in ' '.join(str(v) for v in r.values()).lower():
                mov += 1
                continue
            wr.writerow(r)
    # the two codings, merged by point id
    inv, games, coding, tlp = {}, [], {}, []
    for k in (1, 2, 3):
        x = json.load(open(f'{e2}/inv_out_p{k}/inventory.json', encoding='utf-8'))
        for g in (x if isinstance(x, list) else x['games']):
            gid = g.get('game')
            games.append({kk: v for kk, v in g.items() if kk != 'turns'} | {'part': k})
            for t in g.get('turns') or []:
                pid = t.get('point_id') or t.get('id')
                inv[pid] = dict(t, game=gid, part=k)
        c = json.load(open(f'{e2}/selcode_out_p{k}/coding.json', encoding='utf-8'))
        for pid, t in c['turns'].items():
            coding[pid] = dict(t, part=k)
        tlp += [dict(x, part=k) for x in c.get('turn_list_problems') or []]
    json.dump({'what': 'the first coding (INV_JOB, three parts), every turn keyed by point id; field names as each part wrote them', 'games': games,
               'turns': inv}, open(f'{main_in}/inventory.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump({'format': 'pds-exam-v2-selcode', 'what': "Part A's blind second coding (three parts), merged", 'turns': coding,
               'turn_list_problems': tlp}, open(f'{main_in}/coding.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    sel = json.load(open(f'{e2}/select/selection.json', encoding='utf-8'))
    drops = {os.path.basename(p)[:-4] for p in glob.glob(f'{e2}/build/drops/*.txt')}
    draft = json.load(open(f'{ASM}/exam_v2_draft.json', encoding='utf-8'))
    pts = {p['id']: p for p in draft['points']}
    rows = []
    for c in sel['candidates']:
        st = 'point' if c['point_id'] in pts else ('dropped at build (G1): see build_drops/' if c['point_id'] in drops else 'MISSING')
        rows.append({'point_id': c['point_id'], 'game': c['game'], 'global_turn': c['global_turn'], 'clip': c['clip'], 'status': st})
    if any(r['status'] == 'MISSING' for r in rows):
        sys.exit('a candidate is neither a point nor a G1 drop: stop')
    json.dump({'what': 'every turn both codings call usable (select_v2.py; the rule: addendum 8, K1), and what became of it',
               'table': sel['table'], 'candidates': rows}, open(f'{main_in}/selection.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    os.makedirs(f'{main_in}/build_drops')
    for p in glob.glob(f'{e2}/build/drops/*.txt'):
        shutil.copyfile(p, f'{main_in}/build_drops/{os.path.basename(p)}')
    rep = json.load(open(f'{ASM}/lister_report.json', encoding='utf-8'))
    # the lister-check summaries (G1): problem types and step counts only; no plan end, no line tag beyond key / alternative
    os.makedirs(f'{main_in}/lister_drops')
    for pid in sorted({r['point'] for r in rep['rows'] if r['verdict'] != 'pass'}):
        mine = [r for r in rep['rows'] if r['point'] == pid and r['verdict'] != 'pass']
        verdicts = {r['verdict'] for r in mine}
        head = ('DROPPED (G1): its key line failed the lister check' if 'drop' in verdicts else
                'not dropped: ' + ', '.join(sorted({'resolved by R1 (the lister\'s first segment is used)' if v == 'resolved_by_R1'
                                                    else 'an alternative line was removed (G1)' for v in verdicts})))
        with open(f'{main_in}/lister_drops/{pid}.txt', 'w', encoding='utf-8') as f:
            f.write(f'{pid}: frozen-7 lister check (check_lister_v2.py): {head}\n')
            for r in mine:
                f.write(f"  {'the key line' if r['key_line'] else 'an alternative line'}: verdict {r['verdict']}; problems "
                        f"{[x['type'] for x in r['problems']]}; steps: line {r['line_steps']}, cut {r['cut_steps']}, lister {r['lister_steps']}\n")
    # the reviews of the games with a build drop (item 3 judges whether each drop is forced)
    drop_games = sorted({os.path.basename(p)[4:-4].rsplit('-t', 1)[0] for p in glob.glob(f'{e2}/build/drops/*.txt')})
    stg0 = json.load(open(f'{e2}/STAGING.json', encoding='utf-8'))
    rec0 = {(p['part'], rel): h for p in stg0['parts'] for rel, h in p['files'].items()}
    for g in drop_games:
        src = next(c['folder'] for c in sel['candidates'] if c['game'] == g)
        ipart = int(re.search(r'inv_in_p(\d+)', src).group(1))
        h = sha(f'{src}/REVIEW.md')
        if rec0.get((ipart, f'sources/{g}/REVIEW.md')) != h:
            sys.exit(f'{g}: REVIEW.md hash not in the usability staging record: stop')
        os.makedirs(f'{main_in}/sources/{g}')
        shutil.copyfile(f'{src}/REVIEW.md', f'{main_in}/sources/{g}/REVIEW.md')
    end_of = {r['point']: r['plan_end'] for r in rep['rows'] if r['ref'] == 'his'}
    cat = lambda e: 'chance' if e == 'chance' else ('opponent_choice' if e == 'opponent_choice' else 'end_of_turn')
    summ = {pid: {'deck': p['deck'], 'answer_kind': p['answer']['answer_kind'], 'first_segment_ends': cat(end_of[pid]),
                  'status': p['answer']['status']} for pid, p in pts.items()}
    json.dump({'what': "per point: its answer kind, its deck, and how its key line's first segment ends (frozen-7's lister: at a chance action, at "
               "an opponent's choice, or at the end of the turn); no line, no answer", 'points': summ,
               'counts': {'answer_kind': dict(collections.Counter(x['answer_kind'] for x in summ.values())),
                          'first_segment_ends': dict(collections.Counter(x['first_segment_ends'] for x in summ.values()))}},
              open(f'{main_in}/labels_summary.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump({'what': "run 2's AGGREGATE mix (SELCHECK_JOB.md, Part B); no per-point result",
               'points_by_deck': {'13-A': 23, 'deck 12': 14, 'Kingambit': 12}, 'points_by_kind': {'prepare': 22, 'attack now': 22, 'sacrifice': 5},
               'chance_ending_points': '33 of 49, counted under v1.6\'s rule (no opponent\'s-choice stop)', 'points': 49, 'games': 26,
               'scope': {'full': 19, 'partial': 9, 'none': 21},
               'build_time_drops_v16': "3 (../build/BUILD.md): one for a list problem, two 'cost judged too high', which addendum 5's G1 no longer allows"},
              open(f'{main_in}/run2_mix.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    shutil.copyfile(f'{e2}/inv_in_p1/RULES_FOR_AGENTS.md', f'{main_in}/RULES_FOR_AGENTS.md')
    files_list(main_in)
    # the facts jobs, one per labelling part
    lab = json.load(open(f'{e2}/LABEL_STAGING.json', encoding='utf-8'))
    stg = json.load(open(f'{e2}/STAGING.json', encoding='utf-8'))
    rec = {(p['part'], rel): h for p in stg['parts'] for rel, h in p['files'].items()}
    sel_rows = {c['point_id']: c for c in sel['candidates']}
    record = {'main': {}, 'facts': [], 'index_rows_left_out_naming_a_mov': mov}
    for k, base in enumerate(parts, 1):
        os.makedirs(f'{base}/sources')
        pids = [pid for pid in lab['parts'][k - 1]['points'] if pid in pts]
        facts = {}
        for pid in pids:
            v = pts[pid]['position']
            facts[pid] = {'opp_ambiguous': v.get('opp_ambiguous') or [], 'turn_effects': v.get('turn_effects') or [], 'stadium': v.get('stadium'),
                          'board_effects': {f'{side}.board[{i}]': b['effects'] for side in ('me', 'opp')
                                            for i, b in enumerate(v[side]['board']) if b.get('effects')}}
        json.dump({'what': "per point id, ONLY the position's free-text fact fields of the candidate view (PREREG_RUN3 addendum 5, G5 and G13 item 6)",
                   'points': facts}, open(f'{base}/position_facts.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        for g in sorted({sel_rows[p]['game'] for p in pids}):
            src = sel_rows[next(p for p in pids if sel_rows[p]['game'] == g)]['folder']
            ipart = int(re.search(r'inv_in_p(\d+)', src).group(1))
            for d, _, fs in os.walk(src):
                for f in fs:
                    if f not in ('REVIEW.md', 'CLIPS.json'):
                        continue
                    relg = os.path.relpath(os.path.join(d, f), src)
                    h = sha(os.path.join(d, f))
                    if f == 'REVIEW.md' and rec.get((ipart, os.path.join('sources', g, relg))) != h:
                        sys.exit(f'{g}/{relg}: hash not in the usability staging record: stop')
                    dst = os.path.join(base, 'sources', g, relg)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copyfile(os.path.join(d, f), dst)
        open(f'{base}/FACTS_RULES.md', 'w', encoding='utf-8').write('\n'.join(facts_rules) + '\n')
        shutil.copyfile(f'{e2}/inv_in_p1/RULES_FOR_AGENTS.md', f'{base}/RULES_FOR_AGENTS.md')
        files_list(base)
        os.makedirs(f'{e2}/selcheck_facts_out_p{k}')
        record['facts'].append({'part': k, 'points': pids, 'files': {os.path.relpath(os.path.join(d, f), base): sha(os.path.join(d, f))
                                                                      for d, _, fs in os.walk(base) for f in fs}})
        readonly(base)
        print(f'facts part {k}: {len(pids)} points, {len({sel_rows[p]["game"] for p in pids})} games')
    os.makedirs(f'{e2}/selcheck_out')
    record['main'] = {os.path.relpath(os.path.join(d, f), main_in): sha(os.path.join(d, f)) for d, _, fs in os.walk(main_in) for f in fs}
    readonly(main_in)
    # the prompts
    doc = open(f'{run3}/jobs/SELCHECK_JOB.md', encoding='utf-8').read()
    pb = doc.split('---- the prompt (SELCHECK_JOB_PROMPT.txt) ----', 1)[1].strip() + '\n'
    M = f'{E2_ABS}/selcheck_in/'
    item5 = re.search(r'5\. \*\*The free-text facts\*\*.*?(?=\n\nWrite `selcheck_out/SELECTION_CHECK\.md`)', pb, re.S)
    if not item5:
        sys.exit('Part B prompt: item 5 not found: stop')
    pb = (pb.replace('/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md', M + 'RULES_FOR_AGENTS.md')
          .replace('- **Read only:** /home/dacz8976/exam_v2/selcheck_in/ and RULES_FOR_AGENTS.md.',
                   f'- **Read only:** {M} (its RULES_FOR_AGENTS.md included). Its files are listed in `{M}FILES.txt`, one path per line, relative to '
                   f'{M}: you have no search, listing or shell tool, so take every path from that list. Part A reported no turn-list problem, so '
                   'reviews are staged only for the games with a build drop (`sources/<game>/REVIEW.md`, for item 3); the free-text facts (item 5) '
                   'are checked by five separate jobs. The `agreement.json` that addendum 8 K1 names is not given: find the two codings\' '
                   'disagreements from inventory.json and coding.json yourself.')
          .replace(item5.group(0), "5. **The free-text facts** are checked by five separate jobs, one per labelling part, beside the reviews; "
                   "their flags are merged with your result. Don't check them here: write `free_text_flags: []`.")
          .replace('`selcheck_out/', f'`{E2_ABS}/selcheck_out/'))
    for must in (M + 'FILES.txt', 'free_text_flags: []', f'{E2_ABS}/selcheck_out/SELECTION_CHECK.md'):
        if must not in pb:
            sys.exit(f'Part B prompt edit did not take: {must!r}: stop')
    os.makedirs(f'{e2}/jobs', exist_ok=True)
    open(f'{e2}/jobs/SELCHECK_JOB_PROMPT.txt', 'w', encoding='utf-8').write(pb)
    turns_rule = re.search(r'\*\*Turns and ids\.\*\*.*?(?=\n\n## )', pb, re.S).group(0)
    for k in range(1, 6):
        F, FO = f'{E2_ABS}/selcheck_facts_in_p{k}/', f'{E2_ABS}/selcheck_facts_out_p{k}/'
        fp = f"""You are an independent checker for Dustin's PocketDeckSim project (Pokémon TCG Pocket, the mobile game; read {F}RULES_FOR_AGENTS.md first). The coordinator launched you. You have never seen any bot's or judge's results on these exams, and you must not look for them. Never print environment variables or any key.

**Hard rules**
- **Read only:** {F} (its RULES_FOR_AGENTS.md included). Its files are listed in `{F}FILES.txt`, one path per line, relative to {F}: you have no search, listing or shell tool, so take every path from that list.
- **Write only** under {FO}.
- No git, no cargo, no subagents, no bot, no judge.
- **Never open:**
  - rl/results/weekly_review_2026-10-18/, rl/ai_judge/, ~/exam/, ~/exam_run1/, ~/exam_run2/, any other folder of /home/dacz8976/exam_v2/;
  - the agent mailbox, or any references or labels file.
- **Budget:** $5.

{turns_rule}
- A linked battle's `CLIPS.json` says whether its clips' folders carry ONE review of the whole battle; if they do, read that review once.

## The job: the selection check's item 5, the free-text facts, for this part's points (part {k} of 5)
`{F}position_facts.json` holds, per point id, ONLY the position's free-text fact fields from the candidate view: `opp_ambiguous`, `turn_effects`, `stadium` and each board Pokémon's `effects` (`{F}FACTS_RULES.md`: PREREG_RUN3 addendum 5, G5 and G13 item 6). These fields must state facts of the position only, in the review's own terms. Read every point's fields beside its review (`sources/<game>/REVIEW.md`; the point id names the game and the global turn), and report any wording that:
- hints at what he did or should do;
- judges a play;
- says more than the review states.
A note of which card printing was chosen, among the printings that match the facts the review shows, is the builder's record of a choice the review can't settle: flag the choice of printing itself only if it hints at his move or judges a play. Check every fact such a note cites (a name, an HP, an attack or Ability title) and every other statement in it against the review, at or before the point's turn, by the three tests above.

Give the point id, the field and the words. Don't rewrite anything yourself: a flagged text is rewritten to the review's own factual wording, or removed.

Write `{FO}facts_check.json`:

    {{"format": "pds-exam-v2-selcheck-facts", "part": {k}, "checked": ["<point id>", ...],
     "free_text_flags": [{{"point_id", "field", "words", "why"}}]}}

with every point id of position_facts.json in "checked". Finish by printing the number of points checked and the number of flags.
"""
        open(f'{e2}/jobs/SELCHECK_FACTS_PROMPT_p{k}.txt', 'w', encoding='utf-8').write(fp)
    record['prompts'] = {os.path.basename(p): sha(p) for p in sorted(glob.glob(f'{e2}/jobs/SELCHECK_*PROMPT*.txt'))}
    json.dump(record, open(f'{e2}/SELCHECK_STAGING.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'main: {len(record["main"])} files; index rows naming a .MOV left out: {mov}; prompts: {len(record["prompts"])}')


if __name__ == '__main__':
    main()

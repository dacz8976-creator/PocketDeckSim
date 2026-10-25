#!/usr/bin/env python3
"""Stage exam v2's usability coding (INV_JOB) and the selection check's Part A (SELCODE) from the real snapshot, in time-ordered parts.

  stage_jobs.py RUN3_DIR SNAPSHOT_DIR EXAM_V2_DIR RULES_FOR_AGENTS_MD [--parts 3]

- The in-window games come from RUN3_DIR/window.json (the committed snapshot record), sorted by start time and cut into --parts
  contiguous parts (sizes differ by at most one). The parts are a mechanical split by time, so no worker holds 90 reviews at once.
- sources/<game id>/: one folder per game (game id = v2_helpers.game_id of its opening clip's UTC start). A battle in several clips
  (PREREG_RUN3 addendum 4) holds clip01_<packet>/, clip02_<packet>/, ... (the packet name without its '.mp4') and CLIPS.json, built
  from window.json's metadata and the clips' review hashes alone (whether the clips carry one review of the whole battle).
  Each folder holds only REVIEW.md, LEAD_ACCEPTANCE.json, LADDER_ENTRY.json (where present), the QR file(s) and UNCERTAINTIES.json,
  each copied from SNAPSHOT_DIR/sources/<packet>/ and checked against window.json's sha256 (and against the copy's own hash). An
  exact-list game (addendum 3) with no QR file in its packet gets its exact-list packet's QR_DECODE.json, from the snapshot's copy,
  checked against window.json's exact_list record.
- inv_in_p<k>/: sources/, window.json (this part's games, metadata only), INV_BRIEF.md (v1.6's, verbatim), RULES_FOR_AGENTS.md.
- selcode_in_p<k>/: sources/ (the same files), INV_BRIEF.md, RULES_EXCERPT.md (PREREG_RUN3 section 2's usability lines, addendum 4's
  E1, E2 and E7, addendum 5's G3 and G6, verbatim), RULES_FOR_AGENTS.md. turns.json is added after the INV job, by make_turns.py.
- FILES.txt in each in-folder lists every path the worker may read (Part A's lists turns.json ahead): the workers run with
  --restricted, which leaves them Read and Edit only, with no search or listing tool (smoke-tested Oct 25 on dummy files).
- jobs/INV_JOB_PROMPT_p<k>.txt and jobs/SELCODE_JOB_PROMPT_p<k>.txt: the prompts of jobs/INV_JOB.md and jobs/SELCHECK_JOB.md (Part A),
  with this part's folders as absolute paths (the worker runs from its in-folder), the local RULES_FOR_AGENTS.md, one line on the
  brief's v1.6 paths and one line on linked battles' reviews. Empty inv_out_p<k>/ and selcode_out_p<k>/ are made.
- STAGING.json (EXAM_V2_DIR): every part's games and every staged file's sha256 (sources, generated inputs and prompts). The in-folders
  are then made read-only (chmod a-w). Refuses to overwrite an earlier staging.
"""
import argparse, difflib, hashlib, json, os, re, shutil, stat, sys

KEEP = ('REVIEW.md', 'LEAD_ACCEPTANCE.json', 'LADDER_ENTRY.json', 'UNCERTAINTIES.json')
QR = re.compile(r'^(?:LINKED_.*)?QR_(?:ID|DECODE)\.json$')
E2_ABS = '/home/dacz8976/exam_v2'
RULES_SRC = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md'


def sha(p):
    with open(p, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def game_id(start_utc):
    m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z', start_utc)
    if not m:
        raise ValueError(start_utc)
    return '{}{}{}_{}{}{}000_SR'.format(*m.groups())


def clip_folder(order, packet):
    return f"clip{order:02d}_{packet[:-4] if packet.endswith('.mp4') else packet}"


def between(lines, start, stop):
    """The lines from the first that starts with `start` up to (not including) the next that starts with `stop`."""
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith(stop))
    return lines[i:j]


def prompt_of(doc, marker, end=None):
    body = open(doc, encoding='utf-8').read().split(marker, 1)[1]
    if end:
        body = body.split(end, 1)[0]
    return body.strip() + '\n'


def deck_qr_file(r, names_opening):
    """The file in the opening folder that holds the list's filmed code, from window.json's deck_source (metadata)."""
    m = re.match(r'filmed code \(([^;)]+)', r.get('deck_source') or '')
    if not m:
        sys.exit(f"{r['packet']}: deck_source {r.get('deck_source')!r} names no filmed code: stop")
    f = m.group(1).rsplit('/', 1)[-1]
    if f not in names_opening:
        sys.exit(f"{r['packet']}: its deck source {f} is not in the staged opening folder {sorted(names_opening)}: stop")
    return f


def readonly(top):
    for d, dirs, files in os.walk(top):
        for f in files:
            p = os.path.join(d, f)
            os.chmod(p, os.stat(p).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))
    for d, dirs, files in sorted(os.walk(top), key=lambda t: -len(t[0])):
        os.chmod(d, os.stat(d).st_mode & ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run3')
    ap.add_argument('snapshot')
    ap.add_argument('exam_v2')
    ap.add_argument('rules_for_agents')
    ap.add_argument('--parts', type=int, default=3)
    a = ap.parse_args()
    if os.path.abspath(a.exam_v2) != E2_ABS:
        sys.exit(f'the prompts name {E2_ABS}; stage there: stop')
    w = json.load(open(os.path.join(a.run3, 'window.json'), encoding='utf-8'))
    games = sorted((r for r in w['packets'] if r['status'] == 'in'), key=lambda r: r['start_utc'])
    ids = [game_id(r['start_utc']) for r in games]
    if len(set(ids)) != len(ids):
        sys.exit('two games share a game id: stop')
    for k in range(1, a.parts + 1):
        for d in (f'inv_in_p{k}', f'inv_out_p{k}', f'selcode_in_p{k}', f'selcode_out_p{k}'):
            if os.path.exists(os.path.join(a.exam_v2, d)):
                sys.exit(f'{d} exists already: stop')
    if os.path.exists(os.path.join(a.exam_v2, 'STAGING.json')):
        sys.exit('STAGING.json exists already: stop')

    # RULES_EXCERPT.md (Part A): verbatim spans of PREREG_RUN3.md
    pre = open(os.path.join(a.run3, 'PREREG_RUN3.md'), encoding='utf-8').read().splitlines()
    spans = [('PREREG_RUN3 section 2 (the usability lines)', between(pre, '- **A point is every one of his turns that is USABLE**', '- **No discretionary picking.**')),
             ('PREREG_RUN3 addendum 4, E1', between(pre, '**E1.', '**E2.')),
             ('PREREG_RUN3 addendum 4, E2', between(pre, '**E2.', '**E3.')),
             ('PREREG_RUN3 addendum 4, E7', between(pre, '**E7.', '## Addendum 5')),
             ('PREREG_RUN3 addendum 5, G3', between(pre, '**G3.', '**G4.')),
             ('PREREG_RUN3 addendum 5, G6', between(pre, '**G6.', '**G7.'))]
    excerpt = '# Rules excerpt for the blind second coding (exam v2, run 3)\n\nVerbatim from PREREG_RUN3.md; nothing else of it is given.\n'
    for title, ls in spans:
        excerpt += f'\n## {title}\n\n' + '\n'.join(ls).strip() + '\n'

    brief = os.path.join(a.run3, '..', 'build', 'INV_BRIEF.md')
    v16_note = ("- **The brief's own paths are v1.6's** (its Source folders, its 39 games, its /home/dacz8976/exam/inv/ output and its budget): "
                "use only the folders and the budget named in this prompt.")
    linked_note = ("  - A linked battle's `CLIPS.json` says whether its clips' folders carry ONE review of the whole battle. "
                   "If they do, read that review once and count each turn once; its clip boundary is where the review places it.")
    inv_p = prompt_of(os.path.join(a.run3, 'jobs', 'INV_JOB.md'), '---- the prompt (INV_JOB_PROMPT.txt) ----')
    sel_p = prompt_of(os.path.join(a.run3, 'jobs', 'SELCHECK_JOB.md'), '---- the prompt (SELCODE_JOB_PROMPT.txt) ----', '## Part B')
    anchor_inv = '- **Where the brief names other files,** use these instead:'
    anchor_sel = '- **Turns and ids.**'
    anchor_clip = "  - A game whose folder holds `clip01_…`, `clip02_…` and so on is ONE battle recorded in several clips: read the clips in order as one game. Its count continues across clips and never restarts."
    rules_ref = '/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/RULES_FOR_AGENTS.md'
    for p in (inv_p, sel_p):
        assert p.count(anchor_clip) == 1 and p.count(rules_ref) == 1, 'a prompt anchor moved'
    assert inv_p.count(anchor_inv) == 1 and sel_p.count(anchor_sel) == 1

    os.makedirs(os.path.join(a.exam_v2, 'jobs'), exist_ok=True)
    rules_sha = sha(a.rules_for_agents)
    n = len(games)
    bounds = [round(n * k / a.parts) for k in range(a.parts + 1)]
    staging = {'what': 'exam v2 job staging (stage_jobs.py)', 'window_record': {'file': os.path.join(a.run3, 'window.json'),
               'sha256': sha(os.path.join(a.run3, 'window.json'))}, 'snapshot': a.snapshot,
               'rules_for_agents': {'from': a.rules_for_agents, 'sha256': rules_sha}, 'parts': []}
    for k in range(1, a.parts + 1):
        part = list(zip(ids, games))[bounds[k - 1]:bounds[k]]
        inv_in = os.path.join(a.exam_v2, f'inv_in_p{k}')
        sel_in = os.path.join(a.exam_v2, f'selcode_in_p{k}')
        files_rec, gl, qr_from = {}, [], {}

        def put(rel, src, h):
            for base in (inv_in, sel_in):
                dst = os.path.join(base, 'sources', rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
                if sha(dst) != h:
                    sys.exit(f'{dst}: the copy differs: stop')
            files_rec[os.path.join('sources', rel)] = h

        for gid, r in part:
            clips = r.get('clips') or [{'clip_order': 1, 'packet': r['packet'], 'start_utc': r['start_utc'], 'files': r['files']}]
            if r.get('clips'):
                clips = [dict(c, files=(r['files'] if i == 0 else c['files'])) for i, c in enumerate(clips)]
            multi = len(clips) > 1
            opening_names = []
            for c in clips:
                src = os.path.join(a.snapshot, 'sources', c['packet'])
                rel = os.path.join(gid, clip_folder(c['clip_order'], c['packet'])) if multi else gid
                names = [f for f in sorted(c['files']) if f in KEEP or QR.match(f)]
                if 'REVIEW.md' not in names:
                    sys.exit(f"{c['packet']}: no REVIEW.md in the record: stop")
                for f in names:
                    h = sha(os.path.join(src, f))
                    if h != c['files'][f]['sha256']:
                        sys.exit(f"{c['packet']}/{f}: sha256 {h[:12]} differs from window.json's {c['files'][f]['sha256'][:12]}: stop")
                    put(os.path.join(rel, f), os.path.join(src, f), h)
                if c['clip_order'] == 1:
                    opening_names = list(names)
                    if not any(QR.match(f) for f in names):
                        # the list's filmed code is in its exact-list packet (addendum 3), recorded in window.json with its sha256
                        x = r.get('exact_list') or {}
                        want = (x.get('files') or {}).get('QR_DECODE.json')
                        want = want.get('sha256') if isinstance(want, dict) else want
                        if not want:
                            sys.exit(f"{c['packet']}: no QR file in the record and no exact-list QR_DECODE.json: stop")
                        src_q = os.path.join(a.snapshot, 'sources', x['folder'], 'QR_DECODE.json')
                        h = sha(src_q)
                        if h != want:
                            sys.exit(f'{src_q}: sha256 {h[:12]} differs from window.json exact_list {want[:12]}: stop')
                        put(os.path.join(rel, 'QR_DECODE.json'), src_q, h)
                        opening_names.append('QR_DECODE.json')
                        qr_from[gid] = f"{x['folder']}/QR_DECODE.json (the exact-list packet, PREREG_RUN3 addendum 3)"
            if multi:
                revs = [open(os.path.join(a.snapshot, 'sources', c['packet'], 'REVIEW.md'), 'rb').read() for c in clips]
                shared = []
                for b in revs[1:]:
                    x, y = revs[0].decode('utf-8').splitlines(), b.decode('utf-8').splitlines()
                    same = sum(bl.size for bl in difflib.SequenceMatcher(None, x, y, autojunk=False).get_matching_blocks())
                    shared.append((same, len(x), len(y)))
                one_review = all(s >= max(lx, ly) - 2 for s, lx, ly in shared)
                cj = {'game': gid, 'battle_id': r.get('battle_id'),
                      'clips': [{'clip': c['clip_order'], 'folder': clip_folder(c['clip_order'], c['packet']), 'packet': c['packet'],
                                 'start_utc': c['start_utc'], 'review_sha256': hashlib.sha256(rv).hexdigest(), 'review_bytes': len(rv),
                                 **({'review_lines_shared_with_clip01': f'{s} of {ly}'} if i else {})}
                                for i, (c, rv, (s, lx, ly)) in enumerate(zip(clips, revs, [(0, 0, 0)] + shared))],
                      'one_review_of_the_whole_battle': one_review,
                      'note': ('The clips\' REVIEW.md files are the same review of the whole battle (byte-identical, or differing in at most '
                               'two lines): read it once and count each turn once.' if one_review else
                               'The clips\' REVIEW.md files differ: each covers its own part of the battle.')
                              + ' Built from the snapshot record (clip order, packet names, start times) and the reviews\' hashes and line counts alone.'}
                for base in (inv_in, sel_in):
                    with open(os.path.join(base, 'sources', gid, 'CLIPS.json'), 'w', encoding='utf-8') as f:
                        json.dump(cj, f, indent=1, ensure_ascii=False)
            gl.append({'game': gid, 'start_utc': r['start_utc'], 'folder': f'sources/{gid}', 'packet': r['packet'],
                       'clips': len(clips), 'deck': r['deck'],
                       'deck_qr_file': (clip_folder(1, r['packet']) + '/' if multi else '') + (
                           'QR_DECODE.json' if gid in qr_from else deck_qr_file(r, opening_names)),
                       'review_completion': r['review_completion'],
                       **({'qr_file_from': qr_from[gid]} if gid in qr_from else {}),
                       **({'partial_review_note': r['partial_review_note']} if r.get('partial_review_note') else {})})
        with open(os.path.join(inv_in, 'window.json'), 'w', encoding='utf-8') as f:
            json.dump({'what': f'exam v2 (run 3) in-window games, part {k} of {a.parts} (by start time); PREREG_RUN3 section 1 and addendum 6',
                       'window_start_exclusive': w['window_start_exclusive'], 'window_end_inclusive': w['window_end_inclusive'],
                       'games': gl}, f, indent=1, ensure_ascii=False)
        for base in (inv_in, sel_in):
            shutil.copyfile(brief, os.path.join(base, 'INV_BRIEF.md'))
            shutil.copyfile(a.rules_for_agents, os.path.join(base, 'RULES_FOR_AGENTS.md'))
        with open(os.path.join(sel_in, 'RULES_EXCERPT.md'), 'w', encoding='utf-8') as f:
            f.write(excerpt)
        # the workers run with --restricted, which leaves no search or listing tool: every path they may read is listed here
        for base, later in ((inv_in, []), (sel_in, ['turns.json'])):
            listed = sorted(os.path.relpath(os.path.join(d, f), base) for d, _, fs in os.walk(base) for f in fs)
            with open(os.path.join(base, 'FILES.txt'), 'w', encoding='utf-8') as f:
                f.write('\n'.join(sorted(listed + later)) + '\n')
        os.makedirs(os.path.join(a.exam_v2, f'inv_out_p{k}'))
        os.makedirs(os.path.join(a.exam_v2, f'selcode_out_p{k}'))
        I, IO, S, SO = (f'{E2_ABS}/{x}_p{k}/' for x in ('inv_in', 'inv_out', 'selcode_in', 'selcode_out'))
        p1 = (inv_p.replace('/home/dacz8976/exam_v2/inv_in/', I).replace('/home/dacz8976/exam_v2/inv_out/', IO)
              .replace('`inv_in/', '`' + I).replace('`inv_out/', '`' + IO)
              .replace(rules_ref, I + 'RULES_FOR_AGENTS.md')
              .replace(anchor_inv, v16_note + '\n' + anchor_inv).replace(anchor_clip, anchor_clip + '\n' + linked_note))
        p2 = (sel_p.replace('/home/dacz8976/exam_v2/selcode_in/', S).replace('/home/dacz8976/exam_v2/selcode_out/', SO)
              .replace('`selcode_out/', '`' + SO)
              .replace(rules_ref, S + 'RULES_FOR_AGENTS.md')
              .replace(anchor_sel, v16_note + '\n' + anchor_sel).replace(anchor_clip, anchor_clip + '\n' + linked_note))
        files_line = ("- **Your folder's files** are listed in `{0}FILES.txt`, one path per line, relative to {0}. "
                      "You have no search, listing or shell tool, so take every path from that list.")
        p1 = p1.replace('and RULES_FOR_AGENTS.md. Text files only, never images or videos.',
                        '(its RULES_FOR_AGENTS.md included). Text files only, never images or videos.\n' + files_line.format(I), 1)
        p2 = p2.replace('and RULES_FOR_AGENTS.md. Text files only, never images or videos.',
                        '(its RULES_FOR_AGENTS.md included). Text files only, never images or videos.\n' + files_line.format(S)
                        + ' `RULES_EXCERPT.md` there holds the pre-registration\'s usability rules, verbatim.', 1)
        assert f'{I}FILES.txt' in p1 and f'{S}FILES.txt' in p2, 'the Read only line moved'
        for p, tag in ((p1, 'inv_in/'), (p1, 'inv_out/'), (p2, 'selcode_in/'), (p2, 'selcode_out/'), (p1, 'Projects/Pocket'), (p2, 'Projects/Pocket')):
            if re.search(r'(?<![_\w])' + re.escape(tag), p):
                sys.exit(f'part {k}: a prompt still names {tag}: stop')
        for p in (p1, p2):
            for path in re.findall(r'/home/dacz8976/exam_v2/(\w+)/', p):
                if path not in (f'inv_in_p{k}', f'inv_out_p{k}', f'selcode_in_p{k}', f'selcode_out_p{k}'):
                    sys.exit(f'part {k}: a prompt names /home/dacz8976/exam_v2/{path}/: stop')
        for name, p in ((f'INV_JOB_PROMPT_p{k}.txt', p1), (f'SELCODE_JOB_PROMPT_p{k}.txt', p2)):
            with open(os.path.join(a.exam_v2, 'jobs', name), 'w', encoding='utf-8') as f:
                f.write(p)
        generated = {}
        for base in (inv_in, sel_in):
            for d, _, fs in os.walk(base):
                for f in fs:
                    rel = os.path.relpath(os.path.join(d, f), a.exam_v2)
                    if os.path.relpath(os.path.join(d, f), base) not in files_rec:
                        generated[rel] = sha(os.path.join(d, f))
        staging['parts'].append({'part': k, 'games': [g['game'] for g in gl], 'first': gl[0]['start_utc'], 'last': gl[-1]['start_utc'],
                                 'linked_battles': sum(g['clips'] > 1 for g in gl), 'files': files_rec, 'generated': generated,
                                 'prompts': {n: sha(os.path.join(a.exam_v2, 'jobs', n)) for n in (f'INV_JOB_PROMPT_p{k}.txt', f'SELCODE_JOB_PROMPT_p{k}.txt')}})
        readonly(inv_in)
        readonly(sel_in)
        print(f"part {k}: {len(gl)} games ({gl[0]['start_utc']} .. {gl[-1]['start_utc']}), "
              f"{sum(g['clips'] > 1 for g in gl)} linked, {len(files_rec)} source files, {len(generated)} generated files, "
              f"review text {sum(os.path.getsize(os.path.join(inv_in, p)) for p in files_rec if p.endswith('REVIEW.md'))} bytes")
    with open(os.path.join(a.exam_v2, 'STAGING.json'), 'w', encoding='utf-8') as f:
        json.dump(staging, f, indent=1, ensure_ascii=False)
    print(f'{n} games in {a.parts} parts; STAGING.json written; in-folders read-only')


if __name__ == '__main__':
    main()

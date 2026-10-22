#!/usr/bin/env python3
"""Exam v2's deck files from the deck codes filmed at the start of each in-window game (PREREG_RUN3 section 1: an exact list is QR-verified).

  make_v2_decks.py --evidence DIR [DIR ...] --frozen-db DATABASE_JSON --out run3/decks

Read only: each packet's QR_ID.json or QR_DECODE.json `payload` (the filmed code). For every distinct payload:
- decode it with the deck journal's decode_payload (lib/encode_qr.py's layout): its card entities and Energy;
- the code names the CARD, not the printing: each entity is written as ONE of its printings (encode_qr's catalog) that the frozen engine tree's
  database holds: the printing the repository's deck files use most (decks/, at the given ref), else the first released (set order below), so
  the lists use the same printings as every deck the project already plays (printings of one card play the same: the journal's
  `plays_same_as` rule; the choice of printing is recorded);
- write `run3/decks/v2deck_<first 10 hex of sha256(payload)>.txt` in the deck format (journal.list_lines);
- check that the file encodes back to the same code: code_cards(file) == decode_payload(payload), 20 cards.
`DECKS.json` maps each deck file to its payload, the games that filmed it, the QR file's schema and any weakness the packet records
(e.g. battle_full20_proven = false). Games without a filmed code get no deck file here (they need an exact list under PREREG_RUN3
section 1 and addendum 3, D1).
A game is one Drive recording (its drive id: the packet folder's name before "_ScreenRecording", or the whole name of a targeted
addendum folder such as Codex's QR_EXACT_LISTS_2026-10-21/<drive id>/). A game with two QR sources is listed once, the second under
`also_from`; two sources with different payloads stop the script. Deck files whose card lines are identical (two codes for one list)
name each other in `same_list_as`."""
import argparse, collections, glob, hashlib, json, os, sys

REPO = '/home/dacz8976/pincand'
sys.path.insert(0, os.path.join(REPO, 'rl', 'deck_journal'))
sys.path.insert(0, os.path.join(REPO, 'lib'))
import journal  # noqa: E402
import encode_qr  # noqa: E402


SET_ORDER = ['P-A', 'A1', 'A1a', 'A2', 'A2a', 'A2b', 'A3', 'A3a', 'A3b', 'A4', 'A4a', 'A4b', 'P-B', 'B1', 'B1a', 'B2', 'B2a', 'B2b', 'B3', 'B3a',
             'B3b', 'B4', 'B4a', 'B4b']


def norm_key(k):
    kind, num = k.split(':')
    return f'{kind}:{int(num):06d}'


def release_key(cid):
    s, n = cid.rsplit(' ', 1)
    return (SET_ORDER.index(s) if s in SET_ORDER else len(SET_ORDER), int(n))


def repo_usage(ref):
    """How often each printing appears in the repository's deck files at `ref` (decks/**/*.txt)."""
    import re, subprocess
    ls = subprocess.run(['git', '-C', REPO, 'ls-tree', '-r', '--name-only', ref, 'decks/'], capture_output=True, text=True)
    if ls.returncode or not ls.stdout.strip():
        sys.exit(f'git ls-tree {ref} decks/ failed or is empty: {ls.stderr.strip()}')
    names = ls.stdout.split()
    line = re.compile(r'^\s*(\d+)\s+.+?\s+((?:P-[AB])|(?:[AB]\d[a-z]?))\s+(\d{1,3})\s*$')
    use = collections.Counter()
    for n in names:
        if n.endswith('.txt'):
            for l in subprocess.run(['git', '-C', REPO, 'show', f'{ref}:{n}'], capture_output=True, text=True).stdout.splitlines():
                m = line.match(l)
                if m:
                    use[f'{m.group(2)} {int(m.group(3)):03d}'] += int(m.group(1))
    return use


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', nargs='+', required=True)
    ap.add_argument('--frozen-db', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--decks-ref', default='origin/main')
    a = ap.parse_args()
    frozen_ids = {c.get('id') for e in json.load(open(a.frozen_db, encoding='utf-8')) for c in e.values()}
    usage = repo_usage(a.decks_ref)
    printings = collections.defaultdict(list)
    for cid, rec in encode_qr.BYID.items():
        printings[norm_key(rec['entity_key'])].append(cid)
    payloads, by_drive, continuations = {}, {}, []
    for ev in a.evidence:
        for d in sorted(glob.glob(os.path.join(ev, '*'))):
            qr_pays = {}
            for f in ('QR_ID.json', 'QR_DECODE.json'):
                p = os.path.join(d, f)
                if os.path.exists(p):
                    with open(p, encoding='utf-8-sig') as fh:
                        qq = json.load(fh)
                    qr_pays[f] = next((qq[k] for k in ('payload', 'qr_payload', 'decoded_payload') if isinstance(qq.get(k), str) and qq[k]), None)
            if len(set(qr_pays.values())) > 1:
                sys.exit(f'{d}: QR_ID.json and QR_DECODE.json give different payloads')
            for f in ('QR_ID.json', 'QR_DECODE.json'):
                p = os.path.join(d, f)
                if os.path.exists(p):
                    with open(p, encoding='utf-8-sig') as fh:
                        q = json.load(fh)
                    pay = qr_pays[f]
                    if not pay and (q.get('linked_payload') or q.get('linked_qr_metadata') or q.get('status') == 'not_visible_in_this_clip'):
                        # a continuation clip of a linked battle (PREREG_RUN3 addendum 4): no code of its own; its link names the
                        # opening clip and that clip's code, which must equal the opening clip's own code (checked after the scan)
                        linked = q.get('linked_payload')
                        linked_file = f'{f}:linked_payload' if linked else None
                        opening = (q.get('linked_opening_source') or q.get('linked_source') or {}).get('drive_file_id')
                        if not linked and q.get('linked_qr_metadata'):
                            lp = os.path.join(d, os.path.basename(q['linked_qr_metadata']))
                            if not os.path.exists(lp):
                                sys.exit(f'{p}: its linked QR file {q["linked_qr_metadata"]} is missing')
                            with open(lp, encoding='utf-8-sig') as fh:
                                lq = json.load(fh)
                            linked = next((lq[k] for k in ('payload', 'qr_payload', 'decoded_payload') if isinstance(lq.get(k), str) and lq[k]), None)
                            linked_file = os.path.basename(q['linked_qr_metadata'])
                            if opening and lq.get('drive_file_id') and lq['drive_file_id'] != opening:
                                sys.exit(f'{lp}: names opening {lq["drive_file_id"]}, but {f} names {opening}')
                            opening = opening or lq.get('drive_file_id')
                        if not linked or not opening:
                            sys.exit(f'{p}: a clip with no code of its own and no linked code / opening clip')
                        continuations.append({'packet': os.path.basename(d), 'batch': os.path.basename(ev), 'qr_file': f,
                                              'drive_id': os.path.basename(d).split('_ScreenRecording')[0], 'opening_drive_id': opening,
                                              'linked_payload': linked, 'linked_qr_file': linked_file})
                        break
                    if not pay:
                        sys.exit(f'{p}: no payload')
                    weak = {k: q[k] for k in ('battle_full20_proven', 'unsaved_changes_prompt', 'notes') if k in q}
                    src = {'packet': os.path.basename(d), 'batch': os.path.basename(ev), 'qr_file': f,
                           'schema': q.get('schema'), 'weak': weak,
                           'filename': q.get('filename') or q.get('source_filename') or (q.get('source') if isinstance(q.get('source'), dict) else {}).get('filename')}
                    # one game = one Drive recording: a packet folder is "<drive id>_ScreenRecording_..." or, for a targeted addendum, "<drive id>"
                    drive = os.path.basename(d).split('_ScreenRecording')[0]
                    if drive in by_drive:
                        first_pay, first = by_drive[drive]
                        if first_pay != pay:
                            sys.exit(f'{drive}: two QR sources with different payloads ({first["packet"]}, {src["packet"]})')
                        first.setdefault('also_from', []).append({k: src[k] for k in ('packet', 'batch', 'qr_file', 'schema', 'weak')})
                        break
                    game = dict(src, drive_id=drive)
                    by_drive[drive] = (pay, game)
                    payloads.setdefault(pay, []).append(game)
                    break
    # each continuation joins its opening clip's game: one game per battle; its linked code must be the opening clip's own code
    for c in continuations:
        if c['drive_id'] in by_drive:
            sys.exit(f"{c['packet']}: a continuation that also has a code of its own")
        if c['opening_drive_id'] not in by_drive:
            sys.exit(f"{c['packet']}: its opening clip {c['opening_drive_id']} has no code of its own in the given evidence")
        opay, ogame = by_drive[c['opening_drive_id']]
        if c['linked_payload'] != opay:
            sys.exit(f"{c['packet']}: its linked code is not its opening clip's code ({ogame['packet']})")
        ogame.setdefault('continuations', []).append({k: c[k] for k in ('packet', 'batch', 'qr_file', 'drive_id', 'linked_qr_file')})
    os.makedirs(a.out, exist_ok=True)
    index = {}
    for pay, games in sorted(payloads.items(), key=lambda kv: kv[1][0]['packet']):
        dec = journal.decode_payload(pay)
        counts = collections.Counter(norm_key(k) for k in dec['cards'])
        pairs, choices = [], {}
        for ent, n in sorted(counts.items()):
            cands = [c for c in printings.get(ent, []) if c in frozen_ids]
            if not cands:
                sys.exit(f'{ent}: no printing in the frozen database (payload {pay[:16]}...)')
            pick = sorted(cands, key=lambda c: (-usage[c], release_key(c)))[0]
            choices[ent] = {'picked': pick, 'printings': sorted(cands, key=release_key), 'repo_uses': usage[pick],
                            'why': 'used most in the repo decks' if usage[pick] else 'first released'}
            pairs.append((n, pick))
        lines = journal.list_lines(dec['energy'], pairs)
        back = journal.code_cards(dec['energy'], pairs)
        if sorted(norm_key(k) for k in back['cards']) != sorted(norm_key(k) for k in dec['cards']) or back['energy'] != dec['energy']:
            sys.exit(f'payload {pay[:16]}...: the deck file does not encode back to the filmed code')
        if sum(n for n, _ in pairs) != 20:
            sys.exit(f'payload {pay[:16]}...: {sum(n for n, _ in pairs)} cards, not 20')
        key = 'v2deck_' + hashlib.sha256(pay.encode()).hexdigest()[:10]
        path = os.path.join(a.out, key + '.txt')
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('\n'.join(lines) + '\n')
        with open(path, 'rb') as fh:
            fsha = hashlib.sha256(fh.read()).hexdigest()
        weak = any(s['weak'].get('battle_full20_proven') is False for g in games for s in [g, *g.get('also_from', [])])
        index[key] = {'file': key + '.txt', 'payload': pay, 'payload_sha256': hashlib.sha256(pay.encode()).hexdigest(),
                      'file_sha256': fsha, 'energy': lines[0], 'n_cards': 20,
                      'encodes_back': True, 'games': games, 'printing_choices': choices, 'weak': weak}
        print(f"{key}: {len(games)} game(s), {lines[0]}, encodes back OK{'; WEAK QR (battle_full20_proven=false)' if weak else ''}")
    # two different codes can spell one list (slot order): say so, so a reader never counts them as different lists
    by_content = collections.defaultdict(list)
    for key, v in index.items():
        with open(os.path.join(a.out, v['file']), 'rb') as fh:
            by_content[fh.read()].append(key)
    for keys in by_content.values():
        for k in keys:
            index[k]['same_list_as'] = sorted(x for x in keys if x != k)
    print(f'{len(by_content)} distinct lists')
    import subprocess
    ref_commit = subprocess.run(['git', '-C', REPO, 'rev-parse', a.decks_ref + '^{commit}'], capture_output=True, text=True).stdout.strip()
    json.dump({'what': "exam v2's deck files from the filmed deck codes (make_v2_decks.py); per card, the printing the repo's decks use most, else the first released, among the frozen database's. "
                       "`weak` repeats a source QR file's own flag (battle_full20_proven = false); whether a list counts as exact is the coordinator's ruling (RULINGS.json, PREREG_RUN3 addendum 3), not this flag",
               'decks_ref': a.decks_ref, 'decks_ref_commit': ref_commit,
               'frozen_db_sha256': hashlib.sha256(open(a.frozen_db, 'rb').read()).hexdigest(), 'decks': index},
              open(os.path.join(a.out, 'DECKS.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'{len(index)} deck files from {sum(len(g) for g in payloads.values())} games with a filmed code')


if __name__ == '__main__':
    main()

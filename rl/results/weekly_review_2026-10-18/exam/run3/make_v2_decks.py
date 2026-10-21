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
(e.g. battle_full20_proven = false). Games without a filmed code get no deck file here (they wait for Dustin's exact list)."""
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
    names = subprocess.run(['git', '-C', REPO, 'ls-tree', '-r', '--name-only', ref, 'decks/'], capture_output=True, text=True).stdout.split()
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
    payloads = {}
    for ev in a.evidence:
        for d in sorted(glob.glob(os.path.join(ev, '*'))):
            for f in ('QR_ID.json', 'QR_DECODE.json'):
                p = os.path.join(d, f)
                if os.path.exists(p):
                    q = json.load(open(p, encoding='utf-8-sig'))
                    pay = next((q[k] for k in ('payload', 'qr_payload', 'decoded_payload') if isinstance(q.get(k), str) and q[k]), None)
                    if not pay:
                        sys.exit(f'{p}: no payload')
                    weak = {k: q[k] for k in ('battle_full20_proven', 'unsaved_changes_prompt', 'notes') if k in q}
                    payloads.setdefault(pay, []).append({'packet': os.path.basename(d), 'batch': os.path.basename(ev), 'qr_file': f,
                                                         'schema': q.get('schema'), 'filename': q.get('filename'), 'weak': weak})
                    break
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
        index[key] = {'file': key + '.txt', 'payload': pay, 'payload_sha256': hashlib.sha256(pay.encode()).hexdigest(),
                      'file_sha256': hashlib.sha256(open(path, 'rb').read()).hexdigest(), 'energy': lines[0], 'n_cards': 20,
                      'encodes_back': True, 'games': games, 'printing_choices': choices,
                      'weak': any(g['weak'].get('battle_full20_proven') is False for g in games)}
        print(f"{key}: {len(games)} game(s), {lines[0]}, encodes back OK{'; WEAK QR (battle_full20_proven=false)' if index[key]['weak'] else ''}")
    json.dump({'what': "exam v2's deck files from the filmed deck codes (make_v2_decks.py); per card, the printing the repo's decks use most, else the first released, among the frozen database's",
               'decks_ref': a.decks_ref,
               'frozen_db_sha256': hashlib.sha256(open(a.frozen_db, 'rb').read()).hexdigest(), 'decks': index},
              open(os.path.join(a.out, 'DECKS.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(f'{len(index)} deck files from {sum(len(g) for g in payloads.values())} packets with a filmed code')


if __name__ == '__main__':
    main()

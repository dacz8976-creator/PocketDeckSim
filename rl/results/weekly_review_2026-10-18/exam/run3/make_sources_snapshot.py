#!/usr/bin/env python3
"""Exam v2's sources: a hash-checked snapshot of the accepted review packets of every recording in the window (PREREG_RUN3 section 1; addendum 2, C4),
and the window record the selection check reads.

  make_sources_snapshot.py --evidence DIR [DIR ...] --index BATTLE_REVIEW_INDEX.csv --decks run3/decks/DECKS.json
                           --exact-lists DIR --exact-summary DIR --rulings run3/decks/RULINGS.json
                           [--extra-decks JSON] [--window-start 2026-10-16T03:15:12Z] [--window-end 2026-10-26T04:59:59Z]
                           --out run3/sources --window-out run3/window.json

Read only on the sources. A packet folder's recording start time comes from its name: "ScreenRecording_MM-DD-YYYY_HH-MM-SS" is Chicago local time
(America/Chicago), an iOS name "YYYYMMDD_HHMMSSmmm_iOS" is UTC (both shown by byte-equal twins, laptop-022). In the window means strictly after
--window-start (exam v1.6's last game, 20261016_031512000_iOS) and at or before --window-end (Oct 25, 11:59 PM Central, or Dual Fusion's release).
For each packet in the window:
- acceptance and ranked eligibility from LEAD_ACCEPTANCE.json only (accepted, ladder_eligible, completion_status full_battle_review_complete);
- the exact list (PREREG_RUN3 section 1, addendum 3 D1): a deck file in DECKS.json that this game's filmed code made (matched by drive id,
  so a targeted addendum's QR counts for its game), or a list in the repository matched card for card (--extra-decks {packet name or
  drive id: deck file key}; it must name a deck file, match an in-window packet and agree with any filmed code). A deck that comes from
  a targeted addendum needs --exact-lists and --exact-summary: Codex's addenda are then copied to OUT/<their folder>/ and checked (see
  exact_lists()), each tied to its game by the video's sha256 (the window packet's SOURCE.json and LEAD_ACCEPTANCE). --exact-lists
  needs --rulings: the coordinator's ruling must cover exactly those recordings, with Codex's list letter and the packet's recording
  name, and is attached to the game's record (e.g. 21-57-12's recorded limit);
- one game per recording: a drive id or a video sha256 in two packets stops the run; a clip of a battle recorded in several clips
  (SOURCE.json battle_id / clip_order, or RELATED_SOURCES.json) stops it too, until that case is pre-registered (addendum 3, D6);
- OUT must be empty and WINDOW_OUT new (a stop can leave a partial copy there; nothing is committed after a stop);
- the text files below are copied, and every copied file that some pin names (LEAD_ACCEPTANCE's independent.candidate_sha256, CANDIDATE_FREEZE,
  FIRST_PASS_FREEZE, independent/VERIFICATION.json: any path -> sha256 pair in them) must equal a pinned hash; REVIEW.md must be pinned. A mismatch stops.
- its status: "in", or "excluded" with the written reason (no accepted full review; not ranked; no exact list).
Every review-index row whose recording time is in the window but that no packet folder matches is listed too, for the selection check."""
import argparse, csv, datetime, hashlib, json, os, re, shutil, sys
from zoneinfo import ZoneInfo

TEXT = ['REVIEW.md', 'LEAD_ACCEPTANCE.json', 'LADDER_ENTRY.json', 'LADDER_SAVED.json', 'QR_ID.json', 'QR_DECODE.json', 'UNCERTAINTIES.json', 'SOURCE.json',
        'FINDINGS.json', 'COVERAGE.md', 'CANDIDATE_FREEZE.json', 'FIRST_PASS_FREEZE.json', 'REVIEW_METRICS.json', 'NATIVE_EVIDENCE.json', 'READY.json',
        'ROOT_TEXT_CORRECTION.json', 'independent/VERIFICATION.json']
PIN_FILES = ['LEAD_ACCEPTANCE.json', 'CANDIDATE_FREEZE.json', 'FIRST_PASS_FREEZE.json', 'independent/VERIFICATION.json']
# owner rulings about recordings outside the packets, recorded as given (coordinator-023, Oct 21)
NOTES = ['Oct 18 .MOV: not a game (owner confirmed)']
# Codex's targeted QR addenda (coordinator-024): per recording, and the summary folder
EXACT_TEXT = ['QR_DECODE.json', 'BINDING.json', 'LEAD_ACCEPTANCE.json', 'INDEPENDENT.json', 'ADDENDUM.md', 'REVIEW.md', 'SOURCE.json']
EXACT_SUMMARY = ['EXACT_DECKS.json', 'EXACT_DECK_LISTS.md', 'BINDINGS.json', 'FINAL_VERIFICATION.json', 'SUMMARY_DRIVE_VERIFICATION.json',
                 'ASSIGNMENT.json']
# the Drive copies Dustin linked (coordinator-024): lists and structured data
DRIVE_LINKED = {'EXACT_DECK_LISTS.md': '1EKXHFo7Y_3oz5SFQT7ED6NzLPK9AE7PQ', 'EXACT_DECKS.json': '1fbbF2uvx_tgTg5xl_WpxaENKokJRlhQt'}
SR = re.compile(r'ScreenRecording_(\d{2})-(\d{2})-(\d{4})[ _](\d{2})-(\d{2})-(\d{2})')
IOS = re.compile(r'(\d{8})_(\d{6})(\d{3})_iOS')
HEX = re.compile(r'^[0-9a-f]{64}$')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def start_utc(name):
    m = SR.search(name)
    if m:
        mo, d, y, hh, mi, ss = map(int, m.groups())
        return datetime.datetime(y, mo, d, hh, mi, ss, tzinfo=ZoneInfo('America/Chicago')).astimezone(datetime.timezone.utc)
    m = IOS.search(name)
    if m:
        return datetime.datetime.strptime(m.group(1) + m.group(2), '%Y%m%d%H%M%S').replace(tzinfo=datetime.timezone.utc)
    return None


def pins_of(packet):
    """{relative path: set of pinned sha256} from every pin file, walking any {path, sha256} pair or {filename: sha256} map."""
    pins = {}

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get('path'), str) and isinstance(o.get('sha256'), str) and HEX.match(o['sha256']):
                pins.setdefault(o['path'], set()).add(o['sha256'])
            for k, v in o.items():
                if isinstance(v, str) and HEX.match(v) and ('.' in k and '/' not in k[:1]):
                    pins.setdefault(k, set()).add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for f in PIN_FILES:
        p = os.path.join(packet, f)
        if os.path.exists(p):
            walk(json.load(open(p, encoding='utf-8-sig')))
    return pins


def load(p):
    with open(p, encoding='utf-8-sig') as f:
        return json.load(f)


def md5(p):
    with open(p, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def drive_of(name):
    return name.split('_ScreenRecording')[0]


def exact_lists(exact_dir, summary_dir, out_dir):
    """Codex's targeted QR addenda (coordinator-024): {drive id: record}, their text copied to OUT/<folder>/; stops on any mismatch
    (a stop can leave part of the copy behind in OUT: the real run is in a git worktree, and nothing is committed after a stop).
    Their text files carry no sha256 pin of their own, so they are checked against each other and against the reviewed packet:
    - SUMMARY_DRIVE_VERIFICATION.json must hold exactly the two files Dustin linked, under the Drive ids coordinator-024 gives
      (DRIVE_LINKED), marked verified, and the local EXACT_DECKS.json and EXACT_DECK_LISTS.md must have the md5 and size Codex
      recorded there for those Drive copies;
    - the recording folders must be exactly EXACT_DECKS.json's recordings (as many as its total_recordings);
    - per recording: the folder name is QR_DECODE's drive_file_id; QR_DECODE's payload equals EXACT_DECKS's; the video sha256 in
      QR_DECODE, LEAD_ACCEPTANCE, SOURCE and EXACT_DECKS is one value (main checks it against the window packet's own SOURCE.json and
      LEAD_ACCEPTANCE); BINDING.json equals BINDINGS.json's entry; the QR image's sha256 equals evidence/QR_NATIVE.jpg's."""
    folder = os.path.basename(exact_dir.rstrip('/'))
    root = os.path.join(out_dir, folder)
    summary = {}
    sdv = load(os.path.join(summary_dir, 'SUMMARY_DRIVE_VERIFICATION.json'))
    if sorted(e.get('file') for e in sdv) != sorted(DRIVE_LINKED):
        sys.exit(f"SUMMARY_DRIVE_VERIFICATION.json lists {sorted(str(e.get('file')) for e in sdv)}, not exactly {sorted(DRIVE_LINKED)}: stop")
    for e in sdv:
        p = os.path.join(summary_dir, e['file'])
        if e.get('drive_id') != DRIVE_LINKED[e['file']] or e.get('verified') is not True:
            sys.exit(f"{e['file']}: Drive id {e.get('drive_id')} (verified {e.get('verified')}) is not the copy Dustin linked ({DRIVE_LINKED[e['file']]}): stop")
        if md5(p) != e['md5'] or os.path.getsize(p) != e['bytes']:
            sys.exit(f"{p}: md5/size differ from those Codex recorded for the Drive copy Dustin linked: stop")
    for f in EXACT_SUMMARY:
        p = os.path.join(summary_dir, f)
        os.makedirs(os.path.join(root, '_summary'), exist_ok=True)
        shutil.copyfile(p, os.path.join(root, '_summary', f))
        summary[f] = sha(p)
    ed = load(os.path.join(summary_dir, 'EXACT_DECKS.json'))
    binds = load(os.path.join(summary_dir, 'BINDINGS.json'))
    recs = {r['drive_file_id']: r for r in ed['recordings']}
    folders = sorted(d for d in os.listdir(exact_dir) if os.path.isdir(os.path.join(exact_dir, d)))
    if len(recs) != len(ed['recordings']) or len(recs) != ed.get('total_recordings') or set(folders) != set(recs):
        sys.exit(f"{folder}: the recording folders {len(folders)} are not exactly EXACT_DECKS.json's {len(recs)} recordings "
                 f"(total_recordings {ed.get('total_recordings')}; missing {sorted(set(recs) - set(folders))}, extra {sorted(set(folders) - set(recs))}): stop")
    out = {}
    for d in folders:
        p = os.path.join(exact_dir, d)
        bad = lambda why: sys.exit(f'{folder}/{d}: {why}: stop')
        q, la, bd, src = (load(os.path.join(p, f)) for f in ('QR_DECODE.json', 'LEAD_ACCEPTANCE.json', 'BINDING.json', 'SOURCE.json'))
        r = recs[d]
        if q.get('drive_file_id') != d:
            bad(f"QR_DECODE's drive_file_id is {q.get('drive_file_id')}")
        if la.get('accepted') is not True:
            bad('its LEAD_ACCEPTANCE is not accepted')
        if q.get('payload') != r.get('payload'):
            bad("QR_DECODE's payload is not EXACT_DECKS's")
        vids = {q.get('source_sha256'), la.get('source_sha256'), r.get('source_sha256'), src.get('sha256')}
        if len(vids) != 1 or None in vids:
            bad(f'the video sha256 differs between QR_DECODE, LEAD_ACCEPTANCE, EXACT_DECKS and SOURCE: {sorted(str(v)[:10] for v in vids)}')
        if bd != binds.get(str(r['number'])):
            bad("BINDING.json is not BINDINGS.json's entry")
        nat = os.path.join(p, 'evidence', 'QR_NATIVE.jpg')
        if not os.path.exists(nat) or sha(nat) != q.get('image_sha256'):
            bad("the QR image's sha256 is not evidence/QR_NATIVE.jpg's")
        files = {}
        for f in EXACT_TEXT:
            s = os.path.join(p, f)
            if os.path.exists(s):
                os.makedirs(os.path.join(root, d), exist_ok=True)
                shutil.copyfile(s, os.path.join(root, d, f))
                files[f] = sha(s)
        out[d] = {'folder': f'{folder}/{d}', 'list_id': r.get('list_id'), 'payload': q['payload'], 'video_sha256': q['source_sha256'],
                  'qr_image_sha256': q['image_sha256'], 'binding_limits': bd.get('limits'), 'files': files,
                  'checks': "folder = drive_file_id; payload = EXACT_DECKS's; video sha256 = LEAD_ACCEPTANCE = EXACT_DECKS = SOURCE.json = the reviewed "
                            "packet's SOURCE.json and LEAD_ACCEPTANCE; BINDING = BINDINGS entry; QR image = QR_NATIVE.jpg; summary md5/size = "
                            "Codex's record of the two Drive copies Dustin linked"}
    return {'folder': folder, 'summary_files': summary, 'game_use_limit': ed.get('game_use_limit'),
            'identity_limit': ed.get('identity_limit')}, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', nargs='+', required=True)
    ap.add_argument('--index', required=True)
    ap.add_argument('--decks', required=True)
    ap.add_argument('--extra-decks')
    # required for run 3 (addendum 3): a run without them would record the six Oct 16-17 games as having no exact list
    ap.add_argument('--exact-lists', required=True, help="Codex's targeted QR addenda (BattleLogsData/Evidence/QR_EXACT_LISTS_2026-10-21)")
    ap.add_argument('--exact-summary', required=True, help='their summary folder (Battle Logs/Recording_QA/QR_EXACT_LISTS_2026-10-21)')
    ap.add_argument('--rulings', required=True, help='run3/decks/RULINGS.json: the coordinator\'s deck-list rulings, attached per game')
    ap.add_argument('--window-start', default='2026-10-16T03:15:12Z')
    ap.add_argument('--window-end', default='2026-10-26T04:59:59Z')
    ap.add_argument('--out', required=True)
    ap.add_argument('--window-out', required=True)
    a = ap.parse_args()
    if (os.path.exists(a.out) and os.listdir(a.out)) or os.path.exists(a.window_out):
        sys.exit(f'{a.out} is not empty or {a.window_out} exists: the snapshot is written into a fresh place only')
    ws = datetime.datetime.fromisoformat(a.window_start.replace('Z', '+00:00'))
    we = datetime.datetime.fromisoformat(a.window_end.replace('Z', '+00:00'))
    decks = load(a.decks)['decks']
    by_drive, game_of = {}, {}
    for k, v in decks.items():
        for g in v['games']:
            dr = g.get('drive_id') or drive_of(g['packet'])
            if dr in by_drive:
                sys.exit(f'{a.decks}: game {dr} is listed under two deck files ({by_drive[dr]}, {k}): stop')
            by_drive[dr], game_of[dr] = k, g
    # --extra-decks {packet name or drive id: deck file key}: a list in the repository matched card for card to the game (section 1)
    extra = load(a.extra_decks) if a.extra_decks else {}
    for k, v in extra.items():
        if v not in decks:
            sys.exit(f'--extra-decks: {k} -> {v}: no such deck file in {a.decks}: stop')
        fp = os.path.join(os.path.dirname(os.path.abspath(a.decks)), decks[v].get('file', ''))
        if not os.path.isfile(fp) or sha(fp) != decks[v].get('file_sha256'):
            sys.exit(f'--extra-decks: {k} -> {v}: its file is missing or not the one DECKS.json records: stop')
    exact_meta, exact = exact_lists(a.exact_lists, a.exact_summary, a.out)
    rulings = load(a.rulings)
    rg = rulings.get('games', {})
    if set(rg) != set(exact):
        sys.exit(f'{a.rulings}: its games are not exactly the exact-list recordings (missing {sorted(set(exact) - set(rg))}, '
                 f'extra {sorted(set(rg) - set(exact))}): stop')
    for dr, ru in rg.items():
        if ru.get('exact') is not True or ru.get('codex_list') != exact[dr]['list_id']:
            sys.exit(f"{a.rulings}: {dr}: exact {ru.get('exact')}, list {ru.get('codex_list')} v Codex's {exact[dr]['list_id']}: stop")
    # coordinator-024 records one limit (21-57-12's): it sits on exactly one game, in the words the ruling quotes
    lims = [(dr, ru['limit']) for dr, ru in rg.items() if ru.get('limit')]
    if len(lims) != 1 or any(f'"{lim}"' not in rulings.get('ruling_verbatim', '') for _, lim in lims):
        sys.exit(f'{a.rulings}: the recorded limit must be the one the ruling quotes, on one game (found {len(lims)}): stop')
    used_extra, rec, seen_names = set(), [], set()
    for ev in a.evidence:
        for name in sorted(os.listdir(ev)):
            d = os.path.join(ev, name)
            if not os.path.isdir(d):
                continue
            t = start_utc(name)
            if t is None or not (ws < t <= we):
                continue
            seen_names.add(SR.search(name).group(0) if SR.search(name) else name)
            dr = drive_of(name)
            r = {'packet': name, 'drive_id': dr, 'batch': os.path.basename(ev), 'start_utc': t.strftime('%Y-%m-%dT%H:%M:%SZ'), 'files': {}}
            la_p = os.path.join(d, 'LEAD_ACCEPTANCE.json')
            la = load(la_p) if os.path.exists(la_p) else {}
            full = la.get('accepted') is True and la.get('completion_status') == 'full_battle_review_complete'
            ranked = la.get('ladder_eligible') is True
            src_p = os.path.join(d, 'SOURCE.json')
            src = load(src_p) if os.path.exists(src_p) else {}
            # one battle recorded in several clips: how it counts (one game? which clip?) is not pre-registered yet (laptop-023), so stop
            if src.get('battle_id') or src.get('clip_order') or os.path.exists(os.path.join(d, 'RELATED_SOURCES.json')):
                sys.exit(f"{name}: a clip of a linked battle (battle_id {src.get('battle_id')}, clip {src.get('clip_order')}, "
                         f"RELATED_SOURCES.json {os.path.exists(os.path.join(d, 'RELATED_SOURCES.json'))}): the rule for a battle across "
                         f"several recordings is pending (PREREG_RUN3 addendum 3, D6): stop")
            r['video_sha256'] = src.get('sha256') or la.get('source_sha256')
            ek = name if name in extra else (dr if dr in extra else None)
            if ek:
                used_extra.add(ek)
            g = game_of.get(dr)
            filmed = by_drive.get(dr)
            deck = extra[ek] if ek else filmed
            if ek and filmed and decks[extra[ek]]['payload'] != decks[filmed]['payload']:
                sys.exit(f'{name}: --extra-decks gives {extra[ek]}, but its filmed code made {filmed}: two lists for one game: stop')
            r.update(accepted_full_review=full, ranked=ranked, deck=deck,
                     deck_source=(f"filmed code ({g['batch']}/{g['packet']}/{g['qr_file']}"
                                  + ''.join(f"; also {s['batch']}/{s['packet']}/{s['qr_file']}" for s in g.get('also_from', [])) + ')')
                     if g else ('a repository list matched card for card (--extra-decks)' if ek else None))
            # a deck from a targeted addendum (a folder named by the drive id alone) counts only with that addendum checked here
            if g and any('_ScreenRecording' not in s['packet'] for s in [g, *g.get('also_from', [])]) and dr not in exact:
                sys.exit(f'{name}: its deck {filmed} comes from a targeted addendum; pass --exact-lists and --exact-summary so it is checked: stop')
            x = exact.get(dr)
            if x:
                if not deck:
                    sys.exit(f'{name}: has an exact-list packet ({x["folder"]}) but no deck file: rebuild DECKS.json with that folder: stop')
                if src.get('sha256') != x['video_sha256'] or la.get('source_sha256') != x['video_sha256']:
                    sys.exit(f"{name}: the exact-list packet {x['folder']} is for another video ({x['video_sha256'][:10]} v "
                             f"SOURCE {str(r['video_sha256'])[:10]}, LEAD_ACCEPTANCE {str(la.get('source_sha256'))[:10]}): stop")
                if decks[deck]['payload'] != x['payload']:
                    sys.exit(f"{name}: its deck file {deck} is not the exact-list QR's code: stop")
                r['exact_list'] = {k: v for k, v in x.items() if k != 'payload'}
            if dr in rulings.get('games', {}):
                ru = rulings['games'][dr]
                m = SR.search(name)
                if not m or ru.get('recording', '').replace(' ', '_') != m.group(0).replace(' ', '_'):
                    sys.exit(f"{a.rulings}: {dr}'s recording {ru.get('recording')} is not this packet's ({name}): stop")
                r['deck_ruling'] = dict(ru, ruling=rulings.get('ruling_ref'))
            if not full:
                r['status'], r['reason'] = 'excluded', 'no accepted full review (LEAD_ACCEPTANCE.json)'
            elif not ranked:
                r['status'], r['reason'] = 'excluded', 'not ranked (LEAD_ACCEPTANCE.json ladder_eligible is not true)'
            elif not deck:
                r['status'], r['reason'] = 'excluded', 'no exact deck list (no filmed code, no repository list matched)'
            else:
                r['status'] = 'in'
            pins = pins_of(d)
            if 'REVIEW.md' not in pins:
                sys.exit(f'{name}: REVIEW.md is pinned nowhere')
            dst = os.path.join(a.out, name)
            for f in TEXT:
                src = os.path.join(d, f)
                if not os.path.exists(src):
                    continue
                h = sha(src)
                if f in pins and h not in pins[f]:
                    sys.exit(f'{name}/{f}: sha256 {h[:12]} is not the pinned one ({sorted(x[:12] for x in pins[f])}): stop')
                os.makedirs(os.path.dirname(os.path.join(dst, f)), exist_ok=True)
                shutil.copyfile(src, os.path.join(dst, f))
                r['files'][f] = {'sha256': h, 'pinned': f in pins}
            rec.append(r)
    stray = []
    with open(a.index, encoding='utf-8-sig', newline='') as fh:
        for row in csv.DictReader(fh):
            t = start_utc(row.get('Video', ''))
            if t and ws < t <= we:
                key = SR.search(row['Video']).group(0).replace(' ', '_') if SR.search(row['Video']) else row['Video']
                if not any(key.replace('_', ' ') in n.replace('_', ' ') for n in seen_names):
                    # a camera .MOV is never named here (owner ruling, coordinator-023); his games are screen recordings
                    video = '(a .MOV, name withheld)' if row['Video'].lower().endswith('.mov') else row['Video']
                    stray.append({'video': video, 'status': row.get('Status'), 'start_utc': t.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                  'note': 'in the review index, no packet folder in the given evidence directories'})
    unused = sorted(set(exact) - {r['drive_id'] for r in rec})
    if unused:
        sys.exit(f'exact-list packets for no game in the window: {unused}: stop')
    if set(extra) - used_extra:
        sys.exit(f'--extra-decks keys that match no packet in the window: {sorted(set(extra) - used_extra)}: stop')
    # one game per recording: a packet twice (two batches), or one video under two names (byte-equal twins), would count its points twice
    for key in ('drive_id', 'video_sha256'):
        seen = {}
        for r in rec:
            v = r.get(key)
            if v is None:
                continue
            if v in seen:
                sys.exit(f"{key} {str(v)[:16]} is in two packets ({seen[v]}, {r['batch']}/{r['packet']}): one game counted twice: stop")
            seen[v] = f"{r['batch']}/{r['packet']}"
    out = {'what': "exam v2's window record (make_sources_snapshot.py); sources copied to run3/sources/<packet>/, hash-checked against the packets' pins",
           'window_start_exclusive': a.window_start, 'window_end_inclusive': a.window_end, 'evidence': a.evidence,
           'exact_lists': exact_meta, 'rulings': {'file': a.rulings, 'sha256': sha(a.rulings)},
           'packets': rec, 'index_rows_without_packet': stray, 'notes': NOTES,
           'counts': {'in_window': len(rec), 'in': sum(r['status'] == 'in' for r in rec), 'excluded': sum(r['status'] == 'excluded' for r in rec)}}
    with open(a.window_out, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps(out['counts']), '| index rows without a packet:', len(stray), '| exact-list packets:', len(exact))
    for r in rec:
        print(f"{r['start_utc']} {r['status']:8s} {r.get('deck') or '-':18s} {r['packet'][:60]} {r.get('reason', '')}"
              f"{' [exact list ' + str(r['exact_list']['list_id']) + ']' if r.get('exact_list') else ''}{' [ruling]' if r.get('deck_ruling') else ''}")


if __name__ == '__main__':
    main()

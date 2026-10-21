#!/usr/bin/env python3
"""Exam v2's sources: a hash-checked snapshot of the accepted review packets of every recording in the window (PREREG_RUN3 section 1; addendum 2, C4),
and the window record the selection check reads.

  make_sources_snapshot.py --evidence DIR [DIR ...] --index BATTLE_REVIEW_INDEX.csv --decks run3/decks/DECKS.json
                           [--extra-decks JSON] [--window-start 2026-10-16T03:15:12Z] [--window-end 2026-10-26T04:59:59Z]
                           --out run3/sources --window-out run3/window.json

Read only on the sources. A packet folder's recording start time comes from its name: "ScreenRecording_MM-DD-YYYY_HH-MM-SS" is Chicago local time
(America/Chicago), an iOS name "YYYYMMDD_HHMMSSmmm_iOS" is UTC (both shown by byte-equal twins, laptop-022). In the window means strictly after
--window-start (exam v1.6's last game, 20261016_031512000_iOS) and at or before --window-end (Oct 25, 11:59 PM Central, or Dual Fusion's release).
For each packet in the window:
- acceptance and ranked eligibility from LEAD_ACCEPTANCE.json only (accepted, ladder_eligible, completion_status full_battle_review_complete);
- the exact list: a deck file in DECKS.json that this packet's filmed code made, or one Dustin confirmed (--extra-decks {packet: deck file});
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', nargs='+', required=True)
    ap.add_argument('--index', required=True)
    ap.add_argument('--decks', required=True)
    ap.add_argument('--extra-decks')
    ap.add_argument('--window-start', default='2026-10-16T03:15:12Z')
    ap.add_argument('--window-end', default='2026-10-26T04:59:59Z')
    ap.add_argument('--out', required=True)
    ap.add_argument('--window-out', required=True)
    a = ap.parse_args()
    ws = datetime.datetime.fromisoformat(a.window_start.replace('Z', '+00:00'))
    we = datetime.datetime.fromisoformat(a.window_end.replace('Z', '+00:00'))
    decks = json.load(open(a.decks, encoding='utf-8'))['decks']
    by_packet = {g['packet']: k for k, v in decks.items() for g in v['games']}
    extra = json.load(open(a.extra_decks)) if a.extra_decks else {}
    rec, seen_names = [], set()
    for ev in a.evidence:
        for name in sorted(os.listdir(ev)):
            d = os.path.join(ev, name)
            if not os.path.isdir(d):
                continue
            t = start_utc(name)
            if t is None or not (ws < t <= we):
                continue
            seen_names.add(SR.search(name).group(0) if SR.search(name) else name)
            r = {'packet': name, 'batch': os.path.basename(ev), 'start_utc': t.strftime('%Y-%m-%dT%H:%M:%SZ'), 'files': {}}
            la_p = os.path.join(d, 'LEAD_ACCEPTANCE.json')
            la = json.load(open(la_p, encoding='utf-8-sig')) if os.path.exists(la_p) else {}
            full = la.get('accepted') is True and la.get('completion_status') == 'full_battle_review_complete'
            ranked = la.get('ladder_eligible') is True
            deck = extra.get(name) or by_packet.get(name)
            r.update(accepted_full_review=full, ranked=ranked, deck=deck,
                     deck_source='filmed code (DECKS.json)' if by_packet.get(name) else ('Dustin-confirmed list' if extra.get(name) else None))
            if not full:
                r['status'], r['reason'] = 'excluded', 'no accepted full review (LEAD_ACCEPTANCE.json)'
            elif not ranked:
                r['status'], r['reason'] = 'excluded', 'not ranked (LEAD_ACCEPTANCE.json ladder_eligible is not true)'
            elif not deck:
                r['status'], r['reason'] = 'excluded', 'no exact deck list (no filmed code, no confirmed list)'
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
                    stray.append({'video': row['Video'], 'status': row.get('Status'), 'start_utc': t.strftime('%Y-%m-%dT%H:%M:%SZ'),
                                  'note': 'in the review index, no packet folder in the given evidence directories'})
    out = {'what': "exam v2's window record (make_sources_snapshot.py); sources copied to run3/sources/<packet>/, hash-checked against the packets' pins",
           'window_start_exclusive': a.window_start, 'window_end_inclusive': a.window_end, 'evidence': a.evidence,
           'packets': rec, 'index_rows_without_packet': stray,
           'counts': {'in_window': len(rec), 'in': sum(r['status'] == 'in' for r in rec), 'excluded': sum(r['status'] == 'excluded' for r in rec)}}
    json.dump(out, open(a.window_out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps(out['counts']), '| index rows without a packet:', len(stray))
    for r in rec:
        print(f"{r['start_utc']} {r['status']:8s} {r.get('deck') or '-':18s} {r['packet'][:60]} {r.get('reason', '')}")


if __name__ == '__main__':
    main()

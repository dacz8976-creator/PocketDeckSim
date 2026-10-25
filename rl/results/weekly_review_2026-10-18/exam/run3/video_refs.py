"""The video reference of each question's turn: the recording's filename as Dustin knows it (the review index's 'Video' name), the time the
turn starts in that file, and the clip (null for a one-recording game). The time is the earliest start among the review's own turn labels for
that global turn: a table row whose leading cells name the turn, a heading's "(globalN", or a bullet/bold line that opens with "Global N".
A turn named only in running text gets null. Metadata and the review's time stamps only."""
import csv, json, os, re, sys
E2 = '/home/dacz8976/exam_v2'
W = json.load(open('/home/dacz8976/exam_034_w/rl/results/weekly_review_2026-10-18/exam/run3/window.json', encoding='utf-8'))
IDX = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/BATTLE_REVIEW_INDEX.csv'
videos = {r['Video'] for r in csv.DictReader(open(IDX, encoding='utf-8-sig', newline=''))}
sel = {c['point_id']: c for c in json.load(open(f'{E2}/select/selection.json'))['candidates']}
# A linked battle's one review names its recordings by source; checked by hand. 004518: source2 opens on the QR at 0.0s and holds turns 1-11,
# source1 has no QR and opens at 2-2, so source2 is clip 1 (19-45-18, start 00:45:18Z) and source1 is clip 2 (19-51-08).
SOURCE_OF_CLIP = {('20261022_004518000_SR', 1): 'source2', ('20261022_004518000_SR', 2): 'source1'}
NUM = r'\d{1,4}(?:\.\d+)?'
RANGE = rf'({NUM})\s*s?\s*[-–]\s*({NUM})\s*s?'
PURE = re.compile(rf'(?i)(?:approximately\s*|about\s*|~)?{RANGE}(?:\s*seconds)?')
TURN_CELL = re.compile(r'(?i)^(?:global\s*(?:turn\s*)?|T)?(\d{1,2})(?![\d.\-–])(?:\b|/|,|$)')
LEAD = re.compile(rf'(?i)^(?:global\s*(?:turn\s*)?)(\d{{1,2}})(?!\d)[^:|]{{0,60}}?{RANGE}')
HEAD_LEAD = re.compile(rf'(?i)^(?:global\s*(?:turn\s*)?)(\d{{1,2}})(?!\d)[^:]{{0,60}}?{RANGE}')
HEAD_RANGE = re.compile(rf'(?i)^{RANGE}\s*:?[^(]{{0,30}}?\(?\s*global\s*(?:turn\s*)?(\d{{1,2}})(?!\d)')


def packet_of(game):
    from_id = lambda r: '{}{}{}_{}{}{}000_SR'.format(*re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z', r['start_utc']).groups())
    return next(r for r in W['packets'] if from_id(r) == game)


def file_name(packet, drive):
    rest = packet[len(drive) + 1:]
    return re.sub(r'(ScreenRecording_\d{2}-\d{2}-\d{4})_(\d{2}-\d{2}-\d{2})', r'\1 \2', rest)


def labels(review):
    """(turn, start seconds, source tag or None, line) for each turn label in the review."""
    out = []
    for l in review.splitlines():
        s = l.strip()
        if s.startswith('|'):
            cells = [c.strip() for c in s.strip('|').split('|')]
            if len(cells) < 2 or set(cells[0]) <= set('-: '):
                continue
            turn = start = src = None
            for c in cells[:3]:
                if start is None and PURE.fullmatch(c):
                    start = float(PURE.fullmatch(c).group(1))
                    continue
                m = TURN_CELL.match(c)
                if turn is None and m:
                    turn = int(m.group(1))
                    inner = re.search(rf'(?i)(source\s*\d+)?\s*{RANGE}', c[m.end():])
                    if inner and start is None:
                        start, src = float(inner.group(2)), (inner.group(1) or '').replace(' ', '').lower() or None
            if turn is not None and start is not None:
                out.append((turn, start, src, s))
        elif s.startswith('#'):
            t = s.lstrip('#').strip()
            m, r = HEAD_LEAD.match(t), HEAD_RANGE.match(t)
            if m:
                out.append((int(m.group(1)), float(m.group(2)), None, s))
            elif r:
                out.append((int(r.group(3)), float(r.group(1)), None, s))
        else:
            t = re.sub(r'^[-*\s]+', '', s)
            m = LEAD.match(t)
            if m:
                out.append((int(m.group(1)), float(m.group(2)), None, s))
    return out


def mmss(t):
    return None if t is None else f'{int(t) // 60}:{int(t) % 60:02d}'


def ref(pid):
    c = sel[pid]
    r = packet_of(c['game'])
    if r.get('clips'):
        k = c['clip']
        cl = next(x for x in r['clips'] if x['clip_order'] == k)
        packet, drive = cl['packet'], cl['drive_id']
        folder = next(f for f in os.listdir(c['folder']) if f.startswith(f'clip{k:02d}_'))
        path = f"{c['folder']}/{folder}/REVIEW.md"
    else:
        k = None
        packet, drive = r['packet'], r['drive_id']
        path = f"{c['folder']}/REVIEW.md"
    hits = [x for x in labels(open(path, encoding='utf-8', errors='replace').read()) if x[0] == c['global_turn']]
    if k is not None:
        if any(x[2] is None for x in hits) or SOURCE_OF_CLIP.get((c['game'], k)) is None:
            raise SystemExit(f'{pid}: a linked battle needs labels that name their source, and that source checked by hand')
        hits = [x for x in hits if x[2] == SOURCE_OF_CLIP[(c['game'], k)]]
    elif any(x[2] for x in hits):
        raise SystemExit(f'{pid}: a source named in a one-recording game')
    first = min(hits, key=lambda x: x[1]) if hits else None
    name = file_name(packet, drive)
    return {'file': name, 'at': mmss(first[1]) if first else None, 'clip': k}, name in videos, first, hits


if __name__ == '__main__':
    Q = json.load(open(f'{E2}/questions/QUESTIONS.json', encoding='utf-8'))
    pids = [q['point_id'] for q in Q['questions']] + [x['point_id'] for q in Q['questions'] for x in q.get('also_applies_to') or []]
    for pid in pids:
        v, known, first, hits = ref(pid)
        print(pid, json.dumps(v, ensure_ascii=False), '' if known else 'FILE NOT IN INDEX', f'labels={len(hits)}')
        if first:
            print('     src', first[2], '|', first[3][:150])

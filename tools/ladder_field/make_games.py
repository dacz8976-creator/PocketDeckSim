"""Step A: the Ladder Log's games, each linked to its Codex review (REVIEW.md) when one exists."""
import json, glob, os, sys, csv, re, datetime, collections
logs_dir, index_csv, out = sys.argv[1], sys.argv[2], sys.argv[3]

def wsl2win(p):
    p = p.strip()
    m = re.match(r'/mnt/([a-z])/(.*)', p)
    return (m.group(1).upper() + ':/' + m.group(2)) if m else p

idx = list(csv.DictReader(open(index_csv, encoding='utf-8-sig', newline='')))
by_video = {}
for r in idx:
    paths = [wsl2win(p) for p in r['Review evidence'].split('|') if p.strip()]
    rev = [p for p in paths if p.endswith('REVIEW.md') and os.path.exists(p)]
    by_video[r['Video']] = {'review': rev[0] if rev else None, 'dir': os.path.dirname(rev[0]) if rev else None,
                            'scope': r['Review scope'][:300], 'status': r['Status']}
# only recording names long enough to be unique (a test clip named "T2.MP4" matched "T2" in many notes)
vids = sorted((v for v in by_video if len(os.path.splitext(v)[0]) >= 10), key=len, reverse=True)

def norm_vid(s):
    return re.sub(r'[\s_]+', '', s.lower())
nv = {norm_vid(v): v for v in vids}

games = []
for f in sorted(glob.glob(os.path.join(logs_dir, '*.json'))):
    doc = json.load(open(f, encoding='utf-8'))
    doc = doc.get('data', doc)
    deck = os.path.splitext(os.path.basename(f))[0]
    for g in doc.get('games', []) or []:
        ts = g.get('ts')
        t = datetime.datetime.fromtimestamp(ts / 1000, datetime.timezone.utc) if ts else None
        note = str(g.get('note', ''))
        found = []
        for v in vids:
            stem = os.path.splitext(v)[0]
            if v in note or stem in note:
                found.append(v)
        if not found:
            nn = norm_vid(note)
            found = [nv[k] for k in nv if os.path.splitext(k)[0] and os.path.splitext(k)[0] in nn]
        # drop names contained in a longer found name
        found = [v for v in found if not any(v != w and os.path.splitext(v)[0] in w for w in found)]
        revs = [by_video[v] for v in found if by_video[v]['review']]
        games.append({'game_key': f'{deck}#{g.get("id")}', 'deck_id': deck, 'deck_name': doc.get('name', ''),
                      'ladder_id': g.get('id'), 'ts': ts, 'utc': t.isoformat() if t else None,
                      'result': g.get('result'), 'opp': g.get('opp'), 'note': note,
                      'videos': found, 'reviews': [r['review'] for r in revs], 'review_dirs': [r['dir'] for r in revs]})
games.sort(key=lambda x: x['ts'] or 0)
for i, g in enumerate(games, 1):
    g['n'] = i
json.dump(games, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
c = collections.Counter(len(g['reviews']) for g in games)
print('games', len(games), '| reviews linked per game:', dict(c))
by_month = collections.Counter((g['utc'] or '?')[:7] + ('+rev' if g['reviews'] else '-norev') for g in games)
print(sorted(by_month.items()))
print('sample unlinked:', [(g['utc'][:10], g['deck_id'], g['note'][:90]) for g in games if not g['reviews']][:5])

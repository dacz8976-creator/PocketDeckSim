#!/usr/bin/env python3
"""build.py: in-game deck import codes (QR) for the seven decks of Dustin's ladder sheet, checked, and the page that shows them.

  /home/dacz8976/qrenv/bin/python rl/results/ladder_qr_page_2026-10-14/build.py [--pause-decks DIR] [--html OUT.html]
  deps: qrcode, pillow, numpy, zxing-cpp (a venv outside the repository; lib/encode_qr.py and lib/decode_qr.py name the same ones)

For each deck (the exact tested list: the deck file as committed on main; the slow report's manifest.json gives the file and its SHA-256):
  1. the file's SHA-256 is the one in the report's manifest (both places it is written);
  2. lib/encode_qr.py writes the game's code (`parse` checks every name against the card catalog and the count of 20);
  3. the code is decoded again here, by the documented byte layout and NOT by the encoder, and compared with the deck file card for card: the same cards and counts
     (by the entity the code names), the same Energy bytes, and every printing the deck file lists is a printing of the entity the code names;
  4. the QR image is read back (zxing-cpp): the PNG lib/encode_qr.py writes, and the SVG that goes on the page, rebuilt from its own path text;
  5. against codes that already exist: the Pause Games `pause_decks` documents (--pause-decks, a folder of their JSON files, saved with the ArtifactData tool) and the QR images in decks/brews.
The page (a self-contained HTML file) is written last, from the results, and its QR codes are read back out of the finished file.
Exit 1 when any check fails."""
import argparse, base64, collections, glob, hashlib, html, io, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'lib'))
import encode_qr as E          # noqa: E402
import numpy as np             # noqa: E402
import qrcode                  # noqa: E402
import zxingcpp                # noqa: E402
from PIL import Image          # noqa: E402

DECKS = [
    dict(key='brew-07', group='Shortlist', label='Brew 07', title='Hoopa, Darkrai and Sableye', file='decks/brews/brew-07-hoopa-darkrai-sableye.txt',
         report='2026-10-12_brew-07-hoopa-darkrai-sableye', pg=['b07'], png='decks/brews/brew-07-hoopa-darkrai-sableye.png',
         blurb='Hoopa ex, Darkrai ex and Mega Sableye ex, with Deceptive Needle, Lucky Ice Pop and Starting Plains.'),
    dict(key='deck-12', group='Shortlist', label='Deck 12', title='Ariados, Whimsicott and Ogerpon', file='decks/dustin/12-ariados-whimsicott-ogerpon.txt',
         report='2026-10-13_12-ariados-whimsicott-ogerpon', pg=[], png=None,
         blurb='Ariados and Whimsicott ex with Teal Mask Ogerpon ex, Team Rocket\'s Goo-zooka and Quick-Grow Extract.'),
    dict(key='deck-13a', group='Shortlist', label='Deck 13-a', title='Alolan Ninetales and Raticate', file='decks/dustin/13-a-ninetales-raticate.txt',
         report='2026-10-12_13-a-ninetales-raticate', pg=['d13'], png=None,
         blurb='Alolan Ninetales ex and Team Rocket\'s Raticate ex, with Soothing Shore and Elegant Cape.'),
    dict(key='brew-08', group='Also tested', label='Brew 08', title='Entei and Rainbow Cave', file='decks/brews/brew-08-entei-rainbow-cave.txt',
         report='2026-10-09_brew-08-entei-rainbow-cave', pg=[], png='decks/brews/brew-08-entei-rainbow-cave.png',
         blurb='Entei ex with Flame Patch, Giant Cape and two Rainbow Cave.'),
    dict(key='brew-09', group='Also tested', label='Brew 09', title='Sableye and Obstagoon', file='decks/brews/brew-09-sableye-obstagoon.txt',
         report='2026-10-12_brew-09-sableye-obstagoon', pg=[], png='decks/brews/brew-09-sableye-obstagoon.png',
         blurb='Mega Sableye ex and Galarian Obstagoon, with Rare Candy and Deceptive Needle.'),
    dict(key='draft-a', group='Also tested', label='Draft A', title='Wallace (Mega Sharpedo and Ninetales)', file='decks/brews/drafts_2026-10-01/draft-A-wallace.txt',
         report='2026-10-08_draft-A-wallace', pg=['dA'], png=None,
         blurb='The tested Wallace version: one Misty and one Wallace. The older two-Misty Shark Tempo version is a different list and a different code.'),
    dict(key='draft-d', group='Also tested', label='Draft D', title='Entei and Houndoom', file='decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt',
         report='2026-10-12_draft-D-entei-grimhound', pg=['dD'], png=None,
         blurb='Entei ex with Houndour, one Mega Houndoom ex, Victini and Magby.'),
]
ENERGY_NAME = {1: 'Grass', 2: 'Fire', 3: 'Water', 4: 'Lightning', 5: 'Psychic', 6: 'Fighting', 7: 'Darkness', 8: 'Metal'}
RANK = {'C': 0, 'U': 1, 'R': 2, 'RR': 3, 'AR': 4, 'SR': 5, 'SAR': 6, 'IM': 7, 'UR': 8, 'SSR': 9}
def ekey(k):
    """the catalog writes entity keys zero-padded ('pokemon:020640'); the code carries the number: 'pokemon:20640'"""
    kind, num = k.split(':')
    return f'{kind}:{int(num)}'


BY_ENTITY = collections.defaultdict(list)
for a in E.BYID.values():
    BY_ENTITY[ekey(a['entity_key'])].append(a)
norm = E._norm


def parse_deck(path):
    """lib/encode_qr.py's parse(), with one difference: a card name that differs from the catalog's only in spaces, case or punctuation is accepted and reported
    (the catalog spells B4 095 "GalarianZigzagoon"; parse() would refuse the deck file's "Galarian Zigzagoon"). The id is what the code uses. Any other mismatch still fails.
    -> (energy bytes, [(count, id)], [name notes])"""
    flat = lambda s: re.sub(r'[^a-z0-9]', '', norm(s))
    energy, cards, notes = [], [], []
    for raw in open(path, encoding='utf-8'):
        line = raw.split('#')[0].strip()
        if not line:
            continue
        if line.lower().startswith('energy:'):
            for e in line[7:].split(','):
                if e.strip().lower() not in E.ENERGY:
                    raise SystemExit(f'{path}: unknown energy "{e}"')
                energy.append(E.ENERGY[e.strip().lower()])
            continue
        m = E.LINE.match(line)
        if not m:
            raise SystemExit(f'{path}: cannot parse line: {line}')
        n, name, cid = int(m[1]), m[2], m[3]
        a = E.BYID.get(cid)
        if not a:
            raise SystemExit(f'{path}: unknown card id {cid} ({name})')
        if norm(a['raw_name']) != norm(name):
            if flat(a['raw_name']) != flat(name):
                raise SystemExit(f'{path}: {cid} is "{a["raw_name"]}" in the catalog, not "{name}"')
            notes.append(f'{cid}: the deck file says "{name}", the catalog "{a["raw_name"]}" (spelling only; the code uses the id)')
        cards.append((n, cid))
    if sum(n for n, _ in cards) != 20:
        raise SystemExit(f'{path}: {sum(n for n, _ in cards)} cards, need 20')
    if not energy:
        raise SystemExit(f'{path}: no "Energy:" line')
    return energy, cards, notes


def sha256_file(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def decode_code(code):
    """the game's code -> ([trainer entity keys], [pokemon entity keys], [energy bytes]); by the layout in decode_qr.py, not through the encoder"""
    b = base64.b64decode(code, validate=True)
    nt = b[0]
    i = 1
    trainers = ['trainer:%d' % (int.from_bytes(b[i + 3 * k:i + 3 * k + 3], 'big') - 10_000_000) for k in range(nt)]
    i += 3 * nt
    npk = b[i]
    i += 1
    pokes = ['pokemon:%d' % int.from_bytes(b[i + 3 * k:i + 3 * k + 3], 'big') for k in range(npk)]
    i += 3 * npk
    ne = b[i]
    i += 1
    energy = list(b[i:i + ne])
    if i + ne != len(b):
        raise ValueError(f'{len(b) - i - ne} bytes left over')
    return trainers, pokes, energy


def entity_name(key):
    lst = BY_ENTITY.get(key)
    return lst[0]['raw_name'] if lst else f'UNKNOWN {key}'


def deck_multiset(cards):
    c = collections.Counter()
    for n, cid in cards:
        c[ekey(E.BYID[cid]['entity_key'])] += n
    return c


def lowest_rarity_printing(key):
    return sorted(BY_ENTITY[key], key=lambda a: (RANK.get(a['rarity'], 5), a['deckgym_id']))[0]['deckgym_id']


def read_text(img):
    r = zxingcpp.read_barcodes(img)
    return r[0].text if r else None


def svg_for(code):
    """-> (svg markup, n modules): the QR for `code` (error correction M, as lib/encode_qr.py), 4-module quiet zone, one path of runs of dark modules"""
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=1, border=0)
    q.add_data(code)
    q.make(fit=True)
    m = q.get_matrix()
    n = len(m)
    runs = []
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]:
                    x += 1
                runs.append(f'M{x0 + 4},{y + 4}h{x - x0}v1h-{x - x0}z')
            else:
                x += 1
    size = n + 8
    svg = (f'<svg class="qr" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" shape-rendering="crispEdges" role="img" aria-label="Deck import QR code">'
           f'<rect width="{size}" height="{size}"/><path d="{"".join(runs)}"/></svg>')
    return svg, size


def read_svg(svg, scale=8):
    """rasterise a page QR from its own path text (no SVG renderer needed: the path is only runs of unit-high rectangles) and read it with zxing"""
    vb = int(re.search(r'viewBox="0 0 (\d+) \d+"', svg).group(1))
    img = np.full((vb * scale, vb * scale), 255, dtype=np.uint8)
    d = re.search(r'<path d="([^"]+)"', svg).group(1)
    cmds = re.findall(r'M(\d+),(\d+)h(\d+)v1h-(\d+)z', d)
    if ''.join(f'M{a},{b}h{c}v1h-{e}z' for a, b, c, e in cmds) != d:
        raise ValueError('path text has commands the reader does not know')
    for x, y, w, w2 in cmds:
        assert w == w2
        img[int(y) * scale:(int(y) + 1) * scale, int(x) * scale:(int(x) + int(w)) * scale] = 0
    return read_text(img)


def compare_to(code, other_code):
    """-> ('same code' | 'same cards, other order' | 'different', {entity name: (count here, count there)} for the entities that differ, energy differs?)"""
    if code == other_code:
        return 'same code', {}, False
    t1, p1, e1 = decode_code(code)
    t2, p2, e2 = decode_code(other_code)
    c1, c2 = collections.Counter(t1 + p1), collections.Counter(t2 + p2)
    diff = {entity_name(k): (c1.get(k, 0), c2.get(k, 0)) for k in sorted(set(c1) | set(c2)) if c1.get(k, 0) != c2.get(k, 0)}
    if not diff and sorted(e1) == sorted(e2):
        return 'same cards, other order', {}, False
    return 'different', diff, sorted(e1) != sorted(e2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pause-decks', help='folder with the Pause Games pause_decks documents (one JSON file each)')
    ap.add_argument('--html', help='where to write the page (default: ladder_qr_page.html beside this script)')
    args = ap.parse_args()
    commit = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short=8', 'HEAD'], capture_output=True, text=True).stdout.strip()
    pg = {}
    if args.pause_decks:
        for f in sorted(glob.glob(os.path.join(args.pause_decks, '*.json'))):
            d = json.load(open(f, encoding='utf-8'))
            if d.get('code'):
                pg[os.path.splitext(os.path.basename(f))[0]] = d
    out, fails = [], []

    def check(deck, name, ok, detail=''):
        deck['checks'].append({'name': name, 'ok': bool(ok), 'detail': detail})
        if not ok:
            fails.append(f"{deck['key']}: {name} {detail}")

    for deck in DECKS:
        deck['checks'], deck['notes'] = [], []
        path = os.path.join(ROOT, deck['file'])
        deck['sha256'] = sha256_file(path)
        mf = json.load(open(os.path.join(ROOT, 'rl', 'results', 'slow_reports', deck['report'], 'manifest.json'), encoding='utf-8'))
        m1, m2 = mf['decks'][0], mf['slow_report']
        check(deck, 'file is the one in the report manifest', m1['path'] == deck['file'] and m2['deck_file'] == deck['file'] and m1['sha256'] == deck['sha256'] == m2['deck_file_sha256'],
              f"sha256 {deck['sha256'][:16]}..., manifest says {m1['sha256'][:16]}... and {m2['deck_file_sha256'][:16]}...; state: {m2.get('deck_file_state')}")
        energy, cards, name_notes = parse_deck(path)
        deck['notes'] += name_notes
        code = E.encode(energy, cards)
        deck['code'], deck['energy_bytes'] = code, energy
        deck['energy'] = [ENERGY_NAME[e] for e in energy]
        # the deck file, line by line
        want = deck_multiset(cards)
        lines = []
        for n, cid in cards:
            a = E.BYID[cid]
            lines.append({'n': n, 'name': a['raw_name'], 'id': cid, 'kind': 'Pokémon' if a['entity_key'].startswith('pokemon') else 'Trainer', 'entity': ekey(a['entity_key'])})
        deck['cards'] = lines
        # 3. decode the code again
        tr, pk, en = decode_code(code)
        got = collections.Counter(tr + pk)
        check(deck, 'code decodes to 20 cards', len(tr) + len(pk) == 20 and sum(n for n, _ in cards) == 20, f'{len(tr)} Trainers + {len(pk)} Pokémon')
        check(deck, 'same cards and counts as the deck file', got == want, '; '.join(f'{entity_name(k)} {got.get(k, 0)} v {want.get(k, 0)}' for k in sorted(set(got) | set(want)) if got.get(k, 0) != want.get(k, 0)) or f'{len(want)} different cards')
        check(deck, 'same Energy as the deck file', sorted(en) == sorted(energy), f'bytes {en} v {energy}')
        bad = [l for l in lines if l['id'] not in {a['deckgym_id'] for a in BY_ENTITY.get(l['entity'], [])}]
        check(deck, 'every printing in the deck file is a printing of the card the code names', not bad, str(bad))
        # the code names the card, not the printing: where decode_qr.py would show another printing than the file lists
        deck['printing_notes'] = [f"{l['name']}: file {l['id']}, decode_qr.py shows {lowest_rarity_printing(l['entity'])}" for l in lines if lowest_rarity_printing(l['entity']) != l['id']]
        # 4. the QR image
        png = os.path.join(HERE, 'png', deck['key'] + '.png')
        os.makedirs(os.path.dirname(png), exist_ok=True)
        E.write_qr(code, png)
        check(deck, 'QR image (lib/encode_qr.py PNG) reads back as the code', read_text(np.array(Image.open(png).convert('L'))) == code)
        svg, size = svg_for(code)
        deck['svg'] = svg
        check(deck, 'QR image on the page (SVG) reads back as the code', read_svg(svg) == code, f'{size - 8} x {size - 8} modules')
        # 5. codes that already exist
        cmp_ = []
        for pid in deck['pg']:
            if pid not in pg:
                deck['notes'].append(f'Pause Games document {pid} not given (--pause-decks)')
                continue
            verdict, diff, edif = compare_to(code, pg[pid]['code'])
            cmp_.append({'what': f"Pause Games {pid} \"{pg[pid].get('name')}\"", 'verdict': verdict, 'diff': diff, 'energy_differs': edif})
        if deck['png']:
            ex = np.array(Image.open(os.path.join(ROOT, deck['png'])).convert('L'))
            text = read_text(ex)
            if text is None:
                cmp_.append({'what': f"image {deck['png']}", 'verdict': 'unreadable', 'diff': {}, 'energy_differs': False})
            else:
                verdict, diff, edif = compare_to(code, text)
                cmp_.append({'what': f"image {deck['png']}", 'verdict': verdict, 'diff': diff, 'energy_differs': edif})
        # any Pause Games document with exactly these cards
        for pid, d in sorted(pg.items()):
            if pid in deck['pg']:
                continue
            verdict, diff, edif = compare_to(code, d['code'])
            if verdict != 'different':
                cmp_.append({'what': f"Pause Games {pid} \"{d.get('name')}\"", 'verdict': verdict, 'diff': diff, 'energy_differs': edif})
        deck['compared'] = cmp_
        out.append(deck)

    # the page, and the codes read back out of the finished file
    html_path = args.html or os.path.join(HERE, 'ladder_qr_page.html')
    page = render_page(out, commit)
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page)
    text = open(html_path, encoding='utf-8').read()
    svgs = re.findall(r'<svg class="qr".*?</svg>', text, re.S)
    ok_page = len(svgs) == len(out) and all(read_svg(s) == d['code'] for s, d in zip(svgs, out))
    if not ok_page:
        fails.append('the QR codes read back out of the finished page file do not all match')
    for d in out:
        d['checks'].append({'name': 'QR image read back out of the finished page file', 'ok': ok_page, 'detail': html_path})
    # a record without the SVGs
    rec = [{k: v for k, v in d.items() if k != 'svg'} for d in out]
    json.dump({'commit': commit, 'decks': rec, 'failed': fails}, open(os.path.join(HERE, 'verification.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, 'verification.txt'), 'w', encoding='utf-8') as f:
        for d in out:
            f.write(f"== {d['label']}: {d['title']}  ({d['file']}, sha256 {d['sha256'][:16]}...)\n   code {d['code']}\n")
            for c in d['checks']:
                f.write(f"   [{'ok' if c['ok'] else 'FAIL'}] {c['name']}" + (f" ({c['detail']})" if c['detail'] and not c['ok'] else '') + '\n')
            for c in d['compared']:
                extra = '; '.join(f'{k}: {a} here, {b} there' for k, (a, b) in c['diff'].items())
                f.write(f"   v {c['what']}: {c['verdict']}" + (f' ({extra})' if extra else '') + ('; Energy differs' if c['energy_differs'] else '') + '\n')
            for n in d['printing_notes']:
                f.write(f'   printing note: {n}\n')
            for n in d['notes']:
                f.write(f'   note: {n}\n')
    print(open(os.path.join(HERE, 'verification.txt'), encoding='utf-8').read())
    print('FAILED:' if fails else 'all checks passed', *fails, sep='\n  ' if fails else ' ')
    return 1 if fails else 0


def render_page(decks, commit):
    from page import render
    return render(decks, commit)


if __name__ == '__main__':
    sys.exit(main())

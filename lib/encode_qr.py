#!/usr/bin/env python3
"""Encode a Pocket Deck Lab decklist (.txt) into a Pokémon TCG Pocket deck code and QR image.

Inverse of decode_qr.py. Same byte layout, verified 2026-09-15 by a byte-exact round trip on
decks/dustin/02-arceus-crobat.txt against the code the game itself produced:
    base64( [n_trainers][3-byte 10,000,000 + entity id]... [n_pokemon][3-byte entity id]... [n_energy][energy bytes] )
Entity ids come from s216_card_catalog_v1.json (entity_key), so the QR names the card, not a
printing or rarity — any printing you own satisfies it.

Known unknowns (2026-09-15): the game's own codes list cards in a non-obvious order; this tool
writes them in decklist order. Whether the game accepts a different order is untested — scan the
"Test B" code on the Season Brews page (or run this on any deck and import it) to settle it.
Energy bytes 9/10 (Dragon?/Colorless?) are unverified, same as the decoder.

Decklist format (what decks/brews/*.txt and decks/dustin/*.txt already use):
    Energy: Psychic            # or "Energy: Water, Fighting"
    2 Arceus ex A2a 071        # <count> <name> <set> <number>
    ...

deps: pip install qrcode pillow      (zxing-cpp optional, for --verify)
usage: encode_qr.py deck.txt [more ...] [--out DIR] [--verify]
   prints the code for each deck and writes <DIR>/<deckname>.png (default: next to the .txt)
"""
import sys, os, re, json, base64, argparse

_here = os.path.dirname(os.path.abspath(__file__))
_cat = next((p for p in (os.environ.get('PDL_CATALOG', ''), os.path.join(_here, 's216_card_catalog_v1.json'),
                         os.path.join(_here, '..', 's216_card_catalog_v1.json'), 's216_card_catalog_v1.json')
             if p and os.path.exists(p)), None)
if not _cat:
    raise SystemExit('s216_card_catalog_v1.json not found (set PDL_CATALOG or run from the project)')
BYID = {a['deckgym_id']: a for a in json.load(open(_cat, encoding='utf-8'))['aliases']}
ENERGY = {'grass': 1, 'fire': 2, 'water': 3, 'lightning': 4, 'psychic': 5, 'fighting': 6, 'darkness': 7, 'metal': 8,
          'dark': 7, 'electric': 4}
LINE = re.compile(r'^(\d+)\s+(.+?)\s+([A-Z][0-9A-Za-z\-]*\s\d{3})$')
_norm = lambda s: s.replace('’', "'").strip().lower()


def parse(path):
    energy, cards = [], []
    for raw in open(path, encoding='utf-8'):
        line = raw.split('#')[0].strip()
        if not line:
            continue
        if line.lower().startswith('energy:'):
            for e in line[7:].split(','):
                e = e.strip().lower()
                if e not in ENERGY:
                    raise SystemExit(f'{path}: unknown energy "{e}"')
                energy.append(ENERGY[e])
            continue
        m = LINE.match(line)
        if not m:
            raise SystemExit(f'{path}: cannot parse line: {line}')
        n, name, cid = int(m[1]), m[2], m[3]
        a = BYID.get(cid)
        if not a:
            raise SystemExit(f'{path}: unknown card id {cid} ({name})')
        if _norm(a['raw_name']) != _norm(name):
            raise SystemExit(f'{path}: {cid} is "{a["raw_name"]}" in the catalog, not "{name}"')
        cards.append((n, cid))
    total = sum(n for n, _ in cards)
    if total != 20:
        raise SystemExit(f'{path}: {total} cards, need 20')
    if not energy:
        raise SystemExit(f'{path}: no "Energy:" line')
    return energy, cards


def encode(energy, cards):
    tr, pk = [], []
    for n, cid in cards:
        kind, num = BYID[cid]['entity_key'].split(':')
        (tr if kind == 'trainer' else pk).extend([int(num)] * n)
    b = bytes([len(tr)]) + b''.join((10_000_000 + x).to_bytes(3, 'big') for x in tr)
    b += bytes([len(pk)]) + b''.join(x.to_bytes(3, 'big') for x in pk)
    b += bytes([len(energy)]) + bytes(energy)
    return base64.b64encode(b).decode()


def write_qr(code, png_path):
    import qrcode
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=3)
    q.add_data(code)
    q.make(fit=True)
    q.make_image(fill_color='black', back_color='white').save(png_path)


def verify(code, png_path):
    import zxingcpp, numpy as np
    from PIL import Image
    r = zxingcpp.read_barcodes(np.array(Image.open(png_path).convert('L')))
    return bool(r) and r[0].text == code


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('decks', nargs='+')
    ap.add_argument('--out', help='directory for PNGs (default: beside each .txt)')
    ap.add_argument('--verify', action='store_true', help='re-read each PNG with zxing-cpp')
    ap.add_argument('--no-png', action='store_true', help='print codes only')
    args = ap.parse_args()
    for path in args.decks:
        energy, cards = parse(path)
        code = encode(energy, cards)
        print(f'== {os.path.basename(path)}  code={code}')
        if args.no_png:
            continue
        out_dir = args.out or os.path.dirname(os.path.abspath(path))
        os.makedirs(out_dir, exist_ok=True)
        png = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + '.png')
        write_qr(code, png)
        msg = f'   wrote {png}'
        if args.verify:
            msg += '  (QR reads back OK)' if verify(code, png) else '  (QR READ-BACK FAILED)'
        print(msg)

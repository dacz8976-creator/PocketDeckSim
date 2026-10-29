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

Dual Fusion (C1) cards (release checklist R7): the catalog has none yet, so parse() and encode() also
read the PROVISIONAL overlay lib/c1_provisional_entities.json (read by lib/check_c1_overlay.py), only
for ids the catalog lacks: the catalog always wins. Its entries are in PROVISIONAL, never in BYID:
BYID stays the catalog's, so its other readers (rl/deck_journal/journal.py, the Ladder QR page's
build.py) still refuse C1 cards until the catalog has them. A deck that uses an overlay entry prints
which. A new card the overlay does not cover (C1 118 Bewear ex, SP1, P-C) is refused with the reason.
If the catalog has any id the overlay lists, this tool refuses: compare with lib/check_c1_overlay.py
and drop the overlay. PDL_C1_OVERLAY=off skips the overlay.

Decklist format (what decks/brews/*.txt and decks/dustin/*.txt already use):
    Energy: Psychic            # or "Energy: Water, Fighting"
    2 Arceus ex A2a 071        # <count> <name> <set> <number>; SP1's three Mew are "SP1 -03".."SP1 -01"
    ...

deps: pip install qrcode pillow      (zxing-cpp optional, for --verify)
usage: encode_qr.py deck.txt [more ...] [--out DIR] [--verify]
   prints the code for each deck and writes <DIR>/<deckname>.png (default: next to the .txt)
"""
import sys, os, re, json, base64, argparse

_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)
import check_c1_overlay as c1  # noqa: E402  (the provisional C1 overlay, release checklist R7)
_cat = next((p for p in (os.environ.get('PDL_CATALOG', ''), os.path.join(_here, 's216_card_catalog_v1.json'),
                         os.path.join(_here, '..', 's216_card_catalog_v1.json'), 's216_card_catalog_v1.json')
             if p and os.path.exists(p)), None)
if not _cat:
    raise SystemExit('s216_card_catalog_v1.json not found (set PDL_CATALOG or run from the project)')
_aliases = json.load(open(_cat, encoding='utf-8'))['aliases']
BYID = {a['deckgym_id']: a for a in _aliases}      # the catalog only; never the provisional overlay
# C1 printings the catalog lacks, from the provisional overlay; load() refuses any overlap, so the catalog wins
PROVISIONAL, NOT_COVERED = c1.load(_aliases)


def card(cid):
    """The catalog's entry for an id, else the provisional overlay's (it has 'provisional': True); None if neither."""
    return BYID.get(cid) or PROVISIONAL.get(cid)


ENERGY = {'grass': 1, 'fire': 2, 'water': 3, 'lightning': 4, 'psychic': 5, 'fighting': 6, 'darkness': 7, 'metal': 8,
          'dark': 7, 'electric': 4}
# the number may carry a minus sign: SP1's three Mew are 'SP1 -03'..'SP1 -01' (as lib/brew_consistency.py reads them)
LINE = re.compile(r'^(\d+)\s+(.+?)\s+([A-Z][0-9A-Za-z\-]*\s-?\d+)$')
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
        a = card(cid)
        if not a and cid in NOT_COVERED:
            raise SystemExit(f'{path}: {cid} ({name}) cannot be encoded: its deck-code entity is not known yet. '
                             f'{NOT_COVERED[cid]["reason"]} (lib/c1_provisional_entities.json)')
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
        kind, num = card(cid)['entity_key'].split(':')
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
        prov = [cid for _, cid in cards if cid in PROVISIONAL]
        if prov:
            print(f'   provisional C1 entities (until the community catalog has C1; lib/c1_provisional_entities.json): '
                  f'{", ".join(prov)}')
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

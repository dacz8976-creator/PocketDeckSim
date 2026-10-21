#!/usr/bin/env python3
"""Sort every changed game of the candidate's self-checks (games/new/*.diff.tsv) by what could explain it.

For each differing deal: the two deck files (research names -> decks/research/<name>.txt; pairs files -> held_file/panel_file),
and which candidate change could reach it by its cards:
  growl  : a card with an attacker-side cut (the 18 printings the Growl-to-0 rule reads) is in either deck
  fossil : a Fossil card (#401)            multihit: an "at random" multi-hit attacker (#390)
  onplay : Miraidon ex / Koraidon ex / Roaring Moon / Poltchageist (#385)
  energy : a deck declaring Dragon or Colorless Energy (#344)
Output: games/classify.tsv (one row per changed deal) and a count per run. The FINAL group needs the U build where a deck
could be reached by more than one change, or by none (then the game is (c) unexplained until shown otherwise)."""
import json, re, shlex, sys
from pathlib import Path

W = Path('/home/dacz8976/pincand_work')
R = Path('/home/dacz8976/pincand')
SW2 = R / 'rl/results/engine_switch_rules2_2026-10'
NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
TABLE28 = [(x, y) for k, x in enumerate(NAMES) for y in NAMES[k + 1:]]
CUT = {('A1', 151), ('A1', 239), ('A3', 226), ('A4b', 194), ('A4b', 195), ('A2a', 30), ('A3a', 15), ('A4', 59), ('A4', 78),
       ('A4', 173), ('B3', 78), ('B3', 168), ('B3b', 26), ('B3b', 56), ('B4', 49), ('P-B', 82), ('B4', 134), ('P-A', 30)}


def db_index():
    db = json.load(open(R / 'engine/database.json', encoding='utf-8'))
    idx = {}
    def walk(x):
        if isinstance(x, dict):
            cid = x.get('id')
            if isinstance(cid, str) and ' ' in cid and 'name' in x:
                idx[cid] = x
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(db)
    return idx


IDX = None


def deck_cards(path):
    cards, energy = [], ''
    for line in (R / path).read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line.lower().startswith('energy:'):
            energy = line.split(':', 1)[1]
            continue
        m = re.match(r'(\d+)\s+(?:.*\s)?(\S+)\s+(\d+)$', line)   # "2 B3 079" or "2 Riolu B3 079"
        if m:
            cards.append((m.group(2), int(m.group(3))))
    return cards, energy


def reach(path):
    global IDX
    if IDX is None:
        IDX = db_index()
    cards, energy = deck_cards(path)
    tags = set()
    for s, n in cards:
        if (s, n) in CUT:
            tags.add('growl')
        e = IDX.get(f'{s} {n:03d}') or IDX.get(f'{s} {n}')
        text = json.dumps(e).lower() if e else ''
        name = (e or {}).get('name', '')
        if 'fossil' in name.lower():
            tags.add('fossil')
        if 'at random' in text and 'time' in text and 'damage' in text:
            tags.add('multihit')
        if name in ('Miraidon ex', 'Koraidon ex', 'Roaring Moon', 'Poltchageist'):
            tags.add('onplay')
    if re.search(r'dragon|colorless', energy, re.I):
        tags.add('energy')
    return tags


def decks_for(name, pairing):
    lines = (SW2 / f'{name}.run').read_text().splitlines()
    args = shlex.split(next(l[5:] for l in lines if l.startswith('args ')))
    if '--decks' in args:
        a, b = TABLE28[pairing]
        return f'decks/research/{a}.txt', f'decks/research/{b}.txt'
    pf = args[args.index('--pairs') + 1].replace('/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim', str(R))
    for row in Path(pf).read_text().splitlines()[1:]:
        c = row.split('\t')
        if c[0] == str(pairing):
            return c[3], c[5]
    raise KeyError((name, pairing))


def main():
    out = open(W / 'games/classify.tsv', 'w')
    out.write('run\tpairing\ti\tfields\tdeck_a\tdeck_b\treach\n')
    for f in sorted((W / 'games/new').glob('*.diff.tsv')):
        name = f.name[:-len('.diff.tsv')]
        rows = [l.split('\t') for l in f.read_text().splitlines()[1:] if l]
        counts = {}
        for r in rows:
            p, i, fields = int(r[0]), r[1], r[2]
            da, dbk = decks_for(name, p)
            tags = sorted(reach(da) | reach(dbk)) or ['NONE']
            key = '+'.join(tags)
            counts[key] = counts.get(key, 0) + 1
            out.write(f'{name}\t{p}\t{i}\t{fields}\t{da}\t{dbk}\t{key}\n')
        if rows:
            print(f'{name}: {len(rows)} changed deals; by reach: {counts}')
    out.close()


if __name__ == '__main__':
    main()

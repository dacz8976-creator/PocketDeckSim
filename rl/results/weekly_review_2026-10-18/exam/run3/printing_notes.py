#!/usr/bin/env python3
"""The opponent's printing notes in a position's opp_ambiguous (coordinator-048, Oct 25, Part B facts): each printing note becomes
"Opponent's <name>: the position uses printing <set number>." with no evidence clause. The "chosen by HP / attack title / Ability title"
clauses can cite what the review first shows after the point's turn, and the lists of other printings come from card data; both are dropped.
Each printing choice is kept as it is: the set number is read from the position itself (the opponent's Active, Bench, the cards behind them,
their Tools, the discard and the Stadium) and must be one the old note names.
  - A Tool whose name the review did not read keeps that fact: "Opponent's <Tool phrase>: its name was not shown; the position uses <card>,
    printing <set number>."
  - The review's 'Silver Pad' (no such card): "Opponent's Order Pad: the review calls it 'Silver Pad', which is no card's name; the position
    uses printing <set number>."
  - A note that is not about the opponent's printings (his own hand, a reconstructed Energy) is kept word for word.
  - Two printing notes also state a fact of an earlier play that the position rests on (Brock's two Energy, the Grunt's Confusion): that
    fact stays as its own sentence (FACTS_KEPT).
A note the rules cannot settle (its card not in the position, two printings in play, a set number the old note does not name) stops the run.

  printing_notes.py EXAM_V2_DIR DRAFT_JSON OUT_JSON    (a dry run over a draft: every note, old and new, and the checks)
"""
import collections, json, os, re, sys

SETNO = r'(?:P-[AB]|[AB]\d[a-z]?)\s+\d{1,3}'
CARD = re.compile(rf'^(.*?)\s+({SETNO})$')
KEPT = (re.compile(r'^His hand: '), re.compile(r"^Opponent Benched Oricorio's 1 Lightning is a reconstruction; "))
# Two printing notes also state a fact of an earlier play that is not printing evidence and that the position rests on (both reviewers of
# the rewrite, Oct 25): it stays, as its own sentence, after the printing sentence. Both plays come before every position that carries them.
FACTS_KEPT = {
    "Opponent Brock printing not shown; A1 224 used (A1 224 and A1 271 match by name); the review shows its one play on global 1 putting two "
    "Fighting Energy on Onix, while the database text of both printings attaches one":
        "Opponent's Brock: the review shows its one play, on global 1, putting two Fighting Energy on Onix; Brock's card text attaches one.",
    "Opponent Team Rocket Grunt printing not shown; A2b 072 used (A2b 072 and A2b 091 match); the review shows it making his Active Confused "
    "with a coin for the opponent's own Active, which is not the database text of Team Rocket Grunt":
        "Opponent's Team Rocket Grunt: the review shows it making his Active Confused, with a coin flip for the opponent's own Active, which "
        "is not Team Rocket Grunt's card text.",
}
EVIDENCE = ('chosen by', 'attack title', 'Ability title', 'printings have')
_DB = {}


def db(e2):
    if not _DB:
        raw = json.load(open(f'{e2}/bin/frozen_db_b5e68fc8.json', encoding='utf-8'))
        cards = [v for e in raw for v in e.values()]
        _DB['names'] = sorted({c['name'] for c in cards}, key=len, reverse=True)
        _DB['attacks'] = {a['title'] for c in cards for a in c.get('attacks') or []}
        _DB['abilities'] = {c['ability']['title'] for c in cards if c.get('ability')}
    return _DB


def split(card):
    m = CARD.match(card)
    if not m:
        raise ValueError(f'no set number in {card!r}')
    return m.group(1), re.sub(r'\s+', ' ', m.group(2))


def opp_cards(pos):
    """(name, set number, zone, the names in its evolution stack or None, its HP or None) of every opponent card in the position. A card
    behind and a Tool belong to the whole stack ("Wurmple under Silcoon" is behind Beautifly, under Silcoon)."""
    out, o = [], pos['opp']
    for i, b in enumerate(o['board']):
        n, s = split(b['card'])
        stack = (n,) + tuple(split(u)[0] for u in b.get('behind') or [])
        out.append((n, s, 'active' if i == 0 else 'bench', stack, b.get('hp')))
        for u in b.get('behind') or []:
            out.append((*split(u), 'behind', stack, None))
        for t in b.get('tools') or []:
            out.append((*split(t), 'tool', stack, None))
    for c in o.get('discard') or []:
        out.append((*split(c), 'discard', None, None))
    st = pos.get('stadium')
    if st:
        out.append((*split(st['card']), 'stadium', None, None))
    return out


# Notes the rules above cannot settle, each settled by hand from the position and the point's other notes (recorded in the run's output).
BY_HAND = {
    ('LAD-20261024_003927000_SR-t10', 'Opponent Electrike (the first, benched on global turn 1) printing chosen by HP (60) only (its attack was '
     'not shown); A2a 027, B2b 026, B2b 098 and P-B 043 match'):
        ("Opponent's Electrike (the first, benched on global turn 1): the position uses printing A2a 027.",
         "two Electrike are in play: the Active one is B2b 026 (the point's other note, 'Opponent Active Electrike'); the first one, now "
         "under Mega Manectric ex, is A2a 027"),
}


def names_in(text, e2):
    """The card names in text, longest first, without overlaps, in order of position."""
    found, taken = [], [False] * len(text)
    for n in db(e2)['names']:
        for m in re.finditer(r'(?<![\w\'’])' + re.escape(n) + r'(?![\w’])', text):
            if not any(taken[m.start():m.end()]):
                found.append((m.start(), n))
                for k in range(m.start(), m.end()):
                    taken[k] = True
    return [n for _, n in sorted(found)]


class Unsettled(Exception):
    pass


def pick(pos, card, s, zone=None, holder=None, hp=None):
    """The set number of the opponent's `card` in the position (optionally in `zone`, in `holder`'s stack, with `hp`). When the old note s
    names set numbers, the one used must be among them; a note that names none (its card's printings by HP only) is not cross-checked."""
    allc = [c for c in opp_cards(pos) if c[0] == card]
    cand = [c for c in allc if (zone is None or c[2] == zone) and (holder is None or (c[3] and holder in c[3])) and (hp is None or c[4] == hp)]
    if not cand:
        raise Unsettled(f'{card} ({zone or "any zone"}{", stack of " + holder if holder else ""}{", " + str(hp) + " HP" if hp else ""}) is not in the position')
    sets = sorted({c[1] for c in cand})
    named = {re.sub(r'\s+', ' ', x) for x in re.findall(SETNO, s)}
    if len(sets) > 1:
        sets = [x for x in sets if x in named]
        if len(sets) != 1:
            raise Unsettled(f'{card}: printings {sorted({c[1] for c in cand})} in play, the note names {sorted(named)}')
    if named and sets[0] not in named:
        raise Unsettled(f'{card}: the position uses {sets[0]}, which the note does not name ({sorted(named)})')
    return sets[0]


def subject(s):
    """The note's subject: its words before 'printing' (or the first ':' or ';'), without 'Opponent', keeping a parenthesis that tells two
    cards apart ("(70 HP)", "(under Greninja)", "(the first, benched on global turn 1)")."""
    head = re.split(r'\s+printings?\b|:|;', s, maxsplit=1)[0]
    head = re.sub(r"^Opponent(?:'s)?\s+", '', head)
    return re.sub(r'\s+', ' ', head).strip()


def rewrite_one(pos, s, e2, pid=None):
    """[new texts] for one old note, and its kind."""
    if any(k.match(s) for k in KEPT):
        return [s], 'kept'
    if (pid, s) in BY_HAND:
        return [BY_HAND[(pid, s)][0]], 'by_hand'
    if "'Silver Pad'" in s:
        st = pick(pos, 'Order Pad', s)
        return [f"Opponent's Order Pad: the review calls it 'Silver Pad', which is no card's name; the position uses printing {st}."], 'silver_pad'
    m = re.match(r"^Opponent(?:'s)?\s+(?P<subj>[^:;]*\bTool\b[^:;]*):\s*its title (?:was not read|is not displayed)", s)
    if m:
        subj = m.group('subj')
        hold = names_in(subj, e2)
        if len(hold) != 1:
            raise Unsettled(f'tool note: holder not found in {subj!r}')
        named = {re.sub(r'\s+', ' ', x) for x in re.findall(SETNO, s)}
        # the Tool in the holder's stack; when the holder is gone ("the first Igglybuff", now in the discard), the Tool in the discard
        tools = sorted({(c[0], c[1]) for c in opp_cards(pos) if c[2] == 'tool' and hold[0] in c[3] and c[1] in named})
        if not tools and any(c[0] == hold[0] and c[2] == 'discard' for c in opp_cards(pos)):
            tools = sorted({(c[0], c[1]) for c in opp_cards(pos) if c[2] == 'discard' and c[1] in named})
        if len(tools) != 1:
            raise Unsettled(f'tool note: {len(tools)} matching Tools for {hold[0]}')
        return [f"Opponent's {subj}: its name was not shown; the position uses {tools[0][0]}, printing {tools[0][1]}."], 'tool'
    m = re.match(rf"^Opponent(?:'s)?\s+(?P<subj>[^:;]+): only (?P<set>{SETNO}) matches$", s)
    if m and len(names_in(m.group('subj'), e2)) == 1:
        card = names_in(m.group('subj'), e2)[0]
        return [f"Opponent's {m.group('subj')}: the position uses printing {pick(pos, card, s)}."], 'printing'
    if not s.startswith('Opponent') or 'printing' not in s:
        raise Unsettled('not a recognised note')
    subj = subject(s)
    sub_names = names_in(subj, e2)
    in_discard = 'in the discard' in s
    hp = re.search(r'\((\d+) HP\)', subj)
    hp = int(hp.group(1)) if hp else None
    if re.search(r'\bunder\b', subj) and len(sub_names) >= 2:
        card, holder = sub_names[:2]  # "Caterpie (under Butterfree and under Metapod)": Caterpie, in Butterfree's stack
        return [f"Opponent's {subj}: the position uses printing {pick(pos, card, s, 'behind', holder)}."], 'printing'
    if len(sub_names) == 1:
        card = sub_names[0]
        zone = 'bench' if re.search(r'\bBenched\b', subj) else 'active' if re.search(r'\bActive\b', subj) else 'discard' if in_discard else None
        if s in FACTS_KEPT:
            return [f"Opponent's {subj}: the position uses printing {pick(pos, card, s, zone, hp=hp)}.", FACTS_KEPT[s]], 'printing_and_fact'
        return [f"Opponent's {subj}: the position uses printing {pick(pos, card, s, zone, hp=hp)}."], 'printing'
    # several cards in one note: the names given in its subject, or (a 'Trainer printings' note) the names it lists that are in the position
    have = {c[0] for c in opp_cards(pos)}
    cards = sub_names if sub_names else [n for n in names_in(s, e2) if n in have]
    cards = list(dict.fromkeys(cards))
    if not cards:
        raise Unsettled('several-card note with no card in the position')
    where = ' in the discard' if in_discard else ''
    return [f"Opponent's {c}{where}: the position uses printing {pick(pos, c, s, 'discard' if in_discard else None)}." for c in cards], 'several'


def rewrite(pos, e2):
    """(new opp_ambiguous list, [record per old note]). Exact duplicates in the new list are kept once."""
    new, rec = [], []
    for s in pos.get('opp_ambiguous') or []:
        texts, kind = rewrite_one(pos, s, e2, pos.get('id'))
        rec.append({'old': s, 'new': texts, 'kind': kind, **({'by_hand': BY_HAND[(pos.get('id'), s)][1]} if kind == 'by_hand' else {})})
        for t in texts:
            if t not in new:
                new.append(t)
    subj = collections.defaultdict(set)
    for t in new:
        m = re.match(r"^(Opponent's .*?): the position uses printing (.*)\.$", t)
        if m:
            subj[m.group(1)].add(m.group(2))
    clash = {k: v for k, v in subj.items() if len(v) > 1}
    if clash:
        raise Unsettled(f'one name, two printings: {clash}')
    return new, rec


def leaks(texts, e2):
    """Each new text's evidence words, and attack or Ability names (a name that is also a card name in the same text is a card)."""
    d, out = db(e2), []
    for t in texts:
        hit = [w for w in EVIDENCE if w.lower() in t.lower()]
        cards = ' '.join(names_in(t, e2))
        for n in d['attacks'] | d['abilities']:
            if re.search(r'(?<![\w\'’])' + re.escape(n) + r'(?![\w’])', t) and n not in cards:
                hit.append(n)
        if hit:
            out.append((t, hit))
    return out


if __name__ == '__main__':
    e2, draft, out = sys.argv[1:4]
    d = json.load(open(draft, encoding='utf-8'))
    rows, bad, kinds = [], [], collections.Counter()
    for p in d['points']:
        pos = p['position']
        try:
            new, rec = rewrite(pos, e2)
        except Unsettled as e:
            bad.append((p['id'], str(e)))
            continue
        for r in rec:
            kinds[r['kind']] += 1
        rows.append({'point': p['id'], 'old': pos.get('opp_ambiguous') or [], 'new': new, 'records': rec})
    alltexts = [t for r in rows for t in r['new'] if not any(k.match(t) for k in KEPT)]
    lk = leaks(sorted(set(alltexts)), e2)
    json.dump({'rows': rows, 'unsettled': bad, 'kinds': kinds, 'leaks': lk}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('points:', len(d['points']), '| settled:', len(rows), '| unsettled:', len(bad))
    print('old notes by kind:', dict(kinds), '| old notes:', sum(len(r['old']) for r in rows), '| new notes:', sum(len(r['new']) for r in rows))
    print('distinct new texts:', len(set(alltexts)), '| leaks:', len(lk))
    for x in bad[:40]:
        print('  UNSETTLED', x)
    for x in lk[:40]:
        print('  LEAK', x)

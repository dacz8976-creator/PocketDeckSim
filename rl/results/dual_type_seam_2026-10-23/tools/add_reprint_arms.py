#!/usr/bin/env python3
"""Give every B4b Trainer reprint the CardId arms of its base printings (release prep, Oct 24 2026).

usage, from the repo root:
    python3 -I rl/results/dual_type_seam_2026-10-23/tools/add_reprint_arms.py [--check]

In this fork Trainer logic is keyed by CardId, so a reprint does nothing until it is named wherever its base
printing is named. A base printing of a B4b Trainer is a Trainer of any other set with the same name AND the
same effect text (engine/database.json; ids -> enum names from engine/src/card_ids.rs).

In FILES, outside #[cfg(test)] items, comments and string literals, every `CardId::<base>` is classified:
  - a pattern alternative (a match arm `A | B =>`, `matches!(x, A | B)`, `Some(A | B)` inside one of those,
    `if let A = ..`, or any `A | B` alternation of CardId paths): ` | CardId::<twin>` is added right after the
    LAST base alternative of that pattern, for every twin of every base in it that is not there yet, each
    once, in id order;
  - an element of a list or slice literal made only of CardId paths (`[..]`, `&[..]`, `vec![..]`): every
    missing twin is added after the last occurrence of its bases; one per line if the list is one per line
    (the indentation and the line ending are copied from the base's line), else inline; a `[CardId; N]` type
    written on the list's own declaration is updated to the new length;
  - anything else (an equality, a function argument, a constant): NOT edited, printed as SKIPPED with
    file:line and the line, to be decided by hand.
Bytes are read and written as they are. Text is inserted inside lines, and a new line copies the ending of the
line it follows, so CRLF, LF and mixed files keep every line's ending.

--check prints what would change, writes nothing, and exits 1 if anything would change. A second run changes
nothing (the script re-analyses its own output and says so).
"""
import bisect
import json
import re
import sys
from collections import Counter, defaultdict

ENGINE = 'engine'
FILES = [
    'src/actions/apply_trainer_action.rs',
    'src/move_generation/move_generation_trainer.rs',
    'src/actions/trainer_coin_plan.rs',
    'src/players/fuel_credit.rs',
    'src/players/value_functions.rs',
    'src/hooks/core.rs',
    'src/tools.rs',
    'src/hooks/retreat.rs',
    'src/state/played_card.rs',
    'src/players/public_pricing_player.rs',
    'src/stadiums.rs',
]
TWIN_SET = 'B4b'


# ---------------------------------------------------------------------------------------------- card data
def set_of(card_id):
    return card_id.split(' ')[0]


def id_key(card_id):
    s, n = card_id.split(' ')
    return (s, int(n)) if n.isdigit() else (s, 10 ** 6, n)


def load_twins():
    """twins_of: base enum -> [twin enum] (id order); twin_order: twin enum -> sort key; pairs for the table."""
    db = json.load(open(f'{ENGINE}/database.json', encoding='utf-8'))
    trainers = [entry['Trainer'] for entry in db if 'Trainer' in entry]
    ids_text = open(f'{ENGINE}/src/card_ids.rs', encoding='utf-8').read()
    enum_of = {m.group(1): m.group(2)
               for m in re.finditer(r'map\.insert\("([^"]+)",\s*CardId::(\w+)\)', ids_text)}
    by_name = defaultdict(list)
    for t in trainers:
        if set_of(t['id']) != TWIN_SET:
            by_name[t['name']].append(t)
    twins = sorted((t for t in trainers if set_of(t['id']) == TWIN_SET), key=lambda t: id_key(t['id']))
    twins_of = defaultdict(list)
    twin_order = {}
    pairs = []
    for t in twins:
        bases = sorted((b for b in by_name[t['name']] if b['effect'] == t['effect']), key=lambda b: id_key(b['id']))
        other = sorted((b for b in by_name[t['name']] if b['effect'] != t['effect']), key=lambda b: id_key(b['id']))
        for card in [t] + bases:
            if card['id'] not in enum_of:
                sys.exit(f'ERROR: {card["id"]} has no map.insert line in card_ids.rs')
        tw = enum_of[t['id']]
        twin_order[tw] = id_key(t['id'])
        for b in bases:
            twins_of[enum_of[b['id']]].append(tw)
        pairs.append((t, bases, other))
    for base in twins_of:
        twins_of[base].sort(key=lambda e: twin_order[e])
    return twins_of, twin_order, pairs, enum_of


# ---------------------------------------------------------------------------------------------- Rust lexing
RAW_STR = re.compile(r'b?r(#*)"')


def code_view(text):
    """`text` with comments, string literals and char literals blanked to spaces (line breaks kept). A blanked
    string or char literal keeps a `0` in its first column so that it still reads as one token."""
    out = list(text)
    n = len(text)

    def wipe(a, b, keep_token):
        for k in range(a, b):
            if out[k] not in '\r\n':
                out[k] = ' '
        if keep_token and b > a:
            out[a] = '0'

    i = 0
    while i < n:
        c = text[i]
        if text.startswith('//', i):
            j = text.find('\n', i)
            j = n if j < 0 else j
            wipe(i, j, False)
            i = j
            continue
        if text.startswith('/*', i):
            depth, j = 1, i + 2
            while j < n and depth:
                if text.startswith('/*', j):
                    depth, j = depth + 1, j + 2
                elif text.startswith('*/', j):
                    depth, j = depth - 1, j + 2
                else:
                    j += 1
            wipe(i, j, False)
            i = j
            continue
        after_ident = i > 0 and (text[i - 1].isalnum() or text[i - 1] == '_')
        m = None if after_ident else RAW_STR.match(text, i)
        if m:
            close = '"' + m.group(1)
            j = text.find(close, m.end())
            j = n if j < 0 else j + len(close)
            wipe(i, j, True)
            i = j
            continue
        if c == '"' or (not after_ident and text.startswith('b"', i)):
            j = i + (1 if c == '"' else 2)
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            j = min(j + 1, n)
            wipe(i, j, True)
            i = j
            continue
        if c == "'" or (not after_ident and text.startswith("b'", i)):
            k = i + (1 if c == "'" else 2)
            if k < n and text[k] == '\\':
                j = text.find("'", k + 2)
                j = n if j < 0 else j + 1
                wipe(i, j, True)
                i = j
                continue
            if k + 1 < n and text[k + 1] == "'" and text[k] not in '\r\n':
                wipe(i, k + 2, True)
                i = k + 2
                continue
            # otherwise a lifetime or a loop label: an ordinary character
        i += 1
    return ''.join(out)


TOKEN = re.compile(r"""
    (?P<path>[A-Za-z_][A-Za-z0-9_]*(?:[ \t]*::[ \t]*[A-Za-z_][A-Za-z0-9_]*)*)
  | (?P<num>[0-9][A-Za-z0-9_]*)
  | (?P<punct>::|=>|==|!=|<=|>=|\|\||\|=|&&|->|\.\.=|\.\.\.|\.\.|\+=|-=|\*=|/=|%=|\^=|&=|<<=|>>=|[^\sA-Za-z0-9_])
""", re.X)
OPEN, CLOSE = '([{', ')]}'
NOT_AN_INDEX_BASE = {'in', 'return', 'mut', 'let', 'if', 'else', 'match', 'break', 'yield', 'move'}


class Tok:
    __slots__ = ('kind', 'text', 'start', 'end')

    def __init__(self, kind, text, start, end):
        self.kind, self.text, self.start, self.end = kind, text, start, end

    def segments(self):
        return [s.strip() for s in self.text.split('::')] if self.kind == 'path' else []


def is_cardid(tok):
    seg = tok.segments()
    return len(seg) >= 2 and seg[-2] == 'CardId'


def name_of(tok):
    return tok.segments()[-1]


def prefix_of(tok):
    return tok.text[:tok.text.rindex('::') + 2]


class Source:
    def __init__(self, text):
        self.text = text
        self.code = code_view(text)
        self.toks = [Tok(m.lastgroup, m.group(), m.start(), m.end()) for m in TOKEN.finditer(self.code)]
        self.line_starts = [0] + [m.end() for m in re.finditer('\n', text)]
        self.partner = {}
        self.encl = [None] * len(self.toks)
        stack = []
        for k, t in enumerate(self.toks):
            self.encl[k] = stack[-1] if stack else None
            if t.text in OPEN and len(t.text) == 1:
                stack.append(k)
            elif t.text in CLOSE and len(t.text) == 1:
                if not stack or OPEN[CLOSE.index(t.text)] != self.toks[stack[-1]].text:
                    raise SystemExit(f'ERROR: unbalanced {t.text!r} at line {self.line(t.start)}')
                o = stack.pop()
                self.partner[o], self.partner[k] = k, o
        if stack:
            raise SystemExit(f'ERROR: unclosed {self.toks[stack[-1]].text!r} at line {self.line(self.toks[stack[-1]].start)}')
        self.test_ranges, self.notes = self._test_ranges()

    def line(self, pos):
        return bisect.bisect_right(self.line_starts, pos)

    def line_text(self, pos):
        a = self.line_starts[self.line(pos) - 1]
        b = self.text.find('\n', pos)
        return self.text[a:len(self.text) if b < 0 else b].strip()

    def tok(self, k):
        return self.toks[k] if 0 <= k < len(self.toks) else Tok('eof', '', len(self.text), len(self.text))

    def _attr_end(self, k):
        """k is a `#` followed by `[`: the index just after the attribute's closing `]`."""
        return self.partner[k + 1] + 1

    def _test_ranges(self):
        ranges, notes = [], []
        k = 0
        while k < len(self.toks):
            t = self.toks[k]
            if t.text == '#' and self.tok(k + 1).text == '[' and self.tok(k + 2).text == 'cfg':
                end_attr = self._attr_end(k)
                body = [x.text for x in self.toks[k + 2:end_attr - 1]]
                if body == ['cfg', '(', 'test', ')']:
                    j = end_attr
                    while self.tok(j).text == '#' and self.tok(j + 1).text == '[':
                        j = self._attr_end(j)
                    depth = 0
                    while j < len(self.toks):
                        x = self.toks[j].text
                        if x in '([' and len(x) == 1:
                            depth += 1
                        elif x in ')]' and len(x) == 1:
                            depth -= 1
                        elif x == '{' and depth == 0:
                            j = self.partner[j]
                            break
                        elif x == ';' and depth == 0:
                            break
                        j += 1
                    ranges.append((t.start, self.tok(j).end))
                    k = j
                elif 'test' in body:
                    notes.append(f'NOTE line {self.line(t.start)}: {" ".join(body)} is not #[cfg(test)]; treated as live code')
            k += 1
        return ranges, notes

    def in_test(self, pos):
        return any(a <= pos < b for a, b in self.test_ranges)


# ---------------------------------------------------------------------------------------------- classification
def group_at(src, k):
    """The run of CardId paths joined by single `|` around token k: (first index, last index)."""
    s = e = k
    while src.tok(s - 1).text == '|' and is_cardid(src.tok(s - 2)):
        s -= 2
    while src.tok(e + 1).text == '|' and is_cardid(src.tok(e + 2)):
        e += 2
    return s, e


def pattern_context(src, s, e):
    before, after = src.tok(s - 1).text, src.tok(e + 1).text
    if after == '=>':
        return 'match arm'
    if before == 'let' and after == '=':
        return 'if let'
    o = src.encl[s]
    if (o is not None and src.toks[o].text == '(' and src.tok(o - 1).text == '!'
            and src.tok(o - 2).text == 'matches' and before == ',' and after in (')', 'if')):
        return 'matches!'
    if after == 'if' and o is not None and src.toks[o].text == '{' and before in ('{', ',', '}'):
        return 'match arm (guarded)'
    if before == '(' and src.tok(s - 2).text in ('Some', 'Ok', 'Err') and after == ')':
        outer = pattern_context(src, s - 2, e + 1)
        if outer:
            return f'{src.tok(s - 2).text}(..) in {outer}'
    return None


def list_context(src, k):
    o = src.encl[k]
    if o is None or src.toks[o].text != '[':
        return None
    c = src.partner[o]
    elems, want_elem = [], True
    for j in range(o + 1, c):
        t = src.toks[j]
        if want_elem:
            if not is_cardid(t):
                return None
            elems.append(j)
            want_elem = False
        else:
            if t.text != ',':
                return None
            want_elem = True
    if not elems:
        return None
    prev = src.tok(o - 1)
    if len(elems) == 1 and ((prev.kind in ('path', 'num') and prev.text not in NOT_AN_INDEX_BASE)
                            or prev.text in (')', ']')):
        return None  # `x[CardId::A]` is an index, not a list
    return o, c, elems


def skip_kind(src, k):
    before, after = src.tok(k - 1).text, src.tok(k + 1).text
    if before in ('==', '!=') or after in ('==', '!='):
        return 'equality'
    o = src.encl[k]
    if o is not None and src.toks[o].text == '(' and src.tok(o - 1).kind == 'path' and before in ('(', ',', '&'):
        return f'argument of {src.tok(o - 1).text}()'
    return 'other'


def analyse(text, twins_of, twin_order):
    """Return (edits, report rows, skipped rows, counts). An edit is (start, end, replacement)."""
    src = Source(text)
    edits, rows, skipped = [], [], []
    counts = Counter()
    seen_groups, seen_lists = set(), set()
    order = lambda e: twin_order[e]
    for k, t in enumerate(src.toks):
        if not is_cardid(t) or name_of(t) not in twins_of:
            continue
        if src.in_test(t.start):
            counts['in #[cfg(test)] (ignored)'] += 1
            continue
        s, e = group_at(src, k)
        kind = pattern_context(src, s, e)
        if kind is None and e > s:
            kind = 'pattern alternation'
        if kind is not None:
            if (s, e) in seen_groups:
                continue
            seen_groups.add((s, e))
            group = [src.toks[x] for x in range(s, e + 1, 2)]
            present = {name_of(g) for g in group}
            want = sorted({tw for g in group for tw in twins_of.get(name_of(g), []) if tw not in present}, key=order)
            bases = [g for g in group if name_of(g) in twins_of]
            counts[f'pattern: {kind}'] += 1
            if want:
                last = bases[-1]
                pre = prefix_of(last)
                edits.append((last.end, last.end, ''.join(f' | {pre}{w}' for w in want)))
                rows.append((src.line(last.start), kind, [name_of(b) for b in bases], want))
            continue
        lst = list_context(src, k)
        if lst is not None:
            o, c, elems = lst
            if o in seen_lists:
                continue
            seen_lists.add(o)
            names = [name_of(src.toks[j]) for j in elems]
            present = set(names)
            anchors = defaultdict(list)
            for tw in sorted({tw for n in names for tw in twins_of.get(n, []) if tw not in present}, key=order):
                anchors[max(j for j in elems if tw in twins_of.get(name_of(src.toks[j]), []))].append(tw)
            elem_lines = [src.line(src.toks[j].start) for j in elems]
            one_per_line = (len(set(elem_lines)) == len(elems)
                            and (len(elems) > 1 or src.line(src.toks[o].start) != elem_lines[0]))
            counts['list' + (' (one per line)' if one_per_line else ' (inline)')] += 1
            added = 0
            for j, tws in sorted(anchors.items()):
                el = src.toks[j]
                pre = prefix_of(el)
                line_start = src.line_starts[src.line(el.start) - 1]
                indent = text[line_start:el.start]
                nl = text.find('\n', el.end)
                comma = src.tok(j + 1)
                comma_on_line = comma.text == ',' and (nl < 0 or comma.start < nl)
                if one_per_line and not indent.strip() and nl >= 0 and (comma_on_line or src.tok(j + 1).text == ']'):
                    eol = '\r\n' if text[nl - 1] == '\r' else '\n'
                    if comma_on_line:
                        new = ''.join(f'{indent}{pre}{tw},{eol}' for tw in tws)
                    else:  # the base is the last element and has no trailing comma
                        edits.append((el.end, el.end, ','))
                        new = ''.join(f'{indent}{pre}{tw}{"," if i < len(tws) - 1 else ""}{eol}' for i, tw in enumerate(tws))
                    edits.append((nl + 1, nl + 1, new))
                    rows.append((src.line(el.start), 'list (one per line)', [name_of(el)], tws))
                else:
                    edits.append((el.end, el.end, ''.join(f', {pre}{tw}' for tw in tws)))
                    rows.append((src.line(el.start), 'list (inline)', [name_of(el)], tws))
                added += len(tws)
            if added:
                m = re.search(r'\[\s*CardId\s*;\s*(\d+)\s*\]\s*=\s*$', src.code[:src.toks[o].start])
                if m:
                    n_old = int(m.group(1))
                    edits.append((m.start(1), m.end(1), str(n_old + added)))
                    rows.append((src.line(m.start(1)), 'array length', [f'[CardId; {n_old}]'], [f'[CardId; {n_old + added}]']))
            continue
        kind = skip_kind(src, k)
        counts['SKIPPED'] += 1
        skipped.append((src.line(t.start), kind, name_of(t), src.line_text(t.start)))
    raw = sum(1 for m in re.finditer(r'\bCardId\s*::\s*(\w+)', text) if m.group(1) in twins_of)
    code = sum(1 for t in src.toks if is_cardid(t) and name_of(t) in twins_of)
    if raw != code:
        counts['in comments/strings (ignored)'] += raw - code
    return edits, rows, skipped, counts, src.notes


def apply_edits(text, edits):
    spans = sorted(edits, key=lambda x: (x[0], x[1]))
    for (a1, b1, _), (a2, b2, _) in zip(spans, spans[1:]):
        if a2 < b1:
            raise SystemExit(f'ERROR: overlapping edits at {a1}..{b1} and {a2}..{b2}')
    for a, b, new in sorted(edits, key=lambda x: (x[0], x[1]), reverse=True):
        text = text[:a] + new + text[b:]
    return text


def endings(data):
    crlf = data.count(b'\r\n')
    return crlf, data.count(b'\n') - crlf


# ---------------------------------------------------------------------------------------------- main
def main():
    check = '--check' in sys.argv[1:]
    unknown = [a for a in sys.argv[1:] if a != '--check']
    if unknown:
        sys.exit(__doc__)
    twins_of, twin_order, pairs, enum_of = load_twins()

    names = sorted({t['name'] for t, _, _ in pairs})
    print(f'PAIRS: {len(pairs)} {TWIN_SET} Trainer reprints, {len(names)} names, {len(twins_of)} base printings')
    for t, bases, other in pairs:
        line = f'  {t["id"]} {t["name"]} ({t["trainer_card_type"]}) <- ' + (', '.join(b['id'] for b in bases) or 'NO BASE')
        if other:
            line += '   [same name, other text: ' + ', '.join(b['id'] for b in other) + ']'
        print(line)
    no_base = [t['id'] for t, bases, _ in pairs if not bases]
    if no_base:
        print(f'WARNING: no base printing for {", ".join(no_base)}')

    total_edits, total_skipped = Counter(), 0
    changed = []
    for rel in FILES:
        path = f'{ENGINE}/{rel}'
        data = open(path, 'rb').read()
        text = data.decode('utf-8')
        edits, rows, skipped, counts, notes = analyse(text, twins_of, twin_order)
        print(f'\n== {path}')
        for note in notes:
            print('  ' + note)
        for line, kind, bases, added in sorted(rows):
            print(f'  EDIT    {path}:{line}  [{kind}]  after {", ".join(bases)}: + {", ".join(added)}')
            total_edits[(rel, kind)] += 1
        for line, kind, base, context in skipped:
            print(f'  SKIPPED {path}:{line}  [{kind}]  CardId::{base}  |  {context}')
        total_skipped += len(skipped)
        print('  counts: ' + (', '.join(f'{k} {v}' for k, v in sorted(counts.items())) or 'no base printing named'))
        if not edits:
            continue
        new_text = apply_edits(text, edits)
        new_data = new_text.encode('utf-8')
        again = analyse(new_text, twins_of, twin_order)[0]
        if again:
            raise SystemExit(f'ERROR: {path}: a second pass would still change {len(again)} places')
        (c0, l0), (c1, l1) = endings(data), endings(new_data)
        print(f'  line endings: CRLF {c0} -> {c1}, LF {l0} -> {l1}; second pass: no change')
        changed.append(path)
        if not check:
            open(path, 'wb').write(new_data)

    print('\nSUMMARY')
    for (rel, kind), n in sorted(total_edits.items()):
        print(f'  {rel}: {n} x {kind}')
    print(f'  edit sites: {sum(total_edits.values())}; files {"to change" if check else "changed"}: {len(changed)}; SKIPPED: {total_skipped}')
    if check:
        print('  --check: nothing written' + ('; changes are pending' if changed else '; nothing to do'))
        sys.exit(1 if changed else 0)


if __name__ == '__main__':
    main()

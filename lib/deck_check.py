#!/usr/bin/env python3
"""Pocket Deck Lab — the decklist validator. RUN THIS, don't remember rules.

Catches, mechanically, the entire class of parse/reconstruct defects that has
recurred three times in this project (see the regression tests at the bottom):
  §37-R  accented card name silently unmatched   -> a card vanished
  §101   `Pok` name-prefix filter                -> Poke Ball / Pokemon Center Lady vanished
  §102   decklist keyed by NAME not (name,id)    -> a split-print copy vanished

All three shared ONE signature: a card silently disappeared during parsing, and
every check in place validated the OUTPUT (does my deck have 20 cards?) which
greedy-fill guaranteed anyway. The fix is to validate the INPUT and the SHAPE.

usage:
  deck_check.py pool <dir>            validate every .txt deck in a pool dir
  deck_check.py files <deck.txt>...   validate these deck files (run scripts call this)
  deck_check.py lists <file.jsonl>    validate RAW parsed source lists (one JSON obj per line,
                                      {"src":..., "cards":[[n,"name","SET NNN"],...]})
  deck_check.py selftest              run the regression suite
"""
import sys, os, io, json, collections

DB = None
def db():
    global DB
    if DB is None:
        DB = {}
        here = os.path.dirname(os.path.abspath(__file__))
        for p in (os.path.join(here,'deckgym-database.json'),
                  os.path.join(here,'..','deckgym-database.json'),
                  'deckgym-database.json','../deckgym-database.json',
                  os.path.expanduser('~/mnt/Pocket Deck Lab/deckgym-database.json')):
            if os.path.exists(p):
                for e in json.load(io.open(p, encoding='utf-8')):
                    for k, v in e.items():
                        if isinstance(v, dict) and 'id' in v:
                            DB[v['id']] = {'name': v.get('name'), 'kind': k,
                                           'stage': v.get('stage'), 'from': v.get('evolves_from')}
                break
        if not DB:
            raise SystemExit('FATAL: deckgym-database.json not found. This validator REFUSES to run '
                             'without it — a check that silently skips is exactly the failure mode '
                             'this file exists to prevent (it silently passed the s102 fixture once).')
    return DB

def parse(path):
    cards, energy = [], None
    for ln in io.open(path, encoding='utf-8'):
        ln = ln.strip()
        if not ln: continue
        if ln.startswith('Energy:'): energy = ln; continue
        p = ln.split()
        cards.append((int(p[0]), ' '.join(p[1:-2]), ' '.join(p[-2:])))
    return energy, cards

def check(name, cards, strict_ids=True):
    """Returns list of (severity, message). ERROR = do not sim this deck."""
    out = []
    # Zero/negative/fractional counts can otherwise cancel into a legal-looking total.
    for row, entry in enumerate(cards, 1):
        if not isinstance(entry, (list, tuple)) or len(entry) != 3:
            out.append(('ERROR', f'card row {row} must have count, name, and ID'))
            continue
        n, nm, i = entry
        if type(n) is not int or n <= 0:
            out.append(('ERROR', f'card row {row} count must be a positive integer, got {n!r}'))
        if not isinstance(nm, str) or not isinstance(i, str):
            out.append(('ERROR', f'card row {row} name and ID must be strings'))
    if out:
        return out
    tot = sum(n for n, _, _ in cards)
    # 1. THE CORE INVARIANT. A Pocket deck is exactly 20 cards. Always.
    if tot != 20:
        out.append(('ERROR', f'total is {tot}, must be exactly 20 '
                             f'(a missing card here means the PARSER dropped one)'))
    # 2. max-2 is enforced PER-ID (s84)
    per = collections.Counter()
    for n, _, i in cards: per[i] += n
    for i, n in per.items():
        if n > 2: out.append(('ERROR', f'{n} copies of id {i} (max-2 is PER-ID, s84)'))
    # 2b. THE REAL GAME's copy rule (s135 B, rule per Dustin 2026-08-21): max 2 per EXACT
    #     printed NAME. 'ex' is part of the name ('Zoroark ex' != 'Zoroark'); ALL prints of
    #     one name — art variants AND mechanically different cards — share the ONE limit.
    #     The engine only enforces per-id (s84) and will sim an illegal deck silently, which
    #     makes the deck STRONGER than anything a real player may build.
    Dn = db()
    pername = collections.Counter()
    for n, nm, i in cards:
        pername[Dn[i]['name'] if i in Dn and Dn[i].get('name') else nm] += n
    for nm2, n in pername.items():
        if n > 2:
            out.append(('ERROR', f'{n} copies of printed name "{nm2}" — the real game allows 2 '
                                 f'per EXACT name across ALL prints (s135 B); the engine would '
                                 f'sim it anyway'))
    # 3. every id must resolve
    D = db()
    if strict_ids:
        for _, nm, i in cards:
            if i not in D:
                out.append(('ERROR', f'unresolvable id {i} ({nm})'))
            elif i in D and D[i]['name'] and nm.lower() != D[i]['name'].lower():
                out.append(('WARN', f'name/id mismatch: "{nm}" vs db "{D[i]["name"]}" for {i} '
                                    f'(engine resolves by ID and IGNORES the name, s76)'))
    # 4. At least one actual Basic Pokemon is required. Determine this by resolved
    # ID, not the supplied label or the absence of an evolves_from field on Trainers.
    if not any(D.get(i, {}).get('kind') == 'Pokemon' and
               D[i].get('stage') == 0 for _, _, i in cards):
        out.append(('ERROR', 'deck must contain at least one Basic Pokemon'))
    # 5. Evolution ratios are a source-reconstruction/playability HEURISTIC, not
    # deck legality. Thin lines and extra evolution copies are legal; Rare Candy
    # and other effects can also change the intended evolution plan.
    if True:
        cnt = collections.Counter()
        for n, nm, i in cards:
            cnt[(D.get(i, {}).get('name') or nm).lower()] += n
        byname = {}
        for i, v in D.items():
            if v.get('name'): byname.setdefault(v['name'].lower(), v)
        def basic_of(nm, depth=0):
            v = byname.get(nm.lower())
            if not v or not v.get('from') or depth > 4: return nm
            return basic_of(v['from'], depth + 1)
        for n, nm, i in cards:
            info = D.get(i)
            if not info or not info.get('from'): continue
            canonical_name = info.get('name') or nm
            b = basic_of(canonical_name)
            if b.lower() == canonical_name.lower(): continue
            have = cnt.get(b.lower(), 0)
            if have < n:
                out.append(('WARN', f'{n}x {canonical_name} but only {have}x {b} (its line\'s BASIC) — '
                                    f'legal thin evolution line; verify the source list and intended '
                                    f'evolution plan. Quantity mismatch alone is not illegal.'))
    return out

def check_source_lists(path):
    """Validate RAW lists as parsed from the source. EVERY published list is 20 cards;
    any that is not means the parser dropped something. This is the single check that
    would have caught all three historical bugs at parse time."""
    bad = tot = 0
    for ln in io.open(path, encoding='utf-8'):
        d = json.loads(ln); tot += 1
        s = sum(c[0] for c in d['cards'])
        if s != 20:
            bad += 1
            print(f'  PARSER DROPPED SOMETHING: {d.get("src","?")} sums to {s}, not 20')
    print(f'{tot - bad}/{tot} source lists sum to 20' + ('  ✅' if not bad else '  ❌ FIX THE PARSER'))
    return bad == 0

def selftest():
    """Legality and parser regressions; thin-line warnings must not reject legal decks."""
    ok = True
    cases = [
        ('s102 padded reconstruction (20 cards, thin Riolu line is LEGAL)',
         [(1,'Riolu','A2 091'),(2,'Mega Lucario ex','B3 081'),(1,'Lucario','A2 092'),
          (1,'Sawk','B3 086'),(1,'Bonsly','B3 078'),(1,'Hitmonlee','A1 154'),
          (2,"Professor's Research",'P-A 007'),(2,'Copycat','B1 225'),(1,'Cyrus','A2 150'),
          (1,'Korrina','B3 149'),(2,'Poké Ball','P-A 005'),(1,'X Speed','P-A 002'),
          (1,'Arena of Antiquity','B3 154'),(1,'Field Blower','B3 147'),
          (1,'Protective Poncho','B2 147'),(1,'Lucky Ice Pop','B2 145')], False),
        ('s101 dropped card (19 cards, Poké Ball filtered out)',
         [(2,'Swablu','B1 196'),(1,'Mega Altaria ex','B1 102'),(2,'Eevee','B1 184'),
          (2,'Espeon','B3a 020'),(2,'Igglybuff','A4a 059'),(2,'Darkrai','B2b 040'),
          (2,"Professor's Research",'P-A 007'),(1,'Training Area','B2 153'),
          (1,'Copycat','B1 225'),(1,'Sabrina','A1 225'),(1,'Cyrus','A2 150'),
          (1,'Lisia','B1 226'),(1,'X Speed','P-A 002')], True),
        ('s135B per-name limit (4 Bulbasaur via two art prints, 20 cards)',
         [(2,'Bulbasaur','A1 001'),(2,'Bulbasaur','A4b 001'),
          (2,"Professor's Research",'P-A 007'),(2,'Poké Ball','P-A 005'),(2,'Copycat','B1 225'),
          (2,'X Speed','P-A 002'),(2,'Cyrus','A2 150'),(2,'Sabrina','A1 225'),
          (2,'Lisia','B1 226'),(2,'Korrina','B3 149')], True),
        ("s135B suffix distinction (2 Zoroark ex + 1 Zoroark, 20 cards, LEGAL — different names)",
         [(2,'Zorua','B3 105'),(2,'Zoroark ex','B3 106'),(1,'Zoroark','B2b 044'),
          (2,"Professor's Research",'P-A 007'),(2,'Poké Ball','P-A 005'),(2,'Copycat','B1 225'),
          (2,'X Speed','P-A 002'),(2,'Cyrus','A2 150'),(2,'Sabrina','A1 225'),
          (2,'Lisia','B1 226'),(1,'Korrina','B3 149')], False),
        ('s84 per-id max-2 violation',
         [(3,'Poké Ball','P-A 005')] + [(1,'Copycat','B1 225')]*17, True),
    ]
    # The raw parser loss is 19 cards BEFORE any filler is added. Catch the loss
    # at that boundary; the padded 20-card reconstruction above is legal but suspect.
    dropped = cases[0][1][:-1]
    legal = cases[3][1]
    thin = [(1,'Zorua','B3 105')] + legal[1:-1] + [(2,'Korrina','B3 149')]
    no_basic = [(2,'Potion','P-A 001')] + legal[1:]
    negative = [(-1,'Zorua','B3 105')] + thin[1:] + [(2,'Potion','P-A 001')]
    specific = [
        ('s102 actual raw parser loss (19 cards)', dropped, 'ERROR', 'total is 19'),
        ('valid thin evolution line, 20 cards', thin, 'WARN', 'legal thin evolution line'),
        ('20 cards with no Basic Pokemon', no_basic, 'ERROR', 'at least one Basic'),
        ('negative count balanced back to 20', negative, 'ERROR', 'positive integer'),
        ('zero count appended to a legal 20', legal+[(0,'Potion','P-A 001')], 'ERROR', 'positive integer'),
        ('fractional count appended to a legal 20', legal+[(0.0,'Potion','P-A 001')], 'ERROR', 'positive integer'),
        ('invalid ID in otherwise 20-card list', [(2,'Zorua','INVALID 999')]+legal[1:], 'ERROR', 'unresolvable id'),
    ]
    for label, cards, severity, required in specific:
        result = check('t', cards)
        passed = any(s == severity and required in m for s, m in result)
        if severity == 'WARN':
            passed = passed and not any(s == 'ERROR' for s, _ in result)
        if not passed: ok = False
        print(f'  {"✅" if passed else "❌ REGRESSION"} {label}')
    for label, cards, should_fail in cases:
        errs = [m for s, m in check('t', cards) if s == 'ERROR']
        got = bool(errs)
        mark = '✅' if got == should_fail else '❌ REGRESSION'
        if got != should_fail: ok = False
        print(f'  {mark} {label}')
        for e in errs[:2]: print(f'        -> {e}')
    print('selftest', 'PASSED' if ok else 'FAILED')
    return ok

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'selftest'
    if mode == 'selftest': sys.exit(0 if selftest() else 1)
    if mode == 'lists': sys.exit(0 if check_source_lists(sys.argv[2]) else 1)
    if mode in ('pool', 'files'):
        if mode == 'pool':
            d = sys.argv[2]
            paths = [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith('.txt')]
        else:
            paths = sys.argv[2:]
            if not paths: sys.exit('files mode needs at least one deck file')
        bad = 0
        for path in paths:
            name = os.path.basename(path)[:-4]
            _, cards = parse(path)
            res = check(name, cards)
            errs = [m for s, m in res if s == 'ERROR']
            warns = [m for s, m in res if s == 'WARN']
            if errs:
                bad += 1; print(f'❌ {name}')
                for m in errs: print(f'     ERROR {m}')
            elif warns:
                print(f'⚠  {name}')
                for m in warns[:2]: print(f'     WARN  {m}')
        print(f'\n{"❌ "+str(bad)+" deck(s) FAILED — DO NOT SIM" if bad else "✅ " + ("pool" if mode == "pool" else "decks") + " clean"}')
        sys.exit(1 if bad else 0)
    # Anything else used to fall through and exit 0 having checked nothing.
    sys.exit(f'unknown mode {mode!r}: use pool <dir>, files <deck.txt>..., lists <file.jsonl> or selftest')

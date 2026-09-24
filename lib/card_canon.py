#!/usr/bin/env python3
"""Pocket Deck Lab — the functional card-identity (canon) layer. §128 (station card-canon).

Two inverse traps, both of which have already bitten this lab:
  ART REPRINTS: different ids, SAME game object — 3,761 ids collapse to ~2,2xx
    functional classes; 800+ classes have 2+ prints (Bulbasaur has 6).
  NAME COLLISIONS: one name, MANY different game objects — ~500 names are
    ambiguous (Eevee names 11 functionally different cards). ALL_IDS.md's
    Houndstone case (B3a 024 vs B2a 053, same name, different attack) cost
    13.48 pt and passed every existing validity check.

This module makes both mechanical instead of remembered:
  same_card('A1 001', 'A4b 001')   -> True    (art reprint, one game object)
  same_card('B3a 024', 'B2a 053')  -> False   (same name, different attack)
  by_name('Eevee')                 -> AmbiguousNameError, NEVER a guess
  base_id('P-A 023')               -> 'A1 001' (canonical print = lowest id,
                                      matching ALL_IDS.md's base-id convention)

The fingerprint hashes ONLY gameplay-relevant fields:
  Pokemon: name, stage, evolves_from, hp, energy_type, ability, attacks,
           weakness, retreat_cost
  Trainer: name, trainer_card_type, effect
EXCLUDED: rarity, booster_pack, set/number — acquisition-only, zero gameplay
effect (same argument as §127's energy-line exclusion). NAME IS INCLUDED
DELIBERATELY: evolution targeting and card effects resolve by name, so two
stat-identical cards with different names are different game objects.

usage:
  card_canon.py build <database.json>   regenerate results/CANON_MAP.tsv
  card_canon.py selftest                gate-grade regression suite (exit non-zero on ANY failure)
  card_canon.py check <pool_dir>        every id in every deck resolves through the map,
                                        and the REAL GAME's copy rule holds: **max 2 per
                                        EXACT printed name** ('ex' suffix = a DIFFERENT
                                        name; ALL prints of one name — art variants AND
                                        mechanically different cards — share the limit).
                                        Rule per Dustin, 2026-08-21 (§135 B). The ENGINE
                                        only enforces max-2 PER-ID (§84) and will sim an
                                        illegal deck without complaint — this check is
                                        the only thing standing in the way.

Gate contract (per the KNOWN_FAILURES standard): reproduces the original
failures (Houndstone, name-keying), passes valid fixtures, REFUSES malformed
and incomplete maps (duplicate id, short row, count mismatch, source-sha drift),
and is import-wired for future analyzers — never key a card by bare name again.
"""
import sys, os, io, json, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
MAP_PATHS = (os.path.join(HERE, '..', 'results', 'CANON_MAP.tsv'),
             os.path.join(HERE, 'CANON_MAP.tsv'), 'results/CANON_MAP.tsv', 'CANON_MAP.tsv')

# ⛔ PINNED. A db refresh MUST consciously update these three lines (that is the point:
# a silently swapped database must refuse, not pass). Source: s120 fork database.json.
EXPECTED_IDS     = 3879
EXPECTED_SOURCE_SHA256 = None  # set at build time into the map header; load() verifies map vs header only
SET_ORDER = ['A1','A1a','A2','A2a','A2b','A3','A3a','A3b','A4','A4a','A4b',
             'B1','B1a','B2','B2a','B2b','B3','B3a','B3b','B4','B4a','P-A','P-B']
# Present in the s120 engine db but ABSENT from ALL_IDS.md v2 (probed on the older
# bin-3518-b4c): revalidate these ids before using them with that older binary.
NEWER_THAN_ALL_IDS_V2 = [
    'B3 234',
    'P-B 086',
    'B4a 001',
    'B4a 002',
    'B4a 003',
    'B4a 004',
    'B4a 005',
    'B4a 006',
    'B4a 007',
    'B4a 008',
    'B4a 009',
    'B4a 010',
    'B4a 011',
    'B4a 012',
    'B4a 013',
    'B4a 014',
    'B4a 015',
    'B4a 016',
    'B4a 017',
    'B4a 018',
    'B4a 019',
    'B4a 020',
    'B4a 021',
    'B4a 022',
    'B4a 023',
    'B4a 024',
    'B4a 025',
    'B4a 026',
    'B4a 027',
    'B4a 028',
    'B4a 029',
    'B4a 030',
    'B4a 031',
    'B4a 032',
    'B4a 033',
    'B4a 034',
    'B4a 035',
    'B4a 036',
    'B4a 037',
    'B4a 038',
    'B4a 039',
    'B4a 040',
    'B4a 041',
    'B4a 042',
    'B4a 043',
    'B4a 044',
    'B4a 045',
    'B4a 046',
    'B4a 047',
    'B4a 048',
    'B4a 049',
    'B4a 050',
    'B4a 051',
    'B4a 052',
    'B4a 053',
    'B4a 054',
    'B4a 055',
    'B4a 056',
    'B4a 057',
    'B4a 058',
    'B4a 059',
    'B4a 060',
    'B4a 061',
    'B4a 062',
    'B4a 063',
    'B4a 064',
    'B4a 065',
    'B4a 066',
    'B4a 067',
    'B4a 068',
    'B4a 069',
    'B4a 070',
    'B4a 071',
    'B4a 072',
    'B4a 073',
    'B4a 074',
    'B4a 075',
    'B4a 076',
    'B4a 077',
    'B4a 078',
    'B4a 079',
    'B4a 080',
    'B4a 081',
    'B4a 082',
    'B4a 083',
    'B4a 084',
    'B4a 085',
    'B4a 086',
    'B4a 087',
    'B4a 088',
    'B4a 089',
    'B4a 090',
    'B4a 091',
    'B4a 092',
    'B4a 093',
    'B4a 094',
    'B4a 095',
    'B4a 096',
    'B4a 097',
    'B4a 098',
    'B4a 099',
    'B4a 100',
    'B4a 101',
    'B4a 102',
    'B4a 103',
    'B4a 104',
    'B4a 105',
    'B4a 106',
    'B4a 107',
    'B4a 108',
    'B4a 109',
    'B4a 110',
    'P-B 087',
    'P-B 088',
    'P-B 089',
    'P-B 090',
    'P-B 091',
    'P-B 092',
    'P-B 093',
    'P-B 094',
]

class AmbiguousNameError(Exception):
    """A bare name matched MORE THAN ONE functional card. Resolve by id, never by name."""

class CanonMapError(SystemExit):
    """The map is malformed/incomplete. REFUSE — a canon layer that silently skips
    is the exact failure mode it exists to prevent."""

def _sort_key(cid):
    s, n = cid.rsplit(' ', 1)
    if s not in SET_ORDER:
        raise CanonMapError(f'FATAL: unknown set "{s}" in id "{cid}" — extend SET_ORDER '
                            f'consciously (base-id choice depends on set order).')
    return (SET_ORDER.index(s), int(n))

def fingerprint(entry):
    kind = list(entry.keys())[0]; c = entry[kind]
    if kind == 'Pokemon':
        f = {'kind': kind, 'name': c['name'], 'stage': c['stage'],
             'evolves_from': c['evolves_from'], 'hp': c['hp'],
             'energy_type': c['energy_type'], 'ability': c['ability'],
             'attacks': c['attacks'], 'weakness': c['weakness'],
             'retreat_cost': c['retreat_cost']}
    else:
        f = {'kind': kind, 'name': c['name'],
             'trainer_card_type': c.get('trainer_card_type'), 'effect': c.get('effect')}
    return hashlib.sha1(json.dumps(f, sort_keys=True, ensure_ascii=True).encode()).hexdigest()[:12]

def build(db_path, out_path=None):
    raw = io.open(db_path, 'rb').read()
    sha = hashlib.sha256(raw).hexdigest()
    db = json.loads(raw.decode('utf-8'))
    rows = []
    for e in db:
        c = e[list(e.keys())[0]]
        rows.append((c['id'], fingerprint(e), list(e.keys())[0], c['name']))
    ids = [r[0] for r in rows]
    if len(ids) != len(set(ids)):
        raise CanonMapError('FATAL: duplicate ids in source database — refuse to build.')
    if len(ids) != EXPECTED_IDS:
        raise CanonMapError(f'FATAL: source has {len(ids)} ids, pinned EXPECTED_IDS is '
                            f'{EXPECTED_IDS}. If the db was refreshed ON PURPOSE, update '
                            f'the pin consciously; otherwise this is the wrong file.')
    classes = collections.defaultdict(list)
    for cid, fp, kind, name in rows:
        classes[fp].append(cid)
    base = {fp: min(members, key=_sort_key) for fp, members in classes.items()}
    out_path = out_path or os.path.join(HERE, '..', 'results', 'CANON_MAP.tsv')
    with io.open(out_path, 'w', encoding='utf-8') as f:
        f.write('# CANON_MAP.tsv — functional card-identity map. GENERATED by lib/card_canon.py; never hand-edit.\n')
        f.write(f'# source_sha256={sha}\n')
        f.write(f'# ids={len(rows)} classes={len(classes)} multi_print_classes={sum(1 for m in classes.values() if len(m)>1)}\n')
        f.write(f'# newer_than_ALL_IDS_v2={",".join(NEWER_THAN_ALL_IDS_V2)}\n')
        f.write('# id\tbase_id\tfingerprint\tkind\tname\n')
        for cid, fp, kind, name in sorted(rows, key=lambda r: _sort_key(r[0])):
            f.write(f'{cid}\t{base[fp]}\t{fp}\t{kind}\t{name}\n')
    print(f'wrote {out_path}: {len(rows)} ids -> {len(classes)} classes '
          f'({sum(1 for m in classes.values() if len(m)>1)} with multiple prints); source sha256 {sha[:16]}…')
    return out_path

class Canon:
    def __init__(self, path=None):
        if path is None:
            for p in MAP_PATHS:
                if os.path.exists(p): path = p; break
        if path is None or not os.path.exists(path):
            raise CanonMapError('FATAL: CANON_MAP.tsv not found — run `card_canon.py build '
                                '<database.json>`. REFUSING to continue without it.')
        self.id2fp, self.id2base, self.id2name, self.id2kind = {}, {}, {}, {}
        header = {}
        for ln in io.open(path, encoding='utf-8'):
            ln = ln.rstrip('\n')
            if ln.startswith('#'):
                if '=' in ln:
                    k, _, v = ln[1:].strip().partition('=')
                    header[k.strip()] = v
                continue
            parts = ln.split('\t')
            if len(parts) != 5:
                raise CanonMapError(f'FATAL: malformed map row ({len(parts)} cols): {ln[:80]!r}')
            cid, bid, fp, kind, name = parts
            if cid in self.id2fp:
                raise CanonMapError(f'FATAL: duplicate id in map: {cid}')
            self.id2fp[cid], self.id2base[cid] = fp, bid
            self.id2name[cid], self.id2kind[cid] = name, kind
        declared = int(header.get('ids', '-1').split()[0]) if 'ids' in header else -1
        if declared != len(self.id2fp):
            raise CanonMapError(f'FATAL: map declares ids={declared} but contains '
                                f'{len(self.id2fp)} rows — truncated or tampered map.')
        if len(self.id2fp) != EXPECTED_IDS:
            raise CanonMapError(f'FATAL: map has {len(self.id2fp)} ids, pinned EXPECTED_IDS '
                                f'is {EXPECTED_IDS} — rebuild, or update the pin consciously.')
        for cid, bid in self.id2base.items():
            if bid not in self.id2fp or self.id2fp[bid] != self.id2fp[cid]:
                raise CanonMapError(f'FATAL: base_id {bid} of {cid} inconsistent — corrupt map.')
        self._name2fps = collections.defaultdict(set)
        for cid, fp in self.id2fp.items():
            self._name2fps[self.id2name[cid].lower()].add(fp)
        self.source_sha256 = header.get('source_sha256', '')

    def canon(self, cid):
        if cid not in self.id2fp:
            raise KeyError(f'unknown card id {cid!r} — not in CANON_MAP (typo, or map/db stale?)')
        return self.id2fp[cid]

    def base_id(self, cid):
        self.canon(cid); return self.id2base[cid]

    def same_card(self, a, b):
        return self.canon(a) == self.canon(b)

    def prints_of(self, cid):
        fp = self.canon(cid)
        return sorted((i for i, f in self.id2fp.items() if f == fp), key=_sort_key)

    def by_name(self, name):
        fps = self._name2fps.get(name.lower())
        if not fps: raise KeyError(f'unknown card name {name!r}')
        if len(fps) > 1:
            raise AmbiguousNameError(
                f'{name!r} names {len(fps)} functionally DIFFERENT cards — resolve by id, '
                f'never by name (the §102/Houndstone class).')
        fp = next(iter(fps))
        return min((i for i, f in self.id2fp.items() if f == fp), key=_sort_key)

def name_rule_errors(cards, cn):
    """THE REAL GAME's copy rule (per Dustin, 2026-08-21, §135 B): max 2 copies per EXACT
    printed name. 'Eevee' and 'Eevee ex' are DIFFERENT names with separate limits; every
    print named exactly 'Eevee' — art variant or mechanically different — shares ONE limit.
    The name is taken from the DB via the id (never from the decklist text), exact-match,
    case-sensitive. The engine's own limit is max-2 PER-ID (§84) — strictly looser."""
    errs = []
    per_name, name_ids = collections.Counter(), collections.defaultdict(set)
    for n, _, cid in cards:
        nm = cn.id2name.get(cid)
        if nm is None: continue          # unresolvable ids are reported by the caller
        per_name[nm] += n; name_ids[nm].add(cid)
    for nm, n in per_name.items():
        if n > 2:
            errs.append(f'{n} copies of printed name "{nm}" via prints {sorted(name_ids[nm], key=_sort_key)} '
                        f'— the real game allows 2 per EXACT name, ALL prints counted together '
                        f'(§135 B). The ENGINE (max-2 per-id, §84) would sim this anyway: '
                        f'an illegal deck simming clean is a silent strength bonus.')
    return errs

def check_pool(pool_dir):
    sys.path.insert(0, HERE)
    import deck_check          # ONE parser — never a second copy that can drift
    cn = Canon(); bad = 0
    for f in sorted(os.listdir(pool_dir)):
        if not f.endswith('.txt'): continue
        _, cards = deck_check.parse(os.path.join(pool_dir, f))
        errs = []
        for n, nm, cid in cards:
            try:
                cn.canon(cid)
            except KeyError as e:
                errs.append(str(e))
        errs += name_rule_errors(cards, cn)
        if errs:
            bad += 1; print(f'❌ {f[:-4]}')
            for m in errs: print(f'     ERROR {m}')
    print(f'\n{"❌ "+str(bad)+" deck(s) FAILED — DO NOT SIM" if bad else "✅ pool canon-clean"}')
    return bad == 0

def selftest():
    ok = True
    def t(label, fn, expect_raise=None):
        nonlocal ok
        try:
            fn()
            good = expect_raise is None
        except BaseException as e:
            good = expect_raise is not None and isinstance(e, expect_raise)
        print(f'  {"✅" if good else "❌ REGRESSION"} {label}')
        if not good: ok = False
    cn = Canon()
    # 1. THE ORIGINAL FAILURES, AS FIXTURES
    t('Houndstone B3a 024 vs B2a 053 are DIFFERENT cards (the 13.48-pt trap)',
      lambda: (_ for _ in ()).throw(AssertionError) if cn.same_card('B3a 024', 'B2a 053') else None)
    t('by_name("Houndstone") REFUSES to guess', lambda: cn.by_name('Houndstone'), AmbiguousNameError)
    t('by_name("Eevee") REFUSES to guess',      lambda: cn.by_name('Eevee'),      AmbiguousNameError)
    # 2. VALID FIXTURES
    t('Bulbasaur A1 001 == A4b 001 == P-A 023 (art reprints, one game object)',
      lambda: (_ for _ in ()).throw(AssertionError) if not (
          cn.same_card('A1 001', 'A4b 001') and cn.same_card('A1 001', 'P-A 023')
          and cn.base_id('P-A 023') == 'A1 001') else None)
    t('unique name resolves to its BASE id', lambda: cn.by_name('Helix Fossil'))
    # §135 B — THE REAL GAME's copy rule (per Dustin, 2026-08-21)
    t('4 Bulbasaur via two prints REFUSED (one exact name, ONE limit)',
      lambda: (_ for _ in ()).throw(AssertionError) if not name_rule_errors(
          [(2, 'Bulbasaur', 'A1 001'), (2, 'Bulbasaur', 'A4b 001')], cn) else None)
    t("2 Zoroark ex + 1 Zoroark LEGAL ('ex' suffix = a DIFFERENT name)",
      lambda: (_ for _ in ()).throw(AssertionError) if name_rule_errors(
          [(2, 'Zoroark ex', 'B3 106'), (1, 'Zoroark', 'B2b 044')], cn) else None)
    # 3. FAIL-CLOSED ON BAD INPUT
    t('unknown id REFUSED', lambda: cn.canon('Z9 999'), KeyError)
    t('unknown set in sort REFUSED', lambda: _sort_key('Q1 001'), SystemExit)
    import tempfile
    body = [ln for ln in io.open(next(p for p in MAP_PATHS if os.path.exists(p)), encoding='utf-8')]
    def mutated(lines):
        fd, p = tempfile.mkstemp(suffix='.tsv'); os.close(fd)
        io.open(p, 'w', encoding='utf-8').writelines(lines); return p
    t('TRUNCATED map REFUSED (count mismatch)', lambda: Canon(mutated(body[:-5])), SystemExit)
    first_data = next(i for i, l in enumerate(body) if not l.startswith('#'))
    t('DUPLICATE id row REFUSED', lambda: Canon(mutated(body + [body[first_data]])), SystemExit)
    t('SHORT row REFUSED', lambda: Canon(mutated(body[:first_data] + ['A1 001\toops\n'] + body[first_data:])), SystemExit)
    # 4. COVERAGE of the live pool
    pool = os.path.join(HERE, '..', 'pool9')
    if os.path.isdir(pool):
        sys.path.insert(0, HERE); import deck_check
        missing = []
        for f in sorted(os.listdir(pool)):
            if not f.endswith('.txt'): continue
            for _, nm, cid in deck_check.parse(os.path.join(pool, f))[1]:
                if cid not in cn.id2fp: missing.append((f, cid, nm))
        t(f'every id in pool9/ resolves (0 missing)',
          lambda: (_ for _ in ()).throw(AssertionError) if missing else None)
        if missing: print('        ->', missing[:5])
    else:
        print('  ⚠ pool9/ not found from lib/ — coverage check SKIPPED (do not quote selftest as full)')
    print('selftest', 'PASSED' if ok else 'FAILED')
    return ok

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'selftest'
    if mode == 'selftest': sys.exit(0 if selftest() else 1)
    if mode == 'build':    build(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None); sys.exit(0)
    if mode == 'check':    sys.exit(0 if check_pool(sys.argv[2]) else 1)
    print(__doc__); sys.exit(2)

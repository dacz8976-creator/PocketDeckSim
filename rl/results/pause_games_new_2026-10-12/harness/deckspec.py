#!/usr/bin/env python3
"""The 20 cards of the deck a recorded game was played with, from Codex's DECK_USED.json, by function (see cardlib.py).

DECK_USED.json comes in many shapes (13 or so across the 28 games). What it can hold, and how it is used here:
- a QR list: the deck as filmed at the start of the game (the game's own list). Entries are 'semantic entities': name, entity_id and, often, the printings that carry that
  entity (`variant` as a string, 'A2a 053 / A2a 080', or a list, `printing_aliases`, `variant_aliases`, `semantic_variant_references`). Slots or counts.
- a log list (`cards_in_log_order`, `counts_by_name_and_variant`): the list as the Pause Games log saved it, with exact printings, but possibly a later or earlier version
  of the deck than the game's.
When both exist, the QR list says WHICH cards the game had and the log (and every other list in the file, and the entities seen in other games) says which printing carries
an entity. When only the log exists it is the list. A file with no 20-card list at all gives no deck (the game is not converted).
An entry whose printing cannot be told from the files and whose name stands for more than one function in the database is `ambiguous`: the converter settles it from the
ledger (the Pokemon on his board, with their attacks and HP) and says so in the position's notes when it cannot."""
import collections, json, re

import cardlib as C


def _walk(o, path, out):
    """every list of card-like dicts (or None / strings) with its dotted path"""
    if isinstance(o, dict):
        for k, v in o.items():
            _walk(v, f'{path}.{k}' if path else k, out)
    elif isinstance(o, list):
        if o and all(isinstance(x, dict) and isinstance(x.get('name'), str) for x in o):
            out.append((path, o))
        for x in o:
            if isinstance(x, (dict, list)):
                _walk(x, path + '[]', out)


def pids_in(v):
    """printing ids named by a field: a string ('A2a 053 / A2a 080'), a list of strings, or a number-less text"""
    if v is None:
        return []
    if isinstance(v, str):
        return [m.group(1) + ' ' + m.group(2) for m in C.PID_RE.finditer(v)]
    if isinstance(v, list):
        out = []
        for x in v:
            out += pids_in(x)
        return out
    return []


ALIAS_FIELDS = ('variant', 'printing', 'printing_aliases', 'variant_aliases', 'semantic_variant_references')
SKIP_PATH = re.compile(r'conflict|visible|core|candidate|minimum|nearby|prepared|before|snapshot_status', re.I)


def entry_ids(d):
    out = []
    for f in ALIAS_FIELDS:
        out += pids_in(d.get(f))
    return list(dict.fromkeys(out))


ENTITY_RE = re.compile(r'semantic[\s_-]*entity[\s_#:-]*(\d+)', re.I)


def entry_entity(d):
    """the QR's semantic entity of a deck entry: its `entity_id`, else the number in a string the file writes instead ('semantic entity 20770' in `variant`, as game 20261013_022530000's DECK_USED.json does)"""
    e = d.get('entity_id', d.get('semantic_entity_id'))
    if isinstance(e, int):
        return e
    for f in ALIAS_FIELDS + ('variant_as_shown_in_log',):
        v = d.get(f)
        for s in ([v] if isinstance(v, str) else [x for x in v if isinstance(x, str)] if isinstance(v, list) else []):
            m = ENTITY_RE.search(s)
            if m:
                return int(m.group(1))
    return None


def expand(lst):
    """[(dict, count)] -> list of dicts, one per card; None unless the cards add up to 20"""
    out = []
    for d in lst:
        n = d.get('count')
        n = n if isinstance(n, int) and 'position' not in d and 'slot' not in d else 1
        out += [d] * n
    return out if len(out) == 20 else None


def find_lists(j):
    """(qr_lists, log_lists): the 20-card lists of the file, each (path, expanded entries)"""
    found = []
    _walk(j, '', found)
    qr, log = [], []
    for path, lst in found:
        if SKIP_PATH.search(path):
            continue
        ex = expand(lst)
        if ex is None:
            continue
        low = path.lower()
        if low.startswith('cards_in_log_order') or low.startswith('counts_by_name_and_variant') or 'initial_log_snapshot' in low:
            log.append((path, ex))
        elif 'qr' in low or 'filmed' in low or low.startswith('source_'):
            qr.append((path, ex))
    return qr, log


def energy_of(j):
    """Energy types of the deck, from the QR energy when the file has it, else from the log's"""
    def types(v):
        out = []
        if isinstance(v, str):
            out += [C.etype(x) for x in re.split(r'[,/ ]+', v)]
        elif isinstance(v, dict):
            out += [C.etype(v.get('name'))] if (v.get('value') is None or v.get('value')) else []
        elif isinstance(v, list):
            for x in v:
                out += types(x)
        return [t for t in out if t]
    flat = {}

    def walk(o, p):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f'{p}.{k}' if p else k)
        else:
            flat[p] = o
    walk(j, '')
    qr_keys = [k for k in flat if 'energy' in k.lower() and ('qr' in k.lower() or 'filmed' in k.lower())]
    log_keys = [k for k in flat if 'energy' in k.lower() and k not in qr_keys]
    # a dict-valued energy entry (name/value) is a list element: re-walk lists of such dicts
    def collect(keys):
        out = []
        for k in keys:
            out += types(flat[k])
        return list(dict.fromkeys(out))
    for src_keys in (qr_keys, log_keys):
        t = collect(src_keys)
        if t:
            return t
    # lists of {name, value} dicts are not leaves of the walk above: look at them directly
    for k, v in j.items():
        if 'energy' in k.lower():
            t = types(v)
            if t:
                return list(dict.fromkeys(t))
    for k, v in j.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if 'energy' in k2.lower():
                    t = types(v2)
                    if t:
                        return list(dict.fromkeys(t))
    return []


class Entry:
    def __init__(self, name, entity, count):
        self.name, self.entity, self.count = name, entity, count
        self.ids = []          # printing ids the files name for this entry (valid, same name)
        self.cands = []        # first printing of each function the entry could be
        self.ambiguous = False
        self.how = ''

    def __repr__(self):
        return f'{self.name} x{self.count} ent={self.entity} ids={self.ids} cands={self.cands}{" AMBIGUOUS" if self.ambiguous else ""} [{self.how}]'


class DeckSpec:
    def __init__(self):
        self.entries = []
        self.energy = []
        self.source = None          # 'qr' | 'log'
        self.notes = []
        self.version_unverified = False


def read_deck(j, global_entities=None):
    """-> DeckSpec, or None when the file holds no 20-card list"""
    global_entities = global_entities or {}
    qr, log = find_lists(j)
    if not qr and not log:
        return None
    spec = DeckSpec()
    primary = qr[0] if qr else log[0]
    spec.source = 'qr' if qr else 'log'
    # every printing the file names for an entity, or for a name when the entry has no entity (log lists: one entry per exact card)
    by_entity = collections.defaultdict(list)
    name_ids = collections.defaultdict(list)
    for _, lst in qr + log:
        for d in lst:
            ids = [i for i in entry_ids(d) if C.known(i, d['name'])]
            e = entry_entity(d)
            if e is not None:
                by_entity[e] += ids
            name_ids[C.nname(d['name'])] += ids
    # the log list names exact printings: when the QR is primary, the log still settles a name that has only one function in it
    log_ids = collections.defaultdict(list)
    for _, lst in log:
        for d in lst:
            for i in entry_ids(d):
                if C.known(i, d['name']):
                    log_ids[C.nname(d['name'])].append(i)
    groups = collections.OrderedDict()
    for d in primary[1]:
        name = C.nname(d['name'])
        e = entry_entity(d)
        own = [i for i in entry_ids(d) if C.known(i, name)]
        if e is None:
            # no entity: an entry stands for the function of its own printing (a log list), else the name
            key = ('N', name, C.SIG[own[0]] if own else None)
        else:
            key = ('E', e, name)
        g = groups.setdefault(key, Entry(name, e, 0))
        g.count += 1
        g.ids += own
    for key, g in groups.items():
        ids = list(dict.fromkeys(g.ids))
        how = 'entry'
        if g.entity is not None:
            ids = list(dict.fromkeys(ids + by_entity.get(g.entity, [])))
            if not ids:
                ids = list(dict.fromkeys(i for i in global_entities.get(g.entity, []) if C.known(i, g.name)))
                how = 'entity seen in another game' if ids else how
        if not ids and spec.source == 'qr':
            ids = list(dict.fromkeys(log_ids.get(g.name, [])))
            how = 'the log list' if ids else how
        if not ids:
            how = 'database (name only)'
            funcs = C.functions(g.name)
            g.cands = [f[0] for f in funcs]
            g.ids = [i for f in funcs for i in f]
            g.ambiguous = len(funcs) > 1
        else:
            fs = collections.OrderedDict()
            for i in ids:
                fs.setdefault(C.SIG[i], i)
            g.ids = ids
            g.cands = list(fs.values())
            g.ambiguous = len(fs) > 1
            if g.ambiguous and g.entity is not None:
                # one entity is one function: printings of different functions under it mean the files disagree; keep the first as written and say so
                spec.notes.append(f'{g.name}: the files name printings of different functions for entity {g.entity} ({", ".join(ids)}); the first is used')
                g.cands = [g.cands[0]]
                g.ambiguous = False
        g.how = how
        spec.entries.append(g)
    spec.energy = energy_of(j)
    st = str(j.get('exact_list_status') or '')
    if re.search(r'unverified|unavailable|missing_matching|conflict', st) and not re.search(r'filmed_?qr|filmed_exact|exact_filmed|exact20_filmed|exact_live_log_20', st, re.I):
        spec.version_unverified = True
    spec.status = st
    return spec


def global_entity_map(decks):
    """entity id -> printings, from every file that names them (a file that has an entity without its printing then borrows them)"""
    m = collections.defaultdict(list)
    for j in decks:
        qr, log = find_lists(j)
        for _, lst in qr + log:
            for d in lst:
                e = entry_entity(d)
                if e is None:
                    continue
                for i in entry_ids(d):
                    if C.known(i, d['name']) and i not in m[e]:
                        m[e].append(i)
    return m


if __name__ == '__main__':
    import glob, os, sys
    Q = '/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/'
    files = sorted(glob.glob(Q + 'BATCH_2026-10-*_NEW_PAUSE_GAMES/2026*/DECK_USED.json'))
    js = {os.path.basename(os.path.dirname(f))[2:15]: json.load(open(f, encoding='utf-8')) for f in files}
    gm = global_entity_map(js.values())
    for g, j in js.items():
        s = read_deck(j, gm)
        if s is None:
            print('=====', g, 'NO 20-CARD LIST')
            continue
        print('=====', g, s.source, 'energy', s.energy, 'unverified' if s.version_unverified else '', '|', s.status[:60])
        for e in s.entries:
            if '-v' in sys.argv or e.ambiguous or len(e.cands) > 1 or e.how != 'entry':
                print('   ', e)
        for n in s.notes:
            print('   NOTE', n)

#!/usr/bin/env python3
"""A PAIRED VARIANT of a slow report: one deck, one or two cards swapped, played on the very deals of an earlier report of the base deck.

  slow_report.py --paired-with rl/results/slow_reports/<date>_<base deck> --deck decks/.../<variant>.txt     (the rest as for any registration)

The variant reuses the base report's seed_base (no new seed slot), deals, seats, opponents, threads and school rule, and must be played by the same program under the same pin.
It is registered, before any game, in its own folder, as "paired with <the base folder>"; the base folder is only read. Its page (SLOW_REPORT.md) then has a section that sets
each game against its twin in the base report (same opponent, deal, seat and pilot) and says what the card change did.

Why twin games start alike (engine/src/deck.rs, state/mod.rs, game.rs): a game's StdRng is seeded with the game's seed; Game::new shuffles the two decks in seat order with
Fisher-Yates (`SliceRandom::shuffle`, which swaps positions and never looks at a card), repairs a hand that has no Basic Pokémon by choosing among the positions that hold a Basic,
then flips the coin for the first player and rolls the Energy types. The deck is the file's cards in file order, a line "2 X" being two consecutive cards. So a card that keeps
its place in the deck file keeps its place in the shuffle, and the two decks are dealt alike except for that one card; this holds as long as the swapped cards are both Basic or both
not (the repair looks at which positions hold a Basic). A variant whose new card is on another line moves the cards in between, and the deals then differ by more than the card:
the registration says so, and so does the page. The pilots look at their own deck, so a twin can still part from its base game before the card is drawn; the page counts the twins
that were the same game from start to finish.

What the page counts (slow_report.py logs the deck side's moves only: "Play:<card>", "Tool:<card>@<slot>", "Attach", "Evolve", "Attack", "Retreat" ... with the points; no Hit
Points, damage, Special Conditions or opponent moves): how often a swapped card was played and where a Tool went; the opponent's first point being a knock-out of our opening
Active; and turns on which a charged Pokémon did not attack (an indicator of Sleep or Paralysis, not a measurement of them). What the records cannot give is named on the page.
"""
import sys
sys.dont_write_bytecode = True
import collections, json, math, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import slow_report as SR  # noqa: E402

MAX_SWAPS = 2
ENERGY_ABILITIES = {'Thieving Incisors'}   # Abilities that put an Energy on the Pokémon they name; the logged move is "Ability:<title>@<slot>"


# ------------------------------------------------------------------------------------------------------------------ the deck files
class Deck:
    def __init__(self, energy, ids, shown):
        self.energy, self.ids, self.shown = energy, ids, shown


def parse_deck(text):
    """What the engine reads from a deck file, in file order: the Energy types, the card ids ('a3 149': set in lower case, number padded to three digits) with a "2 X" line giving
    two consecutive cards, and the way each id is printed in the file. Like the engine and strength_prereg.deck_signature: a BOM, CRLF, `Pokémon:`/`Trainer:` heading lines, any
    Unicode white space and the printed name do not matter. Raises ValueError for a line that is not a card line."""
    if isinstance(text, bytes):
        text = text.decode('utf-8-sig')
    text = text.lstrip('﻿')
    energy, ids, shown = set(), [], {}
    for ln in text.split('\n'):
        words = [w for w in SR.PRE._WHITE_SPACE_RUN.split(ln) if w]
        if not words or words[0].startswith(('Pokémon:', 'Trainer:')):
            continue
        if words[0].startswith('Energy:'):
            energy.update(t.strip().lower() for t in ln.strip()[len('Energy:'):].split(',') if t.strip())
            continue
        try:
            if len(words) < 3:
                raise ValueError
            n = int(words[0])
        except ValueError:
            raise ValueError(f'{ln.strip()!r} is not a card line') from None
        card = f'{words[-2].lower()} {words[-1].zfill(3)}'
        shown.setdefault(card, ' '.join(words[1:]))
        ids.extend([card] * n)
    return Deck(tuple(sorted(energy)), ids, shown)


def diff_decks(base_text, variant_text, is_basic=None):
    """How the variant differs from the base: {swaps, removed, added ('1 Ilima A3 149'), slots (the places in file order where the two lists differ, from 0), aligned (every swapped
    card keeps its place), cards, basic_shape (True when each swapped card is a Basic as the card it replaces is, False when not, None when unknown), problems}. `is_basic(id)` says
    True, False or None (unknown). A variant is refused (problems) when it has another Energy line or size, no card swapped, or more than MAX_SWAPS."""
    out = dict(swaps=0, removed=[], added=[], slots=[], aligned=False, cards=0, basic_shape=None, problems=[])
    try:
        b, v = parse_deck(base_text), parse_deck(variant_text)
    except ValueError as e:
        out['problems'].append(str(e))
        return out
    out['cards'] = len(b.ids)
    if b.energy != v.energy:
        out['problems'].append(f"the Energy line differs (base: {', '.join(b.energy) or 'none'}; variant: {', '.join(v.energy) or 'none'}): another Energy type changes every game, not one card")
    if len(b.ids) != len(v.ids):
        out['problems'].append(f'the variant has {len(v.ids)} cards and the base deck {len(b.ids)}')
        return out
    names = {**b.shown, **v.shown}
    removed, added = collections.Counter(b.ids) - collections.Counter(v.ids), collections.Counter(v.ids) - collections.Counter(b.ids)
    out['swaps'] = swaps = sum(removed.values())
    out['removed'] = [f'{removed[c]} {names[c]}' for c in dict.fromkeys(b.ids) if c in removed]
    out['added'] = [f'{added[c]} {names[c]}' for c in dict.fromkeys(v.ids) if c in added]
    out['slots'] = slots = [k for k, (x, y) in enumerate(zip(b.ids, v.ids)) if x != y]
    out['aligned'] = swaps >= 1 and len(slots) == swaps
    if swaps == 0:
        out['problems'].append('no card differs from the base deck (the same cards in another order are not a variant: their shuffles are not the base report\'s)')
    elif swaps > MAX_SWAPS:
        out['problems'].append(f'{swaps} card swaps; a paired variant may differ from its base by at most {MAX_SWAPS}')
    if out['aligned'] and is_basic is not None:
        pairs = [(is_basic(b.ids[k]), is_basic(v.ids[k])) for k in slots]
        out['basic_shape'] = None if any(x is None or y is None for x, y in pairs) else all(x == y for x, y in pairs)
    return out


def swap_text(d):
    return ', '.join(['-' + x for x in d['removed']] + ['+' + x for x in d['added']])


def place_text(d, upper=False):
    """In words: whether the swapped cards keep their places in the deck file (and so in the shuffle)."""
    n = d.get('cards') or 20
    if d['aligned']:
        cards = ' and '.join(str(k + 1) for k in d['slots'])
        where = f"card{'s' if len(d['slots']) > 1 else ''} {cards} of {n}"
        return (f"the replaced card{'s' if len(d['slots']) > 1 else ''} keep{'' if len(d['slots']) > 1 else 's'} {'their' if len(d['slots']) > 1 else 'its'} place in the deck file ({where}), "
                f"and so in the shuffle: the deals differ only in {'those cards' if len(d['slots']) > 1 else 'that card'}")
    no = 'does NOT keep its place' if upper else 'does not keep its place'
    return f'the replaced card {no} in the deck file ({len(d["slots"])} of the {n} places differ), so the deals differ in more than the swapped card'


def basic_text(d):
    if d.get('basic_shape') is False:
        return ('a Basic Pokémon is swapped for a card that is not one (or the other way round): the engine repairs a hand with no Basic by looking at which places hold a Basic and draws extra '
                "random numbers to do it, so the twin games' opening hands can differ before the card is drawn, and the opponent's shuffle, the first player and the Energy rolls can differ too")
    return None


# ------------------------------------------------------------------------------------------------------------------ the base report
class Base:
    def __init__(self, path, man, msha, block, repo):
        self.path, self.man, self.msha, self.block = path, man, msha, block
        self.deals, self.seed_base, self.threads = man['deals'], man['seed_base'], man.get('threads')
        self.compare = bool(block.get('paired'))
        self.school_rule = block.get('school_rule') or 'on'
        days = block.get('school_days')
        self.school_days = days if days is not None else SR.DEFAULT_SCHOOL_DAYS
        rel = os.path.relpath(path, repo).replace(os.sep, '/')
        self.folder = path if rel.startswith('..') else rel


def load_base(arg, repo):
    """The registered base report named by --paired-with, refused when it is not a folder, not a registered run, or its registration has changed."""
    path = os.path.abspath(arg)
    if not os.path.isdir(path):
        SR.die(f'REFUSED: --paired-with {arg}: {path} is not a folder')
    man, msha = SR.load_registered(path)
    block = man.get('slow_report')
    if not isinstance(block, dict) or not man.get('decks'):
        SR.die(f'REFUSED: --paired-with {arg}: {path} is not a slow report run (its manifest has no slow_report block)')
    return Base(path, man, msha, block, repo)


class Pairing:
    def __init__(self):
        self.lines, self.problems, self.notes, self.record, self.diff = [], [], [], None, None


def check(base, *, repo, pin, pin_path, program_sha, registry, panel_names, deck_abs, deck_rel, name, basic_check=None):
    """Everything a variant must share with its base, as a Pairing: the plan lines to print, the problems that refuse it (nothing is written while there are any), the notes, and
    the record that goes into the registration."""
    man, block, P = base.man, base.block, Pairing()
    if man.get('stage') != 'use' or len(man['decks']) != 1:
        P.problems.append('the base report is not a slow report of one deck')
    if man.get('program_sha256') != program_sha:
        P.problems.append(f"the program is not the one the base report was played with (this program {program_sha[:12]}, the base report's {str(man.get('program_sha256'))[:12]}): "
                          'a paired variant must be played by the same program')
    now, recorded = SR.sha(pin_path), (block.get('pin') or {}).get('sha256')
    if recorded != now:
        claims = {'pilot': pin['pilot'], 'reference': pin['reference'], 'pinned_program_sha256': pin['program_sha256'], 'harness_source_sha256': pin['harness_source_sha256'],
                  'engine_ref': pin.get('engine_ref'), 'engine_tree': pin.get('engine_tree'), 'scrub_env_prefixes': list(pin['scrub_env_prefixes'])}
        have = dict(block, pilot=man.get('pilot'), reference=man.get('reference'))
        differ = [k for k, v in claims.items() if have.get(k) != v]
        if differ:
            P.problems.append(f"the pin is not the one the base report was registered under (sha256 {str(recorded)[:12]}, now {now[:12]}) and these entries differ: {', '.join(differ)}")
        else:
            P.notes.append(f"the pin file's bytes differ from the base report's (sha256 {str(recorded)[:12]}, now {now[:12]}), but the program, harness source and engine it names are the same")
    if man.get('seats') != [0, 1] or man.get('pair_stride') != SR.PAIR_STRIDE:
        P.problems.append(f"the base report's seats or seed stride are not the slow report's own ({man.get('seats')}, {man.get('pair_stride')})")
    base_panel = [(o.get('name'), o.get('sha256')) for o in man.get('opponents', [])]
    if [n for n, _ in base_panel] != list(panel_names):
        P.problems.append(f"the panel is not the base report's ({', '.join(n for n, _ in base_panel)} v {', '.join(panel_names)})")
    else:
        for n, s in base_panel:
            try:
                changed = SR.sha(os.path.join(repo, *registry[n].split('/'))) != s
            except (OSError, KeyError):
                changed = True
            if changed:
                P.problems.append(f'panel list {n} has changed since the base report was registered (or is missing here), so the twins would not face the same opponents')
    bd = man['decks'][0]
    bpath = os.path.join(repo, *bd['path'].split('/'))
    try:
        with open(bpath, 'rb') as f:
            base_text = f.read()
        if SR.sha(bpath) != bd.get('sha256'):
            P.problems.append(f"the base deck file {bd['path']} has changed since the base report was registered (sha256 {str(bd.get('sha256'))[:12]}, now {SR.sha(bpath)[:12]})")
    except OSError:
        base_text = None
        P.problems.append(f"the base deck file {bd['path']} is not in this checkout")
    with open(deck_abs, 'rb') as f:
        variant_text = f.read()
    d = P.diff = diff_decks(base_text if base_text is not None else b'', variant_text, basic_check)
    if base_text is not None:
        P.problems.extend(d['problems'])
    base_name = block.get('deck_name') or bd['name']
    P.lines.append(f"paired with {base.folder}: {base_name} -> {name}: {swap_text(d) or 'no card swapped'}")
    if d['swaps']:
        P.lines.append(place_text(d, upper=True))
        if basic_text(d):
            P.lines.append('note: ' + basic_text(d))
    P.lines.append(f"seeds from {base.seed_base}, the base report's: no new seed slot is taken; {base.deals} deals, the base report's seats, opponents, program and pin, "
                   f"{base.threads} threads, school rule {base.school_rule} as there")
    P.lines.extend(f'note: {n}' for n in P.notes)
    P.record = dict(folder=base.folder, manifest_sha256=base.msha, base_deck_name=base_name, base_deck_file=bd['path'], base_deck_sha256=bd.get('sha256'),
                    swaps=d['swaps'], removed=d['removed'], added=d['added'], slots=d['slots'], aligned=d['aligned'], basic_shape=d['basic_shape'], cards=d['cards'],
                    pin_note='; '.join(P.notes) or None, seed_base=base.seed_base)
    return P


def question_text(rec, variant_name):
    """The sentence the registration adds to its question: what it is paired with and what differs."""
    return (f" This is a PAIRED VARIANT, paired with {rec['folder']}, which played {rec['base_deck_name']}: {variant_name} differs from it by {swap_text(rec)}"
            f" ({place_text(rec)}). It plays the very same deals, with the same program and pin: the same seed base {rec['seed_base']} (no new seed slot is taken), seats, opponents and panel lists.")


def default_basic_check(repo):
    """id ('a3 149') -> True / False / None (not in the database) from lib/deckgym-database.json, in the checkout or, failing that, beside this script."""
    cache = {}

    def load():
        if 'is_basic' not in cache:
            table = {}
            for root in (repo, SR.ROOT):
                p = os.path.join(root, 'lib', 'deckgym-database.json')
                if os.path.isfile(p):
                    with open(p, encoding='utf-8') as f:
                        for e in json.load(f):
                            for kind, v in e.items():
                                if isinstance(v, dict) and 'id' in v:
                                    table[v['id'].lower()] = kind == 'Pokemon' and v.get('stage') == 0
                    break
            cache['is_basic'] = table
        return cache['is_basic']
    return lambda card_id: load().get(card_id)


# ------------------------------------------------------------------------------------------------------------------ the logged moves
def load_card_data(root):
    """(card_info, name_of, is_tool): card_info(name) = (cheapest attack's Energy count, retreat cost) of a Pokémon by name (the lowest over its printings; (None, None) when unknown),
    name_of(id) = the card's name from lib/deckgym-database.json (None when unknown), and is_tool(name) = whether a Trainer's text says it is attached to a Pokémon."""
    cost, names, tools = {}, {}, set()
    p = os.path.join(root, 'lib', 'deckgym-database.json')
    if os.path.isfile(p):
        with open(p, encoding='utf-8') as f:
            for e in json.load(f):
                for kind, v in e.items():
                    if not isinstance(v, dict) or 'id' not in v:
                        continue
                    names[v['id'].lower()] = v.get('name')
                    if kind != 'Pokemon' and 'attached to' in (v.get('effect') or ''):
                        tools.add(v.get('name'))
                    if kind == 'Pokemon' and v.get('attacks'):
                        a = min(len(x.get('energy_required') or []) for x in v['attacks'])
                        r = len(v.get('retreat_cost') or [])
                        old = cost.get(v['name'])
                        cost[v['name']] = (a, r) if old is None else (min(old[0], a), min(old[1], r))
    return (lambda name: cost.get(name, (None, None))), (lambda card_id: names.get(card_id)), (lambda name: name in tools)


def _find_bench(slots, name):
    c = [k for k in (1, 2, 3) if k in slots and slots[k][0] == name]
    return max(c, key=lambda k: slots[k][1]) if c else None


def walk(g, info):
    """The deck side's logged moves replayed on a board of four places (0 the Active, 1-3 the Bench; each holds [name, Energy count]). The log has no setup and no opponent moves, so the
    board is learned from what the log shows (`act` is the Active's name at each move) and `warnings` counts the times it had to guess. Returns None for a game without a log, else
    {'turns': {our turn t: {logged, attacked, retreated, name, energy}}, 'first_ko': whether the opponent's first point knocked out the opening Active (None: no point), 'opening',
    'tools': [(t, card, 'Active'|'Bench', Pokémon name)], 'plays': [(t, card)], 'warnings'}."""
    log = g.get('log')
    if not log:
        return None
    parity = 1 if g.get('first') == 'deck' else 0
    by_turn = collections.defaultdict(list)
    for e in log:
        by_turn[e['t']].append(e)
    slots, last_p, ko_pending, warnings = {}, [0, 0], False, 0
    opening, intact, first_ko, first_maybe = None, True, None, False
    seat = g.get('seat')   # our seat: an Activate names the player whose Pokémon comes up, so one that names the other seat is the opponent's board
    tools, plays, places, turns = [], [], [], {}
    for t in sorted(set(by_turn) | set(range(1, int(g.get('turns') or 0) + 1))):
        rec = dict(logged=bool(by_turn.get(t)), attacked=False, retreated=False, name='', energy=0)
        for e in by_turn.get(t, []):
            a, act, pts = e['a'], e.get('act') or '', e['p']
            if pts[1] > last_p[1]:
                if first_ko is None:  # the opponent's first point: a knock-out of the Active (a forced Promote, or the Active's name changing under the replay) or of a Benched Pokémon
                    active = a.startswith('Promote') or bool(act and (0 not in slots or act != slots[0][0]))
                    first_ko = bool(active and intact and slots.get(0))
                    # no Promote and the name in front unchanged, but a Pokémon of that name is on the Bench: its forced promotion is not logged, so this may be the Active's knock-out
                    first_maybe = bool(not active and intact and slots.get(0) and _find_bench(slots, slots[0][0]) is not None)
                ko_pending = True
            last_p = list(pts)
            if ko_pending and not a.startswith('Promote:'):
                if act:
                    slots.pop(0, None)
                    k = _find_bench(slots, act)
                    if k is not None:
                        slots[0] = slots.pop(k)
                    else:
                        slots[0] = [act, 0]
                        warnings += 1
                    ko_pending = False
            elif act and t > 0 and (0 not in slots or slots[0][0] != act) and not a.startswith('Promote:'):
                if 0 not in slots:
                    slots[0] = [act, 0]
                    opening = opening or act
                else:
                    intact = False
                    k = _find_bench(slots, act)
                    if k is not None:
                        slots[0], slots[k] = slots[k], slots[0]
                    else:
                        warnings += 1
                        slots[0] = [act, 0]
            try:
                if a.startswith('Place:'):
                    nm, k = a[6:].rsplit('@', 1)
                    slots[int(k)] = [nm, 0]
                    places.append((t, nm))
                elif a.startswith('Attach:'):
                    for part in a[len('Attach:'):].split(' ')[0].split('+'):   # "1Water@0" or "1Water@0+1Water@1": the Energy count, its type, the place
                        m = re.match(r'(\d+)\D*@(\d+)$', part)
                        k = int(m.group(2))
                        if k in slots:
                            slots[k][1] += int(m.group(1))
                        else:
                            warnings += 1
                elif a.startswith('Evolve:'):
                    nm, k = a[7:].rsplit('@', 1)
                    k = int(k)
                    if k in slots:
                        slots[k][0] = nm
                    else:
                        slots[k] = [nm, 0]
                        warnings += 1
                    if k == 0:
                        intact = False
                    places.append((t, nm))
                elif a.startswith('Ability:'):
                    title, k = a[8:].rsplit('@', 1)
                    if title in ENERGY_ABILITIES and int(k) in slots:
                        slots[int(k)][1] += 1
                elif a.startswith('Retreat:'):
                    k, old = int(a.split(':')[1]), slots.get(0)
                    if old:
                        old[1] = max(0, old[1] - (info(old[0])[1] or 0))
                    if k in slots:
                        slots[0] = slots[k]
                    else:
                        warnings += 1
                        slots.pop(0, None)
                    if old:
                        slots[k] = old
                    rec['retreated'], intact = True, False
                elif a.startswith('Promote:'):
                    k = int(a.split('@')[1])
                    slots.pop(0, None)
                    if k in slots:
                        slots[0] = slots.pop(k)
                    else:
                        warnings += 1
                    ko_pending, intact = False, False
                elif a.startswith('Activate:'):
                    k, old = int(a.split('@')[1]), slots.get(0)
                    if seat is not None and int(a.split(':')[1].split('@')[0]) != seat:
                        pass   # our Cyrus or Sabrina bringing up the opponent's Pokémon: nothing changes on our board
                    else:
                        if k in slots:
                            slots[0] = slots[k]
                        if old:
                            slots[k] = old
                        intact = False
                elif a == 'ReturnPokemonToHand':
                    intact = False
                elif a.startswith('Attack:'):
                    rec['attacked'] = True
                elif a.startswith('Tool:'):
                    nm, k = a[5:].rsplit('@', 1)
                    tools.append((t, nm, 'Active' if int(k) == 0 else 'Bench', slots[int(k)][0] if int(k) in slots else None))
                elif a.startswith('Play:'):
                    plays.append((t, a[5:]))
            except (ValueError, IndexError, AttributeError):
                warnings += 1   # a label this replay does not understand
        if rec['logged'] and 0 in slots:
            rec['name'], rec['energy'] = slots[0][0], slots[0][1]
        if t >= 1 and t % 2 == parity:
            turns[t] = rec
    if first_ko is None and g.get('points') and g['points'][1] > last_p[1]:
        first_ko = bool(intact and slots.get(0))   # the point that ended the game: the Active, as no move of ours follows it
    return dict(turns=turns, first_ko=first_ko, first_maybe=first_maybe and not first_ko, opening=opening, tools=tools, plays=plays, places=places, warnings=warnings)


def charged_idle_turns(g, info):
    """Our turns on which the Active could pay for its cheapest attack, did not attack and did not retreat: {own_turns, idle, idle_ex (the Pokémon an ex), attacked, warnings}.
    None for a game without a log. An indicator of Sleep or Paralysis, not a measurement: it also counts a turn on which the pilot chose not to attack."""
    w = walk(g, info)
    if w is None:
        return None
    out = dict(own_turns=len(w['turns']), idle=0, idle_ex=0, attacked=0, warnings=w['warnings'])
    for rec in w['turns'].values():
        if not rec['logged']:
            continue
        if rec['attacked']:
            out['attacked'] += 1
            continue
        cost = info(rec['name'])[0]
        if cost is not None and rec['energy'] >= cost and not rec['retreated']:
            out['idle'] += 1
            out['idle_ex'] += rec['name'].endswith(' ex')
    return out


def first_point(g, info=None):
    """{opening (the name of the Active at our first logged move), scored (the opponent scored), opening_ko (the opponent's first point was a knock-out of that Pokémon, never
    evolved, retreated or switched)}; None for a game without a log."""
    w = walk(g, info or (lambda name: (None, None)))
    if w is None:
        return None
    scored = w['first_ko'] is not None
    return dict(opening=w['opening'], scored=scored, opening_ko=bool(w['first_ko']), opening_ko_maybe=bool(w['first_maybe']), warnings=w['warnings'])


def card_use(g, card, info):
    """How a card was used in a game: {played (times), turns (our turn numbers), targets [(Pokémon name, 'Active'|'Bench')] for a Tool}; None for a game without a log."""
    w = walk(g, info)
    if w is None:
        return None
    own = lambda t: (t + 1) // 2 if g.get('first') == 'deck' else t // 2
    mine = [t for t, c in w['plays'] + w['places'] if c == card]   # a Trainer is played; a Pokémon is placed or evolved into play
    return dict(played=len(mine), turns=[own(t) for t in mine], targets=[(nm, where) for _, c, where, nm in w['tools'] if c == card])


# ------------------------------------------------------------------------------------------------------------------ the page
def locate_base(rundir, rec):
    """The base report's folder: beside this one, or in the checkout this script is in."""
    name = os.path.basename(rec['folder'].rstrip('/'))
    in_checkout = rec['folder'] if os.path.isabs(rec['folder']) else os.path.join(SR.ROOT, *rec['folder'].split('/'))
    for c in (os.path.join(os.path.dirname(os.path.abspath(rundir)), name), in_checkout):
        if os.path.isdir(c):
            return c
    return None


def diff_range(xs):
    """(n, mean, half-width of the 95% t range or None)."""
    n = len(xs)
    if n == 0:
        return 0, 0.0, None
    m = statistics.mean(xs)
    if n < 2:
        return n, m, None
    sd = statistics.stdev(xs)
    return n, m, SR.t_crit(n - 1) * sd / math.sqrt(n)


def range_cell(m, half):
    if half is None:
        return 'n/a'
    return f'{SR.signed_points(m)} ({SR.signed_points(max(-1.0, m - half))} to {SR.signed_points(min(1.0, m + half))})'


def change_note(who, n, m, half):
    """In plain words what the range of the score change (m +- half, fractions, over n twin games) does and does not include; never waves a wide range away."""
    lo, hi = max(-1.0, m - half), min(1.0, m + half)
    if hi - lo >= 2 - 1e-9:
        return f"That range is as wide as the whole possible scale: {SR.plural(n, 'twin game')} are too few to say anything about the change yet."
    if lo <= 0 <= hi:
        return (f"That range includes no change at all: these {SR.plural(n, 'twin game')} do not show that the change helped {who} or that it hurt. They argue against a change much "
                f"larger than {100 * max(abs(lo), hi):.1f} points; a smaller one needs more deals.")
    return f"That range does not include no change: on these {SR.plural(n, 'twin game')} {who} scored {'better' if lo > 0 else 'worse'} with the change."


def pct(xs):
    return SR.pct1(statistics.mean(xs)) if xs else 'n/a'


def card_line_name(line):
    """'1 Giant Cape A2 147' -> 'Giant Cape'."""
    return ' '.join(line.split()[1:-2])


def times(n):
    return f"{n} time{'' if n == 1 else 's'}"


NOT_COUNTABLE = {
    'Giant Cape': "how often the Cape holder survived an attack it would not have survived without the +20: the records hold no Hit Points or damage and not the opponent's attacks, so it cannot be counted",
    'Big Malasada': 'which Special Condition it removed, and whether the Active had one when it was played: the engine picks the condition at random and the choice is not recorded '
                    '(the log has the move "Play:Big Malasada" and nothing else)',
}
OPENING_NOTE = ("Sleep is not recorded. The row on turns a charged Pokémon did not attack is an indicator of it (and of Paralysis): it also counts a turn on which the pilot chose not to "
                'attack or retreat. It is read on twins that started alike, so the difference between the columns is the better reading than either number.')


def comparison_lines(rundir, man, games, card_info=None, name_of=None):
    """The section "Compared with the base report" of a paired variant's page, as lines."""
    rec = man['slow_report']['paired_with']
    L = ['## Compared with the base report\n']
    base_dir = locate_base(rundir, rec)
    if base_dir is None:
        L.append(f"The base report `{rec['folder']}` is not here (looked beside this folder and in the checkout this script is in), so nothing is compared. Put its folder next to this one to compare.\n")
        return L
    try:
        bman, bmsha = SR.load_registered(base_dir)
    except SystemExit as e:
        L.append(f"The base report at `{base_dir}` cannot be used: {str(e.code).splitlines()[0]} Nothing is compared.\n")
        return L
    if bmsha != rec['manifest_sha256']:
        L.append(f"The base report's manifest.json is not the one this report was paired with (sha256 {bmsha[:12]} now, {str(rec['manifest_sha256'])[:12]} when this report was registered), so nothing is compared.\n")
        return L
    pilot, ref = man['pilot'], man['reference']
    bgames = SR.load_games(base_dir)
    twin = lambda g: (g['opp'], g['deal'], g['seat'], g['arm'])
    bmap = {twin(g): g for g in bgames}
    pairs = [(bmap[twin(g)], g) for g in games if twin(g) in bmap]
    deck, base_name = man['slow_report']['deck_name'], rec['base_deck_name']
    L.append(f"Base: `{rec['folder']}` ({base_name}). This deck, {deck}, differs from it by {swap_text(rec)}. Each game below is set against its twin in the base report: the same "
             f"opponent, deal, seat and pilot, so the same seed. {place_text(rec).capitalize()}.\n")
    if basic_text(rec):
        L.append(f'Note: {basic_text(rec)}.\n')
    if len(pairs) != len(games) or len(pairs) != len(bgames):
        L.append(f"Only games played in both reports are compared: {len(pairs)} of the {len(games)} games of this report have a twin in the base report ({len(bgames)} games there).\n")
    by_arm = {arm: [(b, v) for b, v in pairs if v['arm'] == arm] for arm in ('X', 'ref')}
    who = {'X': pilot, 'ref': ref}
    if not pairs:
        L.append('No game has a twin yet.\n')
        return L
    changes = program_changes(rundir, man)
    if changes:
        L.append(f"Note: the program changed {times(changes)} during this run (see What was run), so the twins played after the change were not played by the program that played the base report.\n")
    L.append('### What the change did to the score\n')
    L.append(f'| pilot | twin games | base | {deck} | {deck} minus base |')
    L.append('|---|---|---|---|---|')
    notes = []
    for arm in ('X', 'ref'):
        ps = by_arm[arm]
        if not ps:
            continue
        bs, vs = [SR.SCORE[b['winner']] for b, _ in ps], [SR.SCORE[v['winner']] for _, v in ps]
        n, m, half = diff_range([v - b for b, v in zip(bs, vs)])
        L.append(f'| {who[arm]} | {n} | {pct(bs)} | {pct(vs)} | {SR.signed_points(m)} |')
        same = sum(1 for b, v in ps if b['winner'] == v['winner'])
        line = f"{who[arm]}: {SR.signed_points(m)} points on the same deals" + (f", {SR.range_points(m, half)} (95% interval; this range refers to those {SR.plural(n, 'twin game')})" if half is not None else ' (too few twins for a range)')
        line += f". {same} of the {n} {who[arm]} twins ended the same way (win, tie or loss)"
        logged = [(b, v) for b, v in ps if b.get('log') is not None and v.get('log') is not None]
        if logged:
            clean = lambda g: ([{k: x for k, x in e.items() if k != 'ms'} for e in g['log']], g['points'], g['winner'], g.get('turns'), g.get('plies'))
            line += f"; of the {len(logged)} with a log on both sides, {sum(1 for b, v in logged if clean(b) == clean(v))} were the same game from start to finish"
        differ = sum(1 for b, v in ps if b.get('first') != v.get('first'))
        line += f". Who went first {'was the same in all ' + str(n) if not differ else 'differed in ' + str(differ) + ' of the ' + str(n)} {who[arm]} twins"
        notes.append(line + '.' + (' ' + change_note(who[arm], n, m, half) if half is not None else ''))
    L.append('')
    L.extend(l + '\n' for l in notes)
    L.append('A change of one card is usually too small for these ranges to show it; the counts further down, of whether the card did its job, say more.\n')
    panel = [o['name'] for o in man['opponents']]
    L.append('### Each public list, compared with the base\n')
    L.append(f'| opponent | {pilot}: twins | base | {deck} | difference (95% range) | {ref}: base | {deck} | difference (95% range) |')
    L.append('|---|---|---|---|---|---|---|---|')
    for opp in panel:
        cells = []
        for arm in ('X', 'ref'):
            ps = [(b, v) for b, v in by_arm[arm] if v['opp'] == opp]
            if not ps:
                cells.append(['0', 'n/a', 'n/a', 'n/a'] if arm == 'X' else ['n/a', 'n/a', 'n/a'])
                continue
            bs, vs = [SR.SCORE[b['winner']] for b, _ in ps], [SR.SCORE[v['winner']] for _, v in ps]
            n, m, half = diff_range([v - b for b, v in zip(bs, vs)])
            cells.append(([str(n)] if arm == 'X' else []) + [pct(bs), pct(vs), range_cell(m, half)])
        L.append(f'| {opp} | ' + ' | '.join(' | '.join(c) for c in cells) + ' |')
    L.append('\nEach range refers to the twins on its row (the t range of their score differences); a row has few of them, so it can show a large change, not a small one.\n')
    L.extend(job_lines(rec, by_arm, who, panel, card_info, name_of))
    return L


def program_changes(rundir, man):
    """How many times the program was changed during the run (the lines of its log that the page counts as 'program changed mid-run')."""
    msha = SR.manifest_sha256(rundir)
    log = SR.load_jsonl(os.path.join(rundir, 'slow_report_log.jsonl'))
    legacy = SR.log_started_for(log, msha)
    return sum(1 for e in log if SR.is_program_change(e, man, msha, legacy))


def safe(fn, *args):
    """fn(*args), or None (a game with no usable log) when the record is not one the program writes: a page must never fail on a record."""
    try:
        return fn(*args)
    except (KeyError, TypeError, ValueError, IndexError, AttributeError):
        return None


def console_summary(text):
    """The lines of a paired variant's page worth echoing to the terminal: the score change of each pilot, without markdown ([] for any other page)."""
    if '## Compared with the base report' not in text:
        return []
    sec = text.split('## Compared with the base report')[1].split('\n## ')[0].split('\n### Each public list')[0]
    return ['compared with the base report: ' + l.replace('**', '').replace('`', '').strip() for l in sec.splitlines() if ' points on the same deals' in l]


def job_lines(rec, by_arm, who, panel, card_info, name_of, is_tool=None):
    """"Did the card do its job?": counts from the logged moves, per pilot, base against this deck; and what the records cannot give."""
    info = card_info
    if info is None:
        info, name_of, is_tool = load_card_data(SR.ROOT)
    cards = []
    for line in rec['removed'] + rec['added']:
        shown = card_line_name(line)
        db_name = name_of(' '.join([line.split()[-2].lower(), line.split()[-1].zfill(3)])) if name_of else None
        cards.append(db_name or shown)
    L = ['### Did the card do its job?\n',
         "Counted from the logged moves of the deck's side, which hold the deck's own moves and the points and nothing else (no Hit Points, damage, Special Conditions or opponent moves). "
         "A game without a log counts as no play.\n"]
    for arm in ('X', 'ref'):
        ps = by_arm[arm]
        if not ps:
            continue
        if not any(g.get('log') for pair in ps for g in pair):
            L.append(f'{who[arm]}: no game of this arm has a log (the run was made without one), so nothing is counted.\n')
            continue
        N = len(ps)
        L.append(f'#### {who[arm]} ({N} twin games)\n')
        L.append(f'| | base | this deck |')
        L.append('|---|---|---|')
        for card in dict.fromkeys(cards):
            used = [[safe(card_use, g, card, info) for g in (b, v)] for b, v in ps]   # [(base use, variant use)]
            cell = []
            for side in (0, 1):
                uses = [u[side] for u in used if u[side] is not None]
                plays = sum(u['played'] for u in uses)
                cell.append(f"{times(plays)} in {sum(1 for u in uses if u['played'])} of {N} games")
            L.append(f'| {card} played | {cell[0]} | {cell[1]} |')
            if any(u['targets'] for pair in used for u in pair if u) or (is_tool and is_tool(card)):
                forced = [sum(u[s]['played'] - len(u[s]['targets']) for u in used if u[s]) for s in (0, 1)]
                cell = []
                for side in (0, 1):
                    tg = [t for u in used if u[side] for t in u[side]['targets']]
                    if not tg:
                        cell.append('nothing')
                        continue
                    act, ben = sum(1 for _, w in tg if w == 'Active'), sum(1 for _, w in tg if w == 'Bench')
                    names = collections.Counter(n or 'a Pokémon not seen on the board' for n, _ in tg)
                    cell.append(f"the Active Pokémon {act}, a Benched Pokémon {ben}; " + ', '.join(f'{n} {c}' for n, c in sorted(names.items())))
                L.append(f'| {card} went to | {cell[0]} | {cell[1]} |')
                L.append(f'| {card} put on with only one place to put it, so nothing to log | {forced[0]} | {forced[1]} |')
        fp = [[safe(first_point, g, info) for g in (b, v)] for b, v in ps]
        idle = [[safe(charged_idle_turns, g, info) for g in (b, v)] for b, v in ps]
        row = lambda label, f: L.append(f'| {label} | {f(0)} | {f(1)} |')
        row('games where the opponent scored', lambda s: sum(1 for p in fp if p[s] and p[s]['scored']))
        row("games where the opponent's first point was a knock-out of our opening Pokémon (never evolved or moved)", lambda s: sum(1 for p in fp if p[s] and p[s]['opening_ko']))
        row("games where the opponent's first point was the opening Pokémon or a benched Pokémon of the same name (cannot be told apart)", lambda s: sum(1 for p in fp if p[s] and p[s]['opening_ko_maybe']))
        row('turns a charged Pokémon did not attack, all lists', lambda s: sum(i[s]['idle'] for i in idle if i[s]))
        if 't-altaria' in panel:
            alt = [i for i, (_, v) in zip(idle, ps) if v['opp'] == 't-altaria']
            row('turns a charged Pokémon did not attack, against t-altaria', lambda s: sum(i[s]['idle'] for i in alt if i[s]))
        row('our turns in all, for scale', lambda s: sum(i[s]['own_turns'] for i in idle if i[s]))
        lost = sum(i[s]['warnings'] for i in idle for s in (0, 1) if i[s])
        L.append(f"\nThe replay of the moves lost track of the board {lost} times in these {N * 2} games ({who[arm]}); it sees only the deck's own moves, so a benched Pokémon from the setup is unknown to it.\n")
    L.append('Not countable from these records:\n')
    for card in dict.fromkeys(cards):
        if card in NOT_COUNTABLE:
            L.append(f'- {NOT_COUNTABLE[card]}.')
    L.append(f'- {OPENING_NOTE}\n')
    return L


def run_lines(sr):
    """The lines of "What was run" that name the base report."""
    rec = sr['paired_with']
    out = [f"- Paired with `{rec['folder']}` ({rec['base_deck_name']} -> {sr['deck_name']}: {swap_text(rec)}): the same seeds `{rec['seed_base']} + p x 10,000 + i`, deals, seats, opponents, program and pin, "
           f"so each game here has a twin in that report; no new seed slot was taken. {place_text(rec).capitalize()}."]
    if basic_text(rec):
        out.append(f'- {basic_text(rec).capitalize()}.')
    if rec.get('pin_note'):
        out.append(f"- {rec['pin_note'].capitalize()}.")
    return out

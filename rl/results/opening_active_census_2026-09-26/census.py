#!/usr/bin/env python3
"""Opening Active census (Sept 26, 2026). Code reading and list arithmetic only: no engine game, no build.

For every list in scope (decks/research, decks/dustin, decks/brews, the six B2e archetype lists) this prints and
writes census.json:
  - each Basic Pokemon in the list, with the engine mechanic flag its Ability maps to
    (engine/src/actions/effect_ability_mechanic_map.rs), the class that flag falls in (VARIANT_CLASS below,
    keyed on mechanic variants and their fields, never on card names), and the setup-relevant numbers
    (HP, Retreat, knockout points, attack costs, whether it evolves in the list);
  - how often an opening choice exists, exactly, from the list counts under the engine's deal
    (engine/src/deck.rs 129-149: five random cards; a hand with no Basic swaps one card for a random Basic);
  - which Basic k3/kp3 open today, exactly, from the setup scoring they use
    (engine/src/players/value_functions.rs 459-478, see README section 2);
  - how often the draft candidate's two switches (REGISTRATION_DRAFT.md) would change that opening.

Run from anywhere: python census.py  (Python 3, standard library only).
"""
import io, itertools, json, math, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
ENGINE = os.path.join(ROOT, 'engine', 'src')

# ---------------------------------------------------------------------------------------------
# Pre-set constants of the draft candidate (REGISTRATION_DRAFT.md). Not tuned on any table.
W_ACTIVE_ONLY_FIRST_TURN = 250.0   # switch A: half the Active online-score weight (500), the kq precedent
W_BENCH_WORKING = 250.0            # switch B: same
ONLINE_WEIGHT = 500.0              # ValueFunctionParams::baseline().active_pokemon_online_score

# ---------------------------------------------------------------------------------------------
# Where each Ability mechanic works, read from the engine: the activation gate in
# move_generation/move_generation_abilities.rs 55-288 for activated Abilities, the hook for passive ones.
#   pos:   'active'  works only while the holder is in the Active Spot
#          'bench'   works only while the holder is on the Bench
#          'anywhere' works from the Active Spot and the Bench
#          'bench_entry' fires when the holder is put from the hand onto the Bench
#          'evolve'  fires when the holder is played to evolve (irrelevant to the opening placement)
#   first: True when the Ability only matters during its owner's first turn
#   scope: 'self' (acts on the holder only) or 'board' (acts on other Pokemon, the opponent, or the owner's draws)
#   drawback: the Ability hurts its holder while Active
# Field-dependent variants are resolved in classify() from the variant's own fields.
VARIANT_CLASS = {
    'AncientRoar': ('bench_entry', False, 'board'),
    'AttachEnergyFromDiscardToActiveTypedFromBench': ('bench', False, 'board'),
    'AttachEnergyFromDiscardToSelfAndDamage': ('anywhere', False, 'self'),
    'AttachEnergyFromZoneToActiveTypedOnEvolve': ('evolve', False, 'board'),
    'AttachEnergyFromZoneToActiveTypedPokemon': ('anywhere', False, 'board'),
    'AttachEnergyFromZoneToBenchOnDamaged': ('active', False, 'board'),
    'AttachEnergyFromZoneToSelf': ('anywhere', False, 'self'),
    'AttachEnergyFromZoneToSelfAndDamage': ('anywhere', False, 'self'),
    'AttachEnergyFromZoneToSelfAndEndTurn': ('anywhere', False, 'self'),
    'AttachEnergyFromZoneToYourTypedPokemon': ('active', False, 'board'),
    'BadDreamsEndOfTurn': ('anywhere', False, 'board'),
    'BurnOpponentActive': ('anywhere', False, 'board'),
    'CanEvolveIntoEeveeEvolution': ('anywhere', False, 'self'),
    'CanEvolveOnFirstTurnIfActive': ('active', True, 'self'),
    'CannotAttackWithoutBenchedNames': ('active', False, 'self', 'drawback'),
    'CheckupDamageToAllOpponentPokemon': ('active', False, 'board'),
    'CheckupDamageToOpponentActive': ('active', False, 'board'),
    'CheckupHealAllYourPokemon': ('anywhere', False, 'board'),
    'CoinFlipParalyzeOpponentActiveOnEvolve': ('evolve', False, 'board'),
    'CoinFlipStatusOpponentActive': ('anywhere', False, 'board'),
    'CoinFlipSwitchInOpponentBenchToActive': ('anywhere', False, 'board'),
    'CoinFlipToDenyKnockoutPoints': ('anywhere', False, 'self'),
    'CoinFlipToKnockOutAttackerOnKnockout': ('active', False, 'board'),
    'CoinFlipToPreventDamage': ('anywhere', False, 'self'),
    'CoinFlipToReduceDamage': ('anywhere', False, 'self'),
    'CoinFlipToSurviveKnockOut': ('anywhere', False, 'self'),
    'ConfuseOpponentActive': ('active', False, 'board'),
    'CoordinatedUnit': ('anywhere', False, 'self'),
    'CopyRandomOpponentHandSupporter': ('active', False, 'board'),
    'CounterattackDamage': ('active', False, 'board'),
    'DamageOnKnockoutInActive': ('active', False, 'board'),
    'DamageOneOpponentPokemon': ('anywhere', False, 'board'),
    'DamageOpponentActiveIfArceusInPlay': ('anywhere', False, 'board'),
    'DamageOpponentActiveOnEvolve': ('evolve', False, 'board'),
    'DamageOpponentActiveOnZoneAttachToSelf': ('anywhere', False, 'board'),
    'DiscardEnergyToIncreaseTypeDamage': ('anywhere', False, 'board'),
    'DiscardFromHandToDrawCard': ('anywhere', False, 'board'),
    'DiscardOpponentActiveToolsAndDiscardSelf': ('bench', False, 'board'),
    'DiscardRandomEnergyFromOpponentActiveOnEvolve': ('evolve', False, 'board'),
    'DiscardTopCardOpponentDeck': ('anywhere', False, 'board'),
    'DoubleGrassEnergy': ('anywhere', False, 'board'),
    'DrawCardsOnEvolve': ('evolve', False, 'board'),
    'DrawCardsOncePerTurn': None,  # require_active
    'DualType': ('anywhere', False, 'self'),
    'ElectromagneticWall': ('active', False, 'board'),
    'EndFirstTurnAttachEnergyToSelf': ('anywhere', True, 'self'),
    'EndTurnDrawCardIfActive': ('active', False, 'board'),
    'EndTurnHealSelfIfActive': ('active', False, 'self'),
    'HealActiveTypedOnBenchFromHand': ('bench_entry', False, 'board'),
    'HealActiveYourPokemon': ('anywhere', False, 'board'),
    'HealAllYourPokemon': ('anywhere', False, 'board'),
    'HealOneYourPokemon': None,  # require_active
    'HealOneYourPokemonExAndDiscardRandomEnergy': ('anywhere', False, 'board'),
    'HealSelfOnZoneAttach': ('anywhere', False, 'self'),
    'HealTypedPokemonOnEvolve': ('evolve', False, 'board'),
    'ImmuneToStatusConditions': ('anywhere', False, 'self'),
    'IncreaseAttackCostForOpponentActive': ('active', False, 'board'),
    'IncreaseDamageForEvolutionsFromBench': ('bench', False, 'board'),
    'IncreaseDamageForTwoTypesInPlay': ('anywhere', False, 'board'),
    'IncreaseDamageForTypeInPlay': ('anywhere', False, 'board'),
    'IncreaseDamageIfArceusInPlay': ('anywhere', False, 'self'),
    'IncreaseDamageWhenRemainingHpAtMost': ('anywhere', False, 'self'),
    'IncreaseHpForTypeInPlay': ('anywhere', False, 'board'),
    'IncreaseHpPerAttachedEnergy': ('anywhere', False, 'self'),
    'IncreasePoisonDamage': ('anywhere', False, 'board'),
    'IncreaseRetreatCostForOpponentActive': ('anywhere', False, 'board'),
    'InfiltratingInspection': ('bench_entry', False, 'board'),
    'LegendaryDrive': ('bench_entry', False, 'board'),
    'LookAtTopCardOfDeck': ('anywhere', False, 'board'),
    'LookAtTopCardsPutTrainerTypeToHandOnEvolve': ('evolve', False, 'board'),
    'LuxuryCoin': ('anywhere', False, 'board'),
    'MoveAllTypedEnergyFromBenchToActive': ('anywhere', False, 'board'),
    'MoveAllTypedEnergyFromYourPokemonToSelf': ('anywhere', False, 'self'),
    'MoveAllTypedEnergyToBenchOnKnockout': ('active', False, 'board'),
    'MoveDamageFromOneYourPokemonToThisPokemon': ('anywhere', False, 'board'),
    'MoveFixedDamageFromActiveToThisBenched': ('bench', False, 'board'),
    'MoveRandomEnergyFromOpponentActiveToSelfOnEvolve': ('evolve', False, 'board'),
    'MoveTypedEnergyFromBenchToActive': ('anywhere', False, 'board'),
    'NoOpponentStadiumInActive': ('active', False, 'board'),
    'NoOpponentSupportInActive': ('active', False, 'board'),
    'NoRetreatCost': None,  # target, condition
    'NoRetreatIfHasEnergy': ('anywhere', False, 'self'),
    'OpponentShuffleHandAndDrawOnEvolve': ('evolve', False, 'board'),
    'PoisonAndBurnOpponentActiveOnEvolve': ('evolve', False, 'board'),
    'PoisonAttackerOnDamaged': ('active', False, 'board'),
    'PoisonOpponentActive': ('active', False, 'board'),
    'PreventAllDamageAndEffectsOnEvolve': ('evolve', False, 'self'),
    'PreventAllDamageFromEx': ('anywhere', False, 'self'),
    'PreventAllHealing': ('anywhere', False, 'board'),
    'PreventAttackEffects': ('anywhere', False, 'self'),
    'PreventDamageWhileBenched': ('bench', False, 'self'),
    'PreventFirstAttack': ('anywhere', False, 'self'),
    'PreventOpponentActiveEvolution': ('anywhere', False, 'board'),
    'ProtectSelfNextTurnAfterAttackKnockout': ('anywhere', False, 'self'),
    'PutCardsFromDiscardToHandOnEvolve': ('evolve', False, 'board'),
    'RandomEvolutionFromDeck': None,  # trigger
    'RandomStatusConditionToOpponentActive': ('anywhere', False, 'board'),
    'ReduceAttackCost': None,  # scope
    'ReduceDamageAtFullHp': ('anywhere', False, 'self'),
    'ReduceDamageFromAttacks': ('anywhere', False, 'self'),
    'ReduceDamageFromTypedAttackers': ('anywhere', False, 'self'),
    'ReduceDamageIfArceusInPlay': ('anywhere', False, 'self'),
    'ReduceOpponentActiveDamage': ('active', False, 'board'),
    'ReduceOwnRetreatCostIfAnotherSameNameInPlay': ('anywhere', False, 'self'),
    'ReduceRetreatCostOfYourActiveBasicFromBench': ('bench', False, 'board'),
    'ReduceRetreatCostOfYourActiveTypedFromBench': ('bench', False, 'board'),
    'RemoveRandomSpecialConditionFromActive': ('anywhere', False, 'board'),
    'RevealRandomOpponentHandCard': ('anywhere', False, 'board'),
    'SearchRandomCardFromDeck': ('anywhere', False, 'board'),
    'SleepOnZoneAttachToSelfWhileActive': ('active', False, 'self', 'drawback'),
    'SoothingWind': ('anywhere', False, 'board'),
    'StartTurnRandomPokemonToHand': ('active', False, 'board'),
    'SuppressBasicAbilities': ('anywhere', False, 'board'),
    'SwitchActiveTypedWithBench': ('anywhere', False, 'board'),
    'SwitchActiveUltraBeastWithBench': ('anywhere', False, 'board'),
    'SwitchDamagedOpponentBenchToActive': ('active', False, 'board'),
    'SwitchOutOpponentActiveToBench': None,  # require_active
    'SwitchThisBenchWithActive': ('bench', False, 'self'),
    'TimeRecall': ('anywhere', False, 'board'),
    'ToolCapacity': ('anywhere', False, 'self'),
    'UnownGuard': ('anywhere', False, 'board'),
    'UnownPower': ('anywhere', False, 'board'),
    'VictoryStar': ('anywhere', False, 'board'),
    'VictreebelFragranceTrap': ('active', False, 'board'),
}


def classify(variant, fields):
    """(pos, first_turn, scope, drawback) for one map entry, from the variant and its own fields."""
    c = VARIANT_CLASS.get(variant, 'MISSING')
    if c == 'MISSING':
        raise SystemExit(f'variant {variant} has no class: add it to VARIANT_CLASS before reading anything')
    if c is None:
        if variant in ('DrawCardsOncePerTurn', 'HealOneYourPokemon', 'SwitchOutOpponentActiveToBench'):
            pos = 'active' if 'require_active: true' in fields else 'anywhere'
            return pos, False, 'board', False
        if variant == 'NoRetreatCost':
            scope = 'self' if 'NoRetreatCostTarget::ThisPokemon' in fields else 'board'
            first = 'NoRetreatCostCondition::YourFirstTurn' in fields
            return 'anywhere', first, scope, False
        if variant == 'RandomEvolutionFromDeck':
            pos = 'active' if 'EndOfOpponentTurnIfActive' in fields else 'anywhere'
            return pos, False, 'self', False
        if variant == 'ReduceAttackCost':
            scope = 'board' if 'YourFuturePokemon' in fields else 'self'
            return 'anywhere', False, scope, False
        raise SystemExit(f'unresolved field-dependent variant {variant}')
    return c[0], c[1], c[2], len(c) > 3 and c[3] == 'drawback'


def switch_a(cls):
    """Switch A: an Ability that works only from the Active Spot and only on its owner's first turn."""
    return cls is not None and cls['pos'] == 'active' and cls['first_turn'] and not cls['drawback']


def switch_b(cls):
    """Switch B: an Ability that keeps working from the Bench on other Pokemon or the opponent: Bench-only
    Abilities, and board-scoped Abilities with no Active condition. Self-scoped ones (the holder's own
    defence, charging, retreat) and on-evolve / on-Bench-entry triggers are not Bench-working."""
    if cls is None:
        return False
    return cls['pos'] == 'bench' or (cls['pos'] == 'anywhere' and cls['scope'] == 'board')


# ---------------------------------------------------------------------------------------------
def load_db():
    db = [next(iter(e.items())) for e in json.load(io.open(os.path.join(ROOT, 'lib', 'deckgym-database.json'), encoding='utf-8'))]
    return {v['id']: (k, v) for k, v in db}


def load_mechanic_map():
    src = io.open(os.path.join(ENGINE, 'actions', 'effect_ability_mechanic_map.rs'), encoding='utf-8').read()
    pat = re.compile(r'\n\s*map\.insert\(\s*"((?:[^"\\]|\\.)*)",\s*(AbilityMechanic::(\w+)[^;]*?)\);', re.S)
    out = {}
    for m in pat.finditer(src):
        text = m.group(1)
        # Rust escapes used in a few keys (\u{e9}, \u{a0})
        text = re.sub(r'\\u\{([0-9a-fA-F]+)\}', lambda mm: chr(int(mm.group(1), 16)), text)
        line = src.count('\n', 0, m.start()) + 2
        out[text] = (m.group(3), re.sub(r'\s+', ' ', m.group(2)), line)
    return out


def load_gates():
    """Arms of can_use_ability_by_mechanic: variant -> (arm text, line)."""
    path = os.path.join(ENGINE, 'move_generation', 'move_generation_abilities.rs')
    lines = io.open(path, encoding='utf-8').read().split('\n')
    start = next(i for i, l in enumerate(lines) if l.startswith('fn can_use_ability_by_mechanic'))
    arms, cur = {}, None
    for i in range(start, len(lines)):
        l = lines[i]
        m = re.match(r'\s{8}AbilityMechanic::(\w+)', l)
        if m:
            cur = m.group(1)
            arms.setdefault(cur, [i + 1, ''])
        if cur:
            arms[cur][1] += l.strip() + ' '
        if i > start and lines[i].startswith('}'):
            break
    return {k: (v[1], v[0]) for k, v in arms.items()}


def gate_position(arm):
    """Position condition an activated Ability's gate states (None when the arm says the Ability is passive)."""
    body = arm.split('=>', 1)[1].strip() if '=>' in arm else arm
    if body.startswith('false'):
        return None
    if re.search(r'!is_active|in_play_index != 0|can_use_accept_pain|can_use_dismantling_keys', body):
        return 'bench'
    if re.search(r'(^|[^!|(])is_active &&|_in_play_index == 0 &&', body):
        return 'active'
    if '!require_active || is_active' in body or 'can_use_heal_one_your_pokemon' in body:
        return 'active-if-require_active'
    return 'anywhere'


def parse_list(path, db):
    cards, energy = [], None
    for raw in io.open(path, encoding='utf-8-sig'):
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith('energy'):
            energy = line.split(':', 1)[1].strip()
            continue
        parts = line.split()
        n = int(parts[0])
        cid = parts[-2] + ' ' + parts[-1]
        if cid not in db:
            cid = parts[-2] + ' ' + parts[-1].zfill(3)
        if cid not in db:
            raise SystemExit(f'{path}: unknown card {line}')
        cards.append((n, cid))
    merged = Counter()
    for n, cid in cards:
        merged[cid] += n
    return energy, [(n, cid) for cid, n in merged.items()]


def is_ex(v):
    return v['name'].endswith(' ex')


def is_mega(v):
    return v['name'].startswith('Mega ') and is_ex(v)


def ko_points(v):
    return 3 if is_mega(v) else 2 if is_ex(v) else 1


def highest_evolution(basic, list_cards):
    """card_logic/rare_candy.rs 121-165: Stage 2 from this Basic's line if the list has one, else Stage 1."""
    s1 = [v for _, v in list_cards if v['stage'] == 1 and v.get('evolves_from') == basic['name']]
    s1_names = {v['name'] for v in s1}
    s2 = [v for _, v in list_cards if v['stage'] == 2 and v.get('evolves_from') in s1_names]
    # the engine also finds Stage 2 through its name tables when the Stage 1 is not in the list
    if not s2:
        s2 = [v for _, v in list_cards if v['stage'] == 2 and v.get('evolves_from') in STAGE1_NAMES.get(basic['name'], set())]
    return (s2 or s1 or [None])[0]


STAGE1_NAMES = {}


def online_at_setup(basic, list_cards):
    """value_functions.rs 1663-1735 with effect_aware = false and no Energy: 1.0 exactly when the target form's
    lexicographically largest attack cost is empty (every attack free, or no attack), else 0."""
    target = highest_evolution(basic, list_cards) or basic
    costs = [tuple(a['energy_required']) for a in target.get('attacks', [])]
    return 1.0 if (not costs or max(costs) == ()) else 0.0


def retreat(v):
    return len(v.get('retreat_cost') or [])


# ---------------------------------------------------------------------------------------------
def basic_rows(cards, db, mmap, gates):
    list_cards = [(n, db[cid][1]) for n, cid in cards if db[cid][0] == 'Pokemon']
    rows = []
    for n, cid in cards:
        kind, v = db[cid]
        if kind != 'Pokemon' or v['stage'] != 0:
            continue
        ab = v.get('ability')
        cls = None
        if ab:
            if ab['effect'] not in mmap:
                cls = {'variant': None, 'note': 'Ability text not in the engine map (unimplemented)'}
            else:
                variant, fields, line = mmap[ab['effect']]
                pos, first, scope, drawback = classify(variant, fields)
                arm, arm_line = gates.get(variant, ('', None))
                cls = {'variant': variant, 'fields': fields, 'map_line': line,
                       'pos': pos, 'first_turn': first, 'scope': scope, 'drawback': drawback,
                       'activated': bool(arm) and gate_position(arm) is not None,
                       'gate_position': gate_position(arm) if arm else None, 'gate_line': arm_line}
        evo = highest_evolution(v, list_cards)
        costs = [len(a['energy_required']) for a in v.get('attacks', [])]
        rows.append({
            'id': cid, 'name': v['name'], 'count': n, 'type': v['energy_type'], 'hp': v['hp'],
            'retreat': retreat(v), 'ko_points': ko_points(v), 'weakness': v.get('weakness'),
            'attacks': [f"[{len(a['energy_required'])}] {a['title']} {a.get('fixed_damage') or 0}" for a in v.get('attacks', [])],
            'cheapest_attack_cost': min(costs) if costs else None,
            'evolves_in_list_to': evo['name'] if evo else None,
            'online_at_setup': online_at_setup(v, list_cards),
            'ability': ab['title'] if ab else None,
            'ability_text': ab['effect'] if ab else None,
            'mechanic': cls,
            'switch_a': switch_a(cls) if cls and cls.get('variant') else False,
            'switch_b': switch_b(cls) if cls and cls.get('variant') else False,
        })
    return rows


def setup_value(x, hand, rows_by_id, bonus):
    """kp3's setup score of opening x from a hand whose Basics are `hand` (a Counter of ids), plus the
    candidate's bonus. value_functions.rs 459-478: pokemon value (sum HP, no Energy) + hand - deck
    - Active retreat + 500 x online + HP / knockout points; online and distance weights are 0.
    The search (depth 3: the placement plus two more own setup actions, expectiminimax_player.rs 319-330)
    benches the two highest-HP Basics left, so hand and deck terms are the same for every x."""
    r = rows_by_id[x]
    rest = sorted((rows_by_id[i]['hp'] for i, c in hand.items() for _ in range(c - (1 if i == x else 0))), reverse=True)
    benched = rest[:2]
    ret = r['retreat']
    # Bench Retreat reducers benched within the horizon (hooks/retreat.rs 165-194); approximate: any in the hand
    for i, c in hand.items():
        if c - (1 if i == x else 0) <= 0:
            continue
        m = rows_by_id[i]['mechanic']
        if m and m.get('variant') == 'ReduceRetreatCostOfYourActiveBasicFromBench':
            ret -= 1
        if m and m.get('variant') == 'ReduceRetreatCostOfYourActiveTypedFromBench':
            etype = re.search(r'EnergyType::(\w+)', m['fields']).group(1)
            if r['type'] == etype:
                ret -= int(re.search(r'amount: (\d+)', m['fields']).group(1))
    ret = max(ret, 0)
    v = (r['hp'] + sum(benched)) - ret + ONLINE_WEIGHT * r['online_at_setup'] + r['hp'] / r['ko_points']
    return v + bonus(r)


def pick(hand, rows_by_id, bonus):
    """argmax with ties to the last action in canonical order (observation.rs 37-39 sorts by JSON, whose first
    differing field is the card id; Iterator::max_by returns the last maximum, expectiminimax_player.rs 340-350)."""
    vals = [(x, setup_value(x, hand, rows_by_id, bonus)) for x in sorted(hand)]
    m = max(v for _, v in vals)
    return [x for x, v in vals if abs(v - m) < 1e-9][-1]


def bonus_none(r):
    return 0.0


def bonus_a(r):
    return W_ACTIVE_ONLY_FIRST_TURN if (r['switch_a'] and r['evolves_in_list_to']) else 0.0


def bonus_b(r):
    return -W_BENCH_WORKING if r['switch_b'] else 0.0


def bonus_ab(r):
    return bonus_a(r) + bonus_b(r)


# Reported only, not in the draft candidate: every other Active-only Ability that is not a drawback (C), and
# the drawback class (D: an Ability that hurts its holder while Active), at the same pre-set 250.
def bonus_c(r):
    m = r['mechanic'] or {}
    other_active = m.get('pos') == 'active' and not m.get('first_turn') and not m.get('drawback')
    return 250.0 if other_active else 0.0


def bonus_d(r):
    m = r['mechanic'] or {}
    return -250.0 if m.get('drawback') else 0.0


def bonus_r(r):
    """Reported only: the flag-free alternative to switch B (design option 2), a setup readiness term of -100 per
    Energy of the Active's cheapest own attack. Pre-set so a 2-Energy difference outweighs a 50-HP one."""
    return -100.0 * (r['cheapest_attack_cost'] or 0)


def bonus_ar(r):
    return bonus_a(r) + bonus_r(r)


SWITCHES = (('A', bonus_a), ('B', bonus_b), ('AB', bonus_ab), ('C', bonus_c), ('D', bonus_d), ('R', bonus_r),
            ('AR', bonus_ar))
TABLE_DECKS = ['altaria', 'blaziken', 'hydreigon', 'lucario', 'sceptile', 'suicune', 'vespiquen', 'weezing']


def table_footprint(lists):
    """Expected share of the 28-pairing table's games whose play differs from kp3's at least once. The switches
    act only in the setup evaluation (value_functions.rs 459-478 runs only while the opponent's setup is hidden,
    observation.rs 48-53), and a bench placement or end of setup never changes with the Active fixed, so a game
    differs exactly when either deck's opening Active differs: 1 - (1 - p_a)(1 - p_b) per pairing."""
    p = {}
    for e in lists:
        if e['group'] == 'table':
            p[os.path.basename(e['list'])[:-4]] = e['p_opening_changes']
    out = {}
    for key, _ in SWITCHES:
        per = {}
        for a, b in itertools.combinations(TABLE_DECKS, 2):
            per[f'{a} v {b}'] = round(1 - (1 - p[a][key]) * (1 - p[b][key]), 4)
        out[key] = {'mean_over_28_pairings': round(sum(per.values()) / len(per), 4), 'per_pairing': per}
    return out


def opening_distribution(cards, rows):
    """Exact over the engine's deal: every 5-card draw, weighted by the multivariate hypergeometric."""
    total = sum(n for n, _ in cards)
    rows_by_id = {r['id']: r for r in rows}
    basic_ids = [r['id'] for r in rows]
    counts = {r['id']: r['count'] for r in rows}
    others = total - sum(counts.values())
    denom = math.comb(total, 5)
    res = {'p_no_basic_swapped': 0.0, 'p_choice_ids': 0.0, 'p_choice_names': 0.0, 'p_two_plus_basic_cards': 0.0,
           'kp3_opens': Counter(), 'kp3_opens_with_choice': Counter(), 'kp3_opens_two_plus_cards': Counter(),
           'changed': {k: 0.0 for k, _ in SWITCHES}, 'transitions': {k: Counter() for k, _ in SWITCHES}}
    ranges = [range(0, min(counts[i], 5) + 1) for i in basic_ids]
    total_basics = sum(counts.values())
    for ks in itertools.product(*ranges):
        k = sum(ks)
        if k > 5 or 5 - k > others:
            continue
        p = math.comb(others, 5 - k) / denom
        for i, kk in zip(basic_ids, ks):
            p *= math.comb(counts[i], kk)
        if p == 0:
            continue
        if k == 0:
            res['p_no_basic_swapped'] += p
            for i in basic_ids:  # swap in one random Basic: forced opening, no choice
                res['kp3_opens'][i] += p * counts[i] / total_basics
            continue
        hand = Counter({i: kk for i, kk in zip(basic_ids, ks) if kk})
        names = {rows_by_id[i]['name'] for i in hand}
        choice = len(hand) >= 2
        if len(names) >= 2:
            res['p_choice_names'] += p
        base = pick(hand, rows_by_id, bonus_none)
        res['kp3_opens'][base] += p
        if k >= 2:  # two or more Basic cards: two or more Place actions offered, duplicates included
            res['p_two_plus_basic_cards'] += p
            res['kp3_opens_two_plus_cards'][base] += p
        if choice:
            res['p_choice_ids'] += p
            res['kp3_opens_with_choice'][base] += p
            for key, fn in SWITCHES:
                new = pick(hand, rows_by_id, fn)
                if new != base:
                    res['changed'][key] += p
                    res['transitions'][key][(base, new)] += p
    return res


# ---------------------------------------------------------------------------------------------
def by_name(transitions, db):
    """{(from id, to id): p} -> {'from name -> to name': p}, summing printings that share a name."""
    out = Counter()
    for (a, b), p in transitions.items():
        out[f"{db[a][1]['name']} -> {db[b][1]['name']}"] += p
    return {k: round(v, 4) for k, v in out.most_common()}


def list_files():
    groups = [('table', os.path.join(ROOT, 'decks', 'research')), ('dustin', os.path.join(ROOT, 'decks', 'dustin')),
              ('brew', os.path.join(ROOT, 'decks', 'brews')),
              ('b2e', os.path.join(ROOT, 'rl', 'results', 'b2e_card_check_2026-09-26', 'decks'))]
    out = []
    for g, d in groups:
        for f in sorted(os.listdir(d)):
            if f.endswith('.txt') and (g != 'b2e' or f.startswith('h-')):
                out.append((g, os.path.join(d, f)))
    return out


def validate(out):
    """The census's k3/kp3 opening rule against what the probes actually chose in the two network studies.
    An opening decision is recorded there whenever two or more Place actions are offered (duplicates count),
    so the comparison uses the 'two or more Basic cards' distribution."""
    res = {}
    studies = [
        ('altaria (kp3 probe, B2c Sept 26)', 'decks/research/altaria.txt',
         os.path.join(ROOT, 'rl', 'results', 'altaria_network_divergence_2026-09-26', 'decisions.jsonl'), 'kp3'),
        ('lucario (k3 probe, B2c Sept 25)', 'decks/research/lucario.txt',
         os.path.join(ROOT, 'rl', 'results', 'lucario_network_divergence_2026-09-25', 'decisions.jsonl'), 'k3'),
    ]
    for label, lst, path, bot in studies:
        entry = next(e for e in out['lists'] if e['list'] == lst)
        obs, games = Counter(), set()
        with io.open(path, encoding='utf-8') as f:
            for line in f:
                r = json.loads(line)
                if r.get('turn') != 0 or r['i'] in games:
                    continue
                if bot == 'kp3':
                    d = r.get('kp3_detail') or {}
                    if d.get('slot') != 'active':
                        continue
                    name = d['name']
                else:
                    if r['context'].get('own_active_hp') is not None:
                        continue
                    name = r['k3_move'].replace('place ', '')
                games.add(r['i'])
                obs[name] += 1
        exp = Counter()
        for k, p in entry['kp3_opens_two_plus_basic_cards'].items():
            exp[k.rsplit(' ', 2)[0]] += 400 * p
        res[label] = {
            'games': 400,
            'opening_decisions_observed': sum(obs.values()),
            'opening_decisions_expected': round(400 * entry['p_two_plus_basic_cards'], 1),
            'probe_opens_observed': dict(obs.most_common()),
            'probe_opens_expected': {k: round(v, 1) for k, v in exp.most_common()},
        }
    return res


def main():
    db = load_db()
    for k, v in db.values():
        if k == 'Pokemon' and v['stage'] == 1 and v.get('evolves_from'):
            STAGE1_NAMES.setdefault(v['evolves_from'], set()).add(v['name'])
    mmap = load_mechanic_map()
    gates = load_gates()
    # every mapped variant must have a class (the classifier is keyed on variants, so a new one stops the run)
    for text, (variant, fields, line) in mmap.items():
        classify(variant, fields)
    out = {'generated': 'census.py, Sept 26 2026', 'weights': {'switch_a': W_ACTIVE_ONLY_FIRST_TURN, 'switch_b': W_BENCH_WORKING},
           'engine_map_entries': len(mmap), 'lists': []}
    for group, path in list_files():
        energy, cards = parse_list(path, db)
        rows = basic_rows(cards, db, mmap, gates)
        dist = opening_distribution(cards, rows)
        rel = os.path.relpath(path, ROOT).replace('\\', '/')
        entry = {
            'list': rel, 'group': group, 'energy': energy, 'cards': sum(n for n, _ in cards),
            'basics': rows,
            'p_no_basic_hand_repaired': round(dist['p_no_basic_swapped'], 4),
            'p_opening_choice': round(dist['p_choice_ids'], 4),
            'p_opening_choice_distinct_names': round(dist['p_choice_names'], 4),
            'p_two_plus_basic_cards': round(dist['p_two_plus_basic_cards'], 4),
            'kp3_opens': {db[i][1]['name'] + ' ' + i: round(p, 4) for i, p in dist['kp3_opens'].most_common()},
            'kp3_opens_with_choice': {db[i][1]['name'] + ' ' + i: round(p, 4) for i, p in dist['kp3_opens_with_choice'].most_common()},
            'kp3_opens_two_plus_basic_cards': {db[i][1]['name'] + ' ' + i: round(p, 4) for i, p in dist['kp3_opens_two_plus_cards'].most_common()},
            'carries_switch_a': sorted({r['name'] + ' ' + r['id'] for r in rows if r['switch_a']}),
            'carries_switch_b': sorted({r['name'] + ' ' + r['id'] for r in rows if r['switch_b']}),
            'p_opening_changes': {k: round(v, 4) for k, v in dist['changed'].items()},
            # Keyed by names, so two printings of one name (Suicune's two Frigibax) are summed, not overwritten
            # (second read, Sept 26: the earlier dict comprehension kept only the last printing's share).
            'opening_transitions': {k: by_name(t, db) for k, t in dist['transitions'].items()},
        }
        out['lists'].append(entry)
    out['table_footprint'] = table_footprint(out['lists'])
    # What B2c's play-outs say each Altaria opening change is worth against kp3's Lucario, kp3 continuing on both
    # decks (../altaria_network_divergence_2026-09-26/opening_choice.txt; points, 95% half-width).
    b2c = {'Darkrai -> Eevee': (27.0, 7.8), 'Swablu -> Eevee': (16.1, 8.5), 'Darkrai -> Swablu': (18.6, 8.0)}
    alt = next(e for e in out['lists'] if e['list'] == 'decks/research/altaria.txt')
    exp = {}
    for key in ('A', 'B', 'AB'):
        m = sum(p * b2c[t][0] for t, p in alt['opening_transitions'][key].items())
        hw = math.sqrt(sum((p * b2c[t][1]) ** 2 for t, p in alt['opening_transitions'][key].items()))
        exp[key] = {'points_per_altaria_game': round(m, 1), 'approx_95_half_width': round(hw, 1)}
    out['b2c_expected_altaria_v_lucario'] = exp
    out['validation'] = validate(out)
    with io.open(os.path.join(HERE, 'census.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    # short printout
    for e in out['lists']:
        fl = [f"{r['name']} {r['id']} x{r['count']}: {r['mechanic']['variant'] if r['mechanic'] else '-'}"
              + (f" ({r['mechanic']['pos']}{', first turn' if r['mechanic'].get('first_turn') else ''}, {r['mechanic']['scope']})" if r['mechanic'] and r['mechanic'].get('variant') else '')
              for r in e['basics'] if r['ability']]
        print(f"{e['list']}: choice {e['p_opening_choice']:.3f}; kp3 opens {e['kp3_opens_with_choice']}; "
              f"A {e['p_opening_changes']['A']:.3f} B {e['p_opening_changes']['B']:.3f} AB {e['p_opening_changes']['AB']:.3f}")
        for x in fl:
            print('    ', x)
        for k, _ in SWITCHES:
            if e['opening_transitions'][k]:
                print('     ', k, e['opening_transitions'][k])


if __name__ == '__main__':
    main()

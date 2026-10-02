"""Coin-flip damage prevention, Part 1 (Sept 30; read-only). For each attack helper that delivers damage through a queued
choice, the cards whose attack text maps to its Mechanic (engine/src/actions/effect_mechanic_map.rs, matched against
engine/database.json), and the cards with the two coin Abilities (effect_ability_mechanic_map.rs); then which deck lists
under decks/ (every .txt, recursively) hold any of them. Prints the tables HELPERS.md quotes.
Usage: python3 helpers_census.py   (from anywhere in the repository)"""
import json, re, subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, cwd=Path(__file__).parent).stdout.strip())
ENGINE = ROOT / "engine"
STRING = r'"((?:[^"\\]|\\.)*)"'


def rust_unescape(body):
    """A Rust string literal's body: \\u{..}, \\n, \\t, \\", \\\\, and a backslash-newline continuation."""
    body = re.sub(r"\\\r?\n\s*", "", body)
    body = re.sub(r"\\u\{([0-9a-fA-F]+)\}", lambda m: chr(int(m.group(1), 16)), body)
    return re.sub(r"\\(.)", lambda m: {"n": "\n", "t": "\t", "r": "\r", "0": "\0"}.get(m.group(1), m.group(1)), body)


def inserts(path, enum):
    """(text, variant, argument text) for every map.insert("text", Enum::Variant ...) in a map file."""
    src = (ENGINE / path).read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"map\.insert\(\s*" + STRING + r",\s*" + enum + r"::(\w+)", src):
        text = rust_unescape(m.group(1))
        rest = src[m.end():m.end() + 400]
        depth, args = 0, ""
        for ch in rest:  # the variant's own arguments, up to the insert's closing parenthesis
            if ch in "({":
                depth += 1
            elif ch in ")}":
                if depth == 0:
                    break
                depth -= 1
            args += ch
        out.append((text, m.group(2), " ".join(args.split())))
    return out


attack_map = {t: (v, a) for t, v, a in inserts("src/actions/effect_mechanic_map.rs", "Mechanic")}
ability_map = {t: (v, a) for t, v, a in inserts("src/actions/effect_ability_mechanic_map.rs", "AbilityMechanic")}
cards = [next(iter(e.items())) for e in json.load(open(ENGINE / "database.json", encoding="utf-8"))]

# Each helper, and the Mechanics that call it (the dispatch in apply_attack_action.rs).
HELPERS = [
    ("also_choice_bench_damage", ["AlsoChoiceBenchDamage", "AlsoChoiceBenchDamageFiltered"]),
    ("optional_discard_benched_basic_for_extra_damage", ["OptionalDiscardBenchedBasicForExtraDamage"]),
    ("discard_all_energy_of_type_then_damage_any_opponent_pokemon", ["SelfDiscardAllTypeEnergyAndDamageAnyOpponentPokemon"]),
    ("damage_to_any_opponent_per_target_energy", ["DamageToAnyOpponentPerTargetEnergy"]),
    ("self_discard_energy_then_damage_any_opponent_pokemon", ["SelfDiscardEnergyThenDamageAnyOpponentPokemon"]),
    ("switch_in_opponent_benched_then_damage", ["SwitchInOpponentBenchedThenDamage"]),
    ("direct_damage_if_damaged", ["DirectDamageIfDamaged"]),
    # (b)'s own example, the DirectDamage group:
    ("direct_damage / direct_damage_and_self_card_effect", ["DirectDamage", "DirectDamageAndSelfCardEffect"]),
    # Found in Part 1, outside the seven: attack damage to the opponent through a queued ApplyDamage.
    ("coin_flip_also_choice_bench_damage", ["CoinFlipAlsoChoiceBenchDamage"]),
    ("self_discard_energy_and_choice_bench_damage", ["SelfDiscardEnergyAndChoiceBenchDamage"]),
    ("conditional_bench_damage_attack", ["ConditionalBenchDamage"]),
    ("mega_kangaskhan_ex_double_punching_family", ["MegaKangaskhanExDoublePunchingFamily"]),
    ("shuffle_opponent_tools_into_deck_before_damage", ["ShuffleOpponentToolsIntoDeckBeforeDamage"]),
    ("discard_tools_from_hand_for_damage (its damage is queued in apply_action.rs)", ["DiscardToolsFromHandForDamage"]),
]

by_mechanic = defaultdict(list)
for kind, c in cards:
    if kind != "Pokemon":
        continue
    for a in c.get("attacks") or []:
        hit = attack_map.get(a.get("effect") or "")
        if hit:
            by_mechanic[hit[0]].append((c["id"], c["name"], a["title"], hit[1], a.get("effect")))

coin_cards = []
for kind, c in cards:
    ab = (c.get("ability") or {}) if kind == "Pokemon" else {}
    hit = ability_map.get(ab.get("effect") or "") if ab else None
    if hit and hit[0] in ("CoinFlipToPreventDamage", "CoinFlipToReduceDamage"):
        coin_cards.append((c["id"], c["name"], ab.get("title"), hit[0] + (" " + hit[1] if hit[1] else "")))


def norm(card_id):
    s, n = card_id.rsplit(" ", 1)
    return (s, int(n)) if n.isdigit() else (s, n)


decks = defaultdict(list)
for f in sorted((ROOT / "decks").rglob("*.txt")):
    for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
        # "2 B1 033" or "2 Torchic B1 033": a count, an optional name, then the set and number.
        m = re.match(r"\s*(\d+)\s+(?:.*?\s)?([AB]\d+[a-z]?|P-[AB])\s+(\d+)\s*$", line)
        if m:
            decks[norm(m.group(2) + " " + m.group(3))].append(str(f.relative_to(ROOT)))


def in_decks(card_id):
    return sorted(set(decks.get(norm(card_id), [])))


for helper, mechanics in HELPERS:
    print(f"\n## {helper}  ({', '.join(mechanics)})")
    rows = [r for m in mechanics for r in by_mechanic.get(m, [])]
    if not rows:
        print("  no card in the database maps to it")
    for cid, name, title, args, _ in sorted(rows):
        where = in_decks(cid)
        print(f"  {cid:9s} {name} - {title}  [{args}]" + (f"\n      in decks: {', '.join(where)}" if where else ""))

print("\n## the coin Abilities (the defenders)")
for cid, name, title, mech in sorted(coin_cards):
    where = in_decks(cid)
    print(f"  {cid:9s} {name} - {title}  [{mech}]" + (f"\n      in decks: {', '.join(where)}" if where else ""))
print(f"\n(deck lists read: {len({f for v in decks.values() for f in v})} files under decks/)")

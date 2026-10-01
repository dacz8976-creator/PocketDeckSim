"""The later round of coin-flip prevention (Oct 1; read-only): the reach of each repaired site. For each site, every
printing whose attack text maps to the site's Mechanic (engine/src/actions/effect_mechanic_map.rs, matched against
engine/database.json), and the deck lists under decks/ (every .txt, recursively) that hold it; then the same for the
coin-flip damage Abilities (the defenders), since a site changes play only against one of them. The parsing is
../coin_prevention_repair_2026-09-30/helpers_census.py's, copied.
Usage: python3 reach.py   (from anywhere in the repository)"""
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

# The seven sites of the README's "Recorded for a later round", and the Mechanics that reach them.
SITES = [
    ("Wild Swing (discard_own_benched_type_for_damage, then discard_then_damage_choice)", ["DiscardOwnBenchedTypeForDamage"]),
    ("Wellspring Dance (coin_flip_also_choice_bench_damage)", ["CoinFlipAlsoChoiceBenchDamage"]),
    ("Tornado Shot (self_discard_energy_and_choice_bench_damage)", ["SelfDiscardEnergyAndChoiceBenchDamage"]),
    ("Double Splash / Triple Bombardment (conditional_bench_damage_attack)", ["ConditionalBenchDamage"]),
    ("Mega Kangaskhan ex's second punch (mega_kangaskhan_ex_double_punching_family)", ["MegaKangaskhanExDoublePunchingFamily"]),
    ("Mischievous Ring (shuffle_opponent_tools_into_deck_before_damage)", ["ShuffleOpponentToolsIntoDeckBeforeDamage"]),
    ("Litter (discard_tools_from_hand_for_damage, then discard_tools_then_damage_choice)", ["DiscardToolsFromHandForDamage"]),
]

by_mechanic = defaultdict(list)
for kind, c in cards:
    if kind != "Pokemon":
        continue
    for a in c.get("attacks") or []:
        hit = attack_map.get(a.get("effect") or "")
        if hit:
            by_mechanic[hit[0]].append((c["id"], c["name"], a["title"], hit[1]))

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
            decks[norm(m.group(2) + " " + m.group(3))].append((str(f.relative_to(ROOT)), int(m.group(1))))


def in_decks(card_id):
    return sorted(set(decks.get(norm(card_id), [])))


for site, mechanics in SITES:
    print(f"\n## {site}  ({', '.join(mechanics)})")
    rows = [r for m in mechanics for r in by_mechanic.get(m, [])]
    if not rows:
        print("  no card in the database maps to it")
    for cid, name, title, args in sorted(rows):
        where = in_decks(cid)
        print(f"  {cid:9s} {name} - {title}" + (f"  [{args}]" if args else "")
              + (f"\n      in decks: {', '.join(f'{p} ({n})' for p, n in where)}" if where else "\n      in decks: none"))

print("\n## the coin-flip damage Abilities (the defenders)")
for cid, name, title, mech in sorted(coin_cards):
    where = in_decks(cid)
    print(f"  {cid:9s} {name} - {title}  [{mech}]"
          + (f"\n      in decks: {', '.join(f'{p} ({n})' for p, n in where)}" if where else "\n      in decks: none"))
print(f"\n(deck lists read: {len({p for v in decks.values() for p, _ in v})} files under decks/)")

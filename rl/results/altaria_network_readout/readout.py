"""Readout for a two-network run: the Altaria detector network by default (runs/diag-altaria-lucario, whose reading
is fixed in PRESET_READING.md there), or the Hydreigon run's readout unchanged with --preset hydreigon. This is
results/hydreigon_network_readout/readout.py with the deck, the opponent, the Limitless value and the audited attacks
and abilities made options. Run it after the run's own report steps (audit_v5.py, REPORT.txt). Inside WSL, from the
rl folder, with the run5 venv's python:
    nice -n 19 python results/altaria_network_readout/readout.py --run runs/diag-altaria-lucario [--games 2000] [--workers 3]
    nice -n 19 python results/altaria_network_readout/readout.py --preset hydreigon --run runs/diag-hydreigon-lucario

What it does, on the run's own confirmation deals (seed = the settings' confirmation base + i, the bars' seats):
  1. reads the confirmed checkpoints from state.json (verdict "picks", which finish() in train_v5.py records; it
     refuses while there is no verdict, and, outside --preset hydreigon, until REPORT.txt and both knockout audits
     exist, since its text is written once) and checks REPORT.txt names the same ones;
  2. plays network v network (the two confirmed networks) on those deals, and prints the focus deck's result in all
     four conditions: k3 v k3 (the bars), network v k3 and k3 v network (the confirmation rows), network v network,
     each paired with k3 v k3 on the same deals;
  3. audits the focus network's play, in its confirmation games (replayed from the recorded moves, as audit_v5.py
     does) and live in the network v network games: each audited attack per turn it was on offer (used / passed,
     split by whether it would knock out), each ability, Asleep turns created (Bad Dreams), bench size when the bench
     attack is used, attacking and benching on offered turns;
  4. (altaria) prints the knockout audit of both networks (results/ko_audit, written by the run's report steps); it is
     the run's own, the network against k3, a deviation from PRESET item 3's "network against kp3" that the text
     states with its reason;
  5. applies the pre-set reading: PRESET_READING.md items 1 and 3 (altaria), or RUN5's Hyper Ray reading (hydreigon);
  6. prints the text and writes it to readout.txt here (never overwritten: a taken name gets a time suffix), with
     the network v network games beside it (<same name>_nvn_games.jsonl) and every game's counts
     (<same name>_counts.jsonl).
No new seeds: reusing the confirmation deals is deliberate (that block is reserved for the run's evaluation), so all
four rows are paired. The decisive comparison (PRESET_READING item 2) is kp3_rows.py's; k3's and kp3's own counts on
the same deals are k3_counts.py's.

Audited names are looked up in the focus deck's own file with lib/card.py's database (the engine reads the deck
file's ids); a name no card in the list has stops the script. An ability is counted by what its text says:
  "Once during your turn ..."                      activated: turns it was usable / turns it was used
                                                   (usable = on a Pokemon with more HP left than the damage the
                                                   ability does to itself, as the Hydreigon readout counted Roar);
  "... can evolve during your first turn ..."      Boosted Evolution: turns the Active owner could evolve only
                                                   because of it (the player's first turn, or the turn it was played)
                                                   / turns it evolved then;
  "At the end of each turn ... Asleep ..."         automatic (Bad Dreams): counted as Asleep turns created, i.e.
                                                   turns ending with an attack whose text puts the opponent's Active
                                                   to sleep, used without a knockout, and how many (and what share)
                                                   had the owner in play. Its limits are printed with it: a count of
                                                   sleep attacks, not of damage (waking at the Checkup and the hits
                                                   that landed aren't tracked; an Active already Asleep also counts).
'Would knock out' (--ko-rule): "fixed" = the opponent's Active had no more HP left than the attack's printed damage
(the Hydreigon readout's definition, from the transcripts file); "engine" = a sure knockout as the knockout audit
defines it (audit_v5.py): in each of 4 copies of the true game under different chance seeds, the move gains the
pilot at least one point. The copies are analysis only; the game itself is untouched. "engine" counts Mega Harmony's
bench bonus, Weakness, Training Area and Bad Dreams at the end of the turn, which the printed damage leaves out.
Under "engine" (Altaria's), every attack block also prints the fixed rule's split of the same offered turns under
each row, labelled, so the Hydreigon table stays comparable; it plays nothing and changes no engine-rule number.
The two rules are not interchangeable.
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import multiprocessing as mp  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
RL = HERE.parents[1]
sys.path.insert(0, str(RL))
import train_v5 as T  # noqa: E402

# Per-run defaults. Every value is an option too (see main()); a preset only fills in what isn't given.
PRESETS = {
    # rl/runs/diag-altaria-lucario/PRESET_READING.md. Limitless: Altaria v Lucario 71.9 +- 4.9 (Sept 23 table,
    # results/limitless_check_2026-09-23.md). The names are every attack and ability in decks/research/altaria.txt
    # (python3 lib/card.py on its ids): Sing (Swablu), Mega Harmony (Mega Altaria ex), Stampede and Boosted Evolution
    # (Eevee), Hypnoblast (Espeon), Dark Slumber and Bad Dreams (Darkrai), Sleepy Lullaby (Igglybuff).
    "altaria": {"deck": "altaria", "opp": "lucario", "limitless": (71.9, 4.9),
                "attacks": ("Mega Harmony", "Hypnoblast", "Dark Slumber", "Sing", "Sleepy Lullaby", "Stampede"),
                "abilities": ("Boosted Evolution", "Bad Dreams"), "bench_attack": "Mega Harmony",
                "ko_rule": "engine", "reading": "altaria"},
    # rl/results/hydreigon_network_readout/ (RUN5.md's Hyper Ray reading); k3_counts.py counted two attacks there
    "hydreigon": {"deck": "hydreigon", "opp": "lucario", "limitless": (54.4, 8.0),
                  "attacks": ("Hyper Ray",), "counts_attacks": ("Hyper Ray", "Darkness Claw"),
                  "abilities": ("Roar in Unison",), "bench_attack": None, "ko_rule": "fixed", "reading": "hydreigon"},
}
KO_COPIES = 4           # chance seeds per move for --ko-rule engine (audit_v5.py's K)
LOAD_CHECK_GAMES = 50   # the other network's confirmation games replayed only to prove its weights load
# The diagnostic kp-capable build the Hydreigon readout used (results/hydreigon_network_readout/READING.md). kp3_rows.py
# and k3_counts.py --bot kp3 stop unless the module they imported has exactly this sha256.
DIAG_ADDON_SHA = "c048388b4bcf7103375ea0a1e7c9e965be8e350000c3ac873bd111b69e1eae19"
IDENTITY_DEALS = 200    # the kp3 identity gate's size, the Hydreigon readout's (PRESET: "the same identity gates")


def at_least_10(points):
    """PRESET_READING's '+10 or more'. Win rates are counts over the deals, so a difference is a multiple of 100/n
    points; the slack only stops float rounding from reading exactly +10.0 as under it (train_v5's judge() allows
    1e-9 on margins for the same reason)."""
    return points >= 10 - 1e-6
# Hydreigon reading only: k3 reference counts, not recomputed (see-everything file: used / passed per Hydreigon turn)
K3_NOKO_RATE, SEARCHED_NOKO_RATE = 0.03, 0.82
REFERENCE = [
    "  k3 v k3, first 500 table seeds (see_everything_2026-09-24.md):  KOs 366 / 4;  doesn't KO 8 / 225 (3%);  "
    "Roar used when healthy 630 / 776",
    "  k3 v k3, all 1,000 table games (hydreigon_v_lucario_k3_transcripts_2026-09-24.md):  KOs 732 / 8 (99%);  "
    "doesn't KO 12 / 434 (3%);  17 other;  Roar on 83% of the turns it was usable without knocking Hydreigon out",
    "  searched bots kr3 (see-everything): sees everything  KOs 312 / 15;  doesn't KO 74 / 16 (82%);  "
    "guesses from the list  304 / 21;  66 / 13 (84%)",
]
ATT_KEYS = ("ko_used", "ko_passed", "noko_used", "noko_passed", "other")
HABIT_KEYS = ("turns", "attack_turns", "attack_made", "bench_turns", "bench_made")
FIXED_LABEL = "  fixed rule (printed damage), same turns"   # the sub-row under each engine-rule row in the attack blocks
# Printed in section 4 under the Altaria reading (and kept in README.md), as Fable approved it on Sept 25.
TRANSPARENCY = [
    "  Transparency (what was seen before this readout ran): the dry run replayed 200 Altaria k3 v k3 bar rows (fixed",
    "  before training) as an identity precheck; the reviewer glimpsed STATUS.txt's header (games played, bars 55/45,",
    "  draw gate) with no checkpoint margins. Also: while checking progress at 23:11 CDT on Sept 25, the laptop",
    "  session's own grep of STATUS.txt showed the live-evaluation margin lines for checkpoints 1000k-1400k. This was",
    "  after every definition had been fixed and approved, and nothing in the scripts was changed because of it.",
]

_W = {}


# ---------------------------------------------------------------- options shared by the three scripts
def add_preset_options(ap, counts=False):
    ap.add_argument("--preset", choices=sorted(PRESETS), default="altaria",
                    help="fills in every option below that isn't given (default altaria)")
    ap.add_argument("--deck", default=None, help="the focus deck (a name in the run's pool)")
    ap.add_argument("--opp", default=None, help="the other deck (checked against the run's pool)")
    ap.add_argument("--attacks", default=None, help="audited attacks, comma-separated (lib/card.py names)")
    ap.add_argument("--attack-name", default=None, help="one audited attack (the Hydreigon readout's option)")
    ap.add_argument("--abilities", default=None, help="audited abilities, comma-separated; 'none' for none")
    ap.add_argument("--bench-attack", default=None, help="the attack whose bench size is counted; 'none' for none")
    ap.add_argument("--ko-rule", choices=("engine", "fixed"), default=None, help="what 'would knock out' means")
    if not counts:
        ap.add_argument("--limitless", default=None, help="the focus deck's Limitless score: 'mid,half' or 'none'")


def split_names(s):
    return tuple(x.strip() for x in s.split(",") if x.strip()) if s and s.lower() != "none" else ()


def apply_preset(a, counts=False):
    """Fill the options from the preset. The preset's own values apply only while the deck is the preset's."""
    P = PRESETS[a.preset]
    a.deck = a.deck or P["deck"]
    own = a.deck == P["deck"]
    a.opp = a.opp or (P["opp"] if own else None)
    if a.attack_name and a.attacks:
        raise SystemExit("give --attacks or --attack-name, not both")
    if a.attack_name:
        a.attacks = (a.attack_name,)
    elif a.attacks is not None:
        a.attacks = split_names(a.attacks)
    elif own:
        a.attacks = P.get("counts_attacks", P["attacks"]) if counts else P["attacks"]
    else:
        raise SystemExit(f"--deck {a.deck} isn't the {a.preset} preset's deck: name the attacks (--attacks)")
    a.abilities = split_names(a.abilities) if a.abilities is not None else (P["abilities"] if own else ())
    if a.bench_attack is None:
        a.bench_attack = P["bench_attack"] if own else None
    elif a.bench_attack.lower() == "none":
        a.bench_attack = None
    a.ko_rule = a.ko_rule or P["ko_rule"]
    a.reading = P["reading"] if own else "generic"
    if not counts:
        if a.limitless is None:
            a.limitless = P["limitless"] if own else None
        elif a.limitless.lower() == "none":
            a.limitless = None
        else:
            mid, half = (float(x) for x in a.limitless.split(","))
            a.limitless = (mid, half)
    return a


# ---------------------------------------------------------------- what is audited, from the deck file and lib/card.py
def load_cards():
    """Every card in lib/card.py's database (deckgym-database.json), by id: (kind, card)."""
    spec = importlib.util.spec_from_file_location("pdl_lib_card", T.ROOT / "lib" / "card.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {v["id"]: (k, v) for k, v in mod.load()}


def ability_kind(text):
    if "can evolve during your first turn" in text:
        return "evolve-early"
    if text.startswith("At the end of each turn") and "Asleep" in text:
        return "asleep-turns"
    if text.startswith("Once during your turn"):
        return "activated"
    return None


def resolve(S, a):
    """The audit spec: which card has each audited name, how each ability is counted, which attacks put the
    opponent's Active to sleep. Stops on a name no card in the focus deck's list has."""
    from pdl_rl_env import RawEnv
    names = list(S["pool"])
    if a.deck not in names or len(names) != 2:
        raise SystemExit(f"--deck {a.deck}: the run's pool is {names}; this readout needs a two-deck pool containing it")
    opp = [d for d in names if d != a.deck][0]
    if a.opp not in (None, opp):
        raise SystemExit(f"--opp {a.opp}: the run's pool pairs {a.deck} with {opp}")
    rel = S["pool"][a.deck]
    cards = load_cards()
    ids = RawEnv.deck_card_ids(str(T.ROOT / rel))   # the engine's own reading of the deck file
    unknown = [i for i in ids if i not in cards]
    mons = [cards[i][1] for i in ids if i in cards and cards[i][0] == "Pokemon"]
    att, abl = {}, {}
    for m in mons:
        for at in m.get("attacks", []):
            e = att.setdefault(at["title"], {"owners": set(), "effect": at.get("effect") or ""})
            e["owners"].add(m["name"])
        if m.get("ability"):
            e = abl.setdefault(m["ability"]["title"], {"owners": set(), "effect": m["ability"]["effect"] or ""})
            e["owners"].add(m["name"])
    missing = [x for x in a.attacks if x not in att] + [x for x in a.abilities if x not in abl]
    if missing:
        raise SystemExit(f"{rel}: no Pokemon in the list has {', '.join(missing)} (its attacks: "
                         f"{', '.join(sorted(att))}; abilities: {', '.join(sorted(abl)) or 'none'})")
    if a.bench_attack and a.bench_attack not in a.attacks:
        raise SystemExit(f"--bench-attack {a.bench_attack} must be one of the audited attacks")
    abilities = []
    for name in a.abilities:
        kind = ability_kind(abl[name]["effect"])
        if kind is None:
            raise SystemExit(f"{name}: its text doesn't say how to count it ({abl[name]['effect']!r})")
        m = re.search(r"do (\d+) damage to this Pok", abl[name]["effect"])
        abilities.append({"name": name, "owners": sorted(abl[name]["owners"]), "kind": kind,
                          "self_dmg": int(m.group(1)) if (m and kind == "activated") else 0})
    sleep = sorted(t for t, e in att.items() if "opponent's Active Pokémon is now Asleep" in e["effect"])
    A = {"deck": a.deck, "opp": opp, "file": rel, "ko_rule": a.ko_rule, "bench_attack": a.bench_attack,
         "attacks": list(a.attacks), "owners": {t: sorted(att[t]["owners"]) for t in att},
         "abilities": abilities, "sleep": sleep,
         "asleep_owners": sorted({o for b in abilities if b["kind"] == "asleep-turns" for o in b["owners"]}),
         "unaudited": [t for t in sorted(att) if t not in a.attacks] + [t for t in sorted(abl) if t not in a.abilities],
         "unknown_ids": unknown}
    return A


def preset_line(a):
    if a.reading == "generic":
        return (f"Options: --deck {a.deck} is not the {a.preset} preset's deck, so this is a code test, not a reading "
                f"(the wording below is the {a.preset} reading's).")
    return f"Preset: {a.preset} (PRESET_READING.md in the run folder)."


def spec_lines(A):
    """The audit spec in words (printed at the start of every run; part of the text except under the Hydreigon
    reading, whose text stays as it was)."""
    ow = lambda t: "/".join(A["owners"][t])  # noqa: E731
    L = [f"Audited ({A['file']}; card texts from lib/card.py's database, ids read by the engine from the deck file):",
         "  attacks: " + ", ".join(f"{t} ({ow(t)})" for t in A["attacks"]) + ".",
         "  abilities: " + (", ".join(f"{b['name']} ({'/'.join(b['owners'])}; {b['kind']}"
                                      + (f", {b['self_dmg']} to itself" if b["self_dmg"] else "") + ")"
                                      for b in A["abilities"]) or "none") + ".",
         "  attacks that put the opponent's Active to sleep: " + (", ".join(A["sleep"]) or "none") + "."
         + (f" Bench size counted when {A['bench_attack']} is used." if A["bench_attack"] else ""),
         "  every attack and ability in the list is audited: "
         + ("yes" if not A["unaudited"] else "NO, not audited: " + ", ".join(A["unaudited"])) + "."
         + (f" Ids missing from the database: {A['unknown_ids']}." if A["unknown_ids"] else ""),
         f"  'Would knock out' rule: {A['ko_rule']}."]
    return L


# ---------------------------------------------------------------- one decision, one game
def _init(S, nets, focus, A):
    T.set_decks(S)
    env = T.make_env()
    dim = env.obs_dim + env.action_dim
    _W.update(env=env, nets={d: T.load_scorer(p, dim) for d, p in nets.items()}, focus=focus, audit=A)


def look(env, p, mv):
    """One decision of the focus deck: which audited attacks were on offer (chosen? would it knock out?), which
    abilities, the moves' kinds (attacking and benching), bench size when the bench attack is chosen, and whether
    the move is a sleep attack that leaves the opponent's Active in play (an Asleep turn created)."""
    A = _W["audit"]
    acts = [json.loads(x) for x in env.raw.legal_actions_json()]
    view = json.loads(env.raw.describe(p))
    me, opp = view["me"]["board"], view["them"]["board"][0]
    kinds = [x if isinstance(x, str) else next(iter(x)) for x in acts]
    title = lambda x: x.get("Attack", {}).get("title") if isinstance(x, dict) else None  # noqa: E731
    labels = []

    def fixed_ko(i):
        # the fixed rule (the Hydreigon readout's): the opponent's Active had no more HP left than the printed damage
        return opp is not None and opp["hp_left"] <= acts[i]["Attack"]["fixed_damage"]

    def ko(i):
        if A["ko_rule"] == "fixed":
            return fixed_ko(i)
        if not labels:
            labels.append(env.raw.outcome_labels(KO_COPIES))
        return labels[0][i][0] >= 1

    att = {}
    for name in A["attacks"]:
        idx = [i for i, x in enumerate(acts) if title(x) == name]
        if idx:
            # [chosen, would knock out under the run's rule, under the fixed rule]. The third is a second reading of
            # the same position (plain reads of the view and the legal move); it plays and changes nothing.
            att[name] = [mv in idx, bool(ko(idx[0])), bool(fixed_ko(idx[0]))]
    ab = {}
    for b in A["abilities"]:
        if b["kind"] == "activated":
            idx = [i for i, x in enumerate(acts) if isinstance(x, dict) and "UseAbility" in x
                   and (me[x["UseAbility"]["in_play_idx"]] or {}).get("name") in b["owners"]]
            hp = lambda i: me[acts[i]["UseAbility"]["in_play_idx"]]["hp_left"]  # noqa: E731
            ab[b["name"]] = [any(hp(i) > b["self_dmg"] for i in idx), mv in idx,
                             mv in idx and b["self_dmg"] > 0 and hp(mv) <= b["self_dmg"]]
        elif b["kind"] == "evolve-early":
            early = (me[0] is not None and me[0]["name"] in b["owners"]
                     and (view["turn"] <= 2 or me[0]["played_this_turn"]))
            idx = [i for i, x in enumerate(acts) if early and isinstance(x, dict) and "Evolve" in x
                   and x["Evolve"]["in_play_idx"] == 0]
            ab[b["name"]] = [bool(idx), mv in idx, False]
    rec = {"turn": view["turn"], "end": acts[mv] == "EndTurn", "att": att, "ab": ab,
           "atk": ["Attack" in kinds, kinds[mv] == "Attack"], "place": ["Place" in kinds, kinds[mv] == "Place"]}
    t = title(acts[mv])
    if t is not None and t in A["sleep"] and not (att[t][1] if t in att else ko(mv)):
        rec["asleep"] = any(x is not None and x["name"] in A["asleep_owners"] for x in me)
    if t is not None and t == A["bench_attack"]:
        rec["bench"] = sum(x is not None for x in me[1:])
    return rec


def new_count(A):
    c = {"attacks": {n: dict.fromkeys(ATT_KEYS, 0) for n in A["attacks"]},
         "abilities": {b["name"]: {"turns": 0, "used": 0, "self_ko": 0} for b in A["abilities"]
                       if b["kind"] in ("activated", "evolve-early")},   # automatic ones: "asleep" below
         "asleep": {"created": 0, "with_owner": 0}, "habits": dict.fromkeys(HABIT_KEYS, 0),
         "bench_at": [0, 0, 0, 0]}
    if A["ko_rule"] == "engine":
        # the same offered turns split by the fixed rule (printed damage), printed beside the engine rule's split so
        # the Hydreigon table stays comparable; under the fixed rule it would be the same numbers, so it isn't kept
        c["attacks_fixed"] = {n: dict.fromkeys(ATT_KEYS, 0) for n in A["attacks"]}
    return c


def _split(k, ds, name, j):
    """One turn `ds` of one attack into k: used / passed / other, classified by look()'s knockout flag j (1 = the
    run's rule, 2 = the fixed rule) at the decision where it was used, or where the turn ended."""
    used = [r for r in ds if name in r["att"] and r["att"][name][0]]
    passed = [r for r in ds if name in r["att"] and r["end"]]
    if used:
        k["ko_used" if used[0]["att"][name][j] else "noko_used"] += 1
    elif passed:
        k["ko_passed" if passed[0]["att"][name][j] else "noko_passed"] += 1
    elif any(name in r["att"] for r in ds):
        k["other"] += 1


def tally(recs, A):
    """Per turn of the focus deck, as the transcripts file counted k3: an attack used (classified at the decision
    where it was used), passed (the turn ended with EndTurn while it was on offer; classified there), or offered
    earlier in the turn but not when the turn ended ("other"). An ability: turns it was offered (usable) and turns it
    was used. Attacking and benching: of the turns where the move was on offer (setup excluded, as audit_v5.py).
    Under the engine rule the same turns are also split by the fixed rule ("attacks_fixed"); only the knockout
    split can differ, since used, passed and other don't depend on the rule."""
    c = new_count(A)
    turns = {}
    for r in recs:
        turns.setdefault(r["turn"], []).append(r)
    for t, ds in turns.items():
        for name, k in c["attacks"].items():
            _split(k, ds, name, 1)
            if "attacks_fixed" in c:
                _split(c["attacks_fixed"][name], ds, name, 2)
        for name, k in c["abilities"].items():
            if any(r["ab"][name][0] for r in ds):
                k["turns"] += 1
                k["used"] += any(r["ab"][name][1] for r in ds)
            k["self_ko"] += sum(r["ab"][name][2] for r in ds)
        made = [r["asleep"] for r in ds if "asleep" in r]
        if made:
            c["asleep"]["created"] += 1
            c["asleep"]["with_owner"] += any(made)
        for r in ds:
            if "bench" in r:
                c["bench_at"][r["bench"]] += 1
        if t > 0:
            h = c["habits"]
            h["turns"] += 1
            if any(r["atk"][0] for r in ds):
                h["attack_turns"] += 1
                h["attack_made"] += any(r["atk"][1] for r in ds)
            if any(r["place"][0] for r in ds):
                h["bench_turns"] += 1
                h["bench_made"] += any(r["place"][1] for r in ds)
    return c


def add_into(dst, src):
    for k, v in src.items():
        if isinstance(v, dict):
            add_into(dst[k], v)
        elif isinstance(v, list):
            dst[k] = [x + y for x, y in zip(dst[k], v)]
        else:
            dst[k] += v
    return dst


def total(results, A):
    c = new_count(A)
    for r in results:
        add_into(c, r["count"])
    return c


def play(task):
    """("nvn", game): both seats played by their own network, live. ("replay", row): a recorded confirmation game
    (a network in one seat, k3 in the other) replayed from its moves; the network also re-chooses each move, which
    proves the weights file is the one that played."""
    kind, g = task
    env, nets, focus, A = _W["env"], _W["nets"], _W["focus"], _W["audit"]
    d0, d1 = g["decks"]
    fseat = g["decks"].index(focus)
    rng = np.random.default_rng(g["seed"])  # tie-breaks, exactly as eval_chunk
    moves = None
    if kind == "nvn":
        env.reset(T.DECKS["paths"][d0], T.DECKS["paths"][d1], g["seed"])
    else:
        seat = g["bot_seat"]
        env.reset(T.DECKS["paths"][d0], T.DECKS["paths"][d1], g["seed"], bots=[None, "k3"] if seat == 0 else ["k3", None])
        moves = g["moves"]
    recs, played, same = [], [], 0
    while not env.done:
        p = env.current_player
        obs, feats = env.observe(p), env.action_features()
        i = T.pick(nets[g["decks"][p]].score_actions(obs, feats), rng)
        if moves is not None:
            if len(played) >= len(moves):
                break   # more decisions than were recorded: not an exact replay
            same += i == moves[len(played)]
            i = moves[len(played)]
        if p == fseat:
            recs.append(look(env, p, i))
        played.append(i)
        env.step(i)
    res = env.result() if env.done else None
    out = {"kind": kind, "seed": g["seed"], "decks": g["decks"], "count": tally(recs, A), "decisions": len(played),
           "same": same}
    if kind == "nvn":
        out.update(winner=res[0], points=list(res[1]), turns=res[2], moves=played, ok=True)
    else:
        out.update(deck=g["deck"], ok=res is not None and len(played) == len(moves) and res[0] == g["winner"]
                   and res[2] == g["turns"])
    return out


# ---------------------------------------------------------------- text
def score(g, focus):
    s = g["decks"].index(focus)
    return 1.0 if g["winner"] == s else (0.5 if g["winner"] == -1 else 0.0)


def paired_line(label, games, bars, focus, width):
    """Focus deck's result in one condition, paired with k3 v k3 on the same seeds."""
    seeds = sorted(s for s in games if s in bars)
    n = len(seeds)
    if not n:
        return f"  {label:<{width}}     0   (no games)", float("nan"), float("nan")
    won = [float(games[s]["winner"] == games[s]["decks"].index(focus)) for s in seeds]
    base = [float(bars[s]["winner"] == bars[s]["decks"].index(focus)) for s in seeds]
    sc = [score(games[s], focus) for s in seeds]
    draws = sum(games[s]["winner"] == -1 for s in seeds)
    d = np.array(won) - np.array(base)
    half = 1.96 * d.std(ddof=1) / math.sqrt(n) if n > 1 else float("nan")
    only_here = int(sum(a > b for a, b in zip(won, base)))
    only_bar = int(sum(b > a for a, b in zip(won, base)))
    return (f"  {label:<{width}}{n:>6}{100 * np.mean(won):>8.1f}{draws:>7}{100 * np.mean(sc):>9.1f}"
            f"{100 * d.mean():>+10.1f} ±{100 * half:<5.1f}{only_here:>9} / {only_bar:<5}"), 100 * np.mean(sc), 100 * d.mean()


def hr_line(label, c, width):
    return (f"  {label:<{width}}{c['ko_used']:>6} / {c['ko_passed']:<5}{'(' + c_pct(c, True) + ')':<8}"
            f"{c['noko_used']:>8} / {c['noko_passed']:<5}{'(' + c_pct(c, False) + ')':<8}{c['other']:>6}")


def c_pct(c, ko):
    u, p = (c["ko_used"], c["ko_passed"]) if ko else (c["noko_used"], c["noko_passed"])
    return f"{100 * u / (u + p):.0f}%" if u + p else "—"


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "—"


def ko_words(A, focus_name, opp_name):
    if A["ko_rule"] == "fixed":
        return [f"   'KOs' = {opp_name}'s Active had no more HP left than the attack's printed damage (fixed_damage in the",
                "   legal move), the transcripts file's definition."]
    return [f"   'KOs' = a sure knockout, the knockout audit's definition (audit_v5.py): in each of {KO_COPIES} copies of the true",
            "   game under different chance seeds, the move gains the pilot at least one point (analysis only; the game",
            "   itself is untouched). Every damage change and end-of-turn effect counts (for Altaria: Mega Harmony's",
            "   bench bonus, Weakness, Training Area, Bad Dreams), which the printed damage leaves out. This rule is primary.",
            f"   Under each row, '{FIXED_LABEL.strip()}' splits the same turns by the Hydreigon readout's rule",
            f"   ({opp_name}'s Active had no more HP left than the attack's printed damage), so that table stays comparable.",
            "   The two rules are not interchangeable: the fixed rule ignores Mega Harmony's bench bonus, Weakness, Training "
            "Area and Bad Dreams."]


def audit_lines(rows, A, w=46):
    """PRESET_READING item 3's counts for the conditions in `rows` [(label, count)]: one block per attack, then the
    abilities, Asleep turns created, bench size at the bench attack, and attacking and benching. Every script prints
    its own conditions with these same lines, so the columns line up across readout.py, kp3_rows.py and k3_counts.py."""
    L = []
    for name in A["attacks"]:
        L.append(f"  {name + ' (' + '/'.join(A['owners'][name]) + ')':<{w + 2}}"
                 "   KOs: used / passed    doesn't KO: used / passed   other")
        for label, c in rows:
            L.append("  " + hr_line(label, c["attacks"][name], w))
            if "attacks_fixed" in c:   # the engine rule: the fixed rule's split of the same turns, beside it
                L.append("  " + hr_line(FIXED_LABEL, c["attacks_fixed"][name], w))
    for b in A["abilities"]:
        who = "/".join(b["owners"])
        if b["kind"] == "activated":
            L.append(f"  {b['name']} ({who}): turns it was usable"
                     + (f" on a {who} with more than {b['self_dmg']} HP left" if b["self_dmg"] else "")
                     + " / turns it was used (use %)" + ("; uses that knocked out its own " + who if b["self_dmg"] else ""))
            L += [f"    {label:<{w}}{c['abilities'][b['name']]['turns']:>6} / {c['abilities'][b['name']]['used']:<6}"
                  f"({pct(c['abilities'][b['name']]['used'], c['abilities'][b['name']]['turns'])})"
                  + (f"   self-KO {c['abilities'][b['name']]['self_ko']}" if b["self_dmg"] else "") for label, c in rows]
        elif b["kind"] == "evolve-early":
            L.append(f"  {b['name']} ({who}): turns the Active {who} could evolve only because of it (the player's first"
                     f" turn, or the turn it was played) / turns it evolved then (use %)")
            L += [f"    {label:<{w}}{c['abilities'][b['name']]['turns']:>6} / {c['abilities'][b['name']]['used']:<6}"
                  f"({pct(c['abilities'][b['name']]['used'], c['abilities'][b['name']]['turns'])})" for label, c in rows]
        else:
            L += [f"  {b['name']} ({who}) is automatic; counted as Asleep turns created: turns ending with "
                  + " / ".join(A["sleep"]) + " used without a knockout,",
                  f"  per 100 of the pilot's turns with a choice (setup excluded), and how many of those turns had a {who} in play "
                  f"(and their share; {b['name']} needs a {who} in play)"]
            L += [f"    {label:<{w}}{c['asleep']['created']:>6} of {c['habits']['turns']:<6}"
                  f"({100 * c['asleep']['created'] / c['habits']['turns'] if c['habits']['turns'] else 0:.1f} per 100)"
                  f"   with {who} in play {c['asleep']['with_owner']} of {c['asleep']['created']} "
                  f"({pct(c['asleep']['with_owner'], c['asleep']['created'])})" for label, c in rows]
            L += [f"    Limits: a count of sleep attacks used, not of damage dealt. Not tracked: waking at the Checkup, and "
                  f"the {b['name']} hits that",
                  "    actually landed. A sleep attack on an Active that was already Asleep also counts."]
    if A["bench_attack"]:
        L.append(f"  Bench size when {A['bench_attack']} was used (Benched Pokemon at that moment: 0 / 1 / 2 / 3; mean)")
        for label, c in rows:
            n = sum(c["bench_at"])
            mean = sum(i * k for i, k in enumerate(c["bench_at"])) / n if n else float("nan")
            L.append(f"    {label:<{w}}" + " / ".join(f"{k:>4}" for k in c["bench_at"]) + f"   (mean {mean:.2f} of {n})")
    L.append("  Attacking and benching on offered turns (setup excluded; audit_v5.py's definitions): of the turns where an")
    L.append("  attack / a Basic to the Bench was on offer, the share where one was made")
    for label, c in rows:
        h = c["habits"]
        L.append(f"    {label:<{w}} attacked {h['attack_made']:>5} of {h['attack_turns']:<5} ({pct(h['attack_made'], h['attack_turns'])})"
                 f"   benched {h['bench_made']:>5} of {h['bench_turns']:<5} ({pct(h['bench_made'], h['bench_turns'])})")
    return L


def ko_audit_file(run_dir, deck, ckpt):
    return T.HERE / f"results/ko_audit/v5_{run_dir.name}_{deck}_{ckpt}.json"


def free_name(path):
    """Never overwrite: a taken name gets a time suffix."""
    if not path.exists():
        return path
    alt = path.with_name(f"{path.stem}_{time.strftime('%Y%m%d-%H%M%S')}{path.suffix}")
    if alt.exists():
        raise SystemExit(f"{alt} exists; wait a second and rerun")
    return alt


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--run", required=True, help="run folder (relative paths are taken from the rl folder)")
    ap.add_argument("--games", type=int, default=2000, help="first N confirmation deals (default 2000 = all)")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--out", default=str(HERE / "readout.txt"))
    ap.add_argument("--allow-missing-report", action="store_true",
                    help="run even if REPORT.txt or a knockout-audit file isn't there (section 3 then says MISSING); "
                         "only if the run's report step failed")
    add_preset_options(ap)
    a = apply_preset(ap.parse_args())
    t0 = time.time()
    run_dir = Path(a.run) if Path(a.run).is_absolute() else T.HERE / a.run
    S = json.loads((run_dir / "settings.json").read_text())
    T.check_decks_unchanged(run_dir, S)   # the recorded games were played with the run's own deck files
    A = resolve(S, a)
    legacy = a.reading == "hydreigon"     # the Hydreigon readout's text, unchanged
    spec = spec_lines(A)
    print("\n".join(spec) + "\n")
    focus, opp = A["deck"], A["opp"]
    names = list(S["pool"])
    st = json.loads((run_dir / "state.json").read_text())

    # 1. the confirmed checkpoints, as finish() records them
    picks = (st.get("verdict") or {}).get("picks")
    if not picks or set(picks) != set(names):
        raise SystemExit("state.json has no confirmed checkpoint per network yet (verdict 'picks'); "
                         "run this after the run has finished its confirmations")
    cf = {d: next(c for c in st["confirmations"] if c["deck"] == d and c["name"] == picks[d]) for d in names}
    rep = run_dir / "REPORT.txt"
    rep_text = rep.read_text() if rep.exists() else None
    rep_ok = {d: rep_text is not None and f"Confirmation of the {d} network's {picks[d]} (used for the verdict)" in rep_text
              for d in names}
    nets = {d: str(T.ckpt_path(run_dir, picks[d], d)) for d in names}
    if not legacy and not a.allow_missing_report:
        # the readout is written once and never overwritten, so it waits for run_training_v5.sh's report steps
        # (audit_v5.py writes both knockout audits, then report_v5.py writes REPORT.txt) instead of printing MISSING
        missing = [p.name for p in [ko_audit_file(run_dir, d, picks[d]) for d in (focus, opp)] + [rep] if not p.exists()]
        if missing:
            raise SystemExit(f"not there yet: {', '.join(missing)}. Run this after run_training_v5.sh's report steps "
                             "(audit, REPORT.txt); --allow-missing-report only if a report step failed")

    # the deals: the bars' own rows, checked against the settings' formula (bar_games in train_v5.py)
    rows = [json.loads(x) for x in (run_dir / "eval_games.jsonl").read_text().splitlines()
            if '"kind": "bar"' in x or '"kind": "confirmation"' in x]
    pair = sorted([focus, opp])
    bars = {g["seed"]: g for g in rows if g["kind"] == "bar" and sorted(g["decks"]) == pair}
    formula = {s: [d0, d1] for s, d0, d1, *_ in T.bar_games(S) if sorted([d0, d1]) == pair}
    off = [s for s, g in bars.items() if formula.get(s) != g["decks"]]
    if off:
        raise SystemExit(f"{len(off)} bar rows don't match the settings' seed/seat formula (first: seed {off[0]})")
    seeds = sorted(bars)[:a.games]
    keep = set(seeds)
    bars = {s: bars[s] for s in seeds}
    conf = {d: {g["seed"]: g for g in rows if g["kind"] == "confirmation" and g.get("ckpt") == picks[d]
                and g.get("deck") == d and g["seed"] in keep} for d in names}
    bad_deal = [s for d in names for s, g in conf[d].items() if g["decks"] != bars[s]["decks"]]
    if bad_deal:
        raise SystemExit(f"{len(bad_deal)} confirmation rows sit on a different deal than the bar with the same seed")

    # 2 + 3. play network v network, replay the focus network's confirmation games, and a load check of the other
    tasks = [("nvn", {"seed": s, "decks": bars[s]["decks"]}) for s in seeds]
    tasks += [("replay", conf[focus][s]) for s in sorted(conf[focus])]
    tasks += [("replay", conf[opp][s]) for s in sorted(conf[opp])[:LOAD_CHECK_GAMES]]
    init = (S, nets, focus, A)
    if a.workers == 1:
        _init(*init)
        results = [play(t) for t in tasks]
    else:
        with mp.get_context("spawn").Pool(a.workers, initializer=_init, initargs=init) as pool:
            results = pool.map(play, tasks, chunksize=4)
    nvn = {r["seed"]: r for r in results if r["kind"] == "nvn"}
    rep_f = [r for r in results if r["kind"] == "replay" and r["deck"] == focus]
    rep_o = [r for r in results if r["kind"] == "replay" and r["deck"] == opp]
    good_f = [r for r in rep_f if r["ok"]]

    # the text
    F, O = focus.capitalize(), opp.capitalize()
    base = S["seeds"]["confirm"]
    ident = json.loads((run_dir / "identity.json").read_text())["sha256"]
    addon_ok = ident.get("add-on") in (None, T.sha_file(T.addon_path()))
    L = [f"{F} network run readout — {run_dir.name}   ({time.strftime('%Y-%m-%d %H:%M')})", "",
         f"Confirmed checkpoints (state.json verdict picks, recorded by finish() in train_v5.py): "
         + ", ".join(f"{d} {picks[d]} ({100 * cf[d]['margin']:+.1f} over k3)" for d in names) + ".",
         "  REPORT.txt names the same ones as 'used for the verdict': "
         + ("not written yet" if rep_text is None else ", ".join(f"{d} {'yes' if rep_ok[d] else 'NO'}" for d in names)),
         "  Weights: " + ", ".join(f"{Path(p).name} {T.sha_file(p)[:12]}" for p in nets.values())
         + f". Add-on {T.sha_file(T.addon_path())[:12]} " + ("(the run's own)" if addon_ok else "(DIFFERENT from the run's identity.json)"),
         ""]
    if not legacy:
        L += [preset_line(a) + " Limitless: "
              + (f"{F} v {O} {a.limitless[0]} ± {a.limitless[1]}" if a.limitless else "none given") + "."] + spec + [""]
    L += [f"Deals: the run's own confirmation deals, {len(seeds):,} of them: seed {base:,} + i for i = "
          f"{seeds[0] - base} to {seeds[-1] - base} (settings 'confirm' base), {names[0]} in seat 0 on even i and "
          f"seat 1 on odd i, as in the bars; the engine's coin decides who goes first.",
          "  No new seeds. Reusing this block is deliberate: it is reserved for this run's evaluation, and it makes the",
          "  four rows below paired. Network v network starts from the same deal as the bar; later draws can differ",
          "  once the play differs.", "",
          f"1. {F}'s result on those deals (row = who pilots each side). 'change' = won % minus k3 v k3's on the same",
          "   deals, with a paired 95% interval (1.96 x standard deviation of the per-deal difference / sqrt n).",
          f"   'won only' = deals {F} won here and not in k3 v k3 / the reverse. Score counts a draw as half (Limitless's way).", ""]
    w = 38
    L.append(f"  {'condition':<{w}}{'n':>6}{'won %':>8}{'draws':>7}{'score %':>9}{'change':>10}{'':>7}{'won only here / in bar':>24}")
    bar_line = paired_line(f"k3 {F} v k3 {O} (the bars)", bars, bars, focus, w)
    rows_out = [bar_line,
                paired_line(f"network {F} v k3 {O}", conf[focus], bars, focus, w),
                paired_line(f"k3 {F} v network {O}", conf[opp], bars, focus, w),
                paired_line(f"network v network (new)", nvn, bars, focus, w)]
    L += [r[0] for r in rows_out]
    full = len(seeds) == len(conf[focus]) == S["confirm_per_matchup"]
    if full:
        t = f"{focus}>{opp}"
        mine = rows_out[1][2]
        L.append(f"  Check: the run's own confirmed margin for {F} is {100 * cf[focus]['margin']:+.1f}; this table's "
                 f"{mine:+.1f} ({'same' if abs(mine - 100 * cf[focus]['margin']) < 0.05 else 'DIFFERENT'}); "
                 f"bars {100 * st['bars'][t]['win_rate']:.1f}% in state.json.")
    L.append("")

    c_rep, c_nvn = total(good_f, A), total(nvn.values(), A)
    same_f, dec_f = sum(r["same"] for r in rep_f), sum(r["decisions"] for r in rep_f)
    same_o, dec_o = sum(r["same"] for r in rep_o), sum(r["decisions"] for r in rep_o)
    replay_line = (f"  Replays: {len(good_f):,} of {len(rep_f):,} {F} confirmation games replayed exactly (winner and turns); the "
                   f"{F} network re-chose the recorded move at {same_f:,} of {dec_f:,} decisions, the {O} network at {same_o:,} "
                   f"of {dec_o:,} (first {len(rep_o)} of its confirmation games). All equal = the right weights were loaded.")
    if legacy:
        # Hyper Ray and Roar in Unison: the Hydreigon readout's own section 2, word for word
        at = A["attacks"][0]
        roar = next((b for b in A["abilities"] if b["kind"] == "activated"), None)
        w2 = 42
        L += [f"2. {at}, per turn of the {F} network where it was on offer: used / passed (use %).",
              f"   'KOs' = {O}'s Active had no more HP left than {at}'s damage (the attack's own fixed_damage in",
              "   the legal move; 130 for Hyper Ray), the transcripts file's definition. Passed = the turn ended with EndTurn",
              "   while it was on offer (classified there); 'other' = offered earlier in the turn, not when it ended.", "",
              "  " + " " * w2 + "   KOs: used / passed    doesn't KO: used / passed   other",
              hr_line(f"network {F} v k3 {O} (replayed)", c_rep["attacks"][at], w2),
              hr_line("network v network (live)", c_nvn["attacks"][at], w2),
              "  k3 reference numbers (not recomputed; Hyper Ray, other seeds):"] + REFERENCE
        if roar:
            owner = roar["owners"][0]
            for label, c in ((f"network {F} v k3 {O}", c_rep), ("network v network", c_nvn)):
                k = c["abilities"][roar["name"]]
                L.append(f"  {roar['name']}, {label}: used on {k['used']} of the {k['turns']} turns it was usable on a "
                         f"{owner} with more than {roar['self_dmg']} HP left"
                         + (f" ({100 * k['used'] / k['turns']:.0f}%)" if k["turns"] else "")
                         + f"; uses that knocked out its own {owner}: {k['self_ko']}.")
        L += [replay_line, ""]
    else:
        L += [f"2. The audit (PRESET_READING item 3, descriptive): the {F} network's play, per turn of its own where the",
              "   move was on offer. Attacks: used / passed (use %); passed = the turn ended with EndTurn while it was on",
              "   offer (classified there); 'other' = offered earlier in the turn, not when it ended."]
        L += ko_words(A, F, O) + [
            f"   k3's and kp3's own counts on the same deals: k3_counts.py (--bot k3, --bot kp3); the network against kp3's",
            f"   {O}: kp3_rows.py. Every script prints these same lines, so the columns line up.", ""]
        L += audit_lines([(f"network {F} v k3 {O} (replayed)", c_rep), ("network v network (live)", c_nvn)], A)
        L += [replay_line, ""]
    if len(good_f) < len(rep_f):
        L.insert(0, f"INCOMPLETE: {len(rep_f) - len(good_f)} confirmation games did not replay exactly; they are left "
                    f"out of the {'/'.join(A['attacks'])} count.")
    bad_o = [r for r in rep_o if not r["ok"]]
    weights_bad = same_f != dec_f or same_o != dec_o or bad_o or not rep_f or not rep_o
    if weights_bad:
        L.insert(0, f"INCOMPLETE: weights check failed ({F} re-chose {same_f}/{dec_f}, {O} {same_o}/{dec_o}, "
                    f"{len(bad_o)} {O} replays not exact); the network v network row and the READING are not trustworthy.")

    if legacy:
        L += legacy_reading(a, S, A, cf, c_rep, c_nvn, rows_out, run_dir, picks, focus, opp, weights_bad)
    else:
        L += preset_reading(a, S, A, cf, c_rep, rows_out, run_dir, picks, focus, opp, weights_bad, full,
                            len(good_f) == len(rep_f), nets, len(seeds))
    L += ["", f"Took {time.time() - t0:.0f} s with {a.workers} worker{'s' if a.workers != 1 else ''}. "
              f"Games played here: {len(nvn):,} network v network, {len(rep_f) + len(rep_o):,} confirmation replays."]
    text = "\n".join(L) + "\n"
    print(text)
    out = free_name(Path(a.out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    games_path = free_name(out.with_name(out.stem + "_nvn_games.jsonl"))
    with open(games_path, "w") as f:
        for s in seeds:
            r = nvn[s]
            f.write(json.dumps({"kind": "nvn", "seed": s, "decks": r["decks"], "nets": picks, "winner": r["winner"],
                                "points": r["points"], "turns": r["turns"], "moves": r["moves"]}) + "\n")
    counts_path = free_name(out.with_name(out.stem + "_counts.jsonl"))
    with open(counts_path, "w") as f:
        for r in results:
            f.write(json.dumps({"kind": r["kind"], "seed": r["seed"], "decks": r["decks"],
                                "network": r.get("deck", "both"), "ok": r["ok"], "count": r["count"]}) + "\n")
    print(f"Written: {out}\n         {games_path}\n         {counts_path}")


def legacy_reading(a, S, A, cf, c_rep, c_nvn, rows_out, run_dir, picks, focus, opp, weights_bad):
    """RUN5.md's Hyper Ray reading, as the Hydreigon readout printed it (section 3 there)."""
    F, O = focus.capitalize(), opp.capitalize()
    at = A["attacks"][0]
    gain = 100 * cf[focus]["margin"]
    c = c_rep["attacks"][at]
    noko = c["noko_used"] + c["noko_passed"]
    rate = c["noko_used"] / noko if noko else None
    if rate is None:
        chips, why = None, "no turn offered it without a KO, so there is nothing to read"
    elif rate <= K3_NOKO_RATE:
        chips, why = False, f"{100 * rate:.0f}% is no more than k3's 3%"
    elif rate >= SEARCHED_NOKO_RATE:
        chips, why = True, f"{100 * rate:.0f}% is at the searched bots' level (82-84%)"
    else:
        chips, why = None, (f"{100 * rate:.0f}% is between k3's 3% and the searched bots' 82-84%; RUN5 gives no number "
                            f"for 'chips', so both branches are shown")
    case = {(True, True): "chips with Hyper Ray and gains 10+ over k3 -> learning finds the play k3 misses",
            (True, False): "chips but lands near k3 -> check its benching before concluding",
            (False, True): "gains without chipping -> the gain is elsewhere",
            (False, False): "neither -> ambiguous, and only then is a forced-Hyper-Ray k3 build worth it"}
    g10 = gain >= 10
    L = ["3. READING (RUN5.md's reading, set before the run, applied as written; no new thresholds)"]
    if weights_bad:
        L.append("  NOT TRUSTWORTHY: the weights check failed (see the top line); don't act on this reading.")
    L += [f"  Gain over k3: the {F} network's confirmed margin is {gain:+.1f} points (the run's own number, "
          f"{S['confirm_per_matchup']:,} paired deals; its paired 95% interval is in table 1). RUN5's line is 10+: "
          f"{'yes' if g10 else 'no'}.",
          f"  Chips with Hyper Ray: it used {at} on {c['noko_used']} of {noko} turns where it was on offer "
          f"and wouldn't KO"
          + (f" ({100 * rate:.0f}%)" if rate is not None else "")
          + f" in its games against k3 ({c_pct(c_nvn['attacks'][at], False)} against the {O} network). k3: 3%. Searched bots: 82-84%.",
          f"  RUN5 sets no number for 'chips'. Read here only against those two references: {why}.",
          "  The see-everything file's guide: near ~80% = the network learned the same fix as the searched bot; wins more",
          "  with Hyper Ray still low = it found something else."]
    branches = [chips] if chips is not None else [True, False]
    for b in branches:
        pre = "  -> " if chips is not None else f"  If this {'counts' if b else 'does not count'} as chipping: "
        L.append(pre + case[(b, g10)] + ".")
    if not g10 and (chips is None or chips):
        L.append("     RUN5 doesn't define 'near k3'; any confirmed gain under +10 is read as this branch here.")
        au = ko_audit_file(run_dir, focus, picks[focus])
        if au.exists():
            r = json.loads(au.read_text())
            b_, k_ = r["stats"].get(f"bot|{focus}>{opp}"), r["stats"].get(f"k3|{focus}>{opp}")
            p_ = lambda s, k: f"{s[k + '_made'] / s[k + '_turns']:.0%}" if s and s[k + "_turns"] else "—"  # noqa: E731
            L.append(f"     Benching (knockout audit, {au.name}{'' if r.get('complete') else ', INCOMPLETE'}): the network "
                     f"benched {p_(b_, 'bench')} of the turns it could (k3 {p_(k_, 'bench')}); attacked "
                     f"{p_(b_, 'attack')} (k3 {p_(k_, 'attack')}).")
        else:
            L.append(f"     Benching: the knockout audit file isn't there ({au.name}); see REPORT.txt.")
    if a.limitless:
        mid, pm = a.limitless
        miss = lambda x: abs(x - mid)  # noqa: E731
        k3s, nvs = rows_out[0][1], rows_out[3][1]
        L += [f"  Toward Limitless ({F} {mid} ± {pm}, results/limitless_check_2026-09-23.md), scores with draws as half:",
              f"    k3 v k3 {k3s:.1f} (off by {miss(k3s):.1f}); network v network {nvs:.1f} (off by {miss(nvs):.1f}): "
              f"{'moved toward' if miss(nvs) < miss(k3s) else 'did not move toward'} Limitless; "
              f"{'inside' if miss(nvs) <= pm else 'outside'} Limitless's 95% range.",
              f"    One side only: network {F} v k3 {O} {rows_out[1][1]:.1f} (off by {miss(rows_out[1][1]):.1f}); "
              f"k3 {F} v network {O} {rows_out[2][1]:.1f} (off by {miss(rows_out[2][1]):.1f}).",
              "    RUN5's warning: a bot can gain over k3 and still take the matchup further from reality."]
    L += ["  Before any of this is read: RUN5 says the result isn't read until the auditor's pair checks pass. This",
          "  readout does not run them."]
    return L


def audit_summary(path):
    """The knockout audit's own table lines (audit_v5.py's summary) and its stats, or None when it isn't there."""
    if not path.exists():
        return None
    r = json.loads(path.read_text())
    lines = r["summary"].splitlines()
    head = next((i for i, x in enumerate(lines) if x.startswith("  matchup")), None)
    return r, ([] if head is None else lines[head:])


def preset_reading(a, S, A, cf, c_rep, rows_out, run_dir, picks, focus, opp, weights_bad, full, replays_ok, nets,
                   n_deals):
    """PRESET_READING.md's items 1 and 3 (item 2 is kp3_rows.py's), plus the knockout audit (section 3)."""
    F, O = focus.capitalize(), opp.capitalize()
    L = [f"3. The knockout audit (PRESET_READING item 3; audit_v5.py, written by the run's report steps). 'bot' = the",
         "   network piloting the first deck, 'k3' = k3 piloting it on the same seeds (the bars).",
         "   STATED DEVIATION from PRESET_READING item 3, which asks for the audit \"network against kp3\": the knockout",
         "   audit shown here is the run's own, the network against k3. Reason: a knockout audit of net|kp3 would be new",
         "   code. The decisive D (net|kp3 win % minus kp3|kp3 win %, kp3_rows.py) is unaffected, and the attack and bench",
         "   counts for net|kp3 are live in kp3_rows.py's audit block. A knockout audit against kp3, if ever needed for a",
         "   decision, is a later registered addition.", ""]
    got = {}
    for d in (focus, opp):
        p = ko_audit_file(run_dir, d, picks[d])
        s = audit_summary(p)
        got[d] = s
        if s is None:
            L.append(f"  MISSING: {p.name} isn't there yet (run_training_v5.sh writes it after the confirmations); "
                     "rerun this readout after the report steps.")
            continue
        r, table = s
        same_w = r["inputs"].get("checkpoint sha256", {}).get(d) == T.sha_file(nets[d])
        wtxt = "the same as this readout's" if same_w else "DIFFERENT from this readout's"
        L.append(f"  The {d} network's {picks[d]} ({p.name}; {'complete' if r.get('complete') else 'INCOMPLETE'}; "
                 f"weights {wtxt}):")
        L += ["  " + x for x in table]
    if got[focus] is not None and full and replays_ok:
        b = got[focus][0]["stats"].get(f"bot|{focus}>{opp}") or {}
        h = c_rep["habits"]
        mine = (h["attack_turns"], h["attack_made"], h["bench_turns"], h["bench_made"])
        theirs = tuple(b.get(k) for k in ("attack_turns", "attack_made", "bench_turns", "bench_made"))
        L.append(f"  Check: section 2's attacking/benching counts for network {F} v k3 {O} {mine} "
                 f"{'equal' if mine == theirs else 'DIFFER FROM'} the audit's {theirs} (turns offered, made; attack then bench).")
    L.append("")

    gain = 100 * cf[focus]["margin"]
    L += ["4. READING (PRESET_READING.md, fixed before training; applied as written, no new thresholds)"]
    if weights_bad or not replays_ok:
        L.append("  NOT TRUSTWORTHY: an identity gate failed (see the top lines); don't act on this reading.")
    if not full:
        L.append(f"  NOT THE PRE-SET READING: only {n_deals:,} of the run's {S['confirm_per_matchup']:,} confirmation "
                 "deals were read (--games); the identity gates and the network v network row are for those only.")
    L += [f"  Identity gates (PRESET 'Before anything is read'): the recorded confirmation games replayed exactly: "
          f"{'yes' if replays_ok else 'NO'}; the network re-chose every recorded move: {'NO' if weights_bad else 'yes'}.",
          ("  The pair checks passed before training (PRESET; rl/results/altaria_pair_checks_2026-09-25/). This readout"
           if a.reading == "altaria" else "  The pair checks are the run's own record, not this readout's. This readout"),
          "  does not run them."]
    if a.reading == "altaria":
        L += TRANSPARENCY
    L += [f"  Item 1, the run's own RUN5 line: the {F} network's confirmed margin over k3 is {gain:+.1f} points on "
          f"{S['confirm_per_matchup']:,} paired bar deals (state.json; its paired 95% interval is in table 1). +10 or "
          f"more counts as a gain: {'yes' if at_least_10(gain) else 'no'}.",
          "  Item 2, the decisive comparison D = (network v kp3) - (kp3 v kp3): kp3_rows.py, on the diagnostic add-on.",
          "  Item 3, the audit: sections 2 and 3 above, with k3_counts.py's k3 and kp3 counts and kp3_rows.py's network",
          f"  v kp3 counts beside them (descriptive; the knockout audit is against k3, the deviation stated in section 3)."]
    if a.limitless:
        mid, pm = a.limitless
        miss = lambda x: abs(x - mid)  # noqa: E731
        k3s, nvs = rows_out[0][1], rows_out[3][1]
        L += [f"  Network v network against Limitless ({F} {mid} ± {pm}, results/limitless_check_2026-09-23.md), scores",
              "  with draws as half:",
              f"    k3 v k3 {k3s:.1f} (off by {miss(k3s):.1f}); network v network {nvs:.1f} (off by {miss(nvs):.1f}): "
              f"{'moved toward' if miss(nvs) < miss(k3s) else 'did not move toward'} Limitless; "
              f"{'inside' if miss(nvs) <= pm else 'outside'} Limitless's 95% range.",
              f"    One side only: network {F} v k3 {O} {rows_out[1][1]:.1f} (off by {miss(rows_out[1][1]):.1f}); "
              f"k3 {F} v network {O} {rows_out[2][1]:.1f} (off by {miss(rows_out[2][1]):.1f})."]
        s = got[opp]
        if s is None:
            L.append(f"    The {O} network's own flaws: its knockout audit isn't there yet (see section 3).")
        else:
            st_ = s[0]["stats"]
            b, k = st_.get(f"bot|{opp}>{focus}"), st_.get(f"k3|{opp}>{focus}")
            f_ = lambda x, n, m: f"{x[n]:,} of {x[m]:,}" if x else "—"  # noqa: E731
            L += [f"    Beside it, the {O} network's own flaws (knockout audit, {ko_audit_file(run_dir, opp, picks[opp]).name}):"
                  f" it missed {f_(b, 'ko_missed', 'ko_turns')} sure knockouts",
                  f"    (k3 piloting {O} on the bars: {f_(k, 'ko_missed', 'ko_turns')}) and {f_(b, 'win_missed', 'win_turns')} "
                  f"sure wins (k3: {f_(k, 'win_missed', 'win_turns')}); attacked {pct(b['attack_made'], b['attack_turns']) if b else '—'} "
                  f"(k3 {pct(k['attack_made'], k['attack_turns']) if k else '—'}), benched "
                  f"{pct(b['bench_made'], b['bench_turns']) if b else '—'} (k3 {pct(k['bench_made'], k['bench_turns']) if k else '—'}).",
                  f"    A {O} network that misses more than k3 flatters {F} in the network v network row."]
    L.append("  Item 4: no follow-up training, whatever this shows.")
    return L


if __name__ == "__main__":
    main()

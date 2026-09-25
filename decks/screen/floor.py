#!/usr/bin/env python3
"""The A2 floor check (Dustin's decision, Sept 25; rl/RUN5.md A2 and section 8 of docs/REVIEW_2026-09-24_direction.md).

    python3 decks/screen/floor.py DECK.txt --out DIR [--games 240] [--pilot kp3] [--meta-pilot kp3]
                                  [--seed 7100] [--goldfish PATH] [--opponents DIR]
    python3 decks/screen/floor.py --self-check

A floor verdict needs all of: 240 games per matchup, kp3 on both sides, the opponents in decks/screen/opponents/, and
the coverage from the official release's goldfish (project_manifest.json available_release, hash checked). Any other
--games is a development run and gives no verdict. With 240 games but other pilots, opponents or goldfish, the page
reads "control reading, not a floor verdict" and names what differs (the positive control runs deck 14 under k3).

It plays the screen's own games with the official engine (the manifest's available release, via current_engine.py):
the deck against each list in decks/screen/opponents/, half in seat 0 (seed = seed + 1000 x opponent index) and half
in seat 1 (+500), with deckgym simulate --seed-stream, exactly as run_screen.py. Each call also writes the engine's
per-decision traces (--data-output: the board, every playable move and the chosen move) and per-game results
(--results-output) to a temporary folder, which is read one game at a time and then deleted. The verdict, the worst
matchups, the failure modes and the flagged-card counts all come from those same games. No 8-deck average is reported
for ranking.

Games: fixed at 240 per matchup, 1,920 per run (Dustin, Sept 25). Any other --games is a development run: no verdict.

Verdict (fixed before any floor game; the band is the screen's own binomial noise at 20%):
  n = games in the run; W = the deck's wins (draws are not wins); band = 1.96 x sqrt(0.2 x 0.8 / n).
  W/n below 0.2 - band: fail. Within the band: borderline. Above 0.2 + band: clears the floor.
  (n = 1,920: fail <= 349, borderline 350-418, clears >= 419. n = 480: 78 / 79-113 / 114.) The page prints these
  edges in wins, since the percentages round onto the edges.
  'untrusted' replaces 'fail' only when a flagged card with a countable role was used on under 25% of at least 20
  opportunities (a fail that may be the bot's blind spot rather than the deck's fault). Borderline never becomes
  untrusted. Unflagged cards are never counted. The 25% line is a flag for a person; the share is always printed.

Flagged card: a card of the list with any entry in A1's coverage (engine/examples/goldfish.rs --coverage): an
  incomplete engine status or a named limitation; a text the pilot leaves unpriced (the opponent-hand/deck text rule;
  for a public-pricing pilot, kp/kq/kd, texts in kp's 62 audited texts are priced and drop out); an attack k's damage
  estimate prices at printed damage; an effect that pays off during the opponent's turn, which the search doesn't
  play out. Printings of one card (same name, different ids) are one card: their turns are counted together.

Role of each flagged card (Dustin, Sept 25: every card has a job; the page prints the role beside its count so a
wrong role is visible). An opportunity is one of the deck's turns (game, turn number, setup included) on which:
  attacker                     its attack could be chosen with it Active (its flagged attacks if the flag names
                               attacks, else any of its attacks); used = that attack chosen.
  activated ability            UseAbility on it was offered; used = chosen.
  bench piece/passive ability  putting it into play (Place, or Evolve into it) was offered; used = chosen.
  wall                         it was the Active and a retreat was offered; used = it was still the Active at the
                               deck's last decision of that turn.
  Trainer (played)             playing it from hand was offered (a Tool counts on its Play, not the stacked
                               AttachTool); used = chosen. For a Supporter, turns on which the deck played another
                               Supporter are not opportunities (one Supporter a turn; Fable's refinement, Sept 25).
  not countable                no count; never feeds 'untrusted'.
  Default roles come from the flag: a Trainer is 'Trainer (played)'; a Pokemon with a flagged attack is 'attacker';
  a flagged ability is 'activated ability' if the run ever offered it as UseAbility, else 'bench piece/passive
  ability'; an engine-status flag on a Pokemon is 'attacker'. ROLES below sets a deck's role for a card when the
  default is wrong, and the page says which roles were set.

Failure modes: A1's per-game fields (goldfish.rs play()), recomputed from the same traces for the deck's own turns
  (setup excluded): went first; first own turn a main attacker could attack / did attack; opponent's points before
  that; Stage 2 in play by own turn 3; dead cards where the deck closes its main phase (hand cards not offered as a
  move, a Supporter held after one was played excepted), own turns 2-4. Main attackers: the list's attackers in
  lib/brew_pages.py LISTS (A1's own harness entries), else the Pokemon with the highest printed damage, labelled.
"""
import argparse, glob, hashlib, json, math, os, re, shutil, subprocess, sys, tempfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "lib"))
from current_engine import resolve  # noqa: E402

BAR = 0.20
SMALL_SHARE = 0.25
MIN_OPPORTUNITIES = 20
FIXED_GAMES = 240   # per matchup, 1,920 per floor run (Dustin, Sept 25: "Yes. Fix.")
FLOOR_PILOT = "kp3"
DEFAULT_OPPONENTS = os.path.join(HERE, "opponents")
PRICING_PILOT = re.compile(r"k[pqd]\d+")   # the codes the engine builds as PublicPricingPlayer (players/mod.rs)
ROLES_ALL = ("attacker", "activated ability", "bench piece/passive ability", "wall", "Trainer (played)", "not countable")
# A deck's role for a flagged card when the default from its flag is wrong, or set in advance: {deck path: {name: role}}.
# The Payback lists' roles were set by the page's author before any floor game on them (section 8, Sept 25), for the
# pre-use check; a name here that is not flagged in a run has no effect.
ROLES = {
    "decks/brews/brew-06-pyukumuku-silvally-payback.txt": {
        "Silvally": "attacker", "Team Rocket's Mewtwo": "attacker",
        "Pyukumuku": "bench piece/passive ability", "Rocky Helmet": "Trainer (played)"},
    "decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt": {
        "Silvally": "attacker", "Team Rocket's Scyther": "attacker",
        "Pyukumuku": "bench piece/passive ability", "Rocky Helmet": "Trainer (played)"},
}


def band(n):
    return 1.96 * math.sqrt(BAR * (1 - BAR) / n)


def verdict_of(wins, n, counts):
    """counts: {card name: (opportunities, used, role)} for the flagged cards."""
    p, b = wins / n, band(n)
    if p > BAR + b:
        return "clears the floor"
    if p >= BAR - b:
        return "borderline"
    for opp, used, role in counts.values():
        if role != "not countable" and opp >= MIN_OPPORTUNITIES and used / opp < SMALL_SHARE:
            return "untrusted"
    return "fail"


def win_edges(n):
    """(most wins that still fail, fewest wins that clear) at n games, from verdict_of itself; -1 / n + 1 when no
    win count fails / clears (a development run of 15 games or fewer, where the band is 20 points or wider)."""
    return (max((w for w in range(n + 1) if verdict_of(w, n, {}) == "fail"), default=-1),
            min((w for w in range(n + 1) if verdict_of(w, n, {}) == "clears the floor"), default=n + 1))


def self_check():
    for n, lo, hi in ((480, 78, 114), (1920, 349, 419)):
        assert verdict_of(lo, n, {}) == "fail" and verdict_of(lo + 1, n, {}) == "borderline", n
        assert verdict_of(hi - 1, n, {}) == "borderline" and verdict_of(hi, n, {}) == "clears the floor", n
        assert win_edges(n) == (lo, hi), n
    assert win_edges(8) == (-1, 4) and win_edges(16) == (0, 7)   # tiny development runs: no crash
    assert verdict_of(10, 1920, {"X": (40, 4, "attacker")}) == "untrusted"
    assert verdict_of(10, 1920, {"X": (40, 10, "attacker")}) == "fail"         # exactly 25% is not a small share
    assert verdict_of(10, 1920, {"X": (19, 0, "attacker")}) == "fail"          # too few opportunities to judge
    assert verdict_of(10, 1920, {"X": (40, 0, "not countable")}) == "fail"     # not countable never feeds it
    assert verdict_of(400, 1920, {"X": (40, 0, "attacker")}) == "borderline"   # borderline never becomes untrusted
    # a Supporter's opportunities leave out turns on which the deck played another Supporter
    sup = dict(kind="Trainer", supporter=True, ids={"S1"}, flag_attacks=set())
    off, cho = {"play": {1, 2, 3, 4}}, {"play": {2}}
    assert role_sets("Trainer (played)", sup, off, cho, set(), {1: "OTHER", 2: "S1", 4: "OTHER"}) == ({2, 3}, {2})
    item = dict(sup, supporter=False)
    assert role_sets("Trainer (played)", item, off, cho, set(), {1: "OTHER"}) == ({1, 2, 3, 4}, {2})
    print("self-check passed: edges 349/350/418/419 (n 1,920) and 78/79/113/114 (n 480); untrusted rule; Supporter turns")


# --- cards and actions as the engine serialises them -----------------------------------------------------------------

def card_fields(card):
    """{'Pokemon': {...}} / {'Trainer': {...}} / a bare trainer card -> its fields."""
    if isinstance(card, dict) and len(card) == 1 and next(iter(card)) in ("Pokemon", "Trainer"):
        return next(iter(card.values()))
    return card if isinstance(card, dict) else {}


def active_id(state, seat):
    slot = state["in_play_pokemon"][seat][0]
    return card_fields(slot["card"]).get("id") if slot else None


def active_name(state, seat):
    slot = state["in_play_pokemon"][seat][0]
    return card_fields(slot["card"]).get("name") if slot else None


def body(action):
    a = action["action"]
    return (a, None) if isinstance(a, str) else next(iter(a.items()))


def tags(action, state, seat, card):
    """How this move of the deck touches `card`: attack_any / attack_flag (its attack, with it Active), ability
    (UseAbility on it), entry (Place or Evolve into it), play (it played from hand), retreat (a retreat with it Active)."""
    kind, v = body(action)
    ids = card["ids"]
    out = set()
    if kind == "Attack" and active_id(state, seat) in ids:
        out.add("attack_any")
        if v.get("title") in card["flag_attacks"]:
            out.add("attack_flag")
    elif kind == "UseAbility":
        slot = state["in_play_pokemon"][seat][v["in_play_idx"]]
        if slot and card_fields(slot["card"]).get("id") in ids:
            out.add("ability")
    elif kind == "Play":
        if card_fields(v["trainer_card"]).get("id") in ids:
            out.add("play")
    elif kind in ("Place", "Evolve"):
        if card_fields(v[0] if kind == "Place" else v["evolution"]).get("id") in ids:
            out.add("entry")
    elif kind == "Retreat":
        if active_id(state, seat) in ids:
            out.add("retreat")
    return out


def hand_card_of(action):
    kind, v = body(action)
    if kind == "Play":
        return card_fields(v["trainer_card"]).get("id")
    if kind == "Place":
        return card_fields(v[0]).get("id")
    if kind == "Evolve":
        return card_fields(v["evolution"]).get("id")
    if kind == "AttachTool":
        return card_fields(v["tool_card"]).get("id")
    return None


# --- the flagged list ------------------------------------------------------------------------------------------------

def audited_texts():
    src = open(os.path.join(ROOT, "engine", "src", "players", "public_pricing_player.rs"), encoding="utf-8").read()
    block = src[src.index("pub(crate) const AUDITED_TEXTS"):]
    block = block[:block.index("];")]
    texts = re.findall(r'r#"(.*?)"#', block, flags=re.S)
    assert len(texts) == 62, f"expected kp's 62 audited texts, found {len(texts)}"
    return set(texts)


def database():
    db = json.load(open(os.path.join(ROOT, "lib", "deckgym-database.json"), encoding="utf-8"))
    return {v["id"]: (k, v) for e in db for k, v in e.items()}


def flagged_cards(coverage, pilot, db):
    """{card name: card facts and the reasons it is flagged}, for the cards the floor counts. Coverage is per id;
    flagged printings of one card are merged under its name (ids = the flagged printings)."""
    audited = audited_texts() if PRICING_PILOT.fullmatch(pilot.lower()) else set()
    out = {}
    for cid, c in sorted(coverage.items()):
        kind, card = db[cid]
        reasons, flag_attacks, ability_flag, status = [], set(), False, False
        if not c["engine_complete"] or c["limitations"]:
            status = True
            reasons.append(f"engine: {c['engine_status']}" + (f"; {', '.join(c['limitations'])}" if c["limitations"] else ""))
        texts = {}
        if kind == "Pokemon":
            if card.get("ability"):
                texts[f"ability {card['ability']['title']}"] = card["ability"]["effect"]
            for a in card.get("attacks", []):
                if a.get("effect"):
                    texts[f"attack {a['title']}"] = a["effect"]
        else:
            texts["its effect"] = card.get("effect") or ""
        for label in c["unpriced_text_rule"]:
            if texts.get(label, "").lower() in audited:
                continue                        # kp prices this text
            reasons.append(f"{label}: text the pilot leaves unpriced (opponent's hand or deck)")
            flag_attacks |= {label[7:]} if label.startswith("attack ") else set()
            ability_flag |= label.startswith("ability ")
        for e in c["estimator_printed_damage"]:
            reasons.append(f"{e} (k's damage estimate)")
            flag_attacks.add(e.split(":")[0])
        for label in c["pays_off_on_opponent_turn"]:
            reasons.append(f"{label}: pays off during the opponent's turn, which the search doesn't play out")
            flag_attacks |= {label[7:]} if label.startswith("attack ") else set()
            ability_flag |= label.startswith("ability ")
        if reasons:
            e = out.setdefault(c["name"], dict(name=c["name"], ids=set(), kind=kind, reasons=[], flag_attacks=set(),
                                               ability_flag=False, status=False, has_attacks=False, supporter=False))
            e["ids"].add(cid)
            e["reasons"] += [r for r in reasons if r not in e["reasons"]]
            e["flag_attacks"] |= flag_attacks
            e["ability_flag"] |= ability_flag
            e["status"] |= status
            e["has_attacks"] |= bool(card.get("attacks")) if kind == "Pokemon" else False
            e["supporter"] |= kind == "Trainer" and card.get("trainer_card_type") == "Supporter"
    return out


def default_role(card, ability_offered):
    if card["kind"] != "Pokemon":
        return "Trainer (played)"
    if card["flag_attacks"]:
        return "attacker"
    if card["ability_flag"]:
        return "activated ability" if ability_offered else "bench piece/passive ability"
    return "attacker" if card["has_attacks"] else "bench piece/passive ability"


def main_attackers(deck_path, db):
    import brew_pages
    rel = os.path.relpath(os.path.abspath(deck_path), ROOT).replace(os.sep, "/")
    for e in brew_pages.LISTS:
        if e["path"] == rel:
            return list(e["attackers"]), "the list's attackers in lib/brew_pages.py LISTS (A1's harness entry)"
    best, dmg = None, -1
    for line in open(deck_path, encoding="utf-8-sig"):
        p = line.split()
        if len(p) >= 3 and p[0].isdigit():
            kind, card = db.get(f"{p[-2]} {p[-1]}", (None, None))
            if kind == "Pokemon":
                d = max((a.get("fixed_damage") or 0 for a in card.get("attacks", [])), default=0)
                if d > dmg:
                    best, dmg = card["name"], d
    return [best], "fallback: the Pokemon with the highest printed damage (no A1 entry for this list)"


# --- games -----------------------------------------------------------------------------------------------------------

def run_call(engine, p0, p1, players, n, seed, seat, handle):
    """One deckgym call. Checks every game completed and that the printed wins match the result files, then hands
    each game (its result and its traces, one game at a time to bound memory) to `handle`, and deletes the traces."""
    tmp = tempfile.mkdtemp(prefix="floor_", dir="/tmp" if os.path.isdir("/tmp") else None)
    try:
        out = subprocess.run([engine, "simulate", "--num", str(n), "--players", players, "--seed", str(seed),
                              "--seed-stream", "--data-output", os.path.join(tmp, "data"),
                              "--results-output", os.path.join(tmp, "res"), "-p", p0, p1],
                             capture_output=True, text=True)
        text = out.stdout + out.stderr
        if "Player 0 won" not in text:
            raise SystemExit(f"engine refused {p0} vs {p1}:\n{text[-400:]}")
        printed = tuple(int(re.search(pat, text)[1]) for pat in (r"Player 0 won: (\d+)", r"Player 1 won: (\d+)", r"Draws: (\d+)"))
        results = [json.load(open(rf, encoding="utf-8")) for rf in sorted(glob.glob(os.path.join(tmp, "res", "*.json")))]
        if len(results) != n or any(r.get("completion") != "completed" for r in results):
            raise SystemExit(f"{p0} vs {p1} seed {seed}: {len(results)} of {n} games completed; no verdict")
        wins = sum(1 for r in results if r["outcome"] == {"Win": seat})
        if (printed[0] if seat == 0 else printed[1]) != wins:
            raise SystemExit(f"{p0} vs {p1} seed {seed}: printed wins {printed} disagree with the result files")
        for r in sorted(results, key=lambda r: r["randomness"]["game_seed"]):
            files = sorted(glob.glob(os.path.join(tmp, "data", r["game_id"], "ply_*.json")))
            if len(files) != r["plies"]:
                raise SystemExit(f"game {r['game_id']}: {len(files)} trace files for {r['plies']} plies; no verdict")
            handle(r, [json.load(open(f, encoding="utf-8")) for f in files])
        return printed
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def game_record(result, plies, seat, flagged, attackers):
    """A1's fields and, per flagged card, the turns each tag was offered / chosen and the wall turns kept; and the
    Supporter the deck played on each turn."""
    rec = dict(seed=result["randomness"]["game_seed"], seat=seat, won=result["outcome"] == {"Win": seat},
               draw=result["outcome"] not in ({"Win": 0}, {"Win": 1}), points=result["final_points"],
               turns=result["final_turn"], went_first=None, could=None, did=None, conceded=None, stage2=False,
               dead={})
    offered = {name: defaultdict(set) for name in flagged}   # card name -> tag -> turns
    chosen = {name: defaultdict(set) for name in flagged}
    supporter_of = {}                                         # turn -> id of the Supporter the deck played
    last_active = {}                                          # turn -> the deck's Active at its last decision
    turn_seen, own_turn, supporter_played, closed = 0, 0, False, False
    for p in plies:
        st, actor = p["state"], p["actor"]
        if st["turn_count"] != turn_seen and st["turn_count"] >= 1:
            turn_seen, supporter_played, closed = st["turn_count"], False, False
            if st["current_player"] == seat:
                own_turn += 1
            if st["turn_count"] == 1:
                rec["went_first"] = st["current_player"] == seat
        if actor != seat:
            continue
        t = st["turn_count"]
        for name, card in flagged.items():
            for a in p["playable_actions"]:
                for tag in tags(a, st, seat, card):
                    offered[name][tag].add(t)
            for tag in tags(p["chosen_action"], st, seat, card):
                chosen[name][tag].add(t)
        kind, v = body(p["chosen_action"])
        if kind == "Play" and card_fields(v["trainer_card"]).get("trainer_card_type") == "Supporter":
            supporter_of[t] = card_fields(v["trainer_card"]).get("id")
        # the deck's Active after this decision: a retreat moves it off (the next state shows the new Active)
        last_active[t] = None if kind == "Retreat" else active_id(st, seat)
        if own_turn == 0:
            continue
        is_main = active_name(st, seat) in attackers
        if is_main and rec["could"] is None and any(body(a)[0] == "Attack" for a in p["playable_actions"]):
            rec["could"] = own_turn
        if own_turn <= 3 and any(s and card_fields(s["card"]).get("stage") == 2 for s in st["in_play_pokemon"][seat]):
            rec["stage2"] = True
        if kind in ("Attack", "EndTurn") and not closed:
            closed = True
            can = {hand_card_of(a) for a in p["playable_actions"]}
            dead = sum(1 for c in st["hands"][seat] if card_fields(c).get("id") not in can and not (
                supporter_played and card_fields(c).get("trainer_card_type") == "Supporter"))
            rec["dead"][own_turn] = dead
        if kind == "Play" and card_fields(v["trainer_card"]).get("trainer_card_type") == "Supporter":
            supporter_played = True
        if kind == "Attack" and rec["did"] is None and is_main:
            rec["did"], rec["conceded"] = own_turn, st["points"][1 - seat]
    if rec["did"] is None:
        rec["conceded"] = result["final_points"][1 - seat]
    kept = {name: {t for t in offered[name]["retreat"] if last_active.get(t) in card["ids"]}
            for name, card in flagged.items()}
    return rec, offered, chosen, kept, supporter_of


def role_sets(role, card, off, cho, kept, supporter_of):
    """(opportunity turns, used turns) for one game under the card's role."""
    if role == "attacker":
        tag = "attack_flag" if card["flag_attacks"] else "attack_any"
        return off[tag], cho[tag]
    if role == "activated ability":
        return off["ability"], cho["ability"]
    if role == "bench piece/passive ability":
        return off["entry"], cho["entry"]
    if role == "wall":
        return off["retreat"], kept
    if role == "Trainer (played)":
        if card.get("supporter"):
            return {t for t in off["play"] if supporter_of.get(t) in (None, *card["ids"])}, cho["play"]
        return off["play"], cho["play"]
    return set(), set()


# --- the page --------------------------------------------------------------------------------------------------------

def failure_rows(recs):
    rows = []
    for first in (True, False):
        g = [r for r in recs if r["went_first"] is first]
        n = max(len(g), 1)
        by = lambda k, t: sum(1 for r in g if r[k] is not None and r[k] <= t) / n  # noqa: E731
        dead = [d for r in g for t, d in r["dead"].items() if 2 <= t <= 4]
        rows.append((("went first" if first else "went second"), len(g),
                     *(by("could", t) for t in (2, 3, 4)), *(by("did", t) for t in (2, 3, 4)),
                     sum(r["conceded"] for r in g) / n, sum(1 for r in g if r["did"] is None) / n,
                     sum(1 for r in g if r["stage2"]) / n, (sum(dead) / len(dead)) if dead else float("nan"),
                     sum(1 for r in g if r["won"]) / n))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--games", type=int, default=FIXED_GAMES, help="games per matchup (fixed at 240 for a verdict)")
    ap.add_argument("--pilot", default="kp3")
    ap.add_argument("--meta-pilot", default="kp3")
    ap.add_argument("--seed", type=int, default=7100)
    ap.add_argument("--goldfish", help="A1's goldfish program for the coverage (default: the official release's, "
                    "project_manifest.json available_release; any other makes the run a control reading)")
    ap.add_argument("--opponents", default=DEFAULT_OPPONENTS)
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args()
    self_check()
    if a.self_check:
        return
    if not a.deck or not a.out:
        raise SystemExit("usage: floor.py DECK.txt --out DIR (or --self-check)")
    if a.games < 2:
        raise SystemExit("--games must be at least 2 (half the games are played in each seat)")
    try:
        engine = str(resolve(project=ROOT))
    except (OSError, ValueError) as e:
        raise SystemExit(f"REFUSED: {e}")
    release = json.load(open(os.path.join(ROOT, "project_manifest.json"), encoding="utf-8"))["available_release"]
    official_goldfish = os.path.join(ROOT, release["goldfish"])
    a.deck, a.out, a.opponents = os.path.abspath(a.deck), os.path.abspath(a.out), os.path.abspath(a.opponents)
    a.goldfish = os.path.abspath(a.goldfish or official_goldfish)
    if not os.path.isfile(a.goldfish):
        raise SystemExit(f"no goldfish program at {a.goldfish}")
    goldfish_sha = hashlib.sha256(open(a.goldfish, "rb").read()).hexdigest()
    opps = sorted(glob.glob(os.path.join(a.opponents, "*.txt")))
    if not opps:
        raise SystemExit(f"no opponent lists (*.txt) in {a.opponents}")
    # what makes this run something other than the floor verdict (see the docstring)
    not_floor = []
    if a.pilot != FLOOR_PILOT or a.meta_pilot != FLOOR_PILOT:
        not_floor.append(f"pilots {a.pilot} on the deck and {a.meta_pilot} on the panel, not {FLOOR_PILOT} on both")
    if os.path.realpath(a.opponents) != os.path.realpath(DEFAULT_OPPONENTS):
        not_floor.append(f"opponents from {a.opponents}, not decks/screen/opponents")
    if goldfish_sha != release["goldfish_sha256"]:
        not_floor.append(f"coverage from a goldfish ({goldfish_sha[:12]}…) other than the official release's")
    os.makedirs(a.out, exist_ok=True)
    name = os.path.splitext(os.path.basename(a.deck))[0]
    rel = os.path.relpath(a.deck, ROOT).replace(os.sep, "/")
    db = database()
    names_in_list = {db[f"{p[-2]} {p[-1]}"][1]["name"] for p in (line.split() for line in open(a.deck, encoding="utf-8-sig"))
                     if len(p) >= 3 and p[0].isdigit() and f"{p[-2]} {p[-1]}" in db}
    unknown = sorted(set(ROLES.get(rel, {})) - names_in_list)
    if unknown:
        raise SystemExit(f"ROLES names cards that are not in {rel}: {unknown}")
    cov_path = os.path.join(a.out, f"{name}_coverage.json")
    subprocess.run([a.goldfish, "--deck", a.deck, "--panel", a.opponents, "--games", "0",
                    "--coverage", cov_path], check=True, capture_output=True, cwd=os.path.join(ROOT, "engine"))
    coverage = json.load(open(cov_path, encoding="utf-8"))
    flagged = flagged_cards(coverage, a.pilot, db)
    attackers, attackers_src = main_attackers(a.deck, db)
    attackers = set(attackers)
    recs, per_opp, printed_lines, per_game = [], [], [], []
    for i, o in enumerate(opps):
        oname = os.path.splitext(os.path.basename(o))[0]
        h, s = a.games // 2, a.seed + 1000 * i
        before = len(recs)
        for seat, (p0, p1, players, n, seed) in enumerate(((a.deck, o, f"{a.pilot},{a.meta_pilot}", h, s),
                                                           (o, a.deck, f"{a.meta_pilot},{a.pilot}", a.games - h, s + 500))):
            def handle(result, plies, seat=seat, oname=oname):
                rec, off, cho, kept, sup = game_record(result, plies, seat, flagged, attackers)
                rec["opponent"] = oname
                recs.append(rec)
                per_game.append((result["game_id"], off, cho, kept, sup))
            printed_lines.append((oname, seat, run_call(engine, p0, p1, players, n, seed, seat, handle)))
        per_opp.append((oname, sum(r["won"] for r in recs[before:]), a.games))
    n = len(recs)
    wins = sum(r["won"] for r in recs)
    counts, role_src = {}, {}
    for cname, card in flagged.items():
        ability_offered = any(off[cname]["ability"] for _, off, _, _, _ in per_game)
        role = ROLES.get(rel, {}).get(cname)
        role_src[cname] = "set for this deck" if role else "default from the flag"
        role = role or default_role(card, ability_offered)
        assert role in ROLES_ALL, role
        opp_t, used_t = set(), set()
        for gid, off, cho, kept, sup in per_game:
            o_, u_ = role_sets(role, card, off[cname], cho[cname], kept[cname], sup)
            opp_t |= {(gid, t) for t in o_}
            used_t |= {(gid, t) for t in u_ if t in o_}
        counts[cname] = (len(opp_t), len(used_t), role)
    verdict = verdict_of(wins, n, counts)
    if a.games != FIXED_GAMES:
        verdict = f"no verdict (development run: {a.games} games per matchup; the floor is fixed at {FIXED_GAMES})"
    elif not_floor:
        verdict = f"control reading, not a floor verdict ({'; '.join(not_floor)}): {verdict}"
    b = band(n)
    lo, hi = win_edges(n)
    L = [f"# Floor check: {name}", "",
         f"**Verdict: {verdict}.** {wins} wins in {n} games ({100 * wins / n:.2f}%) against the {len(opps)} lists in "
         f"{os.path.relpath(a.opponents, ROOT)}. Bar 20% with the screen's own noise ±{100 * b:.2f} points at this n: "
         + (f"{lo} wins or fewer fail, " if lo >= 0 else "no win count fails at this n, ")
         + f"{lo + 1}-{hi - 1} are borderline, "
         + (f"{hi} or more clear the floor." if hi <= n else "no win count clears at this n."),
         "Flagged cards (the bot is known not to price them fully): " + ("; ".join(
             f"{k} as {role}: used on {us} of {op} opportunities" + (f" ({100 * us / op:.1f}%)" if op else "")
             for k, (op, us, role) in sorted(counts.items())) or "none")
         + ". A share under 25% of at least 20 opportunities is a flag for a person to look at.",
         "Not a ranking: no average across decks is used for anything else.", "",
         f"- Engine: {os.path.relpath(engine, ROOT)} (the manifest's available release). Pilots: {a.pilot} on the deck, "
         f"{a.meta_pilot} on the panel. {a.games} games per matchup, seeds {a.seed} + 1,000 x opponent (seat 0) and "
         f"+500 (seat 1), --seed-stream.", "",
         "## Worst matchups (each line ±{:.0f} points at {} games)".format(100 * 1.96 * math.sqrt(0.25 / a.games), a.games), ""]
    for oname, w, g in sorted(per_opp, key=lambda x: x[1]):
        L.append(f"- {oname}: {w}/{g} = {100 * w / g:.0f}%")
    L += ["", "## Coverage flag: cards the bot may not play as a strong player would", "",
          "| card | role (source) | why flagged | opportunities | used | share |", "|---|---|---|---|---|---|"]
    for cname, card in sorted(flagged.items()):
        op, us, role = counts[cname]
        share = f"{100 * us / op:.1f}%" if op else "—"
        mark = "" if role == "not countable" else (" — under 25%" if op >= MIN_OPPORTUNITIES and us / op < SMALL_SHARE
                                                   else (" — too few opportunities to judge" if op < MIN_OPPORTUNITIES else ""))
        prints = f" ({', '.join(sorted(card['ids']))})"
        sup = "; a Supporter: turns with another Supporter played left out" if card["supporter"] and role == "Trainer (played)" else ""
        L.append(f"| {cname}{prints} | {role} ({role_src[cname]}{sup}) | {'; '.join(card['reasons'])} | {op} | {us} | {share}{mark} |")
    if not flagged:
        L.append("| (none) | | | | | |")
    L += ["", "Roles: attacker = its attack chosen on turns it could attack with it Active; activated ability = used on "
          "turns it was offered; bench piece/passive ability = put into play on turns it could be; wall = still the "
          "Active at the end of turns a retreat was offered; Trainer (played) = played on turns it could be. A wrong "
          "role is set per deck in floor.py's ROLES.",
          "", "## Failure modes (A1's measures, from these games; the deck's own turns, setup excluded)", "",
          "| | games | could attack with a main attacker by turn 2 / 3 / 4 | did by turn 2 / 3 / 4 | opponent's points "
          "before the first main attack | never attacked with a main attacker | Stage 2 by turn 3 | dead cards per turn "
          "(turns 2-4) | won |", "|---|---|---|---|---|---|---|---|---|"]
    for row in failure_rows(recs):
        lab, g, c2, c3, c4, d2, d3, d4, conc, never, st2, dead, won = row
        pc = lambda x: f"{100 * x:.0f}%"  # noqa: E731
        L.append(f"| {lab} | {g} | {pc(c2)} / {pc(c3)} / {pc(c4)} | {pc(d2)} / {pc(d3)} / {pc(d4)} | {conc:.2f} | "
                 f"{pc(never)} | {pc(st2)} | {dead:.2f} | {pc(won)} |")
    L += ["", f"Main attackers for these measures ({attackers_src}): {', '.join(sorted(attackers))}. "
          f"Draws: {sum(r['draw'] for r in recs)}.",
          "", "## For a second reader", "",
          f"- Coverage from {os.path.relpath(a.goldfish, ROOT) if a.goldfish.startswith(ROOT) else a.goldfish} "
          f"(sha256 {goldfish_sha}; {'the official release' if goldfish_sha == release['goldfish_sha256'] else 'NOT the official release'}; "
          f"`--games 0 --coverage`): `{name}_coverage.json`. Per-game records: `{name}_games.jsonl`.",
          "- The engine's own printed lines per call (player 0 won / player 1 won / draws); a plain run_screen.py run "
          "with the same pilots, seeds and games must print the same:"]
    for oname, seat, (p0w, p1w, dr) in printed_lines:
        L.append(f"  - {oname}, deck in seat {seat}: {p0w} / {p1w} / {dr}")
    open(os.path.join(a.out, f"{name}.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    with open(os.path.join(a.out, f"{name}_games.jsonl"), "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print("\n".join(L[:4]))
    print(f"Written: {os.path.join(a.out, name + '.md')}")


if __name__ == "__main__":
    main()

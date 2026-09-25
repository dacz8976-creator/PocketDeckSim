#!/usr/bin/env python3
"""One plain page per brew list: what the cards allow, what the bot does with them, and where the bot is blind.

    python3 lib/brew_pages.py OUT_DIR [--games 50] [--trials 20000] [--only brew-01]

For each list in LISTS it runs the card-draw model (lib/brew_consistency.py, 20,000 shuffles) and the
engine goldfish (engine/examples/goldfish.rs: k3 pilots the list against each deck in decks/research, once
with the opponent bot 'et', which only ends its turn, and once with 'aa', which attaches and attacks), then
writes OUT_DIR/<list>.md and an index comparing the pages with the Ladder Log records. Build the goldfish
first: cd engine && cargo build --release --example goldfish.

Goldfish seeds: 22,200,000,000 + opponent x 10,000 + i (opponents in file order), the same deals for 'et'
and 'aa' and for every list.
"""
import argparse, io, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import brew_consistency  # noqa: E402

GOLDFISH = os.path.join(ROOT, "engine", "target", "release", "examples", "goldfish")
SEED = 22_200_000_000

# The calibration anchors: Dustin's lists with Ladder Log games (ladder_log_games.csv on main, Sept 15-24).
# attackers = the main attackers; combo = the pieces the list needs in play together.
LISTS = [
    dict(path="decks/dustin/07-skarmory-stall.txt", label="Deck 07: Skarmory stall", attackers=["Skarmory ex"],
         combo=[], ladder="3-1", notes=[]),
    dict(path="decks/brews/brew-05b-meowstic-hatterene-comfey.txt", label="Brew 05b: Meowstic / Hatterene / Comfey",
         attackers=["Hatterene"], combo=["Meowstic", "Hatterene"], ladder="3-3 (Sept 15 list)",
         notes=["Comfey the only Basic to start off, not ideal.",
                "2 cards left to draw and I don't have the second Meowstic or Hatterene.",
                "Good setup this time, Meowstic and Hatterene evolved on turn two."]),
    dict(path="decks/brews/brew-01-arceus-crobat-xatu.txt", label="Brew 01: Arceus / Crobat / Xatu",
         attackers=["Xatu", "Arceus ex"], combo=["Arceus ex", "Crobat", "Xatu"], ladder="1-3",
         notes=["Never drew Crobat, or Xatu... Probably need more draw cards or Copycat.",
                "Arceus ex takes 3 energy... Once again deck seems too difficult to draw cards you need."]),
    dict(path="decks/brews/brew-03a-arceus-nihilego-toxapex.txt", label="Brew 03a: Arceus / Nihilego / Toxapex",
         attackers=["Toxapex", "Arceus ex"], combo=["Nihilego", "Toxapex"], ladder="1-3", notes=[]),
    dict(path="decks/brews/brew-06-pyukumuku-silvally-payback.txt", label="Brew 06: Pyukumuku / Silvally / TR Mewtwo (Payback)",
         attackers=["Silvally", "Team Rocket's Mewtwo"], combo=["Pyukumuku", "Silvally"], ladder="0-3",
         notes=["Opened with only TR Mewtwo.",
                "Hitmonchan ex and Great Tusk took both Pyukumukus for 2 points before Silvally had 3 energy.",
                "Never drew Rocky Helmet."]),
    dict(path="decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt", label="Brew 06b: Pyukumuku / Silvally / TR Scyther (Grass)",
         attackers=["Silvally", "Team Rocket's Scyther"], combo=["Pyukumuku", "Silvally"], ladder="0-3", notes=[]),
]


def pct(x):
    return "n/a" if x is None else f"{100 * x:.0f}%"


def goldfish(path, attackers, opp_bot, games, out_dir, stem):
    games_out = os.path.join(out_dir, "raw", f"{stem}_{opp_bot}.jsonl")
    cov = os.path.join(out_dir, "raw", f"{stem}_coverage.json")
    cmd = [GOLDFISH, "--deck", os.path.join(ROOT, path), "--panel", os.path.join(ROOT, "decks", "research"),
           "--bot", "k3", "--opp-bot", opp_bot, "--games", str(games), "--seed", str(SEED),
           "--attackers", ",".join(attackers), "--games-out", games_out, "--coverage", cov]
    summary = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=os.path.join(ROOT, "engine")).stdout
    with open(os.path.join(out_dir, "raw", f"{stem}_{opp_bot}.txt"), "w") as f:
        f.write(" ".join(cmd[1:]) + "\n" + summary)
    recs = [json.loads(line) for line in open(games_out) if line.strip()]
    return recs, json.load(open(cov))


def bot_numbers(recs):
    ok = [r for r in recs if r["crashed"] is None]
    out = {"games": len(recs), "crashed": len(recs) - len(ok),
           "crash_reasons": sorted({r["crashed"] for r in recs if r["crashed"]})}
    for first in (True, False):
        g = [r for r in ok if r["went_first"] == first]
        n = max(len(g), 1)
        by = lambda key, t: sum(1 for r in g if r[key] is not None and r[key] <= t) / n
        dead = [d for r in g for d in r["dead_at_end_of_turn"][1:4] if d is not None]
        out["first" if first else "second"] = {
            "games": len(g),
            "could": {t: by("first_main_attack_offered_turn", t) for t in (2, 3, 4)},
            "did": {t: by("first_main_attack_turn", t) for t in (2, 3, 4)},
            "conceded": sum(r["points_conceded_before_main_attack"] for r in g) / n,
            "conceded_any": sum(1 for r in g if r["points_conceded_before_main_attack"] > 0) / n,
            "never_main": sum(1 for r in g if r["first_main_attack_turn"] is None) / n,
            "stage2": sum(1 for r in g if r["stage2_by_turn3"]) / n,
            "dead": sum(dead) / max(len(dead), 1),
            "won": sum(1 for r in g if r["list_won"]) / n,
        }
    return out


def flags(coverage):
    out = []
    for cid, c in sorted(coverage.items(), key=lambda kv: kv[1]["name"]):
        why = []
        if not c["engine_complete"]:
            why.append(f"engine: {c['engine_status']}")
        why += [f"engine limitation: {x}" for x in c["limitations"]]
        why += [f"{x} mentions the opponent's hand or deck: k3 scores it as doing nothing" for x in c["unpriced_text_rule"]]
        why += [f"{x}: k3's damage estimate uses the printed damage" for x in c["estimator_printed_damage"]]
        why += [f"{x} pays off during the opponent's turn, which k3 doesn't search (its clock counts HP and the "
                f"opponent's best damage, not effects like this)" for x in c["pays_off_on_opponent_turn"]]
        if why:
            out.append((c["name"], cid, why))
    return out


def page(cfg, model, et, aa, cov, engine_commit, games):
    L = []
    L.append(f"# {cfg['label']}\n")
    L.append(f"List: `{cfg['path']}`. Main attackers: {', '.join(cfg['attackers'])}."
             + (f" Combo: {', '.join(cfg['combo'])} in play by your turn {model['combo_turn']}." if cfg["combo"] else ""))
    L.append(f"Ladder Log: {cfg['ladder']}." + "".join(f"\n- \"{n}\"" for n in cfg["notes"]))
    L.append("")
    if model["structure"]:
        L.append("**List check:** " + " ".join(model["structure"]) + "\n")
    L.append(f"## What the cards allow ({model['trials']:,} shuffles, no opponent)\n")
    L.append("The card-draw model plays solitaire: draws, plays its draw and search cards, puts Basics down, "
             "evolves, and gives each turn's energy to the Pokémon closest to attacking. It shows what the list "
             "can do, not what a player or bot will do.\n")
    L.append("| | going first | going second |\n|---|---|---|")
    f, s = model["first"], model["second"]
    L.append(f"| Opening hand with one Basic | {pct(f['one_basic_opening'])} | {pct(s['one_basic_opening'])} |")
    for t in (2, 3, 4):
        L.append(f"| A main attacker could attack by your turn {t} | {pct(f['attacker_ready'].get(str(t), f['attacker_ready'].get(t)))} "
                 f"| {pct(s['attacker_ready'].get(str(t), s['attacker_ready'].get(t)))} |")
    L.append(f"| Stage 2 in play by your turn 3 | {pct(f['stage2_by_turn3'])} | {pct(s['stage2_by_turn3'])} |")
    if cfg["combo"]:
        L.append(f"| Combo in play by your turn {model['combo_turn']} | {pct(f['combo_by_turn'])} | {pct(s['combo_by_turn'])} |")
    stuck = lambda d: ", ".join(f"{d.get(str(k), d.get(k, 0)):.1f}" for k in (1, 2, 3, 4))
    L.append(f"| Stuck cards in hand, end of turns 1-4 | {stuck(f['stuck_per_turn'])} | {stuck(s['stuck_per_turn'])} |")
    lone = f["lone_starter"]
    if lone:
        L.append("\nWhen the opening hand has one Basic, it is: " + ", ".join(
            f"{n} ({pct(v)} of all games)" for n, v in lone.items()) + ".")
    L.append("\n**Chance each card has been in your hand by the end of your turn 1 / 2 / 3 / 4** (going second; "
             "going first is the same card count, a turn earlier in the game). \"With search\" plays the list's "
             "draw and search cards; \"draws only\" is the exact odds from drawing alone, ignoring the rule that "
             "the opening hand always has a Basic.\n")
    L.append("| card | with search | draws only |\n|---|---|---|")
    for n in sorted(s["seen_by_turn"], key=lambda n: (n not in cfg["attackers"] + cfg["combo"], n)):
        w = " / ".join(pct(s["seen_by_turn"][n][str(k)] if str(k) in s["seen_by_turn"][n] else s["seen_by_turn"][n][k]) for k in (1, 2, 3, 4))
        d = " / ".join(pct(s["seen_by_turn_draws_only"][n][str(k)] if str(k) in s["seen_by_turn_draws_only"][n] else s["seen_by_turn_draws_only"][n][k]) for k in (1, 2, 3, 4))
        L.append(f"| {n} | {w} | {d} |")
    L.append(f"\n## What the bot does with it (k3 piloting, {et['games']} games against each opponent bot)\n")
    L.append(f"k3 plays the list against the 8 table decks, {games} deals each, once against a bot that only ends "
             "its turn ('et': pure goldfish) and once against one that attaches and attacks ('aa': points given up "
             "before the list's first real attack). \"Could\" means a main attacker was in the Active Spot with an "
             "attack available; \"did\" means k3 used it.\n")
    fl = flags(cov)
    if fl:
        L.append("**Bot numbers untrusted for this list**: some of its cards hit a path k3 prices badly (see the last section).\n")
    L.append("| | vs et, first | vs et, second | vs aa, first | vs aa, second |\n|---|---|---|---|---|")
    rows = [et["first"], et["second"], aa["first"], aa["second"]]
    L.append("| games | " + " | ".join(str(r["games"]) for r in rows) + " |")
    for t in (2, 3, 4):
        L.append(f"| main attacker could / did attack by turn {t} | " + " | ".join(
            f"{pct(r['could'][t])} / {pct(r['did'][t])}" for r in rows) + " |")
    L.append("| never attacked with a main attacker | " + " | ".join(pct(r["never_main"]) for r in rows) + " |")
    L.append("| points given up before the first main attack (average; share of games with any) | "
             + " | ".join(f"{r['conceded']:.2f}; {pct(r['conceded_any'])}" for r in rows) + " |")
    L.append("| Stage 2 in play by turn 3 | " + " | ".join(pct(r["stage2"]) for r in rows) + " |")
    L.append("| dead cards at the end of turns 2-4 (average) | " + " | ".join(f"{r['dead']:.1f}" for r in rows) + " |")
    L.append("| won (a sanity check, not a strength rating) | " + " | ".join(pct(r["won"]) for r in rows) + " |")
    crashes = et["crashed"] + aa["crashed"]
    L.append(f"\nGames that crashed (a card the engine can't play): {crashes}"
             + (": " + "; ".join(et["crash_reasons"] + aa["crash_reasons"]) if crashes else "") + ".")
    L.append("Dead cards: cards in hand that no offered move could use when the list attacked or ended its turn "
             "(a Supporter held because one was already played that turn doesn't count).\n")
    L.append("## Where the bot is blind on this list\n")
    if fl:
        for name, cid, why in fl:
            L.append(f"- **{name}** ({cid}): " + "; ".join(why) + ".")
    else:
        L.append("No card in the list hits a known k3 fallback path.")
    L.append(f"\nEngine commit {engine_commit}; goldfish seeds {SEED:,} + opponent x 10,000 + i (i < {games}); "
             f"card-draw model seed {model['seed']:,}.")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir")
    ap.add_argument("--games", type=int, default=50)
    ap.add_argument("--trials", type=int, default=20000)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    a.out_dir = os.path.abspath(a.out_dir)
    os.makedirs(os.path.join(a.out_dir, "raw"), exist_ok=True)
    engine_commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                                   text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "engine/src", "engine/examples/goldfish.rs"], cwd=ROOT,
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        engine_commit += " (with uncommitted engine changes)"
    index = []
    for cfg in LISTS:
        stem = os.path.splitext(os.path.basename(cfg["path"]))[0]
        if a.only and a.only not in stem:
            continue
        model = brew_consistency.run(os.path.join(ROOT, cfg["path"]), cfg["attackers"], tuple(cfg["combo"]),
                                     3, a.trials)
        json.dump(model, open(os.path.join(a.out_dir, "raw", f"{stem}_model.json"), "w"), indent=1)
        et_recs, cov = goldfish(cfg["path"], cfg["attackers"], "et", a.games, a.out_dir, stem)
        aa_recs, _ = goldfish(cfg["path"], cfg["attackers"], "aa", a.games, a.out_dir, stem)
        et, aa = bot_numbers(et_recs), bot_numbers(aa_recs)
        with io.open(os.path.join(a.out_dir, f"{stem}.md"), "w", encoding="utf-8") as f:
            f.write(page(cfg, model, et, aa, cov, engine_commit, a.games))
        index.append((cfg, stem, model, et, aa, bool(flags(cov))))
        print(stem, "done", flush=True)
    json.dump([{"list": stem, "ladder": cfg["ladder"],
                "one_basic": [m["first"]["one_basic_opening"], m["second"]["one_basic_opening"]],
                "ready_t3": [m["first"]["attacker_ready"][3], m["second"]["attacker_ready"][3]],
                "bot_aa": aa, "bot_et": et, "untrusted": u} for cfg, stem, m, et, aa, u in index],
              open(os.path.join(a.out_dir, "raw", "index.json"), "w"), indent=1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Writes the --pairs files for the gauntlet runs into tsv/ beside this script. Run from the repo root (WSL):
    python3 rl/results/gauntlet_runs_2026-09-26/make_tsvs.py
Deck paths are relative to the repo root, which is also the scan's --root ('..' from the build's engine/ folder):
the run scripts play the copies in /home/dacz8976/engine-b2e-7fc6ccb at the same relative paths.

(a) tsv/new_decks.tsv: 25 pairings, seed base 21,108,000,000 (seed = base + 10,000 x pairing + i, i < 500).
    p = 8 d + o, d = 0 Mega Scizor ex Revavroom (COVERAGE row), 1 Dragonair Mega Rayquaza ex, 2 Mega Altaria ex
    Greninja (SCOREBOARD rows); o in B2e's panel order (lucario, altaria, sceptile, vespiquen, suicune, hydreigon,
    weezing, blaziken), panel files decks/screen/opponents/t-<o>.txt. Pairing 24 (added after the 24 so no number
    shifts): Rayquaza (held, seat 0 on even i) v Altaria/Greninja. The new deck is the held (first-named) deck.
(b) tsv/var_<version>.tsv: one file per version (the scan takes each pairing number once, so each version is its
    own run on the SAME pairing numbers and seeds as its deck's main list).
    - Lucario, Suicune, Weezing (table decks): the table's own deals, seed base 72,000,000 and the table's pairing
      numbers (legality_scan's order: the 28 pairs (a, b), a < b, over NAMES = altaria, blaziken, hydreigon,
      lucario, sceptile, suicune, vespiquen, weezing). The table's first-named deck is the TSV's held deck, so the
      seats are the table's; the version stands in for its deck on whichever side that is. The other deck is the
      table's own file, decks/research/<name>.txt. 7 pairings each.
    - Charizard Y: B2e's pairings 40-47, seed base 21,106,000,000, the version as the held deck against
      decks/screen/opponents/t-<o>.txt, exactly B2e's rows with the held file swapped. 8 pairings each.
    Versions: v-<deck>_2 (the second list; for Charizard Y the existing l-charizardy.txt), v-<deck>_swap1, _swap2.
(identity) tsv/id_<deck>_main.tsv: the same rows with the deck's MAIN list (t-<deck>.txt for the table decks,
    h-charizardy_entei.txt with B2e's own keys for Charizard Y). Run on 2 pairings x 20 deals, they must replay the
    reference games (the table's kp3 files; B2e's b2e_kp3_arch.jsonl).
Extra columns (deck, version, variant_side) are ignored by the scan and read by the checks and the reader.
"""
import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tsv")
NAMES = ["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
TABLE_PAIRS = list(itertools.combinations(NAMES, 2))  # legality_scan.rs: (0..8).flat_map(a -> (a+1..8)), in order
PANEL = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
T = "decks/screen/opponents/t-{}.txt"
RESEARCH = "decks/research/{}.txt"
G = "decks/gauntlet_2026-09-26/{}.txt"
NEW = [("scizor", G.format("g-mega_scizor_revavroom"), "coverage"),
       ("rayquaza", G.format("g-dragonair_mega_rayquaza"), "scoreboard"),
       ("altaria_greninja", G.format("g-mega_altaria_greninja"), "scoreboard")]
BASE_NEW, BASE_TABLE, BASE_B2E = 21_108_000_000, 72_000_000, 21_106_000_000
B2E_CHARIZARD_FIRST = 40  # b2e_pairings.tsv: pairings 40-47 = charizardy_entei v PANEL
H_CHARIZARD = "rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt"
VERSIONS = {  # deck -> [(version key, file)]
    "lucario": [("v-lucario_2", G.format("v-lucario_2")), ("v-lucario_swap1", G.format("v-lucario_swap1")),
                ("v-lucario_swap2", G.format("v-lucario_swap2"))],
    "suicune": [("v-suicune_2", G.format("v-suicune_2")), ("v-suicune_swap1", G.format("v-suicune_swap1")),
                ("v-suicune_swap2", G.format("v-suicune_swap2"))],
    "weezing": [("v-weezing_2", G.format("v-weezing_2")), ("v-weezing_swap1", G.format("v-weezing_swap1")),
                ("v-weezing_swap2", G.format("v-weezing_swap2"))],
    "charizardy": [("l-charizardy", "decks/screen/panel_ladder_2026-09-26/l-charizardy.txt"),
                   ("v-charizardy_swap1", G.format("v-charizardy_swap1")),
                   ("v-charizardy_swap2", G.format("v-charizardy_swap2"))],
}
HEADER = ["pairing", "block", "held_key", "held_file", "opponent", "panel_file", "seed_first", "seed_last",
          "sub_block_end", "deck", "version", "variant_side"]
# New decks NOT played by run (a), with the reason (the task: a list with a card that is unimplemented or wrong in a
# way that changes play is not run; the rest is). Their pairing numbers and seeds stay reserved, so nothing shifts.
# tsv/new_decks_run.tsv is new_decks.tsv without them; tsv/not_run.json records why (the reader prints it).
NOT_RUN = {
    "scizor": "Mega Scizor ex B2b 047's Bullet Slugger (+50 'if this Pokémon moved from your Bench to the Active Spot "
              "this turn') is wrong in a way that changes play: after an end-of-turn or Checkup Knock Out on the "
              "opponent's turn the engine promotes the new Active only after the next turn has started, so a promoted "
              "Mega Scizor ex keeps the per-turn moved_to_active_this_turn flag and hits 150, where Pocket's ruling "
              "gives no bonus (state/mod.rs 1205, 1391-1423; apply_action_helpers.rs 963-965; apply_attack_action.rs "
              "4909-4924). Five of the eight panel decks can cause such Knock Outs. Upheld 3 to 0 by the skeptics "
              "(decks/gauntlet_2026-09-26/card_check.md). Not run on the pre-repair engine; check it again after the "
              "promotion-timing repair.",
}


def seeds(base, p, games=500):
    return base + 10_000 * p, base + 10_000 * p + games - 1, base + 10_000 * p + 9_999


def table_rows(deck, key, path, block):
    """The table deck's 7 pairings with (key, path) standing in for it on its own side."""
    rows = []
    for p, (a, b) in enumerate(TABLE_PAIRS):
        if deck not in (a, b):
            continue
        side = "a" if a == deck else "b"
        ka, fa = (key, path) if side == "a" else (a, RESEARCH.format(a))
        kb, fb = (key, path) if side == "b" else (b, RESEARCH.format(b))
        rows.append([p, block, ka, fa, kb, fb, *seeds(BASE_TABLE, p), deck, key, side])
    assert len(rows) == 7
    return rows


def charizard_rows(key, path, block):
    return [[B2E_CHARIZARD_FIRST + o, block, key, path, opp, T.format(opp), *seeds(BASE_B2E, B2E_CHARIZARD_FIRST + o),
             "charizardy", key, "a"] for o, opp in enumerate(PANEL)]


def write(name, rows):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(HEADER) + "\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    return name


def main():
    os.makedirs(OUT, exist_ok=True)
    written = []
    new = []
    for d, (key, path, role) in enumerate(NEW):
        for o, opp in enumerate(PANEL):
            p = 8 * d + o
            new.append([p, role, key, path, opp, T.format(opp), *seeds(BASE_NEW, p), key, key, "a"])
    new.append([24, "scoreboard", "rayquaza", NEW[1][1], "altaria_greninja", NEW[2][1], *seeds(BASE_NEW, 24),
                "rayquaza", "rayquaza", "a"])
    written.append(write("new_decks.tsv", new))
    written.append(write("new_decks_run.tsv", [r for r in new if r[2] not in NOT_RUN]))
    with open(os.path.join(OUT, "not_run.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(NOT_RUN, f, indent=1, ensure_ascii=False)
        f.write("\n")
    for deck, versions in VERSIONS.items():
        for key, path in versions:
            rows = charizard_rows(key, path, "variation") if deck == "charizardy" else table_rows(deck, key, path, "variation")
            written.append(write(f"var_{key}.tsv", rows))
        if deck == "charizardy":
            # B2e's own rows (held_key charizardy_entei, its file), so the replay can be compared byte for byte.
            main_rows = [r[:9] + ["charizardy", "charizardy_entei", "a"] for r in charizard_rows("charizardy_entei", H_CHARIZARD, "A_archetype")]
        else:
            main_rows = table_rows(deck, deck, T.format(deck), "identity")
        written.append(write(f"id_{deck}_main.tsv", main_rows))
    print("wrote tsv/: " + ", ".join(written))
    print("table pairings per deck: " + "; ".join(
        f"{d}: " + ",".join(str(p) for p, (a, b) in enumerate(TABLE_PAIRS) if d in (a, b)) for d in ("lucario", "suicune", "weezing")))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Writes the gauntlet deck files (decks/gauntlet_2026-09-26/) from the proposal
(rl/results/gauntlet_proposal_2026-09-26/README.md section 1 and section 6, Proposal B; exact lists in gauntlet.json)
and checks every file against gauntlet.json. Run from the repo root in WSL:  python3 rl/results/gauntlet_runs_2026-09-26/make_decks.py

- g- files: the three new decks, cards in the proposal's order.
- v-<deck>_2: the second list (gauntlet.json -> variation -> <deck> -> tests[0] -> twin -> list).
- v-<deck>_swap1/2: the proposal's two single-card Trainer swaps (gauntlet.json -> proposal_B_sensitivity -> swaps).
- The v- files are written as the main file with the changed lines replaced IN PLACE: each card that comes in
  sits on the line (the deck position) of the card it replaces. The engine builds the deck in file order and
  shuffles positions, so on the same seed the new card is dealt exactly where the old one would have been, and the
  paired comparison stays as tight as it can. A name can therefore appear on two lines (the engine and
  lib/deck_check.py add them up).
- Charizard Y's second list is the existing decks/screen/panel_ladder_2026-09-26/l-charizardy.txt (the README's
  section 6 table); it is not rewritten here. Its swaps start from h-charizardy_entei.txt.
Checks (exit 1 on any failure): each file's card multiset equals the list gauntlet.json gives; each t- file main
list parses to the same ordered card ids as the table's decks/research file (so a TSV may use either); every id is
in lib/deckgym-database.json.
"""
import collections
import io
import json
import os
import sys

ROOT = os.getcwd()
OUT = os.path.join(ROOT, "decks", "gauntlet_2026-09-26")
G = json.load(io.open(os.path.join(ROOT, "rl/results/gauntlet_proposal_2026-09-26/gauntlet.json"), encoding="utf-8"))
DB = {}
for e in json.load(io.open(os.path.join(ROOT, "lib/deckgym-database.json"), encoding="utf-8")):
    for k, v in e.items():
        if isinstance(v, dict) and "id" in v:
            DB[v["id"]] = v["name"]

NEW = {
    "g-mega_scizor_revavroom.txt": ("Metal", [
        "2 Varoom A2b 055", "1 Orthworm B2a 077", "2 Scyther B2b 001", "2 Mega Scizor ex B2b 047",
        "2 Revavroom B2b 050", "1 Cyrus A2 150", "1 Red A2b 071", "2 Poké Ball P-A 005",
        "2 Professor's Research P-A 007", "2 Copycat B1 225", "2 Metal Core Barrier B2 148",
        "1 Training Area B2 153"]),
    "g-dragonair_mega_rayquaza.txt": ("Fire, Lightning", [
        "2 Dratini B2b 051", "2 Gouging Fire B3a 054", "2 Dragonair B4 117", "1 Mega Rayquaza ex B4 120",
        "1 Sabrina A1 225", "1 Pokémon Center Lady A2b 070", "2 Poké Ball P-A 005",
        "2 Professor's Research P-A 007", "2 Copycat B1 225", "1 Ancient Booster Energy Capsule B3a 069",
        "1 Professor Sada B3a 072", "1 Small Balloon B3b 064", "2 Rainbow Cave B4 155"]),
    "g-mega_altaria_greninja.txt": ("Psychic", [
        "2 Froakie A1 087", "2 Greninja A1 089", "1 Mega Altaria ex B1 102", "2 Swablu B1 196",
        "1 Bonsly B3 078", "1 Oricorio B4 078", "1 Cyrus A2 150", "2 Poké Ball P-A 005", "2 Rare Candy A3 144",
        "2 Professor's Research P-A 007", "2 Copycat B1 225", "1 Hiking Trail B2b 069",
        "1 Small Balloon B3b 064"]),
}
# Where gauntlet.json holds each new deck's list.
NEW_SRC = {
    "g-mega_scizor_revavroom.txt": lambda: G["additions"][0]["representative_list"],
    "g-dragonair_mega_rayquaza.txt": lambda: G["variation_growth_candidates"]["Dragonair Mega Rayquaza ex"]["modal_list"],
    "g-mega_altaria_greninja.txt": lambda: G["variation_growth_candidates"]["Mega Altaria ex Greninja"]["modal_list"],
}

T = "decks/screen/opponents/t-{}.txt"
H = "rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt"
# (output file, main file, archetype, [(line in the main file, [lines that take its place])], what gauntlet.json says)
VARIANTS = [
    ("v-lucario_2.txt", T.format("lucario"), "Mega Lucario ex Lucario",
     [("2 Riolu B3 079", ["2 Riolu A2 091"]), ("1 Protective Poncho B2 147", ["1 Lucky Ice Pop B2 145"])], "twin"),
    ("v-lucario_swap1.txt", T.format("lucario"), "Mega Lucario ex Lucario",
     [("1 Protective Poncho B2 147", ["1 Lucky Ice Pop B2 145"])], 0),
    ("v-lucario_swap2.txt", T.format("lucario"), "Mega Lucario ex Lucario",
     [("1 Pokémon Center Lady A2b 070", ["1 Sabrina A1 225"])], 1),
    ("v-suicune_2.txt", T.format("suicune"), "Suicune ex Baxcalibur",
     [("1 Frigibax B2a 034", ["2 Frigibax B2a 034"]), ("1 Frigibax P-B 037", []),
      ("1 Team Rocket's Boss B4a 071", ["1 Giant Cape A2 147"]), ("1 Field Blower B3 147", ["1 Mars A2 155"])], "twin"),
    ("v-suicune_swap1.txt", T.format("suicune"), "Suicune ex Baxcalibur",
     [("1 Team Rocket's Boss B4a 071", ["1 Giant Cape A2 147"])], 0),
    ("v-suicune_swap2.txt", T.format("suicune"), "Suicune ex Baxcalibur",
     [("1 Field Blower B3 147", ["1 Mars A2 155"])], 1),
    ("v-weezing_2.txt", T.format("weezing"), "Team Rocket's Weezing ex Hoopa ex",
     [("1 Darkrai ex A2 110", ["1 Mega Absol ex B1 151"]),
      ("2 Copycat B1 225", ["1 Copycat B1 225", "1 Pokémon Center Lady A2b 070"]),
      ("1 Mars A2 155", ["1 Lucky Ice Pop B2 145"]), ("1 Field Blower B3 147", ["1 Lucky Ice Pop B2 145"])], "twin"),
    ("v-weezing_swap1.txt", T.format("weezing"), "Team Rocket's Weezing ex Hoopa ex",
     [("1 Mars A2 155", ["1 Lucky Ice Pop B2 145"])], 0),
    ("v-weezing_swap2.txt", T.format("weezing"), "Team Rocket's Weezing ex Hoopa ex",
     [("2 Copycat B1 225", ["1 Copycat B1 225", "1 Pokémon Center Lady A2b 070"])], 1),
    ("v-charizardy_swap1.txt", H, "Mega Charizard Y ex Entei ex",
     [("2 Copycat B1 225", ["1 Copycat B1 225", "1 Rainbow Cave B4 155"])], 0),
    ("v-charizardy_swap2.txt", H, "Mega Charizard Y ex Entei ex",
     [("1 Lucky Ice Pop B2 145", ["1 Sabrina A1 225"])], 1),
]


def ms(lines):
    """Card multiset by id from 'N Name SET NUM' lines."""
    c = collections.Counter()
    for ln in lines:
        p = ln.split()
        c[" ".join(p[-2:])] += int(p[0])
    return c


def ids_in_order(path):
    out = []
    for ln in io.open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ln.startswith("Energy:"):
            continue
        p = ln.split()
        out += [" ".join(p[-2:])] * int(p[0])
    return out


def card_lines(path):
    lines = [l.rstrip("\n") for l in io.open(path, encoding="utf-8")]
    return lines[0], [l for l in lines[1:] if l.strip()]


def parse_swap(s):
    # "Lucky Ice Pop B2 145 (copy 1)" -> "B2 145"
    s = s.split(" (copy")[0].split()
    return " ".join(s[-2:])


def main():
    os.makedirs(OUT, exist_ok=True)
    bad = []
    written = []
    for fn, (energy, lines) in NEW.items():
        want = ms(NEW_SRC[fn]())
        if ms(lines) != want:
            bad.append(f"{fn}: differs from gauntlet.json: {ms(lines) - want} / {want - ms(lines)}")
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"Energy: {energy}\n" + "\n".join(lines) + "\n")
        written.append(fn)
    proposal = {a["archetype"]: a for a in G["proposal_B_sensitivity"]["archetypes"]}
    for fn, main_file, arch, ops, what in VARIANTS:
        energy, lines = card_lines(os.path.join(ROOT, main_file))
        new = list(lines)
        for old, repl in ops:
            if new.count(old) != 1:
                bad.append(f"{fn}: line {old!r} appears {new.count(old)} times in {main_file}")
                continue
            k = new.index(old)
            new[k:k + 1] = repl
        main_ms = ms(lines)
        if what == "twin":
            want = ms(G["variation"][arch]["tests"][0]["twin"]["list"])
            # the proposal_B copy of the twin must be the same list (Charizard's is not used: see below)
            if ms(proposal[arch]["twin"]["list"]) != want:
                bad.append(f"{fn}: gauntlet.json's two copies of the {arch} twin differ")
        else:
            sw = proposal[arch]["swaps"][what]
            want = main_ms.copy()
            want[parse_swap(sw["out"])] -= 1
            want[parse_swap(sw["in"])] += 1
            want = +want
        if ms(new) != want:
            bad.append(f"{fn}: {ms(new) - want} extra, {want - ms(new)} missing against gauntlet.json")
        with open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n") as f:
            f.write(energy + "\n" + "\n".join(new) + "\n")
        written.append(fn)
    # every id resolves, and the name on the line is the database's
    for fn in written:
        _, lines = card_lines(os.path.join(OUT, fn))
        for ln in lines:
            p = ln.split()
            i, nm = " ".join(p[-2:]), " ".join(p[1:-2])
            if i not in DB:
                bad.append(f"{fn}: unknown id {i}")
            elif DB[i] != nm:
                bad.append(f"{fn}: {nm!r} but the database names {i} {DB[i]!r}")
        if sum(ms(lines).values()) != 20:
            bad.append(f"{fn}: {sum(ms(lines).values())} cards")
    # t- files = the table's research files, card by card in order (so either can stand for the main list)
    for d in ("lucario", "suicune", "weezing", "altaria", "blaziken", "hydreigon", "sceptile", "vespiquen"):
        a, b = ids_in_order(os.path.join(ROOT, T.format(d))), ids_in_order(os.path.join(ROOT, f"decks/research/{d}.txt"))
        if a != b:
            bad.append(f"t-{d}.txt and decks/research/{d}.txt differ in card order or content")
    # Charizard Y: the README's second list is l-charizardy.txt; gauntlet.json's proposal_B twin is another list.
    lz = ms(card_lines(os.path.join(ROOT, "decks/screen/panel_ladder_2026-09-26/l-charizardy.txt"))[1])
    hz = ms(card_lines(os.path.join(ROOT, H))[1])
    jz = ms(proposal["Mega Charizard Y ex Entei ex"]["twin"]["list"])
    print(f"Charizard Y: l-charizardy.txt vs h-: +{dict(lz - hz)} -{dict(hz - lz)}; "
          f"gauntlet.json proposal_B twin vs h-: +{dict(jz - hz)} -{dict(hz - jz)}; "
          f"l- equals that twin: {lz == jz}")
    print(f"written to {OUT}: " + ", ".join(written))
    if bad:
        print("PROBLEMS:")
        for b in bad:
            print("  ", b)
        sys.exit(1)
    print("DECKS OK: every file equals gauntlet.json's list; ids resolve; names match; 20 cards each; "
          "t- files = decks/research files in card order")


if __name__ == "__main__":
    main()

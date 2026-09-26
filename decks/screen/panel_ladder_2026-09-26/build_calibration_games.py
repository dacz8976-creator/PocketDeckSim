#!/usr/bin/env python3
"""Build calibration_games.csv (A3) from ladder_mapping.csv and the Ladder Log artifact.

usage: python build_calibration_games.py --logs DIR [--mapping ladder_mapping.csv] [--out calibration_games.csv]
  DIR holds the artifact's `logs` collection as one JSON file per deck id (what `ArtifactData list`
  with an out_dir writes: {"games": [{"id", "opp", "result", "note", "ts"}, ...]}).

One row per logged game whose opponent maps to a panel list (decks/screen/opponents/t-*.txt,
exact or variant) or to an off-panel archetype that has a list file in this folder. Dustin's deck
is resolved to its file; games whose deck has no file are kept and marked usable=0.
New games need a row in ladder_mapping.csv first; a new deck id needs a DECK_FILES entry below.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
SEPT24_COPY = os.path.join(REPO, "rl", "results", "limitless_skill_model_2026-09-25", "ladder_log_games.csv")

# Ladder Log deck id -> (file relative to the repo root, status, note). Resolved on Sept 26 by reading
# decks/dustin and decks/brews and comparing the log's deck names and game notes with the files.
DECK_FILES = {
    "d02": ("decks/dustin/02-arceus-crobat.txt", "file", ""),
    "d07": ("decks/dustin/07-skarmory-stall.txt", "file", ""),
    "brew-01": ("decks/brews/brew-01-arceus-crobat-xatu.txt", "file", ""),
    "brew-03a": ("decks/brews/brew-03a-arceus-nihilego-toxapex.txt", "file-deviates",
                 "log note for the Dustox game says a second Poison tool replaced the Cape; the file still has Giant Cape"),
    "brew-04": ("decks/brews/brew-04-xatu-slowking.txt", "file-deviates",
                "log note says Giant Cape -> Elegant Cape (B3b 065) and X Speed -> Peculiar Plaza for this game; the file has Giant Cape and X Speed"),
    # The log calls this deck "Meowstic / Hatterene / Comfey (2026-09-15 list)" and its notes mention Comfey and
    # Peculiar Plaza. brew-05-meowstic-hatterene-confusion.txt has neither; brew-05b-meowstic-hatterene-comfey.txt
    # has both, and decks/screen/results.md already pairs the same 3-3 ladder record with brew-05b.
    "brew-05": ("decks/brews/brew-05b-meowstic-hatterene-comfey.txt", "file",
                "log id brew-05 = the Comfey list = brew-05b file (not brew-05-...-confusion.txt, which has no Comfey or Peculiar Plaza)"),
    "brew-05c": ("", "no-file", "Cape variant of brew-05b; no file in decks/brews"),
    "brew-06": ("decks/brews/brew-06-pyukumuku-silvally-payback.txt", "file", ""),
    "brew-06b": ("decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt", "file", ""),
    "c-skarmory-ex-chandelure": ("", "no-file", "custom Skarmory ex / Chandelure list; no file in decks/dustin or decks/brews"),
}

# Limitless archetype name (as in ladder_mapping.csv) -> (key, list file) for off-panel lists in this folder
OFF_PANEL_FILES = {
    "Mega Charizard Y ex Entei ex": ("charizardy", "decks/screen/panel_ladder_2026-09-26/l-charizardy.txt"),
    "Mega Sharpedo ex Gyarados": ("sharpedo", "decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt"),
}

FIRST_RE = re.compile(r"\bwent first\b", re.I)
SECOND_RE = re.compile(r"\bwent second\b", re.I)


def load_artifact_games(logs_dir):
    games = {}
    files = sorted(glob.glob(os.path.join(logs_dir, "*.json")))
    if not files:
        raise SystemExit(f"no JSON files in {logs_dir}")
    for path in files:
        deck_id = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        for g in doc.get("games", []):
            key = (deck_id, int(g["ts"]))
            if key in games:
                raise SystemExit(f"duplicate (deck_id, ts) in artifact: {key}")
            games[key] = dict(g, deck_id=deck_id)
    return games


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", required=True, help="folder of the artifact's logs collection, one JSON per deck id")
    ap.add_argument("--mapping", default=os.path.join(HERE, "ladder_mapping.csv"))
    ap.add_argument("--out", default=os.path.join(HERE, "calibration_games.csv"))
    a = ap.parse_args()

    with open(a.mapping, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    art = load_artifact_games(a.logs)
    if len(rows) != len(art):
        raise SystemExit(f"{a.mapping} has {len(rows)} rows, the artifact has {len(art)} games: map the new games first")

    for r in rows:  # every mapping row is one artifact game with the same opponent text and result
        key = (r["deck_id"], int(r["ts"]))
        if key not in art:
            raise SystemExit(f"mapping row not in artifact: {key} {r['opponent_text']}")
        g = art[key]
        if g["opp"] != r["opponent_text"] or g["result"] != r["result"]:
            raise SystemExit(f"mapping row differs from artifact: {key}: {g['opp']!r}/{g['result']} vs {r['opponent_text']!r}/{r['result']}")

    if os.path.isfile(SEPT24_COPY):  # the Sept 24 copy must be a subset of what the artifact holds
        with open(SEPT24_COPY, encoding="utf-8", newline="") as f:
            copy = [(c["opponent_archetype"], c["result"]) for c in csv.DictReader(f)]
        pool = [(r["opponent_text"], r["result"]) for r in rows]
        for item in copy:
            if item in pool:
                pool.remove(item)
            else:
                raise SystemExit(f"Sept 24 copy has a game the artifact does not: {item}")
        print(f"cross-check: all {len(copy)} games of the Sept 24 copy are in the artifact ({len(pool)} newer)")

    out_rows = []
    for r in rows:
        g = art[(r["deck_id"], int(r["ts"]))]
        panel_key = r["panel_key"].strip()
        arch = r["mapped_archetype"]
        if panel_key:
            opp_key, opp_file = panel_key, f"decks/screen/opponents/t-{panel_key}.txt"
        elif arch in OFF_PANEL_FILES:
            opp_key, opp_file = OFF_PANEL_FILES[arch]
        else:
            continue  # no list file for this opponent: not a calibration game
        if r["deck_id"] not in DECK_FILES:
            raise SystemExit(f"unknown deck id {r['deck_id']}: add it to DECK_FILES")
        deck_file, deck_status, deck_note = DECK_FILES[r["deck_id"]]
        for p in (deck_file, opp_file):
            if p and not os.path.isfile(os.path.join(REPO, p)):
                raise SystemExit(f"missing file: {p}")
        note = g.get("note", "") or ""
        went_first = "1" if FIRST_RE.search(note) else ("0" if SECOND_RE.search(note) else "")
        list_match = "variant" if r["class"] == "panel variant" else ("inferred" if r["confidence"] == "likely" else "exact")
        out_rows.append({
            "game_id": g["id"], "date": r["date"], "ts": r["ts"], "deck_id": r["deck_id"], "deck_played": r["deck_played"],
            "deck_file": deck_file, "deck_file_status": deck_status, "deck_file_note": deck_note,
            "opponent_text": r["opponent_text"], "mapped_archetype": arch, "class": r["class"],
            "opponent_key": opp_key, "opponent_file": opp_file, "list_match": list_match, "confidence": r["confidence"],
            "went_first": went_first, "result": r["result"], "win": "1" if r["result"] == "W" else "0",
            "usable": "1" if deck_file else "0", "note": note,
        })

    out_rows.sort(key=lambda x: int(x["ts"]))
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    usable = [x for x in out_rows if x["usable"] == "1"]
    pairs = sorted({(x["deck_file"], x["opponent_file"]) for x in usable})
    wins = sum(int(x["win"]) for x in usable)
    print(f"wrote {a.out}: {len(out_rows)} rows with a listed opponent, {len(usable)} usable, "
          f"record {wins}-{len(usable) - wins}, {len(pairs)} distinct pairs")
    for x in out_rows:
        if x["usable"] != "1":
            print(f"  not usable: {x['deck_id']} vs {x['opponent_key']} ({x['result']}): {x['deck_file_note']}")


if __name__ == "__main__":
    main()

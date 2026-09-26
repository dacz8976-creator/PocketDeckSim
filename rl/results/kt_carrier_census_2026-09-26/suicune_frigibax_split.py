#!/usr/bin/env python3
"""kt carrier census, follow-up (2026-09-26): the Suicune ex Baxcalibur Frigibax split.

Recounts, straight from the DEVELOPMENT-half standings (split.json
development_event_ids; holdout standings never opened), how many Suicune ex
Baxcalibur decklists carry Frigibax P-B 037 (Stiffen, a switch-1 card), how many
carry Frigibax B2a 034 (Chilly, not in the set), how many carry both, and how each
list compares with the panel's own Suicune list (decks/screen/opponents/t-suicune.txt).
Reports; decides nothing.

Output: suicune_frigibax_split.json in this folder (read by suicune_frigibax_split.md).
Run from the repo root with Windows python:
  python rl/results/kt_carrier_census_2026-09-26/suicune_frigibax_split.py
"""
import gzip
import io
import json
import os
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LSM = os.path.join(ROOT, "rl", "results", "limitless_skill_model_2026-09-25")
RAW = os.path.join(LSM, "raw")
SPLIT = os.path.join(LSM, "split.json")
PANEL = os.path.join(ROOT, "decks", "screen", "opponents", "t-suicune.txt")
OUT = os.path.join(HERE, "suicune_frigibax_split.json")
ARCH = "Suicune ex Baxcalibur"
PB = "P-B 037"    # Frigibax, Stiffen (group 3, switch 1)
B2A = "B2a 034"   # Frigibax, Chilly 20 (outside the set)


def norm_id(set_code, number):
    """'P-B', '37' -> 'P-B 037' (the cards.json form)."""
    s = str(set_code).strip()
    n = str(number).strip()
    try:
        n = "%03d" % int(n)
    except ValueError:
        pass
    return "%s %s" % (s, n)


def read_panel(path):
    cards = Counter()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.lower().startswith("energy"):
                continue
            parts = line.split()
            cards[norm_id(parts[-2], parts[-1])] += int(parts[0])
    return cards


def placing_key(r):
    p = r["placing"]
    return (0, p) if isinstance(p, int) else (1, 10 ** 9)


def main():
    panel = read_panel(PANEL)
    assert sum(panel.values()) == 20, panel
    with open(SPLIT, encoding="utf-8") as f:
        split = json.load(f)
    dev_ids = list(split["development_event_ids"])
    holdout_ids = list(split["holdout_event_ids"])
    assert not set(dev_ids) & set(holdout_ids)

    rows = []
    n_entries = 0
    events_with_list = set()
    for eid in dev_ids:
        with gzip.open(os.path.join(RAW, eid + "_details.json.gz"), "rt", encoding="utf-8") as f:
            det = json.load(f)
        with gzip.open(os.path.join(RAW, eid + "_standings.json.gz"), "rt", encoding="utf-8") as f:
            standings = json.load(f)
        if isinstance(standings, dict):
            standings = standings.get("standings") or standings.get("data") or []
        for s in standings:
            if (s.get("deck") or {}).get("name") != ARCH:
                continue
            n_entries += 1
            dl = s.get("decklist")
            if not dl:
                continue
            events_with_list.add(eid)
            cards = Counter()
            other_frig = Counter()
            for section in ("pokemon", "trainer"):
                for c in dl.get(section) or []:
                    if not isinstance(c, dict):
                        continue
                    cnt = int(c.get("count") or 0)
                    if c.get("set") is None or c.get("number") is None:
                        if (c.get("name") or "").strip().casefold() == "frigibax":
                            other_frig["name-only"] += cnt
                        continue
                    cid = norm_id(c["set"], c["number"])
                    cards[cid] += cnt
                    if (c.get("name") or "").strip().casefold() == "frigibax" and cid not in (PB, B2A):
                        other_frig[cid] += cnt
            rec = s.get("record") or {}
            rows.append({
                "player": s.get("player"), "player_name": s.get("name"),
                "event_id": eid, "event_name": det.get("name"), "event_size": det.get("players"),
                "date": (det.get("date") or "")[:10], "placing": s.get("placing"),
                "drop": bool(s.get("drop")),
                "record": "%s-%s-%s" % (rec.get("wins", ""), rec.get("losses", ""), rec.get("ties", "")),
                "pb037_copies": cards.get(PB, 0), "b2a034_copies": cards.get(B2A, 0),
                "other_frigibax": dict(other_frig),
                "n_cards": sum(cards.values()),
                "shares_with_panel": sum((cards & panel).values()),
                "extra_vs_panel": dict(cards - panel), "lacks_vs_panel": dict(panel - cards),
                "url": "https://play.limitlesstcg.com/tournament/%s/player/%s/decklist" % (eid, s.get("player")),
            })

    pb_lists = sorted([r for r in rows if r["pb037_copies"]],
                      key=lambda r: (placing_key(r), -(r["event_size"] or 0), r["date"]))
    b2a_lists = [r for r in rows if r["b2a034_copies"]]
    both = [r for r in rows if r["pb037_copies"] and r["b2a034_copies"]]
    pb_only = [r for r in rows if r["pb037_copies"] and not r["b2a034_copies"]]
    b2a_only = sorted([r for r in rows if r["b2a034_copies"] and not r["pb037_copies"]],
                      key=lambda r: (placing_key(r), -(r["event_size"] or 0), r["date"]))
    neither = [r for r in rows if not r["pb037_copies"] and not r["b2a034_copies"]]
    exact = [r for r in rows if r["shares_with_panel"] == 20]

    summary = {
        "note": "REPORTS; decides nothing. Development-half standings only; holdout never opened.",
        "archetype": ARCH,
        "panel_list": PANEL.replace(ROOT + os.sep, "").replace(os.sep, "/"),
        "panel_frigibax": {PB: panel.get(PB, 0), B2A: panel.get(B2A, 0)},
        "development_events_scanned": len(dev_ids),
        "holdout_events_not_opened": len(holdout_ids),
        "entries": n_entries,
        "lists_with_decklist": len(rows),
        "events_with_decklist": len(events_with_list),
        "lists_not_20_cards": sum(1 for r in rows if r["n_cards"] != 20),
        "frigibax_copies_per_list_histogram": dict(Counter(
            r["pb037_copies"] + r["b2a034_copies"] + sum(r["other_frigibax"].values()) for r in rows)),
        "other_frigibax_printings_seen": sorted({k for r in rows for k in r["other_frigibax"]}),
        "lists_carrying_pb037": len(pb_lists),
        "copies_pb037": sum(r["pb037_copies"] for r in rows),
        "lists_carrying_b2a034": len(b2a_lists),
        "copies_b2a034": sum(r["b2a034_copies"] for r in rows),
        "lists_carrying_both": len(both),
        "lists_pb037_only": len(pb_only),
        "lists_b2a034_only": len(b2a_only),
        "lists_neither": len(neither),
        "pb037_copy_split": dict(Counter(r["pb037_copies"] for r in pb_lists)),
        "b2a034_copy_split": dict(Counter(r["b2a034_copies"] for r in b2a_lists)),
        "lists_equal_to_panel_20_of_20": len(exact),
        "lists_equal_to_panel_that_carry_pb037": sum(1 for r in exact if r["pb037_copies"]),
        "shares_with_panel_histogram": dict(Counter(r["shares_with_panel"] for r in rows)),
        "pb037_carriers_by_placing": pb_lists,
        "b2a034_only_best_10_by_placing": b2a_only[:10],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)

    for k, v in summary.items():
        if k.endswith("by_placing"):
            continue
        print("%-42s %s" % (k, v))
    print("\nP-B 037 carriers by placing (placing of event size, player, date, record, copies, drop, shares/20 with panel):")
    for r in pb_lists:
        print("  %-5s of %-4s %-14s %s %-7s PB x%d B2a x%d %-5s %2d/20" % (
            r["placing"], r["event_size"], r["player"], r["date"], r["record"],
            r["pb037_copies"], r["b2a034_copies"], "drop" if r["drop"] else "", r["shares_with_panel"]))
    print("\nB2a 034-only lists, best 10 by placing:")
    for r in b2a_only[:10]:
        print("  %-5s of %-4s %-14s %s %-7s B2a x%d %2d/20" % (
            r["placing"], r["event_size"], r["player"], r["date"], r["record"],
            r["b2a034_copies"], r["shares_with_panel"]))
    print("\nwritten:", OUT)


if __name__ == "__main__":
    main()

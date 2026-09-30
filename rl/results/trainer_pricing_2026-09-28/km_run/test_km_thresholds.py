#!/usr/bin/env python3
"""km_thresholds.py on synthetic counts (no game): the cases its rule must get right, each with a known answer. The
baseline arm is kta3 (Amendment 1, Sept 30: km re-issued on kta), the candidate arm km3.

  python3 test_km_thresholds.py <scratch folder>

Writes synthetic counter-tool rows (the tool's row format, the table's seeds and seats, made-up counts) into the
folder, runs km_thresholds.py's own command line on them, and checks:
  S1  M1 PASS CASE: kta3 plays Arena on 1/4 of its offered turns, km3 on 5/12 (paired by deal); T = 1/3 exactly and the
      lower bound is above zero, so the line gets a threshold.
      M2 CANNOT-PASS CASE: both arms play Training Area on 33/100, km3 differing on a few deals in both directions; the
      lower bound is below zero, so the line cannot pass (its midpoint 33/100 is recorded, not used).
  S2  OFFERED-ZERO CASE: km3's arm never has Training Area offered: M2 cannot pass (no offered turn).
      M1 with kta3 at 1/2 and km3 at 3/4: T = 5/8 (used by the guard case below).
  G1  EXACT COMPARISON on the gating deals 0-199 with S1's T1 = 1/3: km3 at 600/1800 = 1/3 exactly passes (at least T);
      km3 at 599/1800 (displayed 33.3%, the same as T) is below T and does not pass; M2 stays "cannot pass".
  G2  GUARD CASE with S2's T1 = 5/8: kta3's own gating rate 7/8 is at or above T, so M1 is "not shown at this size"
      even though km3's rate (1) is above T.
  and that a second run on the same files writes byte-identical output (the frozen seed and order).
Exit 0 when every case gives its known answer."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KT = os.path.join(HERE, "km_thresholds.py")
BASES = {"table": 72_000_000, "new_decks.tsv": 21_108_000_000}
CELLS = {("table", 0): ("altaria", "blaziken"), ("table", 1): ("altaria", "hydreigon"), ("table", 2): ("altaria", "lucario"),
         ("table", 3): ("altaria", "sceptile"), ("table", 4): ("altaria", "suicune"), ("table", 8): ("blaziken", "lucario"),
         ("table", 13): ("hydreigon", "lucario"), ("table", 18): ("lucario", "sceptile"), ("table", 19): ("lucario", "suicune"),
         ("table", 20): ("lucario", "vespiquen"), ("table", 21): ("lucario", "weezing"),
         ("new_decks.tsv", 8): ("rayquaza", "lucario"), ("new_decks.tsv", 9): ("rayquaza", "altaria"),
         ("new_decks.tsv", 16): ("altaria_greninja", "lucario")}
M1 = [("table", 2), ("table", 8), ("table", 13), ("table", 18), ("table", 19), ("table", 20), ("table", 21),
      ("new_decks.tsv", 8), ("new_decks.tsv", 16)]
M2 = [("table", 0), ("table", 1), ("table", 3), ("table", 4), ("new_decks.tsv", 9)]
ORDER = [c for c in CELLS]   # the tool's km17 order for these 14 cells


def row(cell, i, code, arena, training):
    """arena / training: (offered, played) on Lucario's / Altaria's side, or None for no entry."""
    a, b = CELLS[cell]
    seats = [a, b] if i % 2 == 0 else [b, a]
    counts = []
    for s in (0, 1):
        cards = {}
        if seats[s] == "lucario" and arena is not None:
            cards["Arena of Antiquity"] = {"offered": arena[0], "played": arena[1], "targets": {}}
        if seats[s] == "altaria" and training is not None:
            cards["Training Area"] = {"offered": training[0], "played": training[1], "targets": {}}
        counts.append({"cards": cards, "deck": seats[s], "seat": s})
    return {"a": a, "a_file": f"synthetic/{a}.txt", "b": b, "b_file": f"synthetic/{b}.txt", "bots": [code, code],
            "counts": counts, "first_seat": i % 2, "i": i, "moves": "0" * 16, "pairing": cell[1], "seat_decks": seats,
            "seed": BASES[cell[0]] + 10_000 * cell[1] + i, "source": cell[0], "xspeed": []}


def write(path, deals, code, arena_fn, training_fn):
    """arena_fn(n, i) / training_fn(n, i): (offered, played) for the n-th unit of the line (cells in the line's order,
    deals in increasing i), or None."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for cell in ORDER:
            for i in deals:
                k = i - deals.start
                ar = arena_fn(M1.index(cell) * len(deals) + k, i) if cell in M1 else None
                tr = training_fn(M2.index(cell) * len(deals) + k, i) if cell in M2 else None
                f.write(json.dumps(row(cell, i, code, ar, tr), sort_keys=True, separators=(",", ":")) + "\n")


def sh(*args):
    p = subprocess.run([sys.executable, KT, *args], capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stdout, p.stderr)
        raise SystemExit(f"km_thresholds.py {args[0]} exited {p.returncode}")
    return p.stdout


def expect(cond, what):
    print(("  ok    " if cond else "  WRONG ") + what)
    return bool(cond)


def main():
    d = sys.argv[1]
    os.makedirs(d, exist_ok=True)
    sample, gating = range(200, 300), range(0, 200)
    ok = True
    # S1: M1 pass (1/4 v 5/12), M2 cannot pass (33/100 both, flips both ways).
    write(f"{d}/s1_kta3.jsonl", sample, "kta3", lambda n, i: (1, int(i % 4 == 0)), lambda n, i: (1, int(i % 3 == 0)))
    write(f"{d}/s1_km3.jsonl", sample, "km3", lambda n, i: (1, int((5 * n) % 12 < 5)),
          lambda n, i: (1, int((i % 3 == 0) != (i % 25 == 7))))
    out = sh("sample", "--kta3", f"{d}/s1_kta3.jsonl", "--km3", f"{d}/s1_km3.jsonl", "--json", f"{d}/s1.json", "--txt", f"{d}/s1.txt")
    print("==== S1: thresholds.txt\n" + out)
    s1 = json.load(open(f"{d}/s1.json"))["lines"]
    ok &= expect(s1["M1"]["kta3"]["rate"] == "1/4" and s1["M1"]["km3"]["rate"] == "5/12", "S1 M1 rates 1/4 and 5/12 (225/900, 375/900)")
    ok &= expect(s1["M1"]["T"] == "1/3" and s1["M1"]["status"] == "threshold" and s1["M1"]["interval"][0] > 0,
                 "S1 M1: T = 1/3 exactly, lower bound above zero -> THRESHOLD (the pass case)")
    ok &= expect(s1["M2"]["T"] == "33/100" and s1["M2"]["status"] == "cannot pass" and s1["M2"]["interval"][0] <= 0,
                 "S1 M2: equal rates 33/100, lower bound at or below zero -> CANNOT PASS (the cannot-pass case)")
    ok &= expect(repr(s1["M1"]["interval"][0]) == s1["M1"]["interval_detail"]["lower_repr"],
                 "S1: the JSON float reads back to the printed repr digit for digit")
    os.replace(f"{d}/s1.json", f"{d}/s1_first.json")
    sh("sample", "--kta3", f"{d}/s1_kta3.jsonl", "--km3", f"{d}/s1_km3.jsonl", "--json", f"{d}/s1.json", "--txt", f"{d}/s1_again.txt")
    ok &= expect(open(f"{d}/s1.json", "rb").read() == open(f"{d}/s1_first.json", "rb").read(),
                 "S1 rerun on the same files: thresholds.json byte-identical (the frozen seeds and order)")
    # S2: M2 never offered in km3's arm; M1 1/2 v 3/4 (T = 5/8).
    write(f"{d}/s2_kta3.jsonl", sample, "kta3", lambda n, i: (1, int(i % 2 == 0)), lambda n, i: (1, int(i % 3 == 0)))
    write(f"{d}/s2_km3.jsonl", sample, "km3", lambda n, i: (1, int(i % 4 != 3)), lambda n, i: None)
    out = sh("sample", "--kta3", f"{d}/s2_kta3.jsonl", "--km3", f"{d}/s2_km3.jsonl", "--json", f"{d}/s2.json", "--txt", f"{d}/s2.txt")
    print("==== S2: thresholds.txt\n" + out)
    s2 = json.load(open(f"{d}/s2.json"))["lines"]
    ok &= expect(s2["M2"]["km3"]["offered"] == 0 and s2["M2"]["T"] is None and s2["M2"]["status"] == "cannot pass"
                 and s2["M2"]["interval_detail"]["zero_offered_replicates"] == 10_000,
                 "S2 M2: km3 never offered -> rate undefined, every replicate 0.0, CANNOT PASS (the offered-zero case)")
    ok &= expect(s2["M1"]["T"] == "5/8" and s2["M1"]["status"] == "threshold", "S2 M1: T = 5/8, THRESHOLD")
    # G1: gating deals with S1's T1 = 1/3: exactly T passes; one play fewer (same display) does not.
    write(f"{d}/g_kta3.jsonl", gating, "kta3", lambda n, i: (1, int(i % 4 == 0)), lambda n, i: (1, int(i % 3 == 0)))
    write(f"{d}/g1_km3_exact.jsonl", gating, "km3", lambda n, i: (1, int(n < 600)), lambda n, i: (1, 1))
    write(f"{d}/g1_km3_below.jsonl", gating, "km3", lambda n, i: (1, int(n < 599)), lambda n, i: (1, 1))
    out = sh("gate", "--thresholds", f"{d}/s1.json", "--kta3", f"{d}/g_kta3.jsonl", "--km3", f"{d}/g1_km3_exact.jsonl")
    print("==== G1a: gate, km3 at exactly T\n" + out)
    ok &= expect("M1 Arena of Antiquity: kta3 450/1800 = 1/4" in out and "km3 600/1800 = 1/3" in out and "PASSES" in out,
                 "G1a: km3's gating rate 1/3 equals T = 1/3 -> PASSES (at least T, compared exactly)")
    ok &= expect("M2 Training Area" in out and "CANNOT PASS" in out, "G1a: M2 stays CANNOT PASS whatever its gating rates")
    out = sh("gate", "--thresholds", f"{d}/s1.json", "--kta3", f"{d}/g_kta3.jsonl", "--km3", f"{d}/g1_km3_below.jsonl")
    print("==== G1b: gate, km3 one play below T\n" + out)
    ok &= expect("km3 599/1800 = 599/1800 (33.3%)" in out and "T = 1/3 (33.3%)" in out and "below T" in out,
                 "G1b: 599/1800 displays as 33.3% like T, but is below T exactly -> NOT SHOWN (the display is never compared)")
    # G2: the guard, with S2's T1 = 5/8: kta3's own gating rate 7/8 is already at or above it.
    write(f"{d}/g2_kta3.jsonl", gating, "kta3", lambda n, i: (1, int(i % 8 != 7)), lambda n, i: (1, 0))
    write(f"{d}/g2_km3.jsonl", gating, "km3", lambda n, i: (1, 1), lambda n, i: (1, 0))
    out = sh("gate", "--thresholds", f"{d}/s2.json", "--kta3", f"{d}/g2_kta3.jsonl", "--km3", f"{d}/g2_km3.jsonl")
    print("==== G2: gate, the guard\n" + out)
    ok &= expect("kta3 1575/1800 = 7/8" in out and "the guard" in out,
                 "G2: kta3's gating rate 7/8 >= T = 5/8 -> NOT SHOWN AT THIS SIZE (the guard), though km3's rate 1 is above T")
    print("ALL CASES GIVE THEIR KNOWN ANSWER" if ok else "A CASE IS WRONG")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

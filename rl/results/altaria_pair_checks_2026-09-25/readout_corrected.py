#!/usr/bin/env python3
"""The Altaria pair checks' readout under the corrected C2 completeness rule (Fable's ruling, Sept 25, written before
any training result existed; Dustin can overrule).

    readout_corrected.py INTERFACE_DIR V22_DIR PARITY_DIR

Corrected rule: every C2 game in which the probed seat had at least one decision must contribute at least one probed
decision; a game in which the probed seat had no decision (it ended with no error before the probed seat had any
choice: the add-on plays single-option moves itself) is counted, listed with its seed and how it ended, and is not a
failure. Every other condition is readout.py's, unchanged, and C2's hidden-information and control conditions are
recomputed from the saved counts. READOUT.txt (the original rule) is kept unchanged beside this one.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# How the listed games ended: replayed with the rules4 program and traces (README.md, "The two games").
ENDINGS = {
    21_101_100_083: "Altaria went first; Igglybuff's Sleepy Lullaby (10, Asleep) on Lucario's lone Bonsly (30 HP), then a "
                    "Benched Darkrai's Bad Dreams (20) at the end of turn 1; Lucario's setup was forced",
    21_101_100_088: "the same line: Altaria first, Sleepy Lullaby then Bad Dreams knock out a lone Bonsly on turn 1; "
                    "Lucario's setup was forced",
}


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    iface = Path(sys.argv[1])
    s = json.loads((iface / "summary.json").read_text(encoding="utf-8"))["c2"]
    rows = [json.loads(line) for line in (iface / "c2_games.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    errors = [r for r in rows if r.get("error")]
    no_choice = [r for r in rows if not r.get("error") and r["decisions"] == 0]
    probed = [r for r in rows if not r.get("error") and r["decisions"] > 0]
    counts = s["counts"]
    hidden = [k for k in counts if ".hidden." in k]
    control = [k for k in counts if ".own_hand_control." in k]
    no_hidden_changes = all(counts[k]["changed"] == 0 and counts[k]["checked"] > 0 for k in hidden)
    controls_sensed = all(counts[k]["changed"] > 0 and counts[k]["checked"] > 0 for k in control)
    c2_ok = (len(rows) == s["games_expected"] == 100 and not errors and len(probed) + len(no_choice) == len(rows)
             and s["probe_decisions"] > 0 and no_hidden_changes and controls_sensed)
    unlisted = [r["seed"] for r in no_choice if r["seed"] not in ENDINGS]
    c1_ok = json.loads((iface / "summary.json").read_text(encoding="utf-8"))["c1"]["pass"] is True

    # the other 16 conditions, exactly as readout.py states them
    original = subprocess.run([sys.executable, str(HERE / "readout.py"), *sys.argv[1:]], capture_output=True, text=True).stdout
    # check lines only ("OK    " / "FAIL  "), not readout.py's closing summary line ("FAIL: ..." / "PAIR CHECKS ...")
    others = [line for line in original.splitlines()
              if line.startswith(("OK    ", "FAIL  ")) and "Interface C1+C2 passed" not in line]
    assert len(others) == 16, f"expected readout.py's 16 other checks, found {len(others)}"
    checks = [(f"Interface C1 passed (100 of 100 exact replays)", c1_ok),
              (f"Interface C2 passed under the corrected rule: {len(probed)} games probed, {len(no_choice)} with no decision "
               f"for the probed seat (listed), {len(errors)} errors; hidden invariance on {sum(counts[k]['checked'] for k in hidden if 'legal_moves' in k)} "
               f"decisions, controls sensed", c2_ok and not unlisted)]
    print("Readout under the corrected C2 completeness rule (README.md). The original rule's readout is READOUT.txt.")
    for label, ok in checks:
        print(("OK    " if ok else "FAIL  ") + label)
    for line in others:
        print(line)
    print("Games in which the probed seat had no decision (not failures under the corrected rule):")
    for r in no_choice:
        print(f"  C2 game {r['game_index']}, seed {r['seed']:,}, {r['scenario']}, result {r.get('result')}: "
              f"{ENDINGS.get(r['seed'], 'NOT LISTED: replay it before accepting')}")
    bad = sum(not ok for _, ok in checks) + sum(line.startswith("FAIL") for line in others)
    total = len(checks) + len(others)
    print(f"PAIR CHECKS PASSED UNDER THE CORRECTED RULE ({total} of {total} OK)" if not bad
          else f"FAIL: {bad} of {total} checks failed; the Altaria run stays unread")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

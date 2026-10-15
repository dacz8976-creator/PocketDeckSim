#!/usr/bin/env python3
"""The second half of the old-position route (brief item 6): keep an exported position only where km3 on the CURRENT engine makes the
position's recorded `km3_move` in most of 12 seeds (7 or more; pg_pos "free" run, first action of km3's plan). The others are dropped and
listed with their reason. skip_replay.rs --export writes the positions; pg_pos (rl/results/pause_games_decisions_2026-10-02/harness) is built
on the current engine (the engine tree of the branch, with the pg_label import, as pgd_build.sh builds it).

  skip_positions.py --positions positions.json --manifest manifest.json --pg-pos ./pg_pos --out kept.json --dropped dropped.tsv [--root REPO]
Run from the repository root (the manifest's deck paths are relative to it)."""
import argparse, json, re, subprocess, sys

SEEDS = list(range(1, 13))
NEED = 7


def norm(label):
    """The replay's labels carry an ability's title ("Ability:Volt Charge@2"); pg_pos's do not ("Ability@2")."""
    return re.sub(r"^Ability:.*@(\d+)$", r"Ability@\1", label or "")


def same_move(recorded, made):
    return norm(recorded) == norm(made)


def run_pg_pos(pg_pos, positions, decks, seeds):
    """{id: {"problems": [...], "free": [(seed, first action label), ...]}} from one pg_pos run over the positions."""
    import os, tempfile
    with tempfile.TemporaryDirectory() as t:
        pj = os.path.join(t, "positions.json")
        with open(pj, "w") as f:
            json.dump(positions, f)
        want = sorted({p["deck"] for p in positions} | {p.get("filler", p["deck"]) for p in positions})
        cmd = [pg_pos, "--positions", pj, "--seeds", ",".join(map(str, seeds))]
        for k in want:
            cmd += ["--deck", f"{k}={decks[k]}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
    out = {p["id"]: {"problems": [], "free": [], "error": None} for p in positions}
    if r.returncode != 0:
        for v in out.values():
            v["error"] = f"pg_pos exited {r.returncode}: {r.stderr.strip()[-300:]}"
    for line in r.stdout.splitlines():
        try:
            j = json.loads(line)
        except ValueError:
            continue
        if j.get("id") not in out:
            continue
        if j.get("kind") == "position":
            out[j["id"]]["problems"] = j.get("problems", [])
        elif j.get("kind") == "free":
            out[j["id"]]["free"].append((j["seed"], (j.get("plan") or [None])[0]))
    return out


def check_positions(positions, decks, pg_pos, seeds=SEEDS, need=NEED):
    """(kept, dropped): kept positions carry km3_agree (seeds where km3's first move was the recorded one) and km3_seeds."""
    runs = run_pg_pos(pg_pos, [p for p in positions if p.get("km3_move")], decks, seeds)
    kept, dropped = [], []
    for p in positions:
        if not p.get("km3_move"):
            dropped.append({"id": p["id"], "reason": "no km3_move recorded for this decision"})
            continue
        r = runs[p["id"]]
        if r["error"] or r["problems"]:
            dropped.append({"id": p["id"], "reason": r["error"] or "pg_pos could not build it: " + "; ".join(r["problems"])})
            continue
        agree = sum(same_move(p["km3_move"], m) for _, m in r["free"])
        if len(r["free"]) == len(seeds) and agree >= need:
            kept.append({**p, "km3_agree": agree, "km3_seeds": len(seeds)})
        else:
            dropped.append({"id": p["id"], "reason": f"km3 on the current engine makes the recorded {p['km3_move']} in {agree} of {len(r['free'])} seeds"
                                                  f" (it needs {need} of {len(seeds)}); its moves: {sorted({m or '-' for _, m in r['free']})}"})
    return kept, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--positions", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--pg-pos", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dropped", required=True)
    a = ap.parse_args()
    m = json.load(open(a.manifest))
    decks = {d["name"]: d["path"] for d in m["decks"] + m["opponents"]}
    positions = json.load(open(a.positions))
    kept, dropped = check_positions(positions, decks, a.pg_pos)
    json.dump(kept, open(a.out, "w"), indent=1)
    with open(a.dropped, "w") as f:
        f.write("id\treason\n" + "".join(f"{d['id']}\t{d['reason']}\n" for d in dropped))
    print(f"skip_positions: {len(kept)} kept, {len(dropped)} dropped (of {len(positions)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

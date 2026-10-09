"""split_collect.py: the split-run collector (the cloud, Oct 9; rl/results/split_runs_2026-10-09/README.md).

A registered strength run (a manifest written by strength_prereg.py) can be played in slices: each worker runs
`strength run --manifest M/manifest.json --out <its own folder> --only-deck NAME ...` with the registration's own seeds, and stamps its
folder with `split_collect.py stamp` (the sha256 of the manifest it played and of the program it played with: game records don't carry
them). This script then merges the folders and proves the merge is the registered run:
  - every game the manifest expects (rl/strength/src/main.rs's job list: each deck against each opponent of another name, each deal, each
    seat, the arms ref and X) appears exactly once, with the inputs the manifest gives it: deck, opponent, deal, seat, arm, seed, the
    pilot of each side;
  - every worker played this manifest (byte for byte, by sha256) with the registration's program (the manifest's program_sha256, or, when
    the manifest names none, the same program as every other worker), and only the decks of its own slice;
  - anything else is flagged: a missing game, a duplicate (the same content: kept once; different content: a conflict, neither kept), a
    game with other inputs or not in the registration, an errored game (errors.jsonl), an unreadable line (a run stopped mid-write).
The merged games.jsonl holds each kept game's line exactly as its worker wrote it, in the job list's order. MERGE_RECORD.md says which
worker played what, with which build, and every gap. The exit status is 0 only for a complete, clean merge.

  split_collect.py stamp --manifest M/manifest.json --program PATH --worker NAME --out W [--only-deck NAME]...
  split_collect.py merge --manifest M/manifest.json --worker W1 --worker W2 ... --out OUT
  split_collect.py compare A.jsonl B.jsonl     (game for game, the content without the timing fields; exit 0 when equal)
"""
import argparse, hashlib, json, os, sys

INPUTS = ("deck", "opp", "deal", "seat", "arm", "seed", "pilot_deck", "pilot_opp")
TIMING = ("wall_s", "started_at")   # and moves_*'s total_s and ms, and each log entry's ms: see content()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def expected_jobs(m):
    """The harness's job list (rl/strength/src/main.rs, run()), in its order, with each game's key and inputs."""
    stride = m.get("pair_stride") or 10_000
    jobs = []
    for di, d in enumerate(m["decks"]):
        for oi, o in enumerate(m["opponents"]):
            if o["name"] == d["name"]:
                continue
            for deal in range(m["deals"]):
                for seat in m["seats"]:
                    for arm in ("ref", "X"):
                        jobs.append({"key": f"{d['name']}|{o['name']}|{deal}|{seat}|{arm}", "deck": d["name"], "opp": o["name"],
                                     "deal": deal, "seat": seat, "arm": arm, "seed": m["seed_base"] + (di * 1000 + oi) * stride + deal,
                                     "pilot_deck": m["pilot"] if arm == "X" else m["reference"], "pilot_opp": m["reference"]})
    return jobs


def content(rec):
    """A game record without its timing (wall time, start time, each decision's milliseconds): what a replay must reproduce."""
    out = {k: v for k, v in rec.items() if k not in TIMING}
    for side in ("moves_deck", "moves_opp"):
        if isinstance(out.get(side), dict):
            out[side] = {k: v for k, v in out[side].items() if k not in ("total_s", "ms")}
    for side in ("log", "log_opp"):
        if isinstance(out.get(side), list):
            out[side] = [{k: v for k, v in e.items() if k != "ms"} if isinstance(e, dict) else e for e in out[side]]
    return out


def read_games(path):
    """(line, record) for each line of a games.jsonl, and the lines that don't parse (with their line numbers)."""
    games, bad = [], []
    if not os.path.isfile(path):
        return games, bad
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f.read().splitlines(), 1):
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                if not isinstance(rec, dict) or "key" not in rec:
                    raise ValueError("no key")
                games.append((line, rec))
            except ValueError:
                bad.append((n, line[:80]))
    return games, bad


def collect(manifest_path, worker_dirs):
    with open(manifest_path, encoding="utf-8") as f:
        m = json.load(f)
    msha = sha256_file(manifest_path)
    jobs = expected_jobs(m)
    by_key = {j["key"]: j for j in jobs}
    problems, workers, seen = [], [], {}   # seen: key -> [(worker, line, record)]
    programs = {}
    for wdir in worker_dirs:
        name = os.path.basename(os.path.normpath(wdir))
        stamp_path = os.path.join(wdir, "worker.json")
        stamp = None
        if os.path.isfile(stamp_path):
            with open(stamp_path, encoding="utf-8") as f:
                stamp = json.load(f)
            name = stamp.get("worker") or name
        else:
            problems.append({"kind": "stamp", "worker": name, "key": None, "detail": "no worker.json: which manifest and program it played is not recorded"})
        if stamp:
            if stamp.get("manifest_sha256") != msha:
                problems.append({"kind": "manifest", "worker": name, "key": None,
                                 "detail": f"played manifest sha256 {str(stamp.get('manifest_sha256'))[:12]}, not this one ({msha[:12]})"})
            psha = stamp.get("program_sha256")
            programs[name] = psha
            if m.get("program_sha256") and psha != m["program_sha256"]:
                problems.append({"kind": "program", "worker": name, "key": None,
                                 "detail": f"program sha256 {str(psha)[:12]}, not the registration's {m['program_sha256'][:12]}"})
        games, bad = read_games(os.path.join(wdir, "games.jsonl"))
        for n, text in bad:
            problems.append({"kind": "unreadable", "worker": name, "key": None, "detail": f"games.jsonl line {n} does not parse: {text!r}"})
        errs, _ = read_games(os.path.join(wdir, "errors.jsonl"))
        for _, e in errs:
            problems.append({"kind": "error", "worker": name, "key": e["key"], "detail": f"the harness recorded an error: {str(e.get('error'))[:200]}"})
        slice_ = set(stamp.get("only_deck") or []) if stamp else set()
        played = 0
        for line, rec in games:
            key = rec["key"]
            job = by_key.get(key)
            if job is None:
                problems.append({"kind": "unexpected", "worker": name, "key": key, "detail": "not a game of this registration"})
                continue
            wrong = [f"{k} {rec.get(k)!r}, not {job[k]!r}" for k in INPUTS if rec.get(k) != job[k]]
            if wrong:
                problems.append({"kind": "mismatch", "worker": name, "key": key, "detail": "; ".join(wrong)})
                continue
            if slice_ and job["deck"] not in slice_:
                problems.append({"kind": "outside slice", "worker": name, "key": key, "detail": f"deck {job['deck']} is not in its slice {sorted(slice_)}"})
            seen.setdefault(key, []).append((name, line, rec))
            played += 1
        workers.append({"worker": name, "dir": os.path.abspath(wdir), "games": played, "slice": sorted(slice_),
                        "program_sha256": stamp.get("program_sha256") if stamp else None,
                        "manifest_sha256": stamp.get("manifest_sha256") if stamp else None,
                        "engine_tree": stamp.get("engine_tree") if stamp else None})
    if not m.get("program_sha256") and len(set(programs.values())) > 1:
        problems.append({"kind": "program", "worker": None, "key": None,
                         "detail": "the manifest names no program and the workers played different ones: "
                                   + ", ".join(f"{w} {str(p)[:12]}" for w, p in sorted(programs.items()))})
    lines = []
    for job in jobs:
        copies = seen.get(job["key"], [])
        if not copies:
            problems.append({"kind": "missing", "worker": None, "key": job["key"], "detail": "no worker played it"})
            continue
        if len(copies) > 1:
            same = all(content(c[2]) == content(copies[0][2]) for c in copies[1:])
            who = ", ".join(c[0] for c in copies)
            if not same:
                problems.append({"kind": "conflict", "worker": None, "key": job["key"], "detail": f"{len(copies)} copies ({who}) with different content: none kept"})
                continue
            problems.append({"kind": "duplicate", "worker": None, "key": job["key"], "detail": f"{len(copies)} copies ({who}), the same content: the first kept"})
        lines.append(copies[0][1])
    return {"manifest": m, "manifest_sha256": msha, "manifest_path": os.path.abspath(manifest_path), "expected": len(jobs), "lines": lines,
            "workers": workers, "problems": problems, "complete": not problems and len(lines) == len(jobs)}


def merge_record(res):
    m = res["manifest"]
    out = [f"# Merge record: {m.get('name')}", "",
           f"**{'COMPLETE' if res['complete'] else 'INCOMPLETE'}**: {len(res['lines'])} of {res['expected']} expected games merged; "
           f"{len(res['problems'])} problem(s).", "",
           f"- Manifest: `{res['manifest_path']}`, sha256 `{res['manifest_sha256']}`.",
           f"- Registered program sha256: `{m.get('program_sha256')}`; engine: {m.get('engine')}; repo commit: {m.get('repo_commit')}.",
           f"- Pilot {m.get('pilot')} against reference {m.get('reference')}; seed base {m.get('seed_base')}, pair stride {m.get('pair_stride') or 10000}.",
           "- The merged games.jsonl holds each kept game's line as its worker wrote it, in the harness's job order.", "",
           "| Worker | Slice (--only-deck) | Games | Program sha256 | Manifest sha256 | Engine tree |", "|---|---|---:|---|---|---|"]
    for w in res["workers"]:
        out.append(f"| {w['worker']} | {', '.join(w['slice']) or '(all)'} | {w['games']} | `{w['program_sha256']}` | `{w['manifest_sha256']}` | {w['engine_tree']} |")
    out += ["", "## Problems", ""]
    if not res["problems"]:
        out.append("None: every expected game appears exactly once, with its registered inputs, from a worker on this manifest and program.")
    for p in res["problems"]:
        where = " ".join(x for x in (f"worker {p['worker']}" if p.get("worker") else "", f"game `{p['key']}`" if p.get("key") else "") if x)
        out.append(f"- **{p['kind']}** {where}: {p['detail']}")
    return "\n".join(out) + "\n"


def main(argv):
    if not argv:
        print("usage:\n" + "\n".join(__doc__.strip().splitlines()[-3:]), file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "stamp":
        ap = argparse.ArgumentParser(prog="split_collect.py stamp")
        ap.add_argument("--manifest", required=True)
        ap.add_argument("--program", required=True)
        ap.add_argument("--worker", required=True)
        ap.add_argument("--out", required=True)
        ap.add_argument("--only-deck", action="append", default=[])
        a = ap.parse_args(rest)
        with open(a.manifest, encoding="utf-8") as f:
            m = json.load(f)
        names = {d["name"] for d in m["decks"]}
        unknown = [d for d in a.only_deck if d not in names]
        if unknown:
            print(f"stamp: not decks of this registration: {unknown} (its decks: {sorted(names)})", file=sys.stderr)
            return 2
        record = a.program + ".build.json"
        tree = None
        if os.path.isfile(record):
            with open(record, encoding="utf-8") as f:
                tree = json.load(f).get("engine_tree_archived")
        os.makedirs(a.out, exist_ok=True)
        stamp = {"worker": a.worker, "manifest_sha256": sha256_file(a.manifest), "program_sha256": sha256_file(a.program),
                 "only_deck": a.only_deck, "engine_tree": tree, "manifest": os.path.abspath(a.manifest), "program": os.path.abspath(a.program)}
        with open(os.path.join(a.out, "worker.json"), "w", encoding="utf-8") as f:
            json.dump(stamp, f, indent=1)
            f.write("\n")
        print(f"stamped {a.out}: manifest {stamp['manifest_sha256'][:12]}, program {stamp['program_sha256'][:12]}, slice {a.only_deck or '(all)'}")
        return 0
    if cmd == "merge":
        ap = argparse.ArgumentParser(prog="split_collect.py merge")
        ap.add_argument("--manifest", required=True)
        ap.add_argument("--worker", action="append", required=True)
        ap.add_argument("--out", required=True)
        a = ap.parse_args(rest)
        res = collect(a.manifest, a.worker)
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "games.jsonl"), "w", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in res["lines"])
        with open(os.path.join(a.out, "MERGE_RECORD.md"), "w", encoding="utf-8") as f:
            f.write(merge_record(res))
        print(f"{'COMPLETE' if res['complete'] else 'INCOMPLETE'}: {len(res['lines'])} of {res['expected']} games; {len(res['problems'])} problem(s); see {a.out}/MERGE_RECORD.md")
        return 0 if res["complete"] else 1
    if cmd == "compare":
        if len(rest) != 2:
            print("usage: split_collect.py compare A.jsonl B.jsonl", file=sys.stderr)
            return 2
        (ga, bad_a), (gb, bad_b) = read_games(rest[0]), read_games(rest[1])
        diffs = [f"line {i + 1}: {ra[1]['key']} v {rb[1]['key']}" for i, (ra, rb) in enumerate(zip(ga, gb)) if content(ra[1]) != content(rb[1])]
        ok = not diffs and not bad_a and not bad_b and len(ga) == len(gb)
        print(f"{len(ga)} and {len(gb)} games; game for game (content, not timing) {'EQUAL' if ok else 'DIFFERENT'}"
              + (f"; {len(diffs)} differ: {diffs[:10]}" if diffs else "") + (f"; unreadable lines {len(bad_a)}, {len(bad_b)}" if bad_a or bad_b else ""))
        return 0 if ok else 1
    print(f"unknown command {cmd!r}; usage:\n" + "\n".join(__doc__.strip().splitlines()[-3:]), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

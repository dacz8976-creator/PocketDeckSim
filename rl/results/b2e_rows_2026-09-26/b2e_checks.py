#!/usr/bin/env python3
"""Mechanical checks for the B2e rows (no games are played here). Called by run_b2e_identity.sh and
run_b2e_rows.sh; read_b2e.py imports check_rows() and re-runs it before reading anything.

    b2e_checks.py subset <out|-> <bot> <pairings> <games> <jsonl> [<jsonl> ...]
        Collect the games of the listed pairings with deal i < games from the given per-game files, check that
        there is exactly one per (pairing, i), all of them, and that both sides were piloted by <bot>. Writes
        them to <out> (one line per game, as read) unless <out> is "-". Exit 1 on any problem.

    b2e_checks.py same [--drop k1,k2] <new jsonl> <reference jsonl>
        Stricter than compare.py, which looks at nine fields only: both files must hold the same (pairing, i) set,
        once each and not empty, and every new line must equal its reference line BYTE FOR BYTE (so hyper_ray,
        chase_order and the absence of any added key are checked too). With --drop, the listed keys must be present
        in every new line and are removed first; the rest must then equal the reference line exactly (both
        re-serialized the same way, types included). Exit 1 on any difference. A difference is printed with the
        keys that differ (on one side only, or with different values), per line and counted over all lines.

    b2e_checks.py table_tsv <reference jsonl> <seed base> <out tsv>
        Writes a --pairs file that replays the table pairings found in <reference jsonl> (a legality_scan
        --games-out file): held_key = a, held_file = decks/research/<a>.txt, opponent = b,
        panel_file = decks/research/<b>.txt, seed_first = base + 10,000 x pairing. Run with --seed-base <base> =
        72,000,000, --pairs mode must then replay the table's own games (run_b2e_identity.sh).

    b2e_checks.py rows <pairings.tsv> <seed base> <games> <k3 arch> <k3 dustin> <kp3 arch> <kp3 dustin>
        The B2e rows, in section 4's four block files (b2e_<pilot>_arch.jsonl: block A_archetype, pairings 0-47;
        b2e_<pilot>_dustin.jsonl: block B_dustin, 48-95). Each block file holds exactly one game per (pairing, i)
        for every TSV row of its block and i < games, and nothing else; so each pilot's two files hold every TSV
        row. Every line has every field the specification names (pairing, a, b, i, seed, bot_a, bot_b,
        first_seat, winner_seat, points, turns, first_deck_score, moves as 16 hex digits, a_file, b_file), seed =
        seed_first + i = base + 10,000 x pairing + i, first_seat = i % 2 (even i = held deck in seat 0),
        a/b/a_file/b_file as the TSV row, bot_a = bot_b = the pilot, first_deck_score consistent with
        winner_seat; a game with findings also names one example per finding code (finding_examples, same codes),
        a game without has neither key; k3 and kp3 on the same deals; each file's per-game findings summed equal
        its own .txt log's findings section (the log is the jsonl's name with .txt). Prints findings per pairing,
        each code with its first example in that pairing, and a last line "ROWS PASS ..." or "ROWS FAIL ...".
        Exit 1 on FAIL. RULE findings do not fail the check (they stop the reading of that pairing; read_b2e.py
        withholds it) but are listed.
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict

PILOTS = ("k3", "kp3")
# Section 4's block files: file name part -> the TSV's block column.
BLOCKS = {"arch": "A_archetype", "dustin": "B_dustin"}
# Every per-game line must carry these (README section 4: today's fields; a_file/b_file identify the --pairs row).
FIELDS = ("pairing", "a", "b", "i", "seed", "bot_a", "bot_b", "first_seat", "winner_seat", "points", "turns",
          "first_deck_score", "moves", "a_file", "b_file")
MOVES = re.compile(r"[0-9a-f]{16}")


def load_games(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError as e:
                    raise SystemExit(f"{path} line {n}: not JSON ({e})")
    return out


def load_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    by_p = {}
    for r in rows:
        p = int(r["pairing"])
        if p in by_p:
            raise SystemExit(f"{path}: pairing {p} listed twice")
        by_p[p] = r
    return by_p


def subset(out, bot, pairings, games, paths):
    want = {int(p) for p in pairings.split(",")}
    kept, problems = {}, []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                g = json.loads(line)
                if g["pairing"] in want and g["i"] < games:
                    key = (g["pairing"], g["i"])
                    if key in kept:
                        problems.append(f"pairing {key[0]} deal {key[1]} appears twice")
                    kept[key] = line.rstrip("\r\n") + "\n"
                    if g.get("bot_a") != bot or g.get("bot_b") != bot:
                        problems.append(f"pairing {key[0]} deal {key[1]}: bots {g.get('bot_a')}/{g.get('bot_b')}, not {bot}")
    missing = [(p, i) for p in sorted(want) for i in range(games) if (p, i) not in kept]
    if missing:
        problems.append(f"{len(missing)} games missing, first {missing[:3]}")
    if out != "-":
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            for key in sorted(kept):
                f.write(kept[key])
    print(f"subset of {', '.join(paths)}: {len(kept):,} games (pairings {sorted(want)}, deals < {games}, bot {bot}); "
          f"problems: {len(problems)}")
    for p in problems[:5]:
        print("  ", p)
    return not problems


def _raw_games(path):
    """{(pairing, i): (raw line bytes without the newline, parsed)} and the keys seen more than once."""
    out, dups = {}, []
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.rstrip(b"\r\n")
            if not raw.strip():
                continue
            g = json.loads(raw)
            key = (g["pairing"], g["i"])
            if key in out:
                dups.append(key)
            out[key] = (raw, g)
    return out, dups


def _canon(g):
    return json.dumps(g, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _differing_keys(new, ref):
    """The keys on one side only and the keys whose values differ (types included), as one sorted list."""
    return sorted([f"{k} (new only)" for k in set(new) - set(ref)] + [f"{k} (reference only)" for k in set(ref) - set(new)]
                  + [k for k in set(new) & set(ref) if _canon(new[k]) != _canon(ref[k])])


def same(new_path, ref_path, drop=()):
    new, dn = _raw_games(new_path)
    ref, dr = _raw_games(ref_path)
    problems = []
    if not new or not ref:
        problems.append(f"empty: new {len(new)} games, reference {len(ref)} games")
    if dn or dr:
        problems.append(f"repeated (pairing, i): new {dn[:3]}, reference {dr[:3]}")
    only_new, only_ref = sorted(set(new) - set(ref)), sorted(set(ref) - set(new))
    if only_new or only_ref:
        problems.append(f"only in new {len(only_new)} {only_new[:3]}; only in reference {len(only_ref)} {only_ref[:3]}")
    bad = []
    keys_differing = Counter()
    for k in sorted(set(new) & set(ref)):
        g = new[k][1]
        if drop:
            missing = [x for x in drop if x not in g]
            if missing:
                bad.append((k, f"no {missing} in the new line"))
                continue
            g = {x: v for x, v in g.items() if x not in drop}
            if _canon(g) == _canon(ref[k][1]):
                continue
        elif new[k][0] == ref[k][0]:
            continue
        keys = _differing_keys(g, ref[k][1]) or ["(same keys and values; the bytes differ: key order or number format)"]
        keys_differing.update(keys)
        bad.append((k, "differs in " + ", ".join(keys)))
    if bad:
        problems.append(f"{len(bad)} lines differ; keys differing (lines): "
                        + (", ".join(f"{x} ({n})" for x, n in sorted(keys_differing.items())) or "none (missing keys)"))
    how = f"without {','.join(drop)}, types included" if drop else "byte for byte"
    print(f"same lines ({how}): {new_path} v {ref_path}: {len(set(new) & set(ref)) - len(bad):,} of "
          f"{len(set(new) | set(ref)):,} games identical; problems: {len(problems)}")
    for p in problems[:5]:
        print("  ", p)
    for k, why in bad[:3]:
        print(f"   pairing {k[0]} deal {k[1]}: {why}")
        print(f"     new: {new[k][0][:400].decode('utf-8', 'replace')}")
        print(f"     ref: {ref[k][0][:400].decode('utf-8', 'replace')}")
    return not problems


def table_tsv(ref_path, base, out):
    names = {}
    with open(ref_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                g = json.loads(line)
                if names.setdefault(g["pairing"], (g["a"], g["b"])) != (g["a"], g["b"]):
                    raise SystemExit(f"{ref_path}: pairing {g['pairing']} names two different deck pairs")
    if not names:
        raise SystemExit(f"{ref_path}: no games")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("pairing\tblock\theld_key\theld_file\topponent\tpanel_file\tseed_first\n")
        for p in sorted(names):
            a, b = names[p]
            f.write(f"{p}\ttable\t{a}\tdecks/research/{a}.txt\t{b}\tdecks/research/{b}.txt\t{base + 10_000 * p}\n")
    print(f"table_tsv: {out}: pairings {sorted(names)} from {ref_path}, seed_first = {base:,} + 10,000 x pairing")
    return True


def log_findings(path):
    """The '(occurrences / games affected)' section of a legality_scan log: {code: (occurrences, games)}."""
    out, inside = {}, False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("Findings (occurrences / games affected):"):
                inside = True
                continue
            if not inside or not line.strip() or line.startswith("      e.g."):
                continue
            s = line.strip()
            if s == "none":
                continue
            code, counts = s.rsplit(": ", 1)
            occ, games = (int(x) for x in counts.split(" / "))
            out[code] = (occ, games)
    if not inside:
        raise ValueError(f"{path}: no findings section (did the scan finish?)")
    return out


def check_rows(tsv_path, base, games, files, out=print):
    """files: {pilot: {"arch": jsonl path, "dustin": jsonl path}}, section 4's four block files. Returns
    (ok, findings, examples): findings[pilot][pairing] = Counter of code -> games affected;
    examples[pilot][pairing][code] = (deal i, seed, the scan's example text), from the pairing's lowest deal
    with that code."""
    rows = load_tsv(tsv_path)
    problems = []
    if not rows:
        problems.append(f"{tsv_path} lists no pairings")
    keysets, findings, examples = {}, {}, {}
    for pilot, blocks in files.items():
        seen = {}
        per_pairing = defaultdict(Counter)
        first = defaultdict(dict)
        pilot_bad = []
        if set(blocks) != set(BLOCKS):
            pilot_bad.append(f"block files {sorted(blocks)}, want {sorted(BLOCKS)}")
        for block, path in blocks.items():
            block_rows = {p for p, r in rows.items() if r.get("block") == BLOCKS.get(block)}
            if not block_rows:
                pilot_bad.append(f"{block}: the TSV has no pairings of block {BLOCKS.get(block)}")
            bad = []
            try:
                gs = load_games(path)
            except OSError as e:
                gs = []
                bad.append(f"cannot read: {e}")
            in_file = set()
            occ_total, games_total = Counter(), Counter()
            for g in gs:
                key = (g.get("pairing"), g.get("i"))
                absent = [x for x in FIELDS if x not in g]
                if absent:
                    bad.append(f"pairing {key[0]} deal {key[1]}: no {', '.join(absent)}")
                    continue
                if not (isinstance(g["moves"], str) and MOVES.fullmatch(g["moves"])):
                    bad.append(f"pairing {key[0]} deal {key[1]}: moves {g['moves']!r} is not a 16-hex-digit hash")
                if key in seen:
                    bad.append(f"pairing {key[0]} deal {key[1]} twice")
                    continue
                seen[key] = g["seed"]
                in_file.add(key)
                r = rows.get(g.get("pairing"))
                if r is None:
                    bad.append(f"pairing {key[0]} not in the TSV")
                    continue
                p, i = key
                if p not in block_rows:
                    bad.append(f"pairing {p} is block {r.get('block')}, not {BLOCKS.get(block)}")
                if not (isinstance(i, int) and 0 <= i < games):
                    bad.append(f"pairing {p}: deal {i!r} outside 0..{games - 1}")
                    continue
                want_seed = int(r["seed_first"]) + i
                if g["seed"] != want_seed or g["seed"] != base + 10_000 * p + i or g["seed"] > int(r["seed_last"]):
                    bad.append(f"pairing {p} deal {i}: seed {g['seed']}, want {want_seed}")
                if g["first_seat"] != i % 2:
                    bad.append(f"pairing {p} deal {i}: first_seat {g['first_seat']}")
                for field, want in (("a", r["held_key"]), ("b", r["opponent"]), ("a_file", r["held_file"]),
                                    ("b_file", r["panel_file"]), ("bot_a", pilot), ("bot_b", pilot)):
                    if g.get(field) != want:
                        bad.append(f"pairing {p} deal {i}: {field} {g.get(field)!r}, want {want!r}")
                w = g["winner_seat"]
                want_score = 0.5 if w == -1 else (1.0 if w == g["first_seat"] else 0.0)
                if w not in (-1, 0, 1) or g["first_deck_score"] != want_score:
                    bad.append(f"pairing {p} deal {i}: winner_seat {w}, first_deck_score {g['first_deck_score']}")
                fs, fx = g.get("findings"), g.get("finding_examples")
                if fs is None:
                    if fx is not None:
                        bad.append(f"pairing {p} deal {i}: finding_examples without findings")
                    continue
                if not (isinstance(fs, dict) and fs and all(isinstance(n, int) and n > 0 for n in fs.values())):
                    bad.append(f"pairing {p} deal {i}: findings {fs!r} is not code -> count")
                    continue
                if not (isinstance(fx, dict) and set(fx) == set(fs) and all(isinstance(x, str) and x for x in fx.values())):
                    bad.append(f"pairing {p} deal {i}: finding_examples does not give one example per finding code")
                    fx = {}
                for code, n in fs.items():
                    per_pairing[p][code] += 1
                    occ_total[code] += n
                    games_total[code] += 1
                    if code in fx and (code not in first[p] or i < first[p][code][0]):
                        first[p][code] = (i, g["seed"], fx[code])
            expected = len(block_rows) * games
            if len(in_file) != expected or len(gs) != expected:
                bad.append(f"{len(gs):,} lines, {len(in_file):,} distinct games; want {expected:,} "
                           f"({len(block_rows)} pairings of block {BLOCKS.get(block)} x {games})")
            missing = [(p, i) for p in sorted(block_rows) for i in range(games) if (p, i) not in in_file]
            if missing:
                bad.append(f"{len(missing):,} (pairing, deal) of the block missing, first {missing[:3]}")
            # The file's own log: its findings section must be exactly these games' findings, summed.
            log = path[:-len(".jsonl")] + ".txt" if path.endswith(".jsonl") else None
            try:
                logged = log_findings(log) if log else None
            except (OSError, ValueError) as e:
                logged = None
                bad.append(f"log: {e}")
            if logged is not None:
                summed = {c: (occ_total[c], games_total[c]) for c in occ_total}
                if summed != logged:
                    bad.append(f"per-game findings {summed} differ from the log's {logged}")
            out(f"{pilot} {block}: {path}: {len(gs):,} lines, {len(in_file):,} distinct games; problems {len(bad)}")
            for b in bad[:8]:
                out(f"   {b}")
            pilot_bad += [f"{block}: {b}" for b in bad]
        missing = [(p, i) for p in rows for i in range(games) if (p, i) not in seen]
        if missing:
            pilot_bad.append(f"its files together miss {len(missing):,} (pairing, deal), first {missing[:3]}")
            out(f"{pilot}: its files together miss {len(missing):,} (pairing, deal) of the TSV's {len(rows)} x {games}")
        problems += [f"{pilot} {b}" for b in pilot_bad]
        keysets[pilot] = seen
        findings[pilot] = per_pairing
        examples[pilot] = first
    if len(keysets) == 2:
        a, b = (keysets[p] for p in PILOTS if p in keysets)
        if a != b:
            problems.append("k3 and kp3 are not on the same (pairing, deal, seed) set")
            out("   k3 and kp3 are not on the same (pairing, deal, seed) set")
        else:
            out(f"k3 and kp3 on the same {len(a):,} deals (pairing, i, seed)")

    def listed(pilot, p, kind, c):
        return "; ".join(f"{k}: {n} games (e.g. deal {examples[pilot][p][k][0]}: {examples[pilot][p][k][2][:200]})"
                         if k in examples[pilot][p] else f"{k}: {n} games (no example)"
                         for k, n in sorted(c.items()) if k.startswith(kind))

    for pilot in files:
        rule = {p: c for p, c in findings[pilot].items() if any(k.startswith("RULE") for k in c)}
        check = {p: c for p, c in findings[pilot].items() if any(k.startswith("CHECK") for k in c)}
        out(f"{pilot} RULE findings: " + ("none" if not rule else f"in {len(rule)} pairings (reading withheld there)"))
        for p in sorted(rule):
            out(f"   pairing {p} ({rows[p]['held_key']} v {rows[p]['opponent']}): " + listed(pilot, p, "RULE", rule[p]))
        out(f"{pilot} CHECK findings: " + ("none" if not check else f"in {len(check)} pairings"))
        for p in sorted(check):
            out(f"   pairing {p} ({rows[p]['held_key']} v {rows[p]['opponent']}): " + listed(pilot, p, "CHECK", check[p]))
    ok = not problems
    n_rule = sum(1 for pilot in files for c in findings[pilot].values() if any(k.startswith("RULE") for k in c))
    if ok:
        names = ", ".join(path for blocks in files.values() for path in blocks.values())
        out(f"ROWS PASS: {names}: each pilot's two block files hold its {len(rows)} pairings x {games} deals as "
            f"{tsv_path} (seeds, seats, decks, pilots, blocks); RULE findings in {n_rule} pilot-pairings")
    else:
        out(f"ROWS FAIL: {len(problems)} problems, first: {problems[0]}")
    return ok, findings, examples


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    cmd = sys.argv[1]
    if cmd == "subset" and len(sys.argv) >= 7:
        out, bot, pairings, games = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
        sys.exit(0 if subset(out, bot, pairings, games, sys.argv[6:]) else 1)
    if cmd == "same" and len(sys.argv) in (4, 6):
        drop = ()
        if len(sys.argv) == 6:
            if sys.argv[2] != "--drop":
                raise SystemExit(__doc__)
            drop = tuple(x for x in sys.argv[3].split(",") if x)
        sys.exit(0 if same(sys.argv[-2], sys.argv[-1], drop) else 1)
    if cmd == "table_tsv" and len(sys.argv) == 5:
        sys.exit(0 if table_tsv(sys.argv[2], int(sys.argv[3]), sys.argv[4]) else 1)
    if cmd == "rows" and len(sys.argv) == 9:
        tsv, base, games = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        files = {"k3": {"arch": sys.argv[5], "dustin": sys.argv[6]}, "kp3": {"arch": sys.argv[7], "dustin": sys.argv[8]}}
        ok, _, _ = check_rows(tsv, base, games, files)
        sys.exit(0 if ok else 1)
    raise SystemExit(__doc__)


if __name__ == "__main__":
    main()

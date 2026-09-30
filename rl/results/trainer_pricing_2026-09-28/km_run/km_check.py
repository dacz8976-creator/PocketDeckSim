#!/usr/bin/env python3
"""The checks run_km.sh makes on its own files (km's registration, ../REGISTRATION_DRAFT.md, read with Amendment 1
(Sept 30): km re-issued on kta; modelled on ../../kta_2026-09-29/kta_check.py). Each prints one line (or a file) and
exits 0 when the check passes, 1 when it fails, 2 on a malformed input. None of them reads a result: they compare
seeds, seats, decks, bots, move fingerprints and (for identity) whole game rows, never a winner, a score or a count.
The reference files, their sha256 and the build come from km_config.json (km_config.py), the one set the runner and
the reader use (Amendment 1 (b) item 3).

  refs --config C --root R [--committed] [--groups g1,g2,...]
        every reference file the config names (kta3's ec7e1a8 both-sides files): its sha256 is the config's; it holds
        exactly the group's pairings x deals i < N, once each, every game kta3 on both sides, on seed seed_base +
        pairing x 10,000 + i, first_seat i % 2, between the pairs file's decks (or legality_scan's NAMES pair); with
        --committed, tracked by git and unchanged from HEAD (Amendment 1 (b) item 3: "Every reference file is committed
        on main").

  complete FILE --pairings L --games N --seed-base B --bot-a X --bot-b Y (--pairs TSV | --decks)
        legality_scan's output holds exactly the deals (pairing, i < N) of those pairings, once each, and every game is
        the one that run plays: seed B + pairing x 10,000 + i, first_seat i % 2, bots X and Y, decks from the pairs
        file's row (a = held_key, b = opponent, a_file = held_file, b_file = panel_file) or legality_scan's NAMES pair.
  same MINE REF --max-i N --expect C --label L [--fields all|id]
        identity: MINE's games equal REF's games with i < N on the pairings MINE holds, deal for deal; "all" compares
        the whole row (the same program version writes the same fields), "id" the identity fields (moves, decisions,
        openings, winner_seat, points, seed, first_seat, which every reference row must carry, and a_file, b_file where
        the reference carries them); exactly C such games.
  rules PAGE
        the scan page's Findings list no RULE finding.
  rows-complete FILE --cells SPEC --first-deal F --games N --bot X (--counts | --no-counts) --root R [--decks-arg D]
        the counter tool's rows (--rows-out) hold exactly the cells SPEC names ("km17", or the tool's --pairings list,
        e.g. table:2,new_decks.tsv:8), in the tool's cell order, deals F .. F+N-1 in order, and every row is the game
        its deal names: seed, seats, decks and deck files, both seats played by X, and counts present or absent.
  rows-v-games ROWS --from A --to Z --table GAMES [--new17 GAMES] --label L [--cells N]
        registration step 3: a measuring run's rows against a pilot's own game files, deal by deal for i = A .. Z: the
        move fingerprint, both decks (names, and files where the game file has them), the seed and the seats. No
        count is read. --new17 is needed only when the rows hold new_decks.tsv cells; --cells N asserts that the rows
        hold exactly N cells (Amendment 1 (e) item 3: "with the cell counts asserted (17, and 2)").
  d-pairs --out F --base B --deals N
        clause (d)'s block (step 4 (d); D2): nine rows, Lucario first-named (in seat 0 on even j), rows 0-6 the table
        cells 2, 8, 13, 18, 19, 20, 21 in that order, row 7 Rayquaza v Lucario, row 8 Altaria/Greninja v Lucario,
        each row with its cell's own deck files; seed_first = B + row x 10,000.
  pairings-of TSV [--side a|b] [--only L]
        a pairs file's pairing numbers (comma-separated), optionally only its variant_side rows / only those in L.
  inputs --part I|T|R --root R --build B --here H --out O --config C
        the files a part's games and checks read besides the pinned programs, one per line (relative to R when inside
        it), sorted: the config itself among them. run_km.sh records their sha256 at the part's first start and checks
        them at every step.
  commit-order --root R --amendment C --registration REG --paths P1 [P2 ...] [--with-or-before Q1 [Q2 ...]]
        section 4.0 steps 6-8, in that order: each path's first commit in HEAD's history (the commit that added it)
        strictly before the next path's, and the last strictly before the amendment C (a different commit, and its
        ancestor); C is a commit in HEAD's history that changes REG. Each Q (the sample's raw rows files: step 7 computes
        the independent check "from those committed raw files") is first committed at P1's first commit or before it.
        Reads git only.
  one-list tree --config C --root R
        Amendment 1 (b) item 4, "the deck lists from B's tree": every pairs file the runs read and every deck list those
        files and clause (d) name, and decks/research's lists, byte for byte equal in the working tree and in B's tree.
  one-list write --config C --root R --build B --out O --programs P --dest F
        km's one list (Amendment 1 (b) item 4), written to F (the runner writes <O>/km_inputs.sha256.part and moves it):
        "# set" lines naming the set (the candidate, the baseline, B in full, the build folder, the counter tool's
        source sha256, the eight reference files and the cloud's outputs as the config names them, the three programs
        as programs.txt records them), then sha256sum lines (paths relative to R when inside it, checked from R) for the
        config, the eight reference files, the cloud's outputs as extracted into <B>/ref, the build's tool source and
        decks/research, every pairs file and deck list the runs read (see `tree`), and the three programs.
  one-list check --config C --root R --out O [--build B] [--programs P]
        the list in O against everything: STATUS.txt's last "KM INPUTS (WRITTEN|CHANGED) <S> <time> km_inputs.sha256
        <sha256>" line gives its sha256 (it changes only by a dated STATUS.txt line); its set lines equal the config's
        values; its files are exactly the ones `write` lists for this config and build, each with its sha256 on the
        disk; the config's own entry is the config loaded; with --programs, programs.txt names exactly its programs.
"""
import argparse, glob, hashlib, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import km_config  # noqa: E402  (the one set: build, baseline, reference files, program pins)

NAMES =["altaria", "blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]  # legality_scan's
TABLE28 = [(x, y) for k, x in enumerate(NAMES) for y in NAMES[k + 1:]]   # --decks: pairing p is the p-th (a, b), a < b
ID_FIELDS = ("moves", "decisions", "openings", "winner_seat", "points", "seed", "first_seat", "a_file", "b_file")
CORE_ID_FIELDS = ID_FIELDS[:7]   # Amendment 1 (c) item 4: "moves, decisions, openings, winner, points, seed and seats"
NEW_DECKS_TSV = "rl/results/gauntlet_runs_2026-09-26/tsv/new_decks.tsv"
BASES = {"table": 72_000_000, "new_decks.tsv": 21_108_000_000}
# The counter tool's km17 cells, in its order (tool_census.rs, KM17_TABLE then KM17_NEW; registration step 3).
KM17 = [("table", 0, "altaria", "blaziken"), ("table", 1, "altaria", "hydreigon"), ("table", 2, "altaria", "lucario"),
        ("table", 3, "altaria", "sceptile"), ("table", 4, "altaria", "suicune"), ("table", 5, "altaria", "vespiquen"),
        ("table", 6, "altaria", "weezing"), ("table", 8, "blaziken", "lucario"), ("table", 13, "hydreigon", "lucario"),
        ("table", 18, "lucario", "sceptile"), ("table", 19, "lucario", "suicune"), ("table", 20, "lucario", "vespiquen"),
        ("table", 21, "lucario", "weezing"), ("new_decks.tsv", 8, "rayquaza", "lucario"),
        ("new_decks.tsv", 9, "rayquaza", "altaria"), ("new_decks.tsv", 16, "altaria_greninja", "lucario"),
        ("new_decks.tsv", 17, "altaria_greninja", "altaria")]
HEADER = ["pairing", "block", "held_key", "held_file", "opponent", "panel_file", "seed_first", "seed_last", "sub_block_end"]
# Clause (d)'s nine rows (step 4 (d)): (row, Lucario's file, opponent, opponent's file, the cell the row is).
D_ROWS = [(0, "decks/research/lucario.txt", "altaria", "decks/research/altaria.txt", "table 2"),
          (1, "decks/research/lucario.txt", "blaziken", "decks/research/blaziken.txt", "table 8"),
          (2, "decks/research/lucario.txt", "hydreigon", "decks/research/hydreigon.txt", "table 13"),
          (3, "decks/research/lucario.txt", "sceptile", "decks/research/sceptile.txt", "table 18"),
          (4, "decks/research/lucario.txt", "suicune", "decks/research/suicune.txt", "table 19"),
          (5, "decks/research/lucario.txt", "vespiquen", "decks/research/vespiquen.txt", "table 20"),
          (6, "decks/research/lucario.txt", "weezing", "decks/research/weezing.txt", "table 21"),
          (7, "decks/screen/opponents/t-lucario.txt", "rayquaza", "decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt",
           "new_decks.tsv 8"),
          (8, "decks/screen/opponents/t-lucario.txt", "altaria_greninja", "decks/gauntlet_2026-09-26/g-mega_altaria_greninja.txt",
           "new_decks.tsv 16")]


def rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def tsv(path):
    """A --pairs file's rows as dicts (read as legality_scan reads it: BOM dropped, fields trimmed)."""
    with open(path, encoding="utf-8-sig") as f:
        lines = [ln.rstrip("\r\n") for ln in f if ln.strip()]
    header = [h.strip() for h in lines[0].split("\t")]
    return [dict(zip(header, (x.strip() for x in ln.split("\t")))) for ln in lines[1:]]


def complete(a):
    want = {(p, i) for p in (int(x) for x in a.pairings.split(",") if x != "") for i in range(a.games)}
    if a.pairs:
        decks = {int(r["pairing"]): {"a": r["held_key"], "b": r["opponent"], "a_file": r["held_file"], "b_file": r["panel_file"]}
                 for r in tsv(a.pairs)}
    else:
        decks = {p: {"a": x, "b": y, "a_file": None, "b_file": None} for p, (x, y) in enumerate(TABLE28)}
    got, n, bad = set(), 0, []
    for g in rows(a.file):
        n += 1
        got.add((g["pairing"], g["i"]))
        exp = {"seed": a.seed_base + 10_000 * g["pairing"] + g["i"], "first_seat": g["i"] % 2, "bot_a": a.bot_a,
               "bot_b": a.bot_b, **decks.get(g["pairing"], {"a": None, "b": None})}
        diff = [f for f, v in exp.items() if g.get(f) != v]
        if diff:
            bad.append(((g["pairing"], g["i"]), diff))
    ok = n == len(want) and got == want and not bad
    print(f"{os.path.basename(a.file)}: {n} games; {'complete' if ok else 'NOT the expected'} set of {len(want)} deals "
          f"(seeds {a.seed_base:,} + pairing x 10,000 + i, first_seat i % 2, {a.bot_a} v {a.bot_b}, decks from "
          f"{os.path.basename(a.pairs) if a.pairs else 'legality_scan NAMES (--decks)'})"
          + ("" if not bad else f"; {len(bad)} games are not the expected game, the first {bad[0][0]} on {', '.join(bad[0][1])}"))
    return ok


def same(a):
    mine = {}
    for g in rows(a.mine):
        k = (g["pairing"], g["i"])
        if k in mine:
            print(f"{a.label}: deal {k} twice in {os.path.basename(a.mine)}; FAIL")
            return False
        mine[k] = g
    pairings = {k[0] for k in mine}
    ref = {(g["pairing"], g["i"]): g for g in rows(a.ref) if g["i"] < a.max_i and g["pairing"] in pairings}
    if a.fields == "all":
        bad = [k for k in ref if mine.get(k) != ref[k]]
        what = "every field of the reference's row"
    else:
        lacking = sorted({f for g in ref.values() for f in CORE_ID_FIELDS if f not in g})
        if lacking:   # the seven core fields are always compared: a reference without one would narrow the check
            print(f"{a.label}: the reference {os.path.basename(a.ref)} lacks {', '.join(lacking)} in some rows (the identity "
                  f"compares {', '.join(CORE_ID_FIELDS)} on every game); FAIL")
            return False
        fields = list(CORE_ID_FIELDS) + [f for f in ID_FIELDS if f not in CORE_ID_FIELDS and all(f in g for g in ref.values())]
        bad = [k for k in ref if k not in mine or any(mine[k].get(f) != ref[k][f] for f in fields)]
        what = ", ".join(fields)
    extra = [k for k in mine if k not in ref]
    ok = not bad and not extra and len(ref) == a.expect
    print(f"{a.label}: {len(ref) - len(bad)} of {len(ref)} games equal on {what}"
          f"{'' if not extra else f'; {len(extra)} games not in the reference'}"
          f"{'' if len(ref) == a.expect else f'; expected {a.expect} reference games'}"
          f"{'' if not bad else f'; first differing deal {sorted(bad)[0]}'}; {'PASS' if ok else 'FAIL'}")
    return ok


def rules(a):
    text = open(a.page, encoding="utf-8").read()
    if "\nFindings (occurrences / games affected):" not in text:
        print(f"{os.path.basename(a.page)}: no Findings section (an incomplete page)")
        return False
    tail = text.split("\nFindings (occurrences / games affected):", 1)[1]
    found = [ln.strip() for ln in tail.splitlines() if ln.strip().startswith("RULE")]
    print(f"{os.path.basename(a.page)}: " + ("no RULE finding" if not found else f"RULE findings: {'; '.join(found)}"))
    return not found


def cells_of(spec):
    if spec == "km17":
        return list(KM17)
    keep = []
    for e in (x for x in spec.split(",") if x):
        src, p = e.split(":")
        keep.append((src, int(p)))
    unknown = [k for k in keep if k not in {(c[0], c[1]) for c in KM17}]
    if unknown:
        raise SystemExit(f"cells {unknown} are not km17 cells")
    return [c for c in KM17 if (c[0], c[1]) in keep]   # the tool keeps the cells in their own (km17) order


def rows_complete(a):
    cells = cells_of(a.cells)
    new = {int(r["pairing"]): r for r in tsv(os.path.join(a.root, NEW_DECKS_TSV))}
    expect = []
    for src, p, x, y in cells:
        if src == "table":
            files = (f"{a.decks_arg}/{x}.txt", f"{a.decks_arg}/{y}.txt")
        else:
            r = new[p]
            if (r["held_key"], r["opponent"]) != (x, y):
                print(f"{NEW_DECKS_TSV} pairing {p} is {r['held_key']} v {r['opponent']}, not {x} v {y}")
                return False
            files = (r["held_file"], r["panel_file"])
        for i in range(a.first_deal, a.first_deal + a.games):
            expect.append({"source": src, "pairing": p, "a": x, "b": y, "a_file": files[0], "b_file": files[1], "i": i,
                           "seed": BASES[src] + 10_000 * p + i, "first_seat": i % 2,
                           "seat_decks": [x, y] if i % 2 == 0 else [y, x], "bots": [a.bot, a.bot]})
    got = rows(a.file)
    bad = []
    if len(got) != len(expect):
        bad.append(f"{len(got)} rows, not {len(expect)}")
    for k, (g, e) in enumerate(zip(got, expect)):
        diff = [f for f, v in e.items() if g.get(f) != v]
        has = "counts" in g and "xspeed" in g
        if has != a.counts:
            diff.append("counts present" if has else "counts missing")
        elif has and (len(g["counts"]) != 2 or any(g["counts"][s].get("seat") != s or g["counts"][s].get("deck") != e["seat_decks"][s]
                                                   for s in (0, 1))):
            diff.append("counts' seats")
        if diff:
            bad.append(f"row {k + 1} ({e['source']} {e['pairing']} i {e['i']}): {', '.join(diff)}")
            if len(bad) > 3:
                break
    ok = not bad
    print(f"{os.path.basename(a.file)}: {len(got)} rows; {'complete' if ok else 'NOT the expected rows'} "
          f"({len(cells)} cells x deals {a.first_deal}-{a.first_deal + a.games - 1}, {a.bot} both sides, "
          f"{'with' if a.counts else 'without'} counts)" + ("" if ok else "; " + "; ".join(bad[:4])))
    return ok


def rows_v_games(a):
    refs = {"table": a.table, "new_decks.tsv": a.new17}
    got = rows(a.rows)
    want_cells = {(r["source"], r["pairing"]) for r in got}
    ref = {}
    for src, path in refs.items():
        if path is None:
            continue
        for g in rows(path):
            if a.first <= g["i"] <= a.last and (src, g["pairing"]) in want_cells:
                ref[(src, g["pairing"], g["i"])] = g
    seen, bad = set(), []
    for r in got:
        k = (r["source"], r["pairing"], r["i"])
        if not a.first <= r["i"] <= a.last:
            continue
        if k in seen:
            bad.append((k, "twice"))
            continue
        seen.add(k)
        g = ref.get(k)
        if g is None:
            bad.append((k, "no game in the reference"))
            continue
        seats = [g["a"], g["b"]] if g["first_seat"] == 0 else [g["b"], g["a"]]
        diff = [f for f in ("moves", "seed", "first_seat", "a", "b") if r.get(f) != g.get(f)]
        diff += ["seat_decks"] if r.get("seat_decks") != seats else []
        diff += [f for f in ("a_file", "b_file") if f in g and r.get(f) != g[f]]
        if diff:
            bad.append((k, ",".join(diff)))
    missing = sorted(set(ref) - seen)
    want = len(want_cells) * (a.last - a.first + 1)
    cells_ok = a.cells is None or len(want_cells) == a.cells
    ok = not bad and not missing and len(seen) == want == len(ref) and cells_ok
    names = ", ".join(os.path.basename(p) for p in (a.table, a.new17) if p is not None)
    print(f"{a.label}: {len(seen) - len(bad)} of {want} deals equal on the move fingerprint, both decks, seed and seats "
          f"({len(want_cells)} cells{'' if a.cells is None else f', {a.cells} cells expected'}, i {a.first}-{a.last}; "
          f"references {names}; differing {len(bad)}, missing {len(missing)}); no count read; {'PASS' if ok else 'FAIL'}"
          + ("" if not bad else f"; first {bad[0]}") + ("" if not missing else f"; first missing {missing[0]}")
          + ("" if cells_ok else f"; WRONG CELL COUNT: {len(want_cells)}, not {a.cells}"))
    return ok


def d_pairs(a):
    if not 1 <= a.deals <= 10_000:
        raise SystemExit("--deals must be 1 to 10,000")
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(HEADER) + "\n")
        for row, lfile, opp, ofile, _cell in D_ROWS:
            s = a.base + 10_000 * row
            f.write("\t".join([str(row), "d_km", "lucario", lfile, opp, ofile, str(s), str(s + a.deals - 1), str(s + 9_999)]) + "\n")
    last = a.base + 10_000 * D_ROWS[-1][0] + a.deals - 1
    print(f"{os.path.basename(a.out)}: clause (d)'s block, 9 rows (" + "; ".join(f"{r} = {c}" for r, _, _, _, c in D_ROWS)
          + f"), Lucario first-named, seeds {a.base:,} + row x 10,000 + j, j < {a.deals} (last {last:,})")
    return True


def pairings_of(a):
    rs = tsv(a.file)
    ps = [r["pairing"] for r in rs if a.side is None or r["variant_side"] == a.side]
    if a.only is not None:
        keep = set(x for x in a.only.split(",") if x)
        ps = [p for p in ps if p in keep]
    print(",".join(ps))
    return True


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def refs(a):
    """The config's reference files (kta3's ec7e1a8 both-sides games), each checked whole; see the module docstring."""
    cfg = km_config.load(a.config, require=False)
    base = cfg["comparison"]["baseline"]
    groups = [g for g in (a.groups.split(",") if a.groups else km_config.GROUPS)]
    ok = True
    for g in groups:
        r = cfg["refs"][g]
        p = os.path.join(a.root, r["path"])
        if not os.path.exists(p):
            print(f"refs {g}: {r['path']} is missing; FAIL")
            ok = False
            continue
        got = sha256_of(p)
        bad = []
        if got != r["sha256"]:
            bad.append(f"sha256 {got}, not the config's {r['sha256']}")
        if a.committed:
            tracked = subprocess.run(["git", "-C", a.root, "ls-files", "--error-unmatch", "--", r["path"]], capture_output=True).returncode == 0
            clean = subprocess.run(["git", "-C", a.root, "diff", "--quiet", "HEAD", "--", r["path"]], capture_output=True).returncode == 0
            if not (tracked and clean):
                bad.append("not committed, or differs from HEAD")
        if r["pairs"]:
            decks = {int(x["pairing"]): (x["held_key"], x["opponent"], x["held_file"], x["panel_file"])
                     for x in tsv(os.path.join(a.root, r["pairs"]))}
        else:
            decks = {p_: (x, y, None, None) for p_, (x, y) in enumerate(TABLE28)}
        want = {(p_, i) for p_ in r["pairings"] for i in range(r["deals"])}
        seen, wrong, n = set(), [], 0
        for gm in rows(p):
            n += 1
            k = (gm.get("pairing"), gm.get("i"))
            if k in seen:
                wrong.append((k, "twice"))
                continue
            seen.add(k)
            d = decks.get(k[0])
            diff = []
            if (gm.get("bot_a"), gm.get("bot_b")) != (base, base):
                diff.append(f"bots {gm.get('bot_a')} v {gm.get('bot_b')}")
            if d is None or (gm.get("a"), gm.get("b")) != d[:2] or any(
                    f in gm and gm[f] != v for f, v in (("a_file", d[2]), ("b_file", d[3])) if v is not None):
                diff.append("decks")
            if k[1] is None or gm.get("seed") != r["seed_base"] + 10_000 * k[0] + k[1] or gm.get("first_seat") != k[1] % 2:
                diff.append("seed or seats")
            if diff:
                wrong.append((k, ", ".join(diff)))
        if seen != want or n != r["games"]:
            bad.append(f"{n} games on {len(seen)} deals, not the {r['games']} deals of pairings {r['pairings'][0]}-"
                       f"{r['pairings'][-1]} x i < {r['deals']}")
        if wrong:
            bad.append(f"{len(wrong)} games are not the deal's game, the first {wrong[0][0]}: {wrong[0][1]}")
        print(f"refs {g}: {r['path']}: " + ("; ".join(bad) + "; FAIL" if bad else
              f"sha256 = the config's ({got[:16]}...); {n:,} games, {len(r['pairings'])} pairings x i < {r['deals']}, every "
              f"one {base} on both sides on its deal (seed {r['seed_base']:,} + pairing x 10,000 + i, first_seat i % 2, the "
              f"{'pairs file' if r['pairs'] else 'NAMES'} decks){'; committed and unchanged' if a.committed else ''}; PASS"))
        ok &= not bad
    return ok


def inputs(a):
    root = os.path.normpath(a.root)
    cfg = km_config.load(a.config)
    ref_of = {g: os.path.join(root, cfg["refs"][g]["path"]) for g in km_config.GROUPS}
    names = [os.path.abspath(a.config)]

    def pairs_and_decks(pf):
        names.append(pf)
        for r in tsv(pf):
            names.extend([os.path.join(root, r["held_file"]), os.path.join(root, r["panel_file"])])

    def coverage():  # the coverage groups' pairs files, their lists and kta3's coverage references (the config's)
        for g in ("b2e", "scizor", "var_v-lucario_2", "var_v-suicune_2", "var_v-weezing_2", "var_l-charizardy"):
            pairs_and_decks(os.path.join(root, cfg["refs"][g]["pairs"]))
            names.append(ref_of[g])

    for pat in ("run_km.sh", "km_check.py", "km_config.py", "km_thresholds.py", "footprint_km.py"):
        names += glob.glob(os.path.join(a.here, pat))
    names += glob.glob(os.path.join(a.build, "decks", "research", "*.txt"))
    names += glob.glob(os.path.join(root, "decks", "research", "*.txt"))
    names += [os.path.join(a.out, cfg["programs"]["pins"]), os.path.join(a.out, "tool_census.rs"), os.path.join(a.out, LIST_NAME)]
    ref = os.path.join(a.build, "ref")
    co = cfg["cloud_outputs"]
    if a.part == "I":   # Amendment 1 (e) item 3: the 45 cells, the coverage references, 8a's slice and tool tests 1 and 3
        names += [ref_of["table"], ref_of["new17"]]
        names += [os.path.join(ref, os.path.basename(co[k]["path"])) for k in ("km3_smoke", "tool_test3_rows", "tool_test3_trace")]
        pairs_and_decks(os.path.join(root, NEW_DECKS_TSV))
        coverage()
    if a.part in ("T", "R"):
        names += [ref_of["table"], ref_of["new17"]]
        pairs_and_decks(os.path.join(root, NEW_DECKS_TSV))
    if a.part == "R":
        coverage()
        pairs_and_decks(os.path.join(a.out, "pairs", "d_lucario_block.tsv"))
        names += [os.path.join(root, "rl", "results", "kta_2026-09-29", "coverage_skip.py"),
                  os.path.join(a.out, "GO_km_tables")]
    out = set()
    for p in names:
        p = os.path.normpath(os.path.abspath(p))
        out.add(os.path.relpath(p, root) if p.startswith(root + os.sep) else p)
    print("\n".join(sorted(out)))
    return True


def commit_order(a):
    def git(*args):
        return subprocess.run(["git", "-C", a.root, *args], capture_output=True, text=True)

    r = git("rev-parse", "--verify", "--quiet", a.amendment + "^{commit}")
    if r.returncode != 0 or not r.stdout.strip():
        print(f"the amendment {a.amendment} is not a commit here")
        return False
    amend = r.stdout.strip()
    if git("merge-base", "--is-ancestor", amend, "HEAD").returncode != 0:
        print(f"the amendment {amend[:7]} is not in HEAD's history")
        return False
    changed = git("diff", "--name-only", amend + "^", amend).stdout.splitlines()
    if a.registration not in changed:
        print(f"the amendment {amend[:7]} does not change {a.registration}")
        return False
    def first_add(p):
        adds = git("log", "--diff-filter=A", "--format=%H", "HEAD", "--", p).stdout.split()
        return adds[-1] if adds else None   # git log lists newest first: the last is the commit that first added it

    chain = []
    for p in a.paths:
        c = first_add(p)
        if c is None:
            print(f"{p} was never added in HEAD's history")
            return False
        chain.append((p, c))
    steps = chain + [("the amendment", amend)]
    for (p1, c1), (p2, c2) in zip(steps, steps[1:]):
        if c1 == c2 or git("merge-base", "--is-ancestor", c1, c2).returncode != 0:
            print(f"{p1} (commit {c1[:7]}) is not strictly before {p2} (commit {c2[:7]})"
                  + ("; they are the same commit" if c1 == c2 else "")
                  + ": section 4.0 steps 6-8 are three commits, in that order; FAIL")
            return False
    early = []
    for q in a.with_or_before or []:   # the sample's raw files: committed with thresholds.json or before it (step 7)
        c = first_add(q)
        if c is None:
            print(f"{q} was never added in HEAD's history (step 7 computes the independent check from the committed raw files); FAIL")
            return False
        if c != chain[0][1] and git("merge-base", "--is-ancestor", c, chain[0][1]).returncode != 0:
            print(f"{q} (commit {c[:7]}) is not committed with or before {chain[0][0]} (commit {chain[0][1][:7]}): step 7 "
                  f"computes the independent check from the committed raw files; FAIL")
            return False
        early.append((q, c))
    print("commit order (section 4.0 steps 6-8): "
          + "".join(f"{q} first committed at {c[:7]}; " for q, c in early)
          + "; ".join(f"{p} first committed at {c[:7]}" for p, c in chain)
          + f"; then the amendment {amend[:7]}, which changes {os.path.basename(a.registration)}: "
          + ("the raw files with or before the first, then " if early else "") + "each strictly before the next; PASS")
    return True


# ---- km's one list (Amendment 1 (b) item 4) --------------------------------------------------------------------------
LIST_NAME = "km_inputs.sha256"
COVERAGE = ("b2e", "scizor", "var_v-lucario_2", "var_v-suicune_2", "var_v-weezing_2", "var_l-charizardy")
PROGRAM_PATHS = {"deckgym": "engine/target/release/deckgym", "legality_scan": "engine/target/release/examples/legality_scan",
                 "tool_census": "engine/target/release/examples/tool_census"}   # in the build folder, as run_km.sh builds them


def list_decks_and_pairs(cfg, root):
    """Repo paths (sorted) of every pairs file the runs read (new_decks.tsv and the coverage groups') and every deck list
    they name, clause (d)'s lists and decks/research's lists: the files (b) item 4 lists "from B's tree"."""
    names = set()
    for pf in [NEW_DECKS_TSV] + [cfg["refs"][g]["pairs"] for g in COVERAGE]:
        names.add(pf)
        for r in tsv(os.path.join(root, pf)):
            names.update([r["held_file"], r["panel_file"]])
    for _row, lf, _opp, of, _cell in D_ROWS:
        names.update([lf, of])
    names.update(f"decks/research/{os.path.basename(p)}" for p in glob.glob(os.path.join(root, "decks", "research", "*.txt")))
    return sorted({os.path.normpath(n).replace(os.sep, "/") for n in names})


def tree_differences(root, commit, paths):
    """The paths whose working-tree bytes are not commit's blob (or that are missing on either side)."""
    inp = "".join(f"{commit}:{p}\n" for p in paths).encode()
    r = subprocess.run(["git", "-C", root, "cat-file", "--batch"], input=inp, capture_output=True)
    out = r.stdout
    if r.returncode != 0 or out.count(b"\n") < len(paths):
        return [f"git cat-file --batch failed in {root} (exit {r.returncode}): {r.stderr.decode(errors='replace')[:200]}"]
    bad, pos = [], 0
    for p in paths:
        nl = out.index(b"\n", pos)
        head = out[pos:nl].decode(errors="replace").split()
        pos = nl + 1
        if len(head) != 3 or head[1] != "blob":
            bad.append(f"{p}: not a file in {commit[:7]}'s tree")
            continue
        size = int(head[2])
        blob, pos = out[pos:pos + size], pos + size + 1
        wt = os.path.join(root, p)
        if not os.path.isfile(wt):
            bad.append(f"{p}: not in the working tree")
        elif open(wt, "rb").read() != blob:
            bad.append(f"{p}: the working tree's differs from {commit[:7]}'s")
    return bad


def _rel(root, p):
    p = os.path.normpath(os.path.abspath(p))
    return os.path.relpath(p, root) if p.startswith(root + os.sep) else p


def read_programs(pp):
    """programs.txt's lines as {name: (sha256, path)} (sha256sum's format), or a string saying what is wrong."""
    got = {}
    for ln in (x.strip() for x in open(pp, encoding="utf-8")):
        if not ln or ln.startswith("#"):
            continue
        parts = ln.split(None, 1)
        if len(parts) != 2 or not km_config.HEX64.match(parts[0]):
            return f"a line of {os.path.basename(pp)} is not in sha256sum's format: {ln!r}"
        path_ = parts[1].lstrip("*")
        name = os.path.basename(path_)
        if name not in PROGRAM_PATHS or name in got:
            return f"{os.path.basename(pp)} names {path_!r}: not one of deckgym, legality_scan and tool_census once each"
        got[name] = (parts[0], path_)
    if set(got) != set(PROGRAM_PATHS):
        return f"{os.path.basename(pp)} records {sorted(got)}, not {sorted(PROGRAM_PATHS)}"
    return got


def list_files(cfg, root, build):
    """The files the list pins, as repo-relative or absolute paths, in the list's order."""
    co = cfg["cloud_outputs"]
    files = [_rel(root, cfg["_path"])]
    files += [cfg["refs"][g]["path"] for g in km_config.GROUPS]
    files += [os.path.join(build, "ref", os.path.basename(co[k]["path"])) for k in ("km3_smoke", "tool_test3_rows", "tool_test3_trace")]
    files.append(os.path.join(build, "engine", "examples", "tool_census.rs"))
    files += sorted(glob.glob(os.path.join(build, "decks", "research", "*.txt")))
    files += list_decks_and_pairs(cfg, root)
    files += [os.path.join(build, PROGRAM_PATHS[n]) for n in ("deckgym", "legality_scan", "tool_census")]
    return [_rel(root, os.path.join(root, f)) for f in files]


def list_set(cfg, build, progs, root):
    """The list's "# set" lines (key -> value), from the config, the build folder and programs.txt."""
    co = cfg["cloud_outputs"]
    s = {"candidate": cfg["comparison"]["candidate"], "baseline": cfg["comparison"]["baseline"], "B": cfg["build"]["commit"],
         "config": f"{_rel(root, cfg['_path'])} {sha256_of(cfg['_path'])}",
         "build_folder": os.path.normpath(os.path.abspath(build)), "tool_source_sha256": cfg["counter_tool"]["source_sha256"]}
    for g in km_config.GROUPS:
        s[f"reference {g}"] = f"{cfg['refs'][g]['path']} {cfg['refs'][g]['sha256']}"
    for k in ("km3_smoke", "tool_test3_rows", "tool_test3_trace"):
        s[k] = f"{co[k]['path']} {co[k]['sha256']}"
    for k in ("tool_test1_stdout_sha256", "tool_test1_games_sha256"):
        s[k] = co[k]
    for n in ("deckgym", "legality_scan", "tool_census"):
        s[f"program {n}"] = f"{progs[n][0]} {os.path.normpath(os.path.abspath(progs[n][1]))}"
    return s


def list_write(cfg, root, build, programs, dest):
    """Writes the list to dest; returns (True, summary) or (False, why). Every file must be on the disk, the eight
    references and the cloud's outputs with the config's sha256, the build's tool source with the config's, and the
    programs with programs.txt's."""
    root = os.path.normpath(root)
    progs = read_programs(programs)
    if isinstance(progs, str):
        return False, progs
    for n, (_s, p) in progs.items():
        if os.path.normpath(os.path.abspath(p)) != os.path.normpath(os.path.join(build, PROGRAM_PATHS[n])):
            return False, f"programs.txt names {p} for {n}, not the build's {os.path.join(build, PROGRAM_PATHS[n])}"
    if open(os.path.join(build, "COMMIT"), encoding="utf-8").read().strip() != cfg["build"]["commit"]:
        return False, f"{build}/COMMIT is not B {cfg['build']['commit']}"
    sset = list_set(cfg, build, progs, root)
    want = expected_shas(cfg, sset, root)
    lines, missing, wrong = [], [], []
    for f in list_files(cfg, root, build):
        p = f if os.path.isabs(f) else os.path.join(root, f)
        if not os.path.isfile(p):
            missing.append(f)
            continue
        h = sha256_of(p)
        if f in want and want[f] != h:
            wrong.append(f"{f}: sha256 {h}, not {want[f]}")
        lines.append(f"{h}  {f}")
    if missing or wrong:
        return False, "; ".join([f"missing {m}" for m in missing[:3]] + wrong[:3])
    head = ["# km_inputs.sha256: km's one list (rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md, Amendment 1 (b)",
            "# item 4), written by run_km.sh part I before its first game (with a 'KM INPUTS WRITTEN' line in STATUS.txt) and",
            "# committed with part I's record ((e) item 5). Every runner and read_km.py take the candidate, the baseline, the",
            "# reference files and the program hashes from it, and check it before their first game or read (the runners also",
            "# after their last). The '# set' lines are the set; the others are sha256sum lines (paths relative to the repo",
            "# root when inside it), checked from the repo root. It changes only by a dated STATUS.txt line:",
            "# 'KM INPUTS CHANGED <B's short hash> <UTC time> km_inputs.sha256 <its new sha256>: <why>'."]
    body = [f"# set {k} {v}" for k, v in sset.items()]
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(head + body + lines) + "\n")
    return True, (f"{len(lines)} files (the config, 8 reference files, the cloud's 3 outputs, the build's tool source and "
                  f"decks/research, {len(list_decks_and_pairs(cfg, root))} pairs files and deck lists, 3 programs)")


def expected_shas(cfg, sset, root):
    """The sha256 the list's files must have by the set (the config's, or programs.txt's), by listed path."""
    b = sset["build_folder"]
    co = cfg["cloud_outputs"]
    want = {_rel(root, os.path.join(root, cfg["refs"][g]["path"])): cfg["refs"][g]["sha256"] for g in km_config.GROUPS}
    for k in ("km3_smoke", "tool_test3_rows", "tool_test3_trace"):
        want[_rel(root, os.path.join(b, "ref", os.path.basename(co[k]["path"])))] = co[k]["sha256"]
    want[_rel(root, os.path.join(b, "engine", "examples", "tool_census.rs"))] = cfg["counter_tool"]["source_sha256"]
    for n in PROGRAM_PATHS:
        s, p = sset[f"program {n}"].split(" ", 1)
        want[_rel(root, p)] = s
    return want


def parse_list(p):
    sset, files, bad = {}, [], []
    for ln in open(p, encoding="utf-8").read().splitlines():
        if ln.startswith("# set "):
            k, _, v = ln[6:].partition(" ")
            if k in ("reference", "program"):
                k2, _, v = v.partition(" ")
                k = f"{k} {k2}"
            if k in sset:
                bad.append(f"'# set {k}' twice")
            sset[k] = v
        elif ln.startswith("#") or not ln.strip():
            continue
        else:
            h, sep, f = ln.partition("  ")
            if not sep or not km_config.HEX64.match(h):
                bad.append(f"not a sha256sum line: {ln[:120]!r}")
            else:
                files.append((h, f))
    return sset, files, bad


def list_check(cfg, root, out, build=None, programs=None):
    """km's one list in out against the config, the disk, STATUS.txt and (with programs) programs.txt: (True, summary) or
    (False, the first differences). Used by run_km.sh (one-list check) and read_km.py."""
    root = os.path.normpath(root)
    lp = os.path.join(out, LIST_NAME)
    if not os.path.isfile(lp):
        return False, f"{lp} does not exist: part I writes km's one list before its first game (Amendment 1 (b) item 4)"
    lsha = sha256_of(lp)
    S = cfg["prefix"]
    stp = os.path.join(out, "STATUS.txt")
    rec = [ln for ln in (open(stp, encoding="utf-8").read().splitlines() if os.path.isfile(stp) else [])
           if ln.startswith((f"KM INPUTS WRITTEN {S} ", f"KM INPUTS CHANGED {S} "))]
    m = re.search(r" km_inputs\.sha256 ([0-9a-f]{64})\b", rec[-1]) if rec else None
    if not m:
        return False, (f"STATUS.txt has no 'KM INPUTS WRITTEN|CHANGED {S} <time> km_inputs.sha256 <sha256>' line: the list "
                       f"is not recorded ((b) item 4: it changes only by a dated STATUS.txt line)")
    if m.group(1) != lsha:
        return False, (f"{LIST_NAME} has sha256 {lsha}, not the {m.group(1)} STATUS.txt's last KM INPUTS line records: the "
                       f"list was changed without a dated STATUS.txt line ((b) item 4)")
    sset, files, bad = parse_list(lp)
    if bad:
        return False, f"{LIST_NAME}: " + "; ".join(bad[:3])
    b = sset.get("build_folder")
    if not b:
        return False, f"{LIST_NAME} names no build folder"
    if build is not None and os.path.normpath(os.path.abspath(build)) != b:
        return False, f"{LIST_NAME} names the build folder {b}, not this run's {os.path.normpath(os.path.abspath(build))}"
    cp = os.path.join(b, "COMMIT")
    if not os.path.isfile(cp) or open(cp, encoding="utf-8").read().strip() != cfg["build"]["commit"]:
        return False, f"the list's build folder {b} has no COMMIT file naming B {cfg['build']['commit']}"
    progs = {n: tuple(sset.get(f"program {n}", " ").split(" ", 1)) for n in PROGRAM_PATHS}
    if any(len(v) != 2 or not km_config.HEX64.match(v[0]) for v in progs.values()):
        return False, f"{LIST_NAME} does not name the three programs with their sha256"
    off = [n for n, (_s, p) in progs.items() if p != os.path.normpath(os.path.join(b, PROGRAM_PATHS[n]))]
    if off:
        return False, f"{LIST_NAME} names {off[0]} at {progs[off[0]][1]}, not in its build folder {b}"
    csha = sha256_of(cfg["_path"])
    if sset.get("config", "").rsplit(" ", 1)[-1] != csha:
        return False, (f"the config loaded ({cfg['_path']}, sha256 {csha[:16]}...) is not the one {LIST_NAME} lists "
                       f"({sset.get('config')!r}): the runner and the reader read the config part I listed ((b) item 4; "
                       f"it changes only by a dated STATUS.txt line)")
    want_set = list_set(cfg, b, progs, root)
    diff = [k for k in set(want_set) | set(sset) if want_set.get(k) != sset.get(k)]
    if diff:
        k = sorted(diff)[0]
        return False, (f"{LIST_NAME}'s set differs from the config's on {len(diff)} entries, e.g. '{k}': the list says "
                       f"{sset.get(k)!r}, the config {cfg['_path']} gives {want_set.get(k)!r}")
    got = [f for _, f in files]
    want_files = list_files(cfg, root, b)
    if sorted(got) != sorted(want_files) or len(set(got)) != len(got):
        extra, lack = sorted(set(got) - set(want_files)), sorted(set(want_files) - set(got))
        return False, (f"{LIST_NAME} does not list exactly the files the runs read: {len(lack)} missing from it"
                       + (f" (e.g. {lack[0]})" if lack else "") + f", {len(extra)} not expected" + (f" (e.g. {extra[0]})" if extra else ""))
    want = expected_shas(cfg, sset, root)
    cfg_rel = _rel(root, cfg["_path"])
    want[cfg_rel] = sha256_of(cfg["_path"])
    wrong = []
    for h, f in files:
        p = f if os.path.isabs(f) else os.path.join(root, f)
        if not os.path.isfile(p):
            wrong.append(f"{f} is missing")
        elif sha256_of(p) != h:
            wrong.append(f"{f} has sha256 {sha256_of(p)[:16]}..., not the list's {h[:16]}...")
        elif f in want and want[f] != h:
            wrong.append(f"{f}: the list's sha256 {h[:16]}... is not the {'config loaded' if f == cfg_rel else 'set'}'s {want[f][:16]}...")
    if wrong:
        return False, f"{len(wrong)} of the list's {len(files)} files differ: " + "; ".join(wrong[:3])
    if programs is not None:
        pr = read_programs(programs)
        if isinstance(pr, str):
            return False, pr
        pr = {n: (s, os.path.normpath(os.path.abspath(p))) for n, (s, p) in pr.items()}
        if pr != progs:
            return False, f"{os.path.basename(programs)} does not record the list's three programs: {pr} against {progs}"
    return True, (f"{LIST_NAME} (sha256 {lsha[:16]}..., as STATUS.txt records it): its set is the config's (B {cfg['build']['commit'][:7]}, "
                  f"{sset['candidate']} against {sset['baseline']}, 8 reference files, the cloud's outputs, 3 programs) and its "
                  f"{len(files)} files have their sha256")


def one_list(a):
    cfg = km_config.load(a.config)
    if a.op == "tree":
        paths = list_decks_and_pairs(cfg, os.path.normpath(a.root))
        bad = tree_differences(a.root, cfg["build"]["commit"], paths)
        print(f"{len(paths) - len(bad)} of {len(paths)} pairs files and deck lists the runs read equal B "
              f"{cfg['build']['commit'][:7]}'s tree byte for byte (Amendment 1 (b) item 4)"
              + ("" if not bad else f"; {len(bad)} differ: " + "; ".join(bad[:4])) + ("; PASS" if not bad else "; FAIL"))
        return not bad
    if a.op == "write":
        for x in ("build", "programs", "dest"):
            if not getattr(a, x):
                raise SystemExit(f"one-list write needs --{x}")
        ok, msg = list_write(cfg, a.root, a.build, a.programs, a.dest)
        print(msg)
        return ok
    ok, msg = list_check(cfg, a.root, a.out, a.build, a.programs)
    print(msg + ("; PASS" if ok else "; FAIL"))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("complete"); p.add_argument("file"); p.add_argument("--pairings", required=True)
    p.add_argument("--games", type=int, required=True); p.add_argument("--seed-base", type=int, required=True)
    p.add_argument("--bot-a", required=True); p.add_argument("--bot-b", required=True)
    m = p.add_mutually_exclusive_group(required=True); m.add_argument("--pairs"); m.add_argument("--decks", action="store_true")
    p = sub.add_parser("same"); p.add_argument("mine"); p.add_argument("ref"); p.add_argument("--max-i", type=int, required=True)
    p.add_argument("--expect", type=int, required=True); p.add_argument("--label", required=True)
    p.add_argument("--fields", choices=["all", "id"], default="all")
    p = sub.add_parser("rules"); p.add_argument("page")
    p = sub.add_parser("rows-complete"); p.add_argument("file"); p.add_argument("--cells", required=True)
    p.add_argument("--first-deal", type=int, required=True); p.add_argument("--games", type=int, required=True)
    p.add_argument("--bot", required=True); p.add_argument("--root", required=True)
    p.add_argument("--decks-arg", default="../decks/research")
    m = p.add_mutually_exclusive_group(required=True)
    m.add_argument("--counts", dest="counts", action="store_true"); m.add_argument("--no-counts", dest="counts", action="store_false")
    p = sub.add_parser("rows-v-games"); p.add_argument("rows"); p.add_argument("--from", dest="first", type=int, required=True)
    p.add_argument("--to", dest="last", type=int, required=True); p.add_argument("--table", required=True)
    p.add_argument("--new17", default=None); p.add_argument("--label", required=True)
    p.add_argument("--cells", type=int, default=None)
    p = sub.add_parser("d-pairs"); p.add_argument("--out", required=True); p.add_argument("--base", type=int, required=True)
    p.add_argument("--deals", type=int, required=True)
    p = sub.add_parser("pairings-of"); p.add_argument("file"); p.add_argument("--side", choices=["a", "b"]); p.add_argument("--only")
    p = sub.add_parser("inputs")
    for x in ("--part", "--root", "--build", "--here", "--out", "--config"):
        p.add_argument(x, required=True)
    p = sub.add_parser("refs"); p.add_argument("--config", required=True); p.add_argument("--root", required=True)
    p.add_argument("--committed", action="store_true"); p.add_argument("--groups", default=None)
    p = sub.add_parser("commit-order"); p.add_argument("--root", required=True); p.add_argument("--amendment", required=True)
    p.add_argument("--registration", required=True); p.add_argument("--paths", nargs="+", required=True)
    p.add_argument("--with-or-before", nargs="+", default=None)
    p = sub.add_parser("one-list"); p.add_argument("op", choices=["tree", "write", "check"])
    p.add_argument("--config", required=True); p.add_argument("--root", required=True); p.add_argument("--out")
    p.add_argument("--build"); p.add_argument("--programs"); p.add_argument("--dest")
    a = ap.parse_args()
    if a.cmd == "one-list" and a.op == "check" and not a.out:
        ap.error("one-list check needs --out")
    fn = {"complete": complete, "same": same, "rules": rules, "rows-complete": rows_complete, "rows-v-games": rows_v_games, "d-pairs": d_pairs, "pairings-of": pairings_of, "inputs": inputs,
          "refs": refs, "commit-order": commit_order, "one-list": one_list}[a.cmd]
    try:
        sys.exit(0 if fn(a) else 1)
    except km_config.ConfigError as e:
        print(f"km_check {a.cmd}: STOP: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()

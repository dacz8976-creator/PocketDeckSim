#!/usr/bin/env bash
# Stand-in test for read_kta.py (kta's reading, written blind). It builds fake "fresh" kta trees from the kt DEVELOPMENT
# files relabelled onto kta's fresh seeds (section 3.2 of REGISTRATION.md), plants known effects, runs the reader on each
# tree and shows that the reading moves the way the registration says and that its guards stop it. No game is played and
# NO kta result is read: every reader run passes --dir at a stand-in folder under $W (never a kta tables folder), and the
# file-free modes (--selftest, --parse-page on existing earlier pages) read no kta file at all.
# The stand-in runner files are made the way the registration says the runner makes them: the 45 cells' mixed rows only in
# the cells with a changed game (500 deals) plus the i<40 sample in the others (all 45 at 500 on the ordinary route);
# coverage mixed rows only in the pairings whose both-sides games differ, and coverage_skip.txt naming every pairing.
# Scenarios (expected result in brackets):
#   unit          --selftest; --parse-page on earlier real score45 pages (none is kta's); koh's page with a veto line dropped.
#   dev           kt's development files as they are (kta3 = kt's kta3 games), relabelled onto fresh seeds; (d) x4 to 2,000
#                 per row. At --reps 4000 it must reproduce the development reading: footprint 559 (2.48%), ΔMSE -5.9
#                 (-11.0 to -1.4) wholly below zero, τ̂ +0.21 (+0.06 to +0.31), (d) +1.00 at about +/-0.195, Jasmine 30.2%
#                 against 0.4%, deck 07 +8.5. [ADOPTED, outcome 1; Jasmine reported]
#   null          kta3 = kog3's own games everywhere. [ΔMSE exactly 0 spans zero -> fallback; (d) and Jasmine fail:
#                 NOT ADOPTED (gain, mechanism), never an accuracy negative]
#   gain          null + a planted (d) gain + kta3's development A/B (Jasmine 30%). [spans -> fallback, all four hold: ADOPTED]
#   harm          gain + a footprint and own-side harm on Suicune's cells, on B2e Manectric v Suicune, and on Scizor.
#                 [NOT ADOPTED: harm, coverage]
#   worsen        gain + kta3's results pushed away from Limitless in the 17 reach cells (footprint under 15%).
#                 [ΔMSE wholly above zero: NOT ADOPTED, accuracy-worsening, no fallback]
#   worsen_ord    the same with moves changed in half the reach cells' games (footprint ~19%): the ordinary rule, all 45
#                 cells' mixed rows. [NOT ADOPTED, accuracy-worsening]
#   ord_below     ordinary route, results moved halfway to Limitless, kta3's A/B = kog3's (Jasmine ~0.4%).
#                 [ΔMSE wholly below zero: Jasmine reported only: ADOPTED]
#   jas_low       gain with kta3's deck-07 A/B = kog3's games (Jasmine ~0.4%). [spans: NOT ADOPTED, mechanism]
#   jas_low_below dev with kta3's deck-07 A/B = kog3's games. [below: ADOPTED; deck 07 "did not replicate" beside]
#   guard         gain with kog3's own deck-07 Jasmine rate raised past 20%. [spans: NOT ADOPTED, mechanism (guard)]
#   guard_below   dev with the same kog3 plant. [below: guard reported: ADOPTED]
#   skip_winners  gain + one B2e deal (pairing 4) whose moves differ with the same result, and a coverage_skip.txt that
#                 SKIPs pairing 4 as if winners were enough. [the reader's own check: BAD SKIP, coverage PENDING]
#   skip_unnamed  gain, with one SKIP line removed from coverage_skip.txt. [PENDING: skipped without being named]
#   skip_noreport gain, no coverage_skip.txt. [PENDING]
#   mixed_missing dev with B2e pairing 4's mixed rows removed from the file although its games differ. [PENDING]
#   reach         gain + one changed game in Altaria v Blaziken (no switch-1 card). [HELD by the integrity line;
#                 once explained: ADOPTED]; explained: the same with --integrity-explained. [ADOPTED]
#   reach_harm    harm + the same changed game. [HELD before the failures; once explained: NOT ADOPTED (harm, coverage)];
#                 with --integrity-explained. [NOT ADOPTED: harm, coverage]
#   worsen_reach  worsen + the same changed game. [HELD even under 'wholly above zero'; once explained: NOT ADOPTED
#                 (accuracy-worsening)]; with --integrity-explained. [NOT ADOPTED, accuracy-worsening]
#   c0            gain + one sampled mixed-row game in a zero-footprint cell with different moves. [HELD]
#   ord_reach     worsen_ord + a changed game outside the reach cells: [STOP at 1c]; with --integrity-explained it reads on.
#   edge3374/5    exactly 3,374 / 3,375 changed games (both print 15.00%): reserve at 3,374, ordinary at 3,375.
#   guards        no footprint.txt; a short file; footprint.txt off by one; route text against the counts; a changed seed;
#                 development seeds; (d) at 500 per row; a seat flipped; a short A/B file; identity failed / missing /
#                 short; timing OVER; a RULE finding; a scan page missing (HELD, also on the harm tree); a wrong program
#                 hash; half the 45 cells' mixed rows missing; (d) not in; deck 07's A/B not in (below: holds nothing;
#                 spans: PENDING); a trace file not in (holds nothing) or short (STOP); a score45 page edited to a ΔMSE
#                 interval +0.4 to +20.0 on worsen without the (d) gain [NOT ADOPTED under both open labels, the name
#                 waiting for the rerun] and to a τ̂ bound of -1.10 [PENDING]; --footprint-only; --reuse-45 with its sidecar.
# Every scenario has an expected pattern (the verdict line or the STOP) and some have more (also / never): each is
# checked against the reader's output, a miss is counted and listed at the end, and the script then exits 1.
# Every stand-in tree also carries the Rayquaza traces: kt's development per-game rows (v Lucario) on both opponents'
# fresh seeds, with synthetic per-ply decision rows, so the first-divergence tally is exercised.
# Usage (WSL): bash test_read_kta.sh [stand-in folder]   (FULL=1 prints every reader output in full; REPS, REPS_DEV)
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/kta_2026-09-29"
W=${1:-/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kta/reader-writer/standin}
REPS=${REPS:-100}; REPS_DEV=${REPS_DEV:-4000}
PX=ec7e1a8_fresh
case "$W" in *kta_tables*|*kta_2026-09-29*) echo "refusing: the stand-in folder must not be a kta results folder"; exit 2;; esac
[ "${CLEAN:-0}" = 1 ] && rm -rf "$W"     # CLEAN=1 rebuilds the base trees too (they are kept between runs otherwise)
mkdir -p "$W"; rm -rf "$W/cache"         # the per-scenario runner files are always rebuilt

cat > "$W/make_standin.py" <<'EOF'
import csv, hashlib, json, os, shutil, subprocess, sys
R, W, scn = sys.argv[1:4]
RES = f"{R}/rl/results"
O, KOG, KL = f"{RES}/kt_tables_2026-09-28", f"{RES}/kog_composition_2026-09-27", f"{RES}/koh_2026-09-28/laptop_runs"
TSV, B2ET = f"{RES}/gauntlet_runs_2026-09-26/tsv", f"{RES}/b2e_card_check_2026-09-26/b2e_pairings.tsv"
PX = "ec7e1a8_fresh"
VARS = ("v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy")
AB = ("07", "05", "11", "01", "03")
PAGE = "bot {bots}, 500 table deals per pairing (stand-in page written by test_read_kta.sh)\n\nFindings (occurrences / games affected):\n  none\n"


def b2e_dev():
    for p in ("/tmp/kt_ref_b2e_kog3.jsonl", "/tmp/koh_cloud/b2e_kog3.jsonl", f"{W}/b2e_kog3_dev.jsonl"):
        if os.path.exists(p):
            return p
    out = subprocess.run(["git", "-C", R, "show", "origin/claude/pensive-ptolemy-spwc0b:rl/results/koh_2026-09-28/reading/b2e_kog3.jsonl"],
                         capture_output=True, check=True)
    open(f"{W}/b2e_kog3_dev.jsonl", "wb").write(out.stdout)
    return f"{W}/b2e_kog3_dev.jsonl"


def vbase(v):
    return 23_002_000_000 if v == "l-charizardy" else 23_000_000_000


# group -> (kog3 dev file, kta3 dev file, {direction: (dev mixed file, bots, fresh src name, run name)}, fresh base, both-sides names)
def groups():
    g = {}
    for grp, k, x, base in (("table", f"{KOG}/table_kog3.jsonl", f"{O}/ec7e1a8_kta3_table.jsonl", 23_000_000_000),
                            ("new17", f"{KOG}/new17_kog3.jsonl", f"{O}/ec7e1a8_kta3_new17.jsonl", 23_001_000_000)):
        mx = {dr: (f"{O}/ec7e1a8_mixed_{grp}_kta3_{dr}.jsonl", ("kta3", "kog3") if dr == "first" else ("kog3", "kta3"),
                   f"{PX}_mixed_{grp}_kta3_{dr}.full.jsonl", f"{PX}_mixed_{grp}_kta3_{dr}.jsonl") for dr in ("first", "second")}
        g[grp] = (k, x, mx, base, (f"{PX}_kog3_{grp}.jsonl", f"{PX}_kta3_{grp}.jsonl"))
    g["b2e"] = (b2e_dev(), f"{O}/ec7e1a8_b2e_kta3.jsonl",
                {"first": (f"{O}/ec7e1a8_mixed_b2e_kta3_first.jsonl", ("kta3", "kog3"), f"{PX}_mixed_b2e_kta3_first.full.jsonl", f"{PX}_mixed_b2e_kta3_first.jsonl")},
                23_002_000_000, (f"{PX}_b2e_kog3.jsonl", f"{PX}_b2e_kta3.jsonl"))
    g["scizor"] = (f"{KL}/scizor_kog3.jsonl", f"{O}/ec7e1a8_scizor_kta3.jsonl",
                   {dr: (f"{O}/ec7e1a8_mixed_scizor_kta3_{dr}.jsonl", ("kta3", "kog3") if dr == "first" else ("kog3", "kta3"),
                         f"{PX}_mixed_scizor_kta3_{dr}.full.jsonl", f"{PX}_mixed_scizor_kta3_{dr}.jsonl") for dr in ("first", "second")},
                   23_001_000_000, (f"{PX}_scizor_kog3.jsonl", f"{PX}_scizor_kta3.jsonl"))
    for v in VARS:
        mx = {s: (f"{O}/ec7e1a8_var_{v}_kta3_mixed_{s}.jsonl", ("kta3", "kog3") if s == "a" else ("kog3", "kta3"),
                  f"{PX}_var_{v}_kta3_mixed_{s}.full.jsonl", f"{PX}_var_{v}_kta3_mixed_{s}.jsonl")
              for s in ("a", "b") if os.path.exists(f"{O}/ec7e1a8_var_{v}_kta3_mixed_{s}.jsonl")}
        g[f"var_{v}"] = (f"{KL}/var_{v}_kog3.jsonl", f"{O}/ec7e1a8_var_{v}_kta3.jsonl", mx, vbase(v), (f"{PX}_var_{v}_kog3.jsonl", f"{PX}_var_{v}_kta3.jsonl"))
    return g


def H(tag, g):
    return int(hashlib.md5(f"{tag}:{g['seed']}:{g.get('pairing')}:{g.get('a')}:{g.get('b')}".encode()).hexdigest()[:8], 16)


def newmoves(g, tag="*"):
    g["moves"] = hashlib.md5((g["moves"] + tag).encode()).hexdigest()[:16]


def flip(g, v):
    g["first_deck_score"] = v
    newmoves(g)


def rd(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def wr(dst, recs):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        os.remove(dst)
    with open(dst, "w", encoding="utf-8") as f:
        for g in recs:
            f.write(json.dumps(g, sort_keys=True) + "\n")


def fresh(recs, base, bots=None, keep=None):
    out = []
    for g in recs:
        if keep and not keep(g):
            continue
        g = dict(g)
        g["seed"] = base + 10_000 * g["pairing"] + g["i"]
        if bots:
            g["bot_a"], g["bot_b"] = bots
        out.append(g)
    return out


def x4(recs, bots):
    """(d): 500 development deals per row -> 2,000 (copies k = 0..3, i + 500 k, the same move change in both arms)."""
    out = []
    for k in range(4):
        for g in recs:
            g = dict(g)
            g["i"] += 500 * k
            g["seed"] = 23_003_000_000 + 10_000 * g["pairing"] + g["i"]
            if k:
                newmoves(g, f"#{k}")
            g["bot_a"], g["bot_b"] = bots
            out.append(g)
    return out


def ab_fresh(recs, pilot=None):
    out = []
    for g in recs:
        g = dict(g)
        g["seed"] = g["seed"] - 22_600_000_000 + 23_004_000_000
        if pilot:
            g["pilot"] = pilot
        out.append(g)
    return out


def link(src, dst):
    if os.path.lexists(dst):
        os.remove(dst)
    os.symlink(os.path.realpath(src), dst)


def build_kog3():
    d = f"{W}/kog3"
    if os.path.exists(f"{d}/DONE"):
        return
    for grp, (k, x, mx, base, (nk, nx)) in groups().items():
        wr(f"{d}/{nk}", fresh(rd(k), base, ("kog3", "kog3")))
    wr(f"{d}/{PX}_d_kog3.jsonl", x4(rd(f"{O}/ec7e1a8_d_kog3.jsonl"), ("kog3", "kog3")))
    for deck in AB:
        wr(f"{d}/{PX}_ab_d{deck}_kog3.jsonl", ab_fresh(rd(f"{O}/ec7e1a8_ab_d{deck}_kog3.jsonl")))
    open(f"{d}/DONE", "w").write("ok\n")


def build_base(kind):
    """base_null: kta3 = kog3's games everywhere; base_dev: kta3 = kt's development kta3 games. src/ only."""
    d = f"{W}/base_{kind}/src"
    if os.path.exists(f"{d}/DONE"):
        return
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(f"{W}/kog3"):
        if f.endswith(".jsonl"):
            link(f"{W}/kog3/{f}", f"{d}/{f}")
    for grp, (k, x, mx, base, (nk, nx)) in groups().items():
        wr(f"{d}/{nx}", fresh(rd(k if kind == "null" else x), base, ("kta3", "kta3")))
        for dr, (src, bots, full, run) in mx.items():
            if kind == "null":
                if grp.startswith("var_"):
                    side = {int(r["pairing"]): r["variant_side"] for r in csv.DictReader(open(f"{TSV}/var_{grp[4:]}.tsv", encoding="utf-8"), delimiter="\t")}
                    wr(f"{d}/{full}", fresh(rd(k), base, bots, keep=lambda g, s=dr: side[g["pairing"]] == s))
                else:
                    wr(f"{d}/{full}", fresh(rd(k), base, bots))
            else:
                wr(f"{d}/{full}", fresh(rd(src), base, bots))
    wr(f"{d}/{PX}_d_kta3.jsonl", x4(rd(f"{O}/ec7e1a8_d_{'kog3' if kind == 'null' else 'kta3'}.jsonl"), ("kta3", "kog3")))
    for deck in AB:
        wr(f"{d}/{PX}_ab_d{deck}_kta3.jsonl", ab_fresh(rd(f"{O}/ec7e1a8_ab_d{deck}_{'kog3' if kind == 'null' else 'kta3'}.jsonl"), "kta3"))
    open(f"{d}/DONE", "w").write("ok\n")


def scenario(name, base):
    d = f"{W}/{name}"
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(f"{d}/src")
    for f in os.listdir(f"{W}/base_{base}/src"):
        if f.endswith(".jsonl"):
            link(f"{W}/base_{base}/src/{f}", f"{d}/src/{f}")
    return d


def redo(d, name, mut, keep=None):
    recs = rd(f"{d}/src/{name}")
    out = []
    for g in recs:
        if keep and not keep(g):
            continue
        mut(g)
        out.append(g)
    wr(f"{d}/src/{name}", out)


def equal5(r, s):
    return all(r.get(k) == s.get(k) for k in ("moves", "a", "b", "seed", "first_seat", "a_file", "b_file"))


def page(p, bots):
    open(p[:-len(".jsonl")] + ".txt", "w").write(PAGE.format(bots=bots))


def cache_dir(tag, files, extra=""):
    sig = hashlib.sha1((tag + "|" + "|".join(os.path.realpath(f) for f in files) + "|" + extra).encode()).hexdigest()[:16]
    return f"{W}/cache/{tag}_{sig}"


def finalize(d, lie=()):
    """The runner's files in d/run, from d/src: both sides and (d) and the A/B linked; the 45 cells' mixed rows by 5.2 (c)
    (5.3 on the ordinary route); coverage mixed rows only where both-sides games differ; coverage_skip.txt; the records."""
    run = f"{d}/run"
    shutil.rmtree(run, ignore_errors=True)
    os.makedirs(run)
    G = groups()
    for f in os.listdir(f"{d}/src"):
        if f.endswith(".jsonl") and ".full." not in f:
            link(f"{d}/src/{f}", f"{run}/{f}")
            if "_ab_" not in f:
                page(f"{run}/{f}", "stand-in")
    # the 45 cells
    srcs = [f"{d}/src/{n}" for grp in ("table", "new17") for n in G[grp][4]] + [f"{d}/src/{G[grp][2][dr][2]}" for grp in ("table", "new17") for dr in ("first", "second")]
    cd = cache_dir("g45", srcs)
    if not os.path.exists(f"{cd}/DONE"):
        os.makedirs(cd, exist_ok=True)
        key = lambda g: (g["a"], g["b"], g["i"])  # noqa: E731
        kog = {key(g): g for grp in ("table", "new17") for g in rd(f"{d}/src/{G[grp][4][0]}")}
        kta = {key(g): g for grp in ("table", "new17") for g in rd(f"{d}/src/{G[grp][4][1]}")}
        diff = [k for k in kog if kog[k]["moves"] != kta[k]["moves"]]
        n = len(diff)
        fp = 100 * n / len(kog)
        route = "reserve route (a)-(e)" if 100 * n < 15 * len(kog) else "ordinary adoption rule"
        open(f"{cd}/footprint.txt", "w").write(f"FOOTPRINT kta3: {n} of {len(kog)} paired games on the 45 cells differ from kog3's = {fp:.2f}% -> {route}\n")
        active = {(k[0], k[1]) for k in diff}
        allcells = route.startswith("ordinary")
        for grp in ("table", "new17"):
            for dr in ("first", "second"):
                src, bots, full, runname = G[grp][2][dr]
                keep = [g for g in rd(f"{d}/src/{full}") if allcells or (g["a"], g["b"]) in active or g["i"] < 40]
                wr(f"{cd}/{runname}", keep)
                page(f"{cd}/{runname}", bots)
        open(f"{cd}/DONE", "w").write("ok\n")
    for f in os.listdir(cd):
        if f != "DONE":
            link(f"{cd}/{f}", f"{run}/{f}")
    # coverage
    skip_lines = ["coverage_skip (stand-in): kta3 v kog3 both-sides games compared deal by deal on moves, a, b, seed, first_seat"]
    for grp in ["b2e", "scizor"] + [f"var_{v}" for v in VARS]:
        k_, x_, mx, base, (nk, nx) = G[grp]
        srcs = [f"{d}/src/{nk}", f"{d}/src/{nx}"] + [f"{d}/src/{mx[dr][2]}" for dr in mx]
        mylie = sorted(p for g_, p in lie if g_ == grp)
        cd = cache_dir(grp, srcs, str(mylie))
        if not os.path.exists(f"{cd}/DONE"):
            os.makedirs(cd, exist_ok=True)
            kog = {(g["pairing"], g["i"]): g for g in rd(f"{d}/src/{nk}")}
            kta = {(g["pairing"], g["i"]): g for g in rd(f"{d}/src/{nx}")}
            ps = sorted({p for p, _ in kog})
            eq, nd = dict.fromkeys(ps, 0), dict.fromkeys(ps, 0)
            for (q, i), g in kog.items():
                nd[q] += 1
                eq[q] += equal5(g, kta[(q, i)])
            lines = []
            for p in ps:
                if p in mylie:   # the planted lie: the comparison says SKIP whatever the deals say
                    lines.append(f"SKIP {grp} {p}: {nd[p]} of {nd[p]} deals equal on moves, a, b, seed, first_seat")
                else:
                    lines.append(f"{'SKIP' if eq[p] == nd[p] else 'RUN'} {grp} {p}: {eq[p]} of {nd[p]} deals equal on moves, a, b, seed, first_seat")
            open(f"{cd}/skip.txt", "w").write("\n".join(lines) + "\n")
            for dr, (src, bots, full, runname) in mx.items():
                keep = [g for g in rd(f"{d}/src/{full}") if eq[g["pairing"]] != nd[g["pairing"]] and g["pairing"] not in mylie]
                if keep:
                    wr(f"{cd}/{runname}", keep)
                    page(f"{cd}/{runname}", bots)
            open(f"{cd}/DONE", "w").write("ok\n")
        for f in os.listdir(cd):
            if f not in ("DONE", "skip.txt"):
                link(f"{cd}/{f}", f"{run}/{f}")
        skip_lines += open(f"{cd}/skip.txt").read().splitlines()
    open(f"{run}/coverage_skip.txt", "w").write("\n".join(skip_lines) + "\n")
    # the records (synthetic, in the runner's line formats)
    labels = [(f"{c} {g} i<20 v {ref}", n) for c in ("kog3", "kta3") for g, n, ref in
              (("45 cells", 900, "ec7e1a8 development files"), ("Scizor", 160, "scizor"), ("B2e", 1920, "b2e"),
               ("second lists", 580, "var_*"), ("clause (d)", 160, "ec7e1a8_d"))] + [("A/B tool deck 07 kog3", 240), ("A/B tool deck 07 kta3", 240)]
    with open(f"{run}/identity_check.txt", "w") as f:
        for lab, n in labels:
            f.write(f"{lab}: {n} of {n} equal on ['moves', 'decisions', 'openings', 'winner_seat', 'points', 'seed']\n")
    open(f"{run}/{PX}_timing_1.txt", "w").write("kog3 61 s wall, 720 s CPU; kta3 64 s wall, 752 s CPU; kta3/kog3 wall 1.05 (limit 1.25: within), CPU 1.04\n")
    for arm in ("kog3", "kta3"):   # the counters' pages (reported only): kt's development ones, for the Stiffen line's format
        link(f"{O}/ec7e1a8_census_{arm}.txt", f"{run}/{PX}_census_{arm}.txt")
    traces(run)


TRACE_KINDS = [("Attack", "Scorching Interruption"), ("AttachTool", "Steel Apron"), ("EndTurn", None), ("Retreat", None)]


def traces(run):
    """The Rayquaza traces (run_kta.sh step 7), stand-ins: kt's development per-game rows (v Lucario, kta3 and kog3, 200
    games, Scorching Interruption offered 220 / used 151 and 223 / 150, wins 60 and 59) relabelled onto each opponent's
    fresh seeds, and synthetic kta_trace_moves.py rows: equal decisions where the two arms' per-game rows are equal; where
    they differ, equal up to a known ply, then kta3's choice is one of TRACE_KINDS (by the seed's hash)."""
    src = {arm: rd(f"{O}/ec7e1a8_trace_rayquaza_{arm}_pergame.jsonl") for arm in ("kta3", "kog3")}
    for opp, s0 in (("lucario", 23_005_000_000), ("vespiquen", 23_005_001_000)):
        pg = {arm: {g["seed"] - 21_108_900_000 + s0: {**g, "seed": g["seed"] - 21_108_900_000 + s0} for g in rows}
              for arm, rows in src.items()}
        for arm in pg:
            wr(f"{run}/{PX}_trace_rayquaza_{opp}_{arm}_pergame.jsonl", [pg[arm][s] for s in sorted(pg[arm])])
        for arm in pg:
            out = []
            for s in sorted(pg[arm]):
                hs = int(hashlib.md5(f"trace:{s}".encode()).hexdigest()[:8], 16)
                differ = pg["kta3"][s] != pg["kog3"][s]   # the development arms differ in this game's result or attacks
                j0 = 2 * (hs % 4) + 2                      # an even ply: seat 0's (Rayquaza's) decision
                decs = []
                for j in range(30):
                    mine = arm == "kta3" and differ and j >= j0
                    h = hashlib.md5(f"{'x' if mine else 'k'}:{s}:{j}".encode()).hexdigest()[:8]
                    kind, lab = (TRACE_KINDS[hs % 4] if mine and j == j0 else ("Play", "Poke Ball"))
                    decs.append([j, j % 2, j // 2, 3, kind, lab, h])
                out.append({"seed": s, "won": pg[arm][s]["won"], "draw": False, "turns": pg[arm][s]["final_turn"], "plies": 30,
                            "moves": hashlib.md5("".join(d[6] for d in decs).encode()).hexdigest()[:16], "decisions": decs,
                            "pilot": arm, "opp_pilot": "kog3"})
            wr(f"{run}/{PX}_trace_rayquaza_{opp}_{arm}_moves.jsonl", out)


LIM = None


def limitless():
    global LIM
    if LIM is None:
        v2 = json.load(open(f"{RES}/scoreboard_v2_2026-09-25/limitless_v2_dev.json"))["cells"]
        LIM = {tuple(k.split("|")): tuple(v) for k, v in v2.items()}
        gc = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(open(f"{RES}/gauntlet_runs_2026-09-26/gauntlet_cells.csv"))}
        panel = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
        for a, b in [(x, o) for x in ("rayquaza", "altaria_greninja") for o in panel] + [("rayquaza", "altaria_greninja")]:
            r = gc[("development", a, b)]
            LIM[(a, b)] = (int(r["W"]), int(r["L"]), int(r["T"]))
    return LIM


REACH = lambda g: "suicune" in (g["a"], g["b"]) or "rayquaza" in (g["a"], g["b"])  # noqa: E731


def move_results(d, how, move_frac=0):
    """kta3's both-sides results in the 17 reach cells: 'away' pushes about 10% of a cell's games away from its Limitless
    figure; 'toward' moves the cell halfway to it. move_frac: the share of the reach cells' games whose moves change."""
    lim = limitless()
    for grp in ("table", "new17"):
        name = f"{PX}_kta3_{grp}.jsonl"
        recs = rd(f"{d}/src/{name}")
        cells = {}
        for g in recs:
            if REACH(g):
                cells.setdefault((g["a"], g["b"]), []).append(g)
        for cell, gs in cells.items():
            w, l, t = lim[cell]
            L = (w + 0.5 * t) / (w + l + t)
            s = sum(g["first_deck_score"] for g in gs) / len(gs)
            if move_frac:
                for g in gs:
                    if H("mf", g) % 100 < 100 * move_frac:
                        newmoves(g, "#")
            if how == "away":
                k, target = round(0.10 * len(gs)), (1.0 if s >= L else 0.0)
            else:
                k, target = round(abs(L - s) * 0.5 * len(gs)), (0.0 if L < s else 1.0)
            pool = sorted((g for g in gs if g["first_deck_score"] == 1.0 - target), key=lambda g: H("mv", g))
            for g in pool[:k]:
                flip(g, target)
        wr(f"{d}/src/{name}", recs)


def d_gain(g):
    if g["first_deck_score"] == 0.0 and H("dgain", g) % 30 == 0:
        flip(g, 1.0)


def ab07(d, src, pilot):
    """Replace deck 07's A/B file of arm `pilot` in d/src by the file `src` (under W), relabelled to that pilot."""
    recs = rd(f"{W}/{src}")
    for g in recs:
        g["pilot"] = pilot
    wr(f"{d}/src/{PX}_ab_d07_{pilot}.jsonl", recs)


DEV_AB07 = f"base_dev/src/{PX}_ab_d07_kta3.jsonl"    # kta3's development A/B on deck 07 (Jasmine 30.2%)
KOG_AB07 = f"kog3/{PX}_ab_d07_kog3.jsonl"           # kog3's (Jasmine 0.4%)


def jas_up(g):   # kog3 plays Jasmine on every turn she is offered (the guard's plant)
    if "Jasmine" in g["plays"]:
        o, _ = g["plays"]["Jasmine"]
        g["plays"]["Jasmine"] = [o, o]


build_kog3()
build_base("null")
build_base("dev")
if scn in ("null", "dev"):
    d = scenario(scn, scn)
    finalize(d)
elif scn in ("gain", "harm", "reach", "explained", "reach_harm", "c0", "jas_low", "guard", "skip_winners", "skip_unnamed",
             "skip_noreport"):
    d = scenario(scn, "null")
    redo(d, f"{PX}_d_kta3.jsonl", d_gain)
    ab07(d, DEV_AB07, "kta3")      # kta3's development A/B (Jasmine 30%)
    lie = ()
    if scn in ("harm", "reach_harm"):
        def fp_sui(g):
            if "suicune" in (g["a"], g["b"]) and H("fp", g) % 10 == 0:
                newmoves(g, "fp")
        for grp in ("table", "new17"):
            redo(d, f"{PX}_kta3_{grp}.jsonl", fp_sui)
            for dr, who in (("first", "a"), ("second", "b")):
                def hurt(g, dr=dr, who=who):
                    if g[who] == "suicune" and H("sui", g) % 3 == 0:
                        if dr == "first" and g["first_deck_score"] == 1.0:
                            flip(g, 0.0)
                        if dr == "second" and g["first_deck_score"] == 0.0:
                            flip(g, 1.0)
                redo(d, f"{PX}_mixed_{grp}_kta3_{dr}.full.jsonl", hurt)
        redo(d, f"{PX}_b2e_kta3.jsonl", lambda g: g["pairing"] == 4 and H("fpb", g) % 10 == 0 and newmoves(g, "b"))
        redo(d, f"{PX}_mixed_b2e_kta3_first.full.jsonl", lambda g: g["pairing"] == 4 and g["first_deck_score"] == 1.0 and H("b2e", g) % 2 == 0 and flip(g, 0.0))
        redo(d, f"{PX}_scizor_kta3.jsonl", lambda g: H("fps", g) % 10 == 0 and newmoves(g, "s"))
        redo(d, f"{PX}_mixed_scizor_kta3_first.full.jsonl", lambda g: g["first_deck_score"] == 1.0 and H("scz", g) % 3 == 0 and flip(g, 0.0))
    if scn in ("reach", "explained", "reach_harm"):
        seen = []
        def one(g):
            if not seen and (g["a"], g["b"]) == ("altaria", "blaziken") and g["i"] == 7:
                seen.append(1)
                newmoves(g, "reach")
        redo(d, f"{PX}_kta3_table.jsonl", one)
        if scn in ("explained", "reach_harm"):
            open(f"{d}/explanation.txt", "w").write("Stand-in explanation (test only): the changed Altaria v Blaziken game was planted by "
                                                     "test_read_kta.sh to exercise the integrity line.\n")
    if scn == "c0":
        seen = []
        def one(g):
            if not seen and (g["a"], g["b"]) == ("altaria", "blaziken") and g["i"] == 5:
                seen.append(1)
                newmoves(g, "c0")
        redo(d, f"{PX}_mixed_table_kta3_first.full.jsonl", one)
    elif scn == "jas_low":
        ab07(d, KOG_AB07, "kta3")
    elif scn == "guard":
        redo(d, f"{PX}_ab_d07_kog3.jsonl", jas_up)
    elif scn == "skip_winners":
        seen = []
        def one(g):
            if not seen and g["pairing"] == 4 and g["i"] == 3:
                seen.append(1)
                newmoves(g, "win")   # the moves differ; the result (the winner) does not
        redo(d, f"{PX}_b2e_kta3.jsonl", one)
        lie = (("b2e", 4),)
    finalize(d, lie)
    if scn == "skip_unnamed":
        ls = open(f"{d}/run/coverage_skip.txt").read().splitlines()
        open(f"{d}/run/coverage_skip.txt", "w").write("\n".join(l for l in ls if not l.startswith("SKIP b2e 0:")) + "\n")
    elif scn == "skip_noreport":
        os.remove(f"{d}/run/coverage_skip.txt")
elif scn in ("worsen", "worsen_ord", "ord_below", "ord_reach", "worsen_reach"):
    d = scenario(scn, "null")
    redo(d, f"{PX}_d_kta3.jsonl", d_gain)
    if scn == "ord_below":
        ab07(d, KOG_AB07, "kta3")                    # Jasmine low: reported only when below
    else:
        ab07(d, DEV_AB07, "kta3")
    move_results(d, "toward" if scn == "ord_below" else "away", 0 if scn in ("worsen", "worsen_reach") else 0.5)
    if scn in ("ord_reach", "worsen_reach"):
        seen = []
        def one(g):
            if not seen and (g["a"], g["b"]) == ("altaria", "blaziken") and g["i"] == 7:
                seen.append(1)
                newmoves(g, "reach")
        redo(d, f"{PX}_kta3_table.jsonl", one)
        open(f"{d}/explanation.txt", "w").write("Stand-in explanation (test only): planted by test_read_kta.sh.\n")
    finalize(d)
elif scn in ("jas_low_below", "guard_below", "mixed_missing"):
    d = scenario(scn, "dev")
    if scn == "jas_low_below":
        ab07(d, KOG_AB07, "kta3")
    elif scn == "guard_below":
        redo(d, f"{PX}_ab_d07_kog3.jsonl", jas_up)
    finalize(d)
    if scn == "mixed_missing":
        f = f"{d}/run/{PX}_mixed_b2e_kta3_first.jsonl"
        recs = [g for g in rd(f) if g["pairing"] != 4]
        wr(f, recs)
elif scn in ("edge3374", "edge3375"):
    n = int(scn[4:])
    d = scenario(scn, "null")
    redo(d, f"{PX}_d_kta3.jsonl", d_gain)
    ab07(d, DEV_AB07, "kta3")
    recs = {grp: rd(f"{d}/src/{PX}_kta3_{grp}.jsonl") for grp in ("table", "new17")}
    order = sorted((H("edge", g), grp, j) for grp in recs for j, g in enumerate(recs[grp]) if REACH(g))
    for _, grp, j in order[:n]:
        newmoves(recs[grp][j], "#")
    for grp in recs:
        wr(f"{d}/src/{PX}_kta3_{grp}.jsonl", recs[grp])
    finalize(d)
print("built", scn)
EOF

show() {  # sections 1 (to NOTES) and 9 (the verdict) of a reader run; the full output stays in the folder
  if [ "${FULL:-0}" = 1 ]; then cat "$1"; return; fi
  sed -n '/^1\. THE FOOTPRINT/,/^NOTES/p' "$1" | sed '$d' | grep -v -E '^   (FOOTPRINT|predicted|cross-check)' || true
  if [ -n "${EXTRA:-}" ]; then echo "   [...selected lines, EXTRA=$EXTRA...]"; grep -E "$EXTRA" "$1" | cut -c1-300 || true; fi
  echo "   [...sections 2-8 omitted here; the full output is $1]"
  sed -n '/^9\. VERDICT/,/THE OUTCOMES THE REGISTRATION FIXES/p' "$1" | sed '$d'
}
# ---- the checks: every scenario states what its output must say; a miss is counted, listed at the end, and the script
# then exits 1 (a script that only ran shows nothing).
NCHK=0; FAILS=(); LAST=""; LASTLAB=""
check() {  # output-file label ERE...: each ERE must match a line of the output
  local f=$1 lab=$2 pat; shift 2
  for pat in "$@"; do
    NCHK=$((NCHK + 1))
    if grep -qE -- "$pat" "$f"; then echo "   [check ok] $pat"
    else echo "   [CHECK FAILED] not found: $pat"; FAILS+=("$lab -- not found: $pat"); fi
  done
}
lacks() {  # output-file label ERE...: no line of the output may match
  local f=$1 lab=$2 pat; shift 2
  for pat in "$@"; do
    NCHK=$((NCHK + 1))
    if grep -qE -- "$pat" "$f"; then echo "   [CHECK FAILED] found, must not be: $pat"; FAILS+=("$lab -- found, must not be: $pat")
    else echo "   [check ok] absent: $pat"; fi
  done
}
also() { check "$LAST" "$LASTLAB" "$@"; }    # more lines the last reader output must have
never() { lacks "$LAST" "$LASTLAB" "$@"; }   # lines it must not have
# The verdict lines (section 9 of the reader's output).
V_AD='^   => kta3 is ADOPTED as the working pilot'
V_NA='^   => kta3 is NOT ADOPTED; kog stays the working pilot\. The test\(s\) that failed: '
V_HELD='^   => HELD; once explained: '
V_PEND='^   => PENDING: '

run_reader() {  # folder label expected-ERE extra-args...
  local dir=$1 label=$2 want=$3; shift 3
  echo; echo "################ $label"
  mkdir -p "$dir/pages"
  set +e
  nice -n 19 python3 "$O/read_kta.py" --dir "$dir" --pages-dir "$dir/pages" --reps "$REPS" "$@" > "$dir/reader_output.txt" 2>&1
  local rc=$?
  set -e
  echo "(exit code $rc)"
  if [ $rc -ne 0 ]; then tail -n 3 "$dir/reader_output.txt" | cut -c1-600; else show "$dir/reader_output.txt"; fi
  LAST="$dir/reader_output.txt"; LASTLAB=$label
  if [ $rc -ne 0 ]; then also '^STOP: '; fi          # a nonzero exit is only ever a STOP, never a crash
  also "$want"
  return 0
}
build() { nice -n 19 python3 "$W/make_standin.py" "$R" "$W" "$1"; }

echo "################ unit: --selftest"
mkdir -p "$W/unit"
set +e
python3 "$O/read_kta.py" --selftest > "$W/unit/selftest.txt" 2>&1
set -e
cat "$W/unit/selftest.txt"
check "$W/unit/selftest.txt" "unit: --selftest" '^selftest ok: '
echo; echo "################ unit: --parse-page on the earlier real score45 pages (none is kta's)"
set +e
: > "$W/unit/parse_pages.txt"
while IFS= read -r p; do
  out=$(python3 "$O/read_kta.py" --parse-page "$p" 2>&1); rc=$?
  echo "  ${p#$R/rl/results/}: $(echo "$out" | head -n 1 | cut -c1-140) (exit $rc)" | tee -a "$W/unit/parse_pages.txt"
done < <(find "$R/rl/results" -name 'score45_*.txt' -not -path '*kta*' | sort)
KP="$R/rl/results/koh_2026-09-28/laptop_reading/score45_koh3_vs_kog3.txt"
grep -v '^    deck hydreigon +3.7' "$KP" > "$W/unit/drop_deck_line.txt"
python3 "$O/read_kta.py" --parse-page "$W/unit/drop_deck_line.txt" > "$W/unit/drop_deck_out.txt" 2>&1
echo "  koh's page, a deck-veto line dropped: exit $?: $(head -n 1 "$W/unit/drop_deck_out.txt" | cut -c1-200)"
set -e
check "$W/unit/parse_pages.txt" "unit: --parse-page" '^  .*: PARSED all: .*\(exit 0\)$'
lacks "$W/unit/parse_pages.txt" "unit: --parse-page" '\(exit [1-9][0-9]*\)$'
check "$W/unit/drop_deck_out.txt" "unit: a deck-veto line dropped" '^STOP: .*the parse missed or invented a veto line'

for s in null dev gain harm worsen worsen_ord ord_below ord_reach worsen_reach jas_low jas_low_below guard guard_below skip_winners \
         skip_unnamed skip_noreport mixed_missing reach explained reach_harm c0 edge3374 edge3375; do build $s; done

EXTRA='^   (ΔMSE|LABEL|τ̂ margin|real error|detectable)|pooled over 8 rows|JASMINE LINE|^   deck 07 |held-out direction:|^     (b2e|scizor|var_)|^     kog3 [0-9]+ of [0-9]+ \(|^     v (lucario|vespiquen)|^       (the first|in detail)' \
  REPS=$REPS_DEV run_reader "$W/dev/run" "dev: kt's development games relabelled onto fresh seeds, --reps $REPS_DEV (must match the development reading)" "$V_AD"
also 'kta3: 559 of 22,500 = 2\.4844% .* THE RESERVE ROUTE' 'ΔMSE \(kta3 minus kog3\): -5\.9 points\^2, 95% interval -11\.0 to -1\.4;' \
     'LABEL .*: wholly BELOW zero' 'τ̂ margin \(kog3 minus kta3\): \+0\.21, 90% interval \+0\.06 to \+0\.31;' \
     'pooled over 8 rows \(16,000 deals per arm\): \+1\.00 \+/- 0\.19 points -> a GAIN' \
     'JASMINE LINE \(5\.5\): kta3 1,711 of 5,669 = 30\.18% reaches 20%; guard: kog3 36 of 8,597 = 0\.42%' \
     'deck 07 \(the reason .*\): \+8\.5 points \(\+6\.7 to \+10\.4\) -> REPLICATED' \
     "v lucario: Scorching Interruption turns offered / used: kta3 220 / 151, kog3 223 / 150; Rayquaza's wins: kta3 60, kog3 59 of 200" \
     'v vespiquen: Scorching Interruption turns offered / used: kta3 220 / 151' '^       the first decision that differs, by kind \(kta3.s choice\)'
EXTRA='LABEL|JASMINE LINE|pooled over 8 rows' run_reader "$W/null/run" "null: kta3 = kog3's own games everywhere" "${V_NA}gain, mechanism\.$"
also 'LABEL .*: SPANS zero' 'This is never an accuracy negative'; never "${V_NA}.*accuracy-worsening"
EXTRA='LABEL|JASMINE LINE|pooled over 8 rows' run_reader "$W/gain/run" "gain: planted (d) gain + kta3's development A/B; ΔMSE spans zero, so the fallback" "$V_AD"
also 'the fallback.s four tests all held'
EXTRA='WORSE|VETO|own side:' run_reader "$W/harm/run" "harm: own-side harm on Suicune, B2e Manectric v Suicune and Scizor" "${V_NA}harm, coverage\.$"
EXTRA='^   (ΔMSE|LABEL)' run_reader "$W/worsen/run" "worsen: results pushed away from Limitless in the 17 reach cells (footprint under 15%)" "${V_NA}accuracy-worsening\.$"
also 'LABEL .*: wholly ABOVE zero'
EXTRA='^   (ΔMSE|LABEL)|^1c|integrity line:' run_reader "$W/worsen_ord/run" "worsen_ord: the same with a footprint of about 19%: the ordinary rule" "${V_NA}accuracy-worsening\.$"
also 'THE ORDINARY RULE \(5\.3'
EXTRA='^   (ΔMSE|LABEL)|JASMINE LINE' run_reader "$W/ord_below/run" "ord_below: ordinary route, ΔMSE wholly below zero, Jasmine low (reported only)" "$V_AD"
also 'THE ORDINARY RULE \(5\.3' 'LABEL .*: wholly BELOW zero'
run_reader "$W/ord_reach/run" "ord_reach: ordinary route with a changed game outside the reach cells (must STOP at 1c)" \
  '^STOP: the footprint is .* and the integrity line is not clean'
run_reader "$W/ord_reach/run" "ord_reach explained: the same with --integrity-explained (reads on)" "${V_NA}accuracy-worsening\.$" \
  --integrity-explained "$W/ord_reach/explanation.txt"
also '^INTEGRITY LINES EXPLAINED BY A HUMAN'
EXTRA='^   (ΔMSE|LABEL)|INTEGRITY' run_reader "$W/worsen_reach/run" "worsen_reach: worsen (ΔMSE wholly above zero) + a changed game outside the reach cells: the integrity line holds even 'above'" \
  "${V_HELD}NOT ADOPTED \(accuracy-worsening\)\."
also 'LABEL .*: wholly ABOVE zero'; never "${V_NA}"
run_reader "$W/worsen_reach/run" "worsen_reach explained: the same with --integrity-explained" "${V_NA}accuracy-worsening\.$" \
  --integrity-explained "$W/worsen_reach/explanation.txt"
EXTRA='JASMINE LINE|LABEL' run_reader "$W/jas_low/run" "jas_low: kta3's deck-07 Jasmine rate below 20%, ΔMSE spans zero" "${V_NA}mechanism\.$"
EXTRA='JASMINE LINE|LABEL|^   deck 07 ' run_reader "$W/jas_low_below/run" "jas_low_below: the same with ΔMSE wholly below zero (development games): reported only" "$V_AD"
also 'DID NOT REPLICATE on fresh deals'
EXTRA='JASMINE LINE|LABEL' run_reader "$W/guard/run" "guard: kog3's own deck-07 Jasmine rate at 20% or more, ΔMSE spans zero" "${V_NA}mechanism\.$"
also "JASMINE LINE \(5\.5\): GUARD: kog3's own rate"
EXTRA='JASMINE LINE|LABEL' run_reader "$W/guard_below/run" "guard_below: the same with ΔMSE wholly below zero: reported only" "$V_AD"
also "JASMINE LINE \(5\.5\): GUARD: kog3's own rate"
EXTRA='COVERAGE SHORTCUT|b2e:' run_reader "$W/skip_winners/run" "skip_winners: coverage_skip.txt skips B2e pairing 4 although one deal's moves differ (same winner)" "$V_PEND"
also 'COVERAGE SHORTCUT \(K9\): b2e pairing 4: coverage_skip.txt says SKIP, but 1 of 500 deals differ .*matching winners alone is not enough'
EXTRA='COVERAGE SHORTCUT' run_reader "$W/skip_unnamed/run" "skip_unnamed: a skipped B2e pairing not named in coverage_skip.txt" "$V_PEND"
also 'COVERAGE SHORTCUT \(K9\): b2e pairing 0: skipped without being named in coverage_skip.txt \(holds its test\)'
EXTRA='COVERAGE SHORTCUT|coverage_skip.txt:' run_reader "$W/skip_noreport/run" "skip_noreport: no coverage_skip.txt" "$V_PEND"
also 'coverage_skip.txt: NOT in yet' 'skipped, and coverage_skip.txt is not in to name it'
EXTRA='COVERAGE SHORTCUT' run_reader "$W/mixed_missing/run" "mixed_missing: B2e pairing 4's games differ but its mixed rows are not in the file" "$V_PEND"
also 'COVERAGE SHORTCUT \(K9\): b2e pairing 4 \(first\): [0-9]+ deals differ and the mixed-row file has no rows for it'
run_reader "$W/reach/run" "reach: one changed game in Altaria v Blaziken (no switch-1 card): the integrity line holds the reading" "${V_HELD}ADOPTED\."
also '^        INTEGRITY LINE \(holds the reading; never a registered fail\): 1 changed games in 1 cells whose lists carry no switch-1 card: altaria v blaziken'
run_reader "$W/reach/run" "reach, explained: the same with --integrity-explained" "$V_AD" --integrity-explained "$W/explained/explanation.txt"
EXTRA='WORSE|VETO|INTEGRITY' run_reader "$W/reach_harm/run" "reach_harm: harm + the same out-of-reach game: HELD before the failures, NOT ADOPTED shown as what explaining gives" \
  "${V_HELD}NOT ADOPTED \(harm, coverage\)\."
never "${V_NA}"
run_reader "$W/reach_harm/run" "reach_harm explained: the same with --integrity-explained" "${V_NA}harm, coverage\.$" \
  --integrity-explained "$W/reach_harm/explanation.txt"
EXTRA='INTEGRITY' run_reader "$W/c0/run" "c0: a sampled mixed-row game in a zero-footprint cell differs from kog3's" "${V_HELD}ADOPTED\."
also 'INTEGRITY LINE .*: 1 mixed-row games in 1 zero-footprint cells differ from kog3.s moves'
run_reader "$W/edge3374/run" "edge3374: exactly 3,374 of 22,500 games differ (14.9956%, prints 15.00): the RESERVE route" \
  'kta3: 3,374 of 22,500 = 14\.9956% \(15% is 3,375 games\) -> THE RESERVE ROUTE \(5\.2\)'
also "$V_AD"
run_reader "$W/edge3375/run" "edge3375: exactly 3,375 of 22,500 games differ (15.0000%): the ORDINARY rule" \
  'kta3: 3,375 of 22,500 = 15\.0000% \(15% is 3,375 games\) -> THE ORDINARY RULE \(5\.3'
also "$V_AD"

# ---- guards, on copies of a tree made of symlinks
G="$W/guards"; rm -rf "$G"; mkdir -p "$G"
mk() {  # name [source tree, default gain]
  local src=${2:-gain}
  rm -rf "$G/$1"; mkdir -p "$G/$1"
  for f in "$W/$src/run"/*; do
    [ -f "$f" ] || continue                                   # never a folder (the pages)
    case $(basename "$f") in reader_output.txt|reuse_output.txt) continue;; esac   # a reader would write through the link
    ln -s "$(readlink -f "$f")" "$G/$1/$(basename "$f")"
  done
}
rewrite() {  # guard-folder file python-expression-on-records (rs: the list of records)
  local f="$G/$1/$2"; local src; src=$(readlink -f "$f"); rm "$f"
  python3 - "$src" "$f" "$3" <<'EOF'
import json, sys
rs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
exec(sys.argv[3])
open(sys.argv[2], "w", encoding="utf-8").write("".join(json.dumps(g, sort_keys=True) + "\n" for g in rs))
EOF
}
doctor() {  # guard-folder python-code-on-t: edit the score45 page a first reader run left in <folder>/pages (t: its text)
  local p="$G/$1/pages/score45_kta3_vs_kog3.txt"
  python3 - "$p" "$2" <<'EOF'
import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t0 = t
exec(sys.argv[2])
assert t != t0, "the doctored page did not change"
open(p, "w", encoding="utf-8").write(t)
EOF
}
mk nofp; rm "$G/nofp/footprint.txt"
run_reader "$G/nofp" "guard: no footprint.txt (refuses before reading anything)" '^STOP: .*/footprint\.txt does not exist'
mk short; rewrite short ${PX}_kta3_new17.jsonl 'rs[:] = rs[:8400]'
run_reader "$G/short" "guard: kta3's new-cell file is short (8,400 of 8,500)" '^STOP: .*_kta3_new17\.jsonl: 8400 games, expected 8500'
mk fpoff; rm "$G/fpoff/footprint.txt"; sed 's/^FOOTPRINT kta3: 0 of/FOOTPRINT kta3: 1 of/' "$W/gain/run/footprint.txt" > "$G/fpoff/footprint.txt"
run_reader "$G/fpoff" "guard: footprint.txt disagrees with the files (off by one)" '^STOP: footprint\.txt says 1 games differ; .* give 0'
mk routetext edge3374; rm "$G/routetext/footprint.txt"; sed 's/-> reserve route (a)-(e)$/-> ordinary adoption rule/' "$W/edge3374/run/footprint.txt" > "$G/routetext/footprint.txt"
run_reader "$G/routetext" "guard: footprint.txt's route text (ordinary) against its counts (3,374: reserve)" "^STOP: footprint\.txt's route text .* disagrees"
mk seed; rewrite seed ${PX}_d_kta3.jsonl 'rs[123]["seed"] += 1'
run_reader "$G/seed" "guard: one game of kta3's (d) rows on a different deal" "^STOP: .*_d_kta3\.jsonl: 1 games are not on kta's fresh deals"
mk devseed; rewrite devseed ${PX}_kog3_table.jsonl 'for g in rs: g["seed"] = 72_000_000 + 10_000 * g["pairing"] + g["i"]'
run_reader "$G/devseed" "guard: kog3's table file on the DEVELOPMENT seeds (72,000,000 base), not fresh" "^STOP: .*_kog3_table\.jsonl: 14000 games are not on kta's fresh deals"
mk d500; rewrite d500 ${PX}_d_kog3.jsonl 'rs[:] = [g for g in rs if g["i"] < 500]'; rewrite d500 ${PX}_d_kta3.jsonl 'rs[:] = [g for g in rs if g["i"] < 500]'
run_reader "$G/d500" "guard: clause (d) at 500 deals per row, not the registered 2,000" '^STOP: .*_d_kog3\.jsonl: 4000 games, expected 16000'
mk seat; rewrite seat ${PX}_b2e_kta3.jsonl 'rs[40]["first_seat"] = 1 - rs[40]["first_seat"]'
run_reader "$G/seat" "guard: one kta3 B2e game with its seats swapped (the seat rule and Dustin's 'seats')" '^STOP: .*_b2e_kta3\.jsonl: 1 games break the seat rule'
mk abshort; rewrite abshort ${PX}_ab_d07_kta3.jsonl 'rs[:] = rs[:1900]'
run_reader "$G/abshort" "guard: deck 07's kta3 A/B file is short (1,900 of 1,920)" '^STOP: .*_ab_d07_kta3\.jsonl: 1900 games, expected 1920'
mk idfail; rm "$G/idfail/identity_check.txt"; sed 's/^kog3 B2e i<20 v b2e: 1920 of 1920/kog3 B2e i<20 v b2e: 1919 of 1920/' "$W/gain/run/identity_check.txt" > "$G/idfail/identity_check.txt"
run_reader "$G/idfail" "guard: an identity replay failed (1,919 of 1,920)" '^STOP: IDENTITY FAILED in identity_check\.txt: .*1919 of 1920'
mk idmissing; rm "$G/idmissing/identity_check.txt"
run_reader "$G/idmissing" "guard: no identity record" '^STOP: .*/identity_check\.txt does not exist'
mk idshort; rm "$G/idshort/identity_check.txt"; grep -v 'A/B tool' "$W/gain/run/identity_check.txt" > "$G/idshort/identity_check.txt"
run_reader "$G/idshort" "guard: the identity record lacks the A/B tool check (7,440 of 7,920 games)" '^STOP: identity_check\.txt records 7,440 equal games'
mk timeover; rm "$G/timeover/${PX}_timing_1.txt"; echo "kog3 61 s wall, 720 s CPU; kta3 90 s wall, 900 s CPU; kta3/kog3 wall 1.48 (limit 1.25: OVER), CPU 1.25" > "$G/timeover/${PX}_timing_1.txt"
run_reader "$G/timeover" "guard: the timing line is OVER 1.25x" "^STOP: the timing line is not 'within' the 1\.25x limit"
mk rulef; rm "$G/rulef/${PX}_d_kta3.txt"; printf 'bot kta3\n\nFindings (occurrences / games affected):\n  RULE evolve: empty slot: 1 / 1\n      e.g. planted by the test\n' > "$G/rulef/${PX}_d_kta3.txt"
run_reader "$G/rulef" "guard: a RULE finding in a scan page" '^STOP: a RULE finding in a scan page .*_d_kta3\.txt: RULE evolve'
mk nopage; rm "$G/nopage/${PX}_scizor_kta3.txt"
EXTRA='every file read has its scan page' run_reader "$G/nopage" "guard: the scan page of a file read is missing (holds the reading)" "${V_HELD}ADOPTED\."
also '^        every file read has its scan page .*: no scan page with a Findings block beside .*_scizor_kta3\.jsonl'
mk nopage_fail harm; rm "$G/nopage_fail/${PX}_scizor_kta3.txt"
run_reader "$G/nopage_fail" "guard: the same on the harm tree: a missing page holds before the failures" "${V_HELD}NOT ADOPTED \(harm, coverage\)\."
never "${V_NA}"
mkdir -p "$G/fakeengine/examples"; echo fake > "$G/fakeengine/deckgym"; echo fake > "$G/fakeengine/examples/legality_scan"
mk hash; run_reader "$G/hash" "guard: a program whose sha256 is not section 4's" '^STOP: deckgym sha256 [0-9a-f]+ is not the registered' --engine-dir "$G/fakeengine"
mk nomixed; rm "$G/nomixed/${PX}_mixed_table_kta3_second.jsonl" "$G/nomixed/${PX}_mixed_new17_kta3_second.jsonl"
EXTRA='not in yet|mixed rows, kta3' run_reader "$G/nomixed" "guard: the 45 cells' second-direction mixed rows are not in: (c) waits" "$V_PEND"
also 'mixed rows, kta3 on the second-named deck: not in yet' "if the ΔMSE label is 'spans': PENDING: \(c\) no meta deck"
mk dmissing; rm "$G/dmissing/${PX}_d_kta3.jsonl" "$G/dmissing/${PX}_d_kta3.txt"
run_reader "$G/dmissing" "guard: clause (d)'s kta3 rows are not in" "$V_PEND"
also 'the \(d\) rows are not all in yet'
mk ab07below dev; rm "$G/ab07below/${PX}_ab_d07_kta3.jsonl"
run_reader "$G/ab07below" "guard: deck 07's A/B not in, ΔMSE wholly below zero: it holds nothing (Jasmine is reported only)" "$V_AD"
mk ab07spans gain; rm "$G/ab07spans/${PX}_ab_d07_kta3.jsonl"
run_reader "$G/ab07spans" "guard: deck 07's A/B not in, ΔMSE spans zero: the Jasmine line holds the verdict" "$V_PEND"
also "deck 07's A/B files are not in yet"
# the traces (reported only): one arm's file not in holds nothing; a short file STOPs, as every input does
mk notrace; rm "$G/notrace/${PX}_trace_rayquaza_vespiquen_kta3_moves.jsonl"
EXTRA='^     v (lucario|vespiquen)' run_reader "$G/notrace" "guard: one trace file not in (reported only: holds nothing)" "$V_AD"
also "v vespiquen: not in yet \(${PX}_trace_rayquaza_vespiquen_kta3_moves\.jsonl; holds nothing\)" '^     v lucario: Scorching Interruption'
mk traceshort; rewrite traceshort ${PX}_trace_rayquaza_lucario_kog3_pergame.jsonl 'rs[:] = rs[:199]'
run_reader "$G/traceshort" "guard: a trace file short by one game" '^STOP: .*_trace_rayquaza_lucario_kog3_pergame\.jsonl: 199 games, not the seeds 23,005,000,000 to 23,005,000,199'
# the verdict wording on a page with a ΔMSE bound near a line (score45's page edited, then read with --reuse-45)
mk wl worsen; rm "$G/wl/${PX}_d_kta3.jsonl"; ln -s "$(readlink -f "$W/null/run/${PX}_d_kta3.jsonl")" "$G/wl/${PX}_d_kta3.jsonl"
run_reader "$G/wl" "guard: worsen with no (d) gain (kta3's (d) arm = kog3's games): one label, 'above'" "${V_NA}accuracy-worsening\.$"
doctor wl 't = re.sub(r"(dMSE new - current: )[+-][\d.]+( points\^2, 95% interval )[+-][\d.]+ to [+-][\d.]+ \(not below 0\)", r"\g<1>+10.0\g<2>+0.4 to +20.0 (not below 0)", t)'
run_reader "$G/wl" "guard: the same page with the ΔMSE interval +0.4 to +20.0 (lower bound within 5% of the width of 0): NOT ADOPTED under both open labels, the name waits" \
  '^   => kta3 is NOT ADOPTED \(settled under every open label: above and spans\); .*wait for the --reps 20000 rerun' --reuse-45
also '^   page: .*\(reused: ' '^        \[above\] accuracy-worsening$' '^        \[spans\] .*gain' '^      No accuracy negative is recorded' \
     "^      \(d\) \(if the label is 'spans'\) reads 'gain not shown at this size"
never "${V_NA}" 'This is never an accuracy negative'
mk tau gain
run_reader "$G/tau" "guard: the gain tree, first run (its page is edited next)" "$V_AD"
doctor tau 't = re.sub(r"(real error, current minus new: [+-][\d.]+ points, 90% interval )[+-][\d.]+", r"\g<1>-1.10", t, count=1)'
run_reader "$G/tau" "guard: τ̂ lower bound printed -1.10 (exactly 0.10 from the line) at --reps $REPS: PENDING, the 20,000-rep rerun decides" "$V_PEND" --reuse-45
also '^     PENDING +\(b\) τ̂ margin .*: -1\.10 .*MC-BOUNDARY: within 0\.10 of the -1\.0 line'
run_reader "$W/gain/run" "footprint-only: sections 1, 1b, then stop" '^\(--footprint-only: stopped after the footprint' --footprint-only
never '^9\. VERDICT'
echo; echo "################ --reuse-45: the page is reused only when made by the same command on the same inputs at the same --reps"
rm -rf "$W/gain/run/pages"/score45_*
for step in "first run (nothing to reuse yet: scored afresh)|$REPS|freshly scored, --reps $REPS" \
            "second run, same --reps (reused)|$REPS|reused: made by this same command on inputs with the same sha256, --reps $REPS" \
            "third run, another --reps (not reusable: scored afresh)|$((REPS + 50))|freshly scored, --reps $((REPS + 50))"; do
  IFS='|' read -r what reps want <<< "$step"
  set +e
  nice -n 19 python3 "$O/read_kta.py" --dir "$W/gain/run" --pages-dir "$W/gain/run/pages" --reps "$reps" --reuse-45 > "$W/gain/run/reuse_output.txt" 2>&1
  rc=$?
  set -e
  echo "  $what: exit $rc"
  grep -E "^   page:|--reuse-45:|^WARNING" "$W/gain/run/reuse_output.txt" | cut -c1-160 | sed 's/^/     /'
  check "$W/gain/run/reuse_output.txt" "--reuse-45: $what" "^   page: score45_kta3_vs_kog3\.txt \($want\)"
done
echo; echo "stand-in trees and every reader output are under $W"
echo; echo "################ CHECKS: $((NCHK - ${#FAILS[@]})) of $NCHK passed"
if [ ${#FAILS[@]} -gt 0 ]; then
  printf '  FAILED: %s\n' "${FAILS[@]}"
  exit 1
fi
echo "every check passed"

#!/usr/bin/env bash
# Stand-in test for read_km.py (km's reading, written blind), re-based on Amendment 1 (Sept 30): km3 against kta3. No km
# game exists and none is played or read here: every stand-in "km3" file is one of kta3's ec7e1a8 reference files (the
# ones km_config.json names) RELABELLED (km3 = kta3's own games), with known effects planted on top, and every reader
# run passes --dir at a stand-in folder under $W (never a km results folder) and --config at a stand-in config under $W:
# the real km_config.json's candidate, baseline and reference files (with their sha256), and a stand-in B
# (5eedc0de..., prefix 5eedc0d) and stand-in cloud outputs in place of its required values. The file-free modes
# (--selftest, --parse-page on earlier real score45 pages, none of them km's) read no km file at all.
# The stand-in runner files are made the way the registration says the runner makes them: the 45 cells' mixed rows in
# the cells with a changed game (500 deals) plus an i<40 sample elsewhere; coverage mixed rows only in the pairings whose
# both-sides games differ, and coverage_skip.txt naming every pairing; clause (d)'s 9 Lucario rows x 2,000 deals (the
# table's deals 0-499 from kta3's reference files, the 1,500 block deals synthetic on 22,900,000,000 + row x 10,000 + j
# with Lucario in seat 0 on even j); the counter tool's rows (deals 0-199 of the 17 cells, and the threshold sample's
# deals 200-299 of the 14 gating cells) with SYNTHETIC counts that follow the games (a km3 game with kta3's moves carries
# kta3's counts; a changed km3 game gets the scenario's km3 rates); thresholds.json computed from the sample by the
# registered rule (exact midpoint; the stand-in's paired interval uses 1,000 replicates, not 10,000); the runner's
# records (programs.txt naming stand-in programs in a stand-in build folder whose COMMIT is the stand-in B, STATUS.txt's
# "KM PART B DONE" line with the same hashes, identity_check.txt with Amendment 1 (e) item 3's eight checks at their
# sizes); and a stand-in copy of the registration with a stand-in amendment appended (written under $W, never into the
# repo).
# Scenarios (expected verdict in brackets):
#   unit          --selftest; --parse-page on earlier real score45 pages; koh's page with a veto line dropped [STOP].
#   null          km3 = kta3 everywhere: ΔMSE exactly 0 spans zero -> the fallback; (d) no gain; both thresholds
#                 'cannot pass' (the sample's arms are equal). [NOT ADOPTED (gain, mechanism), never an accuracy negative]
#   gain          null + moves changed on 40% of the 14 gating cells' deals 0-299 (km3's counts there at the km3 rates:
#                 M1 about 34% against T about 28%, M2 about 44% against T about 39%) + a planted (d) gain. [spans,
#                 the fallback's four tests hold: ADOPTED]
#   harm          gain + Lucario's own side hurt in the 45 cells' mixed rows, B2e Manectric v Lucario and Scizor hurt.
#                 [NOT ADOPTED (harm, coverage)]
#   worsen        gain + km3's results pushed away from Limitless in the 17 reach cells (under 15%). [ΔMSE wholly above
#                 zero: NOT ADOPTED (accuracy-worsening), no fallback]
#   worsen_ord    the same with moves changed on half the reach cells' games (about 20%): the ordinary rule. [same]
#   below         gain + km3's results moved halfway to Limitless in the reach cells (reserve route), km3's Arena rate
#                 on the gating deals LOW (about 23%, under T). [ΔMSE wholly below zero: M1 reported only: ADOPTED]
#   below_nogain  below without the (d) gain. [NOT ADOPTED (gain): (d) is required on the reserve route's outcome 1]
#   ord_below     the same as below on the ordinary route. [ADOPTED; M1 reported]
#   ord_nogain    ord_below without the (d) gain. [NOT ADOPTED (gain): (d) is required on the ordinary route too]
#   ord_charm     ord_below + Lucario's own side hurt in the 45 cells' mixed rows: (c) fails but is reported on the
#                 ordinary rule, and no veto candidate exists. [ADOPTED, with the "WHICH READING DECIDED (K4)" note]
#   m1_low        gain with km3's Arena rate on the gating deals under T1 (M1 below threshold in the fallback).
#                 [NOT ADOPTED (mechanism)]
#   guard         gain with kta3's own Arena rate on the gating deals raised past T1. [NOT ADOPTED (mechanism), GUARD]
#   guard_below   below with the same kta3 plant. [ADOPTED; the guard reported]
#   cannot        gain with the sample's km3 Training Area counts equal to kta3's: the amendment records M2 'cannot pass'.
#                 [NOT ADOPTED (mechanism); 'cannot pass' named]
#   cannot_below  below with the same sample. [ADOPTED; M2 reported]
#   skip_winners  gain + one B2e deal (pairing 4) whose moves differ with the same result, and a coverage_skip.txt that
#                 SKIPs pairing 4 as if winners were enough. [PENDING: BAD SKIP]
#   skip_unnamed  gain with one SKIP line removed from coverage_skip.txt. [PENDING]
#   reach         gain + one changed game in Blaziken v Hydreigon (neither Stadium). [HELD; once explained ADOPTED];
#                 with --integrity-explained [ADOPTED]
#   edge3374/5    exactly 3,374 / 3,375 changed games in the reach cells (both print 15.00%): reserve / ordinary. [ADOPTED]
#   guards        the ONE SET: the real config with B unset; a config naming kog3 as the baseline; a config whose table
#                 reference sha256 is not the amendment's; a config moved consistently onto kta's fresh files; the ONE
#                 LIST (km_inputs.sha256): missing; edited without a dated STATUS.txt line; a config other than the one
#                 it lists; a listed file not its sha256; programs.txt (and STATUS.txt's part B line) naming programs
#                 other than the list's; STATUS.txt's part B line against programs.txt; a program in a build
#                 folder of another commit; a program under rl/ (a historical program); thresholds.json's counter-tool
#                 program not the pinned one. Then: no footprint.txt; a short km3 file; footprint.txt off by one; its
#                 route text against its counts; a (d) seed moved; (d) at 500 per row; a (d) block game with Lucario's
#                 seat flipped; (d)'s kta3 arm not kta3's reference game; identity failed / missing / short (the km3
#                 checks dropped); timing OVER; a RULE finding; a scan page missing [HELD]; a program's hash against
#                 programs.txt; the counter tool's source changed; thresholds.json missing / T a float / T not the
#                 midpoint / not in the amendment / 'threshold' with a lower bound at or under zero / sums not the
#                 sample's; the counter rows' kta3 arm not kta3's reference games, km3 arm not km3's games, a short
#                 counter file, a km3 row with kta3's moves but other counts [HELD], the
#                 km3 counters not in [spans: PENDING; below: ADOPTED]; (d) not in [PENDING]; the second-direction mixed
#                 rows not in [PENDING]; score45's page edited to a ΔMSE interval +0.4 to +20.0 [NOT ADOPTED under both
#                 open labels] and to a τ̂ bound of -1.10 [PENDING]; --footprint-only; --reuse-45 with its sidecar.
#   Sept 30 fixes (the two outcome audits' gaps; read_km.py's HISTORY note; on the worsen tree's own page, whose results changed
#   so a ΔMSE interval other than 0 to 0 is legitimate, edited as above and read with --reuse-45, a page standing for a decisive
#   run by its sidecar's --reps rewritten to 20000): a ΔMSE lower bound printed +0.0 whose unrounded value (score.py's new
#   "unrounded (full precision)" line) is +0.03 [wholly ABOVE: NOT ADOPTED (accuracy-worsening)], exactly 0 or printed -0.0 at
#   -0.03 [SPANS, decided, not PENDING], the two lines disagreeing [STOP], the same page below --reps 20000 [still PENDING: K8
#   is separate], a page without the new line [not reused, scored afresh], score.py's new line being opt-in (--full-precision,
#   asked for by this reader only; score45 run directly with and without it on the same files: the default page has no new line
#   and equals the reader's page minus its added lines, byte for byte); the detectable size converted from an unrounded real
#   error of 13.836 (printed 13.8), not the rounded figure; and, on the gain tree, the held-out direction inside the verdict
#   block (equal to section 5a's figure, and 'not in yet' when km3's B2e file is not in) and clause (d)'s pooled mean,
#   half-width and 95% interval at four decimals (equal to the two-decimal figure); --parse-page on a page carrying the new
#   line. Also (Sept 30): the guard "the real km_config.json, B not set yet" now reads a copy of the real config with B nulled,
#   because km's reading set B in the real one and the check could no longer pass on main.
# Every scenario has an expected pattern (the verdict line or the STOP) and some have more (also / never): each is
# checked against the reader's output; a miss is counted, listed at the end, and the script then exits 1.
# Usage (WSL): bash test_read_km.sh [stand-in folder]   (FULL=1 prints every reader output in full; REPS; CLEAN=1)
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/trainer_pricing_2026-09-28/km_run"
W=${1:-/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kmre2/rebaser/standin}
REPS=${REPS:-100}
case "$W" in *km_tables*|*km_run*|*km_build*) echo "refusing: the stand-in folder must not be a km results folder"; exit 2;; esac
[ "${CLEAN:-0}" = 1 ] && rm -rf "$W"
mkdir -p "$W"; rm -rf "$W/cache"
export PYTHONDONTWRITEBYTECODE=1
# The stand-in config: the real km_config.json (candidate, baseline, kta3's reference files with their sha256), with a
# stand-in B and stand-in cloud outputs in place of its required values (the real config refuses to read until the cloud
# reports them; a guard below checks that).
python3 - "$O/km_config.json" "$W/km_config.json" "$W/fakebuild/ref" <<'PYEOF'
import hashlib, json, os, sys
c = json.load(open(sys.argv[1], encoding="utf-8"))
b = "5eedc0de" + "0" * 32
c["about"] = "STAND-IN written by test_read_km.sh from km_config.json: a stand-in B and stand-in cloud outputs; not km's"
c["build"].update(commit=b, round_head=b, round_folder="rl/results/km_build_2099-01-01")
os.makedirs(sys.argv[3], exist_ok=True)
for k in ("km3_smoke", "tool_test3_rows", "tool_test3_trace"):   # stand-in cloud outputs, as the runner extracts them into <build>/ref
    p = os.path.join(sys.argv[3], f"standin_{k}")
    open(p, "w", encoding="utf-8").write(f"stand-in {k} (test_read_km.sh)\n")
    c["cloud_outputs"][k].update(path=f"rl/results/km_build_2099-01-01/standin_{k}", sha256=hashlib.sha256(open(p, "rb").read()).hexdigest())
c["cloud_outputs"].update(tool_test1_stdout_sha256="0" * 64, tool_test1_games_sha256="0" * 64)
json.dump(c, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
PYEOF
CFG="$W/km_config.json"
PX=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["build"]["commit"][:7])' "$CFG")
BASE=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["comparison"]["baseline"])' "$CFG")
CAND=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["comparison"]["candidate"])' "$CFG")
python3 "$O/km_config.py" check --config "$CFG" | tail -n 1
# The counter tool's source (the config's sha256, 05d7ba41...): not on main (main has the older source), so read once
# from the cloud branch's round, where that source was committed (a tool source, not a baseline).
[ -s "$W/tool_census.rs" ] || git -C "$R" show "origin/claude/pensive-ptolemy-spwc0b:$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["counter_tool"]["source_path"])' "$CFG")" > "$W/tool_census.rs"
# Stand-in programs in a stand-in build folder laid out as the runner's (<build>/COMMIT is B).
FB="$W/fakebuild"; mkdir -p "$FB/engine/target/release/examples" "$FB/engine/examples" "$FB/decks/research"
python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["build"]["commit"])' "$CFG" > "$FB/COMMIT"
for p in deckgym examples/legality_scan examples/tool_census; do echo "stand-in program $p (test_read_km.sh)" > "$FB/engine/target/release/$p"; done
cp "$W/tool_census.rs" "$FB/engine/examples/tool_census.rs"; cp "$R"/decks/research/*.txt "$FB/decks/research/"   # as part B lays them out

cat > "$W/make_standin.py" <<'EOF'
import copy, csv, hashlib, json, os, random, shutil, sys
from fractions import Fraction
R, W, scn = sys.argv[1:4]
sys.path.insert(0, f"{R}/rl/results/trainer_pricing_2026-09-28/km_run")
import km_check, km_config   # noqa: E402  (the runner's own one-list code writes the stand-in km_inputs.sha256)
RES = f"{R}/rl/results"
CFG = json.load(open(f"{W}/km_config.json", encoding="utf-8"))   # the stand-in config (the real one's set, a stand-in B)
BASE, CAND = CFG["comparison"]["baseline"], CFG["comparison"]["candidate"]
REF = {g: f"{R}/{CFG['references']['folder']}/{e['file']}" for g, e in CFG["references"]["groups"].items()}
REG = f"{RES}/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md"
PX = CFG["build"]["commit"][:7]
VARS = ("v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy")
VARTSV = {v: f"{R}/{CFG['references']['groups'][f'var_{v}']['pairs']}" for v in VARS}
FB_DIR = f"{W}/fakebuild/engine/target/release"   # the stand-in build folder (its COMMIT is the stand-in B)
PROG_PATH = {"deckgym": f"{FB_DIR}/deckgym", "legality_scan": f"{FB_DIR}/examples/legality_scan",
             "tool_census": f"{FB_DIR}/examples/tool_census"}
PROG_SHA = {k: hashlib.sha256(open(p, "rb").read()).hexdigest() for k, p in PROG_PATH.items()}
KEEP = ("a", "b", "a_file", "b_file", "bot_a", "bot_b", "i", "pairing", "seed", "moves", "first_deck_score", "first_seat")
PAGE = "bot {bots}, stand-in page written by test_read_km.sh\n\nFindings (occurrences / games affected):\n  none\n"
D_BLOCK = 22_900_000_000
D_ROWS = [("table", 2), ("table", 8), ("table", 13), ("table", 18), ("table", 19), ("table", 20), ("table", 21), ("new17", 8), ("new17", 16)]
KM17 = [("table", 0, "altaria", "blaziken"), ("table", 1, "altaria", "hydreigon"), ("table", 2, "altaria", "lucario"),
        ("table", 3, "altaria", "sceptile"), ("table", 4, "altaria", "suicune"), ("table", 5, "altaria", "vespiquen"),
        ("table", 6, "altaria", "weezing"), ("table", 8, "blaziken", "lucario"), ("table", 13, "hydreigon", "lucario"),
        ("table", 18, "lucario", "sceptile"), ("table", 19, "lucario", "suicune"), ("table", 20, "lucario", "vespiquen"),
        ("table", 21, "lucario", "weezing"), ("new_decks.tsv", 8, "rayquaza", "lucario"), ("new_decks.tsv", 9, "rayquaza", "altaria"),
        ("new_decks.tsv", 16, "altaria_greninja", "lucario"), ("new_decks.tsv", 17, "altaria_greninja", "altaria")]
M1C = [("table", 2), ("table", 8), ("table", 13), ("table", 18), ("table", 19), ("table", 20), ("table", 21), ("new_decks.tsv", 8), ("new_decks.tsv", 16)]
M2C = [("table", 0), ("table", 1), ("table", 3), ("table", 4), ("new_decks.tsv", 9)]
CELLAB = {(s, p): (a, b) for s, p, a, b in KM17}
GATING = {CELLAB[c] for c in M1C + M2C}
DEFAULT_PROFILE = {"base": {"gate": {"arena": 0.22, "ta": 0.33}, "sample": {"arena": 0.22, "ta": 0.33}},
                   "cand": {"gate": {"arena": 0.52, "ta": 0.60}, "sample": {"arena": 0.52, "ta": 0.60}},
                   "copy_ta_sample": False}


def H(tag, g):
    return int(hashlib.md5(f"{tag}:{g['seed']}:{g.get('pairing')}:{g.get('a')}:{g.get('b')}".encode()).hexdigest()[:8], 16)


def Hs(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def newmoves(g, tag="*"):
    g["moves"] = hashlib.md5((g["moves"] + tag).encode()).hexdigest()[:16]
    return g


def flip(g, v):
    g["first_deck_score"] = v
    newmoves(g)
    return g


def rd(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def strip(g):
    return {k: g[k] for k in KEEP if k in g}


def wr(dst, recs):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        os.remove(dst)
    with open(dst, "w", encoding="utf-8") as f:
        for g in recs:
            f.write(json.dumps(g, sort_keys=True) + "\n")


def link(src, dst):
    if os.path.lexists(dst):
        os.remove(dst)
    os.symlink(os.path.realpath(src), dst)


def relabel(recs, bots, keep=None):
    out = []
    for g in recs:
        if keep and not keep(g):
            continue
        g = strip(g)
        g["bot_a"], g["bot_b"] = bots
        out.append(g)
    return out


def var_side(v):
    return {int(r["pairing"]): r["variant_side"] for r in csv.DictReader(open(VARTSV[v], encoding="utf-8"), delimiter="\t")}


FB = (CAND, BASE)   # the candidate on the first-named deck (side a), the baseline on the other
SB = (BASE, CAND)


# group -> (the baseline's reference file, {direction: (bots, full src name, run name)}, the candidate's both-sides name)
def groups():
    g = {}
    for grp in ("table", "new17"):
        g[grp] = (REF[grp], {dr: (FB if dr == "first" else SB, f"{PX}_mixed_{grp}_{CAND}_{dr}.full.jsonl",
                                  f"{PX}_mixed_{grp}_{CAND}_{dr}.jsonl") for dr in ("first", "second")}, f"{PX}_{CAND}_{grp}.jsonl")
    g["b2e"] = (REF["b2e"], {"first": (FB, f"{PX}_mixed_b2e_{CAND}_first.full.jsonl", f"{PX}_mixed_b2e_{CAND}_first.jsonl")},
                f"{PX}_b2e_{CAND}.jsonl")
    g["scizor"] = (REF["scizor"], {dr: (FB if dr == "first" else SB, f"{PX}_mixed_scizor_{CAND}_{dr}.full.jsonl",
                                        f"{PX}_mixed_scizor_{CAND}_{dr}.jsonl") for dr in ("first", "second")}, f"{PX}_scizor_{CAND}.jsonl")
    for v in VARS:
        sides = set(var_side(v).values())
        g[f"var_{v}"] = (REF[f"var_{v}"], {s: (FB if s == "a" else SB, f"{PX}_var_{v}_{CAND}_mixed_{s}.full.jsonl",
                                               f"{PX}_var_{v}_{CAND}_mixed_{s}.jsonl") for s in sorted(sides)}, f"{PX}_var_{v}_{CAND}.jsonl")
    return g


STORED = None


def stored():
    """The baseline's 45-cell reference games: {(a, b, i): record}, and {(grp, pairing, i): record}."""
    global STORED
    if STORED is None:
        by_abi, by_gpi = {}, {}
        for grp, f in (("table", REF["table"]), ("new17", REF["new17"])):
            for g in rd(f):
                g = strip(g)
                by_abi[(g["a"], g["b"], g["i"])] = g
                by_gpi[(grp, g["pairing"], g["i"])] = g
        STORED = (by_abi, by_gpi)
    return STORED


def own_luc(g):
    return g["first_deck_score"] if g["a"] == "lucario" else 1 - g["first_deck_score"]


def d_files():
    """(d): the baseline on both sides and the candidate on Lucario (= the baseline's games relabelled), 9 rows x 2,000."""
    _, gpi = stored()
    base_arm, km = [], []
    for r, (grp, p) in enumerate(D_ROWS):
        recs = [gpi[(grp, p, n)] for n in range(500)]
        first, second = recs[0]["a"], recs[0]["b"]
        other = first if second == "lucario" else second
        if grp == "table":
            lf, of = "decks/research/lucario.txt", f"decks/research/{other}.txt"
        else:
            lf, of = (recs[0]["a_file"], recs[0]["b_file"]) if first == "lucario" else (recs[0]["b_file"], recs[0]["a_file"])
        for g in recs:
            k = dict(g, bot_a=BASE, bot_b=BASE)
            x = dict(g, bot_a=CAND if g["a"] == "lucario" else BASE, bot_b=CAND if g["b"] == "lucario" else BASE)
            base_arm.append(k)
            km.append(x)
        for j in range(1500):
            s = recs[j % 500]
            g = {"a": "lucario", "b": other, "a_file": lf, "b_file": of, "bot_a": BASE, "bot_b": BASE, "i": j, "pairing": r,
                 "seed": D_BLOCK + 10_000 * r + j, "moves": hashlib.md5((s["moves"] + f"#d{j}").encode()).hexdigest()[:16],
                 "first_deck_score": own_luc(s), "first_seat": j % 2}
            base_arm.append(g)
            km.append(dict(g, bot_a=CAND))
    return base_arm, km


def build_base():
    d = f"{W}/base_null/src"
    if os.path.exists(f"{d}/DONE"):
        return
    os.makedirs(d, exist_ok=True)
    for grp, (k, mx, nx) in groups().items():
        recs = rd(k)
        wr(f"{d}/{nx}", relabel(recs, (CAND, CAND)))
        for dr, (bots, full, run) in mx.items():
            if grp.startswith("var_"):
                side = var_side(grp[4:])
                wr(f"{d}/{full}", relabel(recs, bots, keep=lambda g, s=dr: side[g["pairing"]] == s))
            else:
                wr(f"{d}/{full}", relabel(recs, bots))
    base_arm, km = d_files()
    wr(f"{d}/{PX}_d_{BASE}.jsonl", base_arm)
    wr(f"{d}/{PX}_d_{CAND}.jsonl", km)
    json.dump(DEFAULT_PROFILE, open(f"{d}/profile.json", "w"))
    open(f"{d}/DONE", "w").write("ok\n")


def scenario(name):
    d = f"{W}/{name}"
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(f"{d}/src")
    for f in os.listdir(f"{W}/base_null/src"):
        if f.endswith(".jsonl"):
            link(f"{W}/base_null/src/{f}", f"{d}/src/{f}")
    json.dump(DEFAULT_PROFILE, open(f"{d}/src/profile.json", "w"))
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


def set_profile(d, fn):
    p = json.load(open(f"{d}/src/profile.json"))
    fn(p)
    json.dump(p, open(f"{d}/src/profile.json", "w"))


def equal5(r, s):
    return all(r.get(k) == s.get(k) for k in ("moves", "a", "b", "seed", "first_seat", "a_file", "b_file"))


def page(p, bots):
    open(p[:-len(".jsonl")] + ".txt", "w").write(PAGE.format(bots=bots))


def cache_dir(tag, files, extra=""):
    sig = hashlib.sha1((tag + "|" + "|".join(os.path.realpath(f) for f in files) + "|" + extra).encode()).hexdigest()[:16]
    return f"{W}/cache/{tag}_{sig}"


# ---- the counter tool's rows (synthetic counts that follow the games)
def draw(moves, name, rate):
    off = 1 + Hs(moves + name) % 4
    pl = sum(1 for k in range(off) if Hs(f"{moves}{name}{k}") % 1000 < rate * 1000)
    return {"offered": off, "played": pl, "targets": {}}


def gen_counts(moves, seat_decks, prof):
    seats, xs = [], []
    for s, dk in enumerate(seat_decks):
        cards = {"Copycat": draw(moves, f"cc{s}", 0.5)}
        if dk == "lucario":
            cards["Arena of Antiquity"] = draw(moves, f"arena{s}", prof["arena"])
        if dk == "altaria":
            cards["Training Area"] = draw(moves, f"ta{s}", prof["ta"])
        if dk in ("lucario", "vespiquen", "weezing"):
            cards["X Speed"] = draw(moves, f"xs{s}", 0.4)
            for k in range(cards["X Speed"]["played"]):
                h = Hs(f"{moves}xsp{s}{k}")
                xs.append({"seat": s, "turn": 3 + k, "hiking_trail": h % 5 == 0, "retreated": h % 3 != 0})
        if dk == "suicune":
            cards["Team Rocket's Boss"] = draw(moves, f"boss{s}", 0.03)
        fb = draw(moves, f"fb{s}", 0.3)
        if fb["played"]:
            fb["targets"] = {"the Stadium": fb["played"] // 2} if fb["played"] > 1 else {"opponent's Tool on Active (x)": 1}
        cards["Field Blower"] = fb
        seats.append({"seat": s, "deck": dk, "cards": cards})
    return seats, xs


def counter_rows(d, cells, deals, prof, rng_name):
    abi, _ = stored()
    km = {}
    for grp in ("table", "new17"):
        for g in rd(f"{d}/src/{PX}_{CAND}_{grp}.jsonl"):
            km[(g["a"], g["b"], g["i"])] = g
    out = {BASE: [], CAND: []}
    for (src, p) in cells:
        a, b = CELLAB[(src, p)]
        for i in deals:
            gk, gx = abi[(a, b, i)], km[(a, b, i)]
            fs = gk["first_seat"]
            sd = [a, b] if fs == 0 else [b, a]
            files = ((f"../decks/research/{a}.txt", f"../decks/research/{b}.txt") if src == "table" else (gk["a_file"], gk["b_file"]))
            base = {"source": src, "pairing": p, "a": a, "b": b, "a_file": files[0], "b_file": files[1], "i": i, "seed": gk["seed"],
                    "first_seat": fs, "seat_decks": sd}
            ck, xk = gen_counts(gk["moves"], sd, prof["base"][rng_name])
            rk = dict(base, bots=[BASE, BASE], moves=gk["moves"], counts=ck, xspeed=xk)
            if gx["moves"] == gk["moves"]:
                cx, xx = copy.deepcopy(ck), copy.deepcopy(xk)
            else:
                cx, xx = gen_counts(gx["moves"], sd, prof["cand"][rng_name])
                if rng_name == "sample" and prof.get("copy_ta_sample"):
                    for s in range(2):
                        if sd[s] == "altaria":
                            cx[s]["cards"]["Training Area"] = copy.deepcopy(ck[s]["cards"]["Training Area"])
            rx = dict(base, bots=[CAND, CAND], moves=gx["moves"], counts=cx, xspeed=xx)
            out[BASE].append(rk)
            out[CAND].append(rx)
    return out


def owner(r, dk, card):
    c = [x for x in r["counts"] if x["deck"] == dk][0]["cards"].get(card, {})
    return c.get("offered", 0), c.get("played", 0)


def thresholds(sample, reg_out):
    """km_thresholds.py's registered rule on the stand-in sample: the exact midpoint; the frozen paired bootstrap's shape
    (per-cell resampling, seeds 20260929 / 20260930) at 1,000 replicates (a stand-in); 'cannot pass' when the lower
    bound is not above zero."""
    lines, amend = {}, []
    for name, card, dk, cells, seed in (("M1", "Arena of Antiquity", "lucario", M1C, 20260929), ("M2", "Training Area", "altaria", M2C, 20260930)):
        idx = {(r["source"], r["pairing"], r["i"]): r for r in sample[BASE]}
        idx2 = {(r["source"], r["pairing"], r["i"]): r for r in sample[CAND]}
        units = [[(*owner(idx[(s, p, i)], dk, card), *owner(idx2[(s, p, i)], dk, card)) for i in range(200, 300)] for (s, p) in cells]
        go = sum(u[0] for c in units for u in c); gp = sum(u[1] for c in units for u in c)
        ko = sum(u[2] for c in units for u in c); kp = sum(u[3] for c in units for u in c)
        rng, diffs = random.Random(seed), []
        for _ in range(1000):
            a = b = c_ = e = 0
            for cu in units:
                for _ in range(100):
                    u = cu[rng.randrange(100)]
                    a += u[0]; b += u[1]; c_ += u[2]; e += u[3]
            diffs.append(0.0 if a == 0 or c_ == 0 else e / c_ - b / a)
        diffs.sort()
        lo, hi = diffs[int(0.025 * 1000)], diffs[int(0.975 * 1000)]
        T = (Fraction(gp, go) + Fraction(kp, ko)) / 2
        status = "threshold" if lo > 0 else "cannot pass"
        lines[name] = {"card": card, "cells": [f"{s}:{p}" for s, p in cells], BASE: {"offered": go, "played": gp},
                       CAND: {"offered": ko, "played": kp}, "interval": [lo, hi], "T": f"{T.numerator}/{T.denominator}", "status": status}
        amend.append(f"- {name}, {card} (STAND-IN): {BASE} {gp:,} of {go:,}, {CAND} {kp:,} of {ko:,}; paired interval {lo:+.4f} to "
                     f"{hi:+.4f}; " + (f"T = {T.numerator}/{T.denominator} ({100 * float(T):.1f}%)." if status == "threshold" else "cannot pass."))
    js = {"note": "STAND-IN written by test_read_km.sh (not km's)", "tool_source_sha256": CFG["counter_tool"]["source_sha256"],
          "km_thresholds_py_sha256": "stand-in", "arms": [BASE, CAND],
          "counter_tool": {"source_sha256": CFG["counter_tool"]["source_sha256"], "program_sha256": PROG_SHA["tool_census"]},
          "lines": lines}
    open(reg_out, "w", encoding="utf-8").write(open(REG, encoding="utf-8").read() + "\n\n## Amendment (STAND-IN written by "
                                              "test_read_km.sh under the scratch folder; not the registration)\n" + "\n".join(amend) + "\n")
    return js


def finalize(d, lie=()):
    run = f"{d}/run"
    shutil.rmtree(run, ignore_errors=True)
    os.makedirs(run)
    G = groups()
    prof = json.load(open(f"{d}/src/profile.json"))
    for f in os.listdir(f"{d}/src"):
        if f.endswith(".jsonl") and ".full." not in f:
            link(f"{d}/src/{f}", f"{run}/{f}")
            page(f"{run}/{f}", "stand-in")
    # the 45 cells: footprint.txt (footprint_km.py's format) and the mixed rows
    abi, _ = stored()
    km = {(g["a"], g["b"], g["i"]): g for grp in ("table", "new17") for g in rd(f"{d}/src/{G[grp][2]}")}
    diff = [k for k in abi if abi[k]["moves"] != km[k]["moves"]]
    n = len(diff)
    reserve = 100 * n < 15 * len(abi)
    open(f"{run}/footprint.txt", "w").write(
        f"FOOTPRINT: {n} of {len(abi)} paired games on the 45 cells differ from {BASE}'s moves = {100 * n / len(abi):.2f}%\n"
        f"ROUTE (fixed on this number, before anything else is read): "
        f"{'RESERVE route, clauses (a)-(e)' if reserve else 'ORDINARY adoption rule (15% or more)'}\n"
        f"by cell (games differing of 500): (stand-in)\n")
    active = {(k[0], k[1]) for k in diff}
    srcs = [f"{d}/src/{G[grp][1][dr][1]}" for grp in ("table", "new17") for dr in ("first", "second")]
    cd = cache_dir("g45", srcs, str(sorted(active)))
    if not os.path.exists(f"{cd}/DONE"):
        os.makedirs(cd, exist_ok=True)
        for grp in ("table", "new17"):
            for dr in ("first", "second"):
                bots, full, runname = G[grp][1][dr]
                keep = [g for g in rd(f"{d}/src/{full}") if (g["a"], g["b"]) in active or g["i"] < 40]
                wr(f"{cd}/{runname}", keep)
                page(f"{cd}/{runname}", bots)
        open(f"{cd}/DONE", "w").write("ok\n")
    for f in os.listdir(cd):
        if f != "DONE":
            link(f"{cd}/{f}", f"{run}/{f}")
    # coverage
    skip_lines = [f"coverage_skip (stand-in): {CAND} v {BASE} both-sides games compared deal by deal on moves, a, b, seed, first_seat"]
    for grp in ["b2e", "scizor"] + [f"var_{v}" for v in VARS]:
        k_, mx, nx = G[grp]
        srcs = [k_, f"{d}/src/{nx}"] + [f"{d}/src/{mx[dr][1]}" for dr in mx]
        mylie = sorted(p for g_, p in lie if g_ == grp)
        cd = cache_dir(grp, srcs, str(mylie))
        if not os.path.exists(f"{cd}/DONE"):
            os.makedirs(cd, exist_ok=True)
            bref = {(g["pairing"], g["i"]): g for g in rd(k_)}
            kmx = {(g["pairing"], g["i"]): g for g in rd(f"{d}/src/{nx}")}
            ps = sorted({p for p, _ in bref})
            eq, nd = dict.fromkeys(ps, 0), dict.fromkeys(ps, 0)
            for (q, i), g in bref.items():
                nd[q] += 1
                eq[q] += equal5(strip(g), kmx[(q, i)])
            lines = []
            for p in ps:
                if p in mylie:
                    lines.append(f"SKIP {grp} {p}: {nd[p]} of {nd[p]} deals equal on moves, a, b, seed, first_seat")
                else:
                    lines.append(f"{'SKIP' if eq[p] == nd[p] else 'RUN'} {grp} {p}: {eq[p]} of {nd[p]} deals equal on moves, a, b, seed, first_seat")
            open(f"{cd}/skip.txt", "w").write("\n".join(lines) + "\n")
            for dr, (bots, full, runname) in mx.items():
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
    # the counters (deals 0-199, 17 cells), the threshold sample (200-299, 14 cells), thresholds.json, the amendment
    ctr = counter_rows(d, [(s, p) for s, p, _, _ in KM17], range(0, 200), prof, "gate")
    smp = counter_rows(d, M1C + M2C, range(200, 300), prof, "sample")
    for arm in (BASE, CAND):
        wr(f"{run}/{PX}_counters_{arm}.jsonl", ctr[arm])
        wr(f"{run}/{PX}_sample_{arm}.jsonl", smp[arm])
    js = thresholds(smp, f"{run}/registration_standin.md")
    json.dump(js, open(f"{run}/thresholds.json", "w"), indent=1)
    # the records (synthetic, in the runner's line formats): Amendment 1 (e) item 3's eight checks at their sizes
    ids = "moves, decisions, openings, winner_seat, points, seed, first_seat"
    t_ref, n_ref = CFG["references"]["groups"]["table"]["file"], CFG["references"]["groups"]["new17"]["file"]
    with open(f"{run}/identity_check.txt", "w") as f:
        f.write("(stand-in identity record written by test_read_km.sh, in run_km.sh part I's formats)\n")
        f.write(f"1 {BASE}, laptop build, the 28 table cells, i < 20, v {t_ref}: 560 of 560 games equal on {ids}; PASS\n")
        f.write(f"2 {BASE}, laptop build, the 17 new cells, i < 20, v {n_ref}: 340 of 340 games equal on {ids}, a_file, b_file; PASS\n")
        f.write(f"3 {CAND} (as {CAND}) equal to {BASE}, laptop build, the 15 table cells with neither damage Stadium, i < 20, v {t_ref}: 300 of 300 games equal on {ids}; PASS\n")
        f.write(f"3 {CAND} (as {CAND}) equal to {BASE}, laptop build, the 13 new cells with neither damage Stadium, i < 20, v {n_ref}: 260 of 260 games equal on {ids}, a_file, b_file; PASS\n")
        f.write(f"4 {CAND} (as {CAND}), laptop build, pairings 0,2,19 (where N2 acts), i < 40, v standin_km3_smoke: 120 of 120 games equal on every field of the reference's row; PASS\n")
        for g_, n_ in (("b2e", 1920), ("scizor", 160), ("var_v-lucario_2", 140), ("var_v-suicune_2", 140), ("var_v-weezing_2", 140), ("var_l-charizardy", 160)):
            f.write(f"5 {BASE}, laptop build, {g_}, i < 20, v {CFG['references']['groups'][g_]['file']}: {n_} of {n_} games equal on {ids}, a_file, b_file; PASS\n")
        f.write(f"6 the counter tool's {BASE} (8a's slice, --no-counts), laptop build, the 17 named cells, i < 20, v {t_ref} / {n_ref}: 340 of 340 deals equal on the move fingerprint, both decks, seed and seats (17 cells, 17 cells expected, i 0-19); no count read; PASS\n")
        f.write(f"6 the counter tool's {CAND} (as {CAND}; 8a's slice, --no-counts), laptop build, pairings 0 and 2, i < 40, v standin_km3_smoke: 80 of 80 deals equal on the move fingerprint, both decks, seed and seats (2 cells, 2 cells expected, i 0-39); no count read; PASS\n")
        f.write("7 tool test 3's exact command, laptop build (kp3, Altaria v Lucario, seeds 20,000,920,000-019, 20 games; counts compared byte for byte, none read): 2 of 2 files equal byte for byte to B's round's files; PASS\n")
        f.write("8 tool test 1's run of the tool, laptop build (kp3, the table's first 20 deals of the 28 pairings, 560 games; counts compared byte for byte, none read): 2 of 2 outputs equal byte for byte to B's round's by sha256; PASS\n")
    open(f"{run}/{PX}_timing_1.txt", "w").write(f"{BASE} 61.0 s wall, 720.0 s CPU; {CAND} 63.0 s wall, 741.0 s CPU; {CAND}/{BASE} wall 1.033 (limit 1.25: within), CPU 1.029\n")
    with open(f"{run}/programs.txt", "w") as f:
        for p in ("deckgym", "legality_scan", "tool_census"):
            f.write(f"{PROG_SHA[p]}  {PROG_PATH[p]}\n")
    with open(f"{run}/STATUS.txt", "w") as f:
        f.write(f"KM PART B DONE {PX} 2099-01-01T00:00:00Z B {CFG['build']['commit']} deckgym {PROG_SHA['deckgym']} legality_scan {PROG_SHA['legality_scan']} "
                f"tool_census {PROG_SHA['tool_census']} (tool source {CFG['counter_tool']['source_sha256']})\n")
    link(f"{W}/tool_census.rs", f"{run}/tool_census.rs")
    # km's one list, by the runner's own code (km_check.py one-list write), and its STATUS.txt line, as part I writes them
    ok, msg = km_check.list_write(km_config.load(f"{W}/km_config.json"), R, f"{W}/fakebuild", f"{run}/programs.txt", f"{run}/km_inputs.sha256")
    if not ok:
        raise SystemExit(f"the stand-in one list could not be written: {msg}")
    with open(f"{run}/STATUS.txt", "a") as f:
        f.write(f"KM INPUTS WRITTEN {PX} 2099-01-01T00:00:01Z km_inputs.sha256 "
                f"{hashlib.sha256(open(f'{run}/km_inputs.sha256', 'rb').read()).hexdigest()} (stand-in, test_read_km.sh; {msg})\n")


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


REACH = lambda g: "lucario" in (g["a"], g["b"]) or "altaria" in (g["a"], g["b"])  # noqa: E731


def mech(d):
    """km3 plays differently on 40% of the 14 gating cells' deals 0-299 (its counter rows there get the km3 rates)."""
    for grp in ("table", "new17"):
        redo(d, f"{PX}_{CAND}_{grp}.jsonl", lambda g: (g["a"], g["b"]) in GATING and g["i"] < 300 and H("mech", g) % 100 < 40 and newmoves(g, "mech"))


def move_results(d, how, move_frac=0):
    lim = limitless()
    for grp in ("table", "new17"):
        name = f"{PX}_{CAND}_{grp}.jsonl"
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
    if own_luc(g) == 0.0 and H("dgain", g) % 12 == 0:
        flip(g, 1.0 if g["a"] == "lucario" else 0.0)


build_base()
d = scenario(scn)
lie = ()
if scn != "null":
    if scn not in ("below_nogain", "ord_nogain"):
        redo(d, f"{PX}_d_{CAND}.jsonl", d_gain)
    if not scn.startswith("edge"):
        mech(d)
def hurt_lucario_mixed(d):
    for grp in ("table", "new17"):
        for dr, who in (("first", "a"), ("second", "b")):
            def hurt(g, dr=dr, who=who):
                if g[who] == "lucario" and H("luc", g) % 3 == 0:
                    if dr == "first" and g["first_deck_score"] == 1.0:
                        flip(g, 0.0)
                    if dr == "second" and g["first_deck_score"] == 0.0:
                        flip(g, 1.0)
            redo(d, f"{PX}_mixed_{grp}_{CAND}_{dr}.full.jsonl", hurt)


if scn == "harm":
    hurt_lucario_mixed(d)
    redo(d, f"{PX}_b2e_{CAND}.jsonl", lambda g: g["pairing"] == 0 and H("fpb", g) % 10 == 0 and newmoves(g, "b"))
    redo(d, f"{PX}_mixed_b2e_{CAND}_first.full.jsonl", lambda g: g["pairing"] == 0 and g["first_deck_score"] == 1.0 and H("b2e", g) % 2 == 0 and flip(g, 0.0))
    redo(d, f"{PX}_scizor_{CAND}.jsonl", lambda g: H("fps", g) % 10 == 0 and newmoves(g, "s"))
    redo(d, f"{PX}_mixed_scizor_{CAND}_first.full.jsonl", lambda g: g["first_deck_score"] == 1.0 and H("scz", g) % 3 == 0 and flip(g, 0.0))
elif scn in ("worsen", "worsen_ord"):
    move_results(d, "away", 0.5 if scn == "worsen_ord" else 0)
elif scn in ("below", "below_nogain", "ord_below", "ord_nogain", "ord_charm", "guard_below", "cannot_below"):
    move_results(d, "toward", 0.5 if scn.startswith("ord") else 0)
    if scn in ("below", "below_nogain", "ord_below", "ord_nogain", "ord_charm"):
        set_profile(d, lambda p: p["cand"]["gate"].update(arena=0.25))       # M1 under its threshold (reported when below)
    if scn == "ord_charm":
        hurt_lucario_mixed(d)                                               # (c) fails; on the ordinary rule it is reported
if scn == "m1_low":
    set_profile(d, lambda p: p["cand"]["gate"].update(arena=0.25))
elif scn in ("guard", "guard_below"):
    set_profile(d, lambda p: p["base"]["gate"].update(arena=0.33))
elif scn in ("cannot", "cannot_below"):
    set_profile(d, lambda p: p.update(copy_ta_sample=True))
elif scn == "skip_winners":
    seen = []

    def one(g):
        if not seen and g["pairing"] == 4 and g["i"] == 3:
            seen.append(1)
            newmoves(g, "win")
    redo(d, f"{PX}_b2e_{CAND}.jsonl", one)
    lie = (("b2e", 4),)
elif scn in ("reach", "explained"):
    seen = []

    def one(g):
        if not seen and (g["a"], g["b"]) == ("blaziken", "hydreigon") and g["i"] == 7:
            seen.append(1)
            newmoves(g, "reach")
    redo(d, f"{PX}_{CAND}_table.jsonl", one)
    open(f"{d}/explanation.txt", "w").write("Stand-in explanation (test only): the changed Blaziken v Hydreigon game was planted by "
                                             "test_read_km.sh to exercise the integrity line.\n")
elif scn.startswith("edge"):
    n = int(scn[4:])
    recs = {grp: rd(f"{d}/src/{PX}_{CAND}_{grp}.jsonl") for grp in ("table", "new17")}
    order = sorted((H("edge", g), grp, j) for grp in recs for j, g in enumerate(recs[grp]) if REACH(g))
    for _, grp, j in order[:n]:
        newmoves(recs[grp][j], "#")
    for grp in recs:
        wr(f"{d}/src/{PX}_{CAND}_{grp}.jsonl", recs[grp])
finalize(d, lie)
if scn == "skip_unnamed":
    ls = open(f"{d}/run/coverage_skip.txt").read().splitlines()
    open(f"{d}/run/coverage_skip.txt", "w").write("\n".join(l for l in ls if not l.startswith("SKIP b2e 0:")) + "\n")
print("built", scn)
EOF

show() {  # sections 1-1b and 9 of a reader run (the full output stays in the folder)
  if [ "${FULL:-0}" = 1 ]; then cat "$1"; return; fi
  sed -n '/^1\. THE FOOTPRINT/,/^NOTES/p' "$1" | sed '$d' | grep -E '^   (km3:|cells with|INTEGRITY|M1 \(|M2 \()' | cut -c1-240 || true
  if [ -n "${EXTRA:-}" ]; then echo "   [...selected lines, EXTRA=$EXTRA...]"; grep -E "$EXTRA" "$1" | cut -c1-300 || true; fi
  echo "   [...sections 2-8 omitted here; the full output is $1]"
  sed -n '/^9\. VERDICT/,/THE OUTCOMES THE REGISTRATION FIXES/p' "$1" | sed '$d' | cut -c1-400
}
NCHK=0; FAILS=(); LAST=""; LASTLAB=""
check() {
  local f=$1 lab=$2 pat; shift 2
  for pat in "$@"; do
    NCHK=$((NCHK + 1))
    if grep -qE -- "$pat" "$f"; then echo "   [check ok] $pat"
    else echo "   [CHECK FAILED] not found: $pat"; FAILS+=("$lab -- not found: $pat"); fi
  done
}
lacks() {
  local f=$1 lab=$2 pat; shift 2
  for pat in "$@"; do
    NCHK=$((NCHK + 1))
    if grep -qE -- "$pat" "$f"; then echo "   [CHECK FAILED] found, must not be: $pat"; FAILS+=("$lab -- found, must not be: $pat")
    else echo "   [check ok] absent: $pat"; fi
  done
}
has() {  # file label fixed-string...: each string must appear in the file (grep -F, no pattern characters)
  local f=$1 lab=$2 s; shift 2
  for s in "$@"; do
    NCHK=$((NCHK + 1))
    if grep -qF -- "$s" "$f"; then echo "   [check ok] $s"
    else echo "   [CHECK FAILED] not found: $s"; FAILS+=("$lab -- not found: $s"); fi
  done
}
hasnt() {  # file label fixed-string...: none may appear
  local f=$1 lab=$2 s; shift 2
  for s in "$@"; do
    NCHK=$((NCHK + 1))
    if grep -qF -- "$s" "$f"; then echo "   [CHECK FAILED] found, must not be: $s"; FAILS+=("$lab -- found, must not be: $s")
    else echo "   [check ok] absent: $s"; fi
  done
}
equal() {  # label a b: two figures the reader printed in two places must be the same text
  NCHK=$((NCHK + 1))
  if [ -n "$2" ] && [ "$2" = "$3" ]; then echo "   [check ok] $1: $2"
  else echo "   [CHECK FAILED] $1: '$2' vs '$3'"; FAILS+=("$1 -- '$2' vs '$3'"); fi
}
also() { check "$LAST" "$LASTLAB" "$@"; }
never() { lacks "$LAST" "$LASTLAB" "$@"; }
V_AD='^   => km3 is ADOPTED as the working pilot'
V_NA="^   => $CAND is NOT ADOPTED; $BASE stays the working pilot\\. The test\\(s\\) that failed: "
V_HELD='^   => HELD; once explained: '
V_PEND='^   => PENDING: '

run_reader() {  # folder label expected-ERE extra-args...
  local dir=$1 label=$2 want=$3; shift 3
  echo; echo "################ $label"
  mkdir -p "$dir/pages"
  set +e
  nice -n 19 python3 "$O/read_km.py" --dir "$dir" --pages-dir "$dir/pages" --reps "$REPS" --m-reps 200 \
    --registration "$dir/registration_standin.md" --config "$CFG" "$@" > "$dir/reader_output.txt" 2>&1
  local rc=$?
  set -e
  echo "(exit code $rc)"
  if [ $rc -ne 0 ]; then tail -n 3 "$dir/reader_output.txt" | cut -c1-600; else show "$dir/reader_output.txt"; fi
  LAST="$dir/reader_output.txt"; LASTLAB=$label
  if [ $rc -ne 0 ]; then also '^STOP: '; fi
  also "$want"
  return 0
}
build() { nice -n 19 python3 "$W/make_standin.py" "$R" "$W" "$1"; }

echo "################ unit: --selftest"
mkdir -p "$W/unit"
set +e
python3 "$O/read_km.py" --selftest --config "$CFG" > "$W/unit/selftest.txt" 2>&1
set -e
cat "$W/unit/selftest.txt"
check "$W/unit/selftest.txt" "unit: --selftest" '^selftest ok: '
echo; echo "################ unit: --parse-page on the earlier real score45 pages (none is km's)"
set +e
: > "$W/unit/parse_pages.txt"
while IFS= read -r p; do
  out=$(python3 "$O/read_km.py" --parse-page "$p" 2>&1); rc=$?
  echo "  ${p#$R/rl/results/}: $(echo "$out" | head -n 1 | cut -c1-140) (exit $rc)" | tee -a "$W/unit/parse_pages.txt"
done < <(find "$R/rl/results" -name 'score45_*.txt' -not -path '*km_*' -not -path '*kta_tables*' | sort)   # no in-progress reading's page
KP="$R/rl/results/koh_2026-09-28/laptop_reading/score45_koh3_vs_kog3.txt"   # koh's committed page (history), a parser test only
grep -v '^    deck hydreigon +3.7' "$KP" > "$W/unit/drop_deck_line.txt"
python3 "$O/read_km.py" --parse-page "$W/unit/drop_deck_line.txt" > "$W/unit/drop_deck_out.txt" 2>&1
echo "  koh's page, a deck-veto line dropped: exit $?: $(head -n 1 "$W/unit/drop_deck_out.txt" | cut -c1-200)"
set -e
check "$W/unit/parse_pages.txt" "unit: --parse-page" '^  .*: PARSED all: .*\(exit 0\)$'
lacks "$W/unit/parse_pages.txt" "unit: --parse-page" '\(exit [1-9][0-9]*\)$'
check "$W/unit/drop_deck_out.txt" "unit: a deck-veto line dropped" '^STOP: .*the parse missed or invented a veto line'
# (Sept 30) score.py's one new line, "unrounded (full precision)": koh's committed page with that line added after each ΔMSE
# line (bounds and real errors moved by less than half a printed digit, so they still print as the page says), then the same
# with one real error moved by 0.2 (it no longer prints as the page says: a STOP).
python3 - "$KP" "$W/unit/full_line.txt" "$W/unit/full_line_bad.txt" <<'PYEOF'
import re, sys
src, good, bad = sys.argv[1:4]
lines = open(src, encoding="utf-8").read().split("\n")


def build(real_shift):
    out, real = [], {}
    for ln in lines:
        m = re.match(r"\s*(\S+): real error\s+([\d.]+) \|", ln)
        if m:
            real[m.group(1)] = float(m.group(2))
        out.append(ln)
        m = re.match(r"\s*dMSE new - current: [+-][\d.]+ points\^2, 95% interval ([+-][\d.]+) to ([+-][\d.]+) \(", ln)
        if m:
            lo, hi = float(m.group(1)) + 0.012, float(m.group(2)) - 0.013
            out.append(f"  unrounded (full precision): dMSE 95% interval {lo!r} to {hi!r}; real error "
                       + ", ".join(f"{b} {v + real_shift!r}" for b, v in real.items()))
            real = {}
    return "\n".join(out)


open(good, "w", encoding="utf-8").write(build(0.036))
open(bad, "w", encoding="utf-8").write(build(0.2))
PYEOF
set +e
python3 "$O/read_km.py" --parse-page "$W/unit/full_line.txt" > "$W/unit/full_line_out.txt" 2>&1
python3 "$O/read_km.py" --parse-page "$W/unit/full_line_bad.txt" > "$W/unit/full_line_bad_out.txt" 2>&1
set -e
check "$W/unit/full_line_out.txt" "unit: --parse-page on a page with score.py's unrounded line" \
  '^PARSED all: .*unrounded ΔMSE bounds -?[0-9]+\.[0-9]+ to -?[0-9]+\.[0-9]+$' '^PARSED dec: .*unrounded ΔMSE bounds -?[0-9]+\.[0-9]+ to -?[0-9]+\.[0-9]+$'
lacks "$W/unit/full_line_out.txt" "unit: --parse-page on a page with score.py's unrounded line" '^STOP'
check "$W/unit/full_line_bad_out.txt" "unit: an unrounded real error that does not print as the page says" \
  "^STOP: score45\\.py's all block: the unrounded real error for .* but the page prints "

for s in null gain harm worsen worsen_ord below below_nogain ord_below ord_nogain ord_charm m1_low guard guard_below cannot cannot_below \
         skip_winners skip_unnamed reach edge3374 edge3375; do build $s; done

EX_M='^   M[12] \(|LABEL|pooled over 9 rows'
EXTRA="$EX_M" run_reader "$W/null/run" "null: km3 = kta3's own games everywhere" "${V_NA}gain, mechanism\.$"
also 'LABEL .*: SPANS zero' 'This is never an accuracy negative' "records 'cannot pass' for M1" "records 'cannot pass' for M2"
never "${V_NA}.*accuracy-worsening"
EXTRA="$EX_M" run_reader "$W/gain/run" "gain: planted (d) gain and the km3 rates; ΔMSE spans zero, so the fallback" "$V_AD"
also 'the fallback.s four tests all held' '^   M1 \(gates: the fallback\).*: PASS: km3 .* is at or above T = [0-9]+/[0-9]+' \
     '^   M2 \(gates: the fallback\).*: PASS: ' 'a GAIN: the whole 95% interval is above zero' 'THE RESERVE ROUTE'
EXTRA='WORSE|VETO|own side:' run_reader "$W/harm/run" "harm: Lucario's own side, B2e Manectric v Lucario and Scizor hurt" "${V_NA}harm, coverage\.$"
also 'lucario: own side .*WORSE beyond noise'
EXTRA='^   (ΔMSE|LABEL)' run_reader "$W/worsen/run" "worsen: results pushed away from Limitless in the 17 reach cells (under 15%)" "${V_NA}accuracy-worsening\.$"
also 'LABEL .*: wholly ABOVE zero' 'THE RESERVE ROUTE'
EXTRA='^   (ΔMSE|LABEL)' run_reader "$W/worsen_ord/run" "worsen_ord: the same with a footprint of about 20%: the ordinary rule" "${V_NA}accuracy-worsening\.$"
also 'THE ORDINARY RULE' 'LABEL .*: wholly ABOVE zero'
EXTRA="$EX_M|^   (ΔMSE)" run_reader "$W/below/run" "below: reserve route, ΔMSE wholly below zero, M1 under its threshold (reported only)" "$V_AD"
also 'THE RESERVE ROUTE' 'LABEL .*: wholly BELOW zero' '^   M1 \(reported: the ΔMSE label is not .spans.\).*: FAIL: km3 .* is below T'
EXTRA="$EX_M" run_reader "$W/below_nogain/run" "below_nogain: the same without the (d) gain: (d) required on the reserve route" "${V_NA}gain\.$"
also 'LABEL .*: wholly BELOW zero' 'NO gain shown at this size'
EXTRA="$EX_M|^   (ΔMSE)" run_reader "$W/ord_below/run" "ord_below: ordinary route, ΔMSE wholly below zero, M1 under its threshold (reported)" "$V_AD"
also 'THE ORDINARY RULE' 'LABEL .*: wholly BELOW zero' '^   M1 \(reported'
EXTRA="$EX_M" run_reader "$W/ord_nogain/run" "ord_nogain: the same without the (d) gain: (d) required on the ordinary route" "${V_NA}gain\.$"
also 'THE ORDINARY RULE'
EXTRA='WORSE|WHICH READING' run_reader "$W/ord_charm/run" "ord_charm: ord_below + Lucario's own side hurt in the mixed rows: (c) fails, reported on the ordinary rule (K4)" "$V_AD"
also '\(c\) no meta deck worse +FAIL \(reported\)' 'WHICH READING DECIDED \(K4\): \(c\) no meta deck.s own side worse beyond paired noise FAILED'
EXTRA="$EX_M" run_reader "$W/m1_low/run" "m1_low: km3's Arena rate under T1 in the fallback" "${V_NA}mechanism\.$"
also '^   M1 \(gates: the fallback\).*: FAIL: km3 .* is below T = ' '^   M2 \(gates: the fallback\).*: PASS' 'mechanism not shown at this size'
EXTRA="$EX_M" run_reader "$W/guard/run" "guard: kta3's own Arena rate at or above T1 in the fallback" "${V_NA}mechanism\.$"
also "^   M1 \(gates: the fallback\).*: FAIL: GUARD: $BASE's own rate on the same deals is already at or above T"
EXTRA="$EX_M" run_reader "$W/guard_below/run" "guard_below: the same guard with ΔMSE wholly below zero: reported only" "$V_AD"
also "^   M1 \(reported.*GUARD"
EXTRA="$EX_M" run_reader "$W/cannot/run" "cannot: the amendment records M2 'cannot pass' (the fallback)" "${V_NA}mechanism\.$"
also "M2 \(Training Area\): .*CANNOT PASS \(recorded; the midpoint is not used\); in the amendment" \
     "^   M2 \(gates: the fallback\).*: FAIL: the dated amendment records 'cannot pass' for M2" '^   M1 \(gates: the fallback\).*: PASS'
EXTRA="$EX_M" run_reader "$W/cannot_below/run" "cannot_below: M2 'cannot pass' with ΔMSE wholly below zero: reported only" "$V_AD"
also "^   M2 \(reported.*'cannot pass'"
EXTRA='COVERAGE SHORTCUT|b2e:' run_reader "$W/skip_winners/run" "skip_winners: coverage_skip.txt skips B2e pairing 4 although one deal's moves differ (same winner)" "$V_PEND"
also 'COVERAGE SHORTCUT \(K9\): b2e pairing 4: coverage_skip.txt says SKIP, but 1 of 500 deals differ .*matching winners alone is not enough'
EXTRA='COVERAGE SHORTCUT' run_reader "$W/skip_unnamed/run" "skip_unnamed: a skipped B2e pairing not named in coverage_skip.txt" "$V_PEND"
also 'COVERAGE SHORTCUT \(K9\): b2e pairing 0: skipped without being named in coverage_skip.txt \(holds its test\)'
run_reader "$W/reach/run" "reach: one changed game in Blaziken v Hydreigon (neither Stadium): the integrity line holds the reading" "${V_HELD}ADOPTED\."
also '^        INTEGRITY LINE \(holds the reading; never a registered fail\): 1 changed games in 1 cells whose lists carry no Training Area or Arena'
run_reader "$W/reach/run" "reach, explained: the same with --integrity-explained" "$V_AD" --integrity-explained "$W/reach/explanation.txt"
also '^INTEGRITY LINES EXPLAINED BY A HUMAN'
run_reader "$W/edge3374/run" "edge3374: exactly 3,374 of 22,500 games differ (14.9956%, prints 15.00): the RESERVE route" \
  'km3: 3,374 of 22,500 = 14\.9956% \(15% is 3,375 games\) -> THE RESERVE ROUTE'
also "$V_AD"
run_reader "$W/edge3375/run" "edge3375: exactly 3,375 of 22,500 games differ (15.0000%): the ORDINARY rule" \
  'km3: 3,375 of 22,500 = 15\.0000% \(15% is 3,375 games\) -> THE ORDINARY RULE'
also "$V_AD"

# ---- guards, on copies of a tree made of symlinks
G="$W/guards"; rm -rf "$G"; mkdir -p "$G"
mk() {  # name [source tree, default gain]
  local src=${2:-gain}
  rm -rf "$G/$1"; mkdir -p "$G/$1"
  for f in "$W/$src/run"/*; do
    [ -f "$f" ] || continue
    case $(basename "$f") in reader_output.txt|reuse_output.txt) continue;; esac
    ln -s "$(readlink -f "$f")" "$G/$1/$(basename "$f")"
  done
}
rewrite() {  # guard-folder file python-on-records (rs)
  local f="$G/$1/$2"; local src; src=$(readlink -f "$f"); rm "$f"
  python3 - "$src" "$f" "$3" <<'PYEOF'
import json, sys
rs = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
exec(sys.argv[3])
open(sys.argv[2], "w", encoding="utf-8").write("".join(json.dumps(g, sort_keys=True) + "\n" for g in rs))
PYEOF
}
rejson() {  # guard-folder python-on-j (thresholds.json)
  local f="$G/$1/thresholds.json"; local src; src=$(readlink -f "$f"); rm "$f"
  python3 - "$src" "$f" "$2" <<'PYEOF'
import json, sys
from fractions import Fraction
j = json.load(open(sys.argv[1], encoding="utf-8"))
exec(sys.argv[3])
json.dump(j, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
PYEOF
}
doctor() {  # guard-folder python-on-t: edit the score45 page a first reader run left in <folder>/pages
  local p="$G/$1/pages/score45_${CAND}_vs_${BASE}.txt"
  python3 - "$p" "$2" <<'PYEOF'
import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t0 = t
exec(sys.argv[2])
assert t != t0, "the doctored page did not change"
open(p, "w", encoding="utf-8").write(t)
PYEOF
}
# ---- the one set (Amendment 1 (b) item 3): the config, the pinned programs, the build they come from
# (Sept 30: this guard read the real km_config.json while B was still unset; once km's reading had set B in it, the check could
# no longer pass on main. It now reads a copy of the real config with the values the cloud reports nulled, as it was then.)
mk cfgunset
python3 - "$O/km_config.json" "$G/cfg_unset.json" <<'PYEOF'
import json, sys
c = json.load(open(sys.argv[1], encoding="utf-8"))
c["build"].update(commit=None, round_head=None, round_folder=None)
json.dump(c, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
PYEOF
run_reader "$G/cfgunset" "guard: the real km_config.json with B not set (a copy with the required values null; nothing is read)" \
  '^STOP: the config .*cfg_unset\.json has required values not set yet \(build\.commit, ' --config "$G/cfg_unset.json"
mkcfg() {  # name python-on-c: a copy of the stand-in config, edited
  python3 - "$CFG" "$G/$1.json" "$2" <<'PYEOF'
import json, sys
c = json.load(open(sys.argv[1], encoding="utf-8"))
exec(sys.argv[3])
json.dump(c, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
PYEOF
}
mk cfgkog; mkcfg cfg_kog3 'c["comparison"]["baseline"] = "kog3"'
run_reader "$G/cfgkog" "guard: a config naming kog3 as km's baseline" "^STOP: the config: .*comparison\.baseline is 'kog3'; km is read against 'kta3'" --config "$G/cfg_kog3.json"
mk cfgsha; mkcfg cfg_sha 'g = c["references"]["groups"]["table"]; g["sha256"] = ("0" if g["sha256"][0] != "0" else "1") + g["sha256"][1:]'
run_reader "$G/cfgsha" "guard: the config's table reference sha256 is not the amendment's (refused when the config is read)" \
  "^STOP: the config: .*references\.groups\.table: sha256 '[0-9a-f]+' not Amendment 1 \(b\) item 3's \(sha256 '6b90d3cf" --config "$G/cfg_sha.json"
mk cfgfresh; mkcfg cfg_fresh 'c["references"]["folder"] = "rl/results/kta_tables_2026-09-29"; g = c["references"]["groups"]["table"]; g.update(file="ec7e1a8_fresh_kta3_table.jsonl", seed_base=23000000000)'
run_reader "$G/cfgfresh" "guard: a config pointing the table group at kta's fresh files, consistently (folder, file, seed base)" \
  "^STOP: the config: .*references\.folder is 'rl/results/kta_tables_2026-09-29', not rl/results/kt_tables_2026-09-28" --config "$G/cfg_fresh.json"
# ---- km's one list (Amendment 1 (b) item 4): km_inputs.sha256 and its STATUS.txt line, checked before anything is read
mk nolist; rm "$G/nolist/km_inputs.sha256"
run_reader "$G/nolist" "guard: no km_inputs.sha256 (the one list; nothing is read)" "^STOP: km's one list: .*/km_inputs\.sha256 does not exist"
mk listline; rm "$G/listline/km_inputs.sha256"; { cat "$W/gain/run/km_inputs.sha256"; echo "# an edit, not recorded"; } > "$G/listline/km_inputs.sha256"
run_reader "$G/listline" "guard: km_inputs.sha256 edited without a dated STATUS.txt line" \
  "^STOP: km's one list: km_inputs\.sha256 has sha256 [0-9a-f]{64}, not the [0-9a-f]{64} STATUS\.txt's last KM INPUTS line records"
mk listcfg; mkcfg cfg_note 'c["about"] += " (a note edited after part I)"'
run_reader "$G/listcfg" "guard: a config other than the one km_inputs.sha256 lists (a note edited after part I)" \
  "^STOP: km's one list: the config loaded \(.*cfg_note\.json, sha256 [0-9a-f]{16}\.\.\.\) is not the one km_inputs\.sha256 lists" --config "$G/cfg_note.json"
mk listsha; rm "$G/listsha/km_inputs.sha256" "$G/listsha/STATUS.txt"
python3 - "$W/gain/run" "$G/listsha" <<'PYEOF'
import hashlib, sys
src, dst = sys.argv[1:3]
ls = open(f"{src}/km_inputs.sha256").read().splitlines()
k = next(j for j, l in enumerate(ls) if not l.startswith("#") and l.split("  ", 1)[1] == "decks/research/lucario.txt")
ls[k] = ("0" if ls[k][0] != "0" else "1") + ls[k][1:]      # the list says another sha256 for a deck list (and STATUS.txt records that list)
open(f"{dst}/km_inputs.sha256", "w").write("\n".join(ls) + "\n")
old, new = (hashlib.sha256(open(p, "rb").read()).hexdigest() for p in (f"{src}/km_inputs.sha256", f"{dst}/km_inputs.sha256"))
open(f"{dst}/STATUS.txt", "w").write(open(f"{src}/STATUS.txt").read().replace(old, new))
PYEOF
run_reader "$G/listsha" "guard: a listed file (decks/research/lucario.txt) is not the sha256 the list records" \
  "^STOP: km's one list: 1 of the list's [0-9]+ files differ: decks/research/lucario\.txt has sha256 [0-9a-f]{16}\.\.\., not the list's"
OB2="$W/otherbuild_b"; rm -rf "$OB2"; cp -r "$FB" "$OB2"
for p in deckgym examples/legality_scan examples/tool_census; do echo "another stand-in program $p (test_read_km.sh)" > "$OB2/engine/target/release/$p"; done
mk listprog; rm "$G/listprog/programs.txt" "$G/listprog/STATUS.txt"
python3 - "$W/gain/run" "$G/listprog" "$FB" "$OB2" <<'PYEOF'
import hashlib, sys
src, dst, fb, ob = sys.argv[1:5]
sh = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()   # noqa: E731
st, out = open(f"{src}/STATUS.txt").read(), []
for ln in open(f"{src}/programs.txt").read().splitlines():   # the same names in another build folder of B, other bytes
    s, p = ln.split("  ", 1)
    q = p.replace(fb + "/", ob + "/")
    out.append(f"{sh(q)}  {q}")
    st = st.replace(s, sh(q))                                  # STATUS.txt's part B line agrees with programs.txt
open(f"{dst}/programs.txt", "w").write("\n".join(out) + "\n")
open(f"{dst}/STATUS.txt", "w").write(st)
PYEOF
run_reader "$G/listprog" "guard: programs.txt and STATUS.txt's part B line agree on programs (in a build of B) other than the list's" \
  "^STOP: programs\.txt does not name km_inputs\.sha256's three programs with their sha256"
mk statusb; rm "$G/statusb/STATUS.txt"; sed -E 's/ deckgym [0-9a-f]{64} / deckgym 0000000000000000000000000000000000000000000000000000000000000000 /' "$W/gain/run/STATUS.txt" > "$G/statusb/STATUS.txt"
run_reader "$G/statusb" "guard: STATUS.txt's part B line gives another deckgym hash than programs.txt" \
  "^STOP: STATUS\.txt's 'KM PART B DONE $PX' line does not give programs\.txt's three sha256"
OB="$W/otherbuild"; rm -rf "$OB"; cp -r "$FB" "$OB"; echo "0123456789abcdef0123456789abcdef01234567" > "$OB/COMMIT"
mk othercommit; rm "$G/othercommit/programs.txt"; sed "s#$FB/#$OB/#" "$W/gain/run/programs.txt" > "$G/othercommit/programs.txt"
run_reader "$G/othercommit" "guard: the programs lie in a build folder of another commit than B" \
  "^STOP: .*otherbuild/engine/target/release/deckgym lies in a build folder whose COMMIT is '0123456789abcdef0123456789abcdef01234567', not B"
OP="$R/rl/engine-2026-09-28/deckgym"
if [ -f "$OP" ]; then
  mk underrl; rm "$G/underrl/programs.txt"; { echo "$(sha256sum "$OP" | cut -d' ' -f1)  $OP"; grep -v '/deckgym$' "$W/gain/run/programs.txt"; } > "$G/underrl/programs.txt"
  run_reader "$G/underrl" "guard: programs.txt names the official program (rl/engine-2026-09-28/deckgym, whose kta<N> is kp-based)" \
    "^STOP: programs\.txt names .*rl/engine-2026-09-28/deckgym, a program under rl/"
fi
mk thrprog; rejson thrprog 'j["counter_tool"]["program_sha256"] = "0" * 64'
run_reader "$G/thrprog" "guard: thresholds.json's sample was counted by another counter-tool program than the pinned one" \
  "^STOP: thresholds\.json: the sample's counter tool was sha256 0{64}, not the pinned "
# ---- the reading's own guards
mk nofp; rm "$G/nofp/footprint.txt"
run_reader "$G/nofp" "guard: no footprint.txt (refuses before reading anything)" '^STOP: .*/footprint\.txt does not exist'
mk short; rewrite short ${PX}_${CAND}_new17.jsonl 'rs[:] = rs[:8400]'
run_reader "$G/short" "guard: km3's new-cell file is short (8,400 of 8,500)" '^STOP: .*_km3_new17\.jsonl: 8400 games, expected 8500'
mk fpoff; rm "$G/fpoff/footprint.txt"
python3 - "$W/gain/run/footprint.txt" "$G/fpoff/footprint.txt" <<'PYEOF'
import re, sys
t = open(sys.argv[1]).read()
open(sys.argv[2], "w").write(re.sub(r"^FOOTPRINT: (\d+) of (\d+)(.*?) = [\d.]+%", lambda m: f"FOOTPRINT: {int(m.group(1)) + 1} of "
                                    f"{m.group(2)}{m.group(3)} = {100 * (int(m.group(1)) + 1) / int(m.group(2)):.2f}%", t, flags=re.M))
PYEOF
run_reader "$G/fpoff" "guard: footprint.txt's count is one more than the files' (its percentage consistent with it)" \
  "^STOP: footprint\\.txt says [0-9]+ games differ; $CAND.s files and $BASE.s reference files give [0-9]+"
mk routetext edge3374; rm "$G/routetext/footprint.txt"; sed 's/RESERVE route, clauses (a)-(e)/ORDINARY adoption rule (15% or more)/' "$W/edge3374/run/footprint.txt" > "$G/routetext/footprint.txt"
run_reader "$G/routetext" "guard: footprint.txt's route text (ordinary) against its counts (3,374: reserve)" "^STOP: footprint\.txt's route text .* disagrees"
mk dseed; rewrite dseed ${PX}_d_${CAND}.jsonl 'rs[7000]["seed"] += 1'
run_reader "$G/dseed" "guard: one (d) game moved to another seed (a deal twice, or off its row)" "^STOP: .*_d_$CAND\\.jsonl: "
mk d500; rewrite d500 ${PX}_d_${BASE}.jsonl 'rs[:] = [g for g in rs if g["seed"] < 22_900_000_000]'; rewrite d500 ${PX}_d_${CAND}.jsonl 'rs[:] = [g for g in rs if g["seed"] < 22_900_000_000]'
run_reader "$G/d500" "guard: clause (d) at 500 per row (D2's block missing), not the registered 2,000" "^STOP: \\(d\\) $BASE: 4,500 games, expected 18,000"
mk dseat; rewrite dseat ${PX}_d_${CAND}.jsonl 'b = [g for g in rs if g["seed"] >= 22_900_000_000][10]; b["first_seat"] = 1 - b["first_seat"]'
run_reader "$G/dseat" "guard: a (d) block game with Lucario in the wrong seat" "^STOP: .*_d_$CAND\\.jsonl: .*the block puts Lucario in seat 0 on even j"
mk dbase; rewrite dbase ${PX}_d_${BASE}.jsonl 'rs[3]["moves"] = "0000000000000000"'
run_reader "$G/dbase" "guard: (d)'s kta3 arm on a table deal is not kta3's reference game" "^STOP: \\(d\\)'s $BASE arm, row 0 .*deal 3: not $BASE's reference game"
mk idfail; rm "$G/idfail/identity_check.txt"; sed 's/^\(1 .*\): 560 of 560 games equal on \(.*\); PASS$/\1: 559 of 560 games equal on \2; FAIL/' "$W/gain/run/identity_check.txt" > "$G/idfail/identity_check.txt"
run_reader "$G/idfail" "guard: an identity line failed (559 of 560)" '^STOP: IDENTITY FAILED in identity_check\.txt'
mk idmissing; rm "$G/idmissing/identity_check.txt"
run_reader "$G/idmissing" "guard: no identity record" '^STOP: .*/identity_check\.txt does not exist'
mk idshort; rm "$G/idshort/identity_check.txt"; grep -v "(as $CAND" "$W/gain/run/identity_check.txt" > "$G/idshort/identity_check.txt"
run_reader "$G/idshort" "guard: the identity record lacks the km3 checks (3, 4 and 6's km3 slice)" \
  "^STOP: identity_check\\.txt records 3,904 equal games, rows and files over 11 lines, checks \\['1', '2', '5', '6', '7', '8'\\]"
mk timeover; rm "$G/timeover/${PX}_timing_1.txt"; echo "$BASE 61.0 s wall; $CAND 90.0 s wall; $CAND/$BASE wall 1.475 (limit 1.25: OVER)" > "$G/timeover/${PX}_timing_1.txt"
run_reader "$G/timeover" "guard: the timing line is OVER 1.25x" "^STOP: the timing line is not 'within' the 1\.25x limit"
mk rulef; rm "$G/rulef/${PX}_d_${CAND}.txt"; printf 'bot km3\n\nFindings (occurrences / games affected):\n  RULE evolve: empty slot: 1 / 1\n' > "$G/rulef/${PX}_d_${CAND}.txt"
run_reader "$G/rulef" "guard: a RULE finding in a scan page" "^STOP: a RULE finding in a scan page .*_d_$CAND\\.txt: RULE evolve"
mk nopage; rm "$G/nopage/${PX}_scizor_${CAND}.txt"
run_reader "$G/nopage" "guard: the scan page of a file read is missing (holds the reading)" "${V_HELD}ADOPTED\."
also "^        every file read has its scan page .*: no scan page with a Findings block beside .*_scizor_$CAND\\.jsonl"
mk proghash; rm "$G/proghash/programs.txt"
python3 - "$W/gain/run/programs.txt" "$G/proghash/programs.txt" <<'PYEOF'
import sys
ls = open(sys.argv[1]).read().splitlines()
ls[0] = ("0" if ls[0][0] != "0" else "1") + ls[0][1:]       # deckgym's recorded hash, one hex digit changed
open(sys.argv[2], "w").write("\n".join(ls) + "\n")
PYEOF
run_reader "$G/proghash" "guard: a program on the disk is not the one programs.txt recorded" '^STOP: deckgym: the program on the disk has sha256 '
mk toolsrc; rm "$G/toolsrc/tool_census.rs"; { cat "$W/tool_census.rs"; echo "// edited"; } > "$G/toolsrc/tool_census.rs"
run_reader "$G/toolsrc" "guard: the counter tool's source is not the config's" "^STOP: the counter tool's source .* has sha256 [0-9a-f]+, not the config's 05d7ba41"
mk thrmissing; rm "$G/thrmissing/thresholds.json"
run_reader "$G/thrmissing" "guard: thresholds.json is not in (the amendment precedes any registered km game)" '^STOP: .*thresholds\.json does not exist'
mk thrfloat; rejson thrfloat 'j["lines"]["M1"]["T"] = float(Fraction(j["lines"]["M1"]["T"]))'
run_reader "$G/thrfloat" "guard: thresholds.json gives M1's T as a float" '^STOP: thresholds\.json M1: T is the float .*exact fraction'
mk thrmid; rejson thrmid 'f = Fraction(j["lines"]["M1"]["T"]) + Fraction(1, 10**9); j["lines"]["M1"]["T"] = f"{f.numerator}/{f.denominator}"'
run_reader "$G/thrmid" "guard: thresholds.json's M1 T is not the exact midpoint (off by 1e-9)" '^STOP: thresholds\.json M1: T = .* is not the exact midpoint'
mk thrunamended; run_reader "$G/thrunamended" "guard: the registration has no amendment with the thresholds" \
  "^STOP: thresholds\.json's M1 \(threshold, T = [0-9]+/[0-9]+\) is not in the registration text" --registration "$R/rl/results/trainer_pricing_2026-09-28/REGISTRATION_DRAFT.md"
mk thrlabel; rejson thrlabel 'j["lines"]["M1"]["interval"][0] = 0.0'
run_reader "$G/thrlabel" "guard: thresholds.json says 'threshold' with a lower bound at zero" "^STOP: thresholds\.json M1: says 'threshold' but its lower bound is 0\.0"
mk thrsums; rejson thrsums 'B, C = j["arms"]; L = j["lines"]["M1"]; L[B]["played"] += 1; f = (Fraction(L[B]["played"], L[B]["offered"]) + Fraction(L[C]["played"], L[C]["offered"])) / 2; L["T"] = f"{f.numerator}/{f.denominator}"; open(sys.argv[2] + ".T", "w").write(L["T"])'
rm "$G/thrsums/registration_standin.md"; { cat "$W/gain/run/registration_standin.md"; echo "- M1 (guard thrsums, STAND-IN): T = $(cat "$G/thrsums/thresholds.json.T")."; } > "$G/thrsums/registration_standin.md"; rm "$G/thrsums/thresholds.json.T"
run_reader "$G/thrsums" "guard: thresholds.json's sums are not the sample rows' (consistent T, in the amendment)" "^STOP: thresholds\.json's M1 sums .* are not the sample rows'"
mk ctrbase; rewrite ctrbase ${PX}_counters_${BASE}.jsonl 'rs[100]["moves"] = "0000000000000000"'
run_reader "$G/ctrbase" "guard: the counters' kta3 arm is not kta3's reference game on one deal" "^STOP: the counters' $BASE arm: 1 rows differ from $BASE's reference files"
mk ctrkm; rewrite ctrkm ${PX}_counters_${CAND}.jsonl 'rs[100]["moves"] = "0000000000000000"'
run_reader "$G/ctrkm" "guard: the counters' km3 arm is not km3's game on one deal" "^STOP: the counters' $CAND arm: 1 rows differ from $CAND's own games"
mk ctrshort; rewrite ctrshort ${PX}_counters_${CAND}.jsonl 'rs[:] = rs[:-1]'
run_reader "$G/ctrshort" "guard: the counters' km3 file is short by one row" "^STOP: the counters .*\\($CAND\\): 3399 rows, expected 3400"
mk ctrcounts; rewrite ctrcounts ${PX}_counters_${CAND}.jsonl 'r = next(x for x in rs if x["a"] == "altaria" and x["b"] == "vespiquen"); r["counts"][0]["cards"]["Copycat"]["played"] = 0 if r["counts"][0]["cards"]["Copycat"]["played"] else 1'
run_reader "$G/ctrcounts" "guard: a km3 counter row with kta3's moves but other counts (holds the reading)" "${V_HELD}ADOPTED\."
also "INTEGRITY LINE .*1 counter deals where $CAND.s game has $BASE.s moves but other counts"
mk ctrmiss; rm "$G/ctrmiss/${PX}_counters_${CAND}.jsonl"
run_reader "$G/ctrmiss" "guard: km3's counter rows not in, ΔMSE spans zero: M1 and M2 hold the verdict" "$V_PEND"
also "if the ΔMSE label is 'spans': PENDING: M1"
mk ctrmissb below; rm "$G/ctrmissb/${PX}_counters_${CAND}.jsonl"
run_reader "$G/ctrmissb" "guard: km3's counter rows not in, ΔMSE wholly below zero: they hold nothing (reported only)" "$V_AD"
mk dmissing; rm "$G/dmissing/${PX}_d_${CAND}.jsonl" "$G/dmissing/${PX}_d_${CAND}.txt"
run_reader "$G/dmissing" "guard: clause (d)'s km3 rows are not in" "$V_PEND"
also 'the \(d\) rows are not all in yet'
mk nomixed; rm "$G/nomixed/${PX}_mixed_table_${CAND}_second.jsonl" "$G/nomixed/${PX}_mixed_new17_${CAND}_second.jsonl"
run_reader "$G/nomixed" "guard: the 45 cells' second-direction mixed rows are not in: (c) waits" "$V_PEND"
also "mixed rows, $CAND on the second-named deck: not in yet" "if the ΔMSE label is 'spans': PENDING: \(c\) no meta deck"
mk wl worsen; rm "$G/wl/${PX}_d_${CAND}.jsonl"; ln -s "$(readlink -f "$W/null/run/${PX}_d_${CAND}.jsonl")" "$G/wl/${PX}_d_${CAND}.jsonl"
run_reader "$G/wl" "guard: worsen with no (d) gain: one label, 'above'" "${V_NA}accuracy-worsening\.$"
doctor wl 't = re.sub(r"(dMSE new - current: )[+-][\d.]+( points\^2, 95% interval )[+-][\d.]+ to [+-][\d.]+ \(not below 0\)", r"\g<1>+10.0\g<2>+0.4 to +20.0 (not below 0)", t)'
run_reader "$G/wl" "guard: the same page with the ΔMSE interval +0.4 to +20.0 (lower bound within 5% of the width of 0): NOT ADOPTED under both open labels" \
  '^   => km3 is NOT ADOPTED \(settled under every open label: above and spans\); .*wait for the --reps 20000 rerun' --reuse-45
also '^   page: .*\(reused: ' '^        \[above\] accuracy-worsening$' '^        \[spans\] .*gain' '^      No accuracy negative is recorded yet'
never "${V_NA}" 'This is never an accuracy negative'
mk tau gain
run_reader "$G/tau" "guard: the gain tree, first run (its page is edited next)" "$V_AD"
doctor tau 't = re.sub(r"(real error, current minus new: [+-][\d.]+ points, 90% interval )[+-][\d.]+", r"\g<1>-1.10", t, count=1)'
run_reader "$G/tau" "guard: τ̂ lower bound printed -1.10 (exactly 0.10 from the line) at --reps $REPS: PENDING, the 20,000-rep rerun decides" "$V_PEND" --reuse-45
also '^     PENDING \(gates\) +no harm: the τ̂ margin .*: -1\.10 .*MC-BOUNDARY: within 0\.10 of the -1\.0 line'
# ---- (Sept 30) the gaps the two outcome audits found, fixed in the reader for the next reading (all on stand-in pages):
#   K7's lower edge at full precision, the held-out direction inside the verdict block, the detectable size as real error from
#   the unrounded real error, and clause (d) at four decimals. The pages are the gain tree's own, edited the way the pages
#   above are; a page stands for a decisive run by its sidecar's --reps being rewritten to 20000 (the reader then reads it
#   with --reps 20000 --reuse-45), since score45 itself is never run here at 20,000 replicates.
echo; echo "################ Sept 30 fixes: K7 at full precision, the held-out line in the verdict block, more digits"
mk k7 gain
run_reader "$G/k7" "K7 tree, first run (the gain tree; its page is copied and edited next)" "$V_AD"
resig() {  # guard-folder from-reps to-reps: the page's sidecar records the run's --reps twice (in its args and as "reps")
  python3 - "$G/$1/pages/score45_${CAND}_vs_${BASE}.txt.reps" "$2" "$3" <<'PYEOF'
import json, sys
p, a, b = sys.argv[1:4]
s = json.load(open(p, encoding="utf-8"))
assert s["reps"] == int(a) and s["args"][-2:] == ["--reps", a], "the sidecar records another --reps"
s["reps"], s["args"][-1] = int(b), b
open(p, "w", encoding="utf-8").write(json.dumps(s, sort_keys=True))       # the reader's own format: sorted keys, no trailing newline
PYEOF
}
K7_DOCTOR='t = re.sub(r"(dMSE new - current: )[+-][\d.]+( points\^2, 95% interval )[+-][\d.]+ to [+-][\d.]+ \(not below 0\)", r"\g<1>+10.0\g<2>@LO@ to +20.0 (not below 0)", t); t = re.sub(r"(unrounded \(full precision\): dMSE 95% interval )\S+ to \S+;", r"\g<1>@UN@ to 20.0;", t)'
V_ANY='^   => km3 is (ADOPTED as the working pilot|NOT ADOPTED)'
k7page() {  # guard-folder printed-lower unrounded-lower [more python on t]: the worsen tree's page (results changed on the 45 cells,
  # so a ΔMSE interval other than 0 to 0 is legitimate) with the interval printed "<printed-lower> to +20.0". The gain tree changes
  # no result at all, so the reader rightly refuses any page of it that shows a ΔMSE interval other than 0 to 0.
  local code=${K7_DOCTOR//@LO@/$2}; code=${code//@UN@/$3}
  mk "$1" worsen; cp -r "$W/worsen/run/pages" "$G/$1/pages"
  doctor "$1" "$code; ${4:-pass}"
}
# the lower bound printed +0.0 whose unrounded value is +0.03, read at the decisive --reps: wholly above zero. The same page also
# carries kta3's real error as 13.836 (printed 13.8), for the detectable-size check.
k7page k7above "+0.0" "0.03" 't = re.sub(r"(\s+kta3: real error\s+)[\d.]+( \|)", r"\g<1>13.8\g<2>", t); t = re.sub(r"(unrounded \(full precision\): dMSE 95% interval \S+ to \S+; real error kta3 )\S+(, )", r"\g<1>13.836\g<2>", t)'
resig k7above "$REPS" 20000
run_reader "$G/k7above" "K7: a lower bound printed +0.0 whose unrounded value is +0.03, at the decisive --reps 20000: wholly ABOVE, NOT ADOPTED (accuracy-worsening)" \
  "${V_NA}accuracy-worsening\.$" --reuse-45 --reps 20000
also 'LABEL .*: wholly ABOVE zero' '^   page: .*\(reused: ' \
     "the lower bound prints as \+0\.0; score\.py's unrounded value is 0\.03, so the interval is wholly ABOVE zero \(K7, read at full precision\)"
never 'PENDING between' 'BOUNDARY: the lower bound prints as \+0\.0' '^   page: .*freshly scored'
python3 - "$G/k7above/pages/score45_${CAND}_vs_${BASE}.txt" "$BASE" > "$G/k7above/expected_detectable.txt" <<'PYEOF'
import math, re, sys
t, base = open(sys.argv[1], encoding="utf-8").read(), sys.argv[2]
m = re.search(r"dMSE new - current: [+-][\d.]+ points\^2, 95% interval ([+-][\d.]+) to ([+-][\d.]+)", t)
sd = (float(m.group(2)) - float(m.group(1))) / 3.92


def line(tau, tail):
    ar = lambda d: math.sqrt(tau * tau + d)
    return (f"MDE50 (1.96 sd) {1.96 * sd:.1f} points^2, as real error {tau:.2f} -> {ar(-1.96 * sd):.2f}; "
            f"MDE80 (2.80 sd) {2.80 * sd:.1f}, as real error {tau:.2f} -> {ar(-2.80 * sd):.2f}" + tail)


good = line(13.836, f" (real error after = sqrt({base}'s^2 - δ), from {base}'s real error 13.836 as score.py computes it, unrounded)")
bad = line(13.8, "")
assert line(13.836, "")[:40] != bad[:40] or line(13.836, "") != bad, "the stand-in cannot tell an unrounded input from a rounded one"
print(good)
print(bad)
PYEOF
has "$G/k7above/reader_output.txt" "K7: the detectable size is converted from the unrounded real error (13.836, printed 13.8)" "$(sed -n 1p "$G/k7above/expected_detectable.txt")"
hasnt "$G/k7above/reader_output.txt" "K7: the detectable size is not converted from the page's rounded real error" "$(sed -n 2p "$G/k7above/expected_detectable.txt")"
# printed -0.0 whose true value is -0.03: spans (the fallback), decided at the decisive --reps, not left PENDING
k7page k7spans "-0.0" "-0.03"
resig k7spans "$REPS" 20000
run_reader "$G/k7spans" "K7: a lower bound printed -0.0 (true value -0.03), at the decisive --reps 20000: SPANS zero, decided (the fallback's tests then give the verdict)" "$V_ANY" --reuse-45 --reps 20000
also 'LABEL .*: SPANS zero'
never 'PENDING between' 'wholly ABOVE zero'
# printed +0.0 whose unrounded value is exactly 0: it reaches zero, so it is not above zero: spans
k7page k7zero "+0.0" "0.0"
resig k7zero "$REPS" 20000
run_reader "$G/k7zero" "K7: a lower bound printed +0.0 that is exactly 0, at --reps 20000: not above zero, SPANS, decided" "$V_ANY" --reuse-45 --reps 20000
also 'LABEL .*: SPANS zero' "score\.py's unrounded value is 0\.0, so the interval is not above zero \(it reaches 0\) \(K7, read at full precision\)"
never 'PENDING between' 'wholly ABOVE zero'
# a page whose two lines disagree (printed +0.0, unrounded -0.03) is edited or mixed: a STOP
k7page k7edit "+0.0" "-0.03"
resig k7edit "$REPS" 20000
run_reader "$G/k7edit" "K7: printed +0.0 but an unrounded -0.03 (which would print -0.0): the page's lines disagree" \
  "^STOP: score45's ΔMSE lower bound prints as \+0\.0 but its 'unrounded \(full precision\)' line gives -0\.03" --reuse-45 --reps 20000
# the near-zero rule (K8) is separate and unchanged: below --reps 20000 the same page is still held PENDING
k7page k7pend "+0.0" "0.03"
run_reader "$G/k7pend" "K7 and K8: printed +0.0, unrounded +0.03 at --reps $REPS: the label is still held open (K8 holds it below 20,000 replicates)" "$V_ANY" --reuse-45
also 'MC-BOUNDARY \(lower edge\): \+0\.0 is within 5% of the interval.s width of 0' 'ΔMSE label: PENDING between above and spans'
# a page without score.py's full-precision line (made without --full-precision) is not reused: it is scored afresh, and says why
k7page k7old "+0.0" "0.03" 't = re.sub(r"(?m)^  unrounded \(full precision\):.*\n", "", t)'
run_reader "$G/k7old" "K7: a page without score.py's unrounded line is not reused (scored afresh)" "${V_NA}accuracy-worsening\.$" --reuse-45
also "\(--reuse-45: score45_${CAND}_vs_${BASE}\.txt is not reusable \(it has no 'unrounded \(full precision\)' line \(made without --full-precision\)\); scoring afresh\)" \
     '^   page: .*\(freshly scored, --reps '
never 'NOTE: this score45 page has no .unrounded \(full precision\). line'
# score.py's new line is OPT-IN (--full-precision, off by default; the older readers and the reproduction scripts compare pages line by
# line): the default page is exactly what score45 always printed, and with the flag it differs only by the added lines. score45 is
# run directly on the very files the reader's page names (its "Source:" and "Mixed rows:" lines), with and without the flag.
python3 - "$G/k7/pages/score45_${CAND}_vs_${BASE}.txt" "$R/rl/results/kpf_2026-09-26/reading" "$REPS" "$BASE" "$CAND" <<'PYEOF' > "$G/k7/optin_result.txt"
import os, re, subprocess, sys
page, k45, reps, base, cand = sys.argv[1:6]
text = open(page, encoding="utf-8").read()
src = re.search(r"^Source: (.+?) \+ (.+?) \(current\) vs (.+?) \+ (.+?) \(new\), paired by deal$", text, re.M).groups()   # paths may hold spaces
mixed = re.search(r"^Mixed rows: (.+?) \+ (.+?) \(\d", text, re.M).groups()
cmd = [sys.executable, "-B", os.path.join(k45, "score45.py"), "--rules", "v2", "--old-games", src[0], src[1], "--new-games", src[2], src[3],
       "--old", base, "--new", cand, "--mixed", *mixed, "--reps", reps]


def run(extra):
    r = subprocess.run(cmd + extra, capture_output=True, text=True, encoding="utf-8", cwd=k45, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert r.returncode == 0, r.stderr[-300:]
    return r.stdout + r.stderr


def norm(t):                     # the page names a random temp file for the Limitless cells; nothing else varies between runs
    return re.sub(r"(?m)^(Limitless cells: ).*$", r"\1<temp>", t)


def dropped(t):
    return "".join(l for l in t.splitlines(True) if not l.startswith("  unrounded (full precision):"))


default, flagged = norm(run([])), norm(run(["--full-precision"]))
added = [l for l in flagged.splitlines(True) if l.startswith("  unrounded (full precision):")]
print("OPTIN default page has no unrounded line" if "unrounded (full precision)" not in default else "OPTIN WRONG default page has the line")
print("OPTIN --full-precision adds exactly one line per block (2)" if len(added) == 2 else f"OPTIN WRONG the flag added {len(added)} lines")
print("OPTIN the flagged page minus its added lines is the default page, byte for byte" if dropped(flagged) == default
      else "OPTIN WRONG the flagged page differs from the default in another line")
print("OPTIN the reader's page minus its added lines is the default page, byte for byte" if dropped(norm(text)) == default
      else "OPTIN WRONG the reader's page differs from the default page in another line")
PYEOF
check "$G/k7/optin_result.txt" "score.py's new line is opt-in (default page byte-identical)" \
  '^OPTIN default page has no unrounded line$' '^OPTIN --full-precision adds exactly one line per block \(2\)$' \
  '^OPTIN the flagged page minus its added lines is the default page, byte for byte$' \
  '^OPTIN the reader.s page minus its added lines is the default page, byte for byte$'
lacks "$G/k7/optin_result.txt" "score.py's new line is opt-in (default page byte-identical)" 'OPTIN WRONG'
# the held-out direction is printed inside the verdict block, beside the verdict, and is the section 5a line's figure
sed -n '/^9\. VERDICT/,/THE OUTCOMES THE REGISTRATION FIXES/p' "$G/k7/reader_output.txt" > "$G/k7/verdict_block.txt"
check "$G/k7/verdict_block.txt" "held-out direction: inside the verdict block" \
  "^   Held-out direction beside the verdict \\(RUN5's frame, step 5b item 4; B2e pairings 0-47, $BASE -> $CAND; gates nothing\\): [0-9]+ closer, [0-9]+ further(, [0-9]+ unchanged)?, mean change in miss [+-][0-9]+\\.[0-9]{2}\\.\$"
equal "held-out direction: the verdict block's figure is section 5a's" \
  "$(sed -n 's/^   held-out direction: \(.*\) (reported, gates nothing)$/\1/p' "$G/k7/reader_output.txt")" \
  "$(sed -n 's/^   Held-out direction beside the verdict (.*gates nothing): \(.*\)\.$/\1/p' "$G/k7/verdict_block.txt")"
mk nob2e; rm "$G/nob2e/${PX}_b2e_${CAND}.jsonl" "$G/nob2e/${PX}_b2e_${CAND}.txt"
run_reader "$G/nob2e" "held-out direction: km3's B2e file not in, the verdict block still carries the line ('not in yet')" "$V_PEND"
sed -n '/^9\. VERDICT/,/THE OUTCOMES THE REGISTRATION FIXES/p' "$G/nob2e/reader_output.txt" > "$G/nob2e/verdict_block.txt"
check "$G/nob2e/verdict_block.txt" "held-out direction: not in yet, inside the verdict block" \
  "^   Held-out direction beside the verdict \\(RUN5's frame, step 5b item 4; gates nothing\\): not in yet \\($CAND's B2e both-sides file is not in\\)\\.\$"
# clause (d): the pooled mean, half-width and 95% interval at four decimals, in section 4 and in the verdict block, agreeing with the
# two-decimal line
check "$G/k7/reader_output.txt" "clause (d) at four decimals" \
  '^   pooled, at more digits .*: [+-][0-9]+\.[0-9]{4} \+/- [0-9]+\.[0-9]{4} points; 95% interval [+-][0-9]+\.[0-9]{4} to [+-][0-9]+\.[0-9]{4}; the gate is the lower edge above zero$'
check "$G/k7/verdict_block.txt" "clause (d) at four decimals, in the verdict block" \
  "^     PASS \\(gates\\) +\\(d\\) Lucario's pooled own-side gain, whole 95% interval above zero: [+-][0-9]+\\.[0-9]{4} \\+/- [0-9]+\\.[0-9]{4} points \\(95% interval [+-][0-9]+\\.[0-9]{4} to [+-][0-9]+\\.[0-9]{4}\\) pooled over 9 rows x 2,000"
python3 - "$G/k7/reader_output.txt" > "$G/k7/d_digits.txt" <<'PYEOF'
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
a = re.search(r"pooled over 9 rows \([\d,]+ deals per arm\): ([+-][\d.]+) \+/- ([\d.]+) points", t)
b = re.search(r"pooled, at more digits .*: ([+-][\d.]+) \+/- ([\d.]+) points; 95% interval ([+-][\d.]+) to ([+-][\d.]+);", t)
m, h, lo, hi = (float(x) for x in b.groups())
ok = (f"{m:+.2f}" == a.group(1) and f"{h:.2f}" == a.group(2) and abs((lo + hi) / 2 - m) < 1.5e-4 and abs((hi - lo) / 2 - h) < 1.5e-4)
print("(d) at two and at four decimals agree" if ok else f"(d) MISMATCH: {a.groups()} vs {b.groups()}")
PYEOF
check "$G/k7/d_digits.txt" "clause (d): the four-decimal figures are the two-decimal ones" '^\(d\) at two and at four decimals agree$'
run_reader "$W/gain/run" "footprint-only: sections 1, 1b, then stop" '^\(--footprint-only: stopped after the footprint' --footprint-only
never '^9\. VERDICT'
echo; echo "################ --reuse-45: the page is reused only when made by the same command on the same inputs at the same --reps"
rm -rf "$W/gain/run/pages"/score45_*
for step in "first run (nothing to reuse yet: scored afresh)|$REPS|freshly scored, --reps $REPS" \
            "second run, same --reps (reused)|$REPS|reused: made by this same command on inputs with the same sha256, --reps $REPS" \
            "third run, another --reps (not reusable: scored afresh)|$((REPS + 50))|freshly scored, --reps $((REPS + 50))"; do
  IFS='|' read -r what reps want <<< "$step"
  set +e
  nice -n 19 python3 "$O/read_km.py" --dir "$W/gain/run" --pages-dir "$W/gain/run/pages" --reps "$reps" --reuse-45 --m-reps 200 \
    --registration "$W/gain/run/registration_standin.md" --config "$CFG" > "$W/gain/run/reuse_output.txt" 2>&1
  rc=$?
  set -e
  echo "  $what: exit $rc"
  grep -E "^   page:|--reuse-45:|^WARNING" "$W/gain/run/reuse_output.txt" | cut -c1-160 | sed 's/^/     /'
  check "$W/gain/run/reuse_output.txt" "--reuse-45: $what" "^   page: score45_${CAND}_vs_${BASE}\.txt \($want\)"
done
echo; echo "stand-in trees and every reader output are under $W"
echo; echo "################ CHECKS: $((NCHK - ${#FAILS[@]})) of $NCHK passed"
if [ ${#FAILS[@]} -gt 0 ]; then
  printf '  FAILED: %s\n' "${FAILS[@]}"
  exit 1
fi
echo "every check passed"

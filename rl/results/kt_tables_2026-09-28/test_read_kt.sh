#!/usr/bin/env bash
# Stand-in test for read_kt.py. It builds a fake kt results tree from kog3's own baseline files relabelled as kt3 / kta3
# (so every difference is zero), runs read_kt.py on it, then plants known effects and shows that the reading moves the
# way it should, and that the completeness guards stop it. No kt game is played and NO real kt file is read: every
# reader run below passes --kt-dir at a stand-in folder (never the real one), and the file-free modes (--selftest,
# --parse-page on koh's and earlier readings' score45 pages) read no kt file at all.
#   unit           --selftest (route from integers, the tau / dMSE boundary logic, the veto-line backstop on canned text);
#                  --parse-page on every existing real score45 page (none is kt's; it is lenient only about the event lines
#                  that pages before Sept 28 lack) and on planted breakages of koh's page (a veto line dropped or renamed).
#   null           everything identical to kog3 -> footprint 0%, both codes reserve route; no Rayquaza gain, so (d) fails.
#   gain           a planted own-side gain on the Rayquaza rows for kt3 and kta3 -> (d) passes, everything else zero.
#   harm           kt3 loses Rayquaza wins; kta3 gains on Rayquaza but loses own-side B2e wins (Manectric), Suicune's
#                  own-side mixed rows (and has a footprint in Suicune's cells) -> clause (c) and coverage fail.
#   ordinary       kt3 changes moves in half its games (footprint ~50%) and its scores move halfway to Limitless -> the
#                  ordinary rule, dMSE below zero; kta3 as in "gain" -> reserve route.
#   ordinary_null  kt3 changes moves in half its games but no result -> the ordinary rule, dMSE not below zero.
#   veto           kt3: Suicune v Vespiquen +10.8 and Hydreigon's own score up about 10 in all its cells (a cell and a deck veto
#                  fire), with own-side harm in the mixed rows -> both COUNT, gate b2 FAILS.
#   await          the same both-sides plants, mixed rows identical to kog3 in one direction and the other direction absent ->
#                  both vetoes AWAIT mixed rows, gate b2 is PENDING (parse and gate of the AWAITS branch).
#   c0             a single mixed-row game with different moves in a zero-footprint cell (kta3) -> an INTEGRITY line and a
#                  PENDING gate, never a FAIL; kt3 (untouched) still PASSES.
#   covonly        kt3's Scizor own side hurt (big), kta3's Scizor own side hurt (a fall under 2 points) and a second list's
#                  own side hurt; both fail ONLY through coverage -> the verdict names which reading decided.
#   edge3374/5     kt3 moves differ in exactly 3,374 / 3,375 of 22,500 games: footprint.txt prints 15.00% both times, the
#                  route is reserve at 3,374 and ordinary at 3,375 (decided from the counts, not from the printout).
#   guards         no footprint.txt, a short file, a footprint.txt that disagrees, a footprint.txt whose route text
#                  disagrees with its counts, a changed seed, a short B2e file, two files not in yet (PROVISIONAL), half the
#                  table mixed rows missing (clause (c) waits), an identity replay that failed, no identity record, a
#                  timing line OVER the limit, a clause (d) file missing on the ordinary route (holds nothing);
#                  --footprint-only; --reuse-45 with its sidecar (reused, then refused at other reps).
# Usage (WSL): bash test_read_kt.sh [stand-in folder]      (FULL=1 prints each reader output in full; EXTRA=regex prints matches)
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/kt_tables_2026-09-28"
W=${1:-/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_readkt/standin}
REPS=${REPS:-100}
S=ec7e1a8
mkdir -p "$W"

# ---- the builder (python): the null tree once, then a scenario = symlinks to it plus the files it changes.
cat > "$W/make_standin.py" <<'EOF'
import csv, hashlib, json, os, sys
R, W, scn = sys.argv[1:4]
RES, S = R + "/rl/results", "ec7e1a8"
KOG, KL = RES + "/kog_composition_2026-09-27", RES + "/koh_2026-09-28/laptop_runs"
TSV = RES + "/gauntlet_runs_2026-09-26/tsv"
B2E = next(p for p in (RES + "/koh_2026-09-28/reading/b2e_kog3.jsonl", "/tmp/kt_ref_b2e_kog3.jsonl", "/tmp/koh_cloud/b2e_kog3.jsonl") if os.path.exists(p))
NULL = W + "/null"


def H(tag, g):
    return int(hashlib.md5(f"{tag}:{g['seed']}:{g.get('pairing')}".encode()).hexdigest()[:8], 16)


def flip(g, v):
    g["first_deck_score"] = v
    g["moves"] = hashlib.md5((g["moves"] + "*").encode()).hexdigest()[:16]


def write(dst, src, bots, keep=None, mut=None):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        os.remove(dst)
    with open(src, encoding="utf-8") as f, open(dst, "w", encoding="utf-8") as o:
        for ln in f:
            if not ln.strip():
                continue
            g = json.loads(ln)
            if keep and not keep(g):
                continue
            g["bot_a"], g["bot_b"] = bots
            if mut:
                mut(g)
            o.write(json.dumps(g, sort_keys=True) + "\n")


def write_recs(dst, recs):
    if os.path.lexists(dst):
        os.remove(dst)
    with open(dst, "w", encoding="utf-8") as o:
        for g in recs:
            o.write(json.dumps(g, sort_keys=True) + "\n")


def extras(d):
    """Item 7's identity record and item 4's timing record, synthetic, in run_kt.sh's own line formats."""
    labels = [("k3 v official", 14000), ("kp3 v official", 14000), ("kog3 v table_kog3", 14000), ("kog3 v new17_kog3", 8500),
              ("kq3 v official", 14000), ("kd3 v 43cef0b (official then)", 1120), ("kpr3 v official", 1120),
              ("kog3 B2e i<40 v b2e_kog3", 3840), ("kog3 Scizor i<40 v scizor_kog3", 320)] + \
             [(f"kog3 {v} i<40 v var_{v}_kog3", n) for v, n in (("v-lucario_2", 280), ("v-suicune_2", 280), ("v-weezing_2", 280), ("l-charizardy", 320))]
    with open(f"{d}/identity_check.txt", "w") as f:
        for lab, n in labels:
            f.write(f"{lab}: {n} of {n} equal on ['moves', 'decisions', 'openings', 'winner_seat', 'points', 'seed']\n")
    with open(f"{d}/{S}_timing_1.txt", "w") as f:
        f.write("kog3 61 s wall, 720 s CPU; kt3 67 s wall, 790 s CPU; kt3/kog3 wall 1.10 (limit 1.25: within), CPU 1.10\n")


def null_tree():
    d = NULL
    os.makedirs(d, exist_ok=True)
    tab, n17 = KOG + "/table_kog3.jsonl", KOG + "/new17_kog3.jsonl"
    for bot in ("kt3", "kta3", "ktb3", "ktc3"):
        write(f"{d}/{S}_{bot}_table.jsonl", tab, (bot, bot))
        write(f"{d}/{S}_{bot}_new17.jsonl", n17, (bot, bot))
    # clause (d): kog3 on the Rayquaza list = the Scizor row's structure, relabelled onto the (d) seed block
    def dseed(g):
        g["seed"] = 22_700_000_000 + 10_000 * g["pairing"] + g["i"]
        g["a"] = "c-rayquaza"
    write(f"{d}/{S}_d_kog3.jsonl", KL + "/scizor_kog3.jsonl", ("kog3", "kog3"), mut=dseed)
    for bot in ("kt3", "kta3"):
        write(f"{d}/{S}_mixed_table_{bot}_first.jsonl", tab, (bot, "kog3"))
        write(f"{d}/{S}_mixed_table_{bot}_second.jsonl", tab, ("kog3", bot))
        write(f"{d}/{S}_mixed_new17_{bot}_first.jsonl", n17, (bot, "kog3"))
        write(f"{d}/{S}_mixed_new17_{bot}_second.jsonl", n17, ("kog3", bot))
        write(f"{d}/{S}_b2e_{bot}.jsonl", B2E, (bot, bot))
        write(f"{d}/{S}_mixed_b2e_{bot}_first.jsonl", B2E, (bot, "kog3"))
        write(f"{d}/{S}_scizor_{bot}.jsonl", KL + "/scizor_kog3.jsonl", (bot, bot))
        write(f"{d}/{S}_mixed_scizor_{bot}_first.jsonl", KL + "/scizor_kog3.jsonl", (bot, "kog3"))
        write(f"{d}/{S}_mixed_scizor_{bot}_second.jsonl", KL + "/scizor_kog3.jsonl", ("kog3", bot))
        write(f"{d}/{S}_d_{bot}.jsonl", f"{d}/{S}_d_kog3.jsonl", (bot, "kog3"))
        for v in ("v-lucario_2", "v-suicune_2", "v-weezing_2", "l-charizardy"):
            rows = list(csv.DictReader(open(f"{TSV}/var_{v}.tsv", encoding="utf-8"), delimiter="\t"))
            sa = {int(r["pairing"]) for r in rows if r["variant_side"] == "a"}
            sb = {int(r["pairing"]) for r in rows if r["variant_side"] == "b"}
            src = f"{KL}/var_{v}_kog3.jsonl"
            write(f"{d}/{S}_var_{v}_{bot}.jsonl", src, (bot, bot))
            if sa:
                write(f"{d}/{S}_var_{v}_{bot}_mixed_a.jsonl", src, (bot, "kog3"), keep=lambda g: g["pairing"] in sa)
            if sb:
                write(f"{d}/{S}_var_{v}_{bot}_mixed_b.jsonl", src, ("kog3", bot), keep=lambda g: g["pairing"] in sb)
    extras(d)


def footprint(d):
    def load(p):
        return {(g["a"], g["b"], g["i"]): g for g in map(json.loads, open(p, encoding="utf-8"))}
    base = {**load(KOG + "/table_kog3.jsonl"), **load(KOG + "/new17_kog3.jsonl")}
    lines = []
    for bot in ("kt3", "kta3", "ktb3", "ktc3"):
        new = {**load(f"{d}/{S}_{bot}_table.jsonl"), **load(f"{d}/{S}_{bot}_new17.jsonl")}
        n = sum(base[k]["moves"] != new[k]["moves"] for k in base)
        fp = 100 * n / len(base)
        route = ("reserve route (a)-(e)" if fp < 15 else "ordinary adoption rule") if bot in ("kt3", "kta3") else "attribution only"
        lines.append(f"FOOTPRINT {bot}: {n} of {len(base)} paired games on the 45 cells differ from kog3's = {fp:.2f}% -> {route}")
    fp = f"{d}/footprint.txt"
    if os.path.lexists(fp):
        os.remove(fp)  # never write through a symlink to the null tree's copy
    open(fp, "w").write("\n".join(lines) + "\n")


def limitless():
    v2 = json.load(open(RES + "/scoreboard_v2_2026-09-25/limitless_v2_dev.json"))["cells"]
    lim = {tuple(k.split("|")): tuple(v) for k, v in v2.items()}
    panel = ["lucario", "altaria", "sceptile", "vespiquen", "suicune", "hydreigon", "weezing", "blaziken"]
    new17 = [(x, o) for x in ("rayquaza", "altaria_greninja") for o in panel] + [("rayquaza", "altaria_greninja")]
    gc = {(r["dataset"], r["a"], r["b"]): r for r in csv.DictReader(open(RES + "/gauntlet_runs_2026-09-26/gauntlet_cells.csv"))}
    for a, b in new17:
        r = gc[("development", a, b)]
        lim[(a, b)] = (int(r["W"]), int(r["L"]), int(r["T"]))
    return lim


def scenario_tree(name):
    d = f"{W}/{name}"
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(NULL):
        if not (f.startswith(S + "_") or f in ("footprint.txt", "identity_check.txt")):
            continue  # never link the null run's pages folder or reader_output.txt: a reader would write through the link
        if os.path.lexists(f"{d}/{f}"):
            os.remove(f"{d}/{f}")
        os.symlink(f"{NULL}/{f}", f"{d}/{f}")
    return d


def redo(d, fname, mut, keep=None):
    """Rewrite one file of scenario d from the null tree's copy, applying mut."""
    src = f"{NULL}/{fname}"
    with open(src, encoding="utf-8") as f:
        first = json.loads(f.readline())
    write(f"{d}/{fname}", src, (first["bot_a"], first["bot_b"]), keep=keep, mut=mut)


def gain(g):
    if g["first_deck_score"] == 0.0 and H("gain", g) % 3 == 0:
        flip(g, 1.0)


def loss(g):
    if g["first_deck_score"] == 1.0 and H("loss", g) % 3 == 0:
        flip(g, 0.0)


def soft_loss(g):   # a fall of about 1.5 points on Scizor's rows (harm beyond noise, but not more than 2 points)
    if g["first_deck_score"] == 1.0 and H("soft", g) % 21 == 0:
        flip(g, 0.0)


def veto_plant(g):
    """Both-sides plants: Suicune v Vespiquen's first-deck score up about 11 (its Limitless is 28.5, sim is above it: the miss
    grows by more than 6, a cell veto); Hydreigon's own score up about 10 in every one of its cells (sim is above Limitless
    for it, so its deck gap grows by more than 2: a deck veto)."""
    a, b = g["a"], g["b"]
    if (a, b) == ("suicune", "vespiquen"):
        if g["first_deck_score"] == 0.0 and H("vetoS", g) % 5 == 0:
            flip(g, 1.0)
    elif a == "hydreigon":
        if g["first_deck_score"] == 0.0 and H("vetoH", g) % 5 == 0:
            flip(g, 1.0)
    elif b == "hydreigon":
        if g["first_deck_score"] == 1.0 and H("vetoH", g) % 5 == 0:
            flip(g, 0.0)


if scn == "null":
    null_tree()
    d = NULL
    footprint(d)
elif scn == "null_extras":         # the identity and timing records, added to an existing null tree
    extras(NULL)
    d = NULL
elif scn == "null_footprint":      # only the null tree's footprint.txt, regenerated from its files
    d = NULL
    footprint(d)
elif scn == "gain":
    d = scenario_tree("gain")
    for bot in ("kt3", "kta3"):
        redo(d, f"{S}_d_{bot}.jsonl", gain)
    footprint(d)
elif scn == "harm":
    d = scenario_tree("harm")
    redo(d, f"{S}_d_kt3.jsonl", loss)            # kt3 loses Rayquaza wins
    redo(d, f"{S}_d_kta3.jsonl", gain)           # kta3 gains on Rayquaza ...
    redo(d, f"{S}_mixed_b2e_kta3_first.jsonl", lambda g: (g["first_deck_score"] == 1.0 and g["pairing"] < 8 and H("b2e", g) % 4 == 0) and flip(g, 0.0))
    def moves_change(g):  # a footprint in Suicune's cells only: the moves differ, the result does not
        if "suicune" in (g["a"], g["b"]) and H("fp", g) % 10 == 0:
            flip(g, g["first_deck_score"])
    for f in (f"{S}_kta3_table.jsonl", f"{S}_kta3_new17.jsonl"):  # ... and has a footprint in Suicune's cells
        redo(d, f, moves_change)
    for kind, who in (("first", "a"), ("second", "b")):
        for pre in ("table", "new17"):
            def hurt(g, kind=kind, who=who):
                if g[who] == "suicune" and H("sui", g) % 3 == 0:
                    if kind == "first" and g["first_deck_score"] == 1.0:
                        flip(g, 0.0)
                    if kind == "second" and g["first_deck_score"] == 0.0:
                        flip(g, 1.0)
            redo(d, f"{S}_mixed_{pre}_kta3_{kind}.jsonl", hurt)
    footprint(d)
elif scn in ("ordinary", "ordinary_null"):
    d = scenario_tree(scn)
    lim = limitless()
    for bot in ("kt3",):
        for f, srcp in ((f"{S}_{bot}_table.jsonl", None), (f"{S}_{bot}_new17.jsonl", None)):
            recs = [json.loads(l) for l in open(f"{NULL}/{f}", encoding="utf-8")]
            cells = {}
            for g in recs:
                cells.setdefault((g["a"], g["b"]), []).append(g)
            for cell, gs in cells.items():
                w, l, t = lim[cell]
                L = (w + 0.5 * t) / (w + l + t)
                s = sum(g["first_deck_score"] for g in gs) / len(gs)
                for g in gs:                                   # half the games change moves (footprint about 50%)
                    if g["i"] % 2 == 0:
                        g["moves"] = hashlib.md5((g["moves"] + "#").encode()).hexdigest()[:16]
                if scn == "ordinary":                          # results move halfway to Limitless
                    k = round(abs(L - s) * 0.5 * len(gs))
                    pool = sorted((g for g in gs if g["first_deck_score"] == (1.0 if L < s else 0.0)), key=lambda g: H("ord", g))
                    for g in pool[:k]:
                        flip(g, 0.0 if L < s else 1.0)
            write_recs(f"{d}/{f}", recs)
    for bot in ("kta3",):
        redo(d, f"{S}_d_{bot}.jsonl", gain)
    footprint(d)
elif scn in ("veto", "await"):
    d = scenario_tree(scn)
    for f in (f"{S}_kt3_table.jsonl", f"{S}_kt3_new17.jsonl"):
        redo(d, f, veto_plant)
    if scn == "veto":
        for kind in ("first", "second"):
            for pre in ("table", "new17"):
                def hurt2(g, kind=kind):     # own-side harm: Hydreigon in all its cells, Suicune only in Suicune v Vespiquen
                    who = "a" if kind == "first" else "b"
                    if (g[who] == "hydreigon" or (kind == "first" and (g["a"], g["b"]) == ("suicune", "vespiquen"))) and H("hurt2", g) % 3 == 0:
                        if kind == "first" and g["first_deck_score"] == 1.0:
                            flip(g, 0.0)
                        if kind == "second" and g["first_deck_score"] == 0.0:
                            flip(g, 1.0)
                redo(d, f"{S}_mixed_{pre}_kt3_{kind}.jsonl", hurt2)
    else:                                                # the second direction is not in: the vetoes AWAIT it
        for pre in ("table", "new17"):
            os.remove(f"{d}/{S}_mixed_{pre}_kt3_second.jsonl")
    footprint(d)
elif scn == "c0":
    d = scenario_tree("c0")
    for bot in ("kt3", "kta3"):
        redo(d, f"{S}_d_{bot}.jsonl", gain)
    seen = []
    def one_game(g):                                     # one mixed-row game, zero-footprint cell: different moves, same result
        if not seen and (g["a"], g["b"]) == ("altaria", "blaziken"):
            seen.append(1)
            g["moves"] = hashlib.md5((g["moves"] + "!").encode()).hexdigest()[:16]
    redo(d, f"{S}_mixed_table_kta3_first.jsonl", one_game)
    footprint(d)
elif scn == "covonly":
    d = scenario_tree("covonly")
    for bot in ("kt3", "kta3"):
        redo(d, f"{S}_d_{bot}.jsonl", gain)
    redo(d, f"{S}_mixed_scizor_kt3_first.jsonl", loss)                    # kt3: Scizor's own side down by about 10
    redo(d, f"{S}_mixed_scizor_kta3_first.jsonl", soft_loss)              # kta3: Scizor's own side down by about 1.5
    redo(d, f"{S}_var_v-lucario_2_kta3_mixed_a.jsonl", loss)              # kta3: a second list's own side hurt
    footprint(d)
elif scn in ("edge3374", "edge3375"):
    n = int(scn[4:])
    d = scenario_tree(scn)
    fs = (f"{S}_kt3_table.jsonl", f"{S}_kt3_new17.jsonl")
    recs = {f: [json.loads(l) for l in open(f"{NULL}/{f}", encoding="utf-8")] for f in fs}
    order = sorted((H("edge", g), f, j) for f in fs for j, g in enumerate(recs[f]))
    for _, f, j in order[:n]:                            # exactly n games get different moves; no result changes
        recs[f][j]["moves"] = hashlib.md5((recs[f][j]["moves"] + "#").encode()).hexdigest()[:16]
    for f in fs:
        write_recs(f"{d}/{f}", recs[f])
    footprint(d)
print("built", scn)
EOF

# ---- helpers
show() {  # the footprint + preconditions block, and the verdict block, of a reader run (full output is kept in the folder)
  if [ "${FULL:-0}" = 1 ]; then cat "$1"; return; fi
  sed -n '/^1\. THE FOOTPRINT/,/^NOTES/p' "$1" | sed '$d'
  if [ -n "${EXTRA:-}" ]; then echo "   [...selected lines of sections 2-6, EXTRA=$EXTRA...]"; grep -E "$EXTRA" "$1" | cut -c1-330 || true; fi
  echo "   [...sections 2-6 omitted here; the full output is $1]"
  sed -n '/^7\. VERDICT/,$p' "$1"
}
run_reader() {  # scenario-folder label extra-args...
  local dir=$1 label=$2; shift 2
  echo; echo "################ $label"
  mkdir -p "$dir/pages"
  set +e
  nice -n 10 python3 "$O/read_kt.py" --kt-dir "$dir" --pages-dir "$dir/pages" --reps "$REPS" "$@" > "$dir/reader_output.txt" 2>&1
  local rc=$?
  set -e
  echo "(exit code $rc)"
  if [ $rc -ne 0 ]; then tail -n 4 "$dir/reader_output.txt" | cut -c1-700; else show "$dir/reader_output.txt"; fi
  return 0
}
build() { python3 "$W/make_standin.py" "$R" "$W" "$1"; }

# ---- unit tests that read no kt file at all
echo; echo "################ unit: --selftest (route from the integers; tau and dMSE boundary logic; veto-line backstop on canned text)"
python3 "$O/read_kt.py" --selftest
echo; echo "################ unit: --parse-page on every existing real score45 page (none is kt's; older pages may predate today's format)"
set +e
while IFS= read -r p; do
  out=$(python3 "$O/read_kt.py" --parse-page "$p" 2>&1); rc=$?
  echo "  ${p#$R/rl/results/}: $(echo "$out" | head -n 1 | cut -c1-150) (exit $rc)"
done < <(find "$R/rl/results" -name 'score45_*.txt' -not -path '*kt_tables*' | sort)
set -e
echo; echo "################ unit: koh's page with a veto line dropped or a status renamed must STOP (the veto-line backstop)"
KP="$R/rl/results/koh_2026-09-28/laptop_reading/score45_koh3_vs_kog3.txt"
mkdir -p "$W/unit"
grep -v '^    deck hydreigon +3.7' "$KP" > "$W/unit/drop_deck_line.txt"
grep -v '^    blaziken v weezing +10.7' "$KP" > "$W/unit/drop_cell_line.txt"
sed 's/: COUNTS:/: COUNTED:/' "$KP" > "$W/unit/rename_status.txt"
set +e
for t in drop_deck_line drop_cell_line rename_status; do
  out=$(python3 "$O/read_kt.py" --parse-page "$W/unit/$t.txt" 2>&1); rc=$?
  echo "  $t: exit $rc: $(echo "$out" | head -n 1 | cut -c1-230)"
done
set -e

# ---- the runs
[ -e "$W/null/${S}_kt3_table.jsonl" ] || build null
build null_extras
build null_footprint
for s in gain harm ordinary ordinary_null veto await c0 covonly edge3374 edge3375; do rm -rf "$W/$s"; build $s; done

run_reader "$W/null" "null: kog3's own files relabelled kt3 / kta3 (every difference zero)" --no-attribution
run_reader "$W/gain" "gain: a planted own-side gain on the Rayquaza rows (kt3 and kta3)" --no-attribution
EXTRA='^   page:|Hydreigon|^     \[kta?3\] kog3 [0-9.]+ ->|N4\) ' run_reader "$W/harm" "harm: kt3 loses Rayquaza wins; kta3 has a footprint in Suicune's cells, loses Suicune's and B2e Manectric's own-side wins" --no-attribution
run_reader "$W/ordinary" "ordinary: kt3 at about 50% footprint with scores moved halfway to Limitless; kta3 as in gain (reserve)"
run_reader "$W/ordinary_null" "ordinary_null: kt3 at about 50% footprint, results unchanged" --no-attribution
EXTRA='rule-v2 vetoes that count|NOTE \(N1\)|^   \[kt3\] page' run_reader "$W/veto" "veto: kt3's cell veto (Suicune v Vespiquen) and deck veto (Hydreigon) fire and COUNT through own-side harm in the mixed rows" --no-attribution
EXTRA='rule-v2 vetoes that count|NOTE \(N1\)|not in yet' run_reader "$W/await" "await: the same vetoes, one mixed direction absent: they AWAIT mixed rows (gate b2 PENDING)" --no-attribution
EXTRA='INTEGRITY|integrity:' run_reader "$W/c0" "c0: one mixed-row game with different moves in a zero-footprint cell (kta3): INTEGRITY, PENDING, never FAIL" --no-attribution
EXTRA='second lists:|Scizor|own side: ' run_reader "$W/covonly" "covonly: kt3 and kta3 fail only through the coverage no-harm tests: which reading decided is stated" --no-attribution
run_reader "$W/edge3374" "edge3374: kt3 differs in exactly 3,374 of 22,500 games (14.9956%, prints 15.00): the RESERVE route" --no-attribution
run_reader "$W/edge3375" "edge3375: kt3 differs in exactly 3,375 of 22,500 games (15.0000%): the ORDINARY rule" --no-attribution

# ---- the guards, on copies of the gain tree
G="$W/guards"; rm -rf "$G"; mkdir -p "$G"
mk() {  # name [source scenario, default gain]: a copy of that tree made of symlinks
  local src=${2:-gain}
  rm -rf "$G/$1"; mkdir -p "$G/$1"
  for f in "$W/$src"/${S}_* "$W/$src/footprint.txt" "$W/$src/identity_check.txt"; do ln -s "$(readlink -f "$f")" "$G/$1/$(basename "$f")"; done
}
mk nofp; rm "$G/nofp/footprint.txt"
run_reader "$G/nofp" "guard 1: no footprint.txt (must refuse before reading anything)" --no-attribution
mk short_new17; rm "$G/short_new17/${S}_kt3_new17.jsonl"; head -n 8400 "$W/gain/${S}_kt3_new17.jsonl" > "$G/short_new17/${S}_kt3_new17.jsonl"
run_reader "$G/short_new17" "guard 2: kt3's new-cell table is short (8,400 of 8,500 games)" --no-attribution
mk fp_off; rm "$G/fp_off/footprint.txt"; sed 's/^FOOTPRINT kt3: 0 of/FOOTPRINT kt3: 1 of/' "$W/gain/footprint.txt" > "$G/fp_off/footprint.txt"
run_reader "$G/fp_off" "guard 3: footprint.txt disagrees with the files (kt3 count off by one)" --no-attribution
mk seed; rm "$G/seed/${S}_d_kta3.jsonl"
python3 - "$W/gain/${S}_d_kta3.jsonl" "$G/seed/${S}_d_kta3.jsonl" <<'EOF'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1], encoding="utf-8")]
rows[123]["seed"] += 1   # one game on a different deal
open(sys.argv[2], "w", encoding="utf-8").write("".join(json.dumps(g, sort_keys=True) + "\n" for g in rows))
EOF
run_reader "$G/seed" "guard 4: one game of kta3's Rayquaza rows is on a different deal" --no-attribution
mk short_b2e; rm "$G/short_b2e/${S}_mixed_b2e_kta3_first.jsonl"; head -n 47000 "$W/gain/${S}_mixed_b2e_kta3_first.jsonl" > "$G/short_b2e/${S}_mixed_b2e_kta3_first.jsonl"
run_reader "$G/short_b2e" "guard 5: kta3's B2e own-side mixed rows are short (47,000 of 48,000 games)" --no-attribution
mk missing; rm "$G/missing/${S}_mixed_scizor_kta3_second.jsonl" "$G/missing/${S}_var_l-charizardy_kt3_mixed_a.jsonl"
run_reader "$G/missing" "guard 6: two files not in yet (kta3's Scizor other-direction rows, reported only, so no hold; kt3's Charizard Y own-side rows, which hold kt3 PROVISIONAL)" --no-attribution
mk nomixed; rm "$G/nomixed/${S}_mixed_table_kt3_second.jsonl"
run_reader "$G/nomixed" "guard 7: kt3's table mixed rows are half in (the second-direction file is missing): clause (c) and the vetoes wait" --no-attribution
mk idfail; rm "$G/idfail/identity_check.txt"; sed 's/^k3 v official: 14000 of 14000/k3 v official: 13999 of 14000/' "$W/gain/identity_check.txt" > "$G/idfail/identity_check.txt"
run_reader "$G/idfail" "guard 8: an identity replay failed (13,999 of 14,000): item 7, nothing is read" --no-attribution
mk idmissing; rm "$G/idmissing/identity_check.txt"
run_reader "$G/idmissing" "guard 9: no identity record" --no-attribution
mk timeover; rm "$G/timeover/${S}_timing_1.txt"
echo "kog3 61 s wall, 720 s CPU; kt3 90 s wall, 900 s CPU; kt3/kog3 wall 1.48 (limit 1.25: OVER), CPU 1.25" > "$G/timeover/${S}_timing_1.txt"
run_reader "$G/timeover" "guard 10: the timing line is OVER 1.25x (and no second pair)" --no-attribution
mk routetext edge3374; rm "$G/routetext/footprint.txt"
sed 's/^\(FOOTPRINT kt3: .*\) -> reserve route (a)-(e)$/\1 -> ordinary adoption rule/' "$W/edge3374/footprint.txt" > "$G/routetext/footprint.txt"
run_reader "$G/routetext" "guard 11: footprint.txt's route text (ordinary) disagrees with its counts (3,374 of 22,500 is under 15%)" --no-attribution
mk dmissing_ord ordinary; rm "$G/dmissing_ord/${S}_d_kt3.jsonl"
EXTRA='not in yet|\(d\) rows' run_reader "$G/dmissing_ord" "guard 12: kt3 is on the ORDINARY route and its clause (d) file is not in: reported only, it must NOT hold kt3 PROVISIONAL" --no-attribution
run_reader "$W/gain" "footprint-only: sections 1 and 1b, then stop" --footprint-only
echo; echo "################ --reuse-45: the page is reused only when made by the same command at the same --reps"
mkdir -p "$W/gain/pages"; rm -f "$W/gain/pages"/score45_*
for step in "first run, --reuse-45 (nothing to reuse yet: scored afresh)|$REPS" "second run, same --reps (reused)|$REPS" "third run, another --reps (not reusable: scored afresh)|$((REPS + 50))"; do
  set +e
  nice -n 10 python3 "$O/read_kt.py" --kt-dir "$W/gain" --pages-dir "$W/gain/pages" --reps "${step#*|}" --reuse-45 --no-attribution > "$W/gain/reuse_output.txt" 2>&1
  rc=$?
  set -e
  echo "  ${step%|*}: exit $rc"
  grep -E "^   page:|--reuse-45:|^WARNING" "$W/gain/reuse_output.txt" | cut -c1-200 | sed 's/^/     /'
done
echo; echo "stand-in trees and every reader output are under $W"

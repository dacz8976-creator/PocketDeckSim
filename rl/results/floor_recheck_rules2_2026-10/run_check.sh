#!/usr/bin/env bash
# The floor's pre-use re-check under km3 after rules switch 2 (PLAN.md here; the switch's PLAN.md step 15). Part A.
# A copy of ../floor_recheck_2026-10/run_check.sh (Oct 2's), changed only as PLAN.md says: the new engine's folder and
# hashes, P and its tree, main-8626a35 as the superseded release, Oct 2's files at 2d7082cf as the reference, the
# 10:15-22:00 UTC start rule, and the modes below. The calls are floor.py's and run_screen.py's defaults (km3), except
# the k3 control.
#   bash run_check.sh              the re-check (13,440 games). Start it through rl/strength/launch_detached.sh:
#                                    launch_detached.sh start floor-recheck2 -- bash rl/results/floor_recheck_rules2_2026-10/run_check.sh
#   bash run_check.sh --dry-run    every check, nothing written, no game; prints what a real run would do. Before the pin it
#                                  ends "BEFORE THE PIN: a real run would refuse on ..." (exit 0); a failure that is not the
#                                  pin's own exits 2.
#   bash run_check.sh --engine-check   only the engine and reference checks (run_pages.sh calls this); exit 0 or 2.
# Exit 0: RESULT PASSED. Exit 1: RESULT NOT PASSED. Exit 2: refused to start; no file was written.
# A stop mid-run exits with the failing program's code and logs RECHECK STOPPED, with no RESULT line: not a result.
# It writes only in this folder. Never rerun over existing outputs: move them aside, named, first.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
MODE=run
case "${1:-}" in
  "") ;;
  --dry-run) MODE=dry ;;
  --engine-check) MODE=engine ;;
  *) echo "usage: run_check.sh [--dry-run | --engine-check]"; exit 2 ;;
esac
B6=decks/brews/brew-06-pyukumuku-silvally-payback.txt
B6B=decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt
B5B=decks/brews/brew-05b-meowstic-hatterene-comfey.txt
D14=decks/dustin/14-comfey-raticate-hypno.txt
D07=decks/dustin/07-skarmory-stall.txt

prechecks() {   # explicit checks only: this runs inside "if", where set -e does not apply
  local hm f rc=0 dry=0 shellbad="" pinbad="" timebad=""
  [ "$MODE" = dry ] && dry=1
  if [ "$MODE" != engine ]; then
    hm=$(date -u +%H%M) || { echo "REFUSED: cannot read the clock"; return 2; }
    if [ "${ALLOW_DAYTIME:-0}" != 1 ] && [ $((10#$hm)) -ge 1015 ] && [ $((10#$hm)) -lt 2200 ]; then
      timebad="it is ${hm:0:2}:${hm:2:2} UTC, between 5:15 am and 5 pm Central: the laptop leaves at 7 am and this takes up to an hour (ALLOW_DAYTIME=1 on a day Dustin is home)"
    fi
    if [ "$dry" = 0 ] && [ -z "${LAUNCH_DETACHED_RUN:-}" ]; then
      shellbad+="not started through rl/strength/launch_detached.sh (it outlives the session that starts it)"$'\n'
    fi
    if [ -n "$(env | grep -E '^DECKGYM_' || true)" ]; then
      shellbad+="a DECKGYM_* variable is set: no DECKGYM_* variable is ever set for a floor run"$'\n'
    fi
    for f in PLAN.md run_check.sh run_pages.sh; do
      if ! git ls-files --error-unmatch -- "$D/$f" > /dev/null 2>&1; then
        pinbad+="$f is not committed: the plan and both runners come before any game (they are committed with the pin)"$'\n'
      elif ! git diff --quiet HEAD -- "$D/$f"; then
        pinbad+="$f differs from its commit"$'\n'
      fi
    done
    for f in "$D"/*_games.jsonl "$D"/*_coverage.json "$D"/*-*.md "$D/run_screen.txt" "$D/timing.txt" "$D/verdicts.txt" \
             "$D/run_check.log" "$D/control_k3" "$D/pages"; do
      if [ -e "$f" ]; then shellbad+="$(basename "$f") from an earlier run is here; move it aside, named, first"$'\n'; fi
    done
  fi
  FR_MODE=$MODE python3 - "$D" <<'PRECHECK' || rc=$?
import glob, hashlib, json, os, re, subprocess, sys
D = sys.argv[1]
MODE = os.environ["FR_MODE"]
NEW = "rl/engine-2026-10-12"                                    # rules switch 2's engine folder
PROGS = {"deckgym": "0a9199bca480acf6f862342e042b7f36bb885416659eafeef24485c1783158c4",
         "legality_scan": "bf9d75020558b843a4f71d80a848d9150daff44e34f3b2159c16539b015a0ec7",
         "goldfish": "d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84"}
BUILT = {"deckgym": "/home/dacz8976/engine-rules2-08a9b3a/engine/target/release/deckgym",
         "legality_scan": "/home/dacz8976/engine-rules2-08a9b3a/engine/target/release/examples/legality_scan",
         "goldfish": "/home/dacz8976/engine-rules2-08a9b3a/engine/target/release/examples/goldfish"}
RECORD = "rl/results/engine_switch_rules2_2026-10/programs.sha256"   # sitting 1's builds, never rebuilt
P_COMMIT = "c7a25df49e0b4acdc61f8b78f2cab599d86f5c76"           # P, the final engine commit (switch2.env)
ENGINE_TREE = "70652fff03af511e32a169e16209e158a998dda6"        # P's engine/, the candidate 08a9b3a's
SUPERSEDED = "main-8626a35"
OLD, OLDC = "rl/results/floor_recheck_2026-10", "2d7082cf9fccfd8ae7976c508320f1c8ca4e6b4f"
STEMS = ["brew-06-pyukumuku-silvally-payback", "brew-06b-pyukumuku-silvally-scyther-grass",
         "control_k3/14-comfey-raticate-hypno", "brew-05b-meowstic-hatterene-comfey", "07-skarmory-stall"]
REFS = [f"{OLD}/{s}{x}" for s in STEMS for x in (".md", "_coverage.json", "_games.jsonl")] + [f"{OLD}/run_screen.txt"]
PRICING = "engine/src/players/public_pricing_player.rs"
RUN_SCREEN_STEP10 = "d7bde1af80fa0b80414ced99a056457b8ffef5a352db5b80a3a0f8def6c9ca5b"
INPUTS = ["decks/screen/floor.py", "decks/screen/run_screen.py", "current_engine.py", "lib/deckgym-database.json",
          "lib/brew_pages.py", PRICING, "decks/brews/brew-06-pyukumuku-silvally-payback.txt",
          "decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt", "decks/brews/brew-05b-meowstic-hatterene-comfey.txt",
          "decks/dustin/14-comfey-raticate-hypno.txt", "decks/dustin/07-skarmory-stall.txt"]
bad, pin = [], []        # bad: a failure that is not the pin's own; pin: what the pin itself provides (dry run: reported)


def refuse(msg):
    print("REFUSED: " + msg)
    sys.exit(2)


def git(*a):
    p = subprocess.run(["git", *a], capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def git_out(*a):
    rc, out = git(*a)
    if rc:
        refuse(f"git {' '.join(a)} failed")
    return out


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def blob_equal(path, commit):            # the file on disk is the commit's blob, byte for byte (.gitattributes: -text)
    rc, want = git("rev-parse", "--verify", "--quiet", f"{commit}:{path}")
    return rc == 0 and os.path.isfile(path) and git_out("hash-object", "--", path) == want


rec = {}
for line in open(RECORD, encoding="utf-8"):
    if line.strip():
        h, p = line.split(None, 1)
        rec[p.strip()] = h
for k in PROGS:
    if rec.get(BUILT[k]) != PROGS[k]:
        refuse(f"{RECORD} records {rec.get(BUILT[k])} for {BUILT[k]}, not sitting 1's {PROGS[k]}")
m = json.loads(git_out("show", "HEAD:project_manifest.json")) if blob_equal("project_manifest.json", "HEAD") else None
if m is None:
    pin.append("project_manifest.json differs from HEAD's: the pin must be committed before this runs")
    rel = {}
else:
    rel = m["available_release"]
src = rel.get("source_commit") or ""
engine_pinned = rel.get("artifact") == f"{NEW}/deckgym"
if m is not None and not engine_pinned:
    pin.append(f"the manifest's release is {rel.get('name')} ({rel.get('artifact')}), not rules switch 2's {NEW}/deckgym: "
               "this re-check runs after the pin (the switch's PLAN.md step 15)")
if engine_pinned:
    for k, v in (("legality_scan", f"{NEW}/legality_scan"), ("goldfish", f"{NEW}/goldfish"), ("sha256", PROGS["deckgym"]),
                 ("legality_scan_sha256", PROGS["legality_scan"]), ("goldfish_sha256", PROGS["goldfish"])):
        if rel.get(k) != v:
            bad.append(f"the manifest's available_release {k} is {rel.get(k)!r}, not {v!r}")
    if not re.fullmatch(r"[0-9a-f]{40}", src) or git("cat-file", "-e", src + "^{commit}")[0]:
        refuse(f"the manifest's source_commit {src!r} is not a commit here")
    if rel.get("name") != "main-" + src[:7]:
        bad.append(f"the release is named {rel.get('name')!r}, not main-{src[:7]} (its source commit)")
    if git("rev-parse", "--verify", "--quiet", src + ":engine")[1] != ENGINE_TREE:
        bad.append(f"the source commit {src[:7]}'s engine/ is not P's tree {ENGINE_TREE[:7]}")
    if git("merge-base", "--is-ancestor", P_COMMIT, src)[0]:
        bad.append(f"P ({P_COMMIT[:7]}) is not in the source commit {src[:7]}")
    if git("merge-base", "--is-ancestor", src, "HEAD")[0]:
        bad.append(f"the source commit {src[:7]} is not on HEAD (main)")
    if not any(r.get("name") == SUPERSEDED and r.get("superseded") for r in m.get("historical_releases", [])):
        bad.append(f"{SUPERSEDED} is not in the manifest's historical_releases as superseded")
    sums = {}
    if os.path.isfile(f"{NEW}/SHA256SUMS"):
        for line in open(f"{NEW}/SHA256SUMS", encoding="utf-8"):
            if line.strip():
                h, p = line.split(None, 1)
                sums[os.path.basename(p.strip().lstrip("*"))] = h
    if sums != PROGS:
        bad.append(f"{NEW}/SHA256SUMS does not hold exactly sitting 1's three sums: {sums}")
    for k, h in PROGS.items():
        p = f"{NEW}/{k}"
        if not os.path.isfile(p) or not os.access(p, os.X_OK):
            bad.append(f"{p} is missing or not executable")
            continue
        if sha(p) != h:
            bad.append(f"{p} has sha256 {sha(p)}, not sitting 1's {h}")
        if not blob_equal(p, "HEAD"):
            bad.append(f"{p} is not committed as it is on disk")
    sys.path[:0] = [os.getcwd(), os.path.join(os.getcwd(), "decks", "screen", "panel_ladder_2026-09-26")]
    import current_engine, calibrate  # noqa: E402
    try:
        gym = os.path.relpath(current_engine.resolve(project=os.getcwd()))
    except (OSError, ValueError, KeyError) as e:
        refuse(f"current_engine.py refuses: {e}")
    if gym != f"{NEW}/deckgym":
        bad.append(f"current_engine.py resolves {gym}, not {NEW}/deckgym")
    try:
        pilot, where = calibrate.working_pilot()
    except ValueError as e:
        refuse(f"the screen's and the floor's pilot can't be read: {e}")
    if pilot != "km3":
        bad.append(f"the screen and the floor default to {pilot}, not km3: {where}")
    if not blob_equal(PRICING, src):
        bad.append(f"{PRICING} differs from the source commit's (floor.py reads its pricing-pilot pattern from it)")
for p in REFS:
    if not blob_equal(p, OLDC):
        bad.append(f"{p} is not Oct 2's file as committed at {OLDC[:7]}")
if bad or (pin and MODE != "dry"):
    print("\n".join("REFUSED: " + b for b in bad + pin))
    sys.exit(2)
if engine_pinned:
    print(f"engine {rel['name']} ({rel['artifact']}): deckgym {PROGS['deckgym'][:16]}, legality_scan {PROGS['legality_scan'][:16]}, "
          f"goldfish {PROGS['goldfish'][:16]}, sitting 1's builds of 08a9b3a ({RECORD}), committed with SHA256SUMS; manifest "
          f"committed; source commit {src[:7]} on HEAD, P {P_COMMIT[:7]} in it, engine/ tree {ENGINE_TREE[:7]}; {SUPERSEDED} "
          f"superseded; current_engine.py resolves {gym}; screen and floor default km3; {PRICING} as at {src[:7]}")
else:
    print("BEFORE THE PIN: a real run would refuse on the engine check: " + "; ".join(pin))
print(f"references: Oct 2's {len(REFS)} files in {OLD}/, each its blob at {OLDC[:7]}")
opp_now = sorted(glob.glob("decks/screen/opponents/*.txt"))
for p in INPUTS + opp_now:
    if not os.path.isfile(p):
        print(f"input (reported, not a gate) {p}: MISSING")
        continue
    note = "as at" if blob_equal(p, OLDC) else "CHANGED since"
    if p == "decks/screen/run_screen.py":
        note = ("the one step 10 ran; " if sha(p) == RUN_SCREEN_STEP10 else "NOT the one step 10 ran (d7bde1af); ") + note
    print(f"input (reported, not a gate) {p}: sha256 {sha(p)[:16]}, {note} {OLDC[:7]}")
then = {x for x in git_out("ls-tree", "--name-only", OLDC, "decks/screen/opponents/").splitlines() if x.endswith(".txt")}
if then != set(opp_now):
    print(f"input (reported, not a gate) the panel lists differ from {OLDC[:7]}'s: now {opp_now}, then {sorted(then)}")
PRECHECK
  # rc 2: refused inside the python block (its lines are above)
  if [ "$rc" != 0 ]; then echo "REFUSED: the engine and reference checks did not pass (above)"; return 2; fi
  if [ -n "$timebad" ]; then
    if [ "$dry" = 1 ]; then echo "note: a real run would refuse now: $timebad"; else shellbad+="$timebad"$'\n'; fi
  fi
  if [ "$dry" = 1 ]; then
    if [ -n "$shellbad" ]; then printf '%s' "$shellbad" | sed 's/^/REFUSED: /'; return 2; fi
    if [ -n "$pinbad" ]; then printf '%s' "$pinbad" | sed 's/^/BEFORE THE PIN: a real run would refuse: /'; fi
    return 0
  fi
  if [ -n "$shellbad$pinbad" ]; then printf '%s' "$shellbad$pinbad" | sed 's/^/REFUSED: /'; return 2; fi
  return 0
}

t() { local tag=$1 s; shift; stage=$tag; s=$(date +%s); "$@"; echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }

run() {
  stage=start
  trap 'rc=$?; if [ $rc != 0 ] && [ -n "$stage" ]; then echo "$(date -u +%FT%TZ) RECHECK STOPPED in $stage: exit code $rc (a script, program or system stop, not a result; no RESULT line; move the files of this run aside, named, then start again)"; fi' EXIT
  echo "$(date -u +%FT%TZ) RECHECK START: run_check.sh $(sha256sum "$D/run_check.sh" | cut -c1-16), PLAN.md $(sha256sum "$D/PLAN.md" | cut -c1-16) (sha256; HEAD $(git rev-parse --short HEAD))"
  printf '%s\n' "$PRE"
  local F="python3 decks/screen/floor.py"
  t brew-06 $F "$B6" --out "$D"
  t brew-06b $F "$B6B" --out "$D"
  t control-14-k3 $F "$D14" --out "$D/control_k3" --pilot k3 --meta-pilot k3
  t brew-05b $F "$B5B" --out "$D"
  t deck-07 $F "$D07" --out "$D"
  t run_screen python3 decks/screen/run_screen.py "$B6" "$B6B" --games 240 > "$D/run_screen.txt" 2>&1
  echo "$(date -u +%F\ %T) FLOOR RECHECK DONE" >> "$D/timing.txt"
  stage=
  python3 - "$D" <<'VERDICT'
import json, os, re, sys
D = sys.argv[1]
OLD = "rl/results/floor_recheck_2026-10"
NEW_GYM, NEW_GF = "rl/engine-2026-10-12/deckgym", "rl/engine-2026-10-12/goldfish"
NEW_GF_SHA = "d8cfb7799770e16623c5d5ddc47b3ce55a714d66ec541fa8eb476a77fcf79a84"
OLD_GYM, OLD_GF = "rl/engine-2026-10-02/deckgym", "rl/engine-2026-10-02/goldfish"
OLD_GF_SHA = "cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66"
PAGES = {"brew-06": "brew-06-pyukumuku-silvally-payback", "brew-06b": "brew-06b-pyukumuku-silvally-scyther-grass",
         "control": "control_k3/14-comfey-raticate-hypno", "brew-05b": "brew-05b-meowstic-hatterene-comfey",
         "deck-07": "07-skarmory-stall"}
OCT2 = {"brew-06": 125, "brew-06b": 262, "control": 196, "brew-05b": 577, "deck-07": 1098}
# the engine lines: (Oct 2's text, this run's text, times it occurs)
MD_SUBS = [(f"\n- Engine: {OLD_GYM} (", f"\n- Engine: {NEW_GYM} (", 1),
           (f"\n- Coverage from {OLD_GF} (sha256 {OLD_GF_SHA}; ", f"\n- Coverage from {NEW_GF} (sha256 {NEW_GF_SHA}; ", 1)]
RS_SUBS = [(f"; engine {OLD_GYM})\n", f"; engine {NEW_GYM})\n", 2)]
L, short = [], []


def need(cond, label, text):
    L.append(("PASS " if cond else "NOT MET ") + text)
    if not cond:
        short.append(label)


def page(stem):
    text = open(os.path.join(D, stem + ".md"), encoding="utf-8").read()
    m = re.search(r"\*\*Verdict: (.+?)\.\*\* (\d+) wins in (\d+) games", text)
    verdict = m[1].rsplit(": ", 1)[-1] if m[1].startswith("control reading") else m[1]
    pilots = re.search(r"Pilots: (\S+) on the deck, (\S+) on the panel", text).groups()
    engine = re.search(r"^- Engine: (\S+)", text, flags=re.M)[1]
    opp = {o: int(w) for o, w in re.findall(r"^- (t-[\w-]+): (\d+)/\d+ = ", text, flags=re.M)}
    return dict(verdict=verdict, full=m[1], wins=int(m[2]), n=int(m[3]), pilots=pilots, engine=engine, opp=opp)


def screen(path):
    out, cur = {}, None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"== (\S+): (\d+)/(\d+) ", line)
        if m:
            cur = out.setdefault(m[1], {"total": int(m[2]), "opp": {}})
            continue
        m = re.match(r"\s+(t-[\w-]+)\s+(\d+)-", line)
        if m and cur is not None:
            cur["opp"][m[1]] = int(m[2])
    return out


def compare(rel, subs):       # this run's file v Oct 2's with the engine lines put in; byte for byte
    try:
        new = open(os.path.join(D, rel), "rb").read()
        want = open(os.path.join(OLD, rel), "rb").read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"cannot read ({e})"
    for a, b, n in subs:
        if want.count(a) != n:
            return False, f"Oct 2's file holds the engine line {a.strip()!r} {want.count(a)} times, not {n}"
        want = want.replace(a, b)
    if new == want.encode("utf-8"):
        return True, "equal but for the engine lines" if subs else "byte-equal"
    nl, wl = new.decode("utf-8", "replace").split("\n"), want.split("\n")
    diff = [i for i in range(max(len(nl), len(wl))) if (nl[i] if i < len(nl) else None) != (wl[i] if i < len(wl) else None)]
    if not diff:
        return False, "differs in bytes that do not decode"
    i = diff[0]
    a = repr(nl[i][:160]) if i < len(nl) else "(no line)"
    b = repr(wl[i][:160]) if i < len(wl) else "(no line)"
    more = ", ..." if len(diff) > 10 else ""
    return False, (f"{len(diff)} line{'s' if len(diff) > 1 else ''} differ{'' if len(diff) > 1 else 's'} "
                   f"(line {', '.join(str(j + 1) for j in diff[:10])}{more}); line {i + 1} now: "
                   f"{a}; Oct 2's, engine lines put in: {b}")


P = {}
for k, stem in PAGES.items():
    try:
        P[k] = page(stem)
    except (OSError, TypeError, AttributeError) as e:
        P[k] = None
        need(False, f"{k} page unreadable", f"{k}: the page {stem}.md could not be read ({e})")
try:
    S = screen(os.path.join(D, "run_screen.txt"))
except OSError as e:
    S = {}
    need(False, "run_screen.txt unreadable", f"run_screen.txt could not be read ({e})")
for k in ("brew-06", "brew-06b"):
    p = P[k]
    if p is None:
        continue
    need(p["verdict"] == "fail" and p["pilots"] == ("km3", "km3") and p["n"] == 1920, f"{k} verdict",
         f"{k}: '{p['full']}', {p['wins']} of {p['n']}, pilots {p['pilots'][0]}/{p['pilots'][1]} "
         "(needed: fail, km3 on both sides, 1920 games)")
    s = S.get(PAGES[k], {"total": None, "opp": {}})
    need(len(p["opp"]) == 8 and s["opp"] == p["opp"] and s["total"] == p["wins"], f"{k} run_screen",
         f"{k}: plain run_screen.py per opponent {s['opp'] or 'missing'} (total {s['total']}) v the floor's {p['opp']} "
         f"(total {p['wins']})")
c = P["control"]
if c is not None:
    need(c["verdict"] == "untrusted" and c["pilots"] == ("k3", "k3") and c["n"] == 1920, "control verdict",
         f"control deck 14: '{c['full']}', {c['wins']} of {c['n']} (needed: untrusted, k3 on both sides, 1920 games)")
engines = sorted({p["engine"] for p in P.values() if p})
need(engines == [NEW_GYM] and all(P.values()), "engine line", f"engine on every page: {engines} (needed: {NEW_GYM})")
got = {k: (p["wins"] if p else None) for k, p in P.items()}
need(got == OCT2, "wins differ from Oct 2's",
     "wins equal Oct 2's exactly: " + ", ".join(f"{k} {got[k]} (Oct 2: {OCT2[k]})" for k in PAGES))
files = [(stem + x, MD_SUBS if x == ".md" else []) for stem in PAGES.values()
         for x in (".md", "_coverage.json", "_games.jsonl")] + [("run_screen.txt", RS_SUBS)]
for rel, subs in files:
    good, what = compare(rel, subs)
    need(good, f"{rel} differs", f"{rel} v {OLD}/{rel}: {what}")
name = json.load(open("project_manifest.json", encoding="utf-8"))["available_release"]["name"]
if not short:
    result = (f"RESULT PASSED {name}: the floor stays usable under km3 on {NEW_GYM}. brew-06 fail {got['brew-06']}, "
              f"brew-06b fail {got['brew-06b']}, the deck 14 k3 control untrusted {got['control']}, brew-05b "
              f"{got['brew-05b']}, deck 07 {got['deck-07']:,} (of 1,920 each), Oct 2's exactly; run_screen gives the "
              f"floor's wins per opponent; all {len(files)} outputs equal Oct 2's but for the engine lines")
else:
    result = (f"RESULT NOT PASSED {name}: {len(short)} of {len(L)} checks not met ({'; '.join(short)}); the floor isn't "
              "used until Dustin has seen the pages")
out = [result, ""] + L
with open(os.path.join(D, "verdicts.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(L + ["", result]))
sys.exit(1 if short else 0)
VERDICT
}

PRE=$(prechecks 2>&1) && prc=0 || prc=$?
case "$MODE" in
  dry)
    printf '%s\n' "$PRE"
    [ "$prc" = 0 ] || exit 2
    echo "PLAN (dry run, nothing written): Part A plays floor.py's defaults (km3, 240 games per matchup, seed 7,100) on brew-06," \
         "brew-06b, the k3 control deck 14 (control_k3/), brew-05b and deck 07 (1,920 games each), then run_screen.py on brew-06 and" \
         "brew-06b (240 per matchup); compares all 16 outputs with Oct 2's (rl/results/floor_recheck_2026-10/ at 2d7082cf) with" \
         "the engine lines put in; writes verdicts.txt (RESULT line first), timing.txt and run_check.log here."
    exit 0 ;;
  engine)
    printf '%s\n' "$PRE"; [ "$prc" = 0 ] || exit 2; exit 0 ;;
esac
if [ "$prc" != 0 ]; then printf '%s\n' "$PRE"; exit 2; fi
run 2>&1 | tee -a "$D/run_check.log"

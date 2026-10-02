#!/usr/bin/env bash
# The floor's pre-use re-check under km3 after the rules engine switch (PLAN.md here; the switch's PLAN.md step 15).
# Run after the pin, from anywhere in WSL; it writes only in this folder. The same calls as
# ../floor_recheck_2026-09-30/run_check.sh: the pilots are floor.py's and run_screen.py's defaults (km3), except the k3
# control. Then it compares every output with Sept 30's (as committed at 654d139) and writes verdicts.txt, whose first
# line is the RESULT line.
# Exit 0: RESULT PASSED. Exit 1: RESULT NOT PASSED. Exit 2: refused to start; no file was written.
# A stop mid-run exits with the failing program's code and logs RECHECK STOPPED, with no RESULT line: not a result.
set -euo pipefail
export GIT_OPTIONAL_LOCKS=0
D=$(cd "$(dirname "$0")" && pwd); R=$(cd "$D/../../.." && pwd); cd "$R"
B6=decks/brews/brew-06-pyukumuku-silvally-payback.txt
B6B=decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt
B5B=decks/brews/brew-05b-meowstic-hatterene-comfey.txt
D14=decks/dustin/14-comfey-raticate-hypno.txt
D07=decks/dustin/07-skarmory-stall.txt

refuse() { echo "REFUSED: $*"; exit 2; }

prechecks() {   # explicit checks only: this runs inside "if", where set -e does not apply
  local hm f
  hm=$(date -u +%H%M) || refuse "cannot read the clock"
  if [ "${ALLOW_DAYTIME:-0}" != 1 ] && [ $((10#$hm)) -ge 1030 ] && [ $((10#$hm)) -lt 2200 ]; then
    refuse "it is ${hm:0:2}:${hm:2:2} UTC, between 5:30 am and 5 pm Central: the laptop leaves at 7 am and this takes up to an hour (ALLOW_DAYTIME=1 on a day Dustin is home)"
  fi
  for f in PLAN.md run_check.sh; do
    git ls-files --error-unmatch -- "$D/$f" > /dev/null 2>&1 || refuse "$f is not committed: the plan comes before any game (it is committed with the pin)"
  done
  git diff --quiet HEAD -- "$D/PLAN.md" "$D/run_check.sh" || refuse "the plan or the runner differs from its commit"
  for f in "$D"/*_games.jsonl "$D"/*_coverage.json "$D"/*-*.md "$D/run_screen.txt" "$D/timing.txt" "$D/verdicts.txt" "$D/control_k3"; do
    if [ -e "$f" ]; then refuse "$(basename "$f") from an earlier run is here; move it aside first"; fi
  done
  python3 - "$D" <<'PRECHECK' || { echo "REFUSED: the engine and reference checks did not pass (above)"; exit 2; }
import glob, hashlib, json, os, re, subprocess, sys
D = sys.argv[1]
NEW = "rl/engine-2026-10-02"                                   # the rules pin's engine folder
PROGS = {"deckgym": "2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e",
         "legality_scan": "978912748c83fd6c8ee8e3e966c9a6b95c9fdf1eb9d500c7367b2c1463e71699",
         "goldfish": "cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66"}
BUILT = {"deckgym": "/home/dacz8976/engine-rules-5a18d31/engine/target/release/deckgym",
         "legality_scan": "/home/dacz8976/engine-rules-5a18d31/engine/target/release/examples/legality_scan",
         "goldfish": "/home/dacz8976/engine-rules-5a18d31/engine/target/release/examples/goldfish"}
RECORD = "rl/results/engine_switch_rules_2026-10/programs.sha256"   # sitting 1's builds, never rebuilt
R_COMMIT = "f8cfa9c1df4bbcfb72a3b9d9b0247b081a1ffd26"           # R, sonnet/rules-fixes
ENGINE_TREE = "38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5"        # R's engine/, the candidate 5a18d31's
SUPERSEDED = "main-d363ba8"
OLD, OLDC = "rl/results/floor_recheck_2026-09-30", "654d139d2ae1056f02991e00ce5221079a2b01bc"
STEMS = ["brew-06-pyukumuku-silvally-payback", "brew-06b-pyukumuku-silvally-scyther-grass",
         "control_k3/14-comfey-raticate-hypno", "brew-05b-meowstic-hatterene-comfey", "07-skarmory-stall"]
REFS = [f"{OLD}/{s}{x}" for s in STEMS for x in (".md", "_coverage.json", "_games.jsonl")] + [f"{OLD}/run_screen.txt"]
PRICING = "engine/src/players/public_pricing_player.rs"
RUN_SCREEN_STEP10 = "d7bde1af80fa0b80414ced99a056457b8ffef5a352db5b80a3a0f8def6c9ca5b"
INPUTS = ["decks/screen/floor.py", "decks/screen/run_screen.py", "current_engine.py", "lib/deckgym-database.json",
          "lib/brew_pages.py", PRICING, "decks/brews/brew-06-pyukumuku-silvally-payback.txt",
          "decks/brews/brew-06b-pyukumuku-silvally-scyther-grass.txt", "decks/brews/brew-05b-meowstic-hatterene-comfey.txt",
          "decks/dustin/14-comfey-raticate-hypno.txt", "decks/dustin/07-skarmory-stall.txt"]


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


bad = []
rec = {}
for line in open(RECORD, encoding="utf-8"):
    if line.strip():
        h, p = line.split(None, 1)
        rec[p.strip()] = h
for k in PROGS:
    if rec.get(BUILT[k]) != PROGS[k]:
        refuse(f"{RECORD} records {rec.get(BUILT[k])} for {BUILT[k]}, not sitting 1's {PROGS[k]}")
if not blob_equal("project_manifest.json", "HEAD"):
    refuse("project_manifest.json differs from HEAD's: the pin must be committed before this runs")
m = json.loads(git_out("show", "HEAD:project_manifest.json"))
rel = m["available_release"]
if rel.get("artifact") != f"{NEW}/deckgym":
    refuse(f"the manifest's release is {rel.get('name')} ({rel.get('artifact')}), not the rules pin's {NEW}/deckgym: "
           "this re-check runs after the pin (the rules switch's PLAN.md step 15)")
for k, v in (("legality_scan", f"{NEW}/legality_scan"), ("goldfish", f"{NEW}/goldfish"), ("sha256", PROGS["deckgym"]),
             ("legality_scan_sha256", PROGS["legality_scan"]), ("goldfish_sha256", PROGS["goldfish"])):
    if rel.get(k) != v:
        bad.append(f"the manifest's available_release {k} is {rel.get(k)!r}, not {v!r}")
src = rel.get("source_commit") or ""
if not re.fullmatch(r"[0-9a-f]{40}", src) or git("cat-file", "-e", src + "^{commit}")[0]:
    refuse(f"the manifest's source_commit {src!r} is not a commit here")
if rel.get("name") != "main-" + src[:7]:
    bad.append(f"the release is named {rel.get('name')!r}, not main-{src[:7]} (its source commit)")
if git("rev-parse", "--verify", "--quiet", src + ":engine")[1] != ENGINE_TREE:
    bad.append(f"the source commit {src[:7]}'s engine/ is not R's tree {ENGINE_TREE[:7]}")
if git("merge-base", "--is-ancestor", R_COMMIT, src)[0]:
    bad.append(f"R ({R_COMMIT[:7]}) is not in the source commit {src[:7]}")
if git("merge-base", "--is-ancestor", src, "HEAD")[0]:
    bad.append(f"the source commit {src[:7]} is not in HEAD")
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
        bad.append(f"{p} is not Sept 30's file as committed at {OLDC[:7]}")
if bad:
    print("\n".join("REFUSED: " + b for b in bad))
    sys.exit(2)
print(f"engine {rel['name']} ({rel['artifact']}): deckgym {PROGS['deckgym'][:16]}, legality_scan {PROGS['legality_scan'][:16]}, "
      f"goldfish {PROGS['goldfish'][:16]}, sitting 1's builds of 5a18d31 ({RECORD}), committed with SHA256SUMS; manifest "
      f"committed; source commit {src[:7]} on HEAD, R {R_COMMIT[:7]} in it, engine/ tree {ENGINE_TREE[:7]}; {SUPERSEDED} "
      f"superseded; current_engine.py resolves {gym}; screen and floor default km3; {PRICING} as at {src[:7]}")
print(f"references: Sept 30's {len(REFS)} files in {OLD}/, each its blob at {OLDC[:7]}")
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
}

t() { local tag=$1 s; shift; stage=$tag; s=$(date +%s); "$@"; echo "$tag $(( $(date +%s) - s )) s wall" >> "$D/timing.txt"; }

run() {
  stage=start
  trap 'rc=$?; if [ $rc != 0 ] && [ -n "$stage" ]; then echo "$(date -u +%FT%TZ) RECHECK STOPPED in $stage: exit code $rc (a script, program or system stop, not a result; no RESULT line; move the files of this run aside, then start again)"; fi' EXIT
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
OLD = "rl/results/floor_recheck_2026-09-30"
NEW_GYM, NEW_GF = "rl/engine-2026-10-02/deckgym", "rl/engine-2026-10-02/goldfish"
NEW_GF_SHA = "cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66"
OLD_GYM, OLD_GF = "rl/engine-2026-09-30/deckgym", "rl/engine-2026-09-30/goldfish"
OLD_GF_SHA = "8f6056a0aa3fd232cbd9c7329a63f8542c2f3a20f756a69e466b51a27ce02073"
PAGES = {"brew-06": "brew-06-pyukumuku-silvally-payback", "brew-06b": "brew-06b-pyukumuku-silvally-scyther-grass",
         "control": "control_k3/14-comfey-raticate-hypno", "brew-05b": "brew-05b-meowstic-hatterene-comfey",
         "deck-07": "07-skarmory-stall"}
SEPT30 = {"brew-06": 125, "brew-06b": 262, "control": 196, "brew-05b": 577, "deck-07": 1098}
# the engine lines: (Sept 30's text, this run's text, times it occurs)
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


def compare(rel, subs):       # this run's file v Sept 30's with the engine lines put in; byte for byte
    try:
        new = open(os.path.join(D, rel), "rb").read()
        want = open(os.path.join(OLD, rel), "rb").read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return False, f"cannot read ({e})"
    for a, b, n in subs:
        if want.count(a) != n:
            return False, f"Sept 30's file holds the engine line {a.strip()!r} {want.count(a)} times, not {n}"
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
                   f"{a}; Sept 30's, engine lines put in: {b}")


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
need(got == SEPT30, "wins differ from Sept 30's",
     "wins equal Sept 30's exactly: " + ", ".join(f"{k} {got[k]} (Sept 30: {SEPT30[k]})" for k in PAGES))
files = [(stem + x, MD_SUBS if x == ".md" else []) for stem in PAGES.values()
         for x in (".md", "_coverage.json", "_games.jsonl")] + [("run_screen.txt", RS_SUBS)]
for rel, subs in files:
    good, what = compare(rel, subs)
    need(good, f"{rel} differs", f"{rel} v {OLD}/{rel}: {what}")
name = json.load(open("project_manifest.json", encoding="utf-8"))["available_release"]["name"]
if not short:
    result = (f"RESULT PASSED {name}: the floor stays usable under km3 on {NEW_GYM}. brew-06 fail {got['brew-06']}, "
              f"brew-06b fail {got['brew-06b']}, the deck 14 k3 control untrusted {got['control']}, brew-05b "
              f"{got['brew-05b']}, deck 07 {got['deck-07']:,} (of 1,920 each), Sept 30's exactly; run_screen gives the "
              f"floor's wins per opponent; all {len(files)} outputs equal Sept 30's but for the engine lines")
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

if ! PRE=$(prechecks 2>&1); then printf '%s\n' "$PRE"; exit 2; fi
run 2>&1 | tee -a "$D/run_check.log"

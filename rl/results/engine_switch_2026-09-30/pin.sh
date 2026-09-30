#!/usr/bin/env bash
# The kta/km engine switch, steps 8-11 of PLAN.md (Dustin, Sept 30, verbatim in RUN5: "Yes, pin if all pass
# (Recommended)"; the default pilot "km3 (Recommended)"; rules items "Keep them out (Recommended)"). No games.
# Runs only after prepare.sh's PREPARE DONE, and only if every identity line is n of n. A mismatch stops everything:
# the manifest stays untouched and it goes to Dustin first.
#   8  main (the working copy) moves to a merge commit of 53fc5a1 with parents main and 53fc5a1, as --no-ff makes one:
#      the built candidate itself if main hasn't moved since (prepare.sh gave it the final merge message; checked
#      here), else a fresh merge made off-tree whose engine/ must equal the built candidate's. Checked before the working
#      copy changes: engine/ is B's tree 9c84fef, only the three players files differ from the Sept 28 release
#      (engine/UPSTREAM.md, a note, aside), nothing outside rl/results/, engine/src/players/ and engine/UPSTREAM.md comes
#      with the merge, and it deletes nothing (the existing records it changes are named in the MERGED line and the
#      switch README).
#   9-11 are built in a scratch folder first and checked there; then installed in one go, checked again, committed:
#   9  the three tested programs (their sha256 must equal PIN_STATUS's) for rl/engine-2026-09-30/ with SHA256SUMS;
#      update_manifest.py (main-9b4df9b to the history, superseded); current_engine.py must resolve the new deckgym.
#   10 staged/ run_screen.py and floor.py (default km3; floor.py's pricing-pilot pattern fixed) and the pattern test,
#      only as reviewed (staged/STAGED.sha256) and only if the working copy still has the files they were made from
#      (staged/BASE.sha256); the test, floor.py --self-check and the calibration's pilot reading (km3) must pass.
#   11 docs.patch (the reviewed doc text), filled with the merge and candidate shas, applied to main's docs.
#   Then one pin commit of exactly those files plus this folder (not staged/) and ../floor_recheck_2026-09-30/, as
#   33f56da on Sept 28. It is made from a private index (the installed files exactly as built, the programs with the
#   executable bit, mode 100755), and main moves to it only if main is still where the pin left it. Other sessions'
#   changes elsewhere, staged or not, are left alone. Nothing is pushed.
# Every check that can run before the working copy changes runs first. --check runs only those and changes nothing
# (PIN_CHECK_WITHOUT_PREPARE=1 with --check skips the prepare, identity and program gates, for a dry run before
# prepare has finished). A stop writes "PIN STOPPED: <why>" to PIN_STATUS.txt (pin mode only). A stop after the install
# began undoes it first (each installed file still as the pin wrote it goes back to main's, or away if new; the pin's
# paths are unstaged). The merge stays, and a re-run recognises it. After a hard kill mid-install (no trap ran),
# restore the pin paths first (git status shows them). The pin is done when its commit is on main.
# Just before the pin: python3 make_docs_patch.py (RUN5 moves often; re-review docs.patch if it changed), then --check.
# Usage (WSL): bash pin.sh [--check]        Optional: PIN_BUILD_DIR=<dir with engine/target/release, or that dir>
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O="$R/rl/results/engine_switch_2026-09-30"; S="$O/staged"; P="$R/rl/engine-2026-09-30"
FR="$R/rl/results/floor_recheck_2026-09-30"; STATUS="$O/PIN_STATUS.txt"
B_HEAD=53fc5a1edf35f66873a7cb96f19374048e2e8597       # claude/pensive-ptolemy-spwc0b, the round head; B = 1f6319e
ENGINE_TREE=9c84fefd44a4719678415b0e12a717b8ead373a9  # B's engine/ (and 53fc5a1's): the byte check
OLD=9b4df9bcaeab62f075305f57a2643a4f8f15ff15          # the Sept 28 release's source commit (main-9b4df9b)
CAND_REF=refs/pocketdecksim/engine-switch-candidate   # prepare.sh's CREF (not a branch)
PLAYERS="engine/src/players/mod.rs engine/src/players/public_pricing_player.rs engine/src/players/value_functions.rs"
PIN_PATHS=(project_manifest.json decks/screen/floor.py decks/screen/run_screen.py decks/screen/test_floor_pricing_pilot.py
           START_HERE.md CLAUDE.md rl/RUN5.md rl/engine-2026-09-30)
FOLDERS=(rl/results/engine_switch_2026-09-30 rl/results/floor_recheck_2026-09-30
         ':(exclude)rl/results/engine_switch_2026-09-30/staged' ':(exclude)rl/results/engine_switch_2026-09-30/.prepare.*'
         ':(exclude)rl/results/engine_switch_2026-09-30/*.part' ':(exclude)rl/results/engine_switch_2026-09-30/__pycache__')
COMMIT_PATHS=("${PIN_PATHS[@]}" "${FOLDERS[@]}")
PROGS=(deckgym legality_scan goldfish)
PIN_SUBJECT='^Pin the kta/km engine (main-'   # the pin commit's subject (git log --grep): the pin is done when it is on main
GIT_ID=(-c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com)
MODE=pin; [ "${1:-}" = --check ] && MODE=check
[ -z "${1:-}" ] || [ "$1" = --check ] || { echo "usage: bash pin.sh [--check]"; exit 2; }
now() { date -u +%FT%TZ; }
note() { if [ $MODE = pin ]; then echo "$(now) $*" >> "$STATUS"; fi; echo "$*"; }
PHASE=gates; STOPPED=0; UNDO=""; M=""; PIN_PARENT=""; F=""; INSTALLED=()
stop() {  # the stop line (pin mode); after the install began, the install is undone first
  STOPPED=1
  if [ "$PHASE" = install ]; then undo_install; fi
  if [ $MODE = pin ]; then echo "$(now) PIN STOPPED: $*$UNDO" >> "$STATUS"; fi
  echo "PIN STOPPED: $*$UNDO" >&2; exit 1
}
git_retry() {  # git args...: retried for up to 30 s while another git process holds a lock file (GitHub Desktop, a session)
  local i
  for i in 1 2 3 4 5 6 7 8 9 10; do
    if git "$@" 2> "$TMP/git.err"; then return 0; fi
    grep -q "\.lock': File exists" "$TMP/git.err" || break
    sleep 3
  done
  cat "$TMP/git.err" >&2; return 1
}
git_err() { head -n 2 "$TMP/git.err" 2> /dev/null | tr '\n' ' ' || true; }
undo_install() {  # each installed file still as the pin wrote it goes back to PIN_PARENT's (or away, if new); the pin's
                  # paths are unstaged in the shared index. A file that is not as the pin wrote it is left, and named.
  set +e
  local f n=0 left=""
  PHASE=undone
  git_retry reset -q -- "${COMMIT_PATHS[@]}" || left+="(unstaging failed: git reset -q -- the pin's paths) "
  if [ "$(git rev-parse HEAD)" != "$PIN_PARENT" ]; then
    UNDO="; main moved during the pin (HEAD $(git rev-parse --short HEAD), not ${PIN_PARENT:0:7}), so the installed files are left for a person: ${INSTALLED[*]}"
    return 0
  fi
  for f in "${INSTALLED[@]}"; do
    if [ -f "$f" ] && cmp -s -- "$f" "$F/$f"; then
      if git cat-file -e "$PIN_PARENT:$f" 2> /dev/null; then git show "$PIN_PARENT:$f" > "$f"; else rm -f -- "$f"; fi
      n=$((n + 1))
    elif [ -e "$f" ]; then left+="$f "; fi
  done
  rmdir -- "$P" 2> /dev/null
  UNDO="; the install was undone ($n of ${#INSTALLED[@]} files back as they were${left:+; left: $left}); the merge ${M:0:7} stays and a re-run recognises it"
  return 0
}
on_exit() {
  local rc=$? ph=$PHASE
  set +e
  if [ $rc -ne 0 ] && [ $STOPPED = 0 ] && [ $MODE = pin ]; then
    if [ "$PHASE" = install ]; then undo_install; fi
    echo "$(now) PIN STOPPED: exit code $rc outside a check, in phase $ph (a script, system or signal stop; see the terminal)$UNDO" >> "$STATUS"
  fi
  rm -rf "$TMP"
}
TMP=$(mktemp -d); trap on_exit EXIT; trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
exec 9>/tmp/pocketdecksim_pin_2026-09-30.lock; flock -n 9 || { echo "another pin.sh is running"; STOPPED=1; exit 1; }
cd "$R"

# --- gate 1: not done yet; prepare done, on a commit whose engine/ is B's -------------------------------------------
done_x=$(git log -1 --format=%h --grep="$PIN_SUBJECT" HEAD) || true
if [ -n "$done_x" ]; then echo "the pin is already done: its commit $done_x is on main (nothing to do)"; STOPPED=1; exit 0; fi
SKIP_PREP=0; [ $MODE = check ] && [ "${PIN_CHECK_WITHOUT_PREPARE:-0}" = 1 ] && SKIP_PREP=1
if [ $SKIP_PREP = 0 ]; then   # prepare.sh's lock, held for this whole run: no pin reads (or commits) a pass being rewritten
  exec 8>> "$O/.prepare.lock"
  flock -n 8 || stop "prepare.sh (or a child it left) holds .prepare.lock: a pass is under way; wait for its PREPARE DONE"
fi
if [ $SKIP_PREP = 1 ]; then
  echo "CHECK: prepare, identity and program gates skipped (PIN_CHECK_WITHOUT_PREPARE=1); C = 53fc5a1 for the merge checks"
  C=$B_HEAD
else
  [ -f "$STATUS" ] || stop "no PIN_STATUS.txt: prepare.sh has not run"
  last=$( { grep -E '^PREPARE (HALT|STOPPED|DONE) ' "$STATUS" || true; } | tail -1)
  case $last in "PREPARE DONE "*) ;; *) stop "prepare's last state is not DONE: '${last:-none}'";; esac
  C=$(echo "$last" | cut -d' ' -f3)
  [[ $C =~ ^[0-9a-f]{40}$ ]] || stop "the PREPARE DONE line doesn't name a full commit: '$last'"
  # prepare's HALT and STOPPED lines are governed by the HALT rule below (a quoted sha256sum check may say FAILED), and
  # the pin's own STOPPED and AFTER HALT lines by the pin; a FAILED or MISMATCH anywhere else stops the pin
  if awk '!/^PREPARE (HALT|STOPPED) / && !/^[0-9-]+T[0-9:]+Z PIN (STOPPED:|AFTER HALT)/ && /FAILED|MISMATCH/ {bad = 1}
          END {exit !bad}' "$STATUS"; then
    stop "a FAILED or MISMATCH line in PIN_STATUS.txt outside prepare's HALT and STOPPED lines (a mismatch stops everything and goes to Dustin)"
  fi
  if grep -q '^PREPARE HALT ' "$STATUS"; then   # a gate failed once: "pin if all pass" needs Dustin's word again
    [ -n "${PIN_AFTER_HALT:-}" ] || stop "a PREPARE HALT is on record in PIN_STATUS.txt; 'pin if all pass' no longer covers it. With Dustin's word, run with PIN_AFTER_HALT='<his words>'"
    [ $MODE = pin ] && note "PIN AFTER HALT (Dustin): $PIN_AFTER_HALT"
  fi
  if [ -s "$O/candidate.txt" ]; then
    [ "$(sed -n 's/^candidate //p' "$O/candidate.txt")" = "$C" ] || stop "candidate.txt doesn't name the commit PREPARE DONE names (${C:0:7})"
  fi
fi
git cat-file -e "$C^{commit}" 2>/dev/null || stop "PREPARE DONE names $C, which is not a commit here"
b_engine() {   # $1 = an engine/ tree: equal to B's 9c84fef, engine/UPSTREAM.md (the fork's notes) aside
  [ -z "$(git diff-tree -r --name-only "$ENGINE_TREE" "$1" | grep -vx 'UPSTREAM.md' || true)" ]
}
b_engine "$(git rev-parse "$C:engine")" || stop "the built commit ${C:0:7}'s engine/ is not B's (tree 9c84fef, UPSTREAM.md aside)"
[ "$(git rev-parse "$B_HEAD:engine")" = "$ENGINE_TREE" ] || stop "53fc5a1's engine/ is not tree 9c84fef"
if [ $SKIP_PREP = 0 ] && git rev-parse -q --verify "$CAND_REF" >/dev/null; then
  [ "$(git rev-parse "$CAND_REF")" = "$C" ] || stop "$CAND_REF is not the commit PREPARE DONE names (${C:0:7})"
fi

# --- gate 2: every identity line n of n; each required reference named with its own count; the simulate lines -------
if [ $SKIP_PREP = 0 ]; then
python3 - "$O" "$R" <<'EOF' || stop "identity or simulate lines (printed above)"
import os, re, sys
O, R = sys.argv[1], sys.argv[2]
files = [f for f in ("identity_check.txt", "pin_identity.txt") if os.path.isfile(os.path.join(O, f))]
if "identity_check.txt" not in files:
    print("no identity_check.txt"); sys.exit(1)
lines = [(f, l.rstrip("\n")) for f in files for l in open(os.path.join(O, f), encoding="utf-8")]
extra = ["PIN_STATUS.txt"] + sorted(f for f in os.listdir(O) if re.fullmatch(r".*cli.*\.txt", f))
status = [l.rstrip("\n") for f in extra for l in open(os.path.join(O, f), encoding="utf-8", errors="replace")]
num = lambda s: int(s.replace(",", ""))
PAIR = r"(\d[\d,]*) of (\d[\d,]*)"
bad = []
for f, l in lines:     # switch_check.py's failure words, and the old ones
    if re.search(r"\b(MISMATCH|FAILED|DIFFERS)\b|NOT the expected|RULE findings|panicked", l):
        bad.append(f"{f}: {l}")
    for a, b in re.findall(PAIR, l):
        if num(a) != num(b) or num(b) == 0:
            bad.append(f"{f}: {a} of {b} in: {l}")
REFS = {"kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table.jsonl": 14000, "kta_tables_2026-09-29/ec7e1a8_fresh_kta3_new17.jsonl": 8500,
        "kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl": 14000, "kt_tables_2026-09-28/ec7e1a8_kta3_new17.jsonl": 8500,
        "km_tables_2026-09-30/1f6319e_km3_table.jsonl": 14000, "km_tables_2026-09-30/1f6319e_km3_new17.jsonl": 8500}
for rel, n in REFS.items():
    rows = sum(1 for _ in open(os.path.join(R, "rl", "results", rel), encoding="utf-8"))
    if rows != n:
        bad.append(f"{rel} has {rows} games, expected {n}")
    base = os.path.basename(rel)[:-len(".jsonl")]
    pairs = [num(b) for f, l in lines if base in l for a, b in re.findall(PAIR, l)]
    if rows not in pairs:
        bad.append(f"no identity line names {base} with {rows} of {rows}")
for bot in ("k3", "kp3", "kog3"):     # a label "k3 ..." or a file name "..._k3_500" / "table_k3."
    pairs = [num(b) for f, l in lines if re.search(rf"(?<![a-z0-9]){bot}(?![a-z0-9,])", l) for a, b in re.findall(PAIR, l)]
    if 14000 not in pairs:
        bad.append(f"no identity line for {bot} with 14000 of 14000")
SIM = {"k3": (150, 90, 0), "kp3": (144, 96, 0), "kog3": (149, 91, 0), "kta3": None, "km3": None}  # Sept 28's lines
for bot, want in SIM.items():
    got = set()
    for l in [l for f, l in lines] + status:
        m = re.search(r"Player 0 won: (\d+).*?Player 1 won: (\d+).*?Draws: (\d+)", l)
        if m and f"{bot},{bot}" in l:
            got.add(tuple(map(int, m.groups())))
    if not got or (want and got != {want}):
        bad.append(f"deckgym simulate {bot},{bot}: {sorted(got) or 'no line'}" + (f", expected {want}" if want else ""))
for b in bad:
    print("  ", b)
print(f"identity: {len(lines)} lines in {', '.join(files)}; " + ("all n of n, every reference named with its count, simulate lines as Sept 28" if not bad else f"{len(bad)} problem(s)"))
sys.exit(1 if bad else 0)
EOF
fi

# --- gate 3: the tested programs, found by their PIN_STATUS hashes --------------------------------------------------
declare -A WANT; E=""
if [ $SKIP_PREP = 0 ]; then
  for n in "${PROGS[@]}"; do
    WANT[$n]=$( { grep -E "sha256[: ]+[0-9a-f]{64} +([^ ]*/)?$n( |$)" "$STATUS" || true; } | tail -1 | { grep -oE '[0-9a-f]{64}' || true; } | sed -n 1p)
    [ -n "${WANT[$n]}" ] || stop "no 'sha256 <hash> $n' line in PIN_STATUS.txt"
  done
  cands=(); [ -n "${PIN_BUILD_DIR:-}" ] && cands+=("$PIN_BUILD_DIR")
  if [ -s "$O/programs.sha256" ]; then     # prepare.sh's own record: "<sha256>  <build>/engine/target/release/deckgym"
    while read -r h p; do
      case $p in */deckgym) [ "$h" = "${WANT[deckgym]}" ] || stop "programs.sha256 and PIN_STATUS disagree on deckgym"
                            cands+=("$(dirname "$p")");; esac
    done < "$O/programs.sha256"
  fi
  for d in "$HOME"/engine-switch-"${C:0:7}" "$HOME"/engine-*"${C:0:7}"* "$HOME"/engine-*; do [ -d "$d" ] && cands+=("$d"); done
  sha() { sha256sum < "$1" | cut -c1-64; }
  for d in "${cands[@]}"; do
    e="$d/engine/target/release"; [ -f "$e/deckgym" ] || e="$d"
    [ -f "$e/deckgym" ] && [ -f "$e/examples/legality_scan" ] && [ -f "$e/examples/goldfish" ] || continue
    [ "$(sha "$e/deckgym")" = "${WANT[deckgym]}" ] || continue
    [ "$(sha "$e/examples/legality_scan")" = "${WANT[legality_scan]}" ] || continue
    [ "$(sha "$e/examples/goldfish")" = "${WANT[goldfish]}" ] || continue
    E="$e"; break
  done
  [ -n "$E" ] || stop "no build whose deckgym, legality_scan and goldfish have PIN_STATUS's hashes (set PIN_BUILD_DIR)"
  echo "programs: $E (hashes as PIN_STATUS)"
fi

# --- gate 3b: sizes. GitHub refuses a file of 100 MB; everything the pin commit would carry is here already -----------
big=$( { git ls-files -o -m --exclude-standard -- "${FOLDERS[@]}"
         if [ -n "$E" ]; then printf '%s\n' "$E/deckgym" "$E/examples/legality_scan" "$E/examples/goldfish"; fi; } \
       | while IFS= read -r f; do if [ -f "$f" ] && [ "$(stat -c %s -- "$f")" -gt 95000000 ]; then echo "$f"; fi; done || true)
[ -z "$big" ] || stop "files over 95 MB would go into the pin commit (GitHub refuses 100 MB): $(echo "$big" | tr '\n' ' ')(nothing changed)"

# --- gate 4: the working copy -----------------------------------------------------------------------------------------
[ "$(git symbolic-ref -q --short HEAD || true)" = main ] || stop "the working copy is not on main"
H=$(git rev-parse HEAD)
dirty=$(git status --porcelain --untracked-files=all -- "${PIN_PATHS[@]}" | grep -v ' rl/engine-2026-09-30/' || true)
[ -z "$dirty" ] || stop "uncommitted changes in the pin's own paths (commit or restore them first): $(echo "$dirty" | tr '\n' ';')"
if [ -e "$P" ]; then
  [ $SKIP_PREP = 0 ] && [ -f "$P/SHA256SUMS" ] || stop "rl/engine-2026-09-30 exists and isn't a recorded copy of the tested build"
  while read -r h n; do [ "$h" = "${WANT[$n]:-x}" ] || stop "rl/engine-2026-09-30/$n isn't the tested build"; done < "$P/SHA256SUMS"
  ( cd "$P" && sha256sum -c --quiet SHA256SUMS ) || stop "rl/engine-2026-09-30 doesn't match its SHA256SUMS"
fi
[ -f "$FR/PLAN.md" ] && [ -f "$FR/run_check.sh" ] && [ -f "$FR/check_verdicts.py" ] \
  || stop "floor_recheck_2026-09-30/PLAN.md, run_check.sh and check_verdicts.py must be there (committed with the pin, before any game)"
[ -z "$(ls "$FR" | grep -vxE 'PLAN.md|run_check.sh|check_verdicts.py' || true)" ] || stop "floor_recheck_2026-09-30 has files besides its plan: no game may come before the plan's commit"
# runs in this working copy that the pin would change under them: the screen, floor and calibration scripts (they read
# the manifest, the screen and the floor) and cargo or a program in engine/ (the merge rewrites engine/src/players/).
# By working folder or arguments, so a run in another worktree (PocketDeckSim-sonnet) doesn't count.
busy=""
for d in /proc/[0-9]*; do
  pid=${d#/proc/}; [ "$pid" != "$$" ] || continue
  argv=(); { mapfile -d '' -t argv < "$d/cmdline"; } 2> /dev/null || continue
  [ ${#argv[@]} -gt 0 ] || continue
  args="${argv[*]}"; cwd=$(readlink "$d/cwd" 2> /dev/null || true)
  case "${argv[0]##*/}" in grep|rg) continue;; esac
  here=0; case "$cwd/" in "$R"/*) here=1;; esac; case "$args" in *"$R/"*) here=1;; esac
  case "$args" in
    *run_screen.py*|*floor.py*|*run_calibration.py*|*candidate_run.py*|*trace_pilot.py*)
      if [ $here = 1 ]; then busy+="$pid: $args; "; fi;;
  esac
  case "${argv[0]##*/}" in
    cargo|rustc|deckgym|legality_scan|goldfish|tool_census)
      case "$cwd/" in "$R"/engine/*) busy+="$pid: $args (in engine/); ";; esac;;
  esac
done
[ -z "$busy" ] || stop "a screen, floor, calibration or engine run in this working copy is going; the pin would change its files mid-run: $busy"

# --- gate 5: the merge, computed off-tree and checked before anything changes ----------------------------------------
MERGED=0; FF=0
if git merge-base --is-ancestor "$B_HEAD" "$H"; then          # a re-run after step 8
  M=$( { grep -oE 'MERGED 53fc5a1 into main as [0-9a-f]{40}' "$STATUS" 2>/dev/null || true; } | tail -1 | cut -d' ' -f6)
  [ -n "$M" ] && git merge-base --is-ancestor "$M" "$H" || stop "main already contains 53fc5a1, but not through a merge this script recorded"
  [ "$(git rev-parse "$H:engine")" = "$(git rev-parse "$M:engine")" ] || stop "main contains 53fc5a1 but its engine/ changed since the recorded merge"
  T=$(git rev-parse "$M^{tree}"); BASE=$(git rev-parse "$M^1"); MERGED=1; HOW="already merged (re-run)"
  [ "$M" != "$C" ] || FF=1
elif [ "$(git rev-parse -q --verify "$C^1" || true)" = "$H" ] && [ "$(git rev-parse -q --verify "$C^2" || true)" = "$B_HEAD" ]; then
  M=$C; T=$(git rev-parse "$C^{tree}"); BASE=$H; FF=1
  HOW="a fast-forward to the built candidate, main's merge commit (main hasn't moved since it was made)"
  subj=$(git log -1 --format=%s "$C")   # main carries its message: it must be the final merge message (prepare.sh's)
  case $subj in "Merge claude/pensive-ptolemy-spwc0b at 53fc5a1 into main"*) ;;
    *) stop "the candidate's message is not the final merge message, and main would carry it: '$subj'";; esac
else
  out=$(git merge-tree --write-tree "$H" "$B_HEAD") || stop "merging 53fc5a1 into main ${H:0:7} has conflicts: $(echo "$out" | tail -n +2 | tr '\n' ' ')"
  T=$(echo "$out" | head -1); M=""; BASE=$H; HOW="a fresh merge commit of 53fc5a1 into main ${H:0:7}, made here (main moved since the candidate)"
fi
b_engine "$(git rev-parse "$T:engine")" || stop "the merge's engine/ is not B's tree 9c84fef (UPSTREAM.md aside)"
TE=$(git rev-parse "$T:engine")
[ "$TE" = "$(git rev-parse "$C:engine")" ] || stop "the merge's engine/ differs from the built candidate's in: $(git diff-tree -r --name-only "$(git rev-parse "$C:engine")" "$TE" | tr '\n' ' ')(the pin needs them byte-identical)"
if [ "$TE" = "$ENGINE_TREE" ]; then TEWORD="tree 9c84fef (B's)"; else TEWORD="tree ${TE:0:7} (B's 9c84fef but engine/UPSTREAM.md)"; fi
eng=$(git diff --no-renames --name-only "$OLD" "$T" -- engine ':(exclude)engine/UPSTREAM.md' | tr '\n' ' ' | sed 's/ $//')
[ "$eng" = "$PLAYERS" ] || stop "engine/ against the Sept 28 release changes: $eng (expected only: $PLAYERS; engine/UPSTREAM.md, a note, aside)"
git diff --no-renames --name-status "$BASE" "$T" > "$TMP/merge.ns"
outside=$(cut -f2- "$TMP/merge.ns" | grep -vE '^(rl/results/|engine/src/players/|engine/UPSTREAM\.md$)' || true)
[ -z "$outside" ] || stop "the merge would change files outside rl/results/ and engine/src/players/: $(echo "$outside" | tr '\n' ' ')"
gone=$(awk -F'\t' '$1 != "A" && $1 != "M" {print $1 " " $2}' "$TMP/merge.ns")
[ -z "$gone" ] || stop "the merge would delete or retype files on main: $(echo "$gone" | tr '\n' ';')"
NRES_A=$(awk -F'\t' '$1 == "A" && $2 ~ /^rl\/results\// {n++} END {print n + 0}' "$TMP/merge.ns")
RES_M=$(awk -F'\t' '$1 == "M" && $2 ~ /^rl\/results\// {print $2}' "$TMP/merge.ns")
NRES_M=$(printf '%s' "$RES_M" | grep -c . || true)
RES_M_LINE=$(printf '%s\n' "$RES_M" | paste -sd' ' -)
if [ -n "$RES_M" ]; then RES_M_MD="$NRES_M files, $(printf '%s\n' "$RES_M" | sed 's/.*/`&`/' | paste -sd',' - | sed 's/,/, /g')"
else RES_M_MD="none"; fi
if [ $FF = 1 ]; then
  CAND_NOTE="Main hadn't moved since the candidate, so main's merge commit is the built and replayed candidate ${C:0:7} itself."
else
  CAND_NOTE="Main had moved since the candidate, so \`pin.sh\` made main's merge commit itself; its \`engine/\` equals the built candidate ${C:0:7}'s byte for byte. ${C:0:7} is kept only on the laptop (\`$CAND_REF\`; not a branch, not pushed); elsewhere, build from main's merge commit, the same \`engine/\`."
fi
if [ $MERGED = 0 ]; then       # paths the merge writes must not be dirty or untracked in the working copy
  clash=""
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if [ -e "$f" ] && ! git ls-files --error-unmatch -- "$f" >/dev/null 2>&1; then clash+="$f (untracked); "; fi
  done < <(git diff --no-renames --name-only --diff-filter=A "$H" "$T")
  mod=$( { git diff --name-only; git diff --cached --name-only; } | sort -u | grep -Fx -f <(git diff --no-renames --name-only "$H" "$T") || true)
  [ -z "$mod" ] || clash+="$(echo "$mod" | sed 's/$/ (modified)/' | tr '\n' ';')"
  [ -z "$clash" ] || stop "the merge would overwrite local files: $clash"
fi
echo "merge: $HOW; engine/ = $TEWORD = the built candidate's; engine/ vs 9b4df9b: players only; under rl/results/ $NRES_A files added, $NRES_M existing records changed (${RES_M_LINE:-none}); nothing deleted"

# --- gate 6: step 9's manifest, step 10's staged files and step 11's patch, tried in scratch folders -----------------
( cd "$R" && sha256sum -c --quiet "$S/BASE.sha256" ) || stop "floor.py or run_screen.py changed since staging: re-run make_staged.py and re-review staged/staged.patch"
staged_ok() { [ -s "$S/STAGED.sha256" ] && ( cd "$S" && sha256sum -c --quiet STAGED.sha256 ); }
staged_ok || stop "a staged file or staged.patch is not as make_staged.py recorded it (staged/STAGED.sha256): re-run make_staged.py and re-review staged/staged.patch"
mkdir -p "$TMP/t/decks/screen"
cp "$S/decks/screen/floor.py" "$S/decks/screen/run_screen.py" "$S/decks/screen/test_floor_pricing_pilot.py" "$TMP/t/decks/screen/"
for x in engine lib current_engine.py project_manifest.json; do ln -s "$R/$x" "$TMP/t/$x"; done
ln -s "$R/decks/screen/opponents" "$TMP/t/decks/screen/opponents"
git show "$B_HEAD:engine/src/players/mod.rs" > "$TMP/mod_B.rs"
PLAYERS_MOD_RS="$TMP/mod_B.rs" python3 "$TMP/t/decks/screen/test_floor_pricing_pilot.py" > "$TMP/test.log" 2>&1 \
  || { cat "$TMP/test.log"; stop "the staged pattern test fails against B's mod.rs"; }
python3 "$TMP/t/decks/screen/floor.py" --self-check > /dev/null || stop "the staged floor.py --self-check fails"
wp() { python3 -c "import sys; sys.path.insert(0, sys.argv[1]); import calibrate; print(calibrate.working_pilot(sys.argv[2])[0])" \
         "$R/decks/screen/panel_ladder_2026-09-26" "$1"; }
[ "$(wp "$TMP/t/decks/screen")" = km3 ] || stop "the calibration doesn't read km3 from the staged screen and floor"
git show "HEAD:project_manifest.json" > "$TMP/manifest_base.json" || stop "git show HEAD:project_manifest.json"
if [ $SKIP_PREP = 0 ]; then for n in "${PROGS[@]}"; do echo "${WANT[$n]}  $n"; done
else for n in "${PROGS[@]}"; do printf '%064d  %s\n' 0 "$n"; done; fi > "$TMP/sums_check"
python3 "$O/update_manifest.py" "$H" "$C" "$TMP/sums_check" "$TMP/manifest_base.json" "$TMP/manifest_check.json" --check > /dev/null \
  || stop "update_manifest.py --check fails on main's manifest (nothing changed)"
fill() {  # merge7 out: docs.patch with its placeholders filled; an unknown placeholder fails
  python3 - "$O/docs.patch" "$2" "$1" "${C:0:7}" "$RES_M_MD" "$CAND_NOTE" <<'EOF'
import re, sys
src, out, m7, c7, mod, cand = sys.argv[1:7]
t = open(src, encoding="utf-8").read()
for k, v in (("@CAND_NOTE@", cand), ("@RESULTS_MODIFIED@", mod), ("@MERGE7@", m7), ("@CAND7@", c7)):
    t = t.replace(k, v)
left = sorted(set(re.findall(r"@[A-Z0-9_]+@", t)))
if left:
    sys.exit("docs.patch has unknown placeholders: " + " ".join(left))
open(out, "w", encoding="utf-8", newline="\n").write(t)
EOF
}
build_docs() {  # merge7 dir: main's START_HERE.md, CLAUDE.md and rl/RUN5.md with docs.patch applied (and its two new files)
  local f
  fill "$1" "$TMP/docs_$1.patch" || stop "docs.patch has an unknown placeholder"
  for f in START_HERE.md CLAUDE.md rl/RUN5.md; do
    mkdir -p "$2/$(dirname "$f")"; git show "HEAD:$f" > "$2/$f" || stop "git show HEAD:$f"
  done
  ( cd "$2" && GIT_CEILING_DIRECTORIES="$TMP" git apply "$TMP/docs_$1.patch" ) 2> "$TMP/apply.err" \
    || { cat "$TMP/apply.err" >&2; stop "docs.patch no longer applies to main's docs: re-run make_docs_patch.py and re-review docs.patch"; }
}
build_docs "${H:0:7}" "$TMP/docs_check"
echo "staged screen/floor as reviewed: the test passes against B's mod.rs, self-check passes, calibration reads km3; the new manifest builds; docs.patch applies to main's docs"
if [ $MODE = check ]; then echo "CHECK PASSED: nothing was changed"; exit 0; fi

# ======================================================================================================================
# From here main changes.
# --- step 8: the merge -------------------------------------------------------------------------------------------------
PHASE=merge
if [ $MERGED = 0 ]; then
  if [ -z "$M" ]; then
    cat > "$TMP/merge_msg" <<MSG
Merge claude/pensive-ptolemy-spwc0b at 53fc5a1 into main: the kta/km engine switch, players only (Dustin, Sept 30: "pin if all pass")

engine/ is B's (km's build 1f6319e, tree 9c84fef), byte-identical to the built and replayed candidate ${C:0:7}
(kept on the laptop at $CAND_REF; main had moved since it was made). Against main ${H:0:7}, the first parent, only
engine/src/players/ (three files) and rl/results/ change ($NRES_A files added, $NRES_M existing records changed); the
rules code is main's, and the pending rules items stay out. Made off-tree by rl/results/engine_switch_2026-09-30/pin.sh
(git merge-tree, git commit-tree).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
    M=$(git "${GIT_ID[@]}" commit-tree "$T" -p "$H" -p "$B_HEAD" -F "$TMP/merge_msg") || stop "git commit-tree failed; nothing merged"
  fi
  [ "$(git rev-parse HEAD)" = "$H" ] || stop "main moved during the pin's checks (now $(git rev-parse --short HEAD)); nothing merged: run the pin again"
  git_retry merge --ff-only -q "$M" || stop "git merge --ff-only ${M:0:7} failed ($(git_err)); nothing merged"
  [ "$(git rev-parse HEAD)" = "$M" ] || stop "HEAD is not ${M:0:7} after the fast-forward"
  note "MERGED 53fc5a1 into main as $M ($HOW); engine/ = $TEWORD, byte-identical to the built candidate ${C:0:7}'s; engine/ vs 9b4df9b: $PLAYERS; under rl/results/ $NRES_A files added and $NRES_M existing records changed (${RES_M_LINE:-none}); nothing deleted"
else
  [ "$(git rev-parse HEAD)" = "$H" ] || stop "main moved during the pin's checks (now $(git rev-parse --short HEAD)): run the pin again"
fi
PIN_PARENT=$(git rev-parse HEAD)

# --- steps 9-11, built in a scratch folder first: nothing in the working copy changes until every file is made -------
PHASE=build
F="$TMP/final"; mkdir -p "$F/rl/engine-2026-09-30" "$F/decks/screen"
for n in "${PROGS[@]}"; do
  src="$E/examples/$n"; [ $n != deckgym ] || src="$E/deckgym"
  cp -- "$src" "$F/rl/engine-2026-09-30/$n" || stop "copying $n"
  chmod 755 "$F/rl/engine-2026-09-30/$n"
done
( cd "$F/rl/engine-2026-09-30" && sha256sum "${PROGS[@]}" > SHA256SUMS ) || stop "sha256sum of the programs"
while read -r h n; do [ "$h" = "${WANT[$n]}" ] || stop "the copy of $n is not the tested build"; done < "$F/rl/engine-2026-09-30/SHA256SUMS"
( cd "$R/rl/engine-2026-09-28" && sha256sum -c --quiet SHA256SUMS ) || stop "the Sept 28 programs changed"
git show "HEAD:project_manifest.json" > "$TMP/manifest_base.json" || stop "git show HEAD:project_manifest.json"
python3 "$O/update_manifest.py" "$M" "$C" "$F/rl/engine-2026-09-30/SHA256SUMS" "$TMP/manifest_base.json" "$F/project_manifest.json" \
  || stop "update_manifest.py"
staged_ok || stop "a staged file changed during the pin (staged/STAGED.sha256)"
cp -- "$S/decks/screen/floor.py" "$S/decks/screen/run_screen.py" "$S/decks/screen/test_floor_pricing_pilot.py" "$F/decks/screen/" \
  || stop "copying the staged files"
build_docs "${M:0:7}" "$F"
mkdir -p "$TMP/t2/rl"; cp -- "$R/current_engine.py" "$F/project_manifest.json" "$TMP/t2/"
ln -s "$F/rl/engine-2026-09-30" "$TMP/t2/rl/engine-2026-09-30"
got=$(python3 "$TMP/t2/current_engine.py") || stop "current_engine.py refuses the new manifest (tried in a scratch folder; nothing installed)"
[ "$got" = "$(realpath "$F/rl/engine-2026-09-30/deckgym")" ] || stop "current_engine.py resolves $got from the new manifest (scratch folder)"
mapfile -t FILES < <(cd "$F" && find . -type f | sed 's|^\./||' | LC_ALL=C sort)
[ ${#FILES[@]} -eq 13 ] || stop "the pin would install ${#FILES[@]} files, not 13: ${FILES[*]}"
# just before the install: main where the pin left it, and every file the pin writes still main's (or absent, or already
# exactly the pin's) and not staged by anyone
[ "$(git rev-parse HEAD)" = "$PIN_PARENT" ] || stop "main moved during the pin (now $(git rev-parse --short HEAD)); nothing installed"
( cd "$R" && sha256sum -c --quiet "$S/BASE.sha256" ) || stop "floor.py or run_screen.py changed during the pin; nothing installed"
git diff --cached --quiet -- "${FILES[@]}" || stop "a file the pin writes is staged in the shared index (another session?); nothing installed"
for f in "${FILES[@]}"; do
  if git cat-file -e "$PIN_PARENT:$f" 2> /dev/null; then
    [ "$(git hash-object -- "$f" 2> /dev/null || true)" = "$(git rev-parse "$PIN_PARENT:$f")" ] \
      || stop "$f in the working copy is not main's (an uncommitted edit?); nothing installed"
  elif [ -e "$f" ]; then
    cmp -s -- "$f" "$F/$f" || stop "$f is here already and is not what the pin writes (move it aside); nothing installed"
  fi
done

# --- the install, in one go, and the checks in the working copy ---------------------------------------------------------
PHASE=install
for f in "${FILES[@]}"; do
  INSTALLED+=("$f")
  mkdir -p -- "$(dirname -- "$f")" && cp -- "$F/$f" "$f" || stop "installing $f failed"
done
got=$(python3 "$R/current_engine.py") || stop "current_engine.py refuses the new release"
[ "$got" = "$P/deckgym" ] || stop "current_engine.py resolves $got, not rl/engine-2026-09-30/deckgym"
python3 decks/screen/test_floor_pricing_pilot.py > "$TMP/test2.log" 2>&1 || { cat "$TMP/test2.log"; stop "test_floor_pricing_pilot.py fails in the working copy"; }
python3 decks/screen/floor.py --self-check > /dev/null || stop "floor.py --self-check fails"
[ "$(wp "$R/decks/screen")" = km3 ] || stop "the calibration doesn't read km3 from the screen and the floor"
for f in "${FILES[@]}"; do cmp -s -- "$f" "$F/$f" || stop "$f changed right after the install (another session?)"; done
note "PINNED in rl/engine-2026-09-30: $(tr '\n' ' ' < "$P/SHA256SUMS")"
note "MANIFEST available_release = main-${M:0:7} (rl/engine-2026-09-30/deckgym); main-9b4df9b in the history, superseded; current_engine.py resolves it"
note "SCREEN AND FLOOR default km3 (run_screen.py, floor.py); PRICING_PILOT matches every public-pricing code B builds, not k3; test_floor_pricing_pilot.py and floor.py --self-check pass; the calibration reads km3"
note "DOCS: START_HERE, CLAUDE.md, RUN5, rl/engine-2026-09-30/README.md and this folder's README.md (docs.patch)"
note "PIN DONE ${M:0:7}: every step passed; this file goes into the pin commit (should that commit fail, a PIN STOPPED line follows and the install is undone)"

# --- the pin commit: from a private index, so exactly the pin's files go in (the programs executable), and main moves
# --- to it only if main is still where the pin left it (git update-ref with the old value)
XI="$TMP/index"
GIT_INDEX_FILE="$XI" git read-tree "$PIN_PARENT" || stop "git read-tree (private index)"
GIT_INDEX_FILE="$XI" git add -- "${FOLDERS[@]}" || stop "git add of this folder and floor_recheck_2026-09-30 (private index)"
for f in "${FILES[@]}"; do
  mode=100644; case $f in rl/engine-2026-09-30/deckgym|rl/engine-2026-09-30/legality_scan|rl/engine-2026-09-30/goldfish) mode=100755;; esac
  blob=$(git hash-object -w -- "$F/$f") || stop "git hash-object $f"
  GIT_INDEX_FILE="$XI" git update-index --add --cacheinfo "$mode,$blob,$f" || stop "git update-index $f (private index)"
done
tree=$(GIT_INDEX_FILE="$XI" git write-tree) || stop "git write-tree (private index)"
git diff-tree -r --no-renames --name-status "$PIN_PARENT" "$tree" > "$TMP/pin.ns"
extra=$(cut -f2- "$TMP/pin.ns" | grep -vxF -f <(printf '%s\n' "${FILES[@]}") | grep -vE '^rl/results/(engine_switch|floor_recheck)_2026-09-30/' || true)
[ -z "$extra" ] || stop "the pin commit would also change: $(echo "$extra" | tr '\n' ' ')"
gone=$(awk -F'\t' '$1 != "A" && $1 != "M" {print $1 " " $2}' "$TMP/pin.ns")
[ -z "$gone" ] || stop "the pin commit would delete or retype: $(echo "$gone" | tr '\n' ';')"
missing=$(printf '%s\n' "${FILES[@]}" | grep -vxF -f <(cut -f2- "$TMP/pin.ns") || true)
[ -z "$missing" ] || stop "the pin commit would not change: $(echo "$missing" | tr '\n' ' ')"
cat > "$TMP/pin_msg" <<MSG
Pin the kta/km engine (main-${M:0:7}, built from ${C:0:7}) and move the screen and floor to km3 (Dustin, Sept 30: "pin if all pass", "km3")

A players-only switch: main-9b4df9b's rules unchanged; engine/src/players/ is B's (1f6319e; three files).
- identity (engine_switch_2026-09-30/identity_check.txt), every replay n of n: kta3 v ec7e1a8's fresh games
  14,000 + 8,500 and development games 14,000 + 8,500; km3 v B's 14,000 + 8,500; k3, kp3, kog3 14,000 each v the
  Sept 28 references
- deckgym simulate repeats Sept 28's k3, kp3 and kog3 lines on seed 7100; kta3 and km3 run; goldfish --coverage runs
- kt3, ktb3, ktc3: kog-based as B defines them; diagnostic, no identity claim

Also: the manifest (main-9b4df9b kept as history, superseded); the programs committed executable (mode 100755);
run_screen.py and floor.py default to km3 together; floor.py's pricing-pilot pattern matches every public-pricing code
B builds (kp kq kd kpr koa kob kor kpf kpg kog koh kph kpha kphb kt kta ktb ktc km), not k3, with
decks/screen/test_floor_pricing_pilot.py and a self-check assert; START_HERE, CLAUDE.md and RUN5 point at
rl/engine-2026-09-30/; the floor's pre-use re-check plan under km3 (floor_recheck_2026-09-30/), committed before any of
its games.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
X=$(git "${GIT_ID[@]}" commit-tree "$tree" -p "$PIN_PARENT" -F "$TMP/pin_msg") || stop "git commit-tree (the pin commit)"
[ "$(git symbolic-ref -q HEAD || true)" = refs/heads/main ] || stop "the working copy left main during the pin"
git_retry reset -q "$X" -- "${COMMIT_PATHS[@]}" || stop "putting the pin's files in the shared index failed ($(git_err))"
git_retry update-ref -m "pin.sh: pin the kta/km engine (main-${M:0:7})" refs/heads/main "$X" "$PIN_PARENT" \
  || stop "main moved during the pin, or its ref stayed locked ($(git_err)); nothing committed"
PHASE=done
[ "$(git rev-parse HEAD)" = "$X" ] || stop "HEAD is not the pin commit ${X:0:7} after git update-ref"
changed=$(git status --porcelain --untracked-files=no -- "${COMMIT_PATHS[@]}" || true)
echo "pin commit ${X:0:7} on merge ${M:0:7}. Not pushed."
[ -z "$changed" ] || echo "NOTE: in the working copy these pin paths differ from the pin commit (an edit by another session after the install?): $(echo "$changed" | tr '\n' ';')"
if git merge-base --is-ancestor origin/main HEAD 2> /dev/null; then
  echo "origin/main as last fetched ($(git rev-parse --short origin/main)) is behind main, so the push should go straight in."
else
  echo "NOTE: origin/main as last fetched has commits main lacks: a push is refused until they are merged. Ask before pulling."
fi
echo "Next, in GitHub Desktop: Fetch origin first; if it then offers Pull origin, ask the laptop session before pulling; else Push origin."
echo "After the push: tell Sonnet's calibration task, and the cloud through Dustin's paste block, that the official engine is main-${M:0:7} (rl/engine-2026-09-30/) and the working pilot is km3 on both sides of the screen and the floor: take main before any screen, floor or calibration run, and start a new --out rather than resuming a kog3 file."
echo "Then the floor's pre-use re-check (about 1 hour): bash rl/results/floor_recheck_2026-09-30/run_check.sh"
git --no-pager log -1 --stat --format='%h %s' > "$TMP/log" || true; head -40 "$TMP/log"

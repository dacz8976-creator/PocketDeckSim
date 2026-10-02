#!/usr/bin/env bash
# The rules engine switch's pin: PLAN.md steps 11, 12 and step 13's documents (Dustin, Sept 30: "Sure go for all 9", a
# conditional go, "pin if all pass"; Oct 1: "My conditional approval stands: pin the existing candidate once all
# remaining required trace checks pass"; ../README.md). No games, no build. Adapted from
# ../../engine_switch_2026-09-30/pin.sh (its structure, safety and undo).
# Runs only when sittings 1 and 2 passed for the candidate 5a18d31 (STATUS.txt: SITTING 1 DONE, SITTING 2 DONE and every
# STEP 4-10 DONE line, each step's files still as its step_<n>.sha256 records them; no HALT) and 8c passed (../8c_RESULT.txt,
# committed by the laptop after the coordinator's audit; its one line is in README.md here). A failed gate stops
# everything: main, the manifest and the documents stay untouched, and it goes to the coordinator first.
#   11 main moves to a merge commit of R (f8cfa9c, sonnet/rules-fixes) made off-tree on CURRENT main: git merge-tree
#      --write-tree (a conflict stops), git commit-tree with parents main and R. Checked before anything changes: main's
#      engine/ is unchanged since c9f4224 (the candidate's first parent; tree 9c84fef, main-d363ba8's); the merge's engine/
#      is R's tree 38af8b0, the built candidate's, byte for byte; against main, outside rl/results/ exactly the plan's 9
#      engine files change (sitting1.sh's ALLOWED), each modified; engine/src/players/ and every Cargo.lock unchanged;
#      nothing deleted or retyped anywhere. Then the working copy's files for exactly the merge's changed paths are
#      written from the merge (each must be main's beforehand, or absent if added), the shared index's entries for
#      exactly those paths are set to the merge's (as pin.sh line 487 does for its own paths), and main moves with git
#      update-ref, only from the value the pin read (never a checkout). pin.sh's step 8 did the same through git merge
#      --ff-only.
#   12 the three tested programs (their sha256 must be programs.sha256's) for rl/engine-2026-10-02/ with SHA256SUMS and
#      README.md; update_manifest_rules.py (main-d363ba8 to the history, superseded; the release main-<merge short>);
#      current_engine.py must resolve the new deckgym. The screen and the floor keep km3 (no file of theirs changes).
#   13 the reviewed documents in docs/ (README.md here), each installed only if its target still has its BASE.sha256
#      hash and the draft its DOCS.sha256 hash, with @@MERGE@@ and @@MERGE_SHORT@@ filled with the merge commit.
#   Then one pin commit of exactly: project_manifest.json, rl/engine-2026-10-02/, the installed documents, this switch's
#   folder (without docs/'s drafts, .sitting*, *.part, __pycache__; docs/'s BASE.sha256, DOCS.sha256 and CHANGES.md go
#   in) and ../../floor_recheck_2026-10/ (its plan, before any of its games). It is made from a private index (the programs executable, mode 100755), and main moves to it only
#   if main is still where the pin left it. The uncommitted files of those two folders it carries are listed by --check
#   and must be unchanged since the check gate, and PIN_STATUS.txt's SWEPT line names them. Other sessions' changes
#   elsewhere, staged or not, are left alone. Nothing is pushed. After the commit, docs/'s drafts are moved out of the
#   repository to ~/pin_rules_drafts_<merge short>/ (copies of START_HERE.md, CLAUDE.md and RUN5 with placeholders).
# Every check that can run before the working copy changes runs first, steps 12-13 built in a scratch folder included.
# --check runs them all and changes nothing (no ref, file or index entry; git merge-tree writes only objects).
# PIN_CHECK_WITHOUT_8C=1 with --check skips the 8c gate, for a dry run before 8c_RESULT.txt is in. A stop writes
# "PIN STOPPED: <why>" to PIN_STATUS.txt (pin mode only). Each file is re-checked just before it is overwritten. A stop
# during the merge's install undoes it (main had not moved). Once main is on the merge, the merge stays, a stop says so
# (don't push before the pin finishes), and a re-run recognises it (by its MERGING or MERGED line). A stop after the
# pin's install began undoes the install (each installed file still as the pin wrote it goes back as it was, or away if
# new; the pin's paths are unstaged if the pin had set them). If main moved meanwhile, the undo goes ahead only when the
# new commit didn't touch the pin's paths; otherwise it says to check main first. After a hard kill mid-install (no trap
# ran), restore the paths git status shows to main's first (the merge's install too: main had not moved), then re-run.
# The busy check sees WSL processes only: no commits (GitHub Desktop included) or runs elsewhere while the pin runs. The
# pin is done when its commit is on main.
# Usage (WSL): bash pin_rules.sh [--check]     Optional: PIN_BUILD_DIR=<dir with engine/target/release, or that dir>;
#   PIN_AFTER_HALT='<Dustin's words>' if a SITTING HALT is on record.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
main() {  # the whole script, read in full before it runs (called on the last line; the body is left unindented)
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SELF="$HERE/$(basename -- "${BASH_SOURCE[0]}")"
R=$(cd "$HERE/../../../.." && pwd)
REL=rl/results/engine_switch_rules_2026-10; O="$R/$REL"
[ "$HERE" -ef "$O/pin" ] && [ -f "$R/project_manifest.json" ] \
  || { echo "pin_rules.sh: run the copy in <repository>/$REL/pin (this one is in $HERE)" >&2; exit 2; }
DREL=$REL/pin/docs; D="$R/$DREL"
PREL=rl/engine-2026-10-02; P="$R/$PREL"
FRREL=rl/results/floor_recheck_2026-10; FR="$R/$FRREL"
STATUS="$O/PIN_STATUS.txt"; SLOG="$O/STATUS.txt"; MANIFEST_PY="$HERE/update_manifest_rules.py"
C=5a18d31657897545a9eaaf849c9d0cb5b0a08ffa        # the built and replayed candidate (main c9f4224 + R)
RC=f8cfa9c1df4bbcfb72a3b9d9b0247b081a1ffd26       # R, the head of sonnet/rules-fixes
MAIN_C=c9f422433362041a582004ecd1be4f099e6c73e2   # the candidate's first parent
RTREE=38af8b0cc4f35fdccc647ed540a56ec8f5e6c1d5    # R's engine/ (and the candidate's): the byte check
MAIN_ENGINE=9c84fefd44a4719678415b0e12a717b8ead373a9  # main-d363ba8's engine/, main's until the merge
CREF=refs/pocketdecksim/rules-switch-candidate    # sitting1.sh's (not a branch)
ALLOWED=(engine/src/actions/apply_action.rs engine/src/actions/apply_attack_action.rs engine/src/actions/attack_outcome.rs
         engine/src/hooks/core.rs engine/src/card_validation.rs engine/tests/b4a_attack_batch2_test.rs
         engine/tests/victini_victory_star_test.rs engine/tests/pokemon/hisuian_goodra_securely_sheltered_test.rs
         engine/tests/pokemon/meowth_carefree_steps_test.rs)    # sitting1.sh's: PLAN.md's 9 files
PROGS=(deckgym legality_scan goldfish)
declare -A WANT=([deckgym]=2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
                 [legality_scan]=978912748c83fd6c8ee8e3e966c9a6b95c9fdf1eb9d500c7367b2c1463e71699
                 [goldfish]=cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66)   # step 5's (programs.sha256)
STEPS=(4 5 6 7 7b 7c 8-seeds 8b 8 9 10)
COND3=297                                          # Dustin, Oct 1: "including all 297 flagged cases"
REQUIRED_DOCS=(START_HERE.md CLAUDE.md rl/RUN5.md "$REL/README.md")   # PLAN.md step 13
NOTED_DOCS=(rules/09_engine_repairs_2026-09-22.md rules/04_actions_cards_effects.md "$REL/PLAN.md")  # step 13 names them too
FR_FILES='PLAN\.md|[A-Za-z0-9_.-]+\.(sh|py)'      # what floor_recheck_2026-10/ may hold before its plan's commit
PIN_SUBJECT='^Pin the rules engine (main-'         # the pin commit's subject (git log --grep): done when it is on main
GIT_ID=(-c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com)
FOLDERS=("$REL" "$FRREL" ":(exclude)$REL/.sitting*" ":(exclude)$REL/*.part" ":(exclude)$REL/*__pycache__*"
         ":(exclude)$FRREL/*.part" ":(exclude)$FRREL/*__pycache__*")   # docs/'s drafts are excluded once listed
MODE=pin
case "${1:-}" in "") ;; --check) MODE=check;; *) echo "usage: bash pin_rules.sh [--check]" >&2; exit 2;; esac
[ $# -le 1 ] || { echo "usage: bash pin_rules.sh [--check]" >&2; exit 2; }
SKIP8C=0
if [ -n "${PIN_CHECK_WITHOUT_8C:-}" ]; then
  [ $MODE = check ] || { echo "PIN_CHECK_WITHOUT_8C is for --check only: unset it for the pin" >&2; exit 2; }
  if [ "$PIN_CHECK_WITHOUT_8C" = 1 ]; then SKIP8C=1; fi
fi
now() { date -u +%FT%TZ; }
note() { if [ $MODE = pin ]; then echo "$(now) $*" >> "$STATUS"; fi; echo "$*"; }
sha() { sha256sum < "$1" | cut -c1-64; }
PHASE=gates; STOPPED=0; UNDO=""; M=""; H=""; X=""; PIN_PARENT=""; F=""; FR_MADE=""; MERGED=0; MIDX=0; PIDX=0
INSTALLED=(); MW=(); MDIRS=(); MPATHS=(); MSTAT=(); FILES=(); DOCS_T=(); COMMIT_PATHS=()
declare -gA PRE=()   # each file the pin writes: its sha256 at the pre-install check, or "absent"
ON_MERGE="(not pushed: don't push before the pin finishes; re-run it once the stop is cleared)"
phase_undo() {  # what a stop leaves: an install is undone; once main is on the merge, the stop line says so
  case $PHASE in
    merge_install) undo_merge;;
    install) undo_install;;
    merged|build) UNDO="; main is on the merge ${M:0:7}, which stays $ON_MERGE";;
    gates|merge) if [ "$MERGED" = 1 ]; then UNDO="; main is on the merge ${M:0:7} from an earlier run, which stays $ON_MERGE"; fi;;
  esac
}
stop() {  # the stop line (pin mode); a stop inside an install undoes it first
  STOPPED=1
  phase_undo
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
undo_merge() {  # main not on the merge: each file the merge's install wrote, still as written, goes back as it was (or away
                # if new), and, if the pin had set them, the shared index's entries for the merge's paths go back to HEAD's.
                # Others are left, named. If main moved meanwhile (another session's commit), the same is done when that
                # commit didn't touch the merge's paths; if it did, the files are left and a person checks main first.
  set +e
  local f n=0 left="" i head moved=""
  PHASE=merge_undone
  head=$(git rev-parse HEAD)
  if [ -n "$M" ] && [ "$head" = "$M" ]; then
    UNDO="; main is on the merge ${M:0:7}, which stays $ON_MERGE"; return 0
  fi
  if [ "$head" != "$H" ]; then
    if ! git diff --quiet "$H" "$head" -- "${MPATHS[@]}"; then
      if [ $MIDX = 1 ]; then git_retry reset -q -- "${MPATHS[@]}"; fi
      UNDO="; main moved during the merge's install to ${head:0:7}, and that commit carries some of the merge's paths: check main first (the written files are left for a person: ${MW[*]})"
      return 0
    fi
    moved="; main moved meanwhile to ${head:0:7} (another session's commit; it doesn't touch the merge's paths)"
  fi
  if [ $MIDX = 1 ]; then git_retry reset -q -- "${MPATHS[@]}" || left+="(unstaging failed: git reset -q -- the merge's paths) "; fi
  for f in "${MW[@]}"; do
    if [ -f "$f" ] && cmp -s -- "$f" "$TMP/mnew/$f"; then
      if [ -e "$TMP/mbak/$f" ]; then cp -p -- "$TMP/mbak/$f" "$f"; else rm -f -- "$f"; fi
      n=$((n + 1))
    elif [ -e "$f" ]; then left+="$f "; fi
  done
  for (( i = ${#MDIRS[@]} - 1; i >= 0; i-- )); do rmdir -- "${MDIRS[i]}" 2> /dev/null; done
  UNDO="; the merge's install was undone ($n of ${#MW[@]} files back as they were${left:+; left: $left})${moved:-; main is still ${H:0:7}}"
  return 0
}
undo_install() {  # each installed file still as the pin wrote it goes back as it was (or away, if new); the pin's paths
                  # are unstaged in the shared index if the pin had set them. A file that is not as the pin wrote it is
                  # left, and named. If main moved meanwhile, as undo_merge.
  set +e
  local f n=0 left="" head moved=""
  PHASE=undone
  head=$(git rev-parse HEAD)
  if [ -n "$X" ] && [ "$head" = "$X" ]; then UNDO="; the pin commit ${X:0:7} is on main, so nothing was undone"; return 0; fi
  if [ "$head" != "$PIN_PARENT" ]; then
    if [ ${#INSTALLED[@]} -gt 0 ] && ! git diff --quiet "$PIN_PARENT" "$head" -- "${INSTALLED[@]}"; then
      if [ $PIDX = 1 ]; then git_retry reset -q -- "${COMMIT_PATHS[@]}"; fi
      UNDO="; main moved during the pin to ${head:0:7}, and that commit carries some of the pin's files: check main first (the installed files are left for a person: ${INSTALLED[*]})${M:+; the merge ${M:0:7} stays}"
      return 0
    fi
    moved="; main moved meanwhile to ${head:0:7} (another session's commit; it doesn't touch the pin's files)"
  fi
  if [ $PIDX = 1 ]; then git_retry reset -q -- "${COMMIT_PATHS[@]}" || left+="(unstaging failed: git reset -q -- the pin's paths) "; fi
  for f in "${INSTALLED[@]}"; do
    if [ -f "$f" ] && cmp -s -- "$f" "$F/$f"; then
      if [ -e "$TMP/bak/$f" ]; then cp -p -- "$TMP/bak/$f" "$f"; else rm -f -- "$f"; fi
      n=$((n + 1))
    elif [ -e "$f" ]; then left+="$f "; fi
  done
  rmdir -- "$P" 2> /dev/null; if [ -n "$FR_MADE" ]; then rmdir -- "$FR" 2> /dev/null; fi
  UNDO="; the install was undone ($n of ${#INSTALLED[@]} files back as they were${left:+; left: $left})${moved}${M:+; the merge ${M:0:7} stays and a re-run recognises it $ON_MERGE}"
  return 0
}
on_exit() {
  local rc=$? ph=$PHASE
  set +e
  if [ $rc -ne 0 ] && [ $STOPPED = 0 ]; then
    phase_undo
    if [ $MODE = pin ]; then
      echo "$(now) PIN STOPPED: exit code $rc outside a check, in phase $ph (a script, system or signal stop; see the terminal)$UNDO" >> "$STATUS"
    fi
    echo "PIN STOPPED: exit code $rc outside a check, in phase $ph$UNDO" >&2
  fi
  rm -rf "$TMP"
}
TMP=$(mktemp -d); trap on_exit EXIT; trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
exec 9>/tmp/pocketdecksim_pin_rules_2026-10.lock; flock -n 9 || { echo "another pin_rules.sh is running"; STOPPED=1; exit 1; }
cd "$R"
SELF_SHA=$(sha "$SELF"); MPY_SHA=$(sha "$MANIFEST_PY")

# --- gate 1: not done yet; no sitting running ---------------------------------------------------------------------------
done_x=$(git log -1 --format=%h --grep="$PIN_SUBJECT" HEAD) || true
if [ -n "$done_x" ]; then echo "the pin is already done: its commit $done_x is on main (nothing to do)"; STOPPED=1; exit 0; fi
[ -f "$SLOG" ] && [ -f "$STATUS" ] || stop "no STATUS.txt or PIN_STATUS.txt in $REL"
if [ $MODE = pin ]; then
  note "PIN START: pin_rules.sh ${SELF_SHA:0:16}, update_manifest_rules.py ${MPY_SHA:0:16} (sha256; HEAD $(git rev-parse --short HEAD))"
fi
exec 8>> "$O/.sitting1.lock"; flock -n 8 || stop "sitting1.sh (or a child it left) holds .sitting1.lock"
exec 7>> "$O/.sitting2.lock"; flock -n 7 || stop "sitting2.sh (or a child it left) holds .sitting2.lock"

# --- gate 2: the record: both sittings done for the candidate, every step's line and files, no HALT --------------------
for n in 1 2; do
  grep -qE "^SITTING $n DONE $C( |$)" "$SLOG" || stop "STATUS.txt has no 'SITTING $n DONE $C' line"
  for f in "$SLOG" "$STATUS"; do
    last=$( { grep -E "^SITTING $n (HALT|STOPPED|PAUSED|DONE) " "$f" || true; } | tail -1)
    case $last in "SITTING $n DONE $C"*) ;; *) stop "sitting $n's last state in ${f##*/} is not DONE ${C:0:7}: '${last:0:100}'";; esac
  done
done
for s in "${STEPS[@]}"; do
  grep -qE "^STEP $s DONE ${C:0:7} " "$SLOG" || stop "STATUS.txt has no 'STEP $s DONE ${C:0:7}' line"
  ( cd "$O" && sha256sum -c --quiet "step_$s.sha256" ) > "$TMP/c.out" 2>&1 \
    || stop "step $s's files are not as step_$s.sha256 records them: $(head -n 3 "$TMP/c.out" | tr '\n' ' ')"
done
# the pin's own STOPPED and AFTER HALT lines are the pin's; a FAILED or MISMATCH anywhere else stops the pin
if awk '!/^[0-9-]+T[0-9:]+Z PIN (STOPPED:|AFTER HALT)/ && /FAILED|MISMATCH/ {bad = 1} END {exit !bad}' "$STATUS"; then
  stop "a FAILED or MISMATCH line in PIN_STATUS.txt (a mismatch stops everything and goes to Dustin)"
fi
if grep -qE '^SITTING [12] HALT ' "$SLOG" "$STATUS"; then   # a check failed once: "pin if all pass" needs his word again
  [ -n "${PIN_AFTER_HALT:-}" ] || stop "a SITTING HALT is on record; 'pin if all pass' no longer covers it. With Dustin's word, run with PIN_AFTER_HALT='<his words>'"
  if [ $MODE = pin ]; then note "PIN AFTER HALT (Dustin): $PIN_AFTER_HALT"; fi
fi
prep=$( { grep -E '^PREPARE (DONE|HALT|STOPPED) ' "$STATUS" || true; } | grep -vE "^PREPARE DONE $C( |$)" || true)
[ -z "$prep" ] || stop "PIN_STATUS.txt has a PREPARE line that is not 'PREPARE DONE ${C:0:7}': ${prep:0:100}"
cand() { sed -n "s/^$1 //p" "$O/candidate.txt" | head -n 1; }
[ "$(cand candidate)" = "$C" ] && [ "$(cand r)" = "$RC" ] && [ "$(cand main)" = "$MAIN_C" ] && [ "$(cand engine_tree)" = "$RTREE" ] \
  || stop "candidate.txt doesn't name candidate ${C:0:7}, main ${MAIN_C:0:7}, R ${RC:0:7} and engine tree ${RTREE:0:7}"
git cat-file -e "$C^{commit}" 2> /dev/null || stop "the candidate ${C:0:7} is not here"
git cat-file -e "$RC^{commit}" 2> /dev/null || stop "R ${RC:0:7} is not here (Fetch origin)"
[ "$(git rev-parse "$C^1")" = "$MAIN_C" ] && [ "$(git rev-parse "$C^2")" = "$RC" ] || stop "the candidate's parents are not c9f4224 and R"
[ "$(git rev-parse "$C:engine")" = "$RTREE" ] && [ "$(git rev-parse "$RC:engine")" = "$RTREE" ] \
  || stop "the candidate's or R's engine/ is not tree ${RTREE:0:7}"
if git rev-parse -q --verify "$CREF" > /dev/null; then
  [ "$(git rev-parse "$CREF")" = "$C" ] || stop "$CREF is not the candidate ${C:0:7}"
fi

# --- gate 3: 8c (committed by the laptop after the coordinator's audit) --------------------------------------------------
git cat-file -e "HEAD:$REL/handoff_8c.tsv" 2> /dev/null || stop "handoff_8c.tsv is not committed"
git diff --quiet HEAD -- "$REL/handoff_8c.tsv" || stop "handoff_8c.tsv differs from its commit"
git show "HEAD:$REL/handoff_8c.tsv" > "$TMP/handoff.tsv"
read -r HN HC3 < <(awk -F'\t' 'NR == 1 {for (i = 1; i <= NF; i++) if ($i == "full_prevention_only") c = i; next}
  NF > 1 {n++; if (c && $c == "yes") y++} END {print n + 0, (c ? y + 0 : -1)}' "$TMP/handoff.tsv")
SC=$( { grep -E "^STEP (8b|8) DONE ${C:0:7} " "$SLOG" || true; } | { grep -oE 'changed [0-9]+ of [0-9]+ deals' || true; } | awk '{s += $2} END {print s + 0}')
[ "$HN" = "$SC" ] && [ "$HN" -gt 0 ] || stop "handoff_8c.tsv has $HN changed games, the STEP 8b and 8 lines $SC"
[ "$HC3" = "$COND3" ] || stop "handoff_8c.tsv has $HC3 CONDITION 3 games, not the $COND3 of Dustin's word"
# The coordinator's wording (Oct 2): the rule's verdicts stand as produced; the games Dustin accepted are listed as his
# documented exceptions (8c_DECISION.md, committed), and nothing is left unaccounted.
WANT8C="8C PASS <Sonnet's result commit, 40 hex> rule verdicts: unexplained <u>, judgment <j>; all <u+j> accepted by Dustin <dates> as documented exceptions explained by A/B (8c_DECISION.md; <evidence>); net unaccounted 0; changed $HN accounted $HN; condition3 $COND3 traced $COND3; 8b_rows_vs_cloud equal"
if [ $SKIP8C = 1 ]; then
  echo "CHECK: the 8c gate skipped (PIN_CHECK_WITHOUT_8C=1); 8c_RESULT.txt must be committed with the one line: $WANT8C"
  C8N=$HN; C8S=$(printf '%040d' 0); C8LINE="(not checked)"
else
  C8=$REL/8c_RESULT.txt
  git cat-file -e "HEAD:$C8" 2> /dev/null || stop "no 8c_RESULT.txt committed on main: 8c has not passed (or the laptop has not recorded it). It must hold: $WANT8C"
  git diff --quiet HEAD -- "$C8" || stop "8c_RESULT.txt differs from its commit"
  git show "HEAD:$C8" | tr -d '\r' > "$TMP/8c.txt"
  k=$(grep -cE '^8C( |$)' "$TMP/8c.txt" || true)
  [ "$k" = 1 ] || stop "8c_RESULT.txt has $k lines starting with 8C, not 1"
  C8LINE=$(grep -E '^8C( |$)' "$TMP/8c.txt")
  re='^8C PASS ([0-9a-f]{40}) rule verdicts: unexplained ([0-9]+), judgment ([0-9]+); all ([0-9]+) accepted by Dustin [^;()]+ as documented exceptions explained by A/B \(8c_DECISION\.md; [^()]+\); net unaccounted 0; changed ([0-9]+) accounted ([0-9]+); condition3 ([0-9]+) traced ([0-9]+); 8b_rows_vs_cloud equal$'
  [[ $C8LINE =~ $re ]] || stop "8c_RESULT.txt's line is not '$WANT8C': '$C8LINE'"
  C8S=${BASH_REMATCH[1]}; U8=${BASH_REMATCH[2]}; J8=${BASH_REMATCH[3]}; A8=${BASH_REMATCH[4]}
  C8N=${BASH_REMATCH[5]}; ACC8=${BASH_REMATCH[6]}; C3A=${BASH_REMATCH[7]}; C3T=${BASH_REMATCH[8]}
  [ "$A8" = "$((U8 + J8))" ] || stop "8c_RESULT.txt: $A8 accepted, but the rule's verdicts are unexplained $U8 + judgment $J8"
  git cat-file -e "HEAD:$REL/8c_DECISION.md" 2> /dev/null || stop "8c_RESULT.txt cites 8c_DECISION.md, which is not committed"
  git diff --quiet HEAD -- "$REL/8c_DECISION.md" || stop "8c_DECISION.md differs from its commit"
  [ "$C8N" = "$HN" ] && [ "$ACC8" = "$HN" ] \
    || stop "8c_RESULT.txt: changed $C8N, accounted $ACC8; handoff_8c.tsv has $HN changed games"
  [ "$C3A" = "$COND3" ] && [ "$C3T" = "$COND3" ] \
    || stop "8c_RESULT.txt: condition3 $C3A, traced $C3T; both must be $COND3"
  git cat-file -e "$C8S^{commit}" 2> /dev/null || stop "8c_RESULT.txt names Sonnet's result ${C8S:0:7}, which is not here (Fetch origin)"
  echo "8c: $C8LINE"
fi

# --- gate 4: the tested programs (programs.sha256 and watch.sha256 still verify; the copies come from that build) ------
sha256sum -c --quiet "$O/programs.sha256" > "$TMP/c.out" 2>&1 || stop "programs.sha256 no longer verifies: $(head -n 3 "$TMP/c.out" | tr '\n' ' ')"
sha256sum -c --quiet "$O/watch.sha256" > "$TMP/c.out" 2>&1 || stop "watch.sha256 no longer verifies: $(head -n 3 "$TMP/c.out" | tr '\n' ' ')"
declare -A WHERE
for n in "${PROGS[@]}"; do
  w=deckgym; [ $n = deckgym ] || w=examples/$n
  lines=$(awk -v w="/engine/target/release/$w" 'length($0) > 66 {p = substr($0, 67)
    if (length(p) >= length(w) && substr(p, length(p) - length(w) + 1) == w) print substr($0, 1, 64) "\t" p}' "$O/programs.sha256")
  [ -n "$lines" ] && [ "$(printf '%s\n' "$lines" | wc -l)" = 1 ] || stop "programs.sha256 doesn't name one build of $n"
  [ "${lines%%$'\t'*}" = "${WANT[$n]}" ] || stop "programs.sha256's $n is not ${WANT[$n]:0:8}, step 5's"
  WHERE[$n]=${lines#*$'\t'}
  grep -qE "^[0-9TZ:-]+ sha256 ${WANT[$n]} $n \(new, plain\)$" "$STATUS" || stop "PIN_STATUS.txt has no 'sha256 ${WANT[$n]:0:8}... $n (new, plain)' line"
done
E=$(dirname -- "${WHERE[deckgym]}")
[ "${WHERE[legality_scan]}" = "$E/examples/legality_scan" ] && [ "${WHERE[goldfish]}" = "$E/examples/goldfish" ] \
  || stop "programs.sha256 names the three programs in different builds"
if [ -n "${PIN_BUILD_DIR:-}" ]; then E="$PIN_BUILD_DIR/engine/target/release"; [ -f "$E/deckgym" ] || E="$PIN_BUILD_DIR"; fi
src_of() { if [ "$1" = deckgym ]; then echo "$E/deckgym"; else echo "$E/examples/$1"; fi; }
for n in "${PROGS[@]}"; do
  [ -f "$(src_of $n)" ] && [ "$(sha "$(src_of $n)")" = "${WANT[$n]}" ] || stop "$(src_of $n) is not the tested $n (sitting 1's build)"
done
echo "programs: $E (deckgym ${WANT[deckgym]:0:8}, legality_scan ${WANT[legality_scan]:0:8}, goldfish ${WANT[goldfish]:0:8}: programs.sha256's, never rebuilt); watch.sha256 verifies"

# --- gate 5: sizes. GitHub refuses a file of 100 MB; everything the pin commit would carry is here already -------------
big=$( { git ls-files -o -m --exclude-standard -- "${FOLDERS[@]}"; for n in "${PROGS[@]}"; do src_of $n; done; } \
       | while IFS= read -r f; do if [ -f "$f" ] && [ "$(stat -c %s -- "$f")" -gt 95000000 ]; then echo "$f"; fi; done || true)
[ -z "$big" ] || stop "files over 95 MB would go into the pin commit (GitHub refuses 100 MB): $(echo "$big" | tr '\n' ' ')"

# --- gate 6: the working copy ----------------------------------------------------------------------------------------------
[ "$(git symbolic-ref -q --short HEAD || true)" = main ] || stop "the working copy is not on main"
H=$(git rev-parse HEAD)
dirty=$(git status --porcelain --untracked-files=all -- project_manifest.json "$PREL" | grep -v "^?? $PREL/" || true)
[ -z "$dirty" ] || stop "uncommitted changes in the pin's own paths (commit or restore them first): $(echo "$dirty" | tr '\n' ';')"
if [ -e "$P" ]; then   # a recorded copy of the tested build (a re-run after a hard kill) is fine; anything else is not
  [ -f "$P/SHA256SUMS" ] || stop "$PREL exists and isn't a recorded copy of the tested build (move it aside)"
  while read -r h n; do [ "$h" = "${WANT[$n]:-x}" ] || stop "$PREL/$n isn't the tested build"; done < "$P/SHA256SUMS"
  ( cd "$P" && sha256sum -c --quiet SHA256SUMS ) > /dev/null 2>&1 || stop "$PREL doesn't match its SHA256SUMS"
fi
( cd "$R/rl/engine-2026-09-30" && sha256sum -c --quiet SHA256SUMS ) > /dev/null 2>&1 || stop "the Sept 30 programs (rl/engine-2026-09-30/) changed"
wp() { python3 -c "import sys; sys.path.insert(0, sys.argv[1]); import calibrate; print(calibrate.working_pilot(sys.argv[2])[0])" \
         "$R/decks/screen/panel_ladder_2026-09-26" "$R/decks/screen" 2>&1; }
pilot=$(wp) || stop "calibrate.working_pilot fails on the screen and the floor: $pilot"
[ "$pilot" = km3 ] || stop "the screen and the floor default to $pilot, not km3 (this switch changes no default)"
# runs in this working copy that the pin would change under them: the screen, floor and calibration scripts (they read
# the manifest), a sitting or the floor re-check, and cargo or a program in engine/ (the merge rewrites engine/src/).
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
    *run_screen.py*|*floor.py*|*run_calibration.py*|*candidate_run.py*|*trace_pilot.py*|*run_check.sh*|*sitting1.sh*|*sitting2.sh*)
      if [ $here = 1 ]; then busy+="$pid: $args; "; fi;;
  esac
  case "${argv[0]##*/}" in
    cargo|rustc|deckgym|legality_scan|goldfish|tool_census)
      case "$cwd/" in "$R"/engine/*) busy+="$pid: $args (in engine/); ";; esac;;
  esac
done
[ -z "$busy" ] || stop "a screen, floor, calibration, sitting or engine run in this working copy is going; the pin would change its files mid-run: $busy"

# --- gate 7: step 11's merge, computed off-tree and checked before anything changes --------------------------------------
MERGED=0
if git merge-base --is-ancestor "$RC" "$H"; then          # a re-run after step 11
  # the merge this script recorded: its MERGED line, or its MERGING line (written just before main moved, so a kill
  # between main's move and the MERGED line is recognised too); the latest one that main contains
  for m in $( { grep -oE "(MERGED|MERGING) ${RC:0:7} into main as [0-9a-f]{40}" "$STATUS" 2> /dev/null || true; } | cut -d' ' -f6 | tac); do
    if git merge-base --is-ancestor "$m" "$H" 2> /dev/null; then M=$m; break; fi
  done
  [ -n "$M" ] || stop "main already contains R ${RC:0:7}, but not through a merge this script recorded"
  [ "$(git rev-parse "$M^2")" = "$RC" ] || stop "the recorded merge ${M:0:7}'s second parent is not R"
  [ "$(git rev-parse "$H:engine")" = "$RTREE" ] || stop "main contains R, but its engine/ changed since the recorded merge ${M:0:7}"
  T=$(git rev-parse "$M^{tree}"); BASE=$(git rev-parse "$M^1"); MERGED=1; HOW="already merged as ${M:0:7} (a re-run)"
else
  [ "$(git rev-parse "$H:engine")" = "$MAIN_ENGINE" ] || stop "main's engine/ is not tree ${MAIN_ENGINE:0:7} (main-d363ba8's, the candidate's base)"
  git merge-base --is-ancestor "$MAIN_C" "$H" || stop "main does not contain c9f4224, the candidate's first parent"
  git diff --quiet "$MAIN_C" "$H" -- engine/ || stop "engine/ changed on main since c9f4224: $(git diff --name-only "$MAIN_C" "$H" -- engine/ | tr '\n' ' ')"
  out=$(git merge-tree --write-tree "$H" "$RC") || stop "merging R into main ${H:0:7} has conflicts: $(echo "$out" | tail -n +2 | tr '\n' ' ')"
  T=$(echo "$out" | head -n 1); BASE=$H; HOW="a fresh merge commit of R into main ${H:0:7}, made off-tree"
fi
TE=$(git rev-parse "$T:engine")
[ "$TE" = "$RTREE" ] || stop "the merge's engine/ is not R's tree ${RTREE:0:7} (the built candidate's); it differs in: $(git diff-tree -r --name-only "$RTREE" "$TE" | tr '\n' ' ')"
got=$(git diff --no-renames --name-only "$BASE" "$T" -- . ':(exclude)rl/results/' | LC_ALL=C sort)
want=$(printf '%s\n' "${ALLOWED[@]}" | LC_ALL=C sort)
[ "$got" = "$want" ] || stop "outside rl/results/ the merge changes: $(echo $got) (expected exactly the plan's 9 engine files)"
nm=$(git diff --no-renames --name-status "$BASE" "$T" -- . ':(exclude)rl/results/' | awk -F'\t' '$1 != "M" {print $1 " " $2}')
[ -z "$nm" ] || stop "outside rl/results/ the merge doesn't only modify: $(echo "$nm" | tr '\n' ';')"
git diff --quiet "$BASE" "$T" -- engine/src/players/ || stop "the merge changes engine/src/players/"
lock=$(git diff --name-only "$BASE" "$T" | grep -E '(^|/)Cargo\.lock$' || true)
[ -z "$lock" ] || stop "the merge changes $(echo $lock)"
git diff --no-renames --name-status "$BASE" "$T" > "$TMP/merge.ns"
git diff --no-renames --name-only "$BASE" "$T" > "$TMP/merge.paths"
gone=$(awk -F'\t' '$1 != "A" && $1 != "M" {print $1 " " $2}' "$TMP/merge.ns")
[ -z "$gone" ] || stop "the merge would delete or retype files on main: $(echo "$gone" | tr '\n' ';')"
NRES_A=$(awk -F'\t' '$1 == "A" && $2 ~ /^rl\/results\// {n++} END {print n + 0}' "$TMP/merge.ns")
RES_M=$(awk -F'\t' '$1 == "M" && $2 ~ /^rl\/results\// {print $2}' "$TMP/merge.ns")
NRES_M=$(printf '%s' "$RES_M" | grep -c . || true)
RES_M_LINE=$(printf '%s\n' "$RES_M" | paste -sd' ' -)
merge_clash() {  # the merge's paths in the working copy: each modified one still main's, each added one absent (or
                 # already the merge's), none staged
  local i f clash="" staged
  for i in "${!MPATHS[@]}"; do
    f=${MPATHS[i]}
    if [ "${MSTAT[i]}" = M ]; then
      [ -f "$f" ] && [ "$(git hash-object -- "$f")" = "$(git rev-parse "$H:$f")" ] || clash+="$f (not main's); "
    elif [ -e "$f" ] || [ -L "$f" ]; then
      [ -f "$f" ] && [ "$(git hash-object -- "$f")" = "$(git rev-parse "$T:$f")" ] || clash+="$f (here already, not the merge's); "
    fi
  done
  staged=$(git diff --cached --name-only -- "${MPATHS[@]}" | tr '\n' ' ')
  [ -z "$staged" ] || clash+="staged in the shared index: $staged"
  [ -z "$clash" ] || stop "the merge would overwrite local files: $clash"
}
if [ $MERGED = 0 ]; then
  while IFS= read -r -d '' st && IFS= read -r -d '' f; do MSTAT+=("$st"); MPATHS+=("$f"); done \
    < <(git diff -z --no-renames --name-status "$H" "$T")
  merge_clash
fi
echo "merge: $HOW; engine/ = R's tree ${RTREE:0:7} = the built candidate's; outside rl/results/ exactly the plan's 9 engine files, each modified; players/ and Cargo.lock unchanged; under rl/results/ $NRES_A files added, $NRES_M existing records changed (${RES_M_LINE:-none}); nothing deleted"

# --- gate 8: steps 12 and 13 built in a scratch folder, and the floor re-check's plan ------------------------------------
build_docs() {  # fill dir base: docs/'s drafts checked and filled into dir; the targets in $TMP/docs.tsv and docs.list
  [ -d "$D" ] || stop "no $DREL/: the reviewed documents (PLAN.md step 13) are not in yet"
  [ -s "$D/DOCS.sha256" ] && [ -s "$D/BASE.sha256" ] || stop "$DREL/ needs DOCS.sha256 and BASE.sha256 (README.md here)"
  local ok=1
  python3 - "$D" "$R" "$3" "$1" "$2" "$TMP/merge.paths" "$REL" "$FRREL" "${REQUIRED_DOCS[*]}" > "$TMP/docs.tsv" 2> "$TMP/docs.err" <<'EOF' || ok=0
import hashlib, os, re, subprocess, sys
D, R, base, full, out, mpaths, rel, frrel, required = sys.argv[1:10]
def die(msg):
    sys.exit("  " + msg)
def sums(name, rel_to):
    got = {}
    for n, line in enumerate(open(os.path.join(D, name), encoding="utf-8"), 1):
        line = line.rstrip("\r\n")
        if not line.strip():
            continue
        m = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
        if not m:
            die(f"{name} line {n} is not '<sha256>  <path>' ({rel_to}): {line!r}")
        p = m.group(2)[2:] if m.group(2).startswith("./") else m.group(2)
        if p in got:
            die(f"{name} names {p} twice")
        got[p] = m.group(1)
    return got
docs, bases = sums("DOCS.sha256", "relative to docs/"), sums("BASE.sha256", "relative to the repository")
if not docs:
    die("DOCS.sha256 lists no draft")
present = {os.path.relpath(os.path.join(dp, f), D).replace(os.sep, "/") for dp, _, fs in os.walk(D) for f in fs}
unlisted = sorted(present - set(docs) - {"DOCS.sha256", "BASE.sha256", "CHANGES.md"})   # CHANGES.md: the drafter's notes
if unlisted:
    die("docs/ holds files DOCS.sha256 doesn't list (move them out of docs/, or list them): " + " ".join(unlisted))
extra = sorted(set(bases) - set(docs))
if extra:
    die("BASE.sha256 names paths DOCS.sha256 doesn't: " + " ".join(extra))
merged = {l.rstrip("\n") for l in open(mpaths, encoding="utf-8") if l.strip()}
for p in sorted(docs):
    parts = p.split("/")
    if p.startswith("/") or any(x in ("", ".", "..") for x in parts):
        die(f"{p}: not a plain relative path")
    if not p.endswith(".md"):
        die(f"{p}: only .md documents are installed from docs/")
    if p.startswith(("engine/", ".git/", rel + "/pin/")) or (p.startswith("rl/engine-2026-10-02/") and p != "rl/engine-2026-10-02/README.md"):
        die(f"{p}: not a document the pin may install")
    if p in merged:
        die(f"{p}: step 11's merge changes this path, so no draft can be based on it")
missing = [p for p in required.split() if p not in docs]
if missing:
    die("docs/ has no draft for " + " ".join(missing) + " (PLAN.md step 13)")
ls = subprocess.run(["git", "-C", R, "ls-tree", "-z", base, "--"] + sorted(docs), capture_output=True, check=True).stdout
blob = {}
for rec in ls.split(b"\0"):
    if rec:
        meta, path = rec.split(b"\t", 1)
        blob[path.decode()] = meta.split()[2].decode()
sha = lambda b: hashlib.sha256(b).hexdigest()
gitsha = lambda b: hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()
own = (rel + "/", frrel + "/")   # the pin's own folders: committed with the pin as they are, so a BASE hash is enough
for p in sorted(docs):
    src = open(os.path.join(D, p), "rb").read()
    if sha(src) != docs[p]:
        die(f"docs/{p} is not as DOCS.sha256 records it (changed since it was reviewed)")
    tgt, want = os.path.join(R, p), bases.get(p, "0" * 64)
    if want == "0" * 64:
        if os.path.lexists(tgt) or p in blob:
            die(f"{p} exists, but BASE.sha256 drafts it as a new file")
        state = "new"
    else:
        if not os.path.isfile(tgt):
            die(f"{p} is not here, but BASE.sha256 has it")
        cur = open(tgt, "rb").read()
        if sha(cur) != want:
            die(f"{p} changed since it was drafted (BASE.sha256): re-draft it, re-review it and rewrite both lists")
        if not p.startswith(own) and blob.get(p) != gitsha(cur):
            die(f"{p} in the working copy is not main's (an uncommitted edit?)")
        state = "replaces"
    k = src.count(b"@@MERGE_SHORT@@") + src.count(b"@@MERGE@@")
    filled = src.replace(b"@@MERGE_SHORT@@", full[:7].encode()).replace(b"@@MERGE@@", full.encode())
    left = sorted({x.decode() for x in re.findall(rb"@@[A-Z0-9_]+@@", filled)})
    if left:
        die(f"docs/{p} has unknown placeholders: " + " ".join(left))
    if p in ("START_HERE.md", "CLAUDE.md") and b"rl/engine-2026-10-02" not in filled:
        die(f"{p}'s draft doesn't name rl/engine-2026-10-02 (the official engine line)")
    os.makedirs(os.path.dirname(os.path.join(out, p)), exist_ok=True)
    open(os.path.join(out, p), "wb").write(filled)
    print(f"{p}\t{state}\t{want}\t{k}\t{docs[p][:16]}\t{sha(filled)[:16]}")
EOF
  [ $ok = 1 ] || { cat "$TMP/docs.err" >&2; stop "the documents in $DREL/ (printed above; nothing changed)"; }
  cut -f1 "$TMP/docs.tsv" > "$TMP/docs.list"
}
docs_base_ok() {  # just before the install: each document's target still has its BASE hash (or is still absent)
  local p st want
  while IFS=$'\t' read -r p st want _; do
    if [ "$st" = new ]; then [ ! -e "$p" ] && [ ! -L "$p" ] || stop "$p appeared during the pin; nothing installed"; PRE[$p]=absent
    else [ -f "$p" ] && [ "$(sha "$p")" = "$want" ] || stop "$p changed during the pin; nothing installed"; PRE[$p]=$want; fi
  done < "$TMP/docs.tsv"
}
fmt() { echo "$1" | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta'; }
engine_readme() {  # merge-commit out: rl/engine-2026-10-02/README.md (used when docs/ has no draft of it)
  python3 - "$1" "$(fmt "$C8N")" "${C8S:0:7}" "$2" <<'EOF'
import sys
m, n, s, out = sys.argv[1:5]
t = """# The official engine from Oct 1: main-@M7@

- **Programs:** `deckgym`, `legality_scan`, `goldfish`; sha256 in `SHA256SUMS` and `project_manifest.json`. Linux (WSL or the cloud). Committed with the executable bit (git mode 100755), so a Linux clone runs them as they are.
- **Built** in WSL on Oct 1 (03:16 UTC) from one `git archive` of 5a18d31, the merge candidate: main c9f4224 plus `sonnet/rules-fixes` at R f8cfa9c, whose `engine/` is R's (tree 38af8b0). `cargo build --release --locked`, `--example legality_scan`, `--example goldfish`.
  - Main's merge commit @M7@ has an `engine/` byte-identical to it (checked by `../results/engine_switch_rules_2026-10/pin/pin_rules.sh`). Main had moved since the candidate (outside `engine/`), so the pin made main's merge commit itself. 5a18d31 is kept only on the laptop (`refs/pocketdecksim/rules-switch-candidate`; not a branch, not pushed); elsewhere, build from main's merge commit, the same `engine/`.
- **What it is:** a rules switch on main-d363ba8's engine; the players are unchanged.
  - Repair A, Victory Star with a Confused attacker: the Confusion coin comes first; on heads, Victory Star is offered on the attack's own coins.
  - Repair B, coin-flip damage prevention and Chase Order: Guarded Grill and Securely Sheltered come off after Weakness, and queued attack damage flips the coin.
  - kd's follow-ons and the fixes F1-F7.
  - Nine engine files change: five rules files and four test files; `engine/src/players/` and `Cargo.lock` don't. The repairs, kd's follow-ons included, act only with a coin-Ability Pokémon (Meowth B2 124/204, Togekiss A4 080, Bastiodon A2 114, Hisuian Goodra B3b 050) or Victini (B3 025, P-B 049) in play, and every replay without one was identical (steps 7-10).
  - km3 stays the working pilot, on both sides of the screen and the floor.
  - Still open (rules/09): Victory Star with CoinFlipToBlockAttack, and with Confusion plus a pending Will, stays gated; Wild Swing, the own-Bench form of `also_choice_bench_damage`, six other sites and a copied Chase Order's discard branch still skip the coin.
- **Approved:** Dustin, Sept 30: "Sure go for all 9" (a conditional go, "pin if all pass"). Oct 1: Victory Star smoke game 28 accepted as the one documented judgment exception (its Copycat explanation is supported by a possible sampled path, not a replay of the bot's exact original search), and "My conditional approval stands: pin the existing candidate once all remaining required trace checks pass" (RUN5; `../results/engine_switch_rules_2026-10/README.md`).
- **Evidence** (`../results/engine_switch_rules_2026-10/`; every replay matched by pairing and game number, counts asserted):
  - Step 7: 151,240 identity games equal to their references on every field: kta3 fresh and development, km3, k3 and kp3 on scoreboard v3's 45 cells, kog3, kq3, kpr3, and kd3 as a gate.
  - Step 7b: the watch build's 28,000 table games equal the plain ones; every repair counter 0, both off-gate counters above 0.
  - Step 7c: Dustin's decks 02, 06, 08 and 14, 1,920 floor games each, equal.
  - Steps 8 and 8b: 72,960 carrier and scratch games. The @N@ changed games are each accounted for in 8c (`8c_RESULT.txt`): the 297 CONDITION 3 games each traced, and 8 the rule could not settle each explained by repair A or B and accepted by Dustin on Oct 2 (`8c_DECISION.md`; Sonnet's result @S7@).
  - Step 9: km3's coverage baselines, 66,500 games, equal.
  - Step 10: `deckgym simulate` repeats k3 150/90/0, kp3 144/96/0 and kog3 149/91/0, and kta3 and km3 equal Sept 30's lines; goldfish `--coverage` byte-equal; `run_screen` under km3 equal.
- **History:** `../engine-2026-09-30/` (main-d363ba8) and earlier are kept unchanged, with their hashes in the manifest's historical releases.
"""
t = t.replace("@M7@", m[:7]).replace("@N@", n).replace("@S7@", s)
open(out, "w", encoding="utf-8", newline="\n").write(t)
EOF
}
build_final() {  # merge-commit dir base check|final: every file the pin writes, built and checked in dir; FILES lists them
  local fill=$1 dir=$2 base=$3 n got expected mf=()
  rm -rf "$dir"; mkdir -p "$dir/$PREL"
  for n in "${PROGS[@]}"; do cp -- "$(src_of $n)" "$dir/$PREL/$n" || stop "copying $n"; chmod 755 "$dir/$PREL/$n"; done
  ( cd "$dir/$PREL" && sha256sum "${PROGS[@]}" > SHA256SUMS ) || stop "sha256sum of the programs"
  while read -r h n; do [ "$h" = "${WANT[$n]}" ] || stop "the copy of $n is not the tested build"; done < "$dir/$PREL/SHA256SUMS"
  git show "$base:project_manifest.json" > "$TMP/manifest_base.json" || stop "git show ${base:0:7}:project_manifest.json"
  [ "$4" = final ] || mf=(--check)
  python3 "$MANIFEST_PY" "$fill" "$C" "$dir/$PREL/SHA256SUMS" "$TMP/manifest_base.json" "$dir/project_manifest.json" "$C8N" "$C8S" "${mf[@]}" \
    > "$TMP/manifest.out" 2>&1 || { cat "$TMP/manifest.out" >&2; stop "update_manifest_rules.py refuses (printed above; nothing changed)"; }
  build_docs "$fill" "$dir" "$base"
  if ! grep -qx "$PREL/README.md" "$TMP/docs.list"; then engine_readme "$fill" "$dir/$PREL/README.md" || stop "writing $PREL/README.md"; fi
  rm -rf "$TMP/t2"; mkdir -p "$TMP/t2/rl"; cp -- "$R/current_engine.py" "$dir/project_manifest.json" "$TMP/t2/"
  ln -s "$dir/$PREL" "$TMP/t2/$PREL"
  got=$(python3 "$TMP/t2/current_engine.py" 2>&1) || stop "current_engine.py refuses the new manifest (tried in a scratch folder; nothing installed): $got"
  [ "$got" = "$(realpath "$dir/$PREL/deckgym")" ] || stop "current_engine.py resolves $got from the new manifest (scratch folder)"
  mapfile -t FILES < <(cd "$dir" && find . -type f | sed 's|^\./||' | LC_ALL=C sort)
  expected=$( { printf '%s\n' project_manifest.json "$PREL"/{deckgym,legality_scan,goldfish,SHA256SUMS,README.md}; cat "$TMP/docs.list"; } | LC_ALL=C sort -u)
  [ "$(printf '%s\n' "${FILES[@]}")" = "$expected" ] || stop "the pin would write ${FILES[*]}, not $(echo $expected)"
  mapfile -t DOCS_T < "$TMP/docs.list"
}
fr_gate() {  # the floor re-check's plan is there (or drafted in docs/), and nothing of a run is
  local bad
  [ -f "$FR/PLAN.md" ] || grep -qx "$FRREL/PLAN.md" "$TMP/docs.list" \
    || stop "$FRREL/PLAN.md must be there, or drafted in docs/: the floor re-check's plan is committed with the pin, before any of its games"
  if [ -d "$FR" ]; then
    bad=$(cd "$FR" && find . -mindepth 1 \( -type d -printf '%P/\n' -o ! -type d -printf '%P\n' \) | grep -vxE "$FR_FILES" || true)
    [ -z "$bad" ] || stop "$FRREL/ holds more than its plan and scripts ($(echo $bad)): no game may come before the plan's commit"
  fi
}
# --check, and the pin before step 11: main's HEAD stands in for the merge commit
build_final "$H" "$TMP/check" "$H" check
fr_gate
for f in "${FILES[@]}"; do   # the pin's own files as they are now: main's, absent, or already exactly the pin's
  if grep -qxF -- "$f" "$TMP/docs.list" || [ "$f" = "$PREL/README.md" ]; then continue; fi   # their BASE; its text names the merge
  if git cat-file -e "$H:$f" 2> /dev/null; then
    [ "$(git hash-object -- "$f" 2> /dev/null || true)" = "$(git rev-parse "$H:$f")" ] || stop "$f in the working copy is not main's"
  elif [ -e "$f" ]; then cmp -s -- "$f" "$TMP/check/$f" || stop "$f is here already and is not what the pin writes (move it aside)"; fi
done
for p in "${DOCS_T[@]}"; do FOLDERS+=(":(exclude,literal)$DREL/$p"); done   # the drafts (their names are the targets')
# what the pin commit also carries from the two folders: each file there that is untracked or differs from main, besides
# the pin's own files and PIN_STATUS.txt (path, git blob). Checked again just before the commit: nothing new, nothing changed.
sweep_snapshot() {
  local f
  { git ls-files -o --exclude-standard -- "${FOLDERS[@]}"; git diff --no-renames --name-only HEAD -- "${FOLDERS[@]}"; } \
    | LC_ALL=C sort -u | { grep -vxF -f <(printf '%s\n' "${FILES[@]}" "$REL/PIN_STATUS.txt") || true; } \
    | while IFS= read -r f; do
        if [ -f "$f" ]; then printf '%s\t%s\n' "$f" "$(git hash-object -- "$f")"; else printf '%s\tgone\n' "$f"; fi
      done > "$1"
}
sweep_snapshot "$TMP/sweep0.tsv"
nd=""; for p in "${NOTED_DOCS[@]}"; do grep -qxF -- "$p" "$TMP/docs.list" || nd+="$p "; done
echo "steps 12-13 built in a scratch folder: the programs as tested; the manifest builds (main-d363ba8 to the history); current_engine.py resolves the new deckgym; $PREL/README.md from $(grep -qx "$PREL/README.md" "$TMP/docs.list" && echo "docs/" || echo "the pin's own text"); ${#FILES[@]} files in all"
echo "documents (each against its BASE and DOCS hash; main's HEAD fills the placeholders in this scratch build):"; awk -F'\t' '{printf "  %s: %s, %s placeholder(s)\n", $1, ($2 == "new" ? "a new file" : "replaces its drafted base"), $4}' "$TMP/docs.tsv"
[ -z "$nd" ] || echo "NOTE: PLAN.md step 13 also names $nd(no draft in docs/; not a stop)"
echo "floor re-check: $FRREL/PLAN.md $( [ -f "$FR/PLAN.md" ] && echo "is there" || echo "is drafted in docs/"), and no game file"
echo "the pin commit also carries $(grep -c . "$TMP/sweep0.tsv" || true) uncommitted file(s) of $REL and $FRREL (docs/'s drafts excluded; each must be unchanged at the commit):"
awk -F'\t' '{printf "  %s%s\n", $1, ($2 == "gone" ? " (deleted: the pin stops)" : "")}' "$TMP/sweep0.tsv"
if [ $MODE = check ]; then echo "CHECK PASSED: nothing was changed"; exit 0; fi

# ======================================================================================================================
# From here main changes.
COMMIT_PATHS=(project_manifest.json "$PREL" "${DOCS_T[@]}" "${FOLDERS[@]}")
# PLAN.md step 8c's evidence was "touched_check.txt complete, then PREPARE DONE"; 8c_RESULT.txt (gate 3) takes its place
if ! grep -qE "^PREPARE DONE $C( |$)" "$STATUS"; then
  echo "PREPARE DONE $C $(now): sittings 1 and 2 passed, and 8c passed ($C8LINE; 8c_RESULT.txt); written by pin/pin_rules.sh" >> "$STATUS"
fi
# --- step 11: the merge ------------------------------------------------------------------------------------------------
PHASE=merge
if [ $MERGED = 0 ]; then
  cat > "$TMP/merge_msg" <<MSG
Merge sonnet/rules-fixes (R f8cfa9c) into main: the rules switch (repairs A + B, kd's follow-ons, F1-F7)

engine/ is R's tree 38af8b0, byte-identical to the built and replayed candidate ${C:0:7} (main c9f4224 + R; kept
on the laptop at $CREF). Main has moved since, outside engine/.
Against main ${H:0:7}, the first parent, outside rl/results/ only the plan's 9 engine files change:
$(printf '  %s\n' "${ALLOWED[@]}")
engine/src/players/ and Cargo.lock do not, and nothing is deleted; under rl/results/ $NRES_A files are added and
$NRES_M existing records changed. Made off-tree by rl/results/engine_switch_rules_2026-10/pin/pin_rules.sh (git
merge-tree, git commit-tree); main moved to it with git update-ref from the value the pin read. The pin commit follows
(PLAN.md steps 12-13).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
  M=$(git "${GIT_ID[@]}" commit-tree "$T" -p "$H" -p "$RC" -F "$TMP/merge_msg") || stop "git commit-tree failed; nothing merged"
  [ "$(git rev-parse "$M^{tree}")" = "$T" ] && [ "$(git rev-parse "$M^1")" = "$H" ] && [ "$(git rev-parse "$M^2")" = "$RC" ] \
    && ! git rev-parse -q --verify "$M^3" > /dev/null || stop "the merge commit ${M:0:7} is not (main, R) with the checked tree; nothing merged"
  [ "$(git rev-parse HEAD)" = "$H" ] || stop "main moved during the pin's checks (now $(git rev-parse --short HEAD)); nothing merged: run the pin again"
  mkdir -p "$TMP/mnew" "$TMP/mbak"
  for f in "${MPATHS[@]}"; do
    mkdir -p -- "$TMP/mnew/$(dirname -- "$f")"; git cat-file --filters "$M:$f" > "$TMP/mnew/$f" || stop "git cat-file --filters ${M:0:7}:$f"
  done
  merge_clash   # again, right before the working copy changes
  PHASE=merge_install
  for i in "${!MPATHS[@]}"; do
    f=${MPATHS[i]}
    if [ -f "$f" ] && cmp -s -- "$f" "$TMP/mnew/$f"; then continue; fi   # already the merge's (an identical untracked copy)
    # re-checked just before it is overwritten: a modified path's backup must still be main's, an added path still absent
    if [ "${MSTAT[i]}" = M ]; then
      mkdir -p -- "$TMP/mbak/$(dirname -- "$f")"; cp -p -- "$f" "$TMP/mbak/$f" || stop "backing up $f"
      [ "$(git hash-object --path="$f" -- "$TMP/mbak/$f")" = "$(git rev-parse "$H:$f")" ] \
        || stop "$f changed since the check (another session's edit?); it was not overwritten"
    elif [ -e "$f" ] || [ -L "$f" ]; then
      stop "$f appeared since the check (another session?); it was not overwritten"
    fi
    d=$(dirname -- "$f"); nd=()
    while [ ! -d "$d" ]; do nd=("$d" "${nd[@]}"); d=$(dirname -- "$d"); done
    MW+=("$f")
    if [ ${#nd[@]} -gt 0 ]; then mkdir -p -- "$(dirname -- "$f")" || stop "making the folder of $f"; MDIRS+=("${nd[@]}"); fi
    cp -- "$TMP/mnew/$f" "$f" || stop "writing $f"
    if [ "$(git ls-tree "$M" -- "$f" | cut -d' ' -f1)" = 100755 ]; then chmod +x -- "$f"; fi
  done
  [ "$(git rev-parse HEAD)" = "$H" ] || stop "main moved during the merge's install (now $(git rev-parse --short HEAD)); nothing merged"
  MIDX=1   # from here an undo also unstages the merge's paths
  git_retry reset -q "$M" -- "${MPATHS[@]}" || stop "setting the shared index's entries for the merge's paths failed ($(git_err))"
  [ "$(git rev-parse HEAD)" = "$H" ] || stop "main moved while the shared index was set (now $(git rev-parse --short HEAD)); nothing merged"
  note "MERGING ${RC:0:7} into main as $M (from main ${H:0:7}; if main is on it, the merge is done and a re-run recognises it)"
  git_retry update-ref -m "pin_rules.sh: merge R f8cfa9c into main (the rules switch)" refs/heads/main "$M" "$H" \
    || stop "main moved during the pin, or its ref stayed locked ($(git_err)); nothing merged"
  PHASE=merged
  [ "$(git rev-parse HEAD)" = "$M" ] || stop "HEAD is not ${M:0:7} after git update-ref"
  note "MERGED ${RC:0:7} into main as $M ($HOW); engine/ = R's tree ${RTREE:0:7}, byte-identical to the built candidate ${C:0:7}'s; outside rl/results/ exactly the plan's 9 engine files, each modified; players/ and Cargo.lock unchanged; under rl/results/ $NRES_A files added and $NRES_M existing records changed (${RES_M_LINE:-none}); nothing deleted; ${#MW[@]} files written in the working copy"
  left=$(git status --porcelain --untracked-files=no -- "${MPATHS[@]}" || true)
  [ -z "$left" ] || note "NOTE: after the merge, git status shows changes in its paths: $(echo "$left" | head -n 5 | tr '\n' ';')"
else
  [ "$(git rev-parse HEAD)" = "$H" ] || stop "main moved during the pin's checks (now $(git rev-parse --short HEAD)): run the pin again"
fi
PIN_PARENT=$(git rev-parse HEAD)

# --- steps 12-13, built in a scratch folder first: nothing else in the working copy changes until every file is made ---
PHASE=build
F="$TMP/final"
build_final "$M" "$F" "$PIN_PARENT" final
fr_gate
# just before the install: main where the pin left it; every file the pin writes still main's (or absent, or already
# exactly the pin's; a document still its BASE) and not staged by anyone
[ "$(git rev-parse HEAD)" = "$PIN_PARENT" ] || stop "main moved during the pin (now $(git rev-parse --short HEAD)); nothing installed"
git diff --cached --quiet -- "${FILES[@]}" || stop "a file the pin writes is staged in the shared index (another session?); nothing installed"
docs_base_ok
for f in "${FILES[@]}"; do   # PRE: each file's state now (docs_base_ok set the documents'), re-checked at its install
  if grep -qxF -- "$f" "$TMP/docs.list"; then continue; fi
  if git cat-file -e "$PIN_PARENT:$f" 2> /dev/null; then
    [ "$(git hash-object -- "$f" 2> /dev/null || true)" = "$(git rev-parse "$PIN_PARENT:$f")" ] \
      || stop "$f in the working copy is not main's (an uncommitted edit?); nothing installed"
    PRE[$f]=$(sha "$f")
  elif [ -e "$f" ]; then
    cmp -s -- "$f" "$F/$f" || stop "$f is here already and is not what the pin writes (move it aside); nothing installed"
    PRE[$f]=$(sha "$f")
  else PRE[$f]=absent; fi
done

# --- the install, in one go, and the checks in the working copy --------------------------------------------------------
PHASE=install
[ -d "$FR" ] || FR_MADE=1
for f in "${FILES[@]}"; do   # each re-checked just before it is overwritten: its backup as at the pre-install check
  if [ -e "$f" ] || [ -L "$f" ]; then
    mkdir -p -- "$TMP/bak/$(dirname -- "$f")"; cp -p -- "$f" "$TMP/bak/$f" || stop "backing up $f"
    [ "${PRE[$f]:-unset}" != absent ] && [ "$(sha "$TMP/bak/$f")" = "${PRE[$f]:-unset}" ] \
      || stop "$f changed since the pre-install check (another session's edit?); it was not overwritten"
  elif [ "${PRE[$f]:-unset}" != absent ]; then stop "$f went away since the pre-install check (another session?)"; fi
  INSTALLED+=("$f")
  mkdir -p -- "$(dirname -- "$f")" && cp -- "$F/$f" "$f" || stop "installing $f failed"
done
for n in "${PROGS[@]}"; do chmod 755 "$P/$n"; done
got=$(python3 "$R/current_engine.py" 2>&1) || stop "current_engine.py refuses the new release: $got"
[ "$(realpath "$got")" = "$(realpath "$P/deckgym")" ] || stop "current_engine.py resolves $got, not $PREL/deckgym"
pilot=$(wp) && [ "$pilot" = km3 ] || stop "the screen and the floor no longer default to km3 ($pilot)"
for f in "${FILES[@]}"; do cmp -s -- "$f" "$F/$f" || stop "$f changed right after the install (another session?)"; done
note "PINNED in $PREL: $(tr '\n' ' ' < "$P/SHA256SUMS")(programs.sha256's, never rebuilt)"
note "MANIFEST available_release = main-${M:0:7} ($PREL/deckgym); main-d363ba8 in the history, superseded; current_engine.py resolves it; the screen and the floor stay km3"
note "DOCS: $(awk -F'\t' '{printf "%s (%s; draft %s, installed %s, %s placeholder(s)); ", $1, ($2 == "new" ? "new" : "replaced its BASE"), $5, $6, $4}' "$TMP/docs.tsv")$PREL/README.md from $(grep -qx "$PREL/README.md" "$TMP/docs.list" && echo "docs/" || echo "pin_rules.sh's own text")"

# --- the pin commit: from a private index, so exactly the pin's files go in (the programs executable), and main moves
# --- to it only if main is still where the pin left it (git update-ref with the old value)
[ "$(sha "$SELF")" = "$SELF_SHA" ] && [ "$(sha "$MANIFEST_PY")" = "$MPY_SHA" ] || stop "pin_rules.sh or update_manifest_rules.py changed during the run"
XI="$TMP/index"
GIT_INDEX_FILE="$XI" git read-tree "$PIN_PARENT" || stop "git read-tree (private index)"
GIT_INDEX_FILE="$XI" git add -- "${FOLDERS[@]}" || stop "git add of this switch's folder and floor_recheck_2026-10 (private index)"
# what the add swept in besides the pin's own files and PIN_STATUS.txt: each must be as at the check gate (sweep0.tsv)
GIT_INDEX_FILE="$XI" git diff --cached --no-renames --name-status "$PIN_PARENT" -- "$REL" "$FRREL" > "$TMP/swept.ns" \
  || stop "git diff --cached (private index)"
swept=""; bad=""; printf '%s\n' "${FILES[@]}" "$REL/PIN_STATUS.txt" > "$TMP/own.list"
while IFS=$'\t' read -r st p; do
  if grep -qxF -- "$p" "$TMP/own.list"; then continue; fi
  b=$(GIT_INDEX_FILE="$XI" git rev-parse -q --verify ":$p" 2> /dev/null || echo gone)
  w=$(awk -F'\t' -v p="$p" '$1 == p {print $2}' "$TMP/sweep0.tsv")
  if [ -z "$w" ] || [ "$w" != "$b" ]; then bad+="$p "; fi
  swept+="$p ($st); "
done < "$TMP/swept.ns"
[ -z "$bad" ] || stop "the pin commit would carry files of $REL or $FRREL that are new or changed since the check gate (another session writing there?): $bad"
note "SWEPT into the pin commit from $REL and $FRREL (uncommitted before it, each as at the check gate): ${swept:-none}"
note "PIN DONE ${M:0:7}: every step passed; this file goes into the pin commit (should that commit fail, a PIN STOPPED line follows and the install is undone)"
GIT_INDEX_FILE="$XI" git add -- "$REL/PIN_STATUS.txt" || stop "git add PIN_STATUS.txt (private index)"
for f in "${FILES[@]}"; do
  mode=100644; case $f in "$PREL"/deckgym|"$PREL"/legality_scan|"$PREL"/goldfish) mode=100755;; esac
  blob=$(git hash-object -w --no-filters -- "$F/$f") || stop "git hash-object $f"
  GIT_INDEX_FILE="$XI" git update-index --add --cacheinfo "$mode,$blob,$f" || stop "git update-index $f (private index)"
done
tree=$(GIT_INDEX_FILE="$XI" git write-tree) || stop "git write-tree (private index)"
git diff-tree -r --no-renames --name-status "$PIN_PARENT" "$tree" > "$TMP/pin.ns"
extra=$(cut -f2- "$TMP/pin.ns" | grep -vxF -f <(printf '%s\n' "${FILES[@]}") | grep -vE "^($REL|$FRREL)/" || true)
[ -z "$extra" ] || stop "the pin commit would also change: $(echo "$extra" | tr '\n' ' ')"
drafts=$(cut -f2- "$TMP/pin.ns" | grep -E "^$DREL/" | grep -vxE "$DREL/((BASE|DOCS)\.sha256|CHANGES\.md)" || true)
[ -z "$drafts" ] || stop "the pin commit would carry docs/'s drafts: $(echo "$drafts" | tr '\n' ' ')"
gone=$(awk -F'\t' '$1 != "A" && $1 != "M" {print $1 " " $2}' "$TMP/pin.ns")
[ -z "$gone" ] || stop "the pin commit would delete or retype: $(echo "$gone" | tr '\n' ';')"
missing=$(printf '%s\n' "${FILES[@]}" | grep -vxF -f <(cut -f2- "$TMP/pin.ns") || true)
[ -z "$missing" ] || stop "the pin commit would not change: $(echo "$missing" | tr '\n' ' ')"
cat > "$TMP/pin_msg" <<MSG
Pin the rules engine (main-${M:0:7}): repairs A + B, kd's follow-ons, F1-F7 (the rules switch)

Dustin, Sept 30: "Sure go for all 9" (a conditional go, "pin if all pass"); Oct 1: Victory Star smoke game 28 is the
one documented judgment exception, and "My conditional approval stands: pin the existing candidate once all remaining
required trace checks pass".
- engine/: R f8cfa9c's tree 38af8b0 (main's merge ${M:0:7}), byte-identical to the built and replayed candidate
  ${C:0:7}; the plan's 9 engine files change (5 rules, 4 tests); engine/src/players/ and Cargo.lock unchanged
- identity, all equal: 151,240 games (step 7), the watch build's 28,000 with the table's counters (7b), Dustin's decks
  02, 06, 08 and 14 (7c), km3's coverage baselines 66,500 (9), the command line, goldfish and the screen (10)
- carrier and scratch games (8, 8b): $(fmt "$C8N") changed, each accounted for in 8c (8c_RESULT.txt: the 297
  CONDITION 3 games each traced; 8 the rule could not settle, each explained by repair A or B and accepted by Dustin
  on Oct 2, 8c_DECISION.md; Sonnet's result ${C8S:0:7})
- the programs in rl/engine-2026-10-02/ (mode 100755) with SHA256SUMS and README.md; the manifest (main-d363ba8 kept
  as history, superseded); the documents ($(echo "${DOCS_T[@]}")); this switch's record; the floor's pre-use re-check
  plan (floor_recheck_2026-10/), committed before any of its games. km3 stays the working pilot.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
X=$(git "${GIT_ID[@]}" commit-tree "$tree" -p "$PIN_PARENT" -F "$TMP/pin_msg") || stop "git commit-tree (the pin commit)"
[ "$(git symbolic-ref -q HEAD || true)" = refs/heads/main ] || stop "the working copy left main during the pin"
[ "$(git rev-parse HEAD)" = "$PIN_PARENT" ] || stop "main moved during the pin (now $(git rev-parse --short HEAD)); nothing committed"
PIDX=1   # from here an undo also unstages the pin's paths
git_retry reset -q "$X" -- "${COMMIT_PATHS[@]}" || stop "putting the pin's files in the shared index failed ($(git_err))"
[ "$(git rev-parse HEAD)" = "$PIN_PARENT" ] || stop "main moved while the shared index was set (now $(git rev-parse --short HEAD)); nothing committed"
git_retry update-ref -m "pin_rules.sh: pin the rules engine (main-${M:0:7})" refs/heads/main "$X" "$PIN_PARENT" \
  || stop "main moved during the pin, or its ref stayed locked ($(git_err)); nothing committed"
PHASE=done
[ "$(git rev-parse HEAD)" = "$X" ] || stop "HEAD is not the pin commit ${X:0:7} after git update-ref"
changed=$(git status --porcelain --untracked-files=no -- "${COMMIT_PATHS[@]}" || true)
# docs/'s drafts (copies of START_HERE.md, CLAUDE.md and RUN5 with placeholders) leave the repository, so no session reads
# them as instructions and GitHub Desktop doesn't offer them for a commit; BASE.sha256, DOCS.sha256 and CHANGES.md stay
DRAFTS_TO="$HOME/pin_rules_drafts_${M:0:7}"; nmv=0
for p in "${DOCS_T[@]}"; do
  if [ -f "$D/$p" ]; then { mkdir -p -- "$DRAFTS_TO/$(dirname -- "$p")" && mv -- "$D/$p" "$DRAFTS_TO/$p" && nmv=$((nmv + 1)); } || true; fi
done
find "$D" -mindepth 1 -type d -empty -delete 2> /dev/null || true
echo "pin commit ${X:0:7} on merge ${M:0:7}. Not pushed."
[ -z "$changed" ] || echo "NOTE: in the working copy these pin paths differ from the pin commit (an edit by another session after the install?): $(echo "$changed" | tr '\n' ';')"
if git merge-base --is-ancestor origin/main HEAD 2> /dev/null; then
  echo "origin/main as last fetched ($(git rev-parse --short origin/main)) is behind main, so the push should go straight in."
else
  echo "NOTE: origin/main as last fetched has commits main lacks: a push is refused until they are merged. Ask before pulling."
fi
echo "Next, in GitHub Desktop: Fetch origin first; if it then offers Pull origin, ask the laptop session before pulling; else Push origin."
echo "After the push: tell Sonnet, and the cloud through Dustin's paste block, that the official engine is main-${M:0:7} ($PREL/); the working pilot stays km3. Take main before any screen, floor or calibration run."
echo "Then the floor's pre-use re-check (PLAN.md step 15), as $FRREL/PLAN.md says."
echo "docs/'s drafts are not committed: $nmv of ${#DOCS_T[@]} moved out of the repository to $DRAFTS_TO$( [ "$nmv" = "${#DOCS_T[@]}" ] || echo "; move the rest out of $DREL/ by hand, and never commit them")."
git --no-pager log -1 --stat --format='%h %s' > "$TMP/log" || true; head -n 40 "$TMP/log"
}
main "$@"

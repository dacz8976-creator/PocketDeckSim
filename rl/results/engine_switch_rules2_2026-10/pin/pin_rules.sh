#!/usr/bin/env bash
# Rules switch 2's pin: PLAN.md steps 11-14 and the hand-off to step 15 (../PLAN.md steps 11-14 and 15: "The pin: after
# PREPARE DONE and your word. Merge off-tree, pin_rules.sh with the new file list, and the programs to rl/engine-<date>/;
# main-8626a35 moves to history", then the documents). Dustin, Oct 9: "1-3 sure" (go, "update if everything passes"; the
# scope; the new reference games) and "Alright it is fine to use the laptop over the weekend" (../PLAN.md lines 24-29,
# ../RELEASE_PACKAGE.md); "The pin still waits for his word on any judgment call" (PLAN.md line 29 and section 6). No games,
# no build. A copy of ../../engine_switch_rules_2026-10/pin/pin_rules.sh (the Oct 1 switch's pin, which made
# main-8626a35; itself adapted from ../../engine_switch_2026-09-30/pin.sh: its structure, safety and undo), adapted for
# switch 2 by ADAPTATION_SPEC.md section 10; what was adapted is listed at the end of this header.
# Runs only when sittings 1 and 2 passed for the candidate ../candidate.txt names (main + P; STATUS.txt: SITTING 1 DONE,
# SITTING 2 DONE, STEP 7c-seeds DONE and every STEP 4-10 DONE line, each step's files still as its step_<n>.sha256
# records them; no HALT, unless Dustin's word is given) and 8c passed (../8c_RESULT.txt, committed by the laptop after the
# coordinator's audit; its one line is in README.md here). A failed gate stops everything: main, the manifest and the
# documents stay untouched, and it goes to the coordinator first.
#   11 main moves to a merge commit of P (the final engine commit of claude/coin-prevention-round2, taken by commit:
#      ../switch2.env's P) made off-tree on CURRENT main: git merge-tree --write-tree (a conflict stops), git commit-tree
#      with parents main and P. Checked before anything changes: main's engine/ is unchanged since the candidate's first
#      parent (switch2.env's OFFICIAL_TREE, main-8626a35's); the merge's engine/ is P's tree (P_TREE), the built
#      candidate's, byte for byte; against main, outside rl/results/ exactly the engine files of
#      ../allowed_engine_files.tsv change, each with its listed status (M or A); engine/src/players/, every Cargo.lock and
#      Cargo.toml unchanged; nothing deleted or retyped anywhere; no record P brings under this switch's folder clashes
#      with a file of the same name on main or in the working copy (ADAPTATION_SPEC 1.10). Then the working copy's files
#      for exactly the merge's changed paths are written from the merge (each must be main's beforehand, or absent if
#      added), the shared index's entries for exactly those paths are set to the merge's (as pin.sh line 487 does for its
#      own paths), and main moves with git update-ref, only from the value the pin read (never a checkout). pin.sh's step
#      8 did the same through git merge --ff-only.
#   12 the three tested programs (programs.sha256's plain build, as PIN_STATUS.txt's "(new, plain)" lines name them) for
#      switch2.env's ENGINE_DIR (rl/engine-<the pin's date>/) with SHA256SUMS and README.md; update_manifest_rules.py
#      (main-8626a35 to the history, superseded; the release main-<merge short>); current_engine.py must resolve the new
#      deckgym. The screen and the floor keep km3 (no file of theirs changes).
#   13-14 the reviewed documents in docs/ (README.md here), each installed only if its target still has its BASE.sha256
#      hash and the draft its DOCS.sha256 hash, with @@MERGE@@ and @@MERGE_SHORT@@ filled with the merge commit.
#   Then one pin commit of exactly: project_manifest.json, ENGINE_DIR/, the installed documents, this switch's folder
#   (without docs/'s drafts, .sitting*, *.part, __pycache__; docs/'s BASE.sha256, DOCS.sha256 and CHANGES.md go in) and
#   step 15's folder (switch2.env's FR_REL: its plan, before any of its games). It is made from a private index (the
#   programs executable, mode 100755), and main moves to it only if main is still where the pin left it. The uncommitted
#   files of those two folders it carries are listed by --check and must be unchanged since the check gate, and
#   PIN_STATUS.txt's SWEPT line names them. Other sessions' changes elsewhere, staged or not, are left alone. Nothing is
#   pushed. After the commit, docs/'s drafts are moved out of the repository to ~/pin_rules2_drafts_<merge short>/ (copies
#   of START_HERE.md, CLAUDE.md and RUN5 with placeholders). The STEP 15 HANDOFF line (PIN_STATUS.txt, and printed) lists
#   step 15's work.
# Every check that can run before the working copy changes runs first, steps 12-14 built in a scratch folder included.
# --check runs them all and changes nothing (no ref, file or index entry; git merge-tree writes only objects).
# PIN_CHECK_WITHOUT_8C=1 with --check skips the 8c gate, for a dry run before 8c_RESULT.txt is in. A stop writes
# "PIN STOPPED: <why>" to PIN_STATUS.txt (pin mode only); a start refused (a data file or value not final, an environment
# variable set) writes nothing and exits 2. Each file is re-checked just before it is overwritten. A stop during the
# merge's install undoes it (main had not moved). Once main is on the merge, the merge stays, a stop says so (don't push
# before the pin finishes), and a re-run recognises it (by its MERGING or MERGED line). A stop after the pin's install
# began undoes the install (each installed file still as the pin wrote it goes back as it was, or away if new; the pin's
# paths are unstaged if the pin had set them). If main moved meanwhile, the undo goes ahead only when the new commit didn't
# touch the pin's paths; otherwise it says to check main first. After a hard kill mid-install (no trap ran), restore the
# paths git status shows to main's first (the merge's install too: main had not moved), then re-run.
# The busy check sees WSL processes and launch_detached's pid files only: no commits (GitHub Desktop included) or runs
# elsewhere while the pin runs. The pin is done when its commit is on main.
# Usage (WSL): bash pin_rules.sh --check       (a few seconds: run it plainly; it changes nothing)
#   The pin itself: start it through rl/strength/launch_detached.sh, as every run that must outlive the starting process
#   (README "Long runs on the laptop"; its own pid file is not "busy"), so a closed window or a tool call's time limit cannot
#   cut it mid-install with no trap run:
#   bash rl/strength/launch_detached.sh start rules2-pin --dir "$R" -- bash "$R/rl/results/engine_switch_rules2_2026-10/pin/pin_rules.sh"
#   Optional: PIN_BUILD_DIR=<dir with engine/target/release, or that dir>; PIN_AFTER_HALT='<Dustin's words>' if a SITTING
#   HALT is on record; PIN_DUSTIN='<Dustin's words>' when a judgment call waits for him: 8c_RESULT.txt has unexplained or
#   judgment-call games ("dustin <a>" above 0), or deck 10's t-weezing floor row changed with no Will reached in its Will row
#   (PLAN.md section 6: the pin waits for his word). His words must be in the committed 8c_DECISION.md, verbatim (spaces and
#   line breaks aside). It takes minutes, at home with nothing else going.
# Adapted for switch 2 (ADAPTATION_SPEC.md section 10; old line numbers are the Oct 1 copy's):
#   - this folder (REL), its lock /tmp/pocketdecksim_pin_rules2_2026-10.lock and sitting locks; ENGINE_DIR (PREL) and
#     FR_REL (FRREL) from ../switch2.env, read with a regex and never sourced; the pin needs every data file final: a
#     "# TO FINALIZE" first line or a TO_FINALIZE value refuses the start (P-2, ADAPTATION_SPEC 1.2);
#   - the candidate and its main from ../candidate.txt; P, P_TREE, OFFICIAL_TREE (main's engine/ until the merge), CREF
#     and the old programs from switch2.env; the allowed files with their statuses from allowed_engine_files.tsv; each
#     checked against git at the start (git diff OFFICIAL P -- engine/, git log OFFICIAL..P -- engine/) (P-3);
#   - the tested programs read from programs.sha256 (no constants), cross-checked with PIN_STATUS.txt, in sitting 1's
#     build folder engine-rules2-<candidate short> (P-4, P-12); STEP 7c-seeds required (P-5);
#   - gate 3: 8c's new line (verdicts on_board/lookahead/unexplained/judgment, both halves and the revert check for every
#     lookahead game, the traced counts of CONDITION 3 = the hand-off's offgate_only rows, of its none rows and of its
#     other_only rows, Dustin's count); handoff_8c.tsv equal to its per-set files put together; the changed games of the
#     STEP 7c, 8b, 8 and 9 lines, step by step, against it; deck 10's t-weezing floor row tied to its Will row (pairing
#     60); PIN_DUSTIN, verbatim in 8c_DECISION.md, when a judgment call waits for him (P-6, P-11; the reviews of Oct 9);
#   - gate 6: the old programs are switch2.env's OLD_DIR; no DECKGYM_* in the environment (a start refusal, section 1.8);
#     a live launch_detached run in this working copy, a strength process, or a process of a run $HOME/runs/watch.list
#     names is busy too (P-13);
#   - gate 7: P instead of R; statuses checked; Cargo.toml as well as Cargo.lock; the reserved names (P-14);
#   - the documents (required: PLAN.md steps 11-14's list, rules/09, rules/04 and the READOUT included, and the files of
#     switch2.env's PIN_NOTED_EXTRA; rules/02 and PLAN.md noted; START_HERE keeps the 23.3B seed row; START_HERE and
#     CLAUDE.md name ENGINE_DIR), the engine README, the manifest's arguments, the messages and the subject '^Pin rules switch 2 (main-'
#     (the old one matches the Oct 2 pin 24374a00 on main, so gate 1 would answer "already done"); the drafts folder;
#     the STEP 15 HANDOFF line (P-7, P-8, P-15 to P-20).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0
unset PYTHONOPTIMIZE   # update_manifest_rules.py's checks are asserts: -O would drop them
main() {  # the whole script, read in full before it runs (called on the last line; the body is left unindented)
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SELF="$HERE/$(basename -- "${BASH_SOURCE[0]}")"
R=$(cd "$HERE/../../../.." && pwd)
REL=rl/results/engine_switch_rules2_2026-10; O="$R/$REL"
OLDREL=rl/results/engine_switch_rules_2026-10      # the Oct 1 switch (its pin made main-8626a35): never written here
[ "$HERE" -ef "$O/pin" ] && [ -f "$R/project_manifest.json" ] \
  || { echo "pin_rules.sh: run the copy in <repository>/$REL/pin (this one is in $HERE)" >&2; exit 2; }
DREL=$REL/pin/docs; D="$R/$DREL"
STATUS="$O/PIN_STATUS.txt"; SLOG="$O/STATUS.txt"; MANIFEST_PY="$HERE/update_manifest_rules.py"
ENVF="$O/switch2.env"
DATA_TSV=(allowed_engine_files.tsv engine_commits.tsv counters.tsv floor_7c.tsv reuse.tsv tools_8c.tsv)
# From the data files after gate 1 (ADAPTATION_SPEC 1.2; the names are the Oct 1 script's): RC = P (PLAN's P, the final
# engine commit; R on Oct 1), RTREE = P_TREE, MAIN_ENGINE = OFFICIAL_TREE (main-8626a35's engine/, main's until the
# merge), CREF, PREL = ENGINE_DIR (P is its folder), FRREL = FR_REL, ALLOWED and ALLOWED_NS (status<TAB>path).
# C and MAIN_C from candidate.txt (gate 2); WANT from programs.sha256 (gate 4).
PREL=""; P=""; FRREL=""; FR=""; RC=""; RTREE=""
PROGS=(deckgym legality_scan goldfish)
declare -A WANT=() OLDSUM=() E2=() CH=() PH=()
STEPS=(4 5 6 7 7b 7c 8-seeds 8b 8 9 10)   # each with its step_<n>.sha256; 7c-seeds has its STEP line only (as Oct 1)
CHANGED_STEPS=(7c 8b 8 9)                  # each STEP line holds one 'changed <N> of <M> deals' (ADAPTATION_SPEC 1.5)
# PLAN.md steps 11-14 name these documents: rules/09's open entries closed; rules/04 §9's Victory Star lines and the 2b note;
# READOUT §4's stale items; the engine README, CLAUDE.md, START_HERE's engine line and seed row, RUN5; and, through switch2.env's
# PIN_NOTED_EXTRA (required at the pin), the files holding Sonnet's note 8 and km3's new B2e reference (question 3a)
REQUIRED_DOCS=(START_HERE.md CLAUDE.md rl/RUN5.md "$REL/README.md" rules/09_engine_repairs_2026-09-22.md
               rules/04_actions_cards_effects.md rl/results/rules_recordings_2026-10-01/READOUT.md)
NOTED_DOCS=(rules/02_damage_knockouts_points.md "$REL/PLAN.md")   # not in PLAN.md's list: a NOTE when not drafted
FR_FILES='PLAN\.md|[A-Za-z0-9_.-]+\.(sh|py)'      # what step 15's folder may hold before its plan's commit
PIN_SUBJECT='^Pin rules switch 2 (main-'           # the pin commit's subject (git log --grep): done when it is on main
GIT_ID=(-c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com)
FOLDERS=()   # this switch's folder and step 15's, set once FR_REL is read
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
refuse() {  # before PIN START: nothing is written (ADAPTATION_SPEC 1.2 and 1.5: "start refused", exit 2)
  STOPPED=1
  echo "start refused: $*" >&2; exit 2
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
exec 9>/tmp/pocketdecksim_pin_rules2_2026-10.lock; flock -n 9 || { echo "another pin_rules.sh (rules switch 2) is running"; STOPPED=1; exit 1; }
cd "$R"
SELF_SHA=$(sha "$SELF"); MPY_SHA=$(sha "$MANIFEST_PY")

# --- gate 1: not done yet ------------------------------------------------------------------------------------------------
done_x=$(git log -1 --format=%h --grep="$PIN_SUBJECT" HEAD) || true
if [ -n "$done_x" ]; then echo "the pin is already done: its commit $done_x is on main (nothing to do)"; STOPPED=1; exit 0; fi

# --- the data files (ADAPTATION_SPEC 1.2): read with a regex, never sourced; the pin needs every one final and committed,
# --- and each value checked against git. A refusal here writes nothing (no PIN START yet).
[ -f "$ENVF" ] || refuse "$REL/switch2.env is missing"
n=0; re='^([A-Z0-9_]+)=([^ ]*)$'
while IFS= read -r line || [ -n "$line" ]; do
  n=$((n + 1))
  case $line in ''|'#'*) continue;; esac
  [[ $line =~ $re ]] || refuse "switch2.env: line $n is not KEY=VALUE: '${line:0:80}'"
  [ -z "${E2[${BASH_REMATCH[1]}]+x}" ] || refuse "switch2.env: ${BASH_REMATCH[1]} is set twice"
  E2[${BASH_REMATCH[1]}]=${BASH_REMATCH[2]}
done < "$ENVF"
for k in "${!E2[@]}"; do
  if [ "${E2[$k]}" = TO_FINALIZE ]; then
    case $k in ENGINE_DIR|FR_REL|PIN_NOTED_EXTRA) refuse "switch2.env: $k is TO FINALIZE (set at the pin: the laptop session names it and commits switch2.env)";;
               *) refuse "switch2.env: $k is TO FINALIZE (PLAN: P is not final yet; the pin needs every value)";; esac
  fi
done
for t in "${DATA_TSV[@]}"; do
  [ -f "$O/$t" ] || refuse "$REL/$t is missing"
  first=""; IFS= read -r first < "$O/$t" || true
  case $first in '# TO FINALIZE'*) refuse "$t: the file is TO FINALIZE (PLAN: P is not final yet)";; esac
done
for t in switch2.env "${DATA_TSV[@]}"; do
  git cat-file -e "HEAD:$REL/$t" 2> /dev/null || refuse "$REL/$t is not committed (the pin reads committed data files only: commit it, then start again)"
  git diff --quiet HEAD -- "$REL/$t" || refuse "$REL/$t differs from its commit (commit it or restore it, then start again)"
done
need() {  # need VAR KEY REGEX WHAT: VAR is set to switch2.env's KEY, which must match REGEX
  local v=${E2[$2]-}
  [ -n "$v" ] || refuse "switch2.env has no $2 ($4)"
  [[ $v =~ $3 ]] || refuse "switch2.env: $2=${v:0:80} is not $4"
  printf -v "$1" '%s' "$v"
}
need RC P '^[0-9a-f]{40}$' "a full commit (P, the final engine commit)"
need RTREE P_TREE '^[0-9a-f]{40}$' "a full tree id (P's engine/)"
need P_BRANCH P_BRANCH '^origin/[A-Za-z0-9._/-]+$' "a fetched branch (origin/...)"
need OFFICIAL OFFICIAL '^[0-9a-f]{40}$' "a full commit (main-8626a35's merge)"
need MAIN_ENGINE OFFICIAL_TREE '^[0-9a-f]{40}$' "a full tree id (the official engine/)"
need OLD_NAME OLD_RELEASE_NAME '^main-[0-9a-f]{7}$' "a release name (main-<7 hex>)"
need OLDPREL OLD_DIR '^rl/engine-[0-9]{4}-[0-9]{2}-[0-9]{2}$' "a programs folder (rl/engine-<date>)"
need 'OLDSUM[deckgym]' OLD_DECKGYM_SHA256 '^[0-9a-f]{64}$' "a sha256"
need 'OLDSUM[legality_scan]' OLD_LEGALITY_SCAN_SHA256 '^[0-9a-f]{64}$' "a sha256"
need 'OLDSUM[goldfish]' OLD_GOLDFISH_SHA256 '^[0-9a-f]{64}$' "a sha256"
need CREF CREF '^refs/pocketdecksim/[A-Za-z0-9._/-]+$' "a refs/pocketdecksim/ ref"
need SEED_NEW SEED_NEW_BLOCK '^[1-9][0-9]{9,11}$' "a seed block"
need PREL ENGINE_DIR '^rl/engine-2026-1[0-2]-[0-3][0-9]$' "rl/engine-<the pin's date> (the new programs folder)"
need FRREL FR_REL '^rl/results/[A-Za-z0-9_.-]+$' "rl/results/<step 15's folder>"
[ "$PREL" != "$OLDPREL" ] || refuse "switch2.env: ENGINE_DIR is OLD_DIR ($OLDPREL), the official programs' folder; the pin makes a new one"
[ "$FRREL" != "$REL" ] && [ "$FRREL" != "$OLDREL" ] || refuse "switch2.env: FR_REL ($FRREL) must be step 15's own folder"
NOTED_EXTRA=${E2[PIN_NOTED_EXTRA]-}
if [ -n "$NOTED_EXTRA" ]; then   # PLAN.md steps 11-14's documents too: required, as the others
  re='^[A-Za-z0-9_./-]+(,[A-Za-z0-9_./-]+)*$'
  [[ $NOTED_EXTRA =~ $re ]] || refuse "switch2.env: PIN_NOTED_EXTRA is not a comma list of repository paths"
  IFS=, read -r -a extra_docs <<< "$NOTED_EXTRA"; REQUIRED_DOCS+=("${extra_docs[@]}")
elif [ $MODE = pin ]; then
  refuse "switch2.env has no PIN_NOTED_EXTRA: PLAN.md steps 11-14 name Sonnet's note 8's stale items and km3's new B2e reference for the 16 rows (question 3a) among the pin's documents; name their files there (a comma list), draft them in pin/docs/, commit, then start again"
fi
P="$R/$PREL"; FR="$R/$FRREL"
FOLDERS=("$REL" "$FRREL" ":(exclude)$REL/.sitting*" ":(exclude)$REL/*.part" ":(exclude)$REL/*__pycache__*"
         ":(exclude)$FRREL/*.part" ":(exclude)$FRREL/*__pycache__*")   # docs/'s drafts are excluded once listed
ALLOWED=(); ALLOWED_NS=(); hdr=0; n=0; re=$'^(M|A)\t(engine/[A-Za-z0-9_./-]+)$'
while IFS= read -r line || [ -n "$line" ]; do
  n=$((n + 1))
  case $line in ''|'#'*) continue;; esac
  if [ $hdr = 0 ]; then
    [ "$line" = $'status\tpath' ] || refuse "allowed_engine_files.tsv: line $n is not the header 'status<TAB>path'"
    hdr=1; continue
  fi
  [[ $line =~ $re ]] || refuse "allowed_engine_files.tsv: line $n is not '<M or A><TAB>engine/<path>' (the pin takes modified and added engine files only: nothing deleted): '${line:0:100}'"
  ALLOWED+=("${BASH_REMATCH[2]}"); ALLOWED_NS+=("${BASH_REMATCH[1]}"$'\t'"${BASH_REMATCH[2]}")
done < "$O/allowed_engine_files.tsv"
[ ${#ALLOWED[@]} -gt 0 ] || refuse "allowed_engine_files.tsv lists no engine file"
git cat-file -e "$RC^{commit}" 2> /dev/null || refuse "P ${RC:0:7} is not here (Fetch origin)"
git cat-file -e "$OFFICIAL^{commit}" 2> /dev/null || refuse "the official engine's commit ${OFFICIAL:0:7} is not here"
[ "$(git rev-parse "$RC:engine")" = "$RTREE" ] || refuse "P ${RC:0:7}'s engine/ is not switch2.env's P_TREE ${RTREE:0:7}"
[ "$(git rev-parse "$OFFICIAL:engine")" = "$MAIN_ENGINE" ] || refuse "${OFFICIAL:0:7}'s engine/ is not switch2.env's OFFICIAL_TREE ${MAIN_ENGINE:0:7}"
git merge-base --is-ancestor "$OFFICIAL" "$RC" || refuse "P ${RC:0:7} does not contain the official engine ${OFFICIAL:0:7}"
got=$(git diff --no-renames --name-status "$OFFICIAL" "$RC" -- engine/ | LC_ALL=C sort)
want=$(printf '%s\n' "${ALLOWED_NS[@]}" | LC_ALL=C sort)
[ "$got" = "$want" ] || refuse "allowed_engine_files.tsv is not git diff --name-status ${OFFICIAL:0:7} P -- engine/ (git: $(echo "$got" | tr '\t\n' ' ;'))"
got=$(git log --format=%H "$OFFICIAL..$RC" -- engine/ | LC_ALL=C sort)
want=$(awk -F'\t' '/^#/ {next} !h {h = 1; if ($1 != "commit" || $2 != "kind") {print "(no header)"; exit} next} NF {print $1}' "$O/engine_commits.tsv" | LC_ALL=C sort)
[ "$got" = "$want" ] || refuse "engine_commits.tsv's commits are not git log ${OFFICIAL:0:7}..P -- engine/ ($(echo "$got" | wc -l) in git, $(echo "$want" | wc -l) listed)"
# the revert switches P's engine reads (named in the engine README and the manifest): DECKGYM_* in engine/src/ at P and
# not at the official engine; every revert_switch of counters.tsv must be one of them
mapfile -t sw_p < <(git grep -h -o -E 'DECKGYM_[A-Z0-9_]+' "$RC" -- engine/src/ | LC_ALL=C sort -u || true)
mapfile -t sw_o < <(git grep -h -o -E 'DECKGYM_[A-Z0-9_]+' "$OFFICIAL" -- engine/src/ | LC_ALL=C sort -u || true)
SWITCHES=()
for s in "${sw_p[@]}"; do case " ${sw_o[*]} " in *" $s "*) ;; *) SWITCHES+=("$s");; esac; done
[ ${#SWITCHES[@]} -gt 0 ] || refuse "P's engine/src/ reads no new DECKGYM_* switch (precondition (e): one revert switch per gate)"
cs=$(awk -F'\t' '/^#/ {next} !h {h = 1; for (i = 1; i <= NF; i++) if ($i == "revert_switch") c = i; if (!c) {print "NOCOLUMN"; exit} next}
  $c != "-" && $c != "" {n = split($c, sw, "+"); for (i = 1; i <= n; i++) print sw[i]}' "$O/counters.tsv" | LC_ALL=C sort -u)   # a "+" joins switches set together
[ "$cs" != NOCOLUMN ] || refuse "counters.tsv has no revert_switch column"
for s in $cs; do case " ${SWITCHES[*]} " in *" $s "*) ;; *) refuse "counters.tsv names the revert switch '$s', which P's engine/src/ doesn't read";; esac; done
if [ -n "${E2[DECKGYM_SWITCHES]-}" ]; then   # optional: the list as the laptop session wrote it (ADAPTATION_SPEC section 3)
  [ "$(tr ',' '\n' <<< "${E2[DECKGYM_SWITCHES]}" | LC_ALL=C sort -u)" = "$(printf '%s\n' "${SWITCHES[@]}")" ] \
    || refuse "switch2.env's DECKGYM_SWITCHES is not the set P's engine reads: ${SWITCHES[*]}"
fi
# environment hygiene (ADAPTATION_SPEC 1.8): at P the engine reads its switches from the environment, and one left set
# would make the checks below read another engine's evidence as this one's
bad_env=$(compgen -e | grep -E '^(DECKGYM_.*|PDL_EQUIV_DEALS|GOLDFISH_TRACE)$' | tr '\n' ' ' || true)
[ -z "$bad_env" ] || refuse "set in the environment: $bad_env(unset each, then start again)"
DATA_LINE=$(for t in switch2.env "${DATA_TSV[@]}"; do printf '%s %s, ' "$t" "$(sha "$O/$t" | cut -c1-16)"; done)

[ -f "$SLOG" ] && [ -f "$STATUS" ] || stop "no STATUS.txt or PIN_STATUS.txt in $REL"
if [ $MODE = pin ]; then
  note "PIN START: pin_rules.sh ${SELF_SHA:0:16}, update_manifest_rules.py ${MPY_SHA:0:16} (sha256; HEAD $(git rev-parse --short HEAD)); data: ${DATA_LINE%, }; env: no DECKGYM_* set; P ${RC:0:7}, $PREL, $FRREL"
fi
exec 8>> "$O/.sitting1.lock"; flock -n 8 || stop "sitting1.sh (or a child it left) holds .sitting1.lock"
exec 7>> "$O/.sitting2.lock"; flock -n 7 || stop "sitting2.sh (or a child it left) holds .sitting2.lock"

# --- gate 2: the record: both sittings done for the candidate, every step's line and files, no HALT --------------------
[ -s "$O/candidate.txt" ] || stop "no candidate.txt in $REL (sitting 1's step 4)"
cand() { sed -n "s/^$1 //p" "$O/candidate.txt" | head -n 1; }
C=$(cand candidate); MAIN_C=$(cand main)
[[ $C =~ ^[0-9a-f]{40}$ && $MAIN_C =~ ^[0-9a-f]{40}$ ]] || stop "candidate.txt doesn't name a candidate and its main (40 hex each)"
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
grep -qE "^STEP 7c-seeds DONE ${C:0:7} " "$SLOG" || stop "STATUS.txt has no 'STEP 7c-seeds DONE ${C:0:7}' line"
# the pin's own STOPPED, AFTER HALT and DUSTIN lines are the pin's; a FAILED or MISMATCH anywhere else stops the pin
if awk '!/^[0-9-]+T[0-9:]+Z PIN (STOPPED:|AFTER HALT|DUSTIN:)/ && /FAILED|MISMATCH/ {bad = 1} END {exit !bad}' "$STATUS"; then
  stop "a FAILED or MISMATCH line in PIN_STATUS.txt (a mismatch stops everything and goes to Dustin)"
fi
if grep -qE '^SITTING [12] HALT ' "$SLOG" "$STATUS"; then   # a check failed once: "update if everything passes" needs his word again
  [ -n "${PIN_AFTER_HALT:-}" ] || stop "a SITTING HALT is on record; 'update if everything passes' no longer covers it. With Dustin's word, run with PIN_AFTER_HALT='<his words>'"
  if [ $MODE = pin ]; then note "PIN AFTER HALT (Dustin): $PIN_AFTER_HALT"; fi
fi
prep=$( { grep -E '^PREPARE (DONE|HALT|STOPPED) ' "$STATUS" || true; } | grep -vE "^PREPARE DONE $C( |$)" || true)
[ -z "$prep" ] || stop "PIN_STATUS.txt has a PREPARE line that is not 'PREPARE DONE ${C:0:7}': ${prep:0:100}"
v=$(cand engine_tree); [ -z "$v" ] || [ "$v" = "$RTREE" ] || stop "candidate.txt's engine_tree ${v:0:7} is not P_TREE ${RTREE:0:7}"
for k in p r; do v=$(cand $k); [ -z "$v" ] || [ "$v" = "$RC" ] || stop "candidate.txt's '$k' line ${v:0:7} is not switch2.env's P ${RC:0:7}"; done
git cat-file -e "$C^{commit}" 2> /dev/null || stop "the candidate ${C:0:7} is not here"
[ "$(git rev-parse "$C^1")" = "$MAIN_C" ] && [ "$(git rev-parse -q --verify "$C^2" || true)" = "$RC" ] \
  && ! git rev-parse -q --verify "$C^3" > /dev/null || stop "the candidate's parents are not main ${MAIN_C:0:7} and P ${RC:0:7}"
[ "$(git rev-parse "$C:engine")" = "$RTREE" ] || stop "the candidate's engine/ is not P's tree ${RTREE:0:7}"
if git rev-parse -q --verify "$CREF" > /dev/null; then
  [ "$(git rev-parse "$CREF")" = "$C" ] || stop "$CREF is not the candidate ${C:0:7}"
fi
if ! git merge-base --is-ancestor "$RC" "$P_BRANCH" 2> /dev/null; then
  note "NOTE: P ${RC:0:7} is not on $P_BRANCH as last fetched (P is taken by commit, PLAN.md section 2; not a stop)"
fi

# --- gate 3: 8c (committed by the laptop after the coordinator's audit) --------------------------------------------------
git cat-file -e "HEAD:$REL/handoff_8c.tsv" 2> /dev/null || stop "handoff_8c.tsv is not committed"
git diff --quiet HEAD -- "$REL/handoff_8c.tsv" || stop "handoff_8c.tsv differs from its commit"
git show "HEAD:$REL/handoff_8c.tsv" > "$TMP/handoff.tsv"
# rows by step and by category (ADAPTATION_SPEC 1.12: reach, offgate_only = CONDITION 3, other_only, none)
awk -F'\t' '/^#/ {next}
  !h {h = 1; for (i = 1; i <= NF; i++) {if ($i == "step") s = i; if ($i == "category") c = i}; next}
  NF > 1 {n++; st[($s == "" ? "-" : $s)]++
          if ($c == "offgate_only") y++; else if ($c == "none") z++; else if ($c == "other_only") o++; else if ($c != "reach") bad++}
  END {if (!s || !c) {print "NOHEADER"; exit}; printf "%d %d %d %d %d", n + 0, y + 0, z + 0, o + 0, bad + 0; for (k in st) printf " %s=%d", k, st[k]; print ""}' \
  "$TMP/handoff.tsv" > "$TMP/handoff.counts"
read -r HN HC3 HNONE HOTHER HBAD HREST < "$TMP/handoff.counts" || true
[ "$HN" != NOHEADER ] && [ -n "$HN" ] || stop "handoff_8c.tsv has no 'step' and 'category' columns (sitting2_check.py's HEADER)"
[ "$HBAD" = 0 ] || stop "handoff_8c.tsv has $HBAD rows whose category is not reach, offgate_only, other_only or none"
# handoff_8c.tsv must be exactly the per-set row files (each in its step's manifest, checked in gate 2) put together in
# sitting2.sh's order: a rebuild that failed (only a note in sitting2.sh) cannot leave a stale hand-off here
{ head -n 1 "$TMP/handoff.tsv"
  for f in 7c_km3 8b_cloud_km3 8b_cloud_k3 8b_new2_km3 8b_new2_k3 8_km3 8_k3 8_will_km3 8_will_k3 9_km3; do
    [ -f "$O/handoff_$f.tsv" ] || stop "handoff_$f.tsv is missing (the rows its step handed to 8c)"
    tail -n +2 "$O/handoff_$f.tsv"
  done; } > "$TMP/handoff.expect"
cmp -s -- "$TMP/handoff.expect" "$TMP/handoff.tsv" \
  || stop "handoff_8c.tsv is not the per-set files handoff_<set>.tsv of steps 7c, 8b, 8 and 9 put together (a stale rebuild?): rebuild it with sitting2_check.py handoff, as sitting2.sh's checkpoints do, and commit it"
declare -A HS=(); for kv in ${HREST:-}; do HS[${kv%%=*}]=${kv#*=}; done
SC=0; hs=0
for s in "${CHANGED_STEPS[@]}"; do   # the last DONE line of each step (a step done again after a halt counts once)
  l=$( { grep -E "^STEP $s DONE ${C:0:7} " "$SLOG" || true; } | tail -n 1)
  k=$( { printf '%s\n' "$l" | grep -oE 'changed [0-9]+ of [0-9]+ deals' || true; } | wc -l)
  [ "$k" = 1 ] || stop "STATUS.txt's last 'STEP $s DONE ${C:0:7}' line holds $k 'changed <N> of <M> deals' phrases, not 1"
  PH[$s]=$(printf '%s\n' "$l" | grep -oE 'changed [0-9]+ of [0-9]+ deals')
  CH[$s]=$(echo "${PH[$s]}" | cut -d' ' -f2)
  [ "${HS[$s]:-0}" = "${CH[$s]}" ] || stop "handoff_8c.tsv has ${HS[$s]:-0} step-$s rows; STEP $s's line says ${PH[$s]}"
  SC=$((SC + 10#${CH[$s]})); hs=$((hs + ${HS[$s]:-0}))
done
[ "$hs" = "$HN" ] || stop "handoff_8c.tsv has $HN rows, of which only $hs are steps 7c, 8b, 8 and 9"
[ "$HN" = "$SC" ] && [ "$HN" -gt 0 ] || stop "handoff_8c.tsv has $HN changed games, the STEP 7c, 8b, 8 and 9 lines $SC (none at all would contradict the cloud's 8b rows)"
# PLAN.md section 3: deck 10's t-weezing floor row has no watch build, so its change is judged through step 8's Will row of
# the same matchup (deck 10 v t-weezing, pairing 60). When step 7c reports that floor row changed, a changed game of that Will
# row must show Will with a Confused attacker on the board (will_confused_attack); otherwise it is a judgment call for Dustin.
NEED_WORD=""   # why the pin waits for Dustin's word (a judgment call; PLAN.md section 6)
l=$( { grep -E "^STEP 7c DONE ${C:0:7} " "$SLOG" || true; } | tail -n 1)
FD10=$( { printf '%s\n' "$l" | grep -oE "page 10's t-weezing: [0-9]+ of [0-9]+ games differ" || true; } | head -n 1 | cut -d' ' -f4)
[[ $FD10 =~ ^[0-9]+$ ]] || stop "STATUS.txt's last STEP 7c line has no \"page 10's t-weezing: <k> of <n> games differ\" (deck 10's floor row, PLAN.md step 7c)"
W60=$(awk -F'\t' 'NR == 1 {for (i = 1; i <= NF; i++) {if ($i == "step") s = i; if ($i == "pairing") p = i; if ($i == "reach2_counters") r = i}; next}
  s && p && r && $s == "8" && $p == 60 && index($r, "\"will_confused_attack\"") {n++} END {print n + 0}' "$TMP/handoff.tsv")
if [ "$FD10" -gt 0 ]; then
  if [ "$W60" -gt 0 ]; then echo "deck 10's t-weezing floor row: $FD10 games changed in step 7c; its Will row (step 8, pairing 60) has $W60 changed games with will_confused_attack on the board (PLAN.md section 3 judges it there)"
  else NEED_WORD+="deck 10's t-weezing floor row changed in $FD10 games (step 7c), and no changed game of its Will row (step 8, pairing 60) shows will_confused_attack (PLAN.md section 3 judges that floor row through it); "; fi
fi
N8='(0|[1-9][0-9]*)'
WANT8C="8C PASS <the 8c result commit, 40 hex> verdicts: on_board <b>, lookahead <l>, unexplained <u>, judgment <j>; both_halves <l> of <l>; revert <l> of <l> reproduced; condition3 $HC3 traced $HC3; none $HNONE traced $HNONE; other_only $HOTHER traced $HOTHER; changed $HN accounted $HN; dustin <u+j> (8c_DECISION.md); net unaccounted 0; 8b_rows_vs_cloud equal   (with b + l + u + j = $HN)"
if [ $SKIP8C = 1 ]; then
  echo "CHECK: the 8c gate skipped (PIN_CHECK_WITHOUT_8C=1); 8c_RESULT.txt must be committed with the one line: $WANT8C"
  C8S=$(printf '%040d' 0); C8N=$HN; B8=$HN; L8=0; U8=0; J8=0; RV8=0; C3A=$HC3; NNA=$HNONE; NOA=$HOTHER; A8=0
  C8LINE="8C PASS $C8S verdicts: on_board $HN, lookahead 0, unexplained 0, judgment 0; both_halves 0 of 0; revert 0 of 0 reproduced; condition3 $HC3 traced $HC3; none $HNONE traced $HNONE; other_only $HOTHER traced $HOTHER; changed $HN accounted $HN; dustin 0 (8c_DECISION.md); net unaccounted 0; 8b_rows_vs_cloud equal"
else
  C8=$REL/8c_RESULT.txt
  git cat-file -e "HEAD:$C8" 2> /dev/null || stop "no 8c_RESULT.txt committed on main: 8c has not passed (or the laptop has not recorded it). It must hold: $WANT8C"
  git diff --quiet HEAD -- "$C8" || stop "8c_RESULT.txt differs from its commit"
  git show "HEAD:$C8" | tr -d '\r' > "$TMP/8c.txt"
  k=$(grep -cE '^8C( |$)' "$TMP/8c.txt" || true)
  [ "$k" = 1 ] || stop "8c_RESULT.txt has $k lines starting with 8C, not 1"
  C8LINE=$(grep -E '^8C( |$)' "$TMP/8c.txt")
  re="^8C PASS ([0-9a-f]{40}) verdicts: on_board $N8, lookahead $N8, unexplained $N8, judgment $N8; both_halves $N8 of $N8; revert $N8 of $N8 reproduced; condition3 $N8 traced $N8; none $N8 traced $N8; other_only $N8 traced $N8; changed $N8 accounted $N8; dustin $N8 \\(8c_DECISION\\.md\\); net unaccounted 0; 8b_rows_vs_cloud equal\$"
  [[ $C8LINE =~ $re ]] || stop "8c_RESULT.txt's line is not '$WANT8C': '$C8LINE'"
  C8S=${BASH_REMATCH[1]}; B8=${BASH_REMATCH[2]}; L8=${BASH_REMATCH[3]}; U8=${BASH_REMATCH[4]}; J8=${BASH_REMATCH[5]}
  BH8=${BASH_REMATCH[6]}; BHOF=${BASH_REMATCH[7]}; RV8=${BASH_REMATCH[8]}; RVOF=${BASH_REMATCH[9]}
  C3A=${BASH_REMATCH[10]}; C3T=${BASH_REMATCH[11]}; NNA=${BASH_REMATCH[12]}; NNT=${BASH_REMATCH[13]}
  NOA=${BASH_REMATCH[14]}; NOT=${BASH_REMATCH[15]}; C8N=${BASH_REMATCH[16]}; ACC8=${BASH_REMATCH[17]}; A8=${BASH_REMATCH[18]}
  [ "$((B8 + L8 + U8 + J8))" = "$C8N" ] || stop "8c_RESULT.txt: on_board $B8 + lookahead $L8 + unexplained $U8 + judgment $J8 is not changed $C8N"
  [ "$C8N" = "$HN" ] && [ "$ACC8" = "$HN" ] \
    || stop "8c_RESULT.txt: changed $C8N, accounted $ACC8; handoff_8c.tsv has $HN changed games"
  # PLAN.md section 6, change 3: "in lookahead" needs both halves (the code gate, and v2 finding the condition inside the
  # bots' search at the first differing tick) and the revert check reproducing the old choice and scores; a game failing
  # either is a stop, so it cannot be among the lookahead verdicts
  [ "$BHOF" = "$L8" ] && [ "$BH8" = "$L8" ] || stop "8c_RESULT.txt: both_halves $BH8 of $BHOF, but every one of the $L8 lookahead games must meet both halves (PLAN.md section 6, change 3)"
  [ "$RVOF" = "$L8" ] && [ "$RV8" = "$L8" ] || stop "8c_RESULT.txt: revert $RV8 of $RVOF reproduced, but every one of the $L8 lookahead games must be (PLAN.md section 6, change 3)"
  [ "$C3A" = "$HC3" ] && [ "$C3T" = "$HC3" ] \
    || stop "8c_RESULT.txt: condition3 $C3A, traced $C3T; both must be handoff_8c.tsv's $HC3 offgate_only games"
  # the changed games with no round-2 counter at all, or only round 1's or a superset's: each traced, and counted in the
  # records (a game with every counter 0 was "must be identical" in the last plan's mechanic check; the reading that admits
  # it when explained in lookahead is the coordinator's, recorded before sitting 2)
  [ "$NNA" = "$HNONE" ] && [ "$NNT" = "$HNONE" ] \
    || stop "8c_RESULT.txt: none $NNA, traced $NNT; both must be handoff_8c.tsv's $HNONE games of category none (no counter fired)"
  [ "$NOA" = "$HOTHER" ] && [ "$NOT" = "$HOTHER" ] \
    || stop "8c_RESULT.txt: other_only $NOA, traced $NOT; both must be handoff_8c.tsv's $HOTHER games of category other_only"
  [ "$A8" = "$((U8 + J8))" ] || stop "8c_RESULT.txt: dustin $A8, but unexplained $U8 + judgment $J8 = $((U8 + J8)) games need his word"
  git cat-file -e "$C8S^{commit}" 2> /dev/null || stop "8c_RESULT.txt names the 8c result ${C8S:0:7}, which is not here (Fetch origin)"
  if [ "$A8" -gt 0 ]; then NEED_WORD+="8c_RESULT.txt has $A8 games for him (unexplained $U8, judgment $J8; 8c_DECISION.md); "; fi
  echo "8c: $C8LINE"
fi
if [ -n "$NEED_WORD" ]; then   # a judgment call (or a game the rule left unexplained): the pin waits for his word (PLAN.md section 6)
  if [ $SKIP8C = 1 ]; then echo "CHECK: NOTE the pin will wait for Dustin's word: ${NEED_WORD%; }"
  else
    git cat-file -e "HEAD:$REL/8c_DECISION.md" 2> /dev/null || stop "a judgment call waits for Dustin's word (${NEED_WORD%; }), and 8c_DECISION.md is not committed"
    git diff --quiet HEAD -- "$REL/8c_DECISION.md" || stop "8c_DECISION.md differs from its commit"
    [ -n "${PIN_DUSTIN:-}" ] || stop "a judgment call waits for Dustin's word: ${NEED_WORD%; }. With his word, recorded verbatim in 8c_DECISION.md, run with PIN_DUSTIN='<his words>'"
    # his words, as given to the pin, must be the ones on record (whitespace aside): an exported or paraphrased value is not
    pd=$(printf '%s' "$PIN_DUSTIN" | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')
    dd=$(git show "HEAD:$REL/8c_DECISION.md" | tr -s '[:space:]' ' ')
    [ -n "$pd" ] && [[ $dd == *"$pd"* ]] || stop "PIN_DUSTIN's words are not in the committed 8c_DECISION.md: record his words there verbatim first (spaces and line breaks aside), commit it, then run the pin with the same words"
  fi
fi
if [ -n "${PIN_DUSTIN:-}" ]; then
  PIN_DUSTIN=${PIN_DUSTIN//$'\n'/ }
  note "PIN DUSTIN: $PIN_DUSTIN$( [ -n "$NEED_WORD" ] || echo " (no judgment call waits for his word; noted only)")"
fi
printf '%s\n' "$C8LINE" > "$TMP/8c_line.txt"   # update_manifest_rules.py reads the counts from it

# --- gate 4: the tested programs (programs.sha256 and watch.sha256 still verify; the copies come from that build) ------
sha256sum -c --quiet "$O/programs.sha256" > "$TMP/c.out" 2>&1 || stop "programs.sha256 no longer verifies: $(head -n 3 "$TMP/c.out" | tr '\n' ' ')"
sha256sum -c --quiet "$O/watch.sha256" > "$TMP/c.out" 2>&1 || stop "watch.sha256 no longer verifies: $(head -n 3 "$TMP/c.out" | tr '\n' ' ')"
declare -A WHERE
for n in "${PROGS[@]}"; do
  w=deckgym; [ $n = deckgym ] || w=examples/$n
  lines=$(awk -v w="/engine/target/release/$w" 'length($0) > 66 {p = substr($0, 67)
    if (length(p) >= length(w) && substr(p, length(p) - length(w) + 1) == w) print substr($0, 1, 64) "\t" p}' "$O/programs.sha256")
  [ -n "$lines" ] && [ "$(printf '%s\n' "$lines" | wc -l)" = 1 ] || stop "programs.sha256 doesn't name one build of $n"
  WANT[$n]=${lines%%$'\t'*}; WHERE[$n]=${lines#*$'\t'}
  [[ ${WANT[$n]} =~ ^[0-9a-f]{64}$ ]] || stop "programs.sha256's $n line has no sha256"
  grep -qE "^[0-9TZ:-]+ sha256 ${WANT[$n]} $n \(new, plain\)$" "$STATUS" || stop "PIN_STATUS.txt has no 'sha256 ${WANT[$n]:0:8}... $n (new, plain)' line"
  other=$( { grep -E "^[0-9TZ:-]+ sha256 [0-9a-f]{64} $n \(new, plain\)$" "$STATUS" || true; } | { grep -v " ${WANT[$n]} " || true; } | head -n 1)
  [ -z "$other" ] || stop "PIN_STATUS.txt also names another plain $n build: ${other:0:120}"
done
[ "${WANT[deckgym]}" != "${OLDSUM[deckgym]}" ] || stop "programs.sha256's deckgym is $OLD_NAME's own ($OLDPREL): the tested build is not the candidate's"
E=$(dirname -- "${WHERE[deckgym]}")
[ "${WHERE[legality_scan]}" = "$E/examples/legality_scan" ] && [ "${WHERE[goldfish]}" = "$E/examples/goldfish" ] \
  || stop "programs.sha256 names the three programs in different builds"
case $E in */engine-rules2-"${C:0:7}"/engine/target/release) ;;
  *) stop "programs.sha256 names a build in $E, not sitting 1's folder engine-rules2-${C:0:7} (ADAPTATION_SPEC 1.1)";; esac
if [ -n "${PIN_BUILD_DIR:-}" ]; then E="$PIN_BUILD_DIR/engine/target/release"; [ -f "$E/deckgym" ] || E="$PIN_BUILD_DIR"; fi
src_of() { if [ "$1" = deckgym ]; then echo "$E/deckgym"; else echo "$E/examples/$1"; fi; }
for n in "${PROGS[@]}"; do
  [ -f "$(src_of $n)" ] && [ "$(sha "$(src_of $n)")" = "${WANT[$n]}" ] || stop "$(src_of $n) is not the tested $n (sitting 1's build)"
done
BUILT_AT=$(grep -E "^[0-9TZ:-]+ sha256 ${WANT[deckgym]} deckgym \(new, plain\)$" "$STATUS" | head -n 1 | cut -d' ' -f1)
echo "programs: $E (deckgym ${WANT[deckgym]:0:8}, legality_scan ${WANT[legality_scan]:0:8}, goldfish ${WANT[goldfish]:0:8}: programs.sha256's, never rebuilt; recorded $BUILT_AT); watch.sha256 verifies"

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
[ -f "$R/$OLDPREL/SHA256SUMS" ] || stop "$OLDPREL/SHA256SUMS is missing (the official programs, $OLD_NAME)"
( cd "$R/$OLDPREL" && sha256sum -c --quiet SHA256SUMS ) > /dev/null 2>&1 || stop "the official programs ($OLDPREL/, $OLD_NAME) changed"
for n in "${PROGS[@]}"; do
  grep -qxE "${OLDSUM[$n]} [ *]$n" "$R/$OLDPREL/SHA256SUMS" || stop "$OLDPREL/SHA256SUMS doesn't give $n as switch2.env's ${OLDSUM[$n]:0:8}"
done
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
    strength) busy+="$pid: $args (the strength harness: a kx3 run); ";;   # the 2-day combined run was one (no pid file)
  esac
done
# and a process of a long run $HOME/runs/watch.list names (its PATTERN or its CHAIN script, which starts the PATTERN's program
# again after a school-morning wait), a watcher (run_watch.sh, watch_all.sh) aside
WL=${KX_RUNS_DIR:-$HOME/runs}/watch.list
if [ -r "$WL" ]; then
  while IFS='|' read -r wnm _ _ wpat wchain _; do
    case $wnm in ''|'#'*) continue;; esac
    for x in "$wpat" "$wchain"; do
      [ -n "$x" ] || continue
      for q in $(pgrep -f -- "$(printf '%s' "$x" | sed 's/[][\.*^$+?(){}|]/\\&/g')" 2> /dev/null || true); do
        [ "$q" != "$$" ] || continue
        cl=$(tr '\0' ' ' 2> /dev/null < "/proc/$q/cmdline" || true)
        case $cl in ''|*run_watch.sh*|*watch_all.sh*|*pin_rules.sh*) continue;; esac
        busy+="$q: ${cl:0:120} (watch.list's $wnm); "
      done
    done
  done < "$WL"
fi
# and a live launch_detached run in this working copy (a kx3, strength, slow-report or trace run reads the manifest or
# engine/ too; rl/strength/launch_detached.sh's own test of "alive"); the pin's own run, if started that way, is not one
RUNS=${KX_RUNS_DIR:-$HOME/runs}
for f in "$RUNS"/*.pid; do
  [ -e "$f" ] || continue
  rpid=$(sed -n 's/^pid=//p' "$f"); rst=$(sed -n 's/^starttime=//p' "$f"); rpg=$(sed -n 's/^pgid=//p' "$f"); rtag=$(sed -n 's/^tag=//p' "$f")
  [ -z "$rtag" ] || [ "${LAUNCH_DETACHED_RUN:-}" != "$rtag" ] || continue
  live=0
  if [ -n "$rpid" ] && [ -d "/proc/$rpid" ] && [ "$(awk '{print $22}' "/proc/$rpid/stat" 2> /dev/null)" = "$rst" ]; then live=1
  elif [ -n "$rpg" ] && [ -n "$rtag" ]; then
    for q in $(pgrep -g "$rpg" 2> /dev/null || true); do
      if grep -qxzF "LAUNCH_DETACHED_RUN=$rtag" "/proc/$q/environ" 2> /dev/null; then live=1; break; fi
    done
  fi
  [ $live = 1 ] || continue
  rdir=$(sed -n 's/^dir=//p' "$f"); rcmd=$(sed -n 's/^cmd=//p' "$f")
  case "$rdir/ $rcmd" in "$R"/*|*"$R/"*) busy+="launch_detached run $(basename -- "$f" .pid) ($rdir: ${rcmd:0:80}); ";; esac
done
[ -z "$busy" ] || stop "a screen, floor, calibration, sitting, engine or detached run in this working copy is going; the pin would change its files mid-run: $busy"

# --- gate 7: step 11's merge, computed off-tree and checked before anything changes --------------------------------------
MERGED=0
if git merge-base --is-ancestor "$RC" "$H"; then          # a re-run after step 11
  # the merge this script recorded: its MERGED line, or its MERGING line (written just before main moved, so a kill
  # between main's move and the MERGED line is recognised too); the latest one that main contains
  for m in $( { grep -oE "(MERGED|MERGING) ${RC:0:7} into main as [0-9a-f]{40}" "$STATUS" 2> /dev/null || true; } | cut -d' ' -f6 | tac); do
    if git merge-base --is-ancestor "$m" "$H" 2> /dev/null; then M=$m; break; fi
  done
  [ -n "$M" ] || stop "main already contains P ${RC:0:7}, but not through a merge this script recorded"
  [ "$(git rev-parse "$M^2")" = "$RC" ] || stop "the recorded merge ${M:0:7}'s second parent is not P"
  [ "$(git rev-parse "$H:engine")" = "$RTREE" ] || stop "main contains P, but its engine/ changed since the recorded merge ${M:0:7}"
  T=$(git rev-parse "$M^{tree}"); BASE=$(git rev-parse "$M^1"); MERGED=1; HOW="already merged as ${M:0:7} (a re-run)"
else
  [ "$(git rev-parse "$H:engine")" = "$MAIN_ENGINE" ] || stop "main's engine/ is not tree ${MAIN_ENGINE:0:7} ($OLD_NAME's, the candidate's base)"
  git merge-base --is-ancestor "$MAIN_C" "$H" || stop "main does not contain ${MAIN_C:0:7}, the candidate's first parent"
  git diff --quiet "$MAIN_C" "$H" -- engine/ || stop "engine/ changed on main since ${MAIN_C:0:7}: $(git diff --name-only "$MAIN_C" "$H" -- engine/ | tr '\n' ' ')"
  # ADAPTATION_SPEC 1.10: P's branch has records in this same folder (early_warning_8b/, tightened_rule.py, ...); a file of
  # the same name on main or here with other bytes would clash with the merge
  clash=""
  while IFS= read -r -d '' rec; do
    meta=${rec%%$'\t'*}; f=${rec#*$'\t'}; pb=${meta##* }
    hb=$(git rev-parse -q --verify "$H:$f" 2> /dev/null || true)
    if [ -n "$hb" ]; then [ "$hb" = "$pb" ] || clash+="$f (main's is not P's); "
    elif [ -e "$f" ] || [ -L "$f" ]; then
      wb=$(git hash-object -- "$f" 2> /dev/null || true); [ "$wb" = "$pb" ] || clash+="$f (here, not P's); "
    fi
  done < <(git ls-tree -r -z "$RC" -- "$REL/")
  [ -z "$clash" ] || stop "P's records under $REL/ clash with files of the same name (the reserved names): $clash"
  out=$(git merge-tree --write-tree "$H" "$RC") || stop "merging P into main ${H:0:7} has conflicts: $(echo "$out" | tail -n +2 | tr '\n' ' ')"
  T=$(echo "$out" | head -n 1); BASE=$H; HOW="a fresh merge commit of P into main ${H:0:7}, made off-tree"
fi
TE=$(git rev-parse "$T:engine")
[ "$TE" = "$RTREE" ] || stop "the merge's engine/ is not P's tree ${RTREE:0:7} (the built candidate's); it differs in: $(git diff-tree -r --name-only "$RTREE" "$TE" | tr '\n' ' ')"
got=$(git diff --no-renames --name-status "$BASE" "$T" -- . ':(exclude)rl/results/' | LC_ALL=C sort)
want=$(printf '%s\n' "${ALLOWED_NS[@]}" | LC_ALL=C sort)
[ "$got" = "$want" ] || stop "outside rl/results/ the merge changes: $(echo "$got" | tr '\t\n' ' ;') (expected exactly allowed_engine_files.tsv's ${#ALLOWED[@]} engine files, each with its status)"
git diff --quiet "$BASE" "$T" -- engine/src/players/ || stop "the merge changes engine/src/players/"
cargo=$(git diff --name-only "$BASE" "$T" | grep -E '(^|/)Cargo\.(lock|toml)$' || true)
[ -z "$cargo" ] || stop "the merge changes $(echo $cargo)"
git diff --no-renames --name-status "$BASE" "$T" > "$TMP/merge.ns"
git diff --no-renames --name-only "$BASE" "$T" > "$TMP/merge.paths"
gone=$(awk -F'\t' '$1 != "A" && $1 != "M" {print $1 " " $2}' "$TMP/merge.ns")
[ -z "$gone" ] || stop "the merge would delete or retype files on main: $(echo "$gone" | tr '\n' ';')"
NRES_A=$(awk -F'\t' '$1 == "A" && $2 ~ /^rl\/results\// {n++} END {print n + 0}' "$TMP/merge.ns")
RES_M=$(awk -F'\t' '$1 == "M" && $2 ~ /^rl\/results\// {print $2}' "$TMP/merge.ns")
NRES_M=$(printf '%s' "$RES_M" | grep -c . || true)
RES_M_LINE=$(printf '%s\n' "$RES_M" | paste -sd' ' -)
NE_A=$(printf '%s\n' "${ALLOWED_NS[@]}" | grep -c '^A' || true); NE_M=$((${#ALLOWED[@]} - NE_A))
NSRC=$(printf '%s\n' "${ALLOWED[@]}" | grep -c '^engine/src/' || true); NTEST=$((${#ALLOWED[@]} - NSRC))
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
echo "merge: $HOW; engine/ = P's tree ${RTREE:0:7} = the built candidate's; outside rl/results/ exactly allowed_engine_files.tsv's ${#ALLOWED[@]} engine files ($NE_M modified, $NE_A added); players/, Cargo.lock and Cargo.toml unchanged; under rl/results/ $NRES_A files added, $NRES_M existing records changed (${RES_M_LINE:-none}); nothing deleted"

# --- gate 8: steps 12-14 built in a scratch folder, and step 15's plan ---------------------------------------------------
build_docs() {  # fill dir base: docs/'s drafts checked and filled into dir; the targets in $TMP/docs.tsv and docs.list
  [ -d "$D" ] || stop "no $DREL/: the reviewed documents (PLAN.md steps 11-14) are not in yet"
  [ -s "$D/DOCS.sha256" ] && [ -s "$D/BASE.sha256" ] || stop "$DREL/ needs DOCS.sha256 and BASE.sha256 (README.md here)"
  local ok=1
  python3 - "$D" "$R" "$3" "$1" "$2" "$TMP/merge.paths" "$REL" "$FRREL" "${REQUIRED_DOCS[*]}" "$PREL" "$SEED_NEW" > "$TMP/docs.tsv" 2> "$TMP/docs.err" <<'EOF' || ok=0
import hashlib, os, re, subprocess, sys
D, R, base, full, out, mpaths, rel, frrel, required, prel, seed_new = sys.argv[1:12]
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
    if p.startswith(("engine/", ".git/", rel + "/pin/")) or (p.startswith(prel + "/") and p != prel + "/README.md"):
        die(f"{p}: not a document the pin may install")
    if p in merged:
        die(f"{p}: step 11's merge changes this path, so no draft can be based on it")
missing = [p for p in required.split() if p not in docs]
if missing:
    die("docs/ has no draft for " + " ".join(missing) + " (PLAN.md steps 11-14)")
ls = subprocess.run(["git", "-C", R, "ls-tree", "-z", base, "--"] + sorted(docs), capture_output=True, check=True).stdout
blob = {}
for rec in ls.split(b"\0"):
    if rec:
        meta, path = rec.split(b"\t", 1)
        blob[path.decode()] = meta.split()[2].decode()
sha = lambda b: hashlib.sha256(b).hexdigest()
gitsha = lambda b: hashlib.sha1(b"blob %d\0" % len(b) + b).hexdigest()
own = (rel + "/", frrel + "/")   # the pin's own folders: committed with the pin as they are, so a BASE hash is enough
seed_row = f"{int(seed_new):,}".encode()   # 23,300,000,000: START_HERE's row for this switch's new seeds (PLAN section 5)
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
    if p in ("START_HERE.md", "CLAUDE.md") and prel.encode() not in filled:
        die(f"{p}'s draft doesn't name {prel} (the official engine line)")
    if p == "START_HERE.md" and not any(seed_row in line for line in filled.splitlines()):
        die(f"START_HERE.md's draft has no line holding {seed_row.decode()} (this switch's seed row, kept)")
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
engine_readme() {  # merge-commit out: $PREL/README.md (used when docs/ has no draft of it)
  python3 - "$1" "$2" "$C" "$MAIN_C" "$RC" "$RTREE" "$PREL" "$OLDPREL" "$OLD_NAME" "$REL" "$CREF" \
    "${WANT[deckgym]}" "${WANT[legality_scan]}" "${WANT[goldfish]}" "$BUILT_AT" \
    "$C8N" "${C8S:0:7}" "$B8" "$L8" "$U8" "$J8" "$C3A" "${PIN_DUSTIN:-}" \
    "${PH[7c]}" "${PH[8b]}" "${PH[8]}" "${PH[9]}" "${#ALLOWED[@]}" "$NSRC" "$NTEST" "${SWITCHES[*]}" "$NNA" "$NOA" <<'EOF'
import sys
assert len(sys.argv) == 34, sys.argv
(m, out, c, main_c, p, ptree, prel, oldprel, oldname, rel, cref, s_gym, s_scan, s_gold, built_at,
 n, s7, b, l, u, j, c3, dustin, ph7c, ph8b, ph8, ph9, nf, nsrc, ntest, switches, nnone, nother) = sys.argv[1:34]
date = prel[len("rl/engine-"):]
built = built_at[:10] + " (" + built_at[11:16] + " UTC)" if len(built_at) >= 16 else built_at
res = "../" + rel[len("rl/"):]          # rl/results/... seen from rl/engine-<date>/
old = "../" + oldprel[len("rl/"):]
g = lambda x: f"{int(x):,}"
ul = (f"; {g(u)} the rule left unexplained and {g(j)} judgment calls, each accepted by Dustin at the pin (`{res}/8c_DECISION.md`)"
      if int(u) + int(j) else "; none unexplained, and no judgment call")
sw = ", ".join(f"`{s}`" for s in switches.split())
t = f"""# The official engine from {date}: main-{m[:7]} (rules switch 2)

- **Programs:** `deckgym`, `legality_scan`, `goldfish`; sha256 in `SHA256SUMS` and `project_manifest.json`. Linux (WSL or the cloud). Committed with the executable bit (git mode 100755), so a Linux clone runs them as they are.
  - `deckgym` {s_gym}
  - `legality_scan` {s_scan}
  - `goldfish` {s_gold}
  - These are the programs sitting 1 built and tested, copied and never rebuilt (`{res}/programs.sha256`).
- **Built** in WSL on {built} from one `git archive` of {c[:7]}, the merge candidate: main {main_c[:7]} plus P {p[:7]} (the final engine commit of `claude/coin-prevention-round2`), whose `engine/` tree is {ptree[:7]}. `cargo build --release --locked`, `--example legality_scan`, `--example goldfish` (`{res}/PIN_STATUS.txt`, `build.log`).
  - Main's merge commit {m} (main plus P) has an `engine/` byte-identical to it (tree {ptree[:7]}, checked by the pin). Main had moved since the candidate, outside `engine/`, so the pin made main's merge commit itself. {c[:7]} is kept only on the laptop (`{cref}`; not a branch); elsewhere, build from main's merge commit, the same `engine/`.
  - The watch build (`legality_scan` with the round-2 counters) is evidence only. It is not pinned.
- **What it is:** rules switch 2, on {oldname}'s engine (`{old}/`). The engine now follows the plain card text in three more places, plus one text fix:
  - **The round-2 coin package.** Seven more attacks flip Meowth's, Togekiss's, Bastiodon's and Hisuian Goodra's coin when their damage lands: Wild Swing, Wellspring Dance, Tornado Shot, Double Splash, Triple Bombardment, Mischievous Ring and Litter, and Mega Kangaskhan ex's second punch. Any other attack's plain queued hit flips it too. The coin and Guts also answer an attack's damage to its own side's Pokémon, and Perish Body flips for a queued hit. Will works for a Confused attacker and on a block coin ("if tails, that attack doesn't happen"), and Victory Star is offered after that coin's heads. Each Ariados adds 1 to the Retreat Cost. Luxury Coin works only on the player's own Stadium, and a Fossil can't be played under an Item lock.
  - **Fossils are Item cards** at the seven other places that read "Item card" (P3).
  - **Return damage set up by an attack takes Weakness** (+20): Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat and Shell Trap (`rules/02` §2). Bounded Field doubles it (×2). A Tool's or an Ability's return damage (Rocky Helmet, Rough Skin) stays flat.
  - **P1:** Gholdengo's caveat text (no game changes).
  - {nf} engine files change, {nsrc} source and {ntest} test files (`{res}/allowed_engine_files.tsv`).
- **Revert switches.** The engine reads these environment variables, each once per process: {sw}. None is set by default, so every rule above is on. Set one and the program is another engine: never set one in a recorded run. They exist for step 8c's revert check (turning a rule off must bring the old move back).
- **What didn't change: the players.** `engine/src/players/`, `Cargo.lock` and `Cargo.toml` are unchanged. km3 stays the working pilot, on both sides of the screen and the floor.
- **Evidence** (`{res}/`; every replay matched by pairing and game number, counts asserted, on every recorded field):
  - Step 7: 151,240 identity games equal to their references (kta3 fresh and development deals, km3, k3 and kp3 on scoreboard v3's 45 cells, kog3, kq3, kpr3, and kd3 as a gate). So scoreboard v3's 45 cells are re-verified at this engine for k3 and kp3.
  - Step 7b: the watch build's 28,000 table games equal the plain ones; every round-2 exact counter read 0, and `offgate_plain_attack_damage`, `offgate_by_attack` and `offgate_confused_attack` fired.
  - Step 7c: Dustin's decks 02, 06, 08, 14 and 10 and draft D's root and amended pages replayed through `floor.py`, and the watch rows (Oct 1's 32 and 24 new), 20,160 games; the named deck 10 v t-weezing watch row: {ph7c}.
  - Step 8b: the early-warning rows on the old, new and watch builds, 2,800 games: {ph8b}; equal to the cloud's rows.
  - Step 8: the carriers and the Will rows, 54,750 games: {ph8}.
  - Step 9: km3's coverage baselines, 74,500 games: the 80 B2e pairings without Ariados, Scizor and the second lists equal; the 16 Trap Territory pairings (32-39 and 80-87): {ph9}. They are km3's new B2e reference for those rows (Dustin, Oct 9, question 3).
  - Step 10: `deckgym simulate`, goldfish `--coverage` and `run_screen` under km3 equal.
  - Step 8c: all {g(n)} changed games accounted for: {g(b)} on the board, {g(l)} in look-ahead with both halves and the revert check reproducing the old choice and scores{ul}; traced among them, {g(c3)} CONDITION 3 games (only round 2's off-gate counters fired), {g(nnone)} with no counter at all and {g(nother)} with only round 1's or a superset's counters (`{res}/8c_RESULT.txt`; result {s7}).
- **Approved:** Dustin, Oct 9: "1-3 sure" (go, "update if everything passes", with the two stricter checks; the scope; the new reference games) and "Alright it is fine to use the laptop over the weekend" (`{res}/RELEASE_PACKAGE.md`, `PLAN.md`).{(' At the pin, on 8c: "' + dustin + '".') if dustin else ''}
- **History:** `{old}/` ({oldname}) and earlier are kept unchanged, with their hashes in the manifest's historical releases.
"""
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
  python3 "$MANIFEST_PY" "$fill" "$C" "$RC" "$dir/$PREL/SHA256SUMS" "$TMP/manifest_base.json" "$dir/project_manifest.json" \
    "$PREL" "$TMP/8c_line.txt" "${mf[@]}" > "$TMP/manifest.out" 2>&1 \
    || { cat "$TMP/manifest.out" >&2; stop "update_manifest_rules.py refuses (printed above; nothing changed)"; }
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
fr_gate() {  # step 15's plan is there (or drafted in docs/), and nothing of a run is
  local bad
  [ -f "$FR/PLAN.md" ] || grep -qx "$FRREL/PLAN.md" "$TMP/docs.list" \
    || stop "$FRREL/PLAN.md must be there, or drafted in docs/: step 15's plan is committed with the pin, before any of its games"
  if [ -d "$FR" ]; then
    bad=$(cd "$FR" && find . -mindepth 1 \( -type d -printf '%P/\n' -o ! -type d -printf '%P\n' \) | grep -vxE "$FR_FILES" || true)
    [ -z "$bad" ] || stop "$FRREL/ holds more than its plan and scripts ($(echo $bad)): no game may come before the plan's commit"
  fi
}
# the hand-off to step 15 (PLAN.md step 15, section 0's table; RELEASE_PACKAGE.md, "The order"); noted before PIN DONE so
# the pin commit carries it, and printed at the end
STEP15="STEP 15 HANDOFF (PLAN.md step 15; after the push; each new page goes to Dustin beside its old one, and a new failure or judgment call stops and goes to him): 1. the floor's pre-use re-check under km3, as $FRREL/PLAN.md says (about 13,400 games); 2. deck 12's new page (1,920); 3. D's victini-passive page, remade as on Oct 2 (its copy rebuilt from floor_copy.diff and run through run_copy.py on D's first list; 1,920); 4. brew 07's and brew 09's new pages (2 x 1,920; until then their conclusions stay provisional, Dustin Oct 7, PLAN.md section 0); 5. D's root and amended pages (text) from step 7c's replays ($REL/floor_7c/D_root/ and D_amended/); 6. deck 10's new page only if step 7c's page check reported a t-weezing difference ($REL/floor_7c/10/; STATUS.txt's STEP 7c line). Then kx3 rebuilt on the new engine and checked, and the slow report's program rebuilt, its self-checks replayed, and pinned again (RELEASE_PACKAGE.md)"
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
echo "steps 12-14 built in a scratch folder: the programs as tested; the manifest builds ($OLD_NAME to the history); current_engine.py resolves the new deckgym; $PREL/README.md from $(grep -qx "$PREL/README.md" "$TMP/docs.list" && echo "docs/" || echo "the pin's own text"); ${#FILES[@]} files in all"
echo "documents (each against its BASE and DOCS hash; main's HEAD fills the placeholders in this scratch build):"; awk -F'\t' '{printf "  %s: %s, %s placeholder(s)\n", $1, ($2 == "new" ? "a new file" : "replaces its drafted base"), $4}' "$TMP/docs.tsv"
[ -z "$nd" ] || echo "NOTE: no draft in docs/ for $nd(not in PLAN.md steps 11-14's list; not a stop)"
[ -n "$NOTED_EXTRA" ] || echo "NOTE: the files holding Sonnet's note 8 and km3's new B2e reference for the 16 rows (question 3a) are not named yet (switch2.env PIN_NOTED_EXTRA: the pin itself refuses to start without them)"
echo "step 15: $FRREL/PLAN.md $( [ -f "$FR/PLAN.md" ] && echo "is there" || echo "is drafted in docs/"), and no game file"
echo "the pin commit also carries $(grep -c . "$TMP/sweep0.tsv" || true) uncommitted file(s) of $REL and $FRREL (docs/'s drafts excluded; each must be unchanged at the commit):"
awk -F'\t' '{printf "  %s%s\n", $1, ($2 == "gone" ? " (deleted: the pin stops)" : "")}' "$TMP/sweep0.tsv"
echo "$STEP15"
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
  ALLOWED_LIST=$(for x in "${ALLOWED_NS[@]}"; do printf '  %s %s\n' "${x%%$'\t'*}" "${x#*$'\t'}"; done)
  cat > "$TMP/merge_msg" <<MSG
Merge claude/coin-prevention-round2 at P ${RC:0:7} into main: rules switch 2 (round-2 coins, Fossils as Items, return damage takes Weakness)

engine/ is P's tree ${RTREE:0:7}, byte-identical to the built and replayed candidate ${C:0:7} (main ${MAIN_C:0:7} + P;
kept on the laptop at $CREF). Main has moved since, outside engine/.
Against main ${H:0:7}, the first parent, outside rl/results/ only the ${#ALLOWED[@]} engine files of
rl/results/engine_switch_rules2_2026-10/allowed_engine_files.tsv change ($NE_M modified, $NE_A added):
$ALLOWED_LIST
engine/src/players/, Cargo.lock and Cargo.toml do not, and nothing is deleted; under rl/results/ $NRES_A files are
added and $NRES_M existing records changed. Made off-tree by rl/results/engine_switch_rules2_2026-10/pin/pin_rules.sh
(git merge-tree, git commit-tree); main moved to it with git update-ref from the value the pin read. The pin commit
follows (PLAN.md steps 12-14).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
  M=$(git "${GIT_ID[@]}" commit-tree "$T" -p "$H" -p "$RC" -F "$TMP/merge_msg") || stop "git commit-tree failed; nothing merged"
  [ "$(git rev-parse "$M^{tree}")" = "$T" ] && [ "$(git rev-parse "$M^1")" = "$H" ] && [ "$(git rev-parse "$M^2")" = "$RC" ] \
    && ! git rev-parse -q --verify "$M^3" > /dev/null || stop "the merge commit ${M:0:7} is not (main, P) with the checked tree; nothing merged"
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
  git_retry update-ref -m "pin_rules.sh: merge P ${RC:0:7} into main (rules switch 2)" refs/heads/main "$M" "$H" \
    || stop "main moved during the pin, or its ref stayed locked ($(git_err)); nothing merged"
  PHASE=merged
  [ "$(git rev-parse HEAD)" = "$M" ] || stop "HEAD is not ${M:0:7} after git update-ref"
  note "MERGED ${RC:0:7} into main as $M ($HOW); engine/ = P's tree ${RTREE:0:7}, byte-identical to the built candidate ${C:0:7}'s; outside rl/results/ exactly allowed_engine_files.tsv's ${#ALLOWED[@]} engine files ($NE_M modified, $NE_A added); players/, Cargo.lock and Cargo.toml unchanged; under rl/results/ $NRES_A files added and $NRES_M existing records changed (${RES_M_LINE:-none}); nothing deleted; ${#MW[@]} files written in the working copy"
  left=$(git status --porcelain --untracked-files=no -- "${MPATHS[@]}" || true)
  [ -z "$left" ] || note "NOTE: after the merge, git status shows changes in its paths: $(echo "$left" | head -n 5 | tr '\n' ';')"
else
  [ "$(git rev-parse HEAD)" = "$H" ] || stop "main moved during the pin's checks (now $(git rev-parse --short HEAD)): run the pin again"
fi
PIN_PARENT=$(git rev-parse HEAD)

# --- steps 12-14, built in a scratch folder first: nothing else in the working copy changes until every file is made ---
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
note "MANIFEST available_release = main-${M:0:7} ($PREL/deckgym); $OLD_NAME in the history, superseded; current_engine.py resolves it; the screen and the floor stay km3"
note "DOCS: $(awk -F'\t' '{printf "%s (%s; draft %s, installed %s, %s placeholder(s)); ", $1, ($2 == "new" ? "new" : "replaced its BASE"), $5, $6, $4}' "$TMP/docs.tsv")$PREL/README.md from $(grep -qx "$PREL/README.md" "$TMP/docs.list" && echo "docs/" || echo "pin_rules.sh's own text")"

# --- the pin commit: from a private index, so exactly the pin's files go in (the programs executable), and main moves
# --- to it only if main is still where the pin left it (git update-ref with the old value)
[ "$(sha "$SELF")" = "$SELF_SHA" ] && [ "$(sha "$MANIFEST_PY")" = "$MPY_SHA" ] || stop "pin_rules.sh or update_manifest_rules.py changed during the run"
XI="$TMP/index"
GIT_INDEX_FILE="$XI" git read-tree "$PIN_PARENT" || stop "git read-tree (private index)"
GIT_INDEX_FILE="$XI" git add -- "${FOLDERS[@]}" || stop "git add of this switch's folder and $FRREL (private index)"
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
note "$STEP15"
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
if [ "$A8" -gt 0 ]; then
  PIN_8C="$(fmt "$U8") the rule left unexplained and $(fmt "$J8") judgment calls, each accepted by Dustin at the pin
  (8c_DECISION.md): \"$PIN_DUSTIN\""
elif [ -n "$NEED_WORD" ]; then
  PIN_8C="none unexplained and no judgment call in 8c; Dustin's word at the pin (8c_DECISION.md) on ${NEED_WORD%; }: \"$PIN_DUSTIN\""
else
  PIN_8C="none unexplained and no judgment call"
fi
cat > "$TMP/pin_msg" <<MSG
Pin rules switch 2 (main-${M:0:7}): round-2 coins, Fossils as Items, return damage takes Weakness

Dustin, Oct 9: "1-3 sure" (go, "update if everything passes", with the two stricter checks; the scope; the new
reference games) and "Alright it is fine to use the laptop over the weekend".
- engine/: P ${RC:0:7}'s tree ${RTREE:0:7} (main's merge ${M:0:7}), byte-identical to the built and replayed candidate
  ${C:0:7}; ${#ALLOWED[@]} engine files change ($NSRC source, $NTEST tests); engine/src/players/, Cargo.lock and
  Cargo.toml unchanged; the engine reads ${#SWITCHES[@]} revert switches (DECKGYM_*), none set by default
- identity, all equal: 151,240 games (step 7), the watch build's 28,000 with the round-2 counters (7b), the floor pages
  and watch rows of 7c, km3's coverage outside the 16 Trap Territory pairings (9), the command line, goldfish and the
  screen (10)
- the named rows: 7c (deck 10 v t-weezing) ${PH[7c]}; 8b ${PH[8b]}; 8 ${PH[8]}; 9 (the 16 pairings) ${PH[9]};
  $(fmt "$C8N") in all, each accounted for in 8c (8c_RESULT.txt, result ${C8S:0:7}): $(fmt "$B8") on the board,
  $(fmt "$L8") in look-ahead with both halves and the revert check, $PIN_8C; traced among them, $(fmt "$C3A") CONDITION 3
  games, $(fmt "$NNA") with no counter at all and $(fmt "$NOA") with only round 1's or a superset's counters
- the programs in $PREL/ (mode 100755) with SHA256SUMS and README.md; the manifest ($OLD_NAME kept as history,
  superseded); the documents ($(echo "${DOCS_T[@]}")); this switch's record; step 15's plan ($FRREL/),
  committed before any of its games. km3 stays the working pilot.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
MSG
X=$(git "${GIT_ID[@]}" commit-tree "$tree" -p "$PIN_PARENT" -F "$TMP/pin_msg") || stop "git commit-tree (the pin commit)"
[ "$(git symbolic-ref -q HEAD || true)" = refs/heads/main ] || stop "the working copy left main during the pin"
[ "$(git rev-parse HEAD)" = "$PIN_PARENT" ] || stop "main moved during the pin (now $(git rev-parse --short HEAD)); nothing committed"
PIDX=1   # from here an undo also unstages the pin's paths
git_retry reset -q "$X" -- "${COMMIT_PATHS[@]}" || stop "putting the pin's files in the shared index failed ($(git_err))"
[ "$(git rev-parse HEAD)" = "$PIN_PARENT" ] || stop "main moved while the shared index was set (now $(git rev-parse --short HEAD)); nothing committed"
git_retry update-ref -m "pin_rules.sh: pin rules switch 2 (main-${M:0:7})" refs/heads/main "$X" "$PIN_PARENT" \
  || stop "main moved during the pin, or its ref stayed locked ($(git_err)); nothing committed"
PHASE=done
[ "$(git rev-parse HEAD)" = "$X" ] || stop "HEAD is not the pin commit ${X:0:7} after git update-ref"
changed=$(git status --porcelain --untracked-files=no -- "${COMMIT_PATHS[@]}" || true)
# docs/'s drafts (copies of START_HERE.md, CLAUDE.md and RUN5 with placeholders) leave the repository, so no session reads
# them as instructions and GitHub Desktop doesn't offer them for a commit; BASE.sha256, DOCS.sha256 and CHANGES.md stay
DRAFTS_TO="$HOME/pin_rules2_drafts_${M:0:7}"; nmv=0
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
echo "After the push: tell Sonnet and the cloud sessions that the official engine is main-${M:0:7} ($PREL/), rules switch 2; the working pilot stays km3; no DECKGYM_* variable is set in a recorded run. Take main before any screen, floor, calibration, kx3 or slow-report run."
echo "Then step 15 (also in PIN_STATUS.txt): $STEP15"
echo "docs/'s drafts are not committed: $nmv of ${#DOCS_T[@]} moved out of the repository to $DRAFTS_TO$( [ "$nmv" = "${#DOCS_T[@]}" ] || echo "; move the rest out of $DREL/ by hand, and never commit them")."
git --no-pager log -1 --stat --format='%h %s' > "$TMP/log" || true; head -n 40 "$TMP/log"
}
main "$@"

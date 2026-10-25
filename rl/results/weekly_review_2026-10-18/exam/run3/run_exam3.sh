#!/bin/bash
# Exam run 3 (PREREG_RUN3.md, addenda 1-8): km3 played FRESH on exam v2 (frozen at 6e5fab0c, K19) with the registered seeds, then the frozen-7
# judge (Gemini 4 Argon on Vertex AI), then the formal compare on run 3 alone (95%), the POOLED primary with run 2 (97.5%) and the secondaries.
#   MODE=dry bash run_exam3.sh   checks the kit: clone, freeze identity, harness tests, inputs, plan lists, prompt sizes, the batch path with a
#                                MOCKED judge on 3 points (and missing_ids on a row taken out), pool_runs.py's tests. It plays no km3 and makes
#                                no comparison (run 1's dry runs played km3 on the exam; that is not repeated).
#   MODE=live KIT_COMMIT=<sha> bash run_exam3.sh   the run, from the pinned kit commit. km3 only inside the night window (02:00-12:50Z).
#                                Anything the registration does not cover stops it (STATUS STOP), before any workaround.
# Scheduling (K20, the coordinator's decision of Oct 25, registered before any run 3 row; not a frozen judge setting): 2 workers; a task that
# frozen-7's budget_judge.py records as NOT SENT (never issued as an HTTP request) may go in up to 3 later passes, 120 s apart; anything
# ambiguous counts as sent and gets run 2's A4 single resend; a decision with a row is never asked again (next_pass.py). The primary's $40
# cap covers all its passes; never-sent tasks left after pass 3 stop the run. The repeat follows the same rule.
set -euo pipefail
MODE=${MODE:-dry}
readonly WORKERS=2 LATER_PASSES=3 PASS_WAIT=120
REF=judge-prompt-frozen-7
REF_COMMIT=712593a1b77b203ec23fb15589c158c6bddb2bf2
FREEZE_COMMIT=6e5fab0c2069f782ca43c7670384003a1a47edba    # exam v2, frozen (PREREG_RUN3 addendum 8, K19)
EXAM_BRANCH=sonnet/exam-2026-10-19
RUN3=rl/results/weekly_review_2026-10-18/exam/run3
RUN2=rl/results/weekly_review_2026-10-18/exam/run2/live-20261021T2000Z
RUN1=rl/results/weekly_review_2026-10-18/exam/run1
SEEDS=25101000001,25101000002,25101000003                 # registered in START_HERE (Oct 21) before any run 3 row: 25,101,000,000 + s
PROJECT=project-45583ef0-ed57-426c-bde                     # Dustin's Google Cloud project id (not a secret)
TOTAL_USD=75                                               # K8: the ledger for the primary and the repeat
PRIMARY_CAP=40                                             # K8: the primary's cap, all its passes included; the repeat takes what remains
NO_CHOICE_LIMIT=0.20                                       # run 2's A3: above it, a non-pass reads "inconclusive about skill"
WINREPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
OUT=$HOME/exam_run3/$MODE-$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$OUT"
LOG=$OUT/run.log
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
fail() { log "STOP: $*"; echo "STOP" > "$OUT/STATUS"; exit 1; }
trap 'rc=$?; [ -e "$OUT/STATUS" ] || { log "STOP: unexpected exit $rc (line $LINENO)"; echo STOP > "$OUT/STATUS"; }' EXIT
[ -e "$HOME/credit_work/PAUSE" ] && fail "PAUSE file present"
log "mode=$MODE ref=$REF freeze=$FREEZE_COMMIT seeds=$SEEDS workers=$WORKERS later_passes=$LATER_PASSES wait=${PASS_WAIT}s out=$OUT"
log "this script: sha256 $(sha256sum "$0" | cut -c1-64)"
if [ "$MODE" = live ]; then
  [ -n "${KIT_COMMIT:-}" ] || fail "live needs KIT_COMMIT (the pinned kit commit)"
  [ -n "${VERTEX_API_KEY:-}" ] && [ ${#VERTEX_API_KEY} -gt 20 ] || fail "no Vertex key in the environment"
fi

# 1. clean sparse clone of the judge tag; the exam branch for the frozen inputs, the kit and run 2's report
URL=$(git -C "$WINREPO" remote get-url origin) || fail "no origin URL"
git clone -q --filter=blob:none --no-checkout "$URL" "$OUT/repo" || fail "clone"
cd "$OUT/repo"
git fetch -q origin --tags || fail "fetch tags"
git fetch -q origin $EXAM_BRANCH || fail "fetch the exam branch"
git sparse-checkout init --cone
git sparse-checkout set rl/ai_judge lib rl/results/pause_games_decisions_2026-10-02/harness rl/results/pause_games_new_2026-10-13/v2/decks decks/dustin
git checkout -q --detach "$REF" || fail "checkout $REF"
[ "$(git rev-parse HEAD)" = $REF_COMMIT ] || fail "the tag is not $REF_COMMIT"
log "judge ref $(git rev-parse HEAD)"
git merge-base --is-ancestor "$FREEZE_COMMIT" FETCH_HEAD || fail "the freeze commit is not on the exam branch"
EXAM_TIP=$(git rev-parse FETCH_HEAD)
if [ "$MODE" = live ]; then
  [ "$EXAM_TIP" = "$KIT_COMMIT" ] || fail "the exam tip $EXAM_TIP is not the pinned kit commit $KIT_COMMIT"
fi
git diff --quiet "$FREEZE_COMMIT" "$EXAM_TIP" -- "$RUN3/pool_runs.py" "$RUN3/test_pool_runs.py" "$RUN3/frozen_2026-10-25" "$RUN3/decks" \
  || fail "pool_runs.py, its test, the frozen files or the decks changed after the freeze"
log "exam tip $EXAM_TIP (the pooling script, the frozen files and the decks equal the freeze's)"

# 2. the freeze identity (sources, prompt fingerprint, settings, engine tree, both executables), then the harness's tests (mocks and fixtures)
cd rl/ai_judge
python3 freeze_identity.py --check > "$OUT/freeze_check.txt" 2>&1 || { cat "$OUT/freeze_check.txt" | tee -a "$LOG"; fail "freeze_identity.py --check failed"; }
grep -q 0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762 FROZEN.json || fail "prompt fingerprint not in FROZEN.json"
log "freeze_identity --check: pass"
env -u VERTEX_PROJECT -u VERTEX_API_KEY -u ANTHROPIC_API_KEY -u GEMINI_API_KEY python3 -B -m unittest discover -s tests > "$OUT/tests.txt" 2>&1 \
  || { tail -n 5 "$OUT/tests.txt" | tee -a "$LOG"; fail "the harness's tests failed"; }
log "harness tests: $(grep -E '^Ran ' "$OUT/tests.txt") $(tail -n 1 "$OUT/tests.txt")"
LEDGER=$OUT/spend_ledger.json
# every file the run reads from the branch, fetched NOW, before any spend
kit() { git -C "$OUT/repo" show "$EXAM_TIP:$1" > "$2" || fail "git show $1"; }
for f in prep_inputs_v2.py report_only.py next_pass.py pool_runs.py test_pool_runs.py; do kit "$RUN3/$f" "$OUT/$f"; done
kit "$RUN1/relabel_repeat.py" "$OUT/relabel_repeat.py"
kit "$RUN1/categories.py" "$OUT/categories.py"
mkdir -p "$OUT/run2" "$OUT/run3"
kit "$RUN2/report_primary.json" "$OUT/run2/report_primary.json"
kit "$RUN2/in/eligibility.json" "$OUT/run2/eligibility.json"
kit "$RUN3/frozen_2026-10-25/exam_v2_2026-10-25.json" "$OUT/exam_v2.json"
AN="$OUT/repo/rl/ai_judge/analysis.py"

# 3. inputs from the freeze commit, checked against K19
python3 -B "$OUT/prep_inputs_v2.py" "$OUT/repo" "$FREEZE_COMMIT" "$EXAM_TIP" "$REF" "$OUT/in" > "$OUT/prep.txt" 2>&1 || { cat "$OUT/prep.txt" | tee -a "$LOG"; fail "prep_inputs_v2.py"; }
cat "$OUT/prep.txt" | tee -a "$LOG"
P=$OUT/in/positions.json; D=$OUT/in/decks; R=$OUT/in/references.json; E=$OUT/in/eligibility.json
IDS=$(tr '\n' ' ' < "$OUT/in/ids.txt")
NIDS=$(grep -c . "$OUT/in/ids.txt") || fail "no ids"
[ "$NIDS" = 258 ] || fail "$NIDS ids, not 258"

# 4. plan lists (none may be capped) and the prompt sizes (nothing sent): the estimate at the introductory price, against the primary cap
python3 judge.py plans --positions "$P" --decks "$D" --ids $IDS > "$OUT/plans.txt" 2>&1 || fail "plan lister"
grep -i -q 'capped: *true\|capped=True\| True ' "$OUT/plans.txt" && fail "a plan list is capped"
python3 judge.py judge --provider gemini-vertex --positions "$P" --decks "$D" --ids $IDS > "$OUT/prompt_sizes.txt" 2>&1 || fail "prompt build"
python3 - "$OUT/prompt_sizes.txt" "$PRIMARY_CAP" > "$OUT/estimate.txt" <<'EOF' || { cat "$OUT/estimate.txt" | tee -a "$LOG"; fail "estimate above the primary cap"; }
import re, sys
txt = open(sys.argv[1]).read(); limit = float(sys.argv[2])
toks = [int(x.replace(',', '')) for x in re.findall(r'(\d[\d,]*) ?(?:prompt )?tokens', txt)] or [int(x) for x in re.findall(r'"prompt_tokens_estimate": (\d+)', txt)]
n = len(toks); tin = sum(toks)
est = tin * 2 / 1e6 + n * 3000 * 10 / 1e6   # $2 / $10 per Mtok (introductory price), about 3,000 output tokens a call (thinking included)
print(f'estimate: {n} prompts, {tin} input tokens (estimated), about ${est:.2f} per judge run at $2/$10 (the primary cap: ${limit})')
sys.exit(0 if (n and est <= limit) else 1)
EOF
cat "$OUT/estimate.txt" | tee -a "$LOG"

judge_run() {  # $1 out file, $2 tag, $3 run cap, rest: ids. frozen-7's budget_judge.py, one ledger for every run
  local out=$1 tag=$2 cap=$3; shift 3
  local n=$#
  if [ "$MODE" = live ]; then
    python3 budget_judge.py --positions "$P" --decks "$D" --ids "$@" --max-calls "$n" --repeat 1 --workers "$WORKERS" --tag "$tag" --out "$out" \
      --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$cap" --vertex-project "$PROJECT" --live
  else
    env -u VERTEX_API_KEY python3 budget_judge.py --positions "$P" --decks "$D" --ids "$@" --max-calls "$n" --repeat 1 --workers "$WORKERS" \
      --tag "MOCK_DRY_RUN_$tag" --out "$out" --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$cap" --mock
  fi
}
# what the ledger holds now: accrued plus calls in flight (a killed run's in-flight calls are charged when the ledger is next opened)
spent() { python3 -c "import json,sys,os; p=sys.argv[1]; d=json.load(open(p)) if os.path.exists(p) else {}; print(float(d.get('accrued_usd',0))+float(d.get('in_flight_usd',0) or 0))" "$LEDGER"; }
missing_ids() {  # $1 the ids file (any whitespace); rest: result files. Ids with no row at all; exits 1 on any error
  python3 - "$@" <<'EOF'
import json, sys
ids = open(sys.argv[1]).read().split()
have = set()
for f in sys.argv[2:]:
    try:
        with open(f) as fh:
            for line in fh:
                if line.strip():
                    have.add(json.loads(line)['position'])
    except FileNotFoundError:
        pass
print(' '.join(i for i in ids if i not in have))
EOF
}
# a batch (K20): pass 0 sends every decision; each later pass (at most LATER_PASSES, PASS_WAIT apart) sends what next_pass.py allows: a decision
# without a row that was never issued, or issued once (A4's single resend); never one with a row. The primary's passes share PRIMARY_CAP.
# Each pass is logged with tasks asked, sent, NOT SENT, failed, still without a row, and spend. Writes $OUT/$1.files and $OUT/$1.passes.
batch() {  # $1 name, $2 tag, $3 ids file (one id per line), $4 cap mode: primary | repeat
  local name=$1 tag=$2 idf=$3 capmode=$4 rc files="" passargs="" k=0 cap a0 s0 f stdout sendf stats
  a0=$(spent) || fail "$name: the ledger cannot be read"
  sendf=$idf
  while :; do
    f="$OUT/$name.jsonl"; stdout="$OUT/$name.stdout"
    [ $k -gt 0 ] && { f="$OUT/${name}_pass$k.jsonl"; stdout="$OUT/${name}_pass$k.stdout"; }
    if [ "$capmode" = primary ]; then
      cap=$(python3 -c "import sys; print(round(float(sys.argv[1]) - (float(sys.argv[2]) - float(sys.argv[3])), 6))" "$PRIMARY_CAP" "$(spent)" "$a0") || fail "$name: cap"
    else
      cap=$TOTAL_USD
    fi
    python3 -c "import sys; sys.exit(0 if float(sys.argv[1]) > 0 else 1)" "$cap" || fail "$name: the primary cap is spent before pass $k"
    s0=$(spent); rc=0
    judge_run "$f" "$tag$([ $k -gt 0 ] && echo _pass$k || true)" "$cap" $(cat "$sendf") > "$stdout" 2>&1 || rc=$?
    grep -q 'usage:\|error: argument' "$stdout" && fail "$name pass $k: budget_judge usage error (see $(basename "$stdout"))"
    [ "$rc" = 1 ] && fail "$name pass $k: budget_judge exit 1 (see $(basename "$stdout"))"
    [ -e "$f" ] && files="$files $f"
    passargs="$passargs --pass $sendf $stdout"
    stats=$(python3 -B "$OUT/next_pass.py" --ids "$idf" --out "$OUT/${name}_send$((k + 1)).txt" --results $files $passargs) || fail "$name: next_pass.py failed"
    log "$name pass $k: exit $rc, run cap \$$cap, spend \$$(python3 -c "import sys; print(round(float(sys.argv[1]) - float(sys.argv[2]), 4))" "$(spent)" "$s0"); $stats; $(grep 'call(s) returned' "$stdout" || true)"
    [ -s "$OUT/${name}_send$((k + 1)).txt" ] || break      # nothing left to send (complete, or every missing decision issued twice)
    [ $k -ge $LATER_PASSES ] && break                      # no 4th later pass
    k=$((k + 1)); sendf="$OUT/${name}_send$k.txt"
    log "$name: pass $k in ${PASS_WAIT}s, sending $(grep -c . "$sendf")"
    sleep "$PASS_WAIT"
  done
  echo "$files" > "$OUT/$name.files"
  echo "$k" > "$OUT/$name.passes"
}
compare() {  # $1 out report, $2 judge repeats, rest: result files
  local out=$1 reps=$2; shift 2
  set +e
  python3 judge.py compare --positions "$P" --decks "$D" --results "$@" --ids $IDS --bots km3,judge --seeds "$SEEDS" --judge-repeats "$reps" \
    --references "$R" --eligibility "$E" --on-problem fail --failed-judge-rows miss --out "$out" > "$out.stdout" 2>&1
  local rc=$?
  set -e
  echo $rc
}

if [ "$MODE" = dry ]; then
  # the batch path with the mocked judge on 3 points (no key read, nothing sent; mock rows are refused by the formal path)
  head -n 3 "$OUT/in/ids.txt" > "$OUT/dry_ids.txt"
  batch judge_dry dry "$OUT/dry_ids.txt" primary
  ND=$(cat $(cat "$OUT/judge_dry.files") | grep -c .) || ND=0
  [ "$ND" = 3 ] && [ "$(cat "$OUT/judge_dry.passes")" = 0 ] || fail "dry: the mock made $ND rows in $(cat "$OUT/judge_dry.passes") resend pass(es); expected 3 rows, no resend"
  # missing_ids: one row taken out must come back, alone; nothing taken out must give nothing
  head -n 2 "$OUT/judge_dry.jsonl" > "$OUT/dry_two_rows.jsonl"
  M1=$(missing_ids "$OUT/dry_ids.txt" "$OUT/dry_two_rows.jsonl"); M0=$(missing_ids "$OUT/dry_ids.txt" "$OUT/judge_dry.jsonl")
  [ "$M1" = "$(sed -n 3p "$OUT/dry_ids.txt")" ] && [ -z "$M0" ] || fail "dry: missing_ids gave '$M1' and '$M0'"
  tr '\n' ' ' < "$OUT/dry_ids.txt" > "$OUT/dry_ids_oneline.txt"
  [ "$(missing_ids "$OUT/dry_ids_oneline.txt" "$OUT/judge_dry.jsonl")" = "" ] || fail "dry: missing_ids reads a one-line ids file wrongly"
  # next_pass.py on fixtures: ids a b c d; pass 0: a row for a, b TASK FAILED, c NOT SENT, d no line (ambiguous: sent)
  X=$OUT/np; mkdir -p "$X"; printf 'a\nb\nc\nd\n' > "$X/ids"; cp "$X/ids" "$X/s0"
  printf '{"position": "a"}\n' > "$X/r0"
  printf 'TASK FAILED b repeat 0: API error 429\nNOT SENT c repeat 0: a call failed: no further call is sent\n' > "$X/o0"
  python3 -B "$OUT/next_pass.py" --ids "$X/ids" --out "$X/s1" --results "$X/r0" --pass "$X/s0" "$X/o0" > "$X/j1"
  [ "$(tr '\n' ' ' < "$X/s1")" = "b c d " ] || fail "dry: next_pass pass 1 sends '$(tr '\n' ' ' < "$X/s1")', not 'b c d'"
  # pass 1: b fails again, c NOT SENT again, d gets a row -> only c (never issued) may go again; b was issued twice
  printf '{"position": "d"}\n' > "$X/r1"; printf 'TASK FAILED b repeat 0: timeout\nNOT SENT c repeat 0: a call failed\n' > "$X/o1"
  python3 -B "$OUT/next_pass.py" --ids "$X/ids" --out "$X/s2" --results "$X/r0" "$X/r1" --pass "$X/s0" "$X/o0" --pass "$X/s1" "$X/o1" > "$X/j2"
  [ "$(tr '\n' ' ' < "$X/s2")" = "c " ] || fail "dry: next_pass pass 2 sends '$(tr '\n' ' ' < "$X/s2")', not 'c'"
  log "dry judge: 3 mock rows, no later pass; missing_ids and next_pass.py fixture checks pass ($(cat "$X/j2")); ledger \$$(spent)"
  # test_pool_runs.py finds run 2's report beside its own folder (exam/run2/live-20261021T2000Z): the same layout
  T=$OUT/pooltest/exam; mkdir -p "$T/run3" "$T/run2/live-20261021T2000Z/in"
  cp "$OUT/pool_runs.py" "$OUT/test_pool_runs.py" "$T/run3/"
  cp "$OUT/run2/report_primary.json" "$T/run2/live-20261021T2000Z/report_primary.json"
  cp "$OUT/run2/eligibility.json" "$T/run2/live-20261021T2000Z/in/eligibility.json"
  env -u VERTEX_API_KEY python3 -B "$T/run3/test_pool_runs.py" "$AN" > "$OUT/test_pool_runs.txt" 2>&1 \
    || { tail -n 5 "$OUT/test_pool_runs.txt" | tee -a "$LOG"; fail "test_pool_runs failed"; }
  log "pool_runs tests: $(grep -E '^Ran ' "$OUT/test_pool_runs.txt") $(tail -n 1 "$OUT/test_pool_runs.txt")"
  echo "DRY DONE" > "$OUT/STATUS"
  log "dry done: no km3 played, no comparison made"
  exit 0
fi

# 5. km3, played fresh on the registered seeds, inside the night window
HM=$(date -u +%H%M)
{ [ $((10#$HM)) -ge 200 ] && [ $((10#$HM)) -le 1250 ]; } || fail "km3 outside the night window (02:00-12:50Z): now ${HM}Z"
nice -n 19 python3 judge.py run --bot km3 --positions "$P" --decks "$D" --ids $IDS --seeds "$SEEDS" --out "$OUT/km3.jsonl" > "$OUT/km3.stdout" 2>&1 || fail "km3 run"
NK=$(grep -c . "$OUT/km3.jsonl") || NK=0
[ "$NK" = $((NIDS * 3)) ] || fail "km3 rows: $NK, not $((NIDS * 3))"
log "km3 rows: $NK (seeds $SEEDS), sha256 $(sha256sum "$OUT/km3.jsonl" | cut -c1-16)"

# 6. the judge, primary: ONE call per decision, within the primary cap
batch judge_primary run3_primary "$OUT/in/ids.txt" primary
PRIMARY_FILES=$(cat "$OUT/judge_primary.files")
PM=$(missing_ids "$OUT/in/ids.txt" $PRIMARY_FILES) || fail "missing_ids (primary)"
[ -z "$PM" ] || fail "primary incomplete after its passes (K20): $(echo $PM | wc -w) decision(s) without a row: no verdict; stopped for the coordinator"
NJ=$(cat $PRIMARY_FILES | grep -c .) || NJ=0
[ "$NJ" = "$NIDS" ] || fail "judge primary rows: $NJ, not $NIDS (a decision asked twice?)"
log "judge primary rows: $NJ in $(cat "$OUT/judge_primary.passes") resend pass(es); ledger \$$(spent) of \$$TOTAL_USD"

# 7. the formal comparison, run 3 alone (failed judge rows count as misses; any other problem fails the batch)
cp "$OUT/in/eligibility.json" "$OUT/run3/eligibility.json"
RC=$(compare "$OUT/report_primary.json" 1 "$OUT/km3.jsonl" $PRIMARY_FILES)
log "compare (primary, run 3 alone) exit $RC"
[ "$RC" = 0 ] || fail "formal comparison (primary) exit $RC: see report_primary.json(.stdout)"
cp "$OUT/report_primary.json" "$OUT/run3/report_primary.json"
python3 - "$OUT/report_primary.json" "$NO_CHOICE_LIMIT" "$OUT/a3_run3.json" <<'EOF' | tee -a "$LOG"
import json, sys
r = json.load(open(sys.argv[1])); lim = float(sys.argv[2])
f = r['failed_judge_rows']
n, d = f.get('n_primary_decisions'), f.get('n_judge_decisions_primary')
share = (n / d) if (isinstance(n, int) and d) else None
over = share is not None and share > lim
json.dump({'failed_primary_decisions': n, 'judge_decisions_primary': d, 'share': share, 'over_20pct': over,
           'models_returned': r['run'].get('judge_models_returned')}, open(sys.argv[3], 'w'), indent=1)
print(f'failed judge replies (no choice, scored as misses): {n} of {d} primary decisions ({share:.1%} )' if share is not None else f'failed judge replies: {f}')
print(f'models returned: {r["run"].get("judge_models_returned")}; over 20%: {over}')
EOF
A3_OVER=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['over_20pct'])" "$OUT/a3_run3.json")

# 8. the PRIMARY: runs 2 + 3 pooled at 97.5% (section 4), and the chance-ending stratum (section 5). No API call.
set +e
python3 -B "$OUT/pool_runs.py" --analysis "$AN" --run "$OUT/run2/report_primary.json" "$OUT/run2/eligibility.json" --run "$OUT/run3/report_primary.json" "$OUT/run3/eligibility.json" \
  --confidence 0.975 --out "$OUT/pooled_primary.json" > "$OUT/pooled_primary.stdout" 2>&1; PRC=$?
python3 -B "$OUT/pool_runs.py" --analysis "$AN" --run "$OUT/run2/report_primary.json" "$OUT/run2/eligibility.json" --run "$OUT/run3/report_primary.json" "$OUT/run3/eligibility.json" \
  --confidence 0.975 --stratum "$OUT/in/stratum_chance_pooled.txt" --out "$OUT/pooled_chance_stratum.json" > "$OUT/pooled_chance_stratum.stdout" 2>&1; SRC=$?
python3 -B "$OUT/pool_runs.py" --analysis "$AN" --run "$OUT/run3/report_primary.json" "$OUT/run3/eligibility.json" \
  --confidence 0.95 --stratum "$OUT/in/stratum_chance_run3.txt" --out "$OUT/run3_chance_stratum.json" > "$OUT/run3_chance_stratum.stdout" 2>&1; S3=$?
set -e
log "pooled primary exit $PRC (3 = pooling OFF by section 7): $(tail -n 1 "$OUT/pooled_primary.stdout")"
log "pooled chance stratum exit $SRC; run 3 chance stratum exit $S3"
[ "$PRC" = 0 ] || [ "$PRC" = 3 ] || fail "pool_runs.py exit $PRC: see pooled_primary.stdout"
[ "$PRC" = 3 ] && log "NOTE: pooling is OFF (section 7): run 3 is reported as a new series; stopping before the repeat for the coordinator" && { echo "STOP" > "$OUT/STATUS"; exit 1; }
[ "$A3_OVER" = True ] && { log "STOP: failed judge replies above 20% (A3): the primary is computed; stopped before the repeat, for the coordinator"; echo STOP > "$OUT/STATUS"; exit 1; }

# 9. the separate sensitivity repeat (what the ledger has left), then its own comparison (descriptive)
batch judge_repeat_raw run3_repeat "$OUT/in/ids.txt" repeat
REPEAT_RAW=$(cat "$OUT/judge_repeat_raw.files")
[ -n "$REPEAT_RAW" ] && cat $REPEAT_RAW > "$OUT/judge_repeat_raw_all.jsonl" || : > "$OUT/judge_repeat_raw_all.jsonl"
python3 "$OUT/relabel_repeat.py" "$OUT/judge_repeat_raw_all.jsonl" "$OUT/judge_repeat.jsonl" > "$OUT/relabel.txt" 2>&1 || log "relabel failed (sensitivity only): $(tail -n 1 "$OUT/relabel.txt")"
REPEAT_MISSING=$(missing_ids "$OUT/in/ids.txt" $REPEAT_RAW) || REPEAT_MISSING="(missing_ids failed)"
RC2=skipped
if [ -z "$REPEAT_MISSING" ]; then
  RC2=$(compare "$OUT/report_sensitivity.json" 2 "$OUT/km3.jsonl" $PRIMARY_FILES "$OUT/judge_repeat.jsonl")
  log "compare (sensitivity) exit $RC2"
else
  log "repeat INCOMPLETE after its passes (K20): $(echo $REPEAT_MISSING | wc -w) decision(s) without a row: no sensitivity comparison; the run ends STOP after the descriptive steps"
fi

# 10. descriptive: categories, the REPORT-ONLY lines (K19), spend; manifest
python3 "$OUT/categories.py" "$OUT/report_primary.json" "$OUT/in/categories.json" "$OUT/by_category.json" > "$OUT/categories.txt" 2>&1 || log "category breakdown failed (descriptive only)"
python3 -B "$OUT/report_only.py" "$OUT/exam_v2.json" "$OUT/km3.jsonl" $PRIMARY_FILES --out "$OUT/report_only.json" > "$OUT/report_only.txt" 2>&1 || log "report-only lines failed (descriptive only)"
python3 judge.py spend $PRIMARY_FILES $REPEAT_RAW > "$OUT/spend.txt" 2>&1 || true
python3 - "$OUT" "$REF" "$SEEDS" "$RC" "$RC2" "$PRC" "$SRC" "$S3" "$TOTAL_USD" "$PRIMARY_CAP" "$WORKERS" "$LATER_PASSES" "${KIT_COMMIT:-}" <<'EOF'
import hashlib, json, os, sys
out, ref, seeds, rc, rc2, prc, src, s3, total, pcap, workers, later, kit = sys.argv[1:14]
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
files = [f for f in sorted(os.listdir(out)) if os.path.isfile(os.path.join(out, f))]
m = {'mode': 'live', 'judge_ref': ref, 'kit_commit': kit, 'km3_rows': 'played fresh, frozen baseline (judge.py run --bot km3), nice 19, in the night window',
     'seeds': seeds, 'workers': int(workers), 'later_passes_max': int(later), 'passes': {n: open(os.path.join(out, f'{n}.passes')).read().strip()
                                                                                       for n in ('judge_primary', 'judge_repeat_raw') if os.path.exists(os.path.join(out, f'{n}.passes'))},
     'compare_primary_exit': int(rc), 'compare_sensitivity_exit': rc2, 'pooled_primary_exit': int(prc), 'pooled_stratum_exit': int(src),
     'run3_stratum_exit': int(s3), 'a3_run3': json.load(open(os.path.join(out, 'a3_run3.json'))), 'failed_judge_rows': 'miss (run 2 A3)',
     'relabel': 'judge_repeat.jsonl = the repeat rows with repeat 0 -> 1 (run 1 relabel_repeat.py); nothing else changed',
     'spend_bound': f'frozen-7 budget_judge.py: each call reserved at its worst case before sending; ledger ${total} over the primary and the repeat, primary cap ${pcap} (all its passes)',
     'files': {f: h(os.path.join(out, f)) for f in files}, 'inputs': json.load(open(os.path.join(out, 'in', 'inputs_manifest.json')))}
json.dump(m, open(os.path.join(out, 'run_manifest.json'), 'w'), indent=1)
print('manifest written')
EOF
if [ -n "$REPEAT_MISSING" ]; then echo "STOP" > "$OUT/STATUS"; log "STOP: the repeat is incomplete (K20); everything else is written"; exit 1; fi
echo "DONE" > "$OUT/STATUS"
log "done: $(tail -n 1 "$OUT/spend.txt")"

#!/bin/bash
# Exam run 3 (PREREG_RUN3.md, addenda 1-8): km3 played FRESH on exam v2 (frozen at 6e5fab0c, K19) with the registered seeds, then the frozen-7
# judge (Gemini 4 Argon on Vertex AI), then the formal compare on run 3 alone (95%), the POOLED primary with run 2 (97.5%) and the secondaries.
#   MODE=dry bash run_exam3.sh   checks the kit only: clone, freeze identity, harness tests, inputs, plan lists, prompt sizes, a MOCKED judge on 3
#                                points, pool_runs.py's tests. It plays no km3 and makes no comparison (run 1's dry runs played km3 on the
#                                exam; that is not repeated).
#   MODE=live bash run_exam3.sh  the run. km3 only inside the night window (02:00-12:50Z). Stops (STATUS STOP) on anything the registration does
#                                not cover, before any workaround.
set -euo pipefail
MODE=${MODE:-dry}
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
PRIMARY_CAP=40                                             # K8: the primary run's cap (its one resend included); the repeat takes what remains
NO_CHOICE_LIMIT=0.20                                       # run 2's A3: above it, a non-pass reads "inconclusive about skill" (stop and ask)
WINREPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
OUT=$HOME/exam_run3/$MODE-$(date -u +%Y%m%dT%H%MZ)
mkdir -p "$OUT"
LOG=$OUT/run.log
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
fail() { log "STOP: $*"; echo "STOP" > "$OUT/STATUS"; exit 1; }
[ -e "$HOME/credit_work/PAUSE" ] && fail "PAUSE file present"
log "mode=$MODE ref=$REF freeze=$FREEZE_COMMIT seeds=$SEEDS out=$OUT"
if [ "$MODE" = live ]; then
  [ -n "${VERTEX_API_KEY:-}" ] && [ ${#VERTEX_API_KEY} -gt 20 ] || fail "no Vertex key in the environment"
fi

# 1. clean sparse clone of the judge tag; the exam branch for the frozen inputs, the kit and run 2's report
URL=$(git -C "$WINREPO" remote get-url origin)
git clone -q --filter=blob:none --no-checkout "$URL" "$OUT/repo"
cd "$OUT/repo"
git fetch -q origin --tags
git fetch -q origin $EXAM_BRANCH
git sparse-checkout init --cone
git sparse-checkout set rl/ai_judge lib rl/results/pause_games_decisions_2026-10-02/harness rl/results/pause_games_new_2026-10-13/v2/decks decks/dustin
git checkout -q --detach "$REF"
[ "$(git rev-parse HEAD)" = $REF_COMMIT ] || fail "the tag is not $REF_COMMIT"
log "judge ref $(git rev-parse HEAD)"
git merge-base --is-ancestor "$FREEZE_COMMIT" FETCH_HEAD || fail "the freeze commit is not on the exam branch"
EXAM_TIP=$(git rev-parse FETCH_HEAD)
log "exam tip $EXAM_TIP"

# 2. the freeze identity (sources, prompt fingerprint, settings, engine tree, both executables), then the harness's tests (mocks and fixtures)
cd rl/ai_judge
python3 freeze_identity.py --check > "$OUT/freeze_check.txt" 2>&1 || { cat "$OUT/freeze_check.txt" | tee -a "$LOG"; fail "freeze_identity.py --check failed"; }
grep -q 0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762 FROZEN.json || fail "prompt fingerprint not in FROZEN.json"
log "freeze_identity --check: pass"
env -u VERTEX_PROJECT -u VERTEX_API_KEY -u ANTHROPIC_API_KEY -u GEMINI_API_KEY python3 -B -m unittest discover -s tests > "$OUT/tests.txt" 2>&1 \
  || { tail -n 5 "$OUT/tests.txt" | tee -a "$LOG"; fail "the harness's tests failed"; }
log "harness tests: $(grep -E '^Ran ' "$OUT/tests.txt") $(tail -n 1 "$OUT/tests.txt")"
LEDGER=$OUT/spend_ledger.json
kit() { git -C "$OUT/repo" show "$EXAM_TIP:$RUN3/$1" > "$OUT/$(basename "$1")"; }
for f in prep_inputs_v2.py report_only.py pool_runs.py test_pool_runs.py; do kit "$f"; done
git -C "$OUT/repo" show "$EXAM_TIP:$RUN1/relabel_repeat.py" > "$OUT/relabel_repeat.py"
git -C "$OUT/repo" show "$EXAM_TIP:$RUN1/categories.py" > "$OUT/categories.py"

# 3. inputs from the freeze commit, checked against K19
python3 -B "$OUT/prep_inputs_v2.py" "$OUT/repo" "$FREEZE_COMMIT" "$EXAM_TIP" "$REF" "$OUT/in" | tee -a "$LOG"
P=$OUT/in/positions.json; D=$OUT/in/decks; R=$OUT/in/references.json; E=$OUT/in/eligibility.json
IDS=$(tr '\n' ' ' < "$OUT/in/ids.txt")
NIDS=$(wc -l < "$OUT/in/ids.txt")
[ "$NIDS" = 258 ] || fail "$NIDS ids, not 258"

# 4. plan lists (none may be capped) and the prompt sizes (nothing sent): the estimate at the introductory price, against the primary cap
python3 judge.py plans --positions "$P" --decks "$D" --ids $IDS > "$OUT/plans.txt" 2>&1 || fail "plan lister"
grep -i -q 'capped: *true\|capped=True\| True ' "$OUT/plans.txt" && fail "a plan list is capped"
python3 judge.py judge --provider gemini-vertex --positions "$P" --decks "$D" --ids $IDS > "$OUT/prompt_sizes.txt" 2>&1 || fail "prompt build"
python3 - "$OUT/prompt_sizes.txt" "$PRIMARY_CAP" <<'EOF' | tee -a "$LOG" || fail "estimate above the primary cap"
import re, sys
txt = open(sys.argv[1]).read(); limit = float(sys.argv[2])
toks = [int(x.replace(',', '')) for x in re.findall(r'(\d[\d,]*) ?(?:prompt )?tokens', txt)] or [int(x) for x in re.findall(r'"prompt_tokens_estimate": (\d+)', txt)]
n = len(toks); tin = sum(toks)
est = tin * 2 / 1e6 + n * 3000 * 10 / 1e6   # $2 / $10 per Mtok (introductory price), about 3,000 output tokens a call (thinking included)
print(f'estimate: {n} prompts, {tin} input tokens (estimated), about ${est:.2f} per judge run at $2/$10 (the primary cap: ${limit})')
sys.exit(0 if (n and est <= limit) else 1)
EOF

judge_run() {  # $1 out file, $2 tag, $3 run cap, rest: ids. frozen-7's budget_judge.py, one ledger for every run
  local out=$1 tag=$2 cap=$3; shift 3
  local n=$#
  if [ "$MODE" = live ]; then
    python3 budget_judge.py --positions "$P" --decks "$D" --ids "$@" --max-calls "$n" --repeat 1 --workers 4 --tag "$tag" --out "$out" \
      --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$cap" --vertex-project "$PROJECT" --live
  else
    env -u VERTEX_API_KEY python3 budget_judge.py --positions "$P" --decks "$D" --ids "$@" --max-calls "$n" --repeat 1 --workers 4 --tag "MOCK_DRY_RUN_$tag" \
      --out "$out" --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$cap" --mock
  fi
}
accrued() { python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['accrued_usd'])" "$LEDGER" 2>/dev/null || echo 0; }
missing_ids() {  # $1 the ids file; rest: result files. Ids with no row at all (a call with no model reply; addendum A4)
  python3 - "$@" <<'EOF'
import json, sys
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
have = set()
for f in sys.argv[2:]:
    try:
        for line in open(f):
            if line.strip():
                have.add(json.loads(line)['position'])
    except FileNotFoundError:
        pass
print(' '.join(i for i in ids if i not in have))
EOF
}
# a batch: one run, then ONE resend of the ids with no row at all, into a new file on the same ledger (A4). Writes $OUT/$1.files.
batch() {  # $1 name, $2 tag, $3 ids file, $4 run cap ('primary': PRIMARY_CAP for both, the resend's cap reduced by what the first spent)
  local name=$1 tag=$2 idf=$3 capmode=$4 rc=0 files="$OUT/$1.jsonl" cap
  if [ "$capmode" = primary ]; then cap=$PRIMARY_CAP; else cap=$TOTAL_USD; fi
  local a0=$(accrued)
  judge_run "$OUT/$name.jsonl" "$tag" "$cap" $(cat "$idf") > "$OUT/$name.stdout" 2>&1 || rc=$?
  log "$name: exit $rc; $(grep 'call(s) returned' "$OUT/$name.stdout" || true)"
  [ "$rc" = 1 ] && fail "$name: budget_judge usage error (exit 1): see $name.stdout"
  local miss=$(missing_ids "$idf" "$OUT/$name.jsonl")
  if [ -n "$miss" ]; then
    local cap2=$cap
    if [ "$capmode" = primary ]; then cap2=$(python3 -c "import sys; print(round(float(sys.argv[1]) - (float(sys.argv[2]) - float(sys.argv[3])), 6))" "$PRIMARY_CAP" "$(accrued)" "$a0"); fi
    log "$name: $(echo $miss | wc -w) decision(s) without a row (no model reply): one resend (run cap \$$cap2)"
    python3 -c "import sys; sys.exit(0 if float(sys.argv[1]) > 0 else 1)" "$cap2" || fail "$name: the primary cap is spent before the resend"
    judge_run "$OUT/${name}_resend.jsonl" "${tag}_resend" "$cap2" $miss > "$OUT/${name}_resend.stdout" 2>&1 || true
    log "$name resend: $(grep 'call(s) returned' "$OUT/${name}_resend.stdout" || true)"
    [ -s "$OUT/${name}_resend.jsonl" ] && files="$files $OUT/${name}_resend.jsonl"
  fi
  echo "$files" > "$OUT/$name.files"
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
  # the mocked judge on 3 points (no key read, nothing sent; mock rows are refused by the formal path), and pool_runs.py's own tests
  head -n 3 "$OUT/in/ids.txt" | tr '\n' ' ' > "$OUT/dry_ids.txt"
  batch judge_dry dry primary "$OUT/dry_ids.txt" primary
  log "dry judge rows: $(cat $(cat "$OUT/judge_dry.files") | grep -c .) (mock)"
  # test_pool_runs.py finds run 2's report beside its own folder (exam/run2/live-20261021T2000Z): the same layout, from the exam tip
  T=$OUT/pooltest/exam; mkdir -p "$T/run3" "$T/run2/live-20261021T2000Z/in"
  cp "$OUT/pool_runs.py" "$OUT/test_pool_runs.py" "$T/run3/"
  git -C "$OUT/repo" show "$EXAM_TIP:$RUN2/report_primary.json" > "$T/run2/live-20261021T2000Z/report_primary.json"
  git -C "$OUT/repo" show "$EXAM_TIP:$RUN2/in/eligibility.json" > "$T/run2/live-20261021T2000Z/in/eligibility.json"
  env -u VERTEX_API_KEY python3 -B "$T/run3/test_pool_runs.py" "$OUT/repo/rl/ai_judge/analysis.py" > "$OUT/test_pool_runs.txt" 2>&1 \
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
NK=$(grep -c . "$OUT/km3.jsonl")
[ "$NK" = $((NIDS * 3)) ] || fail "km3 rows: $NK, not $((NIDS * 3))"
log "km3 rows: $NK (seeds $SEEDS), sha256 $(sha256sum "$OUT/km3.jsonl" | cut -c1-16)"

# 6. the judge, primary: ONE call per decision, within the primary cap
tr '\n' ' ' < "$OUT/in/ids.txt" > "$OUT/all_ids.txt"
batch judge_primary run3_primary "$OUT/all_ids.txt" primary
PRIMARY_FILES=$(cat "$OUT/judge_primary.files")
[ -z "$(missing_ids "$OUT/in/ids.txt" $PRIMARY_FILES)" ] || fail "primary incomplete after the one resend: $(missing_ids "$OUT/in/ids.txt" $PRIMARY_FILES | wc -w) decision(s) (A4: no verdict)"
log "judge primary rows: $(cat $PRIMARY_FILES | grep -c .); ledger \$$(accrued) of \$$TOTAL_USD"

# 7. the formal comparison, run 3 alone (failed judge rows count as misses; any other problem fails the batch)
RC=$(compare "$OUT/report_primary.json" 1 "$OUT/km3.jsonl" $PRIMARY_FILES)
log "compare (primary, run 3 alone) exit $RC"
[ "$RC" = 0 ] || fail "formal comparison (primary) exit $RC: see report_primary.json(.stdout)"
python3 - "$OUT/report_primary.json" "$NO_CHOICE_LIMIT" <<'EOF' | tee -a "$LOG" || fail "failed judge replies above the registered 20% (A3): stopped before the repeat, for the coordinator"
import json, sys
r = json.load(open(sys.argv[1])); lim = float(sys.argv[2])
f = r['failed_judge_rows']
n, d = len(f.get('rows') or []), f.get('n_judge_decisions_primary') or f.get('n_primary') or 0
share = n / d if d else 0
print(f'failed judge replies (no choice, scored as misses): {n} of {d} primary decisions ({share:.1%}); models returned {r["run"].get("judge_models_returned")}')
sys.exit(1 if share > lim else 0)
EOF

# 8. the separate sensitivity repeat (what the ledger has left), then its own comparison (descriptive)
batch judge_repeat_raw run3_repeat "$OUT/all_ids.txt" repeat
REPEAT_RAW=$(cat "$OUT/judge_repeat_raw.files")
cat $REPEAT_RAW > "$OUT/judge_repeat_raw_all.jsonl"
python3 "$OUT/relabel_repeat.py" "$OUT/judge_repeat_raw_all.jsonl" "$OUT/judge_repeat.jsonl" | tee -a "$LOG"
REPEAT_MISSING=$(missing_ids "$OUT/in/ids.txt" $REPEAT_RAW)
[ -z "$REPEAT_MISSING" ] || log "repeat INCOMPLETE (sensitivity only): $(echo $REPEAT_MISSING | wc -w) decision(s) without a row"
RC2=$(compare "$OUT/report_sensitivity.json" 2 "$OUT/km3.jsonl" $PRIMARY_FILES "$OUT/judge_repeat.jsonl")
log "compare (sensitivity) exit $RC2"

# 9. the PRIMARY: runs 2 + 3 pooled at 97.5% (section 4), and the chance-ending stratum (section 5), with run 3 alone beside it
git -C "$OUT/repo" show "$EXAM_TIP:$RUN2/report_primary.json" > "$OUT/run2_report_primary.json"
git -C "$OUT/repo" show "$EXAM_TIP:$RUN2/in/eligibility.json" > "$OUT/run2_eligibility.json"
AN="$OUT/repo/rl/ai_judge/analysis.py"
set +e
python3 -B "$OUT/pool_runs.py" --analysis "$AN" --run "$OUT/run2_report_primary.json" "$OUT/run2_eligibility.json" --run "$OUT/report_primary.json" "$E" \
  --confidence 0.975 --out "$OUT/pooled_primary.json" > "$OUT/pooled_primary.stdout" 2>&1; PRC=$?
python3 -B "$OUT/pool_runs.py" --analysis "$AN" --run "$OUT/run2_report_primary.json" "$OUT/run2_eligibility.json" --run "$OUT/report_primary.json" "$E" \
  --confidence 0.975 --stratum "$OUT/in/stratum_chance_pooled.txt" --out "$OUT/pooled_chance_stratum.json" > "$OUT/pooled_chance_stratum.stdout" 2>&1; SRC=$?
python3 -B "$OUT/pool_runs.py" --analysis "$AN" --run "$OUT/report_primary.json" "$E" \
  --confidence 0.95 --stratum "$OUT/in/stratum_chance_run3.txt" --out "$OUT/run3_chance_stratum.json" > "$OUT/run3_chance_stratum.stdout" 2>&1; S3=$?
set -e
log "pooled primary exit $PRC (3 = pooling OFF by section 7); pooled stratum exit $SRC; run 3 stratum exit $S3"
[ "$PRC" = 0 ] || [ "$PRC" = 3 ] || fail "pool_runs.py exit $PRC: see pooled_primary.stdout"

# 10. descriptive: categories, the REPORT-ONLY lines (K19), spend; manifest
python3 "$OUT/categories.py" "$OUT/report_primary.json" "$OUT/in/categories.json" "$OUT/by_category.json" | tee -a "$LOG" || log "category breakdown failed (descriptive only)"
git -C "$OUT/repo" show "$FREEZE_COMMIT:$RUN3/frozen_2026-10-25/exam_v2_2026-10-25.json" > "$OUT/exam_v2.json"
python3 -B "$OUT/report_only.py" "$OUT/exam_v2.json" "$OUT/km3.jsonl" $PRIMARY_FILES --out "$OUT/report_only.json" | tee -a "$LOG" || log "report-only lines failed (descriptive only)"
python3 judge.py spend $PRIMARY_FILES $REPEAT_RAW > "$OUT/spend.txt" 2>&1 || true
python3 - "$OUT" "$REF" "$SEEDS" "$RC" "$RC2" "$PRC" "$TOTAL_USD" "$PRIMARY_CAP" <<'EOF'
import hashlib, json, os, sys
out, ref, seeds, rc, rc2, prc, total, pcap = sys.argv[1:9]
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
files = [f for f in sorted(os.listdir(out)) if os.path.isfile(os.path.join(out, f))]
m = {'mode': 'live', 'judge_ref': ref, 'km3_rows': 'played fresh, frozen baseline (judge.py run --bot km3), nice 19, in the night window', 'seeds': seeds,
     'compare_primary_exit': int(rc), 'compare_sensitivity_exit': int(rc2), 'pooled_primary_exit': int(prc), 'failed_judge_rows': 'miss (run 2 A3)',
     'relabel': 'judge_repeat.jsonl = the repeat rows with repeat 0 -> 1 (run 1 relabel_repeat.py); nothing else changed',
     'spend_bound': f'frozen-7 budget_judge.py: each call reserved at its worst case before sending; ledger ${total} over the primary and the repeat, primary cap ${pcap} (its resend included)',
     'files': {f: h(os.path.join(out, f)) for f in files}, 'inputs': json.load(open(os.path.join(out, 'in', 'inputs_manifest.json')))}
json.dump(m, open(os.path.join(out, 'run_manifest.json'), 'w'), indent=1)
print('manifest written')
EOF
echo "DONE" > "$OUT/STATUS"
log "done: $(tail -n 1 "$OUT/spend.txt")"

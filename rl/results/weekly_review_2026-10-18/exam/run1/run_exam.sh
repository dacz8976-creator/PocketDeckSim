#!/bin/bash
# The unseen-positions exam's first scored run (PLAN step 3). MODE=dry mocks the judge (no API call, no key read); MODE=live is run only on the
# coordinator's go, after Astra passes the frozen tag. Everything runs from a clean sparse clone of the judge tag; inputs come from the exam commit.
#   MODE=dry REF=<commit or tag> bash run_exam.sh        MODE=live bash run_exam.sh   (REF defaults to judge-prompt-frozen-4)
set -euo pipefail
MODE=${MODE:-dry}
REF=${REF:-judge-prompt-frozen-4}
EXAM_COMMIT=5518fd604760edb40b41d1406723f14cd8343b78       # exam v1.6, passed by Astra
WINREPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
HERE=$(cd "$(dirname "$0")" && pwd)
TOTAL_USD=25          # the authorized total for both judge runs: a HARD bound (budget_judge.py reserves each call's worst case before sending it)
RUN_CAP=12            # and each run's own hard cap
EST_LIMIT=12.0        # an estimate above this for one run stops the script before any call
if [ "$MODE" = live ]; then SEEDS=25100000001,25100000002,25100000003; else SEEDS=25100900001,25100900002,25100900003; fi
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
OUT=$HOME/exam_run1/$MODE-$(date -u +%Y%m%dT%H%MZ)
mkdir -p "$OUT"
LOG=$OUT/run.log
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
fail() { log "STOP: $*"; echo "STOP" > "$OUT/STATUS"; exit 1; }
[ -e "$HOME/credit_work/PAUSE" ] && fail "PAUSE file present"
log "mode=$MODE ref=$REF exam=$EXAM_COMMIT seeds=$SEEDS out=$OUT"

# 1. clean sparse clone of the judge tag, and the exam commit for the inputs
URL=$(git -C "$WINREPO" remote get-url origin)
git clone -q --filter=blob:none --no-checkout "$URL" "$OUT/repo"
cd "$OUT/repo"
git fetch -q origin --tags
git fetch -q origin sonnet/exam-2026-10-19
git sparse-checkout init --cone
git sparse-checkout set rl/ai_judge lib rl/results/pause_games_decisions_2026-10-02/harness rl/results/pause_games_new_2026-10-13/v2/decks decks/dustin
git checkout -q --detach "$REF"
log "judge ref $(git rev-parse HEAD)"
git merge-base --is-ancestor "$EXAM_COMMIT" origin/sonnet/exam-2026-10-19 || fail "exam commit not on the exam branch"

# 2. the freeze identity must pass (sources, prompt fingerprint, settings, engine tree, both executables)
cd rl/ai_judge
python3 freeze_identity.py --check > "$OUT/freeze_check.txt" 2>&1 || { cat "$OUT/freeze_check.txt" | tee -a "$LOG"; fail "freeze_identity.py --check failed"; }
log "freeze_identity --check: pass"
# the spend bound's own tests (mocks and old fixtures only: no key, no API call, nothing from the exam)
env -u ANTHROPIC_API_KEY python3 "$HERE/test_budget.py" > "$OUT/test_budget.txt" 2>&1 || { tail -5 "$OUT/test_budget.txt" | tee -a "$LOG"; fail "test_budget.py failed"; }
log "spend bound tests: $(tail -1 "$OUT/test_budget.txt")"
LEDGER=$OUT/spend_ledger.json

# 3. inputs from the exam commit
python3 "$HERE/prep_inputs.py" "$OUT/repo" "$EXAM_COMMIT" "$REF" "$OUT/in" | tee -a "$LOG"
P=$OUT/in/positions.json; D=$OUT/in/decks; R=$OUT/in/references.json; E=$OUT/in/eligibility.json
IDS=$(tr '\n' ' ' < "$OUT/in/ids.txt")
NIDS=$(wc -l < "$OUT/in/ids.txt")

# 4. plan lists (none may be capped) and the judge's prompt sizes (nothing sent)
python3 judge.py plans --positions "$P" --decks "$D" --ids $IDS > "$OUT/plans.txt" 2>&1 || fail "plan lister"
grep -i -q 'capped: *true\|capped=True' "$OUT/plans.txt" && fail "a plan list is capped"
python3 judge.py judge --positions "$P" --decks "$D" --ids $IDS > "$OUT/prompt_sizes.txt" 2>&1 || fail "prompt build"
python3 - "$OUT/prompt_sizes.txt" "$EST_LIMIT" <<'EOF' | tee -a "$LOG" || fail "cost estimate above the limit"
import re, sys
txt = open(sys.argv[1]).read(); limit = float(sys.argv[2])
toks = [int(x.replace(',', '')) for x in re.findall(r'(\d[\d,]*) ?(?:prompt )?tokens', txt)]
if not toks:
    toks = [int(x) for x in re.findall(r'"prompt_tokens_estimate": (\d+)', txt)]
n = len(toks); tin = sum(toks)
est = tin * 3 / 1e6 + n * 1500 * 15 / 1e6   # assumed $3 / $15 per Mtok, about 1.5k output tokens a call (reasoning included)
print(f'estimate: {n} prompts, {tin} input tokens, about ${est:.2f} per judge run (limit ${limit})')
sys.exit(0 if (n and est <= limit) else 1)
EOF

# 5. km3 rows from the frozen baseline executable (kx3: the frozen baseline does not play it; see README)
python3 judge.py run --bot km3 --positions "$P" --decks "$D" --ids $IDS --seeds "$SEEDS" --out "$OUT/km3.jsonl" > "$OUT/km3.stdout" 2>&1 || fail "km3 run"
log "km3 rows: $(wc -l < "$OUT/km3.jsonl")"

judge_run() {  # $1 out file, $2 tag. judge.judge_one with the FROZEN settings, under the hard spend bound (one ledger for both runs)
  if [ "$MODE" = live ]; then
    python3 "$HERE/budget_judge.py" --positions "$P" --decks "$D" --ids $IDS --max-calls "$NIDS" --repeat 1 --workers 4 --tag "$2" --out "$1" \
      --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$RUN_CAP" --live
  else
    env -u ANTHROPIC_API_KEY python3 "$HERE/budget_judge.py" --positions "$P" --decks "$D" --ids $IDS --max-calls "$NIDS" --repeat 1 --workers 4 \
      --tag "MOCK_DRY_RUN_$2" --out "$1" --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$RUN_CAP" --mock
  fi
}
compare() {  # $1 out report, $2 judge repeats, rest: result files
  local out=$1 reps=$2; shift 2
  set +e
  python3 judge.py compare --positions "$P" --decks "$D" --results "$@" --ids $IDS --bots km3,judge --seeds "$SEEDS" --judge-repeats "$reps" \
    --references "$R" --eligibility "$E" --on-problem fail --out "$out" > "$out.stdout" 2>&1
  local rc=$?
  set -e
  echo $rc
}

# 6. the judge: ONE primary call per decision
judge_run "$OUT/judge_primary.jsonl" exam_run1_primary > "$OUT/judge_primary.stdout" 2>&1 || { tail -3 "$OUT/judge_primary.stdout" | tee -a "$LOG"; fail "judge primary run"; }
log "judge primary: $(grep 'call(s) returned' "$OUT/judge_primary.stdout")"
log "judge primary rows: $(wc -l < "$OUT/judge_primary.jsonl")"

# 7. the formal comparison (primary): any problem at a primary point fails the batch
RC=$(compare "$OUT/report_primary.json" 1 "$OUT/km3.jsonl" "$OUT/judge_primary.jsonl")
log "compare (primary) exit $RC"
[ "$RC" = 0 ] || fail "formal comparison (primary) exit $RC: see report_primary.json(.stdout)"

# 8. the separate sensitivity repeat, then its own comparison
judge_run "$OUT/judge_repeat_raw.jsonl" exam_run1_repeat > "$OUT/judge_repeat.stdout" 2>&1 || { tail -3 "$OUT/judge_repeat.stdout" | tee -a "$LOG"; fail "judge repeat run"; }
log "judge repeat: $(grep 'call(s) returned' "$OUT/judge_repeat.stdout")"
python3 "$HERE/relabel_repeat.py" "$OUT/judge_repeat_raw.jsonl" "$OUT/judge_repeat.jsonl" | tee -a "$LOG"
RC2=$(compare "$OUT/report_sensitivity.json" 2 "$OUT/km3.jsonl" "$OUT/judge_primary.jsonl" "$OUT/judge_repeat.jsonl")
log "compare (sensitivity) exit $RC2"

# 9. descriptive breakdown by deck kind and answer kind (not part of the formal result), spend, manifest
python3 "$HERE/categories.py" "$OUT/report_primary.json" "$OUT/in/categories.json" "$OUT/by_category.json" | tee -a "$LOG" || log "category breakdown failed (descriptive only)"
python3 judge.py spend "$OUT/judge_primary.jsonl" "$OUT/judge_repeat_raw.jsonl" > "$OUT/spend.txt" 2>&1 || true
python3 - "$OUT" "$MODE" "$REF" "$SEEDS" "$RC" "$RC2" <<'EOF'
import hashlib, json, os, sys
out, mode, ref, seeds, rc, rc2 = sys.argv[1:7]
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
files = [f for f in sorted(os.listdir(out)) if os.path.isfile(os.path.join(out, f))]
m = {'mode': mode, 'judge_ref': ref, 'seeds': seeds, 'compare_primary_exit': int(rc), 'compare_sensitivity_exit': int(rc2),
     'relabel': 'judge_repeat.jsonl = judge_repeat_raw.jsonl with repeat 0 -> 1 (relabel_repeat.py); nothing else changed',
     'baseline_note': 'km3 only: the frozen baseline executable plays k<number>/km<number> bots, not kx3',
     'spend_bound': 'budget_judge.py: each call reserved at its worst case before sending; $25 total over both runs (spend_ledger.json), $12 per run',
     'files': {f: h(os.path.join(out, f)) for f in files}, 'inputs': json.load(open(os.path.join(out, 'in', 'inputs_manifest.json')))}
json.dump(m, open(os.path.join(out, 'run_manifest.json'), 'w'), indent=1)
print('manifest written')
EOF
echo "DONE" > "$OUT/STATUS"
log "done: $(cat "$OUT/spend.txt" | tail -1)"

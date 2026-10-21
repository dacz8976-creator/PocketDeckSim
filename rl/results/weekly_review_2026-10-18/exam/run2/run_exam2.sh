#!/bin/bash
# Exam run 2 (PREREG_RUN2.md and its addendum 1): the frozen-4 prompt answered by Gemini 4 Argon (judge-prompt-frozen-7, Vertex AI), against
# run 1's km3 rows reused unchanged. MODE=dry mocks the judge (budget_judge.py --mock: no key read, no call); MODE=live calls the model.
#   MODE=dry bash run_exam2.sh        MODE=live bash run_exam2.sh
set -euo pipefail
MODE=${MODE:-dry}
REF=judge-prompt-frozen-7
REF_COMMIT=712593a1b77b203ec23fb15589c158c6bddb2bf2
EXAM_COMMIT=5518fd604760edb40b41d1406723f14cd8343b78       # exam v1.6, passed by Astra
EXAM_BRANCH=sonnet/exam-2026-10-19
RUN1=rl/results/weekly_review_2026-10-18/exam/run1
KM3_SHA=3cc523d32f7290780881f79b5ec67d7945843c72af92bd0d0a8dab34a1f76fab
SEEDS=25100000001,25100000002,25100000003                 # run 1's registered km3 seeds (the reused rows)
PROJECT=project-45583ef0-ed57-426c-bde                     # Dustin's Google Cloud project id (not a secret; addendum A1)
TOTAL_USD=14.57                                            # $15 in all minus the smoke's $0.4234 on its own ledger (addendum A5)
WINREPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
HERE=$(cd "$(dirname "$0")" && pwd)
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
OUT=$HOME/exam_run2/$MODE-$(date -u +%Y%m%dT%H%MZ)
mkdir -p "$OUT"
LOG=$OUT/run.log
log() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
fail() { log "STOP: $*"; echo "STOP" > "$OUT/STATUS"; exit 1; }
[ -e "$HOME/credit_work/PAUSE" ] && fail "PAUSE file present"
log "mode=$MODE ref=$REF exam=$EXAM_COMMIT km3 rows reused (run 1) out=$OUT"

# 1. clean sparse clone of the judge tag; the exam branch for the inputs and run 1's km3 rows
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
git merge-base --is-ancestor "$EXAM_COMMIT" FETCH_HEAD || fail "exam commit not on the exam branch"
EXAM_TIP=$(git rev-parse FETCH_HEAD)

# 2. the freeze identity (sources, prompt fingerprint, settings, engine tree, both executables), then the harness's tests (mocks and fixtures)
cd rl/ai_judge
python3 freeze_identity.py --check > "$OUT/freeze_check.txt" 2>&1 || { cat "$OUT/freeze_check.txt" | tee -a "$LOG"; fail "freeze_identity.py --check failed"; }
grep -q 0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762 FROZEN.json || fail "prompt fingerprint not in FROZEN.json"
log "freeze_identity --check: pass"
env -u VERTEX_PROJECT -u VERTEX_API_KEY -u ANTHROPIC_API_KEY -u GEMINI_API_KEY python3 -B -m unittest discover -s tests > "$OUT/tests.txt" 2>&1 \
  || { tail -n 5 "$OUT/tests.txt" | tee -a "$LOG"; fail "the harness's tests failed"; }
log "harness tests: $(grep -E '^Ran ' "$OUT/tests.txt") $(tail -n 1 "$OUT/tests.txt")"
LEDGER=$OUT/spend_ledger.json

# 3. inputs from the exam commit (run 1's prep_inputs.py, unchanged)
git -C "$OUT/repo" show "$EXAM_TIP:$RUN1/prep_inputs.py" > "$OUT/prep_inputs.py"
python3 "$OUT/prep_inputs.py" "$OUT/repo" "$EXAM_COMMIT" "$REF" "$OUT/in" | tee -a "$LOG"
P=$OUT/in/positions.json; D=$OUT/in/decks; R=$OUT/in/references.json; E=$OUT/in/eligibility.json
for pair in "$P:17bea6e345667f765ea6d78fd427f091ed6671c4a5e0ef923ed80f30f6cb02c1" "$R:12e0e997620f19b241597e2fac80f530e278daedb6af1aabc27953197cc809fd" \
            "$E:6199ddeffd8ad084a726c0e6e356abb908112724068eb2985ce9cae2344daac2"; do
  f=${pair%%:*}; want=${pair##*:}
  [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$want" ] || fail "$(basename "$f") is not run 1's ($want)"
done
log "inputs: positions, references and eligibility equal run 1's (sha256)"
IDS=$(tr '\n' ' ' < "$OUT/in/ids.txt")
NIDS=$(wc -l < "$OUT/in/ids.txt")

# 4. plan lists (none may be capped) and the prompt sizes (nothing sent): the estimate at the introductory price
python3 judge.py plans --positions "$P" --decks "$D" --ids $IDS > "$OUT/plans.txt" 2>&1 || fail "plan lister"
grep -i -q 'capped: *true\|capped=True' "$OUT/plans.txt" && fail "a plan list is capped"
python3 judge.py judge --provider gemini-vertex --positions "$P" --decks "$D" --ids $IDS > "$OUT/prompt_sizes.txt" 2>&1 || fail "prompt build"
python3 - "$OUT/prompt_sizes.txt" "$TOTAL_USD" <<'EOF' | tee -a "$LOG" || fail "estimate above the ledger"
import re, sys
txt = open(sys.argv[1]).read(); limit = float(sys.argv[2])
toks = [int(x.replace(',', '')) for x in re.findall(r'(\d[\d,]*) ?(?:prompt )?tokens', txt)] or [int(x) for x in re.findall(r'"prompt_tokens_estimate": (\d+)', txt)]
n = len(toks); tin = sum(toks)
est = tin * 2 / 1e6 + n * 3000 * 10 / 1e6   # $2 / $10 per Mtok (introductory price), about 3,000 output tokens a call (thinking included); the lister's estimate runs high
print(f'estimate: {n} prompts, {tin} input tokens (estimated), about ${est:.2f} per judge run at $2/$10 (the ledger: ${limit})')
sys.exit(0 if (n and est <= limit) else 1)
EOF

# 5. km3: run 1's rows, reused unchanged (PREREG section 3)
git -C "$OUT/repo" show "$EXAM_TIP:$RUN1/live-20261020T0059Z/km3.jsonl" > "$OUT/km3.jsonl"
[ "$(sha256sum "$OUT/km3.jsonl" | cut -d' ' -f1)" = $KM3_SHA ] || fail "km3.jsonl is not run 1's"
log "km3 rows: $(wc -l < "$OUT/km3.jsonl") (run 1's, sha256 ${KM3_SHA:0:12})"

judge_run() {  # $1 out file, $2 tag, rest: ids. frozen-7's budget_judge.py (judge.judge_one with the FROZEN settings), one ledger for every run
  local out=$1 tag=$2; shift 2
  local n=$#
  if [ "$MODE" = live ]; then
    python3 budget_judge.py --positions "$P" --decks "$D" --ids "$@" --max-calls "$n" --repeat 1 --workers 4 --tag "$tag" --out "$out" \
      --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$TOTAL_USD" --vertex-project "$PROJECT" --live
  else
    env -u VERTEX_API_KEY python3 budget_judge.py --positions "$P" --decks "$D" --ids "$@" --max-calls "$n" --repeat 1 --workers 4 --tag "MOCK_DRY_RUN_$tag" \
      --out "$out" --ledger "$LEDGER" --total-usd "$TOTAL_USD" --run-cap-usd "$TOTAL_USD" --mock
  fi
}
missing_ids() {  # ids with no row at all in the given files (a call with no model reply; addendum A4)
  python3 - "$OUT/in/ids.txt" "$@" <<'EOF'
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
# a batch: one run, then ONE resend of the ids with no row at all, into a new file on the same ledger (addendum A4). Prints the files made.
batch() {  # $1 name, $2 tag
  local name=$1 tag=$2 rc=0 files="$OUT/$1.jsonl"
  judge_run "$OUT/$name.jsonl" "$tag" $IDS > "$OUT/$name.stdout" 2>&1 || rc=$?
  log "$name: exit $rc; $(grep 'call(s) returned' "$OUT/$name.stdout" || true)"
  local miss=$(missing_ids "$OUT/$name.jsonl")
  if [ -n "$miss" ]; then
    log "$name: $(echo $miss | wc -w) decision(s) without a row (no model reply): one resend"
    judge_run "$OUT/${name}_resend.jsonl" "${tag}_resend" $miss > "$OUT/${name}_resend.stdout" 2>&1 || true
    log "$name resend: $(grep 'call(s) returned' "$OUT/${name}_resend.stdout" || true)"
    files="$files $OUT/${name}_resend.jsonl"
    [ -s "$OUT/${name}_resend.jsonl" ] || files="$OUT/$name.jsonl"
  fi
  echo "$files" > "$OUT/$name.files"
}
compare() {  # $1 out report, $2 judge repeats, rest: result files
  local out=$1 reps=$2; shift 2
  local onp=fail; [ "$MODE" = dry ] && onp=inconclusive   # mock rows are refused by the formal path: the dry run checks that they are the only problem
  set +e
  python3 judge.py compare --positions "$P" --decks "$D" --results "$@" --ids $IDS --bots km3,judge --seeds "$SEEDS" --judge-repeats "$reps" \
    --references "$R" --eligibility "$E" --on-problem $onp --failed-judge-rows miss --out "$out" > "$out.stdout" 2>&1
  local rc=$?
  set -e
  echo $rc
}

# 6. the judge, primary: ONE call per decision
batch judge_primary run2_primary
PRIMARY_FILES=$(cat "$OUT/judge_primary.files")
[ -z "$(missing_ids $PRIMARY_FILES)" ] || fail "primary incomplete after the one resend: $(missing_ids $PRIMARY_FILES) (no verdict; addendum A4)"
log "judge primary rows: $(cat $PRIMARY_FILES | grep -c .)"

# 7. the formal comparison, primary (failed judge rows count as misses; any other problem fails the batch)
RC=$(compare "$OUT/report_primary.json" 1 "$OUT/km3.jsonl" $PRIMARY_FILES)
log "compare (primary) exit $RC"
if [ "$MODE" = dry ]; then
  python3 - "$OUT/report_primary.json" <<'EOF' | tee -a "$LOG"
import json, sys, collections
r = json.load(open(sys.argv[1]))
kinds = collections.Counter((p.get('kind'), p.get('bot')) for p in r.get('problems', []))
print('dry compare problems:', dict(kinds))
bad = [k for k in kinds if k[0] != 'mock_row']
sys.exit(1 if bad else 0)
EOF
else
  [ "$RC" = 0 ] || fail "formal comparison (primary) exit $RC: see report_primary.json(.stdout)"
fi

# 8. the separate sensitivity repeat (what the ledger has left), then its own comparison
batch judge_repeat_raw run2_repeat
REPEAT_RAW=$(cat "$OUT/judge_repeat_raw.files")
cat $REPEAT_RAW > "$OUT/judge_repeat_raw_all.jsonl"
git -C "$OUT/repo" show "$EXAM_TIP:$RUN1/relabel_repeat.py" > "$OUT/relabel_repeat.py"
python3 "$OUT/relabel_repeat.py" "$OUT/judge_repeat_raw_all.jsonl" "$OUT/judge_repeat.jsonl" | tee -a "$LOG"
REPEAT_MISSING=$(missing_ids $REPEAT_RAW)
[ -z "$REPEAT_MISSING" ] || log "repeat INCOMPLETE (sensitivity only): $(echo $REPEAT_MISSING | wc -w) decision(s) without a row"
RC2=$(compare "$OUT/report_sensitivity.json" 2 "$OUT/km3.jsonl" $PRIMARY_FILES "$OUT/judge_repeat.jsonl")
log "compare (sensitivity) exit $RC2"

# 9. descriptive: categories (run 1's script), Gemini v run 1's Sonnet judge, the no-choice count; spend; manifest
git -C "$OUT/repo" show "$EXAM_TIP:$RUN1/categories.py" > "$OUT/categories.py"
python3 "$OUT/categories.py" "$OUT/report_primary.json" "$OUT/in/categories.json" "$OUT/by_category.json" | tee -a "$LOG" || log "category breakdown failed (descriptive only)"
git -C "$OUT/repo" show "$EXAM_TIP:$RUN1/live-20261020T0059Z/report_primary.json" > "$OUT/run1_report_primary.json"
python3 "$HERE/desc_vs_run1.py" "$OUT/report_primary.json" "$OUT/run1_report_primary.json" "$E" "$OUT/vs_run1.json" | tee -a "$LOG" || log "Gemini v run 1 description failed"
python3 judge.py spend $PRIMARY_FILES $REPEAT_RAW > "$OUT/spend.txt" 2>&1 || true
python3 - "$OUT" "$MODE" "$REF" "$SEEDS" "$RC" "$RC2" "$TOTAL_USD" <<'EOF'
import hashlib, json, os, sys
out, mode, ref, seeds, rc, rc2, total = sys.argv[1:8]
h = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
files = [f for f in sorted(os.listdir(out)) if os.path.isfile(os.path.join(out, f))]
m = {'mode': mode, 'judge_ref': ref, 'km3_rows': "run 1's km3.jsonl, reused unchanged (PREREG_RUN2 section 3)", 'seeds': seeds,
     'compare_primary_exit': int(rc), 'compare_sensitivity_exit': int(rc2), 'failed_judge_rows': 'miss (addendum A3)',
     'relabel': 'judge_repeat.jsonl = the repeat rows with repeat 0 -> 1 (run 1 relabel_repeat.py); nothing else changed',
     'spend_bound': f'frozen-7 budget_judge.py: each call reserved at its worst case before sending; ${total} ledger over the primary and the repeat (spend_ledger.json)',
     'files': {f: h(os.path.join(out, f)) for f in files}, 'inputs': json.load(open(os.path.join(out, 'in', 'inputs_manifest.json')))}
json.dump(m, open(os.path.join(out, 'run_manifest.json'), 'w'), indent=1)
print('manifest written')
EOF
echo "DONE" > "$OUT/STATUS"
log "done: $(tail -n 1 "$OUT/spend.txt")"

#!/bin/bash
# Stage 2 scoring, run once after STAGE2 ENDED: the registered analysis (game_analysis.py, gate 6 kit) on the stage-2 run dir.
# Writes only under ~/relplan/gemini/stage2/score. The clone must be the addendum commit and stay clean.
set -u
R=/home/dacz8976/credit_work/gemini
Z=/home/dacz8976/relplan/gemini/stage2
D=$Z/run
O=$Z/score
ADD=c1e5642e52f3f43319783e1c4ad3a3d1303077d6
mkdir -p "$O"
LOG=$O/score.log
say() { echo "$(date -u +%FT%TZ) $*" | tee -a "$LOG"; }
die() { say "SCORE STOP: $*"; exit 1; }

cd "$R" || die "no clone"
H=$(git rev-parse HEAD) || die "git"
[ "$H" = "$ADD" ] || die "HEAD $H is not the addendum $ADD"
[ -z "$(git status --porcelain)" ] || die "clone not clean before scoring"
pgrep -f 'game_runner.py run' >/dev/null && die "game_runner is still running"
python3 - "$D/run_end.json" <<'PY' || die "run_end is not a complete stage-2 end"
import json, sys
e = json.load(open(sys.argv[1]))
ok = e.get('stage') == 2 and e.get('planned_deals') == 128 and e.get('complete_deals') == 128 and e.get('stopped_early') is False and e.get('stop_reason') is None
print('run_end:', json.dumps(e, sort_keys=True))
sys.exit(0 if ok else 1)
PY

say "inputs (sha256):"
sha256sum "$D/run_end.json" "$D/run_start.json" "$D/deals.jsonl" "$D/games.jsonl" "$Z/ledger.json" "$Z/stage2.plan.json" | tee -a "$LOG" > "$O/inputs.sha256"
say "kit: game_analysis.py $(sha256sum rl/ai_judge/game_analysis.py | cut -c1-16), game_kit.py $(sha256sum rl/ai_judge/game_kit.py | cut -c1-16), analysis.py $(sha256sum rl/ai_judge/analysis.py | cut -c1-16) at $H"

export PYTHONDONTWRITEBYTECODE=1
say "gate 6 self-test:"
nice -n 19 python3 rl/ai_judge/game_analysis.py --self-test > "$O/selftest.txt" 2>&1
rc=$?
cat "$O/selftest.txt" >> "$LOG"
tail -1 "$O/selftest.txt" | tee -a "$LOG"
[ $rc = 0 ] && grep -qx 'GATE6 PASS' "$O/selftest.txt" || die "gate 6 self-test did not pass (rc $rc)"

say "registered analysis:"
nice -n 19 python3 rl/ai_judge/game_analysis.py --run-dir "$D" --out "$O/analysis.json" > "$O/analysis_stdout.txt" 2>&1
rc=$?
cat "$O/analysis_stdout.txt" | tee -a "$LOG"
[ $rc = 0 ] || die "analysis rc $rc"
sha256sum "$O/analysis.json" | tee -a "$LOG"

[ -z "$(git status --porcelain)" ] || die "clone not clean after scoring"
say "SCORE DONE"

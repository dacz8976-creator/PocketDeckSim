#!/usr/bin/env bash
# Second reader, read-only: when the kpr mixed rows' README and rows entered git (the "design fixed before any row ran" claim).
set -uo pipefail
cd "$(dirname "$0")/../../../.."
D=rl/results/kpr_mixed_rows_2026-09-26
for f in README.md run_kpr_mixed.sh mixed_kpr3_first.jsonl mixed_kpr3_second.jsonl spot_kp3_p0-2.jsonl kpr3_replay_p1.jsonl; do
  echo "== $f: commits on any ref (oldest last)"
  TZ=UTC git log --all --date=format-local:'%Y-%m-%d %H:%M' --format='%h %cd %s' -- "$D/$f" | cut -c1-160
done
echo "== git status of the folder (read-only)"
git status --short -- "$D" rl/results/table_readings_2026-09-24 | head -40
echo "== file times (UTC)"
TZ=UTC ls -l --time-style='+%Y-%m-%d %H:%M' "$D"

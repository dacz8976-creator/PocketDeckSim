#!/usr/bin/env bash
# Second reader's read-only git checks for kpr3_paired_reading.md (Sept 26). No add/commit/stash/checkout.
# Usage (WSL): check_git.sh <scratch dir>   (copies the branch files it needs into the scratch dir)
set -uo pipefail
SP=$1
B=origin/claude/pensive-ptolemy-spwc0b
cd "$(dirname "$0")/../../../.."   # repo root
mkdir -p "$SP/branch"
for f in kpr3_500.jsonl kpr3_500.txt identity_k3_500.jsonl identity_kp3_500.jsonl identity_kq3_500.jsonl identity_kd3_40.jsonl \
         table_commit_identity_k3_40.jsonl table_commit_identity_kp3_40.jsonl table_commit_identity_kq3_40.jsonl run_kpr3_table.sh run_identity.sh; do
  git show "$B:rl/results/kpr_2026-09-25/$f" > "$SP/branch/$f"
done
git show "$B:rl/results/kd_2026-09-25/kd3_500.jsonl" > "$SP/branch/kd3_500.jsonl"
echo "== sha256 of the kpr3 table copied out"
sha256sum "$SP/branch/kpr3_500.jsonl"
echo "== branch head"
git log -1 --format='%h %cI %s' $B
echo "== commit times (UTC, committer and author)"
for c in 9a35f54 0adfeb7 1981bb4 14c7d9b 53638a7 e09fb46 d141623 8f16338 aa87fa3; do
  TZ=UTC git log -1 --date=format-local:'%Y-%m-%d %H:%M' --format="%h  committed %cd  authored %ad  %s" $c
done
echo "== commits touching the kpr README on the branch"
TZ=UTC git log --date=format-local:'%Y-%m-%d %H:%M' --format='%h %cd %s' $B -- rl/results/kpr_2026-09-25/README.md
echo "== commits touching kpr3_500.jsonl on the branch (oldest last)"
TZ=UTC git log --date=format-local:'%Y-%m-%d %H:%M' --format='%h %cd %s' $B -- rl/results/kpr_2026-09-25/kpr3_500.jsonl
echo "== line counts of kpr3_500.jsonl at those commits"
for c in $(git log --format='%h' $B -- rl/results/kpr_2026-09-25/kpr3_500.jsonl); do
  echo "$c $(git show $c:rl/results/kpr_2026-09-25/kpr3_500.jsonl | wc -l)"
done
echo "== engine/ changes 53638a7..e09fb46"
git diff --stat 53638a7 e09fb46 -- engine/
git diff --numstat 53638a7 e09fb46 -- engine/
echo "== all changes 53638a7..e09fb46 (any path)"
git diff --stat 53638a7 e09fb46 | tail -5
echo "== e09fb46 itself (vs its parent)"
git show --stat --format='%h %s' e09fb46 | head -20
echo "== 53638a7 itself (vs its parent)"
git show --stat --format='%h %s' 53638a7 | head -20
echo "== engine/ changes 1981bb4..53638a7 (should be tests only if 53638a7's bot code is 1981bb4's)"
git diff --numstat 1981bb4 53638a7 -- engine/
echo "== engine/ changes 14c7d9b..e09fb46"
git diff --numstat 14c7d9b e09fb46 -- engine/
echo "== parents chain from 9a35f54 to aa87fa3 (first-parent, oldest first)"
git log --reverse --first-parent --format='%h %s' 9a35f54^..aa87fa3 | head -40
echo "== engine/ tree hashes"
for c in 53638a7 14c7d9b e09fb46 aa87fa3; do echo "$c $(git rev-parse $c:engine)"; done
echo "== commits after e09fb46 touching engine/ up to the branch head"
git log --format='%h %s' e09fb46..$B -- engine/
echo "== the table's run script"
cat "$SP/branch/run_kpr3_table.sh"
echo "== go-ahead search: commit messages on every ref"
git log --all -i --format='%h %s' --grep='go-ahead' --grep='go ahead'
echo "== 1981bb4 full message"
git log -1 --format='%B' 1981bb4
echo "== git grep 'go-ahead' on the branch and on main (rl/ docs/)"
git grep -n -i 'go-ahead' $B -- rl docs | cut -c1-220
git grep -n -i 'go-ahead' main -- rl docs | cut -c1-220

#!/usr/bin/env bash
# Read-only git checks for kpr3's reading (laptop, Sept 26): identity files at the table's build, the engine diff
# between the full replay (53638a7) and the table (e09fb46), commit times, and any record of "Dustin's go-ahead" for
# amendment 5 (1981bb4). Nothing is added, committed or checked out. Usage (WSL): git_checks.sh <scratch dir>
set -uo pipefail
O=$1
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
B=origin/claude/pensive-ptolemy-spwc0b
mkdir -p "$O"
for f in table_commit_identity_k3_40.jsonl table_commit_identity_kp3_40.jsonl table_commit_identity_kq3_40.jsonl identity_k3_500.jsonl identity_kq3_500.jsonl identity_kd3_40.jsonl; do
  git show "$B:rl/results/kpr_2026-09-25/$f" > "$O/$f"
done
echo "== branch head"; git log -1 --format='%h %ci %s' "$B"
echo "== kpr commits on the branch (oldest first), with times"
for c in 9a35f54 0adfeb7 1981bb4 14c7d9b 53638a7 e09fb46 df46e0a d141623 8f16338 aa87fa3; do
  git log -1 --format='%h %ci %an | %s' "$c"
done
echo "== full message of 1981bb4"; git log -1 --format='%B' 1981bb4
echo "== full message of 9a35f54"; git log -1 --format='%B' 9a35f54 | head -60
echo "== engine/ diff 53638a7..e09fb46 (stat)"; git diff --stat 53638a7 e09fb46 -- engine
echo "== engine/ tree hash at e09fb46 and at the branch head"; git rev-parse e09fb46:engine "$B:engine"
echo "== commits touching the kpr README"; git log --format='%h %ci %s' "$B" -- rl/results/kpr_2026-09-25/README.md
echo "== 'go-ahead' / 1981bb4 / amendment 5 in every commit message on the branch and main"
git log --all --format='%h %ci %s%n%b' | grep -n -i -E "go-ahead|go ahead|1981bb4|amendment 5" | head -40
echo "== the same words in files on the branch (rl/ and docs/)"
git grep -n -i -E "go-ahead|go ahead|1981bb4|amendment 5" "$B" -- rl docs | head -40
echo "== the same words in files on main (rl/ and docs/)"
git grep -n -i -E "go-ahead|go ahead|1981bb4|amendment 5" HEAD -- rl docs | head -40

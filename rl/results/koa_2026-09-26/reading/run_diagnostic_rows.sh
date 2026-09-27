#!/usr/bin/env bash
# koa's diagnostics, the discriminating rows (REGISTRATION.md section 7, "B and R"): kob3 on Hydreigon, Vespiquen and
# Weezing, and kor3 on Suicune, Vespiquen and Weezing, each deck's 7 table pairings, both directions (the diagnostic on the
# deck only, kp3 on the other), at the official engine. Attribution only, read after koa's decision. Runs after kpg's
# held-out runs (anchored wait).
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"; O="$R/rl/results/koa_2026-09-26/reading"
SCAN="$R/rl/engine-2026-09-27/legality_scan"
note() { echo "$(date -u +%FT%TZ) $*" >> "$O/STATUS.txt"; }
until grep -q 'KPG HELDOUT RUNS DONE' "$R/rl/results/kpg_2026-09-27/STATUS.txt" 2>/dev/null; do
  grep -q 'FAILED' "$R/rl/results/kpg_2026-09-27/STATUS.txt" 2>/dev/null && break; sleep 60; done
cd "$R/engine"
pairs_of() { python3 -c "import itertools; N=['altaria','blaziken','hydreigon','lucario','sceptile','suicune','vespiquen','weezing']; P=list(itertools.combinations(N,2)); print(','.join(str(i) for i,(a,b) in enumerate(P) if '$1' in (a,b)))"; }
run() { local name=$1; shift; [ -s "$O/$name.jsonl" ] && return; local s=$(date +%s)
  RAYON_NUM_THREADS=14 nice -n 10 "$SCAN" --decks ../decks/research "$@" --games 500 --games-out "$O/$name.jsonl.part" > "$O/$name.txt" 2>&1 \
    || { note "FAILED: $name"; exit 1; }
  mv "$O/$name.jsonl.part" "$O/$name.jsonl"; note "$name done in $(( $(date +%s) - s )) s ($(wc -l < "$O/$name.jsonl") games)"; }
for spec in kob3:hydreigon kob3:vespiquen kob3:weezing kor3:suicune kor3:vespiquen kor3:weezing; do
  b=${spec%%:*}; d=${spec#*:}; P=$(pairs_of $d)
  run diag_${b}_${d}_first --pairings "$P" --bot-a $b --bot-b kp3
  run diag_${b}_${d}_second --pairings "$P" --bot-a kp3 --bot-b $b
done
echo "$(date -u +%F\ %T) DIAGNOSTIC ROWS DONE" >> "$O/STATUS.txt"

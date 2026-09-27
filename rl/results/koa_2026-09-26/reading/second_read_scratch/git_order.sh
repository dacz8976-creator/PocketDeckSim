#!/usr/bin/env bash
# Read-only: the commit order of koa's reading files.
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
S="$R/rl/results/koa_2026-09-26/reading/second_read_scratch"
cd "$R"
{
  git log --format="%h %ad %s" --date=iso -- rl/results/koa_2026-09-26/reading/footprint.txt rl/results/koa_2026-09-26/reading/READING_numbers.txt rl/results/koa_2026-09-26/reading/score28_koa3_vs_kp3.txt rl/results/koa_2026-09-26/reading/table_koa3.jsonl | head -20
  echo "---- 8e6375b"
  git show --stat --format="%h %ad %s" --date=iso 8e6375b | head -20
  echo "---- files added per commit"
  for f in footprint.txt READING_numbers.txt score28_koa3_vs_kp3.txt mixed_koa3_first.jsonl b2e_koa3.jsonl; do
    echo "$f: $(git log --diff-filter=A --format='%h %ad' --date=iso -- rl/results/koa_2026-09-26/reading/$f | tail -1)"
  done
} > "$S/git_order.txt" 2>&1

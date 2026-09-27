#!/usr/bin/env bash
# Read-only: are the raw files read here the committed ones?
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
S="$R/rl/results/koa_2026-09-26/reading/second_read_scratch"
cd "$R"
{
  git status --short -- rl/results/koa_2026-09-26 rl/results/kpf_2026-09-26/reading/table_kp3.jsonl rl/results/kpf_2026-09-26/reading/b2e_kp3.jsonl rl/results/table_readings_2026-09-24/score.py rl/results/scoreboard_v2_2026-09-25 rl/results/b2e_card_check_2026-09-26/limitless_cells.csv rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
  echo "---- last commits"
  git log --format="%h %ad %s" --date=iso -3 -- rl/results/kpf_2026-09-26/reading/table_kp3.jsonl rl/results/kpf_2026-09-26/reading/b2e_kp3.jsonl
  echo "---- HEAD"; git log --format="%h %ad %s" --date=iso -3
} > "$S/git_state.txt" 2>&1

#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
echo "== branch"; git rev-parse --abbrev-ref HEAD; git rev-parse --short HEAD
echo "== status (short, limited)"; git status --short | head -30
echo "== log harness converter"; git log --oneline -8 -- rl/results/pause_games_new_2026-10-12/harness/ledger_to_positions.py
echo "== log v2"; git log --oneline -8 -- rl/results/pause_games_new_2026-10-13/v2/positions_all.json
echo "== branches with v2"; git branch -a --contains $(git log -1 --format=%H -- rl/results/pause_games_new_2026-10-13/v2/positions_all.json) 2>/dev/null | head
echo "== diff converter HEAD vs 28df6315"; git diff --stat 28df6315 HEAD -- rl/results/pause_games_new_2026-10-12/harness/ | tail -5
echo "== converter_checkup_ko readme"; ls rl/results/converter_checkup_ko_2026-10-13/ 2>/dev/null

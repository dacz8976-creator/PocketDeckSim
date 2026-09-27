#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim" || exit 1
git log --date=iso --format="%h %ad %s" -n 50
echo "=== files touching koa reading ==="
git log --date=iso --format="%h %ad %s" --name-status -- rl/results/koa_2026-09-26/ | head -150
echo "=== registration history ==="
git log --date=iso --format="%h %ad %s" -- rl/results/opening_active_census_2026-09-26/REGISTRATION.md
echo "=== kpg registration ==="
git log --date=iso --format="%h %ad %s" -- rl/results/kpg_2026-09-27/
echo "=== status ==="
git status --short | head -60

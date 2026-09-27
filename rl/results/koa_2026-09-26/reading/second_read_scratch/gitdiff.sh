#!/bin/bash
cd "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim" || exit 1
echo "=== diff read_koa.py since 8e6375b ==="
git diff 8e6375b -- rl/results/koa_2026-09-26/reading/read_koa.py
echo "=== commit 8e6375b full stat ==="
git show --stat --format="%h %ad %an %s%n%b" 8e6375b
echo "=== 4e48fb1 stat ==="
git show --stat --format="%h %ad %an %s%n%b" 4e48fb1 | head -80
echo "=== 01f7847 stat ==="
git show --stat --format="%h %ad %an %s%n%b" 01f7847 | head -40
echo "=== any commits after 8e6375b ==="
git log --all --date=iso --format="%h %ad %s" 8e6375b..
echo "=== branches ==="
git branch -a

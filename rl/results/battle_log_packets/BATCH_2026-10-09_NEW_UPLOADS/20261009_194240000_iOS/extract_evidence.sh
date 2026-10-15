#!/usr/bin/env bash
set -euo pipefail
root='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-09_NEW_UPLOADS/20261009_194240000_iOS'
input='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/20261009_194240000_iOS.MP4'
mkdir -p "$root/evidence"
while read -r name time; do
  ffmpeg -nostdin -hide_banner -loglevel error -ss "$time" -i "$input" -frames:v 1 -q:v 3 "$root/evidence/${name}.jpg"
done <<'TIMES'
setup_hand 17.0
active_pair 23.6
opponent_research 28.6
soothing_shore 31.8
owner_turn 34.4
draw_mega_manectric 36.4
owner_research 40.0
draw_cyrus 42.4
draw_research 43.4
lightning_attach 45.2
coin_heads 48.0
weakness_60 51.2
point_award 56.2
victory 61.0
results 67.0
TIMES

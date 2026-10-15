#!/bin/bash
set -e
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs'
out="$base/Recording_QA/RULE_TEST_2026-10-09_HEAVY_HELMET/20261009_223237000_iOS/independent_sol"
for t in 77.5 185 190 207.5 211 212.5 214 217.5; do
  /usr/bin/ffmpeg -hide_banner -loglevel error -threads 1 -ss "$t" -i "$base/20261009_223237000_iOS.MP4" -frames:v 1 -q:v 2 "$out/exact_${t}s.jpg"
done

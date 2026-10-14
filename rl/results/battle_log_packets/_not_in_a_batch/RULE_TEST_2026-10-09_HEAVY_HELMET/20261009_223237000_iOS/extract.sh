#!/bin/bash
set -e
base='/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs'
packet="$base/Recording_QA/RULE_TEST_2026-10-09_HEAVY_HELMET/20261009_223237000_iOS"
mkdir -p "$packet/frames"
/usr/bin/ffmpeg -hide_banner -loglevel error -i "$base/20261009_223237000_iOS.MP4" -vf 'fps=1/5' -q:v 3 "$packet/frames/overview_%03d.jpg"

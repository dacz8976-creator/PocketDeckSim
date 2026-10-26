#!/bin/bash
cd /home/dacz8976/video_trial || exit 1
for f in briefs/*.md run_game.sh; do sed -i 's/\r$//' "$f"; done
ls briefs
head -2 run_game.sh

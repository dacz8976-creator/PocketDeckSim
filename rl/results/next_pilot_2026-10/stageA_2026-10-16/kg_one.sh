#!/bin/bash
# One kg_log call: O S SEED_BASE DECK DECK_PILOT OPP_PILOT GAMES OUTDIR (run from the repository root).
OPPS=(t-altaria t-blaziken t-hydreigon t-lucario t-sceptile t-suicune t-vespiquen t-weezing)
o=$1; s=$2; base=$3; deck=$4; dp=$5; op=$6; n=$7; dir=$8
nice -n 10 /home/dacz8976/stageA/bin/kg_log --deck "$deck" --opp "decks/screen/opponents/${OPPS[$o]}.txt" --deck-pilot "$dp" --opp-pilot "$op" \
    --seat "$s" --seed-base "$base" --games "$n" > "$dir/o${o}_s${s}.jsonl" 2> "$dir/o${o}_s${s}.err"

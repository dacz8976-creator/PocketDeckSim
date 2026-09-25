#!/usr/bin/env bash
# The Copycat / Darkness Claw / attack tallies in the report. From the repo root, with engine/ built.
# 250 games per bot, both sides the same bot; the first-named deck is always in seat 0.
set -euo pipefail
for pair in "hydreigon lucario 72130000 hvl" "blaziken sceptile 72090000 bvs"; do
  set -- $pair
  for bot in k3 b3n1; do
    engine/target/release/deckgym simulate --num 250 --seed "$3" --seed-stream --players "$bot,$bot" -p \
      "decks/research/$1.txt" "decks/research/$2.txt" -vv > "$4_attacks_$bot.log" 2>&1
    echo "== $1 v $2, $bot: $(grep -E '^Player 0 won' "$4_attacks_$bot.log")"
    echo "   Copycat $(grep -c 'trainer_card: B1 225 Copycat' "$4_attacks_$bot.log")"
    grep -o 'chose Attack(Attack { energy_required: \[[^]]*\], title: "[^"]*"' "$4_attacks_$bot.log" \
      | sed 's/.*title: //' | sort | uniq -c | sort -rn
  done
done

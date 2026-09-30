#!/bin/bash
# Card checks for the carrier lists, all on the official engine's programs (rl/engine-2026-09-30/, sha256 checked):
# every id through lib/card.py (one printing, no B4b), lib/deck_check.py, the goldfish coverage (card status, 0 games),
# and a legality scan: km3 on both sides, each list against the 8 panel lists, 10 games a pairing, on Claude diagnostic
# seeds 20,970,000,000 + pairing x 10,000 + i (outside START_HERE's ranges and the plan's carrier block 23,100,000,000).
# Usage: bash check_carriers.sh   (from anywhere; writes check_output.txt, coverage/, scan/)
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); ROOT=$(git -C "$HERE" rev-parse --show-toplevel); E=$ROOT/rl/engine-2026-09-30
cd "$ROOT"
(cd "$E" && sha256sum -c SHA256SUMS) || { echo "official programs do not match SHA256SUMS"; exit 1; }
LISTS="garchomp_meowth.txt alternates/togekiss_meowth.txt alternates/hisuian_goodra.txt alternates/houndoom_victini.txt fallback/coinflip_deck.txt fallback/coinflip_deck_padded.txt fallback/fire_victini.txt"
echo "== ids (lib/card.py): printings per id, and B4b"
for f in $LISTS; do
  tr -d '\r' < "$HERE/$f" | grep -v '^Energy:' | while read -r n rest; do
    id=$(echo "$rest" | awk '{print $(NF-1)" "$NF}')
    head=$(python3 lib/card.py "$id" 2>&1 | head -1)
    case "$id" in B4b*) b4b=" B4B" ;; *) b4b="" ;; esac
    echo "$f | $n x $id | $head$b4b"
  done
done
echo "== lib/deck_check.py files"
for f in $LISTS; do echo "$f: $(python3 lib/deck_check.py files "$HERE/$f" 2>&1 | tail -1)"; done
echo "== goldfish coverage (card status), 0 games"
mkdir -p "$HERE/coverage"
for f in $LISTS; do
  out="$HERE/coverage/$(basename "$f" .txt).json"
  "$E/goldfish" --deck "$HERE/$f" --games 0 --panel decks/screen/opponents --coverage "$out" > /dev/null 2>&1; echo "$f: exit $?"
done
echo "== legality scan: km3, each list v the 8 panel lists, 10 games a pairing"
mkdir -p "$HERE/scan"
{ printf 'pairing\theld_key\theld_file\topponent\tpanel_file\n'; p=0
  for f in $LISTS; do for o in altaria blaziken hydreigon lucario sceptile suicune vespiquen weezing; do
    printf '%s\t%s\t%s\tt-%s\tdecks/screen/opponents/t-%s.txt\n' $p "$(basename "$f" .txt)" "rl/results/engine_switch_rules_2026-10/carriers/$f" $o $o; p=$((p+1)); done; done
} > "$HERE/scan/pairs.tsv"
(cd "$ROOT/engine" && "$E/legality_scan" --pairs "$HERE/scan/pairs.tsv" --seed-base 20970000000 --games 10 --bot km3 \
  --games-out "$HERE/scan/games.jsonl" > "$HERE/scan/scan_page.txt" 2> "$HERE/scan/scan_stderr.txt"; echo "scan exit $?")
wc -l < "$HERE/scan/games.jsonl"

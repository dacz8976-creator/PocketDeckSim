#!/bin/bash
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
O="$R/rl/results/koa_2026-09-26/reading"
head -c 700 "$O/table_koa3.jsonl"; echo
head -c 700 "$O/b2e_koa3.jsonl"; echo
head -c 700 "$R/rl/results/kpf_2026-09-26/reading/b2e_kp3.jsonl"; echo
head -5 "$R/rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv"
sed -n '1,5p' "$R/rl/results/b2e_card_check_2026-09-26/limitless_cells.csv"
ls "$R/rl/results/b2e_rows_2026-09-26/" 2>/dev/null
head -c 500 "$R/rl/results/b2e_rows_2026-09-26/b2e_kp3_arch.jsonl" 2>/dev/null; echo
cd "$R" && python3 lib/card.py "B1 184" 2>&1 | head -5; python3 lib/card.py "B1 196" 2>&1 | head -5; python3 lib/card.py "B2b 040" 2>&1 | head -5
echo "=== grep Eevee in gauntlet/new decks ==="
grep -ril "eevee\|B1 184\|B1-184" "$R/decks/research" "$R/decks/gauntlet"* 2>/dev/null | head
ls "$R/decks/"

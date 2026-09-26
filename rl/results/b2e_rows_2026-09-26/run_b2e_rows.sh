#!/usr/bin/env bash
# The B2e rows (../b2e_card_check_2026-09-26/README.md section 4): all 96 pairings of b2e_pairings.tsv x 500 deals,
# k3 on both sides, then kp3 on both sides on the same deals, seeds 21,106,000,000 + pairing x 10,000 + i, even i =
# the held deck in seat 0. Runs only after run_b2e_identity.sh has written its IDENTITY PASS line for this very
# binary. Before the games: lib/deck_check.py on the twelve held files (the copies that are played). After them:
# b2e_checks.py rows (96 x 500 lines per file, seeds/seats/decks/pilots as the TSV, k3 and kp3 on the same deals,
# per-game findings = the log's).
# Usage (in WSL):  bash run_b2e_rows.sh        Time: about 1.7 h per pilot at cloud speed, more on the laptop.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/b2e_rows_2026-09-26"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
TSV=rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv
BASE=21106000000
GAMES=500
die() { echo "ROWS NOT RUN: $*" >&2; exit 1; }

# 0. Gates: the identity PASS for this binary; the played TSV = the repo's; the played copies = identity.txt's
#    hashes; no finished run overwritten.
[ -x "$SCAN" ] || die "no binary at $SCAN"
SHA=$(sha256sum "$SCAN" | cut -d' ' -f1)
[ -f "$D/identity_check.txt" ] || die "no identity_check.txt (run run_b2e_identity.sh first)"
[ "$(tail -n 1 "$D/identity_check.txt" | cut -d' ' -f1-3)" = "IDENTITY PASS $SHA:" ] \
  || die "identity_check.txt does not end in the IDENTITY PASS line for $SHA"
[ "$(head -n 1 "$D/identity.txt" | cut -d' ' -f1)" = "$SHA" ] || die "identity.txt names another binary"
cmp -s "$R/$TSV" "$B/$TSV" || die "the repo's $TSV changed since the build; rebuild or check it"
# The copies that are played (the TSV and its 20 deck files in $B) must still be the ones identity.txt records.
[ "$(wc -l < "$B/inputs_sha256.txt")" -eq 21 ] || die "$B/inputs_sha256.txt does not list the TSV and 20 deck files"
( cd "$B" && sha256sum --quiet -c inputs_sha256.txt ) || die "a played input in $B changed since the build"
while IFS= read -r line; do
  grep -qxF -e "$line" "$D/identity.txt" || die "identity.txt does not record: $line"
done < "$B/inputs_sha256.txt"
for bot in k3 kp3; do
  [ ! -e "$D/b2e_$bot.jsonl" ] || die "b2e_$bot.jsonl exists; move it away rather than overwrite it"
done

# 1. The held files, as played.
mapfile -t HELD < <(tail -n +2 "$R/$TSV" | cut -f4 | awk '!seen[$0]++')
[ "${#HELD[@]}" -eq 12 ] || die "expected 12 held files in the TSV, found ${#HELD[@]}"
( cd "$B" && python3 "$R/lib/deck_check.py" files "${HELD[@]}" ) > "$D/deck_check.txt" 2>&1 \
  || die "deck_check failed on the held files (deck_check.txt)"

# 2. The rows: k3, then kp3, same deals.
echo "scan binary $SHA" > "$D/rows_check.txt"
cd "$B/engine"
for bot in k3 kp3; do
  s=$(date +%s)
  nice -n 10 "$SCAN" --pairs "$B/$TSV" --seed-base "$BASE" --games "$GAMES" --bot "$bot" \
    --games-out "$D/b2e_$bot.jsonl" > "$D/b2e_$bot.txt" 2>&1 || die "the $bot rows exited non-zero (b2e_$bot.txt)"
  echo "b2e_$bot $(( $(date +%s) - s )) s wall ($(nproc) cores, $(date -u +%FT%TZ) end)" >> "$D/timing.txt"
done

# 3. The rows check.
python3 "$D/b2e_checks.py" rows "$R/$TSV" "$BASE" "$GAMES" "$D/b2e_k3.jsonl" "$D/b2e_kp3.jsonl" >> "$D/rows_check.txt" \
  || { tail -n 1 "$D/rows_check.txt"; exit 1; }
tail -n 1 "$D/rows_check.txt"

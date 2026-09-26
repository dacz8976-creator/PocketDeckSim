#!/usr/bin/env bash
# Stage the gauntlet runs' inputs in the B2e scan's tree (/home/dacz8976/engine-b2e-7fc6ccb), mirroring
# ../b2e_rows_2026-09-26/build_b2e_scan.sh: every TSV in tsv/ and every deck file a TSV names is played from the
# tree's copy at the SAME relative path as in the repo (the scan's --root defaults to '..' from the tree's engine/).
# - A file the tree already has (7fc6ccb's decks/research and decks/screen/opponents files, B2e's h- lists) must be
#   byte-identical to the working copy, or this stops.
# - A new file (decks/gauntlet_2026-09-26/*, l-charizardy.txt, the TSVs) is copied in. If a copy already exists and
#   differs from the working copy, this stops: remove that copy by hand to re-stage it deliberately.
# - Writes inputs_sha256.txt here (sha256 of the tree's copies, paths relative to the root; the run scripts check
#   it with sha256sum -c inside the tree and cmp each copy against the working copy) and inputs_source.txt (for each
#   file: in 7fc6ccb, committed at HEAD with the same bytes, or working copy only; the new files are not committed
#   yet, the laptop session commits them, and their committed bytes must hash to the same values).
# - Refuses unless the tree's scan binary is the one ../b2e_rows_2026-09-26/identity_check.txt passed.
# Plays nothing, builds nothing. Usage (WSL): bash stage_inputs.sh
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/gauntlet_runs_2026-09-26"
B=/home/dacz8976/engine-b2e-7fc6ccb
SCAN="$B/legality_scan_b2e_7fc6ccb"
die() { echo "STAGE FAILED: $*" >&2; exit 1; }

[ -x "$SCAN" ] || die "no scan at $SCAN"
SHA=$(sha256sum "$SCAN" | cut -d' ' -f1)
[ "$(tail -n 1 "$R/rl/results/b2e_rows_2026-09-26/identity_check.txt" | cut -d' ' -f1-3)" = "IDENTITY PASS $SHA:" ] \
  || die "the B2e identity_check.txt does not end in the IDENTITY PASS line for $SHA"
cd "$R"
python3 "$D/gauntlet_checks.py" tsvs > /dev/null || die "gauntlet_checks.py tsvs fails (run it to see why)"
mapfile -t TSVS < <(ls rl/results/gauntlet_runs_2026-09-26/tsv/*.tsv)
mapfile -t DECKS < <(for t in "${TSVS[@]}"; do tail -n +2 "$t" | cut -f4,6 | tr '\t' '\n'; done | sort -u)
for f in "${TSVS[@]}" "${DECKS[@]}"; do
  [ -f "$f" ] || die "$f is missing in the working copy"
  if [ -e "$B/$f" ]; then
    cmp -s "$f" "$B/$f" || die "$B/$f differs from the working copy's $f (remove the copy to re-stage it on purpose)"
  else
    mkdir -p "$(dirname "$B/$f")"
    cp "$f" "$B/$f"
  fi
done
( cd "$B" && sha256sum "${TSVS[@]}" "${DECKS[@]}" ) > "$D/inputs_sha256.txt"
for f in "${TSVS[@]}" "${DECKS[@]}"; do
  if git cat-file -e "7fc6ccb:$f" 2>/dev/null && git show "7fc6ccb:$f" | cmp -s - "$f"; then echo "$f  in 7fc6ccb (same bytes)"
  elif git cat-file -e "HEAD:$f" 2>/dev/null && git show "HEAD:$f" | cmp -s - "$f"; then echo "$f  committed at HEAD $(git log -1 --format=%h -- "$f") (same bytes)"
  else echo "$f  working copy only (not committed yet)"; fi
done > "$D/inputs_source.txt"
echo "staged ${#TSVS[@]} TSVs and ${#DECKS[@]} deck files in $B; scan $SHA"
echo "wrote $D/inputs_sha256.txt and inputs_source.txt"

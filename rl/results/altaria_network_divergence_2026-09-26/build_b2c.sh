#!/usr/bin/env bash
# Build net_divergence_kp (B2c for the Altaria detector network) in a scratch folder outside the repo: the engine at
# 7fc6ccb (main; the official engine's commit, rl/engine-2026-09-25/README.md) from git archive, plus ONE new file,
# engine/examples/net_divergence_kp.rs, copied from this folder. Nothing else in the tree is changed, and the repo's
# engine/ is not touched. Then cargo build --release --locked -j 4 --example net_divergence_kp, niced to 19.
# Checks before building: the scratch folder is new; 7fc6ccb has no file of that name; the Altaria and Lucario deck
# files in the archive equal the working copy's and the run's identity.json hashes (the decks the network games were
# played with); no other cargo build is running (the laptop has ~7.5 GB: one build at a time, so this waits).
# Usage (in WSL):  bash build_b2c.sh        Writes identity.txt beside this script.
#                  REBUILD=1 bash build_b2c.sh   re-copies the example into an existing scratch folder and rebuilds
#                  it there (only the example recompiles), after checking that the folder's engine/ and decks/ still
#                  equal 7fc6ccb's (tar --compare against git archive). Used by the review, Sept 26.
set -euo pipefail
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
D="$R/rl/results/altaria_network_divergence_2026-09-26"
C=7fc6ccb
B=/home/dacz8976/engine-b2c-$C
EX=net_divergence_kp
SRC="$D/$EX.rs"
RUN="$R/rl/runs/diag-altaria-lucario"
GAMES="$R/rl/results/altaria_network_readout/kp3_rows_games.jsonl"
die() { echo "BUILD FAILED: $*" >&2; exit 1; }

REBUILD=${REBUILD:-0}
if [ "$REBUILD" = 1 ]; then
  [ -d "$B/engine" ] || die "REBUILD=1 needs an existing $B (build once without REBUILD)"
else
  [ -e "$B" ] && die "$B already exists; remove it (rm -rf $B) to build from scratch, or REBUILD=1"
fi
[ -f "$SRC" ] || die "no source at $SRC"
[ -f "$GAMES" ] || die "no games file at $GAMES"
cd "$R"
git cat-file -e "$C^{commit}" || die "commit $C not found"
git cat-file -e "$C:engine/examples/$EX.rs" 2>/dev/null && die "$C already has engine/examples/$EX.rs"

# 0. One build at a time.
for _ in $(seq 1 240); do
  pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null || break
  echo "$(date '+%T') another cargo build is running; waiting" >&2
  sleep 30
done
if pgrep -x cargo >/dev/null || pgrep -x rustc >/dev/null; then die "another cargo build still running after 2 h"; fi

# 1. The source at 7fc6ccb, and the one new example file.
if [ "$REBUILD" = 1 ]; then
  [ "$(cat "$B/COMMIT")" = "$C $(git rev-parse "$C")" ] || die "$B/COMMIT is not $C"
  # tar --compare also lists mode/owner/time differences (the archive's are not the extracted files'); only a
  # content, size or missing-file line fails the check
  git archive "$C" engine decks | tar --compare -C "$B" > "$B/compare.txt" 2>&1 || true
  if grep -Ev ': (Mode|Uid|Gid|Mod time) differs$' "$B/compare.txt" | grep -q .; then
    grep -Ev ': (Mode|Uid|Gid|Mod time) differs$' "$B/compare.txt" | head -n 20 >&2
    die "$B no longer equals $C's engine/ and decks/"
  fi
else
  mkdir -p "$B"
  git rev-parse "$C" | sed "s/^/$C /" > "$B/COMMIT"
  git archive "$C" engine decks | tar -x -C "$B"
fi
cp "$SRC" "$B/engine/examples/$EX.rs"

# 2. The decks: the archive's copies = the working copy = the run's identity.json.
for d in altaria lucario; do
  f="decks/research/$d.txt"
  cmp -s "$f" "$B/$f" || die "$f in the working copy differs from $C's"
  want=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['sha256']['deck: $d'])" "$RUN/identity.json")
  got=$(sha256sum "$B/$f" | cut -d' ' -f1)
  [ "$got" = "$want" ] || die "$f sha256 $got is not the run's ($want)"
done

# 3. Build (nice 19, 4 jobs; --locked keeps 7fc6ccb's Cargo.lock exactly).
cd "$B/engine"
if ! { time nice -n 19 cargo build --release --locked -j 4 --example "$EX" ; } > "$B/build.txt" 2>&1; then
  tail -n 40 "$B/build.txt" >&2
  die "cargo build failed (log: $B/build.txt)"
fi
cp "target/release/examples/$EX" "$B/${EX}_$C"
SHA=$(sha256sum "$B/${EX}_$C" | cut -d' ' -f1)
HOW="built from git archive"
[ "$REBUILD" = 1 ] && HOW="rebuilt in place (REBUILD=1: tree checked equal to $C, only the example recompiled)"

# 4. identity.txt (the first line is the binary; run_b2c.sh reads it and the input lines).
{
  echo "$SHA  ${EX}_$C  ($B/${EX}_$C)"
  echo
  echo "source: $(cat "$B/COMMIT") (main; the official engine's commit) + engine/examples/$EX.rs from this folder"
  echo "example sha256: $(sha256sum "$SRC" | cut -d' ' -f1)"
  echo "official deckgym (rl/engine-2026-09-25/deckgym; not used here): $(sha256sum "$R/rl/engine-2026-09-25/deckgym" | cut -d' ' -f1)"
  echo "built $(date -u +%FT%TZ) with $(cargo --version), $(rustc --version); $HOW"
  echo
  echo "inputs (sha256):"
  ( cd "$B" && sha256sum decks/research/altaria.txt decks/research/lucario.txt )
  echo "$(sha256sum "$GAMES" | cut -d' ' -f1)  rl/results/altaria_network_readout/kp3_rows_games.jsonl"
} > "$D/identity.txt"
echo "built $B/${EX}_$C  sha256 $SHA"

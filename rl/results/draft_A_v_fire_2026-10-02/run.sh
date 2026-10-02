#!/usr/bin/env bash
# Draft A v the Fire list: plays the registered games (README.md beside this file) and writes RESULTS.md.
#
#   bash rl/results/draft_A_v_fire_2026-10-02/run.sh          play (resumable), then analyze.py report
#   bash rl/results/draft_A_v_fire_2026-10-02/run.sh --plan   every check except the commit check, then print the 40
#                                                             planned calls; plays nothing and writes nothing
#
# Linux only (WSL or the cloud), from a git checkout of the repository. It refuses before any game unless README.md,
# run.sh and analyze.py are committed and unmodified, the engine is the manifest's available release (main-8626a35,
# through current_engine.py) with the pinned hashes, floor.py has its pinned hash, and the three lists are the
# committed, pinned files. A finished chunk is never replayed; files are written as .part and renamed when complete.
set -euo pipefail
R="$(cd "$(dirname "$0")/../../.." && pwd -P)"; cd "$R"
D=rl/results/draft_A_v_fire_2026-10-02
export PYTHONDONTWRITEBYTECODE=1
PLAN=0; [ "${1:-}" = "--plan" ] && PLAN=1
refuse() { echo "REFUSED: $*" >&2; exit 2; }

# --- pinned identities (README sections 2 and 3) ----------------------------------------------------------------------
WANT_NAME=main-8626a35
WANT_DG=2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
WANT_GF=cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66
WANT_FLOOR=8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a
declare -A LIST=([draftA]=decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt
                 [deck13]=decks/dustin/13-a-ninetales-raticate.txt
                 [opponent]=rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt)
declare -A LIST_SHA=([draftA]=3f39092ba6680cc5b8013b961e2f5a0f07bc779816ade7a6891983082b2e7417
                     [deck13]=f79ad459a1188f10ba34be4606f3cbc60db21386e8ef91721c5506239653b6fa
                     [opponent]=07b98258ec896664f27d4722db83a26041d23230d598d8216115ba7a77b43cef)
declare -A LIST_BLOB=([draftA]=19331d7896e16728e6f727aad4a0941c6e7e94f8
                      [deck13]=f6de36a84f7199d70b64551edf756cdd1330bd20
                      [opponent]=ecb57120a4878d467303616a03f2eb703e0ff094)
SEED_BASE=23200000000   # seed = SEED_BASE + 500 x seat + i, i < 500, the same for both lists (README section 4)
PER_SEAT=500
CHUNK=50                # games per deckgym call; chunk c of a seat plays seeds base + 500 x seat + 50 x c .. + 49
PLAYERS=km3,km3

sha() { sha256sum < "$1" | cut -d' ' -f1; }
committed() {   # the file is in HEAD and the file on disk is byte for byte that blob (read-only: no index, no checkout)
  local head; head=$(git rev-parse -q --verify "HEAD:$1" 2>/dev/null) || return 1
  [ "$head" = "$(git hash-object "$1")" ]
}

# 1. the registration is committed before any game
for f in "$D/README.md" "$D/run.sh" "$D/analyze.py"; do
  if ! committed "$f"; then
    [ $PLAN = 1 ] && { echo "plan: $f is not committed yet (a real run refuses here)"; continue; }
    refuse "$f is not committed, or differs from its committed version: the registration comes before any game"
  fi
done

# 2. the engine is the manifest's available release, with the pinned hashes
eng=$(python3 -c 'import sys; sys.path.insert(0, "."); from current_engine import resolve; print(resolve(project="."))') \
  || refuse "current_engine.py refused the engine"
[ "$eng" = "$(realpath rl/engine-2026-10-02/deckgym)" ] || refuse "current_engine resolves $eng, not rl/engine-2026-10-02/deckgym"
read -r m_name m_sha m_gf m_gfsha < <(python3 -c 'import json; r = json.load(open("project_manifest.json"))["available_release"]; print(r["name"], r["sha256"], r["goldfish"], r["goldfish_sha256"])')
[ "$m_name" = "$WANT_NAME" ] || refuse "the manifest's available release is $m_name, not $WANT_NAME"
[ "$m_sha" = "$WANT_DG" ] && [ "$(sha "$eng")" = "$WANT_DG" ] || refuse "deckgym's sha256 is not the pinned $WANT_DG"
GF="$R/$m_gf"
[ "$m_gfsha" = "$WANT_GF" ] && [ "$(sha "$GF")" = "$WANT_GF" ] || refuse "goldfish's sha256 is not the pinned $WANT_GF"
[ "$(sha decks/screen/floor.py)" = "$WANT_FLOOR" ] || refuse "decks/screen/floor.py's sha256 is not the pinned $WANT_FLOOR"

# 3. the three lists are the committed, pinned files
for key in draftA deck13 opponent; do
  f=${LIST[$key]}
  [ "$(sha "$f")" = "${LIST_SHA[$key]}" ] || refuse "$f's sha256 is not the pinned ${LIST_SHA[$key]}"
  [ "$(git hash-object "$f")" = "${LIST_BLOB[$key]}" ] && committed "$f" || refuse "$f is not the committed blob ${LIST_BLOB[$key]}"
done

if [ $PLAN = 1 ]; then
  echo "plan: engine $m_name $eng; goldfish $GF; pilots $PLAYERS; checks passed"
  for tag in draftA deck13; do for seat in 0 1; do for ((c = 0; c < PER_SEAT / CHUNK; c++)); do
    seed=$((SEED_BASE + PER_SEAT * seat + CHUNK * c))
    if [ $seat = 0 ]; then p0=${LIST[$tag]}; p1=${LIST[opponent]}; else p0=${LIST[opponent]}; p1=${LIST[$tag]}; fi
    printf 'plan: %s seat %s chunk %02d: deckgym simulate --num %s --players %s --seed %s --seed-stream -p %s %s\n' \
      "$tag" "$seat" "$c" "$CHUNK" "$PLAYERS" "$seed" "$p0" "$p1"
  done; done; done
  exit 0
fi

exec 9> /tmp/draft_A_v_fire_2026-10-02.lock
flock -n 9 || refuse "another run.sh of this folder is running"
mkdir -p "$D/games" "$D/coverage"
{
  echo "== $(date -u '+%F %T') UTC run.sh start (chunks already finished are kept, never replayed)"
  echo "git HEAD $(git rev-parse HEAD)"
  echo "engine $m_name: $eng (current_engine.py resolves it)"
  sha256sum "$eng" "$GF" decks/screen/floor.py "$D/analyze.py" "$D/run.sh" "$D/README.md" current_engine.py \
    project_manifest.json lib/deckgym-database.json engine/src/players/public_pricing_player.rs \
    "${LIST[draftA]}" "${LIST[deck13]}" "${LIST[opponent]}"
  echo "$(python3 --version 2>&1); $(uname -srm); $(nproc) cores"
} >> "$D/provenance.txt"

# 4. the coverage of each list: the official goldfish's --coverage, floor.py's own call (no game is played)
for key in draftA deck13 opponent; do
  out="$D/coverage/${key}_coverage.json"
  [ -s "$out" ] && continue
  (cd engine && "$GF" --deck "$R/${LIST[$key]}" --panel "$R/decks/screen/opponents" --games 0 --coverage "$R/$out.part" > /dev/null)
  mv "$out.part" "$out"
done

# 5. the games: 2 lists x 2 seats x 10 chunks of 50; traces go to /tmp, are read by analyze.py extract, then deleted
TMPROOT=$(mktemp -d /tmp/dAvf_XXXXXX)
trap 'rm -rf "$TMPROOT"' EXIT
echo "$(date -u '+%F %T') games start" >> "$D/run.log"
for tag in draftA deck13; do for seat in 0 1; do for ((c = 0; c < PER_SEAT / CHUNK; c++)); do
  out="$D/games/${tag}_s${seat}_c$(printf %02d "$c").jsonl"
  [ -s "$out" ] && continue
  seed=$((SEED_BASE + PER_SEAT * seat + CHUNK * c))
  if [ $seat = 0 ]; then p0=${LIST[$tag]}; p1=${LIST[opponent]}; else p0=${LIST[opponent]}; p1=${LIST[$tag]}; fi
  T="$TMPROOT/call"; rm -rf "$T"; mkdir -p "$T"
  s=$(date +%s)
  nice -n 10 "$eng" simulate --num "$CHUNK" --players "$PLAYERS" --seed "$seed" --seed-stream \
    --data-output "$T/data" --results-output "$T/res" -p "$p0" "$p1" > "$T/stdout.txt" 2>&1 \
    || { tail -20 "$T/stdout.txt" >&2; refuse "deckgym failed for $out"; }
  nice -n 10 python3 "$D/analyze.py" extract --tmp "$T" --tag "$tag" --seat "$seat" --seed "$seed" --num "$CHUNK" \
    --coverage "$D/coverage/${tag}_coverage.json" --out "$out.part" >> "$D/run.log"
  mv "$out.part" "$out"
  rm -rf "$T"
  echo "$(date -u '+%F %T') $out: seeds $seed..$((seed + CHUNK - 1)), $(( $(date +%s) - s )) s" >> "$D/run.log"
done; done; done
n=$(ls "$D"/games/*.jsonl | wc -l)
[ "$n" = 40 ] || refuse "expected 40 chunk files, found $n"
echo "$(date -u '+%F %T') games done; report" >> "$D/run.log"

# 6. the page
python3 "$D/analyze.py" report --dir "$D" >> "$D/run.log"
echo "$(date -u '+%F %T') done" >> "$D/run.log"
echo "done: $D/RESULTS.md"

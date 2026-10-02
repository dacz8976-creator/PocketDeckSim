#!/usr/bin/env bash
# Draft A v the Fire list, the Wallace addendum: plays the registered games (ADDENDUM_WALLACE.md beside this file) and
# writes wallace/RESULTS.md. run.sh adapted to the one new list; the main test's files are read, never written.
#
#   bash rl/results/draft_A_v_fire_2026-10-02/run_wallace.sh          play (resumable), then analyze_wallace.py report
#   bash rl/results/draft_A_v_fire_2026-10-02/run_wallace.sh --plan   every check except the commit checks, then print
#                                                                     the 20 planned calls; plays and writes nothing
#
# Linux only (WSL or the cloud), from a git checkout of the repository. It refuses before any game unless
# ADDENDUM_WALLACE.md, run_wallace.sh, analyze_wallace.py and the Wallace list are committed and unmodified; README.md
# and analyze.py are the committed, registered files (analyze.py with the sha256 it was run with); the main test's 40
# game files are committed and unmodified (the pairing reads them); the engine is the manifest's available release
# (main-8626a35, through current_engine.py) with the pinned hashes; floor.py has its pinned hash; and the four lists
# are the committed, pinned files. A finished chunk is never replayed; files are written as .part and renamed.
set -euo pipefail
R="$(cd "$(dirname "$0")/../../.." && pwd -P)"; cd "$R"
D=rl/results/draft_A_v_fire_2026-10-02
W=$D/wallace
export PYTHONDONTWRITEBYTECODE=1
PLAN=0; [ "${1:-}" = "--plan" ] && PLAN=1
refuse() { echo "REFUSED: $*" >&2; exit 2; }

# --- pinned identities (ADDENDUM sections 2 and 3) ----------------------------------------------------------------------
WANT_NAME=main-8626a35
WANT_DG=2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e
WANT_GF=cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66
WANT_FLOOR=763278659ea9a1ac7983c9cd2da2ff5f1f2c1e96468818cb84b29c106bb4b1e0     # floor.py since 9e139e65 (ADDENDUM section 3)
WANT_ANALYZE=6ae4ec850f0a4678e03620be15b0a001b49cd910bfb2e55829f16c6422903563   # analyze.py as registered and run
declare -A LIST=([wallace]=decks/brews/drafts_2026-10-01/draft-A-wallace.txt
                 [draftA]=decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt
                 [deck13]=decks/dustin/13-a-ninetales-raticate.txt
                 [opponent]=rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt)
declare -A LIST_SHA=([wallace]=b5b66d02a0f20da6388ed90db83e6b72eb91134070795a0be36e6d5a3b0ab504
                     [draftA]=3f39092ba6680cc5b8013b961e2f5a0f07bc779816ade7a6891983082b2e7417
                     [deck13]=f79ad459a1188f10ba34be4606f3cbc60db21386e8ef91721c5506239653b6fa
                     [opponent]=07b98258ec896664f27d4722db83a26041d23230d598d8216115ba7a77b43cef)
declare -A LIST_BLOB=([wallace]=f231dc58051fdf35374892c06b9220f317f54201
                      [draftA]=19331d7896e16728e6f727aad4a0941c6e7e94f8
                      [deck13]=f6de36a84f7199d70b64551edf756cdd1330bd20
                      [opponent]=ecb57120a4878d467303616a03f2eb703e0ff094)
SEED_BASE=23200000000   # seed = SEED_BASE + 500 x seat + i, i < 500: the main test's deals (README section 4)
PER_SEAT=500
CHUNK=50                # games per deckgym call; chunk c of a seat plays seeds base + 500 x seat + 50 x c .. + 49
PLAYERS=km3,km3

sha() { sha256sum < "$1" | cut -d' ' -f1; }
committed() {   # the file is in HEAD and the file on disk is byte for byte that blob (read-only: no index, no checkout)
  local head; head=$(git rev-parse -q --verify "HEAD:$1" 2>/dev/null) || return 1
  [ "$head" = "$(git hash-object "$1")" ]
}
must_commit() {
  if ! committed "$1"; then
    [ $PLAN = 1 ] && { echo "plan: $1 is not committed yet (a real run refuses here)"; return 0; }
    refuse "$1 is not committed, or differs from its committed version: $2"
  fi
}

# 1. the addendum's registration is committed before any game; the main test's registration and games are unchanged
for f in "$D/ADDENDUM_WALLACE.md" "$D/run_wallace.sh" "$D/analyze_wallace.py" "${LIST[wallace]}"; do
  must_commit "$f" "the registration comes before any game"
done
for f in "$D/README.md" "$D/analyze.py"; do
  committed "$f" || refuse "$f differs from its committed version: the main test's registration must stay unchanged"
done
[ "$(sha "$D/analyze.py")" = "$WANT_ANALYZE" ] || refuse "analyze.py's sha256 is not the registered $WANT_ANALYZE"
n=0
for f in "$D"/games/*.jsonl; do
  committed "$f" || refuse "$f differs from its committed version: the pairing reads the recorded games"
  n=$((n + 1))
done
[ "$n" = 40 ] || refuse "expected the main test's 40 game files in $D/games, found $n"

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

# 3. the four lists are the pinned files (the Wallace list's commit is checked in step 1)
for key in wallace draftA deck13 opponent; do
  f=${LIST[$key]}
  [ "$(sha "$f")" = "${LIST_SHA[$key]}" ] || refuse "$f's sha256 is not the pinned ${LIST_SHA[$key]}"
  [ "$(git hash-object "$f")" = "${LIST_BLOB[$key]}" ] || refuse "$f is not the blob ${LIST_BLOB[$key]}"
  [ "$key" = wallace ] || committed "$f" || refuse "$f is not the committed blob ${LIST_BLOB[$key]}"
done

if [ $PLAN = 1 ]; then
  echo "plan: engine $m_name $eng; goldfish $GF; pilots $PLAYERS; checks passed"
  for seat in 0 1; do for ((c = 0; c < PER_SEAT / CHUNK; c++)); do
    seed=$((SEED_BASE + PER_SEAT * seat + CHUNK * c))
    if [ $seat = 0 ]; then p0=${LIST[wallace]}; p1=${LIST[opponent]}; else p0=${LIST[opponent]}; p1=${LIST[wallace]}; fi
    printf 'plan: wallace seat %s chunk %02d: deckgym simulate --num %s --players %s --seed %s --seed-stream -p %s %s\n' \
      "$seat" "$c" "$CHUNK" "$PLAYERS" "$seed" "$p0" "$p1"
  done; done
  exit 0
fi

exec 9> /tmp/draft_A_v_fire_2026-10-02_wallace.lock
flock -n 9 || refuse "another run_wallace.sh of this folder is running"
mkdir -p "$W/games" "$W/coverage"
{
  echo "== $(date -u '+%F %T') UTC run_wallace.sh start (chunks already finished are kept, never replayed)"
  echo "git HEAD $(git rev-parse HEAD)"
  echo "engine $m_name: $eng (current_engine.py resolves it)"
  sha256sum "$eng" "$GF" decks/screen/floor.py "$D/analyze.py" "$D/analyze_wallace.py" "$D/run_wallace.sh" \
    "$D/ADDENDUM_WALLACE.md" "$D/README.md" current_engine.py project_manifest.json lib/deckgym-database.json \
    engine/src/players/public_pricing_player.rs "${LIST[wallace]}" "${LIST[draftA]}" "${LIST[deck13]}" "${LIST[opponent]}"
  echo "$(python3 --version 2>&1); $(uname -srm); $(nproc) cores"
} >> "$W/provenance.txt"

# 4. the coverage of the Wallace list: the official goldfish's --coverage, floor.py's own call (no game is played)
out="$W/coverage/wallace_coverage.json"
if [ ! -s "$out" ]; then
  (cd engine && "$GF" --deck "$R/${LIST[wallace]}" --panel "$R/decks/screen/opponents" --games 0 --coverage "$R/$out.part" > /dev/null)
  mv "$out.part" "$out"
fi

# 5. the games: 2 seats x 10 chunks of 50; traces go to /tmp, are read by analyze_wallace.py extract, then deleted
TMPROOT=$(mktemp -d /tmp/dAvfW_XXXXXX)
trap 'rm -rf "$TMPROOT"' EXIT
echo "$(date -u '+%F %T') games start" >> "$W/run.log"
for seat in 0 1; do for ((c = 0; c < PER_SEAT / CHUNK; c++)); do
  out="$W/games/wallace_s${seat}_c$(printf %02d "$c").jsonl"
  [ -s "$out" ] && continue
  seed=$((SEED_BASE + PER_SEAT * seat + CHUNK * c))
  if [ $seat = 0 ]; then p0=${LIST[wallace]}; p1=${LIST[opponent]}; else p0=${LIST[opponent]}; p1=${LIST[wallace]}; fi
  T="$TMPROOT/call"; rm -rf "$T"; mkdir -p "$T"
  s=$(date +%s)
  nice -n 10 "$eng" simulate --num "$CHUNK" --players "$PLAYERS" --seed "$seed" --seed-stream \
    --data-output "$T/data" --results-output "$T/res" -p "$p0" "$p1" > "$T/stdout.txt" 2>&1 \
    || { tail -20 "$T/stdout.txt" >&2; refuse "deckgym failed for $out"; }
  nice -n 10 python3 "$D/analyze_wallace.py" extract --tmp "$T" --seat "$seat" --seed "$seed" --num "$CHUNK" \
    --coverage "$W/coverage/wallace_coverage.json" --out "$out.part" >> "$W/run.log"
  mv "$out.part" "$out"
  rm -rf "$T"
  echo "$(date -u '+%F %T') $out: seeds $seed..$((seed + CHUNK - 1)), $(( $(date +%s) - s )) s" >> "$W/run.log"
done; done
n=$(ls "$W"/games/*.jsonl | wc -l)
[ "$n" = 20 ] || refuse "expected 20 chunk files, found $n"
echo "$(date -u '+%F %T') games done; report" >> "$W/run.log"

# 6. the page
python3 "$D/analyze_wallace.py" report >> "$W/run.log"
echo "$(date -u '+%F %T') done" >> "$W/run.log"
echo "done: $W/RESULTS.md"

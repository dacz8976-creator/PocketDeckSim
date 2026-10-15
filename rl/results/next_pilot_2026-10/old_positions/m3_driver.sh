#!/bin/bash
# M3 (ky3 phase 1, the laptop): export the 25 old-engine decision states as pg_pos positions and keep those where km3 on the current
# engine makes the recorded km3 move in at least 7 of 12 seeds. Waits for 17:00 Central. Builds at nice 19 on the WSL disk.
set -uo pipefail
REPO="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
SP=/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/m3
W=/home/dacz8976/m3_work
OUT=$W/out
log() { echo "$(date -u +%FT%TZ) $*"; }
fail() { log "FAILED: $*"; touch $W/FAILED; exit 1; }
mkdir -p $W $OUT
unset KX_EXTRA_LISTS
log "m3 driver start"
while [ "$(TZ=America/Chicago date +%H)" -lt 17 ] && [ "$(TZ=America/Chicago date +%H)" -ge 7 ]; do sleep 300; done
log "17:00 Central passed: building"
FREE=$(df --output=avail -BG /mnt/c | tail -n 1 | tr -dc 0-9)
[ "$FREE" -ge 20 ] || fail "C: has ${FREE} GB free (needs 20)"
cd "$REPO" || fail "no repo"
G="git -c user.name=dacz8976-creator -c user.email=dacz8976@gmail.com"
$G fetch --no-auto-maintenance origin 2>&1 | tail -n 1
BR=$(git rev-parse --short=12 origin/sonnet/ky3-pilot); MAIN=$(git rev-parse --short=12 origin/main)
log "ky3-pilot $BR, main $MAIN"
SE=rl/results/next_pilot_2026-10/skip_export
git show d142d659:$SE/skip_replay.rs > $W/skip_replay.rs || fail "skip_replay.rs"
git show d142d659:$SE/skip_positions.py > $W/skip_positions.py || fail "skip_positions.py"
C=rl/results/strength_2026-10-08_kx3_combined
DEV=rl/results/strength_2026-10-03_kx3_dev
log "deck files against both manifests"
python3 - "$REPO" "$C/manifest.json" "$DEV/manifest.json" <<'PY' || fail "deck sha"
import hashlib, json, sys
repo = sys.argv[1]
for mp in sys.argv[2:]:
    m = json.load(open(f"{repo}/{mp}"))
    bad = [d["name"] for d in m["decks"] + m["opponents"] if hashlib.sha256(open(f"{repo}/{d['path']}", "rb").read()).hexdigest() != d["sha256"]]
    print(mp.split("/")[-2], "decks:", "all equal" if not bad else f"DIFFERENT {bad}")
    sys.exit(1) if bad else None
PY
build() {  # <commit> <name>
    rm -rf "$W/$2" && mkdir -p "$W/$2"
    git -C "$REPO" archive "$1" engine | tar -x -C "$W/$2"
    cp "$W/skip_replay.rs" "$W/$2/engine/examples/"
    (cd "$W/$2/engine" && CARGO_BUILD_JOBS=8 CARGO_TARGET_DIR="$W/target_$2" nice -n 19 cargo build --release --locked --example skip_replay 2>&1 | grep -E "^error|Finished") || return 1
    log "$2: commit $(git -C "$REPO" rev-parse --short=12 "$1"), engine tree $(git -C "$REPO" rev-parse --short=12 "$1:engine"), skip_replay $(sha256sum < "$W/target_$2/release/examples/skip_replay" | cut -c1-16)"
}
build 172cbe9c combined || fail "combined build"
build d513e37b frozen || fail "frozen build"
log "pg_pos on main's engine ($MAIN)"
H=rl/results/pause_games_decisions_2026-10-02/harness
rm -rf $W/pgbuild && mkdir -p $W/pgbuild
git archive origin/main engine | tar -x -C $W/pgbuild
for f in pgd_patch.py pg_pos.rs; do git show origin/main:$H/$f > $W/$f || fail "$f"; done
git show origin/main:$H/dg_patch.py > $W/dg_patch.py 2>/dev/null || git show origin/main:rl/results/pause_games_decisions_2026-10-02/c8c/dg_patch.py > $W/dg_patch.py 2>/dev/null
(cd $W && python3 -B $W/pgd_patch.py $W/pgbuild/engine) || fail "pgd_patch"
mkdir -p $W/pgbuild/engine/examples && cp $W/pg_pos.rs $W/pgbuild/engine/examples/pg_pos.rs
(cd $W/pgbuild/engine && CARGO_BUILD_JOBS=8 CARGO_TARGET_DIR=$W/target_pg nice -n 19 cargo build --release --locked --example pg_pos 2>&1 | grep -E "^error|Finished") || fail "pg_pos build"
cp $W/target_pg/release/examples/pg_pos $W/pg_pos
log "pg_pos main engine $(git rev-parse --short=12 origin/main:engine), sha $(sha256sum < $W/pg_pos | cut -c1-16)"
log "the requested games only"
python3 - "$REPO" "$SP" "$W" <<'PY' || fail "filter"
import json, sys
repo, sp, w = sys.argv[1:]
for run, d in (("comb", "strength_2026-10-08_kx3_combined"), ("dev", "strength_2026-10-03_kx3_dev")):
    keys = {l.split("\t")[1] for l in open(f"{sp}/requests_{run}.tsv").read().splitlines()[1:] if l.strip()}
    with open(f"{w}/games_{run}.jsonl", "w") as o:
        n = 0
        for line in open(f"{repo}/rl/results/{d}/games.jsonl"):
            if json.loads(line)["key"] in keys:
                o.write(line); n += 1
    print(run, n, "games for", len(keys), "keys")
    assert n == len(keys)
PY
cp $SP/requests_comb.tsv $SP/requests_dev.tsv $SP/cases.tsv $W/
log "export: combined run on the combined build"
$W/target_combined/release/examples/skip_replay --games $W/games_comb.jsonl --manifest $C/manifest.json --arm X --out $OUT/dec_comb.jsonl --check $OUT/check_comb.jsonl --export $W/requests_comb.tsv --pos-out $OUT/positions_comb.json --drop-out $OUT/dropped_export_comb.tsv 2> $OUT/stderr_comb.txt || fail "export comb"
log "export: development run on the frozen build"
$W/target_frozen/release/examples/skip_replay --games $W/games_dev.jsonl --manifest $DEV/manifest.json --arm X --out $OUT/dec_dev.jsonl --check $OUT/check_dev.jsonl --export $W/requests_dev.tsv --pos-out $OUT/positions_dev.json --drop-out $OUT/dropped_export_dev.tsv 2> $OUT/stderr_dev.txt || fail "export dev"
python3 - "$REPO" "$OUT" <<'PY' || fail "merge"
import json, sys
repo, out = sys.argv[1:]
pos = json.load(open(f"{out}/positions_comb.json")) + json.load(open(f"{out}/positions_dev.json"))
json.dump(pos, open(f"{out}/positions.json", "w"), indent=1)
names = {}
for d in ("strength_2026-10-08_kx3_combined", "strength_2026-10-03_kx3_dev"):
    m = json.load(open(f"{repo}/rl/results/{d}/manifest.json"))
    for x in m["decks"] + m["opponents"]:
        assert names.setdefault(x["name"], x["path"]) == x["path"], f"{x['name']} has two paths"
json.dump({"decks": [{"name": k, "path": v} for k, v in sorted(names.items())], "opponents": []}, open(f"{out}/manifest_merged.json", "w"), indent=1)
for c in ("comb", "dev"):
    ck = [json.loads(l) for l in open(f"{out}/check_{c}.jsonl")]
    print(c, len(ck), "games,", sum(x["replayed_exactly"] for x in ck), "replayed exactly")
print(len(pos), "positions exported")
PY
log "km3 on the current engine, 12 seeds"
python3 $W/skip_positions.py --positions $OUT/positions.json --manifest $OUT/manifest_merged.json --pg-pos $W/pg_pos --out $OUT/kept.json --dropped $OUT/dropped.tsv || fail "skip_positions"
cat $OUT/dropped_export_comb.tsv $OUT/dropped_export_dev.tsv $OUT/dropped.tsv
log "driver finished"
touch $W/DONE

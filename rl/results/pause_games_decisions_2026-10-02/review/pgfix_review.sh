#!/bin/bash
# Review of the cloud's pg_pos fix (claude/pensive-ptolemy-spwc0b 2aeaafad): new runner built on F's engine (cd20a97a); its tests; km3 on the
# kx3 study's 119 positions v the committed runs_km3 (must be byte-equal: those positions have no new field); the positions regenerated with the
# old and the new converter into a scratch folder (old must reproduce the committed file; new may differ only by the new fields); the 14
# Special-Condition positions loaded with --dump-state; the knock-out count against the opponent's points. Nothing is written into the checkout.
set -u
[ -f "$HOME/.cargo/env" ] && . "$HOME/.cargo/env"
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
W=$HOME/pgfix_review
FIX=2aeaafad
HD=rl/results/pause_games_decisions_2026-10-02/harness
HN=rl/results/pause_games_new_2026-10-12
Q=rl/results/pause_positions_kx3_2026-10
QA="/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA"
log() { echo "[$(date -u +%FT%TZ)] $*"; }
env | grep -qE '^DECKGYM_' && { log "STOP: DECKGYM_* set"; exit 1; }
cd "$R" || exit 1
rm -rf "$W"; mkdir -p "$W/F" "$W/dec" "$W/new" "$W/regen_old" "$W/regen_new" "$W/km3"
log "1. build the new runner on F (cd20a97a)"
git archive cd20a97a2e76897fae9883389cee4bf7ce5b3d97 engine | tar -x -C "$W/F" && find "$W/F" -type f -exec touch {} +
git show $FIX:$HD/pg_pos.rs > "$W/F/engine/examples/pg_pos.rs"
python3 -B "$HD/pgd_patch.py" "$W/F/engine" > "$W/patch.log" 2>&1 || { log "STOP: pgd_patch"; exit 1; }
(cd "$W/F/engine" && CARGO_TARGET_DIR="$W/target" nice -n 10 cargo build --release --locked --example pg_pos) > "$W/build.log" 2>&1 || { tail -n 30 "$W/build.log"; log "STOP: build"; exit 1; }
cp "$W/target/release/examples/pg_pos" "$W/pg_pos_F2"
log "built pg_pos_F2 sha256 $(sha256sum < "$W/pg_pos_F2" | cut -c1-16); pg_pos.rs $(git show $FIX:$HD/pg_pos.rs | sha256sum | cut -c1-16)"
log "2a. pg_pos tests"
git archive $FIX $HD | tar -x -C "$W/dec"
(cd "$W/dec/$HD" && PG_POS="$W/pg_pos_F2" python3 -m unittest test_pg_pos 2>&1 | tail -n 4)
log "2b. converter tests (real ledgers available here)"
git archive origin/main $HN | tar -x -C "$W/new"
git show $FIX:$HN/harness/ledger_to_positions.py > "$W/new/$HN/harness/ledger_to_positions.py"
git show $FIX:$HN/harness/test_ledger_to_positions.py > "$W/new/$HN/harness/test_ledger_to_positions.py"
(cd "$W/new/$HN/harness" && PG_CARD_DB="$R/engine/database.json" python3 -m unittest test_ledger_to_positions 2>&1 | tail -n 4)
log "3. km3 on the 119 with the new runner v the committed runs_km3"
DECKARGS=(); for f in "$HN"/decks/KW*.txt; do DECKARGS+=(--deck "$(basename "$f" .txt)=$f"); done
while read -r id; do
  [ -n "$id" ] || continue
  nice -n 10 "$W/pg_pos_F2" --positions "$HN/positions_all.json" "${DECKARGS[@]}" --seeds 1,2,3,4,5,6,7,8,9,10,11,12 --bot km3 --only "$id" > "$W/km3/out_$id.jsonl" 2> "$W/km3/err_$id.txt" || log "km3 failed on $id"
done < "$Q/run_ids.txt"
python3 - "$Q/run_ids.txt" "$W/km3" "$Q/runs_km3" <<'EOF'
import json, sys, os
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
strip = lambda r: {k: v for k, v in r.items() if k not in ("ms", "time", "elapsed", "wall_s")}
eq, bad = 0, []
for i in ids:
    a = [strip(json.loads(l)) for l in open(os.path.join(sys.argv[2], f"out_{i}.jsonl")) if l.strip()]
    b = [strip(json.loads(l)) for l in open(os.path.join(sys.argv[3], f"out_{i}.jsonl")) if l.strip()]
    if a == b: eq += 1
    else: bad.append(i)
print(f"km3, new runner v committed runs_km3: equal {eq} of {len(ids)}; differ {bad[:10]}")
EOF
log "4. positions regenerated with the old and the new converter (batches 06, 09, 11, as regenerate.sh), scratch only"
G=(); for b in "$QA"/BATCH_2026-10-0[69]_NEW_PAUSE_GAMES "$QA"/BATCH_2026-10-11_NEW_PAUSE_GAMES; do for d in "$b"/2026*; do [ -f "$d/TURN_LEDGER.json" ] && G+=("$d"); done; done
PG_CARD_DB="$R/engine/database.json" python3 -B "$HN/harness/ledger_to_positions.py" "$W/regen_old/positions_all.json" "$W/regen_old/report_convert.json" "${G[@]}" > "$W/regen_old.log" 2>&1 || log "old converter failed"
PG_CARD_DB="$R/engine/database.json" python3 -B "$W/new/$HN/harness/ledger_to_positions.py" "$W/regen_new/positions_all.json" "$W/regen_new/report_convert.json" "${G[@]}" > "$W/regen_new.log" 2>&1 || log "new converter failed"
python3 - "$HN/positions_all.json" "$W/regen_old/positions_all.json" "$W/regen_new/positions_all.json" "$Q/run_ids.txt" <<'EOF'
import json, sys, copy
com, old, new = (json.load(open(p)) for p in sys.argv[1:4])
ids = set(l.strip() for l in open(sys.argv[4]) if l.strip())
print(f"committed {len(com)}, old converter {len(old)}, new converter {len(new)} positions; old reproduces the committed file: {old == com}")
o, n = {p["id"]: p for p in old}, {p["id"]: p for p in new}
NOTE = "(not represented: the harness has no condition field)"
def norm(p, drop_notes):
    p = copy.deepcopy(p)
    p["me"].pop("knockouts", None); p["opp"].pop("knockouts", None)
    for s in ("me", "opp"):
        for b in p[s]["board"]:
            b.pop("conditions", None)
    if drop_notes:
        p["notes"] = "; ".join(x for x in str(p.get("notes") or "").split("; ") if NOTE not in x)
    return p
other = [i for i in o if i not in n or norm(o[i], True) != norm(n[i], False) and norm(o[i], True) != norm(n[i], True)]
print(f"positions differing beyond the new fields and the old condition note: {len(other)} {other[:8]}")
conds = [i for i in sorted(n) if any(b.get("conditions") for s in ("me", "opp") for b in n[i][s]["board"])]
print(f"positions with a condition now: {len(conds)}; of the study's 119: {sum(i in ids for i in conds)}")
for i in conds:
    print("  ", i, "in study" if i in ids else "-", {s: [(b['card'], b['conditions']) for b in n[i][s]['board'] if b.get('conditions')] for s in ("me", "opp")})
left = [i for i in sorted(n) if NOTE in str(n[i].get("notes"))]
print(f"positions still carrying the old 'not represented' note: {len(left)}")
bad_ko = [(i, n[i]["me"].get("knockouts"), n[i]["points"]) for i in sorted(n) if n[i]["me"].get("knockouts") is None
          or n[i]["me"]["knockouts"] > n[i]["points"][1] or (n[i]["points"][1] > 0 and n[i]["me"]["knockouts"] == 0)]
print(f"knock-out count v the opponent's points (count > points, or points > 0 with count 0, or no count): {len(bad_ko)}")
for r in bad_ko[:20]:
    print("  ", r)
from collections import Counter
print("count distribution:", sorted(Counter(n[i]["me"].get("knockouts") for i in n).items()))
json.dump(conds, open(sys.argv[3] + ".conds.json", "w"))
EOF
log "5. --dump-state on the condition positions (new converter's records, new runner)"
NDECK=(); for f in "$W/regen_new"/KW*.txt; do NDECK+=(--deck "$(basename "$f" .txt)=$f"); done
[ ${#NDECK[@]} -gt 0 ] || NDECK=("${DECKARGS[@]}")
for id in $(python3 -c "import json; print(' '.join(json.load(open('$W/regen_new/positions_all.json.conds.json'))))"); do
  "$W/pg_pos_F2" --positions "$W/regen_new/positions_all.json" "${NDECK[@]}" --seeds 1 --bot km3 --only "$id" --dump-state 2>/dev/null | python3 -c "import json,sys
for l in sys.stdin:
    r = json.loads(l)
    if r.get('kind') == 'state': print('  state', r['id'], 'knockouts', r['knockouts'], 'conditions', r['conditions'])
    if r.get('kind') == 'position' and r.get('problems'): print('  PROBLEMS', r['id'], r['problems'])"
done
log "DONE pgfix review"

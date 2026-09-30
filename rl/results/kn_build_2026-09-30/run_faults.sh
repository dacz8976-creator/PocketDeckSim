#!/bin/bash
# Plants one fault at a time, runs kn's tests, restores the file byte for byte.
cd /home/user/PocketDeckSim/engine
SP=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/kn_faults
run() { timeout 2400 cargo test --release --features test-utils --lib -- kn_tests kn3_from_get_player 2>&1 | grep -E "^error|test .*(ok|FAILED)$|test result" ; }
# Fault 1: N1 reads the opponent's printed Retreat Cost, not the board cost.
python3 - <<'PY'
from pathlib import Path
p=Path('src/players/value_functions.rs'); s=p.read_text()
a="        (opp.active_retreat_cost - my.active_retreat_cost) * params.active_retreat_cost\n"
b="        (state.maybe_get_active(opponent).and_then(|c| c.card.get_retreat_cost().map(|r| r.len())).unwrap_or(0) as f64 - my.active_retreat_cost) * params.active_retreat_cost\n"
assert s.count(a)==1; p.write_text(s.replace(a,b))
PY
echo "== fault 1: printed cost"; run
cp $SP/vf.orig src/players/value_functions.rs
# Fault 2: get_player gives kn km's value function.
python3 - <<'PY'
from pathlib import Path
p=Path('src/players/mod.rs'); s=p.read_bytes().decode()
a="PlayerCode::KN { .. } => Box::new(value_functions::public_clock_effect_kn_value_function),"
b="PlayerCode::KN { .. } => Box::new(value_functions::public_clock_effect_km_value_function),"
assert s.count(a)==1; p.write_bytes(s.replace(a,b).encode())
PY
echo "== fault 2: get_player wires kn to km"; run
cp $SP/mod.orig src/players/mod.rs
# Fault 3 (the test's own sensitivity): the move-for-move test's "N1 off" player has N1 on.
python3 - <<'PY'
from pathlib import Path
p=Path('src/players/value_functions.rs'); s=p.read_text()
a="                    value(state, myself, EvalFeatures { opponent_retreat_cost: false, ..EvalFeatures::KN })\n                }),"
b="                    value(state, myself, EvalFeatures { opponent_retreat_cost: true, ..EvalFeatures::KN })\n                }),"
assert s.count(a)==1; p.write_text(s.replace(a,b))
PY
echo "== fault 3: the test's N1-off player has N1 on"; run
cp $SP/vf.orig src/players/value_functions.rs
cmp src/players/value_functions.rs $SP/vf.orig && cmp src/players/mod.rs $SP/mod.orig && echo "restored byte for byte"

#!/bin/bash
# Plants one fault at a time in kr's code, runs kr's tests, restores the file byte for byte.
cd /home/user/PocketDeckSim/engine
SP=/tmp/claude-0/-home-user-PocketDeckSim/34d9e85d-3b01-5241-9ab7-1245e81714ba/scratchpad/kr_faults
run() { timeout 2400 cargo test --release --features test-utils -- kr_tests kr3_from_get_player kr3_on_the_ten 2>&1 | grep -E "^error|test .*(ok|FAILED)$|test result: FAILED|test result: ok. [1-9]" ; }
plant() { python3 - "$1" "$2" <<'PY'
import sys
from pathlib import Path
p=Path('src/players/value_functions.rs'); s=p.read_text(); a,b=sys.argv[1],sys.argv[2]
assert s.count(a)==1, a; p.write_text(s.replace(a,b))
PY
}
echo "== fault 1: Goo-zooka's effect counts whenever it is on the board (no liveness)"
plant "if !matches!(effect, CardEffect::IncreasedRetreatCost { .. }) || live {" "if !matches!(effect, CardEffect::IncreasedRetreatCost { .. }) || live || true {"
run; cp $SP/vf.orig src/players/value_functions.rs
echo "== fault 2: the Active's own candidates are charged too"
plant "for candidate in candidates.iter_mut().filter(|c| c.slot != 0) {" "for candidate in candidates.iter_mut() {"
run; cp $SP/vf.orig src/players/value_functions.rs
echo "== fault 3: kt_clocks gives each clock the other side's flag"
plant "let (c2_theirs, c2_mine) = (features.retreat_opponent_threat, features.retreat_own_threat);" "let (c2_theirs, c2_mine) = (features.retreat_own_threat, features.retreat_opponent_threat);"
run; cp $SP/vf.orig src/players/value_functions.rs
echo "== fault 4: the 200-deal test's \"C2 off\" player has C2 on"
plant "let off = EvalFeatures { retreat_opponent_threat: false, retreat_own_threat: false, ..EvalFeatures::KR };" "let off = EvalFeatures::KR;"
run; cp $SP/vf.orig src/players/value_functions.rs
cmp src/players/value_functions.rs $SP/vf.orig && echo "restored byte for byte"

#!/bin/bash
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
ls "$R/decks/gauntlet_2026-09-26/"
grep -n -i "eevee" "$R/decks/gauntlet_2026-09-26/card_check.json" | head
for f in "$R"/decks/gauntlet_2026-09-26/*.txt; do echo "== $f"; cat "$f"; done 2>/dev/null | head -120
echo "=== kpf new17 pairs ==="
head -c 600 "$R/rl/results/kpf_2026-09-26/reading/new17_kp3.jsonl"; echo
python3 - <<'EOF'
import json
R="/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim"
ps=set()
for l in open(R+"/rl/results/kpf_2026-09-26/reading/new17_kp3.jsonl"):
    g=json.loads(l); ps.add((g["pairing"],g["a"],g["b"],g.get("a_file"),g.get("b_file")))
for p in sorted(ps): print(p)
EOF

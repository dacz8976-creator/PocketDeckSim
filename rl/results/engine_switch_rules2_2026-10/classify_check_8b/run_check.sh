#!/usr/bin/env bash
# The switch-2 copies of classify_8c.py and coin_lookahead.py (this folder's parent), run on step 8b's changed games, against
# classify_8b.py's recorded verdicts (../early_warning_8b/classify_output.txt). Inputs: step 8b's work dir (run_8b.sh's: the 8b
# rows, the watch rows, root/, bin_old_vs_trace, bin_new_vs_trace) and a coin_probe_v2 built with precondition (a)'s round-2
# conditions (056158c3's coin_probe_v2.rs, on 31616338's engine) with that engine's source folder (the programs' working directory).
# Usage: run_check.sh <8b work dir> <coin_probe_v2 binary> <its engine folder> <scratch dir>
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
W8B=$1 PROBE=$2 ENG=$3 V=$4
rm -rf "$V" && mkdir -p "$V/c8c" "$V/cla"
# 1. classify_8c.py: a hand-off file of step 8b's changed games (any field of the old row differs), its exact and off-gate counters
#    from the watch rows; the work dir as classify_8c.py wants it.
ln -s "$W8B/root" "$V/c8c/root"
ln -s "$W8B/bin_old_vs_trace" "$W8B/bin_new_vs_trace" "$V/c8c/"
ln -s "$PROBE" "$V/c8c/bin_probe_coin_probe_v2"
for e in old new probe; do mkdir "$V/c8c/$e"; ln -s "$ENG" "$V/c8c/$e/engine"; done
python3 - "$W8B" "$HERE/../early_warning_8b/pairs_8b.tsv" "$V/c8c/handoff_8b.tsv" <<'PY'
import hashlib, json, sys
W, pairs_tsv, out = sys.argv[1:]
pairs = {int(c[0]): (c[3], c[5]) for c in (l.split("\t") for l in open(pairs_tsv).read().splitlines()[1:])}
blob = lambda p: (lambda d: hashlib.sha1(b"blob %d\0" % len(d) + d).hexdigest())(open(f"{W}/root/{p}", "rb").read())
with open(out, "w") as f:
    f.write("step\tbot\tpairing\ti\tseed\theld_file\theld_blob\tpanel_file\tpanel_blob\told_moves\tnew_moves\texact_counters\toffgate_counters\n")
    for bot in ("km3", "k3"):
        load = lambda kind: {(r["pairing"], r["i"]): r for r in map(json.loads, open(f"{W}/8b_{kind}_{bot}.jsonl"))}
        old, new, watch = load("old"), load("new"), load("watch")
        for k in sorted(old):
            if all(new[k].get(n) == v for n, v in old[k].items()):
                continue
            ex = {n: v.get("ticks", v) for n, v in watch[k].items() if isinstance(v, dict) and not n.startswith("offgate_")}
            off = {n: v.get("ticks", v) for n, v in watch[k].items() if isinstance(v, dict) and n.startswith("offgate_")}
            held, panel = pairs[k[0]]
            f.write("\t".join(map(str, ["8b", bot, k[0], k[1], old[k]["seed"], held, blob(held), panel, blob(panel), old[k]["moves"],
                                        new[k]["moves"], json.dumps(ex), json.dumps(off)])) + "\n")
PY
python3 "$HERE/../classify_8c.py" --work "$V/c8c" --tsv "$V/c8c/handoff_8b.tsv" --out "$HERE/classify_8c_out" --steps 8b --jobs 6 \
    --controls-from "$W8B" --controls-tag 8b > "$HERE/classify_8c_stdout.txt" 2>&1 && echo "classify_8c.py: exit 0" || echo "classify_8c.py: exit $?"
cp "$V/c8c/handoff_8b.tsv" "$HERE/"
# 2. coin_lookahead.py on one pairing (km3, pairing 35, all 40 deals), as a smoke directory.
P=$HERE/../early_warning_8b/pairs_8b.tsv
A=$W8B/root/$(awk -F'\t' '$1 == 35 {print $4}' "$P"); B=$W8B/root/$(awk -F'\t' '$1 == 35 {print $6}' "$P")
(cd "$ENG" && "$W8B/bin_old_vs_trace" --a "$A" --b "$B" --seed-base 23100000000 --pairing 35 --bot km3 --deals "$(seq -s, 0 39)" | gzip > "$V/cla/trace_old_8626a358.jsonl.gz")
(cd "$ENG" && "$W8B/bin_new_vs_trace" --a "$A" --b "$B" --seed-base 23100000000 --pairing 35 --bot km3 --deals "$(seq -s, 0 39)" | gzip > "$V/cla/trace_R.jsonl.gz")
python3 -c "import json, sys; [sys.stdout.write(l) for l in open(sys.argv[1]) if json.loads(l)['pairing'] == 35]" "$W8B/8b_watch_km3.jsonl" > "$V/cla/watch_R.jsonl"
(cd "$ENG" && python3 "$HERE/../coin_lookahead.py" --dir "$V/cla" --a "$A" --b "$B" --seed-base 23100000000 --probe "$PROBE" --bot km3 \
    --pairing 35) > "$HERE/coin_lookahead_output.txt" 2>&1 && echo "coin_lookahead.py: exit 0" || echo "coin_lookahead.py: exit $?"
# 3. Game for game against classify_8b.py's verdicts.
python3 - "$HERE" <<'PY'
import csv, re, sys
H = sys.argv[1]
old, bot, p = {}, None, None
for l in open(f"{H}/../early_warning_8b/classify_output.txt"):
    if m := re.match(r"^=+ *(km3|k3)|^(km3|k3):", l):
        bot = m[1] or m[2]
    if m := re.search(r"pairing (\d+)", l[:30]):
        p = int(m[1])
    if m := re.match(r"  i = +(\d+):.*=> (.*)$", l):
        old[(bot, p, int(m[1]))] = m[2].strip()
new = {(r["bot"], int(r["pairing"]), int(r["i"])): (r["verdict"], r["strict"]) for r in csv.DictReader(open(f"{H}/classify_8c_out/verdicts.tsv"), delimiter="\t")}
same = [k for k in new if old.get(k) == new[k][0]]
print(f"classify_8c.py v classify_8b.py: {len(same)} of {len(new)} verdicts the same ({len(old)} in classify_8b's output); "
      f"strict differs from the verdict in {sum(v != s for v, s in new.values())}")
for k in sorted(set(new) - set(same)):
    print(f"  DIFFERENT {k}: classify_8b {old.get(k)}, classify_8c {new[k]}")
look = re.findall(r"^i = +(\d+):.*=> (.*)$", open(f"{H}/coin_lookahead_output.txt").read(), re.M)
agree = sum(old.get(("km3", 35, int(i))) == v.split(" (STRICT")[0].strip() for i, v in look)
print(f"coin_lookahead.py (km3, pairing 35) v classify_8b.py: {agree} of {len(look)} verdicts the same")
PY

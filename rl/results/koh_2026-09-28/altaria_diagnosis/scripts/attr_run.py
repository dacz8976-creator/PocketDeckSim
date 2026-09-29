"""Attribution run: for each first-divergence row (same board, Altaria's decision), price the root actions with kog, kpf (R only),
kpha (R + A), kphb (R + B) and koh (R + A + B), and record which action each variant picks (last of ties, as the game does).
usage: attr_run.py <pairing> <shard> <nshards> <out>"""
import json, subprocess, sys, time, re
W = "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria"
pairing, shard, nsh, outfn = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
recs = json.load(open(W + "/rows/rows_all.json.stories.json"))
sel = [r for r in recs if int(r["p"]) == pairing and r.get("state_equal_at_div") in (True, "True") and int(r["div_actor"]) == int(r["alt_seat"])]
sel.sort(key=lambda r: int(r["i"]))
sel = sel[shard::nsh]
names = ["blaziken", "hydreigon", "lucario", "sceptile", "suicune", "vespiquen", "weezing"]
B = W + "/code/target/release/examples/altpos_orig"
E = W + "/code/eng/decks/research"
done = set()
try:
    for ln in open(outfn):
        try:
            done.add(json.loads(ln)["seed"])
        except Exception:
            pass
except FileNotFoundError:
    pass
out = open(outfn, "a")
t0 = time.time()
for r in sel:
    if r["seed"] in done:
        continue
    cmd = ["nice", "-n", "10", "env", "RAYON_NUM_THREADS=1", B, E + "/altaria.txt", E + f"/{names[pairing]}.txt", str(r["seed"]), str(r["alt_seat"]), str(r["div_k"]), "kog,kpf,kpha,kphb,koh", "kog", "1"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    picks = {}
    for ln in p.stdout.split("\n"):
        m = re.match(r"VARIANT (\w+): chosen .*= (.*)", ln)
        if m:
            picks[m.group(1)] = m.group(2).strip()
    out.write(json.dumps({"seed": r["seed"], "p": pairing, "delta": r["delta"], "kog_act": r["kog_act"].strip(), "koh_act": r["koh_act"].strip(), "cat": r.get("cat"), "picks": picks, "turn": r["div_turn"]}) + "\n")
    out.flush()
print("shard", shard, "rows", len(sel), "secs", round(time.time() - t0))

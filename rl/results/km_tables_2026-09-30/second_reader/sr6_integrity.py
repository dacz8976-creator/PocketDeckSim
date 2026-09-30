"""Item 8 (the rest of it): the program pins (programs.txt, STATUS.txt's 'KM PART B DONE' line, km_inputs.sha256,
the programs on the disk now); the eight reference files against km_config.json's sha256; the recorded input lists;
the committed state of the km folder (git); and the laptop's identity games replayed against their references with
this script's own comparison (Amendment 1 (e) item 3), plus km3's registered games against the laptop's km3
identity games on the same deals (determinism).
Writes OUT/sr6_integrity.txt."""
import sys, os, re, json, subprocess
sys.path.insert(0, "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/km_tables_2026-09-30/second_reader")
from sr_lib import *

lines = []
p = lines.append
cfg = json.load(open(CONFIG, encoding="utf-8"))

# ---------- programs
prog = {}
for ln in open(K + "/programs.txt", encoding="utf-8"):
    h, path = ln.split()
    prog[os.path.basename(path)] = (h, path)
status = open(K + "/STATUS.txt", encoding="utf-8").read()
m = re.search(r"KM PART B DONE \S+ \S+ B (\w+) deckgym (\w+) legality_scan (\w+) tool_census (\w+) \(tool source (\w+)\)", status)
st = {"deckgym": m.group(2), "legality_scan": m.group(3), "tool_census": m.group(4)}
p(f"PINS: STATUS 'KM PART B DONE' B = {m.group(1)} (config {cfg['build']['commit']}; equal {m.group(1) == cfg['build']['commit']}); tool source {m.group(5)} (config {cfg['counter_tool']['source_sha256']}; equal {m.group(5) == cfg['counter_tool']['source_sha256']})")
kin = open(K + "/km_inputs.sha256", encoding="utf-8").read()
for name in ("deckgym", "legality_scan", "tool_census"):
    h, path = prog[name]
    disk = sha(path) if os.path.exists(path) else "MISSING"
    p(f"  {name}: programs.txt {h[:16]}..; STATUS {st[name][:16]}..; km_inputs.sha256 lists it: {h in kin}; on the disk now {disk[:16]}..;"
      f" all equal: {h == st[name] == disk and h in kin}")
p(f"  Amendment 2's counter-tool program sha256 9e7bdc1b47b9eda6...: equal to the pin: {prog['tool_census'][0].startswith('9e7bdc1b47b9eda69540fd5263acbab7a1f081f7467db657af5fbb7def47f807')}")
for part in ("I", "T", "R"):
    n = len(re.findall(rf"KM PART {part} DONE 1f6319e", status))
    p(f"  STATUS 'KM PART {part} DONE' lines: {n}")

# ---------- reference files
p("REFERENCE FILES (kta3's, ec7e1a8) against km_config.json:")
for g, v in cfg["references"]["groups"].items():
    h = sha(KT + "/" + v["file"])
    p(f"  {g:>18}: {v['file']} sha256 equal to the config's: {h == v['sha256']}")
# km3's registered 45-cell files against the hashes recorded before the reading (STATUS line 60 / coverage_skip.txt)
for f, pref in (("km3_table.jsonl", "aff167ac8ca56054"), ("km3_new17.jsonl", "8623d6f958ab46bd")):
    h = sha(B + f)
    p(f"  1f6319e_{f}: sha256 {h[:16]}.. equal to the footprint line's {pref}: {h.startswith(pref)}")
p(f"  km_config.json sha256 prefix a352c04fcb588372 (STATUS): {sha(CONFIG).startswith('a352c04fcb588372')}")

# ---------- recorded input lists
for lst in ("km_inputs.sha256", "1f6319e_inputs_I.sha256", "1f6319e_inputs_T.sha256", "1f6319e_inputs_R.sha256"):
    ok = bad = 0
    badl = []
    for ln in open(K + "/" + lst, encoding="utf-8"):
        if ln.startswith("#") or not ln.strip():
            continue
        h, path = ln.split(None, 1)
        path = path.strip()
        full = path if path.startswith("/") else REPO + "/" + path
        if os.path.exists(full) and sha(full) == h:
            ok += 1
        else:
            bad += 1
            badl.append(path)
    p(f"  {lst}: {ok} files equal to their recorded sha256 now, {bad} not{': ' + ', '.join(badl) if badl else ''}")

# ---------- git: the folder as committed
def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True)
d = git("diff", "--stat", "18bd89c", "--", "rl/results/km_tables_2026-09-30", "rl/results/kt_tables_2026-09-28", "rl/results/trainer_pricing_2026-09-28/km_run/km_config.json")
p(f"GIT: tracked changes since 18bd89c in the km folder, kt's folder and km_config.json: {d.stdout.strip() or 'none'}")
s = git("show", "--stat", "--format=%h %s", "dac7dcf")
files = [l.split("|")[0].strip() for l in s.stdout.splitlines() if "|" in l]
p(f"  dac7dcf (footprint committed alone): files {files}")
hc = git("log", "-1", "--format=%h", "--", "rl/results/km_tables_2026-09-30/1f6319e_km3_table.jsonl")
p(f"  last commit touching 1f6319e_km3_table.jsonl: {hc.stdout.strip()}")

# ---------- identity replays (Amendment 1 (e) item 3), my own comparison
F15 = ("moves", "decisions", "openings", "winner_seat", "points", "seed", "first_seat", "first_deck_score", "a", "b", "a_file", "b_file", "turns")
REFT = by_key(rd(KT + "/ec7e1a8_kta3_table.jsonl"), pairing)
REFN = by_key(rd(KT + "/ec7e1a8_kta3_new17.jsonl"), pairing)
KMT = by_key(rd(B + "km3_table.jsonl"), pairing)
KMN = by_key(rd(B + "km3_new17.jsonl"), pairing)


def cmp(path, ref, bots=None, fields=F15):
    games = rd(path)
    n = dif = 0
    for g in games:
        r = ref[g["pairing"]][g["i"]]
        n += 1
        if bots:
            assert (g["bot_a"], g["bot_b"]) == bots
        if any(g.get(f) != r.get(f) for f in fields):
            dif += 1
    return n, dif


p("IDENTITY REPLAYS (my comparison on moves, decisions, openings, winner_seat, points, seed, first_seat, score, decks, files, turns):")
for f, ref, bots, note in (("laptop_id_kta3_table_i20.jsonl", REFT, ("kta3", "kta3"), "kta3 v kta3's table references"),
                           ("laptop_id_kta3_new17_i20.jsonl", REFN, ("kta3", "kta3"), "kta3 v kta3's new17 references"),
                           ("laptop_id_km3_table15_i20.jsonl", REFT, ("km3", "km3"), "km3 equal to kta3 on the 15 table cells with neither damage Stadium"),
                           ("laptop_id_km3_new13_i20.jsonl", REFN, ("km3", "km3"), "km3 equal to kta3 on the 13 new cells with neither damage Stadium"),
                           ("laptop_id_km3_table15_i20.jsonl", KMT, ("km3", "km3"), "the same games v km3's registered games (determinism)"),
                           ("laptop_id_km3_new13_i20.jsonl", KMN, ("km3", "km3"), "the same games v km3's registered games (determinism)"),
                           ("laptop_id_km3_smoke_i40.jsonl", KMT, ("km3", "km3"), "km3 smoke (pairings 0, 2, 19, i < 40) v km3's registered games")):
    n, dif = cmp(B + f, ref, bots)
    p(f"  {f}: {n} games, {dif} differ ({note})")
cloud = REPO + "/" + cfg["cloud_outputs"]["km3_smoke"]["path"]
if os.path.exists(cloud):
    cs = by_key(rd(cloud), pairing)
    n, dif = cmp(B + "laptop_id_km3_smoke_i40.jsonl", cs, ("km3", "km3"))
    p(f"  laptop km3 smoke v the cloud's smoke ({cfg['cloud_outputs']['km3_smoke']['path']}, sha256 equal to config: {sha(cloud) == cfg['cloud_outputs']['km3_smoke']['sha256']}): {n} games, {dif} differ")
else:
    p(f"  the cloud's km3 smoke file is not on this checkout ({cloud}); not compared")
for g, v in cfg["references"]["groups"].items():
    if g in ("table", "new17"):
        continue
    f = f"laptop_id_{g}_kta3_i20.jsonl"
    ref = by_key(rd(KT + "/" + v["file"]), pairing)
    n, dif = cmp(B + f, ref, ("kta3", "kta3"))
    p(f"  {f}: {n} games, {dif} differ (kta3 v {v['file']})")
write("sr6_integrity.txt", lines)

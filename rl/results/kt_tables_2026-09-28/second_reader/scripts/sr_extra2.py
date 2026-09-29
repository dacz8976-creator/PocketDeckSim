import sys
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_kt2/second-reader")
from sr_lib import *

LR = R + "/koh_2026-09-28/laptop_runs"
for code in ("kta3", "kt3"):
    print("###", code)
    def cnt(basep, mixp, key=pairing):
        b = load([basep], key); m = load([mixp], key)
        d = sum(m[p][i]["moves"] != b[p][i]["moves"] for p in b for i in b[p])
        return d, sum(len(c) for c in b.values())
    tot_d = tot_n = 0
    d, n = cnt(SCR + "/data/b2e_kog3.jsonl", f"{K}/{B}_mixed_b2e_{code}_first.jsonl")
    print(f"  B2e mixed (code on the B2e deck only), all 96 pairings: {d} of {n} games differ from kog3's")
    b = load([SCR + "/data/b2e_kog3.jsonl"], pairing); m = load([f"{K}/{B}_mixed_b2e_{code}_first.jsonl"], pairing)
    dh = sum(m[p][i]["moves"] != b[p][i]["moves"] for p in b if p < 48 for i in b[p])
    print(f"    held-out 0-47: {dh} of 24000")
    d, n = cnt(LR + "/scizor_kog3.jsonl", f"{K}/{B}_mixed_scizor_{code}_first.jsonl")
    print(f"  Scizor mixed (code on Scizor): {d} of {n}")
    for nm, bf in (("v-lucario_2", "v-lucario_2"), ("v-suicune_2", "v-suicune_2"), ("v-weezing_2", "v-weezing_2"), ("l-charizardy", "l-charizardy")):
        b = load([LR + f"/var_{bf}_kog3.jsonl"], pairing)
        dd = nn = 0
        for suf in ("a", "b"):
            pth = f"{K}/{B}_var_{nm}_{code}_mixed_{suf}.jsonl"
            if os.path.exists(pth):
                m = load([pth], pairing)
                for p in m:
                    for i in m[p]:
                        nn += 1
                        dd += m[p][i]["moves"] != b[p][i]["moves"]
        print(f"  second list {nm} (list side rows): {dd} of {nn} games differ")

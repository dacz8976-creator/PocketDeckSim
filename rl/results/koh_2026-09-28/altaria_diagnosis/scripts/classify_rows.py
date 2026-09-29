import json, sys, collections
sys.path.insert(0, "/mnt/c/Users/dacz8/AppData/Local/Temp/claude/C--Users-dacz8-Projects/1b119d13-736d-4588-ba63-0e9ef1756970/scratchpad/wf_altaria/positions")
from lib import *
from summ import *

rows = json.load(open(RES + "/koh_2026-09-28/laptop_reading/mechanism_rows.json"))
alt = [r for r in rows if r["deck"] == "altaria"]
seeds = {r["seed"] for r in alt}
T_ = {
    "kp3": load(DG + "/dump_base.txt", seeds),
    "kpf": load(DG + "/dump_kpf.txt", seeds),
    "koh": load(SCR + "/dump_koh_v_kog3.txt", seeds),
    "kog": load(SCR + "/dump_kog_v_kog3.txt", seeds),
}


def feats(tr, seat, T):
    acts = own_turn_summary(tr, seat, T)
    if acts is None:
        return None
    a, o, n = end_state(tr, seat, T)
    if a is None:
        return None
    atk = [x for x in acts if x.startswith("ATTACK")]
    ret = [x for x in acts if x.startswith("Retreat")]
    ev = [x for x in acts if x.startswith("Evolve")]
    att = [x for x in acts if x.startswith("Attach")]
    board = tuple(sorted((m["name"], m["e"]) for m in a["mons"]))
    return {"active": a["mons"][0]["name"], "act_e": a["mons"][0]["e"], "atk": atk[0][7:] if atk else "-", "ret": ret, "ev": ev, "att": att, "board": board,
            "actD": a["mons"][0]}


def label(fk, f3, ff):
    same3 = fk["board"] == f3["board"] and fk["active"] == f3["active"] and fk["atk"] == f3["atk"]
    samef = fk["board"] == ff["board"] and fk["active"] == ff["active"] and fk["atk"] == ff["atk"]
    if same3 and samef:
        return "same as both"
    if same3:
        return "= kp3 turn"
    if samef:
        return "= kpf turn"
    # Active-level classification
    return "neither"


out = []
for r in alt:
    seat = r["altaria_seat"]; T = r["turn"]
    fk = feats(pick(T_["koh"][r["seed"]], "first"), seat, T)
    f3 = feats(pick(T_["kp3"][r["seed"]], "first"), seat, T)
    ff = feats(pick(T_["kpf"][r["seed"]], "first"), seat, T)
    fg = feats(pick(T_["kog"][r["seed"]], "first"), seat, T)
    lab = label(fk, f3, ff) if fk and f3 and ff else "?"
    labg = label(fk, fg, ff) if fk and fg and ff else "?"
    out.append((r, fk, f3, ff, fg, lab, labg))
    def s(f):
        return f"{f['active']}[{f['act_e']}] atk={f['atk']} ret={[x[8:] for x in f['ret']]} ev={[x[7:] for x in f['ev']]}" if f else "?"
    print(f"{r['seed']} {r['slice'][:6]} T{T} mv={r.get('move')} | koh: {s(fk)}\n        kp3: {s(f3)}\n        kpf: {s(ff)}\n        label vs kp3/kpf: {lab} ; vs kog/kpf: {labg}")
print()
print(collections.Counter((r["slice"], lab) for r, fk, f3, ff, fg, lab, labg in out))
print(collections.Counter((r["slice"], r.get("move"), lab) for r, fk, f3, ff, fg, lab, labg in out))

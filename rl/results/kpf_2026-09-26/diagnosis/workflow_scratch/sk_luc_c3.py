"""Skeptic: are the analyst's cited example seeds members of the recounted patterns? plus overlap checks."""
from collections import Counter
from sk_luc_lib import load_cached, z2, binom_split, RIOLU_LINE, WALLS
out, _ = load_cached()
R = {r["seed"]: r for r in out}
name = lambda p: p["name"] if p else None
endA = lambda r, who: name(r[who]["end"]["active"])
unused = lambda r: r["div_in_own_turn"] and r["div_board"]["zone"].startswith("Some")


def wall_to(f, targets=tuple(RIOLU_LINE)):
    return any(x["from"] in WALLS and x["to"] in targets for x in f["retreats"])


def zcat(f):
    z = f["zone"]
    if z is None:
        return "none"
    if z["pos"] == 0:
        return "endActive"
    return "active_then_retreated" if z["slot"] == 0 else "bench"


za = lambda f: f["zone"] is not None and not f["zone"]["before_k"]
teary = lambda f: "ATTACK Teary Attack" in f["attacks"]
P = {
    "P1": lambda r: endA(r, "kpf") in RIOLU_LINE and endA(r, "kp3") in WALLS,
    "P2": lambda r: wall_to(r["kpf"]) and not wall_to(r["kp3"]),
    "P3": lambda r: teary(r["kp3"]) and not teary(r["kpf"]),
    "P4": lambda r: unused(r) and zcat(r["kpf"]) == "endActive" and zcat(r["kp3"]) != "endActive",
    "P5": lambda r: unused(r) and r["kpf_cat"] == "RETREAT" and r["kpf"]["retreats"] and r["kpf"]["retreats"][0]["from"] in WALLS
    and r["kpf"]["retreats"][0]["to"] in RIOLU_LINE and r["kpf"]["zone"] is not None and not r["kpf"]["zone"]["before_k"]
    and r["kpf"]["zone"]["pos"] != 0,
    "P6": lambda r: endA(r, "kpf") in WALLS and endA(r, "kp3") in RIOLU_LINE,
    "P7": lambda r: za(r["kpf"]) and za(r["kp3"]) and r["kpf"]["zone"]["slot"] == 0 and r["kp3"]["zone"]["slot"] != 0,
    "P8": lambda r: name(r["div_board"]["active"]) == "Hitmonlee",
}
cited = {
    "P1": [72130094, 72190009, 72190005, 72080070, 72180053, 72020010],
    "P2": [72130094, 72080079, 72190049, 72180092, 72020137, 72190011],
    "P3": [72080079, 72190060, 72180092, 72130094],
    "P4": [72130094, 72190005, 72080070, 72080079],
    "P5": [72130061, 72180048, 72200010, 72200037, 72200129, 72020086],
    "P6": [72020118, 72080063, 72130056, 72130081, 72080143, 72020025],
    "P7": [72020010, 72130094, 72020018, 72020072],
    "P8": [72080055, 72080059, 72020148, 72080039],
}
for p, seeds in cited.items():
    res = []
    for s in seeds:
        r = R.get(s)
        res.append(f"{s}:{r['kind'][0] if r else '?'}:{'Y' if r and P[p](r) else 'N'}")
    print(p, " ".join(res))
for s in (72130094, 72190005, 72080070, 72180053, 72190049, 72180092, 72190011, 72190060, 72020137):
    r = R[s]
    print(s, r["kind"], "div active", name(r["div_board"]["active"]), "| kp3 end", endA(r, "kp3"), r["kp3"]["acts"][:7],
          "| kpf end", endA(r, "kpf"), r["kpf"]["acts"][:7])

# overlap of the harm patterns
W = [r for r in out if r["kind"] == "worse"]
B = [r for r in out if r["kind"] == "better"]
for grp, lab in ((W, "worse"), (B, "better")):
    c = Counter()
    for r in grp:
        c[tuple(k for k in ("P1", "P2", "P3") if P[k](r))] += 1
    print(lab, "overlap P1/P2/P3:", dict(c))
# conditional on Bonsly active at divergence
for lab, grp in (("worse", W), ("better", B)):
    bon = [r for r in grp if name(r["div_board"]["active"]) == "Bonsly"]
    print(lab, "Bonsly@div", len(bon), "kpf drops Teary where kp3 uses it:", sum(P["P3"](r) for r in bon),
          "kpf end active Riolu line & kp3 wall:", sum(P["P1"](r) for r in bon),
          "kp3 teary:", sum(teary(r["kp3"]) for r in bon), "kpf teary:", sum(teary(r["kpf"]) for r in bon))
    hit = [r for r in grp if name(r["div_board"]["active"]) == "Hitmonlee"]
    print(lab, "Hitmonlee@div", len(hit), "P1:", sum(P["P1"](r) for r in hit), "P6-like (kp3 Riolu line end):",
          sum(P["P6"](r) for r in hit))
    rio = [r for r in grp if name(r["div_board"]["active"]) in RIOLU_LINE]
    print(lab, "RioluLine@div", len(rio), "P6:", sum(P["P6"](r) for r in rio), "P1:", sum(P["P1"](r) for r in rio))

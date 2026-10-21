"""Print the distinct plans (with seed counts) of km3, kmbc3 and kmbd3 at the item 7 cases, keep checks and other changed turns."""
import json, os, collections
O = "/home/dacz8976/stageA/out"
CASES = [("3", "KW-261013_010837000-t07"), ("4", "KW-261012_225319000-t06"), ("5", "KW-261013_014423000-t07"), ("6", "KW-261013_015659000-t05"),
         ("7", "KW-261013_010837000-t09"), ("9", "KW-261012_210041000-t06"), ("10", "KW-261012_203719000-t07"), ("11", "KW-261012_210823000-t08"),
         ("12", "KW-261012_010706000-t11"), ("13", "KW-261013_010837000-t05"), ("14", "KW-261013_014423000-t03"), ("15", "KW-261012_203719000-t11"),
         ("keep RC", "KW-261012_010706000-t05"), ("keep RC", "KW-261012_210823000-t06"), ("keep RC", "KW-261012_230258000-t09"),
         ("keep line", "KW-261012_203719000-t13"), ("other", "KW-261012_010706000-t13"), ("other", "KW-261012_203719000-t09"),
         ("other", "KW-261012_225319000-t04"), ("other", "KW-261013_015659000-t03"), ("other", "KW-261012_203719000-t03"),
         ("other", "KW-261012_210823000-t04"), ("other", "KW-261013_020824000-t05"), ("other", "KW-261012_210041000-t08")]


def plans(arm, tid):
    p = f"{O}/pos_{arm}/out_{tid}.jsonl"
    c = collections.Counter()
    first = None
    for line in open(p):
        j = json.loads(line)
        if j.get("kind") == "free":
            c[(tuple(j.get("plan") or []), j.get("cut"))] += 1
        if j.get("kind") == "position" and first is None:
            first = j.get("summary")
    return c, first


for label, tid in CASES:
    print(f"\n######## case {label}: {tid}")
    for arm in ("km3", "kmbc3", "kmbd3"):
        c, summ = plans(arm, tid)
        if arm == "km3" and summ:
            me = summ["me"]
            print("   board:", [(b["slot"], b["card"], len(b["energy"]), b["hp"], b.get("tools")) for b in me["board"]], "hand:", me["hand"])
        for (plan, cut), n in c.most_common():
            print(f"   {arm:6} {n:2}/12 cut={cut}: {' > '.join(plan)}")

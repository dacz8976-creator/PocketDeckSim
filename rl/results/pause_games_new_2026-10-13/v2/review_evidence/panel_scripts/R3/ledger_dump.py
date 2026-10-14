import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/"
paths = {
 "210041": QA + "BATCH_2026-10-12_NEW_LONG_VIDEOS/20261012_210041000_iOS/TURN_LEDGER.json",
 "230258": QA + "BATCH_2026-10-12_ADDITIONAL_TWO/20261012_230258000_iOS/TURN_LEDGER.json",
}
DROP = {"evidence_ids", "source_video", "timestamp_seconds", "basis", "source_local_interval_seconds", "turn_evidence_ids",
        "discard_snapshot_ids", "timing", "count_method", "reveal_position"}

def strip(o):
    if isinstance(o, dict):
        return {k: strip(v) for k, v in o.items() if k not in DROP and v not in (None, [], {}, "")}
    if isinstance(o, list):
        return [strip(x) for x in o]
    return o

g = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else "all"
d = json.load(open(paths[g], encoding='utf-8'))
if which == "top":
    for k, v in d.items():
        if k != "turns":
            print(k, json.dumps(strip(v), ensure_ascii=False, indent=1))
    sys.exit()
for t in d["turns"]:
    if which != "all" and str(t["turn_number"]) not in which.split(","):
        continue
    print("#" * 30, "TURN", t["turn_number"], t["who_played"])
    print(json.dumps(strip(t), ensure_ascii=False, indent=1))

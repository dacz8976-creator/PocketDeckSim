import json
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/"
d = json.load(open(base + "20261013_014423000_iOS/TURN_EVIDENCE.json", encoding="utf-8"))
for c in d["owner_turn_captures"]:
    print(json.dumps(c, ensure_ascii=False)[:2500])
    print("-" * 40)
d = json.load(open(base + "20261013_010837000_iOS/TURN_EVIDENCE.json", encoding="utf-8"))
print(json.dumps(d["discard_snapshots"], ensure_ascii=False)[:2000])
print(json.dumps(d["frames"][0], ensure_ascii=False)[:1500])
# frames mentioning Thieving / Grass / opponent energy zone
import re
for f in d["frames"]:
    t = json.dumps(f, ensure_ascii=False)
    if re.search(r"Thieving|Incisor|Grass|Ilima|timeout|Victory", t):
        print(t[:700])

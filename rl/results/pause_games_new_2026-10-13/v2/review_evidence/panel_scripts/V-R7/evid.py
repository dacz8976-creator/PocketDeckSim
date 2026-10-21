import json, sys
QA = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/20261013_015659000_iOS"
ev = json.load(open(f"{QA}/TURN_EVIDENCE.json"))
want = set(sys.argv[1].split(","))
print(type(ev), list(ev.keys())[:10] if isinstance(ev, dict) else len(ev))
def walk(x, path=""):
    if isinstance(x, dict):
        idv = x.get("id") or x.get("evidence_id")
        if idv in want:
            print("==", path, json.dumps(x, ensure_ascii=False)[:1500])
        for k, v in x.items():
            walk(v, path + "/" + str(k))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            walk(v, path + f"[{i}]")
walk(ev)
# also grep raw text for Rare Candy
raw = open(f"{QA}/TURN_EVIDENCE.json", encoding="utf-8").read()
import re
for m in re.finditer(r"(?i)rare candy", raw):
    print("RC:", raw[max(0, m.start()-300):m.end()+300].replace("\n", " "))
    print("----")

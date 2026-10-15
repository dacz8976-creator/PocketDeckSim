import json, re, sys
base = "/mnt/c/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/BATCH_2026-10-13_REMAINING_SIX/"
for g in ["20261013_010837000_iOS", "20261013_014423000_iOS"]:
    d = json.load(open(base + g + "/TURN_EVIDENCE.json", encoding="utf-8"))
    print("=" * 60, g, type(d))
    if isinstance(d, dict):
        for k, v in d.items():
            print(k, type(v).__name__, (len(v) if hasattr(v, "__len__") else v) if not isinstance(v, str) else v[:200])
        items = None
        for k, v in d.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                items = v
                print("first item of", k, json.dumps(v[0], ensure_ascii=False)[:1500])
                break
    # search text for hand count / opponent hand statements
    txt = json.dumps(d, ensure_ascii=False)
    for pat in [r"opponent hand[^\"]{0,120}", r"fan[^\"]{0,100}", r"Grass[^\"]{0,100}", r"full-art[^\"]{0,120}", r"B3a 078[^\"]{0,100}"]:
        hits = re.findall(pat, txt, re.I)
        print(pat, len(hits))
        for h in hits[:12]:
            print("   ", h)

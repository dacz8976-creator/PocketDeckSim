import json, re
base = "/mnt/c/Users/dacz8/Projects/Pocket Deck Sim/PocketDeckSim/rl/results/pause_games_new_2026-10-12/review_evidence/"
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + f"[{i}]")
    else:
        yield path, o
for f in ("verify_panel_output.json", "reader_panel_output.json"):
    D = json.load(open(base + f, encoding="utf-8"))
    print("#####", f)
    seen = set()
    for path, v in walk(D):
        if isinstance(v, str) and re.search(r"energy_next|next Energy|opponent's next", v):
            # print the parent finding
            key = path.rsplit("/", 1)[0]
            if key in seen:
                continue
            seen.add(key)
            print("---", path)
            print(v[:1500])

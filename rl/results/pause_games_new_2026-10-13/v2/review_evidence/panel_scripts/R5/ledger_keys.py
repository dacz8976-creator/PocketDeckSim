import json, sys
p = sys.argv[1]
d = json.load(open(p, encoding="utf-8"))
def show(o, depth=0, maxd=3):
    if depth > maxd:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            t = type(v).__name__
            ln = len(v) if isinstance(v, (list, dict, str)) else ""
            print("  " * depth + f"{k}: {t} {ln}")
            if isinstance(v, (dict, list)):
                show(v, depth + 1, maxd)
    elif isinstance(o, list) and o:
        show(o[0], depth + 1, maxd)
show(d, 0, int(sys.argv[2]) if len(sys.argv) > 2 else 3)

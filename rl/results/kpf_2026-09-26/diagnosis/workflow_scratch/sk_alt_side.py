import re
MONRX = re.compile(r"^(.+?) (\d+)hp((?: [A-Z]{3})*) E\[([A-Za-z]*)\]$")


def side(s):
    parts = s.split(" | ")
    head = parts[0]
    m = re.match(r"Z(\S+)/(\S+) D(\d+) H(\d+) P(\d+)", head)
    act = parts[1].strip() if len(parts) > 1 else "-"
    bench = parts[2].strip() if len(parts) > 2 else ""

    def mon(x):
        mm = MONRX.match(x.strip())
        return None if not mm else (mm.group(1), int(mm.group(2)), mm.group(3).strip(), mm.group(4))
    a = None if act in ("-", "") else mon(act)
    b = [mon(x) for x in re.findall(r"[^,]+?hp(?: [A-Z]{3})* E\[[A-Za-z]*\]", bench)]
    return {"zc": m.group(1), "zn": m.group(2), "D": int(m.group(3)), "H": int(m.group(4)), "P": int(m.group(5)),
            "a": a, "b": [x for x in b if x]}

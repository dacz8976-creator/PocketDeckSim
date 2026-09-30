#!/usr/bin/env python3
"""checker-a, step 2 (run only after check_a.txt was written): compare check_a.txt with thresholds.json
and append the comparison to check_a.txt. Parses check_a.txt's own printed figures; recomputes nothing."""
import hashlib
import json
import re
import sys

check_txt, thr_json = sys.argv[1], sys.argv[2]
text = open(check_txt, encoding="utf-8").read()
thr = json.load(open(thr_json, encoding="utf-8"))

mine = {}
for block in re.split(r"^=+$", text, flags=re.M)[1:]:
    name = re.search(r"^(M[12])\s", block.strip(), flags=re.M).group(1)
    d = {}
    for arm, lab in (("kta3", r"kta3:"), ("km3", r"km3: ")):
        m = re.search(r"^\s+%s\s*offered (\d+), played (\d+)" % lab, block, flags=re.M)
        d[arm] = {"offered": int(m.group(1)), "played": int(m.group(2))}
    m = re.search(r"R_kta3 = \d+/\d+ = (\S+)\s+\((\S+)\)", block); d["kta3"]["rate"], d["kta3"]["rate_display"] = m.group(1), m.group(2)
    m = re.search(r"R_km3  = \d+/\d+ = (\S+)\s+\((\S+)\)", block); d["km3"]["rate"], d["km3"]["rate_display"] = m.group(1), m.group(2)
    m = re.search(r"T = \(R_kta3 \+ R_km3\) / 2 = (\S+)\s+\((\S+)\)", block); d["T"], d["T_display"] = m.group(1), m.group(2)
    d["lower"] = re.search(r"lower bound: (\S+)", block).group(1)
    d["upper"] = re.search(r"upper bound: (\S+)", block).group(1)
    d["idx"] = [int(x) for x in re.search(r"lower = sorted\[(\d+)\], upper = sorted\[(\d+)\]", block).groups()]
    d["zero"] = int(re.search(r"difference set to 0.0\): (\d+)", block).group(1))
    d["result"] = "cannot pass" if "CANNOT PASS" in block else "threshold"
    mine[name] = d

rows = []
def cmp(label, a, b):
    ok = (a == b)
    rows.append(("AGREE" if ok else "DISAGREE", label, a, b))
    return ok

ins = thr["inputs"]
for arm, fn in (("kta3", "1f6319e_sample_kta3_rows.jsonl"), ("km3", "1f6319e_sample_km3_rows.jsonl")):
    m = re.search(r"%s\s+sha256 (\w+)\s+rows (\d+)" % re.escape(fn), text)
    cmp("input %s sha256" % arm, m.group(1), ins[arm]["sha256"])
    cmp("input %s rows" % arm, int(m.group(2)), ins[arm]["rows"])
cmp("python version", re.search(r"^python: (\S+)", text, flags=re.M).group(1), thr["python"])

for name in ("M1", "M2"):
    t, d = thr["lines"][name], mine[name]
    for arm in ("kta3", "km3"):
        cmp("%s %s offered" % (name, arm), d[arm]["offered"], t[arm]["offered"])
        cmp("%s %s played" % (name, arm), d[arm]["played"], t[arm]["played"])
        cmp("%s %s rate (exact fraction)" % (name, arm), d[arm]["rate"], t[arm]["rate"])
        cmp("%s %s rate display" % (name, arm), d[arm]["rate_display"], t[arm]["rate_display"])
    cmp("%s T (exact fraction)" % name, d["T"], t["T"])
    cmp("%s T display" % name, d["T_display"], t["T_display"])
    cmp("%s lower bound (repr)" % name, d["lower"], t["interval_detail"]["lower_repr"])
    cmp("%s upper bound (repr)" % name, d["upper"], t["interval_detail"]["upper_repr"])
    cmp("%s lower bound (float, bitwise)" % name, float(d["lower"]).hex(), float(t["interval"][0]).hex())
    cmp("%s upper bound (float, bitwise)" % name, float(d["upper"]).hex(), float(t["interval"][1]).hex())
    cmp("%s sorted elements used" % name, d["idx"], t["interval_detail"]["sorted_elements"])
    cmp("%s zero-offered replicates" % name, d["zero"], t["interval_detail"]["zero_offered_replicates"])
    cmp("%s result (threshold / cannot pass)" % name, d["result"], t["status"])

out = ["", "#" * 100,
       "COMPARISON WITH thresholds.json (appended after the numbers above were written; thresholds.json was not",
       "opened before then). thresholds.json sha256 %s" % hashlib.sha256(open(thr_json, "rb").read()).hexdigest(),
       "  (thresholds.json records km_thresholds.py sha256 %s; check_a.py is a separate program)" % thr["km_thresholds_py_sha256"],
       "status   | figure | checker-a | thresholds.json"]
for s, lab, a, b in rows:
    out.append("%-8s | %s | %s | %s" % (s, lab, a, b))
n_bad = sum(1 for r in rows if r[0] != "AGREE")
out.append("SUMMARY: %d figures compared, %d AGREE, %d DISAGREE." % (len(rows), len(rows) - n_bad, n_bad))
with open(check_txt, "a", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out) + "\n")
print("\n".join(out))

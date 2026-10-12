"""For each failing test in a cargo test log: is the test new or changed since the official engine (8626a358)?
Usage: changed_tests.py LOG REPO NEW OLD"""
import re, subprocess, sys
log, repo, new, old = sys.argv[1:]
fails = sorted(set(re.findall(r"^test (\S+) \.\.\. FAILED", open(log).read(), re.M)))
files = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", new, "engine"], capture_output=True, text=True).stdout.split()
files = [f for f in files if f.endswith(".rs")]
def body(rev, path, name):
    p = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"], capture_output=True, text=True)
    if p.returncode:
        return None
    s = p.stdout
    m = re.search(rf"\bfn {re.escape(name)}\s*\(", s)
    if not m:
        return None
    i = s.index("{", m.end()); depth = 0
    for j in range(i, len(s)):
        depth += {"{": 1, "}": -1}.get(s[j], 0)
        if depth == 0:
            return s[m.start():j + 1]
cache = {}
for t in fails:
    name = t.split("::")[-1]
    hits = []
    for f in files:
        b = body(new, f, name) if (new, f) not in cache or name in cache[(new, f)] else None
        if b:
            hits.append((f, b))
    if not hits:
        print(f"{t}\tNOT FOUND"); continue
    status = []
    for f, b in hits:
        ob = body(old, f, name)
        status.append(f"{f}: " + ("new" if ob is None else "changed" if ob != b else "UNCHANGED"))
    print(f"{t}\t" + "; ".join(status))

"""Read-only card check of c-magnezone_ex_magnezone.txt against the switch-2 engine P (no games)."""
import json, subprocess, sys
from pathlib import Path
M = Path(sys.argv[1]); ENGINE_DB = Path(sys.argv[2]); REPO = Path(sys.argv[3])
ids = [" ".join(l.split()[-2:]) for l in (M / "deck.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
lib = {next(iter(e.values()))["id"]: e for e in json.load(open(M / "lib_db.json", encoding="utf-8"))}
eng = {next(iter(e.values()))["id"]: e for e in json.load(open(ENGINE_DB, encoding="utf-8"))}
cs = json.load(open(M / "card_status.json"))
status = {c["id"]: c for c in (cs["cards"] if isinstance(cs, dict) else cs)}
cov, old = json.load(open(M / "coverage.json")), json.load(open(M / "coverage_sept26.json"))
fails = 0
print(f"{len(ids)} distinct cards: {', '.join(ids)}\n")
for i in ids:
    text = subprocess.run([sys.executable, str(REPO / "lib/card.py"), i], capture_output=True, text=True, cwd=REPO).stdout.strip()
    same_db = lib.get(i) == eng.get(i)
    st = status.get(i, {})
    same_cov = cov.get(i) == old.get(i)
    ok = (bool(text) and same_db and st.get("status") == "Complete" and not st.get("limitations")
          and cov[i]["engine_complete"] and not cov[i]["limitations"] and same_cov)
    fails += not ok
    print(f"== {i}: {'PASS' if ok else 'FAIL'}; lib/card.py entry = P's engine/database.json entry: {same_db}; card_status: {st.get('status')}, "
          f"limitations {list(st.get('limitations', []))}; goldfish coverage {cov[i]['engine_status']}, flags "
          f"{ {k: v for k, v in cov[i].items() if isinstance(v, list) and v} or 'none'}; same as Sept 26's coverage: {same_cov}")
    print("   " + text.replace("\n", "\n   "))
extra = sorted(set(cov) ^ set(ids))
print(f"\ncoverage ids beyond the list (or missing): {extra or 'none'}")
print(f"RESULT: {len(ids) - fails} of {len(ids)} cards pass; {'PASS' if not fails and not extra else 'FAIL'}")

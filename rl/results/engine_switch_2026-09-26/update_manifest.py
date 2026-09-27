"""Point project_manifest.json at the pinned repaired engine (run only after pin_official.sh wrote PIN DONE).
The Sept 25 release moves to historical_releases unchanged, with a superseded note. Usage: python3 update_manifest.py <merge commit full sha>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
commit = sys.argv[1]
status = open(os.path.join(HERE, "PIN_STATUS.txt"), encoding="utf-8").read()
assert "PIN DONE" in status and "PIN FAILED" not in status, "pin not done"
sums = dict(reversed(l.split()) for l in open(os.path.join(ROOT, "rl", "engine-2026-09-27", "SHA256SUMS"), encoding="utf-8"))
path = os.path.join(ROOT, "project_manifest.json")
m = json.load(open(path, encoding="utf-8"))
old = m["available_release"]
assert old["name"] == "main-7fc6ccb", old["name"]
old = dict(old, superseded="2026-09-27 by main-" + commit[:7] + " (the repaired engine; rl/engine-2026-09-27/)")
m["historical_releases"].append(old)
m["available_release"] = {
    "name": "main-" + commit[:7],
    "artifact": "rl/engine-2026-09-27/deckgym",
    "sha256": sums["deckgym"],
    "legality_scan": "rl/engine-2026-09-27/legality_scan",
    "legality_scan_sha256": sums["legality_scan"],
    "goldfish": "rl/engine-2026-09-27/goldfish",
    "goldfish_sha256": sums["goldfish"],
    "goldfish_note": "A1's goldfish and coverage tool (engine/examples/goldfish.rs), built in the same WSL tree as deckgym and legality_scan; decks/screen/floor.py gives a floor verdict only with this hash.",
    "source_commit": commit,
    "source_working_tree": False,
    "built": "2026-09-27 in WSL: cargo build --release, --example legality_scan and --example goldfish, from git archive of main at source_commit (the merge of claude/pensive-ptolemy-spwc0b; engine/ identical to 9bffbda, the kpf build)",
    "identity_evidence": "rl/results/engine_switch_2026-09-26/pin_identity.txt: k3 and kp3 over the table's 14,000 deals equal the repaired engine's references (the cloud's af8489f_{k3,kp3}_500.jsonl: moves, decisions, result) and the kpf build's table runs, 14,000 of 14,000 each; deckgym simulate runs k3 and kp3 on seed 7100; goldfish --coverage runs. The repairs' replays: rl/results/rules09_fixes_2026-09-26/ (only Legendary Pulse and promotion timing change table games); the mechanic check: rl/results/engine_switch_2026-09-26/README.md",
    "approved": "Dustin, Sept 26-27, 2026: 'Go' on the switch after the replays; the literal mechanic check with the restated 'in lookahead' rule (RUN5 Rules, Engine repairs)",
    "purpose": "Official engine from Sept 27: rules4 plus the ten rules/09 repairs of Sept 26 (version string unchanged at 0.1.0-pdl.rules4), and the kp, kd, kq, kpr, koa, kpf and kpg players. The 0.7.2 RL add-on wheel and its run identities are unchanged.",
}
m["latest_source_commit"] = commit
m["latest_source_note"] = "engine/ is tracked in git. The available release (main-" + commit[:7] + ") was built from this commit; later engine commits are newer source, not the release build."
json.dump(m, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(path, "a", encoding="utf-8").write("\n")
print("manifest now points at", m["available_release"]["artifact"], m["available_release"]["sha256"][:16])

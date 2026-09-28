"""Point project_manifest.json at the pinned kog engine (run only after pin_finish.sh has copied the programs).
The Sept 27 release moves to historical_releases unchanged, with a superseded note.
Usage: python3 update_manifest.py <merge commit full sha> <built commit full sha (engine/ identical)>"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
commit, built = sys.argv[1], sys.argv[2]
status = open(os.path.join(HERE, "PIN_STATUS.txt"), encoding="utf-8").read()
assert f"PREPARE DONE {built}" in status and "FAILED" not in status, "prepare not done for this commit"
sums = dict(reversed(l.split()) for l in open(os.path.join(ROOT, "rl", "engine-2026-09-28", "SHA256SUMS"), encoding="utf-8"))
path = os.path.join(ROOT, "project_manifest.json")
m = json.load(open(path, encoding="utf-8"))
old = m["available_release"]
assert old["name"] == "main-83e17ae", old["name"]
old = dict(old, superseded="2026-09-28 by main-" + commit[:7] + " (kog, the composed pilot; rl/engine-2026-09-28/)")
m["historical_releases"].append(old)
m["available_release"] = {
    "name": "main-" + commit[:7],
    "artifact": "rl/engine-2026-09-28/deckgym",
    "sha256": sums["deckgym"],
    "legality_scan": "rl/engine-2026-09-28/legality_scan",
    "legality_scan_sha256": sums["legality_scan"],
    "goldfish": "rl/engine-2026-09-28/goldfish",
    "goldfish_sha256": sums["goldfish"],
    "goldfish_note": "A1's goldfish and coverage tool (engine/examples/goldfish.rs), built in the same WSL tree as deckgym and legality_scan; decks/screen/floor.py gives a floor verdict only with this hash.",
    "source_commit": commit,
    "source_working_tree": False,
    "built": "2026-09-28 in WSL: cargo build --release, --example legality_scan and --example goldfish, from git archive of " + built + " (the head of claude/pensive-ptolemy-spwc0b); source_commit is its merge into main, whose engine/ is byte-identical (checked by pin_finish.sh)",
    "identity_evidence": "rl/results/engine_switch_2026-09-28/pin_identity.txt: k3 and kp3 over the table's 14,000 deals equal the official references (main-83e17ae's table runs), and kog3 equals the cloud's a823b6d table and the laptop's composition table, 14,000 of 14,000 each; deckgym simulate runs k3, kp3 and kog3 on seed 7100; goldfish --coverage runs. Engine changes since main-83e17ae: bot code (players/) plus a behaviour-preserving refactor in hooks/ for kt's evaluator (README.md in that folder).",
    "approved": "Dustin, Sept 28, 2026: 'Pin it now', with the last switch's conditions; the hooks refactor ruled on as recorded in rl/results/engine_switch_2026-09-28/README.md",
    "purpose": "Official engine from Sept 28: rules unchanged from main-83e17ae (rules4 plus the ten rules/09 repairs); adds the kog, koh, kph and kt players. kog3 is the working pilot (composition check passed Sept 28). The 0.7.2 RL add-on wheel and its run identities are unchanged.",
}
m["latest_source_commit"] = commit
m["latest_source_note"] = "engine/ is tracked in git. The available release (main-" + commit[:7] + ") was built from this commit; later engine commits are newer source, not the release build."
json.dump(m, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
open(path, "a", encoding="utf-8").write("\n")
print("manifest now points at", m["available_release"]["artifact"], m["available_release"]["sha256"][:16])

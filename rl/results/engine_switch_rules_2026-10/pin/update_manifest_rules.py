"""The new project_manifest.json for the rules switch's pin (PLAN.md step 12; run by pin_rules.sh only). Adapted from
../../engine_switch_2026-09-30/update_manifest.py. pin_rules.sh builds every pin file in a scratch folder first, so this
writes the new manifest to <out>, not into the repository: pin_rules.sh installs it with the others after checking them
all. The Sept 30 release (main-d363ba8) moves to historical_releases unchanged, with a superseded note.
Usage: python3 update_manifest_rules.py <merge commit> <built candidate commit> <SHA256SUMS> <base manifest> <out>
                                        <8c changed games> <8c result commit> [--check]
  <merge commit>, <built candidate commit>, <8c result commit>: full shas. <SHA256SUMS>: the three programs' sums, as
  pinned. <base manifest>: main's project_manifest.json before the pin (pin_rules.sh passes git show of it).
  <8c changed games>: the n of 8c_RESULT.txt's line (every changed game of steps 8 and 8b, each accounted for).
  --check: skips the PIN_STATUS.txt conditions (pin_rules.sh runs it so before the merge, with main's HEAD standing in
  for the merge commit)."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
R_SHA = "f8cfa9c1df4bbcfb72a3b9d9b0247b081a1ffd26"   # R, the head of sonnet/rules-fixes
OLD_NAME = "main-d363ba8"
NEW_DIR = "rl/engine-2026-10-02"
check = "--check" in sys.argv[1:]
args = [a for a in sys.argv[1:] if a != "--check"]
assert len(args) == 7, __doc__
commit, built, sums_path, base_path, out, changed, c8 = args
for s in (commit, built, c8):
    assert re.fullmatch(r"[0-9a-f]{40}", s), "full shas, please: " + s
assert re.fullmatch(r"[1-9][0-9]*", changed), "the changed-game count: " + changed
if not check:
    status = open(os.path.join(HERE, "..", "PIN_STATUS.txt"), encoding="utf-8").read()
    for n in (1, 2):
        assert re.search(rf"^SITTING {n} DONE {built}\b", status, re.M), f"no 'SITTING {n} DONE {built[:7]}' in PIN_STATUS.txt"
    # the pin's own STOPPED and AFTER HALT lines are the pin's; any other FAILED or MISMATCH line stops here
    scan = [l for l in status.splitlines() if not re.match(r"[0-9-]+T[0-9:]+Z PIN (STOPPED:|AFTER HALT)", l)]
    bad = [l for l in scan if "FAILED" in l or "MISMATCH" in l]
    assert not bad, f"a FAILED or MISMATCH line in PIN_STATUS.txt: {bad[:2]}"
    assert re.search(rf"MERGED {R_SHA[:7]} into main as {commit}\b", status), "pin_rules.sh has not recorded the merge"
sums = dict(reversed(l.split()) for l in open(sums_path, encoding="utf-8") if l.strip())
assert set(sums) == {"deckgym", "legality_scan", "goldfish"}, sums
m = json.load(open(base_path, encoding="utf-8"))
old = m["available_release"]
assert old["name"] == OLD_NAME, old["name"]
assert all(r.get("name") != "main-" + commit[:7] for r in m["historical_releases"]), "already in the history"
old = dict(old, superseded="2026-10-02 by main-" + commit[:7] + " (the rules switch: repairs A + B, kd's follow-ons, "
           "F1-F7; " + NEW_DIR + "/)")
m["historical_releases"].append(old)
n = f"{int(changed):,}"
m["available_release"] = {
    "name": "main-" + commit[:7],
    "artifact": NEW_DIR + "/deckgym",
    "sha256": sums["deckgym"],
    "legality_scan": NEW_DIR + "/legality_scan",
    "legality_scan_sha256": sums["legality_scan"],
    "goldfish": NEW_DIR + "/goldfish",
    "goldfish_sha256": sums["goldfish"],
    "goldfish_note": "A1's goldfish and coverage tool (engine/examples/goldfish.rs), built in the same WSL tree as deckgym and legality_scan; decks/screen/floor.py gives a floor verdict only with this hash.",
    "source_commit": commit,
    "source_working_tree": False,
    "built": "2026-10-01 (03:16 UTC) in WSL: cargo build --release --locked, --example legality_scan and --example goldfish, "
             "from one git archive of " + built + " (the merge candidate: main c9f4224 plus sonnet/rules-fixes at R f8cfa9c, "
             "whose engine/ is R's, tree 38af8b0); source_commit is main's own merge commit of R, whose engine/ is "
             "byte-identical to the candidate's (checked by rl/results/engine_switch_rules_2026-10/pin/pin_rules.sh); the "
             "candidate commit is kept on the laptop only (refs/pocketdecksim/rules-switch-candidate, not pushed).",
    "identity_evidence": "rl/results/engine_switch_rules_2026-10/ (README.md, identity_check.txt, table_counters.txt, "
                         "touched_check.txt, 8c_RESULT.txt), each replay matched by pairing and game number with counts "
                         "asserted: step 7, 151,240 games equal to their references on every field (kta3 fresh and "
                         "development, km3, k3 and kp3 on scoreboard v3's 45 cells, kog3, kq3, kpr3, and kd3 as a gate); "
                         "step 7b, the watch build's 28,000 table games equal to the plain ones, every repair counter 0 and "
                         "both off-gate counters above 0; step 7c, Dustin's decks 02, 06, 08 and 14, 1,920 floor games each "
                         "equal; steps 8 and 8b, 72,960 carrier and scratch games on the old, new and watch builds, watch "
                         "equal to new and every all-zero-counter game equal to the old one, and the " + n + " changed games "
                         "each accounted for in 8c (the 297 CONDITION 3 games each traced; 8 games the rule could not settle, "
                         "each explained by repair A or B and accepted by Dustin on Oct 2, 8c_DECISION.md; Sonnet's result "
                         + c8[:7] + "); step 9, km3's coverage baselines, "
                         "66,500 games equal; step 10, deckgym simulate repeats k3 150/90/0, kp3 144/96/0 and kog3 149/91/0 "
                         "and kta3 and km3 equal Sept 30's lines, goldfish --coverage byte-equal, run_screen under km3 equal. "
                         "Engine changes since main-d363ba8: the plan's 9 files (actions/apply_action.rs, "
                         "actions/apply_attack_action.rs, actions/attack_outcome.rs, hooks/core.rs, card_validation.rs and "
                         "four test files); engine/src/players/ and Cargo.lock unchanged.",
    "approved": "Dustin, Sept 30, 2026: 'Sure go for all 9' (a conditional go, 'pin if all pass'); Oct 1: Victory Star smoke "
                "game 28 accepted as the one documented judgment exception (its Copycat explanation is a possible sampled "
                "path, not a replay of the bot's exact original search), and 'My conditional approval stands: pin the "
                "existing candidate once all remaining required trace checks pass' (rl/RUN5.md; "
                "rl/results/engine_switch_rules_2026-10/README.md)",
    "purpose": "Official engine from Oct 1: main-d363ba8's engine (rules4 plus the ten rules/09 repairs; the kta and km "
               "players) plus the rules switch: repair A (Victory Star with a Confused attacker: the Confusion coin first, "
               "then Victory Star on the attack's own coins), repair B (coin-flip damage prevention and Chase Order: "
               "Guarded Grill and Securely Sheltered come off after Weakness, and queued attack damage flips the coin), "
               "kd's follow-ons and the fixes F1-F7. engine/src/players/ is unchanged: km3 stays the working pilot on both "
               "sides of the screen and the floor, and every pilot plays as before unless a coin-Ability Pokémon (Meowth "
               "B2 124/204, Togekiss A4 080, Bastiodon A2 114, Hisuian Goodra B3b 050) or Victini (B3 025, P-B 049) is in "
               "play. Still open (rules/09): Victory Star with CoinFlipToBlockAttack, and with Confusion plus a pending "
               "Will, stays gated; Wild Swing, the own-Bench form of also_choice_bench_damage, six other sites and a "
               "copied Chase Order's discard branch still skip the coin. The 0.7.2 RL add-on wheel and its run "
               "identities are unchanged.",
}
m["latest_source_commit"] = commit
m["latest_source_note"] = "engine/ is tracked in git. The available release (main-" + commit[:7] + ") was built from this commit's engine/; later engine commits are newer source, not the release build."
text = json.dumps(m, indent=2, ensure_ascii=False) + "\n"
json.loads(text)
open(out, "w", encoding="utf-8", newline="\n").write(text)
print("manifest (" + out + ") points at", m["available_release"]["artifact"], m["available_release"]["sha256"][:16])

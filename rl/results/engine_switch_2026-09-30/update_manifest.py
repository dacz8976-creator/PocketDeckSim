"""The new project_manifest.json for the pinned kta/km engine (step 9 of the Sept 30 switch; run by pin.sh only). pin.sh
builds every pin file in a scratch folder first, so this writes the new manifest to <out>, not into the repository: pin.sh
installs it with the others after checking them all. The Sept 28 release (main-9b4df9b) moves to historical_releases
unchanged, with a superseded note.
Usage: python3 update_manifest.py <merge commit> <built candidate commit> <SHA256SUMS> <base manifest> <out> [--check]
  <merge commit>, <built candidate commit>: full shas. <SHA256SUMS>: the three programs' sums, as pinned.
  <base manifest>: main's project_manifest.json before the pin (pin.sh passes git show HEAD:project_manifest.json).
  --check: skips the PIN_STATUS.txt conditions (pin.sh runs it so before the merge, on today's manifest)."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
check = "--check" in sys.argv[1:]
args = [a for a in sys.argv[1:] if a != "--check"]
assert len(args) == 5, __doc__
commit, built, sums_path, base_path, out = args
assert re.fullmatch(r"[0-9a-f]{40}", commit) and re.fullmatch(r"[0-9a-f]{40}", built), "full shas, please"
if not check:
    status = open(os.path.join(HERE, "PIN_STATUS.txt"), encoding="utf-8").read()
    done = re.findall(r"PREPARE DONE ([0-9a-f]{40})", status)
    assert done and done[-1] == built, f"the last PREPARE DONE is not {built}"
    # prepare's HALT and STOPPED lines (which quote sha256sum's "FAILED") are governed by the HALT rule and
    # PIN_AFTER_HALT in pin.sh, and the pin's own STOPPED and AFTER HALT lines by the pin; any other such line stops here
    scan = [l for l in status.splitlines() if not re.match(r"PREPARE (HALT|STOPPED) ", l)
            and not re.match(r"[0-9-]+T[0-9:]+Z PIN (STOPPED:|AFTER HALT)", l)]
    bad = [l for l in scan if "FAILED" in l or "MISMATCH" in l]
    assert not bad, f"a FAILED or MISMATCH line in PIN_STATUS.txt: {bad[:2]}"
    assert re.search(rf"MERGED \S+ into main as {commit}\b", status), "pin.sh has not recorded the merge"
sums = dict(reversed(l.split()) for l in open(sums_path, encoding="utf-8") if l.strip())
assert set(sums) == {"deckgym", "legality_scan", "goldfish"}, sums
m = json.load(open(base_path, encoding="utf-8"))
old = m["available_release"]
assert old["name"] == "main-9b4df9b", old["name"]
assert all(r.get("name") != "main-" + commit[:7] for r in m["historical_releases"]), "already in the history"
old = dict(old, superseded="2026-09-30 by main-" + commit[:7] + " (kta and km, a players-only switch; rl/engine-2026-09-30/)")
m["historical_releases"].append(old)
same = "the merge candidate itself (main had not moved; pin.sh fast-forwarded main to it)." if commit == built else \
    ("main's own merge commit of 53fc5a1, whose engine/ is byte-identical to the candidate's (checked by pin.sh); the "
     "candidate commit is kept on the laptop only (refs/pocketdecksim/engine-switch-candidate, not pushed).")
m["available_release"] = {
    "name": "main-" + commit[:7],
    "artifact": "rl/engine-2026-09-30/deckgym",
    "sha256": sums["deckgym"],
    "legality_scan": "rl/engine-2026-09-30/legality_scan",
    "legality_scan_sha256": sums["legality_scan"],
    "goldfish": "rl/engine-2026-09-30/goldfish",
    "goldfish_sha256": sums["goldfish"],
    "goldfish_note": "A1's goldfish and coverage tool (engine/examples/goldfish.rs), built in the same WSL tree as deckgym and legality_scan; decks/screen/floor.py gives a floor verdict only with this hash.",
    "source_commit": commit,
    "source_working_tree": False,
    "built": "2026-09-30 in WSL: cargo build --release, --example legality_scan and --example goldfish, from git archive of "
             + built + " (the merge candidate: main plus claude/pensive-ptolemy-spwc0b at 53fc5a1, whose engine/ is B's, "
             "1f6319e, tree 9c84fef); source_commit is " + same,
    "identity_evidence": "rl/results/engine_switch_2026-09-30/identity_check.txt, each replay matched by pairing and game "
                         "number with counts asserted: kta3 equals ec7e1a8's committed games on the fresh deals "
                         "(kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table 14,000 of 14,000, _new17 8,500 of 8,500) and the "
                         "development deals (kt_tables_2026-09-28/ec7e1a8_kta3_table 14,000, _new17 8,500); km3 equals B's "
                         "(km_tables_2026-09-30/1f6319e_km3_table 14,000, _new17 8,500); k3, kp3 and kog3 equal the Sept 28 "
                         "pin's references, 14,000 of 14,000 each; deckgym simulate repeats the Sept 28 lines for k3, kp3 and "
                         "kog3 on seed 7100 and runs kta3 and km3; goldfish --coverage runs. Engine changes since "
                         "main-9b4df9b: players only (engine/src/players/mod.rs, public_pricing_player.rs, value_functions.rs).",
    "approved": "Dustin, Sept 30, 2026: 'Yes, pin if all pass (Recommended)'; default pilot 'km3 (Recommended)'; rules items "
                "'Keep them out (Recommended)' (rl/RUN5.md, km, 'The official engine switch carrying kta and km')",
    "purpose": "Official engine from Sept 30: rules unchanged from main-9b4df9b (rules4 plus the ten rules/09 repairs); a "
               "players-only switch. kta<N> is ec7e1a8's kog-based kta (kog + switch 1, the Tool cut; adopted 'unconfirmed' "
               "Sept 30). km<N> is kta + N2, the attacker's lasting Stadium damage bonus in the clock, as built at B "
               "(1f6319e; adopted in the tables 'unconfirmed' Sept 30). km3 is the working pilot: the screen and the floor "
               "default to it on both sides. kt3, ktb3 and ktc3 are now the kog-based presets as B defines them: diagnostic, "
               "no identity claim, never adopted (the kp-based kt presets of Sept 26-28 replay on rl/engine-2026-09-28/). "
               "k3, kp3 and kog3 play unchanged. The 0.7.2 RL add-on wheel and its run identities are unchanged.",
}
m["latest_source_commit"] = commit
m["latest_source_note"] = "engine/ is tracked in git. The available release (main-" + commit[:7] + ") was built from this commit's engine/; later engine commits are newer source, not the release build."
text = json.dumps(m, indent=2, ensure_ascii=False) + "\n"
json.loads(text)
open(out, "w", encoding="utf-8", newline="\n").write(text)
print("manifest (" + out + ") points at", m["available_release"]["artifact"], m["available_release"]["sha256"][:16])

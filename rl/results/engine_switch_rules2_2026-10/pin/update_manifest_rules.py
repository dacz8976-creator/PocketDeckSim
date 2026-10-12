"""The new project_manifest.json for rules switch 2's pin (PLAN.md steps 11-14; run by pin_rules.sh only). A copy of
../../engine_switch_rules_2026-10/pin/update_manifest_rules.py (the Oct 1 switch's, which wrote main-8626a35's entry;
itself adapted from ../../engine_switch_2026-09-30/update_manifest.py), adapted for switch 2 by ADAPTATION_SPEC.md
section 11 (U-1 to U-9). pin_rules.sh builds every pin file in a scratch folder first, so this writes the new manifest to
<out>, not into the repository: pin_rules.sh installs it with the others after checking them all. The Oct 2 release
(switch2.env's OLD_RELEASE_NAME, main-8626a35) moves to historical_releases unchanged, with a superseded note.
Usage: python3 update_manifest_rules.py <merge commit> <built candidate commit> <P> <SHA256SUMS> <base manifest> <out>
                                        <engine dir> <8c line file> [--check]
  <merge commit>, <built candidate commit>, <P>: full shas (P must be ../switch2.env's P). <SHA256SUMS>: the three
  programs' sums, as pinned. <base manifest>: main's project_manifest.json before the pin (pin_rules.sh passes git show
  of it). <engine dir>: rl/engine-<the pin's date> (switch2.env's ENGINE_DIR). <8c line file>: a file whose one line
  starting with 8C is 8c_RESULT.txt's (its grammar is in README.md here); the 8c counts are read from it.
  Also read (never written): ../switch2.env (P_TREE, CREF, the old release; KEY=VALUE lines read with a regex),
  ../candidate.txt (the candidate's main), ../allowed_engine_files.tsv (the engine file counts), ../STATUS.txt (the last
  STEP 7c, 8b, 8 and 9 DONE lines' 'changed <N> of <M> deals'), ../PIN_STATUS.txt (the build time: its
  'sha256 <deckgym> deckgym (new, plain)' line), git (the DECKGYM_* switches P's engine/src/ reads and the official
  engine's doesn't), and PIN_DUSTIN from the environment (Dustin's words on 8c's games, when the 8c line has any).
  --check: skips the PIN_STATUS.txt conditions (pin_rules.sh runs it so before the merge, with main's HEAD standing in
  for the merge commit); the 8c result commit may then be 40 zeros (PIN_CHECK_WITHOUT_8C=1)."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.dirname(HERE)                                      # rl/results/engine_switch_rules2_2026-10
R = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REL = "rl/results/engine_switch_rules2_2026-10"
check = "--check" in sys.argv[1:]
args = [a for a in sys.argv[1:] if a != "--check"]
assert len(args) == 8, __doc__
commit, built, p_sha, sums_path, base_path, out, new_dir, c8_path = args
for s in (commit, built, p_sha):
    assert re.fullmatch(r"[0-9a-f]{40}", s), "full shas, please: " + s
assert re.fullmatch(r"rl/engine-2026-1[0-2]-[0-3][0-9]", new_dir), "the engine dir must be rl/engine-<the pin's date>: " + new_dir
date = new_dir[len("rl/engine-"):]


def read_env(path):  # KEY=VALUE lines, read with a regex and never evaluated (ADAPTATION_SPEC 1.2)
    env = {}
    for n, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        if not line or line.startswith("#"):
            continue
        m = re.fullmatch(r"([A-Z0-9_]+)=([^ ]*)", line)
        assert m, f"switch2.env line {n} is not KEY=VALUE: {line[:80]!r}"
        assert m.group(1) not in env, f"switch2.env sets {m.group(1)} twice"
        env[m.group(1)] = m.group(2)
    return env


env = read_env(os.path.join(O, "switch2.env"))
for k, v in env.items():
    assert v != "TO_FINALIZE", f"switch2.env: {k} is TO FINALIZE (the pin needs every value)"
for k in ("P", "P_TREE", "OFFICIAL", "OLD_RELEASE_NAME", "OLD_DIR", "OLD_DECKGYM_SHA256", "OLD_LEGALITY_SCAN_SHA256",
          "OLD_GOLDFISH_SHA256", "CREF", "ENGINE_DIR"):
    assert env.get(k), f"switch2.env has no {k}"
assert env["P"] == p_sha, f"<P> {p_sha[:7]} is not switch2.env's P {env['P'][:7]}"
assert env["ENGINE_DIR"] == new_dir, f"<engine dir> {new_dir} is not switch2.env's ENGINE_DIR {env['ENGINE_DIR']}"
OLD_NAME, OLD_DIR, P_TREE = env["OLD_RELEASE_NAME"], env["OLD_DIR"], env["P_TREE"]
assert re.fullmatch(r"[0-9a-f]{40}", P_TREE), "switch2.env's P_TREE: " + P_TREE
assert new_dir != OLD_DIR, f"the engine dir is the official programs' own folder ({OLD_DIR})"

cand = {}
for line in open(os.path.join(O, "candidate.txt"), encoding="utf-8").read().splitlines():
    k, _, v = line.partition(" ")
    cand.setdefault(k, v)
assert cand.get("candidate") == built, f"candidate.txt doesn't name the candidate {built[:7]}"
main_c = cand.get("main", "")
assert re.fullmatch(r"[0-9a-f]{40}", main_c), "candidate.txt has no main line"

allowed, hdr = [], False
for n, line in enumerate(open(os.path.join(O, "allowed_engine_files.tsv"), encoding="utf-8").read().split("\n"), 1):
    if not line or line.startswith("#"):
        continue
    if not hdr:
        assert line == "status\tpath", f"allowed_engine_files.tsv line {n} is not the header"
        hdr = True
        continue
    m = re.fullmatch(r"(M|A)\t(engine/[A-Za-z0-9_./-]+)", line)
    assert m, f"allowed_engine_files.tsv line {n}: {line[:100]!r}"
    allowed.append(m.group(2))
assert allowed, "allowed_engine_files.tsv lists no engine file"
nsrc = sum(p.startswith("engine/src/") for p in allowed)
ntest = len(allowed) - nsrc

slog = open(os.path.join(O, "STATUS.txt"), encoding="utf-8").read().splitlines()
ph = {}
for s in ("7c", "8b", "8", "9"):
    lines = [x for x in slog if x.startswith(f"STEP {s} DONE {built[:7]} ")]
    assert lines, f"STATUS.txt has no 'STEP {s} DONE {built[:7]}' line"
    found = re.findall(r"changed ([0-9]+) of ([0-9]+) deals", lines[-1])
    assert len(found) == 1, f"STEP {s}'s last DONE line holds {len(found)} 'changed <N> of <M> deals' phrases, not 1"
    ph[s] = (int(found[0][0]), int(found[0][1]))

N = r"(0|[1-9][0-9]*)"
c8_lines = [x for x in open(c8_path, encoding="utf-8").read().splitlines() if re.match(r"8C( |$)", x)]
assert len(c8_lines) == 1, f"the 8c line file has {len(c8_lines)} lines starting with 8C, not 1"
m8 = re.fullmatch(rf"8C PASS ([0-9a-f]{{40}}) verdicts: on_board {N}, lookahead {N}, unexplained {N}, judgment {N}; "
                  rf"both_halves {N} of {N}; revert {N} of {N} reproduced; condition3 {N} traced {N}; none {N} traced {N}; "
                  rf"other_only {N} traced {N}; changed {N} accounted {N}; dustin {N} "
                  r"\(8c_DECISION\.md\); net unaccounted 0; 8b_rows_vs_cloud equal", c8_lines[0])
assert m8, "the 8c line is not in README.md's grammar: " + c8_lines[0]
c8 = m8.group(1)
b, l, u, j, bh, bhof, rv, rvof, c3a, c3t, nna, nnt, noa, nott, n8, acc, a8 = (int(x) for x in m8.groups()[1:])
assert b + l + u + j == n8 == acc, f"8c: on_board {b} + lookahead {l} + unexplained {u} + judgment {j}, changed {n8}, accounted {acc}"
assert bh == bhof == l, f"8c: both_halves {bh} of {bhof}, but every one of the {l} lookahead games must meet both (PLAN.md section 6)"
assert rv == rvof == l, f"8c: revert {rv} of {rvof} reproduced, but every one of the {l} lookahead games must be (PLAN.md section 6)"
assert c3a == c3t, f"8c: condition3 {c3a}, traced {c3t}"
assert nna == nnt and noa == nott, f"8c: none {nna} traced {nnt}, other_only {noa} traced {nott}"
assert a8 == u + j, f"8c: dustin {a8}, but unexplained {u} + judgment {j}"
assert n8 == sum(v[0] for v in ph.values()), f"8c: changed {n8}, the STEP 7c, 8b, 8 and 9 lines {sum(v[0] for v in ph.values())}"
assert n8 > 0, "8c: no changed game at all"
if not check:
    assert c8 != "0" * 40, "the 8c result commit is 40 zeros (PIN_CHECK_WITHOUT_8C is for --check only)"
dustin = " ".join(os.environ.get("PIN_DUSTIN", "").split())
if a8 > 0:
    assert dustin, f"8c has {a8} games for Dustin's word, and PIN_DUSTIN is not set (PLAN.md line 29 and section 6)"

pin_status = open(os.path.join(O, "PIN_STATUS.txt"), encoding="utf-8").read()
sums = dict(reversed(x.split()) for x in open(sums_path, encoding="utf-8") if x.strip())
assert set(sums) == {"deckgym", "legality_scan", "goldfish"}, sums
bm = re.search(rf"^([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})T([0-9]{{2}}:[0-9]{{2}}):[0-9]{{2}}Z sha256 {sums['deckgym']} deckgym \(new, plain\)$",
               pin_status, re.M)
assert bm, "PIN_STATUS.txt has no 'sha256 <the pinned deckgym> deckgym (new, plain)' line (sitting 1's step 5)"
built_at = f"{bm.group(1)} ({bm.group(2)} UTC)"
if not check:
    for k in (1, 2):
        assert re.search(rf"^SITTING {k} DONE {built}\b", pin_status, re.M), f"no 'SITTING {k} DONE {built[:7]}' in PIN_STATUS.txt"
    # the pin's own STOPPED, AFTER HALT and DUSTIN lines are the pin's; any other FAILED or MISMATCH line stops here
    scan = [x for x in pin_status.splitlines() if not re.match(r"[0-9-]+T[0-9:]+Z PIN (STOPPED:|AFTER HALT|DUSTIN:)", x)]
    bad = [x for x in scan if "FAILED" in x or "MISMATCH" in x]
    assert not bad, f"a FAILED or MISMATCH line in PIN_STATUS.txt: {bad[:2]}"
    assert re.search(rf"MERGED {p_sha[:7]} into main as {commit}\b", pin_status), "pin_rules.sh has not recorded the merge"

m = json.load(open(base_path, encoding="utf-8"))
old = m["available_release"]
assert old["name"] == OLD_NAME, old["name"]
for key, prog, want in (("sha256", "deckgym", env["OLD_DECKGYM_SHA256"]),
                        ("legality_scan_sha256", "legality_scan", env["OLD_LEGALITY_SCAN_SHA256"]),
                        ("goldfish_sha256", "goldfish", env["OLD_GOLDFISH_SHA256"])):
    path_key = "artifact" if prog == "deckgym" else prog
    assert old.get(path_key) == f"{OLD_DIR}/{prog}" and old.get(key) == want, \
        f"the base manifest's {OLD_NAME} doesn't give {prog} as {OLD_DIR}/{prog} with switch2.env's sha256"
assert old.get("source_commit") == env["OFFICIAL"], f"the base manifest's {OLD_NAME} is not built from switch2.env's OFFICIAL"
assert all(r.get("name") != "main-" + commit[:7] for r in m["historical_releases"]), "already in the history"
assert all(not str(r.get("artifact", "")).startswith(new_dir + "/") for r in m["historical_releases"] + [old]), \
    f"{new_dir} is already a release's folder"


def switch_names(ref):  # the DECKGYM_* environment variables a commit's engine/src/ reads
    r = subprocess.run(["git", "-C", R, "grep", "-h", "-o", "-E", "DECKGYM_[A-Z0-9_]+", ref, "--", "engine/src/"],
                       capture_output=True)
    assert r.returncode in (0, 1), "git grep: " + r.stderr.decode(errors="replace")[:300]
    return set(r.stdout.decode().split())


switches = sorted(switch_names(p_sha) - switch_names(env["OFFICIAL"]))
assert switches, "P's engine/src/ reads no new DECKGYM_* switch"

old = dict(old, superseded=f"{date} by main-{commit[:7]} (rules switch 2: the round-2 coin package, Cursed Jewel's "
                           f"Weakness, Fossils as Items; {new_dir}/)")
m["historical_releases"].append(old)
g = lambda x: f"{x:,}"
step = {s: f"changed {g(ph[s][0])} of {g(ph[s][1])} deals" for s in ph}
judged = (f"; {g(u)} the rule left unexplained and {g(j)} judgment calls, each accepted by Dustin at the pin "
          f"({REL}/8c_DECISION.md)" if a8 else "; none unexplained and no judgment call")
m["available_release"] = {
    "name": "main-" + commit[:7],
    "artifact": new_dir + "/deckgym",
    "sha256": sums["deckgym"],
    "legality_scan": new_dir + "/legality_scan",
    "legality_scan_sha256": sums["legality_scan"],
    "goldfish": new_dir + "/goldfish",
    "goldfish_sha256": sums["goldfish"],
    "goldfish_note": "A1's goldfish and coverage tool (engine/examples/goldfish.rs), built in the same WSL tree as deckgym and legality_scan; decks/screen/floor.py gives a floor verdict only with this hash.",
    "source_commit": commit,
    "source_working_tree": False,
    "built": f"{built_at} in WSL: cargo build --release --locked, --example legality_scan and --example goldfish, "
             f"from one git archive of {built} (the merge candidate: main {main_c[:7]} plus P {p_sha[:7]}, the final "
             f"engine commit of claude/coin-prevention-round2, whose engine/ is P's, tree {P_TREE[:7]}); source_commit "
             f"is main's own merge commit of P, whose engine/ is byte-identical to the candidate's (checked by "
             f"{REL}/pin/pin_rules.sh); the candidate commit is kept on the laptop only ({env['CREF']}, not pushed).",
    "identity_evidence": f"{REL}/ (README.md, STATUS.txt and each step's records, handoff_8c.tsv, 8c_RESULT.txt), "
                         f"each replay matched by pairing and game number with "
                         f"counts asserted: step 7, 151,240 games equal to their references on every field (kta3 fresh "
                         f"and development, km3, k3 and kp3 on scoreboard v3's 45 cells, kog3, kq3, kpr3, and kd3 as a "
                         f"gate); step 7b, the watch build's 28,000 table games equal to the plain ones, every round-2 "
                         f"exact counter 0 and offgate_plain_attack_damage, offgate_by_attack and offgate_confused_attack "
                         f"above 0; step 7c, 20,160 games: Dustin's decks 02, 06, 08, 14 and 10 and draft D's root and "
                         f"amended pages replayed through floor.py, and the watch rows (Oct 1's 32 and 24 new), equal "
                         f"outside the named deck 10 v t-weezing rows (watch row: {step['7c']}); step 8b, 2,800 "
                         f"early-warning games on the old, new and watch builds (Oct 1's recorded new-engine games as the "
                         f"old side of its scratch rows), watch equal to new, {step['8b']}, equal to the cloud's rows; "
                         f"step 8, 54,750 carrier and Will-row games (Oct 1's recorded new-engine games as the carriers' "
                         f"old side), watch equal to new, {step['8']}; step 9, 74,500 km3 coverage games: the 80 B2e "
                         f"pairings without Ariados, Scizor and the second lists equal, and the 16 Trap Territory "
                         f"pairings (32-39 and 80-87) {step['9']}, km3's new B2e reference for those rows (Dustin, Oct 9, "
                         f"question 3); step 10, deckgym simulate, goldfish --coverage and run_screen under km3 equal. "
                         f"8c: the {g(n8)} changed games each accounted for, {g(b)} on the board and {g(l)} in look-ahead "
                         f"with both halves and the revert check reproducing the old choice and scores{judged}; "
                         f"traced among them, {g(c3a)} CONDITION 3 games, {g(nna)} with no counter at all and {g(noa)} "
                         f"with only round 1's or a superset's counters; result {c8[:7]}. Engine changes since {OLD_NAME}: "
                         f"{len(allowed)} files ({nsrc} source, {ntest} tests; {REL}/allowed_engine_files.tsv); "
                         f"engine/src/players/, Cargo.lock and Cargo.toml unchanged.",
    "approved": "Dustin, Oct 9, 2026: '1-3 sure' (1: a conditional go, 'update if everything passes', with the two "
                "stricter checks; 2: the scope as recommended; 3: the new reference games as recommended; "
                f"{REL}/RELEASE_PACKAGE.md), and 'Alright it is fine to use the laptop over the weekend' (the sittings "
                f"on the laptop; {REL}/PLAN.md, the Oct 9 status)"
                + (f"; at the pin, on 8c's games: '{dustin}' ({REL}/8c_DECISION.md)" if dustin else ""),
    "purpose": f"Official engine from {date}: {OLD_NAME}'s engine (the Oct 2 rules switch on the Sept 30 engine; the kta "
               f"and km players) plus rules switch 2, taken by commit (P {p_sha[:7]}): the round-2 coin package (seven "
               "more attacks, Wild Swing among them, flip Meowth's, Togekiss's, Bastiodon's and Hisuian Goodra's coin, "
               "and any attack's plain queued hit flips it too; the coin and Guts answer an attack's damage to its own "
               "side; Perish Body flips for a queued hit; Will works for a Confused attacker and on a block coin, and "
               "Victory Star is offered after a block coin's heads; each Ariados adds 1 to the Retreat Cost; Luxury "
               "Coin works only on the player's own Stadium; a Fossil can't be played under an Item lock), Fossils as "
               "Item cards at the seven other places (P3), and return damage set up by an attack taking Weakness "
               "(Cursed Jewel, Spike Armor, Bristling Spikes, Needle Lariat and Shell Trap; Bounded Field doubles it; "
               "a Tool's or an Ability's return damage stays flat), with Gholdengo's caveat text (P1). "
               "engine/src/players/ is unchanged: km3 stays the working pilot on both sides of the screen and the "
               f"floor. The engine reads {len(switches)} revert switches from the environment ({', '.join(switches)}), "
               "each once per process and none set by default, so every rule of the switch is on; set one and the "
               "program is another engine, so never set one in a recorded run (they exist for 8c's revert check). The "
               "0.7.2 RL add-on wheel and its run identities are unchanged.",
}
m["latest_source_commit"] = commit
m["latest_source_note"] = "engine/ is tracked in git. The available release (main-" + commit[:7] + ") was built from this commit's engine/; later engine commits are newer source, not the release build."
text = json.dumps(m, indent=2, ensure_ascii=False) + "\n"
json.loads(text)
open(out, "w", encoding="utf-8", newline="\n").write(text)
print("manifest (" + out + ") points at", m["available_release"]["artifact"], m["available_release"]["sha256"][:16])

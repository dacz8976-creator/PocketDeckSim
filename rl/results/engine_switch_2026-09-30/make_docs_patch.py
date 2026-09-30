"""Step 11 of the Sept 30 engine switch: the doc text, as a patch for review (docs.patch). Nothing here edits a doc.

The patch is made from HEAD's START_HERE.md, CLAUDE.md and rl/RUN5.md by exact text replacements (each anchor must
occur exactly once), plus two new files: rl/engine-2026-09-30/README.md and this folder's README.md. It carries four
placeholders that pin.sh fills when it applies the patch: @MERGE7@ (main's merge commit, short), @CAND7@ (the built
candidate, short), @CAND_NOTE@ (one sentence: main's merge commit is the candidate itself, or pin.sh made its own and
the candidate stays on the laptop) and @RESULTS_MODIFIED@ (the existing records under rl/results/ that the merge
changes, as pin.sh finds them). pin.sh applies it to HEAD's docs, so if RUN5 (or another doc) moves before the pin, the pin stops before
anything changes: re-run this just before the pin (anchors are text, not line numbers) and re-review the diff.

Usage (WSL): python3 make_docs_patch.py   -> docs.patch next to it
"""
import difflib, os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def head(rel):
    return subprocess.run(["git", "-C", ROOT, "show", f"HEAD:{rel}"], check=True, capture_output=True).stdout.decode("utf-8")


def once(text, old, new, rel):
    n = text.count(old)
    assert n == 1, f"{rel}: anchor found {n} times, expected once:\n{old}"
    return text.replace(old, new)


# --- the new files ---------------------------------------------------------------------------------------------------

ENGINE_README = """# The official engine from Sept 30: main-@MERGE7@

- **Programs:** `deckgym`, `legality_scan`, `goldfish`; sha256 in `SHA256SUMS` and `project_manifest.json`. Linux (WSL or the cloud). Committed with the executable bit (git mode 100755), so a Linux clone runs them as they are.
- **Built** in WSL from `git archive` of @CAND7@, the merge candidate: main plus the cloud branch `claude/pensive-ptolemy-spwc0b` at 53fc5a1, whose `engine/` is B's (km's build, 1f6319e; tree 9c84fef). `cargo build --release`, `--example legality_scan`, `--example goldfish`.
  - main's merge commit @MERGE7@ has an `engine/` byte-identical to it (checked by `../results/engine_switch_2026-09-30/pin.sh`). @CAND_NOTE@
- **What it is:** a players-only switch. The rules are the Sept 28 engine's, unchanged (rules4 plus the ten rules/09 repairs); three files in `engine/src/players/` changed.
  - `kta<N>` is ec7e1a8's kog-based kta: kog + switch 1, the Tool cut. Adopted "unconfirmed" Sept 30.
  - `km<N>` is kta + N2, the attacker's lasting Stadium damage bonus in the clock, as built at B. Adopted in the tables "unconfirmed" Sept 30.
  - km3 is the working pilot, on both sides of the screen and the floor. k3 stays the reproduction reference. k3, kp3 and kog3 play exactly as on the Sept 28 engine.
  - **Name change:** `kt3`, `kta3`, `ktb3` and `ktc3` are now the kog-based presets as B defines them. kt3, ktb3 and ktc3 are diagnostic: no identity claim, never adopted. The older kp-based presets (the Sept 26-28 kt records) replay only on `../engine-2026-09-28/`.
- **Approved:** Dustin, Sept 30: "Yes, pin if all pass (Recommended)", with km3 as the default pilot and the rules items kept out (RUN5, km, "The official engine switch carrying kta and km").
- **Evidence** (`../results/engine_switch_2026-09-30/README.md` and `identity_check.txt`; every replay matched by pairing and game number, counts asserted):
  - kta3 equals ec7e1a8's committed games on the fresh deals (table 14,000, new decks 8,500) and on the development deals (14,000 and 8,500).
  - km3 equals B's committed games (14,000 and 8,500).
  - k3, kp3 and kog3 equal the Sept 28 pin's references, 14,000 of 14,000 each.
  - `deckgym simulate` repeats Sept 28's k3, kp3 and kog3 lines on seed 7,100 and runs kta3 and km3; goldfish `--coverage` runs.
- **History:** `../engine-2026-09-28/` (main-9b4df9b) and earlier are kept unchanged, with their hashes in the manifest's historical releases.
"""

SWITCH_README = """# The kta/km engine switch (Sept 30): main-9b4df9b → main-@MERGE7@

**Dustin, Sept 30** (verbatim in RUN5, km, "The official engine switch carrying kta and km"): prepare now; "Yes, pin if all pass (Recommended)"; the default pilot "km3 (Recommended)"; the rules items "Keep them out (Recommended)". A mismatch would have stopped the switch with the manifest untouched and gone to him first. The plan he answered: `PLAN.md`.

**What changes in engine/** (`git diff --stat 9b4df9b @MERGE7@ -- engine`): players only, `players/mod.rs`, `players/public_pricing_player.rs` and `players/value_functions.rs`. `engine/` is B's tree 9c84fef exactly. The rules code is unchanged, so the rules-side steps (the repair mechanic check, the refactor check, new frozen k3 and kp3 tables) don't apply; any rules item comes in a later switch under the full procedure.

## Preparation (`prepare.sh`; `PIN_STATUS.txt`)

- Built `deckgym`, `legality_scan` and `goldfish` from `git archive` of @CAND7@ (main plus 53fc5a1).
- **Identity** (`identity_check.txt`): each replay matched by (pairing, game number), counts asserted.

| pilot | reference | games | result |
|---|---|---:|---|
| kta3 | ec7e1a8's fresh games, `kta_tables_2026-09-29/ec7e1a8_fresh_kta3_table.jsonl` and `_new17` (the only replay never played at B) | 14,000 + 8,500 | identical |
| kta3 | ec7e1a8's development games, `kt_tables_2026-09-28/ec7e1a8_kta3_table.jsonl` and `_new17` | 14,000 + 8,500 | identical |
| km3 | B's games, `km_tables_2026-09-30/1f6319e_km3_table.jsonl` and `_new17` | 14,000 + 8,500 | identical |
| k3, kp3, kog3 | the Sept 28 pin's references | 14,000 each | identical |

- The suggested extras (kq3 on the table, kog3 on the 17 new cells, kd3, kpr3) are reported beside in the same file when run (EXTRAS=1, the default; `PIN_STATUS.txt` says whether they ran). The plan didn't require them, but a difference there would still have stopped the run.
- `deckgym simulate`, 240 games on seed 7,100: k3, kp3 and kog3 repeat Sept 28's lines (150/90/0, 144/96/0, 149/91/0); kta3 and km3 run. goldfish `--coverage` runs.

## The pin (`pin.sh`, run once after PREPARE DONE)

- **Merge:** 53fc5a1 into main as @MERGE7@, a merge commit with parents main and 53fc5a1 (as a `--no-ff` merge makes one), made off-tree with git merge-tree and commit-tree. @CAND_NOTE@ Nothing outside `rl/results/` and `engine/src/players/` came along, and nothing was deleted (the MERGED line in `PIN_STATUS.txt`).
  - It brings the cloud's build and identity records onto main (`km_build_2026-09-29/`, `-09-30/`, `kt_kog_2026-09-28/`).
  - It also replaces existing records on main with the cloud branch's later versions: @RESULTS_MODIFIED@. Checked Sept 30 against main d353621, these were kt's registration (`kt_2026-09-26/README.md`: main's older "RE-ISSUED ON KOG" text gives way to amendment 2 and the withdrawn amendment 3, the text that main's `kta_2026-09-29/REGISTRATION.md` already cites as kt's source), the `BUILD.md` notes of kt, koh and kph, and `tool_turn_effect_census_2026-09-25/tool_census.rs` (the counter tool's extension from km's build round).
- **Programs:** copied to `rl/engine-2026-09-30/` with `SHA256SUMS`, the same hashes as the tested build, committed executable (mode 100755). In the manifest, main-9b4df9b moved to the history as superseded. `current_engine.py` resolves the new program.
- **Screen and floor:** both default to km3 (`run_screen.py`, `floor.py`, together; the calibration reads both and finds km3).
  - `floor.py`'s pricing-pilot pattern now matches every code B builds as a public-pricing player: kp, kq, kd, kpr, koa, kob, kor, kpf, kpg, kog, koh, kph, kpha, kphb, kt, kta, ktb, ktc and km, at any depth, and not k3.
  - Before, it matched only kp, kq, kd and kog, so under kta3 or km3 the floor would have flagged kp's 62 audited cards as unpriced, with no error.
  - `decks/screen/test_floor_pricing_pilot.py` lists those codes and checks them against `players/mod.rs`; `floor.py --self-check` now asserts that the floor's own pilot is a pricing code.
- **The floor's pre-use re-check under km3:** planned in `../floor_recheck_2026-09-30/PLAN.md`, committed with the pin, before any of its games.

**Name change to know about:** in the official program, `kt3`, `kta3`, `ktb3` and `ktc3` are the kog-based presets since this switch (kta3 the adopted one; kt3, ktb3 and ktc3 diagnostic, with no identity claim). The kp-based records (`kt_2026-09-26/identity/43cef0b_*`) replay on `rl/engine-2026-09-28/`, which is kept unchanged.

## After the pin

- **Before Push origin:** Fetch origin in GitHub Desktop. If it then offers Pull origin, origin/main has commits main lacks; ask the laptop session before pulling. `pin.sh` prints whether origin/main, as last fetched, is behind main.
- **After the push:** tell Sonnet's calibration task, and the cloud through Dustin's paste block, that the official engine is main-@MERGE7@ (`rl/engine-2026-09-30/`) and the working pilot is km3 on both sides of the screen and the floor. Take main before any screen, floor or calibration run, and start a new `--out` rather than resuming a kog3 file: its rows are for another engine and pilot, so they don't carry over.
- **The floor's pre-use re-check:** `bash rl/results/floor_recheck_2026-09-30/run_check.sh` (about 1 hour). If it fails, the floor isn't used until Dustin has seen the pages.
- **Left for a follow-up:** two labels still say kog3, the brew scorecard's header in `decks/screen/panel_ladder_2026-09-26/build_brew_scorecard.py` and `run_calibration.py`'s docstring. They are labels, not checks.

## Next switch backlog (rules items, kept out of this one by Dustin's word; each needs the full procedure)

- **Victory Star / Confusion repair** (`rules/09`). The cloud's drafts are 6415e39 and d4fbc2a on its branch.
- **Coin-flip prevention + Chase Order repair.** The cloud's draft is e52a73b on its branch.
  - Sonnet's independent second read (local branch sonnet/repair-review, 4d45dae, `SECOND_READ_sonnet.md`) found both ready for the laptop's switch review, with no blockers.
  - For that switch's replay: the kd follow-on one-line changes in `persistent_defender_damage` (`rules/09`) must travel with it, and one non-kog3 bot must be run through the cloud's scratch decks.
- **Upstream 09e964f's two knockout-promotion fixes** (`rules/09`, `engine/UPSTREAM.md`). They are not a clean pick: they bring observation and serde changes.
- **PR bcollazo/deckgym-core#383** (Heavy Helmet, Harden, Hide, Blocking Shell), if upstream merges it.
- **B4b card data** (upstream 9044ff6, reprint-only), pinned to Mega Garchomp ex's release.
"""

NEW = {"rl/engine-2026-09-30/README.md": ENGINE_README, "rl/results/engine_switch_2026-09-30/README.md": SWITCH_README}

# --- the edits -------------------------------------------------------------------------------------------------------

EDITS = {
    "START_HERE.md": [(
        "`rl/engine-2026-09-28/` (`deckgym`, `legality_scan`, `goldfish`), main-9b4df9b: rules4 plus the ten rules/09 "
        "repairs, with the kog pilot. `project_manifest.json` names it with its hashes, and `current_engine.py` and the "
        "screen resolve to it. Earlier engines are history there.\n",
        "`rl/engine-2026-09-30/` (`deckgym`, `legality_scan`, `goldfish`), main-@MERGE7@: rules4 plus the ten rules/09 "
        "repairs, with the km pilot (kta + N2) on both sides of the screen and the floor. `project_manifest.json` names it "
        "with its hashes, and `current_engine.py` and the screen resolve to it. Earlier engines are history there. Since "
        "Sept 30, `kt3`, `kta3`, `ktb3` and `ktc3` name the kog-based presets; the older kp-based ones replay on "
        "`rl/engine-2026-09-28/`.\n")],
    "CLAUDE.md": [(
        re.compile(r"- The official engine program is `rl/engine-2026-09-28/deckgym`.*?to it: copy it, never rebuild it\.\n", re.S),
        "- The official engine program is `rl/engine-2026-09-30/deckgym` (since Sept 30; main-@MERGE7@: the Sept 28 rules\n"
        "  unchanged, rules4 plus the ten rules/09 repairs, with the kog-based kta and km players added;\n"
        "  `rl/engine-2026-09-30/README.md`). The working pilot is km3, on both sides of the screen and the floor. Since\n"
        "  Sept 30, kt3/kta3/ktb3/ktc3 name the kog-based presets (kt3, ktb3 and ktc3 are diagnostic only). Earlier programs\n"
        "  (`rl/engine-2026-09-28/`, `-09-27/`, `-09-25/`, `rl/addon-0.7.2/deckgym`) are history; the verified add-on 0.7.2\n"
        "  wheel (`rl/addon-0.7.2/wheels/`) is unchanged, and run identities bind to it: copy it, never rebuild it.\n")],
    "rl/RUN5.md": [
        ("- **Official engine:** `rl/engine-2026-09-28/`, main-9b4df9b (pinned Sept 28; rules4 + the ten rules/09 repairs, "
         "with the kog, koh, kph and kt players). The rules-file refactor it carries passed RUN5's three-part check "
         "(`results/engine_switch_2026-09-28/`).\n",
         "- **Official engine:** `rl/engine-2026-09-30/`, main-@MERGE7@ (pinned Sept 30; a players-only switch: the Sept 28 "
         "rules unchanged, rules4 + the ten rules/09 repairs, with the kog-based kta and km players from B, 1f6319e). kta3 "
         "and km3 replay their recorded games game for game, and k3, kp3 and kog3 the Sept 28 references "
         "(`results/engine_switch_2026-09-30/`). kt3, ktb3 and ktc3 are now kog-based: diagnostic, no identity claim. The "
         "Sept 28 engine (`rl/engine-2026-09-28/`, main-9b4df9b) is kept; its kp-based kt presets replay the Sept 26-28 kt "
         "records.\n"),
        ("- **Pilot:** kog3 = kp3 + koa's opening switch A + kpg's discard-Energy credit F.\n"
         "  - It passed its composition check Sept 28 (`results/kog_composition_2026-09-27/READING.md`) and is \"unconfirmed\" "
         "until the post-freeze read.\n"
         "  - The screen and the floor use it on both sides; the floor was re-checked under it "
         "(`results/floor_recheck_2026-09-28/`).\n",
         "- **Pilot:** km3 = kta3 + N2 (the Stadium damage bonus in the clock); kta3 = kog3 + switch 1 (the Tool cut); "
         "kog3 = kp3 + koa's opening switch A + kpg's discard-Energy credit F.\n"
         "  - km3 was adopted in the tables Sept 30 (`results/km_tables_2026-09-30/READING.md`), after kta3 (Sept 30, "
         "`results/kta_tables_2026-09-29/READING.md`) and kog3 (Sept 28, `results/kog_composition_2026-09-27/READING.md`). "
         "Each is \"unconfirmed\" until the post-freeze read; if that read drops km, the default goes back to kta3.\n"
         "  - The screen and the floor use km3 on both sides since the Sept 30 engine switch. The floor's pre-use re-check "
         "under km3 is `results/floor_recheck_2026-09-30/` (planned and committed with the pin; if it fails, the floor isn't "
         "used until Dustin has seen the pages). The Sept 28 one, under kog3: `results/floor_recheck_2026-09-28/`.\n"),
        (". The screen and the floor stay on kog3 until the official engine switch.\n",
         ". The screen and the floor stayed on kog3 until the official engine switch (Sept 30, main-@MERGE7@).\n"),
        ("The screen and the floor stay on kog3 until the official engine switch carries kta and km.\n",
         "The screen and the floor stayed on kog3 until the official engine switch carried kta and km (pinned Sept 30 as "
         "main-@MERGE7@; they use km3 since).\n"),
        ("kt3, ktb3 and ktc3 are kept as B defines them, labelled diagnostic with no identity claim.\n",
         "kt3, ktb3 and ktc3 are kept as B defines them, labelled diagnostic with no identity claim.\n"
         "      - **Pinned Sept 30:** every replay matched (`results/engine_switch_2026-09-30/README.md`). The official engine "
         "is main-@MERGE7@ in `rl/engine-2026-09-30/`; the screen and the floor default to km3, with `floor.py`'s "
         "pricing-pilot pattern fixed and tested. The floor's pre-use re-check under km3 follows "
         "(`results/floor_recheck_2026-09-30/PLAN.md`).\n"),
        ("  - The engine switches of Sept 25, 27 and 28.\n",
         "  - The engine switches of Sept 25, 27, 28 and 30.\n"),
        ("with bit-for-bit reproduction of the k3, kp3 and kog3 tables (14,000 games each) on the pinned engine "
         "`rl/engine-2026-09-28/` plus a card-effect pass",
         "with bit-for-bit reproduction of the k3, kp3 and kog3 tables (14,000 games each) and of kta3's and km3's recorded "
         "games (the Sept 30 switch's references) on the pinned engine `rl/engine-2026-09-30/` plus a card-effect pass"),
    ],
}


def edited(rel):
    text = head(rel)
    assert "\r\n" not in text, f"{rel} has CRLF line endings"
    for old, new in EDITS[rel]:
        if isinstance(old, re.Pattern):
            hits = old.findall(text)
            assert len(hits) == 1, f"{rel}: pattern found {len(hits)} times"
            text = old.sub(lambda _m: new, text)
        else:
            text = once(text, old, new, rel)
    return head(rel), text


out = []
for rel in EDITS:
    a, b = edited(rel)
    out += difflib.unified_diff(a.splitlines(True), b.splitlines(True), f"a/{rel}", f"b/{rel}", n=3)
for rel, text in NEW.items():
    assert not os.path.exists(os.path.join(ROOT, rel)), f"{rel} exists already"
    assert text.endswith("\n")
    out += difflib.unified_diff([], text.splitlines(True), "/dev/null", f"b/{rel}", n=3)
open(os.path.join(HERE, "docs.patch"), "w", encoding="utf-8", newline="\n").write("".join(out))
print(f"docs.patch: {len(out)} lines; placeholders @MERGE7@, @CAND7@, @CAND_NOTE@ and @RESULTS_MODIFIED@ are filled by pin.sh")

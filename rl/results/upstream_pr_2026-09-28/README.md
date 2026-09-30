# Upstream pull request: non-attack damage fix (OPENED Sept 29: https://github.com/bcollazo/deckgym-core/pull/383)

**Opened Sept 29 by the laptop session at Dustin's word** ("You can do the pull request unless I need to"):
- The branch `fix/non-attack-damage-protections` (2aa705d) is on his fork, dacz8976-creator/deckgym-core. He had already forked it.
- The PR is from his account, with the title and body below plus two lines: the base it was tested on, and the Claude Code note.
- Upstream main had moved to 9044ff6 (B4b and 09e964f), which doesn't touch the PR's files. GitHub reports it MERGEABLE.
- Upstream's checks (build-and-test, build 3.12) were queued at opening. A first-time contributor's runs may wait for the maintainer's approval.

**Status (Sept 28, about 10:20 pm Central):**
- The commit author is now his noreply address. The branch commit is now `2aa705d` (it was `e5a0562` before the
  Water Shuriken test was added on Sept 28 about 10:45 pm; same author, same fix, one more test).
- The body's wording note is one sentence, and it has a place for the in-game result.
- Clippy passes (the cloud's run, Sept 29; section "Formatting and lint").
- Both in-game tests are done and in the body:
  - Poison (`heavyhelmetpoisontest.MP4`, Sept 28): Heavy Helmet cut an attack 110 → 90, then Poison did the full 10.
  - Water Shuriken (`20260929_195929000_iOS.MP4`, Sept 29): Heavy Helmet cut Blizzard 80 → 60, then Water Shuriken did the full 20.
  - Harden (`20260929_204425000_iOS.MP4`, Sept 29, Sol review lead-accepted): Water Shuriken did the full 20 through Harden, while the same Harden prevented Ice Wing's 40.
- Waiting on:
  - his Fork click and "push";
  - optionally, the Water Shuriken test for the second line. Dustin: "I'll get you proof". If it isn't done, delete that placeholder line before posting; the card text and the Poison test carry the argument.

Nothing here has been pushed to GitHub, no remote was added, and nothing was opened. The branch exists
only in the WSL clone `/home/dacz8976/upstream-pr/deckgym-core`. Nothing in the PocketDeckSim repo was
committed; the only files written there are this README and the `.patch`.

In plain words: four cards (Heavy Helmet, Cascoon's Harden, Shinx's Hide, Carracosta's Blocking Shell)
say they only work against damage "from attacks", but the upstream engine applies them to every kind of
damage (Poison, Burn, Darkrai's Bad Dreams, ...). The fix makes them work only against attack damage,
copying how the engine already treats Steel Apron and Metal Core Barrier. It comes with 6 tests (one of them
checks that Greninja's Water Shuriken is not cut by Heavy Helmet), and the whole existing test suite still passes.

## Facts

| | |
|---|---|
| Upstream | https://github.com/bcollazo/deckgym-core |
| Base (upstream `main`, re-checked with `git fetch` and `git ls-remote` at the end; it did not move) | `ca4b67f41eaa514103833b8b6f6829a1f0deaa37` |
| Branch | `fix/non-attack-damage-protections` |
| Branch commit | `2aa705d314d3c95441d0cd3f5a9c0290870e0f28` (one commit on top of the base). Author and committer: `dacz8976-creator <307781668+dacz8976-creator@users.noreply.github.com>`, GitHub's private noreply address (Dustin, Sept 28 about 10:15 pm: "yes, that's the right default for a public repository"). This replaces `e5a0562` (same fix, five tests) and, before that, `e4b3f95` (his Gmail address); he can confirm the address under GitHub Settings > Emails. |
| Commit message | "Limit Heavy Helmet, Harden, Hide and Blocking Shell to attack damage" (+ short explanation; its last paragraph now also lists the Water Shuriken test) |
| Diff | 3 files, +351 -7. `src/hooks/core.rs` +27 -7 (unchanged by the sixth test); `tests/rules.rs` +2; new `tests/rules/attack_damage_only_test.rs` +322 |
| Patch | `0001-Limit-Heavy-Helmet-Harden-Hide-and-Blocking-Shell-to.patch` (next to this file; checked with `git apply --check` against a clean checkout of the base: applies cleanly; Unix line endings, no CRs) |
| Remotes | only `origin` = upstream (clone default). Nothing added. |
| Logs | `/home/dacz8976/upstream-pr/logs/` (`main_baseline.log`, `newtests_on_main.log`, `newtests_on_main_soft.log`, `branch_rules.log`, `branch_full.log` for the five-test version; `sixth_on_unfixed_main.log` and `branch2_full.log` for the current six-test commit) |

## The change (all in `src/hooks/core.rs`)

- `get_heavy_helmet_reduction` now takes `attacking_player` and `is_from_active_attack` and returns 0
  unless the damage is from an attack by the opponent. Same first lines as `get_steel_apron_reduction`.
- Hide (`PreventAllDamageAndEffects`) gets `&& is_from_active_attack`.
- Blocking Shell (`PreventDamageFromBasic`) gets `is_from_active_attack &&`.
- Harden (`PreventDamageIfLessOrEqual`): `if prevented_by_threshold && is_from_active_attack`.
- The `matches!(..)` line for Harden is untouched (kept as one long line, which is how upstream has it).
- Short comments quote the relevant card text, like the Steel Apron / Metal Core Barrier comments do.

Not touched: Steel Apron, Metal Core Barrier, Safeguard, Shell Shield, Protective Poncho (its text says
"attacks and Abilities", so it should not be gated), and anything else.

## Tests

New file `tests/rules/attack_damage_only_test.rs`, registered in `tests/rules.rs` (that binary already holds
the "rules from the FAQ / Tips" tests, and the Sleep/Paralysis tests upstream accepted are in the same
folder). Written in upstream's style: `get_test_game_with_board`, `attack_action`, `state.apply_status_condition`,
`SimpleAction::EndTurn` / `ApplyDamage`, `add_effect`, `with_tool`.

| Test | Still true (passes on main and branch) | Bug (fails on main, passes on branch) |
|---|---|---|
| `test_heavy_helmet_cuts_an_opponents_attack_but_not_other_damage` | Snorlax (Retreat 4) + Heavy Helmet takes 20 from a 40 Vine Whip | Poison tick 0 instead of 10; Burn 0 instead of 20; Bad Dreams 0 instead of 20; own player's attack on own Bench: 10 instead of 30 |
| `test_heavy_helmet_does_not_cut_greninjas_water_shuriken` (added Sept 28 after Dustin's ruling) | none needed | Greninja's Water Shuriken (Ability, 20 to the opponent's Active) on a Snorlax holding Heavy Helmet: Snorlax takes 0 (150 HP left), should take the full 20 (130 left) |
| `test_harden_prevents_attack_damage_but_not_other_damage` | Vine Whip (40) still prevented | Poison 0 (should be 10), Burn 0 (20), Bad Dreams 0 (20) |
| `test_hide_prevents_attack_damage_but_not_other_damage` | Vine Whip still prevented | Poison 0 (10), Burn 0 (20), Bad Dreams 0 (20) |
| `test_blocking_shell_prevents_basic_attack_damage_but_not_ability_damage` | Mewtwo ex's Psychic Sphere (Basic, 50) still prevented | Bad Dreams 0 (should be 20) |
| `test_steel_apron_and_metal_core_barrier_are_unchanged` | Metal Core Barrier: Rollout 70 -> 20, Poison still 10. Steel Apron: Vine Whip 40 -> 30, Deceptive Needle still 10 | none (passes on main, on purpose: shows the diff does not widen) |

The "bug" column values for the Heavy Helmet, Harden, Hide and Blocking Shell tests were read off unfixed main with a throwaway soft-assert copy of
the file (results in `newtests_on_main_soft.log`; the file was then restored byte-identical). Every "still
true" assertion matched on main; every "bug" assertion mismatched exactly as listed. The real tests stop at the
first failing assertion, so on main they report: Poison for Heavy Helmet, Harden and Hide; Bad Dreams for
Blocking Shell; Snorlax at 150 instead of 130 for Water Shuriken. The sixth test was run against the real
unfixed `core.rs` (taken from `origin/main` for that one run, then the fix was restored;
`sixth_on_unfixed_main.log`): 5 failed, 1 passed (Steel Apron / Metal Core Barrier).

**Water Shuriken (Dustin's ruling, Sept 28 about 10:40 pm: "Heavy helmet doesn't protect against poison or
effects. Just attack. It doesn't protect against greninja's snipe ability either").** Upstream `ca4b67f`
implements it. `database.json` has the Ability on 6 Greninja printings; `effect_ability_mechanic_map.rs:355`
maps "Once during your turn, you may do 20 damage to 1 of your opponent's Pokémon." to
`AbilityMechanic::DamageOneOpponentPokemon { amount: 20 }`; `damage_one_opponent` in
`apply_abilities_action.rs:484` queues one `ApplyDamage` choice per opponent Pokémon (Active and Bench) with
`is_from_active_attack: false`; that goes through `handle_damage` into `modify_damage`. So on unfixed main
Heavy Helmet cut it (20 - 20 = 0). The test drives the real path (`UseAbility`, then picks the offered
`ApplyDamage` on the Active). Existing upstream coverage only checks Protective Poncho against it
(`tests/tools/protective_poncho_test.rs`).

Note on Blocking Shell: on main it does not actually stop Carracosta's own Poison or Burn (Carracosta is a
Stage 2, so its own checkup damage is never "from a Basic Pokémon"). Only Ability damage that comes from a
Basic Pokémon (Bad Dreams, from Darkrai) was wrongly stopped. The brief lumped all four cards together on
Poison/Burn; this one is narrower, so its test uses Bad Dreams.

## Test results

Command (CI's own): `cargo test -j 2 --no-fail-fast --features "tui test-utils" --all-targets`, `nice -n 19`,
CARGO_BUILD_JOBS=2, RAYON_NUM_THREADS=2, RUST_TEST_THREADS=2, only in the upstream clone. (`--no-fail-fast`
added so a failure could not hide later binaries; there were none.)

| | passed | failed | ignored | exit |
|---|---|---|---|---|
| `main` (`ca4b67f`, pristine) | 1170 | 0 | 0 | 0 |
| the six new tests on unfixed `core.rs` (`cargo test --test rules attack_damage_only`) | 1 passed (Steel Apron / Metal Core Barrier) | **5 failed**: Heavy Helmet, Water Shuriken, Harden, Hide, Blocking Shell | 0 | 101 |
| branch (`2aa705d`) | 1176 | 0 | 0 | 0 |

(The first run of the five original tests on unfixed main, before the Water Shuriken test existed, was the whole
rules binary: 36 passed, 4 failed. `newtests_on_main.log`.)

The only per-binary difference between main and branch is `tests/rules.rs`: 35 -> 41 passed. The Steel
Apron / Metal Core Barrier test passes on both, as intended. CI's later steps (the four `cargo run` example
simulations, the card generators, the Python/maturin workflow) were not run; nothing in this change touches them.

## Formatting and lint

- **cargo fmt:** `cargo fmt -- --check` exits 0 on pristine main and on the branch (no output). This used the
  Ubuntu `rustfmt 1.8.0` (Rust 1.93 family) that an earlier PocketDeckSim session had already unpacked on
  disk (`~/.local/share/pocket-deck-lab/paused-session-2026-09-06/pdl-rustfmt-20260905/`). I checked its
  provenance first: the `.deb` there has SHA256 `5637586a...4abd`, identical to the Ubuntu archive index entry
  for `rustfmt-1.93` on this machine, and the installed `rustc` is Ubuntu's 1.93.1. Nothing was downloaded or
  installed. CI uses "stable" rustfmt, which could differ in tiny details from 1.8.0, so a CI fmt complaint
  is not impossible, but nothing here looks at risk. rustfmt did reformat two spots in the new test file
  before commit (applied).
- **clippy: passes (the cloud, Sept 29; its report is `CLOUD_CLIPPY.md` on the cloud branch `claude/pensive-ptolemy-spwc0b`).** Stable toolchain, rustc 1.94.1, clippy 0.1.94.
  - `cargo clippy --features "tui test-utils" -- -D warnings` (CI) and `cargo clippy --features tui -- -D warnings` (CONTRIBUTING) both pass with 0 warnings, on the patched tree and on the base.
  - `cargo fmt -- --check` passes on both.
  - It ran on the five-test version (main e2ea0c4). The sixth test added afterwards is test code only, which neither clippy command lints, and `core.rs` is unchanged since. fmt was re-run clean after it.
  - An extra `--all-targets` pass found one warning, identical on the base, in a file the patch doesn't touch (`tests/pokemon/victini_victory_star_test.rs:175`). There is none in the patch's files.
- The earlier note, kept for the record: **clippy was not run locally.** The message relayed to me said to install rustfmt and clippy with
  `rustup component add rustfmt clippy`. I did not do that. This machine's Rust comes from Ubuntu apt (there is
  no rustup toolchain, so that command would not apply as written), the original brief said not to install
  anything, and an approval relayed by another agent is not Dustin's own OK to download and install
  software. To get clippy, Dustin (or the laptop session, with his OK) would install Ubuntu's `cargo-clippy` /
  a rustup toolchain, then run CI's exact line: `cargo clippy --features "tui test-utils" -- -D warnings`.
  Note CI's clippy line has no `--all-targets`, so it lints only the library and binaries, not tests; the only
  non-test code touched is a few conditions in `core.rs`, which I do not expect to raise anything.
- Upstream's optional pre-commit hook (`git config core.hooksPath .githooks`) is not enabled in this clone; I
  did not commit through it.

## Re-verification of the brief against upstream `ca4b67f`

All confirmed before editing, at exactly the quoted lines: `get_heavy_helmet_reduction` (696-709) had no attack or
opponent gate; its result is subtracted from all damage in `modify_damage` (1593-1601); Hide and Blocking
Shell (1387-1404) and Harden (1603-1610) had no `is_from_active_attack` gate; Steel Apron (733-739, attack and
opponent gate) and Metal Core Barrier (711-716, attack gate) are gated. Differences and extras worth knowing:

1. **Blocking Shell** does not block Poison/Burn on main (see the note under Tests). Only Basic-source Ability
   damage (Bad Dreams) is wrongly blocked.
2. Poison and Burn are applied with `handle_damage_only(.., is_from_active_attack = false)` and the Pokémon
   itself as the "attacker" (self damage), so the opponent gate alone would not have covered Bad Dreams
   (Darkrai is the attacker there, `false`), and the attack gate alone would not cover the holder's own
   attacks. Heavy Helmet needs both gates.
3. `PreventAllDamageAndEffects` is used by about three dozen texts in `database.json` (36 card printings, Shinx's
   two among them: coin-flip attacks, "If your opponent's Pokémon is Knocked Out...", Samurott's Stance). I
   listed every distinct text: all say "by attacks" or "from—and effects of—attacks", so gating it is right
   for all of them.
   `PreventDamageIfLessOrEqual` (threshold 40) and `PreventDamageFromBasic` are each used by one card.
4. Anything the engine already marks `is_from_active_attack: false` now passes through these four the way it
   already passes through Steel Apron, Metal Core Barrier, Safeguard and Shell Shield: Poison, Burn, Bad
   Dreams and other Ability damage (evolve pings, Snowy Terrain / Sand Slammer at Checkup), Tool damage
   (Rocky Helmet-style retaliation, Deceptive Needle) and delayed-effect damage (Mismagius's Cursed Prose,
   Meowscarada ex's Flower Trick). The last group is upstream's existing classification ("not from an active
   attack"); this change just makes the four cards consistent with it.
5. Not touched, noticed: `get_heavy_helmet_reduction` reads the printed Retreat Cost (`retreat_cost.len() >= 3`),
   not the current one after retreat modifiers. `rules/07_engine_audit_2026-09-22.md` (H2) already lists that as
   a separate open question. Out of scope here.
6. I did not re-check the fork commits `e2ca3ba` / `53cba79` (they are not in upstream); the upstream code was
   fixed and tested on its own.
7. **Greninja's Water Shuriken is implemented upstream and reaches `modify_damage` with
   `is_from_active_attack = false`**, so Heavy Helmet used to cut it to 0 (details under Tests). Same root
   cause, no extra code change needed; it only got its own test.

## Card text (from `python3 lib/card.py`, run in the PocketDeckSim repo)

Identical, character for character, to the strings in upstream's `database.json` (checked).

```
Heavy Helmet  [B1 219]  Trainer
  If the Pokémon this card is attached to has a Retreat Cost of 3 or more, it takes -20 damage from attacks from your opponent's Pokémon.
Cascoon  [B1 006]  Grass  Stage 1 (from Wurmple)  HP 80  weak Fire  retreat 3
  [G] Harden — During your opponent's next turn, prevent all damage done to this Pokémon by attacks if that damage is 40 or less.
Shinx  [A2 058, A2 163]  Lightning  Stage 0  HP 60  weak Fighting  retreat 1
  [L] Hide — Flip a coin. If heads, during your opponent's next turn, prevent all damage from—and effects of—attacks done to this Pokémon.
Carracosta  [B1 067]  Water  Stage 2 (from Tirtouga)  HP 150  weak Lightning  retreat 3
  [WWC] Blocking Shell 100 — Prevent all damage done to this Pokémon by attacks from Basic Pokémon during your opponent's next turn.
Steel Apron  [A4 153]  Trainer
  The [M] Pokémon this card is attached to takes -10 damage from attacks from your opponent's Pokémon, recovers from all Special Conditions, and can't be affected by any Special Conditions.
Metal Core Barrier  [B2 148, B2b 117]  Trainer
  If this card is attached to 1 of your Pokémon, discard it at the end of your opponent's turn.The [M] Pokémon this card is attached to takes -50 damage from attacks from your opponent's Pokémon.
Darkrai  [B2b 040]  Darkness  Stage 0  HP 100  weak Grass  retreat 2
  Ability Bad Dreams: At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20 damage to that Pokémon.
Greninja  [A1 089, A3a 093, A4b 114, A4b 115, A4b 356, P-A 019]  Water  Stage 2 (from Frogadier)  HP 120  weak Lightning  retreat 1
  Ability Water Shuriken: Once during your turn, you may do 20 damage to 1 of your opponent's Pokémon.
```

Wording, since the brief expected "from attacks": only **Heavy Helmet** says "from attacks" word for word.
**Harden** and **Blocking Shell** say "by attacks" (Blocking Shell: "by attacks from Basic Pokémon"), and **Hide**
says "from—and effects of—attacks" (with em dashes). I quoted each exactly as printed; the PR body bolds the
phrase that limits each one to attacks and says so plainly. Steel Apron and Metal Core Barrier say "from attacks
from your opponent's Pokémon" (and Metal Core Barrier's printed text really has no space in "turn.The").

## Rules citation (from the PocketDeckSim `rules/` folder)

`rules/` does have the source. Nothing there names Bad Dreams itself, so the chain is: Bad Dreams is an
Ability, and the official FAQ says Ability damage is not attack damage.

1. `rules/02_damage_knockouts_points.md`, section 4 "Kinds of damage and prevention", lines 75-80:
   - line 78: `| Poison / Burn at Checkup | **No** | [OFFICIAL] Mimikyu ex FAQ |`
   - line 79: `| Ability damage (Greninja Water Shuriken, Crobat Cunning Link, Darkrai Nightmare Aura, Flygon ex Sand Slammer) | **No** | [OFFICIAL] Mimikyu FAQ + [COMMUNITY] did2memo ...`
     (the column header, line 75, is `Counts as "damage from an attack"?`)
   - line 80: Tool damage (Rocky Helmet, Deceptive Needle): No, [OFFICIAL] Mimikyu FAQ
   - lines 83-86: "Therefore "takes -X damage from attacks", Disguise, Safeguard, "prevent all damage done by
     attacks", Giovanni-style boosts and Weakness all ignore those non-attack sources ... Heavy Helmet reduces
     attack damage only. Metal Core Barrier and Steel Apron are right."
2. `RULES_FOR_AGENTS.md`, lines 79-82: "Damage from Abilities and Special Conditions is not "damage from an
   attack": effects that reduce or prevent attack damage (Shuckle ex's Solid Shell, Oricorio's Safeguard,
   "-20 from attacks" Tools) do nothing against poison ticks, ability pings or Rocky Helmet (official: Mimikyu
   ex FAQ)."
3. The original source they cite: the official **Detailed Battle FAQ** (in the game: Menu > Tips > Detailed
   Battle FAQ; section https://app-ptcgpt.pokemon-support.com/hc/en-us/sections/53604902813209), article
   **55980981811097**, "Why didn't Mimikyu ex's Disguise Ability prevent damage?". As recorded in
   `rules/_research_notes/detailed_battle_faq.md` lines 38-40 (captured 2026-09-21):
   - "Mimikyu ex's Disguise Ability does not prevent damage that doesn't come from attacks."
   - Not blocked: "Damage from Special Conditions (such as Poisoned or Burned)"; "Damage from Pokémon
     Abilities (such as Greninja's Water Shuriken)"; "Damage from Pokémon Tools (such as Rocky Helmet)".
   - **Caveat:** line 5 of that file says it was "Captured via WebFetch (summarizer); quoted sentences are as
     returned", so the wording is second-hand. I tried to fetch the article myself and the site answered
     HTTP 403, so I could not confirm the exact words. See "Before you post" below.

Also: `rules/07_engine_audit_2026-09-22.md` lines 81-84 (H2 records the Heavy Helmet card text and the same
source) and `rules/09_engine_repairs_2026-09-22.md` lines 13 and 176-178 (the fork's own repairs of exactly
these bugs). Those are the fork's notes, not independent sources.

Upstream's `tests/rules.rs` header already treats "the in-app Tips panel and the app-linked official Detailed
battle FAQ" as its sources, which is why the tests live there and the PR body cites the same FAQ.

## Decisions (Dustin, Sept 28 about 10:15 pm, verbatim via Fable)

1. **Commit author:** "The noreply address: yes, that's the right default for a public repository." Done: the commit is now `2aa705d` (was `e5a0562`) with `307781668+dacz8976-creator@users.noreply.github.com`, read from his signed-in GitHub account; the sixth-test amend kept that identity.
2. **clippy:** "yes, paste it." The cloud is running CI's clippy and fmt on the patch. Its result goes in `CLOUD_CLIPPY.md` and is folded in here when it lands.
3. **The rule's evidence:** "do it as an in-game test rather than a text lookup, and put the result in the pull request body ... One solo battle: Heavy Helmet on your Active, get it Poisoned, read the Checkup damage. If you can also do it with a Harden or Hide Pokémon, the four cards are covered; if not, Heavy Helmet plus the card texts is enough." The PR body has a place for the result, with the FAQ citation beneath it as secondary.
4. **The card wording:** all four limit the reduction to attacks, "which is the whole argument". The body says it in one sentence, not as a caveat.
5. **Pushing:** the laptop's WSL git signs in to GitHub through `gh` (the same sign-in that pushes PocketDeckSim). Nothing is pushed until he reports the in-game test, forks, and says push.
6. **The Heavy Helmet ruling (Sept 28 about 10:40 pm, verbatim via Fable):** "Heavy helmet doesn't protect against poison or effects. Just attack. It doesn't protect against greninja's snipe ability either, but I'll get you proof." He does the in-game tests himself. This is what the fix already does; the sixth test pins the Greninja case, and the body has a second "Verified in-game" line for it.

## Before you post (Dustin): the in-game test

- One solo battle. Heavy Helmet on your Active: it needs a Retreat Cost of 3 or more, e.g. Snorlax, Cascoon or Carracosta. Get it Poisoned, then read the damage at Checkup: 10 means Heavy Helmet didn't cut it, which is the rule; 0 would mean it did.
- If you can, also do it with Cascoon's Harden or Shinx's Hide in effect: Poison should still do 10.
- Greninja's Water Shuriken on a Pokémon holding Heavy Helmet (Retreat Cost 3 or more): the Ability's 20 should land in full (20, not 0). Your result fills the second "Verified in-game on Sept 29" line in the body.
- Record it in the Pocket Shot List as you did the Helmet, Rare Candy and Pulse checks. The laptop then fills the line "Verified in-game on Sept 29" in the body.
- **Done for Poison (Sept 28):** `heavyhelmetpoisontest.MP4`, reviewed by Sol with an independent lead check (`Battle Logs/Recording_QA/heavyhelmetpoisontest_sol/`).
  - Heavy Helmet cut Magmar's Derisive Roasting from 110 to 90, then Poison did the full 10 at Checkup.
  - The first "Verified in-game" line in the body is filled from that review.
- **Done for Water Shuriken (Sept 29):** recording `20260929_195929000_iOS.MP4`, reviewed by Sol with an independent lead check (`Battle Logs/Recording_QA/20260929_195929000_iOS_rule_sol/`).
  - Blizzard's printed 80 did 60 to Heavy Helmet Regigigas (Retreat Cost 4), then Water Shuriken did the full 20 (60 → 40).
  - The second "Verified in-game" line is filled from that review. Both in-game lines are done.

## Steps for Dustin (website / GitHub Desktop terms)

You do not need GitHub Desktop for this one: the branch lives in the WSL folder and the laptop Claude
session does the push. You do the clicking on github.com.

**(a) Fork.** Go to https://github.com/bcollazo/deckgym-core. Click **Fork** (top right). On the "Create a new
fork" page make sure Owner is **dacz8976-creator**, leave "Copy the `main` branch only" ticked, click **Create fork**.
You end up on https://github.com/dacz8976-creator/deckgym-core.

**(b) Tell the laptop Claude session, and say OK to the push.** Something like: "The fork exists at
github.com/dacz8976-creator/deckgym-core. OK to push the branch `fix/non-attack-damage-protections` to it."
Only after that OK does the laptop session add your fork as a remote and push that one branch (it needs to be
signed in to GitHub as you). It should not push anything else and should not touch upstream's `main`.

**(c) Open the pull request.** On your fork's page you will see a yellow bar, "fix/non-attack-damage-protections
had recent pushes", with a **Compare & pull request** button. Click it. Then:
1. Check the top line: base repository `bcollazo/deckgym-core`, base `main`; head repository
   `dacz8976-creator/deckgym-core`, compare `fix/non-attack-damage-protections`.
2. Paste the **title** and the **body** from below (Markdown renders as you type in the "Preview" tab).
3. Click the **Files changed** tab. You should see exactly 3 files: `src/hooks/core.rs`,
   `tests/rules.rs`, `tests/rules/attack_damage_only_test.rs`, about +351 -7. If it shows anything else, stop and ask.
4. Back on the first tab, click the green **Create pull request**.

After that GitHub runs upstream's checks (fmt, clippy, tests). For a first-time contributor the maintainer may
have to click "Approve and run workflows" before they start, so a "waiting" status is normal. If a check
fails, tell the laptop session; a clippy or fmt complaint is a small fix and a new commit on the same branch
updates the pull request by itself.

**Upstream's requirements:** there is no pull-request template (`.github/` only has workflows and card
prompts). `CONTRIBUTING.md` asks you to fork, branch, commit, push, open the PR, and to make sure `cargo fmt`,
`cargo clippy --features tui -- -D warnings` and `cargo test --features "tui test-utils"` pass (CI runs the
same). All three pass: fmt and tests here, clippy in the cloud. It also welcomes AI-assisted contributions.

## PR title (paste as is)

```
Limit Heavy Helmet, Harden, Hide and Blocking Shell to damage from attacks
```

## PR body (paste as is)

````markdown
## What this fixes

Four cards say they only apply to damage **from attacks**. In `modify_damage` (`src/hooks/core.rs`) they currently apply to every kind of damage instead:

- **Heavy Helmet**: the holder takes 20 less from Poison and Burn (a Poison tick becomes 0), from Ability damage such as Darkrai's Bad Dreams or Greninja's Water Shuriken, from Tool and delayed-effect damage, and even from attacks of its own player.
- **Cascoon's Harden** and **Shinx's Hide**: while the effect lasts, the Pokémon also ignores Poison, Burn and Bad Dreams damage.
- **Carracosta's Blocking Shell**: also ignores Ability damage that comes from a Basic Pokémon (Bad Dreams is Darkrai's Ability, and Darkrai is a Basic). Carracosta's own Poison and Burn were never affected, because Carracosta is a Stage 2, not a Basic.

## Card text

Exactly as stored in `database.json`, with the wording that limits each card to attacks in bold:

- **Heavy Helmet** (B1 219): "If the Pokémon this card is attached to has a Retreat Cost of 3 or more, it takes -20 damage **from attacks** from your opponent's Pokémon."
- **Harden** (Cascoon, B1 006): "During your opponent's next turn, prevent all damage done to this Pokémon **by attacks** if that damage is 40 or less."
- **Hide** (Shinx, A2 058 / A2 163): "Flip a coin. If heads, during your opponent's next turn, prevent all damage **from—and effects of—attacks** done to this Pokémon."
- **Blocking Shell** (Carracosta, B1 067): "Prevent all damage done to this Pokémon **by attacks from Basic Pokémon** during your opponent's next turn."

Each text, quoted exactly, limits the card to damage done by attacks.

## Why Poison, Burn and Ability damage are not damage from attacks

**Verified in-game (recorded test, Sept 28):**
- Wailmer (100 HP, Retreat Cost 3) held Heavy Helmet in the Active Spot.
- Team Rocket's Weezing ex's Boiler Smog made it Poisoned and Burned.
- Team Rocket's Magmar then used Derisive Roasting: "10, ... 50 more damage for each Special Condition affecting your opponent's Active Pokémon", so 110. The game showed **90**, with Heavy Helmet's indicator, and Wailmer went from 100 to 10 HP. That is the −20 on an attack.
- At Checkup, **Poison then did its full 10** (10 → 0 HP): Heavy Helmet did not reduce it.

**Verified in-game (recorded test, Sept 29):**
- Regigigas (Retreat Cost 4) held Heavy Helmet in the Active Spot.
- Articuno ex's Blizzard, printed 80, did **60** to it (120 → 60 HP): the −20 on an attack.
- On the opponent's next turn, Greninja's Water Shuriken ("Ability Water Shuriken: Once during your turn, you may do 20 damage to 1 of your opponent's Pokémon.") did the **full 20** to the same Helmet-wearing Regigigas (60 → 40 HP): Heavy Helmet did not reduce the Ability's damage.

**Verified in-game (recorded test, Sept 29), Harden:**
- Cascoon used Harden, and the game showed its protection.
- On the opponent's next turn, Water Shuriken did the **full 20** to it (110 → 90 HP).
- Then, in the same turn, Articuno ex's Ice Wing (40, an attack) was **prevented** by the same Harden (HP stayed 90).
- So Harden stops attack damage of 40 or less, and not an Ability's damage.

The official Detailed battle FAQ (in the game under Tips), "Why didn't Mimikyu ex's Disguise Ability prevent damage?", also says Disguise "does not prevent damage that doesn't come from attacks", and lists as not blocked: damage from Special Conditions (such as Poisoned or Burned), from Pokémon Abilities (such as Greninja's Water Shuriken) and from Pokémon Tools (such as Rocky Helmet). Wording as recorded in the PocketDeckSim rules notes (`rules/_research_notes/detailed_battle_faq.md`, lines 38-40, captured 2026-09-21); the same notes tabulate it in `rules/02_damage_knockouts_points.md`, section 4, lines 78-79: "Poison / Burn at Checkup: No" and "Ability damage: No", both graded official (Mimikyu ex FAQ).

Darkrai's Bad Dreams is an Ability ("Ability Bad Dreams: At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20 damage to that Pokémon."), and so is Greninja's Water Shuriken ("Ability Water Shuriken: Once during your turn, you may do 20 damage to 1 of your opponent's Pokémon."), so both are Ability damage under the same reading. `tests/rules.rs` already builds its tests on this FAQ and the in-app Tips.

## The change

The engine already does this for the neighbouring cards. `get_steel_apron_reduction` returns 0 unless `is_from_active_attack` (and the attacker is the opponent), `get_metal_core_barrier_reduction` returns 0 unless `is_from_active_attack`, and the Safeguard and Shell Shield checks in `modify_damage` also test `is_from_active_attack`. This PR copies that gate:

- Heavy Helmet: `get_heavy_helmet_reduction` now takes `attacking_player` and `is_from_active_attack` and returns 0 unless the damage is from an attack by the opponent, exactly like `get_steel_apron_reduction` ("from attacks from your opponent's Pokémon").
- Hide, Blocking Shell, Harden: the prevention now also requires `is_from_active_attack`.

Nothing else changes (Steel Apron, Metal Core Barrier, Safeguard, Shell Shield and Protective Poncho are untouched). Damage the engine already flags as not from an attack (Poison, Burn, Ability damage, Tool damage such as Deceptive Needle and Rocky Helmet, delayed damage such as Cursed Prose) now goes through these four cards the same way it already goes through Steel Apron and Metal Core Barrier.

## Tests

New `tests/rules/attack_damage_only_test.rs` (registered in `tests/rules.rs`), six tests:

- `test_heavy_helmet_cuts_an_opponents_attack_but_not_other_damage`: still -20 on an opponent's attack (Retreat Cost 4); Poison, Burn, Bad Dreams and the player's own attack on their own Bench are not reduced.
- `test_heavy_helmet_does_not_cut_greninjas_water_shuriken`: Water Shuriken (an Ability) deals its full 20 to a Heavy Helmet holder with Retreat Cost 4.
- `test_harden_prevents_attack_damage_but_not_other_damage`: a 40-damage attack is still prevented; Poison, Burn and Bad Dreams are not.
- `test_hide_prevents_attack_damage_but_not_other_damage`: attack damage is still prevented; Poison, Burn and Bad Dreams are not.
- `test_blocking_shell_prevents_basic_attack_damage_but_not_ability_damage`: a Basic's attack is still prevented; Bad Dreams (from a Basic) is not.
- `test_steel_apron_and_metal_core_barrier_are_unchanged`: both still reduce an opponent's attack (-10 and -50) and still leave Poison / Deceptive Needle damage alone. It passes before and after, so the diff does not widen anything.

On `main` all but the Steel Apron / Metal Core Barrier test fail (Poison, Burn, Bad Dreams and Water Shuriken deal 0; the own-Bench attack is cut by 20); that one passes. With this change all six pass.

## Checks

- `cargo test --features "tui test-utils" --all-targets`: `main` 1170 passed, 0 failed; this branch 1176 passed, 0 failed (the six new tests).
- `cargo fmt -- --check`: clean.
- `cargo clippy --features "tui test-utils" -- -D warnings` and `cargo clippy --features tui -- -D warnings`: pass, 0 warnings.
````

# Deckgym upstream and Cliff review for Claude agents

Prepared for Dustin and the PocketDeckSim Claude agents on October 16, 2026, America/Chicago.

The two reviews compared our repaired PocketDeckSim engine with bcollazo/deckgym-core and examined IncredibleAloeVera/deckgym-core, the reinforcement-learning fork shared in Discord. The practical goal is to improve reliable play of Dustin's decks, starting with Kingambit, and identify small, useful contributions back to the community.

**Main findings, revised after Sonnet's broader comparison:** the immediate upstream opportunity is B4b printing compatibility, including Mega Garchomp ex, at the next tested engine pin. Sonnet's source comparison found no missing upstream gameplay repair that changes the currently inspected deck matchups; that is not a runtime equivalence result. About 30 local fixes are candidates to offer upstream. Cliff is a real released model, but a trial is not recommended for the current Kingambit work because four key card effects are incomplete and most inspected ladder decks are outside its usable pool.

## Reconciliation with Sonnet's wider review

This revision incorporates the reports Dustin supplied, after reading their actual committed README files and Cliff pool-check output. Sonnet's deck-by-deck comparison provides the practical prioritization missing from the first version of this handoff. Its reports inventory 232 findings and report independent review of 128. Those counts describe Sonnet's workflow; this reconciliation did not independently repeat all 232 comparisons.

| Decision | Revised conclusion |
| --- | --- |
| What to import first | B4b data plus Trainer canonical lookup and our remaining printing-specific handlers, tested together at the next engine pin. The 438 additional entries are 437 reprints and Mega Garchomp ex. |
| What affects current play | Sonnet found no missing upstream gameplay fix that changes the listed matchups. Several missing guards and performance fixes concern cards or states outside those lists. This is a bounded source-review conclusion, not proof that every possible game is identical. |
| What to preserve | Our current Heavy Helmet behavior and the other local rules repairs listed below. Importing the upstream implementation of our own PR 383 would regress the later local Helmet repair. |
| What we already contributed | Both PR 335 and PR 383 are merged. The earlier handoff omitted PR 335. |
| Whether to trial Cliff | No trial now. Kingambit's attack and the relevant Alolan Muk, Glimmora and Regigigas abilities are listed as incomplete. Sonnet's pool check finds only 1 of the 8 ladder-sheet decks and 4 of the 8 panel lists in range. |
| What remains useful from Cliff | Dataset preparation, reveal-memory tests, model compatibility checks, and opponent-pool ideas. The hidden-information concern below remains unresolved and was not addressed by Sonnet's pool review. |

Evidence: [Sonnet's upstream report][sonnet-upstream] at c0fcff86e398eaf3592af5ebdb104e7841ae0850, with [full upstream findings][sonnet-detail-a] and [local contribution findings][sonnet-detail-b]; [Sonnet's Cliff report][sonnet-cliff] and [pool-check output][sonnet-pool] at 6b83f1626e4de11232dac3bad7a7af1ed7ed6de9. These are separate review branches, not new engine releases.

Two qualifications matter when passing on the summaries. First, Cliff does not strictly require NVIDIA hardware: its README documents CPU NdArray and a portable WGPU backend, although current-size WGPU throughput is unmeasured. CUDA requires NVIDIA; practical retraining time on Dustin's hardware was not measured. Second, a reading of direct observation fields alone does not establish that derived features contain no hidden information; retain the source-level Cyberjack concern below. Neither qualification changes the recommendation against a trial for the current decks.

## Scope and evidence

This is a source review and handoff, not a tested integration. GitHub metadata, code, existing tests, local rules records, and release metadata were inspected. Neither external fork nor our engine was built or exercised for these reviews. Previously recorded test results and video observations are identified as existing evidence; the recordings were not watched again.

- **Verified source difference:** code or repository metadata directly inspected.
- **Existing local validation:** previously recorded tests or observations, not rerun here.
- **Author-reported:** a claim or measurement published by the fork author.
- **Needs reproduction:** a plausible or source-traced problem whose runtime behavior was not demonstrated in these reviews.

No simulator code, official release, training configuration, or experiment registration was changed. No GitHub comments, issues, or PRs were posted. Recommendations below are proposed follow-up work and do not supersede current ownership or registered runs.

### Reviewed versions

| Project | Reviewed revision and meaning |
| --- | --- |
| PocketDeckSim checkout | HEAD 35adace7a3013e506aa0dd16936150fc62e7409d, rechecked while preparing this file. |
| Official local engine | main-c045ede, source c045ede0e6d69c9dcb8d4cb3165c8ada3f8ef72e; executables in rl/engine-2026-10-12/. |
| Local engine source identity | HEAD and c045ede both reference engine tree 70652fff03af511e32a169e16209e158a998dda6. This establishes committed source identity, not a fresh binary test. |
| bcollazo/deckgym-core | c3083a3f3191f8a3cccde5fc7f5b7e0033f91fff, current main when checked October 16. |
| IncredibleAloeVera/deckgym-core | e69eea302a4c60802a3a2ba4ad4a219d76b9cc81, current main when checked October 16; that commit is dated August 13, 2026. |

Canonical local checkout: C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim. Pocket Deck Lab is the archived predecessor.

Read [START_HERE.md](../../../START_HERE.md), [PROJECT_INSTRUCTIONS.md](../../../PROJECT_INSTRUCTIONS.md), [RULES_FOR_AGENTS.md](../../../RULES_FOR_AGENTS.md), and current [RUN5.md](../../RUN5.md) before acting. [project_manifest.json](../../../project_manifest.json) identifies the official engine and separate RL add-on. The add-on remains version 0.7.2 on its recorded rules4 engine; it is not automatically the October 12 CLI engine.

GitHub status can change after this handoff. Source links below are pinned where practical; issue and PR pages show live discussion.

## The accepted contributions

[PR 335](https://github.com/bcollazo/deckgym-core/pull/335), also submitted by dacz8976-creator, implements Hisuian Goodra's Securely Sheltered and Bastiodon's Guarded Grill. GitHub metadata was rechecked for this reconciliation: opened July 21, 2026, at 22:42:01 UTC; merged July 22 at 15:04:42 UTC. Its merge commit is ed030d355e216fae0a4d508eb5bc83bd93d6185b. This is an earlier accepted contribution that the first handoff missed.

[PR 383](https://github.com/bcollazo/deckgym-core/pull/383), submitted by dacz8976-creator, limits Heavy Helmet, Harden, Hide, and Blocking Shell to the relevant attack damage.

- Opened September 29, 2026, at 21:38:55 UTC.
- Merged October 16, 2026, at 14:13:26 UTC, or **9:13:26 AM Central**.
- The screenshot's two-week label describes the submission age.
- PR head: 2aa705d314d3c95441d0cd3f5a9c0290870e0f28.
- Merge commit: c3083a3f3191f8a3cccde5fc7f5b7e0033f91fff.
- The PR contains six regression tests and three recorded in-game examples. Our equivalent repairs already existed locally.

Local record: [upstream PR evidence folder](../upstream_pr_2026-09-28/). This acceptance does not mean our entire fork has been merged upstream.

## Useful upstream updates for PocketDeckSim

### Changes worth evaluating, with current-deck relevance

| Change | Comparison with ours | Useful follow-up |
| --- | --- | --- |
| [PR 395](https://github.com/bcollazo/deckgym-core/pull/395), Trainer identity by effect text, merged October 9 | **First priority for the next pin.** Ours dispatches by manually listed printing IDs and has no B4b catalog. Upstream maps equivalent Trainer text to a canonical printing. | Import card data and dispatch together while preserving our Trainer legality and effect repairs. Audit our printing-specific handlers, such as Iris/Haxorus, too. |
| [PR 390](https://github.com/bcollazo/deckgym-core/pull/390), random multi-hit enumeration, merged October 7 | **Verified missing optimization, lower current priority.** Our official source still enumerates every ordered target sequence. Upstream enumerates hit-count distributions with multinomial probabilities. Sonnet found no affected card in the inspected lists. | Measure an affected workload before adapting it. Compare distributions and seeded replay behavior. This is not an established bottleneck in Dustin's current games. |
| [PR 384](https://github.com/bcollazo/deckgym-core/pull/384), stale first-turn ability choice | **Verified missing defensive safeguard.** Ours still panics on EndFirstTurnAttachEnergyToSelf in the ordinary ability handler. | Reproduce the stale-choice path before porting. No local gameplay crash or current-deck impact was demonstrated here. |
| [PR 385](https://github.com/bcollazo/deckgym-core/pull/385), optional on-play abilities outside the owner's turn | **Verified source gap, outside the inspected lists.** Our hand-to-bench hook lacks the upstream setup/owner-turn guard. Sonnet identifies Miraidon ex, Koraidon ex, Roaring Moon and Poltchageist as affected. | Test setup, ordinary benching, and opponent-turn placements, then port the guard at a suitable pin. |
| [PR 386](https://github.com/bcollazo/deckgym-core/pull/386), promotion before queued EndTurn | **Needs reproduction in ours.** Sonnet narrows the candidate to Kiawe plus Jolteon ex's Electromagnetic Wall, outside the inspected lists. Our Checkup phases differ. | Reproduce before choosing PR 386 or the alternative PR 388 approach. Insert the appropriate Promote choice; do not combine both fixes blindly. |

Source pointers in our engine:

- Random multi-hit enumeration: engine/src/actions/apply_attack_action.rs:6021; total_sequences = n.pow(times as u32) at approximately line 6032.
- Trainer ID dispatch: engine/src/move_generation/move_generation_trainer.rs:105 and engine/src/actions/apply_trainer_action.rs.
- Stale ability panic: engine/src/actions/apply_abilities_action.rs:354.
- On-play hook: engine/src/hooks/core.rs:323; caller at engine/src/actions/apply_action.rs:1317.
- Explicit queued EndTurn frames: engine/src/actions/apply_abilities_action.rs:690 and engine/src/actions/apply_trainer_action.rs:1753.

The multi-hit optimization preserves possible damage distributions and probabilities within floating-point tolerance. For example, four targets and twelve hits have 16,777,216 ordered sequences but only 455 hit-count distributions. This is an algorithmic work comparison, **not a measured PocketDeckSim speedup**. Different enumeration order can still change seeded trajectories. Upstream includes probability comparisons against brute force; our integration would still need its own relevant checks.

Upstream PR 395 reports 46 B4b Trainer printings becoming supported by reuse. Its database-wide test checks that canonical mappings retain the expected name and type, with Fossils handled separately. We should retain equivalent checks and our Fossil/Item-lock repairs. Importing only the new dispatch table would not by itself add the missing card catalog.

Sonnet's data comparison found 3,879 shared card IDs with identical fields through B4a. Upstream's September 29 commit 9044ff6 adds 438 entries: 429 B4b and nine Promo-B entries, of which 437 are reprints. The one new card is Mega Garchomp ex, P-B 099. Our separate Garchomp branch has the same card fields, so there is no new card contribution to offer upstream. Regenerate with our data generator instead of applying upstream's line-ending-sensitive generated-file patch. Check both old and new printings, supported-deck validation, Trainer effects, and printing-specific effects before release. Sonnet identifies lib/card_canon.py base_id as an interim way to rewrite lists to existing printings.

### Additional upstream items identified by Sonnet

These extend the initial review. Their local applicability is taken from Sonnet's committed comparison, not a fresh runtime reproduction here.

| Item | Use and limit |
| --- | --- |
| PR 401, Fossil portion | Remove duplicate Fossil-discard choices. Small, but no inspected list uses a Fossil. Keep it separate from that PR's MCTS work; it was open and unmerged at review time. |
| PR 344, Energy Zone validation | Reject Dragon/Colorless Energy Zones clearly. The inspected deck files already have legal Energy lines. Check compatibility with the strength harness and intentionally redacted observation templates. |
| Part of PR 368, shuffle attached cards | Shuffle attached Tools into the deck with Eldegoss/Dunsparce/Accelgor-style effects instead of discarding them. Preserve Professor Turo's separate behavior. No affected card in the inspected lists. |
| PR 374, granted second type | Include an Ability-granted second type in relevant opponent-type damage checks and the bot estimate. The identified cases involve Snover/Sealeo against Urshifu, outside the inspected lists. |
| Regression tests from PRs 343, 346, 347, 348 and 383 | Useful candidates after checking their expected behavior. Rewrite the Dragonair case to require a Dragon Active and include a negative Grass-Active case. Keep our Helmet implementation when taking PR 383 tests. |
| PR 382, replay recording and viewer | Optional way to inspect simulated play. Needs integration and an executable rebuild; per-option scores from PR 391 help only if our pilots emit them. |

Sonnet also identified hash-map ordering as a possible reason random-damage attacks are not reproducible from a seed across runs, covering ten cards and 27 printings outside the inspected lists. Treat that as a source finding to reproduce if working on PR 390, not as a newly measured failure of current deck experiments.

### Updates with different tradeoffs

| Change | What it actually does | Assessment |
| --- | --- | --- |
| [PR 392](https://github.com/bcollazo/deckgym-core/pull/392) | Caps large search forecasts at 20 sampled outcomes, using a repeatable state/action-derived seed. Played actions still use the full distribution. | A search approximation that can change bot choices and miss rare outcomes. It constructs the full forecast before sampling, so it primarily reduces later search work. Evaluate separately from PR 390. |
| [PR 394](https://github.com/bcollazo/deckgym-core/pull/394) | After 100 actions in a turn, free-play choices are restricted to attacks and EndTurn; pending choices still resolve. Stops two-Dusknoir Shadow Void loops. | A deliberate substitute for a timer that changes available choices after the cap. Do not present it as an exact Pocket rules repair. |
| [PR 393](https://github.com/bcollazo/deckgym-core/pull/393) | Dependency updates including pyo3 0.29 and a Python points-list compatibility fix. Ours still declares pyo3 0.22. | Maintenance work to review separately. It does not authorize rebuilding or replacing the pinned RL add-on. No local dependency vulnerability audit was performed. |
| [PR 391](https://github.com/bcollazo/deckgym-core/pull/391) | Records per-option player scores in replays and exposes them in the viewer. | Potentially useful for explaining decisions. Integration and overlap with our diagnostics were not fully assessed. |
| [PR 387](https://github.com/bcollazo/deckgym-core/pull/387) | Makes Stadium and attached Tool cards easier to inspect in the replay viewer. | A useful UI reference, lower priority than correctness and piloting. Our separate interfaces need their own comparison. |

## Fixes already covered and changes to avoid importing blindly

- **Heavy Helmet, including our own PR 383:** keep our current-cost and per-Helmet implementation. Upstream still checks printed Retreat Cost and returns a flat reduction. The older engine/UPSTREAM.md instruction to take upstream's version after PR 383 merges is stale. Taking that source would undo local commit 050cf51d; reuse suitable tests instead.
- **Sleep and Paralysis restrictions:** independently repaired in both projects. Upstream PR 379 contains e38b77d; our older copied status-fix branch is obsolete as a proposed contribution. The two implementations use different paralysis timing models, so a future merge still requires reconciliation.
- **Player code et:** upstream PR 400 repairs the parser, but our official source already handles exact named codes before parameterized prefixes. See engine/src/players/mod.rs:217 and engine/tests/player_code_parser_test.rs. Existing tests were inspected, not run.
- **Caterpie Quick Growth at setup:** upstream PR 389 addresses this. Our source independently schedules Quick Growth through the real end-turn path. See engine/src/actions/apply_action_helpers.rs:90 and engine/tests/rules_repair_timing.rs:343. The exact same setup regression test was not located.
- **HP-aura knockout leaving a stale promotion option:** the specific upstream 09e964f case already passes in the fork because knockout waves and the nested pass resolve before promotion choices are built. The October 1 F8 record does not establish that every possible stale Promote path is safe.
- **Lethal Knock Back change in 09e964f:** Dustin rejected importing this on September 30. Our ruling says the switch completes and the lethal target is knocked out on the Bench. Preserve engine/tests/rules_repair_retaliation_timing.rs:136 and the official Japanese ruling recorded in rules/06_sources.md:124.

**Important documentation correction:** engine/UPSTREAM.md still says the two 09e964f promotion fixes are missing. The later [rules repair record](../../../rules/09_engine_repairs_2026-09-22.md), lines 78-84, and RUN5.md:600 supersede that note. One specific case is already covered and the other was intentionally rejected. Do not start a duplicate port from the older note.

Sonnet's broader comparison adds these preservation points:

| Upstream behavior not to substitute for ours | Reason |
| --- | --- |
| Raticate ex Thieving Incisors | Preserve the local random-Energy selection instead of upstream's shortcut. |
| Team Rocket's Researcher | Preserve exact coin outcomes and Will/Luxury Coin handling instead of the five-head cap. |
| Happiny's Chubby Cheer | Preserve our next-turn timing. |
| Growl/Bonsly/Luxray and Guarded Grill/Securely Sheltered damage order | Preserve the local FAQ-based damage-order repairs. |
| End-of-turn knockouts deferred through Checkup | Conflicts with our Checkup/promotion and Quick Growth timing. A relevant listed interaction involves Caterpie in the Sceptile panel. |
| Victory Star, simultaneous third-point/empty-board ties, and self-discard choices | These overlap our larger staged-choice, rules4 T2, and player-choice repairs. |
| Kabutops Leech Life | Sonnet found text support for our overkill handling, but flagged an untested possible over-heal when a defensive coin reduces damage. Do not change the behavior without resolving that separate case. |

Team Rocket's Goo-zooka with retreat discounts exceeding the added cost remains unsettled. Sonnet found no evidence settling the ordering; leave it unchanged. The proposed Rocky Helmet/Cursed Jewel interaction in open PR 367 also remains a separate rules decision. Its broader implementation could conflict with our return-damage rules, so it is not a ready-made repair to import.

## Contributions we can offer upstream

These differences were checked against bcollazo main c3083a3. Our repairs are in the official engine source; existing local regression tests were not rerun.

### Broader candidate inventory from Sonnet

The first handoff covered too few candidates and overstated Heavy Helmet's priority as a small patch. Sonnet identifies about 30 candidates, with the first 15 classified as small and clear. The table below preserves the broader inventory and its main limitations. The detailed report supplies per-item evidence, estimated patch sizes, and reviewer judgments. These are candidates to reproduce and package, not approved postings or guaranteed acceptances.

| # | Candidate | Evidence or scope to retain |
| --- | --- | --- |
| 1 | Stack multiple Ariados abilities | Small missing-loop behavior; relevant when multiple Ariados are present. |
| 2 | Rare Candy respects Primeval Law and Malamar's Jammer | Check both restrictions and offered targets, not only Aerodactyl ex. |
| 3 | Mythical Slab allows eligible Psychic Pokemon, not only Basics | Narrow card-text condition. |
| 4 | Pichu respects the Benched Basic restriction | Narrow target filter. |
| 5 | Discard-all Energy reaches the Energy discard ledger | Small deterministic fix; relevant to the Hydreigon panel. |
| 6 | Poncho protects against the opponent's relevant effects | Preserve the ownership restriction; can share coverage with row 30. |
| 7 | Only one Stadium may be played per turn | Card-rule restriction and existing local test. |
| 8 | Eevee's first-turn evolution exception applies to itself | Narrow exception scope. |
| 9 | Zero damage does not consume Mimikyu's Disguise | Text and owner recollection; do not present as newly video-verified. |
| 10 | Wallace's maximum-HP threshold includes bonuses | Official FAQ example: a 50-HP Staryu with Giant Cape is ineligible. |
| 11 | Recognize hit-back abilities by effect text, including reprints | Iron Jugulis/Dragalge printings and suppression by Muk or earlier Budew. Same-attack Budew timing is a separate, larger problem. |
| 12 | Legendary Pulse before Hiking Trail | Ordering supported by one recorded local example, not card text alone. |
| 13 | Electrical Cord retains Energy that could not move | Remaining Energy must reach normal knockout discard handling. |
| 14 | Suppress futile self-attach ability suggestions under an Energy Zone lock | Bot behavior improvement, not proof that using the ability is forbidden. |
| 15 | Will does not force Victory Star's fresh reroll | Recorded local evidence; distinct from the larger confusion/block-coin pipeline. |
| 16 | Heavy Helmet uses current Retreat Cost; defender-cost attacks use the defender's side | Natural PR 383 follow-up, but approximately 90-140 lines across three files in Sonnet's estimate. Not the smallest patch. |
| 17 | Healing target filters offer damaged Pokemon only | Based on Dustin's rule; printed text alone does not settle it. |
| 18 | Random Energy selection is actually random | Piers, Unruly Claw, the Psychic Supporter and Thieving Incisors. Additional branching is a maintainer tradeoff. |
| 19 | Attacker promotes first after a double knockout | Recorded local observation, not card-text proof. |
| 20 | Ending player's Lum Berry/Bad Dreams sequence resolves first | Official FAQ worked example. |
| 21 | Clemont's Backpack bonus reaches the opponent's Bench | Card text plus recorded cases; requires a turn-effect field. |
| 22 | Fossils count as Items in locks and other Item-card checks | Attach the October 2 Sail Fossil screenshot; several code sites are involved. |
| 23 | Deal five opening cards, then replace one only if no Basic was drawn | Community studies and Dustin's 50-hand test; affects every game and deserves stronger review. |
| 24 | Attack-generated return damage applies Weakness | Recorded Cursed Jewel/Spike Armor behavior; separate from open PR 367's Helmet interaction. |
| 25 | Flower Shield/Soothing Wind recover status when qualifying Energy arrives | Continuous behavior after the status was first applied; multiple code paths. |
| 26 | Defensive damage coins also run for attacks resolved through queued choices | Extends PR 335 beyond its original path; broad attack coverage and substantial tests required. |
| 27 | Growl-type cuts stay on the affected Pokemon and apply before Weakness | Card text, FAQ ordering and recorded evidence. |
| 28 | Guarded Grill/Securely Sheltered heads reduction applies after Weakness | FAQ damage order; larger than the initial PR 335 implementation. |
| 29 | Search-to-hand effects stop at ten cards | Clemont/Serena/Cabbie/Juliana; evidence by analogy to the hand limit. |
| 30 | Ice Face/Coordinated Unit/Unown Guard protect from opposing attacks only | Ownership restriction; possible bundle with row 6. |

Lower-readiness topics remain separate: Glimmora/Dusknoir coins on non-attack knockouts, Victory Star with confusion or block coins, hit-back ordering after attack effects, new retreat/discard choices, hidden/empty-deck play rules, the T2 tie, and Checkup/promotion architecture. A rare stale-switch frame is still un-reproduced. Do not package these as small, settled fixes. Quick-Grow Extract and Wallace target choice overlap the maintainer's closed-unmerged PR 402 and existing branch, so review that work before proposing a competing patch.

### Detail for candidates from the initial review

### Heavy Helmet and current Retreat Cost

Upstream still checks the printed retreat_cost.len() in src/hooks/core.rs:718. Our implementation checks the current board cost, including whether the holder is Active or Benched.

Recorded local example: with Peculiar Plaza reducing the holder's Retreat Cost below three, Heavy Helmet did not reduce a 40-damage attack. The local repair also handles effects that raise a printed cost into the qualifying range.

- Local commit: 050cf51.
- Implementation: engine/src/hooks/core.rs:706, heavy_helmet_reduction and get_board_retreat_cost_at.
- Test: engine/tests/rules_repair_damage_opening.rs:187.
- Evidence: [rules repair record](../../../rules/09_engine_repairs_2026-09-22.md), lines 224-234; recording heavyhelmet_test.MP4.
- **Assessment:** a natural follow-up to PR 383 with recorded evidence, but Sonnet estimates a larger port than several candidates above. Separate current-cost ownership and defender-cost attack coverage carefully.

### Discarded Energy reaching the discard pile

Upstream damage_and_discard_all_energy clears attached Energy without adding it to the Energy discard ledger. Energy-recovery effects can consequently see too little discarded Energy. Our handler calls discard_from_active.

- Upstream: src/actions/apply_attack_action.rs:4275.
- Local commit: a30b5f8.
- Implementation: engine/src/actions/apply_attack_action.rs:3816.
- Test: engine/tests/rules_repair_damage_opening.rs:166.
- **Assessment:** a small deterministic correction with an existing local regression test. Verify both the removed attachments and the resulting discard ledger on an upstream-based branch.

### Rare Candy respecting Aerodactyl ex

Upstream can_play_rare_candy checks evolution pairs without the position restriction that blocks evolution of the Active under Aerodactyl ex's Primeval Law. Our code uses can_evolve_at_position and also repairs the offered target list.

- Upstream: src/move_generation/move_generation_trainer.rs:614.
- Local commit: 14745ce.
- Implementation: engine/src/move_generation/move_generation_trainer.rs:669.
- Test: engine/src/move_generation/mod.rs:456.
- Evidence: [rules repair record](../../../rules/09_engine_repairs_2026-09-22.md), lines 215-223, records Dustin's September 25 in-game confirmation.
- **Assessment:** relevant to the Rare Candy decks we evaluate; suitable for a focused upstream regression and patch.

### Quick Grow Extract and Wallace

Our implementation lets the player choose the visible Pokémon before randomly selecting an eligible evolution from the deck. Upstream main still randomizes target/evolution pairs together.

- Local implementation: engine/src/actions/apply_trainer_action.rs:2413-2490.
- Local tests: engine/tests/rules_repair_trainers.rs:235 and :276.
- Existing local status: rules/09_engine_repairs_2026-09-22.md:38-39.
- Upstream implementation: src/actions/apply_trainer_action.rs:2141-2197.
- [Issue 399](https://github.com/bcollazo/deckgym-core/issues/399) and [PR 402](https://github.com/bcollazo/deckgym-core/pull/402) were closed after a rules disagreement. **PR 402 is not merged**, despite having a merge_commit_sha field in GitHub's metadata.
- The reporter posted [Quick-Grow footage](https://github.com/bcollazo/deckgym-core/issues/399#issuecomment-6208894143) and [Wallace footage](https://github.com/bcollazo/deckgym-core/issues/399#issuecomment-6209141941) on October 16 and requested reconsideration. These videos were not viewed in this review.

**Assessment:** review the new footage and existing PR 402 before preparing a duplicate implementation. Our local fix is useful comparison evidence.

### Additional leads and unfinished local work

- **Legendary Pulse before Hiking Trail:** repaired locally in 5b75bf9, with recorded evidence and engine/tests/pokemon/additional_ability_logic_test.rs:223. Sonnet's wider comparison includes this candidate; the implementation and evidence pointers are retained here for a focused upstream reproduction and patch.
- **Multiple Ariados stacking:** repaired locally in 5155ff7a, with two-Ariados tests and a relevant recording described in rules/09. Sonnet's wider comparison includes this candidate; reproduce on the chosen upstream revision and refresh overlapping work before packaging it.
- **Attack return damage and the attacker's protections:** still unfinished locally. The October 12 release added Weakness to specified attack-generated return damage, but not all interactions with the attacker's Heavy Helmet and other protections. See rules/09:86. Do not present this as an existing completed fix ready to send.
- **Possible upstream bot evaluation bug:** src/players/value_functions.rs:303 chooses a variable named most_expensive_attack_cost using .max() on Vec<EnergyType>, which is lexicographic rather than by energy count. A concrete card and regression are needed before calling it a confirmed gameplay defect. [Pinned source](https://github.com/bcollazo/deckgym-core/blob/c3083a3f3191f8a3cccde5fc7f5b7e0033f91fff/src/players/value_functions.rs#L303).
- **Continuous performance benchmarks:** [issue 183](https://github.com/bcollazo/deckgym-core/issues/183) remains a possible infrastructure contribution. It is less directly useful than the small correctness fixes above.

### Existing upstream work to avoid duplicating

[PR 401](https://github.com/bcollazo/deckgym-core/pull/401) was rechecked as **open and unmerged**. It covers duplicate Fossil discard choices in issue 397 and the terminal-game move generation problem behind the no-Active/MCTS crash in issue 398. It fixes the terminal search-node path rather than broadly suppressing ability checks.

Other open work found during the first search included MCTS repair (275), end-turn queue refactoring (388), Cursola (337), Lilligant's HP aura (304), Electrode (380), and Magmar/Slowpoke (381). Refresh their status before selecting overlapping work. Old issue 54's wrong-player Energy calculation appeared stale on current source; it is not a verified new task.

## What the Cliff fork actually provides

Repository: [IncredibleAloeVera/deckgym-core](https://github.com/IncredibleAloeVera/deckgym-core). Reference revision: e69eea302a4c60802a3a2ba4ad4a219d76b9cc81.

The [README][aloe-readme], [architecture][aloe-architecture], and source support the following inventory:

- A playable saved RL model, Cliff, with published weights and model metadata.
- Observations, legal-action masks, reveal-memory tracking, and egocentric views.
- A Burn-based neural model, terminal-result learning, configurable training, checkpoints, curriculum machinery, and metrics.
- A growing opponent pool containing scripted opponents and frozen model checkpoints. The pool can preserve strong and historical opponents rather than only recent copies.
- Deck samplers using tournament and tutorial collections.
- Model/schema compatibility checks that reject incompatible observation/action layouts.
- An **unbuilt** deckbuilder described as an energy-based scoring model plus GFlowNet-style sampling. The uniform legal-random-deck quota is also unbuilt.

Some optional systems, including the growing pool and curriculum stages, are off or empty in the default configuration. Availability in the code does not prove which settings were used to train Cliff. Parts of the design rationale live in an unpublished NOTES.md.

### Published model and strength evidence

Cliff's repository includes a 5,047,489-byte weights file. Its [metadata][aloe-meta] reports a rating of approximately 1767.147, deviation 5, and 576,316 games, with an August 13 date. This is the fork's internal Glicko-2 scale anchored to EvolutionRusher, not a human ladder rating.

The originating training run is explicitly unpublished. No originating run logs or held-out result tables were found in the inspected repository tree. Thus, the author describing Cliff as intermediate is not evidence that it matches intermediate humans, handles Dustin's decks, or beats km3.

The author's [performance report][aloe-performance] measured about 1,053 decisions/second and 15 games/second for Cliff using CUDA and 64 simultaneous environments on the stated example-deck workload. Those are throughput measurements, not strength measurements, and were not reproduced on Dustin's hardware.

Loading and evaluating the released model is distinct from reproducing its training. The architecture also records that model-block initialization cannot be reconstructed from init_seed because Burn's global RNG is not seeded by that training path. Together with the unpublished run, this limits claims of exact training reproducibility.

### Card and rules compatibility

- **Current-deck blocker:** Sonnet's pool check marks four Kingambit-deck effects incomplete: Kingambit B3a 043 attack, Alolan Muk B2 097 ability, Glimmora B3a 045 ability, and Regigigas B3 134 ability. The cards exist in the frozen database; their presence does not mean the engine implements the plan. See [pool-check output][sonnet-pool].
- **Inspected deck coverage:** only brew 10 among the eight ladder-sheet decks passes Sonnet's card/status check. Four panel lists pass: Altaria, Blaziken, Lucario and Sceptile. Hydreigon, Suicune, Vespiquen and Weezing require later cards. Passing that check is necessary compatibility evidence, not proof of accurate play or model strength.
- The frozen card enum has **3,520 printings and no B4 entries**. The incomplete-card file has **364 entries**: 240 attacks, 71 abilities, 46 Trainers, and seven Tools. This is a source inventory, not fresh verification of every implemented card.
- B4 and later cards, including B4a cards in Dustin's decks, are absent. Adding them requires engine logic, generated IDs, static/text features, legal-action coverage, and model compatibility work. The published weights are not a drop-in pilot for our newer decks.
- The fork intentionally uses a **99-turn horizon**, enforced by engine code and a test. Our rules specify a 30-turn versus limit. A same-card comparison on different turn limits would not isolate pilot quality.
- Both current and next Energy Zone values for both players are exposed as public. Actual live-game visibility of the opponent's next Energy was not independently checked here. Treat this as an unresolved rules assumption, not a confirmed leak.
- Own deck tokens follow deck iteration order, but the encoder intentionally treats them as a set without positional encoding. That observation alone does not establish a deck-order leak.

The published deck builder filters out incomplete cards, which supports the inference that the published dataset pipeline excludes the Kingambit plan. Because Cliff's originating training run is unpublished, this is not a directly audited history of every deck the model encountered. The practical recommendation is still **no Cliff trial for the current project**. The proposed invariance reproduction below is conditional future work if someone revisits the model, not a new task to run now.

### Hardware and reproducibility qualification

The README documents CPU NdArray inference, reports about 90 decisions per second on its benchmark, and lists portable WGPU as building/running but unmeasured at the current model size. NVIDIA is required for the documented CUDA path, not for every possible execution or training path. No local hardware benchmark or retraining cost estimate was validated here. The released model can be evaluated; exact reproduction of its originating training run remains unsupported by the published materials. Do not restate that limitation as proof that no new training or extension is possible.

Sources: [card IDs][aloe-card-ids], [incomplete report][aloe-incomplete], [model compatibility][aloe-baked], [turn limit][aloe-turn-limit], and [Energy observation fields][aloe-energy].

## Cliff hidden information concern

**A direct source-level information path was found; no runtime reproduction was performed.** This does not show that Cliff learned to exploit it, or quantify its effect on results.

1. src/rl/observation.rs:596 creates ProjectionScratch from the full engine state.
2. src/rl/damage.rs:103-108 constructs the scratch state by cloning the original. The projection changes the acting player and board position; it does not remove hidden cards.
3. src/rl/damage.rs:262 calls forecast_attack_outcomes on the projected state.
4. src/actions/apply_attack_action.rs:3794-3806 computes Cyberjack's damage by counting actual Trainer cards in the opponent's hidden deck.
5. src/rl/observation.rs:1044 onward turns these estimates into threat and knockout features consumed by the model before it chooses an attack.

The Cyberjack effect is registered in src/actions/effect_mechanic_map.rs:1826-1830 and dispatched in apply_attack_action.rs:700-705. Its inclusion in the frozen database/static tables was not independently verified. That and runtime reachability should be checked first.

Primary source chain: [observation construction][aloe-observation], [state projection and forecasting][aloe-damage], [Cyberjack calculation][aloe-cyberjack], [model threat features][aloe-threat].

### Small reproduction to perform before relying on Cliff

Construct two legal positions with identical information available to the acting player: same visible board, hand, known own deck composition, opponent hand/deck sizes, public history, and revealed cards. Change only unrevealed opponent cards so the hidden Trainer count differs. Give the acting Pokémon the relevant implemented attack and sufficient Energy.

Compare the **entire** observation, action mask, derived threat/knockout fields, and deterministic model output under the same inference conditions. They should remain identical when only inaccessible information changes. A changed Cyberjack threat feature would reproduce this path without needing a long training run.

The inspected observation no-leak test checks which card tokens appear. The inspected belief test checks consistency of remembered cards with the real state. Those checks do not establish invariance of every derived input. This is not a claim that no other invariance tests exist anywhere in the fork.

Legal-action round-trip tests are useful, but agreement with the engine's move generator does not prove the underlying Pocket rules are correct. Reuse the tests behind our PlayerObservation boundary, including derived values and action masks.

Sources: [observation tests][aloe-observation-tests], [action-mask tests][aloe-mask-tests], and [belief tests][aloe-belief-tests].

## Tournament data findings

The data pipeline is a potentially useful component even if we never adopt Cliff's model.

- The builder uses Limitless POCKET tournaments before a hardcoded July 30, 2026, 01:00 UTC cutoff, consistent with the pre-B4 pool.
- It deduplicates lists and filters out wrong deck sizes, excessive copies, unavailable cards, and cards marked unimplemented.
- Many source lists lack declared Energy. The author reports that only about one fifth declare it; the builder otherwise infers Energy with a classifier, or a heuristic when dependencies are absent. Preserve that provenance rather than treating inferred Energy as observed tournament data.
- Compiled identities include both cards and Energy. The training population is therefore affected by filtering and Energy inference.
- Current repository tree inspection found **9,579 meta archetype files**. These are label-grouped files that can each hold multiple decks, not 9,579 individual decks or independently established strategic archetypes.
- All five tutorial files were counted: **306 deck blocks**, comprising 59 advanced, 40 beginner, 108 expert, 36 intermediate, and 63 rental.
- The architecture reports **120,444 meta decks, 8,849 archetypes, and 262 tutorial decks**. The latter two counts differ from the current tree/files. The 120,444 meta total was not independently recounted.

Use the import and validation approach for a refreshed current-card dataset. Do not substitute the old collection for the current metagame or cite its deck count as proof of strategic coverage.

Sources: [deck collection][aloe-decks], [meta builder][aloe-meta-builder], [Energy/filtering logic][aloe-energy-builder], and [database compiler][aloe-db-builder].

## Comparison with our existing RL work

| Capability | Our current state | What the Cliff fork may add |
| --- | --- | --- |
| Production pilot | km3 is programmed search and evaluation, not a trained network. ky3 work is also search/piloting work. | A possible future comparison policy after missing mechanics and model compatibility are resolved. Not recommended for a trial now. |
| RL training | NumPy action-scoring networks trained on terminal win/loss/draw, with separate networks for particular piloted decks. | A shared model and broader deck-conditioned training design. Better transfer remains unproven. |
| Past-checkpoint opponents | Already present. The Hydreigon run used a 20% past-opponent share. | More developed opponent selection, archive, rating, and curriculum machinery. |
| Hidden information | PlayerObservation redacts unknown opponent card identities and supplies own remaining deck composition without its actual shuffled order. | Reveal-memory and mask tests worth adapting, while addressing the source-level leak above. |
| Deck discovery | No validated general deck-ranking or automatic deck-discovery system. | The deckbuilder is also still a design, so this is not a completed solution to import. |

Local source references:

- Current pilot and engine: RUN5.md:421-424; engine/src/players/mod.rs:683-710.
- RL model: rl/model.py:1-5.
- Per-deck learning and checkpoint opponents: rl/train_v5.py:18-26 and :407-420; rl/runs/diag-hydreigon-lucario/settings.json:32.
- Information boundary: engine/src/observation.rs:22-29, :54-65, and :136-166.
- RL binding: rl/pdl_rl_env/src/lib.rs:1-8 and :324-362.
- The [rules4 add-on recheck](../astra-review/rules4-addon-recheck-2026-09-22/README.md) reports 4,665 hidden-card/order invariance probes for its tested pair. That is bounded historical validation, not proof for every card or later engine change.

### What our RL results established

The [Hydreigon readout](../hydreigon_network_readout/READING.md) reports a 40.8-percentage-point gain over old k3 in its registered Lucario matchup and learned Hyper Ray chip play that exposed a baseline weakness. [Altaria's readout](../altaria_network_readout/readout.txt) is another narrow diagnostic result.

Earlier Blaziken/Lucario networks lost 12.3 and 13.0 percentage points relative to k3 against held-out Ninetales, recorded in RUN5.md:143-147. Strong results in a familiar matchup do not establish general piloting or reliable deck comparisons.

The current plan at RUN5.md:644-645 excludes terminal-result policy networks as the production pilot while permitting narrow diagnostic networks. This handoff does not change that plan. Broader training is a research direction to assess against actual deck-play needs.

## Suggested order of follow-up

1. **Prepare B4b compatibility for the next tested engine pin.** Bring the data, Trainer mapping and our printing-specific handlers together. Confirm old-printing behavior, new-printing equivalence and the new Garchomp entry. Preserve all later local rules repairs.
2. **Keep current Kingambit piloting work ahead of unrelated engine cleanup.** The broader source review found no missing upstream gameplay repair that changes the inspected matchups. Do not divert current experiments merely because a patch exists upstream.
3. **Select small contribution candidates from the wider inventory.** Ariados stacking, narrow Trainer filters, the discarded-Energy ledger and Rare Candy restrictions are examples. Reproduce on an upstream-based branch and check overlapping work. Heavy Helmet remains useful but is not the smallest port. Posting under Dustin's account still requires authorization.
4. **Batch relevant defensive fixes with a future pin.** Reproduce the ability/promotion paths first. Consider Fossil duplication, Energy validation and other bounded fixes according to actual card use. An arbitrary action cap changes behavior and needs its own decision.
5. **Measure multi-hit work when an affected card or workload makes it relevant.** Check outcome probabilities, ordering and replay effects before and after. Do not claim a speedup for current decks without measuring one.
6. **Defer Cliff execution and retraining.** Its present card/effect coverage does not serve the Kingambit question. If later reconsidered, first establish card compatibility, matched rules and hidden-information invariance; then define a bounded comparison.
7. **Retain the dataset and test ideas for later reuse.** A refreshed tournament field, reveal memory, mask tests and compatibility checks may be useful without adopting the model. Tournament prevalence still does not establish Dustin's ladder opponent distribution.

Do not import the search sampling cap or 100-action limit as if they preserve existing behavior. Do not replace our repaired engine wholesale with either fork. A tested candidate still follows the existing engine-switch process before becoming the official executable.

## Keeping up with upstream

Sonnet's comparison branch adds tools/upstream_watch.py, tools/test_upstream_watch.py, and rl/upstream_watch/LAST_CHECKED.txt. The starting upstream revision is c3083a3f. The report records nine passing script tests; this reconciliation did not rerun them. Those files are available on the review branch, not automatically installed or scheduled by this handoff.

From a checkout containing that tool, `python3 tools/upstream_watch.py` fetches and summarizes new upstream changes. `--mark` also records the current tip, so use it after reviewing the changes. The default upstream clone location is ~/upstream_watch/deckgym-core. The hints LOOK/maybe/skip are triage aids based on changed paths, titles and card-name matches, not verified impact classifications. Short names can be skipped; a rules fix may affect a deck without mentioning its cards.

Use the watcher to identify new card data, relevant rules repairs and crash guards. Compare each candidate with our current implementation before importing it. No recurring task was created, no existing checkpoint was advanced, and no review branch was merged during this reconciliation.

## Reference notes

Local paths and line numbers refer to the reviewed checkout and may move. Remote source links below pin the Aloe revision inspected.

[sonnet-upstream]: https://github.com/dacz8976-creator/PocketDeckSim/blob/c0fcff86e398eaf3592af5ebdb104e7841ae0850/rl/results/upstream_compare_2026-10-16/README.md
[sonnet-detail-a]: https://github.com/dacz8976-creator/PocketDeckSim/blob/c0fcff86e398eaf3592af5ebdb104e7841ae0850/rl/results/upstream_compare_2026-10-16/DETAIL_A.md
[sonnet-detail-b]: https://github.com/dacz8976-creator/PocketDeckSim/blob/c0fcff86e398eaf3592af5ebdb104e7841ae0850/rl/results/upstream_compare_2026-10-16/DETAIL_B.md
[sonnet-cliff]: https://github.com/dacz8976-creator/PocketDeckSim/blob/6b83f1626e4de11232dac3bad7a7af1ed7ed6de9/rl/results/cliff_fork_look_2026-10-16/README.md
[sonnet-pool]: https://github.com/dacz8976-creator/PocketDeckSim/blob/6b83f1626e4de11232dac3bad7a7af1ed7ed6de9/rl/results/cliff_fork_look_2026-10-16/pool_check_output.txt

[aloe-readme]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/README.md
[aloe-architecture]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/RL_ARCHITECTURE.md
[aloe-meta]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/models/Cliff/meta.toml
[aloe-performance]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/PERFORMANCE.md
[aloe-card-ids]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/card_ids.rs
[aloe-incomplete]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/auxiliaries/card_status.txt
[aloe-baked]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/rl/train/baked.rs
[aloe-turn-limit]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/state/mod.rs#L562
[aloe-energy]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/rl/observation.rs#L750
[aloe-observation]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/rl/observation.rs#L593
[aloe-damage]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/rl/damage.rs#L103
[aloe-cyberjack]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/actions/apply_attack_action.rs#L3793
[aloe-threat]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/src/rl/observation.rs#L1044
[aloe-observation-tests]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/tests/rl_observation_test.rs#L62
[aloe-mask-tests]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/tests/rl_action_mask_test.rs#L43
[aloe-belief-tests]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/tests/belief_test.rs#L119
[aloe-decks]: https://github.com/IncredibleAloeVera/deckgym-core/tree/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/decks
[aloe-meta-builder]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/auxiliaries/build_meta_decks.py
[aloe-energy-builder]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/auxiliaries/deck_energy.py#L410
[aloe-db-builder]: https://github.com/IncredibleAloeVera/deckgym-core/blob/e69eea302a4c60802a3a2ba4ad4a219d76b9cc81/auxiliaries/build_deck_dbs.py


Decision this informs: whether the cloud's later coin round, card-text job and follow-up (`claude/coin-prevention-round2`, tip d2d9499, engine at 20e2651) go to the laptop's switch review (the Fable coordinator, Oct 2). Read by the Sonnet session "Opus agents progress" (Claude Sonnet 5.5), independent of the cloud's author, on a local branch off main 7c1b62f8. Seeds: none; nothing was played, and **I did not build or run the tests** (see "Not done"). Rule applied: Dustin's, "plain card text is the rule unless contradicting evidence".

# Second read of the coin-prevention round 2 package (Oct 2)

## Verdict: ready for the laptop's switch review

No change is needed before it. I found no defect in the engine diff: each fix does what the plain card text says, the gates are as tight as the text allows, the tests fail on the parent engine and pass on the fix according to the cloud's logs, and the affected-deck inventory holds against current main. There are **eight notes (below); none blocks the review, and three of them are things the switch itself must prepare** (note 1 and 2: counters and a probe that see the new paths; note 3: the Fossil premise). One check is still mine to do: re-running the suite and the tests-first commits (held for the laptop's go).

## What I read

- The branch's engine diff against main 7c1b62f8 (the pinned engine, main-8626a35; the branch contains main): `apply_attack_action.rs` (+346), `apply_action.rs` (+300), `attack_outcome.rs` (+168), `hooks/core.rs`, `hooks/retreat.rs`, `state/mod.rs`, `trainer_coin_plan.rs`, `move_generation_trainer.rs`, `card_validation.rs`, in full, with the surrounding functions at the branch tip (Will's existing paths in `finish_forecast`, `Outcomes::force_first_heads`, the Wild Swing and Chase Order choices); the whole tests diff (1,287 lines); the cloud's README and `TEXT_AUDIT.md`; the before/after logs and the three suite logs by their result lines.
- The card texts from `lib/deckgym-database.json` on main for every card the package turns on, and a scan of the whole database for each text (`second_read_dbscan.py`), to check the audit's card lists are complete.
- Engine at the tip vs 20e2651: **identical** (the later merge of main changed no engine or test line), so the suites at 20e2651 apply to d2d9499.

## The seven sites of the later coin round (Oct 1)

Plain text of the defenders (all four): "If any damage is done to this Pokémon by attacks, flip a coin. If heads, prevent that damage" (Carefree Steps B2 124/204, Celestial Blessing A4 080), "... takes -100 / -80 damage from that attack" (Guarded Grill A2 114, Securely Sheltered B3b 050). The attack's text for each site, and what the diff does:

| site (printed text) | what the gate does | my reading |
|---|---|---|
| Wild Swing A4 045/215 ("discard any number of your Benched [W] Pokémon... 40 more damage for each") | `discard_then_damage_choice` (`apply_attack_action.rs:390`) now finds the Active's printed Wild Swing as well as Chase Order (`printed_attack`, :429); the total damage is one queued choice (the outcome carries none: `discard_own_benched_type_for_damage`, :6537), so one flip | follows the text; no double flip |
| Wellspring Dance B2 048 (heads: 40 to 1 Benched) | `coin_flip_also_choice_bench_damage` (:5845) gates each bundled Active+Bench choice | follows the text; the tails branch's Active damage already flipped |
| Tornado Shot B3 051 | `self_discard_energy_and_choice_bench_damage` (:3982), bundled | follows the text |
| Double Splash B1a 019, Triple Bombardment B1a 020/078/084 | `conditional_bench_damage_attack` (:6168), each finished choice gated | follows the text |
| Mischievous Ring B4 077 ("Before doing damage, shuffle all Tools...") | `shuffle_opponent_tools_into_deck_before_damage` (:8548) reads the board after the shuffle, inside the effect | follows the text, and the order ("before doing damage") |
| Litter A4a 018 | `discard_tools_then_damage_choice` (:403) in `forecast_discard_own_cards_for_attack_damage` (`apply_action.rs:1835`) | follows the text |
| Mega Kangaskhan ex B2 127/189/202, B4 231 ("used twice in a row. The second attack does 40") | `mega_kangaskhan_ex_double_punching_family` (:2238) queues the 40 as the attack's own damage when any of the opponent's Pokémon has a coin Ability; `state/mod.rs`'s pending-hit check (new arm) keeps the promotion above the waiting punch | the second attack is "an attack", so the coin flips for it: follows the text |

**Gate.** `coin_gated_choice` (:365) rewrites only a choice built as `ApplyDamage` from the attacker's Active whose targets are all the opponent's and one of which has a coin Ability (`any_coin_target`, :351); anything else comes back as it was. Off the gate nothing changes: the control test `the_later_rounds_sites_into_pokemon_without_a_coin_ability_are_unchanged` runs all seven sites into Mega Latios ex for 20 seeds each and asserts every queued choice is still a plain `ApplyDamage`. One looser gate, noted not blamed: the Kangaskhan site gates on any coin-Ability Pokémon in play (the punch lands on whichever Pokémon is Active then), where the others gate on the target.

**The fifth file** (`state/mod.rs`, new arm 1428-1430): `(actor + 1) % 2 == player_with_empty_active && any target is the opponent's slot 0`, for an `ApplyQueuedAttackDamage` in the frame of the attacker. The orientation is right (the targets' flag is relative to the frame's actor), and the test `carefree_steps_flips_for_the_second_punch_after_a_knock_out` asserts the second punch waits for the promotion. As the cloud says, the arm also sees any other queued attack damage aimed at the empty Active; I found no path where that changes an order (not an exhaustive audit, as theirs).

## The card-text job (Oct 2)

| item | plain card text | the engine now | my reading |
|---|---|---|---|
| 1. Will with a Confused attacker | Will (A4 156): "The next time you flip any number of coins for the effect of an attack, Ability, or Trainer card after using this card on this turn, the first coin flip will definitely be heads." The Confusion coin is the Special Condition's check, not an effect of the attack | Will waits through a Confusion tails and goes to the attack's first coin after a heads (`force_first_heads_using_will`, `attack_outcome.rs:627`, before the Confusion gate in `apply_attack_common_modifiers`, :175); Victory Star is still offered on the attack's coins | follows the text, and the game (Recording_QA 210403 T14). The exact-forecast test pins it: tails 1/2 with Will still pending; heads 1/2 spread 1/4, 1/2, 1/4 over 1, 2, 3 Energy; Will used |
| 2. Victory Star with a block coin (Smokescreen and seven other attackers) | Victory Star: "after you flip any coins for an attack of 1 of your [R] Pokémon". The block coin is flipped "if the Defending Pokémon tries to use an attack, your opponent flips a coin", for the effect of the *opponent's* attack | block coin first, never offered; on its heads the attack's own coins are offered (`victory_star_waits_for_gate_heads`, :110; `gate_heads_probability`, :137) | the plain reading, and the audit says what changes if Dustin reads it otherwise (only the last sub-point; shot row `victory-star-block-coin`). Acceptable by his rule |
| 3. Will with a block coin | Will names coins "for the effect of an attack"; the block coin is the attacking player's, for the effect of the opponent's attack | Will makes the block coin heads (`will_goes_to_the_block_coin`, :125; `block_coin_heads_by_will`, `attack_outcome.rs:678`); the attack's own coins stay fair | follows the text; exact-forecast test |
| 4. The coin Abilities on the attacker's own Pokémon | "If any damage is done to this Pokémon by attacks" (no "your opponent's") | own-side split in `apply_defender_damage_prevention_if_needed` (:255); the heads cut in `modify_damage` for either side (`hooks/core.rs`); and `forecast_apply_damage` (`apply_action.rs:782`) flips for any target of an attack's queued `ApplyDamage` | follows the text. Verified that every literal `is_from_active_attack: true` in the engine is built in `apply_attack_action.rs`, so the new flip reaches only attack damage; Checkup, Rocky Helmet and Ability damage stay unflipped (the existing tests for Checkup and Abilities pass) |
| 5. A copied discard attack (Ditto Copy Anything on Chase Order; either Ditto on Wild Swing) | the copy is "this attack" | the discard's damage is a plain queued `ApplyDamage` that `forecast_apply_damage` now flips | follows the text |
| 6. Trap Territory counted once per Ariados | "Your opponent's Active Pokémon's Retreat Cost is 1 more." on each | `hooks/retreat.rs` adds each Ariados's amount | follows the text and the recording (213034: two Ariados, Grass Knot 160 = 40 + 30 x 4); the two new tests (retreat legality at 0, 1, 2; Grass Knot 100, 130, 160) pin it. It also changes Heavy Helmet and every per-Retreat-Cost attack, as the README says |

## The follow-up (Oct 2)

| item | plain card text | the engine now | my reading |
|---|---|---|---|
| Victini's caveat (`card_validation.rs`) | n/a | says what is implemented (gate coins first, never offered; Will to a block coin else the first coin; a reroll is a fresh batch) and what stays open | accurate against the code I read; the test checks only that it names the cases and no longer says "legacy resolution" |
| Luxury Coin on the opponent's Stadium | Luxury Coin: "when you flip any coins for an effect of your Trainer cards" | `luxury_coin_covers` (`trainer_coin_plan.rs`): a Stadium whose recorded owner is the opponent is not covered; an unrecorded owner keeps the offer | the Stadium is its owner's Trainer card, so this follows the text; checked in both entry points |
| A Fossil under an Item lock | "they can't play any Item cards from their hand" | `move_generation_trainer.rs:67` stops `Item` and `Fossil` | right if a Fossil is an Item card; the premise is note 3 |
| Guts on your own Pokémon (E1) | Guts: "If this Pokémon would be Knocked Out by damage from an attack" | `split_with_guts_survival` and `apply_defender_guts_if_needed` take (side, index) | follows the text |
| Perish Body on a plain queued hit (E2) | "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, flip a coin. If heads, the Attacking Pokémon is Knocked Out." | `forecast_apply_damage_after_coins` (`apply_action.rs:854`) flips it for an attack's queued hit that would Knock Out the opponent's Active Cursola, and applies the retaliation before the knockouts | follows the text; one small imprecision, note 7 |

## Tests: do they fail before and pass after?

From the cloud's logs (I read their result lines and failing-test lists; I have not re-run them):

| step | before the fix | after |
|---|---|---|
| the six sites and the gate | 7 failed, 16 passed (`tests_before_fix.log`) | 23 of 23 |
| Mega Kangaskhan ex | 2 failed, 23 passed | 25 of 25 |
| Will with Confusion | 2 failed, 14 passed | passes |
| text-decided fixes (items 2-5) | 7 failed: the block-coin offer, Will on the block coin (x2), own-side Raging Thunder / Shadow Hit / Earthquake, Shaking Stomp, the own-Bench choice's Active hit, the copied discard | 0 failed |
| Trap Territory | 2 failed (both at two Ariados only) | 0 failed |
| the follow-up | 5 failed: Fossil, Perish Body, Luxury Coin, Guts, Victini text | 0 failed |
| full suite | | 2,027 at 29e126a; 2,035 at 5155ff7; **2,039 passed, 0 failed, 0 ignored at 3090abb** (summed over every `test result` line of `suite_followup.log`) |

Each new test asserts the old failure mode by its own number (0 prevented of 60; no pause; 0.5625 for a forecast; 130, not 160), and the three replaced tests were pins of the old behaviour that said so in their own comments. Two things I checked in the tests themselves: they are not weakened (the only removals are those three pins and a helper refactor), and the gate's control test would catch a leak (it asserts no `ApplyQueuedAttackDamage` appears into a non-coin Pokémon).

## The affected-deck inventory against current main (7c1b62f8)

Re-done by card id over the 87 deck files at main (`decks/` and the switch's carriers; script and output beside this file). It agrees with the cloud's, and adds the lists written since:

- **Will:** brew-01, brew-04, Dustin's 10 (1 copy each) only. **Trap Territory:** Dustin's 12 (2 Ariados B1a 006) only. **Victini:** draft D only (`draft-D-entei-grimhound.txt`, 2 Victini; 1 or 2 Mega Houndoom ex, see the drafts branch). **Mesagoza / Arcade:** Dustin's 01 and 08, brew-04; no Gholdengo anywhere. **Wild Swing:** l-sharpedo (2 Gyarados A4 045). **Chase Order:** t-vespiquen (2 Vespiquen ex B4 011). **Hoopa (Mischievous Ring):** none (the Hoopa ex B4 103 in six lists is a different card).
- **None** under `decks/` or the carriers: a coin-Ability defender (Meowth, Togekiss, Bastiodon, Hisuian Goodra), a block-coin attacker, a Ditto, an own-side damage attacker, a Fossil, Gholdengo, a Guts Pokémon, Galarian Cursola.
- So the later round and the follow-up change no game between lists under `decks/`; the card-text job changes deck 12's games (Trap Territory) and the three Will lists' games only when Will is played and the attacker is then Confused or under a block coin (none has a block-coin attacker, so Confused only). Draft D's Victory Star games change only against a block-coin attacker, and none exists in the lists. The coordinator's note that D holds Victini is right and does not change this. The drafts written after the README (A, B, C, and D) hold no card from the first group.
- The database scan (`second_read_dbscan.py`) finds exactly the audit's card lists: 8 block-coin attackers (9 printings), 4 coin-Ability cards (5 printings), Guts 2, Perish Body 1, Will 1, Luxury Coin 1, Ditto-like copiers 4 (Ditto, Mew ex, Mimikyu, Clefairy). One extra hit for Trap Territory's phrase, Team Rocket's Goo-zooka (B4a 068/110), is an attack effect on the Defending Pokémon, not an Ability, and is not what `retreat.rs` loops over.

## Notes (none blocks)

1. **The smoke's "no game changed in lookahead alone" is not established.** The README (Smoke check) says every one of the 23 changed games had `coin_queued_offered` on the board, and no game changed in lookahead alone, and says it did not trace first differences. That is the reading the tightened rule (Oct 1) replaced: a counter firing anywhere in a game explains nothing unless it fires at or before the first differing tick. Step 8c found five lookahead games (and one more the probe miscounted) where the cause is a queued coin-target frame reached only inside the bot's search, with no on-board counter at the first differing tick; the same can hold here. For the switch's early-warning rows this package should be traced with the 8c machinery (`classify_8c.py`, `tightened_rule.py`).
2. **The counters and the probe do not see the new paths.** The cloud says so (`instrument_scan.py` has no counter for Victory Star after a block coin, Will on a gate, the own-side coin, the queued `ApplyDamage` coin, own-side Guts, Perish Body on a queued hit, Trap Territory). The replay at the next switch needs those counters, and `coin_probe` v2 (turn boundary crossed, free pure frames free; queued for the next switch after Dustin's 8c answer) for the lookahead half.
3. **The Fossil premise rests on community sources.** `rules/01` and `rules/04 §6` say a Fossil is an Item card, citing a community page; the local database stores its type as "Fossil" and shows no type line. The fix is right if the premise is, the cloud's shot row `fossil-item-lock` asks for the recording, and I read a printed type line as plain card text under Dustin's rule, so one picture of a Fossil card settles it. The same question applies to Pokémon Tools, which the engine lets through an Item lock (`trainer_move_generation_implementation`, Tool branch); the package does not touch them and I make no claim.
4. **Two ways to flip one coin.** The gated sites build `ApplyQueuedAttackDamage` (the attack's own path, with its text modifiers), and every other queued attack hit now flips in `forecast_apply_damage`, which does not run the attack's text-specific modifiers (it passes `None, None`). The coin outcome is the same; only attack-text-dependent modifiers on a queued hit could differ. The README's Limits section names the first half.
5. **Order of the two gate coins.** The audit says nothing visible depends on whether the Confusion coin or the block coin is flipped first. One thing does: with Will pending, a Confused attacker under a block coin, Will is used on the block coin in every branch including a Confusion tails (the block coin is assumed flipped first), whereas if Confusion came first a tails would leave Will unused. Rare (Confused, block coin and Will together), and Dustin's rule has no text on the order.
6. **Will in non-coin branches is pre-existing, mirrored.** `force_first_heads_using_will` consumes Will in branches that flip no coin, as `finish_forecast`'s `force_first_heads` already does; the text says Will waits for the next coin. Not introduced here.
7. **Perish Body's knockout check** for a queued hit uses `would_knock_out(.., None, None)`, so an attack text that removes defender effects is not considered. Immaterial for the cards that queue today.
8. **rules/ and PLAN.md are not edited** (the README says so). At the switch: rules/09's "Open engine bugs" entries for these sites, rules/04 §9's ⚠ line on Victory Star, §6's Fossil line and `card_validation.rs`'s old caveats will be out of date.

## What I did and did not do

- Did: read the diff and tests in full, checked every card text against the database, scanned the database for each text, re-did the inventory by id, checked the before/after logs' counts, and checked that every literal `is_from_active_attack: true` in the engine is built in attack code (so the new flip cannot reach Checkup or Ability damage).
- **Did not:** build the engine or run any test (held while the laptop's paired comparison runs; it will say when). A run would re-check the 2,039 and the tests-first commits (each new test failing at its parent); I will add the result here if the laptop says so. Did not play a game, check the bots' pricing (`players/` is untouched), or verify any Recording_QA reference (210403, 203626, 213034) against the video.

## Files

`SECOND_READ_sonnet.md` (this), `second_read_inventory.py` and `second_read_inventory_output.txt` (the id-based deck inventory at main 7c1b62f8), `second_read_dbscan.py` and `second_read_dbscan_output.txt` (the database text scan).

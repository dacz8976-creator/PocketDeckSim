# REGISTERED (Sept 26). B5 candidate "opening Active choice": switch A alone (`koa`), with diagnostics `kob` and `kor`

**Status: registered on Sept 26 on Dustin's word in the laptop session's chat, before any game or build of any code named here.** The text below is the reviewed draft (`REGISTRATION_DRAFT.md` at d7dbfb2), with Dustin's rulings written in. It becomes the registration in the commit that adds this file. Any later amendment goes in its own dated commit with its reason, before any game it affects.
- **History:** written by the laptop session's census (Sept 26) and amended to Fable's call (section 8 of `docs/REVIEW_2026-09-24_direction.md`, 05:30 entry). Amended again to Fable's independent review (`../fable_reviews_2026-09-26/opening_active_draft_review.md`): every item applied, withdrawn items not; section 11 lists each.
- **Dustin's rulings (Sept 26, laptop chat), quoted:**
  - **The reserve route:** "The small-fix route: yes, approved as sharpened, with the one change I asked for — the gain must show on at least one deck that isn't yours."
  - **The (d) carrier (direction line 160, (ii)):** "if 335 of 336 real Mega Altaria/Espeon lists run that Eevee, then Altaria is a non-Dustin deck whose real cells are known, so the gain can be checked against Limitless directly rather than only against paired noise. Yes, it counts, and the same ruling covers Suicune for the Tool fix."
  - **The route is chosen by the measured footprint:** "if the fix reaches Altaria, a table deck, it may not be a 'fix the table can barely see' at all — the 15 percent trigger decides which route applies, and it should be read before the route is chosen, as the rule says."
  - **"Register the draft."**
- **What these rulings fix in the text below:**
  - **The route is not assumed.** The first reading after the build and identity checks is the measured footprint on the table: the share of the 14,000 paired table games in which `koa`'s moves differ from kp3's.
    - Under 15%: the reserve route (section 7), clauses (a) to (e).
    - 15% or more: the ordinary adoption rule (section 7's fallback).
    - Predicted 6.0% (section 5). The route is fixed by that number before any other reading, and not revisited.
  - **Clause (d) is the "yes" branch:** Mega Altaria ex Espeon is the carrier archetype, with Altaria's own-side gain on its seven `koa`-v-kp3 rows as the test. The "no" branch in section 7 is kept for the record and does not apply.
  - **Altaria's seven real Limitless cells, before and after, are read beside (d).** Dustin: the gain "can be checked against Limitless directly". They are reported with the prediction that they move toward Limitless, alongside (b)'s τ̂ margin, which already reads Limitless for the whole table. They are not a separate gate.
  - **Switch A alone (`koa`) is the one candidate.** Switches B and R stay diagnostics (`kob`, `kor`), not registered for adoption.
- **Who builds:** the cloud session, which owns player code, from this file. The laptop runs the tables, mixed rows and readings.
- **Amendment 1 (Sept 26, before any game or build of `koa`; Dustin's word in the laptop chat): the broader test group.**
  - `koa` is also read on the 6 held-out tournament archetypes against the 8 panel lists (B2e's 48 archetype pairings: `rl/results/b2e_card_check_2026-09-26/b2e_pairings.tsv`, pairings 0-47, the same deals and seeds as B2e), with `koa` on both sides against kp3's B2e rows (`rl/results/b2e_rows_2026-09-26/b2e_kp3_arch.jsonl`).
  - Dustin's 6 files in those archetypes (pairings 48-95) are reported beside and not counted.
  - What is read: RUN5's held-out veto (no held-out archetype more than 2 further from pooled Limitless than under kp3; the baseline is B2e's table) and each held-out archetype's score change, reported.
  - The prediction: `koa` changes an opening only where Altaria's list or deck 15 is piloted. In these pairings the held decks never open differently, and their games against the panel's Altaria move only through Altaria's own openings. So the held-out changes should sit within noise, except the Altaria cells, which should move the held deck's score down slightly as Altaria improves.
  - The base is the same as section 2's: if the repaired engine is the base, B2e's rows are regenerated there first.
  - Gauntlet additions Dustin approves later are added by a further dated amendment before the table they belong to.
- **Where the numbers come from.** Every number below is from `README.md`, `census.json` and `limitless_carriers.md` / `.json` in this folder. No game was played to make any of them.
  - census.py was checked by check_census.py and by a second read the same day. That read (README section 9) corrected the Suicune `kor` transition in section 5.
  - The rule check behind "0 contradictions in 220 informative games" is `rule_check.py`, with its output in `rule_check_output.txt` and in `census.json` → `validation` → `altaria (kp3 probe, B2c Sept 26)` → `rule_check`.
  - The Limitless carrier count was checked by an independent recount and by a verifier's third count from the raw files (`limitless_carriers.md`, section 7).

## 1. Decision it changes

Whether kp3's setup evaluation gets a card-agnostic term for the opening Active.
- B2c found the Altaria network's opening worth +19.4 ± 4.6 per differing opening against kp3's Lucario. Over its 400 games that is about +7.7 per game, roughly half of the network's +15.8 edge (`../altaria_network_divergence_2026-09-26/RESULT.md`).
- If adopted, the term becomes part of the one pilot for the screen and the table. If not, kp3 stays and the finding goes to B3's feature set.

**Why switch A is the candidate.** B2c's Eevee openings split on whether the Active Eevee evolved on its own first turn, which is what Boosted Evolution allows (README section 5, second read):
- Where it evolved on its first turn: Eevee over Darkrai **+33.7 ± 9.9** (33 games), Eevee over Swablu **+27.9 ± 9.2** (30).
- Where it did not: **+17.4 ± 12.0** (23) and **−2.6 ± 12.9** (19).

So the Eevee-over-Swablu value sits in the games where the first-turn evolution happened, and only switch A can produce that change. That names A's mechanism. The Darkrai half has no such split: B2c can't tell whether the reason is Bad Dreams working from the Bench (B) or Darkrai's 3-Energy attack (R).

The split is descriptive, not a test. It divides on something after the opening (mostly whether the evolution card was in hand). The test is section 7's.

## 2. The change

**Base.** kp3 at one engine commit: **7fc6ccb** (the official engine, `rl/engine-2026-09-25/`), or the repaired commit once it exists. Not "current main, as the builder states": section 8 of `docs/REVIEW_2026-09-24_direction.md` (line 166) queues tier 1 repairs that reach table games, Bad Dreams among them, and any of them would move the base.
- The references are `rl/results/engine_identity_2026-09-25/k3_500.jsonl` and `kp3_500.jsonl` (k3 and kp3 identical 14,000 of 14,000 at 7fc6ccb, `identity.txt` in the same folder).
- If the table's engine commit is not 7fc6ccb, section 4 says what is regenerated first.
- The pilot `koa` is read against is the one in force when its table runs (section 7, "One pilot").
- It changes players' code only: **tier 2**. That names the code tier; it does not mean "no second read" (section 7).

**Where.** The setup branch of `parametric_value_function_ex6` (`engine/src/players/value_functions.rs` 459-478).
- It runs only while the opponent's setup is masked (`setup_opponent_hidden`, `observation.rs` 48-53), that is at turn 0.
- It gets new `EvalFeatures` switches, off in every existing tier.
- The engine's setup path is not touched:
  - what is offered (`move_generation/mod.rs` 30-42, 140-167);
  - the setup handoff (`apply_action_helpers.rs` 47-80);
  - the setup mask and cutoff (`observation.rs` 48-53, 365-367).

**What it adds.** For the evaluating player's own Active only, read through the suppression-aware `get_in_play_ability_mechanic`:
- **Switch A, "first-turn Active-only Ability": +250.** It applies when both hold:
  - the Active's mechanic is in class A: an Ability that works only from the Active Spot and whose payoff is confined to the owner's first turn (or the turn the holder is played); today exactly `AbilityMechanic::CanEvolveOnFirstTurnIfActive`. Active-only Abilities that pay from the first turn onward (Meloetta's, Legendary Pulse, Quick Growth, the Checkup pair) are class C and are left out by design;
  - `get_highest_evolutions(&active.card, own deck + hand)` is non-empty.

  Details:
  - `CanEvolveOnFirstTurnIfActive` is at `actions/abilities/mechanic.rs` 549. Its engine effect is `move_generation/mod.rs` 198-212.
  - Its text also covers "the turn you play it" (the engine lifts both timing rules, `mod.rs` 209-210). The opening placement can use only the first-turn half.
  - Its printings are Eevee B1 184, P-B 011 and P-B 054.
  - **The deck-plus-hand guard is a list-level safety that fires in every Altaria and deck-15 hand.** Altaria carries 2 Espeon B3a 020 in its 20 cards and deck 15 carries 2 Jolteon ex B1 081, and nothing is discarded before setup. So on the table `koa` is a flat +250 for an Active Eevee.
  - **An "evolution in hand" variant is deliberately not registered.** The actor's own hand is visible at setup, and B2c's first-turn-evolution split (section 1) might tempt one. This is decided now, before any game; it is not added later as a diagnostic row.
- **Switch B, "Bench-working Ability": −250.** Diagnostic code only; not registered. "Bench-working" means the Ability works from the Bench, which is not the same as better there: only the 8 Bench-only settings work better from the Bench, and the 44 anywhere-board settings work equally from the Active Spot. It applies when the Active's mechanic is in one of two classes:
  - Bench-only (8 flag settings);
  - "acts on other Pokémon, the opponent or the owner's draws from anywhere in play" (44 flag settings).

  The classes and every flag in them are in `README.md` section 3. `BadDreamsEndOfTurn` is in the second class (`hooks/core.rs` 618-631 reads every in-play holder).
- **Switch R, "setup readiness": −100 per Energy of the Active's cheapest own attack.** Diagnostic code only; not registered. It is the flag-free reading of the Darkrai half, to be read beside B.

**The classes** live in one new players-side function, `opening_ability_class(&AbilityMechanic)`.
- It is an exhaustive `match` with **no wildcard arm**, so a new variant fails to compile until it is classified.
- It mirrors `census.py`'s `VARIANT_CLASS`. Field-dependent variants are resolved from their own fields: `require_active`, `NoRetreatCostCondition::YourFirstTurn`, `RandomEvolutionTrigger::EndOfOpponentTurnIfActive`, `AttackCostReductionScope`, `NoRetreatCostTarget`.
- It names no card. The mechanics are the engine's own flags (the kq precedent, `deals_damage_without_printing_it`).
- Its doc comment is class A's sentence above, word for word.
- **Who classifies a new variant.** A new variant's classification is itself a tier-2 change, made by the engine change's author in the same commit and checked by the phrase test (section 4). No wildcard arm at any level, including the four nested enums NoRetreatCostTarget, NoRetreatCostCondition, AttackCostReductionScope and RandomEvolutionTrigger; no `..` on the five field-dependent variants. Optionally `#![deny(clippy::wildcard_enum_match_arm)]` on the module.
  - The compile error forces a classification, not a correct one. The phrase test is the only check on it.

**Weights.** Pre-set at 250, half the Active online-score weight of 500 (the kq precedent), and not tuned on any table. B3 fits them later if the feature survives.
- The census re-ran at other weights. Every opening prediction below holds for any A weight from 50 to about 460 and any B weight of 50 or more.
- Above about 460, Eevee starts beating Igglybuff's free attack in hands of four or more Basics. So the weight is not a hidden knob on this table.

**Nothing outside turn 0 changes.** Once the Active is placed, the bonus is constant across that player's remaining setup moves. So the only move that can differ from kp3's is the opening Active itself.

## 3. Codes

| code | switches | role |
|---|---|---|
| `koa<N>` | A | **the adoption candidate**, by the reserve route |
| `kob<N>` | B | diagnostic, mixed rows only; not registered for adoption |
| `kor<N>` | R | diagnostic, mixed rows only; not registered for adoption |

- All three are `kp<N>`'s public-pricing arm with the new value function.
- They are parsed before `k<N>`, as kp, kq and kd are (`players/mod.rs` 210-232). The names are free in main's `parse_player_code` as of this reading; the builder may rename them.
- The first draft's `ko<N>` (A + B) is dropped, because B is not registered. If a `ko` code is ever added, parse `koa`, `kob` and `kor` before it. An arm written like kp's (`strip_prefix("ko")`, then `Err` when the rest is not a number) placed first would reject `koa3`.
- Every table and row is played at depth 3.

## 4. Tests and identity checks, before any table

- **k3 and kp3** replay all 14,000 table games move for move from the new binary, against the reference files of section 2 (`rl/results/engine_identity_2026-09-25/k3_500.jsonl` and `kp3_500.jsonl`). This is the standard check for any pilot change.
- **If the table's engine commit is not 7fc6ccb**, kp3's 28 x 500 table and its mixed-row references are regenerated at that commit first; the games that differ from the 7fc6ccb files are listed and shown to lie in cells where the repaired mechanic is reached; scoreboard v2's kp3 row is re-scored on them; `koa`'s footprint and (b), (c) and (d) are read against those files.
- **kq3 and kd3** spot replays on 40 deals per pairing (the kpr practice), because the change sits in the setup branch every k tier reaches. They cost minutes.
- **With every switch off**, the new code path replays kp3 on the same games.
- **Unit tests** on constructed setup hands (Altaria list; A = `koa`, B = `kob`):

  | hand | koa | kob | kp3 |
  |---|---|---|---|
  | {Darkrai, Eevee} | Eevee | Eevee | Darkrai |
  | {Igglybuff, Eevee} | Igglybuff | Igglybuff | Igglybuff |
  | {Darkrai, Swablu} | Darkrai | Swablu | Darkrai |
  | {Swablu, Eevee} | Eevee | Swablu (tie to the id that sorts last as a string, byte order) | Swablu |

  - **How the hands are decided.** Through `decision_fn` on `PlayerObservation::from_state`, or with `setup_opponent_hidden = true` set on the state. The setup branch (`value_functions.rs` 459) runs only when that flag is true, and `from_state` sets it as `turn_count == 0` (`observation.rs` 50); `State::new` leaves it false. A test through `decide_omniscient` passes the raw state and does not exercise the term. (`promotion_continuation_tests.rs` 227 shows how to set the flag on a test state.)
  - Plus one hand with an Eevee and no Espeon anywhere in deck or hand: switch A must not fire.
  - **The phrase test.** Every `EFFECT_ABILITY_MECHANIC_MAP` entry's class must agree with its printed condition phrases: "this Pokémon is in the Active Spot", "this Pokémon is on your Bench", "first turn".
    - Two known exceptions: `CanEvolveIntoEeveeEvolution` (a prohibition: its "first turn" forbids evolving then) and `CannotAttackWithoutBenchedNames` (a drawback classed Active because only the Active attacks; its "on your Bench" names other Pokémon).
    - The phrases are the full "this Pokémon is ..." forms because the short forms fail: "in the Active Spot" also names the target in map lines 524 and 722 (`AttachEnergyFromZoneToActiveTypedPokemon`, classed anywhere).
    - Flags with no position phrase (`BadDreamsEndOfTurn`, `IncreasePoisonDamage`, `SoothingWind`, `TimeRecall`, `DamageOpponentActiveOnZoneAttachToSelf`, `HealActiveYourPokemon`) are classed by their hook, with the hook's file:line beside the arm, because the phrase test cannot check them. Today's lines: `hooks/core.rs` 618-631, `actions/apply_action_helpers.rs` 226-240, `state/mod.rs` 1162-1177, `move_generation/attacks.rs` 181-183, `state/energy.rs` 149-170, and the gate `!card.ability_used` at `move_generation_abilities.rs` 189.
- **The setup-only property, checked on the whole table.** In every table game where neither deck's opening Active differs from kp3's game on the same deal, the candidate's game must equal kp3's move for move.
  - Predicted changed-opening shares are in section 5.
  - Any game that differs with both openings unchanged means the change leaked past turn 0. That stops the reading.
- **Mixed-row identity.** With the code on a deck that carries no flagged Basic, that deck's 3,500 mixed games equal kp3 v kp3 game for game.
  - For `koa` that is every deck but Altaria.
  - For `kob`: Blaziken, Lucario, Sceptile, Suicune.
  - For `kor`: Blaziken, Lucario, Sceptile, Hydreigon.

## 5. Footprint, registered from the census

- **Definition.** A game is "changed" when its play differs from kp3's on the same deal at least once. Because only the opening Active can differ, this is exactly: either deck's opening Active changed.
- **Seeds.** The table's own deals: 72,000,000 + pairing × 10,000 + game, game < 500. They are reused on purpose, as for every table candidate, and the mixed rows use the same deals. No new seed block for the table or its mixed rows. The one new block is for the variant-list check's row against the table's own Altaria list, which has no table pairing (section 7, (d)).

| code | expected share of the 14,000 table games | per deck (share of that deck's openings changed) |
|---|---:|---|
| `koa` | **6.0%** (840; 95% sampling range about 790 to 890) | Altaria 24.0% (Darkrai → Eevee 14.5, Swablu → Eevee 9.5); every other deck 0 |
| `kob` | 14.6% | Altaria 24.0% (Darkrai → Swablu 14.5, Darkrai → Eevee 9.5); Hydreigon 13.3% (Bombirdier → Deino 9.7, → Mega Absol ex 3.6); Vespiquen 16.2% (Teal Mask Ogerpon ex → Shuckle ex 9.7, → Combee 6.6); Weezing 6.6% (Darkrai ex → Team Rocket's Koffing) |
| `kor` | 17.1% | as `kob` on Altaria, Vespiquen and Weezing. Hydreigon 0. Suicune 24.2% (Suicune ex → Chien-Pao ex 9.7, → Frigibax 14.5: P-B 037 8.0, B2a 034 6.6) |
| A + B (reference only, not a code here) | 16.8% | Altaria 33.5% (Darkrai → Eevee 14.5, Darkrai → Swablu 9.5, Swablu → Eevee 9.5), plus `kob`'s other three decks |

A goes alone by Fable's call: B is unattributed (B2c can't tell it from R), and bundling it with A would repeat the kd lesson. The A + B row also shows the pair over the 15% trigger, where A alone is well under it.

**Which number decides (a).** The measured share decides (a), not the census's estimate. `koa`'s 790 to 890 is under 2,100 (15% of 14,000) with margin. `kob`'s 14.55% straddles the line and matters only if B is ever registered.

**Outside the table** (reported, not read by the rule; `census.json` has every list):
- **Dustin's decks and brews:** the written predictions are in section 6.
- **The B2e held-out rows.** No held-out list carries a switch-A flag. So under `koa` a held-out deck's row moves only through its games against Altaria, at most 1/8 of Altaria's cell change. Under `kob`, h-hoopa_absol's own opening changes in 3.6% of deals (section 6).
  - **Predicted sign under `koa`: down.** Every held-out deck's panel average falls by at most Altaria's cell change divided by 8, because Altaria pilots better against it.
  - Whether that is further from Limitless is read from the B2e rows (e9bf38f; direction line 157) before `koa`'s table.
- **The proposed ladder panel** (`decks/screen/panel_ladder_2026-09-26/`). Its eight lists are the table lists card for card. Its two added lists (`l-charizardy.txt`, `l-sharpedo.txt`) carry no A or B flag, and no switch changes their opening. So under `koa` the screen's opponents move only in games against Altaria.

## 6. Predictions: which decks move, and which way

**`koa`, the adoption candidate.**
- **Altaria's own side rises.**
  - **Against Lucario, +5.5 points per game.** This is B2c's play-out values weighted by the census's transition shares. It is ±1.4 from the play-outs alone, and roughly +1 to +10 once the 500-game cell's own noise is added.
  - **Against the other six decks: up, size not predicted.** B2c played out only Altaria v Lucario.
  - **Pooled over its 7 mixed rows: above zero beyond paired noise.**
- **Every other deck's own side is exactly unchanged** (identity, section 4). Altaria's opponents' table scores move only by Altaria's change in that cell.
- **Scoreboard v2 (27-cell decision set; Altaria v Sceptile quarantined).**
  - Altaria is underrated in 4 of its 6 decision cells. The misses, kp3 minus Limitless: Blaziken −17.9, Lucario −10.0, Suicune −7.4, Hydreigon −6.9.
  - It is overrated in the other 2: Vespiquen +9.8, Weezing +7.4.
  - A uniform rise of 3 to 7 points moves the raw mean squared miss by only about −2 to −4 points². That is inside the ΔMSE's noise at 500 or 2,000 deals, so the ordinary adoption rule is predicted not to adopt `koa` (section 7), which is why `koa` goes by the reserve route.
  - Under rule v2 the Vespiquen and Weezing misses may grow. Such a growth is not a veto that counts, because Altaria's own side is better, not worse. It is an investigation item.
- **Sentinels.**
  - Altaria v Hydreigon moves, predicted toward Limitless (kp3 47.6, Limitless 54.5 ± 13.0).
  - Blaziken v Weezing and Suicune v Weezing are exactly unchanged.

**`kob` and `kor`, the diagnostics.**
- **Altaria.** Both predict the same openings, so the same gain against Lucario: +5.3 from B2c.
- **Hydreigon** (`kob` only), **Vespiquen and Weezing** (both), **Suicune** (`kor` only).
  - **Directions, from the census's own class table:**
    - **Suicune under `kor`: down** (Legendary Pulse forgone). Suicune ex's end-of-turn draw works only from the Active (`hooks/core.rs` 381-399; "At the end of your turn, if this Pokémon is in the Active Spot, draw a card."), and `kor` moves it off the Active in 24.2% of Suicune's deals, for Frigibax (14.5%) or Chien-Pao ex (9.7%), for the whole game.
    - **Hydreigon under `kob`: up.** Bombirdier's Villainous Delivery works only from the Bench, and Deino, the evolving Basic, opens instead.
    - **Vespiquen and Weezing under both: direction not predicted.**
  - **Which part of B each carrier is.** Under `kob`, Hydreigon is the Bench-only carrier (Bombirdier). Altaria (Darkrai's Bad Dreams), Vespiquen (Teal Mask Ogerpon ex's Soothing Wind) and Weezing (Darkrai ex's Nightmare Aura) are anywhere-board carriers. So `kob`'s mixed rows attribute the two parts of B without a new code.
  - The footprint caps each own-side change at about its changed share × 15 points per changed game: Weezing ±1.0, Hydreigon ±2.0, Vespiquen ±2.4, Suicune ±3.6.
  - The attribution question is whether Hydreigon moves under `kob` and Suicune under `kor`, since elsewhere the two diagnostics make the same changes. What those rows can and cannot say is in section 7.

**Written predictions for Dustin's decks and brews** (`census.json`, share of all deals whose opening changes; weights 250).
- **Under `koa` (switch A): deck 15 only.**
  - 15 Jolteon Oricorio Raticate: 9.7% (Oricorio → Eevee). **Predicted up, reported only.** Jolteon ex B1 081 is a Stage 1 from Eevee and `STAGE1_LOOKUP` is built from `evolves_from` (`card_logic/rare_candy.rs` 14-26), so the gate fires. Deck 15 is not a B2e held-out deck.
  - Every other deck of Dustin's, every brew and every B2e list: unchanged.
- **Under `kob` (switch B): four of Dustin's decks, six brews and one B2e list.**

  | list | opening changes | transitions |
  |---|---:|---|
  | 05 Indeedee Stoutland | 17.6% | Indeedee ex → Lillipup 17.6 |
  | 08 Garchomp toolbox | 8.0% | Celebi → Gible 8.0 |
  | 12 Ariados Whimsicott Ogerpon | 16.2% | Teal Mask Ogerpon ex → Spinarak 9.7, → Cottonee 6.6 |
  | 14 Comfey Raticate Hypno | 16.2% | Comfey → Team Rocket's Drowzee 9.7, → Team Rocket's Rattata 6.6 |
  | brew-03a Arceus Nihilego Toxapex | 29.5% | Nihilego → Arceus ex 17.6, → Mareanie 11.8 |
  | brew-03b Arceus Crobat Nihilego Toxapex | 20.4% | Nihilego → Arceus ex 9.7, → Mareanie 6.6, → Zubat 4.2 |
  | brew-05b Meowstic Hatterene Comfey | 16.2% | Comfey → Hatenna 9.7, → Espurr 6.6 |
  | brew-06 Pyukumuku Silvally Payback | 4.2% | Comfey → Pyukumuku 4.2 |
  | brew-06b Pyukumuku Silvally Scyther | 10.7% | Teal Mask Ogerpon ex → Team Rocket's Scyther 6.6, → Pyukumuku 4.2 |
  | brew-07 Hoopa Darkrai Sableye | 3.6% | Darkrai ex → Mega Sableye ex 3.6 |
  | h-hoopa_absol (B2e) | 3.6% | Darkrai ex → Mega Absol ex 3.6 |

  - **Carrying a B flag but unchanged:**
    - deck 03 (Wailmer already opens);
    - deck 04 (both of its B carriers are penalised alike);
    - deck 07 (Skarmory ex already opens).
  - Every other deck and brew: unchanged.
- **Under `kor`:** not listed here. It reaches eight lists B does not touch (decks 01, 02, 03, 11 and 15; brews 01, 02 and 10). Its transitions are in `census.json`, key R.
- **How these are checked.** They are predictions of openings only. The per-game opening counter (section 7) checks them whenever these lists are played under the code, and the rule does not read them. Under `koa`, a screen of Dustin's decks moves only through deck 15's own openings and through games against Altaria.

## 7. The reading

**Route: chosen by the measured footprint, read first.** Dustin approved the reserve route (Sept 26) and ruled that a panel archetype whose real lists carry the card may be the (d) carrier.
- Reading order:
  1. Build and identity checks (section 4).
  2. `koa`'s table on the 14,000 table deals.
  3. **The footprint:** the share of paired games whose moves differ from kp3's. **Under 15% → the reserve route below; 15% or more → the ordinary adoption rule (the fallback at the end of this section).** Predicted 6.0%.
- The route is fixed by that number before (b) to (e) or any ΔMSE is read, and not revisited.

The five clauses are as fixed in section 8 of `docs/REVIEW_2026-09-24_direction.md` (line 130), applied to `koa`:

- **(a) Footprint under 15%.**
  - Predicted 6.0%, measured on the table (section 5).
  - The census corrects section 8's assumption that this candidate's footprint is above the trigger ("the choice is made in every game"). The opening changes only in hands where a flagged Basic sits beside another Basic.
- **(b) No harm.**
  - On the table, the τ̂ margin (kp3 minus `koa`) must have a 90% interval lower bound of −1.0 or above.
  - **Predicted sign: positive and small.** Altaria's four underrated decision cells outweigh its two overrated ones (section 6). So a negative margin reads as a surprise, not as noise.
  - No veto may count under rule v2 (section 8's (b) as written).
  - **Reported before and after, not a gate: Altaria's seven Limitless cells.** Section 8 reports a (d) archetype's real Limitless cells this way, and here that archetype's cells are the table's Altaria cells. The "before" figures (kp3 table against scoreboard v2, development half; `limitless_carriers.md` section 6):

    | Altaria v | kp3 | Limitless v2 (n) |
    |---|---:|---|
    | Blaziken | 58.6 | 76.5 ± 14.3 (34) |
    | Hydreigon | 47.6 | 54.5 ± 13.0 (56) |
    | Lucario | 62.4 | 72.4 ± 6.9 (161) |
    | Sceptile (quarantined) | 42.8 | 45.4 ± 9.4 (108) |
    | Suicune | 48.8 | 56.2 ± 12.1 (65) |
    | Vespiquen | 47.4 | 37.6 ± 9.8 (93) |
    | Weezing | 40.4 | 33.0 ± 13.4 (47) |

- **(c) In the 28-pairing mixed rows, no meta deck's own side worse beyond paired noise.** This is read from the same `koa` v kp3 rows as (d), for every meta deck's own side:
  - **Altaria's own side:** its seven rows with `koa` on Altaria.
  - **Each of the seven opponents' own side:** its row with `koa` on it against kp3's Altaria. These rows are identities (section 4), so the change is exactly 0.
  - **The 21 pairings without Altaria** are identities in both directions (section 4). No deck's own side can move there.
- **(d) A gain beyond paired noise on the new bot's own side, and on a Limitless top-30 archetype that is not Dustin's and carries the relevant cards.**
  - **The archetype is Mega Altaria ex Espeon.**
    - Sept 10 rank 2 (289 players) and window rank 2; not Dustin's by the kt census's rule.
    - **Carrier share: 335 of its 336 development-half Limitless lists (99.7%; 95% interval 98.3 to 99.9%)** carry Eevee B1 184, two copies in 333. That covers all 52 of its events and all 51 of its top-8 finishes. Every carrier also runs Espeon B3a 020, so switch A can fire.
    - The table's Altaria list is its representative: 144 of the 336 lists equal it card for card.
    - Source: `limitless_carriers.md`, from the Cowork Limitless pull (`rl/results/limitless_skill_model_2026-09-25/`), one of the two list sources section 8 names.
    - The count is development half only. The holdout standings were not opened, as in the kt census and B2e, so there is no pooled figure.
  - **The test.** `koa` v kp3 mixed rows on Altaria's seven pairings, both directions: the candidate on one deck, kp3 on the other, 14 rows × 500 deals on the table's seeds.
    - The gain is Altaria's own side, pooled over its seven rows with `koa` on Altaria, above zero beyond paired noise.
    - The archetype is the table's own Altaria, so both halves of (d) are read on the same rows.
    - **Under this choice (d) is one test, not two.** The clause reduces to the own-side gain on Altaria's seven `koa`-v-kp3 rows. The seven before/after Limitless cells in (b) are the only added evidence, reported, not gated.
    - Those seven rows are also (c)'s Altaria reading, and the Altaria v Lucario row repeats the matchup that produced the hypothesis, on new deals. The fixed text was written for an archetype outside the eight lists ("the table can see the fix through them even though the eight lists cannot"); no non-Dustin list in scope other than Altaria's own and its two variant lists carries the flag.
  - **Dustin's ruling, once for both candidates, may a panel deck serve as the (d) archetype? YES (Sept 26).** It covers this candidate's Altaria and kt's Suicune. Only the "yes" branch below applies; the "no" branch is kept as it was written before the ruling.
    - The kt carrier census raised the same question for Suicune (kt switch 1; `../kt_carrier_census_2026-09-26/README.md`, section 7). One ruling covers kt's Suicune and this candidate's Altaria.
    - **If he rules yes** (and approves the route): (d) is the one test above, with the variant-list rows below reported beside it.
    - **If he rules no (written now, before any game):** the only top-30 carrier off the panel is Mega Altaria ex Igglybuff (Sept 10 rank 29; window rank 34). It carries the card in 4 of 25 lists (16%), one copy each, with no top-8 finish, and no list was built for it (`limitless_carriers.md`, section 3). No other top-30 archetype carries the card.
      - By the closure sentence, an occasional carrier with no built list does not "carry the relevant cards". So **the route is closed for `koa`**, and adoption can come only by Dustin's explicit override, recorded as such. The fallback below (the ordinary adoption rule) still reads `koa` and is predicted not to adopt it.
      - The other way to write this branch, naming Mega Altaria ex Igglybuff now with a carrier list built, card-checked and legality-scanned by the B2e rule before any game, is not taken here. Dustin can choose it instead, but only before any game.
    - **A fact for the ruling, with no position taken:** Eevee B1 184 is also in Dustin's deck 15. The archetype is still not his by the kt rule, which reads the archetype's named Pokémon.
  - **A (d) check outside the eight lists' own cells, run under either ruling.** `koa` on `decks/variants-2026-09-23/altaria_lanora_blockdragon_2026-09-10.txt` against the eight panel lists, paired with kp3 on the same list and the same deals, 8 × 500 games per arm (8,000 games, on the laptop, after B2e).
    - **The list and its source.** LaNora's Block Dragon list (Sept 10, 1st of 150): provenance at `rl/results/limitless_check_2026-09-23.md` line 108 and its SHA-256 at line 119. It recurs in 27 Limitless lists and carries 2 Eevee B1 184 with 2 Espeon B3a 020; switch A changes 16.0% of its openings (README section 8).
    - **The pairing.** The variant list takes Altaria's place against each of the eight panel lists. One arm has `koa` on the variant list, the other kp3; kp3 plays the opponent in both. Deals: against the seven non-Altaria lists, the table's seeds for Altaria's pairing with that deck (72,000,000 + pairing × 10,000 + game, game < 500), as the list-refresh variant games did (`limitless_check_2026-09-23.md` line 115). Against the table's own Altaria list, which has no table pairing, a new block above every range in START_HERE's seed table, written into the dated registration commit before any game.
    - **What is read.** The variant's own-side gain (the `koa` arm minus the kp3 arm, same deals), pooled over the eight rows, beyond paired noise; predicted up.
    - **How it counts: reported beside (d), not a gate.** Dustin ruled yes, so (d)'s test stays Altaria's seven rows and these variant rows are reported beside it. (Fable's plan lens recommended them as (d)'s outside-the-table evidence and the flags lens called them optional; they are run and reported.)
  - **The closure sentence, verbatim from section 8 (line 130):**

    > Stated up front, before any census is read: if the card census finds no Limitless top-30 archetype outside Dustin's decks that carries reduction Tools or turn-effect cards, or finds one with no usable decklist, the route is closed for that candidate and adoption can come only by Dustin's explicit override, recorded as such, as with kp3; the route is not loosened after the census is seen.

    - Its card words are kt's. For this candidate the relevant cards are switch A's printings (Eevee B1 184, P-B 011, P-B 054).
    - Dustin ruled that a panel deck may serve (Sept 26). The count found such an archetype (Mega Altaria ex Espeon, with usable lists in numbers), so the sentence does not close the route.
    - If he rules that it may not, the sentence applies as written: the Igglybuff variant's 16% share with no built list does not count (the "no" branch above), so the route is closed for `koa`.
- **(e) As in section 8:** "On that evidence, adoption for the screen and the table pilot together, so there is only ever one pilot."
- **One pilot.** `koa` is read against the pilot in force when its table runs. If kt3 has been adopted by then, `koa` is rebuilt on kt3 with kt3's references as the base and this registration is re-issued, not amended. If both pass separately, the combined code gets section 4's identity checks and one table before it becomes the pilot. (kt's switch 1 is pending by the same route on the same kp3 base; direction line 161.)
- **Confirmation.** The holdout was spent on Sept 25, so confirmation can only come from events after the freeze date. The plan's confirmation needs size as well as direction (RUN5: the τ̂ margin at least half the development half's, with its own 90% interval above zero), which a no-harm candidate with a margin predicted near zero (bound −1.0, (b)) cannot meet by design.
  - So under the reserve route `koa` becomes the working pilot and stays "unconfirmed" until the plan defines confirmation for no-harm candidates.
  - That is a plan question for Dustin (the kt registration has the same gap), not a clause the builder invents later.
  - A proposal for him, not registered here: (b) re-read on the post-freeze cells with the same −1.0 bound, and Altaria's seven post-freeze cells reported against `koa`'s and kp3's tables.
- **Second reader.** `koa`'s adoption gets a second reader (RUN5: any pilot adopted or played by Dustin gets one). "Tier 2" in section 2 names the code tier; it does not mean "no second read".

**Fallback: if the measured footprint is 15% or more** (Dustin approved the reserve route, so this is the only way it applies), `koa` is read by the ordinary adoption rule as fixed: paired ΔMSE on the decision set, adopted only if the whole 95% interval is below zero, vetoes under rule v2, no doubling. Predicted outcome: not adopted, because a change confined to six decision cells moves ΔMSE by about −2 to −4 points², inside its noise at 500 or 2,000 deals. Adoption would then be Dustin's override, recorded as such.
- (A "no" on the panel-deck question would also have led here. Dustin ruled yes, so it does not.)
- "Undecided" is not an outcome of the adoption rule; the doubling to 2,000 deals belongs to the τ̂ margin rule for variant screens (RUN5; direction line 201), not to adoption.

**Under either route, reported and not decided on:**
- Correlation, favorites right, real error τ̂ for kp3 and `koa`.
- The footprint against section 5.
- The per-deck opening transitions.
- **A per-game counter the table files must carry:** each seat's opening Active under the code played, so the transitions can be read from the files without replays.

**B and R: the diagnostics `kob` and `kor`.**
- **Mixed rows only, side by side.** Each diagnostic plays one deck with kp3 on the other, both directions, on the same deals as `koa`'s rows.
  - They cover the decks each one changes: `kob` Altaria, Hydreigon, Vespiquen, Weezing; `kor` Altaria, Suicune, Vespiquen, Weezing.
  - Their identity decks (section 4) are played as checks.
- **They are run before either switch is ever registered, and they are for attribution, not adoption.** They could name the Darkrai half: Hydreigon's own side up under `kob`, or Suicune's own side down under `kor`, as defined under "What they can and cannot say" below.
- **Reading order.** `koa`'s decision is read first and never from the `kob` or `kor` files.
- **What they can and cannot say.**
  - `kob`'s and `kor`'s Altaria rows are predicted equal to `koa`'s within noise and are not evidence for B or R. Both make the same Altaria changes (Darkrai → Swablu 14.5%, Darkrai → Eevee 9.5%), worth +5.3 against Lucario from B2c (0.1454 × 18.6 + 0.0947 × 27.0), nearly `koa`'s +5.5 (0.1454 × 27.0 + 0.0947 × 16.1) through different hands.
  - The only rows that can discriminate are single decks whose caps sit at or below paired noise: Hydreigon about ±2.0 under `kob`, Suicune about ±3.6 under `kor`, against about ±4 to ±4.8 per 500-game mixed row and about ±1.5 to ±1.8 pooled over seven (`../table_readings_2026-09-24/kpr3_paired_reading.md`).
  - **"The Darkrai half proves real"** means Hydreigon's own side up beyond pooled noise under `kob` (and unchanged under `kor`, which does not touch it), or Suicune's own side down under `kor`. Anything short leaves it unnamed. That is the predicted outcome: "not determined".
- Neither is an adoption candidate under this registration. Any later B or R candidate is a new registration.
- **The accepted cost of not bundling B.** `koa` leaves the {Darkrai, Swablu} hands opening Darkrai, unchanged: 14.5% of Altaria's deals, where B2c measured Swablu over Darkrai at +18.6 ± 8.0 over 41 games, about +2.7 per Altaria-v-Lucario game.

## 8. What would refute it

- **A leak.** Any identity in section 4 fails, including a changed game with both openings unchanged. Stop, and fix before reading anything.
- **The census's model of kp3's setup choice is wrong.** For example:
  - Altaria's changed-opening share under `koa` falls outside 22.6 to 25.4% of its 3,500 games;
  - a transition not in section 5 appears;
  - another deck's opening changes.

  Then the predictions above do not hold, and the reading stops for a re-read.
- **The B2c result does not carry to the rule.** `koa` on Altaria alone, pooled over its 7 mixed rows, shows Altaria's own side at or below zero beyond paired noise. Or Altaria v Lucario's mixed row lands below zero beyond its noise (predicted +5.5).
  - Either way, switch A does not capture what the network did. It is not adopted, and the finding goes to B3 unchanged.
- **A reason to doubt the class table, not a refutation of `koa`.** A `kor` Suicune row that is not down (section 6) is a reason to doubt the class table as a setup rule. README section 6 records it under option 2 as a known weakness of R relative to B.
- **Not a refutation, stated in advance:**
  - A table ΔMSE not below zero (predicted).
  - `kob` and `kor` making the same Altaria change (predicted). This leaves the Darkrai half unnamed, which is a reason to register nothing more yet.

## 9. Known limits (kept as registered)

- **Only one matchup has values.** Play-out values exist for Altaria v Lucario only. The other cells' signs are expected, not measured.
- **The Hydreigon network's openings are unread.** Its records hold only move numbers. A replay-only pass (no probes, no play-outs) can name them before the table if Fable wants it; this registration doesn't depend on it.
- **Who goes first isn't used.** It isn't a field of the setup observation, and no term may read the opponent's hand count during setup (`observation.rs` 56). B2c shows the gain is the same either way.
- **Weakness to the opponent can't be used.** The opponent's board is masked at setup and kp3 has no list.
- **Other Active-only Abilities are left out** (switch C in the census: Caterpie's Quick Growth, Legendary Pulse, Innards Out). Nothing measured supports them, and they would add Sceptile and brews 06/06b to the footprint.
- **Drawback Abilities are left out** (Regigigas's Seal of Antiquity, which kp3 opens in 16% of deck 01's deals). Reported only.
- **The carrier count is development half only** (`limitless_carriers.md`, section 2).
- **An engine rules question, tier 1 and separate.** On-Bench-entry triggers fire for setup placements (`apply_action.rs` 1111-1120). No list in scope carries one.
- **Unmapped Abilities.** A Basic whose Ability the engine has not mapped carries no flag; the coverage flag reports it. (`get_ability_mechanic` returns `None` for a text not in the map, `effect_ability_mechanic_map.rs` 878-893, so `opening_ability_class` is never reached. None of the 48 lists' Basics has one today.)

## 10. Sources

- `README.md` (this folder): the setup code path with file and line, the flag classes, the census table, the network-study checks (including the first-turn-evolution split, section 5) and the design options.
- `census.json`: per list, the Basics and their flags, the choice and opening shares, and the transitions for A, B, A+B, C, D, R and A+R. Also `table_footprint`, `b2c_expected_altaria_v_lucario` and `validation`.
- `check_census.py` and its outputs: the independent re-derivation.
- `rule_check.py`, `rule_check_output.txt` and `census.json` → `validation` → `altaria (kp3 probe, B2c Sept 26)` → `rule_check`: kp3's opening rule against B2c's records (235 opening decisions; 0 contradictions in 215 informative games, 220 counting kp3's later setup picks; the network's order fits 220 of 235, exceptions listed by game).
- `../fable_reviews_2026-09-26/opening_active_draft_review.md` and its three lens notes: Fable's review of the 3c60d16 version, applied in this one (section 11).
- `../engine_identity_2026-09-25/`: the base's reference files (`k3_500.jsonl`, `kp3_500.jsonl`, `identity.txt`).
- `docs/REVIEW_2026-09-24_direction.md`, section 8, line 160: Dustin's rulings, (ii) the panel-deck question (answered yes, Sept 26, laptop chat; quoted at the top of this file).
- `limitless_carriers.md` and `limitless_carriers.json` (this folder): the clause (d) carrier count by Altaria variant, every archetype that carries the flag, the independent recount, and Altaria's seven "before" cells.
- `docs/REVIEW_2026-09-24_direction.md`, section 8, line 130: the reserve route's clauses and the closure sentence.
- `../kt_carrier_census_2026-09-26/README.md`: the Dustin rule, the ranks and the panel-deck question for Suicune.
- `../altaria_network_divergence_2026-09-26/RESULT.md` and `opening_choice.txt`: the B2c values.
- `../table_readings_2026-09-24/kpr3_paired_reading.md`: kp3's cells used in sections 6 and 7.
- `../scoreboard_v2_2026-09-25/limitless_v2_dev.json`: the Limitless v2 cells.

## 11. Changes from Fable's review (Sept 26), for the builder's amendment record

The review read the draft at 3c60d16; its line numbers are that version's. Every high and medium item is applied as the review words it, and every low item. Not applied, because the review withdrew them: the weight-gate and KQ/KD zeroing "obligation" (section 2's "off in every existing tier" and section 4's replays already cover identity), the "four-Basic" objection (only "or more" added), and anything about "Fable's ruling" (the draft never said it).

| item | what changed | where now |
|---|---|---|
| H1 | One engine commit named (7fc6ccb, or the repaired commit once it exists) with the reference files by path; regeneration rule if the table's commit is not 7fc6ccb | section 2 "Base"; section 4, second bullet |
| H2 | The fallback is the ordinary adoption rule as fixed, no doubling, predicted "not adopted", adoption then by override; "not below zero" replaces "undecided" | section 7, fallback; section 8; section 6 wording |
| M1 | (d) is one test under the Espeon choice; the "no" branch written now (route closed for `koa`, override only); the variant-list rows run under either ruling and reported | section 7 (d); status block |
| M2 | Class A defined as Active-only with the payoff confined to the first turn (or the turn played); class C left out by design; same sentence as the doc comment | section 2, switch A and "The classes"; README plain words |
| M3 | Phrase test on "this Pokémon is ..." phrases, two exceptions, the six phrase-less flags classed by hook with file:line | section 4 |
| M4 | The rule check as a script and output, and a `rule_check` block in `census.json` | `rule_check.py`, `rule_check_output.txt`, `census.json`; status block; README sections 2 and 5 |
| M5 | Reading order, what `kob`/`kor` can and cannot say, what "the Darkrai half proves real" means, the cost of not bundling B | section 7, diagnostics |
| M6 | Suicune under `kor` down, Hydreigon under `kob` up, Vespiquen and Weezing not predicted; a `kor` Suicune row not down is a reason to doubt the class table | section 6; section 8; README section 6, option 2 |
| M7 | Confirmation: working pilot, "unconfirmed" until the plan defines it for no-harm candidates, a plan question for Dustin; a proposal given, not registered | section 7, "Confirmation" |
| M8 | One pilot: read against the pilot in force; rebuilt and re-issued on kt3 if kt3 is adopted first; combined code checked and tabled if both pass | section 7, "One pilot"; section 2 "Base" |
| L1 | "222 and 1" attributed to the right count | README section 5 |
| L2 | Ties go to the id that sorts last as a string (byte order) | section 4 table; README section 2 |
| L3 | Constructed hands decided through `decision_fn` on `PlayerObservation::from_state` | section 4 |
| L4 | The deck-plus-hand guard is inert on every list in scope; no "evolution in hand" variant | section 2, switch A |
| L5 | Who classifies a new variant; no wildcard at any level, no `..` on field-dependent variants | section 2, "The classes" |
| L6 | Route 1 cites ruling (ii) at direction line 160 as a precondition, with the fallback | section 7, "Route"; status block |
| L7 | All four opening counts and the ordering check quoted | README plain words |
| L8 | Boosted Evolution's three printings | README section 3 |
| L9 | 130 flag settings over 124 variants (156 map entries) | README section 3 |
| L10 | "Works from the Bench, not the same as better there"; Bench-only and anywhere-board carriers named | section 2, switch B; section 6 |
| L11 | Unmapped Abilities carry no flag; the coverage flag reports them | section 9 |
| L12 | The measured share decides (a) | section 5 |
| L13 | Held-out decks down by at most Altaria's change / 8; deck 15 up, reported only | sections 5 and 6 |
| L14 | kq3 and kd3 spot replays; a second reader for adoption; (b)'s margin predicted positive and small | sections 4 and 7 |

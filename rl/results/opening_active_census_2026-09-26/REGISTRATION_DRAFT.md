# DRAFT: not registered. B5 candidate "opening Active choice" (`koa`, with diagnostics `kob` and `kor`)

**Status.** This is a draft written by the laptop session's census (Sept 26), for Fable to review and then for the cloud or the laptop to register.
- It becomes a registration only when the builder copies it, with any amendments and each one's reason, into a dated commit before any game of any code named here.
- Two things are needed first:
  - **Fable's review.**
  - **Dustin's choice of route** (section 7). It changes which code is the adoption candidate.
- Every number below is from `README.md` and `census.json` in this folder (census.py, checked by check_census.py and by a second read the same day, README section 9, which corrected the Suicune `kor` transition in section 5). No game was played to make it.

## 1. Decision it changes

Whether kp3's setup evaluation gets a card-agnostic term for the opening Active.
- B2c found the Altaria network's opening worth +19.4 ± 4.6 per differing opening against kp3's Lucario. Over its 400 games that is about +7.7 per game, roughly half of the network's +15.8 edge (`../altaria_network_divergence_2026-09-26/RESULT.md`).
- If adopted, the term becomes part of the one pilot for the screen and the table. If not, kp3 stays and the finding goes to B3's feature set.

## 2. The change

**Base.** kp3 at the official engine's commit (7fc6ccb, `rl/engine-2026-09-25/`) or current main, as the builder states. Players' code only: **tier 2**.

**Where.** The setup branch of `parametric_value_function_ex6` (`engine/src/players/value_functions.rs` 459-478).
- It runs only while the opponent's setup is masked (`setup_opponent_hidden`, `observation.rs` 48-53), that is at turn 0.
- It gets new `EvalFeatures` switches, off in every existing tier.
- The engine's setup path is not touched: what is offered (`move_generation/mod.rs` 30-42, 140-167), the setup handoff (`apply_action_helpers.rs` 47-80), and the setup mask and cutoff (`observation.rs` 48-53, 365-367).

**What it adds.** For the evaluating player's own Active only, read through the suppression-aware `get_in_play_ability_mechanic`:
- **Switch A, "first-turn Active-only Ability": +250.** Applies when the Active's mechanic is in the class "works only from the Active Spot and pays on its owner's first turn", *and* `get_highest_evolutions(&active.card, own deck + hand)` is non-empty.
  - Today that class is exactly `AbilityMechanic::CanEvolveOnFirstTurnIfActive` (`actions/abilities/mechanic.rs` 549). Its engine effect is `move_generation/mod.rs` 198-212.
  - Its text also covers "the turn you play it" (the engine lifts both timing rules, `mod.rs` 209-210). The class is defined by the first-turn half, the only one the opening placement can use.
  - Its printings are Eevee B1 184, P-B 011 and P-B 054.
- **Switch B, "Bench-working Ability": −250** (diagnostic code only under the recommended route). Applies when the Active's mechanic is in the class Bench-only (8 flag settings) or "acts on other Pokémon, the opponent or the owner's draws from anywhere in play" (44 flag settings).
  - The classes and every flag in them are in `README.md` section 3. `BadDreamsEndOfTurn` is in the second class (`hooks/core.rs` 618-631 reads every in-play holder).
- **Switch R, "setup readiness": −100 per Energy of the Active's cheapest own attack** (diagnostic code only). This is the flag-free reading of the Darkrai half, to be read beside B.

**The classes** live in one new players-side function, `opening_ability_class(&AbilityMechanic)`.
- It is an exhaustive `match` with **no wildcard arm**, so a new variant fails to compile until it is classified. It mirrors `census.py`'s `VARIANT_CLASS`, and field-dependent variants are resolved from their own fields: `require_active`, `NoRetreatCostCondition::YourFirstTurn`, `RandomEvolutionTrigger::EndOfOpponentTurnIfActive`, `AttackCostReductionScope`, `NoRetreatCostTarget`.
- It names no card. The mechanics are the engine's own flags (the kq precedent, `deals_damage_without_printing_it`).

**Weights.** Pre-set at 250, half the Active online-score weight of 500 (the kq precedent), and not tuned on any table. B3 fits them later if the feature survives.
- The census re-ran at other weights. Every opening prediction below holds for any A weight from 50 to about 460 and any B weight of 50 or more. Above about 460, Eevee starts beating Igglybuff's free attack in four-Basic hands. So the weight is not a hidden knob on this table.

**Nothing outside turn 0 changes.** Once the Active is placed, the bonus is constant across that player's remaining setup moves. So the only move that can differ from kp3's is the opening Active itself.

## 3. Codes

| code | switches | role |
|---|---|---|
| `koa<N>` | A | **the adoption candidate** under the recommended route |
| `kob<N>` | B | diagnostic, mixed rows only (section 6) |
| `kor<N>` | R | diagnostic, mixed rows only |
| `ko<N>` | A + B | the adoption candidate **only if** route 2 is chosen instead (section 7) |

- All of them are `kp<N>`'s public-pricing arm with the new value function. They are parsed before `k<N>`, as kp, kq and kd are (`players/mod.rs` 210-232). The names are free in main's `parse_player_code` as of this reading; the builder may rename them.
  - Parse `koa`, `kob` and `kor` before `ko`: an arm written like kp's (`strip_prefix("ko")`, then `Err` when the rest is not a number) placed first would reject `koa3`.
- Every table and row is played at depth 3.

## 4. Tests and identity checks, before any table

- **k3 and kp3** replay all 14,000 table games move for move from the new binary. This is the standard check for any pilot change.
- **With both switches off**, the new code path replays kp3 on the same games.
- **Unit tests** on constructed setup hands (Altaria list; A = `koa`, B = `kob`):

  | hand | koa | kob | kp3 |
  |---|---|---|---|
  | {Darkrai, Eevee} | Eevee | Eevee | Darkrai |
  | {Igglybuff, Eevee} | Igglybuff | Igglybuff | Igglybuff |
  | {Darkrai, Swablu} | Darkrai | Swablu | Darkrai |
  | {Swablu, Eevee} | Eevee | Swablu (tie to the later id) | Swablu |

  - Plus one hand with an Eevee and no Espeon anywhere in deck or hand: switch A must not fire.
  - Plus a test that every `EFFECT_ABILITY_MECHANIC_MAP` entry's class agrees with its printed condition phrases ("in the Active Spot", "on your Bench", "first turn"), with the one known exception, `CanEvolveIntoEeveeEvolution`, whose "first turn" is a prohibition.
- **The setup-only property, checked on the whole table.** In every table game where neither deck's opening Active differs from kp3's game on the same deal, the candidate's game must equal kp3's move for move.
  - Predicted changed-opening shares are in section 5.
  - Any game that differs with both openings unchanged means the change leaked past turn 0. That stops the reading.
- **Mixed-row identity.** With the candidate on a deck that carries no flagged Basic, that deck's 3,500 mixed games equal kp3 v kp3 game for game.
  - For `koa` that is every deck but Altaria.
  - For `kob`: Blaziken, Lucario, Sceptile, Suicune.
  - For `kor`: Blaziken, Lucario, Sceptile, Hydreigon.

## 5. Footprint, registered from the census

- **Definition.** A game is "changed" when its play differs from kp3's on the same deal at least once. Because only the opening Active can differ, this is exactly: either deck's opening Active changed.
- **Seeds.** The table's own deals: 72,000,000 + pairing × 10,000 + game, game < 500. Reused on purpose, as every table candidate has; the mixed rows use the same deals. No new seed block.

| code | expected share of the 14,000 table games | per deck (share of that deck's openings changed) |
|---|---:|---|
| `koa` | **6.0%** (840; 95% sampling range about 790 to 890) | Altaria 24.0% (Darkrai → Eevee 14.5, Swablu → Eevee 9.5); every other deck 0 |
| `kob` | 14.6% | Altaria 24.0% (Darkrai → Swablu 14.5, Darkrai → Eevee 9.5); Hydreigon 13.3% (Bombirdier → Deino 9.7, → Mega Absol ex 3.6); Vespiquen 16.2% (Teal Mask Ogerpon ex → Shuckle ex 9.7, → Combee 6.6); Weezing 6.6% (Darkrai ex → Team Rocket's Koffing) |
| `kor` | 17.1% | as `kob` on Altaria, Vespiquen and Weezing. Hydreigon 0. Suicune 24.2% (Suicune ex → Chien-Pao ex 9.7, → Frigibax 14.5: P-B 037 8.0, B2a 034 6.6) |
| `ko` | 16.8% | Altaria 33.5% (Darkrai → Eevee 14.5, Darkrai → Swablu 9.5, Swablu → Eevee 9.5), plus `kob`'s other three decks |

**Outside the table** (reported, not read by the rule; `census.json` has every list):
- **Switch A:** Dustin's deck 15 only (Oricorio → Eevee, 9.7%).
- **Switch B:** decks 05, 08, 12 and 14; brews 03a, 03b, 05b, 06, 06b and 07; and the B2e list h-hoopa_absol (3.6%).
- **The B2e held-out rows.** No held-out list carries a switch-A flag. So under `koa` a held-out deck's row moves only through its games against Altaria, at most 1/8 of Altaria's cell change.
- **The proposed ladder panel** (`decks/screen/panel_ladder_2026-09-26/`): its eight lists are the table lists card for card, and its two added lists (`l-charizardy.txt`, `l-sharpedo.txt`) carry no A or B flag and no switch changes their opening. So the screen moves under `koa` only through games against Altaria.

## 6. Predictions: which decks move, and which way

**`koa`, the adoption candidate.**
- **Altaria's own side rises.**
  - **Against Lucario, +5.5 points per game.** This is B2c's play-out values weighted by the census's transition shares; ±1.4 from the play-outs alone, and roughly +1 to +10 once the 500-game cell's own noise is added.
  - **Against the other six decks: up, size not predicted.** B2c played out only Altaria v Lucario.
  - **Pooled over its 7 mixed rows: above zero beyond paired noise.**
- **Every other deck's own side is exactly unchanged** (identity, section 4). Altaria's opponents' table scores move only by Altaria's change in that cell.
- **Scoreboard v2 (27-cell decision set; Altaria v Sceptile quarantined).**
  - Altaria is underrated in 4 of its 6 decision cells. The misses, kp3 minus Limitless: Blaziken −17.9, Lucario −10.0, Suicune −7.4, Hydreigon −6.9.
  - It is overrated in the other 2: Vespiquen +9.8, Weezing +7.4.
  - A uniform rise of 3 to 7 points moves the raw mean squared miss by only about −2 to −4 points². Too small for the ordinary rule to decide at 500 or 2,000 deals, which is why route 1 is recommended.
  - Under rule v2 the Vespiquen and Weezing cells may grow. Such a growth is not a veto that counts, because Altaria's own side is better, not worse. It is an investigation item.
- **Sentinels.**
  - Altaria v Hydreigon moves, predicted toward Limitless (kp3 47.6, Limitless 54.5 ± 13.0).
  - Blaziken v Weezing and Suicune v Weezing are exactly unchanged.

**`kob` and `kor`, the diagnostics.**
- **Altaria.** Both predict the same openings, so the same gain against Lucario: +5.3 from B2c.
- **Hydreigon** (`kob` only), **Vespiquen and Weezing** (both), **Suicune** (`kor` only).
  - No evidence either way. The footprint caps each own-side change at about its changed share × 15 points per changed game: Weezing ±1.0, Hydreigon ±2.0, Vespiquen ±2.4, Suicune ±3.6.
  - The attribution question is whether Hydreigon moves under `kob` and Suicune under `kor`, since elsewhere the two diagnostics make the same changes.

**`ko`, only if route 2 is chosen.**
- Altaria against Lucario +7.2 (±1.6 from the play-outs).
- The rest as `koa` plus `kob`'s three decks.
- Raw ΔMSE small, as above: **"undecided" is the most likely reading.**

## 7. The reading

**Route 1, recommended: the reserve route, for `koa`.** This applies only if Dustin has approved the reserve route. Section 8 of `docs/REVIEW_2026-09-24_direction.md` still marks it "pending Dustin's OK"; if it is not approved, route 2 applies. The five clauses as written there:
- **(a) Footprint under 15%.**
  - Predicted 6.0%, measured on the table. Section 8's assumption that this candidate's footprint is above the trigger ("the choice is made in every game") is corrected by the census. The opening changes only in hands where a flagged Basic sits beside another Basic.
- **(b) No harm.**
  - The τ̂ margin (kp3 minus `koa`) must have a 90% interval lower bound of −1.0 or above.
  - No veto may count under rule v2.
- **(c) In the 28-pairing mixed rows, no deck's own side worse beyond paired noise.**
  - Structurally only Altaria's own side can move; section 4 checks the rest as identities.
- **(d) A gain beyond paired noise on the new bot's own side (Altaria's 7 mixed rows pooled), and on a Limitless top-30 archetype that is not Dustin's and carries the relevant cards.**
  - The archetype is **Mega Altaria ex Espeon**: Sept 10 rank 2, not Dustin's by the kt census's rule; the table's Altaria list is its representative.
  - **To do before registering.** Count the share of its development-half Limitless lists that carry a flagged printing (Eevee B1 184, P-B 011 or P-B 054), as the kt census did for its cards. This census did not open the Limitless files.
    - A pointer, not the count: the two archetype variant lists on file (`decks/variants-2026-09-23/`, Aug 29 and Sept 10) both carry 2 Eevee B1 184.
  - The closure sentence applies unchanged. If no such archetype carries the card, or it has no usable list, the route is closed and adoption needs Dustin's explicit override.
- **(e) Adoption for the screen and the table pilot together.**
- **Confirmation:** on events after the freeze date. The holdout was spent on Sept 25.

**Route 2: the ordinary rule, for `ko` (A + B).**
- The footprint is 16.8%, over the trigger.
- The rule: paired ΔMSE on the 27-cell decision set, whole 95% interval below zero, vetoes under rule v2. When undecided, deals double to 2,000.
- Section 6 predicts it will most likely stay undecided even at 2,000. That is recorded here, before any table, so that an "undecided" reading is not read later as evidence against the feature.

**Under either route, reported and not decided on:**
- Correlation, favorites right, real error τ̂ for kp3 and the candidate.
- The footprint against section 5.
- The per-deck opening transitions.
- **A per-game counter the table files must carry:** each seat's opening Active under the code played, so the transitions can be read from the files without replays.

**The diagnostics `kob` and `kor`** run as mixed rows only (the candidate on one deck, kp3 on the other; both directions).
- They cover the decks each one changes, plus their identity decks as checks.
- Neither is an adoption candidate under this registration. If the Darkrai half proves real, it is registered separately.

## 8. What would refute it

- **A leak.** Any identity in section 4 fails, including a changed game with both openings unchanged. Stop, and fix before reading anything.
- **The census's model of kp3's setup choice is wrong.** For example:
  - Altaria's changed-opening share under `koa` falls outside 22.6 to 25.4% of its 3,500 games;
  - a transition not in section 5 appears;
  - another deck's opening changes.

  Then the predictions above do not hold, and the reading stops for a re-read.
- **The B2c result does not carry to the rule.** `koa` on Altaria alone, pooled over its 7 mixed rows, shows Altaria's own side at or below zero beyond paired noise. Or Altaria v Lucario's mixed row lands below zero beyond its noise (predicted +5.5).
  - Either way, switch A does not capture what the network did. It is not adopted, and the finding goes to B3 unchanged.
- **Not a refutation, stated in advance:**
  - A table ΔMSE that is undecided (predicted).
  - `kob` and `kor` making the same Altaria change (predicted). This leaves the Darkrai half unnamed, which is a reason to register nothing more yet.

## 9. Known limits (kept as registered)

- **Only one matchup has values.** Play-out values exist for Altaria v Lucario only. The other cells' signs are expected, not measured.
- **The Hydreigon network's openings are unread.** Its records hold only move numbers. A replay-only pass (no probes, no play-outs) can name them before the table if Fable wants it; this registration doesn't depend on it.
- **Who goes first isn't used.** It isn't a field of the setup observation, and the opponent's hand count during setup (`observation.rs` 56) is not to be read by any term. B2c shows the gain is the same either way.
- **Weakness to the opponent can't be used.** The opponent's board is masked at setup and kp3 has no list.
- **Other Active-only Abilities are left out** (switch C in the census: Caterpie's Quick Growth, Legendary Pulse, Innards Out). Nothing measured supports them, and they would add Sceptile and brews 06/06b to the footprint.
- **Drawback Abilities are left out** (Regigigas's Seal of Antiquity, opened by kp3 in 16% of deck 01's deals). Reported only.
- **An engine rules question, tier 1 and separate.** On-Bench-entry triggers fire for setup placements (`apply_action.rs` 1111-1120). No list in scope carries one.

## 10. Sources

- `README.md` (this folder): the setup code path with file and line, the flag classes, the census table, the network-study checks and the design options.
- `census.json`: per list, the Basics and their flags, the choice and opening shares, and the transitions for A, B, A+B, C, D, R and A+R. Also `table_footprint`, `b2c_expected_altaria_v_lucario` and `validation`.
- `check_census.py` and its outputs: the independent re-derivation.
- `../altaria_network_divergence_2026-09-26/RESULT.md` and `opening_choice.txt`: the B2c values.
- `../table_readings_2026-09-24/kpr3_paired_reading.md`: kp3's scoreboard v2 cells used in section 6.

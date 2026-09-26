# DRAFT, not registered. B5 candidate "opening Active choice": switch A alone (`koa`), with diagnostics `kob` and `kor`

**Status.** This draft was written by the laptop session's census (Sept 26) and amended the same day to Fable's call (section 8 of `docs/REVIEW_2026-09-24_direction.md`, 05:30 entry). It stays unregistered until Fable's independent review and Dustin's word; then the cloud or the laptop registers it.
- It becomes a registration only when the builder copies it into a dated commit, with any amendments and the reason for each, before any game of any code named here.
- **Fable's call (Sept 26), for Dustin to confirm:**
  - Switch A alone, code `koa`, is the one candidate. It goes by the reserve route, because its footprint (6.0%) is under the 15% trigger.
  - The clause (d) carrier archetype is Mega Altaria ex Espeon (top-30 rank 2, not Dustin's).
  - Switches B and R stay diagnostics (`kob` and `kor` mixed rows, side by side). They are not registered for adoption.
- **Needed before registering:**
  - Fable's independent review (three lenses plus adversarial checks; section 8 records it as running). The code lens is written, against the first draft (`../fable_reviews_2026-09-26/opening_active_review_code.md`); its findings are not applied here.
  - Dustin's OK for the reserve route itself. Section 8 of `docs/REVIEW_2026-09-24_direction.md` still marks it "pending Dustin's OK".
  - Dustin's panel-deck ruling for clause (d) (section 7). One ruling covers both this candidate and kt.
- **Where the numbers come from.** Every number below is from `README.md`, `census.json` and `limitless_carriers.md` / `.json` in this folder. No game was played to make any of them.
  - census.py was checked by check_census.py and by a second read the same day. That read (README section 9) corrected the Suicune `kor` transition in section 5.
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

**Base.** kp3 at the official engine's commit (7fc6ccb, `rl/engine-2026-09-25/`) or current main, as the builder states. It changes players' code only: **tier 2**.

**Where.** The setup branch of `parametric_value_function_ex6` (`engine/src/players/value_functions.rs` 459-478).
- It runs only while the opponent's setup is masked (`setup_opponent_hidden`, `observation.rs` 48-53), that is at turn 0.
- It gets new `EvalFeatures` switches, off in every existing tier.
- The engine's setup path is not touched:
  - what is offered (`move_generation/mod.rs` 30-42, 140-167);
  - the setup handoff (`apply_action_helpers.rs` 47-80);
  - the setup mask and cutoff (`observation.rs` 48-53, 365-367).

**What it adds.** For the evaluating player's own Active only, read through the suppression-aware `get_in_play_ability_mechanic`:
- **Switch A, "first-turn Active-only Ability": +250.** It applies when both hold:
  - the Active's mechanic is in the class "works only from the Active Spot and pays on its owner's first turn";
  - `get_highest_evolutions(&active.card, own deck + hand)` is non-empty.

  Details:
  - Today that class is exactly `AbilityMechanic::CanEvolveOnFirstTurnIfActive` (`actions/abilities/mechanic.rs` 549). Its engine effect is `move_generation/mod.rs` 198-212.
  - Its text also covers "the turn you play it" (the engine lifts both timing rules, `mod.rs` 209-210). The class is defined by the first-turn half, the only one the opening placement can use.
  - Its printings are Eevee B1 184, P-B 011 and P-B 054.
- **Switch B, "Bench-working Ability": −250.** Diagnostic code only; not registered. It applies when the Active's mechanic is in one of two classes:
  - Bench-only (8 flag settings);
  - "acts on other Pokémon, the opponent or the owner's draws from anywhere in play" (44 flag settings).

  The classes and every flag in them are in `README.md` section 3. `BadDreamsEndOfTurn` is in the second class (`hooks/core.rs` 618-631 reads every in-play holder).
- **Switch R, "setup readiness": −100 per Energy of the Active's cheapest own attack.** Diagnostic code only; not registered. It is the flag-free reading of the Darkrai half, to be read beside B.

**The classes** live in one new players-side function, `opening_ability_class(&AbilityMechanic)`.
- It is an exhaustive `match` with **no wildcard arm**, so a new variant fails to compile until it is classified.
- It mirrors `census.py`'s `VARIANT_CLASS`. Field-dependent variants are resolved from their own fields: `require_active`, `NoRetreatCostCondition::YourFirstTurn`, `RandomEvolutionTrigger::EndOfOpponentTurnIfActive`, `AttackCostReductionScope`, `NoRetreatCostTarget`.
- It names no card. The mechanics are the engine's own flags (the kq precedent, `deals_damage_without_printing_it`).

**Weights.** Pre-set at 250, half the Active online-score weight of 500 (the kq precedent), and not tuned on any table. B3 fits them later if the feature survives.
- The census re-ran at other weights. Every opening prediction below holds for any A weight from 50 to about 460 and any B weight of 50 or more.
- Above about 460, Eevee starts beating Igglybuff's free attack in four-Basic hands. So the weight is not a hidden knob on this table.

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

- **k3 and kp3** replay all 14,000 table games move for move from the new binary. This is the standard check for any pilot change.
- **With every switch off**, the new code path replays kp3 on the same games.
- **Unit tests** on constructed setup hands (Altaria list; A = `koa`, B = `kob`):

  | hand | koa | kob | kp3 |
  |---|---|---|---|
  | {Darkrai, Eevee} | Eevee | Eevee | Darkrai |
  | {Igglybuff, Eevee} | Igglybuff | Igglybuff | Igglybuff |
  | {Darkrai, Swablu} | Darkrai | Swablu | Darkrai |
  | {Swablu, Eevee} | Eevee | Swablu (tie to the later id) | Swablu |

  - Plus one hand with an Eevee and no Espeon anywhere in deck or hand: switch A must not fire.
  - Plus a test that every `EFFECT_ABILITY_MECHANIC_MAP` entry's class agrees with its printed condition phrases ("in the Active Spot", "on your Bench", "first turn"). The one known exception is `CanEvolveIntoEeveeEvolution`, whose "first turn" is a prohibition.
- **The setup-only property, checked on the whole table.** In every table game where neither deck's opening Active differs from kp3's game on the same deal, the candidate's game must equal kp3's move for move.
  - Predicted changed-opening shares are in section 5.
  - Any game that differs with both openings unchanged means the change leaked past turn 0. That stops the reading.
- **Mixed-row identity.** With the code on a deck that carries no flagged Basic, that deck's 3,500 mixed games equal kp3 v kp3 game for game.
  - For `koa` that is every deck but Altaria.
  - For `kob`: Blaziken, Lucario, Sceptile, Suicune.
  - For `kor`: Blaziken, Lucario, Sceptile, Hydreigon.

## 5. Footprint, registered from the census

- **Definition.** A game is "changed" when its play differs from kp3's on the same deal at least once. Because only the opening Active can differ, this is exactly: either deck's opening Active changed.
- **Seeds.** The table's own deals: 72,000,000 + pairing × 10,000 + game, game < 500. They are reused on purpose, as for every table candidate, and the mixed rows use the same deals. No new seed block.

| code | expected share of the 14,000 table games | per deck (share of that deck's openings changed) |
|---|---:|---|
| `koa` | **6.0%** (840; 95% sampling range about 790 to 890) | Altaria 24.0% (Darkrai → Eevee 14.5, Swablu → Eevee 9.5); every other deck 0 |
| `kob` | 14.6% | Altaria 24.0% (Darkrai → Swablu 14.5, Darkrai → Eevee 9.5); Hydreigon 13.3% (Bombirdier → Deino 9.7, → Mega Absol ex 3.6); Vespiquen 16.2% (Teal Mask Ogerpon ex → Shuckle ex 9.7, → Combee 6.6); Weezing 6.6% (Darkrai ex → Team Rocket's Koffing) |
| `kor` | 17.1% | as `kob` on Altaria, Vespiquen and Weezing. Hydreigon 0. Suicune 24.2% (Suicune ex → Chien-Pao ex 9.7, → Frigibax 14.5: P-B 037 8.0, B2a 034 6.6) |
| A + B (reference only, not a code here) | 16.8% | Altaria 33.5% (Darkrai → Eevee 14.5, Darkrai → Swablu 9.5, Swablu → Eevee 9.5), plus `kob`'s other three decks |

A goes alone by Fable's call: B is unattributed (B2c can't tell it from R), and bundling it with A would repeat the kd lesson. The A + B row also shows the pair over the 15% trigger, where A alone is well under it.

**Outside the table** (reported, not read by the rule; `census.json` has every list):
- **Dustin's decks and brews:** the written predictions are in section 6.
- **The B2e held-out rows.** No held-out list carries a switch-A flag. So under `koa` a held-out deck's row moves only through its games against Altaria, at most 1/8 of Altaria's cell change. Under `kob`, h-hoopa_absol's own opening changes in 3.6% of deals (section 6).
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
  - A uniform rise of 3 to 7 points moves the raw mean squared miss by only about −2 to −4 points². That is too small for the ordinary rule to decide at 500 or 2,000 deals, which is why `koa` goes by the reserve route.
  - Under rule v2 the Vespiquen and Weezing misses may grow. Such a growth is not a veto that counts, because Altaria's own side is better, not worse. It is an investigation item.
- **Sentinels.**
  - Altaria v Hydreigon moves, predicted toward Limitless (kp3 47.6, Limitless 54.5 ± 13.0).
  - Blaziken v Weezing and Suicune v Weezing are exactly unchanged.

**`kob` and `kor`, the diagnostics.**
- **Altaria.** Both predict the same openings, so the same gain against Lucario: +5.3 from B2c.
- **Hydreigon** (`kob` only), **Vespiquen and Weezing** (both), **Suicune** (`kor` only).
  - No evidence either way. The footprint caps each own-side change at about its changed share × 15 points per changed game: Weezing ±1.0, Hydreigon ±2.0, Vespiquen ±2.4, Suicune ±3.6.
  - The attribution question is whether Hydreigon moves under `kob` and Suicune under `kor`, since elsewhere the two diagnostics make the same changes.

**Written predictions for Dustin's decks and brews** (`census.json`, share of all deals whose opening changes; weights 250).
- **Under `koa` (switch A): deck 15 only.**
  - 15 Jolteon Oricorio Raticate: 9.7% (Oricorio → Eevee).
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

**Route: the reserve route, for `koa`.** Its predicted footprint is 6.0%, under the 15% trigger. The route applies once Dustin has approved it; section 8 of `docs/REVIEW_2026-09-24_direction.md` still marks it "pending Dustin's OK". The five clauses are as fixed there (line 130), applied to `koa`:

- **(a) Footprint under 15%.**
  - Predicted 6.0%, measured on the table (section 5).
  - The census corrects section 8's assumption that this candidate's footprint is above the trigger ("the choice is made in every game"). The opening changes only in hands where a flagged Basic sits beside another Basic.
- **(b) No harm.**
  - On the table, the τ̂ margin (kp3 minus `koa`) must have a 90% interval lower bound of −1.0 or above.
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
  - **Dustin's ruling, once for both candidates: may a panel deck serve as the (d) archetype?**
    - The kt carrier census raised the same question for Suicune (kt switch 1; `../kt_carrier_census_2026-09-26/README.md`, section 7). One ruling covers kt's Suicune and this candidate's Altaria.
    - **If a panel deck may not serve:** the only top-30 carrier off the panel is Mega Altaria ex Igglybuff (Sept 10 rank 29; window rank 34). It carries the card in 4 of 25 lists (16%), one copy each, with no top-8 finish, and no list was built for it. Whether that occasional share "carries the relevant cards" is the same open reading as Suicune's 11% and Vespiquen's 1.7% in the kt census. No other top-30 archetype carries the card.
    - **A fact for the ruling, with no position taken:** Eevee B1 184 is also in Dustin's deck 15. The archetype is still not his by the kt rule, which reads the archetype's named Pokémon.
  - **The closure sentence, verbatim from section 8 (line 130):**

    > Stated up front, before any census is read: if the card census finds no Limitless top-30 archetype outside Dustin's decks that carries reduction Tools or turn-effect cards, or finds one with no usable decklist, the route is closed for that candidate and adoption can come only by Dustin's explicit override, recorded as such, as with kp3; the route is not loosened after the census is seen.

    - Its card words are kt's. For this candidate the relevant cards are switch A's printings (Eevee B1 184, P-B 011, P-B 054).
    - If Dustin rules that a panel deck may serve, the count found such an archetype (Mega Altaria ex Espeon, with usable lists in numbers), and the sentence does not close the route.
    - If he rules that it may not, the sentence turns on the Igglybuff reading above. If that 16% share does not count either, the route is closed for `koa` and the sentence applies as written.
- **(e) As in section 8:** "On that evidence, adoption for the screen and the table pilot together, so there is only ever one pilot."
- **Confirmation:** on events after the freeze date. The holdout was spent on Sept 25.

**If Dustin does not approve the reserve route,** the ordinary rule is the only route left for `koa`:
- paired ΔMSE on the 27-cell decision set, with the whole 95% interval below zero;
- vetoes under rule v2;
- when undecided, deals double to 2,000.

Section 6 predicts it will most likely stay undecided even at 2,000. That is recorded here, before any table, so that an "undecided" reading is not read later as evidence against the feature.

**Under either route, reported and not decided on:**
- Correlation, favorites right, real error τ̂ for kp3 and `koa`.
- The footprint against section 5.
- The per-deck opening transitions.
- **A per-game counter the table files must carry:** each seat's opening Active under the code played, so the transitions can be read from the files without replays.

**B and R: the diagnostics `kob` and `kor`.**
- **Mixed rows only, side by side.** Each diagnostic plays one deck with kp3 on the other, both directions, on the same deals as `koa`'s rows.
  - They cover the decks each one changes: `kob` Altaria, Hydreigon, Vespiquen, Weezing; `kor` Altaria, Suicune, Vespiquen, Weezing.
  - Their identity decks (section 4) are played as checks.
- **They are run before either switch is ever registered, and they are for attribution, not adoption.** They name the Darkrai half: Hydreigon moving under `kob`, or Suicune moving under `kor`.
- Neither is an adoption candidate under this registration. If the Darkrai half proves real, it gets its own registration.

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
- **Who goes first isn't used.** It isn't a field of the setup observation, and no term may read the opponent's hand count during setup (`observation.rs` 56). B2c shows the gain is the same either way.
- **Weakness to the opponent can't be used.** The opponent's board is masked at setup and kp3 has no list.
- **Other Active-only Abilities are left out** (switch C in the census: Caterpie's Quick Growth, Legendary Pulse, Innards Out). Nothing measured supports them, and they would add Sceptile and brews 06/06b to the footprint.
- **Drawback Abilities are left out** (Regigigas's Seal of Antiquity, which kp3 opens in 16% of deck 01's deals). Reported only.
- **The carrier count is development half only** (`limitless_carriers.md`, section 2).
- **An engine rules question, tier 1 and separate.** On-Bench-entry triggers fire for setup placements (`apply_action.rs` 1111-1120). No list in scope carries one.

## 10. Sources

- `README.md` (this folder): the setup code path with file and line, the flag classes, the census table, the network-study checks (including the first-turn-evolution split, section 5) and the design options.
- `census.json`: per list, the Basics and their flags, the choice and opening shares, and the transitions for A, B, A+B, C, D, R and A+R. Also `table_footprint`, `b2c_expected_altaria_v_lucario` and `validation`.
- `check_census.py` and its outputs: the independent re-derivation.
- `limitless_carriers.md` and `limitless_carriers.json` (this folder): the clause (d) carrier count by Altaria variant, every archetype that carries the flag, the independent recount, and Altaria's seven "before" cells.
- `docs/REVIEW_2026-09-24_direction.md`, section 8, line 130: the reserve route's clauses and the closure sentence.
- `../kt_carrier_census_2026-09-26/README.md`: the Dustin rule, the ranks and the panel-deck question for Suicune.
- `../altaria_network_divergence_2026-09-26/RESULT.md` and `opening_choice.txt`: the B2c values.
- `../table_readings_2026-09-24/kpr3_paired_reading.md`: kp3's cells used in sections 6 and 7.
- `../scoreboard_v2_2026-09-25/limitless_v2_dev.json`: the Limitless v2 cells.

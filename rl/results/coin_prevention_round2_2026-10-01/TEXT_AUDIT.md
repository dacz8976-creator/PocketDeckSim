Decision this informs: which gated or "not seen" cases the next rules switch fixes on the card text, and which stay open as shot-list rows. Set by the Fable coordinator via Dustin, Oct 1 evening (the card-text job, item 2). Read-only: written and committed before any code after item 1.

Seeds: none. Nothing was played; this is a reading of card texts (`python3 lib/card.py`) and code.

# Card-text audit of the gated and "not seen" cases

## The rule (Dustin, Oct 1)

"Plain card text is the rule. A simulator path that contradicts it is a bug, not an open question; nothing waits on a recording to confirm what a card says. Recordings are only for what no card text decides (ordering, timing, promotion order, UI-only behaviour)." (the coordinator's wording of Dustin's rule)

## What was read

- `rules/09_engine_repairs_2026-09-22.md` and `rules/04_actions_cards_effects.md` (the same blobs on main, on R and on this branch).
- `engine/src/card_validation.rs`, `implementation_limitations` (R's version, which this branch carries).
- The two coin-prevention READMEs' open items, and the recordings readout on main 24ef210 (`rl/results/rules_recordings_2026-10-01/READOUT.md`).
- Code line numbers are this branch's head, `27a0c37` (item 1's fix), unless named.

## In plain words

- **Decided by the card text, and the engine contradicts it: 9 cases.** Each is a bug.
  - **Fixed already (1):** item 1, Will with a Confused attacker (A3): `59c7c2a` tests, `27a0c37` fix.
  - **Fixable in the five allowed files (4), to be fixed next, tests first:**
    1. Victory Star with a block coin (Smokescreen and the like): the attack's own coins must get the offer after the block coin's heads (A1).
    2. Will with a block coin: Will must go to the block coin (A2).
    3. The coin Abilities on the attacker's own Pokémon, hit by its own attack: the own-Bench choice (Zapdos, Emolga, Luxray), the own-Pokémon choice (Mimikyu's Shadow Hit) and the own-Bench spreads (Earthquake and the like). The opponent's Active in the own-Bench choice skips its coin too (A4).
    4. A copied discard attack (Chase Order through Ditto's Copy Anything; Wild Swing through either Ditto) skips the coin (A5).
  - **Need a file outside the five (2); not touched, asked in CLOUD_STATUS.md:**
    5. Luxury Coin used on the opponent's Stadium (`trainer_coin_plan.rs`) (A6b).
    6. A Fossil played under an Item lock (`move_generation_trainer.rs`) (D, §6).
  - **Found while reading, outside the three sources (2); listed, not fixed:** Guts on the attacker's own Pokémon, and Perish Body on a plain queued hit (E1, E2). Both are in the five files; asked.
  - Also out of date: Victini's caveat text in `card_validation.rs` (A3), after item 1 and A1. A sixth file: asked.
- **Decided by the text, and the engine already follows it: 7 cases.** No change.
- **Not decided by any card text: 17 cases.** They stay open, each as a shot-list row with what to record.
- **Not rules questions at all: 4** (engine bookkeeping or hidden information no recording can see).

---

## A. The engine's gated cases (card_validation.rs's caveats and the coin rounds' open items)

### A1. Victory Star with CoinFlipToBlockAttack — DECIDED BY TEXT (a bug)

- **Texts:**
  - Victini (B3 025, P-B 049), Victory Star: "Once during your turn, after you flip any coins for an attack of 1 of your [R] Pokémon, you may ignore all results of those coin flips and begin flipping those coins again. You can't use more than 1 Victory Star Ability each turn."
  - The block coin, 8 attacks (Weezing A1a 050 Smokescreen, Manectric A2a 028 Flash, Magmortar A2b 012 Smoke Bomb, Sandygast B1 143 Sand Attack, Magnezone B1a 026 Mirror Shot, Skuntank B2 102 Smokescreen Shot, Sandaconda B3 096 Super Sand Attack): "During your opponent's next turn, if the Defending Pokémon tries to use an attack, your opponent flips a coin. If tails, that attack doesn't happen." Octillery (A4 056, A4 169) Octazooka: the same, "This effect lasts until the Defending Pokémon leaves the Active Spot, and it doesn't stack."
- **What the text decides:**
  - The block coin comes first: it is flipped when the Pokémon "tries to use an attack", and on tails the attack "doesn't happen".
  - On heads the attack happens, and its own coins are "coins for an attack of 1 of your [R] Pokémon". So Victory Star is offered on them.
  - The block coin itself is not offered. It is flipped for the effect of the opponent's attack (Smokescreen's text), not for your [R] Pokémon's attack. This is the plain reading of "for an attack of 1 of your [R] Pokémon"; the Confusion coin has the same shape and the game does not offer it either (202314, 203025, 210403).
  - So the case is the Confusion case's order: block coin first, never rerolled; on heads, the offer on the attack's own coins; no second block coin.
- **The engine:** no offer at all. `try_forecast_victory_star_attack` (`apply_action.rs` 185) returns `None` when `has_unverified_attacker_coin_gate` (`apply_attack_action.rs` 96) sees the block effect, and `victory_star_waits_for_confusion_heads` (119) excludes it. Pinned by `coin_flip_to_block_attack_keeps_its_resolution_without_a_victory_star_offer` and `coin_flip_to_block_attack_result_is_the_old_paths` (`b4a_attack_batch2_test.rs`).
- **Fix:** the Confusion-first path, generalised to the block coin (and to both coins when the attacker is also Confused). Files: `apply_action.rs`, `apply_attack_action.rs`. In the five.
- **What stays open (ordering, not text):** with a Confused attacker that also carries the block effect, which of the two coins comes first. It changes nothing visible: either tails stops the attack, neither is offered, and Will takes the block coin either way (A2). No row needed.
- If Dustin reads "for an attack of 1 of your [R] Pokémon" as including the block coin, only the last sub-point changes; the shot row `victory-star-block-coin` would then be the check.

### A2. Will with CoinFlipToBlockAttack — DECIDED BY TEXT (a bug; found while reading A1)

- **Texts:** Will (A4 156, A4 196): "The next time you flip any number of coins for the effect of an attack, Ability, or Trainer card after using this card on this turn, the first coin flip will definitely be heads." The block coin: as A1 ("your opponent flips a coin": the attacking player flips it).
- **What the text decides:** the block coin is flipped by you, for the effect of an attack (the opponent's Smokescreen). It is the next such coin, so Will makes it heads: the attack happens. Will is then used up, and the attack's own coins are flipped fairly. (Contrast item 1: the Confusion coin is flipped for a Special Condition, not for the effect of an attack, so Will waits for the attack's coins.)
- **The engine:** the block gate drops the coin record (`prepend_nullifying_coin_gate`, `attack_outcome.rs` 590), so `finish_forecast` (`apply_action.rs` 670) finds no coin. The block coin is fair, the attack's coins are fair, and Will lapses unused.
- **Fix:** with Will pending and the block effect, the block coin is heads and Will is used there. With Victory Star (A1) the attack's own batch is then staged unforced. Files: `apply_attack_action.rs`, `attack_outcome.rs`, `apply_action.rs`. In the five.

### A3. Victory Star and Will with a Confused attacker — DECIDED BY TEXT (fixed in item 1)

- **Texts:** Will and Victory Star as above. The Confusion coin is not a card's text: it is the Special Condition's check (rules/04 §9).
- **What the text decides:** Will's coins are "for the effect of an attack, Ability, or Trainer card"; the Confusion check is none of those, so Will goes to the attack's first coin after a Confusion heads, and Victory Star is still offered on the attack's coins. The game agrees (210403, T14, 342-355 s).
- **Done:** `59c7c2a` (the two tests, failing), `27a0c37` (the fix).
- **Left:** Victini's caveat in `card_validation.rs` (96-98) still calls this case "unverified ... left on the legacy resolution", and calls A1 the same. It is a sixth file: asked in CLOUD_STATUS.md.

### A4. The own-Bench form of `also_choice_bench_damage`, and every hit on the attacker's own Pokémon — DECIDED BY TEXT (a bug)

- **Texts:**
  - The four coin Abilities: Meowth (B2 124, B2 204) Carefree Steps and Togekiss (A4 080) Celestial Blessing: "If any damage is done to this Pokémon by attacks, flip a coin. If heads, prevent that damage." Bastiodon (A2 114) Guarded Grill: "... If heads, this Pokémon takes -100 damage from that attack." Hisuian Goodra (B3b 050) Securely Sheltered: "... If heads, this Pokémon takes -80 damage from that attack."
  - The own-Bench choice: Zapdos (A1 103, B1 302) Raging Thunder: "This attack also does 30 damage to 1 of your Benched Pokémon." Emolga (A4 072) Raging Thunder: "... 10 damage to 1 of your Benched Pokémon." Luxray (B1 088, B1 237, P-B 004) Flash Impact: "... 20 damage to 1 of your Benched Pokémon."
  - The own-Pokémon choice: Mimikyu (A3 083, P-A 066) Shadow Hit: "This attack also does 20 damage to 1 of your Pokémon."
  - The own-Bench spreads: Earthquake, "This attack also does 10 damage to each of your Benched Pokémon" (Whiscash A3b 039, Diggersby B2 140, Groudon B4 083) and 20 (Mamoswine A4 098); Great Tusk (B3a 034) Shaking Stomp and Team Rocket's Articuno ex (B4a 014, 080, 089) Hailstorm: "... 20 damage to each of your Benched Pokémon"; Forretress (B2b 046, B2b 104) Enormous Explosion: "This Pokémon also does 100 damage to itself and 50 damage to all Benched Pokémon (both yours and your opponent's)."
- **What the text decides:** "any damage ... by attacks" has no "your opponent's". Damage from your own attack to your own Meowth, Togekiss, Bastiodon or Goodra flips its coin like any other. The opponent's Active hit in the same choice flips too, as every other attack does.
- **The engine:**
  - The own-Bench choice is queued as a plain `ApplyDamage` (`also_choice_bench_damage`, `apply_attack_action.rs` 2854; the comment at 2883 keeps it for its Guts handling), and the later round's gate leaves it alone because it also hits the attacker's Bench (`coin_gated_choice`, 346). So neither the Benched coin Pokémon nor the opponent's Active coin Pokémon flips.
  - Shadow Hit's choice is a plain `ApplyDamage` at your own Pokémon (`also_choice_own_pokemon_damage`, 6413): no coin.
  - The spreads carry the damage in the attack's outcome (`also_bench_damage`, 4365), but the coin split covers only the opponent's Pokémon (`apply_defender_damage_prevention_if_needed`, 241; `split_with_damage_prevention`, `attack_outcome.rs` 681).
  - No coin-Ability Pokémon has a recoil attack, so the attacker's own recoil never meets one.
- **Fix:** the coin split for the attacker's own Pokémon in the outcome (`attack_outcome.rs`, `apply_attack_action.rs`), and the coin for any target of an attack's queued `ApplyDamage` (`forecast_apply_damage`, `apply_action.rs` 769, which already flips Guts there for both sides). In the five.
- Dustin had ruled this form "unchanged" in the coin rounds; his Oct 1 rule supersedes that.

### A5. A copied Chase Order's discard branch (and a copied Wild Swing) — DECIDED BY TEXT (a bug)

- **Texts:**
  - Vespiquen ex (B4 011, B4 180, B4 194) Chase Order: "You may discard 1 of your Benched Basic [G] Pokémon. If you do, this attack does 70 more damage."
  - Gyarados (A4 045, A4 215) Wild Swing: "You may discard any number of your Benched [W] Pokémon. This attack does 40 more damage for each Benched Pokémon you discarded in this way."
  - The copiers: Ditto (A1 205, A1 247) Copy Anything: "Choose 1 of your opponent's Pokémon's attacks and use it as this attack. ..." Ditto (B1a 055, B3b 099, P-B 012) Copy a Friend: "Choose 1 of your Benched Pokémon's attacks, except any Pokémon ex, and use it as this attack. ..." Mew ex Genome Hacking, Mimikyu (A3b 035, P-A 113) Try to Imitate and Clefairy (B4 064, B4 166) Mini-Metronome copy the opponent's Active's attacks.
  - The coin Abilities: as A4.
- **What the text decides:** the copy is "this attack", so its damage is damage by an attack and the coin flips.
- **Where it can happen:** Copy Anything copies a Benched Vespiquen ex's Chase Order while the opponent's Active is a coin Pokémon; either Ditto copies a Wild Swing (Copy a Friend from your own Bench) into a coin Active. (Genome Hacking, Try to Imitate and Mini-Metronome copy the Active's own attack, so their target is the attack's owner, which has no coin Ability.)
- **The engine:** the discard's damage takes the coin path only if the attacker's Active has the attack among its printed attacks (`printed_attack`, `apply_attack_action.rs` 410, used by `chosen_damage_choice`, 390). A copier's printed attacks don't include it, so the damage is a plain `ApplyDamage`: no coin.
- **Fix:** A4's coin on an attack's queued `ApplyDamage` covers it (`apply_action.rs`). In the five.

### A6. Gholdengo's Luxury Coin (four caveats)

- **Text:** Gholdengo (B4a 051, B4a 109) Luxury Coin: "Once during your turn, when you flip any coins for an effect of your Trainer cards, you may ignore all results of those coin flips and begin flipping those coins again. You can't use more than 1 Luxury Coin Ability each turn."
- **(a) "Complete Trainer coin batches are public while Luxury Coin is pending."** Not a rule of the text: what the opponent's screen shows. NOT DECIDED. Row: during a Luxury Coin prompt, film the opponent's screen (does it show the coins before the choice?). Low value: the engine's bots don't use it.
- **(b) "The player activating Arcade or Mesagoza may use Luxury Coin regardless of who played the Stadium."** DECIDED BY TEXT (a bug). Mesagoza (B2a 093): "Once during each player's turn, that player may flip a coin. ..."; Arcade (B4a 072): "Once during each player's turn, that player may flip 3 coins. ...". A Stadium the opponent played is the opponent's Trainer card, and Luxury Coin covers only "your Trainer cards". The engine's Stadium route (`stadium_route`, `trainer_coin_plan.rs` 95) records who played it (`active_stadium_owner`) but never checks it. **Fix needs `trainer_coin_plan.rs`, a sixth file: asked.**
- **(c) Luxury Coin applies to a Trainer chosen by Penny, not to Portrait or Portrait copying Penny.** DECIDED BY TEXT; the engine follows it. Penny (A3b 069 and reprints): "... Use the effect of that card as the effect of this card": the coins are for the effect of Penny, your Trainer card. Smeargle (B2 130, B4 222) Portrait: "... Use the effect of that card as the effect of this Ability": the coins are for an Ability's effect, not a Trainer card's. No change.
- **(d) Unpriced infinite batches (Misty, Team Rocket Grunt, Team Rocket's Researcher).** Not a rules question: the bots' pricing. Out of scope.

### A7. Revavroom's Dual Customization (three caveats)

- **Texts:** Revavroom (B4 115) Dual Customization: "This Pokémon may have up to 2 Pokémon Tool cards attached to it." Sitrus Berry (B1 218): "At the end of each turn, if the Pokémon this card is attached to has half of its maximum HP or less remaining, heal 30 damage from it. If you do, discard this card." Lum Berry (A2 149): "At the end of each turn, if the Pokémon this card is attached to is affected by any Special Conditions, it recovers from all of them, and discard this card."
- **(a) When suppression or devolution removes Dual Customization, the most recently attached excess Tool is discarded.** NOT DECIDED: the text says nothing about losing the Ability. Row: Revavroom with 2 Tools loses Dual Customization (devolved, or its Ability suppressed); record which Tool goes, or whether both stay.
- **(b) Two Sitrus Berries resolve one after the other and recheck HP; Heal Block leaves them attached.** Heal Block part: DECIDED BY TEXT, the engine follows it ("If you do, discard this card": no heal, no discard). The recheck: NOT DECIDED (timing: is the condition read when both trigger, or as each resolves?). Row: Revavroom with 2 Sitrus Berries at a little under half HP, where one heal lifts it above half; record whether the second Berry heals and is discarded. (rules/04 §6 has both healing at 20 → 50 → 80, where the recheck didn't matter.)
- **(c) Two Lum Berries: the first cures everything, so the second stays.** NOT DECIDED (the same timing question). Row: Revavroom with 2 Lum Berries and a Special Condition; record whether one or both are discarded.

### A8. Hisuian Basculegion's Soul Counter

- **Text:** Hisuian Basculegion (B4a 018) Soul Counter: "This attack does 50 more damage for each point your opponent got during their last turn."
- **"Checkup points are attributed to the turn that just ended."** NOT DECIDED (timing: is the Checkup between turns part of "their last turn"?). Row: your Pokémon Knocked Out by Poison or Burn at the Checkup after the opponent's turn, then Soul Counter on your next turn; record the damage.
- **"Legacy serialized states default the point history to zero."** Not a rules question (engine bookkeeping).

### A9. Team Rocket's Researcher

- **Text:** Team Rocket's Researcher (B4a 069, B4a 085): "Flip a coin until you get tails. For each heads, put a random Pokémon that has “Team Rocket” in its name from your deck into your hand."
- **"Random Pokémon put into the hand are not capped at 10 cards."** NOT DECIDED by this text (the 10-card hand is a game rule). Row: play it with 9 cards in hand and 2 or more heads; record the hand size and where the extra card goes. (The engine caps Clemont's, Serena's, Cabbie's and Juliana's searches, rules/09 e935f42, so the two policies differ today.)
- **"The deck is shuffled exactly once after resolution."** Not a rules question: deck order is hidden, so no recording can see it.

## B. rules/09's notes left "not seen"

### B1. Glimmora and Dusknoir after a Burn Knock Out, and on tails — DECIDED BY TEXT; the engine follows it

- **Texts:** Glimmora (B3a 045, B3a 078) Shattering Crystal and Dusknoir (B1 105) Fade into Darkness: "When this Pokémon is Knocked Out, flip a coin. If heads, your opponent can't get any points for it."
- Any Knock Out triggers it, Burn included; tails gives the points as usual. The engine's Checkup wave checks point denial for every Checkup knockout, whatever caused it (`pending_point_denial`, `apply_action_helpers.rs` 201, used at 96-160), and its tests produce both coin results (`rules_repair_end_turn.rs`, `rules_repair_timing.rs`). rules/09 M3's "Burn and tails not seen" needs no row.

### B2. Mimikyu ex's Disguise against a 0-damage attack (Sing) — DECIDED BY TEXT; the engine follows it

- **Text:** Mimikyu ex (B2 073 and reprints) Disguise: "When this Pokémon is first damaged by an attack after coming into play, prevent that damage."
- Sing does no damage, so the Pokémon is not "damaged", and Disguise stays. Fixed that way in 02fe9de (Sept 26). The shot row `mimikyu-disguise-no-damage-attack` (`08` T14) can be dropped.

### B3. Bad Dreams against Hide and Blocking Shell — DECIDED BY TEXT; the engine follows it

- **Texts:** Darkrai (B2b 040) Bad Dreams: "At the end of each turn, if your opponent's Active Pokémon is Asleep, do 20 damage to that Pokémon." Hide (Shinx A2 058, A2 163; Sinistea B2 074, B4a 100; Feebas P-B 072): "... prevent all damage from—and effects of—attacks done to this Pokémon." Blocking Shell (Carracosta B1 067): "Prevent all damage done to this Pokémon by attacks from Basic Pokémon ..." Harden (Silcoon B1 004, Cascoon B1 006): "... prevent all damage done to this Pokémon by attacks if that damage is 40 or less."
- All three name attacks; Bad Dreams is an Ability. Fixed that way in 53cba79; Harden was seen (204425). The rows for Hide and Blocking Shell can be dropped.

### B4. Entries that are out of date (documents only; no engine question)

- "Coin-flip damage cuts come off before Weakness": repaired in R (Sept 30; `attack_outcome.rs`'s `heads_coin_cuts`).
- "Victory Star is never offered while the attacker is Confused": repaired in R (Sept 29 repair A).
- "Coin-flip damage Abilities never flip for damage dealt through a queued choice": repaired by the two coin rounds, except A4 and A5 above.
- rules/04 §9's ⚠ line on Victory Star and Confusion: the same repair.
- These are rules/ edits, not this job's.

## C. rules/09's "Explicitly unresolved" list — none is decided by card text

Each is a game rule, not a card's text. Each stays open as a row.

| Case | What to record |
|---|---|
| The winner when an attack gives the attacker its third point and also Knocks Out the attacker's last Pokémon (by retaliation) | The result screen of such an exchange (Rocky Helmet or Counterattack on the attacker's last Pokémon, at 2 points). |
| Whether Burn comes before a Checkup healing Ability | A Burned Pokémon at 20 HP or less with a Checkup healing Ability in play (Poison before it is already seen). |
| Promotion order after a Checkup double Knock Out | Both Actives Knocked Out by Poison or Burn at the same Checkup; who is asked first. |
| A card effect returning a card to a full hand | Lucky Ice Pop on heads (or Ilima, Koga) with 10 cards in hand; where the card goes. |
| Weakness when an attack's damage is reduced to 0 before Weakness | An attacker under an attack-damage reduction applied before Weakness (Cubone's, Clefable's or Bonsly's −20, rules/09 R1) using a 20-damage attack into a Pokémon Weak to it; 0 or 20? |
| Exact turn-limit timing | The turn limit reached in a long game; when the game ends and how it is scored. |

## D. rules/04's lines marked inferred, untested or not seen

| § | Line | Verdict | Engine / row |
|---|---|---|---|
| 1 | Energy can be attached to a Pokémon put into play this turn | Not decided by text (no card restricts it) | Nothing gated. Row only if wanted: bench a Basic, attach to it the same turn. |
| 1 | Unattached Zone Energy is discarded at the end of the turn | Not decided by text | Nothing gated. Row: end a turn without attaching; check the Zone. |
| 4 | Eevee's Boosted Evolution covers only that Eevee | DECIDED BY TEXT; the engine follows it. Eevee (B1 184, P-B 011, P-B 054): "As long as this Pokémon is in the Active Spot, it can evolve during your first turn or the turn you play it." "This Pokémon" is that Eevee. The 194920 caveat (first-turn limit vs played-this-turn) doesn't matter: both are general limits only that Eevee escapes. | No change. |
| 5 | Special Conditions don't stop Abilities | DECIDED BY TEXT: no Ability text and no Special Condition rule restricts Abilities (Asleep and Paralyzed stop attacking and retreating). | Nothing gated; no row. |
| 6 | A Fossil can't be played under an Item lock | **DECIDED BY TEXT (a bug), if the Fossil's printed card type is Item** (rules/01 and rules/04 §6 say it is; the local database stores the type as "Fossil", so `lib/card.py` can't show it). The lock (Vikavolt A3 065 Disconnect, Chingling B1 109 Jingly Noise, Exploud B1 192 Booming Roar, Cryogonal B2 040 Frozen Lock): "During your opponent's next turn, they can't play any Item cards from their hand." Helix Fossil (A1 216) and the others: "Play this card as if it were a 40-HP Basic [C] Pokémon. ..." | The engine's Item check skips the Fossil type (`move_generation_trainer.rs` 65; Fossils go to `can_place_fossil` at 95), so a Fossil is playable under the lock. **Fix needs `move_generation_trainer.rs`, a sixth file: asked.** A picture of a Fossil card's type line settles the premise; no game test. |
| 6 | Copycat with an empty deck and no other cards in hand | Not decided by text. Copycat (B1 225, B1 270): "Shuffle your hand into your deck. Draw a card for each card in your opponent's hand." | Row: empty deck, Copycat the only card in hand; is it playable? |
| 6 | Clemont and Team Galactic Grunt can be played with every named card visibly out of the deck (v1.7.0) | Not decided by text: the printed text didn't change; the game's rule did. | Row: each card with every named card in play or discarded (Gladion is seen, 152812). |
| 6 | Which discard pile a replaced Stadium goes to | Not decided by text | Row: replace the opponent's Stadium; open both discard piles. |
| 9 | Victory Star with a Confused attacker (⚠ engine) | Repaired (B4). | — |
| 10 | Cards shuffled back into the deck become hidden again | Not a rules question (information) | — |

rules/04 §6's ⚠ list of deck-content checks (Gladion, Grunt, Cabbie, Pokémon Communication, Wallace, the Tool-search Ability) rests on Dustin's hidden-information rule, not on card text; rules/09's rules1 repairs say most were fixed. Outside this audit.

## E. Found while reading, outside the three sources (decided by text; not fixed in this job)

- **E1. Guts on the attacker's own Pokémon.** Conkeldurr (A3 096) and Ursaluna (B3b 058) Guts: "If this Pokémon would be Knocked Out by damage from an attack, flip a coin. If heads, this Pokémon is not Knocked Out, and its remaining HP becomes 10." Any attack, your own included. The engine flips it for every target of a queued `ApplyDamage` (`forecast_apply_damage`), but in an attack's outcome only for the opponent's Pokémon (`apply_defender_guts_if_needed`, `apply_attack_action.rs`). So when your own Earthquake would Knock Out your own Benched Ursaluna, its Guts coin never flips. In the five files; not in the three sources, so not fixed without a word from the coordinator.
- **E2. Perish Body on a plain queued hit.** Galarian Cursola (A4a 035) Perish Body: "If this Pokémon is in the Active Spot and is Knocked Out by damage from an attack from your opponent's Pokémon, flip a coin. If heads, the Attacking Pokémon is Knocked Out." The attack's outcome and its queued `ApplyQueuedAttackDamage` run it; a plain queued `ApplyDamage` at the Active (Chase Order's or Wild Swing's damage into a non-coin Active, for example) does not (`forecast_apply_damage` has no Perish Body). In the five files (`apply_action.rs`); not fixed without a word.
- **E3. Trap Territory counted once** (Ariados B1a 006, B1a 070: "Your opponent's Active Pokémon's Retreat Cost is 1 more."; 213034). This is the job's item 4, in `hooks/retreat.rs`, allowed for that fix only.

## What happens next

| Case | Verdict | Fix | File(s) |
|---|---|---|---|
| A1 Victory Star with a block coin | text: a bug | now, tests first | `apply_action.rs`, `apply_attack_action.rs` |
| A2 Will with a block coin | text: a bug | now, tests first | `apply_attack_action.rs`, `attack_outcome.rs`, `apply_action.rs` |
| A4 coin Abilities on the attacker's own Pokémon (and the opponent's Active in the own-Bench choice) | text: a bug | now, tests first | `attack_outcome.rs`, `apply_attack_action.rs`, `apply_action.rs` |
| A5 a copied discard attack | text: a bug | now, with A4 | `apply_action.rs` |
| `hooks/core.rs`'s kd comment naming Wild Swing, the own-Bench branch and the copied branch as engine gaps | out of date after these fixes | now, comment only | `hooks/core.rs` |
| A3 Victini's caveat text | out of date | asked | `card_validation.rs` (sixth) |
| A6b Luxury Coin on the opponent's Stadium | text: a bug | asked | `trainer_coin_plan.rs` (sixth) |
| D Fossil under an Item lock | text: a bug (premise: printed type Item) | asked | `move_generation_trainer.rs` (sixth) |
| E1 Guts on your own Pokémon; E2 Perish Body on a plain queued hit | text: bugs, outside the three sources | asked | `apply_attack_action.rs`, `attack_outcome.rs`; `apply_action.rs` |
| A6a, A7a, A7b (recheck), A7c, A8, A9 (hand cap), C (six), D (five) | not decided by text | shot-list rows above | — |

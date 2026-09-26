Decision this informs: whether the pilot after kp3 prices the defender's temporary damage cuts and reduction Tools in the threat clock, replaces the flat +10 for a Tool on the Active by what the Tool does for its holder, and credits damage back to the attacker; read against kp3 by the Sept 25 plan. This file is kt's registration (Sept 26), committed before any kt code or game; no engine commit yet (kt is built after the rules/09 fixes and the regenerated kp3 base, step ORDER below).

Seeds: kt's table on the table's deals only (72,000,000 + pairing × 10,000 + i, i < 500, even i = first-named deck in seat 0); the Dustin-deck A/B on the new block 22,600,000,000 – 22,699,999,999 (START_HERE's seed table).

# kt: Tools and temporary damage cuts priced by what they do (registration, Sept 26)

**Source.** Fable's proposed registration text (`rl/results/fable_reviews_2026-09-26/kt_spec_review.md` on main, "The registration text Fable proposes the cloud commit"), taken as written except where marked **[amended]** or **[filled]** below, with the reason beside each; the laptop's answers of Sept 26 (A/B size, opponent seat, Jasmine's denominator, seed block, kp3 regenerated after the rules/09 fixes); and the laptop's carrier census for clause (d) (`rl/results/kt_carrier_census_2026-09-26/README.md` on main). The earlier draft (`../tool_turn_effect_census_2026-09-25/README.md`, c002d2f) is superseded; its census stands. Any change after this commit is a dated amendment before any kt game, and a spec change after any reading is a new code.

## BASE AND CODES

- kt<N> = kp<N> (k's blind search, PublicPricingPlayer with the 62 audited texts) with three EvalFeatures flags, all on. kq's, kd's and kpr's features off. Built on the pilot the kpr reading leaves: **kp3** (the laptop's rule-v2 reading, main 055f6f0, did not adopt kpr3). If that changes, this registration is re-issued, not amended.
- Diagnostic codes, each with one flag on: kta<N> (switch 1), ktb<N> (switch 2), ktc<N> (switch 3). They are parsed before "kt", which is parsed before "k"; the parser test covers kta3, ktb3, ktc3, kt3, kt13 and rejects kt1a. Single-switch readings are attribution, never adoption, except kta under the reserve route below.
  - Pre-registered interactions: ktb alone removes Barrier, Apron and Rocky Helmet play (the +10 is gone and nothing credits them), so a Skarmory or Blaziken regression under ktb is expected, not a bug. ktc alone changes Blaziken's row only.
- The score's flat Tool term (`active_has_tool`, weight 10, both sides) is 0 under kt and ktb, and 10 under kta and ktc.

## RULE (card-agnostic)

A Tool or a temporary damage cut is worth exactly what the engine's own hooks make it worth to its holder where it sits, through terms the score already has, and 0 otherwise. The evaluator calls hooks; it names no card. The per-card table below is the consequence of the rule, kept so a reader can check it; a new Tool needs no spec edit.

## SWITCH 1: the defender's temporary cuts and reduction Tools, in the threat clock (both sides)

- **A new engine hook** in `hooks/core.rs`, next to `persistent_defender_damage`: `temporary_defender_reduction(state, victim, threat, turn) -> u32`. It sums:
  - turn effects registered for `turn` (`State::get_turn_effects`) whose scope covers the victim and whose only-from-ex condition matches the threat (`ReducedDamageForTarget`, `ReducedDamageForType`);
  - the victim's own `CardEffect::ReducedDamage` / `ReducedDamageFromEx` still live on `turn`;
  - Metal Core Barrier's cut, only when `turn` is the holder's opponent's next turn (the engine discards it at the end of that turn whether or not it was hit).
- **Pinned by a test.** For turn == the current turn, on constructed positions covering each effect type, the value equals what `modify_damage` subtracts at those stages. The Weakness stage is not taken over (kd's term stays in B3). Known limit: where the victim is Weak, the engine's cut lands on a bigger number than the clock's estimate, so kt under-counts the cut there.
- **Permanent cuts.** `persistent_defender_damage`'s Tool stages (Steel Apron, Heavy Helmet) as the engine computes them. Heavy Helmet reads the current Retreat Cost once the rules/09 fix is in; the fix goes in first, with its replay, and kt does not mirror the engine.
- **Timing is the clock's own, not a new one.** f = the absolute turn on which the clock already puts the threat's first hit (its missing-Energy count included; for a Benched threat, what the clock uses for it).
  - Temporary cuts are read for turn f.
  - A card effect counts only if its turns_left reaches f.
  - A turn effect counts only if registered for f; Jasmine, Cheren and Blue live on t and t+1 only.
  - Two engine changes this needs: `first_attack_turn` is extended from the Active threat to any slot, and `get_turn_effect_damage_reduction` takes a turn.
- **Hits.** d_first = max(0, damage − temporary − permanent); d_later = max(0, damage − permanent). KO turns = `ko_turns_after_first_attack(hp, d_first, d_later)`, where d_later is per victim.
  - This is the one change to the clock's arithmetic: kp uses one max_damage for every victim.
  - kd's (first, later) structure is not taken over, only this per-victim later damage.
- **Units, stated so the reading can be judged.** The clock counts whole turns at 100 per turn, so a cut that doesn't change the number of hits is worth 0 here.
  - Prediction: Jasmine and the Barrier are played under kt only on turns where they save a hit, so their play rate will be well below the flat +10's 82%.
  - If deck 07 shows no gain, that refutes clock-only pricing, and a finer safety term is a new registered code, not an amendment.
- **Where the table sees it.** Frigibax's Stiffen (Suicune) only. **[filled]** The carrier census confirms the panel's `t-suicune.txt` carries one Frigibax P-B 037 (13 Limitless lists equal it card for card), so switch 1 reaches the table's own Suicune cells.
  - Prediction: Stiffen use rises from 44% of offered turns (55 of 124 under kp3).
  - No table cell moves beyond paired noise under kta3 (footprint expected under 5%).

## SWITCH 2: the flat +10 replaced by the holder's terms (both sides, the same rule each side)

- **HP Tools** (Giant Cape, Leaf Cape, Elegant Cape on a Stage 1): `get_effective_total_hp`, already in the board term (HP × (relevant Energy + 1)), the Active's safety and the clock; nothing more.
  - Predicted worth on a powered Active: up to +80 (Giant Cape) and +120 (Leaf Cape); the same for Field Blower on the opponent's.
  - Elegant Cape on a Basic: 0 on both sides. There is no deck or hand read: `evolution_potential` isn't used (it is off in kp and 0 under public evaluation).
- **Retreat Tools** (Small Balloon, Inflatable Boat): the own Active's retreat term through `get_board_retreat_cost_for_player`, which already prices the eligible case; 0 on an ineligible holder.
  - The opponent's retreat Tools: 0 (the score has no opponent retreat term; a later candidate).
  - Recorded: an eligible Balloon or Boat on the own Active is +1 against −1 for the card, an exact tie decided by move order.
  - Prediction: Altaria's Balloon plays fall from 88% of offered turns, and its useless placements (225 of 501) to near 0. Suicune's Boat plays fall from 60%.
  - The direction of the Altaria and Suicune rows is not predicted. An own-side drop beyond the mixed row's paired noise on either is a rule-v2 veto, and is expected to be the first thing the rows are asked.
- **Damage-cut Tools** (Metal Core Barrier, Steel Apron, Heavy Helmet): through switch 1 on a qualifying holder, 0 otherwise. Under ktb alone: 0.
- **Protective Poncho:** 0 on both sides, Active or Benched, in this candidate.
  - Reason: kp's clock prices hits on the Active only. Bench-hit pricing is the "reach" sub-change that broke Lucario in kd3, and is a later candidate of its own (through `persistent_defender_damage`'s DefenderHit gate and `only_damages_the_bench`, when it comes).
  - Prediction: Lucario's Poncho plays fall from 68% of offered turns (427 of 428 on the Active) to near 0. No prediction for Lucario's row.
- **Counter-damage Tools** (Rocky Helmet; Poison Barb): switch 3.
- **Deceptive Needle:** own side as now (its first chip lands inside the searcher's EndTurn, which the search resolves); opponent's side 0 (the opponent's EndTurn is never searched). Recorded asymmetry.
- **Tools no term reads** get 0, so they are never played under kt:
  - Lucky Egg, Electrical Cord, Leftovers, Memory Light, Lucky Mittens, Lum Berry, Sitrus Berry, Rescue Scarf, Beastite, Dark Pendant, Clear Veil and Future Booster Energy Capsule;
  - any Tool whose only job is to enable "+X if a Tool is attached".

  Accepted and listed. brew-04 (Lucky Egg, 147 attached in 240 audit games) and any B2e held-out deck carrying one are reported under the "no more than 2 further from Limitless" rule.
- **Field Blower, Guzma and Repel** gain exactly what removing or moving the Tool changes under the rule above. Prediction, both directions stated:
  - Blower stops removing the opponent's Needle, Balloon and Boat (453 + 93 + 64 of its 1,414 Active removals under kp3) and keeps removing Capes and Rocky Helmet.
  - Hydreigon's and Weezing's rows rise, and Hydreigon's gap grows (already +5.2 above Limitless on v2 under kp3). A Hydreigon deck-gap veto is the expected readout of this switch.
  - If the mixed rows show the rise is on the opponents' side (Blower decks piloted worse), that is the recorded cause, and the opponent's Needle is the first item of the later candidate "opponent's Tools the search cannot play out".

## SWITCH 3: damage back to the attacker, in the holder's own side's KO clock (both sides)

- **Through `get_counterattack_damage`:** Rocky Helmet, `CardEffect::Counterattack` such as Spike Armor, and `CounterattackDamage` Abilities. None of the latter is in the eight lists; declared here.
- **Formula.** For our clock on threat T against our Active holder H with counter damage c:
  - T's HP for our clock is reduced by c × k, where k is the number of hits T lands on H before our knockout of T;
  - **[amended]** k = min(n_ours − 1 + s, n_theirs) — Fable's text had n_theirs − 1;
  - n_ours is our clock's hit count on T without the counter, n_theirs the opponent's clock's hit count on H, and s = 1 if T's owner is to move (T attacks first), else 0;
  - the count is then recomputed once with the reduced HP.

  Reason for the amendment: the engine applies the counter-damage to the attacker for every damaged Active, whether or not the hit knocked it out (`handle_attack_retaliation`, `actions/apply_action_helpers.rs`), and the rules say the same ("still fires if the holder is Knocked Out", `rules/04`). So the knockout hit counts, and T lands at most n_theirs hits on H.
  - **[amended]** It applies only when T is both the opponent's threat in its own clock and our clock's current victim, the opponent's Active. A Benched threat has not attacked H yet, so its hits are not counted.
  - This couples the two clocks by one read each way, and is stated so.
- **Poison Barb:** not in this candidate. It needs the Special Conditions model, deferred with it, and Barb is in no table deck. `should_poison_attacker` is not called.
- **Prediction:** Blaziken keeps playing Rocky Helmet under kt and ktc (69% of offered turns now) and stops under ktb; Blaziken's row is switch 3's to explain.

## FOOTPRINT AND ROUTES (section 8 line 130, restated verbatim so nothing is loosened later)

- **Footprint** = the share of the table's 14,000 paired games in which the new bot's play differs from kp3's at least once (move fingerprint), measured against the kp3 reference regenerated at the same engine. Reported for kt3, kta3, ktb3 and ktc3.
- **kt3 (all three):** expected over 15%, so the ordinary adoption rule applies:
  - paired ΔMSE against kp3 on scoreboard v2's 27-cell decision set, with the whole 95% interval below zero (binomial, by-event beside it);
  - vetoes under rule v2 (a cell's miss grows by more than 6, a deck's gap by more than 2, a B2e held-out deck more than 2 further), counting only when the 28-pairing mixed rows on the same deals show kt3's own side worse beyond the row's paired noise, and never on a cell with a Limitless band over 15.0;
  - the tau margin with its 90% interval reported beside it.
- **kta3 (switch 1)** under the reserve route, its own reading:
  - (a) footprint under 15% on the same paired files;
  - (b) no harm: tau margin (kp3 minus kta3) 90% lower bound at −1.0 or above, and no rule-v2 veto;
  - (c) mixed rows for the pairings where kta3's footprint is non-zero (Suicune's seven, both directions, 500 deals): no meta deck's own side worse beyond noise;
  - (d) a gain beyond paired noise on kta3's own side on at least one Limitless top-30 archetype that is not Dustin's deck and carries the relevant cards, named below before any list is read; deck 07 and Dustin's other carriers reported too, as motivation and not as the test;
  - (e) adoption for the screen and the table together.

  Stated now: if the carrier census finds no such archetype, or one with no usable decklist, the route is closed for switch 1 and it is adoptable only by Dustin's explicit override, recorded as such. The route is not loosened after the census is seen.
- **Outcomes fixed now:**
  - kt3 passes and kta3 passes: kt adopted (screen and table).
  - kt3 passes and kta3 fails or is closed: nothing adopted as built. Switches 2 and 3 are re-registered as a new code with a new table, unless Dustin overrides for kt as a whole.
  - kt3 fails: nothing adopted. The diagnostic codes are read for attribution only, and the next candidate is registered afresh.

  A spec change after any reading is a new code.

## CARRIER CENSUS FOR (d) **[filled]**: done by the laptop before this commit, before any kt game

**Order, stated plainly.** Fable's text had the census run after this commit. It was run first, by the laptop, and its README was read before this was written, so the archetype names below were chosen with the lists in view. What was fixed before the census ran is the route itself: section 8 line 130's clauses and its closure sentence. The census applied them without choosing between readings, and this file doesn't choose either.

The laptop's census (`rl/results/kt_carrier_census_2026-09-26/`) scanned the Cowork Limitless pull's 63 development events (4,722 decklists; holdout never opened) for the switch-1 card set, over 35 top-30 archetypes (the Sept 10 top 30 and the window's). It found three carrier archetypes; every other archetype carries 0.
- **Dragonair Mega Rayquaza ex**: Gouging Fire B3a 054 (an attack that registers ReducedDamage 30 on itself) in 135 of 143 lists (94%). Sept 10 rank 22; window rank 6.
  - A usable list: `rl/results/kt_carrier_census_2026-09-26/decks/c-dragonair_mega_rayquaza_ex.txt` (20 cards, Energy Fire and Lightning). It is thefossilman's list, 1st of 219 at Umbreon99's Aura Sphere #4 on 2026-09-11 (event 6a7e2b83cdc0391d7fa65afb, development split). deck_check is clean and all 13 cards are fully implemented.
  - Limitless cells against all eight panel decks: pooled equal-weight 46.3 ± 4.8 over 606 matches, none under 20 pooled (`cells_c-dragonair_mega_rayquaza_ex.csv`). These are the before figures for the "reported, not gated" line.
- **Suicune ex Baxcalibur**: Frigibax P-B 037 (Stiffen) in 22 of 200 lists (11%). The panel's own `t-suicune.txt` is one of them, equal to 13 Limitless lists.
- **Vespiquen ex Shuckle ex**: Blue A1a 067 in 4 of 233 lists (1.7%, all Sept 21); no list built.

**The (d) archetype turns on Dustin's ruling, to be recorded in a dated commit before any kta game:**
- **If the Dragonair overlap with his deck 11 does not make Rayquaza "his deck"** (the census's reading 2: Mega Rayquaza ex and Gouging Fire are in no file of his): the (d) archetype is **Dragonair Mega Rayquaza ex** with the list above.
- **If it does** (reading 1, the census's conservative rule, since 2 Dragonair B4 117 are in `decks/dustin/11-archaludon-haxorus-dragonair.txt`): the route is open only through the occasional carriers. Each needs the gain shown on a list that actually carries the card:
  - Suicune ex Baxcalibur with Frigibax P-B 037 (the panel's own list, or the two-Stiffen shell in the census's `carrier_entries.csv`);
  - Vespiquen ex Shuckle ex with Blue (a list to be built from `carrier_entries.csv`).

  Whether an 11% or 1.7% carrier share satisfies "carries the relevant cards", and whether a panel deck can serve, are readings of the fixed text for Dustin.
- **A third reading for Dustin, from the census's section 1.** Section 8's closure sentence names "reduction Tools or turn-effect cards". Gouging Fire and Frigibax are neither: each is a Pokémon whose own attack cuts the damage it takes on the opponent's next turn, a card kind switch 1 prices through the same hook. The only turn-effect carrier outside Dustin's decks is Blue, in 4 Vespiquen lists. Whether that kind counts as "the relevant cards" is also Dustin's to rule.
- Where the (d) archetype has real Limitless cells against the eight table decks, those cells are reported before and after, and not gated.

## DUSTIN-DECK A/B (reported for kt3 and kta3; motivation for switch 1, not its test) **[filled with the laptop's answers]**

- **Decks and arms.** Decks 07, 05, 11, 01 and 03 against the floor panel. kt3 on the deck seat against kp3 on the deck seat, with **kp3 on the opponent's seat in both arms** (the mixed-row design).
- **Size.** 240 games per matchup × 8 = **1,920 games per arm**, paired by seed, with McNemar beside the paired difference.
- **Measures:**
  - deck win rate;
  - Jasmine's play rate with **"offered"** as the denominator (turns on which Jasmine was a legal play, the census's definition);
  - Barrier, Apron and Heavy Helmet placement (qualifying holder or not).
- **Seeds:** **22,600,000,000 – 22,699,999,999**, written into START_HERE's seed table in this commit.
- **The comparison size, separated as Fable noted:**
  - the flat +10 took Jasmine to 82.4% on the 240-seed causal block;
  - the deck-seat-only Jasmine pricing gave +5.7 points on a separate fresh 1,920-game block.

## READOUT COUNTERS (fixed now) **[amended: added]**

- For kp3 (regenerated), kt3, kta3, ktb3 and ktc3 on the same deals:
  - `tool_census.rs`'s per-card table: turns offered, turns played, holder by spot and name, and Field Blower's targets. The tool is in `../tool_turn_effect_census_2026-09-25/`, run on the first 100 deals of each pairing, with fingerprints checked against the table file.
  - `legality_scan`'s Hyper Ray, Chase Order, discard-attack and Ability counters (a03f491).
- Field Blower's rate is reported with the census's denominator, turns on which it was a legal play. The Trainer audit's "turns with an opponent target" figure is quoted beside it, not mixed.

## IDENTITY AND ORDER

1. **rules/09 fixes first**, each its own commit with a full k3 and kp3 replay of the 14,000 table games. Each lists the games that differ and shows they lie in cells where the mechanic is reached (Blaziken v Suicune for Pulse and Hiking Trail; Poké Ball games listed by seed). The fixes:
   - Legendary Pulse v Hiking Trail;
   - Heavy Helmet at the current Retreat Cost;
   - Rare Candy v Primeval Law;
   - Poké Ball A2b 111 with an empty deck;
   - Crawdaunt's "random" Energy discard (Fable's text). **[amended: added]** The Supporter Psychic, which takes the last-attached Energy in the same way (rules/09).
   - **[amended: added]** Discard-all-Energy attacks putting the Energy in the discard pile.
   - **[amended: added]** The end-of-turn and Checkup knockout promotion timing (the knocked-out player promotes before the next player's draw; footage 07aafa3, `docs/REVIEW_2026-09-24_direction.md` on main). Like Pulse, it reaches table games, so its replay is read for changed games.
2. **kp3's reference table regenerated at the fixed engine** (kp3_500 at that commit), and scoreboard v2's kp3 row re-scored on it by the laptop. This is kt's paired base and the base for the footprint.
3. **At kt's build:**
   - k3, kp3 and kq3 replay 14,000 of 14,000 against the fixed-engine references;
   - kd3 and kpr3 replay at least 1,120 of 1,120 (i < 40 of every pairing);
   - a kt-only diff of everything after the last full replay, as the kpr reading required.
4. **The tables.** kt3's table (28 × 500 on the table's deals), then kta3, ktb3 and ktc3 on the same deals.
   - The laptop's mixed rows are run from a build of the table's commit.
   - timing.txt has kt3's 40-deal run within 1.25× kp3's, or the per-leaf Tool classification is rewritten before the table (one pass over `attached_tools` against the effect texts in `tools.rs`, not a `tool_count` call per Tool id).
5. **Everything above is read by the laptop** under rule v2 with score.py; this folder only reports.

## Amendments to Fable's text, in one place

- **Switch 3's hit count:** k caps at n_theirs, not n_theirs − 1, because the engine and the rules fire Rocky Helmet on the knockout hit. It applies only to the opponent's Active threat.
- **Filled in:**
  - the (d) archetype, with both readings, the group-3 wording point, and Dustin's ruling to come (the census ran before this commit, not after);
  - the Stiffen baseline and the Suicune list's one Stiffen card (from the census);
  - the A/B size, opponent seat, denominator and seeds (the laptop's answers);
  - the base (kp3, per the kpr reading).
- **Added:**
  - the readout counters;
  - three engine fixes to step 1: discard-all-Energy to the discard pile; the Supporter Psychic's Energy pick; promotion timing after an end-of-turn or Checkup knockout.

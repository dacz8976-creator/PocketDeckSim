# kt draft spec: Fable's overnight review (Sept 26, 00:40)

**Who wrote this and why.** Fable (the "Deck pilot bot project review" session), overnight on Sept 25 to 26, under Dustin's instruction before bed ("Keep us on track for tonight and make progress. Tokens be damned"). It merges three independent review passes over the branch (the first pass's own file is kept beside this one as `kt_spec_review_pass1_0020.md`); everything was read with `git show` on `origin/claude/pensive-ptolemy-spwc0b` at aa87fa3, nothing checked out, nothing in the working tree touched. It is independent of the cloud session's own reviewers. It is a proposal for the laptop session and for Dustin, who decides; the registration text below is a draft for the cloud to commit, not a registration.

**What it reviews.** The draft spec in `rl/results/tool_turn_effect_census_2026-09-25/README.md` on the branch (revised in c002d2f, "not registered, nothing built"), against the engine on that branch (`hooks/core.rs`, `players/value_functions.rs`, `players/mod.rs`, `hooks/counterattack.rs`, `effects.rs`, `state/mod.rs`, `tools.rs`), the Trainer audit and Skarmory finding on main, and the plan (RUN5 "revised Sept 25"; section 8 lines 130 to 131 for the reserve route and the census reading).

## The verdict, plainly

1. **The spec is not ready to register.** Its aim is right and most of its facts check out (the census numbers reproduce from `kp3_census.txt`; the 16 Dustin-deck card placements are correct; the effect types exist; kd was not adopted, so building on kp is right; no weight is tuned to Limitless). But it is a description of intent, not a registration: several formulas are prose, the footprint is neither defined nor estimated, the adoption route is never named, the paired baseline is not pinned, and one "reuse" claim and one "symmetric" claim are false against the code.

2. **What must change before the census for clause (d) is read** (the carrier census of Limitless top-30 archetypes, which the reserve route needs and which nobody has run; the kp3 table census is done):
   - **Say which route each switch takes and measure the footprint.** Switches 2 and 3 touch nearly every table game (every list runs a Tool, played on 60 to 92% of offered turns; Field Blower in six lists), so the bundle is over the 15% trigger and the ordinary rule applies to it. Switch 1 is table-invisible (Frigibax's Stiffen, 55 uses in 700 Suicune games, is all the table sees) and as bundled it would enter the pilot on the strength of the other two with its own effect unmeasured, or fail with them for reasons that are not its own. Fable's recommendation: register switch 1's single-switch code as its own reserve-route candidate, with the closure sentence from section 8 line 130 verbatim, a named carrier archetype and a named list source, all before any list is read.
   - **Fix the two false claims.** Metal Core Barrier is not in kd's `persistent_defender_damage` (its doc says it is left out; the helpers are private; the function applies Weakness first, which kt does not take over). "Symmetric" fails for the opponent's retreat Tools and Deceptive Needle, which have no opponent-side term in the score, so under switch 2 Field Blower stops removing the opponent's Needle, Balloon and Boat (610 of its 1,414 Active removals under kp3) and Hydreigon and Weezing keep their chip. That is the spec's most predictable table effect and its prediction list does not contain it.
   - **Write the formulas.** Switch 1's timing must be the clock's own (the missing-Energy arithmetic; turn effects live on turns t and t+1 only; the Barrier is discarded at the end of the opponent's next turn whether hit or not), and its later-hit pricing needs a per-victim later damage, which kp's clock does not have. Steel Apron and Heavy Helmet "on every hit", Protective Poncho, Rocky Helmet's hits-before-knockout and Poison Barb's horizon have no arithmetic. Poison Barb needs the Special Conditions model the spec defers; drop it.
   - **Pin the baseline and the identity list.** The rules/09 engine fixes change the Blaziken v Suicune cell (Legendary Pulse v Hiking Trail) and Poké Ball-with-empty-deck games, so after them kp3's reference table is stale and "k3, kp3 and kq3 replay the table unchanged" fails by construction; the kp3 base and scoreboard v2's kp3 row must be regenerated at the fixed engine before kt is paired against them. kd3 and kpr3 are missing from the identity list although switch 1 touches kd's path.
   - **Small but blocking:** the proposed seed block (22,000,000,000) is reserved in START_HERE's table; the diagnostic codes are unnamed and the parser makes `kt1`-style names a depth parse; the Dustin-deck A/B has no game count, opponent pilot or Jasmine denominator.

3. **Is anything a card patch?** No line is a card patch in B5's sense (no rule names a card to force a play). But switch 2 is written as a per-card value table, and three rows (Protective Poncho, Elegant Cape, the reduction Tools) are card descriptions where a generic engine hook exists; built as written they become card-keyed evaluator code. The registration should state the one rule ("a Tool is worth what the engine's own hooks make it worth to its holder where it sits, and 0 otherwise") and give the table as its consequence. Switch 1 keys on effect types and is card-agnostic as required. The engine itself identifies Tools by per-card effect texts, which is fine as long as the evaluator calls the hooks rather than listing cards.

## Findings, by severity

### High

**1. Metal Core Barrier is not handled by `persistent_defender_damage`; the "Tool stages" cannot be called as written; the Weakness order differs.**
Spec line 61: reduction Tools "through the Tool stages kd's `persistent_defender_damage` already runs: Metal Core Barrier (−50 ...), Steel Apron, Heavy Helmet". On the branch `hooks/core.rs` 1682 to 1684 sums only `heavy_helmet_reduction` and `steel_apron_reduction`; its doc at 1601 to 1606 says "Left out ... Metal Core Barrier (it discards itself at the end of the opponent's turn); turn effects" (main: 1577 to 1580, 1613 to 1615). The Barrier lives in `get_metal_core_barrier_reduction(state, target_player, target_idx)` at 715 to 735, a private fn inside `modify_damage`. All the pieces switch 1 needs (`heavy_helmet_reduction`, `steel_apron_reduction`, `get_metal_core_barrier_reduction`, `get_turn_effect_damage_reduction`, `get_reduced_card_effect_modifiers`, `damage_reduction_scope_covers`) are private; `hooks/mod.rs` exports only `persistent_defender_damage`, `DefenderHit`, `DamageModifierContext` and `get_counterattack_damage`. Nor can "Tool stages only, not Weakness" be had by calling the whole function: its stages are one closure, Weakness then reductions with a floor at 0 (1653 to 1714), so kt would subtract the cuts from an un-weakened estimate (a 100 threat into a Weak Barrier holder: engine 120 − 50 = 70, kt 100 − 50 = 50; a 40 threat: engine 10, kt 0). The Skarmory README item 1 states the same exclusion. Fix: one new `pub(crate)` hook (`temporary_defender_reduction`, below), pinned to `modify_damage` by a test.

**2. "Symmetric" is false for retreat Tools and Deceptive Needle; Field Blower will stop answering the opponent's Needle, Balloon and Boat; Hydreigon and Weezing gain.**
The retreat term is own-side only: `value_functions.rs` 556 `(-my.active_retreat_cost) * params.active_retreat_cost`; the spec itself defers "the opponent's Retreat Cost". Deceptive Needle is read only through the searcher's own EndTurn, which the search resolves (`expectiminimax_player.rs` 633 to 657); the opponent's EndTurn is never searched (KP arm: opponent_ply 0, consistent_horizon false, `players/mod.rs` 514 to 524; turn boundary never crossed at 908 to 918). So under kt the opponent's Balloon, Boat and Needle are worth 0 and Field Blower on them scores −1 (the card, `hand_size` weight 1.0 at line 48). In the census the opponent's Active Needle is Blower's most frequent target (85 + 73 + 65 + 103 + 88 + 39 = 453 of 1,414 Active removals; first in five of six Blower lists), Balloon 93 and Boat 64 more. Those plays scored +10 under kp3. Hydreigon is already the largest miss above Limitless (kp3 47.4 against 42.2 on v2) and the deck-gap veto is the likely readout. Spec line 100 "Field Blower is played only where the removed Tool did something for its holder" is not what its own arithmetic gives: it also stops where the Tool did something the evaluator cannot see. Elegant Cape has the same asymmetry by a different route (finding 8).

**3. No footprint, no route, clause (d) unsatisfiable as named, clauses (b) and (c) absent.**
The word "footprint" does not appear in the spec; lines 113 to 114 say only "Switches 2 and 3 are visible on the table" / "Switch 1 is not", and line 53 makes the single-switch codes "diagnostic". The plan defines the footprint (section 8 line 130 (a): "the share of the table's paired games in which the new bot's play differs from kp3's at least once", threshold 15%, set before the census is read) and line 131 expects the bundle to exceed it, so the ordinary rule decides on a table that never sees switch 1. If the bundle fails there is no registered path for the Skarmory fix; if it passes, switch 1 rides in untested (the kd precedent: a bundle "refuted as built", "no split run"; the advice for this candidate was "narrow and one thing at a time"). Clause (d) requires "a gain beyond paired noise on at least one Limitless top-30 archetype that is not Dustin's deck and carries the relevant cards", explicitly so that a route judged on his decks does not "over several fixes build a pilot specifically good at his decks"; the spec names only Dustin's decks 07, 05, 11, 01, 03 and "the held-out decks the laptop names". B2e's six held-out archetypes (dustin 09, 13, 04, 08, 12, brew-08's base) carry no reduction Tool or turn-effect card (grep of `decks/dustin`: Heavy Helmet in 01/03; Jasmine, Metal Core Barrier, Steel Apron in 07; Cheren in 05). The repo has no such list: `decks/classifier/limitless_2026-09-10.json` holds archetype names and counts only; `tournament_decks.json`, `my_decks.json`, `decks/screen/opponents` and `decks/variants-2026-09-23` contain none of the cards. The top-30 table does list Metal archetypes (Magnezone Miraidon ex rank 13, Magnezone ex Magnezone rank 15) where a carrier is plausible, but that must be named and sourced before the lists are read. Clauses (b) (τ̂ margin 90% lower bound at −1.0 or above, no rule-v2 veto) and (c) (no meta deck's own side worse beyond noise in the mixed rows) do not appear; the strings τ̂, MSE, −1.0, margin and veto are absent. Contrast kpr's registration, which carried a dated prediction.

**4. The paired baseline is not pinned, and the identity requirement contradicts the fix ordering.**
Spec line 54: "k3, kp3 and kq3 must replay the table unchanged, proven by replay before any kt table"; line 55: "The engine fixes queued on rules/09 go in first, each with its replay". The branch's `rules/09` (lines 141 to 151) says the Legendary Pulse v Hiking Trail fix changes the Suicune v Blaziken cell (`t-blaziken.txt` line 14 carries Hiking Trail; `t-suicune.txt` line 5 Suicune ex, whose Legendary Pulse is `database.rs` 33663 to 33669); the Poké Ball empty-deck fix (f6e8bca) touches six lists' legal moves. After those fixes the kp3 reference table is stale in at least that cell, the replay fails by construction, and a kt-vs-kp3 paired delta on the old kp3 file confounds the engine fixes with kt there, while scoreboard v2's kp3 row is at the old engine. The plan's rule for engine repairs (section 8 line 127): reproduce the k3 table game for game where the mechanic is not reached, and report where it is. "Read the 28-matchup table against kp3" (line 113) never says which kp3 table. Separately, kd3 and kpr3 are missing from the identity list although switch 1 touches `hooks/core.rs` (kd's path); the branch's own practice for kpr replayed kd3 on 40 deals. The laptop's kpr mixed-rows spot replay covers pairings 0 to 2 only, not Suicune v Blaziken.

**5. Switch 1's timing is inconsistent with the clock it plugs into.**
The spec credits the cut on "the attacker's next attack", this turn or the attacker's next turn (lines 63, 66). The kp clock's first hit lands after the threat's missing Energy (`value_functions.rs` 933, `total_turns += missing_energy`). Jasmine, Cheren and Blue are turn effects registered for turns t and t+1 only (`apply_trainer_action.rs` 1018 to 1037 with `add_turn_effect(..., 1)`; `state/mod.rs` 1063 to 1069); Metal Core Barrier is discarded at the end of every opponent turn whether or not it was hit (`core.rs` 504 to 519); Stiffen and Steel Wing card effects expire on `turns_left`. So `ko_turns_after_first_attack(hp, max(0, damage − cuts), max_damage)` over-credits every time the threat is not ready next turn. kq's `first_attack_turn`, which the spec cites as its timing, does the missing-Energy arithmetic (first_attack = next_turn + 2 × (m − 1)) and drops effects with first_attack > t + turns_left (1391 to 1415), but runs only when the threat is the Active (`_threat_slot == 0`, 960); a Benched threat's first attack is two or more turns away and temporary cuts must not count for it. Also: `get_turn_effect_damage_reduction` (`core.rs` 1189 to 1227) reads the current turn only; it needs a turn parameter so the scope and only-from-ex checks (1213 to 1220) are not re-implemented in the evaluator. `State::get_turn_effects(turn)` exists on the branch (added for kpr) but not on main, so kt depends on the kpr commits or must re-add it.

### Medium

**6. Every-hit pricing for Steel Apron and Heavy Helmet has no formula.** kp's clock divides every victim's HP by the one `max_damage` (966 to 1004); `ko_turns_after_first_attack` (1345 to 1351) changes the first hit only; per-victim later-hit damage is kd's `(first, later)` structure (`KdPricer::hits`, 1259 to 1276), which the spec says is not taken over. The earlier draft (3ac9bdd) had this as open choice 2 and recommended next-attack only; c002d2f chose every hit without recording who decided. A related unit question the registration should answer: the clock counts whole turns to a knockout at 100 per turn (562 to 563), so a cut that does not change the number of hits is worth 0 there, and Jasmine's or the Barrier's value under kt may be far below the flat +10 that gave 82% play and +5.7 points in the causal test; the registration should predict this and say what a low Jasmine rate with no deck-07 gain would mean (a finer safety term is a new code, not a tweak).

**7. The switches are separable as flags, not as effects; the diagnostic names are unfixed with a parse hazard.** With the +10 gone (switch 2), Barrier and Apron are played only if switch 1 credits them (the Skarmory causal test: +10 at 0 takes the Barrier from 74.6% to 1.5%, Apron 70.5% to 2.7%, deck 07 from 132 to 97 wins of 240); Rocky Helmet only if switch 3 covers the card (the spec says so). A switch-2-only code will read as Skarmory and Blaziken regressions that are not bugs. `players/mod.rs` 214 to 267 parses codes by `strip_prefix` then a depth parse, prefix-ordered (`kpr` before `kp`, then `kq`, `kd`, then `k`): `kt1`/`kt2`/`kt3` parse as kt at depth 1/2/3, and letter suffixes must be matched before `kt` because `strip_prefix("kt")` on `kta3` returns an Err before later rules run.

**8. Card-agnosticism: three rows are card descriptions where a hook exists, and one needs a hidden read.** Protective Poncho: the branch's `persistent_defender_damage` already returns (0, 0) for a Benched hit when the defender has Poncho or `PreventDamageWhileBenched` (Shell Shield; `core.rs` 1625 to 1630; `effects.rs` 76 to 78; `effect_ability_mechanic_map.rs` 1002), and kd's `only_damages_the_bench` (`value_functions.rs` 2390) finds bench-only attacks; the spec's new term ("the damage it prevents ... on its next turn, up to the holder's HP") has no formula (which attacks, which Abilities, sum or max, units) and kp's clock is reach-blind (it prices hits on the Active only), so the Bench value needs new code either way. Elegant Cape: `evolution_potential` prices the evolved form at printed `t.hp` (1977) without the holder's Tools, so "discounted as `evolution_potential` discounts it" is not what the function does; kp runs `value_aware = false` (179 to 190) so `evolution_potential` is never computed in kp at all; and under `public_only` it returns 0 (1959 to 1961) because it reads `state.decks[owner]` and `state.hands[owner]` (1357 to 1360, 1965 to 1966), so "an evolution available in the owner's deck or hand" is either 0 for the opponent (an unstated asymmetry) or a hidden-zone read the tier-1 check would reject. Reduction Tools: the engine's reductions are CardId-keyed helpers (703 to 762), so "keyed on the effect type, never on card names" holds only if the evaluator calls the hooks (finding 1). More broadly, the engine has no Tool mechanic enum: Tools are identified by one effect-text constant per card and `tool_count` compares effect strings (`tools.rs` 33 to 37, 39 to 93, 105 to 110), so the registration must state the rule as hook calls with the table as the consequence.

**9. Retreat Tools on an eligible Active become an exact tie, decided by move order; Altaria and Suicune are exposed with no prediction.** Weights: `hand_size` 1.0 (48), `active_retreat_cost` 1.0 (50); public evaluation reads the board retreat cost including the Balloon's and Boat's discounts (688 to 712; `hooks/retreat.rs` 135 to 146), so an eligible Balloon is +1 and the card −1, net exactly 0, not "roughly a tie" (spec line 99). The same accident the Skarmory finding documented for Barrier v Apron (decided only by move order). Altaria plays 501 Balloons per 700 games (276 on eligible holders, 88% of offered turns), Suicune 501 Boats (60%); the census skeptic says the term under-prices a kept Energy ("worth the holder's remaining HP and online score"). Altaria is the deck with the +7 unexplained gap and Altaria v Lucario the tightest band (±4.9). Under rule v2 an own-side drop beyond ±4 in the mixed rows is a veto. Pre-register the predicted direction for both rows.

**10. Switch 2 changes kp's play on Tools outside the table, and two claims about them are wrong.** Every implemented Tool the table lacks (Lucky Egg, Electrical Cord, Leftovers, Memory Light, Lucky Mittens, Lum Berry, Sitrus Berry, Rescue Scarf, Beastite, Dark Pendant, Clear Veil, Future Booster Energy Capsule; `tools.rs` 39 to 93) goes from +9 and always played on the Active to −1 and never played. "Lucky Egg: only Dustin's deck 02 runs it" is wrong: brew-04-xatu-slowking runs it (147 attached in 240 audit games; `trainer_audit_2026-09-25/audit_tools.tsv` line 9, `audit_trainers.tsv` line 34). The leaf estimator does not read `ExtraDamageIfToolAttached` or `DamagePerOwnToolAttached` (`effect_mechanic_map.rs` 1267 to 1300; no such mechanic in `value_functions.rs`, only the flat term at 718), so a Tool whose job is to enable "+X if this Pokémon has a Tool attached" (Pachirisu ex, Melmetal ex, Greedent, Stantler, Iron Boulder, Skarmory A2 111) loses the +10 and gains nothing at the leaf; only a Play + AttachTool + Attack line, exactly kp3's three plies, shows the real damage. These are held-out and brew decks, where "no fix may move one more than 2 further from Limitless" and the B2e card check apply.

**11. Poison Barb needs the Special Conditions model the spec defers; switch 3's hit count couples the two clocks; abilities are undeclared.** "Expected Poison damage per Checkup until it leaves the Active" is unbounded and needs a Poison-tick and Active-tenure model (spec line 107 lists Special Conditions as not in this candidate; census.json: "the k value function has no Poison term at all"). Detection is generic (`counterattack.rs` 117 to 124 `should_poison_attacker` covers Barb and `PoisonAttackerOnDamaged`) but the price is not; Barb is in no table deck (brew-03a, dustin/10 only). `get_counterattack_damage` (13 to 36) sums Rocky Helmet, `CardEffect::Counterattack` (Spike Armor) and `CounterattackDamage` abilities, none of the latter in the eight lists; the spec names only Rocky Helmet. "Each hit the opponent's threat lands on it costs the threat 20, counted against the threat's HP in the holder's own side's KO clock" needs a rule for how many hits land before our knockout of the threat, which is the other clock's KO count.

**12. The Dustin-deck A/B is undesigned, and its comparison size merges two runs.** Lines 115 to 117: "A paired A/B of kt3 against kp3 piloting the deck, against the floor panel" with no game count (the causal test used 1,920 paired games; the floor uses 240 per matchup), no opponent pilot (the Skarmory skeptics showed the opponent's Tools share the same weight, README 41 to 44; the +5.7 came from a deck-seat-only pricing, line 49), and no Jasmine denominator (1.2% in the Trainer audit is Supporter-only turns; 1.3%/1.8% in the Skarmory README; 3 of 97 in the floor smoke). "82% played, +5.7 points" (line 117) merges the 240-seed causal block with a flat +10 (82.4%) and a separate fresh 1,920-game deck-seat-only block (+5.7).

**13. The proposed seed block is reserved.** Spec line 115 "new seeds from 22,000,000,000"; START_HERE lines 149 and 172 (branch: 157): "22,000,000,000 to 22,599,999,999: the cloud's Sept 25 overnight list", with the rule that new blocks go above the last one used; CLAUDE.md: "Pick seeds outside every range in START_HERE's seed table."

### Low

**14. Engine changes switch 1 needs that the spec does not name:** `first_attack_turn` for any threat slot (960); `get_turn_effect_damage_reduction` with a turn parameter; `get_turn_effects(turn)` on main. (Detail in finding 5.)

**15. HP Tools are worth more than the spec predicts, on both sides.** In k's board term a Pokémon is HP × (relevant_energy + 1) (1506 to 1519; 1984 to 1998), so Giant Cape on a powered Active is worth up to +80 and Leaf Cape +120, not "+20 to +30" (line 98), with the same amounts for Field Blower on the opponent's. The rows that will move: Suicune (Giant Cape, Boat), Sceptile and Vespiquen (Leaf Cape), the six Blower lists; Blaziken's row is switch 3's.

**16. Search cost.** kt changes no node count (a Tool's two-ply cost is kp3's move generation: `move_generation_trainer.rs` 386 to 396; `apply_trainer_action.rs` 1887 to 1902; the horizon effect is a kp3 property to check if kt under-delivers, as the spec says). kt's real cost is per leaf: `tool_count` clones a whole `Card` out of `DATABASE` on every call (`database.rs` 86360 to 86365), so a naive per-Tool-id classification is on the order of 100 Card clones per leaf. kd's path (two `tool_count` calls per hit) ran 170 s against kp3's 156 s on the 40-deal identity, and kd3's full table 2,913 s against kp3's 1,561 s on a shared machine. Recommend one pass over `attached_tools` against the `LazyLock` effect texts already in `tools.rs`, and a registered timing budget.

**17. Two Field Blower rates with different denominators are quoted without reconciliation:** 30% of legal turns (census, line 33; `tool_census.rs` 11 to 12) and 41 to 57% of turns with an opponent target (Trainer audit README line 130). Name one as the pre-set measure.

**18. kt is "built on kp, not kd or kpr" (line 52) while kpr's reading was pending.** The kpr review beside this file finds kpr not adoptable, so kp3 is the base; the registration should say kt rebases onto whatever pilot that reading leaves, since the plan allows one pilot (route clause (e)).

**19. Hygiene.** `heavyhelmet_test.MP4` is not in the repo (Battle Logs); cite `rules/05` #19. "plus Heavy Helmet and Steel Apron if they appear" (line 68) is moot: neither is in any of the eight lists. Lucky Egg at 0 plus −1 for the card means it is never played (record as accepted, with brew-04 named). The census lists Stiffen by attack title (`REDUCTION_ATTACKS`), fine for a census, not a rule.

### Verified (info)

The census was run before the spec, on kp3's own table games (2,800 of 2,800 fingerprints equal `kp3_500_*.jsonl`); every "on the Active" figure and the Blower breakdown (1,703 + 26 + 34 = 1,763; 1,414 on the Active; 5,911 offered) reproduce from `kp3_census.txt` lines 3 to 18; Small Balloon 225 of 501 (Espeon 93 + Mega Altaria ex 67 + Igglybuff 65; Igglybuff's Retreat Cost 0, Espeon and Mega Altaria ex Stage 1 per `lib/card.py`); Poncho 427 of 428 and the laptop's 492 of 494; all 16 Dustin-deck placements; effect types with the stated semantics (`effects.rs` 9, 103, 121 to 156; `TurnEffect::ReducedDamageForTarget { scope, only_from_ex }`); Barrier discard at `core.rs` 504 to 519; Heavy Helmet printed cost at 706; `get_effective_total_hp` gates Leaf and Elegant Cape by holder (`played_card.rs` 290 to 310); `get_counterattack_damage` generic; kd not adopted (ΔMSE +14.2, Lucario −2.2 ± 1.4); the 15% threshold and the −1.0 bound were fixed on the plan side (line 130) before the census reading (line 131); B3's fit is on self-play, never Limitless; the spec sets weights by hand.

## The registration text Fable proposes the cloud commit

Draft for the registration commit message and the README's spec section. Numbers in square brackets are for the cloud to fill from the code at the commit; everything else is meant to be committed as written, then amended only by a dated commit before any kt game.

```
kt: Tools and temporary damage cuts priced by what they do (registration, Sept 26)

Decision this informs: whether the pilot after kp3 prices the defender's temporary damage cuts and
reduction Tools in the threat clock, replaces the flat +10 for a Tool on the Active by what the Tool
does for its holder, and credits damage back to the attacker; read against kp3 by the Sept 25 plan.

BASE AND CODES
- kt<N> = kp<N> (k's blind search, PublicPricingPlayer with the 62 audited texts) with three
  EvalFeatures flags, all on. kq's, kd's and kpr's features off. Built on the pilot the kpr reading
  leaves (kp3 as of Sept 26); if that changes, this registration is re-issued, not amended.
- Diagnostic codes, each with one flag on: kta<N> (switch 1), ktb<N> (switch 2), ktc<N> (switch 3).
  They are parsed before "kt", which is parsed before "k"; the parser test covers kta3, ktb3, ktc3,
  kt3, kt13 and rejects kt1a. Single-switch readings are attribution, never adoption, except kta under
  the reserve route below. Pre-registered interactions: ktb alone removes Barrier, Apron and Rocky
  Helmet play (the +10 is gone and nothing credits them), so a Skarmory or Blaziken regression under
  ktb is expected, not a bug; ktc alone changes Blaziken's row only.
- The score's flat Tool term (active_has_tool, weight 10, both sides) is 0 under kt and ktb, 10 under
  kta and ktc.

RULE (card-agnostic): a Tool or a temporary damage cut is worth exactly what the engine's own hooks
make it worth to its holder where it sits, through terms the score already has, and 0 otherwise. The
evaluator calls hooks; it names no card. The per-card table below is the consequence of the rule, kept
so a reader can check it; a new Tool needs no spec edit.

SWITCH 1: the defender's temporary cuts and reduction Tools, in the threat clock (both sides)
- New engine hook in hooks/core.rs, next to persistent_defender_damage:
    temporary_defender_reduction(state, victim, threat, turn) -> u32
  = turn effects registered for `turn` (State::get_turn_effects) whose scope covers the victim and
    whose only-from-ex condition matches the threat (ReducedDamageForTarget, ReducedDamageForType)
  + the victim's own CardEffect::ReducedDamage / ReducedDamageFromEx still live on `turn`
  + Metal Core Barrier's cut, only when `turn` is the holder's opponent's next turn (the engine
    discards it at the end of that turn whether or not it was hit).
  Pinned by a test: for turn == the current turn, on constructed positions covering each effect type,
  the value equals what modify_damage subtracts at those stages. The Weakness stage is not taken over
  (kd's term stays in B3); known limit: where the victim is Weak the engine's cut lands on a bigger
  number than the clock's estimate, so kt under-counts the cut there.
- Permanent cuts: persistent_defender_damage's Tool stages (Steel Apron, Heavy Helmet) as the engine
  computes them; Heavy Helmet at the current Retreat Cost once the rules/09 fix is in (the fix goes in
  first, with its replay; kt does not mirror the engine).
- Timing is the clock's own, not a new one. f = the absolute turn on which the clock already puts the
  threat's first hit (its missing-Energy count included; for a Benched threat, what the clock uses for
  it). Temporary cuts are read for turn f; a card effect counts only if its turns_left reaches f; a
  turn effect only if registered for f (Jasmine, Cheren, Blue live on t and t+1 only). first_attack_turn
  is extended from the Active threat to any slot; get_turn_effect_damage_reduction takes a turn.
- Hits: d_first = max(0, damage - temporary - permanent); d_later = max(0, damage - permanent);
  KO turns = ko_turns_after_first_attack(hp, d_first, d_later), where d_later is per victim (this is the
  one change to the clock's arithmetic: kp uses one max_damage for every victim; kd's (first, later)
  structure is not taken over, only this per-victim later damage).
- Units, stated so the reading can be judged: the clock counts whole turns at 100 per turn, so a cut
  that does not change the number of hits is worth 0 here. Prediction: Jasmine and the Barrier are
  played under kt only on turns where they save a hit; their play rate will be well below the flat
  +10's 82%. If deck 07 shows no gain, that refutes clock-only pricing and a finer safety term is a
  new registered code, not an amendment.
- Where the table sees it: Frigibax's Stiffen (Suicune) only. Prediction: Stiffen use rises from 44%
  of offered turns; no table cell moves beyond paired noise under kta3 (footprint expected under 5%).

SWITCH 2: the flat +10 replaced by the holder's terms (both sides, the same rule each side)
- HP Tools (Giant Cape, Leaf Cape, Elegant Cape on a Stage 1): get_effective_total_hp, already in the
  board term (HP x (relevant Energy + 1)), the Active's safety and the clock; nothing more. Predicted
  worth on a powered Active: up to +80 (Giant) / +120 (Leaf), the same for Field Blower on the
  opponent's. Elegant Cape on a Basic: 0 on both sides (no deck or hand read; evolution_potential is
  not used, it is off in kp and 0 under public evaluation).
- Retreat Tools (Small Balloon, Inflatable Boat): the own Active's retreat term through
  get_board_retreat_cost_for_player, which already prices the eligible case; on an ineligible holder 0.
  The opponent's retreat Tools: 0 (the score has no opponent retreat term; a later candidate).
  Recorded: an eligible Balloon or Boat on the own Active is +1 against -1 for the card, an exact tie
  decided by move order. Prediction: Altaria's Balloon plays fall from 88% of offered turns and its
  useless placements (225 of 501) to near 0; Suicune's Boat plays fall from 60%; direction of the
  Altaria and Suicune rows not predicted; an own-side drop beyond the mixed row's paired noise on
  either is a rule-v2 veto and is expected to be the first thing the rows are asked.
- Damage-cut Tools (Metal Core Barrier, Steel Apron, Heavy Helmet): through switch 1 on a qualifying
  holder; 0 otherwise. Under ktb alone: 0.
- Protective Poncho: 0 on both sides, Active or Benched, in this candidate. Reason: kp's clock prices
  hits on the Active only; Bench-hit pricing is the "reach" sub-change that broke Lucario in kd3 and is
  a later candidate of its own (through persistent_defender_damage's DefenderHit gate and
  only_damages_the_bench, when it comes). Prediction: Lucario's Poncho plays fall from 68% of offered
  turns (427 of 428 on the Active) to near 0; no prediction for Lucario's row.
- Counter-damage Tools (Rocky Helmet; Poison Barb): switch 3.
- Deceptive Needle: own side as now (its first chip lands inside the searcher's EndTurn, which the
  search resolves); opponent's side 0 (the opponent's EndTurn is never searched). Recorded asymmetry.
- Tools no term reads (Lucky Egg, Electrical Cord, Leftovers, Memory Light, Lucky Mittens, Lum Berry,
  Sitrus Berry, Rescue Scarf, Beastite, Dark Pendant, Clear Veil, Future Booster Energy Capsule, and
  any Tool whose only job is to enable "+X if a Tool is attached"): 0, so never played under kt.
  Accepted and listed; brew-04 (Lucky Egg, 147 attached in 240 audit games) and any B2e held-out deck
  carrying one are reported under the "no more than 2 further from Limitless" rule.
- Field Blower, Guzma and Repel gain exactly what removing or moving the Tool changes under the rule
  above. Prediction, both directions stated: Blower stops removing the opponent's Needle, Balloon and
  Boat (453 + 93 + 64 of its 1,414 Active removals under kp3) and keeps removing Capes and Rocky
  Helmet; Hydreigon's and Weezing's rows rise; Hydreigon's gap (already +5.2 above Limitless on v2
  under kp3) grows, and a Hydreigon deck-gap veto is the expected readout of this switch. If the mixed
  rows show the rise is on the opponents' side (Blower decks piloted worse), that is the recorded
  cause, and the opponent's Needle is the first item of the later "opponent's Tools the search cannot
  play out" candidate.

SWITCH 3: damage back to the attacker, in the holder's own side's KO clock (both sides)
- Through get_counterattack_damage (Rocky Helmet, CardEffect::Counterattack such as Spike Armor, and
  CounterattackDamage abilities; none of the latter in the eight lists; declared here).
- Formula: for our clock on threat T against our Active holder H with counter damage c: T's HP for our
  clock is reduced by c x k, where k is the number of hits T lands on H before our knockout of T, k =
  min(n_ours - 1 + s, n_theirs - 1), with n_ours our clock's hit count on T without the counter,
  n_theirs the opponent's clock's hit count on H, and s = 1 if T's owner is to move (T attacks first),
  else 0; the count is then recomputed once with the reduced HP. This couples the two clocks by one
  read each way and is stated so.
- Poison Barb: not in this candidate (needs the Special Conditions model, deferred with it); Barb is
  in no table deck. should_poison_attacker is not called.
- Prediction: Blaziken keeps playing Rocky Helmet under kt and ktc (69% of offered turns now) and stops
  under ktb; Blaziken's row is switch 3's to explain.

FOOTPRINT AND ROUTES (section 8 line 130, restated verbatim so nothing is loosened later)
- Footprint = the share of the table's 14,000 paired games in which the new bot's play differs from
  kp3's at least once (move fingerprint), measured against the kp3 reference regenerated at the same
  engine. Reported for kt3, kta3, ktb3 and ktc3.
- kt3 (all three): expected over 15%, so the ordinary adoption rule: paired dMSE against kp3 on
  scoreboard v2's 27-cell decision set with the whole 95% interval below zero (binomial, by-event
  beside it); vetoes under rule v2 (a cell's miss grows more than 6, a deck's gap more than 2, a B2e
  held-out deck more than 2 further) counting only when the 28-pairing mixed rows on the same deals
  show kt3's own side worse beyond the row's paired noise, never on a cell with a Limitless band over
  15.0; the tau margin with its 90% interval reported beside it.
- kta3 (switch 1) under the reserve route, its own reading: (a) footprint under 15% on the same
  paired files; (b) no harm: tau margin (kp3 minus kta3) 90% lower bound at -1.0 or above, no rule-v2
  veto; (c) mixed rows for the pairings where kta3's footprint is non-zero (Suicune's seven, both
  directions, 500 deals): no meta deck's own side worse beyond noise; (d) a gain beyond paired noise
  on kta3's own side on at least one Limitless top-30 archetype that is not Dustin's deck and carries
  the relevant cards, named below before any list is read; deck 07 and Dustin's other carriers
  reported too, as motivation and not as the test; (e) adoption for the screen and the table together.
  Stated now: if the carrier census finds no such archetype, or one with no usable decklist, the route
  is closed for switch 1 and it is adoptable only by Dustin's explicit override, recorded as such; the
  route is not loosened after the census is seen.
- Outcomes fixed now: kt3 passes and kta3 passes -> kt adopted (screen and table). kt3 passes and kta3
  fails or is closed -> nothing adopted as built; switches 2+3 are re-registered as a new code with a
  new table, unless Dustin overrides for kt as a whole. kt3 fails -> nothing adopted; the diagnostic
  codes are read for attribution only; the next candidate is registered afresh. A spec change after
  any reading is a new code.

CARRIER CENSUS FOR (d), run before any kt game and after this commit
- Source named now: the Cowork agent's Limitless decklist pull for the top-30 archetypes in
  decks/classifier/limitless_2026-09-10.json, from the same B4a events as scoreboard v2's development
  half (URLs and pull date recorded in the census file; the holdout events are not read).
- Cards scanned: Jasmine, Cheren, Blue, Beast Wall, Metal Core Barrier, Steel Apron, Heavy Helmet, and
  any Pokemon whose attack registers ReducedDamage / ReducedDamageFromEx on itself (from the engine's
  effect map, not a hand list).
- Result: the archetype(s) carrying them outside Dustin's decks, with their lists, named in a dated
  commit before the first kt game; candidates the classifier makes plausible are Magnezone Miraidon ex
  (rank 13) and Magnezone ex Magnezone (rank 15), which is a guess to be checked, not a pre-selection.
  Where that archetype has real Limitless cells against the eight table decks, those cells are
  reported before and after, reported and not gated.

DUSTIN-DECK A/B (reported for kt3 and kta3; motivation for switch 1, not its test)
- Decks 07, 05, 11, 01, 03 against the floor panel: kt3 on the deck seat v kp3 on the deck seat, kp3 on
  the opponent's seat in both arms (the mixed-row design), 240 games per matchup x 8 = 1,920 per arm,
  paired by seed, McNemar beside the paired difference. Measures: deck win rate; Jasmine's play rate
  with "offered" as the denominator (turns on which Jasmine was a legal play, the census's definition);
  Barrier, Apron and Heavy Helmet placement (qualifying holder or not).
- Seeds: a block above 22,599,999,999, written into START_HERE's seed table before the first game
  [the cloud names it: 22,600,000,000 to 22,699,999,999 if free].

IDENTITY AND ORDER
1. rules/09 fixes first (Legendary Pulse v Hiking Trail; Heavy Helmet at current Retreat Cost; Rare
   Candy v Primeval Law; Poke Ball with an empty deck; Crawdaunt's Energy choice), each with a full
   k3 and kp3 replay of the 14,000 table games, listing the games that differ and showing they lie in
   cells where the mechanic is reached (Blaziken v Suicune for Pulse/Hiking Trail; Poke Ball games
   listed by seed).
2. kp3's reference table regenerated at the fixed engine (kp3_500 at that commit) and scoreboard v2's
   kp3 row re-scored on it; this is kt's paired base and the base for the footprint.
3. At kt's build: k3, kp3, kq3 replay 14,000 of 14,000 against the fixed-engine references; kd3 and
   kpr3 at least 1,120 of 1,120 (i < 40 of every pairing); a kt-only diff of everything after the last
   full replay, as the kpr reading required.
4. kt3's table (28 x 500 on the table's deals), then kta3, ktb3, ktc3 on the same deals; the laptop's
   mixed rows from a build of the table's commit; timing.txt with kt3's 40-deal run within 1.25x kp3's,
   or the per-leaf Tool classification is rewritten before the table.
5. Everything above is read by the laptop under rule v2 with score.py; this file only reports.
```

## Questions for the laptop session and Dustin

1. Switch 1 as its own reserve-route candidate (kta) with the closure sentence verbatim, or the bundle as one unit with switch 1 riding in untested? If the bundle stays, what is the pre-registered decision when it fails the table but kta3 looks clean? (Findings 3, 7.)
2. Which non-Dustin Limitless top-30 archetype and which list source for clause (d)? Does the Cowork agent pull the Metal archetypes' lists before the census is read, and does the "route closed if none is found" sentence go into the registration verbatim? (Finding 3.)
3. Will kp3 be re-run on the fixed engine as kt's paired base, with scoreboard v2's kp3 row re-scored, and will the identity expectation list the games the rules/09 fixes change? Are kd3 and kpr3 in the identity list? (Finding 4.)
4. Who chose every-hit pricing for Apron and Helmet, and is the per-victim later damage above the formula? Does the clock's whole-turn count (a cut that saves no hit is worth 0) get a written prediction for Jasmine? (Finding 6.)
5. Are the opponent-side values under switch 2 intended to be 0 for retreat Tools, Deceptive Needle and Elegant Cape on a Basic, written into the spec with the dated prediction for Field Blower on Hydreigon's and Weezing's Needles and for Altaria's Balloon, and is the Hydreigon deck-gap veto accepted as the expected readout of the switch? (Findings 2, 8, 9.)
6. Poncho at 0 in this candidate (Bench-hit pricing deferred with kd's reach lesson), or a formula now? Poison Barb deferred with Special Conditions? (Findings 8, 11.)
7. Will each Tool row be expressed as an engine-hook call (`temporary_defender_reduction` pinned to `modify_damage`; `get_effective_total_hp`; `get_board_retreat_cost_for_player`; `get_counterattack_damage`), so a new Tool needs no spec edit? (Findings 1, 8.)
8. Diagnostic code names fixed now with letter suffixes (`kta`, `ktb`, `ktc`) and the parser test? (Finding 7.)
9. For the Dustin-deck A/B: 1,920 games per arm, kp3 on the opponent's seat in both arms, "offered" as Jasmine's denominator, and which unreserved seed block above 22,599,999,999? (Findings 12, 13.)
10. Does kt rebase onto kp3 now that the kpr review finds kpr not adoptable, with the registration saying so? (Finding 18.)

## Questions for the cloud (paste-ready for Dustin)

```
From Fable's overnight review (via Dustin), on the kt draft in
rl/results/tool_turn_effect_census_2026-09-25/README.md at aa87fa3:

1. Metal Core Barrier is not in persistent_defender_damage (its doc says it is left out; the helper is
   private; the function applies Weakness first). Please replace "the Tool stages kd already runs" with
   a named hook, temporary_defender_reduction(state, victim, threat, turn), pinned to modify_damage by
   a test, and state that Weakness is not taken over.
2. "Symmetric" is false for the opponent's retreat Tools and Deceptive Needle (no opponent retreat term;
   the opponent's EndTurn is never searched). Under switch 2 Field Blower stops removing them (610 of
   its 1,414 Active removals under kp3). Please write that asymmetry in, with the prediction that
   Hydreigon's and Weezing's rows rise and Hydreigon's deck-gap veto is the expected readout.
3. Please define the footprint (share of the 14,000 paired games differing from kp3, measured at the
   same engine), say which route each switch takes, and carry section 8 line 130 (a) to (e) and its
   closure sentence verbatim. Fable's proposal: switch 1 as its own reserve-route code (kta), with a
   named carrier archetype and list source before any list is read.
4. Timing: use the clock's own first-hit turn (missing Energy included); turn effects live on t and t+1
   only; the Barrier is discarded at the end of the opponent's next turn regardless; later hits need a
   per-victim later damage (kp has one max_damage). Please write d_first / d_later and the KO-turn
   formula, and predict Jasmine's play rate given that a cut which saves no hit is worth 0 in a
   whole-turn clock.
5. Baseline: the rules/09 fixes change Blaziken v Suicune and Poke Ball games, so kp3's reference
   table must be regenerated at the fixed engine and v2's kp3 row re-scored before kt is paired
   against it. Add kd3 and kpr3 to the identity list.
6. Drop Poison Barb (Special Conditions deferred); price Poncho at 0 in this candidate (Bench-hit
   pricing is kd's reach lesson, a later candidate); Elegant Cape on a Basic 0 on both sides (no deck
   or hand read). State the off-table Tools that become never-played (brew-04 runs Lucky Egg).
7. Name the diagnostic codes with letter suffixes (kta, ktb, ktc; kt1 parses as depth 1). Pick a seed
   block above 22,599,999,999 (22.0B to 22.6B is reserved). Fix the A/B design: 1,920 games per arm,
   kp3 on the opponent's seat, "offered" as Jasmine's denominator; the 82% and the +5.7 are from
   different runs.
8. Fable's full proposed registration text is in
   rl/results/fable_reviews_2026-09-26/kt_spec_review.md on main; take or amend it in a dated commit
   before any kt game.
```

## Raw material

Branch copies and check scripts in the session scratchpad under `reviews/` (`branch/kt_spec_README.md`, `branch/hooks_core.rs`, `branch/hooks_mod.rs`, `branch/hooks_counterattack.rs`, `branch/value_functions.rs`, `branch/players_mod.rs`, `branch/expectiminimax_player.rs`, `branch/tools.rs`, `branch/played_card.rs`, `branch/kp3_census.txt`, `branch/kd_README.md`, `branch/kpr_README.md`; `kt_review_branch_check.sh`, `_check2.sh`, `_check3.sh`, `kt_cards.sh`). The first review pass's file is `kt_spec_review_pass1_0020.md` beside this one. Main-side references: `rl/results/trainer_audit_2026-09-25/`, `rl/results/skarmory_tool_jasmine_2026-09-25/README.md`, `docs/REVIEW_2026-09-24_direction.md` lines 127, 130, 131, `rl/RUN5.md` lines 380 to 395, `START_HERE.md` seed table, `CLAUDE.md`.

# REGISTERED (Sept 27): kph = kpg + R′, kpf's projection with its two diagnosed faults fixed

**Registered before any kph code or game.** One review, two lenses (engine code; rules and plan), all findings applied: `REVIEW.md`.
- Dustin, Sept 27, in chat (recorded here first), on kpf's vetoes: "leave it provisional and diagnose … the fix is registered as a new candidate on top of kpg and read against the 45 cells and the coverage decks; the vetoed cells are the cells that decide it, not the cells it's tuned to."
- Sources:
  - the diagnosis `../kpf_2026-09-26/diagnosis/DIAGNOSIS.md`;
  - Dustin's blind quiz on its ten positions, `../blind_quiz2_2026-09-27/RESULTS.md`.

## 1. In plain words

- **The problem.** kpf's projection (R) gives next turn's Energy to whatever stands in the Active Spot. That makes Altaria, Lucario and Vespiquen swap a cheap attacker out for an Energy-hungry Pokémon and drop the cheap attack. Their own sides play worse (kpf's vetoes).
- **Two causes:**
  - The readiness score treats an unevolved Basic as if it were already its evolution.
  - The clock credits the Zone Energy only to the Active slot.
- **The fix (R′): kph = kpg + R′,** with R′ being R plus:
  - **A.** Each evolution step still to take counts as one missing Energy. The clock already uses this rule.
  - **B.** The clock may give the Zone Energy to any one of the side's Pokémon that can really be in the Active Spot for its next attack under the game's retreat rule. Dustin's quiz notes price next turn's retreat in Q06, Q08 and Q10, and B adds that.
- **Dustin's quiz agrees with A and B:** kp3's way in 7 of 7 of their positions.
- **What kph keeps that Dustin wouldn't do: R's tempo credit** (moving the main attacker up a turn early). A benched attacker with no Energy still gets only the one Zone Energy from B, so feeding it in front a turn sooner still wins the clock (DIAGNOSIS 235). Dustin rejected that move at Q10 ("sure"). It is open (section 7), counted in the mechanism check, and gates nothing.
- **Rayquaza's gain should survive:** Mega Rayquaza ex and Gouging Fire don't evolve, and their credit comes from being in front. A pre-set trace check reports it.

## 2. What kph is

- **Base.**
  - kph's base is kpg: kp + F, the discard-Energy credit exactly as built at 9bffbda.
  - If the composed pilot (kp3 + koa's opening switch A + F; Dustin's composition ruling) has passed its composition check when kph's table runs, R′ is added to that composed code instead, and its references are the composed pilot's. This is the RUN5 "one pilot" rule. The reading names the base used.
  - **If kpg (F) fails its confirmation,** kph's verdict lapses with it, since kph carries F. R′ is then read again on the base in force at that time, as a new reading under the rules in force.
- **R′ = R** (kpr's `projected_active_energy`, its horizons and amendment 5, exactly as in kpf) **with two changes, each behind its own switch:**
  - **A: evolution-aware readiness** (only in the projected branch of the readiness score, `calculate_active_pokemon_online_score`, `value_functions.rs` 2122-2124):
    - A separate variant. `pokemon_online_score` itself is unchanged, since kq's bench score also calls it (2456).
    - Let `target` be the yardstick card `pokemon_online_score` already picks (2365-2370): the highest evolution in the owner's deck and hand, or the card itself.
    - Let `steps = target.stage.saturating_sub(active.stage)` (as line 1002 does).
    - If `total` is 0, the score is 1.0, as the existing early return does (2401-2402).
    - If `steps > 0`: the projected reading is `clamp((total − missing − steps) / total, 0, 1)`, and the score is `max(that, the unprojected reading)`, the unprojected reading being kp3's.
    - If `steps = 0`: the score is R's projected reading exactly, with no max.
    - This is the clock's own rule: each evolution step counts as one turn, the same unit as missing Energy (`value_functions.rs` 909-912, 1009-1010).
  - **B: the side's Zone Energy, to a Pokémon that can reach the Active** (in the damage-aware clock with a horizon):
    - The clock is `min(clock(no projection), clock(Active projected as R does), min over qualifying benched s of clock(s given the Zone Energy only))`. The clock already takes a min (943-946). The scan that projects slot 0 only (983-989) gets its parameter widened to (horizon, slot, Zone-only).
    - **Qualifying:** s can be in the Active Spot at its next attack by the game's retreat rule, read from the board:
      - **Payment:** the current Active's board Retreat Cost, `get_board_retreat_cost_for_player` (`retreat.rs` 112), must be payable from the Energy already attached to it. Retreat costs are Colorless, so the count decides. This excludes this turn's discounts (X Speed, Leaf), which `get_retreat_cost_for_player` (105) includes. A cost of 0 always passes the payment test.
      - **Not blocked:** kq's player-aware retreat block (`value_functions.rs` 1537-1540): Asleep or Paralyzed, `CardEffect::NoRetreat`, a Fossil. Status and effects are read from the board now, as kq's block does.
      - **Already retreated:** when the credited attack is this turn (the side's turn is running), also require `!state.has_retreated`.
      - No hand card is assumed (no X Speed or Switch), so the rule is the same for both sides and list-free.
    - **What s gets:** exactly the Zone terms in `projected_active_energy_and_discard`'s turn list (2229-2242, 2254-2258), with the same `running` test (including `end_turn_scored_before_it`), and without `zone_blocked`, since `NoEnergyFromZoneToActive` blocks only the Active (`state/energy.rs` 76-85). So at the usual leaf, with the opponent to move and its turn running, an opponent's benched s gets one Zone Energy, as its Active does.
    - Ability Energy stays Active-only, as in R. B never gives s discard-pile Energy.
    - Both sides, each at its own horizon. The opponent's side stays board-only.
    - Taking the minimum over recipients keeps the clock never slower than R's (the test `the_clock_never_gets_slower_for_the_projection`, 3837).
- **No new constant, no card list, no hidden information.** On the opponent's side `public_only` leaves the deck unseen, so `target` is the card itself and `steps` = 0 (2353-2370): A never changes the opponent's reading.
- **Diagnostic codes:** A only and B only, run only if the reading needs attribution. The parser entry for `kph` goes before `kp` (`players/mod.rs` 233-236).

## 3. Why these changes and not others (kept short; the diagnosis has the detail)

- **A** answers the channel with the clearest harm: Swablu 15/3, bare Riolu 24/11, Combee 9/2, pooled 48/16. Dustin's Q03-Q05 all went kp3's way.
- **B** answers the channel with the biggest behaviour change: forward swaps 52/32, Lucario's forward-v-back z = 3.2. Dustin's Q01, Q02, Q06 and Q07 all went kp3's way.
- **The retreat condition** comes from Dustin's notes: "next turn retreat with shuckle" (Q06), and at Q10 "you would need another xspeed to retreat shuckle", said of the bench-feed alternative (G to the benched Vespiquen ex behind a Shuckle ex with nothing to pay its retreat), not of moving Vespiquen ex up.
  - Without it, B would credit that benched Vespiquen ex.
  - In every diagnosed swap the retreat was free or paid from Energy held, so the condition changes none of the diagnosed decisions. It prevents a new over-credit.
- **Not Dustin's gate** ("project only when the Active is the best attacker"): it misses the harmful swaps and would switch R off for Mega Rayquaza ex after Mega Burst (DIAGNOSIS section 2). Q02 also went against it.
- **Amendment to DIAGNOSIS section 4's overshoot signs** (line 272, "kph abandons the Lucario hides or the Vespiquen tempo trades"), made before registration from quiz 2:
  - By design kph keeps both. Dustin chose neither (Q09 "neither": the hide "is basically wasting an energy … Next turn, that's what I would do"; Q10 "sure" against the tempo trade).
  - So neither keeping nor dropping them is a sign of anything. Both are counted in the mechanism check and reported, gating nothing.

## 4. Build and tests (the cloud)

- **Build:** on main, at the official engine's source, as a player code beside kpf/kpg.
- **Tests on constructed boards** (each board states its timing: mid-turn, or the leaf after EndTurn):
  - **A, steps = 0:** A equals R exactly.
  - **A, steps > 0:** A is never below the unprojected reading.
  - **Swablu** (deck's only evolution Mega Altaria ex [PP]) with P and Zone P: A reads 0.5.
  - **Bare Riolu** (deck's only evolution Mega Lucario ex [FF]), Zone F now and next: A reads 0 at the leaf after EndTurn and 0.5 mid-turn; R reads 0.5 and 1.0 on the same boards. If the yardstick cost on the built board isn't [FF], the expected values are recomputed from the formula above before the test runs, and the note says so.
  - **B, never slower:** B is never slower than R's clock, and equals it with an empty Bench. A B case is added to the test at 3837.
  - **B, opponent:** at the usual leaf, an opponent's qualifying benched Pokémon gets one Zone Energy, as its Active does.
  - **Dustin's Q01** (Bonsly Active, Mega Lucario ex benched with F, Zone F; Bonsly's retreat is 0): the keep-Bonsly and swap lines, built at the same leaf timing, read the same clock.
  - **Dustin's Q10, bench-feed alternative:** Shuckle ex Active with no Energy (board Retreat Cost 1), Vespiquen ex benched with G, X Speed's turn effect active, `has_retreated` = true. Vespiquen ex is not credited.
  - **Positive control:** the same board with Shuckle ex holding a G. Vespiquen ex is credited.
  - **F on:** nothing counts twice. B takes Zone Energy only, never discard-pile Energy.
  - **Opponent's side reads only its board,** following `kpr_reads_no_hidden_card` (3884).
- **Identity:**
  - kp3, k3, kpg3 and kpf3 at the kph build equal their official references on 2 pairings × 40 deals.
  - On kpg's base: kph with A and B both off equals kpf; with R off, it equals kpg.
  - On the composed base: kph with R′ off equals the composed pilot; with A and B off, it equals the composed pilot plus R.

## 5. The reading (registered on the 45 cells, RUN5 "The frame a candidate is read in")

- **Order:**
  1. **Footprint, read before anything else** (RUN5 446): the share of paired games on the 45 cells whose moves differ from the base's. Under 15%, the reserve route (a)-(e) applies; otherwise the ordinary adoption rule does. The route is fixed on that number. Expected: the ordinary rule, since B moves the defensive clock on every deck (DIAGNOSIS 263).
  2. Build, identity and tests.
  3. **Mechanism check** (diagnostic, not an adoption test): kph's mixed rows on the 840 diagnosed deals (`../kpf_2026-09-26/diagnosis/selected.json`), with dumps.
     - **Slices,** pinned to the corrected records in `../kpf_2026-09-26/diagnosis/workflow_scratch/`: `luc_rows.json` (bare Riolu, Lucario's swaps and hides), `v_rows.json` (Combee, Vespiquen's swaps and tempo trades), `sk_alt_rows.json` with `altaria_games.jsonl` (Swablu/Eevee, Altaria's swaps). `classify.py` now splits dumps where the tick restarts (the duplicate-seed fix).
     - **Denominator:** the diagnosed first-divergence positions that kph reaches with an identical board. Positions kph never reaches (it split earlier) are counted and reported, not dropped silently.
     - **Counted:** in each slice and pooled, how often kph plays kp3's move against kpf's. A's slices are Swablu/Eevee, bare Riolu and Combee; B's slice is the forward swaps.
     - **Also reported, gating nothing:** Lucario hides and Vespiquen tempo trades kept or dropped (section 3's amendment).
     - Besides that, the three decks' mixed rows on their deals not in `selected.json`.
  4. **Rayquaza pre-set check** (diagnostic, reported, never gating): the same 200 Rayquaza v Lucario deals (seeds 21,108,900,000+), kp3 on Lucario, on the official build. Paired 95% intervals for kph − kpf3 on wins and on each use rate: Scorching Interruption and Mega Burst, against kpf3's 254/262, 141/155 and 110 wins.
  5. **The 45 cells** (the table's deals and the 21,108 block), against kph's own base at the same engine (kpg3 now; the composed pilot if it is in force), by the route fixed in step 1. Under the ordinary rule:
     - paired ΔMSE with the whole 95% interval below zero;
     - vetoes: a cell's miss grows more than 6, a deck's gap more than 2, a held-out deck more than 2 further. They count only when mixed rows on the same deals show kph's own side worse beyond the row's paired noise (about ±4 at 500 games; RUN5 386-388), and never on a cell whose Limitless band is wider than about ±15. Otherwise they are investigation items.
  6. **Held-out and coverage decks, before any verdict is final:**
     - B2e's held-out archetypes (pairings 0-47): one moving more than 2 points further from its Limitless average is a veto, through mixed rows as above. Dustin's files (48-95) are reported beside.
     - The variation check's second lists and the Scizor row count for no harm only (RUN5 417). A veto there blocks the takeover; a gain is reported, not credited.
  7. **Confirmation** on Limitless events after Sept 24 (never the spent Sept 25 holdout), with size as well as direction (RUN5 390-393). Under the ordinary rule: on the post-freeze events alone, kph's τ̂ margin over its base must be at least half its development margin, with its own 90% interval above zero; the pooled figure and the sign are reported beside it. Under the reserve route: the no-harm re-check (the τ̂ margin's 90% lower bound at −1.0 or above, and no veto; RUN5 411-414).
- **Development data (RUN5 441-443):**
  - All 45 cells are development evidence for kph, as for kpg. The 18 table cells holding Altaria, Lucario or Vespiquen were used to diagnose it, and the 840 design deals sit inside their veto rows (the lowest 20 + 20 deals per cell, DIAGNOSIS 37). The 17 new cells were used to design kpf.
  - Dustin's 10 quiz positions are development data too.
  - The 45-cell verdict is read by the rule as registered; post-freeze confirmation is what makes it permanent.

## 6. What would show it wrong (stated before any game)

- **A fails:** in the mechanism check, kph plays kp3's move in half or fewer of the reached positions in any of the Swablu/Eevee, bare-Riolu or Combee slices, or pooled across them.
- **B fails:** kph still makes more than half of the reached forward swaps.
- **The harm lies elsewhere:** the Altaria, Lucario or Vespiquen mixed rows are still worse than the base beyond that deck's paired mixed-row noise, the same interval used for kpf's vetoes. The next lead is Dustin's "which piece is at risk" (the small scores favour the bigger Pokémon in front; RESULTS section 3).
- **Rayquaza's gain is reached:** the paired interval for kph − kpf3 lies wholly below zero on wins or on either use rate. Then A or B reaches the discard lines. This is reported as a finding and gates nothing.
- **No gain:** the 45-cell ΔMSE interval doesn't clear zero against the base.

## 7. Open, not in kph (recorded so they aren't lost)

- **R's tempo credit** (Q10, "sure"): kph keeps it by design (section 1). Dustin would not move Vespiquen ex up a turn early there. A later candidate, if the mechanism check shows the tempo trades still cost games.
- **kp3 skips a cheap attack at Q09** where Dustin attacks. Neither fix touches it.
- **X Speed played and not used** (Dustin, Sept 27, on Q02's game, seed 72190009, turn 2; before the bots split, so both share it):
  - The bot attached F to Hitmonlee, played X Speed, benched Bonsly, then swung Stretch Kick at an empty Bench (no effect).
  - The free retreat into Bonsly for Teary Attack (costs nothing: 10 damage, and Frigibax's attacks do −30 next turn) was there. Bonsly's retreat is 0, so Hitmonlee could come straight back.
  - Not traced yet. Possibly the free chip plus the damage shield isn't valued, or the X Speed, retreat and attack line is beyond the search.
- **Shared by both bots, outside R:**
  - Stadium denial (Training Area to remove Fragrant Forest);
  - Copycat against a small opponent hand;
  - whether the bot foresees end-of-turn Bad Dreams damage when choosing an attach (Q07's opponent).
- **Protection by points at risk and by redundancy** (Dustin, Sept 27: "If it was mega lucario that was getting hit, hiding is worthwhile because mega is 3 points and the game. You just need one riolu to survive … and you already have one on the bench riolu").
  - Whether to shield a piece should depend on its knockout points and on whether it is the only copy of the win condition.
  - The small scores the diagnosis names (safety as HP per knockout point; the Active's HP as the clock's first victim) don't read redundancy. This is a later candidate, not kph.
- **Energy on the Active as retreat fuel, and Pokémon whose job is on the Bench** (Dustin's Q08 reason, confirmed: "That deck works with darkrai on the bench, I'm trying to get him to the bench asap").
  - Darkrai's Bad Dreams works from anywhere, while Dark Slumber costs [CCC] and its Retreat Cost is 2.
  - No score reads "this Pokémon is doing its job from the Bench, get it there". This is a later candidate, related to koa's part B (not opening Darkrai).

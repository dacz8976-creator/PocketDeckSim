# Why kpf plays Altaria, Lucario and Vespiquen worse (diagnosis, Sept 27)

This covers kpf's mixed-row vetoes: its own side got worse beyond noise on Altaria (−2.5 ± 1.6 points), Lucario (−3.6 ± 1.4) and Vespiquen (−1.9 ± 1.4). None of the three lists has a recovery card, so F never fires for them and every difference comes from R.

Each deck got its own analysis, and a separate skeptic recounted every number from the dumps and checked the code. This file keeps only what the skeptics let stand, using their recounts where the two disagree. No games were run and nothing was built.

## In plain words

- **What R changes.** On all three decks, kpf takes its free or cheap attacker out of the Active Spot, or stops paying to bring it in, so that a Pokémon that still needs Energy stands there instead. The free or cheap attacker is Igglybuff, Bonsly or Shuckle ex. kpf also drops that turn's cheap attack (Sleepy Lullaby, Teary Attack, Triple Slap).
  - **kpf attacks less than kp3, not more.** At the first move where the two differ, kp3 attacks and kpf doesn't in 55 Altaria games, 138 Lucario games and 95 Vespiquen games. The reverse happens in 16, 3 and 3.
- **What hurts.** These swaps show up more in games kpf lost than in games it won.
  - The clearest harm is when the Pokémon put in front is an unevolved Basic: Swablu, Riolu or Combee. The bot is scoring it as if it were already Mega Altaria ex, Mega Lucario ex or Vespiquen ex.
  - Across the three decks that slice is 48 lost games against 16 won. Each deck's slice was found after looking at the games, so this is strong evidence but not proof.
- **Why.** R gives next turn's Zone Energy to whichever Pokémon stands in the Active Spot when the turn ends. Two parts of the bot's scoring use that credit, and each goes wrong in its own way:
  - **"Is my Active ready?"** This score measures a Basic against its evolution's attack but forgets the evolution still has to happen. With R, a Swablu holding one Energy looks as ready as a Mega Altaria ex with two. kp3 used to charge about 250 points for putting a half-ready Basic in front, and that charge disappears.
  - **"How fast can I win?"** This clock gives the credit only to the Active. A benched attacker one Energy short looks a turn slower than the same Pokémon moved up, so the bot moves it up a turn early and gives up the cheap attack.
- **Dustin's idea: right place, wrong effect.**
  - He was right that the projection wrongly assumes the Zone Energy goes to the Active.
  - The predicted behaviour is wrong: kpf attacks less, and the Pokémon holding the Active Spot need no Energy anyway.
  - His fix (project only when the Active is the side's best attacker) would miss most of the harmful swaps, because after the swap the Active is the best attacker.
  - It would also take the projection away from Mega Rayquaza ex right after Mega Burst, which is where kpf's Rayquaza gain comes from.
- **Proposed fix (reasoned from the code, untested).** Two changes to R, with no new numbers and no card lists:
  - **A.** When R judges whether a Pokémon that still has to evolve is ready, each evolution step counts as one missing Energy. That is the rule the clock already uses. The Pokémon is never judged less ready than kp3 would judge it.
  - **B.** In the clock, the Zone Energy may go to any one of your Pokémon, Bench included, whichever wins fastest. The clock is never slower than it is now.
  - Mega Rayquaza ex and Gouging Fire are Basic Pokémon that don't evolve, so fix A leaves them exactly as kpf reads them, and fix B only adds options. Rayquaza's gain should therefore survive, but that has to be checked.
  - The fix would be registered on top of kpg as a new candidate (working name **kph**).
- **Not known yet:**
  - How the swaps actually lose games. On Lucario, the Pokémon kpf put in front is not hit more often in lost games.
  - Part of Vespiquen's excess (Sabrina, move order) has no explanation through R.
  - The ten quiz positions in section 5 are the cheapest way to settle the key calls.

---

## 1. What R makes these three decks do (only patterns that survived the skeptics)

**How to read the tables.**
- Each deck has 140 "worse" games (kpf's side did worse than kp3 on that deal) and 140 "better" games: 20 of each per cell, the lowest deal numbers.
- Counts are worse/better. A pattern that hurts shows up more in worse games. A pattern present equally in both is just something kpf does differently.
- Tests: exact two-proportion (Fisher) on x/140 against y/140, or an exact sign test on the pattern games.
- Each deck was sliced 30 to 40 ways, so single p-values near 0.02 to 0.05 are weak on their own.

**Data fix, applies to all three decks.** The shared `divergences.jsonl` and `summary.txt` are wrong for 32 of the 840 records: 10 Lucario and 22 Vespiquen, none for Altaria.
- `run_dumps.sh` traced some seeds twice (pairings 2, 5 and 20), and `classify.py` joins traces by seed only.
- Every analysis below splits the dumps where the tick restarts. After that, all 840 first divergences are kpf's own decisions.
- The corrected per-game records are in the scratch folder (`luc_rows.json`, `v_rows.json`, `altaria_games.jsonl`).
- `classify.py` itself was not edited. Fix it before anyone reuses it.

### Altaria (245 divergences on Altaria's own turn: 123 worse, 122 better)

| Pattern | worse / better | Test | Reading |
|---|---:|---|---|
| kpf moves a Pokémon up (usually by retreating Igglybuff, which retreats for free) where kp3 keeps Igglybuff in front, attacks and builds the Bench | 23 / 13 | p = 0.10 | Different; not clearly harmful |
| kpf retreats, then puts the Zone Energy on the new Active, where kp3 attached to the Bench | 20 / 7 | Fisher 0.013 | **Hurts** |
| The same, whatever kp3 did | 31 / 14 | Fisher 0.008 | **Hurts** (the most robust Altaria signal) |
| The Pokémon kpf feeds in front is an unevolved Swablu or Eevee, which then uses Sing or Stampede (Swablu alone 12/2) | 15 / 3 | Fisher 0.006 | **Hurts, suggestive**: found after looking; fades to 23/12 when widened, and 21/20 for just ending the turn with one in front |
| Dustin's pure form: kpf feeds the Active it already has, where kp3 builds the Bench | 17 / 14 (13/12 with no retreat anywhere in the turn) | n.s. | Not what hurts |
| Feeding Darkrai, by any route | 16 / 14 | n.s. | Not what hurts |
| Who to promote after a knockout | 15 / 15 | n.s. | Neutral |
| Opposite direction: with a 0-Energy Espeon in front, kpf feeds a benched Mega Altaria ex and skips Hypnoblast (counted in turns) | kpf 14/50 turns in worse games, 12/45 in better; kp3 0/29 and 1/30 | n.s. between worse and better | Different (about 27% v 2% of such turns); neutral |
| Attacks at the divergence: kp3 only v kpf only | 55 v 16 games | | kpf attacks less |

Notes:
- The harmful cases are spread across all seven opponents.
- The skeptic's recounts replace several of the analyst's numbers: retreat-then-feed 20/7, not 23/9; pure form 17/14, not 14/12.
- The "Bench to Active" row (37/21) is fragile. If you count where the Energy is at the end of the turn it becomes 33/20 (p 0.06 to 0.10), and the whole 5-way table is not significant (p ≈ 0.19). It is left out above for that reason.
- Losing Sleepy Lullaby is not what separates worse from better games: kpf uses Lullaby 0.26 times less per game in worse games and 0.24 times less in better games.

### Lucario (280 games, all divergences on Lucario's own decisions after the data fix)

| Pattern | worse / better | Test | Reading |
|---|---:|---|---|
| **Direction of the front-line change.** kpf moves the Riolu line forward with a wall behind it, or hides it behind a wall | worse 58 forward / 15 back; better 35 / 30 | z = 3.20, p = 0.0014 | **Hurts** (the strongest signal of the whole diagnosis) |
| kpf ends the turn with Riolu, Mega Lucario ex or Lucario in front where kp3 keeps Bonsly or Hitmonlee there | 58 / 35 | z = 2.92, p = 0.004 | **Hurts** |
| … with a bare Riolu in front | 24 / 11 | sign p = 0.04 | **Hurts** |
| … with Mega Lucario ex or Lucario in front | 34 / 24 | sign p = 0.24 | Not significant alone |
| kpf's first differing move is a Retreat | 55 / 31 | p = 0.002 | **Hurts**, as part of the same event |
| kpf retreats a wall into Riolu or Mega Lucario ex and kp3 doesn't (kp3 makes that retreat in 6 and 6 games) | 36 / 19 | p = 0.011 | Hurts, as part of the same event |
| Mirror: kpf puts a wall in front where kp3 leaves the Riolu line. Usually F goes on the Active Riolu, then Riolu retreats paying with it (11 of 15, 25 of 30) | 15 / 30 | z = −2.44 | **Helps** |
| Bonsly in front at the divergence ("Teary Attack dropped", 57/36, restates this) | 43 / 27 | z = 2.21 | Hurts, as part of the same event |
| With the Zone Energy still unused: kpf's ends the turn on its Active, kp3's goes elsewhere (the reverse is 17/25) | 41 / 25 | z = 2.27 | Weak; part of the forward swap |
| Dustin's exact failure: retreat into a bare Riolu, the Zone Energy credited mid-turn, then attached on the Bench, Riolu left with nothing | 6-7 / 0 (9/0 loosely) | sign p 0.016-0.031 | Real but small; defined after looking |
| First Zone attach to the Active under kpf, to the Bench under kp3 | 47 / 45 | n.s. | Different; neutral |
| Hitmonlee in front with no Energy: kp3 feeds it and uses Stretch Kick; kpf builds the Riolu line and doesn't attack | 11 / 17 | n.s. | Different; neutral (kpf builds here) |
| Attacks at the divergence: kp3 only v kpf only | 138 v 3 games | | kpf attacks less |

Notes:
- **Refuted:** "the attacker kpf exposed got hit or knocked out before its next turn" does not tell worse from better games (37/57 v 20/35, p = 0.46), and a knockout that fast is rare (4/57 v 2/35). The data show that the forward swap hurts, not how.
- The excess against Hydreigon, Sceptile and Suicune only (31/41 v 27/52, p = 0.02) was a grouping chosen after looking. Suggestive only.

### Vespiquen (280 games, all divergences on Vespiquen's own decisions after the data fix; all 3,500 deals: 465 worse / 388 better, net −2.2 points)

| Pattern | worse / better | Test | Reading |
|---|---:|---|---|
| kp3 attacks (almost always Shuckle ex's Triple Slap); kpf skips the attack and feeds Vespiquen ex or Ogerpon ex (the reverse is 2/1) | 48 / 47 | p = 1.0 | Different; not what hurts |
| Whole game: kpf attacks on 71.0% of Zone turns v 88.3%; Triple Slaps 569 → 261 | | | Different. The worse/better split is fully explained by winners attacking more, so this is not evidence of harm |
| **Zone Energy on a 1-cost Pokémon in front in both games, but the games differ.** Contents: kpf keeps Combee in front and attacks where kp3 plays X Speed into Shuckle ex (9/2, plus 1); kp3 plays Sabrina and kpf doesn't (7/1); pure reorders (11/5); other small differences (10/6). Opening turns 2-3, 6 of 7 opponents | 37 / 14 (26/9 without reorders) | Fisher 0.0006 (binomial 0.002) | **Hurts**: the only Vespiquen result that passes a 40-test correction, and only on Fisher |
| Both bots feed a 1-cost Active and attack, but differ in more than move order (overlaps the row above) | 24 / 8 | Fisher 0.004 | Hurts; mixed contents |
| Combee attacks (Reckless Charge) where kp3 plays X Speed into Shuckle ex | 9/2 strict (p 0.06); 11/4; 12/5 | | Direction holds; not significant alone |
| "Same plan, different slot": kpf retreats Shuckle ex, puts Vespiquen ex/Ogerpon ex in front and feeds it there, where kp3 chips and feeds it on the Bench | 14/7 strict, 16/8 loose | p ≈ 0.15-0.19 | Not beyond chance |
| Tempo trade: kpf feeds the main attacker in front a turn sooner, where kp3 feeds a 0-Energy Shuckle ex or Combee and attacks | 19 / 25 | p = 0.41 | Neutral, leaning helpful |
| Turn 1 with no Zone Energy: kpf ends with Shuckle ex in front | 26 / 30 | n.s. | Neutral |
| Pure reorders | 16 / 11 | n.s. | Noise |
| Attacks at the divergence: kp3 only v kpf only | 95 v 3 games | | kpf attacks less |

Note: the reading gave −1.9 ± 1.4 for Vespiquen, and the analyst's recount of all 3,500 deals gives −2.2. The two may count ties or average cells differently. This was not checked further.

---

## 2. Does Dustin's hypothesis hold?

The hypothesis: the projection assumes the turn's Zone Energy goes to the Active. For a deck that builds its Bench while the Active stalls, that credits the Active with readiness it won't have. The bot then attacks, or commits to the Active, when it should build.

| Deck | Verdict (after the skeptic) | Why |
|---|---|---|
| Altaria | **Partly supported** | kpf does commit the Zone Energy to the Active Spot where kp3 builds, but the excess comes only through retreat-then-feed (31/14). The pure form, feeding the Active it already has instead of the Bench, is balanced (17/14). kpf attacks less, not more. |
| Lucario | **Partly supported** | The Riolu line moved forward where kp3 builds behind a wall is the strongest signal (z = 3.2). But the credit doesn't go to the stalling Pokémon: Bonsly's attack is free and reads ready either way. kpf moves the attacker up to collect the credit. kpf attacks less (138 v 3). |
| Vespiquen | **Not supported** | The stalling Pokémon, Shuckle ex, costs one Energy and usually already has it, so extra credit on it changes nothing. kpf attacks less (95 v 3). "Commit to the Active when kp3 builds" is 18/10 (p ≈ 0.16). The significant excess comes through Combee's readiness score, Sabrina and move order. |

**Overall: not supported as stated, though its premise is right.**
- The premise holds. The projection gives the Zone Energy to the Active Spot and nowhere else. That is the root of all three decks' problems.
- The predicted effect is wrong in two ways:
  1. The bot attacks less, on every deck.
  2. The stalling Pokémon (Igglybuff, Bonsly, Shuckle ex) need no extra Energy, so crediting them changes nothing.

**What the data point to instead.** The credit goes to whoever ends the turn in the Active Spot.
- Altaria and Lucario pay a free retreat to put an Energy-hungry Pokémon there. Vespiquen stops paying an X Speed to take one away.
- Either way, the front line ends the turn with a Pokémon that isn't ready, and the cheap attack is dropped.
- The harm concentrates where that Pokémon is an unevolved Basic scored against its evolution's attack: Swablu 15/3, bare Riolu 24/11, Combee 9/2. Pooled, that is 48/16, p ≈ 0.0001 if it had been planned; it wasn't.

**Why Dustin's gate is not the fix.** The gate: project the Zone attach only when the Active is the side's best attacker by the evaluator's own reckoning.
- **Lucario and Vespiquen:** after the harmful swap, the Active is the best attacker (Mega Lucario ex with F, Vespiquen ex with G), so it keeps its credit. Nothing changes.
- **Lucario's helpful hides:** a Hitmonlee with no Energy is not the best attacker, so it would lose its credit and read 0 instead of 1.0, worth 500 points. That pushes toward the harmful swaps and away from the helpful hides (15/30).
- **Altaria:** the gate would work only through a quirk of the threat pick: a free 10-damage attack outranks a 40-damage attacker one Energy short. It would also change about half of all Altaria positions, in won and lost games alike.
- **Rayquaza:** checked by "the evaluator's own reckoning" without the projection, a Mega Rayquaza ex right after Mega Burst is never the best attacker.
  - Its Mega Burst is estimated as 50 × the [R] and [L] Energy attached, which is 0 after discarding, and the clock skips attacks estimated at 0.
  - So the gate would switch off R exactly where R made Rayquaza attack. The same happens to Gouging Fire left with one Energy after Scorching Interruption.
  - Using the projected reading instead would not rescue the gate on Lucario and Vespiquen, because of the first point.

---

## 3. The mechanism, in code terms

All references are to `engine/src/players/value_functions.rs` at kpf's build.

**The root.**
- `projected_active_energy_and_discard` (2223-2311) adds the side's future Energy to one Pokémon, the one passed in, which is always the Active (slot 0). That Energy is this turn's unused Zone Energy while the turn runs, next turn's Zone Energy, and Active-only Ability Energy.
- Attaching the Zone Energy anywhere clears `current` (`state/energy.rs` 27). So feeding the Bench also takes a projected Energy away from the Active.
- At the usual leaf, scored after the owner's EndTurn, R adds exactly next turn's Zone Energy to whoever stands in the Active Spot. Benched Pokémon get nothing, even one the Active could retreat into for free next turn.

**Channel 1: the Active's readiness score.**
- `calculate_active_pokemon_online_score` (2111-2127) is projected whenever R is on (577 in setup, 610 in play). Its weight is 500 (line 51).
- It calls `pokemon_online_score` (2340-2412), which measures the Pokémon against its highest evolution in the owner's deck and hand (2361-2370). The effect-aware yardstick is that evolution's best payable attack.
- It never counts the evolution step still to take.
- Under kp3:
  - a Swablu with P reads 0.5 against Mega Harmony [PP];
  - a Riolu with F reads 0.5 against [FF];
  - a Combee with G reads 0.5 against Chase Order [GG].
- Under R, next turn's Energy makes all three read 1.0, the same as Igglybuff or Bonsly, whose empty cost always reads 1.0 (2401-2402).
- So the 250-point charge kp3 made for putting a half-ready Basic in front disappears. The front line is then decided by small terms:
  - `active_safety` = HP per knockout point (2095-2104);
  - the Active's HP as the first victim in the opponent's clock (100 per turn).
- Both favour the bigger Basic over Igglybuff (30 HP) or Bonsly (30 HP).
- Mid-turn, with the Zone Energy unused, even a Riolu with no Energy reads 1.0 (two credited). That produces Lucario's 6-7 "credited, then attached on the Bench" games.

**Channel 2: the clock.**
- `turns_until_opponent_wins_scan` projects slot 0 only (line 984: `Some(horizon) if slot == 0`).
- It picks the threat by fewest missing Energy first, then most damage (1018).
- `calculate_turns_until_opponent_wins_damage_aware` takes the smaller of the clocks with and without projection (943-946). Weight 100 per turn (line 55).
- A benched attacker one Energy short reads 1 missing, so a free chip attack (0 missing) stays the threat. Moved into slot 0, the same attacker reads 0 missing at full damage.
- Worked by hand (not evaluator output):
  - **Lucario 72130094 t3:** swapping Bonsly for Mega Lucario ex takes the clock from about 15-16 turns to about 2, roughly +1,300 points.
  - **Vespiquen 72200103 t4:** about +300.
  - **Altaria 72000056 t4:** Darkrai moved up early reads 0 missing at 40 damage instead of Igglybuff's 10.
- In each case kp3's line reaches the same attack next turn with a free or affordable retreat, but gets no credit, because only slot 0 is projected.
- The code's own test `the_clock_counts_the_active_threats_energy_at_its_next_attack` (3816-3827) says "Only the Active is projected".

**The opposite direction (neutral).** Because R promises next turn's Energy to the Active every turn, an Active that could attack now with this turn's Energy counts as ready anyway. kpf then spends the real Energy on the Bench and skips the attack:
- Altaria's 0-Energy Espeon, 27% of such turns v 2% for kp3;
- Lucario's Hitmonlee cases.
Neither is harmful in the data.

**Is it one mechanism?** One root (the credit belongs to the Active Spot), two channels, weighted differently by deck:

| | Channel 1: readiness score (Basic scored as its evolution) | Channel 2: clock (credit only in slot 0) |
|---|---|---|
| Altaria | Swablu or Eevee fed in front, 15 / 3 (post hoc) | Darkrai moved up a turn early: seen in the boards, 4 / 1, not shown to hurt |
| Lucario | Bare Riolu forward, 24 / 11 | Mega Lucario ex or Lucario forward, 34 / 24 (n.s.) |
| Vespiquen | Combee kept in front instead of X Speed into Shuckle ex, 9 / 2, inside the 37/14 cell | Vespiquen ex or Ogerpon ex moved up early, 14 / 7 (n.s.) |
| Pooled (exact binomial, slices chosen after looking) | **48 / 16, p ≈ 0.0001** | 52 / 32, p ≈ 0.04 |

Channel 1 carries the clearer harm on all three decks. Channel 2 carries the biggest behaviour change: Lucario's forward swaps and Vespiquen's early moves.

Not explained by either channel:
- Vespiquen's Sabrina difference (7/1) and its reorders (11/5);
- the Lucario analyst's term sizes, which are hand arithmetic; nobody reconstructed which search leaf won each decision.

---

## 4. Proposed correction: candidate kph = kpg + R′

**Principle.** R promises a Pokémon the Energy it will really have by its next attack. Two things break that promise, and the fix repairs both from rules the evaluator already has:
- the Energy is credited to a slot, not to the Pokémon it will go to;
- a Basic is credited as if it were already its evolution.

The fix adds no constant and no card or list reading. It uses only public information, plus the owner's own deck and hand, which the readiness score already reads.

**Definition (precise enough to register).** `kph<N>` is `kpg<N>` (kp + F, unchanged) plus R′. R′ is kpr's projection exactly as built (`projected_active_energy`, its horizons, amendment 5), used in the same two places, with two changes, each behind its own switch.

**A. Evolution-aware readiness, in `calculate_active_pokemon_online_score` with a horizon.**
- Let `target` be the yardstick card `pokemon_online_score` already chooses: the highest evolution in the owner's deck and hand, or the card itself.
- Let `steps` = `target.stage − active.stage`, which is 0 when `target` is the card itself.
- On the projected Pokémon, the projected reading is `clamp((total − missing − steps) / total, 0, 1)`.
- The score used is the larger of that and the unprojected reading, which is kp3's.
- When `steps` = 0 this is R exactly. The reading always lies between kp3's and R's.
- This is the clock's own rule: its evolution-aware scan counts each step still to take "as one more turn, the same unit as missing energy" (909-912 and 1009-1010). The readiness score now agrees with the clock on when a Basic can use its evolution's attack.

**B. The Zone Energy belongs to the side, in `calculate_turns_until_opponent_wins_damage_aware` with a horizon.**
- `clock = min(clock(None), clock(Active projected as now), min over each benched Pokémon s of clock(s given the Zone Energy only))`.
- **Zone Energy for s:** the same Zone terms the Active gets at that horizon. That is this turn's unused `current` while the owner's turn runs, then `next` where the horizon includes next turn.
- **Blocking effects:** a turn effect that blocks Zone attaches only to the Active (`NoEnergyFromZoneToActive`) does not block s.
- **Ability sources** stay Active-only, as now.
- Both sides, each at its current horizon. The opponent's side stays board-only.
- Taking the minimum over recipients, instead of projecting every Pokémon in one scan, is deliberate. A single scan could let a weak benched Pokémon that becomes 0 missing displace a stronger Active that is still short, and so make the clock slower. That is the failure the comment at 915-917 and the test `the_clock_never_gets_slower_for_the_projection` guard against. With the minimum, the clock is never slower than R's.

**What each change should do** (reasoned from the code and the boards; nothing was run):
- **A:**
  - Swablu with P and Zone P reads 0.5 again. The retreat into Swablu to Sing loses its 250 points.
  - A bare Riolu with F reads 0.5, and one with nothing reads 0 (R gave 0.5 to 1.0), so Bonsly stays in front.
  - Combee with G reads 0.5, so paying X Speed to put Shuckle ex in front is worth it again.
  - Lucario's helpful hides stay and get stronger: Hitmonlee, which does not evolve, keeps its 1.0, while the Riolu it would replace now reads less.
  - Espeon, Mega Altaria ex, Vespiquen ex, Ogerpon ex and Mega Lucario ex have nothing left to evolve into, so they read as under R. Vespiquen's tempo trades (19/25) are untouched.
- **B:**
  - In 72130094, the benched Mega Lucario ex with F is credited FF in kp3's line too. Both lines' clocks match, the roughly 1,300-point pull disappears, and the remaining terms favour keeping Bonsly and attacking.
  - The same holds for Darkrai behind Igglybuff (Altaria) and Vespiquen ex behind Shuckle ex (72200103).
  - A benched attacker with no Energy is still credited only one, so feeding the main attacker in front a turn sooner still wins the clock. The tempo trade is kept.
- **Not addressed:**
  - Vespiquen's Sabrina and move-order differences;
  - the Espeon "ready anyway" pattern (neutral);
  - the threat pick's quirk that a free 10-damage attack outranks a bigger attacker one Energy short. That quirk is older than R and also affects kp3; it is a separate change.

**How it keeps Rayquaza's gain.**
- `lib/card.py` gives Mega Rayquaza ex as Stage 0 and Gouging Fire as a Basic, and the list has nothing that evolves from either. So `steps` = 0 for both, and A leaves their readings exactly as kpf reads them after Mega Burst or Scorching Interruption.
- B leaves the Active term of the clock unchanged and only adds recipients, so it can only make a clock faster. After a discard attack, the drained Active is where R's credit mattered, and that credit is untouched. If anything, B makes the discard line's clock faster still.
- **Two residual risks:**
  1. B also speeds the no-attack line wherever a benched Pokémon one Zone Energy short is the fastest threat.
  2. A takes back R's credit for a Dratini in front, since Dragonair is its evolution.
- **Pre-set check:** in the 200 Rayquaza v Lucario traces, kph's Scorching Interruption and Mega Burst use and wins must stay within noise of kpf3's (254/262, 141/155, 110 wins).

**Variants considered and not chosen:**
- **Waive A's step when the evolution card is already in hand.** A Basic can evolve and attack in the same turn, so this is closer to R's promise. It is equally free of constants, but it keeps more of R. The dumps hide hands, so the data can't choose between the two. A as stated reuses the clock's existing rule and is the conservative choice.
- **Limit B to Pokémon the Active can retreat into with the Energy it holds.** The clock already lets a benched Pokémon attack without paying a retreat. In every diagnosed case the retreat was free (Igglybuff, Bonsly) or paid from Energy the Pokémon held (Shuckle ex). So this adds a rule and changes none of the diagnosed cases.
- **Dustin's gate** (section 2).

**Registration details.**
- Diagnostic codes: `kph` with only A, and `kph` with only B. Run them only if the reading needs attribution.
- The code name `kph` is unused today (searched). The builder confirms it doesn't shadow a parser prefix: `kpf`/`kpg`/`kpr`/`kp` are matched in `players/mod.rs` 233-260.
- Tests on constructed boards:
  - A equals R when steps = 0, and A is never below the unprojected reading;
  - Swablu with P and Zone P reads 0.5;
  - B is never slower than R's clock, and equals it with an empty Bench;
  - with Bonsly Active, Mega Lucario ex benched with F and Zone F, the keep-Bonsly and swap lines read the same clock;
  - with F on, nothing is counted twice. B takes Zone Energy only, never discard-pile Energy.
- **Footprint warning.** B changes the defensive clock too: the opponent's benched attackers now get their Zone credit. That will move games on every deck. It needs the full 45 cells, mixed rows and the coverage decks, under the existing rule.

**Suggested order, cheapest first:**
1. Dustin answers the quiz below.
2. After the build, a mechanism check on the 840 diagnosed deals: kph's mixed rows with dumps, compared at the same first-divergence positions. This is a diagnostic, not an adoption test.
3. Register, one review, then the 45 cells.

**Stated before any game: what would show the diagnosis or the fix wrong.**
- On the 840 deals, kph still plays kpf's move in most of the Swablu/Eevee, bare-Riolu and Combee positions. Then A isn't doing what section 3 says.
- kph abandons the Lucario hides or the Vespiquen tempo trades. Then A or B overshoots.
- The Altaria, Lucario or Vespiquen mixed rows are still worse than kp3 beyond noise. Then the harm lies elsewhere, for example in how the exposed attacker is lost, which the data never showed.
- Rayquaza's traces fall back toward kp3's. Then B or A reaches the discard lines.

---

## 5. Quiz positions for Dustin

All come from analysts' suggestions that their skeptics checked line by line against the dumps and did not reject.
- Each is the first move where kp3 and kpf differ, so the board before the move is the same in both games. `dump_base.txt` shows it.
- For 72050138 and 72200103, the kpf-on-Vespiquen game is the **second** copy of the seed in `dump_kpf.txt` (from lines 23256 and 51610). For 72050131, the Altaria game is the first copy (from line 21027).
- Choice 1 is always kp3's move and choice 2 is kpf's. Ask him blind, without saying which bot played which. The italic notes are for the record, not for the quiz.

1. **72130094, turn 3. Lucario v Hydreigon (a worse game).**
   - Board: Bonsly 30 HP in front with no Energy; Riolu 60 on the Bench; Mega Lucario ex in hand; Fighting Zone Energy now and next turn. Both bots also play Professor's Research.
   - Opponent: Mega Absol ex 160 HP with one [D] in front; Deino on the Bench.
   - Choice 1: evolve Mega Lucario ex on the Bench, attach F to it, Teary Attack.
   - Choice 2: retreat Bonsly for free, evolve Mega Lucario ex in the Active Spot, attach there, no attack.
   - *Decides fix B.* If he picks 1, the clock's slot-only credit is the error. If he picks 2, moving the Mega up is right and the Lucario harm lies elsewhere.
2. **72190009, turn 4. Lucario v Suicune (worse).**
   - Board: Hitmonlee 80 HP with one F in front; Bonsly and Riolu on the Bench; Mega Lucario ex available; Zone F.
   - Opponent: Baxcalibur 140 with [WW] in front; Suicune ex and Frigibax on the Bench.
   - Choice 1: Professor's Research, evolve on the Bench, attach F to the benched Mega, Stretch Kick.
   - Choice 2: pay Hitmonlee's retreat, Mega Lucario ex in front with one F, no attack.
   - *Decides fix B when the wall's retreat has to be paid, and bears on Dustin's gate*, which would strip Hitmonlee's credit here. In kpf's game the Mega had taken 90 by its next turn.
3. **72080079, turn 2. Lucario v Blaziken (worse).**
   - Board: Bonsly in front; Riolu on the Bench; Zone F.
   - Opponent: Heatmor 80 HP with no Energy; Castform Sunny Form on the Bench.
   - Choice 1: attach F to the benched Riolu, Copycat, bench a second Riolu, Teary Attack.
   - Choice 2: retreat into Riolu, attach F, Fighting Fist for 10.
   - *Decides fix A* (a bare Basic put in front). The clock is not the driver here.
4. **72050131, turn 2. Altaria v Vespiquen (worse).**
   - Board: after Professor's Research, Igglybuff 30 HP in front; two Swablu in hand or on the Bench; no Energy anywhere.
   - Opponent: Shuckle ex 120 in front; Combee, Shuckle ex and Combee on the Bench.
   - Choice 1: bench both Swablu, attach P to a benched Swablu, Sleepy Lullaby.
   - Choice 2: retreat Igglybuff into Swablu, attach P to it, Sing.
   - *Decides fix A for Altaria* (the Swablu slice, 15/3).
5. **72160098, turn 2. Vespiquen v Hydreigon (worse).**
   - Board: Combee 40 HP in front; nothing on the Bench; Zone G; hand of five: Shuckle ex, X Speed, Leaf Cape, Fragrant Forest, Field Blower.
   - Opponent: Mega Absol ex 170 with two Deino on the Bench.
   - Choice 1: bench Shuckle ex, Leaf Cape on Combee, X Speed, retreat into Shuckle ex, attach to it, Triple Slap.
   - Choice 2: attach G to Combee, Leaf Cape on Combee, Reckless Charge; Shuckle ex stays on the Bench.
   - *Decides fix A for Vespiquen*, inside its only significant excess (37/14).
6. **72200103, turn 4. Vespiquen v Lucario (worse).**
   - Board: Shuckle ex 120 with [G] in front; Combee on the Bench; Vespiquen ex in hand; Zone G.
   - Opponent: Mega Lucario ex 170 with [F] in front; Riolu and Hitmonlee on the Bench.
   - Choice 1: evolve Combee on the Bench, attach to it, Triple Slap.
   - Choice 2: retreat Shuckle ex (discarding its G) into Combee, evolve in the Active Spot, attach there, no attack.
   - *Decides fix B for Vespiquen.* Is moving Vespiquen ex up a turn early ever right here?
7. **72000056, turn 4. Altaria v Blaziken (worse; Altaria has 1 point).**
   - Board: after Copycat, Igglybuff 30 HP in front; on the Bench, Darkrai 100 with no Energy, Swablu 50, and Darkrai 100 with P; Zone P.
   - Opponent: Torchic 60 HP with no Energy in front; Mega Blaziken ex 210 on the Bench.
   - Choice 1: attach to the benched Darkrai that has P (now PP), Sleepy Lullaby.
   - Choice 2: retreat Igglybuff into that Darkrai, attach (PP), no attack.
   - *Decides fix B for Altaria, and is Dustin's own scenario.* kp3 moved Darkrai up the next turn anyway, and its Lullaby plus Bad Dreams took Torchic a turn earlier.
8. **72010118, turn 3. Altaria v Hydreigon (worse).**
   - Board: Darkrai 80 HP with no Energy in front; Swablu 50 and Darkrai 100 on the Bench, neither with Energy; Zone P.
   - Opponent: Deino 60 HP with [D] in front; another Deino on the Bench.
   - Choice 1: attach to the benched Swablu (towards Mega Altaria ex).
   - Choice 2: attach to the Active Darkrai (towards Dark Slumber).
   - *Tests Dustin's hypothesis in its pure form*, which is balanced in the data (17/14). If he calls choice 2 a clear mistake, the balanced count means the evaluator gets this spot wrong under both bots.
9. **72020118, turn 2. Lucario v Altaria (a better game; the helpful side).**
   - Board: Riolu 60 with no Energy in front; Hitmonlee 80 and Riolu on the Bench; Zone F.
   - Opponent: Swablu in front; Eevee and Darkrai on the Bench.
   - Choice 1: attach F to the benched Hitmonlee and keep Riolu in front.
   - Choice 2: attach F to Riolu, then retreat Riolu behind Hitmonlee, paying with that F.
   - *Checks what the fix must keep.* The fix predicts choice 2 becomes more likely. If Dustin prefers choice 1, the helpful pattern is luck.
10. **72050138, turn 3. Vespiquen v Altaria (a worse game, from the pattern that leans helpful).**
    - Board: Teal Mask Ogerpon ex 160 HP with no Energy in front; X Speed already played; on the Bench, Shuckle ex 120, Vespiquen ex 170 and Shuckle ex 120; no Energy anywhere; hand empty.
    - Opponent: Darkrai 100 in front; Swablu 50 with P on the Bench.
    - Choice 1: retreat into Shuckle ex, attach, Triple Slap.
    - Choice 2: retreat into Vespiquen ex, attach, no attack.
    - *Checks R's tempo credit*, which the fix keeps. If Dustin picks choice 1, the tempo trade is not worth keeping either.

---

## 6. Caveats and what remains unknown

1. **Nothing was run.**
   - The mechanism is argued from the code and hand arithmetic. The term sizes (+250, about +300, about +1,300) are not evaluator output, and nobody reconstructed which search leaf won each decision.
   - The fix's effect on any deck, Rayquaza included, is a prediction.
2. **Sampling.**
   - The 20 worse and 20 better games per cell are the lowest deal numbers, not a random draw.
   - The counts show which patterns go with a worse result, not what share of each deck's loss each pattern causes.
   - "Worse" labels the whole game, so the first divergence need not be the move that decided it.
3. **Multiple comparisons.** Each deck was sliced 30 to 40 ways. What clears a strict correction:
   - Lucario's forward-against-backward split (p = 0.0014);
   - Vespiquen's 37/14 cell, on Fisher only.
   Altaria's best result is p = 0.008. The pooled "unevolved Basic in front" figure (48/16) adds up three slices that were each chosen after looking.
4. **How the harm happens is not shown.** On Lucario the exposed attacker is not hit or knocked out more often in lost games. "The wall should take the next hit" is a guess.
5. **Hidden hands.** The dumps show hand size only. Some of kpf's choices may be justified by cards in hand, for example whether Mega Altaria ex was there when Swablu went forward. This is also why fix A's in-hand variant can't be judged from this data.
6. **Unexplained residue.** Vespiquen's Sabrina difference (7/1) and reorders (11/5) have no R mechanism identified. They may be search noise from a changed score, not a pattern.
7. **Whole-game counts are confounded by the outcome**, because winners attack more. Examples: Vespiquen's attack rate 88% → 71%; Altaria's Sing +0.37 per game in worse games. They describe what kpf does differently, not harm.
8. **Fix side effects.**
   - B changes the opponent-threat clock for every deck.
   - A changes how every Basic with an evolution is read in front under R. For example, Hydreigon's Deino goes back toward kp3's reading. Hydreigon's R gain came from Hyper Ray, fired by an evolved Pokémon, so it should be untouched, but that is unchecked.
   - Both need the full table, mixed rows and coverage decks.
9. **Pipeline bug.** `classify.py` joins duplicate-seed traces (32 records wrong: 10 Lucario, 22 Vespiquen). It was not edited here. Fix it before it is reused.

## Files

All scratch files are in `workflow_scratch\`:
- **Altaria analysis:** `alt_*.py`, `altaria_games.jsonl`, `better_BA.txt`.
- **Lucario analysis:**
  - scripts: `luc_*.py`;
  - corrected records: `luc_rows.json`;
  - parsed traces: `luc_games.pkl`;
  - runner: `luc_run.sh`;
  - readable stories: `luc_read.py`.
- **Vespiquen analysis:** `v_*.py`, `v_rows.json` (corrected records), `v_cls.json`, `v_worse.txt`, `v_better.txt`.
- **Skeptics:** `sk_alt_*.py` (`sk_alt_pat.py` is superseded by `sk_alt_pat2.py`), `sk_luc_*.py` with `sk_luc_games.pkl`, `vsk_*.py`.
- **This synthesis:** `syn_cards.sh` (card texts for the cards cited in sections 3 and 4) and `syn_binom.py`/`syn_binom.sh` (the pooled binomials).

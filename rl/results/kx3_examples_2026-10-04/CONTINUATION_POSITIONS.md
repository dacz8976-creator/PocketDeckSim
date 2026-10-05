# Positions for the continuation experiment (laptop Opus, Oct 5)

For the cloud's experiment: take the same first move, then continue it two ways, and compare.
- **(a) km3's continuation:** km3 plays every later decision, as kx3's play-outs do today.
- **(b) the plan's continuation:** the intended plan is played out for the next own turns, with km3 filling every decision the plan doesn't name, and on both sides after the plan ends.

The question is whether km3's later play hides good first moves, as the examples suggest. That answers item 4 of the Oct 2
approval (DESIGN.md section 9).

All eight positions are exact-list (`B-` ids): draft A against the fixed computer deck Mega Blastoise ex / Wailord ex,
Step-Up Battle: Advanced, Soothing Shore in play.
- **Positions:** `rl/results/pause_games_decisions_2026-10-02/positions_kx.json`. The opponent list is
  `decks/computer/blastoise-wailord-deluxe.txt` (the `BL` filler).
- **Game records:** each position's game is in the Battle Logs batch `BATCH_2026-10-02_DRAFT_A_V_BLASTOISE_WAILORD`, as a turn ledger and review.
- **Checked descriptions:** `../playout_pilot_positions_2026-10-04/EXAMPLES_SOURCE.md`, which has the board, hand and both
  pilots' choices for each.
- **Excluded on purpose:** positions from Dustin's 3-0 games where every move already won all 16 play-outs (for example
  B-215203-t06 and B-215825-t06). A decided position can't show hiding.

**How to script a plan.** Write each step at the level of intent ("put the turn's Water on the Benched Vulpix", "evolve
that Vulpix when Alolan Ninetales ex is in hand"), not as fixed action indices. Draws and coins differ between sampled
worlds. If a step isn't legal in a world (the card wasn't drawn, a coin went tails), skip it and let km3 decide that step;
count how often that happens. Each step below is what the recorded game did. The steps after the first are the plan to
script.

| # | Position | Decision maker, result | Milestone | The plan's first move | km3's first move |
|---|---|---|---|---|---|
| 1 | B-214254-t06 | Dustin, won 3-0 | preparing an attacker | the turn's Water on the Benched Vulpix | Turbo Shark at once (the Water is never attached) |
| 2 | B-214254-t10 | Dustin, won 3-0 | keeping a damaged attacker in front | Lucky Ice Pop (then Irida) on the Active Mega | Irida, then the Pops (same HP); skips the turn's Water |
| 3 | B-205731-t08 | Auto, won 3-2 | preparing an attacker; managing a sacrifice | evolve the Benched Vulpix into Alolan Ninetales ex, keeping the damaged Mega in front | retreat now into the Vulpix and evolve it in the Active Spot |
| 4 | B-205731-t10 | Auto, won 3-2 | preparing an attacker; managing a sacrifice | bench the Alolan Vulpix and give it the turn's Water | retreat first; Copycat in 5 of 12 seeds |
| 5 | B-210952-t14 | Auto, lost 2-3 | preparing an attacker | bench Carvanha and give it the turn's Water | the same, plus Elegant Cape on the Ninetales ex (kx3 retreated and passed: a failure) |
| 6 | B-210952-t16 | Auto, lost 2-3 | preparing an attacker; adapting | bench the Alolan Vulpix | the same line plus Elegant Cape on the Active Ninetales ex (kx3 attacked at once in 2 of 3 seeds) |
| 7 | B-210952-t18 | Auto, lost 2-3 | preparing an attacker (denial) | Misty on the Vulpix, keeping Mega Blastoise ex Active under Binding Snow (kx3's line) | Cyrus on the 20-HP Baxcalibur, then the knockout (Auto's line, which lost) |
| 8 | B-205731-t02 | Auto, won 3-2 | early development | the turn's Water on the Active Carvanha, then Sharp Fang | Copycat |

## The plans, step by step

**1. B-214254-t06.** Active: Mega Sharpedo ex with Elegant Cape (220 HP, 1 Water). Bench: Carvanha (1 Water) and Alolan Vulpix (1 Water). Turn 6, 0-0.
- Turn 6: the turn's Water on the Vulpix, then Turbo Shark, whose extra Water goes to the Vulpix (3 Water).
- Turn 8: evolve Carvanha into Mega Sharpedo ex and give it the turn's Water. Turbo Shark, extra Water to the Vulpix (4).
- Turn 10: Turbo Shark, extra Water to the Vulpix (5).
- Turn 12: evolve the Vulpix into Alolan Ninetales ex, retreat the Mega for free (Retreat Cost 0) into it, then Binding Snow. Bench a second Vulpix if one is in hand.
- kx3's play-outs tied the Water-first line with km3's attack-first line: 0.938 v 0.938, 0.750 v 0.750, 0.750 v 0.688.

**2. B-214254-t10.** Active: the Caped Mega Sharpedo ex at 120 of 220 HP, 1 Water. Bench: a second Mega Sharpedo ex (190, 2 Water) and an Alolan Vulpix with 4 Water. The computer's Wailord ex (250 HP, 4 Water) does 100 a turn.
- Turn 10: Lucky Ice Pop, then the second Pop if the first comes back, then Irida (up to 200). The turn's Water on the Mega. Turbo Shark (Wailord to 180), extra Water to the Vulpix (5).
- Turn 12: draw (Professor's Research, Poké Ball if drawn), evolve the Vulpix into Alolan Ninetales ex, retreat the Mega for free into it, then Binding Snow.
- Turns 14 and later: Binding Snow each turn (the lock keeps Energy Zone attachments off the computer's Active).
- kx3 changed nothing at any of its 14 decisions here.

**3. B-205731-t08.** Active: Mega Sharpedo ex at 100 of 190, 2 Water. Bench: Alolan Vulpix (60 HP, 2 Water). The computer's Active Baxcalibur is at 90 of 140 HP. Hand: Alolan Ninetales ex x2, Copycat, Irida, Lucky Ice Pop, Misty.
- Turn 8: keep the Mega in front. Evolve the Benched Vulpix into Alolan Ninetales ex. Lucky Ice Pop, then Irida (Mega 100 to 160). The turn's Water on the Mega. Turbo Shark (Baxcalibur to 20), extra Water to the Ninetales ex (3).
- Turn 10: bench a new Vulpix and give it the turn's Water. Retreat the Mega for free into the 3-Water Ninetales ex, then Binding Snow.
- km3 and kx3 both retreat at once instead, in every seed.

**4. B-205731-t10.** Active: Mega Sharpedo ex at 50 of 190, 3 Water; a knockout gives the computer 3 points and the game. Bench: Alolan Ninetales ex (150, 3 Water). Hand: Copycat, Alolan Ninetales ex, Misty, Alolan Vulpix. The computer holds 1 card.
- Turn 10: bench the Vulpix and give it the turn's Water. Retreat the Mega for free into the Ninetales ex, then Binding Snow. Don't play Copycat.
- Turn 12: evolve that Vulpix into the Alolan Ninetales ex kept in hand.

**5. B-210952-t14.** Active: Lapras (110 HP, 3 Water). Bench: Mega Sharpedo ex (190, 1 Water) and Alolan Ninetales ex (150, 2 Water). The computer's Active Wailmer is at 50 HP; it can't retreat this turn.
- Turn 14: bench Carvanha and give it the turn's Water. Surf (70) knocks out the Wailmer.
- Turn 16: evolve Carvanha into Mega Sharpedo ex (see position 6's turn).
- The question is whether km3's continuation punishes the Bench Carvanha. kx3 retreated Lapras and passed in all 3 seeds.

**6. B-210952-t16.** Active: Alolan Ninetales ex (150, 2 Water). Bench: Carvanha (50, 1 Water) and Mega Sharpedo ex (190, 1 Water). The computer's Mega Blastoise ex is at 230 HP with 5 Water.
- Turn 16: bench the Alolan Vulpix. Evolve Carvanha into Mega Sharpedo ex. The turn's Water on the Vulpix. Binding Snow (Blastoise to 150). Don't play Elegant Cape.
- Turn 18: evolve the Vulpix into a fresh Alolan Ninetales ex.
- The hiding case seen directly: km3's own later Elegant Cape choice made "bench the Vulpix" lose all 16 play-outs in two seeds. In the third, kx3 kept the set-up and scored about 0.69, against 0.09-0.19 for the move it picked.

**7. B-210952-t18.** Active: Alolan Ninetales ex at 20 HP, 2 Water. Bench: two Mega Sharpedo ex (1 Water each) and an Alolan Vulpix (1 Water). One card left in his deck. The computer's Mega Blastoise ex is Active at 170 of 230 HP with 5 Water. At 6 Water, Triple Bombardment does 50 to 2 Benched Pokémon.
- Turn 18 (kx3's line): Misty on the Vulpix. Evolve it into a fresh Alolan Ninetales ex. Retreat the 20-HP Ninetales ex into it. Water and Elegant Cape on the new Ninetales ex. Binding Snow on the Active Blastoise, so it stays locked at 5 Water.
- Turn 20 and later: keep the lock with Binding Snow and take the knockout when it comes.
- The comparison here is the other way round: kx3's denial line (lead 3.1 to 5.0 standard errors in all 3 seeds) against Auto's Cyrus line, both continued by km3 and then by the plan.

**8. B-205731-t02.** Turn 2: the turn's Water on the Active Carvanha, then Sharp Fang. km3 plays Copycat; kx3 matched Auto in one seed of 3.
- It's a control: a short plan where the play-outs should already see the difference.

## What to report per position

- Each first move's score under (a) and under (b), from the same sampled worlds, with the paired difference and its standard error.
- How often a scripted step was illegal and fell back to km3.
- Whether the plan's first move overtakes km3's move once the plan is played out.

If (b) lifts the plan's first move clearly above km3's, km3's continuation is hiding it. If (b) and (a) agree, the plan's
first move isn't worth more than km3's, at least not with this continuation.

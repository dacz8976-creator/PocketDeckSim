# km3's late Trainer play inside the play-outs (the cloud, Oct 5)

Set by the Fable coordinator via Dustin, Oct 5. The continuation experiment (`../playout_continuation_2026-10-05/`)
was accepted, and it exposed a habit: where the plan beat km3's own continuation, the difference was a Trainer km3
plays late. This is a bounded diagnosis of that habit.
- **Where it lives.** Branch `claude/playout-pilot`, nothing merged.
- **What it touches.**
  - No table games, and no engine change: `engine/src` is untouched.
  - The one new program is a read-only instrument, `engine/examples/trainer_habits.rs`.
  - The cost measurements use the accepted plan continuation as it is.

## In short

- **Copycat is the habit that matters, but not the way the "hold it" rule says.**
  - km3 plays it 1.8 times a game (0.9 a side) in its own games, and 0.48 times per play-out at the 8 positions.
  - By the rule given (hold it when the hand has 2 or more cards playable this turn or next), a competent player would
    have held it 38% of the time in km3's own games and 39% in the play-outs.
  - On average, though, Copycat improves km3's hand: 2.6 cards go back, 3.4 come in, and only 9% of plays leave fewer
    playable cards.
- **What it costs, measured.** Withholding Copycat from draft A's side, on the continuation study's exact worlds:
  - **+0.19 at position 4**, where it throws away a playable Misty to draw about 2 cards;
  - +0.06 at position 8 (within the noise), where it throws away a ready Mega Sharpedo ex on turn 2;
  - **−0.12 and −0.18 at positions 1 and 2**, where it trades about 2 cards for 5 (the computer holds big hands);
  - about zero elsewhere.
  - So it is a good card played at the wrong moments, not a bad habit as such.
- **The rule given points the wrong way at these positions.** It would hold:
  - 35% of the Copycats at position 2, where Copycat helps;
  - only 3% at position 8, where it hurts.
  - What separates them is how many cards it draws against how many it throws away, and whether a ready evolution goes
    back.
- **Tools: two narrow habits, no broad one.**
  - A Tool on a Pokémon that never attacks is rare once games that simply ended are set aside: 5%, in games and in
    play-outs.
  - But **Protective Poncho went on the Active in 100 of 100 attaches** (a Benched Pokémon was there in 86). Poncho
    protects only on the Bench.
  - **Elegant Cape went on a non-Stage-1 Pokémon in 62 of 108** of km3's own attaches. It adds no HP until that Pokémon
    evolves.
  - In the play-outs the Cape goes on the Stage 1 Ninetales ex or Mega Sharpedo ex 96% of the time. Its one known cost
    is timing: position 6 of the continuation study.
- **Heal Supporters are not a habit.** km3 heals 20 or less with Irida, Pokémon Center Lady or Erika 0% to 11% of the
  time, and always heals as much as the card can. Withholding Irida at the 8 positions only costs: up to −0.41, never a
  gain beyond noise. (Misty, playable instead in 88% of the play-outs' Iridas, is the worse use of the Supporter.)
- **Elegant Cape's timing.** Withholding it gains +0.17 at position 6 (the continuation study's hiding case) but costs
  −0.07 and −0.11 at position 7. Same card, opposite signs, and no one-line rule separates them.
- **kx3 doesn't change these habits at its own decisions.** In the development run, kx3 played Copycat 0.91 times a game
  on the deck's side, exactly as km3 did on the same deals. The four Tools: 0.30 v 0.32. The heal Supporters: 0.28 v 0.27.
- **The proposal (not built): a Copycat rule for the play-outs only.** Inside the play-outs, Copycat is held when:
  - it wouldn't draw at least 2 more cards than it shuffles away (the opponent's hand count is public), or
  - an evolution for a Pokémon in play would go back into the deck.
  - At the 8 positions it holds 7% (position 2) and 24% (position 1) of the Copycats there, and 83% (position 4) and
    100% (position 8).
  - km3 itself, and kx3's own move, are untouched.
  - How to test it, in three steps that each gate the next, is in "The proposal".

## What was measured, and on what

- **km3 in its own games.** The development run `strength_2026-10-03_kx3_dev` kept no KX_TRACE lines (it logged action
  labels only), so the source is its km3 arm.
  - That arm is 560 games, km3 on both sides, the 7 development decks against the 8 panel lists.
  - Each was replayed exactly as the strength harness built it: seat order, `create_players` with km3 twice,
    `Game::new(players, seed)`.
  - **All 560 replayed exactly:** every logged deck-side label, the points, the turns and the winner match
    (`events_games.jsonl.replay.jsonl`).
  - Both seats are km3, so every Trainer play in them is km3's: 1,006 Copycats, 365 Tools, 271 heal Supporters.
  - The kx3 arm's logs (labels only) give the side-by-side plays per game.
- **km3 as the play-out policy.** These are the continuation study's km3 continuations of both first moves at the 8
  positions: 128 rounds each, 2,048 play-outs, the same LAB worlds and seeds as kx3's `evaluate`.
  - The worlds were rebuilt in the instrument from the engine's public parts.
  - **All 2,048 end in the study's final-state digest exactly** (`events_playouts.jsonl.replay.jsonl`).
  - The computer deck carries none of these cards, so these are draft A's plays: 990 Copycats, 1,223 Elegant Capes,
    1,451 Iridas.
  - km3 is the play-out policy, so the 560 games are also the play-out policy's habits across the development decks.
    The 8 positions add the very worlds where the continuation study saw a cost.
- **What each habit costs at the 8 positions** (`withhold.py`, `withhold.txt`). The accepted plan continuation, run
  with an `avoid` rule and no steps, plays draft A's side as km3 does except that one Trainer is withheld for 10 own
  turns.
  - The worlds and seeds are the study's; each run's km3 arm equals the study's round for round.
  - Three runs: Copycat, Elegant Cape, Irida.

**Definitions** (in `trainer_habits.rs`):
- **Playable now:** a legal move at the decision uses the card.
- **Playable next turn:** an evolution whose Pokémon is in play; or a Supporter when only the one-Supporter-a-turn rule
  stops it, which is the case right after Copycat.
- **Energy-matching Pokémon:** one whose attacks the deck's Energy can pay.
- **The "hold" rule** is Fable's: 2 or more cards playable this or next turn. A **ready evolution** is an evolution
  card for a Pokémon in play.
- **Tools.**
  - "Within two turns" means the attach turn and the two after it (the opponent's reply, then its own next turn).
  - Attacks are counted while the Pokémon carries the Tool.
  - Its time ends when the Pokémon is knocked out, when the Tool is discarded (an opponent's Field Blower-like effect),
    or at the game's end.
  - "Never attacked, with time to" requires two more own turns carrying it.
- **Heals.** "Healed" is the damage actually removed; "little" is 20 or less.

## (1) Copycat

| | km3's own games | km3 in the play-outs (8 positions, draft A) |
|---|---|---|
| plays | 1,006 (1.80 a game, both seats) | 990 (0.48 a play-out) |
| hand shuffled away (without Copycat) | 2.6 cards: 1.14 playable now, 0.12 next turn; 0.92 Supporters; 0.68 Energy-matching Pokémon | 2.4 cards: 1.20 now, 0.19 next turn; 1.32 Supporters; 0.62 Energy-matching Pokémon |
| playable this or next turn: 0 / 1 / 2 / 3+ | 29% / 33% / 24% / 14% | 7% / 53% / 34% / 5% |
| drew into | 3.4 cards: 1.42 playable now, 1.15 next turn; 1.05 Supporters; 0.96 Energy-matching Pokémon | 3.5 cards: 1.02 now, 1.60 next turn; 1.52 Supporters; 0.94 Energy-matching Pokémon |
| **held by the rule (≥ 2 playable)** | **38%** (turns 1–4: 49%; 5–10: 26%; 11+: 17%) | **39%** |
| threw away a ready evolution | 11% | 19% |
| drew fewer cards than it threw away | 20% | 28% |
| fewer playable cards after than before | 9% | 10% |

- The development decks' side and the panel side are alike: 38% held by the rule for each, 12% and 10% ready
  evolutions.
- In `rates.txt`, by deck: 0.45 a game (deck 09) to 1.39 (deck 01).

**What withholding Copycat changes at the 8 positions** (draft A's side, 10 own turns; 128 rounds, paired):

| # | Position | the plan's first move: km3 → without Copycat | the rival: km3 → without Copycat | Copycat's hand there |
|---|---|---|---|---|
| 1 | B-214254-t06 | 0.766 → 0.648, **−0.117** [−0.177, −0.057] | 0.781 → 0.664, −0.117 [−0.181, −0.053] | 2.2 cards, draws 5.0 |
| 2 | B-214254-t10 | 0.730 → 0.551, **−0.180** [−0.259, −0.100] | the same | 1.8 cards (often a lone Misty), draws 5.2 |
| 3 | B-205731-t08 | 1.000 → 0.992 | 0.992 → 0.992 | 2.8 cards, draws 1.7 |
| 4 | B-205731-t10 | 0.539 → 0.727, **+0.188** [+0.113, +0.262] | the same | 1.6 cards (a lone Misty in half), draws 2.2 |
| 5 | B-210952-t14 | 0.031 → 0.031 | 0.266 → 0.266 | mostly on turn 30, the game decided |
| 6 | B-210952-t16 | 0.000 → 0.000 | 0.113 → 0.113 | the same |
| 7 | B-210952-t18 | 0.430 → 0.430 | 0.133 → 0.133 | the same |
| 8 | B-205731-t02 | 0.789 → 0.844, +0.055 [−0.028, +0.137] | 0.727 → 0.727 (the rival is Copycat itself) | 3.9 cards with a ready Mega Sharpedo ex, draws 3.1 |

- **Position 4's gain is the continuation study's whole plan gain there.** Withholding Copycat alone gives the plan
  continuation's score in every one of the 128 rounds there, for both first moves.
- **Position 8's gain is smaller than the plan's +0.078 there,** and within the noise.

## (2) Tools

| | km3's own games | km3 in the play-outs |
|---|---|---|
| Elegant Cape | 108: on the Active 85%; Stage 1 43% (**62 on a non-Stage-1**: Electrike 20, Alolan Vulpix 13, Lapras 12, Helioptile 10, Carvanha 7); attacked within two turns 63%, knocked out within two 16%; never attacked with time to 6%; its time ended: knocked out 44%, discarded 36%, to the end 19% | 1,223: on the Active 79%, Stage 1 96% (Alolan Ninetales ex 1,022, Mega Sharpedo ex 147); attacked within two turns 85%; never attacked with time to 5% |
| Giant Cape | 56 (Suicune ex 34): on the Active 73%; attacked within two turns 66%; never attacked with time to 7% | none |
| Protective Poncho | 100: **on the Active 100%** (a Benched Pokémon was there in 86); attacked within two turns 75%; never attacked with time to 5% | none |
| Rocky Helmet | 101: on the Active 100% (where it works); attacked within two turns 82%; never attacked with time to 3% | none |
| all four | on a Pokémon that never attacks while carrying it 20%, **with time to 5%** | 9%, with time to 5% |

- **Many "never attacked" Tools are the game's end, or the opponent's Field Blower.** Discarded Tools: Elegant Cape 36%,
  Rocky Helmet 40%.
- **The habit Fable asked about (a Tool on a Pokémon that never attacks) is small.**
- **Two narrow ones aren't.**
  - The Poncho on the Active, where its text does nothing.
  - The Elegant Cape put on a Basic early. That is sometimes a pre-load for its evolution: the Cape stays on through
    the evolution.

**What withholding Elegant Cape changes at the 8 positions** (`withhold.txt`):
- **Position 6, after the Vulpix:** +0.172 [+0.129, +0.215]. This is the continuation study's hiding case, and more
  than the plan's +0.133 there, because the plan withheld the Cape only on turn 16. After Binding Snow there: +0.062
  [−0.003, +0.128].
- **Position 7:** −0.066 [−0.109, −0.024] after Misty, −0.113 [−0.157, −0.070] after Cyrus. Here the Cape goes on the
  fresh Ninetales ex, the plan's own line.
- **Elsewhere:** within ±0.02.
- So the Cape cuts both ways too, and what decides it is timing: which Ninetales ex gets the one Cape. No one-line rule
  separates the two.

## (3) Heal Supporters

| | played | healed (could heal) | board damage | healed ≤ 20 | healed nothing | a condition to cure | Misty playable instead |
|---|---|---|---|---|---|---|---|
| Irida, own games | 100 | 40 (40) | 85 | 8% | 0% | 7% | 34% |
| Pokémon Center Lady, own games | 128 | 29 (29) | 77 | 11% | 1% | 17% | — |
| Erika, own games | 43 | 47 (47) | 89 | 2% | 0% | 16% | — |
| Irida, play-outs | 1,451 | 58 (58) | 151 | 0% | 0% | 0% | 88% |

- In all 1,722 heal plays, km3 removed exactly as much damage as the card could, and it almost never played one into an
  undamaged board. So the "little damage" habit isn't there.
- In draft A's play-outs, Irida is played where Misty (Energy) was the alternative.

**What withholding Irida changes at the 8 positions** (`withhold.txt`):
- It costs value wherever it changes anything:
  - position 1: −0.121 and −0.117;
  - position 2: −0.199 (after the Lucky Ice Pop; the rival is Irida itself);
  - position 5: −0.031 and −0.258;
  - position 6: −0.105 (after Binding Snow);
  - position 7: −0.406 and −0.133.
- It is never a gain beyond the noise.
- In these worlds Irida is a good play, and its Supporter is better spent on it than on the Misty in the same hand.

## The 20 examples (`examples.md`)

They were chosen by fixed criteria, the first event in file order meeting each, so `examples.py` reproduces them.

- **Copycat, 11 examples.**
  - Throwing away a ready evolution: position 8's turn 2 twice; a development deck; the panel side.
  - 3 or more playable cards, drawing fewer: two decks.
  - 2 playable on turn 1 or 2.
  - Late, into a small opponent's hand.
  - Position 4's turn-12 Copycat of a lone Misty.
  - An empty-deck Copycat on turn 30.
  - One the rule calls fine.
- **Tools, 6.**
  - Elegant Cape on a Basic that never attacks with time to.
  - Elegant Cape on a 10-HP Basic.
  - Position 6's Cape on the Active Ninetales ex, the continuation study's hiding case.
  - A Benched Mega Sharpedo ex with the Cape that never attacks.
  - A Poncho on the Active.
  - A Giant Cape on a Suicune ex that never attacks.
- **Heal Supporters, 3.** Pokémon Center Lady healing 20; Irida healing 20; Irida with Misty playable.

## The proposal (play-out policy only; not built)

**The change.** Inside the play-outs (`Core::play_out`, both sides), km3's offered moves lose Copycat when either:
1. **it wouldn't draw at least 2 more cards than it shuffles away:** the opponent's hand count (public) is less than the
   player's hand without Copycat + 2; or
2. **an evolution for a Pokémon in play would go back into the deck.**

If that leaves no move, nothing is removed. The mechanism is the one the plan continuation's `avoid` rule already uses:
km3 searches the remaining moves, so km3's code is unchanged. kx3's own decision at the root (the move it proposes and
plays) is not filtered, only the play-outs after it.

**Why this one, and why only this one.**
- **Copycat is the most frequent of the three habits.** It is 1.8 plays a game, against 0.65 Tools and 0.48 heal
  Supporters. Of the two with a measured cost at the 8 positions (Copycat and Elegant Cape), it is the one whose costly plays a
  simple, public test can tell from its good ones.
- **Its cost cuts both ways (+0.19 to −0.18), so a ban is wrong.** The rule must keep the good plays and drop the bad
  ones.
  - At the 8 positions, the net-draw test does that. It holds 7% and 24% of the Copycats where Copycat helps (positions
    2 and 1), and 83% and 100% where it hurts (positions 4 and 8).
  - Fable's "≥ 2 playable" rule doesn't: it holds 35% at position 2 and 3% at position 8.
- **The Poncho-on-the-Active habit is real, but narrow.** Two lists carry Poncho (deck 05 and t-lucario), and draft A
  doesn't, so it can't be measured at these positions. It is the next candidate, as a second one-line rule ("a Poncho
  only to the Bench") once the first is judged.
- **Elegant Cape's cost is timing.** Withholding it gains +0.17 at position 6 and costs −0.07 and −0.11 at position 7.
  That isn't a one-line rule.
- **Heals don't need one.** Withholding Irida only costs, up to −0.41.

**What it would change.**
- It holds 74% of km3's Copycats in its own games. Copycat draws 3.4 cards there against a 2.6-card hand, and the
  development panel holds smaller hands than the computer deck. That is a large change to the play-out policy, so the
  test below gates it in three steps.
- Its cost in time is nothing measurable. The check runs only when Copycat is offered (a count and a scan of the hand),
  and km3's search is unchanged; play-out lengths may change a little either way.

**How to test it** (each step gates the next):
1. **Identity tests, written first.**
   - With the rule off, the play-outs are km3's exactly (as with K = 0 in the continuation tests).
   - With it on, a play-out in which Copycat is never offered ends in the same final state.
   - On the built states: position 8's turn-2 hand is held; position 2's lone Misty against a 5-card hand is played.
2. **The 8 positions, on the same worlds** (128 rounds; about 12 minutes here).
   - Rerun the continuation study's km3 arm with the rule, and kx3's own decision (128 play-outs).
   - Read off each first move's score with and without the rule, and whether kx3's choice moves.
   - **Expected:** position 4 rises by about +0.19 (83% of its Copycats are held), position 8 by up to +0.06, and
     positions 1 and 2 stay within about 0.03.
   - If 1 or 2 fall beyond noise, the margin is wrong: try 1 card instead of 2, which holds 49% in km3's own games.
3. **The development decks.**
   - kx3 with the rule against km3, on the development run's 560 deals with the deck in both seats (the same seeds
     `24,400,000,000 + pair × 10,000 + deal`).
   - Paired with kx3's own development games (arm X) on the same deals; primary measure: the paired difference.
   - The whole run took 42 hours on the laptop's 2 threads. A first cut on the three decks with the most Copycats
     (01: 1.39 a game, 10: 1.20, 06: 1.11) is 240 games, about 18 hours.
   - No table game is needed for any of this.

## Files

- **The instrument:** `engine/examples/trainer_habits.rs`.
  - `games` mode replays an arm of a strength run and checks each game against the run's own log.
  - `playouts` mode replays the continuation study's play-outs and checks each final-state digest.
  - It only watches.
- **The events:**
  - `events_games.jsonl`: 560 games, both seats.
  - `events_playouts.jsonl`: 2,048 play-outs.
  - Each comes with its `.replay.jsonl` check, and the stdout of each run.
  - One line per Copycat, Tool (followed to its end) and heal Supporter, with the hand profile card by card, the board,
    and what followed.
- **The analysis:**
  - `analyze.py` → `rates.txt` (every rate above, by side and by deck);
  - `examples.py` → `examples.md`;
  - `withhold.py` → `withhold.txt` (the three withhold runs);
  - `withhold_*.json`: the withhold plans;
  - `withhold_*.jsonl`: their study lines, with every round.
- **To rerun**, from the repository root, with the examples built:
  - `trainer_habits games --games rl/results/strength_2026-10-03_kx3_dev/games.jsonl --manifest rl/results/strength_2026-10-03_kx3_dev/manifest.json --out <events>`
  - `trainer_habits playouts --plans rl/results/playout_continuation_2026-10-05/plans.json --states rl/results/playout_continuation_2026-10-05/states --study rl/results/playout_continuation_2026-10-05/run/study.jsonl --deck decks/brews/drafts_2026-10-01/draft-A-shark-tempo.txt --opponent decks/computer/blastoise-wailord-deluxe.txt --rounds 128 --seed-base 24200001000 --out <events>`
  - `playout_continuation --plans <this folder>/withhold_copycat.json --states ... --rounds 128 --seed-base 24200001000`

# Quiz 4's three items for the play-out pilot (the cloud, Oct 6)

Set by the Fable coordinator via Dustin, Oct 6, from his quiz 4 notes (`rl/results/blind_quiz4_2026-10-06/RESULTS.md` on
main):
- **The items.**
  1. "Attack when you can": a stricter switch bar away from an attack.
  2. No-effect actions: the Tool tie-break, widened to any action whose printed effect can't do anything now.
  3. The continuation experiment at the three positions where he chose "neither" (Q06, Q07, Q11).
- **How.** Each is its own parameter, with tests first and gates 1 and 2 as before. No table games, and km3 is untouched.
- **Where it lives.** Branch `claude/playout-pilot`, nothing merged.
- **What doesn't change.**
  - km3, `engine/src/players/mod.rs` and the official engine.
  - kx3's default play: both new parameters are off unless the code names them.

## In short

1. **The attack bar (`_za<z>`) is built and passes gates 1 and 2, but as asked it also stops good moves.**
   - In the development run, kx3 left an attack km3 proposed at 26 of 1,902 decisions (1.4%). With `_za3` it keeps
     km3's attack at 22 of them.
     - That includes **Q12**, where Dustin chose km3's attack.
   - **The catch:** only 9 of the 26 skipped the attack for the turn (the bar keeps 8). The other 17 were a move made
     *before* the attack: Misty, Copycat, a Stadium, a retreat. kx3 then attacked later the same turn. The bar stops 14
     of those, so kx3 would attack first and lose the Misty Energy or the Copycat draw.
   - A narrower version would apply the bar only when the switch leaves the turn without an attack. It isn't built here;
     it's Fable's call.
   - The bar can't reach Q01, Q02, Q03 or Q08. There km3's first move wasn't the attack (Energy, Lucky Ice Pop, an
     evolution, Watch Over), and kx3 parted from km3 at that preparation step.
2. **No-effect actions (`_noeffect`):** in progress (the code and its tests are on the branch; counts and gates follow).
3. **The "neither" positions: in these play-outs, Dustin's plan doesn't beat the move kx3 actually played at any of
   the three.** It does beat km3's plan at Q11.
   - **Q06: his plan loses.** It wins 0 of 128 play-outs, against 0.289 for kx3's move (the Psychic to the Benched
     Indeedee ex) and 0.016 for km3's line.
   - **Q07: no difference.** His plan scores 0.500, kx3's attack 0.578 and km3's Bench Energy 0.477, all within noise.
   - **Q11: his plan beats km3's, not kx3's.** Turbo Shark with its Water to Lapras scores 0.336.
     - Against km3's (bench the Vulpix, then Turbo Shark, 0.195): +0.141 [+0.076, +0.205], beyond noise.
     - Against kx3's (retreat into the Vulpix, Gnaw, 0.312): +0.023 [-0.075, +0.122], within noise.
   - **Why the bots missed it at Q11.**
     - km3: its own first move benches the Vulpix, and the play-outs put that cost at 0.141. km3's continuation after
       Turbo Shark gives the Water to Lapras too, so it doesn't hide the plan.
     - kx3: the move was a candidate. With the game's 16 play-outs it scored 0.375 against 0.562 for the retreat kx3
       chose. At 128 the two are equal within noise.
   - The "+1 turn" extensions of his Q06 and Q07 reasoning (Lillipup keeps Tackling; Stoutland stays Active and
     attacks) change nothing. At Q07, km3's own continuation already does exactly that.

## Item 1: "attack when you can" (`_za<z>`)

### What was built

- **The parameter.** `_za<z>`, e.g. `kx3_r16_c12_z2_real_t0_poolmeta_za3`.
  - When km3's move is an attack and kx3's best candidate is not, the switch needs a lead beyond z_attack standard
    errors instead of z.
  - A switch to another attack, or any switch from a move that isn't an attack, keeps the bar z.
  - Off (no `_za` in the code), nothing changes.
- **The trace.** Every switch away from km3's attack names both scores, e.g. "play-outs: +0.438 over km's move, 3.4
  standard errors (threshold 3); away from km's attack: km's attack 0.125, this move 0.562".
  - Every switch the bar stops says so: "the attack bar: the best move leads km's attack by +0.250, 2.2 standard errors,
    past z 2 but not the attack bar 3 (km's attack 0.562, this move 0.812): km's attack kept".
- **Code.** `switch_bar` and the decision block in `engine/src/players/playout_player.rs` (commit 8d16d49f).
- **Tests.** Five in `engine/tests/playout_quiz4_test.rs`, written first (`attack_bar/tests_before.log`, commit
  2ea4754d):
  - the code spells the bar;
  - the bar applies only away from an attack;
  - z_attack equal to z changes nothing;
  - the bar keeps km3's attack against a smaller lead (test decks, seeds 20,000,000,211-216);
  - a switch away from an attack names both scores.

### Where kx3 left km3's attack in the development run (`attack_bar/attack_scan.*`)

**How it was counted.**
- kx3's 560 games of the development run (`strength_2026-10-03_kx3_dev`, arm X) were replayed exactly, move by move from
  the log (`trainer_habits scripted --attack-scan`; all 560 matched).
- At each of kx3's decisions with an attack among the legal moves, km3 was asked with the game's own observation and
  search randomness.
- Where km3 proposed an attack and the log played something else, kx3 decided again from the same randomness, with every
  candidate's score. It did this twice:
  - with the run's own code (24 of the 26 reproduce the logged move; at the other 2, a fresh kx3 keeps the attack);
  - with `_za3` (`attack_scan_za3.jsonl`).
- The summary is `attack_scan.py`, and its output is `attack_scan.txt`, with the full table of all 26.

**What it found.**
- **How often.**
  - km3 proposed an attack at 1,902 of kx3's decisions.
  - kx3 attacked at 1,876 of them and played something else at 26 (1.4%).
- **Why it switched.**
  - **9 skipped the attack for the turn.**
    - End Turn at 5.
    - A retreat at 3.
    - Copycat at 1 (followed by End Turn).
  - **17 attacked later the same turn.**
    - Misty at 3, Copycat at 3, a Stadium played or used at 4, a retreat at 3.
    - Field Blower, Poké Ball, Poison Barb and benching the Vulpix at 1 each.
- **How big kx3's lead was.**
  - Of the 24 that reproduce, 22 led by 3 standard errors or less (most between 2.1 and 2.6).
  - The other 2 led by 3.4 and 10.2.
- **With `_za3`.**
  - **22 attacks are kept:** 8 of the 9 skips, and 14 of the moves before an attack.
  - **2 switches stand.**
    - Deck 05 v Lucario: End Turn at 3.4 SE, where km3's Psychic scored 0.125 v 0.562.
    - Deck 10 v Blaziken: Poison Barb at 10.2 SE, then the attack.
  - **The 2 that don't reproduce stay with the attack, within the noise.**
  - kx3 deciding again with the bar on agrees with the worked-out verdicts at every decision.
- **What those games did.** This can't be pinned on the switch, because the rest of the game decides it.
  - Games with a skipped attack: 8. kx3 won 5 of them; km3 won 2 of the same deals.
  - Games with a move before the attack: 16. kx3 won 10; km3 won 5.

**The quiz positions.**
- **Q12 is in the scan.** kx3 played End Turn instead of Supernatural Feather, +0.312 at 2.1 SE. `_za3` keeps the attack,
  which Dustin chose ("Not sure why you wouldn't attack").
- **Q01, Q02, Q03 and Q08 are out of the bar's reach.** At the position, km3's first move was a preparation step, and its
  attack came later in the turn. kx3's different choice was that first step, and it left no attack for km3's line:
  - Q01: Darkness to the Active, then Venomous Hit;
  - Q02: Lucky Ice Pop twice, Darkness, Venomous Hit;
  - Q03: evolve the Active, then attack;
  - Q08: Watch Over, Psychic Energy, Rare Candy, Psychic.

  A rule for these would have to compare whole turns ("km3's line attacks this turn, kx3's doesn't"), not one decision.
- **Q10 is the reverse.** kx3 attacked (Thunder Shock) and km3 didn't. So is Q07, where kx3 attacked with Psychic.

**The catch, in a sentence.** As asked, "km3's move is an attack and kx3's best candidate is not" also covers "play Misty
or Copycat first, then attack", which is usually right: an attack ends the turn, so Supporters and Items come first.
- The bar would stop 14 such moves in the development run, against 8 real skips.
- A narrower version could apply the bar only when the candidate's play-outs don't attack later in the same turn. It
  isn't built: that's a change to what was asked, so it's Fable's call.

### Gates

- **Gate 1** (`attack_bar/checks/`, at 8d16d49f in a separate worktree, before item 2's code):
  - **The suite:** 2,072 passed, 0 failed.
  - **km3's 240 games** (seed 7100): game for game equal to the official program's, and equal to the pinned record
    `5a18d31_10_cli_km3.txt` on every line but the wall time.
  - **The harness self-checks.**
    - km3: digest 81b572198c04d5d1, unchanged.
    - `kx3_r2_c3_lab`: digest 3a2eb43bd9053639 twice, unchanged.
    - `kx3_r2_c3_lab_za3`: the same digest. The bar never acted in those 2 games.
- **Gate 2 (the 12 + 8 positions).** The bar can only act where km3's move is an attack. Of the 20 positions:
  - **1 qualifies:** B-214254-t06 (Turbo Shark), and kx3 already keeps the attack there.
  - **The other 19 don't:** km3's move there is a Tool placement, a Trainer, a retreat, a bench or an Energy.
  - So the bar changes nothing at the 20 positions, by its rule. The 26 development-run decisions above are its real
    test.

## Item 3: the continuation experiment at the "neither" positions (`neither/`)

### The question and the method

At Q06, Q07 and Q11, Dustin chose neither bot's plan and wrote what he would do. Does his plan win in the play-outs,
and if so, why did neither bot find it? The method is the Oct 5 continuation study's (`../playout_continuation_2026-10-05/`).
- **The positions** were rebuilt exactly from the development run (`trainer_habits positions`, `neither/at.json`,
  `neither/states/`).
  - The game is replayed to the deck side's decision, and each position is checked against the run's log: the turn, the
    number of legal moves, and km3's move there.
  - kx3 decided again at each one from the game's own observation and randomness. It plays what its arm logged at all
    three, so the 16-round trace below is the game's own.
  - Q06 was also rebuilt one move on, after the Benched Indeedee ex's Watch Over. That is where Dustin's plan and km3's
    part.
- **The laptop hadn't added the plans** to `CONTINUATION_POSITIONS.md`. They come from his notes in the published quiz
  key (`../blind_quiz4_2026-10-06/RESULTS.md`), scripted by intent in `neither/plans.json`:
  - **Q06:** the Benched Indeedee ex's Watch Over (healing the Active), retreat into Lillipup, the turn's Psychic Energy
    to it, Tackle.
  - **Q07:** retreat into Stoutland, the turn's Psychic Energy to it, end the turn.
  - **Q11:** Turbo Shark, with its Water to Lapras (the Vulpix stays in hand).
  - Card facts were checked with `lib/card.py`:
    - Bonsly's Teary Attack: the Defending Pokémon's attacks do -30.
    - Indeedee ex's Psychic: 30 + 30 for each Energy on the defender.
    - Stoutland's Guard Dog Visage: the opponent's attacks cost 1 Colorless more while it is Active.
    - Suicune ex's Crystal Waltz: 20 for each Benched Pokémon, both sides.
    - Lillipup: Tackle 20 for one Colorless; weak to Fighting.
- **One new kind of plan step:** "use this Pokémon's Ability", because Q06's plan starts with one.
  - Tests first: `neither/tests_before.log`.
  - The step lives in `playout_plan.rs`, the diagnostic plan continuation; kx3's play never uses it.
- **The study.**
  - **First moves:** Dustin's first move, and a rival (kx3's move in the game; km3's as a second rival where it differs).
  - **Continuations:** each first move is continued two ways, by km3 and by his plan for the turn (K = 1) then km3.
  - **The rest of the game:** the opponent is km3 throughout.
  - **Worlds:** 128 rounds in the same sampled worlds, LAB (the opponent's exact list).
  - **Seeds:** 24,200,001,106 / 107 / 111, and 24,200,001,126 for Q06 one move on.
- **kx3 in the study's worlds.** At each position, kx3 decided with 128 rounds at the study's seed. Its km3 scores for
  the two moves equal the study's (`run/study_stderr.txt`).

### Results (`neither/summary.txt`, from `run/study.jsonl`)

Each score is the deck's mean over 128 play-outs (a win counts 1, a tie 1/2, a loss 0). A comparison is his line minus
the bot's line, round by round in the same worlds, with a 95% interval:
- his line: his first move, then his plan, then km3;
- a bot's line: its first move, then km3.

At Q07 and Q11, his plan and km3's continuation of his first move reach the same final state in all 128 rounds. There,
km3 would play his plan itself once given the first move.

| position | Dustin's plan | kx3's move in the game | km3's plan | his plan v kx3's | his plan v km3's |
|---|---|---|---|---|---|
| Q06 | 0.000 | 0.289 (Psychic to the Benched Indeedee ex) | 0.016 | **-0.289 [-0.368, -0.210]** | -0.016 [-0.037, +0.006] |
| Q07 | 0.500 | 0.578 (Psychic to the Active Indeedee ex, Psychic) | 0.477 | -0.078 [-0.198, +0.042] | +0.023 [-0.062, +0.109] |
| Q11 | 0.336 | 0.312 (retreat into the Vulpix, Gnaw) | 0.195 | +0.023 [-0.075, +0.122] | **+0.141 [+0.076, +0.205]** |

**Q06: his plan loses in every play-out.**
- At Q06, km3's plan begins with the same Watch Over, so the comparison is his line against km3's line from there:
  0.000 v 0.016. Each is far below kx3's move: 0.289, which leads km3's move by +0.273 at 6.9 SE.
- **One move on** (after the Watch Over), every other option is close to lost (0.008 to 0.031). The best is again the
  Psychic to the Benched Indeedee ex (0.234).
- **What the board says** (the play-outs give only the result):
  - Lillipup is weak to Fighting, and all three of the opponent's Pokémon are Fighting.
  - Tackle's 20 doesn't Knock Out the 30-HP Bonsly.
  - The retreat spends the Active Indeedee ex's only Energy. So no Indeedee can attack for two turns, while kx3's line
    has the Benched Indeedee ex ready on the next turn.
  - In round 0 of the "+1 turn" extension, the Active Lillipup is Knocked Out and the second Lillipup is promoted.
- **His point about the Bonsly is right:** Psychic does 0 to it this turn (30 - 30). In the play-outs, though, the fix
  costs more than it gains.
- **Why the bots didn't play it.** The retreat into Lillipup was a candidate for kx3 at Q06, and so was every other
  move. It scored 0.000 of 16 in the game and 0.008 of 128 here. The bots didn't miss it: it's worse in these worlds.

**Q07: no difference.**
- His plan scores 0.500, kx3's attack 0.578 and km3's Energy on the Benched Stoutland 0.477, all within noise.
- **km3's continuation doesn't hide the plan:** after the retreat into Stoutland, km3 gives Stoutland the Energy, which
  is his plan exactly.
- **kx3:** the retreat was a candidate. It scored 0.625 against 0.688 for kx3's choice in the game, and at 128 rounds
  +0.023 over km3's move, within noise.
- **The "+1 turn" extension** (Stoutland stays Active, takes the Energy and uses Sharp Fang) scores the same 0.500. km3
  already plays it that way on the next turn: the extension and km3's continuation end in the same final state in all
  128 rounds.

**Q11: his plan beats km3's, not kx3's.**
- Turbo Shark with the Water to Lapras scores 0.336, against km3's bench-the-Vulpix-then-Turbo-Shark at 0.195:
  +0.141 [+0.076, +0.205], "ahead either way".
- **This is his reason in numbers.** Suicune ex's Crystal Waltz does 20 more for each Benched Pokémon, and benching the
  Vulpix costs 0.141 in the play-outs.
- **km3's continuation doesn't hide it:** after Turbo Shark, km3 also gives the Water to Lapras. km3's own first move
  is the miss.
- **Against kx3's retreat-and-Gnaw** (0.312) it's within noise: +0.023 [-0.075, +0.122].
- **Misty first** also scores 0.336 in kx3's 128-round trace, and kx3 at 128 rounds would play Misty or Turbo Shark,
  tied.
- **In the game**, at 16 rounds, Turbo Shark scored 0.375, Misty 0.438 and the retreat 0.562, so kx3 retreated. That
  is noise: the move it chose is as good in these worlds.

**What this says.**
- Dustin's "neither" plans aren't better than kx3's choices in kx3's own play-outs (km3 continuing, the opponent's
  list known).
- Q11 is the clearest case where his reading of a card (Crystal Waltz) beats km3's plan, and the play-outs agree with
  him.
- Q06 is the reverse: his fix for the Bonsly loses to kx3's quieter build.
- The play-outs judge every plan by km3's later play. So a plan that needs a human's follow-up isn't fully tested, but
  the "+1 turn" versions didn't change the picture.

## Files

- `attack_bar/`
  - `tests_before.log`: item 1's tests before the code.
  - `attack_scan.jsonl`: every decision where km3 proposed an attack, and kx3's decision again where the log left it.
  - `attack_scan_za3.jsonl`: the same with `_za3`.
  - `attack_scan.py` and `attack_scan.txt`: the summary and the full table.
  - `checks/`: gate 1.
- `engine/examples/trainer_habits.rs` gains three modes:
  - `scripted --attack-scan` (item 1);
  - an "effect" event for every move with a card text (item 2);
  - `positions`, which rebuilds a run's position exactly and, with `--kx3`, kx3's own decision there (item 3).
- `neither/`
  - `at.json` and `states/`: the positions and their checks.
  - `plans.json`: Dustin's plans, the rivals and the "+1 turn" extensions.
  - `tests_before.log`: item 3's tests before the code.
  - `run/`: the study's output.
  - `summary.py` and `summary.txt`: the tables, the steps played, round 0's moves, and kx3's traces.
- `engine/src/players/playout_plan.rs`: the Ability step. `engine/examples/playout_continuation.rs`: a state and seed
  per entry, and only the entries being run are checked.

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
3. **The "neither" positions:** in progress.

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

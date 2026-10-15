# Next pilot round: ky3 (v2, Oct 14)

**Goal.** Fix the three planning failures Dustin named (passing up knockouts, exposing unprepared attackers, not building the
Bench) without breaking the turns where passing, sacrificing or delaying is right. F = the frozen kx3; C = the m64 kx3.
**The baseline is ky3 with every switch off, and it must play exactly like F.** Every case is in `DESIGN_NOTE_CASES.md`.

## 1. Where each failure stands

| failure | F's own verified mistakes | right-to-pass cases | first prototype |
|---|---|---|---|
| passing up an attack | 6 of F's 8 pre-registered skips (1 a lean call), and 034953 t14 | 4 hand-checked skips; the game 3 T4 shield | `_atk` |
| exposing an unprepared attacker | none clean: both positions have a Regigigas that can't attack anyway | game 3 T1, the sacrifice | baseline only |
| not building the Bench | none: game 8 T2 was Dustin's own slip, and arming the Benched Cottonee is already kx3's main deck 12 habit | none yet | baseline only |

So phase 1 builds `_atk` and the two Kangaskhan corrections, and measures F on every exposure and Bench position. `_expo` waits
for one clean positive, and `_bench` waits for an F failure. Promotions after a knockout have no position at all.

## 2. The prototype

`ky3` = `kx3_r16_c12_z2_real_t0_poolmeta` on 9a0bc5ac under a new name. Each switch is off unless named (`ky3_atk_punch`).

| switch | the change |
|---|---|
| `_infer` (stays off) | Declared, not tested. On 9a0bc5ac, when no pooled list fits the opponent, kx3 builds an inferred list; F used the closest list. With the switch off, ky3 keeps F's closest list, so it equals F on his ladder positions too. |
| `_atk` | Dustin's attack rule, below. |
| `_punch` | Kangaskhan is forecast as two punches, 80 then 40, each with its own cuts (Heavy Helmet: 60 + 20). The 40 carries on to the next victim, and the threat pick uses 120. |
| `_queue` | At the depth limit, a frame where every choice is a from-attack `ApplyDamage` is resolved before scoring, at any number of choices, like the existing rule (expectiminimax_player.rs:663). It reaches every attack that queues damage (Kangaskhan; Tongue Whip, Diving Icicles and the other target-choice attacks), not only Kangaskhan. |

**The attack rule.** Dustin's Oct 12 ruling (`HAND_CHECK_SKIPS_laptop.md`) puts this rule up for testing both ways: "never end
the turn while a legal attack costs nothing and the attacker isn't needed elsewhere". "Free" means by consequences as well as
cost, and "needed elsewhere" is judged only from what the bot could know. `_atk` tests his rule, not the narrower "follow km's
attack" (km3 proposed no attack at 10 of the 13 same-position turns), so it also fires where km3 itself would skip.

**Dustin, Oct 15, on knockouts:** "Take the knockout if you win or it helps you, but 1 point early doesn't help if it puts you in a
worse position later."
- **A knockout that wins the game is always taken.** No exception applies to it.
- **Any other knockout is judged by where it leaves the game,** not by the point. Taking it is "free" only if it doesn't leave ky3
  worse off: losing the deck's win condition (his Pawniard), or a bigger attack later (his Blade), counts as worse.
- **The one-turn watch is the first approximation of "later".** Section 5 says what follows if it is too short.
- **When it looks:** an attack is legal now, and ky3's chosen move leads to no attack this turn. That means its line attacks in
  fewer than half its play-outs, a count `_zs3` already keeps (playout_player.rs:1211).
- **"Does something":** each legal attack is applied to a copy of the board, with every branch and every target, and queued
  damage such as the second punch resolved. It counts only if it damages or knocks out an opposing Pokémon, Bench included.
- **"Costs nothing", "not needed elsewhere":** a new play-out watch counts the opponent's points from the end of this turn
  through the checkup after their next turn (a win counts as the points they still needed).
  - The skip stands if the attack line gives up at least 0.25 more points than ky3's line, by more than 2 standard errors,
    paired round by round.
  - There are no fixed bans: Rocky Helmet recoil, self-damage and discards count only through this watch.
  - The play-outs sample only worlds that fit what the bot sees.
- **Then:** ky3 plays km's move if km's line attacks this turn. Otherwise it plays the free attack with the best play-out
  score. It does not cover an attack that becomes legal only after an attach (06 v Lucario 4|0 t4).

**`_zs3` is a comparison arm:** F plus the existing skip bar (3 standard errors to switch away from km's attack). At F's 9
true-skip decisions it kept km's attack at 7, including both defensible ones (skip_scan.txt at 172cbe9c), so it should fail the
right-to-pass side. At 8 of the 9, the play-outs preferred skipping by 2.1 to 3.4 standard errors, which is why `_atk` reads
the opponent's next-turn points, not the win rate.

**Where the km changes act:** `_punch` and `_queue` act in ky3's proposal and on its own seat in every play-out. The simulated
opponent stays plain km3, as in every gate-3 game. The move cap (playout_player.rs:1104) calls
`public_clock_effect_km_value_function` directly, so `_queue` never reaches it, and `_punch` reaches it only if the build
rewires that call. The cap matters only above 12 moves, and km's move is always kept.

## 3. The gates, in order

0. **The baseline first:** km3, F and ky3 with no switch, every case, the same 12 seeds. A case is a positive only if the
   baseline meets its property in at most 8 of 12. Otherwise it is a keep check.
1. **The position set, both ways.** `EXPECTED.md` is committed before any run, with each case's property, its baseline count
   and, for each negative, the exception expected to hold it. Arms: `_atk`, `_zs3`, `_punch`, `_queue` and all switches,
   paired with the baseline. A positive passes at 10 or more of 12 and at least 4 above the baseline. A negative or keep check
   passes if no seed loses what the baseline had. A negative counts only if `_atk` looked in at least 6 of its 12 replays;
   otherwise it is "not exercised". The all-switches run must meet every switch's rules, and a failing negative stops its
   switch. `_punch` and `_queue` are judged by their unit tests.
   - `_atk`'s exception is a parameter, not a fixed choice. By default a skip stands only if attacking gives the opponent
     at least 0.25 more points by the checkup after their next turn, by more than 2 standard errors. On the negatives it is
     swept at 0.15, 0.25 and 0.5, so the choice is shown rather than assumed.
   - 10 v Altaria 2|0 t3 is report-only.
2. **Identity:**
   - ky3 with no switch gives F's self-check digest 31d638dbc818b0fa (km3 stays 81b572198c04d5d1) and F's move at every seed.
   - With `_atk`, the games where it never looked match. `_punch` must be bit-equal wherever no Kangaskhan is in play.
   - `_queue` may change the digest through Diving Icicles (in t-suicune); games with no firing must match. Firings are counted.
3. **A no-harm strength run:** ky3 with the passed switches v F on the 560 development deals, paired, setup decks first (F −
   km3 is +20.4 ± 5.8 there; +19.8 ± 6.0 on the exam). It can rule out a loss of about 3.5 points per 100 games but can't
   show a gain: `_atk` touches about 0.4% of attack turns, and m64's +3.8 needed 528 pairs. Count the skips again, and give
   kx3 games v total games. Anything larger needs Dustin's word. Speed is reported, never a gate (all near 0 on ~200 s).
   It is not sized now: after gate 1 passes, it is sized together with F's paired games, and it goes to Dustin with its cost.

## 4. Build, cost, who

- **Branch** `sonnet/ky3-pilot` from 9a0bc5ac, with no merge: main's engine equals 9a0bc5ac's outside the kx players. The
  corrected positions and main's `pg_pos.rs` (28df6315: Special Conditions, knock-out count) are read by path.
- **Old positions, one route:** a new `skip_replay.rs` export mode on the old tree writes the exact state at a game key and
  decision as a pg_pos position. It is kept only if km3 on the current engine makes its recorded `km3_move` there in most of
  12 seeds; otherwise it is dropped and listed.
- **Deck 12:** only game 3 T4 now, by hand. Its opponent list (Miraidon ex) goes to F and ky3 through `KX_EXTRA_LISTS`. That
  list is built only from what the video showed: Dustin is never asked to identify an opponent's deck.
- **Seats:** in phase 1 the changes act on ky3's own seat only.
- **Code:** a Sonnet job on the API credit worker, one commit per switch, tests first. **The laptop reviews each code diff before
  any run; Fable audits that review.**
- **Decided at the audit (Fable, Oct 15):**
  - the old positions are exported to pg_pos;
  - ky3 starts from 9a0bc5ac with the closest-list fallback restored, and gate 2 covers that;
  - 010837 t03 and 203719 t17 wait for Dustin's ruling, asked one line each. That ruling never blocks phase 1's build.
- **Cost (estimates):** phase 1 is about 25-30 sandbox-hours. That is about 25 positions × 12 replays × 5 arms at the
  position study's F rate (14 for 127 positions), plus 5 self-checks at about 2.2 each. Gate 3 is about 75-80 more, plus F's
  paired games if none exist on this engine. At the exam's rate (about $31 for about 350), that comes to a few dollars, then
  about $7. Gate 3's size and cost go to Dustin first.

## 5. All three failures, in phase 1 (Fable's audit, Oct 15)

Dustin asked to see all three failures handled. Phase 1 builds code only where a clean positive exists today: `_atk`, plus the
Kangaskhan fixes `_punch` and `_queue`. `_expo` is not built on weak positives. Finding the evidence for the other two failures is
part of phase 1, not deferred:
- **Exposing unprepared attackers:** a reader pass over F's 32 skip turns whose last retreat left an Active with no Energy in front.
  It looks for clean positives (F exposed an attacker where a prepared one was the better play) and clean negatives (correct
  sacrifices).
- **Failing to build the Bench:**
  - cases from his own season games on setup decks: the Ladder Log, and pause games as they come;
  - the setup-deck gap in the exam: m64 − F +1.6 (−3.6 to +6.7);
  - the development decks: F − km3 +20.4 ± 5.8, while more thinking time adds nothing there.

**Dustin's two plan passes** (010837 t03, protecting Pawniard; 203719 t17, letting Glimmora fall to grow Overlord's Blade; see
`DESIGN_NOTE_CASES.md`) are `_atk` negatives that a one-turn points watch can't see.
- `EXPECTED.md` records them as a known limit.
- If `_atk` fails them, the next iteration tries a longer watch (through two opponent turns) or a plan-value term, never a special
  case for one card.
- If `_atk` passes them, the report says why: what the watch saw. That would be unexpected.

**The round is not done until** each failure has a measured baseline (km3, F, ky3 with no switch, on its cases) and, wherever a
clean positive exists, a switch tested both ways like `_atk`.

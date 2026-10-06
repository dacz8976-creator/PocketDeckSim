# The Tool-placement rule for the play-outs (the cloud, Oct 6)

Set by the Fable coordinator via Dustin, Oct 5. The Trainer-habit diagnosis (`../playout_trainer_habits_2026-10-05/`) was
accepted; its Copycat rule is parked. This builds the other rule it pointed to: in kx3's play-outs, a Tool is attached
only where its printed effect can apply.
- **Where it lives.** Branch `claude/playout-pilot`, nothing merged.
- **What it touches.**
  - The rule is off by default. `_tools` at the end of a kx code turns it on (`kx3_r16_c12_z2_real_t0_poolmeta_tools`).
    Every earlier code means what it meant.
  - The play-out rule changes only the play-outs, on both sides of the board. The follow-up's tie-break changes kx3's own
    move, and only within the noise. km3 itself is untouched and stays the reference.
  - New code is only under `engine/src/players/` (a new file, `playout_tools.rs`, declared from
    `playout_player.rs`, so `mod.rs` is unchanged), plus tests and examples. The rest of `engine/` is as it was.
- **No table games.** The only games played were checks that the build replays earlier games exactly.
- **The follow-up (Oct 6, amended the same day).** Fable accepted the play-out rule through gate 2 and asked for the
  same rule at kx3's own decision. The first version (c775972d) dropped placements without an effect from kx3's
  candidates. Fable amended it before it was used in any run: a planning bot must keep legal preparation moves
  evaluable (a Poncho on an Active that will retreat, a Tool placed ahead of an evolution). So it is now a
  **within-noise tie-break**, and `_tools` means the play-out rule and the tie-break together. Its results are in "The
  tie-break at kx3's own decision" below; gate 3 tests this version.

## In short: the tie-break at kx3's own decision (Oct 6, amended)

- **What it does.** Every placement stays in kx3's pool and gets its play-outs.
  - Only when no move clears the z bar, and km3's proposed placement has no printed effect now while another placement
    has one, kx3 plays the placement with an effect that km3 prefers. That is km3's choice among them, with the same
    randomness as the play-out rule.
  - The trace says "tie-break: Tool effect" and why km3's placement has none.
  - km3's placement is kept when its play-outs lead that one beyond the noise (2 standard errors); the trace says so.
  - With `_tools` off nothing changes. The play-out rule is as built.
- **Gate 1 passed again** (at dcd703d5).
  - km3 replays the official program's 240 games exactly.
  - Suite: 2,066 passed, 0 failed. With the kept-case test added after gate 2 (14 Tool tests), 2,067 passed, 0 failed.
  - Self-checks: km3 81b572198c04d5d1; LAB 3a2eb43bd9053639 with `_tools` off, twice, and on.
- **kx3's 62 development-run misplacements, decided again** (from each game's own observation and search randomness,
  as the development run played them):
  - With `_tools` off, a fresh kx3 repeats the logged placement in **62 of 62** (131 of 131 counting every placement
    without effect).
  - With `_tools`, **60 of the 62 now land where the Tool has an effect**, all by the tie-break: Poncho 45 of 45, Heavy
    Helmet 14 of 14, Rocky Helmet 1 of 2.
  - **2 stay, by a play-out lead beyond the noise.** At both, km3 had proposed the placement with an effect, and kx3's
    play-outs moved the Tool to a Benched Pokémon:
    - deck 10's Poison Barb to Oricorio, +0.25 (2.2 standard errors);
    - deck 06's Rocky Helmet to Torchic, +0.375 (3.0 standard errors).
    - The tie-break never overrides a play-out lead.
  - None of the 62 was a placement without effect kept by its own play-outs. Gate 2 found one (dev04).
  - kx3's other 69 placements without effect had no spot with an effect (Elegant Cape 44, Heavy Helmet 20, Poison Barb
    5). There's no tie-break there, and all 69 are unchanged.
  - The play-out rule alone (no tie-break) moves **none** of the 62.
- **Gate 2: it doesn't hurt** (LAB, 64 rounds, paired).
  - **The 8 continuation positions** aren't Tool placements, so nothing changes there.
  - **The 12 development positions, one step on** (each Tool played, so the decision is its placement):
    - the tie-break plays the placement with an effect at 9;
    - the play-outs already pick one at 2 (deck 03's Heavy Helmet, dev09 and dev10);
    - at 1, km3's placement is kept by its play-outs. That's dev04: deck 05's Poncho on the Active Indeedee ex leads
      every Bench placement by +0.0625 (2.05 standard errors). It's a preparation move the play-outs value, the case
      Fable wanted kept, and it is now a test.
  - `_tools` on − off is within the noise at all 12 (−0.031 to 0).
- **Gate 3 is updated, still not run:** this version, decks 01, 10, 06, 05 and 03, on the development run's own deals.
  - 400 kx3 games: about 15 hours on the laptop's 2 threads, stoppable and resumable.
  - The self-check digest the laptop's build must print is c426e4c860e836ed.

## In short: the play-out rule (gates 1 and 2 accepted)

- **The rule, as built.** At a Tool placement inside a play-out, km3 chooses as always. If its choice gives the Tool no
  effect and some other placement would, km3 chooses again among those, with the same decision randomness. Where no
  placement has an effect, km3's choice stands.
- **Decided by each Tool's text, not a list of names.** The rule reads the conditions off the card database's text:
  where the holder must be (Active Spot or Bench), its stage, its type, Ancient / Future / Ultra Beast, and a printed
  Retreat Cost. All 26 distinct Tool texts in the database read cleanly (table below). A text with a word the reader
  doesn't know would fail a test and, in play, limit nothing.
- **Gate 1 passed** (identity). km3 from this branch replays the official program's 240 games exactly. The suite
  passes. The strength harness built from this branch prints the pinned km3 self-check, and the pilot's LAB self-check
  is unchanged with the rule off.
- **Gate 2: it doesn't hurt.** Rule on against rule off, paired on the same worlds and seeds, every move kx3 would
  consider:
  - **The 8 continuation positions: no effect at all.** The rule acted in 4 of 9,472 play-outs, and every score is
    identical (and equal to the continuation run's own kx3 scores, 74 of 74). The Tools there are draft A's Elegant
    Capes, and km3 almost always puts them on a Stage 1 already.
  - **12 development positions** (from the development run, at the decision where km3 played a Tool it then
    misplaced): the rule acted in most play-outs. Over the 53 moves where it acted, on − off averaged +0.008 (typical size 0.025).
  - kx3's choice changed at 2 of the 12:
    - **Deck 03 v t-altaria (dev10): clearly for the better.** With Heavy Helmet in hand and Wailord (Retreat Cost 4)
      Active, the rule-off play-outs scored "play Heavy Helmet" 0.48. km3 then put it on Indeedee ex, where it does
      nothing. With the rule on, it goes on Wailord and the same move scores 0.80. So kx3 keeps the Helmet instead of
      switching to Copycat.
    - Deck 05 v t-sceptile (dev04): within the noise (moves 0.06 apart).
- **One thing to watch: Protective Poncho in deck 05.** Playing Poncho scored a little lower with the rule on at 4 of
  the 6 deck-05 positions, and never higher (−0.02 on average).
  - Only one of those is beyond its interval, and with 56 moves tested, about 3 would be by chance.
  - A possible reason: a Poncho on the Active protects that Pokémon after it retreats to the Bench, and the rule never
    allows that placement.
  - Gate 3 on deck 05 would show whether it's real. Decks 01, 10 and 06 meet a Poncho only on t-lucario's side.
- **kx3's own Tool placements (Fable's question).** In the development run, kx3 placed a Tool where the rule would put
  it elsewhere in **62 of its 506 placements** (12%). km3 did so in 63 of 517 on the same deals. So the play-outs do not
  catch it.
  - By Tool: Poncho 45 of 56 (deck 05), Heavy Helmet 14 (decks 01 and 03, 7 each), Rocky Helmet 2 (deck 06), Poison
    Barb 1 (deck 10), Elegant Cape 0.
  - This rule can't change that, because kx3's own placement is not inside a play-out. The follow-up's tie-break, above,
    is the change at kx3's own decision.
- **Gate 3** was first registered for this rule alone on decks 01, 10 and 06. It now tests the rule together with the
  tie-break, on five decks: see "Gate 3" below.

## The rule, as built (`engine/src/players/playout_tools.rs`)

- **Reading a Tool.** Each place the text says "the ... Pokémon this card is attached to" (or "the ... Ultra Beast"):
  - the words before it give the stage ("Basic", "Stage 1", "Stage 2"), the type ("[W]", ...) and the kind
    ("Ancient", "Future", "Ultra Beast");
  - the words after it give the spot ("is in the Active Spot", "is your Active Pokémon", "is on your Bench") and "has a
    Retreat Cost of N or more" (N from the text);
  - a Tool that lowers or removes the Retreat Cost needs a printed Retreat Cost to lower;
  - "its previous Evolutions" needs a Stage 1 or later.
  - "If this card is attached to 1 of your Pokémon" names no holder and adds nothing.
- **What doesn't limit placement.** Conditions of the moment (damage, Special Conditions, a Knock Out to come) can come
  true on any Pokémon, so they never limit where a Tool goes.
- **The spot is read as the holder's spot now.** Fable's example was "Protective Poncho never on the Active". The same
  reading puts Rocky Helmet, Poison Barb, Leftovers and the Darkness/Lightning Tools on the Active only. The Active is
  always there, so those always have an effective placement when the Active qualifies.
- **The choice.** km3 chooses; only if that choice has no effect and an effective placement exists does km3 choose
  again, among the effective ones, from the same randomness. A play-out where km3 never misplaces a Tool is km3's
  exactly. Interventions are counted.
- **Where it applies.** Both sides of every play-out (the pilot's deck and the opponent model). Never kx3's own move,
  never km3 outside the play-outs.

How each Tool in the database reads (`tool_conditions.jsonl`, from `playout_tool_rule --list-tools`; one row per
distinct text):

| Tool | has an effect only on |
|---|---|
| Ancient Booster Energy Capsule | an Ancient Pokémon |
| Beastite | an Ultra Beast |
| Big Air Balloon | a Stage 2 with a printed Retreat Cost of 1 or more |
| Clear Veil, Giant Cape, Lucky Egg, Lucky Mittens, Lum Berry, Rescue Scarf, Sitrus Berry | anywhere (no condition on the holder) |
| Dark Pendant, Deceptive Needle | a [D] Pokémon in the Active Spot |
| Electrical Cord | an [L] Pokémon in the Active Spot |
| Elegant Cape | a Stage 1 |
| Future Booster Energy Capsule | a Future Pokémon |
| Heavy Helmet | a printed Retreat Cost of 3 or more |
| Inflatable Boat | a [W] Pokémon with a printed Retreat Cost of 1 or more |
| Leaf Cape | a [G] Pokémon |
| Leftovers, Poison Barb, Rocky Helmet | the Active Spot |
| Memory Light | a Stage 1 or later (it has previous Evolutions) |
| Metal Core Barrier, Steel Apron | an [M] Pokémon |
| Protective Poncho | the Bench |
| Small Balloon | a Basic with a printed Retreat Cost of 1 or more |

## Gate 1: identity (passed; `checks/`, `tests_before.log`)

- **Tests first** (`engine/tests/playout_tools_test.rs`, 8 tests; `tests_before.log` shows them failing to compile
  before the rule existed):
  - every Tool text in the database is read;
  - the conditions come from the text;
  - a Tool goes only where its effect can apply, on a test board (Alolan Ninetales ex, Vulpix, Carvanha, Mega Sharpedo
    ex);
  - km3's choice stands unless it has no effect and another placement has one;
  - the code spells the rule (`_tools`);
  - with the rule off, the play-outs are kx3's; and where the rule never acts, they are unchanged;
  - where no placement has an effect, the play-outs are unchanged;
  - where km3 would misplace a Tool (a development-run game), the rule acts.
- **km3 is untouched.** km3 from this branch v the official program `rl/engine-2026-10-02/deckgym`, 240 games (seed
  7100): equal game for game, digest 9dde28db2de6c9bc both, and equal to the pinned record.
- **The suite:** 2,061 passed, 0 failed at 4021a4e8 (`checks/suite.log`). At this commit, 2,061 passed and 0 failed
  again (`checks/suite_final.log`; only examples changed).
- **The strength harness built from this branch** (`checks/strength_selfcheck.txt`):
  - km3 prints the pinned self-check, 81b572198c04d5d1;
  - the pilot's LAB self-check (`kx3_r2_c3_lab`) prints 3a2eb43bd9053639 twice;
  - with the rule on (`kx3_r2_c3_lab_tools`) it prints the same 3a2eb43bd9053639: the rule never acts in those games.
    `KX_PARAMS` shows `tool_rule: true`.

## Gate 2: rule on v off at the positions (`gate2/`)

**How.** `engine/examples/playout_tool_rule.rs`:
- At each position it takes kx3's candidates (km3's move first, cap 12) from `evaluate` in LAB mode (the opponent's exact
  list known).
- Then it plays every candidate out R times with the rule off and R times with it on, from the same sampled worlds and
  seeds (`PlayoutPlayer::tool_rule_study`). So the two are paired round by round.
- A rule-off play-out isn't played when the rule never acted in its rule-on twin: it would be the same play-out.
- kx3's choice is computed both ways by its own rule: the best mean replaces km3's move only on a paired lead beyond 2
  standard errors.

**The 8 continuation positions** (`gate2/continuation.jsonl`, R = 128, seeds 24,200,001,000 + i as in the continuation
experiment):
- The rule acted in 4 of 9,472 play-outs (position 3 once, position 8 three times). No score moved, and kx3's choice is
  the same at all 8.
- Every rule-off mean equals the continuation run's own kx3 score for that move (`../playout_continuation_2026-10-05/run/kx3.jsonl`):
  74 of 74, in order. That is a free check that the study plays the same play-outs as kx3.
- Why so little: the Tools at those positions are draft A's Elegant Capes, and km3 mostly puts them on Alolan
  Ninetales ex or Mega Sharpedo ex, both Stage 1. In the diagnosis's 2,048 play-outs there, all 54 Capes that went on a
  non-Stage-1 Pokémon had no Stage 1 to go to instead.

**12 development positions** (`gate2/development.jsonl`, R = 64, seeds 24,200,002,000 + k). Chosen by a fixed rule from
the development run's km3 games: the first misplacement against each panel opponent for deck 05 (6), the first three of
deck 01, the first two of deck 03, and draft A's one. The position is the decision where km3 played the Tool.

| | game | playing the Tool: off → on (on − off, 95% interval) | play-outs the rule acted in | kx3's choice: off → on |
|---|---|---|---|---|
| dev00 | 05 v t-altaria, seat 0, deal 0 | Protective Poncho: 0.391 → 0.375 (−0.016 [−0.046, +0.015]) | 256 of 256 | Energy to the Active → the same |
| dev01 | 05 v t-blaziken, seat 0, deal 0 | Protective Poncho: 0.141 → 0.109 (−0.031 [−0.118, +0.056]) | 319 of 320 | play Poncho → the same |
| dev02 | 05 v t-hydreigon, seat 0, deal 0 | Protective Poncho: 0.125 → 0.109 (−0.016 [−0.069, +0.038]) | 314 of 320 | play Poncho → the same |
| dev03 | 05 v t-lucario, seat 1, deal 0 | Protective Poncho: 0.000 → 0.000 | 320 of 320 | play Poncho → the same (the game is lost) |
| dev04 | 05 v t-sceptile, seat 1, deal 0 | Protective Poncho: 0.641 → 0.578 (−0.062 [−0.122, −0.003]) | 384 of 384 | play Poncho → **attack (Psychic)** |
| dev05 | 05 v t-suicune, seat 0, deal 0 | Protective Poncho: 0.219 → 0.219 (+0.000 [−0.044, +0.044]) | 384 of 384 | Retreat(1) → the same |
| dev06 | 01 v t-altaria, seat 1, deal 1 | Heavy Helmet: 0.375 → 0.359 (−0.016 [−0.108, +0.077]) | 356 of 384 | Energy to the Active → the same |
| dev07 | 01 v t-altaria, seat 1, deal 3 | Heavy Helmet: 0.000 → 0.000 | 184 of 192 | play Helmet → the same (the game is lost) |
| dev08 | 01 v t-blaziken, seat 1, deal 0 | Heavy Helmet: 1.000 → 1.000 | 128 of 256 | play Helmet → the same (the game is won) |
| dev09 | 03 v t-altaria, seat 0, deal 2 | Heavy Helmet: 0.734 → 0.812 (+0.078 [+0.012, +0.144]) | 76 of 384 | Energy to the Active → the same |
| dev10 | 03 v t-altaria, seat 0, deal 3 | Heavy Helmet: 0.484 → 0.797 (**+0.312** [+0.190, +0.435]) | 171 of 192 | play Copycat → **play Heavy Helmet** (km3's move) |
| dev11 | draft A v t-lucario, seat 1, deal 4 | Elegant Cape: 0.234 → 0.188 (−0.047 [−0.099, +0.005]) | 177 of 192 | EndTurn → the same |

- **Every move, not just the Tool:** 53 of the 56 moves had the rule act in some play-out. On − off over those: mean
  +0.008, typical size 0.025.
- Six intervals exclude zero: +0.312 and +0.078 (the Helmet plays at dev10 and dev09), +0.062 three times (dev04 twice,
  dev11 once), and −0.062 (dev04's Poncho). At the 5% level, about 3 of 56 would by chance.
- **"Doesn't hurt":**
  - nothing moved at the 8 continuation positions;
  - on average nothing moved at the 12 development positions;
  - the one large move is the rule doing its job (dev10).
  - So gate 3 is registered.
- **The Poncho caveat.** At deck 05's six positions, playing Poncho is −0.016, −0.031, −0.016, 0, −0.062 and 0 with the
  rule on.
  - Small, and only dev04's is beyond its interval, but never positive.
  - Poncho's text protects the holder while it is on the Bench. A Poncho on the Active protects it after it retreats, and
    the rule (spot read as "now") never allows that placement.
  - If deck 05 shows it in gate 3, the change would be to stop reading the spot as a condition (a Pokémon can move),
    for every spot Tool alike. That would go against Fable's "Poncho never on the Active", so it's Fable's call.
- `gate2/summary.txt` (by `gate2/summarize.py`) has every move at every position.

## kx3's own Tool placements in the development run (`tool_placements.txt`, `dev_games/`)

Fable asked how often kx3 itself, at its own decisions, places a Tool wrongly. kx3 inherits km3's candidate ranking,
but the play-outs should catch it.
- **The data.**
  - The development run (`strength_2026-10-03_kx3_dev`) kept action labels, not traces.
  - So kx3's arm was replayed: the deck's side follows the logged labels, and km3 plays the opponent.
  - **All 560 replayed exactly.** Where a label fits two moves (which Tool a Field Blower discards), the replay tries
    each until the game matches.
  - km3's arm was replayed as in the Trainer-habit diagnosis (560 of 560).
- **The answer: the play-outs don't catch it.**
  - On the deck's side, kx3 placed 506 Tools; 166 had no effect where placed, and 62 had an effective placement
    elsewhere.
  - km3 on the same deals: 517, 167 and 63.

| deck | Tool | kx3: placed / no effect / the rule would move it | km3: the same |
|---|---|---|---|
| 01 | Heavy Helmet | 72 / 26 / 7 | 76 / 25 / 8 |
| 03 | Heavy Helmet | 126 / 14 / 7 | 123 / 16 / 6 |
| 05 | Protective Poncho | 56 / 55 / 45 | 57 / 57 / 48 |
| 06 | Rocky Helmet | 54 / 2 / 2 | 55 / 0 / 0 |
| 09 | Elegant Cape | 45 / 29 / 0 | 47 / 30 / 0 |
| 10 | Poison Barb | 96 / 7 / 1 | 98 / 7 / 0 |
| draft A | Elegant Cape | 57 / 33 / 0 | 61 / 32 / 1 |

- **"No effect" isn't the same as "the rule would move it."** An Elegant Cape with no Stage 1 in play has no effect
  anywhere, so the rule leaves it.
- **Why the play-outs don't catch it** isn't measured here. The likely reason: at the placement decision, the right and
  wrong spots score almost the same over 16 play-outs (a Poncho matters only when something hits the Bench). kx3 keeps
  km3's move unless another leads by 2 standard errors.
- **The panel's side** (km3 in both arms) misplaces t-altaria's Small Balloon (on a Stage 1, or a Basic with no Retreat
  Cost) in about 31 of its 70 games, and t-lucario's Poncho in about 37. Those are the misplacements the rule corrects
  in the opponent model of every deck's play-outs.

## The tie-break at kx3's own decision (Oct 6, amended; `tie_break/`)

**Why a tie-break, not a filter.**
- Fable first asked for a filter: drop the placements without an effect from kx3's candidates when km3 proposes one. It
  was built and tested (tests 06f34bcf, code c775972d) but never used in a run.
- Fable then amended it: a planning bot must keep legal preparation moves evaluable. A Poncho on an Active that will
  retreat, or a Tool placed ahead of an evolution, has no effect now but may be the right play.
- So nothing leaves the pool. The text only breaks ties.

**As built** (`playout_tools.rs`: `tie_break_placements`, `kept_by_playouts`; `PlayoutPlayer::evaluate`):
1. km3 proposes, and kx3 plays out every distinct legal move, as before.
2. kx3 decides as before: the best mean replaces km3's move only on a paired lead beyond z = 2 standard errors.
3. Only if km3's move stands, and it's a placement with no printed effect now while another placement has one:
   - The target is the placement with an effect that km3 prefers: km3's choice among those, with the same randomness
     as the play-out rule's.
   - If km3's placement leads the target by more than 2 standard errors (paired), it is kept. The reason ends "km's
     move kept".
   - Otherwise kx3 plays the target. The reason starts "tie-break: Tool effect: km's Protective Poncho on Indeedee ex
     in the Active Spot has no printed effect now (it needs the Bench), and no move clears the bar (...)".
- If km3's choice isn't in the pool, the best-scoring placement with an effect is the target. That can't happen at a
  Tool's placement, which offers at most 4 moves against a cap of 12.

**Tests** (`engine/tests/playout_tools_test.rs`, 14 in all; `tie_break/tests_before.log` shows the new ones failing to
compile before the code):
- the premise holds only when km3 proposes a placement without effect and another has one, with why in words;
- km3's placement is kept only by a lead beyond z standard errors (fewer than 2 rounds is never beyond);
- with `_tools` off, every placement is in the pool and there's no tie-break (deck 05's first Poncho in a
  development-run game);
- with it on, every placement stays and is played out, and with nothing clearing the bar kx3 plays km3's preferred
  Bench placement, named "tie-break: Tool effect";
- where no placement has an effect (deck 09's Elegant Cape with only Basics), there's no tie-break;
- **a placement without effect that wins its play-outs beyond the noise is kept**: gate 2's dev04, at 64 rounds.

**Gate 1** (`tie_break/checks/`, at dcd703d5):
- km3 v the official program: 240 of 240 equal, digest 9dde28db2de6c9bc, equal to the pinned record.
- Suite: 2,066 passed, 0 failed (`suite.log`); at the final commit, with the kept-case test, 2,067 passed, 0 failed
  (`suite_final.log`).
- Self-checks: km3 81b572198c04d5d1; `kx3_r2_c3_lab` 3a2eb43bd9053639 twice; `kx3_r2_c3_lab_tools` the same
  3a2eb43bd9053639 (neither the rule nor the tie-break changes those 2 games).

**The development run's placements without effect, decided again** (`tie_break/redecide.jsonl`, `redecide.py`,
`redecide.txt`):
- **How.** `trainer_habits scripted --redecide` replays each game of kx3's arm exactly.
  - At each of kx3's placements without effect, a fresh kx3 decides again, from the observation and search randomness
    the game gave it there.
  - Once as in the development run (`kx3_r16_c12_z2_real_t0_poolmeta`), which must repeat the logged placement.
  - Once with `_tools`.
- **All 560 games replayed exactly.** kx3 decided a placement without effect 131 times. (The development run's count
  of 166 includes 35 placements with a single legal spot, which the engine plays without asking.)
- **With `_tools` off, a fresh kx3 repeats the logged placement in 131 of 131.** So each re-decision starts from
  exactly what kx3 saw and drew.

| kx3's placements without effect | count | `_tools` off: repeats the log | `_tools` on: lands where it has an effect | stays without effect |
|---|---|---|---|---|
| another spot had an effect (the rule would move it) | 62 | 62 | **60**, all by the tie-break | 2, by a play-out lead |
| no spot had an effect | 69 | 69 | none possible | 69, unchanged (no tie-break) |

- **By Tool, of the 62:** Protective Poncho 45 of 45 land right; Heavy Helmet 14 of 14; Rocky Helmet 1 of 2; Poison
  Barb 0 of 1.
- **The 2 that stay** are kx3's play-outs at work, not km3's habit: km3 proposed the Active (where these Tools act), and
  the play-outs moved the Tool to a Benched Pokémon by more than 2 standard errors. Deck 10's Poison Barb went to
  Oricorio (+0.25, 2.2 SE), and deck 06's Rocky Helmet to Torchic (+0.375, 3.0 SE).
- **The play-out rule alone moves none of the 62** (`redecide_rule_only.jsonl`, the same 62 with the code of gate 2's
  rule and no tie-break). Its play-outs left km3's move standing 60 times: 43 as the best mean, 17 within the noise. The
  other 2 are the play-out leads above.
- **None of the 62 was kept by its own play-outs.** In 43 of them km3's placement had the best mean, but never by 2
  standard errors at 16 play-outs.

**Gate 2** (`tie_break/gate2.jsonl`, `gate2_stdout.txt`; `playout_tool_rule --tie-break`; LAB, 64 rounds, the
positions' seeds):
- The 8 continuation positions aren't Tool placements: kx3's pool is the same with `_tools` on, and the tie-break never
  applies. The play-out rule's own gate 2 there (above) stands.
- The 12 development positions are advanced one step: their Tool is played (km3's move there), so the decision is the
  placement. Every placement is played out with the play-out rule off and on, and kx3's choice is taken both ways.

| | game | Tool | km3 proposes (spot) | spots with an effect | kx3, `_tools` off | kx3, `_tools` on | km3's lead over the target | tie-break | on − off (95%) |
|---|---|---|---|---|---|---|---|---|---|
| dev00 | 05 v t-altaria | Protective Poncho | 0 | 3 | 0 | 3 | −0.016 (1.0 SE) | applied | +0.000 [−0.044, +0.044] |
| dev01 | 05 v t-blaziken | Protective Poncho | 0 | 3 | 0 | 3 | +0.016 (0.4 SE) | applied | −0.016 [−0.097, +0.066] |
| dev02 | 05 v t-hydreigon | Protective Poncho | 0 | 2, 3 | 0 | 3 | +0.031 (1.4 SE) | applied | −0.031 [−0.074, +0.012] |
| dev03 | 05 v t-lucario | Protective Poncho | 0 | 2, 3 | 0 | 3 | +0.000 (every round equal) | applied | +0.000 [+0.000, +0.000] |
| dev04 | 05 v t-sceptile | Protective Poncho | 0 | 1, 2, 3 | 0 | 0 | +0.0625 (2.05 SE) | **kept by its play-outs** | +0.000 [+0.000, +0.000] |
| dev05 | 05 v t-suicune | Protective Poncho | 0 | 1, 2, 3 | 0 | 3 | +0.000 (0.0 SE) | applied | +0.000 [−0.044, +0.044] |
| dev06 | 01 v t-altaria | Heavy Helmet | 0 | 3 | 0 | 3 | +0.016 (0.3 SE) | applied | −0.016 [−0.135, +0.104] |
| dev07 | 01 v t-altaria | Heavy Helmet | 0 | 1 | 0 | 1 | +0.000 (every round equal) | applied | +0.000 [+0.000, +0.000] |
| dev08 | 01 v t-blaziken | Heavy Helmet | 0 | 1, 2 | 0 | 2 | +0.000 (every round equal) | applied | +0.000 [+0.000, +0.000] |
| dev09 | 03 v t-altaria | Heavy Helmet | 3 | 1 | 1 | 1 | −0.078 (2.3 SE) | not needed: a play-out lead | +0.000 [+0.000, +0.000] |
| dev10 | 03 v t-altaria | Heavy Helmet | 3 | 0 | 0 | 0 | −0.312 (5.0 SE) | not needed: a play-out lead | +0.000 [+0.000, +0.000] |
| dev11 | draft A v t-lucario | Elegant Cape | 0 | 2 | 0 | 2 | +0.031 (1.4 SE) | applied | −0.031 [−0.074, +0.012] |

- Spot 0 is the Active.
- **On − off is within the noise at all 12.** Where the tie-break applies, the placement with an effect scores within
  the noise of km3's, by definition. At dev02 and dev11 it scores 0.03 lower (1.4 standard errors).
- **dev04 is the kept case.** Deck 05's Poncho on the Active Indeedee ex scores 0.641; every Bench placement scores
  0.578. km3's placement leads by +0.0625 with a standard error of 0.0305: 2.05 standard errors, just over the bar.
- **dev09 and dev10:** the play-outs already move deck 03's Heavy Helmet to the Wailord or Wailmer that it helps (+0.08
  and +0.31), with or without `_tools`.

## Gate 3: the laptop's paired cut (registered here, not run)

Updated Oct 6 for the amended version: it tests the play-out rule and the tie-break together, on decks 01, 10, 06, 05
and 03 (Fable added 05 and 03).

**Design.**
- **Pilot:** `kx3_r16_c12_z2_real_t0_poolmeta_tools`. That is the development run's kx3 (REALISTIC, the pool's 8 meta
  lists, 16 play-outs, cap 12, z 2) plus `_tools`: the play-out rule and the tie-break at its own decision.
- **Reference:** km3.
- **Decks 01, 10, 06, 05 and 03** against the 8 panel lists, 5 deals x 2 seats: the development run's own deals.
- **The rule-off arm is already played.** The config (`gate3/config.json`) lists the seven development decks in that
  run's order, with its seed_base, so every seed is that run's. Only the five decks are played (`--only-deck`).
  So that run's X arm is the rule-off arm, and the harness plays only 400 kx3 games (and 400 km3 games, seconds each):
  about 15 hours at the development run's pace on the laptop's 2 threads.
- **Build check, before reading.** Every km3 reference game must replay the development run's game decision for decision,
  or the pairing is void. `gate3/pair_with_dev.py` checks this first.
- **Reading** (fixed now, `gate3/pair_with_dev.py`):
  - rule on − rule off in game score (win 1, tie ½, loss 0) on the same deck, opponent, deal and seat;
  - mean ± 1.96·sd/√n, per deck and pooled, with every deck weighted equally as a second figure;
  - how many pairs differ at all;
  - for context, kx3 − km3 with the rule on and off on the same deals.
  - The harness's own report (kx3 with the rule − km3) is context too.
- **Size, stated in advance.** 80 paired games a deck is a first cut. It can show a large harm, not a small gain.

**Why pairing with the development run is sound** (`gate3/replay_check/REPLAY_CHECK.txt`):
- The harness was built here from this branch and played, with the rule off, deal 0 seat 0 against t-altaria and
  t-blaziken for decks 06, 10, 01 and 05.
- All 16 games (8 kx3, 8 km3) equal the development run's, decision for decision (437 logged decisions).
- Every km3 reference game of those four decks (320) does too.
- The self-check: with the play-out rule alone, gate 3's pilot printed the development run's own kx3 digest,
  31d638dbc818b0fa (`checks/strength_selfcheck.txt`). With the tie-break it prints c426e4c860e836ed
  (`tie_break/checks/strength_selfcheck_gate3.txt`).
- `engine/` outside `src/players/` hasn't changed since d513e37b, the development run's build.

**Where the rule will act.** km3's own games are a fair guide to what km3 does inside the play-outs. A misplacement the
rule would move happened in:

| deck | games (of 80) | on whose side |
|---|---|---|
| 01 | 20 | its own Heavy Helmet 8; t-altaria 6, t-lucario 6, others 2 |
| 10 | 6 | t-altaria 3, t-lucario 3 |
| 06 | 11 | t-altaria 5, t-lucario 5, t-hydreigon 1 |
| 05 | 50 | its own Poncho 48; t-lucario 7, t-altaria 3 |
| 03 | 19 | its own Heavy Helmet 6; t-altaria 8, t-lucario 7, t-weezing 1 |

- So in decks 10 and 06 the rule mostly changes how the opponent is modelled, and many of their pairs will play out
  identically.
- The tie-break acts at kx3's own placements: decks 05 (Poncho), 01 and 03 (Heavy Helmet), rarely 06 and 10.

**The laptop's steps** (after the exam):
1. In GitHub Desktop: **Fetch origin**, switch to branch `claude/playout-pilot`, **Pull origin**.
2. Build the harness against this branch's engine, from the repository root in WSL:
   `rl/strength/build.sh origin/claude/playout-pilot /home/dacz8976/kx/strength_tools`.
   It prints the engine tree and the program's sha256.
3. Pre-register (this runs the self-checks):
   `python3 rl/strength/strength_prereg.py --config rl/results/playout_tool_rule_2026-10-06/gate3/config.json --out rl/results/strength_<date>_kx3_tools_gate3`
   - km3 must print 81b572198c04d5d1.
   - `kx3_r16_c12_z2_real_t0_poolmeta_tools` must print **c426e4c860e836ed**, as the cloud's build did.
   - That self-check is 12 games with kx3 on both sides: 2 h 11 min in the cloud on 4 cores.
   - If either digest differs, stop and report: the build isn't this one.
4. Run, from the repository root:
   `nice -n 19 /home/dacz8976/kx/strength_tools run --manifest rl/results/strength_<date>_kx3_tools_gate3/manifest.json --out rl/results/strength_<date>_kx3_tools_gate3 --only-deck 01-muk-glimmora-kingambit-regigigas --only-deck 10-xatu-oricorio-tr-weezing --only-deck 06-mega-blaziken-tournament-list --only-deck 05-indeedee-stoutland --only-deck 03-wailord-indeedee-wall`.
   - Add `--stop-after-min M` to stop; the same command resumes.
   - The decks play in the manifest's order: 06, 10, 03, 01, 05.
5. Read:
   - `python3 rl/results/playout_tool_rule_2026-10-06/gate3/pair_with_dev.py rl/results/strength_<date>_kx3_tools_gate3`
     (the primary reading);
   - `python3 rl/strength/strength_report.py --dir rl/results/strength_<date>_kx3_tools_gate3` (context).
6. In GitHub Desktop: **Commit** the run folder, then **Push origin**.

## Files

- Code (branch `claude/playout-pilot`):
  - `engine/src/players/playout_tools.rs`: the rule, from reading a Tool's text to the wrapper around km3 in the
    play-outs, and the tie-break's premise (`tie_break_placements`, `kept_by_playouts`);
  - `engine/src/players/playout_player.rs`: the `_tools` part of the code, the play-outs' wrapper, `tool_rule_study`,
    and the tie-break in `evaluate`;
  - `engine/tests/playout_tools_test.rs`: 14 tests (8 for the play-out rule, 6 for the tie-break);
  - `engine/examples/playout_tool_rule.rs`: the play-out rule's gate-2 runner, the tie-break's (`--tie-break`), and
    `--list-tools`;
  - `engine/examples/trainer_habits.rs` (from the diagnosis): now gives the rule's verdict on every Tool placement,
    dumps positions, replays the kx3 arm from its labels (`scripted`), and decides kx3's placements again
    (`--redecide`).
- Here:
  - `tests_before.log`; `checks/` (km3's 240-game replay, both suite logs, the self-checks);
  - `tool_conditions.jsonl`: every Tool text and the conditions read from it;
  - `dev_games/`: the Tool events of both arms of the development run, with the replay checks;
    `tool_placements.py` and `tool_placements.txt`;
  - `gate2/`: the positions (`positions*.json`, `states/`), the outputs (`continuation.jsonl`, `development.jsonl`, their
    stdout), `summarize.py` and `summary.txt`;
  - `tie_break/`: `tests_before.log`; `checks/` (gate 1 for the tie-break, and the gate-3 pilot's self-check);
    `positions.json`, `gate2.jsonl` and `gate2_stdout.txt`; `redecide.jsonl` (with `_tools`), `redecide_rule_only.jsonl`
    (the play-out rule alone, the 62), `redecide.py` and `redecide.txt`;
  - `gate3/`: `config.json`, `pair_with_dev.py`, `replay_check/` (the 16 replayed games and `REPLAY_CHECK.txt`).

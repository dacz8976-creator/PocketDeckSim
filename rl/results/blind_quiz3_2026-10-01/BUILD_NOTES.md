# Blind quiz 3 ("Your Move, Blind 3") build notes (Sept 30, 2026)

This folder is private: it holds the answer key. Dustin should only ever see the page built from `positions/`.

The quiz has the designer's 12 positions (`candidates/selection.json`), in the designer's page order, as Q01-Q12. Each is the first point where two pilots chose differently on the same deal, on the official engine (`rl/engine-2026-09-30/deckgym`, sha256 119389c5…d215, re-hashed by the build). No position was dropped. No new games were played: everything was rebuilt from the saved plies in `candidates/`. Nothing was written to the repo, nothing was committed and nothing was published.

## Files

| file | what |
|---|---|
| `positions/Q01.json` … `Q12.json` | What the page shows: one document per position, in quiz 2's `positions` format. The doc id is the file name (the model's own `id` is dropped, as in `quiz3-2026-09-27/seed_docs`). There are no seeds, pilot names, results or hints. |
| `answer_key4.json` | Private. `_about` holds the grading rule. Then, for each Q, both pilots' choices (`new_choice` = km3 on table deals, kta3 (and km3) on Dustin's decks; `other_choice` = kta3 or kog3), with: option keys and text, whole turn, the graded part before any draw, what came after the draw, result, final points and turn, and game fingerprint. Each Q also has the seed, seats, `decision`, `grading_rule`, hidden information, notes, replay checks and the page's option list. |
| `build4.py` | The build and every check. Run it from the repo root in WSL: `python3 -B build4.py`. It reads the repo and `mirror/` but never writes to them. |
| `build4.log` | The full output of the last run (0 problems). |

The page fields are the same as quiz 2's seed docs (`order, matchup, turn, you_went_first, situation, points, you, opponent, stadium, turn_effects, this_turn_so_far, log, options, cant_play`), plus one new field, `question`: "What do you do this turn, in order? …". **The published quiz 2 page doesn't display `question`.** Its form already asks the same thing in two parts (the first tap, then the rest of the turn, with "then depends on the draw" after a draw card). On the current page the field is just ignored, so it is safe either way.

## The positions

The newer choice is km3's on table deals and kta3's (and km3's) on Dustin's decks. Results are for the player's deck, each from one game.

| Q | from | your deck v opponent, turn | type | newer choice: first tap → result | other choice: first tap → result |
|---|---|---|---|---|---|
| Q01 | T12 | Lucario v Weezing, t2 (went second) | (a) | km3: Arena of Antiquity → win 4-0, t8 | kta3: bench Hitmonlee → loss 2-5, t13 |
| Q02 | T10 | Suicune v Lucario, t2 (second) | (b) | km3: Field Blower (on the Arena) → win 3-2, t12 | kta3: Center Lady (Field Blower on Poncho) → loss 2-3, t11 |
| Q03 | J02 | deck 07 Skarmory v Lucario, t5 (first) | (c) | kta3/km3: Jasmine → win 3-2, t9 | kog3: Watch Over (then Red) → loss 0-4, t8 |
| Q04 | T04 | Altaria v Suicune, t4 (second) | (a) | km3: Training Area → loss 0-3, t7 | kta3: evolve Mega Altaria ex → loss 2-3, t9 |
| Q05 | T08 | Suicune v Altaria, t7 (first) | (b) | km3: Field Blower (on Training Area) → win 5-2, t9 | kta3: Buster Tail → loss 2-3, t8 |
| Q06 | H01 | deck 01 v Vespiquen, t6 (second) | (c) | kta3/km3: Heavy Helmet (on Benched Regigigas) → win 2-2, t16 (opponent left with no Pokémon) | kog3: Lucky Ice Pop (Helmet on Active Muk) → loss 2-3, t19 |
| Q07 | T05 | Lucario v Altaria, t8 (second) | (a) | km3: Arena of Antiquity → loss 2-5, t13 | kta3: Fighting Pulse → win 5-2, t12 |
| Q08 | T11 | Weezing v Lucario, t5 (first) | (b) | km3: Field Blower (on the Arena) → loss 1-4, t10 | kta3: D on Hoopa ex → win 3-2, t11 |
| Q09 | J03 | deck 07 Skarmory v Altaria, t1 (first) | (c) | kta3/km3: Starting Plains (then Jasmine) → loss 0-4, t8 | kog3: Professor's Research → win 3-2, t15 |
| Q10 | T06 | Altaria v Hydreigon, t4 (second) | (a) | km3: Training Area → loss 2-3, t13 | kta3: evolve Espeon → win 4-2, t12 |
| Q11 | T09 | Suicune v Altaria, t9 (first) | (b) | km3: Soothing Shore → win 4-2, t11 | kta3: W on Suicune ex → loss 1-4, t10 |
| Q12 | H03 | deck 03 Wailord v Sceptile, t6 (second) | (c) | kta3/km3: Heavy Helmet (on Benched Wailord ex) → loss 1-3, t13 | kog3: Soothing Shore (Helmet on Active Wailord) → win 4-2, t20 |

Across the 12 positions, the newer choice won 6 (Q01, Q02, Q03, Q05, Q06, Q11) and lost 5 (Q07, Q08, Q09, Q10, Q12). In Q04 both choices lost. These are single games, so they don't count as evidence either way. In Q06, kta3's game is recorded as a win for seat 0 at 2-2. It is not a win on points: Poison Knocked Out the opponent's last Pokémon (Vespiquen ex) at the end of turn 16, so the opponent had no Pokémon left (checked by the verifier, see VERIFY_NOTES.md). That is the committed result, unchanged here.

## Grading

- **Rule (in the key):** grade only the part of the turn before any draw.
  - A draw is any card that puts unseen cards into the hand: Professor's Research, Copycat, Poké Ball, or using Mesagoza (or Fragrant Forest).
  - The draw card itself is part of the plan. Everything after it isn't graded.
  - The same cut applies to Dustin's plan. If he plays a draw before he reaches the deciding card, mark the position "decided after a draw" instead of guessing.
  - Suicune ex's Legendary Pulse draws at the end of the turn, so it never cuts a plan short.
- **Where the cut falls:**
  - Q06: both pilots use Mesagoza. Its flip found the Kingambit that Rare Candy used, so Rare Candy and the D on Regigigas aren't graded.
  - Q09: kog3's Research is its first tap, so only "Research" is graded on that side.
  - Q10: both play Copycat. Where the P goes (Espeon or Darkrai) came after the draw, so it isn't graded. Training Area before Copycat (km3) or not (kta3) is.
    - Holding Training Area means Copycat shuffles it back into the deck.
  - The other nine positions have no draw in either plan. In Q01 and Q12 the Research had already been played before the position (it shows under "this turn so far").
- **The first tap always settles it only in Q05 and Q07,** where the other plan is a plain attack. Everywhere else, some first taps say nothing on their own, because both plans share that move. When Dustin's first tap is one of these, grade the written plan against `decision`:
  - Q01: bench Hitmonlee.
  - Q02: Center Lady.
  - Q03: Watch Over / Ice Pop.
  - Q04: evolve.
  - Q06: Ice Pop.
  - Q08: the attach.
  - Q09: Starting Plains / bench Indeedee ex.
  - Q10: evolve.
  - Q11: the attach.
  - Q12: Soothing Shore.
  - In Q02, Q06 and Q12 every first tap needs the plan. The decision there is a follow-up choice the option doesn't name: Field Blower's target, or which Pokémon holds the Helmet.
- **Answers that match neither plan:**
  - Q01: an attack without the Arena, or the Arena without an attack.
  - Q02: no Field Blower.
  - Q03: Sabrina or no Supporter.
  - Q06: the Helmet on Pawniard.
  - Q09: no Supporter.
  - Q12: the Helmet on an Indeedee ex.
- Q11 is probably the easiest: Training Area's +10 turns Mega Harmony's 130 into exactly Suicune ex's 140 HP. Q05 has the same sum against Baxcalibur's 140.

## Checks (all passed; `build4.log`)

1. **Engine:** the hash equals quizlib's `ENGINE_SHA` (119389c5…d215). No game was played.
2. **Mirror:** the decklist copies in `mirror/decks/research/` equal a fresh conversion of `decks/dustin/` and `decks/screen/opponents/t-*`, and plain copies of `decks/research/`. The check is read-only.
3. **Fork:** for all 12, `first_diff` of the two pilots' saved games is exactly the candidate's ply and kind "choice":
   - states and choices are equal before it;
   - the state at the fork is equal;
   - both games offer identical legal moves there;
   - the deciding seat is the one to move.
4. **km3 on Dustin's decks:** in Q03, Q06, Q09 and Q12, km3's whole game is identical to kta3's, ply by ply (states and choices). km3 also picks kta3's option at the fork, and the two fingerprints are equal.
5. **Blind render:** each page was rendered once from each pilot's game, and the two renders are identical. They also equal the render stored in `candidates/<id>.json`. The page data doesn't depend on which pilot did what.
6. **Pilots' moves:**
   - Each pilot's whole turn, rebuilt with `describe.turn_lines`, equals the candidate's.
   - Option keys, whole turns and results all equal selection.json.
   - The two first moves are different options.
   - The two graded parts differ in which cards were played or where they went, not only in order.
7. **Every line of the twelve turns is sorted as "draw" or "not a draw"** from a fixed list. An unknown line stops the build.
8. **Leak test** (quiz 2's, adapted, plus pilot and seed patterns):
   - The fields are exactly quiz 2's plus `question`, and `matchup` holds only your own deck.
   - **Opponent:** only the public fields show (hand size, which is correct, and Next Energy only).
   - **Banned text:**
     - no seed (72xxxxxx or 23004xxxxxx);
     - no pilot name (any k?3 form, km, kta, kog) or the word "pilot";
     - no candidate id (T12, J02, …);
     - no result, outcome, choice or winner fields;
     - no state, hands, decks or cards;
     - no deck file names (t-…, dustin-0…, ../, opponents/);
     - no "panel", "newer", "older", "bot" or "baseline".
   - **Cards:** no opponent hand card or deck-only card is named. The opponent's deck name appears only inside card names you've seen.
   - **Own decklist:** exact; only your own 20 cards, with "left" equal to the deck.
   - **Options:** every legal move sits behind exactly one option, in `describe.build_options` order. There are 76 options for 83 legal moves, and 5 options merge identical Bench spots (7 moves folded in):
     - Q01: Hitmonlee to Bench 1, 2 or 3;
     - Q04: P to Eevee on Bench 1 or 2;
     - Q09: Indeedee ex to Bench 1, 2 or 3;
     - Q10: P to, and the evolve of, Eevee on Bench 1 or 2.
     - None of the merged spots differ in a hidden engine field.
9. **Planted leaks:** 261 leaks of 22 kinds were planted across the 12 positions, and all 261 were caught.
10. **describe.py's self-test, 0 problems:**
    - 24 seats were checked against the deck lists.
    - The Retreat Cost model agrees with the engine in 12 positions.
    - 44 hand cards were checked for playability. For Dustin's cards this goes through render4's shim, so that check is circular there.
    - Every between-turn knockout and HP change in the logs is explained.
    - 104 hidden-only names were checked.
    - Planted card and deck-name leaks are caught.
11. **describe.py** is unchanged: its sha256 AE5298E1… equals `quiz3-2026-09-27/describe.py`.

## Things to know

- **Rules oddity:** Q06 (deck 01) and Q12 (deck 03) offer "Use the Stadium Fragrant Forest", but neither deck has a Basic Grass Pokémon (checked against the shown decklists). It's the same as quiz 2's note 5. Neither pilot chose it, and deck 03 used it on turn 4 (shown in Q12's log).
  - The options are left exactly as the engine offers them, so the page stays true to the engine.
  - If Dustin picks it, that probably tells us more about the real game's rule than about his plan.
- **Q06:** kta3's game is a win at 2-2, because the opponent was left with no Pokémon (see above).
- **Q06 page note (added by the verifier):** Alolan Muk's Power of Alchemy is in play, so the two Shuckle ex, Teal Mask Ogerpon ex and your Regigigas have no Ability. The page now says so on each of them. Re-running `build4.py` would rewrite `positions/` and drop these notes.
- **Reserves:**
  - T07 (the same Soothing Shore decision as Q11);
  - H02 (Heavy Helmet, where the decklist count needs the played Tool counted);
  - T01 (not a Stadium, Field Blower or Tool decision).
  - None of them were built.
- **The designer dropped** T02, T03 and J01 (they differ only in the order of the same moves).

## Not done

- No artifact was published or changed, and no db document was written. To use the page:
  - load `positions/Qnn.json` as documents `Qnn` in a new artifact's `positions` collection;
  - use quiz 2's page, which needs no change, and keep its own "answers" collection.
  - Quiz 2's store already holds answers under Q01-Q10, so the new quiz needs a new artifact, the same reason quiz 2 was one.
- Nothing in the repo was touched, and there is no commit.

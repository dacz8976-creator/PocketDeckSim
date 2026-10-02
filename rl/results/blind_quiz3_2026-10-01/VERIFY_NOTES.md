# Blind quiz 3 ("Your Move, Blind 3"): independent check (Sept 30, 2026)

Private, like the rest of this folder. This is a second check of `positions/Q01-Q12.json` and `answer_key4.json`. It does not reuse `build4.py`, `describe.py` or `quizlib.py`. It reads the saved games in `candidates/` directly, gets card facts from `lib/card.py`'s own loader, and re-plays some games on the official engine.

**Result:** all 12 positions pass. I found one real gap on the page (Q06, fixed) and one misleading wording (Q06's 2-2 "win on points", fixed in the notes). No position needs to be dropped.

## What was checked, for every position

1. **The fork.** I found, on my own, the first ply where the two pilots' saved games differ. Every one is a choice, at the key's `ply_index`:
   - states are equal up to it;
   - both games offer the same legal moves there;
   - the deciding seat is the one to move;
   - the turn and `you_went_first` match.
2. **The board against the engine state at that ply.** For both sides:
   - each Pokémon in each slot, with HP (printed HP plus Tool and Stadium bonuses, minus damage), Energy, Tools and Special Conditions;
   - points, deck counts, discard piles, discarded Energy and the Next Energy;
   - your current Energy, your hand (as a set of cards), and whether you've already played a Supporter or retreated this turn;
   - the Stadium and who played it;
   - the opponent's hand count.

   Your decklist was checked against all 20 of your cards across every zone, and each card's "left" count against the deck. For table decks, the list was also checked against `decks/research/<deck>.txt` by card id.
3. **Hidden information.** The opponent shows only: Active, Bench, deck count, discard, discarded Energy, Next Energy (never the current one) and hand count.
   - No opponent hand card or deck card is named.
   - The opponent's deck name only appears inside card names that have been played in view.
   - Grepping the 12 files for pilot names (km/kta/kog/k?3), "pilot", "bot", "newer", "older", "baseline" or "panel", candidate ids, seeds, and result, answer or hint words found nothing. The one hit, "needed to win", is part of Mars's card text.
4. **Which pilot is which.**
   - Everything shown comes from the shared history before the fork, which is identical in both games, so the page can't depend on the pilot.
   - The options are ordered by group (attack or Ability, then Supporter, Item, Tool, Stadium, Stadium use, Energy, Pokémon, evolve, retreat, end turn), the same in all 12. Nothing marks either pilot's option.
5. **The two choices.** Each pilot's move at the fork is the legal move whose number is in that pilot's `option_keys`. The option's text matches the page. Each `whole_turn` matches the raw moves that followed, and `options_on_page` equals the page.
   - On Dustin's decks (Q03, Q06, Q09, Q12), km3's saved game is identical to kta3's, ply by ply.
6. **Card facts.** These were all checked against `lib/card.py`, by the card id in the engine state:
   - every Pokémon on the board: name, stage, type, HP, Weakness, Retreat, Ability text, and each attack's cost, damage and text;
   - every hand and decklist card's text, including the two different Frigibax cards;
   - the Stadium text and every option's card text.

   I also re-checked the key's sums with card.py:
   - Mega Harmony: 40 plus 30 for each of Altaria's 3 Benched = 130, and +10 from Training Area = 140, which is exactly Baxcalibur's or Suicune ex's 140 HP.
   - Fighting Fist: 10 + 30 against an ex + 20 from the Arena = 60.
   - Steel Wing: 70, or 90 with Red.
   - Retreat costs for Heavy Helmet: Regigigas 4, Alolan Muk 3, Wailord / Wailord ex 4, Pawniard / Indeedee ex 1.
7. **The log.** Every line of every turn before the fork, and "this turn so far", was compared with the raw moves. All matched, including the knockouts, Promotes and end-of-turn damage.
8. **Re-traced on the engine.** I used `rl/engine-2026-09-30/deckgym` (sha256 119389c5…d215 OK), one game each, under nice 10, with the same seed, seats and pilots. 7 games:
   - Q01 km3 and kta3;
   - Q06 kta3 and kog3;
   - Q11 km3 and kta3;
   - Q12 km3.

   All 7 match the saved games exactly, every state and every move. Each fork move falls under the key's option. Results equal the committed rows: table winner/points/turns, and A/B move fingerprints b7af549169c6417d and 8b16c3e6c1977252. In Q12, km3 makes kta3's choice (Helmet, option 6) and plays kta3's whole game.

## Fixes made

- **Q06 page (`positions/Q06.json`).** Your Active Alolan Muk's Power of Alchemy says Basic Pokémon in play have no Abilities, and the engine applies it. The page still showed Solid Shell on both Shuckle ex, Soothing Wind on Teal Mask Ogerpon ex, and Seal of Antiquity on your Regigigas, with nothing to say those Abilities are off. Because Seal of Antiquity is off, Regigigas can attack, and that bears on where the Helmet goes.
  - Added one line to each of those four Pokémon's `notes`: "Ability off: Basic Pokémon have no Abilities while Alolan Muk is in play (Power of Alchemy)".
  - Nothing else changed (diffed). The note is the same whichever pilot's game the page comes from.
  - Re-running `build4.py` would rewrite `positions/` without it.
- **Q06's 2-2 "win" (`BUILD_NOTES.md`, and a note in the key's Q06 `notes`).** kta3's game isn't a win on points. Vespiquen ex (170 HP with Leaf Cape, 160 damage, Poisoned) was the opponent's last Pokémon, and Poison Knocked it Out at the end of turn 16. That left the opponent with no Pokémon. The result itself (win for your deck, 2-2, turn 16) is unchanged and matches the committed row.

## Noted, not changed

- **Your current Energy label.** Q05 and Q07 show "already attached", and Q09 shows "none (first player's first turn)", where the engine has no current Energy. Both are true page wording, not errors.
- **Q08.** The engine state still holds Korrina's +30 under turn 4, the turn it was played. It has run out, so the page is right to show no turn effects.
- **Q12.** The database text for Mega Sceptile ex's Terminating Tail reads "Discard Grass[G] Energy". The page says "Discard a Grass Energy", which is what the engine does: it discards one Grass Energy.
- **Q10.** The Copycat option adds "(your opponent has 2 cards in hand, so you'd draw 2)". That's correct.
- **Q06 and Q12 offer "Use the Stadium Fragrant Forest"** to decks with no Basic Grass Pokémon. This is the build notes' known oddity. It fits the rule that a card is blocked only when what you can see shows it can't work.
- **Q02.** Bonsly's Teary Attack shows on Suicune ex as "Its attacks do 30 less damage (until the end of this turn)". That's correct: the effect lasts through this turn.

## Per-position verdict

| Q | from | verdict |
|---|---|---|
| Q01 | T12 | pass |
| Q02 | T10 | pass |
| Q03 | J02 | pass |
| Q04 | T04 | pass |
| Q05 | T08 | pass |
| Q06 | H01 | pass after the fix (Power of Alchemy notes; the 2-2 wording) |
| Q07 | T05 | pass |
| Q08 | T11 | pass |
| Q09 | J03 | pass |
| Q10 | T06 | pass |
| Q11 | T09 | pass |
| Q12 | H03 | pass |

Each question can be answered from what the page shows. The deciding facts are all on the page: the Stadium in play and who played it, Tools, HP, Energy, attack and Ability texts, the hand, and the decklist with the counts left.

The verifier's scripts are in the session scratchpad: `wf_sq/quiz-verifier/` (`verify.py`, `logcheck.py`, `optcheck.py`, `keycheck.py`, `abcheck.py`, `retrace.py`). Nothing in the repo was touched, nothing was committed and nothing was published.

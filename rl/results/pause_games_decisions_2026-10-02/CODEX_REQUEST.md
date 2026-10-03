# Request for the Codex agents: what to add when they re-review games (Oct 2, 2026)

## Update, Oct 2 evening: read this first (the sections below are the original request; the parts already done are marked)

**Done with your batch, thank you.** All five uncertain Draft A hands (`132311` turns 5 and 11, `115323` turn 13, `143837` turns 5 and 7) match what had been assumed, so nothing changed there. Deck 03 games `021402` and `022135` are now built from your hand packets (12 of his turns). So items 1 and 2 of section 2 are finished; item 3 (the Ladder Log games) is your batch in progress, and item 4 (the 26 Auto recordings, one game per deck first) is not started.

**What would help most in the next batch, in order:**

1. **Boards at the start of each owner turn as fresh observations.** The packets this time inherit every board from the accepted review's prose, so some values had to be estimated: the opponent's Energy per Pokémon (the review gives totals, not who holds what), bench order, discard counts. Per owner turn, for both players: every Pokémon in play left to right (name, HP now / maximum, Energy by type, Tool, the evolution stack underneath), the Stadium, both players' points, and the opponent's discard count whenever a pile is opened.
2. **Choices he makes during the opponent's turn.** A forced switch (the opponent's Sabrina) or the promotion after a knockout: write the options on screen and the one he picked, with the frame time. Two such decisions could not be built: `021402` game turn 8 and `023418` game turn 6.
3. **Deck lists for the old Ladder Log games.** The packets say the exact 20 cards are unavailable. If the Ladder Log or Dustin has them, add them: a position needs the list for the cards not yet seen. If nobody has them, the closest list in `decks/dustin/` could stand in and be marked approximate (decision for Dustin; do not substitute without it).
4. **Who made each decision**: the batch already records the Auto flag for a whole game; for Auto games add, per owner turn, whether the decisions were the game's Auto or his own.

**For Dustin to hand to Codex. Written from text only.**

(original request follows)

For Dustin to hand to Codex. Written from text only. It says what has already been rebuilt, in what order to re-review, exactly what to add, and what not to redo.

## 1. What has been rebuilt from the ten pause games

A "turn" here is one of his turns. "Text" = rebuilt from the written review (opening hand, drawn cards and plays named there). "Stills" = read from still frames. "Elimination" = the one card the review's own later plays force. "Checked" = text predicted the hand and stills confirmed it.

**Draft A (the five `shark_sol` games): every one of his 32 turns has a rebuilt hand.**

| recording stem | result, order | his turns (game turn numbers) and how each hand was fixed |
|---|---|---|
| `20261002_143837000` | won by concession 2-1, went first | 1 and 3: stills (the review never names the opening hand); 5 and 7: elimination (the Poké Ball he plays on turn 5 can only be that turn's draw); 9, 11, 13: checked |
| `20261002_114458000` | won 3-2, went second | 2: text; 4, 6, 8: stills (Research's two draws on turn 2 and the cards after his Copycat are not named); 10, 12: checked |
| `20261002_115323000` | lost 2-3, went first | 1, 3, 5, 7: text (best-written game: every draw and Copycat draw named); 9, 11, 13: checked |
| `20261002_132311000` | won 2-0 (opponent timed out), went first | 1: text; 3, 5, 7: stills (Research's two draws on turn 1 and on turn 7 are not named); 9, 11, 13: checked |
| `20261002_143309000` | won 3-0, went second | 2, 4, 6, 8: text; 10: checked (the best-written game for hands) |

Still only **probable**, not certain: `132311` turn 5 (the second Mega Sharpedo ex: fixed by card count) and turn 11 (the Elegant Cape: seen played within seconds of the turn banner, not in the fan); `115323` turn 13 (the Alolan Ninetales ex: seen being dragged from the fan); `143837` turns 5 and 7 (elimination, not seen). The **opponent's hand size** in every position is a count of card backs or bookkeeping, good to about one card.

**Deck 03, the five Wailord games (`competitive_sol`): three of the five are rebuilt from text, every one of his turns.** Their reviews name the opening hand and every drawn card, so no stills were needed.

| recording stem | result, order | his turns rebuilt (game turn numbers, all from text) |
|---|---|---|
| `20261002_020315000` | lost 1-3, went second | 2, 4, 6, 8, 10 (all five) |
| `20261002_020920000` | won by concession 0-0, went second | 2, 4, 6, 8 (all four) |
| `20261002_023418000` | won by concession 0-1, went first | 1, 3, 5, 7, 9, 11 (all six) |

**Not rebuilt, need Codex:** `20261002_021402000` (went first; Wailmer Active, no Bench) and `20261002_022135000` (lost 1-3 after 30 turns, went first, so 15 of his turns). Their reviews name no opening hand and only some of the draws, so no hand could be fixed from the text. Also not built: the one choice he made during the opponent's turn in `023418` (the opponent's Sabrina on game turn 6 forced a switch and he picked the unenergised Wailmer over the Indeedee ex; a mid-opponent-turn position, which the harness does not do yet). The **opponent's hand size** in the three rebuilt games is bookkeeping, not counted.

## 2. Order to re-review, most valuable first

1. **Draft A's uncertain turns** (cheap, five items): `132311` turns 5 and 11, `115323` turn 13, `143837` turns 5 and 7. Name the hand from the frames as the fields below ask. Nothing else in draft A needs redoing.
2. **Deck 03**, his first six turns of `021402`, then of `022135` (the only two deck 03 games not rebuilt). Nothing else in deck 03 needs redoing.
3. **Ladder Log games, by variety of deck** (the pre-season games are the varied ones; the season games are mostly one Entei ex deck):
   - the eight pre-season games, eight different decks: `20260907_232617000` (Eevee / Jolteon ex), `20260908_012720000` (Ogerpon / Whimsicott), `20260908_021327000` (Hypno / Raticate ex), `20260908_022627000` (Comfey / Raticate / Hypno), `20260908_190031000` and `20260908_190933000` (Mega Altaria / Darkrai), `20260909_023151000` (Mega Manectric / Heliolisk), `20260909_032418000` (Rotom ex / Gholdengo);
   - then `20260928_200654000` (Galarian Zigzagoon / Obstagoon) and two of the ten Sept 29 Entei ex games (for example `20260929_002539000` and `20260929_020916000`).
4. **Auto-mode recordings** (all 26 are the game's Auto playing against the computer): one game per deck first, for example `20260930_141742000` (Mega Blaziken), `20260930_142105000` (Ninetales / Raticate, probably deck 13), `20260930_142731000` (Heliolisk), `20260930_143122000` (Passimian / Croagunk), `20260930_143535000` (Dialga ex / Revavroom), `20260930_144608000` (Hitmonchan / Rhydon), `20260930_153142000` (Cubone / Marowak), `20260930_155635000` (Mudkip / Mega Swampert), `20260930_161055000` (Alolan Geodude line / Mega Manectric), `20260930_162102000` (Mega Lucario / Gabite), `20261001_015649000` (Mienfoo / Mienshao), `20261001_020413000` (Guzzlord / Crobat), `20261001_021304000` (Eevee / Gastly), `20261001_022015000` (Mew ex / Gengar / Mega Diancie), `20261001_022632000` (Duskull), `20261001_024209000` (Victini / Pansear / Charmander).

## 3. The fields to add for each game (a template)

Write one table per game, one row per turn (both players' turns), plus the setup. The same wording each time so a script can read it.

| field | what to write | why it matters |
|---|---|---|
| mode flag | `Dustin's own play` or `AUTO: the game's Auto made the decisions` (for every Auto-mode recording, and say where on screen the Auto label shows) | the Auto games are a separate set; its decisions are the autopilot's, not his |
| who went first; the deck | first player; the deck as named on the Pause Games log | seats the position; the unseen cards are the list minus what was seen |
| opening hand | all five cards, before he places his Active, including the one he places | the start of every later hand |
| hand at the start of each of his turns | every card, left to right, after the draw and before he plays anything; mark any card that is only probable | the one thing the earlier reviews did not record |
| every card drawn, by name | the turn draw; **both cards of Professor's Research**; **the Pokémon Poké Ball finds**; every card Copycat draws; any other search | keeps the hand exact between turns |
| his plays in exact order | numbered; target and result of each (Energy goes to which Pokémon; Misty's coin results and target; Ice Pop flips; retreats and the Energy paid; evolutions and onto what; Tools and onto what; the attack and its target, including where Turbo Shark's Energy went); and what he did not do when a warning appeared | the first action and the order are what is compared with the bots |
| board before and after his turn, both sides | each Pokémon: name, HP now and maximum, Energy by type, Tool, damage, Special Condition; the Stadium; effects in force (Item lock, Energy-Zone block, a delayed-damage mark, Barry, and so on) | builds the position |
| points and the turn number | after each turn | the position's score and the game turn |
| the opponent's hand size | counted from the card backs at the start of each of his turns | Copycat and similar cards depend on it |
| both discard piles | the visible cards, every few turns, and after any discard or knockout | the unseen cards |
| the game's result | and, if it was an Auto game, whether the Auto bot lost or won | later comparisons |

## 4. What NOT to redo

- **Do not re-review the ten pause games' outcomes, boards, points, or the plays already in their reviews.** Only add the fields above where section 1 says a hand is missing or probable.
- **Do not redo the five draft A games** except the five uncertain turns in section 2. Their other turns have rebuilt hands, all checked against the stills.
- **Do not redo deck 03 games `020315`, `020920` and `023418`**: every one of his turns there is rebuilt from the text.
- **Do not redo the 16 rule-test recordings** (`*_rule_sol`), the Carefree Steps and Heavy Helmet tests, or the older clip reviews: they are about card rules, not his choices.
- **Do not re-extract frames for a turn that section 1 lists as text or checked.**
- **Do not redo the review of a game just to correct the result or the card identities**: the accepted reviews stand. This request is only for the added fields.

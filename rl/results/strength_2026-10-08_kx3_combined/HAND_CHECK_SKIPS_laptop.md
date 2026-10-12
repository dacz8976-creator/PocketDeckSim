# Hand check of the skip turns: were they mistakes? (the laptop, Oct 12)

**Method.** A reader panel judged each skip turn from `skip_exact/skip_boards.jsonl`. That is the board at every decision, with the
engine's damage forecasts. Card text came from `lib/card.py` and rules from `RULES_FOR_AGENTS.md`. Two independent readers judged
each turn, and a synthesis compared their verdicts. Each turn got one of three verdicts:
- MISTAKE: attacking was clearly better.
- DEFENSIBLE: skipping was as good or better.
- UNCLEAR: the board doesn't settle it.

29 turns were judged:
- each bot's 8 pre-registered skip turns, where km3 proposed an attack and none was made that turn;
- the 13 turns in `REVIEW_SKIP_EXACT_laptop.md` where the candidate skipped from the same position at which the frozen kx3 attacked.

The readers agree on 26 of the 29. The four turns judged by two separate pairs got the same verdict from all four readers. The full
records are in `skip_exact/hand_check_panel_output.json`.

## The pre-registered skips: mostly real mistakes, the same for both bots

| bot | skip turns (of about 1,900 km3 attack proposals) | MISTAKE | DEFENSIBLE |
|---|---:|---:|---:|
| candidate (`_tools _zs3 _m64`) | 8 | 6 (4 large, 2 small) | 2 |
| frozen kx3 | 8 | 6 (5 agreed, 1 leaning) | 2 |

Both bots make the same two kinds of mistake:
1. **They end the turn with an attack still legal that costs nothing,** after setup moves:
   - Stoutland's Sharp Fang into a Baxcalibur that couldn't hit back;
   - Heliolisk's Electrispark, which would have put Butterfree in KO range next turn;
   - Giga Turbo, when EndTurn was the only other move;
   - a sure KO the bot had set up itself.
2. **They retreat or set up instead of taking a sure knockout:**
   - Wailord ex retreated and threw away all 4 Water instead of a certain KO on Castform;
   - Heatmor retreated instead of KO'ing a benched Deino with Tongue Whip, and was lost anyway;
   - an 80-HP Heliolisk was put in front of a sure 90-damage KO.

The defensible ones protected a key Pokémon. Evolving the lone Natu out of a possible Crystal Waltz KO is one, and so is not taking
Rocky Helmet recoil on the future Ninetales ex.

**They are rare:** 8 turns per bot out of about 1,900 km3 attack proposals (0.4%). And the candidate's skip bar `_zs3` does not reduce
them: 8 against 8, with the same kinds of mistake.

## The 13 identical-position turns

There are 9 mistakes, 2 defensible turns and 2 unclear ones (8 mistakes, 1 defensible and 2 unclear by agreement alone).
- Most are small free damage passed up after setup moves.
- A few throw resources away: 4 Energy, an unattached Energy that cost a KO, and a retreat that gave up a sure KO.
- In 5 of the 13, "the frozen kx3 attacked here" overstates things. Its attack came from a different order of plays, was a different
  attack, did nothing, or came from a different board.

## Limits the readers found in the records

- The attack forecasts read only the opponent's Active, so Bench-hitting attacks show 0.
- The opponent-threat forecasts ignore missing Energy, and take the first option of any optional choice. For example, Chase Order
  shows 70 where it can do 140.

## What it suggests (not tested)

A rule of the form "never end the turn while a legal attack costs nothing and the attacker isn't needed elsewhere" would remove most of
these mistakes in both bots. It would be a candidate for the next pilot round, with its own gate. The forecasts' two limits above are
worth fixing before any reading leans on them.

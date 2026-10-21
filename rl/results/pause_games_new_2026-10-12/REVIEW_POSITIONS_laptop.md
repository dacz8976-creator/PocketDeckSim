# The laptop's review of the 121 pause-game positions (Oct 12): not ready for bot runs

A reader panel (Oct 12) checked the 121 positions of `positions_all.json` (main b0805130) against Codex's ledgers before both kx3
versions spend sandbox hours on them.
- Three readers, one per batch: BATCH_2026-10-06, -09 and -11 in `Battle Logs/Recording_QA/`. They compared 30 positions field by
  field with TURN_LEDGER.json and DECK_USED.json, and scripted checks over all 121.
- One reader reviewed `harness/ledger_to_positions.py`.
- Each reader's most serious finding was re-derived by an adversarial verifier, and all four were confirmed.

**Result: about half the positions hold a wrong card of Dustin's, so they can't be used as they are.** Sonnet's km3 read
(`PAUSE_GAMES_NEW_READ_sonnet.md`) is affected in the same positions. Points, turn count, hand counts, HP, attached Energy by type,
Tools, the Stadium and its owner matched the ledgers wherever they were checked. The errors are in which card a name stands for, and in
some plans.

## Blockers (fix before any bot run)

1. **His own cards: one printing per name, and the first printing in the database.** This affects 66 positions in 11 games (213625,
   003547, 031138, 032023, 032857, 033529, 034953, 012927, 020518, 012303, 013009); 38 of them have a wrong card in hand or on the board.
   - `ledger_to_positions.py` lines 296-299 keep one printing per name, merging two different cards: the Guts Conkeldurr A3 096 with
     the Bedrock Breaker B4 089, and two Aegislash, Honedge, Doublade and Meowth.
   - `_card_entries` reads only a `variant` string, so DECK_USED's `printing_aliases`, variant lists and entity-only entries fall back
     to the first printing.
   - The ledger-id override (lines 301-314) trusts Codex's set ids, which are swapped in 034953 (Aegislash and Doublade).
   - Examples:
     - 213625: the Caterpie line became A1 instead of B3b, so his Sunny Wind became an unpayable Gust (t03, t05, t07, t09).
     - 012303 t11: his winning Bedrock Breaker (100 + 20 Arena against Mega Absol ex's 110) became Mega Punch, with no knockout.
     - 031138, 012927 and 020518: the flagged rules-switch-2 cards (Togekiss A4 080, Meowth B2 124, Guts Conkeldurr A3 096) are not
       in the positions at all.
2. **Game 020518 (a Fighting deck) was converted with Water Energy.** DECK_USED stores the Energy as a list the parser doesn't read.
   All 8 positions use the deck file, and 5 have Water as energy_next.

## Major

- **Opponent printings:** the tie-break works only when Codex's text starts with an attack title. 19 positions are confirmed wrong:
  - Oricorio B3 068 instead of B4 078 (003547, 7 positions);
  - Revavroom A2b 056 instead of the Metal Transport B2b 050 (013009, 6);
  - Feebas A4a 021 instead of B3b 014 (014541, 3);
  - Charmeleon B1a 012 instead of B2b 008 (124532, 2);
  - Dragonair B2b 052 instead of B4 117 (003458 t05).
  - 20 more are undecidable from the ledger and stated as fact.
- **Effects from the opponent's last turn are always dropped** (`turn_effects` is always empty): Brass Rock -20, Mach Stealth and
  Pile-Driving Hammer, in 8 positions.
- **Plan steps:**
  - a cancelled Wally recorded as his first move (013009 t11);
  - Boiler Smog dropped when the ledger logs it as a prompt answer (015452 t03, 020258 t04, 020908 t04, 004435 t04);
  - Wally and Turbo Shark's extra Energy targets not named, so those turns can never match a bot's plan (4 positions);
  - a Poké Ball that found nothing kept as the first move (2).
- **014541 used a deck list** that DECK_USED says is the wrong version (4 positions).
- **The rules switch 2 flags** are by name, not printing, and some are hard-coded: 16 of the 21 flagged positions in the Oct 6 batch
  hold no card the switch changed.

## Minor

- Empty plans where he only ended the turn (3).
- Plans cut short by converter limits (4).
- Between-turn tracking: a false knockout and a lost Stadium (213625 t09, t11).
- Evolution stacks after Rare Candy, and the swapped stacks in the two-Kingdra game.
- A crash that dropped 020518's turn 13.
- Lucky Ice Pop's "returns to hand" wording.
- Mega Blaster's milled cards missing from 004435 t10's discard.
- Pokémon under some opponent evolutions taken from the printed line.

## What next

- Sonnet fixes the converter (blockers 1 and 2 and the majors). Then it regenerates the deck files, `positions_all.json` and
  `position_list.tsv` (the switch-2 flags by printing), and re-audits a sample against the ledgers.
- Then comes the kx3 position spec (`../pause_positions_kx3_2026-10/SPEC.md`), whose km3 column (K, on the new engine) replaces
  this folder's km3 tables.
- The km3 read here stands only for positions with no affected card. This review's per-position lists are in the laptop's workflow
  output: positions are named above, and the full evidence is with each reader.

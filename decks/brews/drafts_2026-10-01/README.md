# Brew drafts for the ladder's return (Oct 1, 2026)

**Not run. Not a ranking.** Four draft lists with their reasoning. No game was played for any of them: the only program run was
the floor's coverage check (`goldfish --games 0 --coverage`), which plays nothing. Nothing here says a deck is good. The ladder is
the only score of a brew (START_HERE, PROJECT_INSTRUCTIONS).

**Who and why.** Written by the Sonnet session "Opus agents progress" (Claude Sonnet 5.5) for the Fable coordinator session
("Work delegation and task routing"), who relayed Astra's Oct 1 review of Dustin's ladder play (7-1 against homebrew, 5-10 against
the panel decks; his notes say consistency and tempo). The job was a shortlist of three to five brews for when ranked returns
(about mid-October). The coordinator picks what goes to the floor, and only after the rules switch's sitting 2 is done. This folder
is a new one on the local branch `sonnet/brew-drafts`: no frozen input was touched (`run_screen.py`, `brew-06*`,
`research/{altaria,blaziken}`, `screen/opponents/`, the switch folder) and nothing is integrated.

## The drafts

| File | Idea | Type | Aimed at | Pokémon ex in the list |
|---|---|---|---|---|
| [`draft-A-shark-tempo`](draft-A-shark-tempo.md) | Mega Sharpedo ex hits for one Water energy and arms the Bench each turn; Ninetales ex denies their energy | Water | the Fire decks (Blaziken, Charizard Y / Entei): 0-5 on the ladder | 4 |
| [`draft-B-tide-heal`](draft-B-tide-heal.md) | No ex at all: Starmie and Milotic hit for 60 and the deck heals every turn | Water | the Lucario list | 0 |
| [`draft-C-meowstic-hatterene-v2`](draft-C-meowstic-hatterene-v2.md) | His own confusion lock (05b) with the fixes his notes asked for | Psychic | Lucario (58% in the cousin's sim page); Suicune's Basics (a confused Hatterene's 140 equals their HP); Sceptile's poison and Blaziken's burn (Comfey) | 0 |
| [`draft-D-entei-grimhound`](draft-D-entei-grimhound.md) | Entei ex tempo plus Mega Houndoom ex's three coins with Victory Star | Fire | the Grass decks (Sceptile, Vespiquen) | 4 |

Each `.md` holds the list with every card's text, the plan by turn, the interactions and whether the engine supports them, what
the bot may get wrong in a test, and one line on the panel decks. The `.txt` beside it is the list in the repository's deck format
(`lib/deck_check.py files` says clean: 20 cards, at most 2 per name, a Basic, every id matches its name). Card text comes from
`lib/deckgym-database.json`, which holds no B4b card, so none of these lists has one.

## What the lists are built on

**The Lucario list is built against Pokémon ex.** `decks/screen/opponents/t-lucario.txt` runs Arena of Antiquity (+20 from each
Fighting attacker against an Active ex), Korrina (+30 against an Active ex), Lucario's Fighting Coach (+20 from every Fighting
attacker) and Riolu's Fighting Fist (+30 against an ex). Mega Lucario ex's Fighting Pulse is 90, or 140 with one extra Fighting
energy. Against a non-ex Active that is up to 160; against an ex Active up to 210 before Weakness. `trainer_pricing_2026-09-28`
counts Arena in 391 of 398 real Lucario lists. Dustin is 0-6 against the Mega Lucario decks mapped in the Sept 28 log
(`ladder_counts.md`). His record does not show the ex effect cleanly: three of the six games were with ex-based decks (brew 01,
brew 08, deck 07) and three with non-ex ones (brew 05, and brew 06 twice, whose notes blame tempo: Dugtrio and Hitmonchan ex took
its Pokémon for points before Silvally had its energy). A non-ex deck also gives away one point a Knock Out instead of two
(three for a Mega), so the opponent needs three Knock Outs. Draft B is built for that; draft C is already non-ex.

**What the floor said about close cousins** (km3 on both sides, 240 games per cell, plus or minus 6; not a ranking; from
`rl/results/floor_dustin_2026-09-30/` and `floor_recheck_2026-09-30/`):

| cousin | overall | Lucario | Suicune | Sceptile | Blaziken |
|---|---|---|---|---|---|
| deck 13 Alolan Ninetales / Raticate (draft A shares Ninetales ex) | 56% | 60% | 68% | 52% | 72% |
| deck 03 Wailord / Indeedee wall (draft B shares the heal-and-wall plan) | 61% | 53% | 61% | 62% | 67% |
| brew 05b Meowstic / Hatterene / Comfey (draft C is its edit) | 30% | 58% | 22% | 22% | 39% |
| brew 08 Entei / Rainbow Cave (draft D shares Entei ex and the Cave) | 56% | 54% | 43% | 65% | 36% |

The cousins' numbers say what the shell can do against the bot's panel, not what the new list will do.

**Dustin's ladder record** is in the Ladder Log (collection `logs`, 17 documents, read Oct 1). Brew 05 (the original of 05b) is 3-3 and
05c 1-2. His notes in those games, which draft C answers: Comfey as the only Basic and the first to die; Hatenna dying before
Rare Candy; no Cyrus in 05c; no way to heal against Hitmontop and Rocky Helmet; Peculiar Plaza held back out of fear of Field Blower.
Brew 08 (Entei) is 7-3, six of the seven wins by opponent concession; its losses were to Dragonite, Mega Diancie / Gardevoir and Mega Lucario.

**One thing outside the drafts.** Several lists clear the floor with room and have no ladder games at all in the log: deck 03
(61%), deck 06 (58%), deck 09 (58%), deck 13 (56%), brew 07 (61%). Playing those as they are costs nothing and gives the ladder
something to say about the floor.

## Things every test of these lists has to keep in mind

- **The bot searches three plies.** Anything that pays off in the opponent's turn is not seen: Binding Snow (A) is flagged for
  that. The coverage check flagged one card each in A, C and D and none in B; each draft says which and why.
- **Hatterene's 140 is priced at its printed 70** (flag: `ExtraDamageIfDefenderStatus estimated at printed damage`). A floor page
  for draft C probably understates the deck.
- **Floor roles.** A flagged card's role is the default unless set, and a "fail", "borderline" or "untrusted" verdict on a default
  role is marked provisional. Draft D's Victini would default to "attacker"; its job is the passive Ability, and setting that role is
  Dustin's call on the page.
- **Victory Star (D) is the one card with a named engine caveat** (`card_validation.rs`: confusion and attacker-side coin gates
  bypass the reroll prompt). The Victory Star / Confusion repair is in the rules switch's candidate, not in the official engine yet,
  so run D's floor page after the pin, not before.
- **The sim favours the player who goes second** (for example brew 07: 55% going first, 67% going second). Compare lists on the same
  seats and seeds.
- **Promo availability depends on when Dustin joined.** Promo cards are time-limited. He joined after P-A 014, so he does not have
  Lapras ex (its only printing); draft A's first version ran it and now runs the plain Lapras A3 044 instead. **Any P-A promo
  predates him; P-B promos may or may not**: he does own Mega Houndoom ex (P-B 080, draft D; the coordinator confirmed it). This
  matters only for a card whose *only* printing is a promo. The Poké Ball (P-A 005) and Professor's Research (P-A 007) that every
  list uses are the database's names for cards that also exist as A2b 111 and A4b 373, and they are in his own decks. Beyond that,
  ownership of the other cards is not checked. A check of every card's printings in `lib/deckgym-database.json` (Oct 1) found Lapras
  ex and Mega Houndoom ex to be the only cards in the four lists whose printings are all promos.

## Considered and not drafted

- **Gengar ex lock** (Spellbind: no Supporters while it is Active; Flutter Mane ex: no Trainers for a turn). Locks Supporters and
  Items, not attacks, and Gengar ex is a Stage 2 with Darkness weakness. Lucario still hits.
- **Mega Gardevoir ex ramp** (110 and three Psychic energy). Hits Lucario's Psychic Weakness, but Weezing and Hydreigon hit it back
  and it needs a Stage 2 online by turn 2 to keep up.
- **Mega Blastoise ex with Misty and Irida.** A real beater, but a Stage 2 with a Lightning Weakness and ex-heavy against Lucario;
  draft A covers the Water plan with fewer moving parts.
- **A Sableye Thorns edit of brew 07.** Brew 07 already clears with 60.8% and its holes are the two Grass decks; the edits I found
  (Rocky Helmet, a second Mega Sableye ex) are small enough that playing 07 first tells more.

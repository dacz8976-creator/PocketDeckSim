# Exam inventory: Dustin's ladder turns (from Codex's video reviews)

Source: 38 REVIEW.md files (not 39; BATCH_2026-10-14_LADDER_RESUME_FIVE has only `_batch` and no game folders). Files: `inventory.json` (per game, per turn), `data.txt` (my raw coding), `build.py` (counts).
Read: every REVIEW.md in full, plus SUMMARY / LADDER_ENTRY / QR_DECODE / UNCERTAINTIES metadata. No images, no bot output, no pause_games or next_pilot files.

## Scope
- 38 games read. 2 are excluded: `20261002_011527` and `20261002_012229` are computer battles (opponent AI, Auto control visible; one had Auto ON mid-game). The reviews themselves say they are not ladder games. Their turns were not coded.
- 36 games counted, 178 of his turns. Of those, 2 clips (`20260926_211809`, `20260926_212155`, 5 turns) start mid-game and the reviews say ranked PvP is not proven. They contribute 2 usable turns; every count below includes them unless stated.
- Decks: Deck 12 Ariados/Whimsicott/Ogerpon (10 games), Deck 13-A Alolan Ninetales/Raticate (14 games, no QR file), Kingambit (10 games, all with QR_DECODE.json, one identical payload `C5iWnpiWnpiYYJiapJiapJiaIpiW...` = Poke Ball x2, Rare Candy, Lucky Ice Pop x2, Heavy Helmet, Research x2, Ilima, Copycat, Mesagoza, Alolan Grimer, Alolan Muk, Glimmet x2, Glimmora x2, Pawniard, Kingambit, Regigigas; screen label "New deck 16"), plus the 2 older mid-game clips.
- Pocket has no Energy cards in the deck, so a hand is just the cards named; that is why hands are derivable at all.

## Counts (36 games, 178 turns)
| | turns | usable | near-usable (hand partly, <=2 unknown) |
|---|---:|---:|---:|
| Total | 178 | **91** (89 without the 2 mode-unknown clips) | **19** |
| Deck 12 Ariados/Whimsicott | 49 | 26 | 3 |
| Deck 13-A Ninetales/Raticate | 58 | 36 | 4 |
| Kingambit (QR list) | 66 | **27** | 12 |
| Older mid-game clips | 5 | 2 | 0 |

135 of 178 turns had a real choice. 30 of the 36 games have at least one usable turn.

Per kind (usable / near-usable):
| kind | usable | near |
|---|---:|---:|
| prepare | 54 | 10 |
| attack now | 29 | 6 |
| sacrifice | 6 | 2 |
| abandon | 0 | 1 |
| other | 2 | 0 |

Kingambit only: 27 usable (prepare 19, attack now 5, sacrifice 3) and 12 near-usable (prepare 8, attack now 3, sacrifice 1).

## Five most common reasons a turn is not usable (turns, a turn can have several)
1. No real choice: first turn with nothing to play, forced attack, lethal, asleep and unable to attack: 30
2. Hand partly known, only 1-2 cards unnamed (the near-usable pool): 24
3. Hand mostly unnamed (3+ cards), usually after Copycat/Research draws or an opening hand the review never lists: 22
4. Board partly known: opponent Tool title unreadable, or the review says per-turn Energy counts are not relied on: 15
5. Real choice unclear: concession turns, single-line turns, "why didn't he attack" with no stated alternative: 13
(Next: move incomplete, opponent conceded before he acted or the clip ended: 6.)

## Are there 40 usable decision points?
By the letter of the test, yes: 91 usable turns (89 from certain ladder games), plus 19 near-usable, across 30 games. I would not trust that number at face value. (1) Everything comes from Codex's primary-pass video accounts, which say independent and lead acceptance are pending, so hands and boards are only as good as those accounts. I counted a hand as known when the opening five were listed and each later draw/search was named or forced by what was later played; I allowed a few Copycat refills that the review only half-named. (2) "Real choice" is generous: 54 of the usable turns are ordinary "prepare" turns where a different Energy or bench placement was possible but nothing in the review says it was close. A stricter cut, keeping only usable turns that are a sacrifice, an unusual line, or where the review shows something declined, held back, retreated or dumped (e.g. skipped Hang Down, Copycat discarding Pawniard, Ilima resetting Regigigas, Sabrina targets), gives about 37, 11 of them Kingambit. (3) Turns inside one game are not independent, and the Kingambit deck alone gives 27 usable (39 with near-usable), so a Kingambit-only exam of 40 is not available without accepting near-usable turns. The honest answer: about 40 defensible points across all decks, only about 27 for Kingambit, and the exam needs a human check of each hand ledger before any turn is used.

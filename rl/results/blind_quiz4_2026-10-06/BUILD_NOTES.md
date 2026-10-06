# Blind quiz 4 ("Your Move, Blind 4") build notes (Oct 6, 2026)

`positions/Q01.json` ... `Q12.json` are what the page shows. Nothing private is in this folder: the key (which plan is whose, both games' results, the full plans) is kept outside the repository, in `/home/dacz8976/quiz4_private/`, until Dustin has answered.

The 12 positions are the laptop's selection, in its order. Each is the first decision at which the two pilots chose differently on the same deal. No game was played for this build: every position was rebuilt by replaying the harness job with the official engine program (`rl/engine-2026-10-02/deckgym`, sha256 `2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e`, equal to its `SHA256SUMS`).

## What a position document holds

Quiz 3's fields (`order, matchup, turn, you_went_first, situation, points, you, opponent, stadium, turn_effects, this_turn_so_far, log, options, cant_play`, rendered by the unchanged `describe.py`), with the page's doc id = the file name (no `id` field), plus:

| field | what |
|---|---|
| `question` | "Two plans for the rest of this turn. Each runs from here until its first step that draws or searches for cards ..., its attack, or the end of the turn. Which plan would you play: Plan A, Plan B, both reasonable, or neither?" |
| `plans` | `{"A": {steps, ends, ends_text}, "B": {...}}`. `steps` are plain sentences in order; `ends` is `attack`, `draw` or `end`; `ends_text` is a one-line reading of it. |
| `answer_options` | `["Plan A", "Plan B", "Both reasonable", "Neither"]` |
| `note_prompt` | "A short note (optional): why, or what you would do instead." |

`options` is Quiz 3's list of every legal move with its card text. It is still there as reference; a page that only asks for the plan can ignore it. The two plans' first moves are always two different options.

| Q | your deck | game turn | you went first |
|---|---|---|---|
| Q01 | deck 01 (Muk / Glimmora / Kingambit / Regigigas) | 3 | yes |
| Q02 | deck 01 | 7 | yes |
| Q03 | deck 01 | 9 | yes |
| Q04 | deck 03 (Wailord / Indeedee wall) | 3 | yes |
| Q05 | deck 03 | 6 | no |
| Q06 | deck 05 (Indeedee / Stoutland) | 4 | no |
| Q07 | deck 05 | 4 | no |
| Q08 | deck 05 | 4 | no |
| Q09 | deck 07 (Skarmory ex stall) | 9 | yes |
| Q10 | deck 09 (Mega Manectric / Heliolisk) | 3 | yes |
| Q11 | draft A (Mega Sharpedo / Alolan Ninetales) | 6 | no |
| Q12 | deck 10 (Xatu / Oricorio / TR Weezing) | 3 | yes |

## How the plans are written

Both plans go through one function, so the wording cannot show whose plan it is. It follows the board through the plan (a retreat swaps the Active, an evolve renames the spot) and says "Retreat X (Active), switching in Y (Bench 3)", "Attach Darkness Energy to Z (Bench 1)", "Evolve A (Bench 2) into B", "Use X's Ability T (Bench 3)", "Attack with T", "End your turn without attacking". A plan that ends because the game turn ends, with no attack, gets that last step too. Three readings to know:
- **Lucky Ice Pop** played twice (Q02) reads "Play Lucky Ice Pop (Item), and again each time the coin flip returns it to your hand": the second play is only the coin coming back to the hand.
- **Rare Candy** (Q08) names its target ("evolving Lillipup (Bench 3) into Stoutland"). The engine had exactly one choice there, so the plan does not say it; the build checks that exactly one Basic/Stage 2 pair fits, and stops if not.
- **A plan that stops at a draw** (`ends: draw`: Poké Ball, Copycat, Research, or using Mesagoza or Fragrant Forest) is cut there, as in Quiz 3: what comes after depends on what is drawn. `ends_text` says so.

## Checks (all passed; the build prints 0 problems)

1. **Engine:** the program's sha256 equals `SHA256SUMS`.
2. **Replay equals the harness:** for all 12 jobs the replay (same seed, same seat, the deck files named in the run's manifest, each file's sha256 equal to the manifest's) gives the harness game's winner, points, turns and number of plies, and its deck-seat decision log (18 to 49 decisions per game) equals the harness's log field by field: turn, own turn, action, number of legal moves, points, Active Pokémon, Bench size.
3. **The fork:** the other pilot's log equals it for every decision before the position and differs at it. The position's turn, own turn, Active, Bench size, points and number of legal moves equal the selection's.
4. **Both plans start legally:** each plan's first move is among the legal moves at the position and falls under exactly one option, and the two are different options. Each plan equals the harness log cut at the first draw, attack or end of the game turn (a forced end of turn is not logged, so the cut also ends where the game turn changes).
5. **Plan sense:** every plan step targets an occupied spot, an Evolve fits its Pokémon and was not put into play this turn, there is at most one Energy Zone attachment (and none if this turn's was already made), a retreat can be paid, a played card was in the hand. 17 steps of the replayed pilot's plans (every step that is followed by another step of the same plan) were compared with the real game's board after the step, forced follow-ups included: all equal.
6. **Blind rendering:** each page is rendered from the replayed game. The other pilot's game is identical up to the position (check 3, plus both pilots being deterministic given the state and seed); its own states are not saved, so the render was not repeated from it.
7. **Leak test** (Quiz 3's, adapted): the fields are exactly Quiz 3's plus the four above; `matchup` holds only your own deck; the opponent shows hand size and next Energy only; no seed, pilot, run or file name, no result or choice field; no opponent hand or opponent deck card is named (the opponent's deck name appears only inside card names already on the table); your own decklist is exact (20 cards, `left` equal to the deck); every legal move sits behind exactly one option. A scan of the staged files for pilot and run names, seeds and build hashes found nothing.
8. **Planted leaks:** 346 leaks (a seed, an opponent deck name, a pilot name in a plan step or an option, a field marking which plan is whose, a result field, an opponent hand card in the log or a plan, a changed answer option, ...) were planted across the 12 positions; all 346 were caught.
9. **describe.py's own self-test, 0 problems:** 24 seats checked against the deck lists; the Retreat Cost model agrees with the engine in 12 positions; 37 hand cards checked for playability against the engine's legal moves; every between-turn HP change in the logs explained; 60 hidden-only card names checked.
10. **describe.py is unchanged** (sha256 AE5298E1... equals quiz 3's). Everything this quiz needed beyond it is in a shim module (below).

## Shims (describe.py has no rule for these; each is worded from the card's own text)

- **Heavy Helmet** on a Pokémon (Q02): its text names Retreat Cost only as a condition for -20 damage, so describe.py's guard against unmodelled Retreat Cost Tools is told it is not a modifier.
- **Chase Order** (Vespiquen ex's attack) follow-up, "discard 1 of your Benched Basic [G] Pokémon: 70 more damage" (in Q03's log), and the engine's new continuation step after a Knockout (`ResolveKnockoutPoints`, shown as nothing, like `ResolveAttackRetaliation`).
- **Turn effects:** Clemont's Backpack (Q10): "attacks used by your Magneton or Heliolisk do +20 damage to your opponent's Pokémon"; Will (Q12): "the next time you flip any number of coins ..., the first coin flip will definitely be heads".
- **Rare Candy** (Q08): Herdier added to describe.py's Stage 1 table (Stoutland evolves from Herdier, which is in no quiz deck), so its playability agrees with the engine.
- **"Hidden" cards** are now the opponent's hand and deck only. describe.py also counted your own undrawn cards, but those are not secret (the page shows your own decklist), and in this pool they collide with a card named "Psychic" (also the Energy type) and with names printed on Clemont's Backpack.
- Deck lists for the quiz's seven decks and the six panel lists are converted copies (`N SET NNN`, the form describe.py reads), checked against a fresh conversion of the repo files. For hand cards describe.py has no playability rule for, "playable" means exactly "the engine offers a Play of that card", as in Quiz 3.

## Things to know

- **Fragrant Forest.** In Q01 and Q08 one of the two plans ends by using the Stadium Fragrant Forest ("put a random Basic Grass Pokémon from your deck into your hand"). Decks 01 and 05 have no Basic Grass Pokémon, so it brings nothing; the engine offers it anyway (the same open rules question as quiz 2's note 5 and quiz 3's notes). The plan is shown as the pilot played it.
- **Q12** shows Will's effect (the next coin flip is heads) in the turn effects, although neither plan flips a coin.
- **Held back:** the build has no page, publishes nothing and writes no database document. To use it: load `positions/Qnn.json` as documents `Qnn` of a new artifact's collection and give the page a plan A / plan B / both reasonable / neither choice with the note box.
- Not in the repository: the key and plies (`/home/dacz8976/quiz4_private/`), the build scripts and their log (`/home/dacz8976/quiz4/`, scratch copies of Quiz 3's `describe.py`).

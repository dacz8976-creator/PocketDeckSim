# Ladder Log and Auto-mode recordings: what exists (Oct 2, 2026; text on disk only, no images)

Sources read: `BATTLE_REVIEW_INDEX.csv` (129 videos: 121 Reviewed, 8 awaiting review), `READ_ME_REVIEW_STATUS.md`, `LADDER_HISTORY_PRE_2026-09-15.md`, and the `REVIEW.md` / `SUMMARY.json` of the 54 non-pause, non-rule-test folders under `Recording_QA/`. Counts are from scripts over that text; "named" means a card name appears after "draws" or in an "opening hand" sentence. I did not read the older Boss Folder reviews in full (37 index rows point there).

## How I tell Auto from Dustin's own play

- Dustin's correction (Oct 2): every Ladder Log game is his own play (Auto is not available against other humans). A ladder game has a named human opponent reached by opponent search (a profile, two clocks) and no Auto label.
- An Auto recording is marked three ways in the text: the folder suffix `_auto_sol` (26 folders, Sept 30: 15 and Oct 1: 11), `SUMMARY.json` `mode` = `autopilot_vs_computer` / `auto_vs_ai` / `solo_computer_challenge_with_auto`, and the review's own evidence lines ("Opening explicitly labels opponent AI", "Checked Auto during setup", owner testimony in SOURCE.json). The opponent is "AI" in all 26.
- The older ladder reviews say "Auto switch visible and off" or "Auto state was not independently verified" (e.g. Sept 8, Ogerpon / Whimsicott); by Dustin's rule, a recording with no clear Auto or test label is a ladder game.

## The Auto set (the "game-auto" pilot): 26 recordings, 14 different decks

All 26 are autopilot against the computer (solo or computer challenges; opponent decks such as the Deluxe-pack Inteleon and Raichu lists), recorded Sept 30 (15) and Oct 1 evening (11). The Auto bot piloted Dustin's lists: Mega Blaziken / Torchic / Castform (3), Alolan Ninetales / Raticate, Heliolisk, Passimian / Croagunk, Dialga ex / Revavroom, Hitmonchan / Rhydon / Passimian (2), Cubone / Marowak, Mudkip / Mega Swampert, an Alolan Geodude line with Mega Manectric (2), Mega Lucario / Gabite, Mienfoo / Mienshao, Guzzlord / Crobat, Eevee / Gastly, Mew ex / Gengar / Mega Diancie, Duskull, and Victini / Pansear / Charmander (5-6 games of one list, Oct 1). Results as the reviews state them: about 15 wins, 9 losses, 2 not stated in `SUMMARY.json`. Draft A is in none. One game (20260930_142105000) is an Alolan Ninetales / Team Rocket's Raticate list, probably deck 13 (the review names the core, not the 20 cards).

## The Ladder Log set (his own play against humans)

- **Pre-season, Sept 7-9: 8 games, 8 different cores**: Eevee / Jolteon ex, Teal Mask Ogerpon / Whimsicott, Hypno / Raticate ex, Comfey / Raticate / Hypno, Mega Altaria / Darkrai (2), Mega Manectric / Heliolisk, Rotom ex / Gholdengo (4 wins, 4 losses; `LADDER_HISTORY_PRE_2026-09-15.md`). Their reviews are short (about 4-5 KB for the ones I measured) with no hands.
- **Season, Sept 26-29, in `Recording_QA/`**: about 16 reviewed recordings, mostly one deck (two Entei ex with Giant Cape and Rainbow Cave: 10 games on Sept 29), one Galarian Zigzagoon / Obstagoon game (Sept 28), and several Sept 26-27 games whose summaries name no deck core (the Luckycad / Xatu series among them). Variety here is low; the pre-season games are the varied ones.

## How many turn starts have a hand rebuildable from the text alone

| set | recordings | opening hand named | named draws per game | turn table in the review | turn starts fully determined from text |
|---|---|---|---|---|---|
| Ladder Log, season (28 folders incl. test clips) | ~16 games | 4 of 25 | 0.0 (none names more than one) | 1 | **about 0**: at most the first turn of a few games |
| Ladder Log, pre-season | 8 | not named | ~0 | no | **about 0** |
| Auto | 26 | 14 of 26 | 2.8 (4 games name 5 or more) | 4 | **a handful: roughly 10-20 turn starts in ~4 games**, each needing a check against its own draws and plays |

So with text only I can build essentially no Ladder Log positions and a few Auto ones; every other turn needs a still frame or, as Dustin has arranged, the Codex agents' new transcripts (`PAUSE_GAMES_REVIEW_PROTOCOL.md`: hand at each turn start, every drawn card, plays in order, opponent hand size). For the recordings already on disk the cheapest gain is to have the Codex agents redo only the most different decks first: the eight pre-season ladder games (eight different decks), then one Auto game per deck for the 14 Auto decks.

## What a useful targeted Auto recording would be

The comparison wanted is Dustin's choice, the game Auto's, km3's, and later the prototype's, on the same kind of position. The Auto games above are on decks nobody else has played, so nothing pairs with them. A recording that does: **the game's Auto piloting draft A and deck 13 against one fixed computer opponent (the same computer deck every game), about 10 solo battles each**, recorded under the new capture protocol (hand at every turn start, every drawn card, plays in order). That gives roughly 100 Auto turn starts per deck on decks that already have Dustin's own games (draft A: the five Pause Games; deck 13 and its Raticate relatives: the ladder history) and the intended lines the harness counts (Turbo Shark arming a Bench by own turn 3; Thieving Incisors). If he can add 5 games of his own play on the same two decks against the same computer deck, the Auto games and his are comparable deal for deal.

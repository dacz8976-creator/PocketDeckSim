# Consistency harness (A1): anchors and the answer to D1

Built 2026-09-24, late evening, on branch `laptop/engine-first-2026-09-24` (`lib/consistency.py`). There is one page
per list in this folder. The table at the bottom is rewritten by `--batch`; the text above it was written by hand
from that run (10,000 solitaire deals per seat and 150 engine games per pilot per list; seeds in the table header).

## D1: does the harness separate the anchors that did well from the ones that did badly?

**Yes, on these six anchors, but only through tempo, and the anchors are too thin to prove more than that.**

- **The engine goldfish (scripted pilot) puts the six anchors in the same order as the ladder.** Points conceded
  before the list's first damaging attack: Skarmory 0.29 and Brew 1 (05b) 0.39, against brew-03a 0.71, brew-01 1.16
  and the two Payback lists 1.35 and 1.52. The chance of a damaging attack by own turn 3 is 77% and 79%, against
  35%, 37%, 15% and 14%. The main attacker's first attack comes by own turn 4 in 98% and 65% of games, against 49%,
  48%, 33% and 38%. The two lists that did not lose (3-1, 3-3) sit on one side of a clear gap (0.4 points against
  0.7 or more, about 3.5 standard errors at 150 games), the four that went 1-3 or 0-3 sit on the other, and the
  0-3 pair comes last.
- **The card-finding numbers do not separate them.** Payback gets its pieces (Pyukumuku and Silvally in play) by
  own turn 4 in 83% of deals, more often than Brew 1 (53%) or brew-01 (45%). Its Silvally is in play with CCC by
  turn 4 in 83%, more often than Brew 1's Hatterene (64%). "Main attacker online by own turn 3" separates the lists
  only by Energy cost: every list whose attacker needs three Energy scores 0% going first.
- **Why this is not yet proof:**
  1. The ladder evidence is 3 to 6 games per list. The only difference the ladder itself supports is Skarmory 3-1
     against the Payback lists 0-6 (one-sided Fisher p ≈ 0.03). The gap between 3-3 and 1-3 is noise.
  2. One design fact explains most of the order. The four losing lists attack with a three-Energy attacker
     (Arceus ex CCC, Silvally CCC). Skarmory attacks for MM, and Brew 1 for PP via Rare Candy. Counting the Energy
     on the main attack would sort these six lists the same way, so the anchors cannot show that the harness adds
     information beyond that. What it does add here is the cost of the wait: Payback gives up 1.5 points before
     its first attack, the Arceus lists 0.7 to 1.2.
  3. I looked at about ten measures and report the ones that line up. Three goldfish tempo measures agree with one
     another, which helps, but a check on six lists cannot rule out luck.
  4. Two tournament lists land in the bad band. Weezing gives up 1.05 points before its first damaging attack and
     attacks by turn 3 in 51% of games: its damage comes from Abilities and on-evolve Poison and Burn (Boiler
     Smog, Nightmare Aura), which "first damaging attack" does not count and the scripted pilot does not aim for.
     Altaria gives up 1.26 points before Mega Altaria attacks, and Mega Altaria attacks by turn 4 in 35% of games.
     A bad tempo number is a warning, not a verdict. Do not rank lists on it.
- **The pilot the brief named does not work.** Both `aa` and `er` never bench a Pokémon, not even at setup: the engine
  sorts End Turn first among the legal moves, and both bots fall back to the first move. So `aa` against `aa` is a
  one-Pokémon duel that ends at the first knockout, and `et` never attacks. Every page still has the `aa` row, as
  asked, and it does not separate the anchors (Brew 1: damaging attack by turn 3 in 100% of games; Skarmory: 67%).
  The readings above come from a scripted pilot (the solitaire model's priorities) playing the real rules4 engine
  through the pdl_rl_env 0.7.2 add-on. Its opponent is the same `aa` bot, which is a single Active Pokémon, so
  the clock is fixed and slow.
- **The k3 screen agrees where both exist**: Skarmory 57%, Brew 1 28%, Payback 8% and 16% (Lab `screen/results.md`).

## Do the failure modes match the ladder notes?

| Ladder note (Ladder Log) | What the harness says |
|---|---|
| Payback: "Hitmonchan ex and Great Tusk took both Pyukumukus for 2 points before Silvally had 3 energy"; lesson 8 | **Reproduced, and the worst of all 18 lists.** Payback gives up 1.5 to 1.6 points before Silvally's first attack. Going first, Silvally attacks by own turn 4 in 8% of games (06) and 13% (06b), although the solitaire model has it in play with CCC by turn 4 in 83% of deals. The gap is the wall in front: it has no Energy to retreat (the pilot puts every Energy on Silvally), so Silvally waits until the wall is knocked out. |
| Payback: "Opened with only TR Mewtwo" | 12% of openings (exact). |
| Payback: "Never drew Rocky Helmet" | The single Helmet is drawn or fetched by own turn 3 in 63% of games (61% in 06b). Missing it is a one-in-three event: expected, not bad luck. |
| brew-01: "Never drew crobat, or xatu… Probably need more draw cards"; "Arceus ex takes 3 energy… too difficult to draw cards you need" | **Matches.** Crobat is in play by own turn 3 in 51% of deals and Xatu in 70%. All three pieces are in play by turn 4 in 45%, the lowest of the anchors (Skarmory 96%). Arceus ex is online by own turn 3 going first in 0% of deals. Going first, the list lands a damaging attack by own turn 3 in 10% of games and gives up 1.64 points first. |
| Brew 1 (05b): "comfey the only basic to start" | 13% of openings (exact). The list opens with a single Basic 63% of the time. |
| Brew 1: "I don't have the second meowstic or hatterene" | Hatterene is in play by own turn 3 in 51% of deals and by turn 5 in 74-76%. Without Rare Candy it is 0%, because the list has no Hattrem. Rare Candy and Hatterene are the cards most often stuck in hand at the end of a turn (44% and 38% of turn-ends). |
| brew-03a: "Teal mask ogerpon prevented poison" | This is a matchup fact. The harness has no opponent that cures conditions, so it cannot test this. |
| Skarmory 3-1 (no loss notes) | Best on every tempo number. Skarmory ex attacks by own turn 4 in 98% of games, with 0.29 points given up first. Its dead cards are extra Supporters (Red in 38% of turn-ends). |

## The new brews (07-10), unplayed

All four sit in the good band on tempo, next to Skarmory and the tournament lists. None has Payback's tempo hole.
The harness says nothing about matchups.

- **08 Entei (Rainbow Cave + Flame Patch)** is the fastest of all 18 lists. Its only Basics are the two Entei ex, so an
  Entei always starts; a damaging attack comes by own turn 3 in 100% of games, with nothing given up first. The
  three pieces are together by turn 4 in 84% of deals.
- **07 Hoopa / Darkrai / Sableye**: 0.44 points given up before the first damaging attack; 71% attack by turn 3. Hoopa
  ex needs DDC, so it is 0% online by turn 3 going first.
- **09 Sableye / Obstagoon**: Mega Sableye ex is online by turn 3 in 92% of deals. Obstagoon is the slow half (Rare
  Candy only, no Linoone), so the combo is together by turn 4 in 63%.
- **10 Diancie / Giratina**: 0.45 points given up first. A damaging attack by turn 3 comes in only 42% of games,
  but Diancie attacks by turn 4 in 81%, and the combo is together by turn 4 in 90%.

## Tournament lists, for scale

Across the eight panel lists: main attacker online by own turn 3 in 41-88% of deals (Stage 1 and Stage 2 Megas:
41-73%), 0.15-1.05 points given up before the first damaging attack, and combo by turn 4 in 27-82% (Lucario's
Mega Lucario ex plus Lucario is 27%). Consistency alone does not make these lists good. Most of them are merely
"not slow".

## Coverage flag, in short

15 of the 18 lists carry an (a) card, almost always Copycat. Hydreigon adds Mega Absol ex's Darkness Claw, Weezing
adds Mars and Suicune adds Team Rocket's Boss; blind k3 leaves these unpriced. Sceptile's Caterpie is also flagged,
because its automatic Quick Growth leaves the opposing bot's end of turn unpriced. (b), an attack whose extra damage
the bots never see, hits several main attackers:
- Silvally's Gold Breaker is read as 60 against an ex (150 on the card).
- Hatterene's Mental Crush is read as 70 against a Confused Pokémon (140 on the card).
- Also hit: Galarian Obstagoon, Team Rocket's Scyther, Vespiquen ex, Riolu, Xatu's Life Drain, Toxapex's Severe
  Poison and Mareanie's Venoshock.

So k3's position score (not the damage actually dealt in its searches) undervalues the main attackers of the Payback
lists and Brew 1, on top of whatever else it gets wrong. Every evolution
and every Trainer that changes the next exchange is invisible to the reply-search tiers (c). The per-card lists are
on each page.

## Limits

- Solitaire model: no opponent, no knockouts, no retreat. Setup by attack (Carbink's Glittering Gift, Tandemaus's
  Flock) is ignored, and Copycat assumes the opponent holds 4 cards.
- Scripted pilot: simple priorities. It never plays gusts, offensive Supporters (Red, Cyrus, Sabrina), Team
  Rocket's Master Plan or Will.
- The goldfish opponent is one Active Pokémon that never benches or plays a Trainer. Its clock is slow, and it can
  lose to retaliation alone (Payback beats its Hoopa ex with Innards Out, Rocky Helmet and Dynamite Punch's
  self-damage), so the "won" column means little.
- An engine behaviour I saw but did not check against the game: the engine let Giratina ex's Ability attach an
  Energy on the first player's own turn 1. The solitaire model does not allow that.

## How to run

In WSL, from the repo root:

    python3 lib/consistency.py decks/brews/<brew>.txt --main "<card>" --combo "<a>,<b>|<c>"   # about 35 s
    python3 lib/consistency.py --batch decks/consistency_2026-09-25/lists.tsv               # all 18, about 10 min
    python3 lib/consistency.py <deck> --goldfish 0                                           # no engine; any Python 3

Without `--main` or `--combo`, the harness infers them from the list (the page says so).

<!-- table:start (rewritten by lib/consistency.py --batch) -->
Run: 10,000 solitaire deals per seat, 150 engine games per pilot per list, seeds from 21,002,000,000 (list i: solitaire and scripted-pilot seeds 21,002,000,000 + 10,000·i, aa-pilot seeds that +5,000), opponent `decks/research/weezing.txt` piloted by aa. sp = scripted pilot on the real engine; aa = the engine's attach-and-attack bot as pilot.

| List | Role | Ladder | k3 screen | 1-Basic open | Main online by T3 (1st / 2nd) | by T4 (1st / 2nd) | Combo by T4 (1st / 2nd) | sp: damaging attack by T3 | sp: pts conceded before it | sp: main attacks by T4 | sp: pts conceded before main | sp: dead cards/turn | aa: damaging attack by T3 | (a) cards |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 07-skarmory-stall (main Skarmory ex) | anchor: did well | 3-1 | 57% | 86% | 95% / 95% | 97% / 97% | 96% / 96% | 77% | 0.29 | 98% | 0.29 | 1.4 | 67% | 0 |
| brew-05b-meowstic-hatterene-comfey (main Hatterene) | anchor: middle | 3-3 | 28% | 63% | 51% / 50% | 64% / 63% | 53% / 52% | 79% | 0.39 | 65% | 1.10 | 2.5 | 100% | 1 |
| brew-01-arceus-crobat-xatu (main Arceus ex) | anchor: did badly | 1-3 | - | 52% | 0% / 74% | 84% / 84% | 45% / 45% | 37% | 1.16 | 48% | 1.47 | 2.3 | 77% | 0 |
| brew-03a-arceus-nihilego-toxapex (main Arceus ex) | anchor: did badly | 1-3 | - | 52% | 0% / 75% | 82% / 83% | 66% / 65% | 35% | 0.71 | 49% | 0.78 | 0.7 | 66% | 0 |
| brew-06-pyukumuku-silvally-payback (main Silvally) | anchor: did badly | 0-3 | 8% | 41% | 0% / 72% | 83% / 83% | 83% / 84% | 15% | 1.35 | 33% | 1.51 | 2.8 | 48% | 1 |
| brew-06b-pyukumuku-silvally-scyther-grass (main Silvally) | anchor: did badly | 0-3 | 16% | 41% | 0% / 72% | 83% / 83% | 84% / 83% | 14% | 1.52 | 38% | 1.61 | 2.4 | 51% | 1 |
| brew-07-hoopa-darkrai-sableye (main Hoopa ex) | new brew (unplayed) | - | 62% | 75% | 0% / 85% | 91% / 91% | 78% / 78% | 71% | 0.44 | 73% | 0.39 | 0.9 | 80% | 1 |
| brew-08-entei-rainbow-cave (main Entei ex) | new brew (unplayed) | - | 56% | 95% | 100% / 100% | 100% / 100% | 84% / 85% | 100% | 0.00 | 100% | 0.00 | 2.3 | 100% | 1 |
| brew-09-sableye-obstagoon (main Mega Sableye ex) | new brew (unplayed) | - | 47% | 75% | 92% / 92% | 95% / 96% | 63% / 63% | 59% | 0.29 | 67% | 0.43 | 2.0 | 100% | 1 |
| brew-10-diancie-giratina (main Mega Diancie ex) | new brew (unplayed) | - | 45% | 52% | 0% / 78% | 87% / 87% | 90% / 89% | 42% | 0.45 | 81% | 0.52 | 2.5 | 9% | 1 |
| research-lucario (main Mega Lucario ex) | meta reference | Limitless ~50% | 52% | 75% | 72% / 73% | 80% / 81% | 28% / 27% | 85% | 0.15 | 71% | 0.60 | 2.0 | 73% | 1 |
| research-altaria (main Mega Altaria ex) | meta reference | Limitless ~53% | 46% | 41% | 51% / 51% | 61% / 62% | 49% / 49% | 56% | 0.63 | 35% | 1.26 | 2.2 | 72% | 1 |
| research-hydreigon (main Hydreigon) | meta reference | - | - | 75% | 53% / 53% | 65% / 66% | 55% / 56% | 67% | 0.33 | 53% | 0.79 | 1.8 | 100% | 2 |
| research-weezing (main Hoopa ex) | meta reference (also the goldfish opponent) | - | - | 63% | 0% / 80% | 90% / 89% | 79% / 78% | 51% | 1.05 | 79% | 0.89 | 1.7 | 86% | 2 |
| research-blaziken (main Mega Blaziken ex) | meta reference | - | - | 75% | 53% / 53% | 66% / 66% | 66% / 66% | 61% | 0.32 | 55% | 0.99 | 2.9 | 79% | 1 |
| research-sceptile (main Mega Sceptile ex) | meta reference | - | - | 86% | 41% / 41% | 64% / 64% | 54% / 55% | 68% | 0.23 | 20% | 0.51 | 2.7 | 100% | 2 |
| research-suicune (main Suicune ex) | meta reference | - | - | 63% | 87% / 88% | 92% / 92% | 75% / 74% | 81% | 0.21 | 69% | 0.51 | 2.4 | 31% | 2 |
| research-vespiquen (main Vespiquen ex) | meta reference | - | - | 63% | 75% / 75% | 84% / 84% | 82% / 82% | 37% | 0.37 | 57% | 0.45 | 1.7 | 100% | 1 |

One line per list:

- 07-skarmory-stall: one-Basic opening 86%; Skarmory ex online by own T3 95% first / 95% second (T4 97%/97%); combo by T4 96%/96%; goldfish (scripted pilot v aa): damaging attack by own T3 77% with 0.3 pts conceded first, Skarmory ex attacks by T4 98% with 0.3 conceded first, 1.4 dead cards/turn; unpriced-text cards (a): 0
- brew-05b-meowstic-hatterene-comfey: one-Basic opening 63%; Hatterene online by own T3 51% first / 50% second (T4 64%/63%); combo by T4 53%/52%; goldfish (scripted pilot v aa): damaging attack by own T3 79% with 0.4 pts conceded first, Hatterene attacks by T4 65% with 1.1 conceded first, 2.5 dead cards/turn; unpriced-text cards (a): 1
- brew-01-arceus-crobat-xatu: one-Basic opening 52%; Arceus ex online by own T3 0% first / 74% second (T4 84%/84%); combo by T4 45%/45%; goldfish (scripted pilot v aa): damaging attack by own T3 37% with 1.2 pts conceded first, Arceus ex attacks by T4 48% with 1.5 conceded first, 2.3 dead cards/turn; unpriced-text cards (a): 0
- brew-03a-arceus-nihilego-toxapex: one-Basic opening 52%; Arceus ex online by own T3 0% first / 75% second (T4 82%/83%); combo by T4 66%/65%; goldfish (scripted pilot v aa): damaging attack by own T3 35% with 0.7 pts conceded first, Arceus ex attacks by T4 49% with 0.8 conceded first, 0.7 dead cards/turn; unpriced-text cards (a): 0
- brew-06-pyukumuku-silvally-payback: one-Basic opening 41%; Silvally online by own T3 0% first / 72% second (T4 83%/83%); combo by T4 83%/84%; goldfish (scripted pilot v aa): damaging attack by own T3 15% with 1.3 pts conceded first, Silvally attacks by T4 33% with 1.5 conceded first, 2.8 dead cards/turn; unpriced-text cards (a): 1
- brew-06b-pyukumuku-silvally-scyther-grass: one-Basic opening 41%; Silvally online by own T3 0% first / 72% second (T4 83%/83%); combo by T4 84%/83%; goldfish (scripted pilot v aa): damaging attack by own T3 14% with 1.5 pts conceded first, Silvally attacks by T4 38% with 1.6 conceded first, 2.4 dead cards/turn; unpriced-text cards (a): 1
- brew-07-hoopa-darkrai-sableye: one-Basic opening 75%; Hoopa ex online by own T3 0% first / 85% second (T4 91%/91%); combo by T4 78%/78%; goldfish (scripted pilot v aa): damaging attack by own T3 71% with 0.4 pts conceded first, Hoopa ex attacks by T4 73% with 0.4 conceded first, 0.9 dead cards/turn; unpriced-text cards (a): 1
- brew-08-entei-rainbow-cave: one-Basic opening 95%; Entei ex online by own T3 100% first / 100% second (T4 100%/100%); combo by T4 84%/85%; goldfish (scripted pilot v aa): damaging attack by own T3 100% with 0.0 pts conceded first, Entei ex attacks by T4 100% with 0.0 conceded first, 2.3 dead cards/turn; unpriced-text cards (a): 1
- brew-09-sableye-obstagoon: one-Basic opening 75%; Mega Sableye ex online by own T3 92% first / 92% second (T4 95%/96%); combo by T4 63%/63%; goldfish (scripted pilot v aa): damaging attack by own T3 59% with 0.3 pts conceded first, Mega Sableye ex attacks by T4 67% with 0.4 conceded first, 2.0 dead cards/turn; unpriced-text cards (a): 1
- brew-10-diancie-giratina: one-Basic opening 52%; Mega Diancie ex online by own T3 0% first / 78% second (T4 87%/87%); combo by T4 90%/89%; goldfish (scripted pilot v aa): damaging attack by own T3 42% with 0.4 pts conceded first, Mega Diancie ex attacks by T4 81% with 0.5 conceded first, 2.5 dead cards/turn; unpriced-text cards (a): 1
- research-lucario: one-Basic opening 75%; Mega Lucario ex online by own T3 72% first / 73% second (T4 80%/81%); combo by T4 28%/27%; goldfish (scripted pilot v aa): damaging attack by own T3 85% with 0.2 pts conceded first, Mega Lucario ex attacks by T4 71% with 0.6 conceded first, 2.0 dead cards/turn; unpriced-text cards (a): 1
- research-altaria: one-Basic opening 41%; Mega Altaria ex online by own T3 51% first / 51% second (T4 61%/62%); combo by T4 49%/49%; goldfish (scripted pilot v aa): damaging attack by own T3 56% with 0.6 pts conceded first, Mega Altaria ex attacks by T4 35% with 1.3 conceded first, 2.2 dead cards/turn; unpriced-text cards (a): 1
- research-hydreigon: one-Basic opening 75%; Hydreigon online by own T3 53% first / 53% second (T4 65%/66%); combo by T4 55%/56%; goldfish (scripted pilot v aa): damaging attack by own T3 67% with 0.3 pts conceded first, Hydreigon attacks by T4 53% with 0.8 conceded first, 1.8 dead cards/turn; unpriced-text cards (a): 2
- research-weezing: one-Basic opening 63%; Hoopa ex online by own T3 0% first / 80% second (T4 90%/89%); combo by T4 79%/78%; goldfish (scripted pilot v aa): damaging attack by own T3 51% with 1.0 pts conceded first, Hoopa ex attacks by T4 79% with 0.9 conceded first, 1.7 dead cards/turn; unpriced-text cards (a): 2
- research-blaziken: one-Basic opening 75%; Mega Blaziken ex online by own T3 53% first / 53% second (T4 66%/66%); combo by T4 66%/66%; goldfish (scripted pilot v aa): damaging attack by own T3 61% with 0.3 pts conceded first, Mega Blaziken ex attacks by T4 55% with 1.0 conceded first, 2.9 dead cards/turn; unpriced-text cards (a): 1
- research-sceptile: one-Basic opening 86%; Mega Sceptile ex online by own T3 41% first / 41% second (T4 64%/64%); combo by T4 54%/55%; goldfish (scripted pilot v aa): damaging attack by own T3 68% with 0.2 pts conceded first, Mega Sceptile ex attacks by T4 20% with 0.5 conceded first, 2.7 dead cards/turn; unpriced-text cards (a): 2
- research-suicune: one-Basic opening 63%; Suicune ex online by own T3 87% first / 88% second (T4 92%/92%); combo by T4 75%/74%; goldfish (scripted pilot v aa): damaging attack by own T3 81% with 0.2 pts conceded first, Suicune ex attacks by T4 69% with 0.5 conceded first, 2.4 dead cards/turn; unpriced-text cards (a): 2
- research-vespiquen: one-Basic opening 63%; Vespiquen ex online by own T3 75% first / 75% second (T4 84%/84%); combo by T4 82%/82%; goldfish (scripted pilot v aa): damaging attack by own T3 37% with 0.4 pts conceded first, Vespiquen ex attacks by T4 57% with 0.5 conceded first, 1.7 dead cards/turn; unpriced-text cards (a): 1
<!-- table:end -->

Decision this informs: which numbers a brew page should show Dustin before he spends ladder games on a list. On the six lists he has ladder records for, "points given up before the main attacker's first attack" orders them the same way as his records, and all six are flagged as lists k3 can't judge. Engine commit 86e6154 (goldfish built from 235ab39; the engine code is the same in both).

Seeds: new, not table deals. Goldfish games use 22,200,000,000 + opponent × 10,000 + i (i < 50, opponents in file order, the same deals for every list and both opponent bots). The card-draw model uses Python seed 22,100,000,000.

# Brew consistency pages (A1), Sept 25

One page per list, in this folder. Each page has three parts:

1. **What the cards allow.** A card-draw model plays the list solitaire over 20,000 shuffles, using Pocket's opening rule and the list's own draw and search cards. It gives one-Basic openings and which Basic is then alone, when a main attacker could attack, Stage 2 by turn 3, combo pieces by turn 3, stuck cards, and each card's chance of being seen by turn 1 to 4.
2. **What the bot does with it.** k3 plays the list against the 8 table decks, 50 deals each: 400 games against a bot that only ends its turn ('et'), and 400 against one that attaches and attacks ('aa'). "Could attack" and "did attack" are recorded separately. The pages also give points given up before the first main attack, dead cards, and crashes.
3. **Where the bot is blind.** These are the list's cards that k3 prices with a fallback. Effects that mention the opponent's hand or deck are scored as doing nothing. Attacks with damage effects the threat estimate doesn't read are counted at printed damage. Effects that pay off on the opponent's turn don't count, because k3 doesn't search that turn and its clock counts HP, not damage reduction.

## Calibration against the Ladder Log

Going first / going second. "Aa" columns are against the attacking bot.

| list | ladder | card model: main attacker ready by turn 3 | bot vs aa: main attack by turn 3 | bot vs aa: never used a main attacker | bot vs aa: points given up before first main attack | share of games giving any |
|---|---|---|---|---|---|---|
| Deck 07 Skarmory stall | 3-1 | 95% / 95% | 71% / 92% | 3% / 2% | 0.04 / 0.01 | 2% / 0% |
| Brew 05b Meowstic / Hatterene | 3-3 | 50% / 50% | 16% / 23% | 66% / 71% | 0.28 / 0.23 | 21% / 17% |
| Brew 01 Arceus / Crobat / Xatu | 1-3 | 61% / 94% | 11% / 60% | 54% / 33% | 0.46 / 0.09 | 24% / 8% |
| Brew 03a Arceus / Nihilego / Toxapex | 1-3 | 57% / 92% | 7% / 45% | 55% / 47% | 0.47 / 0.06 | 29% / 5% |
| Brew 06b Silvally / TR Scyther | 0-3 | 82% / 96% | 11% / 32% | 67% / 60% | 0.46 / 0.15 | 31% / 13% |
| Brew 06 Silvally / TR Mewtwo (Payback) | 0-3 | 0% / 92% | 0% / 47% | 58% / 43% | 0.58 / 0.31 | 31% / 15% |

What this shows, plainly:

- **Points given up before the first main attack** (going first) orders the six lists like the ladder: Skarmory lowest, 05b next, the four losing brews highest, with Payback worst. This matches Dustin's notes ("took both Pyukumukus for 2 points before Silvally had 3 energy"). But the ladder records are 4 to 6 games each, so this is a pattern to watch, not a proven yardstick.
- **Skarmory stands apart on everything.** Its attacker is ready and used by turn 3 in most games, it almost never gives up points first, and it almost always uses its main attacker. It also has the worst one-Basic rate (86%). Its lone Basic is usually Skarmory ex itself, so a one-Basic opening isn't the danger for this list. The one-Basic number needs the "which Basic" line beside it.
- **The card model and the bot disagree a lot on the brews.** On brew-01 going first, the cards allow an attack by turn 3 in 61% of games, but k3 made one in 11%. Traces show k3 building Arceus ex, which needs three energy, instead of Xatu. Going first, brew-06b's cards allow 82% and k3 made 11%. Part of this is k3 choosing another attacker, and part is k3 misjudging these attackers (next point). The pages show both numbers so the gap is visible.
- **Every anchor list is flagged: k3 can't judge any of them.** Copycat (in 05b, 06 and 06b) is scored as doing nothing. Skarmory's walls (Jasmine, Metal Core Barrier, Steel Wing) and the Rocky Helmet, Poison Barb, Goo-zooka and Pyukumuku in 03a, 06 and 06b pay off on the opponent's turn, which k3's clock ignores. In all five brews a main attacker has a damage effect the threat estimate reads at printed damage: Xatu's Life Drain, Toxapex's Severe Poison, Hatterene's Mental Crush, Silvally's Gold Breaker and TR Scyther's Second Strike. So "did attack" and "won" on these pages describe k3's play, not the list's ceiling. The card model is the part that doesn't depend on the bot.
- **"Won" against 'aa' is not a strength number.** Every list beats 'aa' 88–99%. The column is only there to show the games run to completion.
- No game crashed. Every card in the six lists is fully implemented in the engine.

Two list-check notes the pages raise: Pyukumuku's attack and Indeedee ex's attack can't be paid with their lists' Energy. Both are walls, so this is by design.

## Files

- `<list>.md`: the pages.
- `raw/<list>_model.json`: card-draw model output. `raw/<list>_{et,aa}.jsonl`: one line per goldfish game. `raw/<list>_{et,aa}.txt`: command and summary. `raw/<list>_coverage.json`: the blind-spot flags. `raw/index.json`: the calibration numbers above.
- Tools: `lib/brew_consistency.py` (card-draw model), `engine/examples/goldfish.rs` (bot runs and flags), `lib/brew_pages.py` (runs both, writes the pages). To add a list, give it a line in `LISTS` in `lib/brew_pages.py` with its main attackers and combo.

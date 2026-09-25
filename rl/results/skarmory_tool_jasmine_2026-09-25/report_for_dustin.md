**Short answer:** The bot can't see the −50 from either card. It plays Metal Core Barrier for a different reason: when it scores a position, it gives a flat bonus for *any* Tool on your Active Pokémon. Jasmine gets no bonus, so to the bot it looks a little worse than doing nothing.

### Why the bot misses the −50
The bot only looks ahead through its own turn. Then it stops and rates the game with its "board score," a single number for how good things look. Both −50s only matter when the opponent attacks, and the bot never looks that far ahead.

### Why the Tool gets played anyway
The board score adds **+10** whenever your Active is holding a Tool. It doesn't check which Tool it is, or whether it does anything for that Pokémon. Each card that leaves your hand costs **1** point. So Barrier on the Active scores **+9**, and Jasmine scores **−1**.

You can see it's the wrong reason. About 1 in 5 Barriers go onto Indeedee ex. It's a Psychic Pokémon, so Barrier does nothing for it.

A test confirmed this is the cause:
- With the +10 turned off, the bot played Barrier on 1.5% of its chances instead of 75%.
- When Jasmine got the same +10, the bot played it on 82% of its chances instead of about 1%.

### Why Jasmine stays in your hand
Every time the bot ended its turn with a playable Jasmine, Jasmine scored exactly 1 point lower. That point is just the card leaving your hand. When it does get played, it's by accident. One case is the opponent's Hiking Trail, which refills your hand. The other is a tie between moves, which Jasmine wins because it's listed last.

### The game rules work correctly
Both cards cut a 150-damage hit on Skarmory ex down to 100. Jasmine actually covers more: every Skarmory ex, even one on the Bench or one switched in, and it stacks with Steel Apron. The catch is that it uses up your Supporter for the turn.

### What this means for your Skarmory deck
The simulator **under-rates** the deck. Its 47% win rate in the last full check comes from a bot that treats Jasmine as a dead card and wastes some Barriers.
- The Tools really do help. Stopping the bot from playing them cost about 13–15 points of win rate (1,920 games).
- A rough fix that makes the bot value Jasmine raised wins by about 6 points (1,920 games). It won more in all 8 matchups.

### Possible fixes (your call; none of these are in the official bot)
1. **Count the real −50** from both cards when the bot guesses how hard the opponent's next hit will be. This is the cleanest fix, and it hasn't been built.
2. **Make the Tool bonus smarter:** only count a Tool that actually does something for the Pokémon holding it. That would stop the Barriers going on Indeedee ex.
3. **The rough fix above:** give Jasmine +10 while it protects your Active. It gained about 6 points, but it's just as blind as the Tool bonus.

Don't simply remove the +10. The bot would stop playing Tools and lose about 13–15 points. Each fix would be a new version of the bot that needs its own test.

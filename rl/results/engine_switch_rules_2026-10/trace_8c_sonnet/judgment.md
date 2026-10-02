# Games that need a judgment (1)

For Dustin, in plain words. The coin probe finds the queued coin-path choice (repair B) only at the leaf of the bot's search: offered at ply 3 in a frame that mixes it with plain moves, so the bot sees it offered but never plays it.

- **km3, pairing 4, deal 106** (held garchomp_meowth v t-sceptile), turn 12, tick 82: the old engine chose `Play { trainer_card: B1a 067 Quick-Grow Extract }` and R chose `Attack(Attack { energy_required: [Grass], title: "Pound", fixed_damage: 20, effect: None })` from the same position. Coin probe: {'tick': 82, 'queued': 3, 'cut': None, 'free': False}.

# Shark Tempo: two untested options

Checked October 2, 2026. Bounded Astra card-mechanics assessment only. Dustin describes the deck as fun and competitive; that is owner testimony, not a rating or a measured result. The five new games were not reviewed in this check. Neither variant below has been tested here.

## Baseline

The configured 20-card list [S1] has 2 Carvanha B4 034, 2 Mega Sharpedo ex B4 035, 2 Alolan Vulpix B2 028, 2 Alolan Ninetales ex B2 029, 1 Lapras A3 044, 2 Misty, 2 Professor's Research, 2 Poke Ball, and 1 each of Copycat, Cyrus, Irida, Elegant Cape and Lucky Ice Pop. Water Energy only.

## Soothing Shore: the smaller experiment

**Compatible.** Its directly inspected text says that at the end of each player's turn, that player heals 20 damage from each of their Pokemon with any Water Energy attached [S4]. This covers Active and Bench, requires attached Water rather than merely Water typing, and applies to both players. It heals your Pokemon at the end of your turn, not again at the end of the opponent's turn.

Sharpedo's attack supplies Water to a Benched Water Pokemon [S2], so its acceleration can also make that Pokemon eligible for Shore healing. Repeated healing could support a damaged Shark retreating to the Bench. That is a compatibility inference, not evidence that it improves this deck.

The tradeoffs are real: Shore cannot rescue a Pokemon already Knocked Out, is delayed until the end of your turn, and can heal opposing Water-powered Pokemon after their turns. That opposing heal can undo part of Shark's 70 damage and change a later knockout threshold. Another Stadium replaces Shore; only one Stadium may be played during your turn, and the same-named Stadium cannot be played over it [S4].

**Practical first test:** replace the single Lucky Ice Pop with one Soothing Shore, retaining the other 19 cards and Water-only setting. This isolates recurring board-wide healing against the existing immediate Active-only heal. Record whether Shore creates an extra surviving attack turn, whether its delayed timing costs an opportunity, and whether enemy healing changes a knockout. Keep the original list as the comparison. This is a proposed test, not a deck edit or an improvement claim.

## Wailord: compatible, but a larger change

Sharpedo's one-Water Turbo Shark does 70 and adds one Water to one Benched Water Pokemon; its printed retreat cost is zero [S2]. Wailmer and either inspected Wailord qualify while Benched. This can build a backup attacker while Shark attacks, then allow Shark to retreat. It cannot accelerate an Active Wailord.

The inspected non-ex Wailord has 200 HP and requires four Colorless for 60 plus 10 per attached Water, giving 100 with four Water. Wailord ex has 250 HP, requires four Water, does 100, and removes its Special Conditions [S3]. Neither is a cheap attacker simply because Shark can help power it. Charging Wailord also diverts attachments that could prepare the existing Ninetales plan. Keeping Shark exposed for additional attack turns matters because its printed Mega knockout rule gives the opponent three points [S2].

Adding Wailord requires Wailmer too: at least two slots for a 1-1 line, plus evolution setup and Bench room. Replacing Lapras alone does not make room. A full 2-2 line costs four slots. For a later, separate experiment, replacing the complete 2-2 Vulpix/Ninetales line with 2 Wailmer and 2 non-ex Wailord would keep the count at 20 and ask a clear question: does a larger backup attacker justify giving up the current Ninetales plan? This is a more substantial redesign than adding Shore, with no evidence yet that the answer is yes. Start with the non-ex version if specifically testing the larger one-point backup role; the ex version is a separate hypothesis.

## Evidence and limits

- **S1:** [Configured artifact deck snapshot](ARTIFACT_DECK_BEFORE.txt), Draft A: Shark Tempo, Pokemon and Trainer tables. Exact configuration only; not proof every recording used every listed card.
- **S2:** [Mega Sharpedo ex enlarged printed card](../20260921_150630_sol_verification/final_packet/frames/00-26.000-turn1-mega-sharpedo.jpg), `20260921_150630000_iOS.MP4`, 00:26.000. Individually inspected for attack, target, free retreat and three-point rule.
- **S3:** [Wailmer and both Wailord printed cards](../20261002_020315000_iOS_competitive_sol/native/t0001.50.jpg), `20261002_020315000_iOS.MP4`, 00:01.500. Individually inspected. The earlier [energy check](../BATCH_2026-10-02_COMPETITIVE/ASTRA_ENERGY_CHECK.md) binds the configured Wailmer B4 036, Wailord B1 057 and Wailord ex B4 037 versions; alternate artwork is visible.
- **S4:** [Soothing Shore enlarged printed text](../20261002_021402000_iOS_competitive_sol/native/t0254.00.jpg), `20261002_021402000_iOS.MP4`, 04:14.000. Individually inspected, including timing, Water condition and Stadium rule box.
- Official-source discovery found no additional specific Shore timing ruling. [Pokemon Support's Gameplay FAQ](https://support.pokemon.com/hc/en-us/articles/30330309361172-Pok%C3%A9mon-TCG-Pocket-Gameplay-FAQ) directs rules questions to the in-game rules and distinguishes Pocket from the physical TCG. The retained in-game card text is the authority here; search-result third-party card text and simulator rules were not used as authority.

Unresolved: optimal cut, exact matchup benefit, actual setup speed, availability of cards, and any resulting win-rate difference. The proposed swaps were not applied. No artifact, simulator, source-media, index or review-log changes were made.

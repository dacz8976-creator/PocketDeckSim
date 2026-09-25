# Why kp3 plays Metal Core Barrier but not Jasmine (Dustin's question, Sept 25)

**In plain words: the bot sees neither card's −50.** It plays Metal Core Barrier because its board score gives a flat +10 to any Tool on the Active, and Jasmine gets nothing. This is a card-agnostic blind spot, and it makes the simulator under-rate Dustin's Skarmory stall deck (07).

**The question:** "Why would the bot play the metal tool for −50 damage, but not the supporter that does the same thing? In the skarmory deck." The floor check had counted Metal Core Barrier played on 79.6% of the turns it could be, and Jasmine on 1.3% (`../floor_payback_check_2026-09-25/07-skarmory-stall.md`).

**How it was answered:**
- A laptop-session workflow ran four independent investigations:
  - the scoring code, with probe positions;
  - the engine's implementation of both cards, with probe tests;
  - 240 traced games;
  - a causal test on the same seeds, with the +10 set to 0 and with Jasmine given the same +10.
- Then a synthesis, then three skeptics (code, data, and alternative explanations).
- Seeds: 21,102,000,000 – 21,102,999,999. Scratch builds only; the official engine is unchanged.
- Full output: `workflow_output.json`. The plain answer as sent to Dustin: `report_for_dustin.md`.

## What was established (it survived the skeptics)

1. **kp3 looks only through its own turn**, then scores the position (`expectiminimax_player.rs` 633-657, 773-798, 914-918). Both −50s act during the opponent's attack, which it never plays out.
   - Its scoring (`public_clock_effect_value_function`, `ValueFunctionParams::baseline()`, `EvalFeatures::OFF`) reads neither Jasmine's stored turn effect nor the Barrier's −50.
   - The threat clock divides raw HP by damage (`value_functions.rs` 905, 941).
   - kd's defender pricing leaves both out on purpose (`hooks/core.rs` 1577-1580).
2. **The +10 decides the Tool plays.** The score adds +10 whenever the bot's Active holds any Tool, whatever it does (`value_functions.rs` 50, 516, 667-672). Each card leaving the hand costs 1 (lines 45, 510). So the score changes as follows:
   - Metal Core Barrier or Steel Apron on the Active: **+9**;
   - a Tool on the Bench: −1;
   - **Jasmine: −1.**
3. **Proof that it's the wrong reason:**
   - About 1 in 5 Barriers go onto a Psychic Indeedee ex, where they do nothing: 63 of 284 in 240 traced games.
   - When both Tools could go on a Tool-free Active, the pick is decided only by move order.
4. **The causal test** (same 240 seeds, official binary against scratch variants):
   - With the +10 at 0, Metal Core Barrier falls from 74.6% of its turns to 1.5%, and Steel Apron from 70.5% to 2.7%.
   - Giving Jasmine's stored effect the same +10 when it covers the Active raises Jasmine from 1.8% to 82.4%.
5. **Jasmine is held because it scores exactly 1 lower** (the hand-size point), at all 191 examined decisions where the turn ended with Jasmine playable. It is not weighed and rejected.
6. **The engine is right.** Both cards cut a 150 hit on Skarmory ex to 100, at the same step (after Weakness) and for the same turn.
   - Jasmine covers more: every Skarmory ex, including one on the Bench or switched in, and it stacks with Steel Apron.
   - The Tool costs no Supporter slot.
7. **Public pricing plays no part here.** kp3 behaves like k3 for these cards.

## What the skeptics corrected

- **"The Tools really do help, worth about 13–15 points": not isolated.**
  - Removing the +10 cut deck 07's wins from 132 to 97 of 240, and every matchup moved the same way.
  - But the same weight also charges −10 when the opponent's Active holds a Tool, and 7 of the 8 panel lists run Tools. So that drop is not a measure of deck 07's own Tools.
  - The baseline block (55.0%) also sits high against the floor's 47.3%.
- **"Jasmine's rare plays are the opponent's Hiking Trail": partly.**
  - In a fresh 1,920-game official block, 26 of 39 Jasmine plays were against Blaziken with Hiking Trail in play and a hand of 3 or fewer.
  - Some others were exact ties that Jasmine won on move order. A few are unexplained.
- **"Pricing Jasmine hasn't been shown to change the win rate": now shown.**
  - The skeptic ran a deck-seat-only version of the Jasmine +10 on a fresh paired 1,920-game block: 1,068 wins (55.6%) against 959 (49.9%), **+5.7 points**.
  - The pairs split 206 to 97 (McNemar z = 6.3), and deck 07 did better in all 8 matchups.

## What it means

- **The simulator under-rates Skarmory stall.** Its floor result (47.3%, "clears the floor") stands. The skew is in the bot's play, not in the verdict.
- **This is a card-agnostic blind spot, in the plan's B5 sense.** Any "during your opponent's next turn, take −X damage" effect is invisible to the bot. Any Tool on the Active gets +10, useful or not.
- **The clean fix is a new registered candidate, not a patch to kp3.** It would price the real reduction from Tools and turn effects in the threat clock for the defender, and drop the flat +10, or make it conditional on the Tool doing something for its holder. The table and a paired A/B would decide, like any candidate.
  - Removing the +10 alone is not the fix: the bot would stop playing Tools at all.

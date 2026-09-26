# B2e held-out decks: the reading (Sept 26)

Descriptive only; no adoption decision is taken from it (spec: `../b2e_card_check_2026-09-26/README.md` sections 4-5). This is the baseline for RUN5's held-out veto ("a held-out deck more than 2 further from Limitless") and for A2's bar. Full tables: `b2e_tables.md`. The generated draft with every pairing's findings and examples: `READING_draft.md`.

**What was run.**
- **Games:** six top-finishing Limitless archetype lists that are also Dustin's decks (Mega Manectric ex/Heliolisk, Team Rocket's Raticate ex/Alolan Ninetales ex, Hoopa ex/Mega Absol ex, Garchomp, Whimsicott ex/Ariados, Mega Charizard Y ex/Entei ex), plus Dustin's own six files as a second set. Each played the eight panel decks, 500 deals per pairing, with k3 on both sides and then kp3 on both sides, on the same deals. That is 96,000 games.
- **Tool:** the official engine (7fc6ccb) through legality_scan with the reviewed `--pairs/--seed-base` extension. Binary sha256 `45ecfda4…3b5b`.
- **Checks before any row was read:**
  - IDENTITY PASS: default flags byte-for-byte equal to the official scan on 4,000 table games, the `--pairs` path replaying the same games, and six refusals.
  - ROWS PASS: every seed, seat, deck and pilot is as the TSV says.
  - No RULE findings in any pairing.
- **Seeds:** 21,106,000,000 + 10,000 × pairing + i. This block and the two Altaria B2c blocks (21,110,000,000+ and 21,160,000,000+) need rows in START_HERE's seed table. That page is shared, so this report asks for the rows rather than editing it.

**In plain words.**
- **The simulator is far off on four of the six held-out archetypes, whichever bot pilots.** Only Whimsicott (few real matches) and Charizard Y/Entei (under kp3) land inside their real-world range.
  - **Mega Manectric ex/Heliolisk is overrated by about 15 points** under both bots: 64% against 49% in real play.
  - **Garchomp is underrated by about 10 points:** 22-23% against 32.5%.
  - **Raticate is the pilot's story.** k3 matches the real 41% almost exactly, but kp3, which finally uses Thieving Incisors, scores it 57.5%, 16 points over. This is the Raticate lift the brew-pilot check found on Sept 25, now measured against real results. Real players either don't get that much from Raticate, or opponents play around it in ways the bot doesn't.
  - **Hoopa ex/Mega Absol ex** is a little over under kp3 (+6.5).
- **For Dustin's own decks, the list matters as much as the pilot.**
  - **Hoopa/Absol:** his deck 04 scores 32.6% where the top-finishing Hoopa/Absol list scores 56.5% on the same deals. That is the largest list difference, +23.9 ± 2.0.
  - **Garchomp:** his list beats the archetype list by 5.3.
  - **Whimsicott and Manectric:** the archetype lists are a little better than his, +5.6 and +3.8.
- **This does not say which decks to play.** The simulator's fit on these archetypes is too loose for that, which is exactly why they are held-out tests. It does say where the bot's blind spots are largest: Manectric, Garchomp, and kp3's Raticate.

**The baseline numbers** (pooled Limitless equal-weight average L; a later candidate vetoes on a deck if |C − L| − |kp3 − L| > 2):

| Archetype | L pooled | kp3 | k3 | abs(kp3 − L) | abs(k3 − L) |
|---|---:|---:|---:|---:|---:|
| Mega Manectric ex Heliolisk | 49.2 | 64.0 | 64.6 | 14.8 | 15.4 |
| Team Rocket's Raticate ex Alolan Ninetales ex | 41.2 | 57.5 | 41.1 | 16.4 | 0.1 |
| Hoopa ex Mega Absol ex | 49.9 | 56.5 | 53.4 | 6.5 | 3.4 |
| Garchomp | 32.5 | 21.6 | 23.3 | 10.9 | 9.2 |
| Whimsicott ex Ariados | 32.3 | 36.3 | 40.2 | 4.0 | 7.9 |
| Mega Charizard Y ex Entei ex | 49.2 | 44.6 | 52.6 | 4.6 | 3.4 |

**A2's bar (kp3, archetype lists, pooled intervals): 2 of 6 inside.** This states the bar; it does not lift or apply the screen's hold, which stays as Dustin set it.

**Limits.**
- Whimsicott's L rests on 60 matches with three one-sided cells.
- Section 6 of the spec flags coverage (cards the bot is known not to price) for most lists. Hoopa/Absol's Darkness Claw is the same blind spot as in the Hydreigon run; kp3 prices it.
- Per-cell misses are in `b2e_tables.md`.

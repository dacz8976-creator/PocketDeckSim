# Appendix: the cost arithmetic (Oct 2)

Every figure here is an [estimate] from list prices and assumed token counts, to be replaced by measurement in week 1. Prices are Anthropic's first-party API list prices as cached on 2026-09-25. Local options cost no money. Nothing here is a strength claim.

## Costing the options (prices: Anthropic first-party API, cached 2026-09-25 in the claude-api skill)

| Model | Input $/M | Output $/M | Cache read $/M | Cache write (5 min) | Min cacheable prefix |
|---|---|---|---|---|---|
| Haiku 4.5 | 1.00 | 5.00 | 0.10 | 1.25x input | 4,096 tokens |
| Sonnet 5.5 | 2.00 | 10.00 | 0.20 | 1.25x | 512 |
| Opus 5.5 | 4.00 | 20.00 | 0.20 | 1.25x | 512 |
| Fable 5.1 | 10.00 | 50.00 | 0.25 | 1.25x | 512 |
Batch API: 50% off, results within 24 h (usually much less); caching inside batches is best-effort.
Thinking tokens bill as output. Sonnet 5.5 / Opus 5.5 / Fable 5.1 reject non-default temperature (400), so their games
are not reproducible from the seed alone; Haiku 4.5 accepts temperature 0 but is still not bit-exact.

Token assumptions (estimates, +-2x until measured):
- Static prefix per deck pair: Pocket rules summary ~1,500 + both lists with card texts ~2,500 + instructions ~500
  = ~4,500 tokens, cached (5-min TTL stays warm while games run continuously). Just clears Haiku's 4,096 minimum.
- Fresh per call: board, hands, discard, points, the legal moves with engine-computed facts (damage after Weakness,
  KO yes/no, Energy needed) ~1,500 (per-action) or ~2,000 (per-turn plan).
- Output incl. thinking: per-action light 1,000 / heavy 3,000; per-turn plan light 2,000 / heavy 5,000.
- Calls per game (the pilot's side only; forced single-option moves skipped): per-action ~40; per-turn plan ~15
  (re-plan after a draw or coin that changes the turn).

Per-action design (40 calls/game): cache read 180K, fresh input 60K, output 40K light / 120K heavy per game.
| Model | $/game light | $/game heavy | 100 games light | 100 games heavy |
|---|---|---|---|---|
| Haiku 4.5 | 0.28 | 0.68 | 28 | 68 |
| Sonnet 5.5 | 0.56 | 1.36 | 56 | 136 |
| Opus 5.5 | 1.08 | 2.68 | 108 | 268 |
| Fable 5.1 | 2.65 | 6.65 | 265 | 665 |

Per-turn plan design (15 calls/game): cache read 67.5K, fresh 30K, output 30K light / 75K heavy.
| Model | $/game light | $/game heavy | 100 games light | 100 games heavy |
|---|---|---|---|---|
| Haiku 4.5 | 0.19 | 0.41 | 19 | 41 |
| Sonnet 5.5 | 0.37 | 0.82 | 37 | 82 |
| Opus 5.5 | 0.73 | 1.63 | 73 | 163 |
| Fable 5.1 | 1.82 | 4.07 | 182 | 407 |
Batch halves these if decisions from all 100 games are lockstepped into rounds; each round waits for the batch, so a
run takes roughly half a day to a few days. If the LLM plays BOTH sides, double everything.
Output (thinking) dominates the bill: 70-90% of each row.

Money per DECK QUESTION (the pilot's games across the panel; 95% half-width at p near 0.5: 100 games ~+-10 points,
400 ~+-5, 1,070 ~+-3). Light-heavy ranges, before the batch discount (batch halves them):
| Model, design | 100 games (+-10) | 400 games (+-5) | 1,070 games (+-3) |
|---|---|---|---|
| Haiku 4.5, per-turn plan | $19-41 | $76-164 | $203-439 |
| Sonnet 5.5, per-turn plan | $37-82 | $148-328 | $396-877 |
| Opus 5.5, per-turn plan | $73-163 | $292-652 | $781-1,744 |
| Fable 5.1, per-turn plan | $182-407 | $728-1,628 | $1,947-4,355 |
| Haiku 4.5, per-action | $28-68 | $112-272 | $300-728 |
| Sonnet 5.5, per-action | $56-136 | $224-544 | $599-1,455 |
| Opus 5.5, per-action | $108-268 | $432-1,072 | $1,156-2,868 |
| Fable 5.1, per-action | $265-665 | $1,060-2,660 | $2,836-7,116 |
For scale, his own time: 10 minutes a game plus recording, so 100 games of his own ~17 h, 400 ~67 h.
Local options cost $0 in money: option (1) at 7-40 min per game is 400 games in ~4-22 h on 10 cores (1,070 games
~12-60 h); option (2) at ~4 min per game is 400 games in ~3 h on 10 cores (1,070 ~7 h). Time to REACH trustworthy play
(build + validation, rough): LLM harness 3-5 days plus the probe; (1) 1-2 weeks; (2) 2-3 weeks (needs a fitted
evaluation that generalises); hybrids come after one of these exists. Every number here is an estimate to be replaced
by measurement in week 1.

Wall time (API latency, estimates): per call Haiku 2-5 s, Sonnet 5-15 s, Opus 10-30 s with thinking.
Per-action: Haiku 2-3 min/game, Sonnet 3-10 min, Opus 7-20 min. 100 games one at a time: Haiku 3-5 h, Sonnet 5-17 h,
Opus 12-33 h; 5 games in parallel divides by ~5 if rate limits allow.

Money gate: API usage is billed to an Anthropic API account (Console credits), separate from his Claude plan; nothing
spends without his word and a dollar cap. A cheap probe comes first: the 20 pause-game turns + quiz positions, one call
each, 3 repeats, Haiku + Sonnet (+ Opus): under ~$10 total. Measure real tokens from response.usage there and redo
this table before any 100-game run.

How we'd know an LLM pilot plays at "human level":
1. Agreement with Dustin's own decisions on the 20 pause-game turns and the quiz positions (km3: same first action on
   8 of 20, split 7, differs 5). Small n: a screen, not a verdict.
2. Same position asked 3 times: how often it gives the same move (consistency).
3. Dustin reads a few complete game logs blind (which pilot?) and marks moves a human wouldn't make.
4. Win rate against km3 on the same deals, paired, both seats.
Known failure modes to design against: miscounted damage/HP (give engine-computed facts), Pocket rules confused with
the physical TCG (rules summary in the prompt; RULES_FOR_AGENTS.md), long-horizon point race (show points and what
each attack would do), illegal moves (impossible: it chooses from the engine's legal list).
Reproducibility: log every prompt and response with the deal seed; the logged transcript is the record; replays read
answers from the log by state hash (deterministic and free); report the same-deal-twice agreement rate.

Local options (1) determinised multi-turn search and (2) ISMCTS / rollouts: $0 money; laptop or cloud cores.
Scale: km3 played 1,000 games in ~2 min on the laptop (Wallace run, 19:06-19:08 UTC), so ~1-2 s per game per thread.
- (1) a 2-turn determinised lookahead (K sampled hidden hands/decks/coins; opponent's reply played by km3; our next
  turn's best line by km3; leaf = km3's evaluation + points): ~10-60 s per decision => 100 games ~3-4 h on 10 cores.
  Deterministic given seeds. Risk: the leaf is still km3's evaluation (bench Energy weakly priced), the opponent model
  is km3, determinisation's strategy-fusion error. Directly targets requirement A2 and the evidence in F.
- (2) ISMCTS with fast rollouts and a fitted evaluation at the leaves: ~2,000 iterations x ~3 ms => ~6 s per decision
  => 100 games ~1 h on 10 cores. Risk: the fitted evaluation's gains were specialised (B); rollout-policy bias.

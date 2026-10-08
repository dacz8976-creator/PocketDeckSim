# Slow report from existing games: 03-wailord-indeedee-wall

**Existing development evidence, not a fresh test.** Nothing was played for this page: it reads games that were already played, by the kx3 development run (2026-10-03) and by gate 3 of the Tool tie-break (2026-10-06), both registered before the first of this deck's games (only 03-wailord-indeedee-wall's games were read, so that is all that was checked).

**kx3 (d513e37b) on 03-wailord-indeedee-wall v km3 on the public panel** (8 public lists: t-altaria, t-blaziken, t-hydreigon, t-lucario, t-sceptile, t-suicune, t-vespiquen, t-weezing). This is not the km3 floor check, which has its own page and its own result and is not changed by anything here; there is no pass or fail line.

## Question 1: how does 03-wailord-indeedee-wall do with kx3, and is that better than with km3?

Size: 80 kx3 games + 80 cheap km3 baseline games (5 deals x 2 seats against each of the 8 public lists; the baseline games are the same deals with km3 on the deck). Source: the development run.

- With kx3, 03-wailord-indeedee-wall scored **80.6%** over the 80 kx3 games: probably between 70.6% and 87.8% (95% interval; this range refers to the 80 kx3 games). A win counts 1, a tie 1/2, a loss 0.
- With km3, on the same deals, it scored 74.4% over the 80 cheap km3 baseline games.
- The gain: kx3 scored **+6.2 points** compared with km3 on the same deals, probably between -1.9 and +14.4 points (95% interval). That range refers to the 80 paired games, each a deal and seat played by both pilots: 80 kx3 games + 80 cheap km3 baseline games.
- Time: kx3 took 770 s a game on average on this deck (about 13 min; slowest 2228 s), 2 games at a time; the km3 baseline games took 1.8 s each.

What the 80-game range can tell and cannot tell: it can tell whether kx3 plays this deck near, clearly above or clearly below an even score against these 8 lists (70.6% to 87.8% here), and it can tell a large gain over km3 from none at all (the gain's range is 16.3 points wide). That range includes no gain at all: these 80 paired games do not show that kx3 plays this deck better than km3, and do not show that it plays it worse. They do argue against a gain much larger than 14.4 points or a loss much larger than 1.9 points; a smaller difference needs more deals. It cannot tell a gain of a point or two from a gain of ten: 80 games decide only that much, and a wide range is a statement of how much 80 games decide, not an answer of "nothing". More deals narrow it (the cost table in the slow-report plan gives the hours).

## Against each public list

| opponent (km3) | kx3 games | score | 95% range |
|---|---|---|---|
| t-altaria | 10 | 90.0% | 59.6% to 98.2% |
| t-blaziken | 10 | 70.0% | 39.7% to 89.2% |
| t-hydreigon | 10 | 80.0% | 49.0% to 94.3% |
| t-lucario | 10 | 60.0% | 31.3% to 83.2% |
| t-sceptile | 10 | 80.0% | 49.0% to 94.3% |
| t-suicune | 10 | 85.0% | 54.1% to 96.5% |
| t-vespiquen | 10 | 90.0% | 59.6% to 98.2% |
| t-weezing | 10 | 90.0% | 59.6% to 98.2% |

Each row's range refers to the 10 kx3 games against that list; with so few games it can separate a very easy or very hard list from an even one, not two similar lists from each other.

## Question 2: does the Tool tie-break change what kx3 does with this deck?

Existing development evidence too: gate 3 of the Tool tie-break (`rl/results/strength_2026-10-06_kx3_tools_gate3`), a candidate build (kx3_r16_c12_z2_real_t0_poolmeta_tools, program sha256 `cf73b2a4e858`, **not the pinned build**), played on the development run's own deals.

Size: 80 kx3 games with the Tool tie-break on + the 80 existing kx3 games with it off, paired by deal and seat (80 paired games; and 80 cheap km3 baseline games, which the gate-3 build replays exactly).

Build check: 80 of the 80 km3 baseline games in the gate-3 run replay the development run exactly (same deals, same moves, same results), and all 80 kx3 games in the gate-3 run start from the development run's own deal (same seed, same first player), so the two runs are the same deals played by the same km3.

- 15 of the 80 pairs had a logged decision that differed (the rule acted).
- 0 of the 80 pairs had a different winner.
- 12 of the 80 pairs ended with different points or a different number of turns.
- On minus off: **+0.0 points**: every one of the 80 on-minus-off differences was exactly 0, so no spread can be estimated from them (this refers to the 80 paired games played with the Tool tie-break on and off).
- For context, kx3 minus km3 on the same deals: with the Tool tie-break on +6.2 points (probably between -1.9 and +14.4 points), off +6.2 points (probably between -1.9 and +14.4 points); each range refers to the 80 paired games.

What this can tell and cannot tell: it can tell what the rule did on these 80 paired games (15 had a changed decision, 0 a changed winner), and it can put a bound on how often it changes a winner: no winner changed in 80 pairs, so the share of deals whose winner the rule changes is probably no more than about 4.6 in 100 (95% Wilson bound on 0 of 80). It cannot tell what the rule does on other deals or other decks (gate 3 pooled 400 paired games, 400 kx3 games with the rule on against the same deals with it off, over 5 decks on its own page), and a rule that acts in 15 of 80 games but changes no winner has not been shown to be harmless or useful: whether it would ever change a result on a deck like this is a question for more deals.

## Where these games come from

- Development run: `rl/results/strength_2026-10-03_kx3_dev`; stage dev; pilot `kx3` against `km3`; program `/home/dacz8976/kx/strength` sha256 `5a8f5c83a791`; manifest sha256 `3c8bac353ca09a23` (matches manifest.sha256); registered 2026-10-03T03:18:14Z, first 03-wailord-indeedee-wall game started 2026-10-03T07:35:41Z (registered before the first of this deck's games); games.jsonl sha256 `d423c96eb831`; only deck 03-wailord-indeedee-wall was read (160 games).
- Gate 3 of the Tool tie-break: `rl/results/strength_2026-10-06_kx3_tools_gate3`; stage dev; pilot `kx3_r16_c12_z2_real_t0_poolmeta_tools` against `km3`; program `/home/dacz8976/kx/strength_tools` sha256 `cf73b2a4e858`; manifest sha256 `23e7919db085a842` (matches manifest.sha256); registered 2026-10-06T18:18:06Z, first 03-wailord-indeedee-wall game started 2026-10-06T22:42:03Z (registered before the first of this deck's games); games.jsonl sha256 `0ebaee6575ba`; only deck 03-wailord-indeedee-wall was read (160 games).
- The pinned build for fresh reports is `/home/dacz8976/kx/strength` sha256 `5a8f5c83a791` (kx3 (d513e37b)); the development run was played by that build.
- Seeds 24400000000 + p x 10000 + i; the gate-3 run used the same deals.

## What this page does not say

It is not a fresh test: nothing here was played for the question asked, so it cannot show how the deck would do with new deals. It is not the km3 floor check (km3 on both sides, with its own floor line and its own result); the two answer different questions and neither changes the other. It is not a ranking against other decks, it says nothing about decks outside the 8 public lists or about the ladder, and there is no pass or fail line: whether 03-wailord-indeedee-wall is worth playing is a call for the player. The 8 lists count equally, and kx3 is better informed here than it would be against a person, because its opponent is always one of the 8 lists and always plays like the km3 it imagines when it looks ahead.

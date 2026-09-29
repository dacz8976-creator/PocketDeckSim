# Overnight, Sept 28-29: one page for Dustin's morning

Kept by the laptop session ("Project familiarization"), which Dustin put in charge overnight. The Fable session "Recommendations and advice" coordinates, under Dustin's word that it may decide while he is away, except for gates he set in his own words. Updated as things land; the newest entries are at the top of each section.

## Decisions waiting for you

- **The Sleep/Paralysis pull request isn't needed.** Upstream merged the same fix on Sept 27 (PR #379, by another contributor, with tests). So the new set will arrive with it already in, as you wanted, and there's nothing to send (`engine/UPSTREAM.md`).
  - **Your choice:** do you want a different first pull request? A read-only check of which of this week's engine repairs upstream still lacks is running now. Its answer will be here, with a suggestion.
  - Nothing goes out without you.

## What happened

- **Your evening rulings are recorded as your words** (3e30896, 5c0cf04):
  - coverage rows count for the mixed-row veto;
  - what koh's and kt's readings hinge on;
  - clause (d) gates on Rayquaza, with Suicune reported;
  - which brew (08 is the better evidence; note setup speed);
  - the B4b trial (pin at the Garchomp release);
  - the PR goes first;
  - the cloud has no cap, and jobs must not overlap.
- **Your brew pages say what to note per ladder game**: went first or second, the turn of your first main attack, and the opponent's points then.
  - Brew 08: `../floor_brews_2026-09-28/brew-08-entei-rainbow-cave.md`, at the end.
  - The Ladder Log's Note box is enough, e.g. "2nd | Entei T2 | opp 0 pts".
- **koh re-judged under your coverage rule.** Weezing's second list is played worse on its own side (−3.8 ± 1.6), which now counts as harm. The verdict is unchanged: not adopted, kog stays.
  - The Hyper Ray census is beside it: Hyper Ray use on turns it can't knock out goes from 20% (kog3) to 90% (koh3).
- **kt's build is in.** The cloud wrote it (ec7e1a8: kt's presets on kog, touching only the players' code), and the laptop built it at 23:53 UTC.
  - The cloud had read your GO as "start kt's games now" (its amendment 3). Fable ruled that isn't in force: the laptop's run is the run of record, and the cloud's identical runs are a cross-check.
- **kt on kog: your word recorded.** "kt tables: go", then "Yes, all; build now" (main f7defd1).
  - kt's first game waits for koh's B2e read.
  - Rayquaza is clause (d)'s one test, with Suicune reported (your 7 pm word).
- **koh: not adopted, provisional** (087528f; `../koh_2026-09-28/laptop_reading/READING.md`).
  - Real error 14.0 → 12.3, but the accuracy test's interval crosses zero.
  - Altaria is played worse, which counts as a veto.
  - The mechanism check fails fix A's line in Altaria's Swablu/Eevee positions only.
  - Lucario and Vespiquen are repaired, and Rayquaza keeps its gain.
- **The engine switch and screen: done Sept 28** (33f56da): the kog engine is official, and the screen and floor use kog3. The floor's Payback re-check passed (b05a4cd).

## Running now

- koh's B2e held-out rows on the laptop (ETA about 01:20 UTC).
  - Then koh's B2e mixed rows, which complete its coverage record.
  - kt's gate opens once the B2e rows are read, without waiting for the mixed rows (Fable: they can't change kt's base).
- kt's identity checks at its build: the old pilots must replay game for game.
- The cloud: its own kt identity and tables, as a cross-check.
- Sonnet agents:
  - the PR preparation;
  - kt's Dustin-deck A/B and readout-counter scripts;
  - a workflow diagnosing why koh plays Altaria worse, at the lowest priority;
  - the Trainer-pricing registration draft.

## Next

- kt, after the gate:
  - timing;
  - the four tables on the 45 cells;
  - the footprint, committed alone before anything else is read;
  - mixed rows;
  - coverage: B2e, Scizor and the second lists, with mixed rows every time;
  - clause (d) (Rayquaza);
  - the Rayquaza traces;
  - the Dustin-deck A/B (Skarmory included).
- An open-cause diagnosis: Sceptile v Vespiquen (sim about 66 v real about 33).

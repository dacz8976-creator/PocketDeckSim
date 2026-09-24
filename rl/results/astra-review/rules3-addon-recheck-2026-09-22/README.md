# Rules3 add-on repair and benchmark recheck

September 22, 2026. **The rules3 recheck is complete, but a newly reported T2 result requires another engine repair before these become a current Run 5 baseline.**

During the final document check, `rules/05` and `rules/06` were updated with Dustin's T2 result: a last Pokemon earning the third point while being Knocked Out yields a tie. The frozen rules3 code still gives the attacker a win in that situation. All results below remain identified rules3 measurements. The completed checks do not establish correctness against this new evidence, and the Weezing/Lucario candidate can reach it. The newly confirmed case is being reproduced before the next repair; historical benchmark files remain unchanged.

The rebuilt add-on reproduced the suspected error: Reverse Thrust could leave a knockout waiting behind the switch choice, while the forecast claimed zero points and no win. Add-on **0.7.1** repairs that result and keeps genuine player choices explicit. It is built on the active **rules3** engine. No Run 5 build or training was started, and historical runs, checkpoints, wheels and environments were preserved.

This carries out the [recheck request](../RULES2_ADDON_RECHECK_REQUEST_20260922.md) on rules3, which superseded rules2 before this work. The original request is preserved.

## k2 versus k3, first

Fresh rules3 results, using the September 20 pairing design: 1,000 paired seeds per directed matchup, with each pilot deck in each seat 500 times. The opponent remains k3. Each comparison changes only whether the pilot is k2 or k3. The shared k3-versus-k3 baseline required 10,000 games, and the k2 comparisons required another 20,000. Draws count as non-wins.

| Pilot deck | Opponent | k2 wins | k3 wins | Gain from k3 |
|---|---|---:|---:|---:|
| Blaziken | Lucario | 44.3% | 47.4% | 3.1 points |
| Lucario | Blaziken | 44.8% | 52.5% | 7.7 points |
| Blaziken | Weezing | 44.1% | 50.4% | 6.3 points |
| Weezing | Blaziken | 39.3% | 48.8% | 9.5 points |
| Blaziken | Altaria | 37.7% | 43.1% | 5.4 points |
| Altaria | Blaziken | 53.4% | 56.8% | 3.4 points |
| Blaziken | Suicune | 46.0% | 54.3% | 8.3 points |
| Suicune | Blaziken | 38.2% | 45.6% | 7.4 points |
| Lucario | Weezing | 45.3% | 53.1% | 7.8 points |
| Weezing | Lucario | 36.8% | 46.9% | 10.1 points |
| Lucario | Altaria | 41.0% | 44.9% | 3.9 points |
| Altaria | Lucario | 52.8% | 55.1% | 2.3 points |
| Lucario | Suicune | 44.0% | 52.7% | 8.7 points |
| Suicune | Lucario | 42.0% | 47.3% | 5.3 points |
| Weezing | Altaria | 52.0% | 60.6% | 8.6 points |
| Altaria | Weezing | 30.7% | 38.7% | 8.0 points |
| Weezing | Suicune | 18.9% | 38.0% | 19.1 points |
| Suicune | Weezing | 42.7% | 61.8% | 19.1 points |
| Altaria | Suicune | 31.9% | 37.1% | 5.2 points |
| Suicune | Altaria | 54.9% | 62.9% | 8.0 points |

The measured k3 win rate exceeded k2 in every direction. These are search-depth comparisons within the simulator, not deck rankings or proof that a learned evaluator can beat k3. Paired discordant counts and unadjusted exact McNemar p-values are in the [full table](benchmarks/pool/summary.md), with [raw games](benchmarks/pool/games.jsonl), [identity](benchmarks/pool/identity.json), and the [frozen task plan](benchmarks/pool/plan.json). The exploratory table has 20 comparisons.

**Provisional candidate for the one-matchup Run 5 design: Weezing piloted against Lucario.** It is close to even under k3 (46.9%) and shows a 10.1-point search-depth gain over k2. The opposite direction is 53.1% under k3 versus 45.3% under k2. Weezing versus Suicune has the largest gain (19.1 points in both directions), but its k3 baseline is less even (38.0%/61.8%). The chosen-pair checks below use the exact frozen Weezing and Lucario lists. This is a test candidate, not a launch decision or a recommendation about ladder strength.

## k3 mirror baseline

The original brew-03a mirror protocol was repeated with 1,000 distinct seeds, alternating which seat is evaluated. Each seat has 500 different games; these two win rates are not complementary counts from the same games.

| Evaluated seat | Wins | Losses | Draws | Win rate |
|---|---:|---:|---:|---:|
| 0 | 255 | 238 | 7 | 51.0% |
| 1 | 266 | 227 | 7 | 53.2% |

Draws are non-wins. The old 45% floor was a prior experiment criterion; this recheck does not set a new Run 5 success criterion. [Mirror evidence](benchmarks/mirror/summary.json).

## Full k3 screen

The full screen completed **16,800 games** across the original 21 local deck names and eight research opponents. All 168 matchups have 100 games, split 50 per evaluated seat; there were 21 draws in total. **51 matchups fall in the original 35–65% win-rate band.** At 100 games per matchup, this is a coarse screen, roughly plus or minus 10 percentage points near 50%, not a deck ranking. The screen supplies alternatives; the candidate above stays tied to the stronger 1,000-seed paired measurement and the completed add-on checks.

[Complete screen table](benchmarks/screen/summary.md), [CSV with seat counts](benchmarks/screen/screen.csv), [matchups in the 35–65% band](benchmarks/screen/even-matchups.json), [identity](benchmarks/screen/identity.json), and [completion validation](completion-validation.json). Current deck bytes are frozen and hashed. The historical screen did not record deck-byte hashes, so matching the old names is not proof that every list is byte-identical to its historical version.

## What the repair changes

Before reading the result of a forecast, 0.7.1 completes public, single-option steps while one of the five new rule-resolution frames remains. That includes a one-option switch above the retaliation frame. It stops after those frames finish, before unrelated later play. A real choice or hidden continuation leaves the forecast visibly unpriced; the move is still offered to the player.

| Focused case | Before | After |
|---|---|---|
| Reverse Thrust earns the third point, one Benched Pokemon | Priced as zero points and no win | One point and a certain win |
| Same attack, two Benched Pokemon | Priced as zero points and no win | Attack row unpriced until the player chooses; either switch row correctly shows the point and win |
| End turn with one Glimmora point-denial coin | Baseline not separately measured in this fixture | Correct two-outcome fixture: half a point expected and 50% win chance |
| End-turn evolution from a known own deck | Baseline not separately measured in this fixture | Public forced continuation priced |
| Evolution involving an unknown opponent card | Hidden continuation | Explicitly unpriced, preserving hidden information |

Six focused final Rust tests passed: one Reverse Thrust test, three continuation tests and two direct encoding tests. The Energy-discard choices and `ChooseRandomEvolutionTarget` appear as distinct legal encoded alternatives. A known-own-deck evolution target can be priced; an unseen evolution card is correctly refused as a forecast, without removing the legal target choice. [Source, logs and rebuild instructions](addon/README.md).

## Chosen-pair replay and hidden-card checks

- **100/100 k3 replays matched**, over 50 distinct seeds and both recorded seats. All 1,919 decision fingerprints matched the ordered legal moves, full referee state and player observation; final states and outcomes matched too. Switching the opponent to k2 matched only 12/100, showing the check can detect changed play.
- **4,665 hidden-card probes passed**, across 50 random games and 50 games with one k3 opponent. Opponent hand/deck reshuffles and own deck-order reshuffles changed neither observations/action features nor legal moves. Deck order and controlled seat were crossed in the one-k3 sample.
- The visible-own-hand positive control changed observations/features on all 3,578 applicable probes; 1,087 were inapplicable because the visible hand did not change. Legal moves changed on 3,120 of 4,665 control probes; some visible hand changes legitimately preserve the move list.
- Twelve additional games matched the actual rules3 executable on winner, points and turn count, for both the rebuilt and final add-ons.

[C1/C2 evidence](checks/weezing-lucario-interface-071/summary.json), [final executable comparison](benchmarks/cli-addon-parity-071.json).

## v2.2 checks, including skips

Twenty fixed-seed random games produced 9,285 offered move rows in each version. Every offered action was examined; eligible loss flags were compared with four sampled chance streams. The main games were never restored during probes, so their chance streams stayed unchanged. This extends the older check, which sampled only the first six moves and actually used one chance stream.

| Check or skip reason | Rebuilt 0.7.0 | Repaired 0.7.1 |
|---|---:|---:|
| Layout consistency checks passed (v2.1/v2.2) | 9,285 | 9,285 |
| In-play counts checked, no errors | 8,721 | 8,625 |
| Count checks skipped for own-side damage | 34 | 34 |
| Loss flags checked, no errors | 6,858 | 6,858 |
| Unpriced, skipped in both count and flag tests | 530 | 626 |
| Flag skipped: follow-up choice | 950 | 854 |
| Flag skipped: Active name changed | 854 | 854 |
| Flag skipped: game ended | 93 | 93 |
| Flag skipped: sampled chance variation or mixed boundaries | 0 | 0 |

The 626 unpriced rows now have explicit reasons: 521 depend on unrevealed opponent cards, nine are concealed setup handoffs, and **96 are attacks with genuine two- or three-way follow-up choices**. Those 96 are no longer presented as settled answers. For attack rows, the final flag check examined 305, skipped 96 as unpriced, 182 for follow-up choices, five for an Active-name change, and 29 for game end. End turn had 1,472 checked, nine concealed-setup refusals, 16 follow-up skips, one Active-name change and 34 game-end skips. Every action-type breakdown is in the [final summary](checks/weezing-lucario-v22-071/summary.json).

The full before/after comparison found **5,541/5,541 unaffected rows byte-identical**. A conservative decision-wide trace excludes any decision whose direct or nested threat lookahead encountered a new rule frame. Across all decisions, 8,816 rows were identical and 469 changed; 224 observation threat-feature blocks changed. The action encoding prefixes and the main-game records stayed identical. [Comparison evidence](checks/feature-comparison.json).

Passing count/loss-flag checks does not prove every point, win or chance forecast. Terminal and pending-choice skips remain visible; the focused fixtures separately establish the repaired scoring. Active changes are detected by name, so same-name swaps are not classified as name changes. Capped forecast branches remain approximations when truncation occurs; the one-coin fixture fits inside the cap.

## Candidate rules exposure

On the exact Weezing and Lucario lists, delayed case 1 is reachable through Koffing and the runtime fault was reproduced. The named point-denial and end-of-opponent-turn evolution cases are absent from both lists. Their focused tests qualify the repair beyond this pair, but do not establish how often such states occur in games.

The pair can reach **#2** (Hoopa ex taking the third point while its last Pokemon is also Knocked Out), which was open when this static audit ran but is now reported settled by Dustin's T2 test as a tie. Rules3 still gives a win; this is a newly confirmed engine defect. **#22** (turn-30 Checkup) and **#24** (random search weighting over cards versus names) remain open. The frozen reachability report below records the earlier state of evidence. The pair does not reach the two-Active Checkup promotion question, Heavy Helmet with modified Retreat Cost, or Stadium replacement ownership. Neither deck uses Gouging Fire or Walking Wake, and both declare one Energy type, so the new typed Energy-payment choices are absent here. [Full static reachability report and hashes](reachability/reachability.md).

## Saved identities and remaining work

- Active engine: `0.1.0-pdl.rules3`, executable SHA-256 `66acb493724ec189300ddaae6bd61de9a175d07677ad3df23da36414a3a922f2`. All 544 recorded engine source files and the executable remain unchanged by this add-on task. [Verification](engine-unchanged.json).
- Benchmarks use the frozen 0.7.0 rebuild, whose engine loop is unchanged by the 0.7.1 feature repair. New learner-facing checks use 0.7.1. Both use the same recorded rules3 engine source. This avoids mixing the old unified1 results into new measurements.
- Final 0.7.1 wheel: `addon/wheels/pdl_rl_env-0.7.1-cp38-abi3-linux_x86_64.whl`, SHA-256 `b4fddfa482f98c1269855c643686d8cd4f994010d508fd70690292a277d4f3c7`. Compiled module SHA-256 `46e7b29fcb188326dcd0b6a2c99113c91bb0ebc70e9ab2dc78df7b933ad1df9a`.
- The original wheel packaging incorrectly claimed manylinux 2.34 compatibility despite requiring GLIBC 2.39. Corrected Linux-specific wheels preserve the exact tested binaries; the originals remain as superseded evidence. The new final environment is `/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071-linux/venv/bin/python`. [Packaging validation](packaging-validation.json).
- The v2.1/v2.2 layouts retain their names and dimensions, but forecast content changed. Any future experiment must identify 0.7.1 explicitly and use a fresh result identity. These reused benchmark seeds are a historical protocol replication, not a fresh future training holdout.
- No Run 5 training, model/search integration build, checkpoint change or launch occurred. The short Run 5 design page, fixed budget and success/speed criteria remain future work. Open in-game questions are not settled by these checks.

Updated `START_HERE.md`, the current status and next-steps paragraphs in `FEASIBILITY.md`, and `LOG.md`. The stale damage-order sentence in `RULES_FOR_AGENTS.md` was also corrected. Original documents are preserved here, and writes were guarded against concurrent changes. Historical results and the original request remain unchanged.

# Rules4 add-on and benchmark recheck

September 22, 2026. **In progress: rules4 is active, add-on 0.7.2 is built, and the chosen-pair checks pass. The complete benchmark refresh is still running.** No Run 5 training or model/search integration build has started.

The [original request](../RULES2_ADDON_RECHECK_REQUEST_20260922.md) was completed on rules3 before the new T2 evidence arrived. The [rules3 packet](../rules3-addon-recheck-2026-09-22/README.md) preserves those results and the demonstrated deferred-KO forecast bug. Rules4 repairs the newly confirmed simultaneous-finish tie, so this separate packet refreshes the engine-dependent measurements rather than relabeling the old results.

## k2 versus k3, first

The full **30,000-game** pool comparison completed first: 1,000 paired seeds per directed matchup, each pilot in each seat 500 times, with the opponent held at k3. There are 10,000 shared k3-versus-k3 baseline games and 20,000 k2 comparison games. The exact five Run 4 lists, policies and seed protocol are unchanged; draws count as non-wins. All identified inputs stayed unchanged during the run.

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

The aggregate table is unchanged from the frozen rules3 measurement. k3 has a higher observed win rate in all twenty directions, but these exploratory paired comparisons are not twenty independent confirmations of significance, a deck ranking, or evidence that a learned evaluator can beat k3. The saved [table](benchmarks/pool/summary.md) includes paired discordant counts and unadjusted exact McNemar p-values. [Raw games](benchmarks/pool/games.jsonl), [frozen plan](benchmarks/pool/plan.json), [identity](benchmarks/pool/identity.json).

**Provisional one-matchup candidate: Weezing piloted against Lucario.** Its k3 result is near even (46.9%) with a 10.1-point gain over k2 (36.8%). The reverse direction is 53.1% under k3 and 45.3% under k2. Weezing/Suicune has the larger 19.1-point gain in both directions, but a less even 38.0%/61.8% k3 baseline. This is a test candidate; it does not authorize Run 5.

## k3 mirror baseline

The brew-03a mirror completed **1,000 games**, using distinct seeds and alternating the evaluated seat. Each seat has 500 different games, so the win rates are not complementary counts of the same games. Draws count as non-wins.

| Evaluated seat | Wins | Losses | Draws | Win rate |
|---|---:|---:|---:|---:|
| 0 | 255 | 238 | 7 | 51.0% |
| 1 | 266 | 227 | 7 | 53.2% |

These results match the frozen rules3 mirror. The historical 45% floor is not a new Run 5 success criterion. [Mirror records and identity](benchmarks/mirror/summary.json).

## Full k3 screen

The full 16,800-game screen is still running. These reused seeds replicate a historical benchmark protocol; they are not a future policy-training holdout.

## Engine and add-on

Rules4 is `0.1.0-pdl.rules4`, with executable SHA-256 `e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415`. It passed 1,826 engine tests and 44 accepted-review segments, then the normal project launcher smoke. [Repair and T2 evidence](../../../../rules4-t2-repair-2026-09-22/README.md).

Add-on **0.7.2** uses the verified 545-file rules4 source snapshot. Its forecast implementation is byte-identical to repaired 0.7.1; the additional test confirms the T2 tie is priced correctly in both seats, with the two point awards retained and zero win/loss probability. The wheel and source snapshots are in the [add-on packet](../../../../rules4-t2-repair-2026-09-22/addon/README.md). The generic Linux wheel preserves the checked compiled module and makes no manylinux compatibility claim.

The original forecast repair remains necessary: Reverse Thrust can postpone scoring behind a player switch. Public single-option rule steps are now followed before reading the forecast; genuine choices and hidden continuations remain explicitly unpriced. The prior before/after test proved 5,541 unaffected rows unchanged during that repair. Its [comparison evidence](../rules3-addon-recheck-2026-09-22/checks/feature-comparison.json) remains identified to rules3/0.7.0 versus 0.7.1.

## Chosen-pair checks

The refreshed table retains Weezing piloted against Lucario as the provisional candidate. These checks use those exact frozen lists:

- **100/100 k3 replays matched**, covering 50 distinct seeds and both recorded seats. All 1,919 decision fingerprints and final outcomes matched. The k2-opponent negative control matched only 12/100.
- **4,665 hidden-card probes passed** across 50 random and 50 one-k3 games. Opponent hidden-card changes and own deck-order reshuffles preserved observations, action features and legal moves. The own-hand control changed observations/features in all 3,578 applicable probes; 1,087 were inapplicable. Legal moves changed in 3,120 control probes and stayed the same in 1,545.
- **12/12 actual-executable comparisons matched** winner, points and turn count, with engine/module/deck identities unchanged.

[C1/C2 results](checks/weezing-lucario-interface-072/summary.json), [actual executable comparison](benchmarks/cli-addon-parity-072/summary.json).

## Forecast checks and skips

The twenty fixed-seed games offered **9,285 action rows** over 1,723 decisions. Every offered row was considered; eligible loss flags were checked with four sampled chance streams. All layout checks passed, with zero errors among the count and loss-flag rows that could be checked.

| Result or skip reason | Rows |
|---|---:|
| In-play count checked | 8,625 |
| Count skipped for own-side damage | 34 |
| Loss flag checked | 6,858 |
| Unpriced, skipped by both checks | 626 |
| Loss flag skipped: follow-up choice | 854 |
| Loss flag skipped: Active name changed | 854 |
| Loss flag skipped: game ended | 93 |
| Loss flag skipped: sampled chance variation or mixed boundaries | 0 |

The 626 unpriced rows comprise 521 unrevealed-opponent-card dependencies, nine concealed setup handoffs, and 96 attacks needing a real follow-up choice (39 two-way and 57 three-way). Attack loss flags: 305 checked, 96 unpriced, 182 pending-choice skips, five Active-name changes and 29 terminal skips. End turn: 1,472 checked, nine unpriced, 16 pending-choice skips, one Active-name change and 34 terminal skips. [Full breakdown](checks/weezing-lucario-v22-072/summary.json).

The saved 0.7.1 and 0.7.2 captures have **all 9,285 feature rows and all 1,723 observations byte-identical**, with the same recorded states, actions and legal lists. This sample does not exercise T2; its outcome is checked by the separate focused fixture. [Capture comparison](checks/rules3-071-vs-rules4-072-features.json).

Passing these sampled count/loss-flag checks does not prove every point or chance forecast. Pending and terminal rows remain visible skips; focused fixtures separately cover scoring. Active swaps are classified by card name, so same-name swaps are not distinguished. Capped chance branches remain approximations when truncation occurs.

## Candidate rules exposure and remaining work

Weezing/Lucario reaches the deferred Reverse Thrust case. Neither list reaches the named point-denial or end-of-opponent-turn evolution cases, which have separate focused fixtures. Hoopa ex can reach the narrow T2 terminal shape; rules4 now handles it. The same self-damage also reaches untested simultaneous-finish variants: if Hoopa's opponent begins on one point, the two knockouts can leave both players at three with only the opponent still having Pokemon. Rules4 retains its previous tie behavior there; the broader community model predicts an opponent win and is not established by T2. Turn-30 Checkup (#22) and random-search weighting (#24) remain open. The pair does not reach Heavy Helmet with modified Retreat Cost or two-Active Checkup promotion order. Both decks use one Energy type and omit Gouging Fire/Walking Wake, so those typed-payment choices are absent here. [Exact lists, hashes and full reachability](reachability/reachability.md).

The add-on's five focused integration tests and two direct choice-encoding unit tests passed. The latter confirm distinct legal Energy-discard and random-evolution targets; unknown-card forecasts remain explicitly unpriced. Remaining in this packet: complete and validate the pool, mirror and screen, then finish updating the current project entry points. Historical runs, checkpoints, environments and result packets remain preserved. The short Run 5 design page and fixed budget/success/speed criteria remain future work.

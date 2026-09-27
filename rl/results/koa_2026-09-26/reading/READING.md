# koa's reading (Sept 27): passes the reserve route

The official engine is main-83e17ae. The registration is `../../opening_active_census_2026-09-26/REGISTRATION.md` with amendments 1 and 2.

**Decision order, as it happened:**
1. The footprint was read first and committed alone (8e6375b), which fixed the route.
2. Clauses (b) to (e) and the held-out check were read next (`READING_numbers.txt`, from `read_koa.py`).
3. This verdict was written before the kob/kor diagnostic rows beyond Altaria were read.
4. No koa number uses a kob or kor file.

**Two independent second readers** re-derived every number from the raw files and checked the reading against the registration clause by clause (`second_read_scratch/`). Both agree with every number.

## In plain words

- **What koa changes:** Altaria's opening Active only.
  - Where the hand holds Eevee with Espeon available, it starts Eevee instead of Darkrai (519 games) or Swablu (329).
  - Nothing else changes, in any deck, in any game.
- **Footprint: 6.06% of the table's games** (848 of 14,000; predicted 6.0%). That is under the 15% trigger, so the reserve route (no harm plus a real gain) applies instead of the ordinary rule.
- **No harm:**
  - The accuracy margin (kp3 minus koa) is −0.01, 90% interval −0.32 to +0.31. The limit is −1.0.
  - No cell or deck veto.
  - No held-out archetype moves more than 0.7 points further from its real results.
- **Real gain:** Altaria's own side gains +2.84 ± 0.99 points pooled over its seven matchups. The opponents' side is exactly unchanged: 3,500 of 3,500 games identical to kp3's.
- **So koa passes.** By clause (e), it becomes the working pilot for the table and the screen together.
  - It stays **"unconfirmed"**: confirmation needs size as well as direction, and a no-harm candidate with a margin near zero can't show size by design (registration section 7, "Confirmation").
  - How no-harm candidates are confirmed is Dustin's plan question, and kt has the same gap. The registration's proposal: re-read (b) on post-freeze cells with the same −1.0 bound, and report Altaria's seven post-freeze cells.
- **Before it actually becomes the pilot, Dustin decides:**
  1. **koa and kpg together** (see below).
  2. **28 or 45 cells.** The registered test is the 28 table cells. koa3 on the 17 new cells is queued as a reported-beside run, since koa touches the two where the panel's Altaria is the opponent. Dustin can rule that the 45-cell view counts.

## The clauses (reserve route, as fixed in the review record's line 130)

| Clause | Registered test | Result |
|---|---|---|
| (a) | footprint under 15% | 6.06% (registered 790-890 games; 848) |
| (b) | τ̂ margin 90% lower bound ≥ −1.0; no veto counts under rule v2 | −0.01 (−0.32 to +0.31); 27-cell set −0.31 to +0.30; no veto |
| (c) | no meta deck's own side worse beyond paired noise | Altaria +2.84 ± 0.99, no row negative. Opponents' rows identical 3,500/3,500. The 21 non-Altaria pairings are identical 10,500/10,500 |
| (d) | own-side gain beyond paired noise on a non-Dustin top-30 archetype with the card (Mega Altaria ex Espeon, Dustin's ruling) | +2.84 ± 0.99 (z 5.7) |
| (e) | adoption for the screen and the table together | subject to the two rulings above |

- **Section 8's refutation checks, all passed:**
  - **Leaks:** none in the table, the mixed rows or B2e. No changed game has both openings unchanged.
  - **Altaria's changed share:** 24.23%, inside the registered 22.6-25.4%.
  - **Other decks' openings:** none changed.
  - **Transitions:** Darkrai→Eevee 14.83% (registered 14.5) and Swablu→Eevee 9.40% (registered 9.5), with no new transition.
  - **Altaria v Lucario:** +2.00 ± 2.54. Not below zero, so not a refutation, but under the B2c point prediction of +5.5.
- **Altaria's seven Limitless cells**, reported and not gated (v2 development half):

  | Altaria v | kp3 → koa3 | Limitless |
  |---|---|---|
  | Blaziken | 58.0 → 59.2 | 76.5 |
  | Hydreigon | 47.2 → 49.8 | 54.5 |
  | Lucario | 62.0 → 64.0 | 72.4 |
  | Sceptile (quarantined) | 43.6 → 48.0 | 45.4 |
  | Suicune | 48.4 → 50.8 | 56.2 |
  | Vespiquen | 47.4 → 52.0 | 37.6 |
  | Weezing | 37.6 → 40.3 | 33.0 |

  - Four cells move toward Limitless and three away.
  - Vespiquen and Weezing move further, which section 6 foresaw as investigation items. Sceptile, which is quarantined, overshoots by 0.9.
  - The "before" figures are the repaired engine's. They differ from the registration's printed 7fc6ccb table, most in Weezing (40.4 before the repairs).
- **Section 4 on a new engine:**
  - kp3's references were regenerated: kpf's runs equal the official build's replay, 14,000/14,000.
  - The games that differ from 7fc6ccb were shown to reach the repaired mechanics (`../../engine_switch_2026-09-26/`, under Dustin's Sept 27 lookahead rule).
  - Scoreboard v2's kp3 row was re-scored as scoreboard v3: 8.4 → 8.7.
  - koa3 at the official build replays the cloud's koa3 at 9af40c8, 1,120 of 1,120.
- **Development data:** Altaria v Lucario is the B2c cell that produced koa's hypothesis. It is re-read here on new deals.

## Dustin's rulings (Sept 27, after this reading)

1. **Combine them:** "One pilot, kp3 plus koa's opening plus kpg's discard credit."
   - It is a composition check of two components already read, not a new candidate: the combined code's identity checks and one table, showing no veto and accuracy no worse than the better component alone. Each component keeps its own verdict, and the combined pilot inherits both.
   - It runs once kpg's held-out check is in.
2. **"Twenty-eight for the verdict, forty-five for no-harm."**
   - koa's adoption verdict stands on the 28 cells it was registered on.
   - Its two new cells (Rayquaza v Altaria, Altaria/Greninja v Altaria) count for no harm only: a veto in either blocks the takeover, and a gain is reported, not credited.
   - From Sept 27 every candidate is registered on 45 cells.
3. **Confirmation:** re-checking no harm on post-Sept-24 events is the standing rule for reserve-route fixes (RUN5 "Rules").
4. **For the record:** "Altaria's scores all rising pushes Vespiquen and Weezing past their real cells. That isn't koa's fault — the fix is correct about the opening — but it means those two cells' remaining error now has one less explanation available." They are on RUN5's open-causes list beside Sceptile v Vespiquen.

## koa and kpg (the question as it stood before the ruling)

- **The conflict:** koa's "both pass separately" sentence names only kt, and kpg's registration says kpg becomes the pilot once confirmed without mentioning koa. The two texts conflict if both pass.
- **What koa's own "one pilot" principle implies:** the combined code (kp3, plus koa's switch A, plus kpg's discard credit) gets section 4's identity checks and one table before it becomes the pilot.
- **For Dustin to rule on,** written down before either becomes the pilot:
  - (i) whether the combined kp3 + A + F is the target;
  - (ii) the order.
- If koa becomes the working pilot first, later candidates need koa3 baselines on all 45 cells.

## Reported beside (Sept 27, after the verdict and the rulings; `extras_numbers.txt`, from `read_koa_extras.py`)

All at the official engine, each against kp3 on the same deals.

- **The 17 new cells: no harm, so the takeover is not blocked** (Dustin's "forty-five for no-harm").
  - Only koa's two cells change (128 and 126 games); the other 15 are identical, 7,500 of 7,500 games.
  - Rayquaza v Altaria 35.4 → 34.4 (real 47.1 ± 10.5; miss +1.0). Altaria/Greninja v Altaria 41.2 → 39.4 (real 37.5 ± 11.5; miss −1.8). Neither is near the 6-point cell veto.
  - The 45-cell view (`score45_koa3_vs_kp3.txt`): real error 15.5 for both; margin −0.01, 90% interval −0.15 to +0.12 (limit −1.0); no cell or deck veto.
- **Dustin's six B2e files** (pairings 48-95, reported only): every file's overall score moves by under 1 point (110-127 games changed of 4,000 each). Each file does 2.6 to 6.2 points worse against Altaria, the expected side effect of a better Altaria opening.
- **The variant-list check (section 7 (d)): up, as predicted.** LaNora's Altaria list gains **+3.67 ± 0.82** on its own side, pooled over its 8 rows. All 8 rows are positive, +2.0 to +5.0 each, including against the table's own Altaria list (+2.4 ± 2.3, amendment 2's block). The fix's gain carries to a second real Altaria list.
- **Diagnostics (attribution only; kob and kor stay unregistered):**
  - **Suicune under kor: −3.33 ± 0.92, down beyond noise, as section 6 predicted** (Suicune ex moved off the Active forgoes Legendary Pulse). All seven rows are negative. By the registration's own wording (section 7) this "names the Darkrai half". Plainly, it shows R's setup-readiness rule costs a deck whose Active only works in front, as the class table said. The class table isn't put in doubt.
  - **Hydreigon under kob: −0.23 ± 0.46, flat.** Section 6 predicted up (Deino opening instead of Bombirdier); the cap was about ±2.0. The Bench-only half of B shows nothing measurable.
  - **Vespiquen and Weezing** (no direction predicted): +0.39 ± 0.74 and +0.44 ± 0.46, within noise, and the same under kob and kor, which make the same changes on those decks.
  - **Identity decks: complete.** Wherever kob or kor sits on a deck its switch doesn't touch, every game equals kp3's (6,000 of 6,000 for each code).
  - Earlier: their Altaria rows are the same 3,500 games for both codes (+1.29 ± 0.98). koa minus kob on Altaria is +1.56 ± 0.95, against the prediction "equal within noise". That is a diagnostic finding only.
  - Nothing more is registered. Any later B or R candidate is a new registration (section 7).
- **For information** (the second reader): the engine switch changed 10,093 of kp3's 24,000 B2e archetype games, including 3,767 of 4,000 in Charizard Y/Entei, where Legendary Pulse fires. B2e has no mechanic check; RUN5 requires one on the table only. Both sides here are on the same engine.

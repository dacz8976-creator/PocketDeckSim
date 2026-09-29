# kt's reading on kog (Sept 29): **not adopted, as registered**. kta3 passed every one of its own tests.

**What was read:** kt's registration on kog, which is amendment 2 of `../kt_2026-09-26/README.md` (on the cloud branch) over the original text. Amendment 3 is not in force. The reading is under Dustin's rulings recorded in `README.md`.
- **Code:** `read_kt.py`, committed at b33a96c before any kt result except the footprint was read. The footprint was committed alone at 6c900fd, as the plan requires. The code was written blind, reviewed twice, and run unchanged.
- **Numbers:** `READING_numbers.txt`, with score45's full pages in `score45_<code>_vs_kog3.txt`.
- **Build and replays:** everything was played by the kt build ec7e1a8. Its 13 identity replays all match game for game, and the timing check passed (0.91×).
- **Two readers:** the laptop is the first. An independent second reader (a Sonnet agent with its own code, which compared only after computing) agrees on every number and both verdicts, with 0 disagreements. An outcome auditor checked the verdict against the registration text (both in `second_reader/`).

## In plain words

- **The footprint fixed the routes:**
  - kt3, all three switches: 64.7% of games differ, so the ordinary adoption rule.
  - kta3, switch 1 alone (the Tool cut): 2.5%, so the reserve route.
- **kt3 fails the ordinary rule.**
  - Real error goes 14.0 → 14.1. ΔMSE is +1.0, 95% interval −16.7 to +18.9, not below zero. That alone decides it.
  - Under Dustin's coverage rule it also plays these own sides worse:
    - three of B2e's held-out decks: Manectric −1.1, Hoopa / Absol −1.1, Garchomp −0.8;
    - two second lists: Weezing −0.7 ± 0.6, Charizard Y −1.7 ± 0.9.
  - Under the older literal wording (harm and more than 2 further) none of these would count. The verdict doesn't depend on it.
  - **The scoreboard points at switch 2, but not beyond noise.** ktb3 alone: real error 14.3, τ margin −0.30, 90% interval −0.75 to +0.23. ktc3 leaves it at 14.0.
  - The coverage harms can't be attributed to a switch: ktb3 and ktc3 have no coverage rows.
- **kta3 passes every test on its route:**
  - (a) footprint 2.5%;
  - (b) τ margin +0.21, 90% interval +0.06 to +0.31, where the rule asks for −1.0 or above. Real error goes 14.0 → 13.8. No veto counts;
  - (c) no meta deck's own side is worse beyond noise. The lowest is Blaziken, −0.15 ± 0.29;
  - (d) the census Rayquaza list's own side gains +1.00 ± 0.39 over its eight rows (52 games better, 12 worse). The Vespiquen row, +3.8, supplies about half of it; without that row the gain is about +0.6;
  - coverage: no harm. But kta3 barely touches most coverage rows. It differs from kog3 in 28 of 48,000 B2e games and in almost none on the second lists. The Scizor row (980 of 4,000 games differ) is the one informative coverage test, and it shows no harm (+0.11 ± 0.61).
- **The outcome the registration fixed before any game** (line 404): "kt3 fails: nothing adopted. The diagnostic codes are read for attribution only, and the next candidate is registered afresh."
  - Amendment 2 doesn't change the outcomes. Its only overrides (lines 400 and 403) don't cover this case.
  - The "nothing adopted" is final, because both codes were read on every coverage row (line 152).
  - **kt is not adopted, and kog stays the working pilot.**
- **Reported beside, gating nothing:**
  - Suicune's own side under kta3 is −0.00 ± 0.25 over its nine rows: no direction.
  - Hydreigon's deck gap goes 7.3 → 9.0 under kt3 and 7.3 → 7.1 under kta3.
  - The power line: kt3's reading could detect a ΔMSE of about −18 half the time.
- **Caution:** score45's own page for kta3 (`score45_kta3_vs_kog3.txt`) prints "ADOPTION RULE (v2): adopt", with ΔMSE −5.9 (−11.0 to −1.4). That is the ordinary rule's view of a code whose footprint put it on the reserve route. It is not a test of kta3 and must not be quoted as an adoption.

## Which condition carried kta3's verdict (Dustin, Sept 29: a column, not a rule)

| Condition | kta3's result | How informative |
|---|---|---|
| (a) footprint under 15% | 2.5% (559 of 22,500 games) | fixes the route |
| (b) no harm on the 45 cells | τ margin +0.21 (90% +0.06 to +0.31); no veto | **little**: with 2.5% of games changed, no harm is nearly automatic |
| (c) no meta deck worse | none worse beyond noise; 17 of 45 cells changed at all | **little**, for the same reason |
| coverage | no harm; but kta3 differs from kog3 in only 28 of 48,000 B2e games and almost none on the second lists. Scizor (980 of 4,000 differ) is the one real test | **little**, except Scizor |
| **(d) the gain on the pre-named deck** | **Rayquaza's own side +1.00 ± 0.39**, 52 games better and 12 worse | **informative**, but see the breakdown below |
| **the behavioural footprint** (the A/B's counters) | **Jasmine played on 30.2% of the turns she was offered** (1,711 of 5,669), against kog3's 0.4%. Barrier / Apron / Helmet placement barely changes. | **informative**: the mechanism acted |

**Clause (d) by cell** (kta3 on the census Rayquaza list v kog3 on it, 500 deals each, paired; kog3 → kta3; each cell ±95%):

| v | kog3 | kta3 | Change |
|---|---:|---:|---|
| Altaria | 37.6 | 37.6 | +0.0 ± 0.0 |
| Blaziken | 33.4 | 33.6 | +0.2 ± 0.4 |
| Hydreigon | 29.6 | 30.6 | +1.0 ± 1.2 |
| Lucario | 41.0 | 41.2 | +0.2 ± 0.7 |
| Sceptile | 18.8 | 19.8 | +1.0 ± 1.2 |
| Suicune | 26.6 | 28.0 | +1.4 ± 1.0 |
| **Vespiquen** | 25.6 | 29.4 | **+3.8 ± 2.0** |
| Weezing | 13.6 | 14.0 | +0.4 ± 1.1 |
| **pooled** | | | **+1.00 ± 0.39** |

- Vespiquen supplies about half the pooled gain; without it the pooled gain is about +0.6.
- Every other cell is 0 or small and positive. It is a gain spread thinly, with one cell carrying half, not one cell alone.

## The Dustin-deck A/B (read Sept 29; reported, gating nothing; `ec7e1a8_ab_table.txt`)

1,920 games per deck and arm, paired with kog3 on the same deals, kog3 on the panel in every arm.

| Deck | kt3 v kog3 | kta3 v kog3 |
|---|---|---|
| **07 (Skarmory)** | +7.2 (+5.2 to +9.2) | **+8.5 (+6.7 to +10.4)** |
| 05 | +0.2 (−1.4 to +1.7) | +1.8 (+0.9 to +2.6) |
| 11 | +0.2 | +0.1 |
| 01 | −0.1 | −0.2 |
| 03 | **−2.1 (−3.9 to −0.4)** | +0.7 (−0.7 to +2.1) |
| all five | +1.1 (+0.4 to +1.7) | **+2.2 (+1.6 to +2.7)** |

- **Deck 07's footprint:** Jasmine rises from 0.4% of offered turns (kog3) to 30.2% (kta3) and 28.8% (kt3).
- **Metal Core Barrier on a qualifying ([M]) holder:** kog3 80%, kta3 79%, kt3 97%. So it's kt3, with switches 2 and 3, that stops Barrier going on a non-[M] holder like Indeedee. kta3 doesn't change it.
- **kt3 costs deck 03** (−2.1 beyond noise, with Heavy Helmet's use falling from 69% to 43%). kta3 doesn't.

## What this leaves for Dustin

- **His hinge, verbatim:** "kt is the Tool fix on the reserve route: the 15 percent trigger read first, no-harm with the −1.0 lower bound, no deck hurt, and the real gain shown ... If the readings show those, the verdicts write themselves; if they show something else, that's the morning conversation."
  - The trigger, read first, put kt3 (kt as registered) on the ordinary rule. Only kta3 landed on the reserve route. So the readings "show something else", and this is his conversation.
  - Equating "the Tool fix" with kta3 is the laptop's reading, not his.
- **The open call: register kta, the Tool cut alone, afresh?** The numbers are above. A fresh registration needs:
  - his word before any game;
  - a development-data declaration covering everything read here: the 45-cell tables, the Rayquaza block, B2e, Scizor, the second lists, and the A/B;
  - confirmation on post-freeze events, by joining the pull's list before the data is opened.
  - The text doesn't say whether it needs new simulator seeds or may reuse these games; that is his to settle.
- **Decided, Sept 29 morning (Dustin): "kta alone, kog stays."** kta gets registered as switch 1 alone, on kog, with clause (d) on Rayquaza as before, Skarmory's +8.5 as the reason the candidate exists, and Suicune reported. `RUN5.md` has his words.

## Records

- The B2e kog3 baseline was read from `/tmp` (sha256 853cdde2…, equal to the cloud branch's `koh_2026-09-28/reading/b2e_kog3.jsonl`).
- The laptop plan (RUN5) asks for a second reader; the registration text in force doesn't. It's done either way.
- Amendment 2's order, "no kt game before koh's verdict", was relaxed by Dustin's word and the gate ruling. The first kt game (timing, 02:52 UTC) came after the gate (02:49 UTC).

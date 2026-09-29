**Verdict: kt3 fails, so the text requires "nothing adopted". kta3's pass adopts nothing. kog stays the working pilot. READING.md is right on the outcome, with five wording corrections below.**

Line numbers are from `git show origin/claude/pensive-ptolemy-spwc0b:rl/results/kt_2026-09-26/README.md`, last touched at b878047. The copy in the local working tree is an older Sept 26 version without amendments 2 and 3.

## 1. Outcome for kt3 failing and kta3 passing

**The decisive text**
- L386 heading: "FOOTPRINT AND ROUTES (section 8 line 130, restated verbatim so nothing is loosened later)".
- L404: "kt3 fails: nothing adopted. The diagnostic codes are read for attribution only, and the next candidate is registered afresh."
- L406 and L7: "A spec change after any reading is a new code."
- L62-65: amendment 2 says "Everything it doesn't name stands as written", and the list includes "the reserve route and its clauses". It does not name the outcomes.

**Route and rule, from the counts**
- kt3's footprint is 14,555 of 22,500 (64.69%). Under L118 that means the ordinary rule.
- The ordinary rule (L119) is ΔMSE with "the whole 95% interval below zero". kt3's ΔMSE is +1.0, 95% interval −16.7 to +18.9, and by event −17.3 to +19.7. It fails, and the bound is nowhere near zero.
- kta3's footprint is 559 of 22,500 (2.48%), so it takes the reserve route.
- I recomputed both footprints from the raw move fingerprints, plus ktb3 at 14,713 and ktc3 at 1,315. They match footprint.txt exactly.
- I also recomputed clause (d) from the raw games: kta3 +1.00 ± 0.39, kt3 +1.00 ± 0.62. Both match.

**Amendment 2 does not change the outcome**
- L121-125 only define "kta3 passes" in the outcomes as passing its footprint-fixed route.
- L125 keeps the "except kta" exception, now "by the route its footprint fixes".
- Nothing in amendment 2 gives kta3 alone an adoption path, a Dustin override for this case, or a re-registration clause.
- The only overrides in the text are L403 (kt as a whole, when kt3 passes and kta3 fails) and L400 (a closed route). Neither applies.

**Residual ambiguity, which the verdict survives**
- L314 ("except kta under the reserve route"), L398 clause (e) ("adoption for the screen and the table together") and L400 ("adoptable only by Dustin's explicit override") could be read as giving kta3 a standalone adoption path.
- The outcomes list is the only place results are enumerated, and it has no such row.
- L152's parenthetical "(kt3 fails; kta3 fails or is closed)" reads best as the two nothing-adopted triggers. The review that produced it (REVIEW_amendment2_laptop_2026-09-28.md, R1 fix at line 15) paraphrases the two original outcomes that way.
- The review's R2 fix said "kta3 passes" is "a gate on kt's adoption, not kta's own adoption". That phrase was not folded in verbatim, so the text never says it outright.
- Adopting kta3 alone now would loosen an outcome "fixed now" after a reading (L386, L406). That makes it a new registration, not a reading of this one.

**What "registered afresh" requires**
- **Registration before games:** the registration is committed before any game or reading of that candidate (L7). It needs Dustin's word (L301: registration "is his decision").
- **Development data:** RUN5 537-539 and L188-191 say cells used to diagnose or design a candidate are development data for it. For kta that now covers the 45-cell tables, the Rayquaza 22,700,000,000 block, B2e, Scizor, the second lists and the coming A/B.
- **Confirmation on new data:** RUN5 486-497 and L192-198 require a re-check on post-freeze events. The candidate joins the pull's list by commit before the data is opened, and the check is τ margin 90% lower bound at −1.0 or above with no veto.
- **No re-reading:** L153 and RUN5 536 say a "new reading under the rules in force, never by re-reading this one".
- **Left open:** the text is silent on whether a fresh registration needs new simulator seeds, or may reuse the ec7e1a8 games. This is a call for Dustin or Fable.

## 2. Is "nothing adopted" final, and are the conditions met?

L152: a "nothing adopted" "stands only once kt3 has been read on all the coverage rows: B2e's 96 pairings, the Scizor row and the four second lists. kta3 is read on them too, by either route." L153 adds that coverage can reopen kt only through a new reading.

**Verified complete, for both kt3 and kta3**
- **B2e:** both-sides files are 96 pairings × 500 (48,000 games). The mixed file has kt on the B2e deck and kog3 on the panel deck, also 48,000 games.
- **Scizor:** both sides, plus mixed rows in both directions, 8 × 500 each.
- **Second lists:** the four lists (29 rows) have both-sides files and the mixed files each list's orientation needs. Weezing has only mixed_b and Charizard Y only mixed_a, which is correct.
- **kog3 baselines:** every baseline covers every pairing with all 500 deals, and its seeds and decks pair one-to-one with the kt files. The B2e baseline's sha256 is 853cdde2… (the branch file). The koh laptop_runs files hold the Scizor and second-list baselines.
- **Preconditions:** all 13 identity replays match, and timing is 0.91×.
- **Verdict line:** READING_numbers line 297 says "Every input of both codes is in".

**Conditions met.** These do not gate finality: the A/B, the counters, the traces, and a second reader. No text in force asks for a second reader.

**Two minor points**
- The B2e baseline was read from /tmp and is not copied into the kt_tables folder. Its hash is printed, so this is recorded but fragile.
- Amendment 2's order (L42, "No kt build or game comes before koh's verdict is committed, coverage included") was relaxed by Dustin's answer and Fable's gate ruling. The first kt game (timing, 02:52Z) came after the gate (02:49Z). This does not affect the outcome, because kog is the base either way.

## 3. Dustin's rulings, and corrections to READING.md

**The kt hinge**
- Dustin's words (RUN5 505-508; kt_tables README line 19): "kt is the Tool fix on the reserve route: the 15 percent trigger read first, no-harm with the −1.0 lower bound, no deck hurt, and the real gain shown on your Skarmory deck ... If the readings show those, the verdicts write themselves; if they show something else, that's the morning conversation."
- The trigger, read first, put kt3 on the ordinary rule, not the reserve route his sentence assumed for "kt". Only kta3 is on the reserve route. So the readings "show something else" and it is his conversation. The hinge does not overturn the registered outcome.
- The Skarmory-deck gain is unread. At the time of my check the A/B had only kog3-arm files (d03's still a `.part`), with no kt3 or kta3 arms. The registration treats deck 07 as motivation, not the test (L397, L429).

**The (d) correction (RUN5 509-511)**
- (d) gates on Rayquaza, which passes at +1.00 ± 0.39. Suicune is reported only, at −0.00 ± 0.25, which is no direction. READING states this correctly.

**Coverage ruling (RUN5 501-504)**
- Own-side harm is a veto in full, and accuracy is only reported. Read literally, amendment 2 item 4 needs more than 2 points further AND own-side harm. On that reading kt3 would have no coverage vetoes, since its largest "further by" is +0.9 on B2e's held-out decks and +1.0 on the second lists.
- The five coverage harms exist only under Dustin's ruling. The verdict is unaffected, because ΔMSE fails on its own. kta3 has no harm under either reading.

**Corrections to READING.md**
1. **Line 17, "Switch 2 is the cause."** This is overstated. Two of ktb3's three numbers cannot be separated from zero:
   - ktb3: real error 14.3, τ margin −0.30 (90% −0.75 to +0.23), ΔMSE +8.4 (−10.4 to +27.7).
   - ktb3 and ktc3 have no coverage rows, so the five coverage harms are not attributed to any switch.
   - Suggested wording: "the scoreboard points at switch 2, but not beyond noise; the coverage harms are unattributed."
   - The same phrase appears in overnight_2026-09-28/README.md line 8 and RUN5 line 352.
2. **Line 21, "no meta deck's own side is worse."** This should read "none worse beyond noise". Blaziken is −0.15 ± 0.29 and Suicune is −0.00 ± 0.25.
3. **Line 42, "the registration asks for one" (a second reader).** The text in force does not ask for one. The only sentence is in the withdrawn amendment 3 (L31), and RUN5 565-566 gives a second reader to pilots "adopted or played by Dustin". Attribute it to the plan or Fable, not the registration.
4. **Line 4, "before any kt result was read."** The footprint, which is a result, was committed at 6c900fd (00:25 -0500). read_kt.py's commit b33a96c came at 01:20 -0500, after kt3's tables and mixed rows had finished. Say "before any result but the footprint".
5. **Open decision (lines 33-38).** Add these:
   - Dustin's own hinge sentence, and that kt3 did not land on the reserve route.
   - The unread Skarmory-deck A/B.
   - That neither override at L400 or L403 covers this case, so a fresh registration needs his word.
   - The fresh-registration requirements from Q1.
   - "kta3's case is strong" is advocacy and should be dropped or reduced to the numbers.
   - The overnight README (line 9) calls kta3 "your Tool fix alone (switch 1, the reserve route you described)". Dustin said "kt is the Tool fix", so equating that with kta3 is the laptop's reading, and the text should say so.

**A caution on score45's kta3 page**
- The score45 page for kta3 prints "ADOPTION RULE (v2): adopt" and ΔMSE −5.9 (−11.0 to −1.4). That is the ordinary-rule view of a code whose route is fixed by footprint as reserve.
- It is not a test and must not be quoted as adoption. READING keeps it out (N11), which is correct.
- Warn Dustin before he sees it.

Files: `C:\Users\dacz8\Projects\Pocket Deck Sim\PocketDeckSim\rl\results\kt_tables_2026-09-28\READING.md`, `READING_numbers.txt`, `README.md`, `STATUS.txt`, `footprint.txt`. Also `...\rl\RUN5.md` and `...\rl\results\overnight_2026-09-28\README.md`. My scratch scripts are in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\wf_kt2\outcome-auditor\`. Nothing was written in the repo.

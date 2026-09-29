# REVIEW of `REGISTRATION_DRAFT.md` (km): the one review, Sept 29

**What this is.** The one review of the km draft, merged from three lenses (rules, engine, power) and checked by the synthesizer where the lenses disagreed. Nothing was run: no game, no build, no engine. The checks were reads of the draft, `rl/RUN5.md`, `engine/src`, kt's registration (`git show origin/claude/pensive-ptolemy-spwc0b:rl/results/kt_2026-09-26/README.md`), kph's registration, the floor's 03b games file, and git tree listings. No kt result file was opened. kt's `footprint.txt` was read.

**Draft line numbers** are the draft as it stands (261 lines, saved Sept 28, 11:11 pm). **RUN5 line numbers** are RUN5 as it stands today.

---

## 1. Verdict

**km can be registered after fixes. Nothing found says the idea or the plan is wrong.**

- The draft follows RUN5's frame closely. The footprint is read first and both routes are written out. There is one gating archetype (Lucario) with a named test. Coverage rows follow Dustin's rule. Development data is declared. Confirmation is at the post-freeze pull.
- The carrier counts recount exactly (Arena in 391 of 398 Lucario lists, Training Area in 329 of 336 Altaria/Espeon lists, Goo-zooka and Ariados in 21 of 21 Whimsicott ex Ariados lists), so the reserve route is open on the count.
- The engine citations hold. N1 and N2 add no constant and no list.

**Two things must change before the text is committed as a registration:**

1. **The sign in the ordinary rule is backwards** (B1, draft line 170). One line.
2. **Clause (d) is not yet one exact test** (B2). Its size, deals and statistic are open, the draft contradicts itself on seeds, and it leaves open a second look at 2,000 deals. As written it is also weak: at the size the draft predicts, it could miss a real gain from about 1 time in 100 up to about 7 times in 10, depending on how many games flip (a model estimate).

**Then 13 should-fix items** (S1 to S13). They would make registered claims false at build time, or leave gaps the reading would be argued over afterwards. The main ones:
- the draft's Goo-zooka prediction points the wrong way (S2);
- N1 has no gain test and there is no "outcomes fixed now" (S1);
- the new hook belongs in `players/`, not `hooks/core.rs` (S3);
- the identity check is thinner than kt's (S8);
- the plan has no owner per job and no reading code (S9).

**Two calls are Dustin's** (section 5): whether N1 stays inside km (Q2), and how many deals clause (d) gets. His word on the text, the build and the tables is still needed, item by item, as for kt.

**Nothing has to be run before registering.** The constructed Goo-zooka board is a test in the build round, not a precondition (section 5).

---

## 2. Where the lenses differed, and what I checked

| Point | Lenses | What I checked | Result |
|---|---|---|---|
| **Does N1 make Goo-zooka played?** Draft: "a tie ... not expected". | Engine: yes, it should rise. Rules and power took the draft's tie as given. | See the chain below. | **The draft's prediction is unsupported.** The code gives a reason to expect the rate to rise. It is not proof. Written as a prediction plus a registered measurement (S2, Q14). |
| **Hook location** (`hooks/core.rs` + a `mod.rs` line, or `players/`) | Rules: use `players/`. Engine: notes `mod.rs`. | `hooks/mod.rs:8-42` re-exports every hook by name, so a new hook needs a line there (a second rules file). `pub mod stadiums` (`lib.rs:23`); `get_training_area_damage_bonus` and `get_arena_of_antiquity_damage_bonus` are `pub fn` (`stadiums.rs:131, 145`). `State::pokemon_energy_types` is `pub(crate)` (`state/mod.rs:663`) and `get_stage` is already re-exported. | **A `players/`-only hook is possible.** kt's rule then holds without any refactor question (S3). |
| **"No test edited"** (draft line 144) | Engine: false as drafted. | `zone_to_bench` stops in `calculate_turns_until_opponent_wins_projected` (`value_functions.rs:1089-1128`) and never reaches the scan (`:1161`). Tests call these positionally (`:4448, 5062, 5123, 5312`), and `5123`/`5312` pass a `b` for `zone_to_bench`, so kph edited call sites. | **Confirmed.** A new flag that reaches the scan changes signatures (S5). |
| **`get_player` silently plays kor** | Engine only. | `players/mod.rs:657-698`: the shared arm ends `_ => ... kor_value_function` (`:685`). | **Confirmed** (S6). |
| **kog3's B2e baseline "not in the tree"** (draft line 185) | Rules and power: stale. | `git ls-tree` shows `rl/results/koh_2026-09-28/reading/b2e_kog3.jsonl` on the cloud branch, not on main. Main has `laptop_runs/scizor_kog3.jsonl` and `var_*_kog3.jsonl`, and koh's B2e rows. | **Stale.** (S11) |
| **Sign of ΔMSE** | Rules only. | koh's printout: "dMSE new - current: -45.1 ... (not below 0)" (`score45_koh3_vs_kog3.txt:14`). | **Confirmed** (B1). |
| **Clause (d) power** | Power (BLOCKER) vs rules (SHOULD_FIX, on exactness). | Formula: per-row sd = 100 × sqrt(q / 500) points, where q is the share of games whose result flips. The 9-row mean has sd = that ÷ 3. That reproduces the power lens's figures. q is unknown (0.08 to 0.30 is the lens's range). | **Formula holds; the figures are model estimates.** I keep B2 a BLOCKER for the ambiguity. The size is Dustin's call. |
| **Footprint centre** | Rules: analogues say lower (2.5% to 11%). Power and engine: 14% to 15% or higher. | Arithmetic: 17 of 45 cells is 37.8% of games. At the draft's 25% to 45% that is 9.4% to 17.0%. N1 adds 0.6 to 1.2 points. So 10% to 18%, centre near 14%, not 13%. kt's analogues: kta3 559 of 8,500 reached-cell games (6.6%); ktc3 1,315 of 4,500 (29.2%). | **No reliable centre.** The analogues are not like-for-like. Written as a wide range with both routes ready (N3). |
| **Keep or drop N1** | Rules: drop. Power: numbers do not favour it. Engine: keep. | kt's spec review asked exactly this ("switch 1 riding in untested?"); kt made each switch its own reading (kt README 393-406). | **Dustin's call** (S1, Q2). |

**The Goo-zooka chain, from the code.**
- Goo-zooka's effect is `IncreasedRetreatCost { amount: 1 }` with duration 1 on their Active (`apply_trainer_action.rs:421-427`).
- The retreat code sums those effects with no duration test (`retreat.rs:239-249`; `played_card.rs:348-353`). `end_turn_maintenance` only drops effects already at 0 (`played_card.rs:460-469`). So a leaf after the bot's turn still shows +1.
- The leaf reads the opponent's cost already (`value_functions.rs:862, 919-943`), then drops it (`:763`).
- Under kog the Goo-zooka line is worth 1 less (the card leaves the hand). Under N1 it is level.
- `play_tick` sorts actions by their JSON string (`game.rs:201`, `observation.rs:37-39`). `EndTurn` is a unit variant, so it sorts first. Then come Attach, AttachTool, Attack, Evolve, Place, Play, Retreat, UseAbility.
- `max_by` keeps the last of equal scores, and `prefer_shorter_win` gives Equal for two `None`s (`expectiminimax_player.rs:64-71, 340-350`). So at an exact tie, Play beats Attach, Attack, EndTurn, Evolve and Place.
- **The draft's own data agrees with the mechanism.** Of the 95 plays in 03b's floor games, 72 were against Blaziken (of 541 chances), 21 against Altaria (of 624), 2 against Weezing (of 440), and 0 in the other 2,840 chances. Draft line 66 already says 12 to 32% against Blaziken (its Hiking Trail) and 0.4 to 3.3% without.
- **Limits.** The tie is exact only if the line has a spare action in the 3-action search and the target Active is still there. The sum is in floating point, so "level" must be tested with a tolerance. kt's registration (README 352-353) records a Balloon tie as "decided by move order" and predicts those plays fall. So the direction of a tie depends on the action and on how many actions it uses. Nobody has measured it.

---

## 3. Findings

Format: where in the draft, the problem, the fix. "Lens" says who found it.

### BLOCKER

**B1. The ordinary rule's sign is reversed.** (rules; verified)
- **Where:** draft line 170. The right sense is at line 203 (item 5). The τ̂ margin at lines 173 and 193 is correctly base minus new.
- **Problem:** it says "Paired ΔMSE, kog3 minus km3, whole 95% interval below zero." `score45.py` prints ΔMSE as new minus current, and below zero means the new pilot is better. Read as written, the rule passes when km3 is worse.
- **Fix:** "paired ΔMSE, km3 minus kog3 (`score45.py`'s 'dMSE new - current'), whole 95% interval below zero." Keep the τ̂ margin as kog3 minus km3. Say once that the two signs are opposite on purpose.

**B2. Clause (d) is not one exact test, and at 500 deals it is weak.** (rules and power, merged)
- **Where:** draft lines 7, 169, 175; consequences at 178 and 202.
- **Problem, exactness:**
  - Line 7 says "No new seed block". Line 169 says RUN5's "double to 2,000 when undecided" applies "as written, on new seeds the laptop picks".
  - In RUN5 that phrase sits in the "Variants and process" line next to the τ̂-margin E = 3 comparison (line 558). It is not extended to the ΔMSE rule, the reserve clauses or the coverage rows. kt did not extend it. kt's amendment 1 kept (d) as one test, not a second chance (kt README 130, 142).
  - "Seeds the laptop picks" leaves the choice until after the result.
  - Clause (d) names the archetype and the pass line. It does not name the deals, the statistic (Lucario's own-side win share; how draws count), the size, or that it is read once.
  - Nothing says the nine rows are clause (c)'s mixed rows, read a second time for gain.
  - Dustin's Sept 28 ruling is that a registration written before the games and satisfying the rule outranks a paraphrase after it (RUN5 line 503). Clause (d) has to be exact for that to hold.
- **Problem, power** (the power lens's model; q is the share of games whose result flips, unknown, taken as 0.08 to 0.30):
  - At 500 deals the 9-row interval has a half-width of about 0.8 to 1.6 points. The draft's own predicted gain is 1.2 to 1.9 points ("about the noise on a deck average", line 175). A real gain of that size clears the test about 31% to 99% of the time (81% to 99% at q 0.08; 31% to 64% at q 0.30).
  - A real 1-point gain is missed 34% to 77% of the time.
  - At 2,000 deals the half-width is 0.3 to 0.8 points, and a 1-point gain clears it 69% to 100% of the time.
  - A miss closes the route for good ("nothing is rescued", line 178).
- **Fix:**
  1. Add to clause (d): "The nine rows are the mixed rows of clause (c) for Lucario's cells. Deals: 72,000,000 + pairing × 10,000 + i for its 7 table cells; 21,108,000,000 + pairing × 10,000 + i for Rayquaza v Lucario and Altaria/Greninja v Lucario; first-named deck in seat 0 on even i. Statistic: Lucario's own-side win share, draws counted as the mixed-row tool counts them (name the tool). Size: N deals per row. It is read once. No doubling, no rerun, no second block."
  2. Say the doubling rule covers only the τ̂-margin "undecided" case, if at all. It never applies to (c), (d) or coverage rows.
  3. Reserve any extra deals as a named seed block now, and put it in START_HERE's seed table in the registration commit (kt did: 22,600,000,000 and 22,700,000,000 blocks). Delete "No new seed block" at line 7, or make it true.
  4. **Size N is Dustin's call** (section 5, D2). The review's lean: 2,000 for (d) only. The first 500 deals per row come from the table and (c). About 27,000 to 36,000 games, roughly 52 to 70 minutes at the laptop's 8.6 games a second, and only if km lands under 15%.
  5. Print beside every gating interval its sd and the smallest gain it could detect half the time and 80% of the time (the eval-power README's "print the power beside every ΔMSE"). Reporting only.

### SHOULD_FIX

**S1. N1 has no gain test, and the draft has no "outcomes fixed now".** (rules, power, engine; Dustin's call)
- **Where:** draft lines 97-98, 175-176, 246 (Q2); section 6 (197-205) has no outcome table.
- **Problem:**
  - Clause (d) gates on Lucario, which carries Arena, so it tests N2 only.
  - No 45-cell list carries Goo-zooka, Plaza or Trap Territory (draft line 224, SCRATCH_NOTES section 6). N1 can only show on the scoreboard as ties, and the draft itself predicts a tie.
  - If km passes (d), N1 is adopted with no gain evidence. Fable's kt spec review asked exactly this ("the bundle as one unit with switch 1 riding in untested?"). kt answered by giving each switch its own reading and fixing outcomes in advance (kt README 393-406).
  - N1 also adds the softest part of the footprint (the "1 to 2%" at line 224 is a guess) next to the 15% line.
- **Fix:** see Q2 for the options. Whichever Dustin picks, add a section "Outcomes fixed now" (as kt did) that states:
  - what is adopted if km3 passes and kmb3 (N2 alone) passes or fails;
  - that N1 is untested for gain, if it stays, and is adoptable only under the no-harm clauses (b) and (c) and vetoes;
  - that a Dustin override is the only route if it fails alone;
  - "a spec change after any reading is a new code" (kt README 406).

**S2. The Goo-zooka predictions point the wrong way, and no measure is registered.** (engine, rules)
- **Where:** draft lines 20-23, 97 ("a tie is decided by list order ... N1 is not expected to make Goo-zooka played"), 230-231 (deck 12, "I expect no visible change"), 258-260 (Q14).
- **Problem:**
  - See the chain in section 2. Under N1 the Goo-zooka line is level with not playing it. The draft is right that the order of the action list breaks the tie. But that list is the canonical sort, which puts Play after Attach, Attack and EndTurn, so the tie goes toward Play. "Not expected to be played" does not follow.
  - On the draft's own data, deck 12 (Hiking Trail, +1 today) goes to +2, so "no visible change" there is unsupported too.
  - Dustin put Goo-zooka on this candidate's list. Yet no measure of its play rate is registered, and Plaza's direction is claimed without one. Waiting for a build result before registering, or editing the text afterwards, would make it a new code.
- **Fix:**
  1. Rewrite the N1 "Honest size" bullet, the deck 12 line and Q14 to say: N1 moves every Goo-zooka line by +1 wherever the target Active is still there at the leaf. The rate is expected to rise, in Trail-less matchups by tie-break (sort order, not value) and with Trail by strict gain. This is a prediction, not proven.
  2. Register the measure now, reported beside, gating nothing. Goo-zooka's plays per chance on brew 03b, and on decks 12, 14, 15 and brew 03a, under km3 (or kma3) against kog3, on the floor's own deals and seeds (`floor_brews_2026-09-28`). Prediction: well above 2.1% in the five matchups where it is 0 today. Plaza's plays per chance on brews 05b and 10 (91% and 54% today) if the "direction" claim stays.
  3. Pre-state the fallback: if the pick does not change, the reading says "km does not fix Goo-zooka". No constant is added, and what to do next is Dustin's decision after the reading.
  4. The constructed 03b board is a build-round diagnostic, not a precondition (Q14).

**S3. The hook should live in `players/`, not `hooks/core.rs`.** (rules, engine)
- **Where:** draft lines 104, 130-131, 249-250 (Q5).
- **Problem:**
  - "One new read-only function in `hooks/core.rs` and nothing else there" is incomplete. `players/` cannot call it without a re-export line in `hooks/mod.rs` (`mod.rs:23-25` do this for the sibling hooks). `mod.rs` is also a rules file.
  - kt's item 7 says the build diff touches `engine/src/players/` only. Anything else needs RUN5's repair or refactor rule before the build is used, and every kog3 baseline is re-run at the build instead of identity-checked (kt README 219-221).
  - RUN5's review tiers make engine-rules changes tier 1, a second reader (RUN5 line 559-561).
  - "Refactor rule not triggered" is right in letter (nothing existing changes) but leaves that path unstated.
- **Fix:** put `lasting_stadium_damage_bonus` in `players/`, calling `crate::stadiums::get_training_area_damage_bonus` and `get_arena_of_antiquity_damage_bonus` (both `pub fn`). That keeps the diff `players/`-only, so the refactor rule and the baseline re-run are never reached. Keep the pin test against `modify_damage`. Reword the rule line to "through the engine's own Stadium bonus functions". Put a comment on both sides pointing at the other, so a later change to either shows up. If Dustin or the cloud insists on `core.rs`, register it as an additive rules-file change: name the `mod.rs` line, write a one-row source equivalence (no rules code calls it), run the full suite, replay k3, kp3 and kog3 on games that execute `modify_damage`'s Stadium branch, and re-run the kog3 baselines at the build.

**S4. The hook is not free, and the timing rule is loose.** (engine, rules)
- **Where:** draft lines 104-105, 150, 256 (Q12).
- **Problem:** `has_stadium` builds the reference card text before it looks at the board (`stadiums.rs:106-113`), and the two bonus functions call it for every Stage 1 attacker, or every [F] attacker against an ex. Called per victim, per clock, per leaf, that allocates even when no Stadium is in play. A threat with an evolution form also clones the deck and hand (engine lens, `value_functions.rs:1873-1879`; not re-read). The 1.10 × kog3 budget has no rule behind it. kt allowed 1.25 with a rerun-once rule (kt README item 7; kt_tables README 77-81). Wall time on a laptop that runs other jobs is about 10% noisy (kt's ratio was 0.91).
- **Fix:** the hook returns 0 first thing when `state.active_stadium.is_none()`, and looks up the evolution form only after that. Timing: 1.25 × kog3 with kt's rerun-once rule (Q12), measured on pairings 0 and 2 (where Stage 1 and [F] threats and both Stadiums occur), in user CPU time or best of several runs.

**S5. The flag path and "no test edited" are wrong as drafted.** (engine; verified)
- **Where:** draft lines 105, 144.
- **Problem:** line 105 says the N2 flag "is passed down as kph's `zone_to_bench` is". `zone_to_bench` stops at `:1089-1128` and never reaches `turns_until_opponent_wins_scan_projected`. N2 must reach the scan, so it adds a parameter to it and to its callers. Tests call these positionally (`:4448, 5062, 5123, 5312, 3272, 3597, 4002, 4083`). "Full suite passes; no test edited" cannot hold.
- **Fix:** name the mechanism in section 4. Either keep every existing signature as a thin wrapper that passes the new flag as false (the pattern kph used for `calculate_turns_until_opponent_wins_damage_aware`, `:1059`), or carry the flag inside `Projection`. Or reword the claim to "no existing test's expected value is edited; call sites are updated for the new argument".

**S6. A mis-wired km code would silently play kor.** (engine; verified)
- **Where:** draft lines 130, 143 (parser).
- **Problem:** the shared `get_player` arm ends `_ => kor_value_function` (`players/mod.rs:685`). If KM, KMA and KMB are added to the or-pattern (`:657-670`) without inner arms, they compile and play kor. Parse tests and identity checks would not catch it if the identity smokes are clean runs only.
- **Fix:** add a `get_player`-level test in the style of the existing kq3, kd3 and kpr3 ones. Build km3, kma3 and kmb3 through `get_player`. On the Goo-zooka board, km3 and kma3 choose Play(Goo-zooka) while kog3 and kmb3 do not. On a Training Area or Arena board, km3 and kmb3 differ from kog3 and kma3 does not. Also reject `kma3x` and `km1a` in the parser tests, by analogy to kt's `kt1a`.

**S7. Test wording that would fail or mislead at build time.** (engine)
- **Where:** draft lines 133-142 (tests), 257 (Q13).
- **Problem:**
  - Line 142 calls `km − kog = (kma − kog) + (kmb − kog)` "exact". That is a float identity and not bit-exact in general. Precedent tests use a tolerance (`(kp - ktb - 10.0).abs() < 1e-9`).
  - N1's term must sit in place of `(-my.active_retreat_cost) * w` at `value_functions.rs:763`. The formula implies it but never says so. Appended after the fuel credit or the opponent-discard term, the same two lines can differ by 1 ulp of rounding, and the tie would then be decided by rounding noise.
  - The Q13 boards must end the turn. A leaf that stops mid-turn has no Hiking Trail top-up. Team Rocket's Thieving Machine moves a card across players, which breaks the 20-cards-per-side conservation the identity relies on.
- **Fix:** state N1's placement as a registered implementation constraint (same position in the sum; flag off leaves the expression untouched). Use bitwise equality only for flag-off identities (KM with both flags off equals KOG; km with N2 off equals kma; km with N1 off equals kmb). Use 1e-9 for the difference-based composition and for the tie tests. Word the constructed boards so the line includes EndTurn or Attack, hands are filled with inert cards, and only the card term is compared.

**S8. The identity check is thinner than kt's.** (rules, power, engine)
- **Where:** draft lines 145-149, 253 (Q9).
- **Problem:**
  - Identity is 2 pairings × 40 deals (80 games) for kog3, k3 and kp3. That is kph's scheme, from before kog existed.
  - km edits shared player code (the clock at `value_functions.rs:1161-1258` and `extract_features`' signature). kt accepted that only through full replays of the bots whose clocks run it (kt README item 7, lines 206-222).
  - The reading pairs km3 against the stored `table_kog3.jsonl` and `new17_kog3.jsonl`, and the footprint counts any drift as km's. Only an identity that covers those files licenses that reuse (RUN5 line 479: baselines from the same engine as the candidate).
  - After 80 identical games the 95% upper bound on an unseen difference rate is 3.7%. A route that sits within a few points of its threshold needs a tighter bound.
  - Identity 3 uses pairings 17 and 14, whose lists carry no Stadium at all, so "a Stadium is in play but not N2's" is covered only by a unit test.
- **Fix:** adopt kt's item 7 with km's presets.
  - k3, kp3 and kog3 in full against the official references (14,000 each).
  - kog3 also against `table_kog3` (14,000) and `new17_kog3` (8,500).
  - kq3 in full if its clock reaches the touched function; kd3 and kpr3 at 1,120.
  - The kog3 B2e, Scizor and second-list baselines at i<40 of every pairing.
  - The diff touches `engine/src/players/` only (S3).
  - Replace identity 3 with kmb3 (N2 alone) on the 28 cells whose lists carry neither Training Area nor Arena (14,000 games, about 27 minutes): it must equal kog3 exactly. That covers the Trail and other-Stadium cases too.
  - Keep the pairing-2 execution argument as an addition.
  - State that any difference stops the reading.

**S9. Ownership, reading code and order are not fixed.** (rules)
- **Where:** draft lines 5, 145-152.
- **Problem:**
  - RUN5 (lines 417-420) wants the plan to name the laptop jobs the cloud must not duplicate, and the reverse. The draft names the laptop jobs (tables, mixed rows, coverage, counters, footprint) but not the cloud's.
  - Timing is called a laptop job at line 150 but is missing from that list.
  - There is no single owner per output file and no output folders named.
  - There is no gate saying no km game precedes the passed identity and tests. The numbering puts the footprint (Step 1) before the build (Step 2).
  - No second reader is named (RUN5 line 559-561: an adopted pilot gets one; the laptop second-reads tier 1, line 563).
  - No reading code is named. kt wrote `read_kt.py` blind from its registration, committed it before any result, and had it reviewed twice.
  - kt's tables are running on the laptop now (RUN5 line 351).
- **Fix:** add an ownership block.
  - **Cloud:** build, tests, `BUILD.md`, identity (one owner only), the one code review.
  - **Laptop:** builds the same commit and checks the sha256; timing; footprint; tables; mixed rows; coverage; counters; kog3 baselines if missing; the reading code; the tier-1 second read of the diff before the first km game.
  - **No overlap:** the laptop does not re-run the cloud's identity, and the cloud runs no tables. A second cloud round happens only after a table has asked a question.
  - **Gate and order:** no km game before identity and tests are committed as passed. Reword step 1 so the footprint is the first result read, not the first thing run.
  - **Output folders:** name two, one cloud and one laptop.
  - **Reading code:** write `read_km.py` blind from the registration, review it, and commit it before any km result. Queue km's laptop jobs behind kt's tables and readings.

**S10. The confirmation lapse clause differs from kt's and breaks the read-once rule.** (rules)
- **Where:** draft line 193.
- **Problem:** "If any of kog's rows is not confirmed at that read, km reads not confirmed at this size too and both are read again at the next pull." kt's registered rule (README 201-204) is different. A passed check stands and is not read again. The candidate stays "unconfirmed" until kog's, kpg's and koa's rows pass at a later pull. Only a check that failed is read again. Re-reading a passed check breaks RUN5's read-once and rolling-freeze rules (RUN5 lines 485-488).
- **Fix:** replace with kt's clause. "km's passed check stands and is not read again. km stays unconfirmed and is confirmed at the first later pull at which kog's, kpg's and koa's rows pass. A failed check, km's or kog's, is read again at the next pull on the events after it."

**S11. The baseline paragraph is stale.** (rules, power; verified)
- **Where:** draft lines 185, 247 (Q3).
- **Problem:** it says kog3's B2e rows are not in the tree and only `b2e_koh3.jsonl.part` exists. `rl/results/koh_2026-09-28/reading/b2e_kog3.jsonl` is on the cloud branch. koh's B2e and mixed rows are now committed on main (`laptop_runs/`, RUN5 line 342), and so are `scizor_kog3.jsonl` and `var_*_kog3.jsonl`.
- **Fix:** rewrite on kt's item 4 rule (kt README 184-187). Use the committed files (`b2e_kog3` from the cloud branch by `git show`; Scizor and second lists from `laptop_runs`) if kog3 at the km build equals them at i<40 of every pairing. Run kog3 at the km build on all 500 deals for any that fail or are missing. Drop "who runs them" as an open question.

**S12. No base-change rule, and N1 overlaps kt's parked "later candidate".** (rules, engine)
- **Where:** draft lines 98, 106, 237.
- **Problem:**
  - kt is being read now on kog, and kt's clock replaces kog's clock. If kta3 or kt3 is adopted first, km's base moves. kt's amendment 2 handled that for koh: re-issue by a dated amendment before any game. The draft has no such rule.
  - "Not kt's" (line 98) hides an interaction. kt's README (line 351) parks the opponent's retreat Tools as "a later candidate", and N1 prices exactly that. It would change what Field Blower, Guzma and Repel are worth under kt's switch 2. In the panel lists that means Small Balloon (`t-altaria`), Inflatable Boat (`t-suicune`) and Bombirdier (`t-hydreigon`, its bench ability lowers the Active [D]'s retreat cost by 1). kt predicts Blower stops removing the opponent's Balloon and Boat (93 and 64 of its 1,414 Active removals under kp3, kt README 366-367). N1 would give those removals value again.
  - The draft's exact-composition test covers only N1 with N2 inside km.
- **Fix:** add: "If kt (or kta) is adopted before km's first game, km is re-issued on the new base by a dated amendment, reviewed before any game. If both pass separately against kog3, they are composed under RUN5's composition rule (lines 507-514), with N2 built into kt's clock (`kt_clocks`) and a fresh identity." Rewrite "Not kt's" to say N1 prices the opponent's retreat Tools kt parked, and that composing with kt's switch 2 needs its own check.

**S13. The ordinary route's expected sign is not stated, and (d) is not said to run on both routes.** (power, rules)
- **Where:** draft lines 170, 175, 178, 203 (item 5).
- **Problem:**
  - Lucario is already over-rated by the simulator: 52.2 under kog3 against 45.6 real (+6.6, line 179). If N2 makes Lucario play better, it moves further from the real figures. The power lens puts ΔMSE at about +2.64 per point of gain, worse (+3 to +10 for a +1 to +3 point Lucario gain), against a ΔMSE sd of 3.7 to 6.5. So a real gain almost never clears zero on the ordinary route.
  - The draft states the accuracy risk only under the reserve route (line 179). Section 6 item 5 (line 203) lists an ordinary-rule fail as evidence against km, when the mechanism predicts it either way.
  - The draft does not say clause (d) is run and reported on the ordinary route. kt's rule for kta3 at 15% or more is that (d) and its report beside are still run and reported, but gate nothing (kt README 124).
- **Fix:** add to step 4: "On the ordinary route the expected sign of ΔMSE is positive if N2 gains on Lucario. (d) and its report beside are run and reported under both routes; on the ordinary route they gate nothing." Reword item 5 so a ΔMSE fail is not called evidence that km is wrong. The rule itself stays as Dustin set it (this is a wording fix, not a rules question).

### NOTE

**N1. Stale RUN5 line numbers.** (all lenses; verified)
- **Where:** draft lines 5, 18-19, 131, 169-171, 181, 189.
- **Problem:** RUN5 grew by 15 lines after line 340. Now: cloud 417-420 (draft says 403); refactor rule 472-478 (457); coverage rows and supersession 495-498 (480-483); kt (d) 503-505 (488); "not adopted is provisional" 523-530 (508); development data 531-533 (516); reserve route 534-541 (519); doubling 558-559 (543). Line 340 (by-event interval) is still right.
- **Fix:** cite section names only, as the draft's own line 8 says, or update the numbers. Print the by-event interval beside the τ̂ margin under the reserve route too, since RUN5 says every 45-cell reading prints it.

**N2. Status, decision line and heading.** (rules)
- **Where:** draft lines 3, 17, 36-37.
- **Problem:** there is no "Decision this informs" line (RUN5 line 559: every experiment names the decision it changes). The heading says "Two rulings" and lists three. Only "Dustin's word on the text" is named.
- **Fix:** add a one-line decision statement. Fix the heading count. Add a Status block: Dustin's word is needed on the text, on the build, and on the tables, item by item (kt README 37-40). The overnight delegation to Fable does not cover his registration gate.

**N3. The footprint prediction.** (rules, power, engine; my arithmetic)
- **Where:** draft lines 15, 158, 222-226.
- **Problem:** the draft says 13% (9 to 19%), "a toss-up". Its own arithmetic gives 9.4% to 17.0% for N2 plus 0.6 to 1.2 for N1: 10% to 18%, centre about 14%. The closest analogues in kt's footprints put it lower: kta3 differed in 6.6% of its reached-cell games and ktc3 in 29.2%. Applied to N2's 17 cells (37.8% of games), that is 2.5% and 11.0% of all games. The draft's 25 to 45% has its top end above the closest analogue. Against that, a Stadium is offered in 76% and 68% of Altaria's and Lucario's games (draft line 223), and kt3 and koh3 (65% and 93%) show broad changes can reach far. None of these is like-for-like.
- **Fix:** restate as "between about 3% and 19%, no reliable centre. Both routes are ready". Keep both routes registered. Add: the reading prints the smallest ΔMSE and the smallest own-side gain it could detect, from the same games (reporting only). Have the compute plan ready for both routes (the reserve route's (c) can need 45,000 games, about 87 minutes).

**N4. (b) is unlikely to bind; two wording fixes.** (power, rules)
- **Where:** draft lines 179, 202 (item 4).
- **Problem:**
  - The τ̂-margin sd is 0.13 to 0.23 at 500 deals. A real Lucario gain of +1.5 gives margin about −0.16 and +3.0 gives about −0.34. So (b) fails only if ΔMSE reaches about +28, far beyond what a small footprint can do. The "b-fail with a real gain" paragraph over-warns for the reserve route.
  - "Lucario's overshoot stays on RUN5's open-cause list": it is not on that list today (RUN5 lines 517-522). RUN5 says each fix's reading adds to it.
  - "Nothing is rescued" should add that adoption then comes only by Dustin's explicit override, recorded as such.
- **Fix:** replace the paragraph with these numbers. Reword to "is added to the open-cause list". Add the override sentence. Reword items 4 and 7 of section 6 to "no Lucario gain of about X or more at this size", with X printed from the reading's sd.

**N5. The harm tests are many, with no floor.** (power; report only)
- **Where:** draft lines 174, 182-184, 186.
- **Problem:** about 21 own-side tests (10 decks in (c), 6 B2e archetypes, Scizor, 4 second lists), each "whole 95% interval below zero", no floor (kph amendment 4). On a harmless candidate whose every test has real noise, that blocks about 4 times in 10 (1 − 0.975²¹ ≈ 41%). It is Dustin's rule (amendment 4), not for this draft to change. Rows a candidate does not move at all have no noise and cannot fire.
- **Fix:** state (c)'s pooling explicitly (per deck, pooled over its cells, as `score.py` does). Print the count of tests beside the harm reading. No rule change.

**N6. Section 6 mixes gates and diagnostics.** (rules, power)
- **Where:** draft lines 162-166, 197-205.
- **Problem:** items 1 (pin), 3 (harm), 4 (no gain) and 5 gate. Items 2 (M1, M2), 6 and 7 and the sentinels do not. Item 6 uses "more than about 3% of games differ", a loose constant, and asks about Boss, X Speed and Copycat "in cells whose lists carry neither Stadium nor N1 cards", but Step 3's counters run only on the 17 Altaria/Lucario cells. M1's "at least 7 of 9" sign line and M2's contrast have no stated size (at 200 deals M2's 95% half-width is about 6 to 9 points, the power lens's estimate).
- **Fix:** mark each item "gates" or "diagnostic, gates nothing". Make item 6 a reported figure, or give it an exact number. Either add the 28 non-carrier cells to the counter run, or restrict item 6 to km3's footprint there (the footprint file gives it). State that a M1 or M2 miss reads "not shown at this size".

**N7. The closure sentence.** (rules)
- **Where:** draft line 178.
- **Problem:** RUN5 says the route's closure sentence is "as fixed in section 8" (line 535). The draft adapts its card class from "reduction Tools or turn-effect cards" to "the relevant cards". Training Area and Arena are Stadium damage bonuses, which are not in that class. The carrier count is verified, so the route is open on the count.
- **Fix:** quote section 8's sentence verbatim beside the adaptation. List "Stadium damage bonuses count as the relevant cards" among the items Dustin approves with the text.

**N8. Coverage reach is incomplete.** (rules)
- **Where:** draft lines 182, 213-218.
- **Problem:** the draft says Manectric, Raticate and Whimsicott "are the ones N1 and N2 can reach". N2 acts on both sides, so it reaches every held-out, Scizor and second-list row whose opponent is the panel Altaria (Training Area) or Lucario (Arena), not only the carriers. kt's item 3 states the principle: a cell is reached when either list carries the card.
- **Fix:** add the opponent-Stadium reach for coverage rows. State that all coverage rows get mixed rows regardless (so no gate is lost).

**N9. Development data list and footprint script.** (rules)
- **Where:** draft lines 188-190, 158.
- **Problem:** the declaration omits the floor's 03b page (95 of 4,445) and the floor re-check that motivated N1's Goo-zooka, and does not say the Sept 25 holdout is spent, not fresh. `footprint.py` asserts `("koh3","koh3")` (line 17), so it needs a km3 variant.
- **Fix:** add those to the declaration. Name a km3 footprint script derived from `footprint.py`.

**N10. Engine details to state in the text.** (engine)
- **Where:** draft lines 96, 105, 119, 176, 204 (item 6), 217-218, 257.
- **Problem, five small ones:**
  1. N2 picks the threat on unbonused damage, then adds the bonus per victim, and treats every hit as landing on the Active (a bench-only attack of an eligible attacker gets a bonus `modify_damage` would not give). Both agree with kp's existing simplifications.
  2. N1 also prices attack-applied Retreat Cost effects and the opponent's retreat Tools and abilities (`retreat.rs:153-222`). The item 6 guard list names only Training Area, Arena, Goo-zooka, Plaza and Trap Territory. Add Small Balloon, Inflatable Boat and Bombirdier (in `t-altaria`, `t-suicune`, `t-hydreigon`; the retreat code reads them).
  3. Whimsicott ex's Grass Knot (extra damage per Energy in the opponent's Retreat Cost) is not in the clock's damage estimate. `value_functions.rs` has no retreat-cost case, and the mechanic is `ExtraDamagePerRetreatCost`. So Whimsicott's held-out row does not test N1 as pricing the card's payoff.
  4. The citation `expectiminimax_player.rs:659-717` for "attack, coin, promotion and queued-target choices as free" covers only the coin and queued-target frames. The range is `:630-771`.
  5. The N2 arithmetic goes at the two `None` branches (`:1219`, `:1250`) only and leaves the kq branch alone. That path is dormant, since km leaves `next_attack_reduction` off.
- **Fix:** state 1, 3 and 5 as intended simplifications in section 2. Add 2 to the guard list. Fix 4's citation.

**N11. The X Speed "96 turns" and the Trail counter.** (engine)
- **Where:** draft lines 67, 162, 254 (Q10).
- **Problem:** the 96-turn group is an upper bound (the census file has no Stadium record).
- **Fix:** keep it labelled an upper bound. Have the Step 3 counter tool record "Hiking Trail in play" at each X Speed turn on the same deals. That settles it for free.

---

## 4. The draft's 14 open questions

Each is **answered** (with what settles it) or **Dustin's call**. Only Q2 is Dustin's call. His two new calls (D1, D2) are in section 5.

| Q | Answer | What settles it |
|---|---|---|
| **1. Amendment 2 or 4** | **Answered: confirmed.** Take kph amendment 2's row definitions (which rows, which deals, the 8-row interval formula 1.96 × sqrt(Σ per-cell variance) / 8) and amendment 4's test. There is no 2-point floor on own-side harm: the whole 95% interval below zero is harm and blocks the takeover. Accuracy on Scizor and the second lists is reported only. B2e's "more than 2 further" veto stands, through mixed rows. All three kinds get own-side mixed rows every time. The draft's Step 5 already reads it this way. Fix only the stale line numbers (N1). | RUN5 "How coverage rows count" (lines 495-498); kph REGISTRATION amendment 4 (lines 35-38); koh's reading as precedent (RUN5 342-350). |
| **2. Is N1 worth carrying?** | **Dustin's call.** Why it is his: it is a direction, not a rule. He put Goo-zooka on this candidate's list, and only N1 touches it. The review's lean and the options are under D1 in section 5. Whatever he picks, S1's outcomes text is needed. | See D1. |
| **3. B2e's kog3 rows** | **Answered: they exist. Nothing needs to run.** Use them if kog3 at the km build equals them at i<40 of every pairing; otherwise run kog3 at the km build on all 500 deals (S11). If it ever had to run: 48,000 games, about 2.2 hours on the laptop. | `git ls-tree` on the cloud branch (`reading/b2e_kog3.jsonl`); kt README item 4 (184-187); kt's identity run reported `kog3 B2e i<40 v b2e_kog3` equal on 3,840 of 3,840 (the rules and power lenses read this; I did not open the file). |
| **4. Board-ability bonuses in the hook** (Lucario's Fighting Coach) | **Answered: keep out.** The class queued is Trainer pricing (RUN5 line 435), and the draft's own rule sentence is "a Trainer whose effect changes a board number". Board abilities are a Pokémon-side scan (`hooks/core.rs:2101-2153`). Adding it would move all nine Lucario cells, confound clause (d) and M1, and by the draft's own reckoning push the footprint past 15%. If wanted, it is its own candidate on top of km. | Draft line 88 and section 3 row 7; engine lens read of `hooks/core.rs`. |
| **5. Duplicate hook and the refactor rule** | **Answered.** A duplicate leaves `modify_damage` untouched, so it is not a refactor in letter. Making `modify_damage` call the new function would be a true refactor needing all three parts. But the record does not let the draft declare the rule "not triggered" while it also edits `hooks/mod.rs`. The clean answer is to put the function in `players/` (S3). | RUN5 lines 472-478; kt README 219-221 (diff scope); the visibility facts in section 2. |
| **6. Gating archetype for (d)** | **Answered: Lucario.** The rules do not choose between Lucario and Altaria (both qualify: Altaria/Espeon has Training Area in 329 of 336 lists). Lucario is rank 1, has Arena in 391 of 398 lists, and no file of Dustin's carries Arena. Even an archetype he also plays still qualifies (RUN5 line 540). Altaria and Suicune-style extras are "reported beside, a finding to write down, not a gate that fired". Make the test exact (B2). Dustin's word on the text covers it. | RUN5 lines 503-505, 534-541; kt README amendment 1; the lenses' recount of `split.json`'s development ids. |
| **7. Accuracy direction** | **Answered: yes, "record it, rescue nothing".** Two corrections (N4): the overshoot is *added to* the open-cause list, and adoption then comes only by Dustin's explicit override. Also (b) is unlikely to be the clause that fails (it needs ΔMSE near +28). The real exposure is the ordinary route (S13). | RUN5 lines 517-530, 534-541; kt README 401-406. |
| **8. Coverage flag learns Stadium and status texts** | **Answered for km: not part of km.** The flag is a text scan in `engine/examples/goldfish.rs:163-219`, not part of any pilot. Changing it changes the goldfish program's sha, which the floor pages cite, so it needs its own build and pin. If wanted later it is a separate screen change, and his to ask for, since it changes what his floor pages flag. | `goldfish.rs`; floor README. |
| **9. Identity size** | **Answered: not enough.** Use kt's item 7 scope (S8). | kt README items 1(2), 7 (95, 206-222); RUN5 line 479. |
| **10. The X Speed claim** | **Answered: no separate replay.** Keep it labelled an upper bound. Add "Hiking Trail in play" to the Step 3 counter (N11). | Draft line 67; `hooks/core.rs:555-568`; the census file records move kinds only. |
| **11. Code letters** | **Answered: free.** No code starts with `km` on main (HEAD b33a96c) or on the cloud branch (I grepped `engine/src/players/mod.rs` on both). Entries go before the `k<N>` fallback. Add parser tests rejecting `kma3x` and `km1a` (S6). | The grep; the kt block at `players/mod.rs:260-274`. |
| **12. Timing budget** | **Answered: use kt's 1.25 × kog3 with the rerun-once rule** (or state why 1.10 is right), after the hook guard (S4). RUN5 has no timing rule. | kt README item 7 (line 222); kt_tables README 77-81 (as the rules lens read it). |
| **13. Is the card-arithmetic identity true?** | **Answered: it holds by conservation, with two exceptions.** Each side's 20 cards are in hand, deck, discard or in play, so the card term is 2 per card in hand and 1 per card in discard or in play. Exceptions: Thieving Machine moves a card across players, and a leaf that stops mid-turn has no Trail top-up. Confirm with two constructed boards that end the turn (S7). It is not a precondition of registering: 1.2 and section 3 stay labelled "derived". | `value_functions.rs:759-762`; `observation.rs:54-57`; `hooks/core.rs:555-568`; `apply_trainer_action.rs:406-413` (engine lens). |
| **14. Does N1 move Goo-zooka?** | **Answered in part.** The draft's worry is refuted by the code: a leaf that does not play the opponent's turn still sees the +1, and the sort order breaks the resulting tie toward Play (section 2). Whether the pick actually changes on real boards is unmeasured. So: register the measure and the fallback now (S2). The constructed board is a build-round diagnostic (section 5, step 6). Not needed before registering. If the pick does not change, the reading says "km does not fix Goo-zooka" and what next is Dustin's, after the reading. | Section 2's chain; RUN5 line 437; kt README 406. |

---

## 5. Before registering, in order

Nothing below runs a game, a build or an engine. Steps 1 to 5 are text and decisions. Steps 6 to 9 come after registration and are listed so the order is fixed.

**Two calls for Dustin (plain words):**
- **D1. Keep the Goo-zooka switch (N1) inside km?**
  - **Option A (the review's lean):** take N1 out of km's gate. km is then N2 alone (today's kmb; that is a change of letters in the text, and nothing is built yet), and the N1-only code stays in the build as a diagnostic. N1's effect on Goo-zooka is still measured (S2). N1 is registered later as its own candidate if he wants it, with its own carrier: Whimsicott ex Ariados (Sept 10 rank 26; Goo-zooka and Ariados in 21 of 21 development lists; held-out deck `h-whimsicott` exists) and the Goo-zooka rate as its evidence.
    - Why: N1 has no gain test, it adds the least certain part of the footprint, and two lenses lean this way.
    - Cost: one more registration cycle for the Goo-zooka card.
  - **Option B:** keep it in. The text then says plainly that N1 rides on N2's clause (d) with no gain evidence, is adoptable only under the no-harm clauses, and that a Dustin override is the only route if it fails alone (S1).
    - Why: it is free, list-free, and the only thing in km that touches Goo-zooka.
- **D2. How many deals for clause (d)** (Lucario's nine cells)?
  - At 500 per cell, a real gain of the size the draft predicts (1.2 to 1.9 points) is caught about 31% to 99% of the time, depending on how many games flip. That range is a model estimate, not a measurement.
  - At 2,000 per cell, a real 1-point gain is caught 69% to 100% of the time. It costs about 27,000 to 36,000 games (52 to 70 minutes), and only if km lands under 15%.
  - The review's lean: 2,000 for (d) only. This is close to his open question from the eval-power README (run small-footprint candidates at 2,000 deals). If he answers that one for the whole reserve route, the text follows his answer.

**The order:**
1. **Apply the findings to the draft** (B1, B2, S1 to S13, N1 to N11), with D1 and D2 as Dustin answers them. The text stays a draft. Dustin's answers go in as recorded lines with the date.
2. **Optional, read-only, no games:** from files already in the tree (koh3-vs-kog3 Lucario rows, the eval-power analyst's per-cell data), compute the smallest gain clause (d) can detect at 500 and 2,000 deals, and print it in the text. It replaces the model estimates in B2 with figures from real paired data.
3. **A check by someone other than the editor** that each finding is applied, or is answered "not applied because ...". This is not a second full review. kph's and kt's pattern was one review, then "all findings applied".
4. **Commit the text as the registration**, with the seed block added to START_HERE's seed table (B2) and the status block naming Dustin's three words (N2). **Dustin's word on the text** (first word). It covers: Lucario as the gate, the exact (d) test, "Stadium damage bonuses count as the relevant cards" (N7), the coverage reading (Q1), and D1's outcome.
5. **Only after his word:** the cloud's one round.
   - Build in `players/` only. Tests (S5, S6, S7). Identity per kt's item 7 scope (S8). `BUILD.md`, with each baseline file named before the first km game (S11).
   - The Goo-zooka board test (Q14) runs here, as a diagnostic.
   - The laptop builds the same commit and checks the sha256.
   - **Dustin's word on the build** (second word), as kt needed for its build.
6. **The reading code:** write `read_km.py` blind from the registration and review it. Commit it before any km result (S9).
7. **The tables, queued behind kt's tables and readings on the laptop.** First the footprint, read first and committed alone; it fixes the route. Timing (S4). Then the route's steps, the mixed rows, the coverage rows, the counters. **Dustin's word on the tables** (third word).
8. **The Goo-zooka and Plaza measures** on the floor's deals (S2). Reported beside.
9. **If kt or kta is adopted before km's first game:** re-issue km on the new base by a dated amendment, reviewed before any game (S12).

---

## 6. What this review did not do

- No game, build or engine run. The power figures (B2, S13, N3, N4, N5) are the power lens's model, built on the analyst's per-cell data for koh3 versus kog3. They depend on q, the share of games whose result flips, which nobody has measured for km. Treat them as scaled estimates. I re-derived the interval formula and several of the pass odds by hand and they reproduce.
- I did not reopen three lens counts: the 391 / 398, 329 / 336 and 21 / 21 carrier counts (the rules lens recounted them from `split.json`'s development ids and the draft's SCRATCH_NOTES agree); the kt identity file's "3,840 of 3,840"; and the eval-power analyst's per-cell misses for Lucario (+38.5, +20.0, +16.1, +8.4 in four cells, +59.5 over nine).
- I did not open any kt result file, any holdout file or `split.json`.
- I did not edit `REGISTRATION_DRAFT.md`. `REVIEW.md` is the only file written in the repo.

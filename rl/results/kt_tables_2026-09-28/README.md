# kt on kog: Dustin's word, and the laptop's runs (Sept 28 night)

**Dustin's word**, typed in the laptop session ("Project familiarization"), Sept 28 about 7 pm Central:
- "kt tables: go".
- Asked whether that also covers kt's registration on kog (amendment 2), the new kt build, and a build before koh's held-out rows land (no kt game until they're read), he answered: **"Yes, all; build now."**
- So all three items of amendment 2's Status (`../kt_2026-09-26/README.md` on the cloud branch, commit 98f9a86 and later) have his word:
  1. amendment 2 as kt's registration on kog;
  2. the new kt build on kog, with its timing run;
  3. kt's tables.
- Amendment 2's order ("no kt build or game before koh's verdict is committed, coverage included") is relaxed by his answer for the build only.
  - kt's first game waits until koh's B2e rows (`b2e_koh3`, in the cloud) are read and committed.
  - koh can't become the pilot whatever B2e shows: its ordinary-rule test already failed (`../koh_2026-09-28/laptop_reading/READING.md`).

**Amendment 1's open point, confirmed by the laptop** (amendment 2's Status allows "from Dustin or the laptop"):
- **Rayquaza is clause (d)'s one test,** with Suicune reported.
- That is the carrier census's choice (`../kt_carrier_census_2026-09-26/README.md`: the census Rayquaza list, 8 × 500 on the 22,700,000,000 block), and amendment 2's item 3 and item 8.

**Dustin's rulings for the reading** (typed in the Fable session "Recommendations and advice", Sept 28, relayed verbatim; recorded the same day, also in RUN5's frame):
- **About 6:40 pm Central, kt's part:** "kt is the Tool fix on the reserve route: the 15 percent trigger read first, no-harm with the −1.0 lower bound, no deck hurt, and the real gain shown on your Skarmory deck and on Suicune as the non-Dustin deck per the earlier ruling, with Suicune's real cells before and after reported. If the readings show those, the verdicts write themselves; if they show something else, that's the morning conversation."
- **The same message, on coverage:** "coverage rows count for the mixed-row veto and are reported for accuracy."
  - So kt3's and kta3's coverage rows (Scizor, the four second lists, B2e's held-out decks) all get own-side mixed rows. B2e's were added to `run_kt.sh`.
- **About 7 pm Central, on the clause (d) conflict:**
  - "Rayquaza, as registered. My "Suicune" tonight was a recollection of the earlier ruling that Suicune could count as the non-Dustin deck for the Tool fix — it was permitted, not required — and the registration then chose Rayquaza on exactly the grounds clause (d) asks for: a Limitless top-30 archetype, carries the relevant Tools, not your deck. A registration written before the games and satisfying the rule outranks a reviewer's paraphrase after it. Changing the gating deck now, with the rows already running, would be the goalpost move the registration exists to prevent, whichever way it went."
  - "Suicune stays reported beside, as the record already says, and if it moves in the same direction as Rayquaza that's supporting evidence; if it moves the other way that's a finding to write down, not a gate that fired."
  - "The correction belongs in the saved rulings too, so the record reads: (d) gates on Rayquaza per registration; Suicune reported; Fable's Suicune wording of Sept 28 was a misstatement and is withdrawn."
- **So:**
  - (d) gates on the census Rayquaza list's eight rows, kta3 v kog3.
  - Suicune's seven mixed rows and its real cells before and after are reported.
  - The Skarmory deck is in the Dustin-deck A/B, as motivation.

**The cloud's amendment 3 is not in force** (Fable's overnight ruling, Sept 28 about 23:45 UTC). Amendment 3 (f72cb77) read the GO as starting kt's games before koh's B2e read. Fable ruled:
- Dustin's "Yes, all; build now" was given here with the koh-first order attached, and the amendment is the cloud's own reading, not his word.
- The laptop's kt run is the run of record.
- The cloud's identity and table runs (`../kt_kog_2026-09-28/`) are a cross-check only. The same commit and seeds should give the same games, and a difference is a finding to stop on. The cloud writes no footprint reading, route, verdict or further amendment.
- Its table files may be input to the laptop's footprint, but only after identity confirms its build hash and its games equal the laptop's on the overlap. This README says so if they are used.

**When the gate opens** (Fable's overnight ruling, Sept 28 about 00:05 UTC):
- `GATE_koh_b2e_read` is written once koh's B2e rows (`b2e_koh3`) are read and committed.
- It doesn't wait for koh's B2e mixed rows. The gate exists because kt's base would change if koh were adopted. koh already fails the ordinary rule on the 45 cells (the ΔMSE interval crosses zero), and mixed rows can only add vetoes, never turn a fail into an adoption.
- koh's B2e mixed rows still run, to complete its coverage record.
- If the B2e read shows anything that would reopen koh, the gate stays shut and Fable is told first.

**The A/B and the readout counters** (`run_kt_ab.sh`, `kt_ab_play.py`, `read_kt_ab.py`, `run_kt_counters.sh`; edd4ab8):
- Written by a Sonnet agent and tested with kog3 only. Reviewed by a second one: no blocker.
- The review's fixes are in:
  - each runner refuses to play before `run_kt.sh` part A (identity) has passed;
  - a finished file is reused only at its full size;
  - one run at a time (a lock);
  - the reader asserts complete files (1,920 games per deck and arm) and reports draws.
- **Launch order:** after `run_kt.sh` part B's footprint is committed, one runner at a time, never beside part B at 12 threads each. That also keeps them off kt's timing check.

**Who does what:**
- **The cloud:** the kt build's code on 233bced's `engine/` (kt's presets redefined on kog), the parser, preset and values tests (item 7), the full suite and `BUILD.md`.
- **The laptop:** builds the same commit, then runs everything that plays games, each from the kt build's own programs with their sha256 recorded:
  - identity (item 7): k3, kp3 and kog3 in full; new17_kog3; kq3; kd3 and kpr3 at 1,120; the coverage baselines at i < 40;
  - the timing run;
  - the four tables on the 45 cells;
  - the mixed rows;
  - coverage;
  - clause (d);
  - the Dustin-deck A/B;
  - the readout counters;
  - the Rayquaza traces.
- **The reading follows amendment 2 and the text it amends:** the footprint first, which fixes each code's route.

**The timing check in `run_kt.sh`** (fixed Sept 28 night; the bug was found by Astra's read-only review and confirmed by Fable):
- The first version reused a cached timing arm after a restart, which timed it at 0 s.
- Now both arms (kog3, then kt3, 40 table deals) always run fresh, and wall time gates as registered (kt3 ≤ 1.25 × kog3). User+sys CPU seconds are recorded beside.
- The laptop runs other jobs at the same time. So if the first pair is over, both arms are rerun once and the second pair decides.
- The cloud's own timing run (`../kt_kog_2026-09-28/`, 4 threads) is a second measurement.

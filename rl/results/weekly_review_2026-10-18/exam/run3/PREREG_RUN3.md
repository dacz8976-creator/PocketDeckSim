# Exam run 3 (exam v2): pre-registration (written Oct 21, 2026, before any game is selected or any position built)

Written by the laptop session on the coordinator's instruction of Oct 21, from Dustin's decision (verbatim, to the coordinator): "I'll play more ranked games this week first; set the cutoff before Dual Fusion lands."
- **Why this run:** run 2 (`../run2/RESULTS_run2.md`) was "inconclusive". Gemini 4 Argon agreed with his first plan segment on 30 of 49 points and km3 on 22: +0.163 [−0.014, +0.347], sign-flip p 0.109.
- **What run 3 does:** it repeats the test on fresh decisions Gemini has never seen, with the same frozen judge and the same pass rule's machinery, and it decides the question **pooled with run 2 under a stricter bar**.
- **Nothing exists yet:** no game has been selected, no position built, no label written and no bot or judge run for exam v2.

## 1. The games: a mechanical window
- **In:** every ranked game Dustin recorded **after** the last game in exam v1.6, through **Sunday Oct 25, 2026, 11:59 PM Central (04:59Z Oct 26)**, or the moment Dual Fusion is released in the game, if that is earlier.
  - v1.6's games are listed in exam_2026-10-19.json, commit 5518fd60, including its excluded and diagnostic game 20261015_210617000_iOS. The last is 20261016_031512000_iOS.
  - **Times** are the recordings' start times as their packets give them (SOURCE.json and the recording name), compared in UTC.
  - **"Ranked"** follows the review rules: a computer (Auto) battle, a rules test or a pause game is not a ranked game.
- **Out:** any game already in v1.6. No game is dropped for its result, deck, opponent or content.
- **The only exclusions are v1.6's written ones,** each listed with its reason in the selection record:
  - a recording that can't be used (no full review, a clip that starts mid-game, a mode not proven to be ranked);
  - no exact deck list (QR-verified, or matched card for card to a list in the repository);
  - developer exposure (someone who builds or runs the judge saw that game's answer material).
- **Pre-Dual-Fusion only.** The engine can't convert positions holding the new dual-type cards, so a game played after the release is outside the window by definition, not dropped.
- **Already known:** the candidate games known today are the 18 of Oct 19 (`BattleLogsData/Evidence/DRIVE_INBOX_2026-10-20`) and the 6 played Oct 16-17 (`DRIVE_LADDER_2026-10-19`, `DRIVE_LADDER_REMAINING_2026-10-19`). Each still goes through the rules above. Games he plays through Oct 25 are added the same way once Codex's reviews are complete.

## 2. The points: every usable decision, v1.6's written rules unchanged
- **A point is every one of his turns that is USABLE** under v1.6's inventory brief (`../build/INV_BRIEF.md`): board_known = yes, hand_known = yes, move_known = yes and real_choice = yes, coded from the game's full review (REVIEW.md and its metadata, text only).
  - "Partly" and "unclear" are not usable. Near-usable turns aren't used.
  - Any answer kind counts (prepare, attack now, sacrifice, abandon or other).
- **No discretionary picking.** v1.6's stage 2 (`../build/A_BRIEF.md`) chose 48-56 of its usable turns with quotas and preferences:
  - at most 4 per game;
  - Kingambit at most 35% of points;
  - every sacrifice and abandon turn;
  - at least 12 "attack now";
  - preferring unusual lines.

  Those quotas and preferences are **not** applied. Every usable turn becomes a point.
- **Building:** each point is built as in v1.6's stage 3 (`../build/A_BRIEF.md`, `../build/BUILD.md`), with the same legal-moves-only program that built v1.6, `~/exam/bin/pg_legal_v14` (sha256 dcefe4ea…). It never constructs a bot.
  - **Its source** is `~/exam/src_legal`, a copy of the stage-A pg_pos source with the legal-only mode (`../build/BUILD.md`).
  - **Its `engine/src` tree is 648f4137, not the frozen tree 70652fff's `src` (a52bafd9).** Cargo.lock is the same. v1.6 was built the same way.
  - What the judge and km3 see is re-derived at run time by the frozen lister and baseline on 70652fff. The formal compare refuses a plan list or recorded line that doesn't hold there.
  - No hidden future.
  - Every approximation is marked.
  - His whole recorded move must apply step by step.
  - A point that can't be built cleanly is dropped and listed with its reason, never padded.
- **The candidate view, the scoring scope, the chance-first and free-chance rules, the label format and the references** are v1.6's (`../README.md`, v1.2-v1.6 sections).
- **Labels use v1.6's adjudication exactly** (`key_rule`):
  - the key is what a good player of his decks would do, which by default is his recorded move;
  - the accepted alternatives carry reasons, and rejected alternatives carry `certified_by`.
- **Dustin's answers** to the unclear spots (v1.6 asked him 5) are recorded verbatim and frozen, with the whole exam v2, its references and its eligibility file, **before any bot or judge output exists for it**.
- **Who labels:** the labels are made by a fresh worker that hasn't seen run 2's per-point results, from the packets and v1.6's rules only. The laptop session, which has seen those results, does the mechanics: inventory plumbing, building, validation and freezing. It doesn't decide accepted alternatives. That's an extra safeguard beyond v1.6's procedure; the coordinator may change who labels before the work starts.
- **Exposure:** Sonnet, the judge's developer, never opens exam v2 or its keys. If anyone who builds or runs the judge sees a game's answer material, that game is excluded from the primary as in v1.6, kept and reported separately with a dated reason.

## 3. The independent selection check (before any bot runs)
- A FRESH credit-worker job that hasn't seen run 2's per-point patterns checks that section 1's window and section 2's rules were applied to every game in the window. The coordinator launches it when the laptop says the build is ready.
- It reports the category mix (deck, answer kind) and the share of chance-ending points next to run 2's.
- Its findings are fixed or answered before the freeze. No bot or judge runs until it has reported.

## 4. The primary result: runs 2 + 3 pooled, the FINAL stage of this series
- **Measure:** Gemini (the frozen-7 judge's primary call) minus km3 (mean over its 3 seeds), prefix agreement, on the primary points of run 2 (49 points, 26 games) and run 3 together.
- **The game is the cluster.** Run 2's and run 3's games are different games by construction.
- **Statistics:** analysis.py's estimator and resampling, unchanged except the level.
  - the game-clustered bootstrap, two-sided **97.5%** interval, seed 20261019;
  - the game-level sign-flip test, two-sided, Monte Carlo with 100,000 draws (exact enumeration only up to 16 games), seed 20261020;
  - at least 10 games.
- **PASS = the 97.5% interval lies entirely above 0 AND the sign-flip p < 0.025.** Anything else is not a pass.
- **The pooling script** combines the two runs' formal reports (each one's per-decision rows, as the formal compare accounts for them) and calls analysis.py's functions at that level.
  - It is written, tested and committed **before run 3's km3 or judge rows exist**.
  - The test: on run 2 alone at 95% it must reproduce run 2's `report_primary.json` contrast (+0.163265, −0.014184, +0.346939, p 0.108869) to the printed digits.
- **Said plainly:**
  - **Stage 2 was declared after stage 1 was seen.** Run 2 was planned as a single test; this second stage and its pooling were decided after its "inconclusive" result. That is why the bar is stricter.
  - **There will be no stage 3,** and no re-pooling on this question, until a bigger fresh set (50 or more new labelled games) exists.

## 5. Secondary results (reported, NOT deciding)
- **Run 3 alone at run 2's rule,** the clean replication: the formal compare's primary prefix verdict on run 3's points (95% game-clustered interval and sign-flip p < 0.05, at least 10 games). With fewer than 10 primary games, no verdict, as analysis.py says.
- **The chance-ending stratum on its own:** the points where an accepted line ends at a chance event (a draw, search or coin), counted as `../run1/RESULTS_run1.md` counted them. It is reported for run 3 and pooled, with its interval, and no verdict is drawn from it.
- **Also reported:**
  - the full-scope block;
  - the repeat (sensitivity, run 2's design);
  - the categories;
  - Gemini against run 1's Sonnet judge, where points overlap (none will, since run 3's points are new).

## 6. Fixed for both stages
- **The judge:** `judge-prompt-frozen-7` (712593a1) untouched: gemini-vertex, gemini-4-argon, location global, thinking HIGH, maxOutputTokens 32,768.
  - The prompt fingerprint is 0cb2421552661b563bdb49fca31aca53f468d0853661908fbbf7730fcb5ba762.
  - The project is passed as `--vertex-project project-45583ef0-ed57-426c-bde`.
- **Run 2's rules, as in `../run2/PREREG_RUN2.md` addendum 1:**
  - `compare --failed-judge-rows miss`;
  - the >20% no-choice reporting rule (A3), for run 3 and for the pooled set;
  - the resend rule (A4: a call with no model reply is re-sent once; a reply is never asked again);
  - one primary call per decision and a separate repeat for sensitivity.
- **Engine and builds: the same as run 2,** not the newly adopted main-4d48844 engine:
  - the frozen engine tree 70652fff03af511e32a169e16209e158a998dda6;
  - the lister bd4eeb6e…;
  - the baseline f35a1a99…;
  - for building the positions, v1.6's `pg_legal_v14` (dcefe4ea…; see section 2 for its source tree).
  - `freeze_identity.py --check` must pass on the tag before any call.
- **km3 is played fresh** on run 3's positions, 3 seeds, from a NEW seed block registered in START_HERE before the run.
  - The intended block is 25,101,000,000-25,101,999,999, with km3 seeds 25,101,000,001-003.
  - If START_HERE shows that block taken, the next free block is used. Either way it is registered before any run 3 row is made.

## 7. The model version
- Every judge row records the Vertex model version string the reply gives, and the date.
- Run 2's rows say "gemini-4-argon".
- **If any run 3 row says otherwise,** pooling is off: run 3 is reported as a new series, under section 5's single-run rule only, and section 4 isn't computed.

## 8. The sentences, written now
- **If the pooled result is not a pass:** "promising, unproven; revisit when 50+ new labelled games exist".
  - With the >20% no-choice rule triggered, instead: "inconclusive about skill: too many failed replies".
- **If it passes:** "Gemini is a better plan picker than km3 on his decisions".
  - The formal kx3 test (frozen-5) still comes before anyone says it beats our best bot.

## 9. Budget
- A **$15 ledger** from Dustin's Google Cloud trial credits, under his standing OK: the primary run at `--total-usd 15 --run-cap-usd 15`, the repeat on what remains, the same per-call worst-case reservation.
- Actual spend (the replies' usage fields at the cited price) is reported apart from the reservations and from the estimate.
- No smoke calls: frozen-7 is unchanged.

## 10. Order and who
1. This file, committed and pushed on `sonnet/exam-2026-10-19` (`run3/`) before any selection. Mailboxed to the coordinator.
2. **The window closes** Oct 25, 11:59 PM Central, or at Dual Fusion's release. Codex completes the reviews.
3. **The build** (light, daytime): the usability coding per section 2 (inventory), the positions with `pg_legal_v14`, the validation, the labels (a fresh worker), and Dustin's answers.
4. **Before any bot or judge output:**
   - the independent selection check (section 3);
   - then the freeze: exam v2, references, eligibility and the pooling script, committed.
5. **The runs:** km3 rows (new seed block); then the judge (API only); then the formal compare on run 3, the pooled primary and the secondaries.
6. Results to the coordinator only, as `RESULTS_run3.md` here.


---

## Addendum 1 (Oct 21, 2026, about 21:00Z; the coordinator's review of the above, before any selection)
The coordinator accepted the five choices reported in laptop-021, and added the following. Nothing has been selected, built or run.

**B1. What the pooled result is about.** The pooled population mixes v1.6's curated points (run 2's 49, chosen with v1.6's quotas) with run 3's all-usable points. So the pooled contrast is about that mixture, not about either selection alone. The run-3-alone secondary (section 5) is the clean replication. The comparison stays paired within points and clustered by game.

**B2. Reported next to run 2's** (descriptive, with the result and with the selection check):
- the category mix (deck, answer kind);
- the chance-ending share;
- the number of points per game.

**B3. The labelling job** replaces section 2's "a fresh worker":
- It is a fresh credit-worker job (`claude -p`, the coordinator's API credits). The laptop drafts its prompt and the coordinator launches it.
- **It gets only:**
  - v1.6's adjudication rules: the inventory brief, the label brief, and the key-line, accepted-alternative, rejection, draw-first and segment rules, restated without any of v1.6's point answers;
  - run 3's positions with the engine's legal lists;
  - Dustin's recorded plays;
  - the games' reviews and his deck lists.
- **Off-limits:** run 1's and run 2's results, any other references, the exam branch's results folders and the judge's files.
- Dustin's answers to its unclear spots are folded in before the freeze.

**B4. The selection check** (section 3) is a SEPARATE fresh credit-worker job. The laptop drafts its prompt and the coordinator launches it.


## Addendum 2 (Oct 21, 2026, about 21:20Z; the coordinator's decisions on laptop-022, before any selection)
**C1. Exposure, worded as decided by the coordinator.** This replaces section 2's "anyone who builds or runs the judge".
- Exposure means the judge's developer (Sonnet), or anyone who could alter the judge. frozen-7 can't be changed by the run.
- The builder's and runner's reads of the reviews are recorded, not exposure.
- A game whose answer material reaches the judge's developer is excluded from the primary, as in v1.6.

**C2. Reads of the candidate games' reviews before this addendum, recorded.** None of these readers is the judge's developer, and none can alter frozen-7.
- **Oct 20-21, the brew 07 read** (mailbox `coordinator__20261021T0125Z-laptop-016`, the coordinator's side job: a read of his brew 07 games plus notes on his other decks).
  - The laptop session and its workflow agents read Codex's REVIEW.md of all 18 Oct 19 games (DRIVE_INBOX_2026-10-20): the 9 brew-07 games, the 7 "Muk it up" games and the 2 Dragonite/Goodra games.
  - That read checked six of his brew-07 decision points against what he could see and the point race, and found no misplay.
- **Oct 21, the read-only inventory** (workflow wf_e56c132e-175, mailbox laptop-022):
  - the games agent read the packets of all 24 candidate games (REVIEW.md, FINDINGS, LEAD_ACCEPTANCE, LADDER_ENTRY, QR, COVERAGE, UNCERTAINTIES and SOURCE);
  - the yield agent read all 24 REVIEW.md files in full and estimated usable turns per game, without recording which turns;
  - the import-path agent opened 2-3 packets from each batch;
  - the cross-check read the packets of 21-57-12 (its full FINDINGS timeline), 10-01-14 and 13-46-35.
- **Oct 21, the laptop session itself:**
  - read the card lists in the 18 Oct 19 QR files, and printed part of one (19-08-57);
  - listed the packet folders.

**C3. The usability coding is a third fresh credit-worker job** (`jobs/INV_JOB.md`), approved by the coordinator. Under section 2's no-picking rule it decides the points, so it isn't done by the laptop session. The three jobs (usability coding, labelling, selection check) and `jobs/ADJUDICATION_RULES.md` are reviewed by the coordinator at launch, after the cutoff.

**C4. Sources:**
- Exam v2 cites a hash-checked snapshot of the accepted packets, taken at the cutoff, on this branch (`run3/sources/`). Each top-level REVIEW.md must equal the hash its packet pins.
- Main's importer is unchanged for now. Its silent skip of the new layout is logged by the coordinator as a separate fix.


## Addendum 3 (Oct 21, 2026; the coordinator's ruling on the exact deck lists, coordinator-024 (mailbox id 20261021T2315Z), before any selection)
Nothing has been selected, built or run. The window is still open.

**D1. The exact-list rule, as run 3 applies it.** This spells out section 1's "no exact deck list (QR-verified, or matched card for card to a list in the repository)". It adds no route.
- **QR-verified:** a game's list is exact when all three hold:
  - a deck code (QR) filmed in that game's own recording, before the battle, decodes to a full 20-card list (card entities, quantities and Energy);
  - the footage from the code to matchmaking shows that this list is the one played: no card editing and no deck change in between;
  - the accepted full review's visible cards agree with it.
- **Or matched:** the game is matched card for card to a list in the repository.
  - No game uses this route so far. Before one does, the laptop asks the coordinator, with the match and its evidence.
  - `make_sources_snapshot.py --extra-decks` only checks that the named deck file is in `decks/DECKS.json` with its recorded hash, and that it agrees with any filmed or exact-list code. The card-for-card match itself is a judgement, not a script check.
- **A list Dustin supplies counts only through one of these two routes.** Any other route needs the coordinator's ruling before selection.
- **A code names the card, not the printing** (artwork, rarity). The deck file writes each card as one printing in the frozen tree's database: the printing the repository's decks use most, else the first released (`make_v2_decks.py`). Printings of one card play the same.
- **A binding with a recorded limit** counts as exact when the coordinator rules so, before any selection. The limit is written with the game (`decks/RULINGS.json`, carried into `window.json`).

**D2. The ruling, verbatim (coordinator-024):** "all seven count as EXACT lists under run 3's deck rule. That includes 21-57-12, with its limit recorded in the record: "decoded QR plus continuous footage of Cancel, the saved rename and selection; the saved list was not reopened"."
- **The seven.** At Dustin's request, Codex read the pre-game QR codes of the six Oct 16-17 games and of 21-57-12. Its findings, as relayed by Dustin, verbatim (recording names in Chicago time):
  - "Oct 16 13:46:35 and 15:05:34: the same list, including Regigigas."
  - "Oct 17 09:51:04 and 10:01:14: the same list, 2 Hoopa ex and 1 Claydol."
  - "Oct 17 10:05:09: changed to 1 Hoopa ex and 2 Claydol."
  - "Oct 17 10:13:06: no Regigigas; includes X Speed, Poison Barb and Cyrus."
  - "The six Oct 16-17 lists are linked to the played decks by continuous selection footage, with no mismatch seen."
  - "Oct 19 21:57:12: the exact "Muk it up" list was decoded. The footage shows Cancel on the discard prompt, then loading, the saved rename and the selection of "Muk it up". No full saved list is reopened afterward."
- **The effect:** the six Oct 16-17 games are no longer excluded for want of an exact list. 21-57-12 keeps its list, with the limit recorded.

**D3. The sources.** At the cutoff, the snapshot copies into `sources/QR_EXACT_LISTS_2026-10-21/`:
- per recording, the seven text files of Codex's targeted addendum, where present: QR_DECODE, BINDING, LEAD_ACCEPTANCE, INDEPENDENT, ADDENDUM, REVIEW and SOURCE (from `BattleLogsData/Evidence/QR_EXACT_LISTS_2026-10-21/<drive id>/`);
- six named files of their summary folder (`Battle Logs/Recording_QA/QR_EXACT_LISTS_2026-10-21/`), under `_summary/`.

These text files carry no sha256 pin of their own. So `make_sources_snapshot.py` checks them and stops on any mismatch:
- **The run needs all three inputs:** `--exact-lists`, `--exact-summary` and `--rulings`. A run without them would record the six Oct 16-17 games as having no exact list.
- **The summary:**
  - SUMMARY_DRIVE_VERIFICATION.json names exactly the two Drive copies Dustin linked, under his Drive ids, marked verified;
  - the local EXACT_DECKS.json and EXACT_DECK_LISTS.md have the md5 and size Codex recorded there for those copies. The check is against Codex's record of the Drive copies; nothing reads Drive itself.
- **The recording folders** are exactly EXACT_DECKS.json's recordings.
- **Per recording:**
  - the folder name is QR_DECODE's Drive id;
  - the QR payload equals EXACT_DECKS's;
  - the video's sha256 is one value in QR_DECODE, LEAD_ACCEPTANCE, SOURCE and EXACT_DECKS, and equals the reviewed packet's own SOURCE.json and LEAD_ACCEPTANCE (both required), so each list belongs to the reviewed game;
  - BINDING.json equals BINDINGS.json's entry;
  - the QR image's sha256 equals the filmed frame's (evidence/QR_NATIVE.jpg);
  - the game's deck (its code in `decks/DECKS.json`) is that QR's code.
- **The ruling** (`decks/RULINGS.json`) must cover exactly these recordings, as exact, with Codex's list letter and the packet's recording name. It carries the one limit coordinator-024 records, in the ruling's words, on 21-57-12.
- **The snapshot also stops when:**
  - a deck from a targeted addendum is used without these checks;
  - a game has two lists;
  - an `--extra-decks` entry matches no game or no recorded deck file;
  - a drive id or a video's sha256 is in two packets (one game counted twice);
  - a clip of a battle recorded in several clips is in the window (D6);
  - the output folder isn't fresh.
- Every copied file's sha256 is recorded in `window.json`. A stop can leave a partial copy in the worktree, and nothing is committed after a stop.

**D4. The deck files** (`decks/`, from `make_v2_decks.py`):
- The seven codes decode with the deck journal. Every card has a printing in the frozen tree's database (70652fff), and each file's 20 cards and Energy equal its code's.
- **4 new files:**
  - `v2deck_5cef509bea` (Oct 16, both games: Codex's list A);
  - `v2deck_03c584b95c` (Oct 17 09:51 and 10:01: B);
  - `v2deck_9d2c3c7ccf` (10:05: C);
  - `v2deck_5c3566c961` (10:13: D).
- 21-57-12's code from Codex (E) equals the one its own packet already gave (`v2deck_438090ee3c`). That file's `weak` flag repeats its first QR file's own note; this ruling, not the flag, decides that it is exact.
- **In all:** 12 deck files, 12 distinct lists, for the 24 games with packets in the three batches so far. The 8 earlier files are unchanged byte for byte.
- One synthetic position per deck file loads in `pg_legal_v14` with no position problem (`build/smoke_v2.py`). The only new chance card is Mesagoza, whose coin is v1.6's UseStadium rule.
- **The snapshot's dry run** (Oct 21, into /tmp only, on DRIVE_INBOX_2026-10-20, DRIVE_LADDER_2026-10-19 and DRIVE_LADDER_REMAINING_2026-10-19): 24 packets in the window, 24 in, 0 excluded.
  - At that time the review index listed 10 Oct 20 recordings in the window with no packet in those three batches:
    - 2 (17-23-26, 17-54-38) are a linked computer rules test, not ranked. Their packets are in the LUXRAY_ESPATHRA_* folders.
    - 8 are in a new batch, `DRIVE_INBOX_2026-10-21`, under review then.
  - Later on Oct 21 the metadata (LEAD_ACCEPTANCE, SOURCE, QR_ID; no review was read) shows:
    - 4 standalone ranked games, each with an accepted full review and a decoded QR (21-09-16, 22-09-39, 22-11-41, 22-17-16);
    - one ranked battle recorded in two clips, 21-00-59 and 21-07-01 (D6), with an accepted full review of the whole linked battle;
    - one linked pair, 22-23-24 and 22-26-30, with a partial review only.
  - The cutoff run passes every batch that holds his ranked games, `DRIVE_INBOX_2026-10-21` included.

**D5. Reads, recorded** (C1: not exposure).
- **The laptop session, Oct 21:**
  - Codex's exact-list files: the QR payloads, bindings, acceptance records, SOURCE files and the summary folder;
  - the decoded card lists;
  - `DRIVE_INBOX_2026-10-21`'s metadata (LEAD_ACCEPTANCE, SOURCE, QR_ID status, whether RELATED_SOURCES exists);
  - the index rows of Oct 20.
- **The read-only verification workflow `wf_5a33f406-b62`** (Oct 21; 19 agents: five checks and an adversarial verifier per should-fix finding, 14 in all):
  - It read the same exact-list files, the original packets' SOURCE.json, LEAD_ACCEPTANCE.json and QR_ID.json, the deck files and the dry-run window records.
  - It ran copies of the scripts on the evidence read only, with changed inputs copied.
- **The read-only re-check `wf_db42117b-1bf`** (Oct 21, 9 agents):
  - It read the same kinds of files, plus `DRIVE_INBOX_2026-10-21`'s LEAD_ACCEPTANCE, SOURCE, QR_ID and RELATED_SOURCES and the index rows.
  - Its runs hashed, but did not open or copy, that batch's REVIEW.md and FINDINGS for the pin check.
- Both workflows were told not to read any window packet's REVIEW.md or FINDINGS.
- None of these readers is the judge's developer, and none can alter frozen-7.

**D6. Open, for the coordinator before the cutoff: one battle recorded in several clips.**
- **The case:** section 1 counts recordings, and v1.6 excluded "a clip that starts mid-game". `DRIVE_INBOX_2026-10-21` now holds a ranked battle split across two recordings:
  - 21-00-59 is the opening clip, with the QR;
  - 21-07-01 continues it, with no QR of its own;
  - Codex reviewed them together as one game (SOURCE.json battle_id `drive-inbox-20261021-game01`, clip_order 1 and 2; LEAD_ACCEPTANCE "Whole linked ranked battle").
- **Neither mechanical reading is right:**
  - counting both clips makes one battle two games (two clusters);
  - dropping the second clip as having "no exact list" gives a false reason.
- **Until the coordinator rules,** both scripts stop on such a clip: `make_v2_decks.py` on a QR file with only a linked payload, and `make_sources_snapshot.py` on a battle_id, a clip_order or a RELATED_SOURCES.json.
- **The laptop's proposal is in laptop-023:** one game per linked battle, made of its clips, with:
  - the opening clip's QR as its list (a continuation's linked payload must equal it);
  - its points drawn from the whole linked review;
  - the battle as the cluster;
  - the first clip's start time as its time.
  
  A linked battle whose review is only partial stays excluded ("no accepted full review").


## Addendum 4 (Oct 22, 2026; the coordinator's ruling on a battle recorded in several clips, coordinator-027 (mailbox id 20261022T1310Z), before any selection)
Nothing has been selected, built or run. The window is still open. This settles addendum 3's open item D6.

**E1. The ruling (coordinator-027), verbatim in the parts that set the rule:**
- "one game per linked battle (Codex's battle_id), made of its clips;"
- "the opening clip's QR is its list, and each continuation's linked payload must equal it;"
- "its points come from the whole linked review;"
- "the battle is the cluster;"
- "the first clip's start time is its time."
- "The change: a recording that ENDS early still counts. The 22-23-24 + 22-26-30 battle ends before the finish, but its opening is recorded. Include it, and let its turns go through the same per-turn usability rule (board, hand and move known, and a real choice); the missing ending only removes later turns."
- "v1.6's exclusion was for a clip that STARTS mid-game, where the state is unknown, and that stays."
- "A battle with NO recorded opening, or no exact list, stays excluded as before."

**E2. How the scripts apply it.**
- **A battle:**
  - is the clips that one battle_id names; the scripts read the battle id from SOURCE.json, its recording_relationships or RELATED_SOURCES.json (Codex uses all three so far), and the clip list from RELATED_SOURCES.json;
  - makes ONE game, in clip order;
  - takes its start time, its packet name and its list from the opening clip (clip 1).
- **The run stops when:**
  - a recording shows a clip relationship (a clip order, a linked or not-visible QR, a LINKED_*_QR_ID.json, or RELATED_SOURCES.json) but names no battle;
  - the clips' listings differ, or a clip's order isn't a whole number;
  - the clip orders are not 1..n, or the clips don't start in that order;
  - the packets naming a battle are not exactly its listed clips (a listed clip missing from the given batches, or a stray packet);
  - a present clip is not the recording its listing names (video sha256);
  - a game or continuation that DECKS.json knows isn't placed in the window record as a game's opening or a later clip of its battle.
- **A continuation's code:**
  - its linked code (`linked_payload`, or the linked QR file it names, `LINKED_*_QR_ID.json`) must equal the opening clip's own code (`make_v2_decks.py`, which then lists it under the opening's game in DECKS.json);
  - the snapshot stops unless DECKS.json ties exactly the battle's other clips to the opening's game;
  - a continuation is never a game of its own.
- **The review:**
  - every clip must be accepted and ranked;
  - a clip's review is complete or partial (Codex marks it partial when the footage misses part of the battle; here, the ending);
  - a game with a partial review counts when its opening is recorded. The scripts take the first clip carrying its own filmed deck code as the sign that the opening is recorded. The game is flagged in the record (`partial_review_note`), and per-turn usability later removes the turns the recording lacks;
  - without a recorded opening it is excluded as "a recording that starts mid-game".
- **The record:** `window.json` lists a battle's clips with each clip's copied files and their sha256, and the duplicate checks cover every clip. RELATED_SOURCES.json and any LINKED_*_QR_ID.json are copied with the other text files.
- **The laptop's reading, for the coordinator to confirm before the cutoff:** the ruling names a recording that ends early. The scripts apply the same test (opening recorded; usability removes the rest) to any accepted partial review. Every such game is flagged for the selection check. So far the only partial game is the 22-23-24 battle, which is the ruled case.

**E3. The case record.**
- **`drive-inbox-20261021-game01`** (DRIVE_INBOX_2026-10-21):
  - clip 1 is 21-00-59 (1Pe3…, its own opening QR);
  - clip 2 is 21-07-01 (11nTG…, `linked_payload` equal to clip 1's code);
  - one accepted full review of the whole linked battle.
  
  It is one game: deck `v2deck_5309993874` (Darkness), start 2026-10-21T02:00:59Z.
- **`DRIVE_INBOX_2026-10-21-game06`:**
  - clip 1 is 22-23-24 (1oPEd…, its own opening QR);
  - clip 2 is 22-26-30 (1RlG7…; its LINKED_CLIP07_QR_ID.json holds clip 1's code);
  - an accepted partial review ("confirmed win with genuinely unrecorded later gameplay").
  
  It is one game: deck `v2deck_4fa967805c` (Mega Sharpedo ex / Wailord / Claydol), start 2026-10-21T03:23:24Z, flagged partial.
- These are two different battles. For each, both clips' packets are copied into the snapshot, and the usability coding reads them as one game.

**E4. The window so far.** This is a dry run (Oct 22, into /tmp only) with all five batches that hold his ranked games: DRIVE_INBOX_2026-10-20, DRIVE_LADDER_2026-10-19, DRIVE_LADDER_REMAINING_2026-10-19, DRIVE_INBOX_2026-10-21 and DRIVE_LADDER_2026-10-21_EVENING.
- 38 games (40 recordings; 2 linked battles): 38 in, 0 excluded.
- 14 deck files, 14 distinct lists. The 12 earlier files are unchanged byte for byte.
- **The 2 new lists:**
  - `v2deck_5309993874`: Darkness, 2 games, Oct 20 evening Central time (02:00-02:09Z Oct 21): the game01 battle and 21-09-16;
  - `v2deck_4fa967805c`: Water, Mega Sharpedo ex / Wailord / Claydol, 12 games: 4 on Oct 20 evening (03:09-03:23Z Oct 21) and 8 on Oct 21 (20:47-22:56Z).
- Every card is in the frozen database, and all 14 deck files load in `pg_legal_v14`. They were built against main b78c8997's deck files (the printing choice) and copied into the builder's `~/exam_v2/decks`. At the cutoff, the rebuilt files must equal these byte for byte, except for any new list.
- **A new chance card:** Wallace (B3b 068). In the frozen engine it works as Quick-Grow Extract does: playing it isn't the chance; its ChooseRandomEvolutionTarget is. So the cut already stops there, and `build/v2_helpers.py` adds `Play:Wallace` beside `Play:Quick-Grow` for the after-chance check.
- The review index's in-window rows without a packet are only the two Oct 20 rules-test recordings (17-23-26, 17-54-38), which are not ranked.
- The cutoff run passes every batch that holds his ranked games, the later ones included.

**E5. Tests.** `test_snapshot_guards.py` has 14 tests, all OK. The new ones:
- a linked battle is one game;
- a battle missing a clip stops the run;
- DECKS.json must tie the continuations;
- a partial game without a recorded opening is excluded;
- a continuation with another code stops `make_v2_decks.py`;
- a battle whose RELATED_SOURCES.json is gone stops the run;
- a stray packet naming a battle stops the run.

`build/test_v2_helpers.py` has 11 tests (Wallace added), all OK.

**E6. Reads, recorded** (C1: not exposure). None of these readers is the judge's developer, and none can alter frozen-7.
- **The laptop session, Oct 22:**
  - the new batches' metadata: LEAD_ACCEPTANCE, SOURCE, RELATED_SOURCES and the QR files. The RELATED_SOURCES and continuation QR files of both linked battles hold some battle text: the board, hand and score at the clip boundary, game06's binding note and its missing-ending note. That text was printed and read.
  - the deck read's per-game extracts (Claydol facts) and its draft.
- **The read-only verification workflow `wf_f62c03bf-cba`** (Oct 22, 9 agents):
  - read the same metadata, the deck files, the window record, coordinator-027 and the frozen engine's source;
  - read Codex's QR_EXACT_LISTS BINDINGS.json lines;
  - ran copies of the scripts on copies of the inputs (metadata and pin files only);
  - was told not to read any REVIEW.md, FINDINGS or COVERAGE.
- **The Mega Sharpedo deck read** (coordinator-026; workflow `wf_294c1154-42e`, Oct 22, 6 agents: three readers, a drafter, an exam-safety check and a fact check):
  - The readers read the 12 Mega Sharpedo games' packets (REVIEW.md, FINDINGS.json, COVERAGE.md, LADDER_ENTRY.json, LEAD_ACCEPTANCE.json; both clips of the 22-23-24 battle) and extracted deck-level facts only.
  - The fact check reopened some of those REVIEW.md files to confirm counts.
  - They were told never to judge a decision of his, and the exam-safety check removed every phrase that could steer a label.
  - The read itself (to the coordinator, laptop-025) gives deck-level counts and card swaps only, with no turn-by-turn assessment.

**E7. E2's reading, resolved (coordinator-028, mailbox id 20261022T1730Z, before any selection), verbatim:**
- "Any accepted partial review whose OPENING is recorded counts. Per-turn usability (board, hand and move known, and a real choice) removes whatever turns the gap or the missing ending leaves unknown."
- "The turns right after a mid-game gap are usable only if the coder can establish the full state at that turn, including any lasting turn effects and the Supporter/Energy/retreat use so far that turn. Otherwise they're not usable."
- "Each such game is flagged for the selection check, as you have it."

The scripts already apply the first and third points (E2). The second is a rule for the usability coding: it goes into the usability job's prompt (`jobs/INV_JOB.md`) at its launch.

## Addendum 5 (Oct 24, 2026 UTC; the advisor's blind review of run 3's machinery, coordinator-034 (mailbox id 20261023T2230Z), before any selection and before the position build)
Nothing has been selected, built or run. The window is still open through Oct 25, 11:59 PM CT (04:59Z Oct 26).
- **The review:** the advisor (Fable) reviewed run 3's labelling and selection machinery at exam tip 9c85ac8d, read-only and blind. Apart from the disclosure in G0, it saw no references, no run 1 or run 2 results and no move lists.
- **The verdict:** no blocker in the design.
- **The coordinator accepted all ten findings (F1-F10).** This addendum records how each is applied (G1-G10), records the mechanics added since addendum 4 (M1), and PROPOSES one rule (R1).
- **Before filing,** this work had an independent read-only review (two agents) and a re-check (two agents), and their findings were fixed. The laptop session's own items were marked "proposed"; the coordinator accepted all of them on Oct 24 (G13).

**G0. Exposure record** (worded as C1 and C2; not exposure: the advisor is not the judge's developer and can't alter frozen-7).
- The advisor read `../README.md`'s v1.5 table. That table names five v1.6 points (Dustin's five answered questions) and their keys.
- Those are v1.6 points, not run 3's. Run 3's games, positions and labels don't exist yet.

**M1. The mechanics added since addendum 4, recorded here for the first time.** All were set before any v2 position exists.
- **Dustox B4 005's Variety Powder** is a chance step, followed by slot (build/v2_helpers.py since aaa40b5c, Oct 21).
- **Since 9c85ac8d** (Oct 23):
  - Fragrant Forest's `UseStadium` is a chance step (the frozen engine searches the deck);
  - Lusamine's `AttachFromDiscard` is a chance step when the discard holds 3+ Energy of 2+ types (the frozen engine's forecast_attach_from_discard branches);
  - Big Malasada is NOT a chance step, although its text removes "a random Special Condition": the engine forecasts one outcome and picks inside it, so neither frozen-7's lister nor pg_legal_v14 stops there. Accepted as a consequence of R1 (G13, item 5).
- **Wallace** is as recorded in addendum 4 (E4).
- **The Oct 23 batch** (DRIVE_LADDER_2026-10-23, 15 games, 16 recordings; 9c85ac8d) brought two new layouts, now read:
  - a continuation's `linked_qr_metadata` given as an absolute Windows path to the opening's QR_ID.json;
  - RELATED_SOURCES.json with `battle_key` and `chronological_sources`.
- **Its six new lists** took the deck files from addendum 4's 14 to 20:
  - v2deck_589bb9927a (Water, 4 games);
  - 4af97d2795 (Water, 2);
  - 693850eaa5 (Water, 1; the third linked battle);
  - f5671a4e7f (Water, 1);
  - 6328cc45fe (Grass, 3);
  - ba2eca5816 (Grass and Fighting, 3).
- **That dry run:** 53 games, 56 recordings, 3 linked battles, 53 in.

**G1. Drops only with evidence (F1).** A point is dropped ONLY with verbatim tool output that forces it. The evidence is either:
- the pg_legal output (at build: an illegal recorded action, or a label it can't match), saved as `build_drops/<point id>.txt`; or
- frozen-7's lister-check row on the point's KEY line (G2: the line reaches no single listed plan, matches ambiguously or can't be read), or a capped plan list.

A summary of the lister-check evidence (problem types and step counts, never a label) goes to the selection check as `lister_drops/<point id>.txt`. There are no other discretionary drops. Section 2's "a point that can't be built cleanly is dropped" now means exactly this.
- **The drop count** is reported next to v1.6's, in the selection check's mix and in RESULTS_run3. v1.6 dropped 3 at build (`../build/BUILD.md`, "Points dropped, and why"): one for a list problem, and two because their "cost [was] judged too high", which G1 no longer allows.
- **An accepted ALTERNATIVE that fails** is removed from its point, with its output recorded; the point keeps its key. That covers a lister-check failure (no_plan, ambiguous or unreadable on an alternative's line), which is settled this way. It also covers a pg_legal validation failure (ADJUDICATION_RULES section 3; accepted, G13 item 2).
- **A line `cut()` can't follow** (v2_helpers.Uncertain) is never cut by hand. Under R1 its first segment is the lister's, from its check row.
- **`validate_v2.py`'s `stop_differs`** is reported only, never a drop reason.

**G2. The frozen-lister check before the freeze (F2).** `check_lister_v2.py` runs on EVERY v2 point.
- **Identity:**
  - frozen-7's `freeze_identity.py --check` must pass in a checkout of the tag judge-prompt-frozen-7;
  - then the checkout's commit must be the tag's, FROZEN.json must name the tag and frozen-7's prompt fingerprint (0cb24215…), and the lister binary that judge.py runs must have FROZEN.json's sha256 (bd4eeb6e…), the formal compare's own test.
- **What it runs:** frozen-7's own plan lister and frozen-7's own replay matching (`judge.match_plans`, the function the formal compare uses). It runs on the candidate view only (G5).
- **What it checks**, for every accepted line, the key included:
  - the line must reach exactly one listed plan, and no list may be capped;
  - the lister's segment is the line up to the step that is that plan's own last step (labels compared as the lister compares them; a step the engine forces is allowed);
  - `cut(line)` must equal that segment: when the plan stops inside the turn, `cut()` stops at the same step; when the plan ends the turn, `cut()` keeps the whole line.
- **The verdicts**, per accepted line:
  - pass;
  - `resolved_by_R1` (cut_differs or uncertain_cut: R1 gives the segment);
  - `remove_alternative` (a failure on an alternative's line, G1);
  - `drop` (a failure on the KEY line, whose reference id is `recorded`, `key` or `his`; or a capped list).
- **It refuses** a point with no references, a reference with no labels, a duplicate position, and a point whose references hold no key line (exit 1).
- **The order of the steps.** These replace section 10's steps 3-4: Dustin's answers now come after the selection check.
  1. build;
  2. labels;
  3. the lister check, first pass;
  4. the selection check, Part A then Part B (G3);
  5. Dustin's answers folded in;
  6. the lister check re-run on the final references;
  7. `build/validate_v2.py` on the assembled exam, which needs the final answers and any lister segments;
  8. the freeze.

  A drop found at step 6 or 7 reaches no selection check, so it is reported with its verbatim row in RESULTS_run3.
- **The report** holds accepted lines (answer material). It is kept with the frozen references, and is never staged to a worker; only `--drops-out` summaries are.
- **A failing point** is resolved by R1 (if accepted) or dropped by G1. Nothing is fixed by judgement, and nothing at all is fixed after any km3 or judge row exists.
- **Trial on v1.6** (machinery only; nothing scored; 3 s; this paragraph stays out of every excerpt staged to a worker):
  - 51 points, 67 accepted lines; the identity gate passes. All 67 lines reach a listed plan.
  - With v1.6's own `cut()`, 5 lines on 4 points stopped later than the lister: at Sabrina (where the opponent must choose a new Active, which the lister ends as "opponent_choice") and at Team Rocket's Raticate ex's Thieving Incisors (a random Energy; the lister stops at it even with one Energy on the opponent's Active).
  - With the present `cut()`, all 67 pass.
  - The PRIMARY prefix result of runs 1 and 2 doesn't depend on the first segment. frozen-7's formal.py (`map_references`; `full_plan_agreement`, lines 440-443: "order of moves up to the plan's own end not mattering: that is prefix agreement") matches each line to its plan by plan identity, and all 67 lines reached their plan.
  - On those 4 points the first segment affects only their scope label (full/partial/none) in the secondary full-scope reading. v1.6 stays frozen and nothing is re-scored. The coordinator decides whether run 2's record notes it.

**R1 (proposed by the laptop session, Oct 24 UTC; ACCEPTED by the coordinator, G13). The first segment follows frozen-7's lister.**
- **The rule:** the scored first segment of an accepted line is exactly where frozen-7's plan lister ends the plan that line reaches. That is at its first chance event (the lister's own test: a forecast with more than one branch, hidden information, or a change to his own deck) or at its first step after which the OPPONENT must act (Sabrina's new Active; a promotion after a knockout during the turn, for example by Darkrai ex's Nightmare Aura). Otherwise it is the whole turn.
- **How it is applied:**
  - `check_lister_v2.py` computes the segment for every accepted line from frozen-7's own replay;
  - `build/v2_helpers.cut()` predicts it for the known cases (v1.6's rule, M1's cards, Sabrina in 4 of the 20 v2 lists, Raticate's Ability);
  - where the two differ, the assembly records the lister's segment for that line in `answer.lister_segments`. It is keyed `his` / `key` / `alt<i>`; the assembly maps the references' ids to these (v1.6 calls his move `recorded`). `validate_v2.py` checks each entry is a non-empty prefix of its line, and checks the stops against it. The field is in LEAK_KEYS, so it can never reach a candidate. There is no judgement and no per-point decision.
- **If R1 is not accepted:** `cut()` reverts to v1.6's rule plus M1 (`OPPONENT_CHOICE_PLAYS` empty, Raticate out of `CHANCE_ABILITY`), and the check's cut_differs and uncertain_cut rows become G1 drop evidence.
- **The basis:** the v1.6 trial (G2) and a card-text audit of the 20 v2 lists (every Ability and Trainer text). No v2 game data, position or label exists.
- **What it amends:** section 2's "the chance-first and free-chance rules ... are v1.6's" and ADJUDICATION_RULES section 3. v1.6's first segment had no opponent's-choice stop and didn't know Raticate's Ability.
- **Its effect on the secondaries:**
  - a segment that ends at an opponent's choice is NOT chance-ending (section 5's stratum counts chance events only);
  - in every pooled secondary, run 2's points keep v1.6's recorded segments and scope labels.

**G3. The disagreement rule (F3).** A turn is usable ONLY if BOTH the usability job (`jobs/INV_JOB.md`) and an independent second coding call it usable. The rule is symmetric and conservative.
- **The second coding is blind:** the selection check is now two jobs (`jobs/SELCHECK_JOB.md`).
  - Part A codes every one of his turns from the reviews and a bare turn list, and sees neither the first coding, the selection, the labels nor any mix.
  - Part B checks the window, the selection and the mix, with both codings.
- **Ties and disputes** never go to anyone who has seen run 2's per-point results: not the laptop session, and not the coordinator as decider of a point.
- **The mechanical rules** for the selection check's other findings:
  - a turn both codings call usable that is missing is built;
  - a turn not called usable by both is not a point;
  - a drop without its G1 evidence is reinstated and built;
  - a missing in-span ranked game is added;
  - an exclusion that doesn't hold gets its written section 1 rule applied;
  - an included game that a written reason excludes is excluded with that reason;
  - a confirmed turn-list problem (Part A's `turn_list_problems`, checked by Part B) is fixed in the turn list, and both codings code that turn.
- **Anything else** that would need judgement goes to a fresh job that hasn't seen run 2's per-point results, or the point is dropped by rule.
- **Game-level window questions** (in span, ranked, linked, list) are ruled by the coordinator from metadata only (G13, item 3).

**G4. Dustin's answers (F4).**
- For v2, `certified_by` allows only `dustin` and `coordinator_decision_from_his_words`; there is no `coordinator_interpretation`.
  - `build/v2_helpers.check_certified_by` refuses anything else, including a rejected alternative without `certified_by`;
  - `build/validate_v2.py` runs it on every answer;
  - `jobs/ADJUDICATION_RULES.md` says the same.
- His answers are collected before anyone describes run 2's or run 3's per-decision patterns to him. The coordinator holds to that.

**G5. Answer fields never reach a candidate (F5).**
- `build/v2_helpers.P` keeps build-only and answer fields on the built position: `kind`, `force`, `_draws`, `_vpatch`, `notes`, `approximate_reason`.
- **A requirement on the v2 assembly**, which is not yet written: every exam position is written as `candidate_view(built)`, and every answer passes `check_certified_by`.
- `candidate_view()`:
  - keeps `CANDIDATE_FIELDS`, drops `ANSWER_FIELDS`, and refuses a field in neither list;
  - `check_candidate()` reads the view as it will be written (a JSON round trip). It refuses an answer key at any depth (run 1's and run 2's LEAK_KEYS, these fields, and the answer file's own field names), and refuses his move's labels or the builder's text in any text of the view. A label without `:`, `@` or `#`, such as EndTurn, counts only as a whole text.
- **Before the freeze,** `build/validate_v2.py` re-runs `check_candidate(exam position, build record)` on every point. It stops on any leak, and on any point without a build record.
- **A residual, accepted with two guards (G13, item 6):** `opp_ambiguous`, `turn_effects`, the board's `effects` and `stadium` hold facts of the position from the review, written in the builder's words. `check_candidate` refuses his move's labels and the builder's notes in them, but their wording is the builder's; the alternative is a fixed vocabulary.
- **The labelling job** sees `label_view(built)`: the candidate view plus `his_move`, never the builder's `notes`, `approximate_reason` or `kind`. The builder, the laptop session, has seen run 2's per-point results.
- **The change from v1.6:** v1.6's candidate view kept `notes` and `approximate_reason`; v2's drops them, and `approximate` stays as a flag. frozen-7's judge code reads none of the three fields. This is one more difference between run 2's and run 3's inputs, which addendum 1's B1 mixture caveat covers.
- **Tests** (`build/test_v2_helpers.py`): the view has exactly `CANDIDATE_FIELDS`; every field P() writes is classified; each injected leak is refused, including in a tuple, under an answer-file name, inside a quoted text, or as a whole-text bare label; `label_view`; all 51 v1.6 positions pass.

**G6. Linked battles and E7 in the job prompts (F6).**
- **The staging:** `jobs/INV_JOB.md`, `jobs/LABEL_JOB.md` and `jobs/SELCHECK_JOB.md` (both parts) stage ONE folder per game: a battle's clips in order (`clip01_…`, `clip02_…`) with `CLIPS.json`. The laptop builds CLIPS.json from the snapshot's metadata alone (clip order, packets, start times). The usability worker records each turn's clip and each clip's turn range.
- **The turn count:** each prompt carries the same "Turns and ids" text: ONE global turn count for every game (the game's own turn counter, both players' turns, as v1.6's `source.global_turn`), which never restarts in a later clip. Every turn is keyed by its point id `LAD-<game>-t<n>`, so ids can't collide or mis-order.
- **E7's second rule** is in INV_JOB's prompt and in Part A's, in the same words: a turn right after a gap is usable only if the full state there, turn effects included, is established.
- **The launch checklists:** each job's checklist has a line for each of these rules.
- **What the workers may open:** every prompt bars the other folders of `/home/dacz8976/exam_v2/`, where the builder's files live.

**G7. pool_runs.py, two distinct runs (F7).** `pool_runs.py` is unchanged; no defect was found. `test_pool_runs.py` gains 9 tests (22 in all) that pool two distinct SYNTHETIC runs.
- **The runs:**
  - run A: 7 points in 5 games, km3 seeds 101-103, 1 failed reply;
  - run B: 6 points in 5 games, seeds 201-203, 1 failed reply;
  - each with a self-consistent report made by frozen-7's own `analysis.analyse`.
- **Checked by hand:**
  - the pooled estimate, 11/39 = 0.282051 over 13 decisions and 10 games (not 0.281746 with run-equal weighting, nor 13/33 with failed replies dropped instead of missed);
  - the rates;
  - the failed-reply share;
  - the sign-flip p, 128/1024 = 0.125;
  - each run alone.
- **The interval** equals frozen-7's `game_bootstrap` on the hand-pooled game clusters, at 0.975 and at 0.95.
- **Degenerate pair:** a pair where every game gives the same difference collapses the interval to the point and takes the PASS branch.
- **Order:** pooling equals one batch of both runs, in either order.
- **Refusals:**
  - a game id, a point id or a km3 seed in both runs;
  - a second run with another model, or with no model list (pooling OFF, exit 3);
  - a second run with the wrong freeze tag, a self-report number the script doesn't reproduce, a wrong failed-reply count, or the first run's eligibility file.

**G8. Weak deck flags (F8).** `make_sources_snapshot.py` collects a source QR's weak flags: `battle_full20_proven` present and not true, or `unsaved_changes_prompt` set.
- **Where it looks:**
  - DECKS.json's sources (the game's own and every `also_from`);
  - each clip's QR_ID.json, QR_DECODE.json and LINKED_*_QR_ID.json, read directly;
  - the exact-list folder's QR_DECODE.json.
- It records them as `weak_qr`. A game that would count and carries a weak flag needs a ruling, or the run STOPS.
- **The ruling:** RULINGS.json may carry an optional `weak_qr` section: {the opening clip's drive id: {"decision": "in" | "excluded", "flags": {file: {flag: value}}, "ruling": "<the coordinator's mailbox id or words>"}}.
  - It is checked strictly: games in the window, opening clips only, exactly those three keys, nothing empty, and only weak flags.
  - An entry must cover every flag found (same file, flag and value), or the run stops.
  - "in" lets the game in, with `weak_qr_ruling` recorded. "excluded" excludes it with the reason "no exact deck list: weak source QR (<flags>): excluded by ruling <ruling>", one of section 1's written reasons.
- **Without an entry:**
  - a game with an addendum 3 game ruling stays in, and `weak_qr_covered_by` records that the game ruling covers the flags found. Accepted (G13, item 4);
  - with neither, the run stops, and its message asks the coordinator to rule in the `weak_qr` section.
- **Today** only 21-57-12 carries one (`battle_full20_proven: false`). Its addendum 3 ruling covers it, so it stays in.

**G9. The exclusion reason (F9).** The rule is unchanged: a partial review counts only when its opening is recorded, and the scripts take the opening clip's own filmed deck code as the sign of that (addendum 4, E2; E7). Only the reason is corrected.
- **A partial game whose list comes by the repository route** (`--extra-decks`) is still excluded, now with the true reason, quoted in full: "the list comes by the repository route (--extra-decks), so no own filmed code shows the opening: a partial review counts only when its opening is recorded with its own pre-game code (PREREG_RUN3 addendum 4, E2; E7)".
- **A true mid-game start** keeps its reason, word for word (tested).

**G10. The freeze is off the clock (F10).** Unanswered ambiguous points stay pending and unscored, as in v1.2. No point is rushed to make Monday.
- A point still pending at the freeze is frozen with status `pending` and kept out of the eligibility file until it is answered.
- `validate_v2.py` checks its position and its his, key and accepted lines, never its pending ones, and lists it as pending.

**G11. Tests and dry runs.**
- **Tests** (E5's counts replaced; all OK):
  - `test_snapshot_guards.py`: 22;
  - `build/test_v2_helpers.py`: 23. v1.6's 51 points are cut as v1.6 did on 47; the other 4 differ only by R1, at Sabrina and at Raticate's Ability;
  - `test_pool_runs.py`: 22;
  - `test_check_lister_v2.py`: 13.
- **The dry snapshot** (scratch folders only):
  - on the six batches above: 53 games, 53 in, 0 excluded;
  - with the newer DRIVE_LADDER_2026-10-23_EVENING (10 recordings, Oct 23 Central time) added: 63 games, 63 in, 0 excluded. No new list (still 20 deck files, byte-identical) and no new layout. The review index's in-window rows without a packet are down to the two Oct 20 rules-test recordings.
- DECKS.json is rebuilt from every batch at the cutoff.

**G12. Reads, recorded** (C1: not exposure).
- **The laptop session, Oct 23-24 (UTC):**
  - the Oct 23 batch's metadata, to read its two new layouts (M1): the QR_ID files, the continuation's `linked_qr_metadata` path, RELATED_SOURCES.json's `battle_key` and `chronological_sources`, and the SOURCE.json keys. No REVIEW.md;
  - v1.6's positions, references and exam file, for the G2 trial and the v1.6 tests (v1.6 material it had already seen);
  - the Ability and Trainer texts of the 20 v2 deck lists (R1's audit; deck-level, card text only);
  - the folder names of DRIVE_LADDER_2026-10-23_EVENING, and its QR files through `make_v2_decks.py` (dry run, scratch output).
- **The fix workflows** `wf_994857d9-f7e` (2 agents: F7, F8/F9) and `wf_f23c665b-a7b` (1 agent: the weak-flag rulings):
  - they were told never to open exam answer material, any run 1 or run 2 live folder, any REVIEW.md text, or any .MOV;
  - they read the machinery and documents, and ran the snapshot guards' tests, which read the batches' metadata files.
- **The review workflow `wf_615680e2-99c` and the re-check `wf_d86e2956-3af`** (2 agents each), under the same exclusions: they read the machinery, the documents, frozen-7's code and the test logs, and ran nothing.

**G13. The coordinator's decisions (coordinator-038, mailbox id 20261024T0210Z, Oct 24, 2026 UTC), recorded as ACCEPTED.** The items marked "proposed" above are settled as follows; where this section and an earlier "proposed" line differ, this section rules.
1. **R1: ACCEPTED.** The first segment follows frozen-7's lister: it ends where the lister ends the plan the line reaches, at a chance event, where the opponent must act, or at the end of the turn.
   - The coordinator's reason, verbatim: "both bots and the judge choose among the lister's plans, so labels must end where those plans end. Otherwise a correct pick can't match."
   - cut() predicts the known cases; the check records the lister's segment where they differ. Nothing is decided per point. This amends section 2's "chance rules are v1.6's".
   - **Run 2's record:** a dated note sits beside RESULTS_run2, at `../run2/ADDENDUM_2026-10-24_first_segments.md`; the results are not edited.
2. **An alternative failing pg_legal: ACCEPTED.** That alternative is removed, and the point keeps its key line. "An illegal alternative can't be picked by either bot, so this is symmetric."
3. **Game-level window rulings: ACCEPTED, with a limit.**
   - The coordinator rules game-level window questions (in span, ranked, linked, deck list) from METADATA ONLY: filenames, times, QR/list identity, review status and linkage. Never from moves or move content.
   - Each ruling is recorded with the metadata it rests on.
   - Point-level ties stay under F3 (G3), never with pattern-aware people.
4. **Weak deck flags: ACCEPTED as G8 has them.**
   - 21-57-12 stays in through addendum 3's ruling (`weak_qr_covered_by`).
   - A NEW weak game without a ruling stops the snapshot until the coordinator rules "in" or "excluded" from metadata, as in item 3.
5. **Big Malasada is not a chance step: ACCEPTED, as a consequence of R1, not a separate judgment.** The first segment follows the frozen lister, which forecasts one outcome there.
6. **Free-text position facts** (`opp_ambiguous`, `turn_effects`, board `effects`, `stadium`): ACCEPTED, with two guards.
   - **(a) Facts only.** `build/v2_helpers.check_candidate` refuses an evaluative or advisory word in those fields, using `BANNED_WORDS`: should, better, best, mistake, misplay, threat, lethal, plan, intend, want, correct, wrong, risky, safe, good, bad, optimal, ideal, blunder, must, needs to, ought, and their inflections. Card, Ability and attack names are taken out first, so "Team Rocket's Master Plan" and "Safeguard" pass. It is tested in `build/test_v2_helpers.py`, and all 51 v1.6 positions pass it.
   - **(b) Blind review.** The selection check's Part B reads every point's free-text fields (`position_facts.json`, those fields only) beside the review, and reports any hint of the answer. A flag is `fix_first`. A flagged text is rewritten to the review's own factual wording, or removed.

## Addendum 6 (Oct 25, 2026 UTC; the window closes early on the owner's direction, the coordinator's message of Oct 25, before any selection, any position build and any bot or judge output)
Nothing has been selected, built or run for exam v2. This addendum is committed BEFORE the real snapshot, and its commit time is the cutoff.

**H1. The owner's direction**, relayed by the coordinator on Oct 25, verbatim: "more games have been added to the ladder log if you want to include them. Also our usage is basically 50% so we can do things today, rather than wait until tomorrow. Nothing is magical about monday".

**H2. The new cutoff: 2026-10-25T15:19:32Z,** this commit's author and committer time. It replaces section 1's end (Sunday Oct 25, 11:59 PM Central, 04:59Z Oct 26) and section 10's step 2.
- The coordinator's words, verbatim: "It's moved earlier on the owner's direction, decided before any selection or bot output and without regard to any game's content."
- The laptop set the time when it committed. It had read no review, no move and no result of any window game (H5 lists what it read).
- Dual Fusion's release (Oct 29, 01:00Z) comes later, so it doesn't bind.

**H3. The window: every ranked game recorded before the cutoff that Codex has reviewed.** Section 1 and addenda 3-5 apply unchanged.
- **"Reviewed"** means an accepted review in the Evidence batches when the real snapshot runs, right after this commit. The snapshot reads the nine ranked batches:
  - DRIVE_INBOX_2026-10-20, DRIVE_LADDER_2026-10-19, DRIVE_LADDER_REMAINING_2026-10-19, DRIVE_INBOX_2026-10-21, DRIVE_LADDER_2026-10-21_EVENING, DRIVE_LADDER_2026-10-23 and DRIVE_LADDER_2026-10-23_EVENING;
  - the two new batches: DRIVE_LADDER_2026-10-24 (16 games, 20 QR_ID files) and DRIVE_LADDER_2026-10-25 (11 games, 16 QR_ID files). Both FINAL_QA files show 0 older recordings queued (the coordinator's read).
  - DRIVE_RULE_TESTS_2026-10-19 holds rules tests, not ranked games.
- **Later games:** a game recorded at or after the cutoff is out of run 3, without exception. So is a game recorded before it whose review is not in those batches at the snapshot.
- **The snapshot's `--window-end`** is 2026-10-25T15:19:31Z (inclusive), one second before the cutoff.

**H4. New lists and weak flags.**
- **New lists** are card-checked against the frozen tree as before: every printing must be in the frozen database (`make_v2_decks.py --frozen-db`, tree 70652fff), and every list must load in `pg_legal_v14` (`smoke_v2.py`).
- **A new weak deck flag** stops the snapshot until the coordinator rules "in" or "excluded" from metadata only (G13, items 3 and 4).

**H5. The dry run and reads before this commit, recorded** (C1: not exposure).
- **The dry run** (Oct 25, 15:10-15:20Z, scratch folders only): `make_v2_decks.py`, the card check and the snapshot, over the nine batches with the default end.
  - **Games:** 90 games (93 recordings, 3 linked battles), 90 in, 0 excluded. The earliest starts 2026-10-16T18:46:35Z and the latest 2026-10-24T20:36:08Z.
  - **Lists:** 27, and the 20 committed deck files are byte-identical. Every list encodes back to its code, and all 27 load in `pg_legal_v14`.
  - **The 7 new lists** (the number of window games with each list, by Energy type): v2deck_2c68a379f5 (Fighting+Metal, 4), v2deck_7907f1e146 (Water, 10), v2deck_8561e086a0 (Grass+Darkness+Metal, 1), v2deck_995ac0891e (Water, 6), v2deck_a75894a903 (Lightning, 3), v2deck_bac3c8a158 (Darkness, 1), v2deck_c4ac51db37 (Psychic, 2).
  - **Weak flags:** none new. The only weak game is still 21-57-12, in through addendum 3's ruling.
  - **No new layout.** The review index's in-window rows without a packet are still the two Oct 20 rules-test recordings.
- **What the laptop read:**
  - the two new batches' folder names and QR_ID file counts;
  - their QR and metadata files, through the two scripts;
  - the window record's metadata (counts, start times, statuses, the layout of the folders and the review files' byte sizes);
  - the 27 lists' smoke lines (deck-level).
- **What it did not read:** any REVIEW.md text, any move or result, and any .MOV (Oct 18 .MOV: not a game (owner confirmed)).

**H6. What follows, in section 10's order:**
1. The real snapshot: `decks/` rebuilt from the nine batches (the committed files unchanged), then `sources/` and `window.json`, committed.
2. The usability coding (INV_JOB) and the selection check's Part A (the blind second coding), both launched by the coordinator on the credit worker.
3. The labels, the build, the lister checks, Part B, Dustin's questions and the freeze. The freeze stays off the clock (G10). km3 rows and other heavy work run at night.

## Addendum 7 (Oct 25, 2026 UTC; two field shapes in part 1 of the usability coding, by the coordinator's ruling of Oct 25, before any label, build, bot or judge output)
- **What happened.** The coding jobs ran 15:54-16:13Z (coordinator-040), staged as `jobs/LAUNCH_2026-10-25.md` records.
  - `make_turns.py` refused INV part 1's inventory, as designed: it names the global turn count `gt`, a name the script did not accept.
  - Parts 2 and 3 passed. Part A part 1 has not run.
- **The coordinator's ruling, verbatim:** "NO re-run of INV p1. Picking between two codings after seeing them would be discretion. Map the key mechanically instead". The record line it set: "INV p1 named the field `gt`; mapped mechanically as an alias; no re-run; no content read".
- **The change for `gt`.** `make_turns.py` accepts `gt` as one more name for the global turn count. A turn carrying two of the names with different values still stops the run. No coding is changed, and nothing is re-run.
- **A second shape, found by the dry run; the coordinator rules it.** Two turns of the linked battle 20261021_032324000_SR carry `clip: null`; the first coding placed no clip there. The first is LAD-20261021_032324000_SR-t6. This is the battle whose recording ends early (addendum 4).
  - `make_turns.py` used to crash there. It now stops with a clear message.
  - The flag `--null-clip` passes such a clip through as null and lists those turns in `TURNS_RECORD_p1.json`.
  - Without the flag, part 1 stops. With it, part 1 gives 145 turns from 30 games and passes 2 null clips through.
  - The turn list's clip only tells Part A where a turn sits. Part A codes each turn by its point id from the one whole-battle review (`CLIPS.json`).
  - Using the flag or not is the coordinator's ruling, recorded here when made.
- **`test_make_turns.py`:** 19 OK. Seven tests are new: the alias in part 1's shape, a conflicting and an agreeing pair, and four for null clips.
- **Reads, recorded** (C1: not exposure). The laptop read the KEY NAMES of `inv_out_p1/inventory.json` and no value:
  - top level: games and totals;
  - game level: game, clips, deck_id, deck_name, deck_cards, result, ladder_eligible, turns and clip_note;
  - turn level: id, gt, clip, board_known, hand_known, move_known, real_choice, kind, line, usable and reason.
  - Two dry runs of the changed script ran on a scratch copy, which was then deleted. Each printed only its last line, quoted above.
- **The coordinator's ruling on the null clips** (coordinator-041, mailbox id 20261025T1620Z), verbatim in its first sentence: "PASS THROUGH the 2 null clips (20261021_032324000_SR, from t6, the battle whose recording ends early)."
  - Its reason: the clip only locates a turn, and Part A codes by point id from the one whole-battle review.
  - The coordinator ran `make_turns.py ~/exam_v2 1 --null-clip`. It made 145 turns from 30 games, with the 2 null clips passed through and listed in `TURNS_RECORD_p1.json`.
  - Part A part 1 ran 16:17-16:23Z, with 0 turn-list problems.

## Addendum 8 (Oct 25, 2026 UTC; the usable set and the build, before any label, bot or judge output)
**K1. The usable set** (`select_v2.py`; addendum 5, G3), mechanical:
- **The rule's reading:** a coding "calls a turn usable" when its four fields are all "yes" (section 2) AND its own `usable` verdict is true. It is symmetric and conservative.
- **The table** (turns; both usable / first only / second only / neither):
  - part 1: 145; 80 / 1 / 1 / 63;
  - part 2: 177; 107 / 12 / 16 / 42;
  - part 3: 154; 74 / 14 / 2 / 64;
  - all: 476; 261 / 27 / 19 / 169.
- No coding's verdict differs from its fields, and every listed turn was coded once by each coding.
- **261 candidates from 76 games.** The two codings' fields and reasons are copied per turn into the local `~/exam_v2/select/agreement.json`, for Part B.

**K2. The build** (section 2; addendum 5, G1 and G5).
- **The tools**, in `~/exam_v2/build/`:
  - `BUILD_BRIEF.md`: the conventions;
  - `check_game.py`: validate_v2's checks, game by game, plus the candidate list;
  - `cards.py`: the frozen database, b5e68fc8.
- **The pilot** game 20261017_150114000_SR settled the conventions:
  - the Bench is compacted, and `Place` takes the lowest empty slot (the lister matches `Place` without its slot);
  - a hidden search counts +1 in the opponent's hand;
  - a printing that can't be told apart is the first listed;
  - the opponent's next Energy comes only from the review at or before the turn.
- **Ten builders** (workflow wf_b0c2c0d9-ae0), one per batch of whole games in time order, then a fresh verifier per batch:
  - each verifier re-derived every position from its review and changed 32 fields, each with the review's words;
  - the build records are `~/exam_v2/build/g/g<game>.py`, kept local until the freeze, as v1.6's were.
- **Result:** 258 points pass, and 3 are dropped under G1 with verbatim pg_legal output (`build/drops/`).
  - The 3: LAD-20261023_001330000_SR-t10, LAD-20261023_005124000_SR-t6 and LAD-20261023_005124000_SR-t12.
  - The cause: the frozen engine's card data doesn't make Buzzwole B2 014 an Ultra Beast, which the game did. So his recorded Lusamine and Ultra Thrusters plays are illegal in the engine.
  - The builder and the verifier both confirmed the drops. The same data gap narrows the legal lists at the kept points 20261023_005124000_SR-t2/-t4/-t8 and 20261023_001330000_SR-t8.

**K3. Machinery corrections the build found** (none changes a rule; tests: `build/test_v2_helpers.py` 24 OK):
1. **His line ends at his Attack.** This is frozen-7's own rule: `judge.py` `normalize_full` and `full_match` end a plan at its Attack, and what follows is bookkeeping.
   - `P()` cuts `force` after the first `Attack:` label, dropping a target, a pending fx attach, ApplyQueuedAttackDamage or a new Active. The build's notes keep what the review shows.
   - The first brief said to write attack targets after the Attack. Doing so would have left one line unreadable to frozen-7 (`ApplyDamage{…}`).
2. **No zone Energy on global turn 1** (the first player's first turn): `P()` sets `energy_now` to None there. Before, the engine listed a zone attach on that turn.
3. **New chance actions:**
   - `Play:Cabbie` joins `DRAW` and `CUTD`: it searches the deck, so it is a chance action under ADJUDICATION_RULES section 3 ("any other card whose effect draws, searches, flips a coin or picks at random");
   - Area Zero joins `CHANCE_STADIUMS`: its use shuffles and draws.
4. **Wallace's random evolution.** `v2_helpers.tool_steps` reads pg_legal_v14's stop at a random evolution ('hidden random choice') as that chance step, matched. The tool leaves the label unmatched although that step's legal list holds it. `check_game.py` and `validate_v2.py` both use it. Before, every line whose first chance step was Wallace read as unmatched.
5. **Tool notes** (`check_game.py`, reported, never silent): the tool stops before his line ends at 4 points, so the rest of the line is not checked by the tool there:
   - an opponent's choice inside his turn: LAD-20261022_004518000_SR-t6 (Sabrina) and LAD-20261024_164318000_SR-t4 (Ancient Roar);
   - a non-chance return to hand: LAD-20261023_011134000_SR-t14 (Parasol Lady);
   - a label that names two cards only in the after-chance variant: LAD-20261024_180942000_SR-t1.
   Each verifier ran those rests in scratch, and they applied. A hidden stop at a line's last label (an attack that moves deck cards: Dragon Pulse, Mega Blaster) is accepted, because nothing of his move comes after it.
6. **Known gaps, not changed:**
   - Misty's coins are not in `DRAW`; one line holds Misty, after an earlier Poké Ball, so the first segment there is the Poké Ball's.
   - The lasting attack boost of a Mega Mawile ex at LAD-20261024_175131000_SR-t6 is not set.
   R1's lister segment rules the first segment in all such cases.

**K4. A dry run of G2 on his lines** (frozen-7's lister and replay matching; the identity gate passed; no labels exist): 258 of 258 key lines reach exactly one listed plan. 7 differ from `cut()` and are settled by R1 (the lister's segment). The real G2 runs after the labels, on every accepted line.

**K5. Reads, recorded** (C1: not exposure).
- **The builders and verifiers** (laptop subagents, briefed with no run 2 result) read the reviews of the 76 games with candidates, as the build requires.
- **The laptop session** read:
  - the codings' key names only, to compute K1 by script;
  - the build agents' reports, which hold review details;
  - the check and lister outputs.
- No one has written or seen a label for these points.

**K6. Next, in G2's order:** the labels (LABEL_JOB, staged in 5 parts: `jobs/LAUNCH_LABEL_2026-10-25.md`), the lister check, Part B, Dustin's answers, the lister check again, `validate_v2.py`, the freeze.

**K7. The question cap, changed before any label was read** (Oct 25, 2026 UTC; the coordinator's message of about 17:30Z).
- **What happened.** The five label jobs were launched with "at most 1 question in this part", which kept the rules' flat "at most 6" for the whole exam. The coordinator stopped them at 17:25Z, about 2 minutes in.
- **Their partial outputs** were moved aside UNREAD to `~/exam_v2/label_out_p<k>.aborted_20261025T172559Z`. Nobody opens them, and they are never used. The out-folders were recreated empty.
- **Dustin's question** (as the coordinator relayed it): whether a flat cap of 6 questions makes sense for 258 points.
- **The coordinator's reason:**
  - v1.6 allowed 6 questions for 51 points; a flat 6 over 258 is about 5 times stricter. Unsure alternatives would be dropped instead of asked, which is a different labelling regime from v1.6's, and the pooling assumes they are the same (the advisor's trap 1).
  - It could also tilt the comparison toward the bot that plays the "standard" line.
- **The change: at most 6 questions PER PART, at most 30 in all.** Each part (48-54 points) is about v1.6's size (51).
  - It is made in ADJUDICATION_RULES' v2 copy (`jobs/ADJUDICATION_RULES.md`, section 2) and in the five prompts.
  - Nothing else changed. The re-staging's hashes (`jobs/LABEL_STAGING_2026-10-25.json`) differ from the first staging's only in ADJUDICATION_RULES.md and the prompts.

**K8. The coordinator's job decisions and the judge budget** (notes 040, 042, 043 and 046; the "$" figures as note 046 restates them).
- **The coding jobs** (note 040): $8 per part, so at most $48 for INV plus Part A.
- **The labels** (note 043):
  - claude-opus-5-5 for all five parts, "they're the answer key";
  - $15 per part, at most $75;
  - deck_kinds as staged, each deck in exactly one part.
  - The cap of 1 question per part was changed to 6 per part by K7.
- **The fix jobs** (note 046): relink $5; the second pass $8 per part (p3, p5).
- **THE JUDGE BUDGET** (note 042, decided before any judge call; it replaces section 9's $15 ledger and changes no analysis rule):
  - a total ledger of $75, with a primary run cap of $40 and the repeat taking what remains;
  - from Dustin's Google trial credits (about $287 left), under his standing OK ("you can use it for anything that could be helpful");
  - run before Nov 30 (the introductory price). The 20% no-choice and resend rules repeat.
  - The reason: about 261 primary plus 261 repeat calls are likely to cost about $25-35 actual, plus headroom for the wrapper's worst-case reservations.

**K9. Five alternatives kept past an unverifiable chance step** (the coordinator's ruling of Oct 25, after laptop-036's pre-validation).
- **The five:** LAD-20261020_033156000_SR-t2, LAD-20261023_115617000_SR-t3, LAD-20261023_122720000_SR-t1, LAD-20261021_225620000_SR-t3 and LAD-20261022_000850000_SR-t8. `validate_v2.py`'s after-chance variant cannot confirm them past their chance step.
- **KEEP them.** The scored part, the first segment up to the chance step, is legal and reaches exactly one plan. What follows a chance step depends on draws or random results that never happened, so under G13 item 2 it is report-only, not "fails validation".
- In the full-scope (secondary) reading their post-chance remainder is unverified: the result note lists them by id in its full-scope caveat. The primary is unaffected.

**K10. The advisor's audit of the answer key, and the fixes** (note 044, mailbox id 20261025T1830Z; clarified in note 046 and the coordinator's note on the A/C outputs). The advisor, read-only, saw the answer key; it builds no bot.
- **A. Re-label of the 3 games recorded in two clips** (20261021_020059000_SR, 20261021_032324000_SR, 20261022_004518000_SR; 8 points).
  - A fresh job (opus, $5, the same rules and confinement) had each game's clip reviews merged, byte for byte, as one whole-battle review read once.
  - Its labels replace the first pass's for those points; the assembly does not read the first pass's labels for them.
  - Result: 1 accepted line and 1 question.
- **B. The chance-first rule,** decided by the assembly for every point (v1.6's draw-first rule extended).
  - His own line, with its first chance action moved to the front, is accepted when that action is Professor's Research, Poké Ball, Lucky Ice Pop, Wallace, Quick-Grow Extract (each with its random-evolution step) or UseStadium under Fragrant Forest, it is legal at the root, and nothing before it feeds it:
    - Wallace / Quick-Grow: no Place, Evolve or Retreat before it;
    - Lucky Ice Pop: no change of his own Active before it;
    - Research, Poké Ball, Fragrant Forest: nothing feeds them.
  - Copycat, Lusamine and every other card stay out. **Deterministic actions before the draw when his line drew first stay unaccepted, as in v1.6.**
  - Result: 27 chance-first variants, all passing the lister check.
  - Every labeller-written order variant of his own move (the same set of actions in another order) is stripped. That is 12: the two the note names (221937-t2 and 224410-t1) and 10 from the second pass.
  - So is 175131-t6, the same Water on the same Pokémon moved before the chance step his line played first. It was found by a scan of every accepted line and is the only one.
- **C. A second, independent alternatives pass over parts 3 and 5** (opus, $8 per part; the trigger is structural: 5/48 and 0/51 accepted, against 6-10 per part elsewhere and v1.6's 16/51).
  - The union with the first pass, each line passing the lister check and pg_legal:
    - added as accepted: 4 (152239-t5, 152239-t7, 181948-t6, 182453-t10);
    - already accepted or equal to a pending line: 6;
    - new questions: 3 (part 3: 235420-t4, 000150-t5, 005124-t8);
    - merged with the first pass's question: 1 (165202-t9).
  - **The rule for a stronger line** (the coordinator's note on the A/C outputs): a second-pass line its labeller called at least as strong as his move goes to Dustin as PENDING with a neutral question, within the part's cap, not to ACCEPTED (finding 4). 180350-t5 is pending; 181948-t8 is already a question (D3).
- **D. Question fixes:**
  - D1: 034501-t3's "Evolve Alolan Muk ex first" moved from accepted to pending, with a neutral question.
  - D2: two new questions, 235420-t10 (Cyrus on the Riolu) and 204548-t7 (Water on Oricorio, then Retreat, built in his order: note 046).
  - D3: four questions de-led to "..., or was your line the better play?": 221218-t5, 165202-t9, 181948-t8 and 221617-t3.
  - D4: the part 5 question at 182453-t8 also covers t10 and t12. Each now carries its own pending line (Turbo Shark in place of ending the turn), and one answer applies to all three.
- **E.** LAD-20261021_213653000_SR-t9: the frozen engine accepts his Wallace line (lister: one plan; pg_legal: legal to the random step; after-chance validated), so his move stays the key. Both Wallace label forms pass the lister.
- **The fixes file** is `~/exam_v2/D_FIXES.json` (sha256 74297a5d78e8a8c5f91a25b078e5f7d38aded0e472e58fec372cbce85df7725f), kept local with the answer key until the freeze.

**K11. Dustin's questions, the answer options and their mapping, set BEFORE he answers** (note 045, mailbox id 20261025T1845Z).
- **Dustin, verbatim (note 045):** "I'm by no means perfect and can make a mistake and I'm not above admitting it if you show me. I can give you my thinking in the moment, but just like in my clinical practice, we have to make decisions off of imperfect information sometimes and sometimes in the moment we make the wrong decision."
- **What he sees:** only what he could see at that moment: the start-of-turn position, his move and the line asked about. Nothing from later turns. The builder's approximation and uncertain-reading texts are left out, because they can cite later turns.
  - Ten question texts were edited, each recorded in the fixes file with its reason. Four are D3's de-leads. The others remove hindsight ("let it fall to 0-2", "let the 60-HP Active fall", "was lost either way", the opponent's later hit on Stoutland, "Eiscue isn't knocked out"), correct facts ("Mega Blaster"; Alolan Muk ex not yet in his hand; the Espeon's start-of-turn HP), or de-lead a tail ("or as the better one").
- **The answer options**, the same for every question, plus an optional note for his thinking in the moment:
  1. **"The alternative was better (my play was a mistake)"**: the alternative becomes the key (`key_line`), `recorded_move_acceptable` is false, and his recorded move becomes a rejected alternative with his words (`rejected_because`, `certified_by: dustin`). This is v1.6's precedent: LAD-20261016_031512000_iOS-t2, "Not attacking was a mistake".
  2. **"Both were fine"**: the alternative is accepted, with his words and `certified_by: dustin`; his move stays the key.
  3. **"My play was better"**: the alternative becomes a rejected alternative with his words and `certified_by: dustin`, and never counts; his move stays the key (v1.6, e.g. LAD-20261014_161324000_iOS-t5).
  4. **"Not sure"**: the alternative is left out. It is not accepted and never counts, and it is recorded with his answer. His move stays the key.
  - His note is stored verbatim with the point (`dustin_answer.words`).
  - A shared question's one answer applies to each point it covers, each to its own pending line.
  - A question unanswered at the freeze leaves its point pending and unscored (G10).
- **The questions:** `~/exam_v2/questions/QUESTIONS.json` (sha256 f84ce10a767299daca90f29af3be2d90cdc57d599705bd59a8f76b7537414c5c): 23 questions (part 1: 4, part 2: 2, part 3: 6, part 4: 5, part 5: 6), plus 2 points sharing one question. Each part is within K7's cap of 6.

**K12. The assembly after A-E, and the selection check's Part B as staged** (`assemble_v2.py`; draft `~/exam_v2/assembly2/exam_v2_draft.json`, sha256 583f0853a9337ce4eaa41a7f1cd550c4649931131b88f8255b948f0ae946852f).
- **Points:** 258, of which 233 are final and 25 pending.
  - Accepted alternatives: 56. Pending lines: 25. Lines removed with their record: 13.
  - Answer kinds: prepare 151, attack now 92, sacrifice 15.
- **The lister check on all 339 lines** (his, accepted and pending): 334 pass, 5 resolved by R1 (3 points), 0 removed, 0 drops.
- **`validate_v2.py`** (pre-freeze run): 314 accepted lines; 0 unmatched, 0 position problems, 0 PGDUMP. 311 of 314 tool stops equal the first segment; the other 3 are K3's tool notes. After the chance step, the rows are K9's five and K3's two tool notes.
- **Part B, staged as six confined jobs** (`stage_partb.py`; record `jobs/SELCHECK_STAGING_2026-10-25.json`).
  - **One main job** for items 1-4: the window, the two codings, no picking and the mix. It holds the reviews of the two games with a build drop, for item 3.
  - **Five facts jobs** for item 5, one per labelling part, each with its points' reviews: one session cannot read 258 points beside about 1 MB of reviews.
  - **The merge rule:** Part B's verdict is fix_first if the main verdict is, if any facts job flags a text, if any facts job's `checked` does not equal its points, or if a job does not finish. Merged flags are reported with their part.
  - **The facts prompts** narrow one spec sentence for printing notes. The choice of printing among those matching the shown facts is flagged only if it hints at his move or judges a play. Every fact such a note cites is still checked against the review. This takes effect only with the coordinator's approval (`jobs/LAUNCH_SELCHECK_B_2026-10-25.md`).
- **Reads, recorded** (C1: not exposure):
  - the laptop session read the labels and the fix jobs' outputs, for the mechanical assembly and the questions;
  - its check workflows (wf_3d47f9e5-b0a, wf_fb19d31e-a29) read the staged inputs, the questions and the draft for their checks.

**K13. The quiz file and the coordinator's rulings on K11** (notes 047, 048; laptop-038).
- **The `video` field:** each of the 23 questions and the 2 shared points now has `video: {file, at, clip}`.
  - `file` is the recording's name as Dustin knows it (his review index).
  - `at` is the earliest start time on that turn's own label in the review, as m:ss in whole seconds. The reviews' times are approximate to about 1 s.
  - `clip` is the clip of a linked battle and null otherwise (addendum 7).
  - The field comes from `video_refs.py`, which `make_questions.py` calls. With the field removed, the file equals K11's `f84ce10a…`; nothing else changed.
- **K11's sha256 is superseded.** QUESTIONS.json, the quiz as published (https://claude.ai/artifact/RLNHNAwm55DpVLe1JniuJC), has sha256 `360361e1cbfcd794887be18135e8d126ee1a54e5291c152bcfb4451f96dcd591`. QUESTIONS.md's is `7fd3fd70c12431a25450e99e3e2fba7ec69ceaf519a4d12972e765029531c1cf`.
  - The file is now frozen as the quiz. Any later change goes to the coordinator first.
  - His answers are read from the quiz's db collection `answers`: one document per question, doc id = point_id, fields `choice`, `note`, `answered_at`, `question`.
  - The shared question is stored once, under 182453-t8, and K11's mapping applies it to t10 and t12.
- **The 10 question-text edits** (K11, D_FIXES `set_question`) are ACCEPTED (note 047).
- **"Not sure"** is recorded as K11 states it (note 047): the alternative is left out and never counts, his move stays the key, and the point is scored.

**K14. Part B's result** (the coordinator launched it at 18:17:48Z: six confined jobs on claude-sonnet-5-5, caps $10 + 5 × $5; all rc=0, ending 18:21:15Z).
- **Main: clean.** The coordinator's `partb_gaps.py` (sha256 `ec8476c8…`, reading selcheck_in only) closed its two gaps:
  - the 261 turns usable in both codings equal the 261 candidates, both ways;
  - first-coding-only: 27 (p1 1, p2 12, p3 14), each given the second coding's reason. All are ordinary not-usable reasons;
  - second-coding-only: 19;
  - selection's 258 points equal labels_summary's `points`. The script's own last line compares the file's top-level keys and prints False; the corrected comparison prints True.
  - The output is kept locally until the freeze, as `PARTB_GAPS_2026-10-25.txt`.
- **Facts: 258 of 258 checked; 116 flags on 104 points, all in `opp_ambiguous`.** Under the merge rule this is **fix_first**, and K15 is the fix.

**K15. The opponent's printing notes** (note 048, decided by the coordinator).
- **Every `opp_ambiguous` printing note in all 258 points is rewritten,** not only the 104 flagged, as "Opponent's <name>: the position uses printing <set number>."
  - **The reason:** the old notes' evidence clauses ("chosen by HP / attack title / Ability title", lists of other printings) can cite what the review first shows after the point's turn, or an HP the review never states.
  - The printing itself is visible to the player by tapping the in-play card (Part B item (c)), so each printing choice is kept as it was.
- **How:** `printing_notes.py`, applied by `assemble_v2.py --printing-notes` to the built positions before anything reads them.
  - The set number is read from the position, and it must be one the old note names.
  - A note listing several cards becomes one sentence per card.
  - A Tool whose name was not read keeps "its name was not shown".
  - The review's 'Silver Pad' becomes Order Pad B4 145.
  - One Electrike note was settled by hand: two Electrike are in play, the Active one B2b 026 and the first one A2a 027.
  - Two notes keep a fact of an earlier play as their own sentence: Brock's two Fighting Energy on Onix, and the Team Rocket Grunt's Confusion. Both plays come before every point that carries them. Part B's facts job for part 5 checked these points and flagged only their attack-title clauses, which are gone.
  - Notes not about a printing are unchanged: one card in his hand that the review does not identify, and the opponent's reconstructed Lightning on Oricorio.
- **The counts:** 866 old notes became 944 new notes, in 251 positions (7 positions have none). 254 built positions changed, counting the 3 G1 drops.
- **The mechanical check:**
  - 0 texts contain "chosen by", "attack title", "Ability title" or "printings have";
  - 0 contain any attack or Ability name (raw word match);
  - 0 name a global turn at or after the point's own turn;
  - the positions are identical before and after, except that field;
  - the answers, references.json, the lister's 339 verdicts and validate_v2's summary are identical.
- **Two independent reviewers** read all 297 distinct old-to-new pairs, one checking fidelity and one checking evidence, hindsight and lost facts. They found no errors besides the two lost facts, which are now kept.
- **Runs 1 and 2 carried the same kind of note.** Their one positions file (sha256 `17bea6e3…`, 51 positions) holds 24 printing notes in 24 positions. 22 of them have a "chosen by" evidence clause, and 2 of those name attack titles. Those notes were not rewritten, and whether any of them cites a later turn was not checked.

**K16. One position fact: 20261021_224410000_SR t9, t11 and t13** (note 048 item 4; none is a quiz point).
- **The note removed:** "His Benched Mega Sharpedo ex: one Water is listed on it; the review says its retreat on global 7 paid that Water, but the card's Retreat Cost is 0".
- **The frames settle it.** Two independent Sonnet checks agree with high confidence. They used frames only, from the recording whose sha256 equals the review's (`01d08f65…`). The frames show:
  - one Water on the Active Mega Sharpedo ex before the retreat (230-237.9 s);
  - no Energy discard step, only the switch-in prompt (236-237.9 s);
  - one Water on it on the Bench from 241.7 s, and at the starts of globals 9, 11 and 13 (285.5-287 s, 309-311 s, 359-361 s).
- **The position already carried that Water and is unchanged.** `check_game.py` reports all OK.
- **No line uses that Water.** All three points are final, and each has only his move: no accepted or pending line.

**K17. The files after K13-K16.** These stay local until the freeze; `assembly2` is kept as the pre-048 assembly.
- `assembly3/exam_v2_draft.json` `440a594a570ce4cce2814e7b643e8a95cf17862526abb28d913a4ed9c45498e7`
- `assembly3/references.json` `60e7bcf5308f8ce504e643c5de6472c591030682de69103f4695394940bd1a6f`, equal to assembly2's
- `assembly3/positions.json` `b75c02e129307b7bce70d0c7fed242b8c504bd0ea15c851ea59643110b80edaa`
- `assembly3/lister_report.json` `7c9a80c97ae8dfb446c54883ed96489f8350e9e7dbf7efed54da5aa7c31eb626`
- `assembly3/printing_notes.json` `ce83a1878c8c4f4c07547753d58a78b212890cce16a814d26d16599eb05eca15`
- `assembly3/validate/VALIDATION_v2.json` `2304d9441db2c79fd1e5bfbbc761bdda54898362ee0e737ff527c53daa77ffaa`
- `D_FIXES.json` `74297a5d78e8a8c5f91a25b078e5f7d38aded0e472e58fec372cbce85df7725f`, unchanged
- build record `g20261021_224410000_SR.py` `300f4897c2989c9f00253d7095bd7ea22ae08b298412dca3618f3df5155c3e28`
- QUESTIONS.json, regenerated from assembly3 into a check folder, is byte-identical to the quiz (`360361e1…`).
- **Reads, recorded** (C1: not exposure). The laptop session's check workflow wf_7cc49a28-d9c ran four agents:
  - two Sonnet frame checks read only the 224410 frames and the time windows, with no positions and no answers;
  - two Opus reviewers read the old-to-new printing-note table, and one of them also opened assembly2's draft read-only to check each pair against its own position.

**K18. The quiz while he answers: Q10, card text on the page, the wording scan** (notes 049, and the coordinator's messages after it).
- **Q10 (LAD-20261023_000150000_SR-t5).**
  - **His report, mid-quiz:** "Dragon's blessing only works if the dragonair is on the bench. You can't use it on yourself so their line isn't possible in real life."
  - **Not an engine finding.** The coordinator checked main b78c8997. The card text: "if this Pokémon is on your Bench, you may attach an Energy from your discard pile to your Active [N] Pokémon". The engine's gate requires the user not to be Active, and the Energy goes to the Active.
  - **The alternative is legal:** Retreat:2 brings the OLDER Dragonair Active, and Ability@1 is the Dragonair just evolved from Dratini, which stays on the Bench.
  - **The cause is twin wording.** "bringing Dragonair (80 HP, on the Bench) into the Active Spot" fitted both 80-HP Dragonair, and "Use Dragonair (evolved from Dratini this turn)'s Ability" did not say that Dragonair was on the Bench.
  - **The coordinator's clarification, in chat (its core):** "Your older Dragonair, already on the Bench, is the one that goes Active when Trapinch retreats. The Dragonair you'd evolve from Dratini that turn stays on the Bench, and it uses Dragon's Blessing to put the Grass (discarded to pay Trapinch's retreat) onto the Active Dragonair. So no Dragonair uses it on itself." It said nothing about any bot or judge.
  - **His reply:** "You're right, I misunderstood the set up and thought I still had a dratini and a dragonair, when I actually had two dragonair. I see now."
  - Q10's answer was re-saved after the clarification (db version 2).
- **Card text on the quiz page** (artifact version 3, published about 20 minutes after note 049, at his request: "The more it resembles real life, the easier it is for me to envision and answer them").
  - **What it shows:** each Pokémon in play with its type, stage, Weakness, retreat cost, Ability and attacks; Tool and Stadium text; and the hand cards, which he taps to read.
  - **Where the text comes from:** the engine database on main b78c8997, by exact printing id. Tools, Stadiums and hand cards are matched by name. No text is shown for Squirtle and Stoutland in the hand, which have more than one printing.
  - **Why it is allowed:** this is text he can read in a real game by tapping a card, so it is not hindsight. The page has no bot or judge content.
  - **The files:** the card map is `cards.json`, sha256 `e978ef911270c882d169dc5a4e2822012dad3fd7e9b9f333346da1fa27e5a59e`. The page sources are in `~/exam_v2/questions/quiz_page/`.
  - **Timing:** questions 1-10 were answered before card text was shown (db versions then: all 1, and Q10 at 2); questions 11-23 have it. A later re-save of questions 1-10 shows as a higher version, and the coordinator reports it with the answers.
- **QUESTIONS.json is unchanged:** `360361e1…`.
- **The wording scan of all 23 questions** (report only; the live file is not changed). A mechanical re-derivation of every step and an independent read-through agree: **13 steps in 5 questions** name a Pokémon whose same-name twin is in play without saying which. In each case:
  - **Q4** (034756-t6), his move, step 3, "Alolan Grimer (80 HP, on the Bench)": it means the older Grimer, already on the Bench. Step 1 benched a second 80-HP one.
  - **Q9** (235420-t4), step 2 of both lines, "Trapinch (60 HP, on the Bench)": it means the leftmost Bench Trapinch. The two are identical: 60 HP, no Energy, no Tools.
  - **Q10** (000150-t5), alternative 1, steps 3 and 4: the case above. Step 3 means the older Dragonair; step 4 means the one evolved from Dratini, on the Bench.
  - **Q19** (165202-t9), steps 1 and 2 of both lines, "Indeedee ex (150 HP, on the Bench)" twice: step 1 is the first from the left and step 2 the second, so each uses Watch Over once. The same words twice can read as one Indeedee ex using it twice.
  - **Q23** (182453-t8), steps 3 and 4 of both lines, "Mega Sharpedo ex (the one the random evolution just made)": it means the one Wallace just made from Carvanha, on the Bench. The step does not say so, and the Active one is its twin. In step 4 the retreat implies the Bench.
  - **Not counted:** Q10's his-move step 3, "Trapinch (the one just benched from the hand)", where "benched" says the place.
  - **No step names an opponent's Pokémon that has a twin.**
- **A second, smaller gap the read-through found, outside twin wording:** in Q23's shared point 182453-t12, steps 2-3 of both lines and step 4 of alternative 1 quote start-of-turn HP (Active 120, Bench 170). Irida in step 1 heals 40 from each Pokémon with Water Energy, so at those steps the two are at 160 and 190. The Pokémon are still named correctly.
- **The coordinator clarifies hits to him in chat,** and each clarification is recorded here as Q10's is.
- **The writer is fixed for future quizzes** in a separate commit (`make_questions.py`):
  - a twin is always named with its place;
  - with what tells it apart: how it got there this turn, "the older one", HP "at the start of the turn", or its place on the Bench counted from the left;
  - the Active one is named without HP.
- **The live quiz stays as generated by the earlier writer.** Regenerated now, 31 step texts would change (and nothing else), so the freeze records the live file `360361e1…`, not a regeneration.
- **The scan's clarifications, relayed to him in chat by the coordinator** in plain words, with no page change and no reload, as with Q10:
  - Q4: step 3 of his move is the older Alolan Grimer;
  - Q9: the two Trapinch are identical, so it does not matter which one evolves;
  - Q19: each Indeedee ex uses Watch Over once;
  - Q23 (t8): steps 3-4 mean the Mega Sharpedo ex Wallace just made;
  - Q23 (t12): the HP shown is from the start of the turn; after Irida the two are at 160 and 190.
  - He was told he can re-check Q4 and Q9 if this changes his view. A re-save shows as a db version above the snapshot (questions 1-10 all at version 1, Q10 at 2), and the coordinator reports it with the answers.

**K19. Dustin's answers, folded in; THE FREEZE** (note 050 and the coordinator's messages after it; off the clock, G10; before any km3 or judge row for exam v2).
- **The answers:** `answers/ANSWERS_RUN3.json`, sha256 `62696826401070716cd7d4ed602ace4ad8cc63582b7dfd87e9b6a9accd533cb0`, with the 23 raw db documents in `answers/raw_db_docs/`.
  - The coordinator read them with ArtifactData after he said "Finished the quiz to the best of my abilities".
  - 23 of 23 are answered, each choice is an exact answer option, and the questions are `360361e1…`.
  - Versions: all 1, except Q10 at 2. Q4 and Q9 were not re-saved after K18's clarifications.
  - Card text was shown for Q11-Q23 and not for Q1-Q10 (K18).
- **The fold-in, by K11's mapping** (`assemble_v2.py --answers`): 25 points (23 questions; Q23's answer applies to 182453-t10 and t12 too). Every note is stored verbatim in `answer.dustin_answer.words`.
  - **Both were fine, 11:** the alternative is accepted (certified_by dustin).
  - **My play was better, 6:** the alternative is rejected (certified_by dustin).
  - **The alternative was better, 5:** the key changed at Q5 020916-t9, Q17 224156-t6, Q18 143157-t4, Q19 165202-t9 and Q22 181948-t8. His move is rejected (certified_by dustin, recorded_move_acceptable false).
  - **Not sure, 3** (Q8, Q10, Q11): the alternative is left out (removed_alternatives), his move stays the key, and the point is scored (note 047).
- **Q17 (224156-t6), the coordinator's decision before the freeze and before any run:**
  - His rejected move's chance-first order (Lucky Ice Pop first, then Snorlax ex) goes with his move: rejected, certified_by `coordinator_decision_from_his_words`.
  - The new key's own chance-first order (Lucky Ice Pop first, then the Terapagos ex line) is ACCEPTED.
  - **The coordinator's reason:** "rule B's chance-first acceptance belongs to the KEY line. K10 named 'his own line' only because his move was the key when it was written. The K11 mapping makes the alternative the key, so B carries over to it unchanged. Nothing before the Pop feeds the line, and the Pop doesn't commit to Snorlax, the mistake he named."
- **The third lines.** Four notes name a line that is neither his move nor the offered alternative:
  - Q8 235420-t10: "Playing cyrus and retreating to goomy might have been the best move."
  - Q9 235420-t4: "retreating to goomy might have been the best move"
  - Q11 005124-t8: "Retreating and attacking with buzzwole maybe would have been the best move"
  - Q15 204548-t7: "switching to bench eiscue wouldn't have been unreasonable"

  **His decision:** "Leave them as notes. Only the lines offered on the quiz count, and the report can show what the judge and bot played at those spots next to my notes." None of them counts.
- **REPORT-ONLY:** at Q8, Q9, Q11 and Q15, RESULTS_run3 shows the judge's and km3's chosen lines beside his note, with no scoring. At Q11 it also says that the non-ex Buzzwole is not an Ultra Beast in the engine data (the cause of the 3 G1 drops).
- **To-dos for the report:**
  - Q1's note asks "I would be curious to know if one was definitely better than the other". It goes on the report's list for after the runs.
  - Q14's note assumes the alternatives came from "the bot". The report says plainly that they came from the labellers.
- **The checks on the final references:**
  - **frozen-7's lister** (`check_lister_v2.py`): 325 lines (258 key lines and 67 accepted): 320 pass, 5 R1, 0 removals, 0 drops, 0 points without a key line. R1 segments are recorded for the 2 lines that turned from pending to accepted (034756-t6 alt0, 182453-t10 alt1). The 5 new keys pass.
  - **validate_v2:** 330 lines (his 258, of which the 5 rejected moves are records; key 5; alt 67): 0 unmatched, 0 position problems, 0 PGDUMP. 327 of 330 tool stops equal the first segment; the other 3 are K3's tool notes. After the chance step, the rows are K9's five and K3's two tool notes.
- **The scope, by v1.6's rule** (`freeze_v2.py`): a line is "full" when its scored segment holds all its strategic actions (every action except chance actions, EndTurn and UseStadium). A point is "full" only if every accepted line is.
  - **258 points: full 90, partial 65, none 103.**
  - The full-scope set is 90 points in 49 games. K9's caveat point 122720-t1 is among them, and the result note's full-scope caveat names it.
- **Eligibility** (`eligibility_v2.json`, frozen-7's `ai_judge_eligibility_v1`; its own shape and problem checks pass):
  - primary = all 258 final points, in 76 games;
  - no developer exposure is recorded, so none is excluded;
  - full_scope_ids = the 90 "full" points.
- **Two independent checks before the freeze** (workflow wf_c85a533f-118):
  - one re-derived every point's scope from the rule;
  - one audited the 25 answered points against K11's mapping, the 233 unanswered points against the pre-answer exam, and the references against the key and acceptable lines.
  - both found no problems: the scope matched on all 258 points and all 325 lines; the mapping held on all 25 answered points, the 233 others are unchanged apart from the scope fields, and the references hold exactly the key and the acceptable lines. Two notes: at 122720-t1 neither line has a strategic action, so it is "full" as v1.6's rule makes it (the rule tests "full" first); at 235420-t4 the newly accepted alternative comes before the chance-first line (alt1 became alt2), consistently in the references and the scopes.
- **Frozen, in this commit** (`frozen_2026-10-25/`, with FREEZE_MANIFEST.json):
  - `exam_v2_2026-10-25.json` `f0627a2149f6ab4427d3be2e52f2bce707d5a2b3db16abef070fc632e6e14913`;
  - `references_v2.json` `650c21a76e5cb79326f1342eab2275890c2ebdd97d4aaa87a957dc4c485bbe4a`;
  - `eligibility_v2.json` `b994a19f2c68f7a911660d5f1c9504cec8b0366118d1404150618f3b0b55ac97`;
  - `positions_v2.json` (the candidate view) `b75c02e129307b7bce70d0c7fed242b8c504bd0ea15c851ea59643110b80edaa`;
  - `ids_v2.txt` `1eb35725534b608e930ebb8bb91bfb69a2e0b71c727b5cfb6f149fc5bdeb9f78`.
- **Committed beside it:**
  - the answer key's inputs: the labels (`labels/`), `D_FIXES.json`, the build records (`build/g/`, `build/drops/`), the selection (`select/selection.json`), the assembly's lister report, printing notes, ASSEMBLY.md, the validation, and `PARTB_GAPS_2026-10-25.txt`;
  - the questions as the quiz showed them (`questions/QUESTIONS.json` `360361e1…`, QUESTIONS.md, and the coordinator's quiz page sources with `cards.json` `e978ef91…`);
  - the answers.
- **Reads, recorded** (C1: not exposure):
  - the laptop session's check workflows wf_0cf48ab7-b0d (the twin-wording check: QUESTIONS.json) and wf_c85a533f-118 (the freeze checks: the answers, the questions, the frozen exam and the pre-answer draft) ran Opus agents only;
  - no Sonnet agent saw any answer material.
- **From here:**
  - nothing in the frozen files changes after any km3 or judge row exists (G2);
  - the runs (km3 rows at night, from the new seed block registered first; then the judge, ledger $75, primary cap $40) wait for the coordinator's go.

**K20. The run's scheduling and kit, registered before any run 3 row** (the coordinator's GO of Oct 25 and its decision on the laptop's rate-limit question; no km3 or judge row exists for exam v2 when this is committed).
- **The risk:** in run 2's first primary pass, 2 of the first 5 calls got HTTP 429 (TPM quota). frozen-7's `budget_judge.py` stops sending after any failed call, so 46 tasks were NOT SENT; the one resend recovered them. Run 3 sends 258 calls (about 3.2M input tokens), so one 429 inside a single resend could leave never-sent tasks, and A4 would then give no verdict.
- **(a) Workers: 2** instead of 4. This is scheduling only: frozen-7's judge settings are unchanged.
- **(b) The passes** (`next_pass.py`):
  - Pass 0 sends every decision. Up to **3 later passes** follow, **120 s** apart.
  - **NOT SENT** covers only a task the harness's own record shows was never issued as an HTTP request: budget_judge printed `NOT SENT <id>` for it in that pass, with no `TASK FAILED <id>` line. Such a task may go in a later pass.
  - **Anything ambiguous counts as SENT** and gets run 2's A4 single resend: a TASK FAILED line (an API error, a timeout, a connection reset, a refusal inside judge_one), or a task in a pass's send list with no line at all. A decision issued twice without a row is never sent again.
  - **A task that got a reply (a row) is never asked again,** in any pass.
  - **Every pass uses the identical frozen-7 config;** only the scheduling differs. Each pass is logged with tasks asked, sent, NOT SENT and failed, those still without a row, and spend.
  - **The $40 primary cap covers all the primary's passes and resends together.** Never-sent tasks left after pass 3 stop the run (STATUS STOP; no verdict; reported). There is no 4th pass.
  - **The repeat follows the same rule** within the ledger's remainder. If it is incomplete after its passes, there is no sensitivity comparison and the run ends STOP. Nothing changes for run 2's rows.
- **Stops:**
  - the run stops for the coordinator on any unregistered event;
  - failed judge replies above 20% (A3): the registered primary and strata are computed (no API call), then the run stops before the repeat;
  - pooling OFF (section 7, a different model): it stops before the repeat;
  - an unexpected exit is written as STATUS STOP.
- **The kit** (`run_exam3.sh`, `prep_inputs_v2.py`, `next_pass.py`, `report_only.py`; the strata in `strata/`, fixed at 39c47136):
  - **Two independent reviewers** (wf_59f4d4d1-cd4) found 2 blockers in the first kit, both now fixed:
    - a one-line id list would have made every batch resend all 258 decisions;
    - the dry run's mocked judge never ran.
  - **Also fixed:**
    - a STOP status on every exit;
    - every branch file fetched before any spend;
    - the kit pinned (`KIT_COMMIT`, the exam tip must equal it; pool_runs.py, its test, the frozen files and the decks must equal the freeze's);
    - the pooled primary and strata computed before the repeat;
    - calls in flight counted in the primary cap;
    - budget_judge usage errors stopped, not resent;
    - the categories' deck kinds read from v2's format;
    - the runs labelled in pool_runs' output.
  - **The dry run checks:** the mocked judge on 3 points (3 rows, no later pass), `missing_ids` on a row taken out and on a one-line list, and `next_pass.py` on fixtures. It plays no km3 and makes no comparison.
- **The seeds** (START_HERE, Oct 21): km3 at 25,101,000,001-003. km3 plays in the night window (02:00-12:50Z), at nice 19.
- **The launch record** (RESULTS_run3 and the run's manifest) names this commit as `KIT_COMMIT`.

**K21. Unchanged kx3 on the frozen exam v2: the dated record, before any kx3 row** (coordinator-051 and -052; written Oct 26 by the laptop session; no kx3 row exists on any exam v2 position).
- **The decision:**
  - Dustin, relayed by the Oct 26 review session (review-001): "Yes. Tell the coordinator to score unchanged kx3 on the frozen exam v2 reusing Gemini's saved rows, no Gemini calls, with a dated record before any row. The adapter waits on that result."
  - Confirmed by him in the coordinator's chat: "Yes, confirmed: score unchanged kx3 on the frozen exam v2, reusing Gemini's saved rows, no Gemini calls, dated record first. The adapter waits."
  - Astra's points, via Dustin (review-002): the record must SHOW the comparison is fair, not only list the differences. Section 7 answers each point.

**1. The program: unchanged kx3, built on the frozen judge's own rules tree.**
- **kx3 is the frozen F pilot.** Its player code is the `engine/src/players` tree 7b093885 (playout_player.rs 9cbd8b1e, playout_pool.rs 5c0eac33). It is byte-identical in three commits:
  - d513e37b, the frozen pilot (Oct 2);
  - cd20a97a, the Oct 12 pin: kx3 on rules switch 2;
  - 87a7f340, the current release: program 7d046b6f on main-4d48844, whose self-checks print the kx3 digest 31d638dbc818b0fa and the km3 digest 81b572198c04d5d1.
- **Its settings are fixed by its code.** Bot code `kx3` = `kx3_r16_c12_z2_real_t0`:
  - km3 proposes a move;
  - up to 12 candidates, each played out 16 times;
  - a candidate replaces km3's move only when it is more than 2 standard errors ahead;
  - REALISTIC knowledge: the opponent's hidden cards are sampled per play-out from its 8-list meta pool, consistent with the cards the opponent has shown, or the closest list when none fits. It never reads the opponent's real list;
  - no time budget, so the result does not depend on machine speed;
  - no extra lists: `KX_EXTRA_LISTS` is unset, and the run checks this.
- **The engine is the frozen tree.**
  - Gemini's and km3's rows came from engine tree 70652fff (frozen-7: lister bd4eeb6e, baseline f35a1a99). The positions were built with pg_legal_v14. 70652fff is main-c045ede's engine (pin commit 818408be).
  - cd20a97a is the frozen pilot merged onto c045ede0. `git diff 818408be cd20a97a -- engine` is 6 files, insertions only: mod.rs (+12 lines registering `kx<N>`), playout_player.rs, playout_pool.rs, one example and two tests. No rules file changes.
  - The card data is the same file: `engine/database.json` blob 0217ade3, sha256 b5e68fc8…, the exam's frozen card data.
  - So kx3 plays under exactly the rules that made Gemini's and km3's rows.
- **Not used:**
  - The current release (7d046b6f, main-4d48844). Its rules include main-4d48844's repairs (#401 Fossil, #385, Growl-to-0, the hit back, #390), which can change legal moves or values on these positions.
  - The Oct 19 probe binary (pg_pos_blade bbc05e1f, ky3-blade). Its players differ, and its kx3 codes are not the frozen F.
- **The executable is new, because no existing one fits.** No existing binary prints frozen-7's labels: the F builds print bare names and `RetreatPay:<slot>`, and frozen-7's baseline has no kx3.
  - It is built exactly as frozen-7 built its baseline (`rl/ai_judge/build_baseline.sh` at tag judge-prompt-frozen-7), with one change: the archive is `git archive cd20a97a engine` instead of the tag's.
  - From the tag, unchanged: pgd_patch.py (904b9e86, the target-preserving printer), dg_patch.py (c98ccc63) and pg_pos.rs (224888a8).
  - Build: `cargo build --release --locked --offline --example pg_pos`, 2 jobs, nice 19, in the night window. About 4 minutes and 0.3 GB (C: has about 17 GB free).
  - Its sha256 is committed in K21's launch line before any kx3 row. The run refuses any other binary.

**2. The dry run: gates on development positions only, before any exam row.** Every gate must pass, or nothing runs on the exam. The development positions are pause-game positions (`heldout: false`), not exam positions.
- **(a) Same engine and printer.** km3 on the new binary prints free-play lines byte-identical to frozen-7's baseline f35a1a99, on 6 development positions, seeds 1-3.
- **(b) Same kx3.** The new binary's kx3 reproduces the frozen pilot's recorded lines on 3 development positions where kx3's line differs from km3's:
  - KW-261005_003547000-t11 and KW-261005_003547000-t13 (the pause-positions study, PF3 runs_B, seeds 1-3);
  - KW-261013_015659000-t05 (P8_v3 runs_F: pg_pos_F_cond2 on cd20a97a with the same pg_pos.rs; seeds 3 and 9).

  Short labels are compared as printed. Where the old printer gave a bare name, frozen-7's `Name#JSON` is compared by its name.
- **(c) The row runner.** `kx3_rows.py` copies frozen-7's `run_pg_pos` body with only its k/km name check lifted. On the development positions:
  - its km3 rows must equal `judge.py run --bot km3`'s, field for field;
  - every kx3 line must map to exactly one listed plan.
- **(d) The timing.** The gates' kx3 seconds per position and seed, set against the estimate in section 4.

**3. Points.** Run 3's 258 primary decisions in 76 games, from the frozen files at 6e5fab0c:
- positions_v2.json b75c02e1…;
- references_v2.json 650c21a7…;
- eligibility_v2.json b994a19f…

**Run 2's 49 points are NOT added** (the laptop's call), for three reasons:
- **One question, one exam.** The question is about exam v2, and the one frozen exam answers it cleanly. Pooling was registered for the Gemini v km3 question as its second stage; this question has no first stage.
- **Different build.** Run 2's v1.6 points have a different candidate view (generic notes), a different build and v1.6's segments. Mixing them brings in B1's mixture caveat for about 16% more decisions.
- **Exposure history.** Run 2's positions carry the laptop's earlier exposure records (run 1's side-run plan and its probe).

So the registered primary is run 3 alone.

**4. Seeds and nights.**
- **Seeds:** kx3 plays each decision on 3 seeds, 25,101,000,001-003, the seeds km3 used. They are paired on purpose: pg_pos fills the same unknowns for both bots on each seed.
  - The block 25,101,000,000-25,101,999,999 is registered in START_HERE for exam run 3's baseline rows. A one-line START_HERE amendment on main, naming kx3's reuse, needs Dustin's yes; K21 is the registration of record either way.
  - The gates use the development positions' own recorded seeds, plus 25,101,900,101 and up.
- **How it runs:** seed-major (all 258 on seed 1, then seed 2, then seed 3); one position at a time (kx3 uses about 11 of the laptop's 16 threads); nice 19.
  - Night window only: 02:00-13:00Z until Nov 1, 03:00-14:00Z after. Never Wednesday night Oct 28, which is Dual Fusion's release.
  - It resumes by (seed, position). A night stops cleanly at 12:50Z.
- **Nights:** Mon Oct 26, Tue Oct 27, Thu Oct 29 and Fri Oct 30. **The registered end is the close of the Fri Oct 30 window (13:00Z Oct 31).**
- **Estimate:** about 1.4-6 h per seed, so 1 night is likely and 2 nights plausible. v2 has 25,849 plans.
  - 1.4-2.4 h comes from the frozen kx3's sandbox timings on 127 positions, scaled to v2's turns and the laptop's speed.
  - 6.1 h comes from the Oct 19 probe's per-plan rate.
  - Tail risk: 9-16 h per seed, if many positions behave like the probe's slow one.
- **If 3 seeds are not complete by the registered end, decided now:** the result uses the seeds complete on all 258 decisions (2, or 1).
  - The precision cost is estimated from run 3's km3 seeds and kx3's recorded seed spread (about 2x km3's): 2 seeds widen the 95% interval by about 1-2%; 1 seed by about 4-7% (stress case about 10%).
  - With no seed complete on all 258, there is no result, and the record says so.

**5. Scoring.** No Gemini call is made. Gemini's saved run-3 primary rows are reused: `live-20261026T020013Z/judge_primary.jsonl` and `judge_primary_pass1.jsonl` at e159551d. km3's `km3.jsonl` from the same folder is reused for the descriptive contrast.
- **The primary compare:** frozen-7's `judge.py compare`
  - with `--bots kx3,judge --contrasts judge:kx3 --seeds` (kx3's complete seeds) `--judge-repeats 1`;
  - with the frozen references_v2.json and eligibility_v2.json;
  - with `--on-problem fail --failed-judge-rows miss --allow-other-binaries`.
- **Why `--allow-other-binaries` is needed:** frozen-7's freeze names f35a1a99 as the one step-bot executable. The switch makes frozen-7 mark its report "experiment" (formal: false), and it also skips frozen-7's lister-identity check. So the K21 script checks two things itself:
  - the plans binary's sha256 equals FROZEN.json's;
  - every kx3 row's pg_pos_sha256 equals the K21 binary's.

  Every other freeze check stays on: the judge rows' frozen settings, the model, the references and the eligibility.
- **The primary:** Gemini minus kx3, prefix agreement, on 258 decisions. It uses frozen-7's analysis.py: the game-clustered 95% interval (20,000 resamples, seed 20261019), the sign-flip test (100,000 draws, seed 20261020), at least 10 games, and its verdict rule. The verdict is one of:
  - "judge higher": the interval lies above 0 and the sign-flip p < 0.05;
  - "kx3 higher";
  - "inconclusive".
- **Descriptive only, no verdict:**
  - kx3 minus km3, a second compare with `--bots kx3,km3` on the same seeds and decisions;
  - the full-scope block;
  - the chance-ending stratum (168 points, `strata/`);
  - the categories.
- **Stops:** a kx3 row whose line maps to no single listed plan is a problem that stops the batch (on-problem fail), for the coordinator. None is expected: same tree, same printer.

**6. What a result means.** The interval is reported in every case.
- **"judge higher":** on these 258 decisions of exam v2, Gemini's first plan segment matches Dustin's accepted moves more often than unchanged kx3's does.
  - This is the comparison section 8 required before anyone says Gemini beats our best bot.
  - It holds on this measure only: prefix agreement, not plan quality. It says nothing about finished games or win rates.
- **"kx3 higher":** the reverse, with the same limits.
- **"inconclusive":** stays inconclusive. It is not evidence that they are equally good.
- **Unchanged either way:** run 3's filed verdict (Gemini v km3) stands, whatever this gives.
- **A limitation, recorded now:** frozen-7's own flag reads "experiment" for this report (section 5). K21 makes it the registered kx3 result.
- **The adapter is not started.**

**7. Fairness, point by point (Astra).**
- **Unchanged kx3:** section 1. The players are byte-identical to the frozen pilot, the settings are fixed by its code, and the binary's sha256 is committed before any row.
- **The same positions and information:**
  - the frozen candidate view, played through the same frozen pg_pos harness and on the same seeds as km3;
  - kx3 reads only its `PlayerObservation`: its hand, the public board, discards, points and counts, and its own deck as an unordered multiset. It samples every hidden card itself, per play-out;
  - no position holds a future card;
  - the card data is b5e68fc8 in both trees.
- **The same rules:** the frozen tree 70652fff, plus kx3's additions only. Gate (a) tests this.
- **The same scoring:** the frozen answers (6e5fab0c), the frozen lister and prefix rule (R1's segments), frozen-7's analysis.py unchanged, and Gemini's saved rows.
- **What differs, and why:** kx3 is a step bot played through pg_pos, as km3 was, while Gemini chose among the listed plans from a prompt. That is the comparison's design, the same as run 3's comparison with km3.

**8. Reads.** The K21 research workflow wf_25af41b0-78d ran Opus agents only:
- program provenance;
- timing (reading run 3's `in/positions.json` only to count forced lines);
- precision (reading run 3's `report_primary.json` rows).

No Sonnet agent was used.

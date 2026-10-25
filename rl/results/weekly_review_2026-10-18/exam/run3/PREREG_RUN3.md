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

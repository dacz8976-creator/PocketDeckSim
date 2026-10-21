# Version journal: build spec

## Purpose
Each deck gets one record of every version of its list: what changed, why, and what every test and every game said about it. That way "which Kingambit list was better, and what did we give up?" can be answered without anyone tracking edits by hand. Agents write it. Dustin only reads it, and nothing new is asked of him.

## Where it lives
- **Everything** is under `rl/deck_journal/`: the code (`journal.py`, standard library) and its tests, and `journals/<deck stem>.json` with its plain-words view `journals/<deck stem>.md`. The stem is the deck's file on main; Kingambit's is `01-muk-glimmora-kingambit-regigigas`. A version whose list is in no deck file still gets an entry; his played list `73dfed58d1d6` is one.
- **The view** is generated from the JSON by `journal.py view`, never edited by hand, and committed with the JSON.
- **Committed** on main by path, like the predictions files. Built by the Sonnet credit worker, reviewed by the laptop.
- **Append-only**: the tool refuses to change or delete an earlier entry or result. A correction is a new result that names what it corrects. The check is against main's committed copy, as `read_ladder.py` checks `versions.json`.

## Entry per version
```json
{"id": "73dfed58d1d6",
 "list": ["Energy: Darkness", "1 Alolan Grimer A3 110", "..."],
 "code_cards": {"energy": [7], "cards": ["pokemon:006910", "...", "trainer:000030", "trainer:000030", "..."]},
 "parent": "35d98d0dcaf2", "parent_basis": "stated | inferred (fewest cards changed)",
 "diff": ["-1 Copycat B1 225", "+1 Lucky Ice Pop B2 145", "-1 Alolan Grimer B2 096", "+1 Alolan Grimer A3 110"],
 "printing_only": ["Poké Ball P-A 005 -> A2b 111", "Professor's Research P-A 007 -> A4b 373"],
 "plays_same_as": null,
 "origin": "his list (filmed deck code) | agent proposal | deck file on main",
 "reason": {"text": "not stated", "by": "Dustin | <agent>", "source": "<note, message or path>"},
 "added": {"at": "<UTC>", "by": "<agent>", "commit": "<sha>"},
 "results": []}
```

**What the tool computes** (never typed by an agent):
- `id`: the first 12 hex digits of `make_predictions.card_list_sha256()` of the list, the same id the predictions files and `versions.json` use.
- `list`: deck-file lines built from (count, id) pairs, each name taken from `lib/card.py` for its id, never copied from a packet. Packet names carry curly apostrophes, and `card_list()` keeps them: `Professor’s Research` gives `672c29a25f6f` instead of `73dfed58d1d6`.
- `code_cards`: the sorted card entities and Energy that the game's deck code holds (`encode_qr.BYID[id]["entity_key"]`). A deck code names cards, not printings (Poké Ball P-A 005 and A2b 111 are one entity), so two lists with the same `code_cards` are one list in the game and cannot be told apart on video.
- `diff` (changes in `code_cards`, written as list lines) and `printing_only` (same entity, a different printing written). When `code_cards` are equal, `plays_same_as` names the earlier version, the two share their setup numbers, and the view merges them. A printing difference is never reported as a change he made.

**Results** are append-only; each carries the date, the writer, the source path and its commit:
- `setup`: the run folder, the tester code's sha256, the seeds, the deal count and the clock; each measure's x/n and Wilson range; the paired difference from the parent, if that run had both.
- `bot`: built by `make_predictions.harness_bots` (slow reports, exams, replays) or `floor_bot` (floors). They check that the run tested this file or a committed copy with the same card list, label the bot and engine, and mark older engines. A bot number is filed only under the id that bot played. Every Kingambit bot number so far was played on `35d98d0dcaf2` (deck 01), not on his list.
- `ladder`: from a counting reading by `read_ladder.py` (`rl/results/ladder_validation/readings/<file>`): the section, the tie (assumed, or confirmed by a `versions.json` note), the test record, the feedback record, wins by concession (full wins), and the card check. **A version with no predictions file**: the games whose `versions.json` note names its id (read with `read_ladder.load_versions`), each as feedback, with the Ladder Log result. No other tie logic.
- `played`: one per game seen in a review packet: the video name, the packet path, the binding (next section), and the result if known. It is not a ladder game unless the Ladder Log has it.
- `note`: free text, for example "deck 01's file on main is not the list he plays".

**First fill**, part of the build: the Kingambit journal starts with two versions.
1. **Deck 01** (`35d98d0dcaf2`): origin "deck file on main", committed Sept 24 (83fd3496), with its existing bot results: replay_b on the current engine (64 games, km3 and kx3), plus the older-engine strength runs and floor, marked older.
2. **His list** (`73dfed58d1d6`): parent deck 01, with 12 `played` games from the Oct 12-13 packets, all bound by their filmed deck code. Reason: "not stated".

The two Haxorus lists (`95c08feb018c`, `b59ea966702c`) go to their own deck's journal.

## Who writes it, and when
The agent that produced a result writes it, right after its run or reading is committed:

| Event | What the agent writes |
|---|---|
| A setup tester run | `setup` |
| A slow report, exam, floor or replay | `bot` |
| A counting reading by `read_ladder.py` | `ladder` |
| A new review packet | `played`, plus a new version if the list is new |
| His note or message about a change | A new version, with his reason |

- Agent-made versions he has not played are entries with origin "agent proposal" and the proposer's reason.
- Writes go only through `journal.py add-version` or `journal.py add-result`, which check that: the id is recomputed from the list; the list passes `lib/deck_check.py`; the parent exists; the source path exists and is committed; a bot result's list matches (via the functions above); nothing earlier changed.

## How a version he actually played is detected
From strongest to weakest; the method is saved as the result's `binding`:
1. **Filmed deck code.** Each packet's `QR_DECODE.json` holds the code filmed at the start of the video (key `payload`, or `qr_payload` in 230258; `DECK_USED.json` has no common field: only 203719 has `filmed_deck_snapshot`, and its `game_version_binding_basis` is empty). Read the code's bytes (base64; layout in `encode_qr.py`'s docstring) into `code_cards` and match a journal version. Compare card sets, never code strings: the game orders the code its own way (the KW files' line order reproduces all 12 filmed codes exactly; the same cards sorted give a different string). All 12 Oct 12-13 Kingambit packets match `73dfed58d1d6`, and none matches deck 01.
2. **The Ladder Log deck catalog** (`LIVE_DECK_CATALOG.json` in the newest packet batch): the saved code when the catalog was exported. It has no edit history, so it shows the list at export time, not at play time; its binding is "catalog, unconfirmed" until 1 agrees.
3. **His note** in the Ladder Log or in chat ("swapped X for Y"). The agent writes the list; the binding stays "his note, unconfirmed" until 1 or 2 agrees.
4. **Cards seen in play.** These never make a version. They can only rule one out: a card not in the list is a "mismatch", as in `read_ladder.py`'s card check.

**Rules for detection**: new `code_cards` from 1 or 2 become a new version, with an inferred parent and the reason "not stated"; nobody asks him. Its printings are the parent's for cards the parent has, else `card_canon`'s base id. Lists are filed by id and `code_cards`, never by file name; that keeps the two Haxorus KW files out of Kingambit's journal. **Known gap**: `read_ladder.py` assumes each game was played with the deck file on main at the time. For Kingambit that file is `35d98d0dcaf2`, while he plays `73dfed58d1d6`. Until the laptop decides whether to update deck 01's file, every Kingambit ladder game needs a `versions.json` note whose `version` confirms the tie; the journal's `played` results supply the evidence path.

## The plain-words view for Dustin
Generated, newest version first, one short block per version. It adds no new place he must visit: agents link it, or paste a block, when they report a deck change. The shape, numbers left out:
```
Kingambit: 2 lists recorded
NOW PLAYING  73dfed58d1d6  (in 12 of your games, Oct 12-13, from the deck code on video)
  Changed from the deck-01 file: 1 Copycat out, 1 Lucky Ice Pop in;
    Alolan Grimer A3 110 in place of B2 096 (a different card).
  Why: not stated.
  Setup odds: Kingambit in play by your turn 3: going first xx% (xx-xx), second xx% (xx-xx).
    Kingambit hits for 140+ before the opponent has 3 points (your 12 games' pace): ...
  Bots: none on this list yet.
  Your ladder games: none logged.
OLDER  35d98d0dcaf2  the deck-01 file (Sept 24)
  Bots: frozen kx3, current engine, replay: xx% (xx-xx), kx3 games n of N total.
```
**Rules for the view**: every number says what it is (setup odds, bot plus engine, or his games) and gives its range; a clock number names its clock. A bot number never appears under a list that bot did not play. Older-engine numbers say "older engine". Ladder records say test or feedback, with the number of games. Printing-only differences are not shown. At most about 10 lines per version; versions that play the same are one block.

## Tests to write first
- The id equals `card_list_sha256` for deck 01 (`35d98d0dcaf2`) and a KW Kingambit list (`73dfed58d1d6`); each Haxorus KW list gets its own id.
- Deck 01 → his list gives exactly the 4 diff lines, with Poké Ball and Professor's Research under `printing_only`, not `diff`.
- All 12 Kingambit packets' filmed codes bind to `73dfed58d1d6`; deck 01 binds to none; a list re-encoded in sorted order still binds (card sets, not strings).
- His list with Poké Ball written as P-A 005 gets a new id, `plays_same_as` his list, and shares one view block.
- A packet list with `Professor’s Research` still yields `73dfed58d1d6`; the tool never produces `672c29a25f6f`.
- Append-only: editing or deleting an earlier result is refused; adding the same result twice (same source and commit) is refused.
- A bot result whose source played a different list is refused.
- A game whose `versions.json` note names a version without a predictions file comes out as feedback.
- The view never shows deck 01's bot numbers under his list, and the same input always gives the same view.

## Out of scope
- Judging which version is better; the setup tester and the readings do that.
- New duties for Dustin.
- The tool never edits deck files, `read_ladder.py`, `make_predictions.py` or `versions.json`. Agents add notes to `versions.json` by its own rules (`rl/results/ladder_validation/DETAILS.md`, section 3).

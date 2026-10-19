# Exam of Dustin's ladder decisions, 2026-10-19

## What it is
The exam holds 51 decision points from 27 of Dustin's real ranked games (Oct 14-16). Each point is one whole turn of his.
- **Each point gives:** the board, the engine's full list of legal first actions, what Dustin did, and any other turns a strong player with the same plan could reasonably have chosen.
- **It asks:** does a bot play these turns the way a good player of his decks would?
- **No bot has seen it:** no bot was developed on these games (they aren't in stage A, the Oct 18 diagnostic or the pause-game sets), and no bot has been run on these positions.

File: `exam_2026-10-19.json`, format `pds-exam-v1.1`. One file serves any bot: km3, kx3, the AI judge, and later an external bot through upstream's `docs/bot-protocol.md`.

## What a candidate may see (`bot_view`)
A candidate sees only `points[i].position` and `points[i].legal_root`.
- **`position`:** pg_pos's input. It carries no "force" line and no hidden future: no deck order, no next draw, no coin result.
- **`legal_root`:** the engine's legal first actions. These are the full list, not any bot's candidates.
- **The answer key:** everything under `points[i].answer`, and `answer_kind`. It must never be shown to a candidate, the AI judge included.

## The file
- **Top level:**
  - `decks`: the list file, deck kinds and why;
  - `categories`, `coverage` and `untested`;
  - `scoring`, `free_chance_first_decision` and `known_limits`;
  - `points`.
- **Each point:**
  - `id`, `game`, `deck`, `deck_kinds`, `answer_kind`, `source` (the game's REVIEW.md and the turn), `position` and `legal_root`;
  - `answer`, which holds:
    - `his_move`: his whole turn, as engine labels;
    - `first_segment`: his actions up to and including his first chance action;
    - `acceptable`: other whole turns, each with a reason;
    - `ambiguous`: a question for Dustin, or null;
    - `why_his`;
    - `legal_steps`: the engine's legal list at each step of his line, up to the first hidden draw or coin;
    - `free_chance_first_variants`.

## Scoring (fixed before any bot runs)
- **Plans stop at the first chance event:** a draw, a search, or a coin, free or not.
- **A correct first segment:** a candidate's first segment is its actions up to and including its first chance action, or its whole turn if it has none. It is correct if, as a set, it equals `answer.first_segment` or the first segment of an `acceptable` line.
- **Free chance steps first:** none of the 51 positions offers a free optional chance step among its first actions. There's no Mesagoza in play and no coin-flip Ability. The only Stadium action at a root is Rainbow Cave's, which isn't a chance event. So there are no "free chance step first" variants. This was decided before any bot run.
- **Independence:** points carry their game id, because turns from one game aren't independent. Results use a game-level bootstrap, paired across bots, and an unclear difference is reported as "inconclusive".
- **Reporting:** per deck kind and per answer kind. There is no single pass/fail.

## Deck mix
| deck | points | deck kinds (how it must be played) |
|---|---:|---|
| 12 (Whimsicott ex / Ariados / Ogerpon ex) | 14 | fast pressure, evolution and setup, Bench preparation, control and combinations |
| 13-A (Alolan Ninetales ex / TR Raticate ex) | 23 | evolution and setup, Bench preparation, control and combinations |
| Kingambit, list A | 14 | evolution and setup, Bench preparation, sacrifice and recovery, control and combinations |

Kingambit is one hard case (27% of points), not the gatekeeper. The answer kinds are prepare 24, attack now 22, sacrifice 5 and abandon 0.

## Coverage, deck kind x answer kind
A point usually tests more than one deck kind, so the rows aren't independent and add up to more than 51.

| deck kind | prepare | sacrifice | attack now | abandon |
|---|---:|---:|---:|---:|
| fast pressure | 0 | 0 | 7 | 0 |
| evolution and setup | 14 | 3 | 12 | 0 |
| Bench preparation | 18 | 4 | 10 | 0 |
| sacrifice and recovery | 3 | 2 | 2 | 0 |
| control and combinations | 16 | 3 | 15 | 0 |

## What is untested
- **Abandon:** there are no points. None of his usable recorded ladder turns had him drop his plan.
- **Fast pressure:** there are only attack-now points (7), all from deck 12.
- **Sacrifice:** there are 5 points, so results are indicative only.

## How the labels were made
- **His move by default:** `his_move` is exactly what he did. It was checked label by label against the engine (BUILD.md).
- **Alternatives:** the Opus labelling agent added them from the review, the card text and the Pocket rules. They appear only where another whole turn was comparable, and each has a one-line reason. There are 13 across 11 points.
- **Ambiguous points:** 5 points carry a question for Dustin. Their alternatives are marked "(pending Dustin's answer)".
- **No bot output was seen while labelling.** No bot ran, and no bot result files were opened.
- **The laptop's final check:**
  - It removed each position's `kind` field, which leaked the answer kind.
  - It moved the answer key under `answer`.
  - It added `first_segment`.
  - It recorded the free-chance decision.

## Known limits
- **Order around a draw:** it is scored as he played it. In 11 points his first segment has other actions before the draw, and a candidate that draws first is scored wrong there. These weren't reviewed one by one; revisit them only if a result hinges on them.
- **Approximate positions:** every position is approximate on the opponent's side. Their list is unknown, and their hand size and discard are estimated from the review (BUILD.md).
- **Engine quirk:** in LAD-20261016_024253000_iOS-t1 (going first), the engine lists `Attach:1Darkness@0 zone` as legal. Pocket gives no Energy on the first turn of the player going first, so this is probably how the position marks the first turn. A candidate that attaches there is breaking a rule, not choosing an alternative.

## Provenance (`build/`)
- **The inventory:** INVENTORY.md and inventory.json, covering 36 games and 178 of his turns: 91 usable and 19 near-usable.
- **The selection and build:** selection.json, BUILD.md, positions.json and legal.jsonl.
- **The legal-moves-only patch:** `pg_pos_legal_only.diff`, applied to stage A's pg_pos source. It never constructs a bot.
- **The worker briefs:** INV, A and B.
- **Cost:** credit jobs of $1.95 (inventory), $4.14 (build) and $2.35 (labels).

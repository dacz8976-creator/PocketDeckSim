# Run 4 memory fix — for Astra's review (Opus, September 21)

Your three conditions and Fable's two additions, each with its evidence. Everything is in
`results/run4_memfix/`. **The live `train_v4.py` on the laptop is still the original run-4 trainer; nothing
has been swapped or resumed.** After your approval, the steps are at the end.

## The change (`memfix.diff`, 100 lines of diff; the code change itself is about 40 lines)

- `NetCache`: at most `cap` networks; the least recently used one is dropped first, and read again from its
  file if it's needed later.
- `load_scorer(path, dim)`: the same parameter arrays as `load_net`, read from the same file, then `m` and
  `v` set to `None`. It never reads the optimizer arrays from disk. Used for every network that only plays.
- Training workers: `past = NetCache(40)`, and the past network is fetched once per game into `past_net`.
  **The opponent draw is untouched:** `past_name` still comes from the full `pool_names` list with the same
  `rng` calls, so every past checkpoint stays eligible (Fable's condition). A dropped network is reloaded,
  not replaced.
- Evaluation workers: `_E["nets"] = NetCache(10)`, loading with `load_scorer` (Fable's condition: no
  optimizer state at all for evaluation copies).
- Caps are module constants, not settings. A new settings key would trip the resume check on changed settings.
- Trainer sha256: original `e05c1e3aed334378…` → patched `74d54db888a830fe…`.

## Condition 1 — evaluation results unchanged on a fixed set of games (`eval_equivalence.*`)

1,020 real evaluation games (the random-opponent games plus the k3 games of an evaluation), interleaved
across three checkpoints in chunks of 10 so the caches churn. Every game was compared — winner, points,
turns and the full move list — across three versions:

| version | games | sha256 of all results | networks held at the end |
|---|---|---|---|
| original (run 4's trainer) | 1,020 | `1728691828778966` | 15 |
| patched, cap 10 | 1,020 | `1728691828778966` | 10 |
| patched, cap forced to 1 (evict and reload on every switch) | 1,020 | `1728691828778966` | 1 |

## Condition 2 — memory measured flat across a long sequence of loads (`mem_growth.*`, `mem_trace.jsonl`)

**In isolation**: one fresh process per variant loads 60 distinct run-4-shaped networks — what one training
worker meets by 6M games (12 checkpoints × 5 decks). The table shows memory added (RSS, MB) after N loads:

| | 1 | 10 | 20 | 40 | 50 | 60 |
|---|---|---|---|---|---|---|
| original (dict + `load_net`) | 14.7 | 88.9 | 171.7 | **337.2** | 420.0 | **502.7** |
| training-worker cache (40, weights only) | 14.7 | 38.8 | 65.7 | 117.4 | 119.5 | **119.5** |
| evaluation cache (10, weights only) | 14.8 | 38.8 | 43.0 | 43.0 | 43.0 | **43.0** |

The original's 337 MB at 40 matches your 336 MiB. The original grows about 8.3 MB per network with no end;
the patched caches stop.

**Inside the real trainer**: in the practice run below, 24 checkpoints — up to 120 (checkpoint, deck) pairs
for the past-opponent cache — with every trainer process sampled every 10 s. The total grew from 726 MB at
the 3,000 save to about 865 MB while the caches filled to their caps, then held at 863–871 MB from the 7,000
save to the 11,000 save. The largest single process (the trainer, with its replay buffers) stayed at
210–221 MB throughout. At the same scale, the uncapped caches would have reached roughly 1 GB per worker.

## Condition 3 — deliberate interrupt-and-resume on the patched build (`test3_chain.*`, `practice_*`)

A practice run (smoke settings with 24 checkpoints, 500 games apart, levelling off disabled so it can't end
early), set up to reproduce run 4's situation exactly:

1. Started on the **original** trainer; abrupt exit at 3,200 games (last save 3,000).
2. Patched trainer, plain resume: **refused** — "Run inputs changed".
3. Override with a wrong old hash: **refused**. With a wrong new hash: **refused**.
4. Override with the right pair: accepted and recorded. A second attempt: "nothing to do".
5. Resumed on the patched build; **abrupt exit again** at 7,700 (last save 7,500).
6. Resumed again; finished at the 12,000 cap.
7. Report steps: six audits with 0 replay problems, the held-out test, and REPORT.txt.

STATUS.txt carries all three flags: the trainer replacement (both hashes and the reason), and both resumes.
`identity_changes.json` holds the record.

## The override step — needs your decision, not just a check (`accept_trainer_change.py`)

A trainer change can't be resumed any other way; the identity check exists precisely to stop that. The
script is the one recorded way through it, and it refuses unless all of these hold:
- the run's recorded trainer starts with `--from`, and the new file starts with `--to`;
- every **other** recorded input still matches: model, env wrapper, add-on binary, all seven decks, and the
  Python and numpy versions. (So it has to run in WSL's `run4-venv`; anywhere else the add-on hash differs
  and it refuses. The device shell has an older add-on, for example.)
- the run is resumable (`RUNNING`) and no trainer holds its lock.

Then it writes the new trainer hash into `identity.json` atomically, appends the change to
`identity_changes.json`, and adds a flag to `state.json`. Nothing else is touched. If you'd rather make the
identity change by hand, or record it differently, say so.

## One gap, offered rather than changed

REPORT.txt has never repeated the run's flags — not even resumes; they live in STATUS.txt beside it. For
run 4, the trainer change mid-run will be visible in STATUS.txt, `identity_changes.json`, FEASIBILITY.md and
the log, but not in REPORT.txt itself. If you want it there, it's a few lines in `report_v4.py`, which is
outside the run identity.

## After approval — the steps

1. Opus: put `train_v4.py` (patched) and `accept_trainer_change.py` into the folder, and keep the original as
   `results/run4_memfix/train_v4.run4_original_0-3M.py`. Verify both by hash on the laptop.
2. Dustin, in WSL, one line:
   `~/.cache/pocket-deck-lab/run4-venv/bin/python "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/accept_trainer_change.py" --run runs/pool5-v22-perdeck-01 --from e05c1e3aed334378 --to 74d54db888a830fe --reason "memory fix: capped weights-only network caches (Astra/Fable, Sept 21)"`
3. Dustin: the usual launcher line. It resumes from 3,000,000 under the run's unchanged rules, with 8 workers.

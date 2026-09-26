# Altaria detector network: the readout scripts (built Sept 25, before the run finished)

These scripts read `rl/runs/diag-altaria-lucario` once it has finished. The reading they apply is the run's own
`PRESET_READING.md`, fixed before training. **Nothing in this folder has read an Altaria training result.** What the
sessions building them saw of the run is listed under "Transparency" below. All three scripts refuse to run until
`state.json` has its verdict, and `readout.py` also waits for `REPORT.txt` and both knockout-audit files.

They are the Hydreigon readout's three scripts (`../hydreigon_network_readout/`), with these made into options:
- the focus deck and the opponent deck;
- the Limitless value;
- the audited attacks and abilities;
- the knockout rule.

`--preset altaria` is the default and fills in Altaria's values. `--preset hydreigon` gives the Hydreigon readout
back, text for text (see "Regression proof" below).

## What each script does

| Script | What it plays | Add-on | Answers |
|---|---|---|---|
| `readout.py` | Network v network on the run's 2,000 bar deals. It also replays the Altaria network's confirmation games from their recorded moves, and checks that the network re-chooses every move. | the verified 0.7.2 wheel (run5 venv) | PRESET items 1 and 3; the identity gates |
| `kp3_rows.py` | net\|kp3, kp3\|kp3 and kp3\|k3 on the same deals. Before that, the identity gate: k3 v k3 must equal the bar rows, and network v k3 must equal the confirmation rows move for move, on the first 200 deals. Otherwise it stops. | the diagnostic build (`PDL_ADDON_DIR`; sha256 `c048388b…` is checked) | PRESET item 2 (decisive) and item 1; item 3 for "network against kp3" |
| `k3_counts.py` | k3 v k3 (`--bot k3`) or kp3 v kp3 (`--bot kp3`) on the bar deals. It replays through the add-on and counts Altaria's play with the same code as `readout.py`. It needs no network. | wheel (k3; it stops if `PDL_ADDON_DIR` is set) / diagnostic build (kp3; sha256 `c048388b…` is checked) | PRESET item 3: the k3 and kp3 columns |

- **The audit (PRESET item 3) is counted by the same code** (`readout.look()` and `readout.tally()`) in all three scripts. Each script prints its own pilots with the same lines, so the tables line up.
- **Pilots and games.** Network v k3 is the replayed confirmation games; network v network and network v kp3 are played live; k3 and kp3 are on the bar deals.
- **What is counted:**
  - **Attacks:** Mega Harmony, Hypnoblast, Dark Slumber, Sing, Sleepy Lullaby and Stampede. Per turn the attack was on offer: used, passed or "other", each split by whether it would knock out. The split uses the sure-knockout rule; under each row, a second row splits the same turns by the fixed (printed-damage) rule, so the Hydreigon table stays comparable.
  - **Boosted Evolution:** the turns the Active Eevee could evolve only because of it, and how often it did.
  - **Bad Dreams:** counted as Asleep turns created, with the Darkrai-in-play share and the count's limits printed beside it.
  - **Mega Harmony:** the bench size each time it is used.
  - **Attacking and benching** on the turns each was on offer.
- **Where the card names come from:** the run's own deck file, looked up in `lib/card.py`'s database. A name that no card in the list has stops the script.
- **Checked names.** Checked against `python3 lib/card.py` for every id in `decks/research/altaria.txt`:

  | Card | Attacks | Ability |
  |---|---|---|
  | Swablu | Sing | |
  | Mega Altaria ex | Mega Harmony | |
  | Eevee | Stampede | Boosted Evolution |
  | Espeon | Hypnoblast | |
  | Darkrai | Dark Slumber | Bad Dreams |
  | Igglybuff | Sleepy Lullaby | |

  - Those are all the attacks and abilities in the list.
  - The four whose text puts the opponent's Active to sleep are Sing, Hypnoblast, Dark Slumber and Sleepy Lullaby.

## How to run it, once the run has finished

- **When:** `STATUS.txt` says FINISHED, and `run_training_v5.sh` has written `REPORT.txt` and both knockout-audit files, `results/ko_audit/v5_diag-altaria-lucario_{altaria,lucario}_<pick>.json`. `readout.py` refuses until all three exist (its text is written once and never overwritten). `--allow-missing-report` runs it anyway, only if a report step failed; section 3 then says MISSING.
- **Where:** inside WSL, from the `rl` folder, with `PY=/home/dacz8976/.cache/pocket-deck-lab/run5-venv/bin/python` and `DIAG=/home/dacz8976/diag-kp-addon/module`.
- **Workers:** the default is 3. `--workers 8` is fine once the laptop is idle.
- **Times** are measured on the Hydreigon run with 3 workers while training ran. The Altaria count dry run went at the same pace, about 0.2 s per deal. With 8 workers on an idle laptop, expect about a third of these.

```
nice -n 19 $PY results/altaria_network_readout/readout.py   --run runs/diag-altaria-lucario                       # ~5 min
PDL_ADDON_DIR=$DIAG nice -n 19 $PY results/altaria_network_readout/kp3_rows.py --run runs/diag-altaria-lucario   # ~15 min
nice -n 19 $PY results/altaria_network_readout/k3_counts.py --run runs/diag-altaria-lucario                       # ~8 min
PDL_ADDON_DIR=$DIAG nice -n 19 $PY results/altaria_network_readout/k3_counts.py --run runs/diag-altaria-lucario --bot kp3   # ~9 min
```

- **Order:** `readout.py` first, since it checks the identity gates and gives item 1. Then `kp3_rows.py`, the decisive row. Then the two counts.
- **Where results go:** each script writes its text here and never overwrites (a taken name gets a time suffix):
  - `readout.txt`, `kp3_rows.txt`, `k3_counts.txt`, `kp3_counts.txt`;
  - beside them, the games or per-game counts as `.jsonl`: `readout_nvn_games`, `readout_counts`, `kp3_rows_games`, `k3_counts_games`, `kp3_counts_games` (the Hydreigon regression's came to 6 MB; Altaria's audits six attacks instead of one, so expect somewhat more).
- **Keep `PDL_ADDON_DIR` unset** for `readout.py` and for `k3_counts.py --bot k3`: they must run on the verified wheel. `readout.py` ignores the variable; `k3_counts.py --bot k3` stops if it is set.
- **The diagnostic build's sha256** (`c048388b…`, `readout.DIAG_ADDON_SHA`) is checked by `kp3_rows.py` and by `k3_counts.py --bot kp3` before anything is played. There is no option to accept another build.
- **Early warning:** `kp3_rows.py --precheck` plays only the k3 v k3 half of the identity gate, needs no verdict, and prints match counts only.

## Which line answers which PRESET_READING item

| PRESET_READING | Where |
|---|---|
| Before anything is read: the pair checks | Done before training (`../altaria_pair_checks_2026-09-25/`). `readout.py` section 4 says so; nothing here reruns them. |
| Before anything is read: the identity gates | `readout.py`: the "Replays:" line in section 2, and "Identity gates" in section 4 (games replayed exactly; the network re-chose every recorded move). `kp3_rows.py`: the two "Identity, first 200 deals" lines, and "STOPPED" at the top if they fail. |
| 1. The run's own RUN5 line | `readout.py` section 4, "Item 1" (state.json's confirmed margin, with yes/no for +10). Table 1's row "network Altaria v k3 Lucario" recomputes it with its paired interval, and the "Check:" line under table 1 confirms it matches. Also in `kp3_rows.py`'s READING, "Item 1", and its line "net\|k3 - k3\|k3". |
| 2. The decisive D | `kp3_rows.py`: the line "DECISIVE net\|kp3 - kp3\|kp3" (points ± 95% interval), then the READING line "D = …" (two decimals, from the exact won-only counts, so exactly +10.00 reads as "+10 or more") with PRESET's own wording for +10 or more and for under +10. It warns "NOT THE PRE-SET READING" if fewer than all 2,000 deals were played or the identity gate had fewer than 200 deals. |
| 3. Use rate per offered turn of every attack, split by knockout | The attack blocks: `readout.py` section 2 (network v k3, network v network), `kp3_rows.py`'s audit block (network v kp3), and `k3_counts.py` (k3 v k3 and kp3 v kp3). Each row is the sure-knockout split; the row under it, "fixed rule (printed damage), same turns", is the fixed rule's split of the same turns. |
| 3. Boosted Evolution | The "Boosted Evolution (Eevee): turns the Active Eevee could evolve only because of it / turns it evolved then" lines, in the same scripts. |
| 3. Bad Dreams as Asleep turns created | The "Bad Dreams (Darkrai) is automatic; counted as Asleep turns created" lines, in the same scripts: the count per 100 turns, "with Darkrai in play N of M (share)", and a "Limits:" line under them. |
| 3. Bench size when Mega Harmony is used | The "Bench size when Mega Harmony was used" lines (counts at 0/1/2/3 benched, and the mean), in the same scripts. |
| 3. Benching and attacking on offered turns | The "Attacking and benching on offered turns" lines, in the same scripts. `readout.py` checks its network v k3 numbers against the knockout audit's "bot" line, and `k3_counts.py` checks k3's against the audit's "k3" line ("Check: … equal"). |
| 3. The knockout audit | `readout.py` section 3: both networks' audit tables from `results/ko_audit/`, with a check that the audited weights are the ones read here. This is the run's own audit, network against k3, not "network against kp3" as PRESET says; section 3 prints this as a stated deviation (see below), and `kp3_rows.py`'s audit block points to it in one line. |
| 3. Network v network against Limitless, with the Lucario network's flaws beside it | `readout.py` table 1's row "network v network (new)" and section 4, "Network v network against Limitless (Altaria 71.9 ± 4.9)". The line under it gives the Lucario network's missed sure knockouts and sure wins, and its attack and bench rates, next to k3 piloting Lucario on the same bars. |
| 4. No follow-up training | `readout.py` section 4's last line (a statement; nothing is trained here). |

## Definitions the pre-set reading left open

Fable (the reviewing session) approved the three audit definitions on Sept 25, before the run finished, with the notes
below. The notes were written into the scripts before any Altaria readout ran. Each definition is an option, so
another choice needs no code change.

- **"Would knock out"** (`--ko-rule`):
  - **What Altaria uses (`engine`), the primary rule:** the knockout audit's "sure knockout". In each of 4 copies of the true game under different chance seeds, the move gains the pilot at least one point. The copies are analysis only; the game itself is not touched.
  - **What Hydreigon used (`fixed`):** the attack's printed damage against the Active's HP left.
  - **Why the change:** the printed damage is wrong for this list. Mega Harmony's printed 40 leaves out its +30 per Benched Pokémon. Lucario's Pokémon are weak to Psychic (+20), Training Area adds 10 to Stage 1 attacks, and Bad Dreams hits at the end of the turn.
  - **Fable's note, done:** every attack block of the Altaria reading also prints the fixed rule's split, labelled "fixed rule (printed damage), same turns", in the row under each sure-knockout row. That is `readout.py` (network v k3, network v network), `kp3_rows.py` (net\|kp3) and `k3_counts.py` (k3 and kp3). So the Hydreigon table stays comparable.
  - **One line in each text says the two rules are not interchangeable:** the fixed rule ignores Mega Harmony's bench bonus, Weakness, Training Area and Bad Dreams.
  - **The fixed split changes nothing else.** It is a second reading of the same position at the same decision (the Active's HP left against the legal move's printed damage). It plays no move and calls nothing in the engine. Used, passed and "other" are the same in both splits; only the knockout columns can differ. The checks are under "Regression proof", in "The fixed-rule split and Fable's other notes".
- **Boosted Evolution "offered":** Eevee is Active, an Evolve move onto the Active spot is legal, and it is the player's first turn or the turn Eevee was played. Those are the only turns the ability changes anything. The engine's own test is `turn_count <= 2` or played this turn (`engine/src/move_generation/mod.rs`).
- **Asleep turns created (Bad Dreams):**
  - **What counts:** a turn of the pilot's that ended with Sing, Hypnoblast, Dark Slumber or Sleepy Lullaby used without a knockout (sure-knockout rule). Also counted is whether a Darkrai was in play then. Bad Dreams needs a Darkrai in play to hit.
  - **Rate:** per 100 of the pilot's turns with a choice.
  - **Fable's note, done: its limits are printed beside the count,** so nobody reads it as damage dealt. It counts sleep attacks used, not damage. Waking at the Checkup and the Bad Dreams hits that actually landed are not tracked. A sleep attack on an Active that was already Asleep also counts.
  - **The Darkrai-in-play share** is printed beside the count ("with Darkrai in play N of M (share)").
- **The kp3 identity gate** is 200 deals, as for Hydreigon, since PRESET asks for "the same identity gates". `--identity-games 2000` checks every deal, for about 60% more time.
- **The knockout audit: a stated deviation.** PRESET item 3 asks for the audit "network against kp3". The knockout audit shown (`readout.py` section 3) is the run's own, network against k3. `readout.py` prints this in section 3 as a stated deviation, with its reason and limits:
  - **Reason:** a knockout audit of net\|kp3 would be new code.
  - **What it doesn't touch:** the decisive D (net\|kp3 win % minus kp3\|kp3 win %) is unaffected.
  - **What is covered anyway:** the attack and bench counts for net\|kp3 are live in `kp3_rows.py`'s audit block, which says in one line that the knockout audit isn't played against kp3 and points to `readout.py` section 3.
  - **Later:** a knockout audit against kp3, if ever needed for a decision, is a later registered addition.

## Regression proof on the Hydreigon run

Run on the finished Hydreigon run, with `--preset hydreigon`, 3 workers, `nice -n 19`. All outputs went to a scratch
folder; nothing under `../hydreigon_network_readout/` or `rl/runs/` was changed.

**First 200 deals, run side by side with the original scripts.**
- **Texts:** all four (`readout`, `k3_counts`, `kp3_counts`, `kp3_rows`) are identical line for line to the originals', apart from the date and the "Took" time.
- **Network v network:** 200 of 200 games equal `readout_nvn_games.jsonl` on disk (winner, points, turns, every move).
- **kp3 rows:** 600 of 600 games equal `kp3_rows_games.jsonl` on disk (all three rows; winner, points, turns, every move).
- **Identity gate:** passed on all 200 deals.

**All 2,000 deals, the generalised scripts alone, against the files on disk.**
- **Texts:** `readout.txt`, `k3_counts.txt`, `kp3_counts.txt` and `kp3_rows.txt` are identical to the files on disk, line for line, apart from the date and the "Took" time. So every number is reproduced, including the decisive +25.2 ± 2.6 and the identity gate (200 of 200, and 200 of 200).
- **Network v network:** `readout_nvn_games.jsonl` is byte-for-byte identical to the file on disk (2,000 games).
- **kp3 rows:** 6,000 of 6,000 games equal `kp3_rows_games.jsonl` (winner, points, turns, every move).
- **The new attacking/benching counter agrees exactly with the knockout audit** (`results/ko_audit/v5_diag-hydreigon-lucario_hydreigon_ckpt_2000k_avg.json`):

  | Pilot | Attacked | Benched | Audit's line |
  |---|---|---|---|
  | Hydreigon network v k3 | 6,174 of 6,806 turns | 2,978 of 4,487 | "bot": the same |
  | k3 on the bars | 6,291 of 7,805 | 3,384 of 3,502 | "k3": the same |

- **Times** (3 workers, `nice -n 19`, training running alongside): readout 257 s, k3 counts 404 s, kp3 counts 467 s, kp3 rows 838 s.

**The new Altaria code was also run in full on the Hydreigon run, as a code test.** That means the generic text, the engine knockout rule, the knockout-audit section and the end-of-run checks, all of which print only on all 2,000 deals. The run used `--deck hydreigon --attacks "Hyper Ray,Darkness Claw,Headbutt,Dark Cutter" --abilities "Roar in Unison" --ko-rule engine`.
- **It ran through,** with every check line passing:
  - the confirmed margin (+40.8, the same);
  - the network's attacking/benching (6,806 / 6,174 / 4,487 / 2,978, equal to the audit's "bot" line);
  - k3's (7,805 / 6,291 / 3,502 / 3,384, equal to the audit's "k3" line);
  - the identity gates (2,000 of 2,000 replays; 39,969 of 39,969 moves re-chosen).
- **Times:** 293 s for the readout and 454 s for the k3 counts, with 3 workers. The engine knockout rule adds about 10-15%.

**The fixed-rule split and Fable's other notes (Sept 25, about 23:25, before the run finished).** The same kind of
checks, small, on the finished Hydreigon run. 3 workers, `nice -n 19`, outputs in scratch; nothing under
`../hydreigon_network_readout/` or `rl/runs/` was changed.
- **`--preset hydreigon` is unchanged.** First 40 deals, the original scripts and these side by side:
  - **Texts:** all four (`readout`, `k3_counts`, `kp3_counts`, `kp3_rows`) are identical line for line, apart from the date and the "Took" time.
  - **Games:** network v network, 40 of 40 equal `readout_nvn_games.jsonl` on disk. The kp3 rows, 120 of 120 equal `kp3_rows_games.jsonl` on disk (winner, points, turns, every move).
- **The Altaria-style path, before and after the change.** First 20 deals, `--deck hydreigon --attacks "Hyper Ray,Darkness Claw,Headbutt,Dark Cutter" --abilities "Roar in Unison" --ko-rule engine`, all four invocations. "Before" is the committed scripts (c8d0548).
  - **The games are the same:** the network v network file is byte-identical, and so are all the kp3-row and count games.
  - **Every engine-rule number is the same:** each game's counts are equal once the new fixed-rule split is taken out.
  - **The texts differ only by added lines:**
    - the fixed-rule rows;
    - the wording under "'KOs' =": "This rule is primary." added to its last line, then three new lines (what the fixed-rule row is, and "not interchangeable");
    - the deviation paragraph in section 3;
    - a pointer to it in section 4's Item 3 line.
- **The fixed-rule split is exactly the Hydreigon rule.** In every game of every script, it equals the main split of a `--ko-rule fixed` run on the same deals. That run's games are the same too.
- **Only the knockout columns differ between the two splits.** Used, passed and "other" are equal in every game.
- **The two rules really do disagree on some turns.** Darkness Claw, for example: under the sure-knockout rule the network used it on 0 knockout turns and 18 non-knockout turns in its 20 confirmation games; by printed damage, 8 and 10.
- **The Altaria-only lines (the Asleep block with its share and limits, and the transparency note)** were checked by printing the Altaria preset's blocks with all-zero counts (nothing played; no run file read). The review below also ran them: the Asleep block on real Altaria games, the note with the reading forced to "altaria".

**Review of that change (Sept 25, about 23:45, before the run finished).** A second session re-checked it on deals
the editor didn't use: i = 1500 to 1529 of the Hydreigon run (30 deals). Each script ran from a scratch copy whose only
change was that deal range (the same one-line change in every copy). 3 workers, `nice -n 19`, outputs in scratch.
- **`--preset hydreigon` against the Hydreigon originals:**
  - All four texts are identical, apart from the date and the "Took" time.
  - Network v network: 30 of 30 games equal `readout_nvn_games.jsonl` on disk.
  - kp3 rows: 90 of 90 games equal `kp3_rows_games.jsonl` on disk.
  - Every per-game count that the earlier 2,000-deal regression also recorded equals its record.
- **The Altaria-style path, before (c8d0548) and after:**
  - Same games: network v network and the kp3 rows equal the files on disk, before and after.
  - Every engine-rule count is equal once the fixed split is taken out.
  - The texts differ only by the added lines.
- **The printed fixed rows are the fixed rule's numbers:**
  - Line for line, they equal the main rows of a `--ko-rule fixed` run on the same deals.
  - Deal by deal, they equal the `--preset hydreigon` counts on the same deals (Hyper Ray, and Darkness Claw in the counts). So the fixed rows really are the Hydreigon table's rule.
- **Real Altaria games:** k3 v k3 on 30 new diagnostic seeds (20,000,777,000 + i), with `decks/research/altaria.txt` against `lucario.txt`. Nothing of the Altaria run was read.
  - `look()` ran at every Altaria decision under both rules. The fixed flag always equalled the fixed rule's own verdict.
  - All 30 games equal the engine loop's own games, so the extra reads changed nothing.
  - Every audited attack, Boosted Evolution, Asleep turns (with and without Darkrai) and Mega Harmony's bench size were reached.
  - The two rules disagreed on Mega Harmony, Hypnoblast and Dark Slumber, as expected. No rate is reported.
- **The Altaria-only lines:** `readout.py` and `kp3_rows.py` ran with the reading forced to "altaria" on the Hydreigon deals. Only the preset line, the pair-check line and the transparency note changed; games and counts are byte-identical.
- **One change by the review:** `kp3_rows.py` now also prints the transparency note in its READING (Altaria only), since the decisive D is there and the dry run's precheck was this script's. Its audit block gained the one-line pointer to the deviation.
  - The `--preset hydreigon` text is still identical to the original's.
  - The Altaria-style text gained only that one line.
  - Its games are byte-identical.

## Transparency: what was seen of the Altaria run before it finished

`readout.py` (section 4) and `kp3_rows.py` (its READING, where the decisive D is) print this same note under the
Altaria reading.

> The dry run replayed 200 Altaria k3 v k3 bar rows (fixed before training) as an identity precheck; the reviewer
> glimpsed STATUS.txt's header (games played, bars 55/45, draw gate) with no checkpoint margins. Also: while checking
> progress at 23:11 CDT on Sept 25, the laptop session's own grep of STATUS.txt showed the live-evaluation margin lines
> for checkpoints 1000k-1400k. This was after every definition had been fixed and approved, and nothing in the scripts
> was changed because of it.

The session that then wrote in Fable's notes (fixed-rule split, Asleep limits, the deviation, this note) read no
Altaria result. In the run folder it read only `PRESET_READING.md` (the reading itself); its tests ran on the finished
Hydreigon run. The session that reviewed that change did the same. In the run folder it read only `PRESET_READING.md`'s
item 3 lines, to check the quoted "network against kp3". `git status` showed `STATUS.txt`'s name; the file wasn't opened.

## Dry run on the Altaria run (Sept 25, while it trained)

Nothing was read beyond what is listed here and under "Transparency" above.
- **Refusals:**
  - `readout.py` and `kp3_rows.py` resolve every audited name against the run's settings and deck files (the table above), then stop with "state.json has no confirmed checkpoint per network yet" (the run had no verdict at the time). They stop before opening the run's game records.
  - `kp3_rows.py` also stops without `PDL_ADDON_DIR`, and with the verified wheel given in its place (wrong sha256).
  - A name no card has (for example `--attacks "Hyper Ray"`) stops the script, and so does a wrong `--opp`.
- **Early warning for the kp3 rows:** `kp3_rows.py --precheck` replayed the run's own k3 v k3 bar rows on the diagnostic build, 200 of 200 exactly (winner and turns). So the build plays this pair's games as the verified wheel does. The other half of the gate (network v k3, every move) needs the verdict.
- **The count code on real Altaria games:**
  - `k3_counts.py` (k3 and kp3) ran on the first 30 bar deals, and 30 of 30 replayed exactly for each bot. (That was before the review made `k3_counts.py` wait for the verdict too.)
  - A checker printed only yes/no per audited move, and every audited move and count was reached. Boosted Evolution was offered, Asleep turns were created (some with Darkrai in play), and Mega Harmony's bench size was recorded.
  - Mega Harmony, Hypnoblast and Dark Slumber were judged both ways (knockout and not). Sing, Sleepy Lullaby and Stampede were judged "no knockout" only in those 30 deals, which is plausible for attacks doing 0-10 damage.
  - Those 30-deal texts stay in scratch, unread. No rate from them is reported anywhere.

## Review (Sept 25, about 23:10, before the run finished)

A second session checked the scripts against `PRESET_READING.md`, the card texts (`python3 lib/card.py` on every id in
both lists, and the engine's `database.rs`), and the Hydreigon run. It read no Altaria training result.

**Changes made:**
- `k3_counts.py` now refuses until the verdict exists, like the other two. With `--bot kp3` it checks the diagnostic build's sha256. With `--bot k3` it stops if `PDL_ADDON_DIR` is set.
- `kp3_rows.py`: the `--addon-sha` option is gone, so the sha256 check can't be switched to another build. `--identity-games 0` is refused, and a gate under 200 deals prints "NOT THE PRE-SET READING".
- **The +10 line is exact.** D comes from the won-only counts and is printed with two decimals. Item 1 allows float rounding, so exactly +10.0 counts as "+10 or more". Before this, a D of exactly +10.0 could be read as under +10.
- `readout.py` waits for `REPORT.txt` and both knockout audits instead of writing a text with MISSING (`--allow-missing-report` to override). It also prints "NOT THE PRE-SET READING" when `--games` is under 2,000.
- None of this changes the Hydreigon text. The 20-deal texts are the same as the builder's, and the network v network games are byte-identical.

**Its own regression, on deals the builder didn't use alone:** 95 Hydreigon deals, i = 211, 230, …, 1997. It used 3 workers under `nice -n 19` and checked every deal separately.
- **Verified wheel:**
  - Network v network equals `readout_nvn_games.jsonl` on disk under the fixed rule and under the engine rule, and so does the original script's game.
  - The confirmation replays are exact, and every move was re-chosen under both rules.
  - The new counts equal the original `look()`/`tally()` for network v network, the replays and k3's counts (Hyper Ray, Darkness Claw, Roar).
  - Under the engine rule, the counts change only in the knockout split.
- **Diagnostic build:**
  - net|kp3, kp3|kp3 and kp3|k3 equal `kp3_rows_games.jsonl` on disk, every move.
  - **net|kp3 under the engine knockout rule also equals it.** This is the decisive row's setting, and the builder's regression never ran it. It shows the analysis copies never change the game.
  - The identity rows pass under the engine rule.
  - kp3's counts equal the original's, and their games are the kp3|kp3 row's games.
- **Result:** everything passed, 95 of 95 on each check.

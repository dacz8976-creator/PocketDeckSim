# The laptop's review of the 92 positions of the Oct 12-13 games (Oct 14): not ready yet

**Why this review:** Dustin decided on Oct 14 to delete the frames of these 14 game packets "after we are done with them". Before that, a
reader panel checked the 92 positions in `positions_all.json` (committed at feddbce6) against Codex's ledgers, field by field.

**Who read what:**
- Seven readers took two games each. Each read every position and every field against the raw `TURN_LEDGER.json` and the other packet
  files.
- An eighth reader covered the pipeline:
  - it reviewed `scripts/normalize_ledger.py`;
  - it rebuilt the deck lists;
  - it ran scripted checks over all 92 positions.
- An adversarial verifier re-derived every blocker and major finding from the raw files.

**What they reviewed is the pipeline's real output.** Re-running main's converter (f6be4fd7) on the normalised ledgers reproduces all 92
positions field for field.

**Result: three groups of positions hold a wrong card, so this set isn't ready for frame deletion or for heavy kx3 runs.**
- In all 92 positions, these match the ledgers:
  - points;
  - his hands;
  - both boards (HP, Energy by type, Tools, Special Conditions);
  - his knock-out count;
  - the Stadium;
  - the rules-switch-2 flags.
- The errors are:
  - three blockers, in which card a name stands for and in one Bench layout;
  - nine majors, in the opponent's next Energy, his plans and two of Codex's misreadings;
  - one runner bug.

Each reader's findings, the verdicts and the evidence paths are in `review_evidence/panel_output.json`. The readers' and verifiers'
scripts are in `review_evidence/panel_scripts/`.

## Blockers (fix before these positions are used)

1. **015011 t01 and t03: every Benched Pokémon is missing, on both sides.**
   - The ledger has his Alolan Grimer (t01), Regigigas and Grimer (t03), and the opponent's Tyrogue (t03).
   - This packet alone nests each Bench entry as `{position, pokemon: {...}}`. The converter's `instances()` and the normaliser's
     `inst()` keep only entries with a `name` key.
   - So the bots see an empty Bench, and Grimer and Regigigas are dealt back into his deck. At t03 the opponent has no Bench, so
     knocking out Falinks would end the game.
   - The scored effect is at t01: km3's Poké Ball, 8 of 12, was judged on that board.
2. **030351 t09, t11, t13 and t15: both of the opponent's Darkrai are the wrong card.** They are B1 154 (120 HP, Shadow Cage DDC, no
   Ability) instead of B2b 040 (100 HP, Bad Dreams, Dark Slumber CCC 40).
   - `opp_pick()` (line 455) keeps only the printings whose printed HP equals the ledger's `hp_max`. Under Starting Plains that is 120,
     so the ledger's "Bad Dreams / Dark Slumber 40; printed 100 HP" is never scored, and nothing is flagged.
   - t03-t07, before Starting Plains, have the right card.
   - The effects:
     - Bad Dreams is gone, so at t13 the two Bad Dreams that knock out his Asleep 40-HP Druddigon (the opponent's second point) never
       happen;
     - B1 154's DDC attack can't be paid with the opponent's Fighting Energy;
     - with the runner bug below, each Darkrai has 140 HP in the engine.
   - Starting Plains occurs only in these four positions, here and in the Oct 12 set.
3. **022530, all 6 positions: his Dratini is A3b 051 (Beat 20). It should be B4 116 (Slam: 2 coins x 20).**
   - The packet's `QR_DECODE.json` (entity 20770, aliases B4 116 only) and `DECK_LOG_SNAPSHOT.json` both say B4 116. So does
     030351's deck file, built from the same QR.
   - Why it went wrong:
     - `DECK_USED.json` here holds a 20-name list (`filmed_cards_in_QR_order`), so `normalize_ledger.py` (line 61) skips the
       QR-plus-snapshot build;
     - `deckspec` can't read the entity from the string `semantic entity 20770`;
     - so the name was settled on an HP tie.
   - `report_convert.json` noted the guess, but no position or read carried it.
   - The play effect is small: same HP, type and retreat, and Dratini is only ever Benched. It is still a wrong card of his, which is the
     Oct 12 blocker class (one verifier rated it major).

## A runner bug (the positions are right; the engine reads them wrongly)

**pg_pos.rs and Starting Plains (030351 t11, t13, t15).**
- `pk()` builds each Pokémon with no Stadium bonus. It caps `hp` at printed HP and stores damage = printed − hp.
- `build()` sets the Stadium only after `set_board`. The first action then refreshes the bonus, so every damaged Basic gains 20 HP.
- In those positions:
  - his Druddigon is 110, not 90, at t11, and 60, not 40, at t13;
  - the opponent's 10-HP Igglybuffs are 30.
- `check_state_dump.py` doesn't compare HP, so it can't catch this.
- The fix belongs in `pg_pos.rs`: set the Stadium before `set_board`, or refresh after it. Until then, km3's reads of those three
  positions can't be trusted.

## Major

1. **The opponent's next Energy falls back to his own deck's Energy (18 positions).** These are all 11 of 010706 (should be Psychic),
   all 6 of 010003 (Water or Lightning) and 203719 t17 (Lightning).
   - When the opponent's zone is hidden at his turn start, line 1229 uses `decks_energy` (his Darkness). It doesn't read the neighbouring
     rows, which name the type.
   - `value_functions.rs` reads the opponent's `next` to project their next attack. So Fantasia Force and Indeedee ex's Psychic look
     unpayable, and Mega Burst's damage changes by 50 in some lines of 203719 t17.
2. **Ilima turns lose his promotion, and the slot numbers after it go wrong (203719 t07, 210823 t08, 020824 t11).**
   - The plan builder has no Promote step, and it never removes the returned Pokémon from its slot list.
   - The resulting errors:
     - 210823 t08's `Attach:1Darkness@1` hits the new Glimmet, not the promoted Glimmora;
     - 020824 t11's `Retreat:3` points at an empty slot (it should be `Retreat:1` after `Promote:0@1`);
     - every forced replay stops right after Ilima.
   - 210823 t08 is therefore wrongly counted among the v2 read's 37 positions where "km3 plays every step".
   - The known limit, a wrong attack label, understated this.
3. **Mesagoza uses logged as `stadium_activation` are dropped (210041 t08, 210823 t02 and t04).** `nk()` maps that kind to `other`, and
   no branch handles it. At 210823 t04, the forced comparison sets his Attach against km3 at step 1, when his real step 1 was the
   Mesagoza flip.
4. **Giga Turbo's extra Energy target is never named (010706 t09, 230258 t11, 010003 t09).** This is the Oct 12 class "targets of extra
   Energy not named": only Turbo Shark gets the `fx` step. No current count changes.
5. **210823, all 6 positions: the opponent's left-Bench "Alolan Meowth" is really Meowth B2 124 / B2 204** (Carefree Steps, Feelin'
   Fine, 50 HP, Colorless, Fighting weakness).
   - Codex's ledger misnamed it as "Alolan Meowth, 50 HP, Nasty Plot". No such card exists, and every Alolan Meowth has 60 HP.
   - The position's A3 108 has the wrong type and attack, and 10 damage that doesn't exist.
   - **Only the frames settle this** (`turn_evidence/t0047.00_top.jpg`, `t0085.50_top.jpg`). The correction is recorded below.
6. **015659 t05, t07 and t09: the opponent's hand is one card short (5/6/5; it should be 6/7/6).**
   - Codex's turn-4 Rare Candy can't have happened, because Mega Lucario ex B3 081 is Stage 1. The frames show only Research leaving the
     hand.
   - The same false Rare Candy sits in the opponent's discard from t05 to t13.
   - The frames also show unlogged hand changes in turns 10-12. The left-out t11 probably had 4 cards, not the inferred 2 (from overview
     frames, lower confidence).
   - **Settled only from the frames.** Recorded below.
7. **022530 t09: Dragon's Blessing's Energy choice (Fighting, from the discard) is missing from his plan.** The harness also labels both
   choices `AttachTypedFromDiscard` without the type. So the forced line is cut before his Frenzied Blade, the attack that the Fighting
   choice makes legal. The fix needs the plan step and a typed harness label.
8. **010706 t15: a Poké Ball that found nothing is kept as his first move.** The ledger says "No Basic found", which the `NOTHING_FOUND`
   pattern doesn't match. It's the only one of 25 such plays. The Oct 12 panel classed exactly this as major.
9. **022530 t03-t11: the opponent's Tool is Elegant Cape B3b 065 (+30 HP on a Stage 1), not Giant Cape.**
   - Codex named it Giant Cape but recorded the Elegant Cape effect: Scyther stays at 70, and Mega Scizor ex goes from 200 to 230.
   - Under Giant Cape the engine clamps Mega Scizor ex to 220 at t05 and t07, and Scyther looks 20 damaged.
   - The ledger's own HP numbers settle it. The verifiers split between major and minor; the clamp is in the runs' position summaries.

## Minor (about 38 findings, some repeated across readers; listed with their positions in `panel_output.json`)

- **Discard bookkeeping.**
  - Energy discarded with a Pokémon that Ilima returns isn't added, on either side.
  - Some Rainbow Cave, Shuckle ex and Fragrant Forest entries are extra or missing.
  - The checkup knock-out restore gives Druddigon 2 Metal where the text says 3.
  - These are `discard_energy` and discard errors beyond the stated Blessing and Rainbow Cave limit, in 010837, 203719, 225319, 015659
    and 020824.
- **Opponent hand counts taken from the low end of Codex's ranges.** These are wrong where the frames give the count (below).
- **Opponent printings that are flagged, not stated:**
  - Pidgey in 210823 (the ledger does tell the two apart: B1 180 under the first Mega Pidgeot ex, A1 186 under the second);
  - Ralts and Kirlia in 010706;
  - Combee, Varoom and 203719's Dratini.
- **Labels.** `his_plan_ended` is false where the turn ended with a `prompt_response` (4 positions), and opponent names and results are
  missing in games_meta (022530, 030351, 015659, 020824).
- **His Glimmora in 014423.** One copy is probably the full-art B3a 078. That's the same card in play.

## What matches, in all 92 (scripted, and by hand per game)

- Identity and points.
- His hands by name, order and count.
- Card conservation by printing.
- Both boards against the ledger's `board_at_start`: HP, Energy by type, Tool and conditions.
- Evolution stacks, including Rare Candy.
- `me.knockouts`, including the checkup knock-outs in 030351 and the Shattering Crystal heads.
- The Stadium and its owner, and his Energy zone.
- `turn_effects`: none are due anywhere.
- The rules-switch-2 flags by printing: 14 yes, 78 no, exactly as in `position_list.tsv`.
- The deck files, apart from 022530's Dratini.
- The three turns left out, and only those.
- `normalize_ledger.py`: its 254 target and result rewrites are each justified by the raw text, and the three QR-plus-snapshot lists
  AGREE.

## Facts only the frames show (recorded here so the frames are not needed for them)

| game | fact | frames |
|---|---|---|
| 210823 | The opponent's left-Bench Pokémon is a full-art Kanto Meowth, B2 124 / B2 204 function (Carefree Steps, Feelin' Fine, 50 HP, Colorless). It is not an Alolan Meowth. | `turn_evidence/t0047.00_top.jpg`, `t0085.50_top.jpg` |
| 015659 | Opponent hand at his t05 / t07 / t09: 6 / 7 / 6 (ledger 5 / 6 / 5). There was no turn-4 Rare Candy, because only Research left the hand. In turns 10-12 there are unlogged hand changes: +1 net in T10, and two cards gone in T12 (open). At his t11 the hand was probably 4. | `turn_evidence/t0114.50_top.png`, `t0157.80_top.png`, `t0208.80_top.png`; overview 00047-00057, 00118-00164 |
| 010706 | Opponent hand at his t03 / t05 / t07: 6 / 7 / 8 (positions 5 / 6 / 7). Ralts shows "Lead" (the B4 071 / B4 167 function); Kirlia shows "[C] Slap 20". | `turn_evidence/capture_128.40_top.jpg`, `capture_190.00_top.jpg`, `capture_260.00_top.jpg`, `capture_532.00_top.jpg`, `capture_572.00_top.jpg` |
| 203719 | Opponent hand at his t07 / t09 / t11 / t13: 4 / 3 / 4 / 4. The low-end rule gave 3 at t07, t11 and t13. | `turn_evidence/t0257.00_top.jpg`, `t0358.00_top.jpg`, `t0416.50_top.jpg`, `t0466.90_top.jpg` |
| 225319 | Opponent hand at his t08: 4 (Codex wrote [5,6]; its own plays give 4). | `turn_evidence/t0401.00_top.jpg` |
| 030351 | The opponent's second Igglybuff carries no Energy at t13 and t15. The ledger's Fighting is a phantom. | `turn_evidence/t0475.00.jpg`, `t0548.00.jpg` |
| 022530 | His Dratini shows Slam (B4 116). The opponent's caped Scyther stays at 70 and Mega Scizor ex shows 230 (Elegant Cape). Both are also settled by the packet's text. | `turn_evidence/t0190.00.jpg`, `t0217.00_top.jpg` |

## Effect on earlier reads

- **Sonnet's v2 read** (`PAUSE_GAMES_2026-10-13_READ_v2_sonnet.md`):
  - 210823 t08 should leave its 37 "km3 plays every step";
  - 210823 t04's step comparison is misaligned;
  - the 18 positions with the wrong opponent Energy and 030351 t09-t15 (Darkrai, and the HP bug from t11) need a re-run after the
    fixes.
- **The kx3 position study, part 2** (`../../pause_positions_kx3_2026-10/READING.md`):
  - 203719 t17 carries the wrong opponent next Energy: Darkness, which should be Lightning;
  - 015659 t05 has the opponent's hand one card short.
  - The other six positions there are clean on every field (010837 t03, t09, t11; 014423 t07; 210041 t06; and 020824 t11's first
    move).

## What next

1. **A fix job for the converter, normaliser, deckspec, `pg_pos.rs` and the forced runner's typed label.** The fixes:
   - unwrap the nested Bench;
   - stop `opp_pick` from filtering on a Stadium- or Tool-boosted HP;
   - build 022530's list from QR plus snapshot;
   - set the Stadium before `set_board`;
   - read the opponent's next Energy from neighbouring rows;
   - add Promote steps and slot updates after Ilima;
   - handle `stadium_activation`;
   - add Giga Turbo's `fx` target;
   - type Dragon's Blessing's choice;
   - catch "No Basic found";
   - carry the frame-only corrections above as recorded overrides.

   Then regenerate v2 and re-check the changed positions against this list.
2. **The frames of these 14 packets stay until then.** 015659's stay until its turn 10-12 hand question is settled or accepted as
   open.
3. Then the 14 games move from `pending` to `games` in the Battle Logs audit list
   (`../../battle_logs_retention_2026-10-14/audited_games.json`), with this review as their evidence.

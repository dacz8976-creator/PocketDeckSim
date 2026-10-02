# The floor check under km3 on the four brew drafts (Oct 2)

**Who wrote this and why.** A Claude Code subagent (Opus 5.5) on the laptop, on a job from the coordinator session. The job:
a floor page for each of the four drafts in `decks/brews/drafts_2026-10-01/` (A, B, C, D), the Sept 28 / Sept 30 way. This README
was written before any game of this run was played. Nothing here is committed by this run (this job may not commit); Dustin or
the coordinator commits it, or not.

**What this is.** The floor check (`decks/screen/floor.py`), run once on each draft list:
- `draft-A-shark-tempo.txt`
- `draft-B-tide-heal.txt`
- `draft-C-meowstic-hatterene-v2.txt`
- `draft-D-entei-grimhound.txt`

and, for draft D only, maybe a second time with one role changed (below).

**It is not a ranking.** The floor is a pass/fail floor (RUN5, A2). Nothing here says which draft is best, and a draft that
clears the floor is not thereby good. It says whether the bot can already tell a list is weak, and how. Dustin's ladder games stay
the only score of a deck.

**Nothing new is decided here.** Every rule is the one already fixed:
- floor.py's own call, nothing added: `python3 decks/screen/floor.py <deck> --out rl/results/floor_drafts_2026-10-02`. Its defaults:
  - pilot km3 on both sides;
  - the official engine `rl/engine-2026-10-02/deckgym`, main-8626a35 (what `current_engine.py` resolves; the manifest's
    available release), sha256 `2f7e5fd6e0ae21fffcb9a4df6e70dc3302e2a372f1fde1eb2bb1aa106747a62e`;
  - coverage from the release's goldfish `rl/engine-2026-10-02/goldfish`, sha256
    `cecc76fbe51b33276e0e2e787b6eacba41c52ef4eaa36c5a20954caeedc50b66`;
  - 240 games per matchup against each of the eight panel decks in `decks/screen/opponents/` (1,920 per draft);
  - seeds 7,100 + 1,000 × opponent (+500 for seat 1), the same seeds as every floor page since Sept 25.
- The floor's re-check on this engine passed this morning (`../floor_recheck_2026-10/verdicts.txt`: RESULT PASSED main-8626a35).
- Verdicts by the A2 bar, read from floor.py's page as printed: at 1,920 games, 349 wins or fewer fail, 350-418 are borderline,
  419 or more clear. "Untrusted" replaces "fail" only on the coverage flag (a flagged card used on under 25% of at least 20 chances).
- Card roles are floor.py's defaults, from each card's flag, for every first run. No role is set for any draft in the committed
  floor.py.
- **Run:** one draft after another, never two at once, at `nice -n 10`. Each takes about 3 minutes. The runner and its log are kept
  in this folder (`run_floor.sh`, `run.log`, `timing.txt`). Pages, per-game files and coverage land here.

**Draft C: Hatterene's 140 is priced at its printed 70.** Mental Crush (Hatterene B3 071) is 70, plus 70 if the opponent's Active
is Confused. The bot's damage estimate does not price that kind of effect, so it counts Mental Crush at 70. The readout copies the
page's own flag line that says so. A floor page for draft C may understate the deck for this reason (the drafts' README says the
same).

**Draft D: Victini's role.** Victini (B3 025) is in draft D for its passive Ability, Victory Star (reroll an attack's coins once a
turn, from the Bench). The drafts' README expects its default role on the page to be "attacker" (its flag is an engine status, and
a Pokémon flagged that way defaults to "attacker"). The proposed role is "bench piece/passive ability". **That role is proposed,
not set: it is Dustin's to confirm, and he hasn't answered.** So:
1. The first run of draft D uses floor.py's default, like the other drafts. Its page shows Victini's default role.
2. If that default already is "bench piece/passive ability", a second run would be identical, so it is not run, and the readout
   says so.
3. Otherwise draft D is run a second time from a **private copy** of floor.py (outside the repository; the committed floor.py is
   not edited), whose only change is one entry in its ROLES table: draft D's Victini as "bench piece/passive ability". Its output
   goes in `draft-D_victini-passive/`. That page is marked at its top as from a modified copy, "proposed role, Dustin's to
   confirm". The copy's diff and the sha256 of both files go below. Same games and seeds: only the Victini row of the coverage
   table, and anything computed from it, can differ.
4. Draft D's first page is its floor page. The second page is a reading for Dustin, not a verdict on a role he has set.

The Victory Star / Confusion repair the drafts' README wanted before D's page is in this engine (main-8626a35, repair A).

**Reading note, fixed before any game.** Each page prints every flagged card's role and where it came from. Where a flagged card
carries a default role, a "fail", "borderline" or "untrusted" there may be a wrong-role problem rather than a deck problem, and
the readout marks that verdict **provisional** (the Sept 30 rule).

**Beside each draft: its cousin's km3 page.** The coordinator's mapping is decks 13 and 03, brew 05b and brew 08. Which draft goes
with which comes from the drafts' README ("What the floor said about close cousins") and the drafts' own notes:
- A with deck 13 (Alolan Ninetales / Raticate): both run Alolan Ninetales ex;
- B with deck 03 (Wailord / Indeedee wall): the heal-and-wall plan, and both run Wailord;
- C with brew 05b (Meowstic / Hatterene / Comfey): draft C is its edit;
- D with brew 08 (Entei / Rainbow Cave): both run Entei ex and Rainbow Cave.

Decks 13 and 03 and brew 08 have km3 pages in `../floor_dustin_2026-09-30/`. Brew 05b does not; its km3 page is
`../floor_recheck_2026-09-30/brew-05b-meowstic-hatterene-comfey.md` (the one the Sept 30 readout reuses). The cousins' pages are on
the Sept 30 engine. The readout copies their numbers beside the drafts' and says nothing about the difference.

**What is not claimed.** No prediction about these verdicts is registered, so nothing here confirms or refutes one. No ranking,
no recommendation, no calibration against the ladder.

**Inputs (sha256, before any game):**
- `decks/screen/floor.py` 8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a (unchanged since a754381, Sept 30)
- `current_engine.py` b05a59e875205643e60254ef3daf4ef0f7752f5cd49acbf597baf357ca333ea7
- `lib/deckgym-database.json` 2f48cb72966c23ba3794f437aa94312e4eadcb2703c32893411ee27fc63b11d9
- `lib/brew_pages.py` bfa3b363af41f64424208d7114b4c98384900f29f173c964975001a24149ecfb
- `engine/src/players/public_pricing_player.rs` c309aff9254d5a7813fe5d1ab278a48a0e6056360a0cb36114dc6d1e8b5f2060
- `draft-A-shark-tempo.txt` 3f39092ba6680cc5b8013b961e2f5a0f07bc779816ade7a6891983082b2e7417
- `draft-B-tide-heal.txt` ed57b178ac286420521325d989d88ff963b1e8b0fcdcd058723d46adb1eb4691
- `draft-C-meowstic-hatterene-v2.txt` 946462dd9e4ca2a139fcee250cde12af41e93c916feb0775684c0e576f3260eb
- `draft-D-entei-grimhound.txt` 4821877fa5d202a3470f9b76d424f750d1883fee1516ecbce2a33937c8d49585
- Repository at main 9cc6667 (the drafts' commit); the panel lists' hashes are in `run.log`.

The readout is `READOUT.md`, written once the pages exist.

## After the runs (added Oct 2, once the pages existed; nothing above was changed)

**The four floor runs** ran 07:42-07:54 UTC, one after another (`timing.txt`: 159, 151, 172 and 190 s). `run.log` holds the
hashes checked before the first game (engine, goldfish, floor.py, the panel lists, the drafts) and floor.py's own output.

**Draft D: Victini's default role is "attacker".** Draft D's page prints `Victini (B3 025) | attacker (default from the flag)`,
flagged for its engine status (the Victory Star caveat in `card_validation.rs`, as on this engine). It is not "bench
piece/passive ability", so the second run was made, as planned above:
- **The private copy:** `floor_victini_passive.py`, in this job's scratch folder (outside the repository), sha256
  `d5a751809b968c9a6a97e9a1f9ccb8e95a0fceab4cabc32861b7262f49c06db3`. The committed `decks/screen/floor.py` is unchanged, sha256
  `8e5395e63a14636827260bcb6e8631f02734aec690d9cf334fce606ed20dce0a` before and after.
- **Its diff, one ROLES entry** (`draft-D_victini-passive/floor_copy.diff`):
  ```
  +    "decks/brews/drafts_2026-10-01/draft-D-entei-grimhound.txt": {"Victini": "bench piece/passive ability"},
  ```
- **How it was run:** floor.py finds the repository from its own file path, so the copy was run by `run_copy.py` (kept in
  `draft-D_victini-passive/`, sha256 `cc82a0326b903d560abcc9fcf832301c3477ab8a3091db13e15c802438ec1c04`), which runs the copy's
  code with its file path set to the committed floor.py's. Same call otherwise: draft D's list, `--out
  rl/results/floor_drafts_2026-10-02/draft-D_victini-passive`, the defaults, `nice -n 10` (`draft-D_victini-passive/run_d2.sh`,
  `run.log`). 07:54-07:57 UTC.
- **Same games:** the coverage file is byte-equal to the first run's, and all 1,920 per-game records are equal except the
  `flagged` field (Victini's counts under its role). The page differs from the first run's on two lines only: line 4 and
  Victini's row.
- **The page is marked** at its top as from a modified copy, "proposed role, Dustin's to confirm". Those six lines were added
  after the run; the page as the copy wrote it had sha256 `3c0cf943105cd34225a0fff8ad4ff2c913b87a579cd68bc9382c33aa2e932adf`.
  The first run's page (`draft-D-entei-grimhound.md`) has sha256
  `d80fdabe475beaece2f9d9ea15a1a98fb2da32ad422102a428381c54875f7204`.

**Draft C: Hatterene's 140 is priced at its printed 70.** The page flags Hatterene (B3 071): "Mental Crush:
ExtraDamageIfDefenderStatus estimated at printed damage (k's damage estimate)". `python3 lib/card.py Hatterene` prints Mental
Crush as 70, with 70 more if the opponent's Active is Confused. The coverage tool (`engine/examples/goldfish.rs`) flags an attack
this way when its effect changes the damage and its mechanic is not one of the 30 that the bot's damage estimate
(`estimated_attack_damage_ex`, `engine/src/players/value_functions.rs`) prices; `ExtraDamageIfDefenderStatus` appears nowhere in
`engine/src/players/`. So the bot's damage estimate, which it uses when it scores a position, counts Mental Crush at 70 even into a Confused Active. The game itself, and any attack the search actually plays out, deals the 140: the engine maps
the text to `ExtraDamageIfDefenderStatus { status: Confused, extra_damage: 70 }` (`engine/src/actions/effect_mechanic_map.rs`).

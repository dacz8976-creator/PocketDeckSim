# Overnight, Sept 28-29: one page for Dustin's morning

Kept by the laptop session ("Project familiarization"). **Since about 11:30 pm Central the laptop session is in charge overnight, with Sonnet agents** (Dustin: "Okay you are back in charge. Fable is too expensive. You and the sonnet agent continue overnight"). Before that, the Fable session coordinated. Gates Dustin set in his own words still need his word, and anything that changes direction comes here as a decision for him. Updated as things land; the newest entries are at the top of each section.

## Decisions waiting for you

- **Your first upstream pull request is ready, not pushed** (your 9 pm pick): `../upstream_pr_2026-09-28/README.md` has the title, the body to paste, and the steps.
  - **What it is:** one commit on upstream's current main, 27 lines changed in `hooks/core.rs`, plus five tests. Upstream's own suite gives 1170 passing on main and 1175 on the branch, with no failures. The four card tests fail on unfixed main, and the Steel Apron / Metal Core Barrier test passes on both. Formatting is clean.
  - **Your conditions are met:** all four texts are quoted exactly, with the limiting words in bold. Only Heavy Helmet says "from attacks" word for word: Harden and Blocking Shell say "by attacks", and Hide says "from—and effects of—attacks". The body says so plainly. The rules citation is `rules/02_damage_knockouts_points.md` lines 78-79, from the official Mimikyu ex FAQ.
  - **Done from your 10:15 pm answers:**
    - The commit now uses your noreply address (`e5a0562`, same code).
    - The wording note is one sentence: each text limits the card to attacks.
    - The body has a line waiting for your in-game result, with the FAQ beneath it as secondary.
    - A sixth test for your Greninja point: Water Shuriken, which Heavy Helmet cut to 0 upstream (commit `2aa705d`; upstream's suite 1176 passing).
    - Clippy, upstream's lint check, passes with 0 warnings (the cloud's run), and formatting is clean. Every check upstream asks for passes.
  - **Your Poison test is in the body.** Heavy Helmet cut Magmar's attack from 110 to 90, then Poison did the full 10 and knocked out Wailmer. It's recorded in `rules/02` too.
  - **Left for you:**
    1. Optionally, the Water Shuriken test for the second line. If you skip it, the laptop deletes that line before you post.
    2. Click Fork on github.com/bcollazo/deckgym-core and tell the laptop "push".
    3. Click "Compare & pull request" on your fork. The README walks through it.
- **The Sleep/Paralysis pull request isn't needed.** Upstream merged the same fix on Sept 27 (PR #379, by another contributor, with tests). So the new set will arrive with it already in, as you wanted, and there's nothing to send (`engine/UPSTREAM.md`).
  - **A different first pull request: you picked the non-attack damage fix at 9 pm** (above). The list you chose from stays here for the later ones. It came from a read-only check (a Sonnet agent reading upstream main ca4b67f of Sept 27; nothing compiled or run).
  - **Suggested first PR: "damage that isn't from an attack no longer gets cut by 'from attacks' protections."**
    - What it fixes: in upstream, a Pokémon with Heavy Helmet takes no Poison damage and only 10 from a Burn. Cascoon under Harden (and Shinx's Hide, Carracosta's Blocking Shell) can't be hurt by Poison, Burn or Bad Dreams. All four cards say "from attacks" or "by attacks".
    - Why first: about 15-20 lines in one function plus three short tests. It copies the check upstream already uses for Steel Apron and Metal Core Barrier right beside it. No other PR touches it, and it doesn't depend on the fork's own code. Heavy Helmet matters for your deck 01.
    - The laptop checked the Heavy Helmet part in upstream's code itself: no attack or opponent check (`hooks/core.rs:696-709`).
  - **Already upstream, nothing to send:** Sleep/Paralysis (and Paralysis timing, and the rule that only one of Asleep, Paralyzed or Confused can apply at a time); the damage order (Weakness between attacker and defender effects); the Checkup order; Checkup knockouts waiting until every Checkup effect is done; Politoed and Weavile's evolution checks. The point-denial coin and Rough Skin/Poison Point are partly there.
  - **Missing upstream, small (good later PRs), one line each:**
    - Mythical Slab keeps a Psychic Pokémon of any stage, not any Basic: a one-line fix, the smallest fallback.
    - Only one Stadium card played per turn: confirmed in your T10 video.
    - In a double knockout, the attacking player promotes first: may break upstream tests that assume player 0 goes first.
    - Rare Candy can't get around Aerodactyl ex's Primeval Law or Malamar's Jammer: confirmed in your video.
    - Legendary Pulse draws before Hiking Trail tops the hand up: confirmed in a video.
    - Discard-all-Energy attacks (Hyper Ray, Thunderbolt and others) put the Energy in the discard pile instead of deleting it.
    - Pichu's Crackly Toss goes to a Benched Basic only.
    - Protective Poncho only blocks the opponent's damage.
    - Lum Berry and Bad Dreams resolve in the official FAQ's order: medium size.
    - Eevee's Boosted Evolution applies only to that Eevee.
    - Mimikyu ex's Disguise isn't used up by a 0-damage hit.
    - Roar in Unison isn't offered under the Energy Zone lock.
    - Poké Ball can't be played on an empty deck.
  - **Missing upstream, but big, tangled or disputed** (not first):
    - the opening-hand deal: changes every seeded game upstream;
    - promotion before the next turn's draw;
    - the point-denial coin on non-attack knockouts: collides with open upstream PRs;
    - retaliation timing: conflicts with upstream's design;
    - Growl/Moonblast reductions;
    - Clemont's Backpack: the fork's version uses a hack;
    - player-chosen Energy discards, and player-chosen Quick-Grow Extract and Wallace targets;
    - the hidden-deck legality rules: your policy, which upstream may not share;
    - damaged-only healing targets;
    - Piers' random Energy: upstream chose otherwise on purpose;
    - the 10-card search cap: still unresolved in the fork's own list;
    - the 3-3 tie: upstream rules the opposite way.
  - Caveats: every patch has to be re-made by hand on a fresh upstream copy, because the fork's rules repairs sit in one big commit. The agent was least sure about Mimikyu, the promotion order and Eevee.

## What happened

- **Your nine brew 08 ladder games went 6-3 (67%), and it set up as fast as the simulator said.** You confirmed they were all brew 08. They're now filed under "Brew 8" in the Ladder Log; the season total is unchanged, 55 games, 26-29.
  - Entei ex attacked on your own turn 2 in seven of the eight games where it attacked, and on turn 3 in the other.
  - The opponent had 0 points every time.
  - Nine games can't measure a rate, but nothing suggests the real deck is slower than predicted. The table is at the end of brew 08's page (`../floor_brews_2026-09-28/brew-08-entei-rainbow-cave.md`).
  - The old "Entei ex (video-visible core)" card in the log is now empty. Remove it from the page whenever you like.
  - One upload, `20260929_020916000_iOS.MP4`, is stuck on a OneDrive download. "Always keep on this device" should free it.

- **koh's B2e held-out rows are read, and kt's gate opened at 02:45 UTC** (0497f47, 2c6d220).
  - The laptop's 48,000 games equal the cloud's copy game for game.
  - No held-out deck moves more than 2 points further from its real figure, so there's no held-out veto. koh stays not adopted, and kog stays the pilot.
  - **Hoopa / Absol drops under koh in both lists** (your 10:15 pm framing): the held-out one 56.9 → 45.5, your own file 33.2 → 26.4.
    - The held-out move is toward Limitless, so it isn't an accuracy veto.
    - Brew 07's main attacker is Hoopa ex. If koh's mixed rows (running now) show koh playing Hoopa's own side worse, that's a coverage veto under last night's rule.
    - **Did the screen check brew 07 under kog3? Yes.** The fourth session's floor run on Sept 28 (`../floor_brews_2026-09-28/`) used kog3 on both sides and the official engine:
      - it clears the floor, 1,177 of 1,920 (61.3%);
      - worst matchups: Sceptile 37% and Vespiquen 50%;
      - one mild flag: Mega Sableye ex's Cursed Jewel is priced at its printed damage, but it's used on 90.6% of chances, so it isn't a role problem.
    - koh's result doesn't touch that number, because kog is the screen's pilot. No extra run is needed before you play 07.

- **Your evening rulings are recorded as your words** (3e30896, 5c0cf04):
  - coverage rows count for the mixed-row veto;
  - what koh's and kt's readings hinge on;
  - clause (d) gates on Rayquaza, with Suicune reported;
  - which brew (08 is the better evidence; note setup speed);
  - the B4b trial (pin at the Garchomp release);
  - the PR goes first;
  - the cloud has no cap, and jobs must not overlap.
- **Your brew pages say what to note per ladder game**: went first or second, the turn of your first main attack, and the opponent's points then.
  - Brew 08: `../floor_brews_2026-09-28/brew-08-entei-rainbow-cave.md`, at the end.
  - The Ladder Log's Note box is enough, e.g. "2nd | Entei T2 | opp 0 pts".
- **koh re-judged under your coverage rule.** Weezing's second list is played worse on its own side (−3.8 ± 1.6), which now counts as harm. The verdict is unchanged: not adopted, kog stays.
  - The Hyper Ray census is beside it: Hyper Ray use on turns it can't knock out goes from 20% (kog3) to 90% (koh3).
- **kt's build is in.** The cloud wrote it (ec7e1a8: kt's presets on kog, touching only the players' code), and the laptop built it at 23:53 UTC.
  - The cloud had read your GO as "start kt's games now" (its amendment 3). Fable ruled that isn't in force: the laptop's run is the run of record, and the cloud's identical runs are a cross-check.
- **kt on kog: your word recorded.** "kt tables: go", then "Yes, all; build now" (main f7defd1).
  - kt's first game waits for koh's B2e read.
  - Rayquaza is clause (d)'s one test, with Suicune reported (your 7 pm word).
- **koh failing, in your framing (9 pm): the Rayquaza gain is still behind a problem nobody has named yet.** R′ was the reworked Hyper Ray fix. It didn't clear R's side effects on the table decks: Altaria is still played worse, and now Weezing's second list too.
  - **The Altaria diagnosis is done** (`../koh_2026-09-28/altaria_diagnosis/SYNTHESIS.md`). It corrects the earlier "first sign": Boosted Evolution isn't the cause.
    - **The "crossed" Swablu/Eevee line is mostly a reading problem.** Fix A works on Swablu: koh never makes kpf's Igglybuff-into-Swablu retreat, 0 of 18 rows, against kpf's 8. A can't act on Eevee by construction, since Espeon needs one Energy, so an Eevee holding one already reads ready. Those Eevee lines don't cost points.
    - **koh's Altaria deficit is small and spread out:** −1.33 ± 1.61 over the traced cells, not clearly beyond noise. It splits three ways:
      - **R's attack-skipping (−0.64):** the tempo trade R′ keeps. It costs points only against Lucario, and no list-free repair was found.
      - **Fix B's retreat-payment test (−0.40):** it counts the fresh Zone Energy twice, once to pay a retreat to a benched Mega Altaria ex and once for the Active attacking. A repair (B counts only Energy the Active held before this turn's Zone attach) was built in a scratch copy. It's identical to koh on every registered slice and moves those rows back to kog's play; that's worth maybe +0.2-0.3 points. It's a candidate, not registered.
      - **Fix A (−0.23):** small.
    - **The synthesizer's own verdict:** "Altaria's evidence alone does not justify changing the player." So the problem behind the Rayquaza gain is now partly named: R's tempo trade against Lucario, plus B's double count. Weezing's second list and Hoopa aren't diagnosed yet.
- **koh: not adopted, provisional** (087528f; `../koh_2026-09-28/laptop_reading/READING.md`).
  - Real error 14.0 → 12.3, but the accuracy test's interval crosses zero.
  - Altaria is played worse, which counts as a veto.
  - The mechanism check fails fix A's line in Altaria's Swablu/Eevee positions only.
  - Lucario and Vespiquen are repaired, and Rayquaza keeps its gain.
- **The engine switch and screen: done Sept 28** (33f56da): the kog engine is official, and the screen and floor use kog3. The floor's Payback re-check passed (b05a4cd).

## Running now

- koh's B2e mixed rows (about 2-3 hours from 02:25 UTC), which complete its coverage record.
- kt: the last identity checks. Then, on its own, the timing run, the four tables on the 45 cells (about 3 hours), and the footprint.
- The cloud: its own kt identity and tables, as a cross-check.
- Sonnet agents:
  - the PR preparation;
  - kt's Dustin-deck A/B and readout-counter scripts;
  - a workflow diagnosing why koh plays Altaria worse, at the lowest priority;
  - the Trainer-pricing registration draft.

## Next

- kt, after the gate:
  - timing;
  - the four tables on the 45 cells;
  - the footprint, committed alone before anything else is read;
  - mixed rows;
  - coverage: B2e, Scizor and the second lists, with mixed rows every time;
  - clause (d) (Rayquaza);
  - the Rayquaza traces;
  - the Dustin-deck A/B (Skarmory included).
- An open-cause diagnosis: Sceptile v Vespiquen (sim about 66 v real about 33).

# Overnight, Sept 28-29: one page for Dustin's morning

Kept by the laptop session ("Project familiarization"), which Dustin put in charge overnight. The Fable session "Recommendations and advice" coordinates, under Dustin's word that it may decide while he is away, except for gates he set in his own words. Updated as things land; the newest entries are at the top of each section.

## Decisions waiting for you

- **Your first upstream pull request: the non-attack damage fix (your 9 pm pick; recorded in RUN5's A5).** The branch is being prepared on a fresh copy of upstream, at low priority, to your two conditions:
  - all four cards' texts quoted from card.py, with "from attacks" shown, and the rules citation taken from `rules/`;
  - one test per card, plus one showing Steel Apron and Metal Core Barrier unchanged.

  When it's ready you'll get the GitHub steps: click Fork, say OK for the laptop to put the branch on your fork, then "Compare & pull request". Nothing is pushed before that.
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
  - **Where the Altaria diagnosis stands** (a Sonnet workflow, still running at the lowest priority; no synthesis yet). Its first sign: in Altaria's opening, koh retreats Igglybuff into Eevee to use Boosted Evolution. Fix A appears to misread the step count when the evolution can happen that same turn.
  - That fits the mechanism check, where fix A fails only in the Swablu/Eevee positions (6 of 15 recovered).
  - It is a first sign, not a finding. What it finds goes here, and no R′ variant is registered before it's read.
- **koh: not adopted, provisional** (087528f; `../koh_2026-09-28/laptop_reading/READING.md`).
  - Real error 14.0 → 12.3, but the accuracy test's interval crosses zero.
  - Altaria is played worse, which counts as a veto.
  - The mechanism check fails fix A's line in Altaria's Swablu/Eevee positions only.
  - Lucario and Vespiquen are repaired, and Rayquaza keeps its gain.
- **The engine switch and screen: done Sept 28** (33f56da): the kog engine is official, and the screen and floor use kog3. The floor's Payback re-check passed (b05a4cd).

## Running now

- koh's B2e held-out rows on the laptop (ETA about 01:20 UTC).
  - Then koh's B2e mixed rows, which complete its coverage record.
  - kt's gate opens once the B2e rows are read, without waiting for the mixed rows (Fable: they can't change kt's base).
- kt's identity checks at its build: the old pilots must replay game for game.
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

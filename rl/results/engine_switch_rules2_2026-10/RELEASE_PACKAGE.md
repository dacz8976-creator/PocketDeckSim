# Rules update 2: what it changes, what it costs, what I need from you

*The laptop session, Oct 9. One page for your decision; the coordinator checked it. The full plan is `PLAN.md` in this folder.*

## What it is

It makes the simulator follow the card text in three places where it doesn't today:
1. **Coin flips, round 2.**
   - Seven more attacks now trigger Meowth's, Togekiss's, Bastiodon's and Hisuian Goodra's coin. Gyarados's Wild Swing is one of them.
   - Will now works for a Confused attacker and against a "flip or the attack doesn't happen" coin (Mirror Shot).
   - Victory Star is offered after that coin.
   - Each Ariados adds 1 to the Retreat Cost, so two add 2.
   - Small fixes to Guts, Perish Body and Luxury Coin.
2. **Fossils count as Item cards everywhere.** The Item lock already treats them that way. Now seven more places do too, such as Thieving Machine, Arven and Junk Spark.
3. **Cursed Jewel and the other four "hit back" attacks now add Weakness (+20).** Your Sableye recording showed it: 60 to a Darkness-weak Houndstone, twice. Rocky Helmet and Abilities stay a flat 20.

The bots' own code doesn't change.

## Where it stands

- **The cloud's part is built and tested.**
  - The final engine version is 140c0be2. 2,072 tests pass and 0 fail.
  - The Cursed Jewel change has an off switch, which the checks use.
- **The early warning is clean.** The cloud played 480 games on the old engine and on the new one, and 25 changed. Every change is explained by the new rules, and none needs a hand check:
  - 18 by Wild Swing now triggering Meowth's coin;
  - 7 by Cursed Jewel's +20.
- **A correction to what I told you at 3:37 pm:** not all the preparation is done. It is now going to the cloud, so the laptop stays free and cool, as you asked tonight.
  - The cloud fixes one line of Gholdengo's note in the card list (text only, no game changes), and makes Bounded Field double a hit back's Weakness, as its text reads (no game we play changes).
  - The cloud finishes the checking tools:
    - the probe learns round 2's cases (Will, Ariados, the coin on your own Pokémon, Guts and Perish Body);
    - the sorting script learns the case where the new game is the shorter one;
    - each rule gets an off switch for the check.
  - Two readers confirm the new tallies, and confirm that the rewritten code plays the same wherever the rules didn't change. Sonnet is one of them, reading on the laptop without building anything.

## What changes in recorded games

- **Expected to change:**
  - deck 12 and the B2e Whimsicott list (two Ariados): 16 of km3's 96 B2e rows, and deck 12's floor page;
  - possibly one row of deck 10's floor page (against t-weezing: Will with a Confused Xatu);
  - brew 07 and 09 against t-altaria, where Espeon is weak to Darkness;
  - the wording of the Victini note on draft D's pages.
- **Must not change:** the frozen tables (45,000 games), every bot's reference games, and everything else.
  - Each changed game has to show the new rule acting, or the bots seeing it coming. That holds even inside the expected rows.
  - Any other change stops the update and comes to you.
- **kx3:** after the update, kx3 is rebuilt on the new engine and checked.
  - Its games should replay exactly, except deck 10 against t-weezing (Will), where every changed game has to be explained.
  - The slow report's pinned program is rebuilt on the new engine too, its self-checks are replayed, and it is pinned again.
  - Slow reports already running on today's program (brew 08 and deck 13, on the cloud) stay valid, because those decks aren't on the affected list.
  - Brew 07 and 09 slow reports wait for the new pin. Until then, brew 07 and 09 results stay provisional.

## Cost (no extra money: the laptop, the cloud and the sessions you already have; the Opus reviews use some of your usage)

| Part | Laptop time |
|---|---|
| The cloud's tools and fix, and the two readings (now, on the cloud; Sonnet reads without building) | none |
| Sitting 1: replay checks, about 199,000 games | about 4 h (7 at most) |
| Sitting 2: early warning, carriers and km3's coverage, about 137,000 games | about 3 h (4.5 at most) |
| Hand traces of anything unexplained, then the update itself | about 1-2 h |
| After the update: new pages (decks 10 and 12, draft D, brews 07 and 09); kx3 and the slow report rebuilt, self-checks replayed, pinned again | about 3-4 h |
| **Total** | **about 11-13 h (about 17 at most), over 2-3 nights** |

## What I need from you (my recommendation first)

1. **Go: "update if everything passes."** Two checks are stricter than Oct 1's:
   - a game one move longer or shorter is judged like any other;
   - the off-switch check is required: turning the rule off must bring the old move back.

   A judgment call always comes to you. **Recommended: yes.**
2. **Scope:** all three parts plus the Gholdengo note. Leave out two bot-code details that no list reaches:
   - how the bots price a Will-boosted coin;
   - their Junk Spark count of Fossils.

   **Recommended: yes.**
3. **New reference games:**
   - The 16 Ariados rows become km3's new reference once every changed game in them passes the check.
   - The frozen tables are never re-based: a change there stops the update.
   - New floor pages after the update: deck 12, deck 10 if its row changed, draft D's three, brew 07 and brew 09. They are judged through the matching checked rows.

   **Recommended: yes.**
4. **Nights:** which nights can the laptop run by itself, and which mornings will you take it? **Recommended:** the first night after the 2-day run is read and the cloud's tools pass. On school days the school-morning rule applies: no new game after 5:15 am, stopped by 6:30, saved by 7.

**The order I'll follow unless you say otherwise:**
1. The 2-day run finishes and is read; meanwhile the cloud does its part.
2. The two sittings.
3. The update.
4. The new pages, then kx3 and the slow report pinned again.

All of this comes before the B4b merge trial is locked in.

## Recorded, not for decision now

**Four Cursed Jewel readings the simulator will follow.** None has been seen in a game, and none changes a recorded game. Each has a shot-list row that could overturn it:
- **Steelix's Metal Defender** doesn't block the hit back on the turn it's used. The card says "your opponent's next turn", and the hit back lands on Steelix's own turn. (Shot list, row 30.)
- **Ledian's Swift** doesn't stop the hit back. Its text covers "this attack's damage", and the hit back is the other attack's damage. (Row 31.)
- **An attacker that U-turned to the Bench** takes the hit back flat. Weakness never applies on the Bench (official). (Row 32.)
- **Bounded Field** doubles the hit back's Weakness (×2), like any attack's.
  - It doubles Weakness for "damage from attacks used by Pokémon in play", and a hit back fits that.
  - The cloud's first version kept +20. It is being switched to the plain reading now, with the Gholdengo line (your card-text rule; the coordinator, Oct 9).
  - No list we play has Bounded Field with one of these attacks, so no game changes. (Row 33.)

**Open rules questions:**
- **Does a hit back count as attack damage for other cards?** Those cards are Heavy Helmet's −20, Disguise, Guts, Rescue Scarf, Lucky Egg and the attacker's own Rocky Helmet.
  - The card text says yes. The simulator says no today, and no list we play reaches it.
  - **Recommended:** a later round. One friend game with Heavy Helmet answers most of it (shot list, row 22).
- **When an attack pushes the holder to the Bench, do Rocky Helmet and Abilities like Rough Skin still hit back?** The simulator says yes, on purpose, and a test pins that. Either reading is defensible. Shot list, row 28.
- **Hala (a simulator risk, not a rules question).** Say you play Hala, then your own Hariyama attacks into a hit back that turn. The simulator might wrongly leave it at 10 HP. No list holds Hala. **Recommended:** a test first, in a later round.

*For the audit:*
- the branch `claude/coin-prevention-round2` at 63c28e6e, engine 140c0be2 (tree 8d71f693), `suite_final.log`;
- `early_warning_8b/` (TRACE LOAD 0);
- Sonnet's `P2_EVIDENCE_sonnet.md` (main 0af262ac);
- P1 still open: `card_validation.rs`:102 at 140c0be2;
- the four readings: `rules_repair_return_damage_weakness.rs`, tests `metal_defender_*`, `swift_*`, `hit_back_on_a_benched_attacker_stays_flat`, `bounded_field_*`; shot-list rows 30-33 added Oct 9.

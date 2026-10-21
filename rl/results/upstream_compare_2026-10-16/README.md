# Our engine against upstream (bcollazo/deckgym-core)

Oct 16, 2026. Read-only: nothing was built or run, nothing was opened, commented on or pushed to bcollazo's repo, and nothing was pushed to main. Upstream was read at its main tip `c3083a3f` (Oct 16, the merge of our own PR #383).

## Short answer

1. **Nothing upstream has that we lack would change a game that Dustin's decks or the 8 panel lists play.** Every card upstream added or fixed since Jul 30 either is not in any of our lists, or we already have our own version that plays the same. The few places where the engines do differ on a card he plays (Raticate ex, Team Rocket's Researcher, Happiny's Chubby Cheer, Heavy Helmet, Growl-type cuts, end-of-turn knockouts) are deliberate: ours follows the card text or his recordings more closely, so taking upstream's version there would be a step backwards (table "Do not take").
2. **What we should take is the B4b card data and a handful of small guards and fixes for boards none of his lists reach** (an out-of-turn ability, an endless-loop cap, a crash, a speed problem), plus optional tests and replay tooling. The data matters because a deck code that uses a B4b printing cannot be loaded by our engine today.
3. **We have about 30 rules fixes upstream lacks.** Fifteen are small, clear and likely to be merged (table B). Two earlier ones were already merged: #335 (merged in 1 day, Jul 22) and #383 (17 days, merged today). Every PR would post under Dustin's account and needs his OK, one by one.
4. **Mega Garchomp ex (P-B 099): upstream already has it** (added Sept 29 in the "B4b" commit). The card lists match one for one up to the b4a release: all 3,879 shared ids are identical in every field. Upstream main has 438 more since (details below).

## How sure this is

Fifteen readers went through slices: seven on what upstream changed (A), eight on what we fixed (B), 232 findings in all. A second reader, told to try to refute each finding, independently checked 128 of them (the ones that lead to a recommendation to act; "skip" and "we already have it" findings were not rechecked). Their corrections are folded in. After that, two more checkers read this page against the findings and their corrections are folded in too. All of it is by reading code, saved GitHub data and our own notes. "Reads as" is not "tested": where a call rests on a reading only, it says so, and before an upstream PR or a port, the quoted test is what settles it. Full findings: `items.json.gz` (everything, with the checkers' notes), `DETAIL_A.md`, `DETAIL_B.md`.

## Where the two engines stand

- **Data:** at upstream's b4a release (`eb71f845`, Aug 27) the card lists are identical: 3,879 ids, zero differences in any entry. Upstream main now has 4,317: the extra **438** came in one commit on Sept 29 (`9044ff6` "B4b"): 429 B4b cards and 9 Promo-B cards. 437 of the 438 are word-for-word reprints of cards we already have under older ids. The one new card is **Mega Garchomp ex (P-B 099)**. The coordinator reports that deckgym.com shows 3,879 of 3,879, which equals the list before B4b; I cannot see what data the site reads, so I do not know whether it is behind or counts differently.
- **Code:** not a merge. We branched at `8b40f55` (Jul 30) and wrote the same cards separately: 560 attack and 156 ability texts are registered in both, under different internal names. Upstream's patches do not apply to ours; each item below was judged by what it does.
- **Mega Garchomp ex:** upstream has the card, and its attack (Falling Edge, "Discard 2 random Energy from this Pokémon") already runs on an effect text that two other cards share. Our own Mega Garchomp branch is field-for-field identical to upstream's entry (it only sits in a different place in the file), so the offer we had in mind dissolves; the card arrives with the B4b data (table A, row 1).

## A. What we should take, ranked

"Changes a listed game" means: does it change any game that Dustin's decks (`decks/dustin`), the brews and drafts, or the 8 panel lists play.

| # | What it is | Kind | Changes a listed game? | Difficulty, conflicts | Our own version? | Call |
|---|---|---|---|---|---|---|
| 1 | **B4b card data (438 cards) plus the trainer lookup by effect text (upstream #395)**, and the few places of ours that name a card by printing number (for example Iris's extra point for Haxorus names three Haxorus ids). | new cards / data | None expected today (a reading, not proven; the identity replays settle it). Unlocks decks that use B4b printings: 79 of the 187 card names in his lists have a B4b or new-promo printing. | Medium. Our data files use Windows line endings and upstream's do not, so upstream's patch cannot be applied: regenerate from its `database.json` with our generator. Needs a new engine pin. A data-only drop is not advised: the 46 new Item/Supporter printings would load, and the command-line check would then refuse a deck that holds one (only programs that skip the check could crash). | Partly: we have all 437 reprints under older ids; the printing-number lookups are ours. | **Take, test first.** Natural moment: the next pin (Garchomp release; C1 on Oct 28). Interim: `lib/card_canon.py base_id` rewrites a list to base printings. |
| 2 | **#385: "when you put this Pokémon from your hand onto your Bench" abilities only on the owner's own turn** (Miraidon ex, Koraidon ex, Roaring Moon, Poltchageist). Ours offers them during setup and to the player whose turn it is not; the second player can be asked to act in the first player's turn 1, and Team Rocket's Boss can trigger it too. | rules fix | No (none of the four is in any list). | Easy, one guard at the top of one function. Needs new tests for setup and the off-turn player. | No | **Take** |
| 3 | **#394: cap of 100 actions per turn** (after that only End Turn and attacks). Stops a game that never ends, for example two Dusknoir passing damage with Shadow Void. | safety | No (no listed deck can repeat an ability without limit). | Easy: one counter in the state, reset in two places (turn change and the setup-to-turn-1 step). Ours counts more steps per turn than upstream, so first log the highest per-turn count over a normal batch; if a turn nears 100 the cap would change games. | No | **Take** |
| 4 | **#390: grouped enumeration of random multi-hit attacks (Gholdengo ex Spending Rush).** Ours lists every hit sequence: 15 Energy against 3 Pokémon is 14.3 million, seconds to forever. Side finding: ours returns random-damage outcomes in hash order, so a seed does not reproduce those attacks between runs (10 cards, 27 printings, none in a list). | safety / speed | No | Easy; same function name and shape in ours. Skip upstream's `perf_watch` diagnostic (changes the executable, so every pin check would be redone). | No | **Take** |
| 5 | **#386: a knockout that empties a player's Active Spot while an "end turn" marker is queued crashes** (the replacement choice sits under the marker). Narrow: needs Kiawe plus Jolteon ex's Electromagnetic Wall. | bug fix | No | Easy: the special case must insert a Promote (not Activate) choice. Upstream's open, unmerged #388 is a different fix for the same hole; take one, not both. | No | **Test first**, then take #386's version |
| 6 | **#401 (open PR), Fossil part only: the "discard Fossil" action is offered twice per Fossil in play.** | bug fix | No (no Fossil in any list) | Trivial: skip Fossils in one ability loop (3 lines). Its other half (the MCTS bot) we skip. | No | **Take** |
| 7 | **#344: the deck check rejects Dragon or Colorless Energy Zones, with a clear message instead of a bare crash.** | safety | No (all 73 deck lists in `decks/` have a legal Energy line) | Trivial, 3 files. Check first: our strength harness calls the same check (`rl/strength/src/main.rs:120-125`) and our observation templates clear the opponent's Energy list on purpose. | No | **Take** |
| 8 | **#368 piece: "shuffle this Pokémon and all attached cards into your deck" puts an attached Tool into the deck; ours discards it** (Eldegoss Float Up, Dunsparce, Accelgor...). | rules fix | No (none of those cards is in a list) | Easy and small; keep our Professor Turo behaviour unchanged. | Partly | **Take** |
| 9 | **"If your opponent's Active is a [X] Pokémon" counts a second type granted by an ability** (upstream #374, merged Sept 27; found while reading #348). Ours reads only the printed type. Only Snover Ice Shard and Sealeo Frozen Splash against the two Urshifu can differ. | rules fix | No | Trivial, one helper, plus the bot's damage estimate (`value_functions.rs:1603-1607`). Moves a damage number, so a pinned study with such an attacker would shift. | Partly | **Take** (low value) |
| 10 | **Tests.** Upstream's test files for Dragonair (#343), Meganium (#346), Silcoon/Cascoon (#347) and Coalossal (#348) as guards; and the six tests that came with #383 (that is our own PR coming back: take the test file only, keep our code). The Dragonair test must be rewritten with a Dragon Active plus a Grass-Active negative case: as written it encodes an upstream bug (no Dragon check). | tests | No | Easy | Partly | **Take** (housekeeping) |
| 11 | **#382: replay recording, a `play` command and a web viewer.** Lets Dustin watch a simulated game of any of his decks, for example the bot playing the Kingambit list. Ours has the older terminal viewer only. | tooling | No | Medium: touches `main.rs`, `simulate.rs`, `game.rs` and changes the executable. #391 (per-move scores in the viewer) only helps if the pilots report scores. | No | **Optional, test first** |

**Not a take, but worth knowing: #367 (open, unmerged since Sept 3).** Rocky Helmet would reflect its 20 back when Mega Sableye ex's Cursed Jewel hit-back lands on a Helmet holder. Upstream main does not do it either, so the two engines are identical today. It could reach brews 07 and 09 (Mega Sableye ex) only against panel t-blaziken's single Helmet, and those two brews have registered ladder predictions. A rules call that needs Dustin's word and the full rules-switch procedure; do not copy upstream's broader logic, which would also reflect off the defender's own Helmet and Rough Skin-type Abilities (our rules say that is wrong).

**Looked at and not worth taking:** `perf_watch` (#390, #392), the 20-branch forecast cap (#392; conflicts with our exact-only search and would change every pinned bot number), the replay scores in the viewer (#391), external bots (#382 part 2, needs a rebuild around our no-peeking boundary), `pyo3` upgrade (#393), MCTS rewrite (#275, #401's MCTS half), test-folder reorganisation (#249), filename-collision (#123), viewer styling (#387), the `et` player-code fix (#400; ours is already right).

**Do not take (taking upstream's version would undo something of ours):**

| Upstream item | What ours does differently |
|---|---|
| Heavy Helmet code (#383); Helmet in decks 01 (both Kingambit lists) and 03 | Upstream still reads the *printed* Retreat Cost and gives a flat -20. Ours reads the current cost and stacks per Helmet (fix `050cf51d`, confirmed by his heavyhelmet_test video). Our notes say "if #383 is merged, take upstream's version": that would regress us. It is table B, row 16. |
| Raticate ex Thieving Incisors (#360); in decks 13-A, 14, 15 | Ours moves a *random* Energy by chance over the types held (built that way in `12938ca2`; the same principle as fix `3102c9eb` for Unruly Claw and the Psychic Supporter). |
| Team Rocket's Researcher (#361); deck 14 | Ours keeps exact odds and handles Will and Luxury Coin; upstream caps at 5 heads. |
| Chubby Cheer (#363); Happiny in deck 04 | Ours has the correct "next turn" timing. |
| Damage order details in #379: Growl-type reductions (Bonsly Teary Attack in t-lucario), Luxray's Intimidating Fang, the Guarded Grill / Securely Sheltered heads cut | Ours follows the official damage-order FAQ and our R1 / switch-1 repairs; upstream's #379 claims the FAQ order but leaves these outside it. (Also table B material, rows 27 and 28.) |
| Kabutops Leech Life overkill (#352) | Plain card text ("the same amount of damage") supports ours, and our test pins it. No recording or ruling either way; the reader suspects ours may over-heal when a defender coin cuts the damage (not run). |
| Defer end-of-turn knockouts until after Checkup (#358) | Collides with our Checkup pause frames, our Sept 26 promotion fix (`5bab907`) and our Quick Growth repair. Reachable only as Deceptive Needle or Bad Dreams against a Quick Growth Caterpie (t-sceptile). |
| Skip the second switch choice on a lethal knock-back (`09e964f` fix 2) | Conflicts with our ruling, Dustin's Sept 30 decision and `rules_repair_retaliation_timing.rs:136`. No listed attacker reaches it. |
| Victory Star in #355 (Victini; draft D only) | Ours is the larger design (staged choice, Will and gate-coin rules). |
| Empty-board tie when both reach 3 points (#379) | Touches our rules4 T2 repair and its test. |
| Random self-discard in Drampa, Gouging Fire, Raging Bolt (#364) | Would undo our player-choice repair. |

**Not settled, leave as is:** Team Rocket's Goo-zooka (#361; decks 12, 14, 15, brews 03a, 03b). Plain use is identical. They differ only when a retreat discount exceeds the added cost, and there is no evidence which order is right; ours matches Oranguru's Primate's Trap.

**Where we already match or are broader (no action):** the card definitions from the card PRs since Jul 30 (#343 to #364, #368, and the open #304, #337, #380, #381) are in ours; where behaviour differs, it is in the tables above. That includes cards in Dustin's decks: Kingambit's Overlord's Blade (both engines count knockouts the same), Xatu Life Drain, Weezing ex Boiler Smog, Dragonair, Cheren, Jasmine, Alolan Muk's Power of Alchemy. Sleep and Paralysis (#379): both engines block attack and retreat, replace each other, and recover at the same Checkup. The only difference is a Paralysis put on a Pokémon during its own owner's turn; every Paralysis in upstream's 4,317 cards targets the opponent's Active, so no card can reach it.

## B. What we could offer upstream, ranked, one small PR each

Each PR posts under Dustin's account and needs his OK. "Basis" says what proves it: card text, the official battle FAQ, a recording of Dustin's, or his rule. Several checkers noted that the printed text is silent and the proof is the recording or his rule; those are marked. "Wants it?" is a 1 to 5 guess at how likely the maintainer is to merge it, from his history (he merged #335 in a day and #383 in 17 days; he cuts search branching in #390, #392 and #394, so anything that adds a player choice is unlikely; he designed #358 on purpose). **Already offered** is "no" for every row unless stated: we searched the titles of all 377 upstream PRs, the saved text of the 53 recent or open ones, the 25 issues (short bodies, no comments) and upstream's commit messages; an old comment could be missed. Our only PRs there are #335 and #383.

**Small and clear (send these first):**

| # | Fix | Basis (one line) | Size | Wants it? | In his lists? |
|---|---|---|---|---|---|
| 1 | **Two Ariados each add +1 Retreat Cost** (upstream stops at the first) | Printed on each Ariados: "Your opponent's Active Pokémon's Retreat Cost is 1 more"; same-name passive Abilities stack. Recording 213034 (T5). | Delete one `break`; about 3 to 9 lines plus a test | 4 | Deck 12 (2 Ariados) |
| 2 | **Rare Candy respects Aerodactyl ex's Primeval Law and Malamar's Evolution Jammer** | Both say "can't play any Pokémon from their hand to evolve"; Rare Candy plays one from hand to evolve. Primeval Law: card text plus a recording consistent with it. Jammer: card text only. | About 15 lines plus a test; the check already exists upstream | 4 | Only against an opponent with those two |
| 3 | **Mythical Slab keeps any Psychic Pokémon, not only a Basic** | Card text: "If that card is a [P] Pokémon, put it into your hand." | 1 line | 5 | No |
| 4 | **Pichu's Crackly Toss attaches only to a Benched *Basic* Pokémon** | Card text: "1 of your Benched Basic Pokémon." | 3 to 4 lines (a mapping entry) | 5 | No |
| 5 | **"Discard all Energy from this Pokémon" puts the Energy in the discard pile** (Hyper Ray, Thunderbolt, Luster Purge...) | A discard goes to the discard pile; cards that read the pile undercount otherwise. | 4 lines plus a test | 4 to 5 | Hydreigon's Hyper Ray (t-hydreigon) |
| 6 | **Protective Poncho only blocks damage from the *opponent's* attacks and Abilities** (not your own Earthquake on your Bench); can bundle with Ice Face / Coordinated Unit / Unown Guard, which have the same gap | Card text: "by your opponent's attacks and Abilities." | One condition plus a test; same area as #383 | 4 | Panel t-lucario, deck 05, brew 06b |
| 7 | **Only one Stadium may be played per turn** | Printed in every Stadium's rules box (not in the card data); proved by Dustin's T10 video ("You can't use any more Stadium cards this turn"). | About 6 to 11 lines in 3 files | 4 | Deck 08, brews 08 and 10 |
| 8 | **Eevee's Boosted Evolution lets only that Active Eevee evolve on the first turn** (upstream lifts the ban for the whole board) | Card text: "it can evolve." Recording 194920 is consistent with it but does not separate the two readings. | About 15 lines out, 6 in | 3 to 4 | Panel t-altaria, deck 15 |
| 9 | **A 0-damage attack does not use up Mimikyu ex's Disguise** | Card text: prevents the "damage"; zero is none. Evidence is the text plus Dustin's recollection, no video. | About 6 lines plus a test | 4 | No |
| 10 | **Wallace's "maximum HP of 50 or less" counts bonuses (Giant Cape)** | Official battle FAQ article 59513864093209 (a 50-HP Staryu with Giant Cape cannot be chosen). | One condition in a shared helper | 4 | Draft A (Wallace) |
| 11 | **Hit-back Abilities are read by their text, not their printing number** (Iron Jugulis, Dragalge ex B3 231 and the B4b reprint do nothing upstream; Muk's Power of Alchemy or an earlier Budew should switch them off) | Each card's own Ability text; made visible by the B4b reprints. Budew's Prickly Powder landing on the same attack is *not* fixed by this (that is the big item below). | About 10 to 15 lines plus tests | 4 to 5 | Muk is in deck 01 (Kingambit); none of the hit-back cards are in a list |
| 12 | **Legendary Pulse draws before Hiking Trail tops the hand up to 3** | Text alone does not set the order; Dustin's recording of Sept 25 does (one clip). | 4 lines plus a test | 4 | Panel t-suicune against t-blaziken |
| 13 | **Electrical Cord keeps the Energy it could not move** (fewer than two Benched Pokémon) | Text: move 2 Energy to Benched Pokémon; the rest is discarded with the holder, not lost. | About 10 lines | 4 | No |
| 14 | **Hydreigon / Giratina ex / Magneton / Milotic ex "attach from the Zone to itself" Abilities are not offered on an Active under an Energy Zone lock** | Nothing forbids using it; it just attaches nothing. Bot behaviour only. | About 8 lines (a pattern they already use for Ice Maker) | 3 to 4 | Panel t-hydreigon; the lock is in deck 13-A |
| 15 | **Will is not applied to a Victory Star reroll** (the reroll is a fresh batch of coins; today upstream forces it) | Card text of both; seen in a real game with Dustin's word (recording 203626). | About 3 lines plus a test | 4 | Victini only in draft D, which has no Will |

**Worth sending, but more code or a weaker basis:**

| # | Fix | Basis | Size | Wants it? | In his lists? |
|---|---|---|---|---|---|
| 16 | **Heavy Helmet reads the holder's *current* Retreat Cost** (Ariados, Goo-zooka and Plaza change it); and Grass Knot / Shadow Seeker read the *defender's* cost from the defender's side. Natural follow-up to #383. | Card text "has a Retreat Cost of 3 or more"; Dustin's heavyhelmet_test.MP4 (Sept 25). | About 90 to 140 lines in 3 files (the retreat-cost function must take the owner) | 3 for the Helmet; 4 for the Grass Knot half | Helmet in deck 01 (Kingambit) and 03; the only reachable route is Ariados or Goo-zooka against a Helmet holder with printed cost 2; Grass Knot in deck 12 |
| 17 | **Healing cards (Potion, Erika, Marlon, Lillie, and Pokémon Center Lady) only offer damaged Pokémon as targets** | Dustin's rule (restated Sept 22). The printed text is silent. | About 6 lines | 3 | Erika (t-sceptile), Lillie (deck 05), Center Lady in many lists |
| 18 | **"Random Energy" is really random** (Piers, Crawdaunt Unruly Claw, the Psychic Supporter, Raticate ex Thieving Incisors; upstream takes the last one attached) | Card text says "random". Upstream chose the shortcut to keep search small; that reason weakened when it capped forecasts at 20 branches (#392). | Piers 3 lines; Thieving Incisors about 6 to 8 | 3 | Raticate ex in decks 13-A, 14, 15; the Psychic Supporter in deck 05 |
| 19 | **After a double knockout, the attacker promotes first** | Dustin's play; one recording (203626) supports it. No card text. | About 5 lines | 3 | Any Rocky Helmet or Destiny Burst game |
| 20 | **Lum Berry / Bad Dreams: the player whose turn is ending resolves first** | The official battle FAQ's worked example is exactly this. | About 25 to 45 lines | 3 | Bad Dreams in t-altaria (Lum Berry is in no list) |
| 21 | **Clemont's Backpack's +20 reaches the opponent's Bench** (Heliolisk's Electrispark) | Card text: "to your opponent's Pokémon", not Active. Seen 4 times. | About 20 lines; needs a new turn-effect field | 3 | Deck 09 |
| 22 | **Fossils count as Item cards** (an Item lock stops them; seven other "Item card" texts count them) | Rests on Dustin's Oct 2 Sail Fossil screenshot (attach it), not on the card data. | Eight sites in 6 files | 2 to 3 | No list has a Fossil |
| 23 | **Opening hand: deal 5; only if none is a Basic, swap one for a Basic** (upstream makes the first card a Basic and deals 4 more) | Two community studies plus Dustin's own 50-hand test. No card text. **It changes every simulated game**, so the maintainer may want more. | About 20 lines in one function | 3 to 4 | Every deck |
| 24 | **The hit-back left by an attack (Cursed Jewel, Spike Armor...) takes Weakness** | The card text does not say; proof is recorded games (183108 twice). Sits next to their open #367 (a different interaction, so a textual conflict is unlikely). | About 50 to 70 lines | 3 | Mega Sableye ex (brews 07, 09) |
| 25 | **Comfey's Flower Shield and Teal Mask Ogerpon ex's Soothing Wind keep working after the status is applied** | Card text "recovers"; applies as soon as the Energy arrives. | About 70 lines, 8 places | 3 | Deck 14; deck 12 |
| 26 | **Coin-flip damage Abilities (Meowth's Carefree Steps, Togekiss, Guarded Grill...) also flip for damage an attack delivers through a queued choice:** Heatmor Tongue Whip, Vespiquen ex Chase Order, Gyarados Wild Swing, Hoopa ex Shadow Bullet and 18 other "also does X to a Benched Pokémon" attacks, Mega Kangaskhan ex's second hit. One function change. | Card text: "if any damage is done to this Pokémon by attacks, flip a coin." Dustin's recordings. #335 did Bastiodon and Goodra only for damage inside the attack outcome. | About 50 to 70 source lines in one function plus a helper, and 150 to 200 test lines (our own commits are not the measure; they do not port) | 4 by the readers, but large; send as a single PR | Vespiquen ex (t-vespiquen); Hoopa ex (t-weezing, Dustin) against Glimmora in deck 01 is the one listed game (the Glimmora coin is skipped on this path too); no listed deck has the Meowth-type defender |
| 27 | **Growl-type cuts ("attacks used by the Defending Pokémon do -20") stay on the Pokémon that was hit** and apply before Weakness | Card text; official FAQ order; recordings. | About 30 lines in 3 files | 3 | Bonsly Teary Attack (t-lucario); Eevee P-A 030 is in no list |
| 28 | **Guarded Grill / Securely Sheltered heads cut comes off after Weakness** | The FAQ's step order. | About 130 lines (our commit; it may not port as is) | 3 | Bastiodon and Hisuian Goodra are in no list |
| 29 | **A search that fills the hand stops at 10 cards** (Clemont, Serena, Cabbie, Juliana) | In-game limit of 10; extends their own #257. Evidence is by analogy. | About 10 lines | 3 | Clemont in deck 09 |
| 30 | **Ice Face, Coordinated Unit and Unown Guard cut damage only from the *opponent's* attacks** | Card text "from attacks from your opponent's Pokémon". Could bundle with row 6. | About 10 lines | 3 | None |

**Big, doubtful, or not ours to send:**

| Item | Why not |
|---|---|
| Glimmora / Dusknoir coin on every knockout, not only knockouts by an attack | Rule is observed (Poison knockout, recording 200857) and Glimmora is in his Kingambit deck, but it needs a new step inside the Checkup and knockout code (60 to 80 lines or a new action); wants it 2 to 3. Worth discussing with Dustin because it is his own deck. |
| Victory Star and Will with a Confused attacker or a block coin | Real and recorded for Confusion (Will deck 10 and brews 01, 04 reach the Will half) but 150 to 250 lines through the coin pipeline; the block-coin half is card text only. |
| Hit-backs resolve after the attack's own effects | Large, architectural; visible mostly via Prickly Powder, plus a small Butterfree Sunny Wind versus Rocky Helmet case (t-sceptile). |
| Player chooses which Energy pays a retreat or is discarded; Misty chooses her target before the coins | New actions and more search branches in the most common move: against what the maintainer is cutting. |
| Empty-deck and hidden-deck play rules (Poké Ball, Arcade, draw Abilities, Cabbie, Mesagoza...) | Rest on Dustin's rule with no recording; upstream's look-inside-the-deck design partly conflicts with them. 1 to 3. |
| The T2 tie (last Pokémon dies to a hit-back after the third point) | One recording, and it contradicts the printed Tips; upstream's author deferred it for lack of evidence. 2 to 3. |
| End-of-turn knockout before Checkup; Quick Growth before Checkup; promote before the draw | These undo the maintainer's own #358 design. 1 to 2. |
| Stale switch frame left empty after an on-knockout hit | Upstream's bug is real by reading, but needs a very rare board and we have not reproduced it. |

**Nothing to send:** #335 and #383 (already merged), Sleep and Paralysis (upstream's #379 matches us), Mega Garchomp ex (upstream has the card), damage order (#379), Perish Body on a queued hit (upstream's own open #337 is stale, 248 commits behind main, and main has no code for it; row 26 would fix it), Quick-Grow Extract / Wallace choosing the target (the maintainer's branch `fix/quick-grow-extract-choice` has it; his #402 and issue #399 were closed unmerged and the reason is not visible, so do not send a competing PR), Luxury Coin on own Stadium (feature not upstream), Mischievous Ring (upstream already right), Raid (upstream #348 did it).

## Keeping up (a minute a week, no new process)

```bash
python3 tools/upstream_watch.py          # what is new upstream since the last look
python3 tools/upstream_watch.py --mark   # same, then record upstream's tip so next week starts there
```

The first run clones upstream (a blobless clone, under 100 MB) into `~/upstream_watch/deckgym-core`. After that it only fetches. The starting point is `rl/upstream_watch/LAST_CHECKED.txt`, set to `c3083a3f` (today's look). It prints one line per merged change: number, date, author, title, which kinds of files it touches (engine/tests/data/tooling), new cards, and the names of cards from our lists that the change mentions, ending in a hint: **LOOK** (new cards, or an engine change that names a card we play, or whose title says fix/bug/panic/crash/wrong/incorrect/stale/loop), **maybe** (other engine changes), **skip** (bots, viewer, bindings, docs, CI only). A run from Oct 1 (titles shortened; the complete output is `weekly_check_sample_output.txt` in this folder):

```
hint  | what                                                                              | engine/tests/data/tooling | new cards | our cards mentioned
LOOK  | #384 2026-10-04 bcollazo: Consume stale ...ability choices instead of panicking   | 1/0/0/0 | - | -
maybe | #385 2026-10-04 bcollazo: Don't offer optional on-play abilities during setup ... | 1/1/0/0 | - | -
maybe | #386 2026-10-04 bcollazo: Resolve a pending promotion before a queued EndTurn     | 1/0/0/0 | - | -
skip  | #387 2026-10-04 bcollazo: viewer: bench-sized stadium card ...                    | 0/0/0/4 | - | -
LOOK  | #390 2026-10-07 bcollazo: Fix exponential Spending Rush enumeration ...           | 5/1/0/1 | - | -
LOOK  | #389 2026-10-07 bcollazo: Don't trigger Caterpie's Quick Growth when setup ends   | 1/1/0/0 | - | Caterpie, Metapod
LOOK  | #394 2026-10-08 bcollazo: Limit actions per turn to 100 ...                       | 3/1/0/0 | - | -
LOOK  | #395 2026-10-09 rook-productions: Key Trainer logic by effect text ...            | 4/2/0/1 | - | Cheren, Clemont, Copycat, Cynthia, ... (+14 more)
skip  | #400 2026-10-16 bcollazo: Fix unreachable 'et' player code ...                    | 0/0/0/1 | - | -
LOOK  | #383 2026-10-16 dacz8976-creator: Limit Heavy Helmet, Harden, Hide ...            | 1/2/0/0 | - | Darkrai, Deceptive Needle, Heavy Helmet, ...
```

(The lines for #391, #392 and #393 are left out here for length.) It matches names of 6 letters or more only and prints the shorter ones it skipped (Misty, Absol, Axew...). A hint is a prompt to read the change, not a verdict. The script has 9 tests (`tools/test_upstream_watch.py`, no network).

**What makes a change worth taking:**

1. It adds cards (new ids in `database.json`; the next one is a new set or promo) or reprints of cards we play: needs the table A row 1 procedure.
2. It changes an engine rule for a card that is in one of his decks or the panel lists (the "our cards mentioned" column), and ours does not already do the same: compare the card text with what our engine does, then take it, or add it to table A.
3. It fixes a crash, a stuck state or an endless loop (title says so, or the change is a guard): a few lines, take it with the next pin.
4. Skip everything else: bots, replay viewer, bindings, docs, CI, dependency bumps, refactors, cards no list plays (we have most of those already).

When a **LOOK** line is worth acting on, its PR number goes to the coordinator, who decides whether it goes into the next pin. Any rules change is a rules switch and needs Dustin's word. Taking a change never needs a post to upstream; posting a fix of ours does, and needs his OK.

## Not checked

- Nothing was compiled or run. Tests quoted as "settling it" were not executed.
- For the open PRs #367 and #388 only the saved PR text was read, not a diff. For #401 the checker read its branch (`fix/ability-move-generation`): the Fossil piece is a 3-line change in `move_generation_abilities.rs`.
- The deckgym.com card count: I do not know which data it reads.
- Whether upstream's maintainer would merge any row of B: the 1 to 5 scores are a judgement from the PR history, not a promise.

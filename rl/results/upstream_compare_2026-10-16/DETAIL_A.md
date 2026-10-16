# Upstream changes we lack (A): condensed findings

One block per finding from the 7 readers, with the independent checker's corrections where one was made (V=confirmed/partly; - = not separately checked because the reader's call was skip/already have). Text is shortened; items.json.gz has everything.

```
[A1] PR384 | performance or safety | own=no | decks=no | diff=trivial | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: A queued 'use ability' choice for Zeraora's first-turn Energy ability (which is never a player choice) crashes the simulator if it reaches the reducer. Upstream turns it into a do-nothing. Only a stale choice (slot now holds a different Pokemon) can reach it.
   DECKS: Zeraora (A3a 021, A4b 149/150, B1 304, P-A 074) is in none of the panel, Dustin or brew lists.
   CONFLICT: None (one match arm). But it only hides the symptom: any other passive ability, or an emptied slot (the expect at :26-28), still panics on a stale choice. It mostly falls away once PR385's guard is t…
   VERIFIER: 
[A1] PR385 | rules fix | own=no | decks=no | diff=easy | rec=take rank=3 conf=CONFIRMED | V=confirmed
   WHAT: Optional 'when you put this Pokemon from your hand onto your Bench' abilities (Miraidon ex / Koraidon ex Legendary Drive, Roaring Moon Ancient Roar, Poltchageist heal) must only be offered on the owner's own turn. Before the fix they were also queued during g…
   DECKS: Miraidon ex, Koraidon ex, Roaring Moon, Poltchageist are in no list. Team Rocket's Boss (panel t-suicune, brew-02) could only trigger it if the opponent's hand held one of those four, so no listed ma…
   CONFLICT: None found. Ours takes the card as an argument (upstream reads the board) so the guard is one line at the top of on_bench_from_hand. players/opening_class.rs:176-179 already classes these as 'bench e…
   VERIFIER: The core claim stands: upstream has the guard, ours does not, and the bad prompts can happen in ours. Five small edits to the finding. 1. Tests. "No test in ours covers any of this" and "ours has none for these abilities" are partly wrong. Ours has in-turn tests: tests/pokemon/miraidon_ex_test.rs:24-93 (Legendary Drive) and tests/pokemon/roaring_moon_test.rs:25-141 (Ancient Ro…
[A1] PR386 | bug fix | own=no | decks=no | diff=easy | rec=test first rank=1 conf=CONFIRMED | V=confirmed
   WHAT: When a knockout empties a player's Active Spot while an 'end turn' marker is queued on the choice stack, the replacement choice was put UNDER the marker, so the turn-ending step ran first and crashed on the empty Active Spot. Upstream now puts the replacement…
   DECKS: Needs Kiawe (in no list) with its Marowak/Turtonator Active already within 40 HP of dying, against Jolteon ex (Dustin deck 15). Giratina ex (brew-10) goes through the second queue site, but when Gira…
   CONFLICT: The special case must run before ours' phase_floor/pending_hit_floor logic (F8, G2 switches) and use SimpleAction::Promote instead of Activate. Alternative: PR388's flag approach for the two sites. D…
   VERIFIER: The core claim, the deck-impact statement and the side finding all hold. I found no error in them, only things to tighten. Nothing was built or run, so "our unit test fails today" is read from the code, not observed. 1. Line numbers. Upstream's fix is src/state/mod.rs:896-911 (the check is at 899-903, the push-on-top branch at 905-911), not 899-912. The test starts at :1095. I…
[A1] PR389 | rules fix | own=yes - sam… | decks=no | diff=trivial | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: Caterpie's Quick Growth ('at the end of your opponent's turn') evolved Caterpie into Metapod when SETUP ended and turn 1 began, because setup is not a real turn.
   DECKS: No change for ours. Caterpie (2), Metapod (2), Butterfree (2) ARE in panel t-sceptile, so an engine with upstream's pre-Oct-7 behaviour would hand the first player's Active Caterpie a free evolution …
   CONFLICT: None. Nothing to port except the test.
   VERIFIER: 
[A1] PR390a | performance or safety | own=no | decks=no | diff=easy | rec=take rank=2 conf=CONFIRMED | V=confirmed
   WHAT: Random multi-hit attacks (Spending Rush: one random hit per Metal Energy) listed every hit sequence (targets^hits). With many Energy this takes seconds to forever (15 Energy vs 3 Pokemon = 14.3M sequences). Upstream enumerates hit-count splits instead (4 targ…
   DECKS: Gholdengo ex (Spending Rush, B2a 078/104/114) is in no list. Of the 18 cards whose attacks choose targets 'at random', none is in any list.
   CONFLICT: None; function has the same name and signature in ours. Outcome probabilities are renormalised downstream (outcomes.rs:493-499), so the exp/ln rounding is harmless. Side effect: the branch ORDER beco…
   VERIFIER: The finding holds. Keep id, what, recommendation "take", difficulty "easy" and changes_decks_games "no". Four things to change in the wording: 1. Wrong cite for "renormalised downstream (outcomes.rs:493-499)". Those lines in ours sit inside `force_first_heads` (ours src/actions/outcomes.rs:447-505). That function only conditions coin-flip outcomes. Spending Rush outcomes carry…
[A1] PR390b | bot / refactor / tooling | own=no | decks=no | diff=medium | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: New opt-in diagnostic module perf_watch (off by default): records a JSON file with the full state whenever one engine step is slow, makes too many branches, or is still running after a deadline (monitor thread), grouped by cause. Also adds Outcomes::len()/is_…
   DECKS: Diagnostic only; changes no game.
   CONFLICT: Hooks three entry points whose names differ in ours (apply_action, try_forecast_action/forecast_action, generate_possible_actions: src/actions/apply_action.rs:46,437,466; src/move_generation/mod.rs:3…
   VERIFIER: 
[A1] PR394 | performance or safety | own=no | decks=no | diff=easy | rec=take rank=2 conf=CONFIRMED | V=confirmed
   WHAT: Per-turn cap of 100 actions: after that only EndTurn and attacks are offered (pending effect choices still resolve). Stops a game that never ends, e.g. two Dusknoir passing damage back and forth with Shadow Void ('as often as you like').
   DECKS: Dusknoir A2 072 (Shadow Void) and Vaporeon are in no list. No listed deck has an ability that can repeat without limit.
   CONFLICT: Add a State field (serde default), count in ours' shared prefix (apply_action_helpers.rs:1162-1197 / wrap_with_common_logic :1283), reset in advance_turn (state/mod.rs:1191-1213) AND at the setup->tu…
   VERIFIER: The core claims hold (upstream has it, ours does not, no listed deck is touched, easy to port). Four things in the finding should change. 1. The line "Search bots stop at depth, so only random-ish players can loop" is unsupported and partly backwards. Search depth limits one decision's lookahead, not how many decisions a player makes in one turn. - Random-ish players cannot ha…
[A1] PR401a | bug fix | own=no | decks=no | diff=trivial | rec=take rank=1 conf=CONFIRMED | V=confirmed
   WHAT: (Open PR) DiscardFossil is offered twice for every Fossil in play, because two code paths both add it.
   DECKS: No Fossil Trainer (Helix, Dome, Old Amber, Plume, Claw, Root, Skull, Armor, Cover, Sail, Jaw) and no Fossil-style Pokemon is in any list.
   CONFLICT: None; skip fossils in ours' ability loop (our G10/G11 Fossil-as-Item switches sit elsewhere).
   VERIFIER: The finding holds. Make these edits: 1. The reader says it could not read the PR diff. It is in the scratch clone. Branch origin/fix/ability-move-generation holds two commits dated Oct 15, be6c0142 and d7520faa. Neither is in upstream main. The Fossil part is a 3-line change in upstream src/move_generation/move_generation_abilities.rs: it skips Fossils in the ability loop. The…
[A1] PR401b | bug fix | own=no | decks=no | diff=easy | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: (Open PR) MCTS player expanded children of FINISHED games and asked for legal moves there; with no Active Pokemon some ability checks crash (issue #398, Baxcalibur's Ice Maker).
   DECKS: Baxcalibur (Ice Maker) is in panel t-suicune, so a tool that generates moves on a finished t-suicune game would panic; the k-family pilots never do. Dustin's pilots do not use MCTS.
   CONFLICT: None.
   VERIFIER: 
[A1] PR388 | bot / refactor / tooling | own=partly | decks=no | diff=easy | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: (Open PR) Replace the remaining 'EndTurn queued on the choice stack' uses with the end_turn_pending flag, so promotions can always be inserted at the bottom and PR386's special case is unnecessary.
   DECKS: Giratina ex (brew-10-diancie-giratina) uses one of the two sites; behaviour would be identical. Kiawe is in no list.
   CONFLICT: Same area as PR386; pick one fix. Flag version also touches the 'forced turn end' logic in ours' search (expectiminimax_player.rs:633-642), which already handles both forms.
   VERIFIER: 
[A1] PR367 | rules fix | own=no | decks=possibly | diff=medium | rec=test first rank=2 conf=PLAUSIBLE | V=partly
   WHAT: (Open PR) When Mega Sableye ex's Cursed Jewel hit-back (40 damage to the attacker that hit it) lands on an attacker holding its own Rocky Helmet, the Helmet should reflect its 20 back onto Sableye.
   DECKS: Mega Sableye ex (brew-07-hoopa-darkrai-sableye, brew-09-sableye-obstagoon) versus a Rocky Helmet holder: panel t-blaziken (1 Helmet), Dustin deck 06, brews 03a, 06, 06b. The other four hit-back attac…
   CONFLICT: The code is small (inside handle_attack_retaliation, next to our P2 Weakness addition), but it is a rules change: needs Dustin's word and the full rules-switch procedure, and brews 07 and 09 have reg…
   VERIFIER: The core facts hold: our engine really lacks the Helmet reflect, and the deck reach is right. But the finding needs these changes. 1. FRAMING. This is not something "upstream has fixed". Upstream main does not have it. PR #367 is open and unmerged (opened 2026-09-03, about six weeks old). It was written in a Claude Code session on bcollazo's account. Upstream main and ours cur…
[A1] PR380 | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=PLAUSIBLE | V=-
   WHAT: (Open PR) Team Rocket's Electrode's Destiny Burst (70 damage back to the attacker when knocked out in the Active Spot).
   DECKS: Team Rocket's Electrode (B4a 020) is in no list.
   CONFLICT: None; nothing to take.
   VERIFIER: 
[A1] PR381 | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: (Open PR) Team Rocket's Magmar (Derisive Roasting, +50 per Special Condition: only tests added) and Team Rocket's Slowpoke (Scavenge: random Item card from discard to hand).
   DECKS: Team Rocket's Slowpoke is in brew-04-xatu-slowking and already works in ours; Team Rocket's Magmar is in no list.
   CONFLICT: None.
   VERIFIER: 
[A1] PR337 | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=PLAUSIBLE | V=-
   WHAT: (Open PR, stacked on #336) Galarian Cursola's Perish Body (coin flip when knocked out by an attack: heads knocks out the attacker).
   DECKS: Galarian Cursola is in no list.
   CONFLICT: None; nothing to take.
   VERIFIER: 
[A1] PR338 | bot / refactor / tooling | own=not appli… | decks=no | diff=hard | rec=not needed rank=1 conf=PLAUSIBLE | V=-
   WHAT: (Open PR) Pure refactor: merge three near-identical 'defender flips a coin' transforms (damage prevention, Guts, Perish Body) into one.
   DECKS: Refactor, no rule change intended.
   CONFLICT: Would collide with our G1-G8 coin gates; no behaviour to gain.
   VERIFIER: 
[A1] PR336 | bot / refactor / tooling | own=not appli… | decks=no | diff=hard | rec=not needed rank=1 conf=PLAUSIBLE | V=-
   WHAT: (Open PR) Pure refactor: Guts ability code shared between the Attack path and the queued-damage path.
   DECKS: Ursaluna (Guts) is in no list.
   CONFLICT: Would collide with ours' G7 own-side Guts and G1-G3 coin gates.
   VERIFIER: 
[A1] PR304 | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: (Open PR) Lilligant's Toughness Aroma (+20 HP to your Grass Pokemon), with the bonus cached on each Pokemon.
   DECKS: Lilligant (B1 018 / B1 329) is in no list.
   CONFLICT: None.
   VERIFIER: 
[A2] B4b-data-437-reprints | new cards or data | own=partly | decks=no | diff=medium | rec=test first rank=3 conf=CONFIRMED | V=confirmed
   WHAT: Upstream commit 9044ff6 'B4b' (Sep 29) adds 438 cards and touches only database.json, card_ids.rs and database.rs (nothing in database.json or card_ids.rs is removed; 6 chunk-boundary lines move in database.rs). 437 are word-for-word reprints of cards we alre…
   DECKS: No deck file in the repo names a B4b id or P-B 095-103 (git grep over decks/ and lib/ on origin/main finds none), so no existing simulated game changes. 79 of the 187 card names in inventory.json hav…
   CONFLICT: No rules fix of ours is overwritten (data only). Practical conflicts: (1) our card_ids.rs, database.rs and database.json are 100% CRLF, upstream's are LF, so the upstream patch cannot be applied; reg…
   VERIFIER: The core finding stands. I read the relevant code in both engines and re-ran the data comparison myself. These edits are needed: 1. Name count. Items and Supporters have 22 names, not 23: 6 Items (Electric Generator, Field Blower, Flame Patch, Lucky Ice Pop, Order Pad, Quick-Grow Extract) and 16 Supporters. The other counts hold: 347 + 8 Pokemon, 12 + 34 = 46 Items/Supporters,…
[A2] mega-garchomp-p-b-099 | new cards or data | own=yes - sam… | decks=possibly | diff=easy | rec=already have rank=4 conf=CONFIRMED | V=-
   WHAT: The one genuinely new card in B4b: Mega Garchomp ex (P-B 099, Promo B): Stage 2 Dragon from Gabite, 220 HP, no weakness, retreat 2, one attack Falling Edge [W][F][C] 190 'Discard 2 random Energy from this Pokemon.' It needs no new rule in either engine: the t…
   DECKS: No list names it today. Natural host: Dustin's 08-garchomp-toolbox (Energy Water+Fighting, 2 Gible A2 121, 2 Gabite B4a 053, 2 Garchomp B4a 054, Mesagoza, Rainbow Cave, Lucky Ice Pop, Copycat, Wally,…
   CONFLICT: None. Upstream's entry equals ours, so a later B4b sync regenerates it without a diff (it moves from after P-B 094 to its P-B 099 slot in the generated files).
   VERIFIER: 
[A2] promo-b-8-reprints | new cards or data | own=partly | decks=no | diff=trivial | rec=take rank=3 conf=CONFIRMED | V=confirmed
   WHAT: The other eight Promo-B cards in the B4b commit, all exact reprints and all Pokemon: Darkrai P-B 095 (= B2b 040), Falinks 096 (= B2 092), Gible 097 (= B4a 052), Gabite 098 (= B4a 053), Delcatty 100 (= B4 135), Charmander 101 (= B2b 007), Drampa 102 (= B4 124)…
   DECKS: No list uses the promo ids. Names in lists: Darkrai (panel t-altaria), Gible/Gabite (deck 08 only, with the A2 121 / B4a 053 printings). The only practical effect: a deck code or list that uses promo…
   CONFLICT: None beyond the CRLF/regeneration and 3,879/3,880 test-count notes in the B4b data item.
   VERIFIER: The finding holds. Upstream does have the eight cards, and ours lacks only their ids. Six small edits to make to the finding: 1. "Field for field" should read "identical in every gameplay field". The id and pack label differ. Rarity also differs on four of the eight: Darkrai (☆ vs ◊◊◊), Charmander (◊◊◊ vs ◊), Drampa (◊◊◊ vs ◊◊), Pikachu ex (☆☆☆ vs ◊◊◊◊). Our engine never reads…
[A2] trainer-identity-pr395 | bot / refactor / tooling | own=no | decks=no | diff=medium | rec=test first rank=3 conf=CONFIRMED | V=confirmed
   WHAT: PR #395 (James Larson / rook-productions, merged Oct 9, closes upstream issue #166 'Make Trainer Implementations Robust to Alternate Versions'): Trainer logic is looked up by effect text instead of by card id. New src/trainer_identity.rs (98 lines): canonical…
   DECKS: Plumbing only. The Trainer names in inventory.json with B4b printings: Copycat (nearly every list), Lucky Ice Pop (panel t-hydreigon; Dustin 01, 03, 07, 08, 11; many brews), Field Blower, Flame Patch…
   CONFLICT: Code is small and conflict-free with our rules fixes, but (1) it sits on the hottest path (every Trainer in hand at every move generation) and upstream's lookup hashes the whole effect text (100-300 …
   VERIFIER: The core claim stands, and so does "test first". Five parts of the finding need fixing. 1. Scope is Item and Supporter only. The B4b Tool and Stadium reprints are not part of #395 and already work in ours. Tools and Stadiums were already keyed by effect text in both engines. Ours: src/tools.rs:33-37 (tool_effect_text_from_card_id) and has_tool/tool_count compare effect text; s…
[A2] ours-id-keyed-followups | bug fix | own=not appli… | decks=no | diff=easy | rec=take rank=2 conf=CONFIRMED | V=partly
   WHAT: Our own spots that still name cards by id and would miss B4b printings (what our docs call the 'B4b-era data details', plus what I found by scanning every CardId:: reference outside tests against the 437 reprints). They ride with the B4b data, they are not an…
   DECKS: Only Haxorus/Iris (deck 11 plays Haxorus B2b 056 and Iris B2b 067 today, so it is fine now) and Lucky Ice Pop / Mesagoza in the coin plan (matters only with Gholdengo in play; no list has Gholdengo) …
   CONFLICT: None; each is a one-line id addition or a switch to a name/text check. Our rules-repair gates already read text and mechanics.
   VERIFIER: The facts hold. The framing and a few details need fixing. 1. WRONG CATEGORY. This is not an upstream change we could take, and the finding itself says so. The "take" means "do it in our own B4b import". Only gap (4), Iris and Haxorus, exists in both engines, so only that one could be offered upstream as a small PR (it needs Dustin's OK). Everything else is ours-only: upstream…
[A2] 09e964f-fix1-hp-aura-promotion | bug fix | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: 09e964f fix 1: after knockouts, remove 'promote this Benched Pokemon' choices for a slot that a later knockout emptied. Case: Lilligant's +20 HP aura ('Each of your [G] Pokemon') disappears when Lilligant is knocked out and kills a damaged Benched Pokemon aft…
   DECKS: Lilligant (the only 'Each of your Pokemon gets +N HP' card) is in no list in inventory.json.
   CONFLICT: Upstream's code filters Activate choices, ours promotes with Promote, so the patch would do nothing on ours (state/mod.rs:1399) and the test can't be pasted verbatim (it expects Activate).
   VERIFIER: 
[A2] 09e964f-fix2-lethal-knock-back | rules fix | own=yes - but… | decks=no | diff=trivial | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: 09e964f fix 2: when a 'switch out your opponent's Active' hit is lethal, do not also queue the switch choice (the opponent chose a new Active twice). Touches Hariyama Push Out, Grapploct Knock Back, Houndour/Yamper Roar, Throh Circle Throw, and Chinchou Lurin…
   DECKS: Of the attackers, only Houndour (draft D) is in any list, and its Roar prints no damage (python3 lib/card.py B1a 015), so it can never be lethal. Hariyama A3 091, Grapploct, Throh, Yamper, Chinchou a…
   CONFLICT: Direct conflict with our lethal-knock-back ruling and tests/rules_repair_retaliation_timing.rs:136; also with Dustin's Sept 30 decision (rules switch question 10).
   VERIFIER: 
[A2] 09e964f-observation-serde-api | bot / refactor / tooling | own=partly | decks=no | diff=medium | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: 09e964f's non-rule part: new src/state/observation.rs (146 lines): read-only public accessors (public_context, public_turn_effects, observed_coin_reflip, effective_attack_cost, effective_attached_energy, decision_actor, knockout_points) and State::agent_snaps…
   DECKS: Adds API surface only; no rule or card effect is touched.
   CONFLICT: agent_snapshot builds a fake Trainer card with id UNKNOWN, which conflicts with our Card::Unknown design and would need rewriting; the accessors read fields we renamed or extended (own_knocked_out_co…
   VERIFIER: 
[A2] 09e964f-external-player-windows | bot / refactor / tooling | own=no | decks=no | diff=medium | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: 09e964f's external_player.rs change: opt-in 'agent_snapshot' protocol messages, Windows support (cmd /D /S /C with no console window instead of sh -c), one buffered write per JSON line (with a unit test), and a docs/bot-protocol.md section.
   DECKS: None; it only changes how an outside bot program is started and spoken to.
   CONFLICT: None, but it depends on the external-bot feature we do not have.
   VERIFIER: 
[A2] upstream-only-gaps-in-b4b-cards | bug fix | own=yes - sam… | decks=no | diff=trivial | rec=not needed rank=1 conf=PLAUSIBLE | V=-
   WHAT: Not an upstream change we lack: places where upstream's own code still gets B4b-reprinted cards wrong and ours is right (found while checking what B4b needs).
   DECKS: Dragalge ex and Chinchou are in no list in inventory.json.
   CONFLICT: None.
   VERIFIER: 
[A3] 379-lockout | rules fix | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #379 (commit e38b77db): Asleep and Paralyzed Pokémon cannot attack or retreat.
   DECKS: Both engines already hand an Asleep or Paralyzed Active no attack and no retreat, so no list sees a difference.
   CONFLICT: None; nothing to bring in.
   VERIFIER: 
[A3] 379-paralysis-timing | rules fix | own=yes - sam… | decks=no | diff=easy | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #379: Paralysis lasts through the victim's whole next turn and clears at the Checkup after it. Upstream also adds a 'turn it was inflicted' stamp, so a Paralysis put on a Pokémon during its OWN owner's turn survives to that owner's following turn.
   DECKS: The two engines differ only if a Pokémon is Paralyzed during its own owner's turn (ours would clear it at once, upstream keeps it). I searched every effect text in upstream's database.json (4,317 car…
   CONFLICT: A stamp means a new field on PlayedCard, which is saved/serialised state and read by our observation layer (src/observation.rs); it would touch our paralysis_lifecycle tests for no reachable gain.
   VERIFIER: 
[A3] 379-exclusive | rules fix | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #379: Asleep, Paralyzed and Confused replace each other (a Pokémon has at most one); Poisoned and Burned still stack with anything.
   DECKS: Same result in both engines for every Sleep/Paralysis/Confusion source in the lists (e.g. Alolan Muk ex's random condition is not in any list).
   CONFLICT: None.
   VERIFIER: 
[A3] 379-active-only | rules fix | own=partly | decks=no | diff=trivial | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: PR #379: Special Conditions can only be put on the Active Pokémon (central guard in apply_status_condition).
   DECKS: Unreachable in play: no card text puts a Special Condition on a Benched Pokémon, so the guard changes nothing for any list. (Upstream needed it because its own tests poisoned Benched Pokémon.)
   CONFLICT: A five-line early return in State::apply_status_condition would not conflict, but it could break our own tests that set a status on a bench slot directly.
   VERIFIER: 
[A3] 379-checkup-order | rules fix | own=yes - sam… | decks=no | diff=trivial | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: PR #379: Pokémon Checkup resolved per Pokémon in the printed order (Poisoned, Burned, Asleep, Paralyzed), the player whose turn just ended first. Upstream itself says there is no visible behaviour change.
   DECKS: Damage is additive and the coins are drawn as a pre-set outcome list, so grouping by condition or by Pokémon gives identical games.
   CONFLICT: Rewriting our loop would only risk the M1 Checkup pause/resume logic (FinishPokemonCheckup frames).
   VERIFIER: 
[A3] 379-empty-board-tie | rules fix | own=yes - but… | decks=possibly | diff=easy | rec=skip rank=2 conf=PLAUSIBLE | V=-
   WHAT: PR #379 (commit ec0f3d98): if BOTH players reach 3 points in the same action and one has no Pokémon left, the empty-board player loses (upstream used to call it a Tie).
   DECKS: Needs both players to hit 3 points on one action (for example a Checkup double Knock Out from Poison, or a retaliation Ability) with one board empty. No specific card in any list makes it likely; Pyu…
   CONFLICT: Directly touches our rules4 T2 repair: the both-at-3 branch sits right after it (lines 1036-1039) and the test at rules4_t2_simultaneous_finish.rs:67-72 would have to change.
   VERIFIER: 
[A3] 379-damage-order | rules fix | own=yes - sam… | decks=possibly | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #379 (commit af33471f): damage is worked out in the official FAQ order: attack damage, effects on the attacker, Weakness, effects on the defender, floor at 0 once at the end (FAQ example 50 x 2 - 20 = 80).
   DECKS: The main order is identical, so taking this fix changes nothing. Three spots differ and upstream is the weaker side in each: (1) attack-reducing effects such as Growl/Teary Attack ('attacks used by t…
   CONFLICT: Nothing to port. Taking upstream's version of Growl/Fang/coin cut would undo our R1 repair, rules switch 1 repair B and the Fang test.
   VERIFIER: 
[A3] 379-bench-fizzle | bug fix | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #379 (commit 7e306c69): 'also does damage to a damaged Benched Pokémon' attacks lost their own damage when no Benched Pokémon had damage (Team Rocket's Zapdos ex Thunderclaw; Wellspring Mask Ogerpon Wellspring Dance test added).
   DECKS: Neither Team Rocket's Zapdos ex nor Wellspring Mask Ogerpon is in any list. Teal Mask Ogerpon ex (t-vespiquen, Dustin 12) is a different card.
   CONFLICT: None.
   VERIFIER: 
[A3] 379-tests-and-tooling | bot / refactor / tooling | own=partly | decks=no | diff=easy | rec=not needed rank=1 conf=PLAUSIBLE | V=-
   WHAT: PR #379 leftovers: ~1,500 lines of new Game-level tests that quote the in-app Tips (evolution timing, deck-out is not a loss, Weakness Active-only, win conditions), plus a card_test fix that swaps template staples when the tested card shares a name with them …
   DECKS: Tests and a developer tool for generating test decks; no effect on simulated games.
   CONFLICT: None; the test files would need their imports adapted to our fork (different test_support names).
   VERIFIER: 
[A3] 358-defer-end-of-turn-ko | rules fix | own=yes - but… | decks=possibly | diff=hard | rec=skip rank=2 conf=PLAUSIBLE | V=-
   WHAT: PR #358: knockout checks for end-of-turn damage (Deceptive Needle, Bad Dreams, delayed damage) are postponed until after every other end-of-turn effect and Checkup effect, so a Pokémon at 0 HP can still be saved (Quick Growth evolving Caterpie into Metapod; G…
   DECKS: Reachable only as Deceptive Needle (t-hydreigon, t-weezing, Dustin 04, brews 07 and 09) or Bad Dreams Darkrai (t-altaria) against a Quick Growth Caterpie (t-sceptile only) that is at or under the dam…
   CONFLICT: Would collide with the M1 Checkup pause/resume frames (FinishPokemonCheckup, point-denial and promotion continuations), the Sept 26 fix that promotes before the next turn starts (5bab907), our Quick …
   VERIFIER: 
[A3] 358-blessed-salt | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #358: Garganacl's Blessed Salt ('During Pokémon Checkup, heal 10 damage from each of your Pokémon') implemented, healing before the deferred Knock Out check.
   DECKS: Garganacl, Flygon, Glaceon are in no list, so Blessed Salt, Sand Slammer and Snowy Terrain never occur in any simulated game.
   CONFLICT: One order difference with no evidence either way: upstream heals BEFORE Sand Slammer / Snowy Terrain damage (apply_action_helpers.rs:343-345), ours heals after (:343-344). Matters only for a Pokémon …
   VERIFIER: 
[A3] 358-quick-growth-slot | rules fix | own=yes - but… | decks=possibly | diff=hard | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: Part of PR #358's design (the engine code predates it): Caterpie's Quick Growth is resolved at the START of the next turn, after the Checkup, and only then are Knock Outs decided.
   DECKS: Caterpie/Metapod exist only in t-sceptile. Upstream order: Poison/Burn damage first, then the evolution cures it, so the Metapod ends 10 or 20 HP lower than in ours, and a Sleep or Burn coin is flipp…
   CONFLICT: Would undo our 'Caterpie evolves before Checkup' repair (rules09 'Other implemented repairs') and the Checkup frame logic.
   VERIFIER: 
[A3] 376-regice-crystal-body | new cards or data | own=yes - but… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #376: Regice's Crystal Body ('Prevent all effects of attacks used by your opponent's Pokémon done to this Pokémon') shares the Clear Veil shield.
   DECKS: Regice (A2 034) and Clear Veil are in no list, so no simulated game contains them (Regigigas in Dustin 01 wants Regice on the Bench but his list has none).
   CONFLICT: None; ours is the broader and more faithful version, so taking upstream's would lose coverage.
   VERIFIER: 
[A3] 376-alolan-muk-power-of-alchemy | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #376: Alolan Muk's Power of Alchemy ('Basic Pokémon in play (both yours and your opponent's) have no Abilities') switched off for Basics on both sides through the single ability lookup.
   DECKS: Alolan Muk (B2 097) is in Dustin's 01-kingambit-as-played and 01-muk-glimmora-kingambit-regigigas, alongside Regigigas (B3 134), whose Seal of Antiquity Muk switches off in BOTH engines (upstream att…
   CONFLICT: None needed. Upstream caches a flag on every PlayedCard (refreshed in State::refresh_ability_board_bonuses, state/mod.rs:237); ours computes it on demand, so there is no stale-flag risk.
   VERIFIER: 
[A3] 374-type-sets-urshifu | new cards or data | own=partly | decks=no | diff=easy | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: PR #374: in-play type sets (printed type plus types granted by an Ability) used for every 'is this a [X] Pokémon' check; Rapid Strike Urshifu ([W]+[F]) and Single Strike Urshifu ([F]+[D]) Double Type.
   DECKS: Neither Urshifu is in any list, and no other card in our database has a granted second type, so nothing a list plays can reach the unfinished spots. (Upstream added the seam for Mega Mewtwo X ex, a B…
   CONFLICT: None; finishing the ~15 printed-type reads would be a small clean-up if Urshifu ever enters a deck. Upstream's version replaces Card::get_type with get_types everywhere, which cannot be applied as a …
   VERIFIER: 
[A3] 357-lana | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #357: Lana (A3 152 / A3 194): playable only with Araquanid in play and an opponent Bench; the player picks which Benched Pokémon is switched in. Also a clippy clean-up in get_ability_mechanic.
   DECKS: Lana and Araquanid are in no list.
   CONFLICT: None. Note upstream's Lana is keyed on CardId A3152 only (apply_trainer_action.rs:82) while ours handles both printings.
   VERIFIER: 
[A4] 343-dragonair-dragons-blessing | new cards or data | own=yes - but… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Dragonair (B4 117, B4 175, B4 233) Ability Dragon's Blessing: once per turn, while Dragonair is on the Bench, attach an Energy from your discard pile to your Active [N] (Dragon) Pokemon. Upstream added it as a new Ability mechanic; Draconic Whip is a plain 40…
   DECKS: Dragonair B4 117 x2 is in Dustin deck 11 (11-archaludon-haxorus-dragonair); no panel or brew list has it. Every Pokemon in deck 11 (Duraludon B4a 055, Archaludon B4a 056, Axew, Fraxure, Haxorus, Drat…
   CONFLICT: Nothing to bring in. Pasting upstream's version would REMOVE our Dragon-type check, and our bot's Dragon's Blessing credit logic (fuel_credit.rs) would then disagree with the engine.
   VERIFIER: 
[A4] 344-energy-zone-guard | performance or safety | own=no | decks=no | diff=trivial | rec=take rank=2 conf=CONFIRMED | V=confirmed
   WHAT: Deck::is_valid now rejects a deck whose Energy Zone is Dragon or Colorless (those Energy do not exist) or empty, and get_color panics with a message naming the player and the Energy instead of a bare todo!().
   DECKS: None of the 88 deck files in decks/ (panel, Dustin, brews, drafts, gauntlet) declares Dragon or Colorless Energy, and every real deck file has an explicit Energy: line (deck 11 uses Fighting, Metal; …
   CONFLICT: 3 files, no overlap with our fixes. One check: ours has hidden-information templates where the opponent's Energy list is cleared on purpose (src/observation.rs:60, state/mod.rs:933-936). is_valid mus…
   VERIFIER: The finding stands. These are the changes I would make to it: 1. The list of callers of is_valid is incomplete. It leaves out the strength harness, rl/strength/src/main.rs:120-125 in the full repo (commit 35adace7). load_deck runs Deck::from_file and then assert!(d.is_valid(), "deck {rel} is not a valid 20-card list"). The check would therefore reach our main measurement tool …
[A4] 346a-cheren-jasmine | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Cheren (B3 151, B3 192): next turn all your Watchog and Stoutland take -100 from attacks by the opponent's Pokemon ex. Jasmine (A4 160, A4 200): next turn all your Steelix and Skarmory ex take -50 from attacks by the opponent's Pokemon. Upstream added one 'na…
   DECKS: Cheren B3 151 x1 is in Dustin deck 05 (indeedee-stoutland); Jasmine A4 160 x2 is in deck 07 (skarmory-stall). Both already behave per card text in ours, so taking upstream's code changes nothing. The…
   CONFLICT: None - nothing to take. Upstream's separate enum would just duplicate our more general one.
   VERIFIER: 
[A4] 346b-meganium-primarina-porygonz-mallow | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Four more cards from PR 346: Meganium Bloomshine (80 and heal 20 from each of your Pokemon), Primarina Melodious Healing (Ability: heal 30 from each of your [W] Pokemon), Porygon-Z Buggy Beam (80; the opponent's next generated Energy becomes one of the 8 type…
   DECKS: None of Meganium, Primarina, Porygon-Z (A2 129) or Mallow is in any list (Florges A1a 038 shares Bloomshine's text; also in none). Butterfree A1 007's Ability uses the same heal-all code but the Butt…
   CONFLICT: None. Nothing to take.
   VERIFIER: 
[A4] 347-silcoon-cascoon-cocoon-collector | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Silcoon (B4 002) and Cascoon (B4 004) Cocoon Collector: put 3 random cards from among Silcoon and Cascoon from your deck onto your Bench. Upstream added a multi-name 'search to Bench' helper.
   DECKS: Silcoon and Cascoon (B4) are in no list. The same mechanic serves Tandemaus' Flock (B2 142, in brew-02-arceus-tandemaus-persian). One tiny difference: when the Bench has fewer free slots than cards d…
   CONFLICT: None. If anyone wants the exact upstream sampling it is a 2-line change to draw_count in shared_mutations.rs:317, but it is not needed.
   VERIFIER: 
[A4] 348-eight-optimizer-cards | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Eight cards in PR 348: Coalossal B1 147 Coal Drop (+50 v a [G] Active), Coalossal B3 094 Mountain Crush (flip until tails, mill the opponent's deck per heads), Politoed B3 035 Raid (+50 if it evolved from Poliwhirl this turn; Rare Candy does not count), Pidge…
   DECKS: None of these eight cards is in any list (Arceus ex is in deck 02 and brews 01-03, but Magnezone A2a 055 is not). Maushold's Triple Gnawing in brew-02 is a different, already-supported text.
   CONFLICT: None. Nothing to take; pasting upstream's versions would only swap our mechanic names.
   VERIFIER: 
[A4] 348x-defender-type-bonus-misses-dual-type | rules fix | own=partly | decks=no | diff=trivial | rec=take rank=1 conf=CONFIRMED | V=partly
   WHAT: Found while checking Coal Drop: 'if your opponent's Active is a [X] Pokemon, +N damage' (Coal Drop, Fearow Peck Bugs, Snover Ice Shard, Sealeo Frozen Splash, Mawile Iron Beam Breaker, Hawlucha Justified Press, Red-Hot Headbutt) - upstream counts every type of…
   DECKS: The six attackers and both Urshifu are in no list in inventory.json, so no deck of Dustin's and none of the panel is touched in simulation. It would only matter if a ladder opponent plays an Urshifu …
   CONFLICT: One helper function, plus its multi-type twin if ours has one (ours folds both into the same function, energy_types is a list). It moves a damage number, so a pinned study that includes such attacker…
   VERIFIER: The core claim stands. Upstream counts a Pokémon's Ability-granted type for "if your opponent's Active is a [X] Pokémon" and ours reads only the printed type. Five things in the finding need changing. 1. Only two of the seven attackers can ever differ. The finding lists Coal Drop, Fearow Peck Bugs, Hawlucha, Mawile, Scovillain, Sealeo and Snover. Rapid Strike Urshifu (B3 051) …
[A4] 349-rhyperior-mountain-swing | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Rhyperior (A2 082, A2 169) Mountain Swing: 150 damage, then discard the top 3 cards of your own deck. Upstream gave its 'discard the top card of your deck' mechanic a count.
   DECKS: Rhyperior is in no list.
   CONFLICT: None.
   VERIFIER: 
[A4] 350-zarude-dark-vengeance | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Zarude (B3 114, P-B 060) Dark Vengeance: 40, +80 if any of your [D] Pokemon was Knocked Out by damage from an attack during your opponent's last turn. Upstream generalised the 'Knocked Out last turn' revenge mechanic with an optional Energy-type filter and no…
   DECKS: Zarude is in no list. Other cards on the same 'Knocked Out last turn' flag: Lapras B2b 017 Raging Freeze (draft-A-shark-tempo, draft-A-wallace) - flag semantics are the same in both engines. The Oric…
   CONFLICT: None; ours is already the superset (also handles the Paralysis variants).
   VERIFIER: 
[A4] tests-from-343-350 | bot / refactor / tooling | own=partly | decks=no | diff=easy | rec=take rank=1 conf=PLAUSIBLE | V=partly
   WHAT: Port upstream's tests for these PRs as regression guards for our engine.
   DECKS: Tests only; no game changes.
   CONFLICT: Dragonair's first test uses a Grass Active; with our type gate use a Dragon Active. The Porygon-Z test calls EnergyType::is_selectable, which ours lacks until item 344 is taken.
   VERIFIER: 1) Split the Dragonair item from the other three. Upstream's first Dragonair test puts a Grass Bulbasaur in the Active spot and expects Dragon's Blessing to attach Energy to it. The card text says "Active [N] (Dragon) Pokémon". So that test encodes an upstream rules bug: upstream has no type check at all. Do not port it unchanged. Port a rewritten version with a Dragon Active …
[A5] 351-disruption-attacks | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #351 (danielnobusada, merged Aug 11, merge 53a64067): five coin-flip resource-disruption attacks. Persian Shadow Claw (A1 197, B1 313): heads discards a random card from the opponent's hand. Purrloin Whiny Voice (B2 104, B2 174) and Krookodile Poaching Fan…
   DECKS: Only Tandemaus B2 142 (Flock) is in a list: brew-02-arceus-tandemaus-persian. The Maushold in that brew is B2 143 (Family Beatdown), not the Triple Gnawing card. The Persian in that brew is Team Rock…
   CONFLICT: Nothing to bring in. The patch would not apply as it stands (apply_attack_action.rs and mechanic.rs differ throughout), and ours has an extra guard upstream's new functions lack (state.prevents_attac…
   VERIFIER: 
[A5] 352-nidoqueen-lovestrike | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #352 (danielnobusada, merged Aug 22, merge 88a8b823), first half: Nidoqueen Lovestrike (A1 168, A1 240, A4 225): 80 damage plus 50 more for each Benched Nidoking.
   DECKS: Nidoqueen and Nidoking are in no list.
   CONFLICT: None.
   VERIFIER: 
[A5] 352-kabutops-leech-life | new cards or data | own=yes - but… | decks=no | diff=easy | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: PR #352 second half: Kabutops Leech Life (A1 159, B2 221): 50 damage, then heal this Pokemon by the same amount of damage done. Upstream adds AttackOutcome::damage_with_pre_and_post and measures the defender's HP before and after.
   DECKS: Kabutops is in no list.
   CONFLICT: Taking upstream's function would flip the rule our test pins (overkill heals the full damage) and drop the Heal Block routing. Plain card text ('the same amount of damage you did') supports ours; the…
   VERIFIER: 
[A5] 353-conditional-coin-attacks | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #353 (danielnobusada, merged Aug 14, merge acb94a00): seven coin-flip attacks with conditions. Sandslash (B2 078) and Wugtrio (B2a 026): 3 coins, 30 per heads. Lugia (B2 131): 2 coins, +40 per heads on 80. Alolan Marowak (A3 027, A3 160): 2 coins, 70 per h…
   DECKS: None of Sandslash, Wugtrio, Lugia, Alolan Marowak, Drapion, Bellossom, Ambipom or Lucky Mittens is in any list.
   CONFLICT: None.
   VERIFIER: 
[A5] 354-eelektross-hydrapple-luxray | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #354 (bcollazo, merged Aug 14, merge 146dae1c), attack half: Eelektross B4 058 Energy Crush (20 more per Energy on all the opponent's Pokemon), Hydrapple B4 127 Fickle Beam (2 coins, 100 more if both heads), Luxray B4 053 Revenge Blast (50 more per point t…
   DECKS: Eelektross, Hydrapple and Luxray (these printings) are in no list.
   CONFLICT: None.
   VERIFIER: 
[A5] 354-sylveon-porygon2-abomasnow-mamoswine | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #354, ability half: Sylveon (B3b 030, B3b 073) Soothing Ribbon (heal 30 from 1 of your Pokemon once a turn if it holds a Tool); Porygon2 (A4 136) Buggy Evolution (attach Energy from the Zone to it, a random evolution from the deck evolves it); Abomasnow (A…
   DECKS: Sylveon (this printing), Porygon2, Abomasnow and Mamoswine are in no list.
   CONFLICT: None; ours is the more general version (type-aware Thick Fat, branch-per-card Porygon2).
   VERIFIER: 
[A5] 355-victini-victory-star | new cards or data | own=yes - but… | decks=possibly | diff=hard | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: PR #355 (uahawke, merged Aug 15, merge 25188da0): Victini's Victory Star (B3 025, P-B 049). After a coin-flipping attack of your [R] Active Pokemon, you may keep the result or reroll the whole batch; once per turn per player; Victini can sit on the Bench. Ups…
   DECKS: Victini B3 025 and Mega Houndoom ex P-B 080 are only in decks/brews/drafts_2026-10-01/draft-D-entei-grimhound (a draft, not ranked). The ordinary case (not Confused, no Will, no defender coin) plays …
   CONFLICT: Direct and large: our staged-choice design (new actions KeepAttackCoinResults/RerollAttackCoins, state.pending_attack_coin_choice, victory_star_used_this_turn), the gate-coin and Will rules from rule…
   VERIFIER: 
[A5] 356-coin-damage-status-attacks | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #356 (danielnobusada, merged Aug 19, merge 43ca90cd), coin-flip damage and status attacks: Farigiraf B3a 058 and Dipplin B4 126 (2 coins, 60 per heads); Croagunk A2 107/173 (20 per coin) and Toxicroak A2 108 (40 per coin), one coin per Pokemon you have in …
   DECKS: None of these cards (these printings) is in any list.
   CONFLICT: None.
   VERIFIER: 
[A5] 356-mega-houndoom-grimhound-flare | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #356, one card: Mega Houndoom ex (P-B 080) Grimhound Flare: 3 coins, 80 damage for each heads (the printed 80 is not added on top).
   DECKS: Mega Houndoom ex P-B 080 is the finisher of draft-D-entei-grimhound (one copy; a draft, not ranked). Nothing else lists it.
   CONFLICT: None.
   VERIFIER: 
[A5] 356-xatu-life-drain | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=2 conf=CONFIRMED | V=-
   WHAT: PR #356, one card: Xatu Life Drain (A4 082, A4 174): flip a coin; on heads the opponent's Active Pokemon's remaining HP becomes 10 (0 damage printed).
   DECKS: Xatu A4 082 is in Dustin's deck 10-xatu-oricorio-tr-weezing (2 copies, with Will) and in brew-01-arceus-crobat-xatu and brew-04-xatu-slowking. No other list has Life Drain.
   CONFLICT: None; ours also has video evidence behind the Will and Poison interaction.
   VERIFIER: 
[A5] 356-heal-attacks | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #356, four heal attacks: Azurill (A4a 063, A4a 077) heal 50 from 1 Benched Pokemon; Spritzee (B1a 035) and Smoliv (P-B 034) heal 20 from 1 of your Pokemon; Alomomola (B4 045) heal 10 from each Benched Pokemon; Ho-Oh (B1 032) Blessed Burn heal 30 from each …
   DECKS: None of these cards is in any list.
   CONFLICT: None.
   VERIFIER: 
[A5] 356-energy-discard-and-draw | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #356, Energy-discard attacks plus one draw: Giratina A2a 061 and Rayquaza B4 119 (discard 2 random Energy from itself); Koraidon B2a 063 (discard 2 [F]); Single Strike Urshifu B3 113 (discard 1 [D]); Dedenne B1 094 (discard a [L] from the opponent); Surski…
   DECKS: None of these cards is in any list. The Oricorios in decks 10 and 15 are B4 078 (Supernatural Feather) and A3 066 (Zzzap); Entei ex and Giratina ex in the brews are different cards from Entei A4 033 …
   CONFLICT: None.
   VERIFIER: 
[A5] 351-test-helpers | bot / refactor / tooling | own=not appli… | decks=no | diff=trivial | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: PR #351 also moves the repeated test helpers trainer_from_id and play_trainer into src/test_support.rs.
   DECKS: No cards involved.
   CONFLICT: None.
   VERIFIER: 
[A6] PR359-b4a-card-data | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Adds the 110 cards of the Team Rocket's Ambition set (B4a) to upstream's card list and card-id table.
   DECKS: None: the data is identical in both engines (also established earlier: shared ids equal).
   CONFLICT: None.
   VERIFIER: 
[A6] PR360-raticate-ex-thieving-incisors | mixed | own=yes - but… | decks=possibly | diff=trivial | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: Team Rocket's Raticate ex: when it evolves from your hand you may steal one random Energy from the opponent's Active Pokemon.
   DECKS: Dustin decks 13-a-ninetales-raticate (and the giant-cape / big-malasada variants), 14-comfey-raticate-hypno, 15-jolteon-oricorio-raticate. It only matters when the opponent's Active holds two or more…
   CONFLICT: Taking upstream's version would undo the same principle as our fix 3102c9eb (a random Energy is a chance over the types held, rules09_engine_repairs.md).
   VERIFIER: 
[A6] PR360-weezing-ex-boiler-smog | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Team Rocket's Weezing ex: Boiler Smog (on evolving from hand, you may make the opponent's Active Poisoned and Burned) and Confusion Gas (60 + Confused).
   DECKS: Panel t-weezing; Dustin 10-xatu-oricorio-tr-weezing; brew-04-xatu-slowking. Behaviour is the same in both engines, so nothing changes if we do nothing.
   CONFLICT: None; ours adds a public-information forecast for Boiler Smog that upstream lacks.
   VERIFIER: 
[A6] PR360-slowking-ex | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Team Rocket's Slowking ex: Evil Inspiration (once per turn, while Active, draw a card) and Hand Kinesis (20 damage per card in your hand).
   DECKS: brew-04-xatu-slowking only. Same damage and draw in both.
   CONFLICT: None.
   VERIFIER: 
[A6] PR360-toxtricity-zapdos-moltres-regidrago | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Four more B4a/B2 ex cards: Toxtricity ex (30 to each damaged Benched Pokemon), Team Rocket's Zapdos ex (50 to one damaged Benched Pokemon), Team Rocket's Moltres ex Heat Charged (3 coins, Fire Energy per heads onto itself), Regidrago (-100 damage if itself da…
   DECKS: None of these four cards is in any deck list.
   CONFLICT: None.
   VERIFIER: 
[A6] PR361-goozooka | new cards or data | own=yes - sam… | decks=possibly | diff=trivial | rec=already have rank=1 conf=PLAUSIBLE | V=-
   WHAT: Team Rocket's Goo-zooka: until the end of the opponent's next turn their Active Pokemon's Retreat Cost is 1 more.
   DECKS: Dustin 12-ariados-whimsicott-ogerpon, 14-comfey-raticate-hypno, 15-jolteon-oricorio-raticate; brew-03a, brew-03b. Plain use is identical. The two engines differ only when a retreat discount is bigger…
   CONFLICT: Ours adds Oranguru's Primate's Trap cost the same late way on purpose (hooks/retreat.rs:237 comment).
   VERIFIER: 
[A6] PR361-researcher | new cards or data | own=yes - but… | decks=possibly | diff=trivial | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: Team Rocket's Researcher: flip a coin until tails; for each heads put a random Pokemon with 'Team Rocket' in its name from your deck into your hand.
   DECKS: Dustin 14-comfey-raticate-hypno only. Upstream's cap matters in 1 game in 32 of Researcher plays (5+ heads); its fixed pick shows a search bot which cards it would get.
   CONFLICT: Ours is the better model; upstream's would lose our exact multiset odds and the Will/Luxury Coin handling.
   VERIFIER: 
[A6] PR361-boss-masterplan-thievingmachine-arcade | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Four B4a Trainer cards: Team Rocket's Boss (put any number of the opponent's hand Basics onto their Bench), Master Plan (confuse opponent; coin tails confuses you too), Thieving Machine (random Item from the opponent's discard into your hand), Arcade (Stadium…
   DECKS: Boss: panel t-suicune, brew-02-arceus-tandemaus-persian. Master Plan: brew-05, brew-05b. Arcade: brew-04. Thieving Machine: no list. Same results in both engines.
   CONFLICT: None. Ours is a superset (Will forcing the Master Plan coin, status immunity on both targets, Arcade blocked at a 7-card hand or empty deck).
   VERIFIER: 
[A6] PR362-serperior-tinkaton | mixed | own=yes - sam… | decks=no | diff=trivial | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: Serperior's Regal Bloom (+30 HP per Grass Energy, doubled by Jungle Totem) and Tinkaton's Gigaton Hammer (140, cannot use it next turn); also a note file for the author's coding assistant.
   DECKS: Neither Serperior B4a 005 nor Tinkaton is in any list.
   CONFLICT: None.
   VERIFIER: 
[A6] PR363-inspiring-dance-chubby-cheer | bug fix | own=yes - but… | decks=yes | diff=trivial | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: Oricorio's Inspiring Dance and Happiny's Chubby Cheer: 'During your NEXT turn, attacks used by your Pokemon do +20 damage'. (Meloetta's +30 version was added later the same way.)
   DECKS: Happiny B4a 063 is in Dustin 04-absol-hoopa-darkrai. The Oricorios in Dustin decks 10 and 15 are B4 078 and A3 066 (other attacks), NOT the Inspiring Dance Oricorio B2 022, which is in no list. So on…
   CONFLICT: Taking upstream's version would break our correct timing.
   VERIFIER: 
[A6] PR364-drampa-gougingfire-ragingbolt-walkingwake | mixed | own=yes - but… | decks=no | diff=trivial | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: Drampa Berserk (+50 if one of your Benched Pokemon is damaged) and Dragon Breath (coin: tails does nothing, heads damage + Paralysis); Gouging Fire (discard 2 Energy, then -30 damage next turn); Raging Bolt Baneful Boom (discard all Energy, Knock Out the Acti…
   DECKS: None of Drampa, Gouging Fire, Raging Bolt, Walking Wake is in any list.
   CONFLICT: Upstream's random self-discard would undo our R2/M7 player-choice repair; its Raging Bolt would undo our effect-prevention check.
   VERIFIER: 
[A6] PR368-kingambit-overlords-blade-and-soul-counter | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Kingambit's Overlord's Blade (+40 per time any of your Pokemon was Knocked Out this game) and Hisuian Basculegion's Soul Counter (+50 per point the opponent got last turn).
   DECKS: Kingambit: Dustin 01-kingambit-as-played and 01-muk-glimmora-kingambit-regigigas. Both engines count identically (including self-inflicted and Checkup knockouts), so nothing changes.
   CONFLICT: None; our Kingambit bot pilot (ky3) reads the same counter.
   VERIFIER: 
[A6] PR368-poison-custom-damage | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Toxicroak's Toxic (Poison that hurts 20 at Checkup) and Toxapex's Severe Poison (Poison that hurts 40), plus Salazzle/Houndoom 'Poisoned and Burned'.
   DECKS: Toxapex B3b 047: brew-03a and brew-03b. Same Checkup numbers in both engines (40 + 10 per Nihilego).
   CONFLICT: None.
   VERIFIER: 
[A6] PR368-swift | rules fix | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Swift (Ledian, Staryu B4 032, Starmie B4 033): damage ignores Weakness and every effect on the opponent's Active Pokemon.
   DECKS: Staryu B4 032 and Starmie B4 033 are in brews/drafts_2026-10-01/draft-B-tide-heal. Same behaviour in both.
   CONFLICT: None.
   VERIFIER: 
[A6] PR368-budew-ability-accessors | mixed | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: Budew's Prickly Powder (Defending Pokemon loses all Abilities until it leaves the Active Spot) plus a big clean-up that routes every Ability lookup through new 'in play' accessors.
   DECKS: Budew is in no list and no panel deck uses it. A few raw lookups remain in ours (src/observation.rs:379,435; src/players/public_reply.rs:639-641) but they are bot/forecast code, not rules.
   CONFLICT: None.
   VERIFIER: 
[A6] PR368-targeting-and-spread | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=PLAUSIBLE | V=-
   WHAT: Attacks that hit chosen or several targets: Palafin Jet Punch, Indeedee Zen Shard, Mandibuzz Blindside, Galarian Obstagoon Bass Control (80 to any), Mimikyu Shadow Hit (20 to your own Pokemon), Forretress Enormous Explosion, Archeops Wild Spin.
   DECKS: None in any list. The Galarian Obstagoon in brew-09 is B2 100 (Merciless Strike), not the Bass Control card B4 097.
   CONFLICT: None.
   VERIFIER: 
[A6] PR368-scaling-damage | new cards or data | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=PLAUSIBLE | V=-
   WHAT: Damage that scales with the board: Mewtwo Psychic (per opposing Energy), Tangrowth Grass Knot and Team Rocket's Arbok (per Energy in opposing Retreat Cost), Team Rocket's Persian Dangerous Rogue (per opposing Benched), Leafeon Leaf Blast, Wishiwashi ex School…
   DECKS: Persian B4a 061: brew-02-arceus-tandemaus-persian (same 10 + 40 per Benched). Gyarados A4 045 is in decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt (a ladder panel deck, not in inventory.json). O…
   CONFLICT: None.
   VERIFIER: 
[A6] PR368-retreat-cost-perspective | bug fix | own=yes - but… | decks=no | diff=easy | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: Not a new card but visible through Grass Knot and Shadow Seeker: when an attack looks at the DEFENDER's Retreat Cost, upstream computes it from the ATTACKER's side.
   DECKS: Only Tangrowth A4 005 and Team Rocket's Arbok B4a 039 use it; neither is in any list.
   CONFLICT: None; ours already has the fix.
   VERIFIER: 
[A6] PR368-shuffle-into-deck-and-switch | new cards or data | own=partly | decks=no | diff=easy | rec=take rank=2 conf=CONFIRMED | V=confirmed
   WHAT: Shuffle/switch attacks: Eldegoss Float Up and Dunsparce Bop 'n' Burrow ('may shuffle this Pokemon and ALL attached cards into your deck'), Accelgor Deck and Cover, Liepard Snatch and Flee, Tsareena Kick Down, Purugly Interrupt, Mew/Noctowl hand reveal, Tapu K…
   DECKS: None of Eldegoss, Dunsparce, Accelgor, Liepard, Tsareena, Purugly, Mew, Noctowl, Tapu Koko is in any list.
   CONFLICT: Small change inside our own shuffle code; our Professor Turo action shares apply_shuffle_in_play_pokemon_into_deck (apply_action.rs:1389) and must keep its current behaviour.
   VERIFIER: The core claim holds. For "shuffle ... and all attached cards into your deck", upstream puts the Tool in the deck and ours discards it. Change these parts of the finding: 1. nature: "new cards or data" is wrong. Both engines already register the same card texts (Float Up, Bop 'n' Burrow, Deck and Cover, Snatch and Flee, Kick Down, Interrupt, the hand reveals, Volt Switch). The…
[A6] PR368-energy-attach-move | new cards or data | own=partly | decks=no | diff=medium | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: Energy-handling attacks: Uxie Mind Boost (attach to Mesprit or Azelf), Sableye Jeweled Gift (random basic Energy to a Benched Pokemon), Mesprit Supreme Blast (only with Uxie and Azelf Benched), Delcatty Energy Blender (move any Energy around), Miltank Rolling…
   DECKS: None of Uxie, Sableye, Mesprit, Delcatty, Miltank is in any list.
   CONFLICT: Our bounded Energy Blender is a documented deliberate shortcut (to keep Vaporeon/Delcatty search cheap); upstream's one-at-a-time version would raise the number of choices our bots search.
   VERIFIER: 
[A7] 383-behaviour | rules fix | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #383 (ours, merged Oct 16): Heavy Helmet, Cascoon's Harden, Shinx's Hide and Carracosta's Blocking Shell apply only to damage from attacks (not Poison, Burn or Ability damage like Bad Dreams and Water Shuriken). Question: what of our own repairs (H2, Hide,…
   DECKS: No change to games, because ours already behaves this way. Cards: Heavy Helmet is in Dustin's 01-kingambit-as-played, 01-muk-glimmora-kingambit-regigigas and 03-wailord-indeedee-wall. Cascoon, Shinx …
   CONFLICT: Do NOT take upstream's Helmet code verbatim. After #383 upstream still reads the PRINTED Retreat Cost (`pokemon_card.retreat_cost.len() >= 3`, upstream core.rs:~712) and gives a flat -20. Ours reads …
   VERIFIER: 
[A7] 383-tests | bot / refactor / tooling | own=partly | decks=no | diff=easy | rec=take rank=2 conf=PLAUSIBLE | V=partly
   WHAT: The test file that came with #383 (tests/rules/attack_damage_only_test.rs, 6 tests, 322 lines): Poison, Burn and Bad Dreams go through Helmet, Harden, Hide and Blocking Shell; Greninja's Water Shuriken is not cut by Helmet; Steel Apron and Metal Core Barrier …
   DECKS: Tests only. Nothing in any list changes.
   CONFLICT: None expected: our behaviour is the same or stricter. One thing to watch: the Steel Apron case needs ours' Steel Apron status immunity, which ours has (src/state/mod.rs:1158). If any test fails on ou…
   VERIFIER: 1. The framing is wrong, not the facts. This file is not upstream's own work. It is our PR #383 coming back. Upstream commit 2aa705d3 (2026-09-28) is authored by dacz8976-creator and merged as c3083a3f (2026-10-16). Our engine had the fix first: 53cba79d (2026-09-26) for Hide, Blocking Shell and Harden, and rules H2 for Heavy Helmet (docs_ours/rules09_engine_repairs.md lines 1…
[A7] 400-et-code | bug fix | own=yes - sam… | decks=no | diff=trivial | rec=already have rank=1 conf=CONFIRMED | V=-
   WHAT: PR #400: the player code 'et' (EndTurnPlayer) could never be selected because any code starting with 'e' went to the e<number> branch first. Fix: match exact named codes first. Adds round-trip tests.
   DECKS: Tool/command-line only. No card involved.
   CONFLICT: None. Upstream's list also contains a bare 'x' (external bot); ours has no bare 'x' because 'x<N>' is our own built-in player (see 382-external-bots).
   VERIFIER: 
[A7] 382-replay-viewer | bot / refactor / tooling | own=no | decks=no | diff=medium | rec=test first rank=3 conf=PLAUSIBLE | V=partly
   WHAT: PR #382 part 1: replay recording (one JSON file per game with a full board snapshot at every decision, legal options and the chosen one), a `play` command that plays one game and prints a link, and a web viewer (viewer/ folder: React + PixiJS + GSAP, 41 files…
   DECKS: No rules or card behaviour changes. It only lets Dustin watch a simulated game of any of his decks, for example the bot piloting the Kingambit list.
   CONFLICT: Files differ in ours: main.rs, simulate.rs (ours has results_output, seed_stream), optimize.rs, game.rs (ours hands bots only a PlayerObservation). An in-engine port changes the executable (new hash)…
   VERIFIER: The core claim stands: upstream really has the replay recorder, the play command and the web viewer, and ours has none of those three. Several details need fixing. 1. "Ours has no viewer" is too strong. Ours has the same terminal viewer that upstream had before #382. - It is the `tui` cargo feature and binary: ours Cargo.toml `tui = ["ratatui","crossterm"]` and `[[bin]] tui re…
[A7] 382-external-bots | bot / refactor / tooling | own=partly | decks=no | diff=medium | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: PR #382 part 2: external bots. Player code 'x' plus --bot-a/--bot-b runs any program as a player over stdin/stdout JSON lines; docs/bot-protocol.md; examples/bots/random_bot.py; a later opt-in 'agent_snapshot' mode (from 09e964f, another reader's slice).
   DECKS: No game changes. Only matters if Dustin wanted to write a bot in another language, which his notes say he does not.
   CONFLICT: Would have to be rebuilt around ours' no-peeking observation (the upstream sender builds ViewState::for_player from the full State), and needs a different code letter than 'x'.
   VERIFIER: 
[A7] 391-action-scores | bot / refactor / tooling | own=no | decks=no | diff=medium | rec=skip rank=2 conf=PLAUSIBLE | V=-
   WHAT: PR #391: a player can report one preference value per legal action (Player::last_scores); recorded in replays; the viewer shows them as percentages or bars; external bots may send a 'scores' array; a forced move (only one legal action) no longer carries a sta…
   DECKS: Display only. Nothing in any list changes.
   CONFLICT: Only useful together with the viewer (382-replay-viewer) and only if the pilots (km3, ky3 and the like) are changed to report their root values: real work in expectiminimax_player.rs, and touching pi…
   VERIFIER: 
[A7] 387-viewer-stadium-tools | bot / refactor / tooling | own=not appli… | decks=no | diff=trivial | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: PR #387: viewer only. The stadium card is drawn bench-sized and an attached Tool peeks out below its Pokémon with its name.
   DECKS: Display only.
   CONFLICT: None; comes along automatically with viewer/ if the viewer is copied.
   VERIFIER: 
[A7] 392-forecast-cap | performance or safety | own=yes - but… | decks=possibly | diff=medium | rec=skip rank=1 conf=PLAUSIBLE | V=-
   WHAT: PR #392 part 1: search players see at most 20 branches of any random result (20 samples weighted 1/20 each, seeded by state and action) instead of every branch; actually playing an action still uses the full exact distribution. Aim: speed, because some effect…
   DECKS: Rules and play are unchanged; only the bots' choices could change, and only where a search node has more than 20 outcomes. Cards named in the PR: Gholdengo ex (Spending Rush) is in no list. Ours' sea…
   CONFLICT: Directly conflicts with ours' exact-only rule and with the frozen pilots (km3 as screener, ky3 in build): sampling would add noise, change every pinned bot number and break the exact claims the guard…
   VERIFIER: 
[A7] 392-perf-watch | performance or safety | own=no | decks=no | diff=medium | rec=skip rank=2 conf=PLAUSIBLE | V=-
   WHAT: PR #392 part 2 (on top of #390's perf_watch module, another reader's slice): the opt-in slow/huge-operation watcher groups incidents by cause (the attack, trainer or ability; for move generation the pending choice) and writes at most N example files per cause…
   DECKS: Diagnostic only. No card or deck is affected.
   CONFLICT: Adds three call sites in hot paths (apply, forecast, move generation) that ours has rewritten, and changes the executable hash (not behaviour), so it needs the identity-replay routine.
   VERIFIER: 
[A7] 393-pyo3 | bot / refactor / tooling | own=not appli… | decks=no | diff=easy | rec=not needed rank=1 conf=PLAUSIBLE | V=-
   WHAT: PR #393: upgrade pyo3 from 0.22 to 0.29 in the engine's Python bindings; six pyclass macros get from_py_object; the bindings' `points` getter is widened from [u8;2] to [u32;2] because newer pyo3 turns u8 arrays into bytes. Cargo.lock also moves crossbeam-epoc…
   DECKS: No effect on any game.
   CONFLICT: None for the engine. If rl/pdl_rl_env were ever moved to pyo3 0.29, check any [u8; N] returned to Python (they become bytes) in rl/pdl_rl_env/src/lib.rs; I did not read that file.
   VERIFIER: 
[A7] 275-mcts-rewrite | bot / refactor / tooling | own=not appli… | decks=no | diff=hard | rec=not needed rank=1 conf=CONFIRMED | V=-
   WHAT: Open PR #275 (June): 'Rewrite MctsPlayer with correct MCTS algorithm' (UCB1 selection, backpropagation along the whole path, arena of nodes). The only branch in our clone for it, origin/claude/mcts-player-plan-hvAZ6 (one commit 38e34810), adds a NEW player Ne…
   DECKS: No card involved. No bot Dustin uses.
   CONFLICT: The new player needs the whole hidden State, which ours' no-peeking boundary forbids; it would have to be redone on observations. Also open PR #401 touches the old MCTS file.
   VERIFIER: 
[A7] 249-reorganize-tests | bot / refactor / tooling | own=not appli… | decks=no | diff=hard | rec=not needed rank=1 conf=PLAUSIBLE | V=-
   WHAT: Open PR #249 (April): move the test files into groups (engine, mechanics, cards, regressions) with shared fixtures; a second commit 868652c0 removes the test-utils feature.
   DECKS: Tests only.
   CONFLICT: Would conflict with nearly every test path in ours and with our pin documents that cite test file names.
   VERIFIER: 
[A7] 123-filename-collision | bot / refactor / tooling | own=no | decks=no | diff=trivial | rec=not needed rank=1 conf=PLAUSIBLE | V=-
   WHAT: Open PR #123 (Nov 2025, from a contributor): fix a Windows warning where the library and the command-line program are both named 'deckgym' and their debug-symbol (.pdb) files collide (issue #122).
   DECKS: Build-system warning only.
   CONFLICT: Would rename the binary, which our scripts call by name (`deckgym`).
   VERIFIER: 
[A7] non-engine-misc | bot / refactor / tooling | own=yes - sam… | decks=no | diff=trivial | rec=skip rank=1 conf=CONFIRMED | V=-
   WHAT: Everything else outside src/ and tests/ that changed upstream since Jul 30: README (new replay-viewer and external-bot sections; card-count badge 3,340 of 3,761 vs ours 3,315), .gitignore (replays/, viewer/node_modules, viewer/dist), .claude/skills/implement-…
   DECKS: None of these touches rules, cards or bots.
   CONFLICT: Taking upstream's SKILL.md alone would mislead card-writing agents, because it assumes the effect-text Trainer keying (#395) that ours lacks. The crossbeam-epoch bump is a harmless lockfile change bu…
   VERIFIER: 
```

# kx3 against km3 on Dustin's positions: before and after (Oct 4)

Written for Dustin. The five-minute version is everything down to "Still open"; the twelve examples are in detail after that. Every example claim comes from `EXAMPLES_SOURCE.md` in this folder, in its checked wording (each example was re-checked against the raw files, and none passed exactly as first written). The strength-run figures come from its `REPORT.md`. Nothing beyond those is added.

**Tied to these builds**
- **The positions:** kx3 from `claude/playout-pilot` b96296a5 (fix round 2), REALISTIC knowledge, the computer's deck added to its opponent pool (`extra:BL`), seeds 1-3 for each of the 152 development positions (7,900 s on the laptop, Oct 4). km3 from the same build replays the official 240 games field for field.
- **The strength run:** build d513e37b. Its kx3 self-check digest is `31d638dbc818b0fa`, the same as b96296a5's. Report: `rl/results/strength_2026-10-03_kx3_dev/REPORT.md`.

**Terms.** km3 is the pilot used so far. kx3 starts from km3's move, then plays every legal move (up to 12) out 16 times to the end of the game with km3 on both sides, and switches away from km3's move only if another move leads by at least 2 standard errors (how far chance alone could move the lead). A play-out scores win 1, tie ½, loss 0, so a lead of 0.0625 is one more win in 16. "Seeds 1-3" are three different deals of the unseen cards. "Auto" is the game's own auto-play, which played his side in some recordings. "Exact list" means both decks were known, so the position can carry a verdict.

## The short answer

1. **In full games kx3 is clearly stronger.** Strength run: +16.6 ± 3.5 points over km3 across 560 paired games on 7 development decks, every deck positive. Two things come with it. kx3 takes about 270 s per game, km3 about 1 s. And the run's own caveat: the 8 opponent lists are also the lists kx3 guesses from, so once a few cards are seen its guess narrows to the right one; against a deck outside that pool it would not.
2. **The positions mostly do not show that gain.** kx3 changed km3's move on 43 of 1,292 decisions (3%; 45 of 1,355 with the forced replays). In about half the decisions km3's move already wins all 16 play-outs: 96 of 176 on Dustin's three 3-0 games (kx3 changed one), 197 of 411 on the computer-deck positions.
3. **One strong improvement:** B-210952-t18 (3.1 to 5.0 standard errors in all 3 seeds). The other three improvements are either just past the bar (2.1 to 2.2 standard errors) or on an approximate list.
4. **The failures have four causes:**
   - *Everything wins:* when every move wins all 16 play-outs, kx3 sees no difference and keeps km3's move.
   - *km3's later moves leak into the play-outs:* km3 plays the rest, so a later km3 mistake (Copycat, the Cape) drags down every move except ones that end the turn. The most likely cause; the play-outs are not logged, so it is not shown directly.
   - *Switches to "end the turn":* 9 of the 43 switches. On 7 of them km3, on the same deal, goes on to attack and kx3's turn has no attack.
   - *Best-of-many noise:* the rule takes the best of up to 12 noisy scores. 21 of the 43 switches sit between 2.0 and 2.5 standard errors (median 2.5), so some are probably chance.
5. **Coordinated plans (item 4 of the Oct 2 approval, `planning_pilot_design_2026-10-02/DESIGN.md` section 9): signs of hiding, none of seeing.** Below.
6. **Turbo Shark line rate: inconclusive** (40.0% to 42.5%). Below.

**Agreement with the recorded player is not strength.** Against Dustin (26 exact-list positions) kx3 and km3 are almost the same: first action matches on all 3 seeds in 16 positions for kx3, 16 for km3; whole plan 12 each. Only one seed differs: B-215203-t02 seed 2, where kx3 played Misty as he did. Against Auto (31 positions) kx3 matches a little less than km3 (first action: 10 positions against 14). Of the 24 changes kx3 made on exact-list positions, 18 could be compared with the recorded choice: 2 moved toward it, 11 away, 5 to a third move; 6 could not be compared. All 11 "away" changes are in one game, 210952, the one Auto lost (18 of the 24 changes are there).

## The twelve positions at a glance

| milestone | position (whose game) | what kx3 did that km3 did not | verdict |
|---|---|---|---|
| preparing an attacker | B-210952-t18 (Auto) | Misty first, Binding Snow on the Blastoise, instead of Cyrus | **better** (3 of 3 seeds) |
| | B-210952-t14 (Auto) | retreat, then end the turn with no attack | **looks worse**; its own play-outs disagree |
| | B-215203-t06 (Dustin) | nothing | can't tell |
| | B-215825-t06 (Dustin) | nothing | can't tell |
| | B-214254-t06 (Dustin) | nothing | can't tell |
| managing a sacrifice | B-214254-t10 (Dustin) | nothing in 14 decisions | can't tell |
| | B-205731-t10 (Auto) | kept Copycat; attacked without attaching Energy | **looks worse** in those two seeds |
| | B-205731-t08 (Auto) | nothing | can't tell |
| adapting when the plan fails | B-210952-t16 (Auto) | Binding Snow at once, dropping the rebuild | **worse** in seeds 1-2 |
| recognising an immediate win | none chosen | the two pilots are the same here | no change |
| no milestone | B-205731-t02 (Auto) | one seed ends the turn, one plays Auto's turn | **mixed** |
| | B-215203-t02 (Dustin) | Misty, aimed at the other Pokémon, in 1 seed of 3 | can't tell (weak) |
| | LR-200654-t06 (Dustin, approximate list) | Hyper Ray where km3 passes | no verdict |

Tally: 1 better, 3 worse or looks worse, 1 mixed, 6 can't tell, 1 no verdict. B-205731-t10, B-205731-t08 and B-210952-t16 are also tagged "preparing an attacker"; each is listed once, under its other milestone. All but the last row are exact-list positions.

## Coordinated plans: signs of hiding, none of seeing

The question (item 4 of the Oct 2 approval): can kx3's play-outs see the value of a plan that spans turns, such as charging a benched attacker while a damaged Pokémon stays in front, then promoting at the right time?
- **Seeing: none.** In no computer-deck position did the first step of Dustin's or Auto's multi-turn plan score clearly above km3's move.
- **Plan steps that differ from km3 usually score level**, often with the same result in all 16 play-outs: the Water on the benched Vulpix, Turbo Shark's Water to the Vulpix, the damaged Mega kept in front.
- **Hiding, clearest inside one turn (B-210952-t16).** The play-outs score "bench the Vulpix" 0 of 16 in every seed, with km3 finishing the turn (the Cape on the Active, the Water on the new Vulpix). In seed 3, where kx3 changed those finishing moves itself, the rebuild scored 0.44 to 0.69. Those numbers are from different seeds and decisions, so not a paired comparison. Three weaker cases look the same (B-205731-t02, B-205731-t10, D3-022135-t07), so this is the clearest case, not the only one.
- **Across several turns**, hiding cannot be told apart from two other explanations: the step truly matters little (Turbo Shark keeps feeding the Vulpix anyway), or the game is already decided.
- *The reader's suggestion, not checked:* positions where the game is in doubt, and a check that plays the candidate move followed by the human's line, or by kx3, on the next turn instead of km3.

## The Turbo Shark line rate: inconclusive

In the strength run, on draft A (shark tempo), "Turbo Shark used (arming a Benched Pokémon) by own turn 3" happened in 42.5% of games with kx3 and 40.0% with km3: +2.5 ± 7.0 points. The interval is far wider than the difference: no sign that kx3 gets the Shark going sooner, and none that it does not.

## Still open

The kx3 v k3 exploit check is running (`rl/results/strength_2026-10-04_kx3_v_k3`, about 12 hours). kx3's play-outs have km3 on both sides, so against km3 its model of the opponent is exact. Here the opponent is k3, a different pilot, on the first 3 of the same deals. The pre-registered reading is kx3 minus km3, each against k3, per deal. If the gain against k3 is near +16.6, kx3's edge is not just exploiting km3; if much smaller, part of it was.

---

# The twelve examples in detail

Development positions only. Full checked wording, trace numbers and what each check corrected: `EXAMPLES_SOURCE.md`.

## Preparing an attacker
First action matches the recorded player on all 3 seeds: Auto 24 positions, kx3 8 and km3 12; Dustin 16 positions, 12 for both.

**B-210952-t18 (Auto's game, lost 2-3): better.**
- *Position.* Turn 18, score 1-1, one card left in his deck. His Active Alolan Ninetales ex has 20 HP left, with two Mega Sharpedo ex and a Vulpix on the Bench. The computer's Mega Blastoise ex is Active (170 of 230 HP, 5 Water) with a 20-HP Baxcalibur on its Bench. With a 6th Water, Triple Bombardment also does 50 to two Benched Pokémon, which would finish the damaged Ninetales ex even from the Bench.
- *Auto.* Evolved the Vulpix, Cyrus pulled in the Baxcalibur, retreated, Turbo Shark knocked it out (2-1). The computer promoted the Blastoise at once, attached a 6th Water on turn 19, and Triple Bombardment knocked out the old Ninetales ex. Lost 2-3.
- *km3 (12 of 12 seeds).* The same Cyrus line, finishing with Binding Snow on Baxcalibur. Binding Snow's lock (no Zone Energy to the computer's Active next turn) still applies, but covers whatever the computer promotes.
- *kx3 (3 of 3 seeds).* Misty first, instead of Cyrus, then Binding Snow (80) on the Active Blastoise. No point this turn, but the Blastoise stays Active under the lock: it cannot take Energy from the Zone or from Baxcalibur's Ice Maker next turn, stays at 5 Water, and Triple Bombardment does no Bench damage. Leads +0.22 to +0.31 (3.1, 5.0 and 3.4 standard errors). Seeds 2 and 3 retreat into the Vulpix before evolving it; the Misty-then-Binding-Snow core is the same.
- *Not shown.* That km3's line would have lost the real game: the computer promoted the Blastoise after the knockout, so km3's Binding Snow would have locked it too. Misty itself adds little (its target made no difference, and Irida, also a Supporter, won 0 of 16). The gain is measured only in kx3's play-outs, where km3 plays the computer; kx3's own line wins only 34-50% of them, and the lock lasts one turn.

**B-210952-t14 (Auto's game): looks worse; untested.**
- *Position.* Turn 14, 0-0. Lapras Active (110 HP, 3 Water); Mega Sharpedo ex and Ninetales ex on the Bench. The computer's Active is a Wailmer (50 HP, 1 Water) that cannot retreat this turn.
- *Auto and km3 (12 of 12).* Bench Carvanha, Water on it, Surf knocks out the Wailmer (first point); km3 adds the Cape on the Ninetales ex. In the real game the computer then sent in the Blastoise and Triple Bombardment knocked out Lapras.
- *kx3 (3 of 3).* Retreat Lapras into the Ninetales ex (discarding 2 Water) and end the turn: no attack, no Energy, no bench.
- *Why.* km3's own move won none of its 16 play-outs in any seed. The retreat beat it by 0.25 to 0.28, then ending the turn beat "bench Carvanha" by 0.16 to 0.22. kx3's scores here are only about 4 to 7 of 16, and no move scored above 7.
- *Verdict.* By the card texts there looks to be a better line: the same retreat, then Water and Binding Snow (80), which knocks out the Wailmer and blocks Zone Energy to the computer's Active next turn; the Ninetales ex (150 HP) would survive Triple Bombardment where Lapras did not. kx3's own play-outs rate it lower, and nothing here tests who is right. One possible cause, not checked: km3, playing the computer, may misplay the Wailmer. 6 of the 24 exact-list switches are in this position.

**B-215203-t06 (Dustin, won 3-0): can't tell.** Turn 6, he leads 1-0. He evolved the Vulpix, retreated Lapras into Mega Sharpedo ex (discarding 2 of its 3 Water), Water on it, Turbo Shark (Wailord 250 to 180). km3 (12 of 12) and kx3 (3 of 3): Water on the Sharpedo, Surf with Lapras, the Vulpix stays a Basic. kx3 changed nothing: the moves tested (evolving, Surf, each Water, ending the turn, his retreat) all won 16 of 16. His line's Turbo Shark Water let the Ninetales ex use Binding Snow on turn 8 (after km3's Surf, turn 10 at the earliest); that comes from Turbo Shark, not from evolving early. In games this one-sided, an edge like this can stay hidden from kx3.

**B-215825-t06 (Dustin, won 3-0): can't tell.** Turn 6, 0-0; Cyrus has no target. He put the Water on the Vulpix, played Misty (the next board shows one Water on each, so one heads) and used Binding Snow. km3 (12 of 12) and kx3 (3 of 3): Water on the Sharpedo, Binding Snow, no Misty (km3 scores it 1 point below ending the turn). Nearly every move won 14 to 16 of 16, and Misty's best lead was one play-out. A line doing both was legal. kx3 leaves a Supporter unused (it costs only the card). His exact order is not shown to be better, and Misty gives Water only on heads.

**B-214254-t06 (Dustin, won 3-0): can't tell.** Turn 6, 0-0. He put the turn's Water on the benched Vulpix, then Turbo Shark. km3 and kx3 attack at once, so the turn's Water is never attached (unattached Energy is discarded). Water-first and attacking tied in kx3's play-outs (0.938 v 0.938, 0.750 v 0.750, 0.750 v 0.688). On the 57 computer-deck positions km3 attacked with the turn's Water unused at 48 decisions: every Water option tied exactly in 38, one led within the noise in 3, level or behind in 7, none past 2 standard errors. In this game the extra Water was never needed, so kx3 copying km3's habit cost nothing.

## Managing a sacrifice
First action matches on all 3 seeds: Auto 3 positions, 1 for kx3 and 1 for km3; Dustin 3 positions, 2 for both.

**B-214254-t10 (Dustin, won 3-0): can't tell (about equal in the play-outs).**
- *Position.* His turn 5, he leads 1-0. Active: Cape Mega Sharpedo ex at 120 of 220 HP, 1 Water. Bench: a fresh Mega Sharpedo ex (2 Water) and a Vulpix with 4 Water. The computer's Wailord ex (4 Water) hits for 100 a turn; Soothing Shore is in play.
- *Dustin.* Kept the damaged Mega in front and healed it (Lucky Ice Pop twice, Irida), Water on it, Turbo Shark, its Water to the Vulpix. Next turn: evolve the Vulpix, free retreat, Binding Snow. Won 3-0 without losing a Pokémon.
- *km3 and kx3.* The same line in 12 of 12 and 3 of 3 (Irida first, then the Pops; both orders end at 200 HP). kx3 changed nothing at any of its 14 decisions.
- *Why.* Turbo Shark's Water to the Vulpix or to the other Mega scored exactly the same in all 3 seeds. Retreating for free into the fresh Mega was offered 11 times and never differed by 2 standard errors; retreating into the 60-HP Vulpix scored -0.50 to -0.84; ending the turn early scored more than 2 standard errors below at 5 of 11 offers. The play-outs saw no difference, but they play km3 on both sides, so a real difference could be unseen. km3's moves scored about 0.70 on average (0.47 to 0.94), so the game leaned his way.

**B-205731-t10 (Auto's game, won 3-2): looks worse in two seeds.**
- *Position.* Turn 10, he leads 1-0. Active Mega Sharpedo ex at 50 of 190 HP: if it falls, the computer gets 3 points and the game. Bench: Ninetales ex. Hand: Copycat, Ninetales ex, Misty, Vulpix. The computer holds 1 card.
- *Auto.* Bench the Vulpix, Water on it, free retreat into the Ninetales ex, Binding Snow. No Copycat.
- *km3 (12 seeds).* Retreat, bench, Water, then Binding Snow (7) or Copycat (5; the record stops at Copycat's draw).
- *kx3.* Seed 3 plays km3's line, then Copycat (the lead for Binding Snow was 1.8 standard errors, under the bar). Seed 1 benches and uses Binding Snow without attaching any Energy, so the turn's Energy is discarded (2.2 standard errors). Seed 2 puts Water on the Sharpedo just before retreating and plays Misty.
- *Verdict.* By the cards, Copycat here trades the Ninetales ex and Misty for one random card, and skipping the attachment loses the Energy. That covers only those two lines; nothing compares Auto's line with seed 2. The probable cause (not recorded): some Water play-outs go on into km3's Copycat, as km3 did in 5 of its own 12 seeds.

**B-205731-t08 (Auto's game, won 3-2): can't tell.** Turn 8, he leads 1-0. His damaged Mega Sharpedo ex (100 of 190 HP) stayed in front: evolve on the Bench, Ice Pop and Irida, Water, Turbo Shark. km3 (12 of 12) and kx3 (3 of 3): retreat into the Vulpix, Irida, evolve it in the Active Spot, Binding Snow, no Energy. Every move except Copycat won 16 of 16 at the first decision, even ending the turn; later decisions were not all ties. kx3 scores only the first move with km3 playing on, so Auto's whole line was never played out. The real game was closer (3-2). On the computer-deck positions, every move scored the same at 108 of 411 kx3 decisions.

## Adapting when the plan fails
First action matches on all 3 seeds: Auto 2 positions, 0 for kx3 and 1 for km3. Dustin has none.

**B-210952-t16 (Auto's game, lost 2-3): worse in seeds 1 and 2.**
- *Position.* Turn 16, 1-1. Lapras, his attacker, was knocked out last turn. Active Ninetales ex (150 HP, 2 Water); Carvanha and Mega Sharpedo ex on the Bench. The computer's Blastoise (5 Water) is Active.
- *Auto.* Rebuilt: bench the Vulpix, evolve Carvanha into Mega Sharpedo ex, Water on the Vulpix, Binding Snow. On turn 18 that Vulpix became a fresh Ninetales ex. *km3 (12 of 12):* the same plus the Cape on the Active Ninetales ex.
- *kx3.* Seeds 1 and 2: Binding Snow at once, with nothing benched, nothing evolved and the Water unused. Seed 3: the rebuild, with the Water on the Active Ninetales ex and the Cape on the Sharpedo it had just evolved.
- *Why.* Benching the Vulpix lost all 16 play-outs in every seed, and so did 8 of the 11 other first moves. Working back from the scores, Binding Snow at once won none of its 16 either: 6 ties (seed 1, 3.0 standard errors) and 4 ties (seed 2, 2.2), most likely games that hit the 30-turn limit. So kx3 switched to a move that won none, in a position the play-outs rate as nearly lost.
- *Verdict.* Worse in seeds 1-2: the switches rest on a handful of ties, not on a plan. In seed 3 the Cape on the new Sharpedo scored 0.688 against 0.125 (4.4 standard errors), but the same Cape on the other, identical Sharpedo scored 0.000, so that gain reflects how km3 plays on, not the Cape. Auto's own finish was never played out.

## Recognising an immediate win
No example was chosen. In the tables the two pilots are the same: Auto 3 positions, first action on all 3 seeds in 1 for both; Dustin 3 positions, 3 for both.

## No milestone

**B-205731-t02 (Auto's game, won 3-2): mixed, a hint and no more.**
- *Position.* Turn 2, he went second. Only Pokémon: a Carvanha (50 HP, no Energy). Hand: Mega Sharpedo ex, Lucky Ice Pop, Irida, Ninetales ex, Copycat. The computer's Meowth is Active and it holds 3 cards. Nothing can evolve on a first turn.
- *Auto.* Water on the Carvanha, then Sharp Fang (30). Kept the Sharpedo in hand and evolved it on turn 4.
- *km3 (12 seeds).* First action Water (7) or Copycat (5). Copycat here shuffles his other 4 cards, including the Mega Sharpedo ex he needs, back into the deck and draws 3.
- *kx3 (3 seeds; on the same seeds km3 alone matched Auto's plan in none).* Seed 1 kept Copycat (ending the turn led by only +0.06). Seed 2 ended the turn at once: no Water, no attack (2.2 standard errors); that is the failure. Seed 3 played km3's Water, then switched Copycat to Sharp Fang (2.1 standard errors): exactly Auto's turn.
- *Verdict.* One seed better, one worse, one unchanged. The likely cause of seed 2 (not shown directly): after Water, km3 usually plays Copycat in the play-outs (6 of its 7 Water seeds), so Water scores about the same as Copycat, and ending the turn is the one first move that stops Copycat this turn. kx3 scores one move at a time, so it cannot score "Water, then Sharp Fang" as a single choice.

**B-215203-t02 (Dustin, won 3-0): can't tell (weak).** Turn 2, he went second. Active Lapras (no Energy, Surf needs 3); Carvanha benched. Hand: Misty, Lucky Ice Pop, Ninetales ex, Copycat. He played Misty on Lapras (one heads) and Water on Lapras, no attack; on turn 4 Lapras had 2 Water, he attached a third and Surf knocked out Meowth for his first point, and he played Copycat that turn. km3 never plays Misty: Copycat in all 12 seeds. kx3, seed 2 only: Misty aimed at the Carvanha, then Water on Lapras (Misty 1.000 v Copycat 0.750; 2.2 standard errors). Seeds 1 and 3 played km3's moves. One seed of three, just past the bar, and a different Misty target: in kx3's line Lapras would have had only 2 Water on turn 4 and could not Surf then. The play-outs model the computer as km3.

**LR-200654-t06 (Dustin's ladder game, approximate list): no verdict.** His list was rebuilt from recordings (18 of 20 cards seen), so this is outside every verdict. Turn 6, his Hydreigon deck against an Arceus ex deck. He evolved Zweilous into Hydreigon and attacked with Tackle from the Zigzagoon. km3 (12 of 12) sets Hydreigon up with Roar in Unison and ends the turn without attacking. kx3 (3 of 3) makes the same set-up, then Hyper Ray (130), Arceus ex 140 to 10. Its play-outs rated the attack above km3's pass in all 3 seeds, by 2.1 to 3.9 standard errors. They used the closest list in the pool, a Darkness Hydreigon / Mega Absol ex deck, nothing like the real opponent. Roar in Unison costs HP (30 each reload), which mattered in the real game: after his turn-8 Roar Hydreigon was on 120, and turn 9's Ultimate Force (130) knocked it out.

## Caveats that apply to every example
- Held-out positions were not run. kx3 ran 3 seeds per position and km3 ran 12; the runner's report prints "/12" by habit, so read kx3's counts as out of 3.
- The computer's exact list was used in the play-outs on the exact-list (B-) positions; on the others the play-outs used meta lists, so those groups are descriptive only.
- The runner plays the first action and the plan up to the first draw card; nothing after that card is compared.

# The play-out pilot kx3 on Dustin's positions: tables, examples and the coordinated-plan check (Oct 4)

Source material for the before/after write-up (Sonnet). Not the write-up itself.

- **Build:** the position runner built from claude/playout-pilot b96296a5 (fix round 2), REALISTIC knowledge with the fixed computer deck added to the pool as `extra:BL` (`KX_EXTRA_LISTS`; FNV-1a `c201ee74320ac6b9`, checked against 33 lists under decks/brews and decks/dustin).
  - b96296a5's kx3 self-check digest equals that of d513e37b, the build of the development strength run (`31d638dbc818b0fa`).
  - km3 from b96296a5 replays the official 240 games field for field; the suite is 2,042/0.
- **Run:** all 152 development positions, seeds 1-3 (not 12; the runner's report prints '/12' by habit), 7,900 s on the laptop, Oct 4 01:19-04:34 UTC. Outputs are copied here under `runs_kx3_trace/` and `report_kx3_trace/`.
- **Analysis:** three readers (tables, examples, coordinated plan), then one adversarial check per example against the raw files. No example passed exactly as first written; each is given below in its CHECKED, corrected wording, with the checker's corrections listed. Scripts: `analysis_scripts/`.

## Agreement tables

## 1. Exact lists: draft A v the computer deck (B- positions, development set). Agreement with the decision maker

Cells read as "all 3 / some / none" for kx and for km3 on the same 3 seeds. km3 over its 12 seeds is "agree / split / differ": agree means at least 10 of 12 seeds, as AGREEMENT_TABLES.md counts. A position with several milestones is counted under each.

### Decision maker: Auto (31 positions, 4 games)

| situation | positions | kx first action (3 seeds) | km3 first action (12 seeds) | km3 first action (same 3 seeds) | kx whole plan (3 seeds) | km3 whole plan (12 seeds) | km3 whole plan (same 3 seeds) |
|---|---|---|---|---|---|---|---|
| all positions | 31 | 10 / 4 / 17 | 14 / 1 / 16 | 14 / 2 / 15 | 4 / 2 / 25 | 4 / 0 / 27 | 4 / 1 / 26 |
| preparing an attacker | 24 | 8 / 2 / 14 | 12 / 0 / 12 | 12 / 0 / 12 | 2 / 0 / 22 | 2 / 0 / 22 | 2 / 0 / 22 |
| managing a sacrifice | 3 | 1 / 0 / 2 | 1 / 0 / 2 | 1 / 0 / 2 | 0 / 0 / 3 | 0 / 0 / 3 | 0 / 0 / 3 |
| adapting when the plan fails | 2 | 0 / 1 / 1 | 1 / 0 / 1 | 1 / 0 / 1 | 0 / 0 / 2 | 0 / 0 / 2 | 0 / 0 / 2 |
| recognising an immediate win | 3 | 1 / 0 / 2 | 1 / 0 / 2 | 1 / 0 / 2 | 1 / 0 / 2 | 1 / 0 / 2 | 1 / 0 / 2 |
| no milestone | 6 | 1 / 2 / 3 | 1 / 1 / 4 | 1 / 2 / 3 | 1 / 2 / 3 | 1 / 0 / 5 | 1 / 1 / 4 |

Seed by seed on the same deals (93 position-seeds), first action matches Auto: both pilots 35, kx only 0, km3 only 10, neither 48. Whole plan: both 14, kx only 1, km3 only 0, neither 78.

### Decision maker: Dustin (26 positions, 3 games)

| situation | positions | kx first action (3 seeds) | km3 first action (12 seeds) | km3 first action (same 3 seeds) | kx whole plan (3 seeds) | km3 whole plan (12 seeds) | km3 whole plan (same 3 seeds) |
|---|---|---|---|---|---|---|---|
| all positions | 26 | 16 / 2 / 8 | 16 / 1 / 9 | 16 / 1 / 9 | 12 / 1 / 13 | 12 / 1 / 13 | 12 / 1 / 13 |
| preparing an attacker | 16 | 12 / 0 / 4 | 12 / 0 / 4 | 12 / 0 / 4 | 8 / 0 / 8 | 8 / 0 / 8 | 8 / 0 / 8 |
| managing a sacrifice | 3 | 2 / 0 / 1 | 2 / 0 / 1 | 2 / 0 / 1 | 2 / 0 / 1 | 2 / 0 / 1 | 2 / 0 / 1 |
| adapting when the plan fails | 0 | - | - | - | - | - | - |
| recognising an immediate win | 3 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 | 3 / 0 / 0 |
| no milestone | 5 | 0 / 2 / 3 | 0 / 1 / 4 | 0 / 1 / 4 | 0 / 1 / 4 | 0 / 1 / 4 | 0 / 1 / 4 |

Seed by seed (78 position-seeds), first action matches Dustin: both 49, kx only 1, km3 only 0, neither 28. Whole plan: both 37, kx only 0, km3 only 0, neither 41.

## 2. Descriptive only (the opponent's real list was not given to kx)

LR- was not asked for. It is added for completeness and uses a reconstructed list for his own deck.

| group: situation | positions | kx first action (3 seeds) | km3 first action (12 seeds) | km3 first action (same 3 seeds) | kx whole plan (3 seeds) | km3 whole plan (12 seeds) | km3 whole plan (same 3 seeds) |
|---|---|---|---|---|---|---|---|
| A- (draft A v humans): all positions | 29 | 11 / 6 / 12 | 11 / 6 / 12 | 11 / 6 / 12 | 5 / 6 / 18 | 5 / 6 / 18 | 5 / 6 / 18 |
| A-: preparing an attacker | 17 | 8 / 1 / 8 | 8 / 1 / 8 | 8 / 1 / 8 | 4 / 1 / 12 | 4 / 1 / 12 | 4 / 1 / 12 |
| A-: managing a sacrifice | 9 | 2 / 0 / 7 | 2 / 0 / 7 | 2 / 0 / 7 | 0 / 0 / 9 | 0 / 0 / 9 | 0 / 0 / 9 |
| A-: adapting when the plan fails | 2 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 | 0 / 0 / 2 | 0 / 0 / 2 | 0 / 0 / 2 |
| A-: recognising an immediate win | 2 | 2 / 0 / 0 | 2 / 0 / 0 | 2 / 0 / 0 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 |
| A-: no milestone | 7 | 0 / 5 / 2 | 0 / 5 / 2 | 0 / 5 / 2 | 0 / 5 / 2 | 0 / 5 / 2 | 0 / 5 / 2 |
| D3- (deck 03): all positions | 27 | 16 / 3 / 8 | 19 / 1 / 7 | 19 / 0 / 8 | 7 / 3 / 17 | 10 / 0 / 17 | 10 / 0 / 17 |
| D3-: preparing an attacker | 13 | 10 / 1 / 2 | 11 / 0 / 2 | 11 / 0 / 2 | 6 / 1 / 6 | 7 / 0 / 6 | 7 / 0 / 6 |
| D3-: managing a sacrifice | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| D3-: adapting when the plan fails | 2 | 1 / 0 / 1 | 1 / 0 / 1 | 1 / 0 / 1 | 0 / 0 / 2 | 0 / 0 / 2 | 0 / 0 / 2 |
| D3-: no milestone | 11 | 4 / 2 / 5 | 6 / 1 / 4 | 6 / 0 / 5 | 1 / 2 / 8 | 3 / 0 / 8 | 3 / 0 / 8 |
| L8- (brew 8): all positions | 10 | 6 / 3 / 1 | 6 / 3 / 1 | 6 / 3 / 1 | 1 / 2 / 7 | 1 / 3 / 6 | 1 / 2 / 7 |
| L8-: preparing an attacker | 5 | 3 / 1 / 1 | 3 / 1 / 1 | 3 / 1 / 1 | 0 / 1 / 4 | 0 / 1 / 4 | 0 / 1 / 4 |
| L8-: managing a sacrifice | 1 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 | 0 / 1 / 0 |
| L8-: recognising an immediate win | 1 | 1 / 0 / 0 | 1 / 0 / 0 | 1 / 0 / 0 | 0 / 0 / 1 | 0 / 0 / 1 | 0 / 0 / 1 |
| L8-: no milestone | 4 | 2 / 2 / 0 | 2 / 2 / 0 | 2 / 2 / 0 | 1 / 1 / 2 | 1 / 2 / 1 | 1 / 1 / 2 |
| LR- (reconstructed list): all positions | 29 | 13 / 2 / 14 | 12 / 3 / 14 | 13 / 2 / 14 | 7 / 3 / 19 | 6 / 4 / 19 | 7 / 3 / 19 |

Seed by seed, first action matches his:
- A-: both 42, kx only 0, km3 only 0, neither 45
- D3-: both 53, kx only 0, km3 only 4, neither 24
- L8-: both 23, kx only 0, km3 only 0, neither 7
- LR-: both 42, kx only 0, km3 only 0, neither 45

## 3. Every kx decision traced

These are the free runs: kx playing its own turn up to the first draw card. Only steps with 2 or more legal moves are traced.

| kind of decision (km3's proposed move) | decisions | kx changed km3's move | kept: km3's move scored best | kept: another move led, within the noise |
|---|---|---|---|---|
| Supporter/Item play | 395 | 11 | 273 | 111 |
| attach Energy | 232 | 4 | 187 | 41 |
| retreat/promote | 80 | 2 | 56 | 22 |
| attack | 189 | 0 | 162 | 27 |
| evolve | 127 | 8 | 95 | 24 |
| ability | 99 | 2 | 80 | 17 |
| end turn | 29 | 3 | 23 | 3 |
| other | 141 | 13 | 95 | 33 |
| all | 1292 | 43 | 971 | 278 |

"other" holds: bench a Basic Pokémon 96, which Pokémon gets the Tool 18, use the Stadium 9, which Pokémon to heal 6, Misty's target 5, Luxury coin re-flip choices 7.

The forced replays (kx asked along his recorded line in 5 A- positions) add 63 decisions: 2 changed and 18 within the noise. That makes 1,355 traced decisions in all, with 45 changed and 296 within the noise.

| group | decisions | changed | within the noise | first-action decisions | changed at the first action |
|---|---|---|---|---|---|
| B- | 411 | 24 | 101 | 171 | 16 |
| A- | 266 | 3 | 52 | 87 | 2 |
| D3- | 262 | 7 | 52 | 81 | 4 |
| L8- | 81 | 0 | 15 | 30 | 0 |
| LR- | 272 | 9 | 58 | 87 | 0 |

| when kx changed km3's move (43) | value |
|---|---|
| median lead (share of play-outs won; 0.0625 = 1 more win in 16) | +0.281 |
| median standard error of that lead | 0.112 |
| median lead / standard error | 2.53 (range of leads +0.125 to +0.688) |
| changes just past the threshold (2.0 to 2.5 SE) / 2.5 to 3 SE / 3 SE or more | 21 / 8 / 14 |
| median number of moves compared at a changed decision | 9 |
| changes to "end the turn" / of which km3 attacked on the same deal and kx did not | 9 / 7 |
| kept km3's move although another move led (within the noise): median lead, median SE | 278: +0.063, 0.101 |

## 4. Where kx changed km3's move on an exact-list (B-) position

| decision maker | changes | toward his choice | away from it | neither | not comparable (kx's line had already left his) |
|---|---|---|---|---|---|
| Auto | 23 | 1 | 11 | 5 | 6 |
| Dustin | 1 | 1 | 0 | 0 | 0 |
| all | 24 | 2 | 11 | 5 | 6 |

| position | decision maker | seed | step | km3 proposed | kx played | his choice there | lead (SE) | change |
|---|---|---|---|---|---|---|---|---|
| B-205731-t02 | Auto | 2 | 1 | play Copycat | end the turn | attach Water to Carvanha (Active) | +0.250 (0.112) | neither |
| B-205731-t02 | Auto | 3 | 2 | play Copycat | attack with Sharp Fang | attack with Sharp Fang | +0.313 (0.151) | toward |
| B-205731-t10 | Auto | 1 | 3 | attach Water to Alolan Vulpix (Bench 3) | attack with Binding Snow | (not the same state) | +0.250 (0.112) | not comparable |
| B-205731-t10 | Auto | 2 | 1 | retreat Mega Sharpedo ex into Alolan Ninetales ex | attach Water to Mega Sharpedo ex (Active) | bench Alolan Vulpix | +0.313 (0.120) | neither |
| B-205731-t10 | Auto | 2 | 2 | retreat Mega Sharpedo ex into Alolan Ninetales ex | play Misty | (not the same state) | +0.313 (0.151) | not comparable |
| B-210952-t10 | Auto | 1 | 1 | evolve Carvanha (Bench 1) into Mega Sharpedo ex | retreat Lapras into Carvanha | evolve Carvanha into Mega Sharpedo ex | +0.438 (0.128) | away |
| B-210952-t10 | Auto | 2 | 1 | evolve Carvanha (Bench 1) into Mega Sharpedo ex | retreat Lapras into Alolan Ninetales ex | evolve Carvanha into Mega Sharpedo ex | +0.375 (0.125) | away |
| B-210952-t10 | Auto | 3 | 1 | evolve Carvanha (Bench 1) into Mega Sharpedo ex | retreat Lapras into Carvanha | evolve Carvanha into Mega Sharpedo ex | +0.375 (0.155) | away |
| B-210952-t12 | Auto | 1 | 1 | attach Water to Mega Sharpedo ex (Bench 1) | retreat Lapras into Mega Sharpedo ex | attach Water to Mega Sharpedo ex (Bench 1) | +0.375 (0.148) | away |
| B-210952-t12 | Auto | 3 | 1 | attach Water to Mega Sharpedo ex (Bench 1) | retreat Lapras into Mega Sharpedo ex | attach Water to Mega Sharpedo ex (Bench 1) | +0.313 (0.136) | away |
| B-210952-t14 | Auto | 1 | 1 | bench Carvanha | retreat Lapras into Alolan Ninetales ex | bench Carvanha | +0.250 (0.079) | away |
| B-210952-t14 | Auto | 1 | 2 | bench Carvanha | end the turn | (not the same state) | +0.156 (0.060) | not comparable |
| B-210952-t14 | Auto | 2 | 1 | bench Carvanha | retreat Lapras into Alolan Ninetales ex | bench Carvanha | +0.250 (0.065) | away |
| B-210952-t14 | Auto | 2 | 2 | bench Carvanha | end the turn | (not the same state) | +0.219 (0.064) | not comparable |
| B-210952-t14 | Auto | 3 | 1 | bench Carvanha | retreat Lapras into Alolan Ninetales ex | bench Carvanha | +0.281 (0.079) | away |
| B-210952-t14 | Auto | 3 | 2 | bench Carvanha | end the turn | (not the same state) | +0.156 (0.075) | not comparable |
| B-210952-t16 | Auto | 1 | 1 | bench Alolan Vulpix | attack with Binding Snow | bench Alolan Vulpix | +0.188 (0.063) | away |
| B-210952-t16 | Auto | 2 | 1 | bench Alolan Vulpix | attack with Binding Snow | bench Alolan Vulpix | +0.125 (0.056) | away |
| B-210952-t16 | Auto | 3 | 2 | evolve Carvanha (Bench 1) into Mega Sharpedo ex | attach Water to Alolan Ninetales ex (Active) | evolve Carvanha into Mega Sharpedo ex | +0.250 (0.112) | away |
| B-210952-t16 | Auto | 3 | 5 | put Elegant Cape on Alolan Ninetales ex (Active) | put Elegant Cape on Mega Sharpedo ex (Bench 1) | (not the same state) | +0.563 (0.128) | not comparable |
| B-210952-t18 | Auto | 1 | 1 | play Cyrus | play Misty | evolve Alolan Vulpix (Bench 3) into Alolan Ninetales ex | +0.281 (0.091) | neither |
| B-210952-t18 | Auto | 2 | 1 | play Cyrus | play Misty | evolve Alolan Vulpix (Bench 3) into Alolan Ninetales ex | +0.313 (0.063) | neither |
| B-210952-t18 | Auto | 3 | 1 | play Cyrus | play Misty | evolve Alolan Vulpix (Bench 3) into Alolan Ninetales ex | +0.219 (0.064) | neither |
| B-215203-t02 | Dustin | 2 | 1 | play Copycat | play Misty | play Misty | +0.250 (0.112) | toward |

Descriptive groups (A-, D3-, LR-): 19 changes, with 0 toward, 5 away, 5 neither and 9 not comparable. The rows are in kx_agreement_tables.md.

### Table findings

- Your question first: yes, something else is running on the laptop. I checked WSL while finishing. The strength pre-registration for kx3 v k3 (rl/results/strength_2026-10-04_kx3_v_k3) is in its self-check: kx3 playing 12 games of t-altaria v t-suicune. It had been going about 10 minutes and was using about 12 to 13 cores. This analysis only read finished result files for a few seconds and did not touch that job.
- Against Auto (31 exact-list positions, 4 games), kx agrees with Auto a little less than km3 does. kx's first action matches Auto's on all 3 seeds in 10 positions. km3 matches in at least 10 of 12 seeds in 14. On the same deals, kx never matched Auto where km3 missed, and km3 matched Auto where kx missed on 10 seeds. Whole plan to the first draw: 4 positions for both.
- Against Dustin (26 positions, 3 games), kx and km3 are almost identical. First action: 16 positions all 3 seeds for kx, 16 agree for km3. Whole plan: 12 for each. The only seed where they part is 215203 turn 2: on seed 2 kx played Misty as Dustin did, where km3 played Copycat. kx put Misty on the benched Carvanha and he put it on the Active Lapras, so the whole plan still differs.
- By milestone, the Auto gap is in 'preparing an attacker'. There kx matches Auto's first action on all 3 seeds in 8 of 24 positions, against km3's 12 of 24. On 'recognising an immediate win' the two pilots are the same: Auto 1 of 3 for both, Dustin 3 of 3 for both.
- Descriptive groups. On A- (29 positions) and L8- (10) kx's counts equal km3's exactly. On D3- (27) kx matches him slightly less: all 3 seeds in 16 positions against km3's 19 at 10 or more of 12, and on 4 seeds km3 matched where kx did not. LR- is the same as km3 on the same 3 seeds.
- How often kx overrode km3: 43 of the 1,292 decisions in kx's own turns (3%). Adding the forced replays gives 45 of 1,355. km3's move had the best play-out score 971 times. Another move led but stayed within the noise 278 times (296 with the forced replays).
- By kind of km3's proposed move, kx changed: a Supporter/Item play 11 of 395, an Energy attachment 4 of 232, a retreat or switch 2 of 80, an attack 0 of 189, an evolution 8 of 127, an Ability 2 of 99, ending the turn 3 of 29, and other choices 13 of 141 (mostly benching a Basic).
- When kx switched, the median lead was +0.28 of a game (about 4.5 more wins in 16 play-outs), with a median standard error of 0.11. That is a median of 2.5 standard errors, just past the 2-SE bar. 21 of the 43 switches sit between 2.0 and 2.5 SE, after comparing a median of 9 moves. Picking the best of several moves makes some switches at that level likely to be chance.
- Worth a look before trusting kx's switches: 9 of the 43 are to 'end the turn'. On 7 of them km3, on the same deal, goes on to attack and kx's turn has no attack at all. Examples: 210952 turn 14 (all 3 seeds), where kx retreats Lapras into Alolan Ninetales ex and ends the turn with no Water and no Surf; and deck 03 game 022135 turn 7 (2 seeds), where kx ends the turn at once. In that turn, km3 and you both benched Indeedee ex, played Pokémon Center Lady and attacked with Wave Splash.
- Toward or away (exact lists only): kx changed km3's move 24 times on B- positions, 23 on Auto's and 1 on Dustin's. On the 18 where the board was the same as the decision maker's, 2 moved toward his choice, 11 away and 5 to a third move. 6 could not be compared because kx's line had already left his. Toward: 205731 turn 2 (Sharp Fang as Auto did, instead of km3's Copycat) and 215203 turn 2 (Dustin's Misty).
- All 11 'away' changes are in one Auto game, 210952, the one Auto lost 2-3. On turns 10, 12 and 14 kx retreats Lapras where Auto and km3 evolved Carvanha, attached Water or benched Carvanha. On turns 10 and 12 kx then attacks with Turbo Shark from the Active Mega Sharpedo ex instead of Surf from Lapras, where its plan reaches an attack. On turn 16 kx attacks with Binding Snow at once on 2 seeds, without first benching Alolan Vulpix and evolving. 18 of the 24 B- changes are in this one game. Matching the decision maker is not the same as playing better.
- The checks all passed. km3's 12-seed runs in runs_km3 equal the original reference run plan for plan (1,824 seed plans). My per-position counts equal the runner's own reports for both pilots. On all 456 position-seeds, the km3 move kx considered at its first decision equals km3's own first action on the same seed. So every first-action difference between kx and km3 is a logged switch, not run noise.

### Caveats

- kx ran 3 seeds per position, km3 ran 12. The runner's report prints '/12' out of habit; kx's counts there are out of 3. 'All 3 seeds' is an easier bar than 'at least 10 of 12', so the like-for-like comparison is the 'km3 on the same 3 seeds' column. Same seed means the same deal of his unseen cards.
- The position runner plays only the first action and the plan up to the first draw card (Research, Poké Ball, Copycat and similar). Nothing after that card is compared, and a turn with no draw card is graded whole. kx is asked only on the pilot's own turn.
- Auto's and Dustin's positions come from different games and are never paired position by position. Compare their rates only. The milestone rows rest on 2 to 24 positions each, and on B- positions the milestones are mechanical tags.
- Agreement is not strength. Matching Auto or Dustin says nothing about which choice was better.
- kx's play-outs model the opponent as km3 (km3 plays both sides). Under REALISTIC knowledge the opponent's list is drawn from a pool. On B- positions the computer deck was the only consistent list and was used in all 6,576 play-outs. On A-, D3-, L8- and LR- the play-outs used meta lists (mostly t-lucario, t-altaria, t-blaziken), and on D3- the computer deck in 2,079 play-outs. None of these is the real opponent's deck, so those groups are descriptive only.
- Toward or away is judged only where kx's plays before that decision equal the decision maker's recorded plays. Coin results (Misty, Lucky Ice Pop) and Bench slot numbers are not checked, the same as in the report. 6 of the 24 B- changes could not be compared. Changes at later steps happen on kx's own line.
- Two Auto turn-1 positions (210612 turn 1, 211613 turn 1) where Auto made no play count as 'none' for both pilots: by the report's rule an empty plan never counts as agreeing. Neither pilot ended those turns without playing.
- Decision kinds are classified by km3's proposed move. Cyrus's choice of the opponent's Pokémon counts as retreat/switch, as the report does. Benching a Basic, Tool target, Stadium, heal target, Misty's target and Luxury coin choices are 'other'. 13 decisions had more than 12 legal moves, so some moves were not played out (the cap). No play-out rounds were lost to engine errors.
- The lead is the paired difference in play-out score: win 1, tie half, loss 0, over 16 play-outs. The SE is its standard error. I read this definition from kx's source on the laptop.
- Development positions only: 152 run (B- 57, A- 29, D3- 27, L8- 10, LR- 29); held-out positions were not run. LR- (reconstructed own list) was not asked for; it is included as descriptive. The 63 forced-replay decisions (5 A- positions) are counted separately from the main table.
- Outputs are in the scratchpad: kx_agreement_tables.md has the full tables, the per-position B- table and the descriptive change list; kx_agreement_rows.json has the rows. Nothing in the repo or under /home/dacz8976 was changed.

## Examples (checked wording)

### improved: B-210952-t18 (decision maker Auto; exact list: True; milestone: preparing an attacker)

Situation: Game 210952, the only one of the 8 games against the computer's Blastoise/Wailord deck that was lost (Auto, 2-3). Game turn 18, score 1-1, one card left in his deck. His Active Alolan Ninetales ex is down to 20 HP with 2 Water. On his Bench are two Mega Sharpedo ex (190 HP, 1 Water each) and an Alolan Vulpix (1 Water). His hand: Irida, Copycat, Alolan Ninetales ex, two Misty, Elegant Cape, Cyrus. The computer's Active is a Mega Blastoise ex at 170 of 230 HP with 5 Water. Its Bench has Frigibax, a Baxcalibur at 20 HP and a Wailmer with 3 Water, and its Soothing Shore is in play. Once the Blastoise has 6 Water, Triple Bombardment (130) also does 50 to 2 Benched Pokémon. That would knock out the damaged Ninetales ex even on the Bench, for the computer's last 2 points.

What Auto did: Evolved the Vulpix into a fresh Alolan Ninetales ex. Cyrus pulled the 20-HP Baxcalibur into the Active Spot, which sent the Blastoise to the Bench. Retreated the old Ninetales ex (paying its 2 Water) into a Mega Sharpedo ex. Put the turn's Water on the new Ninetales ex. Turbo Shark knocked out Baxcalibur (2-1), and its extra Water went to the old Ninetales ex, so Soothing Shore healed it to 40. The computer promoted the Blastoise right after the knockout. On turn 19 it attached a 6th Water, and Triple Bombardment hit the Bench and knocked out the old Ninetales ex. Lost 2-3 (ledger, turns 18-19).

km3 (12 of 12 seeds): Cyrus on Baxcalibur, evolve the Vulpix, retreat into the new Ninetales ex, Water and Elegant Cape on it. Then Binding Snow knocks out Baxcalibur (2-1). Binding Snow's lock (no Energy from the Zone to the Active Pokémon on the computer's next turn) still applies, but it covers whatever the computer promotes. With the Blastoise on the Bench, the computer can attach to it there and then bring it in, for example by promoting the Wailmer and retreating it with its 3 Water.

kx (3 of 3 seeds): Misty first, on the Vulpix, instead of Cyrus. Seed 1: evolve the Vulpix, retreat the 20-HP Ninetales ex into it, put Water and Elegant Cape on the fresh Ninetales ex, then Binding Snow (80) on the Active Mega Blastoise ex. Seeds 2 and 3: retreat into the Vulpix first, then evolve it, and put Elegant Cape on it. The turn's Water went to the old Ninetales ex on the Bench, because Misty's heads had already given the fresh one its second Water. Then Binding Snow on the Blastoise. No point this turn. But the Blastoise stays Active under the lock, so next turn it can't take Energy from the Zone or from Baxcalibur's Ice Maker. It stays at 5 Water, and Triple Bombardment does no Bench damage. The computer's list has no other way to add Energy to it or to pull up a Benched Pokémon. Turn 17 of this game shows the lock working.

Trace evidence: /home/dacz8976/pgd/runs_kx3_trace/err_B-210952-t18.txt, first decision of each seed: 16 play-outs, all with the computer's list (extra:BL). All three seeds switched from km3's Cyrus to Misty. Seed 1: Misty won 0.438 of play-outs, Cyrus 0.156 (lead +0.281, standard error 0.091, 3.1 SE). Seed 2: 0.500 v 0.188 (+0.313, SE 0.063, 5.0 SE). Seed 3: 0.344 v 0.125 (+0.219, SE 0.064, 3.4 SE). Auto's first move (evolve, with km3 finishing the turn) tied Cyrus exactly, probably because km3 plays Cyrus next. That number does not score Auto's actual Turbo Shark line. Irida and attacking at once each won 0 of 16 in every seed. After Misty, kx kept km3's choice at every later step of the turn. km3 reference: /home/dacz8976/pgd/runs_km3/out_B-210952-t18.jsonl. Real ending: TURN_LEDGER.json, turns 17-19.

Why it matters: A clear case where kx's change lines up with how the real game was lost: Auto's line let the Blastoise reach 6 Water and hit the Bench, and kx's line keeps it locked for a turn. Caveats. Misty itself adds little: its target made no difference, and in seed 1 it flipped no heads. Its value is probably that it uses up the turn's one Supporter, so km3 can't play Cyrus and uses Binding Snow on the Blastoise instead. That is a guess, because Irida also uses up the Supporter and won 0 of 16. The gain over km3 is measured only in kx's play-outs, where km3 plays the computer. In the real game the computer promoted the Blastoise after the knockout, and if it had done the same after km3's Binding Snow, the lock would have stopped the 6th Water too. kx's own line wins only 34-50% of its play-outs, and the lock lasts one turn.

<details><summary>What the check corrected</summary>

- Checked and correct: the board, the hand, the score, one card left in his deck (positions_kx.json and the out_ summary). It is the only loss among the 8 Blastoise/Wailord games. km3 plays Cyrus, then the Binding Snow knockout, in 12 of 12 seeds. All of kx's trace numbers match err_B-210952-t18.txt: seed 1 0.438 v 0.156 (+0.281, SE 0.091, 3.1 SE), seed 2 0.500 v 0.188 (+0.313, SE 0.063, 5.0 SE), seed 3 0.344 v 0.125 (+0.219, SE 0.064, 3.4 SE). There were 16 rounds, every play-out used extra:BL, and Irida and attacking at once each won 0 of 16 in every seed. The card texts back the argument: Triple Bombardment needs 3 extra Water (6 in total); Binding Snow stops Energy from the Zone going to the Active Pokémon; Ice Maker takes Energy from the Zone; Misty, Cyrus and Irida are Supporters.
- Wrong timing in Auto's line. The computer promoted the Blastoise on turn 18, right after Turbo Shark's knockout (ledger turn 18: 'Opponent promotes Blastoise'), not on its next turn. On turn 19 it attached the 6th Water. Missing detail: Turbo Shark's extra Water went to the old Ninetales ex, and that Water is why Soothing Shore healed it from 20 to 40.
- kx's line is not the same in all 3 seeds. Only seed 1 goes evolve, retreat, Water on the fresh Ninetales ex. In seeds 2 and 3 the old Ninetales ex retreats into the Vulpix first, then the Vulpix evolves in the Active Spot. The turn's Water then went to the old 20-HP Ninetales ex on the Bench, because Misty's heads had already given the fresh one its second Water. The 'Misty first, Binding Snow on the Blastoise' core is the same in all 3 seeds.
- km3's line is described incompletely. km3 also uses Binding Snow, so the lock is still there in its line. The lock covers whatever the computer has Active (engine: can_attach_energy_from_zone blocks only the Active Spot), not the Pokémon that was hit. 'Ends up on the Bench' depends on the computer's choice of what to promote. The real risk: with the Blastoise on the Bench, the computer can attach to it there and bring it in, for example by promoting the Wailmer and retreating it with its 3 Water.
- Overstated: 'the game was lost exactly the way kx's line avoids' / 'clearest real gain'. The real game shows that Auto's Turbo Shark line lost. It does not show that km3's line would have lost. In the real game the computer promoted the Blastoise after the knockout, and after km3's Binding Snow that would have put the Blastoise under the lock too. kx's edge over km3 rests only on its play-outs, where km3 plays the computer. 'Clearest in the set' was not checked against the other examples.
- Unchecked cause: 'Misty wins because it uses up the turn's one Supporter'. Irida is also a Supporter, and it won 0 of 16 in every seed. So using up the Supporter is not enough on its own; what matters is the follow-up km3 plays after Misty. The data does support 'Misty itself adds little': its target made no difference (seed 1: all four targets tied at 0.406). In seed 1 it flipped no heads, because Binding Snow became usable only after the turn's Water.
- Unchecked cause: 'evolve scored the same as Cyrus because km3 plays Cyrus right after'. The exact tie (SE 0.000 in all 3 seeds) fits that explanation, but the trace does not show km3's follow-up, so it should say 'probably'. Also, this scores Auto's first move with km3 finishing the turn. It does not score Auto's actual Turbo Shark line.
- Minor wording: 'That would knock out the damaged Ninetales ex' should say 'even from the Bench'. While it is Active, 130 knocks it out anyway.

</details>

### improved: B-205731-t02 (decision maker Auto; exact list: True; milestone: none)

Position B-205731-t02 (exact lists, decisions by Auto). Game 205731, which Auto won 3-2. This is game turn 2, and he went second. His only Pokémon is a Carvanha (50 HP, no Energy) in the Active Spot. His hand is Mega Sharpedo ex, Lucky Ice Pop, Irida, Alolan Ninetales ex and Copycat. The computer has Meowth Active (50 HP), Squirtle and Frigibax on the Bench, and 3 cards in hand. No Pokémon can evolve on either player's first turn, so the Mega Sharpedo ex has to wait until turn 4.

What Auto did: Water on the Carvanha, then Sharp Fang (30) on Meowth. Auto kept the Mega Sharpedo ex in hand. On turn 4 it evolved into it, attached Water and used Turbo Shark.

What km3 did (12 seeds): its first action was Water in 7 seeds and Copycat in 5. Its whole plans were Water then Copycat (6 seeds), Copycat alone (5), and Water then Sharp Fang (1). Playing Copycat while the computer holds 3 cards shuffles his other 4 cards into the deck and draws only 3. The Mega Sharpedo ex he needs next turn goes back into the deck.

What kx did (3 seeds). These are the same seeds where km3 alone played Copycat; Copycat; and Water then Copycat, so km3 matched Auto's plan in none of them.
- Seed 1: kept km3's Copycat. The best alternative, ending the turn, led by only +0.063 (SE 0.143). Auto's Water scored below Copycat (0.750 v 0.813).
- Seed 2: switched from Copycat to ending the turn at once, without the Water and without attacking (+0.250, SE 0.112, 2.2 SE). This is the failure entry for this position.
- Seed 3: kept km3's own Water first. Ending the turn led by +0.125, SE 0.155, which is within the noise. At the second decision kx switched from km3's Copycat to Sharp Fang (0.875 v 0.563, +0.313, SE 0.151, 2.1 SE). The result is exactly Auto's turn. Ending the turn also scored above Copycat there (+0.250, SE 0.171), but that is within the noise.
Evidence: /home/dacz8976/pgd/runs_kx3_trace/err_B-205731-t02.txt (16 rounds per decision) and /home/dacz8976/pgd/runs_km3/out_B-205731-t02.jsonl. Auto's turn 4 is position B-205731-t04 in positions_kx.json.

Why it matters: kx's play-outs rated Copycat poorly. kx moved off km3's Copycat in 2 of 3 seeds, each time only just past the 2-SE bar. But only 1 of those 2 moves went to Auto's Water-and-Sharp-Fang line. The other ended the turn with nothing done. kx's play-outs don't reliably favour Auto's line here: in one seed Auto's Water scored below Copycat, and in another ending the turn scored above the Water. The one match came after km3 itself had chosen the Water. With 3 seeds and margins this close to the bar, this is a hint, not proof, that kx fixes the Copycat mistake.

<details><summary>What the check corrected</summary>

- The 'why it matters' line gets the reason wrong. It says kx corrects Copycat 'only when Copycat is the decision being made right now' and that 'only 1 seed of 3 got there'. In fact km3 chose Copycat at the very first decision in seeds 1 and 2 as well (km_move = Copycat in both traces). kx moved off Copycat in 2 of 3 seeds: in seed 2 it switched to ending the turn (+0.250, SE 0.112, 2.2 SE), and in seed 3 it switched to Sharp Fang (+0.313, SE 0.151, 2.1 SE). Seed 1 kept Copycat because the best alternative, ending the turn, led by only +0.063 (SE 0.143). The real limit is that kx's play-outs don't reliably favour Auto's line. In seed 1, Auto's Water scored below Copycat (0.750 v 0.813). In seed 2, ending the turn scored above the Water (0.938 v 0.750).
- 'Ending the turn also beat Copycat: +0.250, SE 0.171' overstates it. That lead is 1.5 standard errors, inside the noise. It should say that ending the turn scored higher, but within the noise.
- Who made which move: in seed 3, the Water was km3's own first move, not a kx change. kx kept it because ending the turn's lead of +0.125 (SE 0.155) was within the noise. kx's only change in seed 3 was Sharp Fang instead of Copycat. The seeds line up between the two runs: in seeds 1 to 3, km3 alone played Copycat; Copycat; and Water then Copycat. So km3 matched Auto's plan in 0 of those 3 seeds, and kx matched it in 1.
- The 'human choice' line says 'He' for moves that Auto made. positions_kx.json records decision_maker Auto for both B-205731-t02 and B-205731-t04. Write 'Auto' so it doesn't read as Dustin's play.
- Report note: the kx report's summary row prints 'first 1/12 plan 1/12' for this position. Read both as 1 of 3. Its per-game table already says 1/3.
- Checked and correct as written: the board (Carvanha B4 034, 50 HP, no Energy, his only Pokémon; the computer has Meowth 50 HP Active, Squirtle and Frigibax on the Bench, 3 cards in hand); his hand of 5; won 3-2; went second. Auto's turn 2 was Water, then Sharp Fang. Auto's turn 4 was evolve into Mega Sharpedo ex, Water, Turbo Shark, with the Mega Sharpedo ex still in hand at t04. km3 over 12 seeds: Water first in 7 and Copycat first in 5; whole plans 6/5/1. Every kx trace number (scores, diff, SE) matches, with 16 rounds each. Card texts: Copycat says 'Shuffle your hand into your deck. Draw a card for each card in your opponent's hand.', so 4 cards go back and 3 are drawn. Mega Sharpedo ex is a Stage 1 from Carvanha. No Pokémon evolves on either player's first turn, so Mega Sharpedo ex could not come down on turn 2.

</details>

### improved: B-215203-t02 (decision maker Dustin; exact list: True; milestone: none)

{"kind":"improved","position_id":"B-215203-t02","exact_list":true,"decision_maker":"Dustin","milestone":"none","situation":"Game 215203 (Dustin, won 3-0), game turn 2, he went second. His Active is a Lapras (110 HP, no Energy; Surf needs 3 Energy), with a Carvanha on the Bench. His hand: Misty, Lucky Ice Pop, Alolan Ninetales ex, Copycat. The computer has Meowth Active, Frigibax and Wailmer on the Bench, and 4 cards in hand.","human_choice":"Misty on Lapras: one heads, then tails, so one Water from Misty. Then his Water for the turn on Lapras, and no attack. On his next turn (game turn 4), Lapras had 2 Water. He attached a third and used Surf (70) that same turn, knocking out the Meowth for his first point. He also played Copycat on turn 4.","km3_choice":"km3 never plays Misty. On all 12 seeds it plays Copycat: right away in 7, after Water on Lapras in 3, after Water on Carvanha in 2. Misty and Copycat are both Supporters, and only one Supporter is allowed per turn.","kx_choice":"Seed 2 only: Misty aimed at the Carvanha (not Lapras), then Water on Lapras, then end of turn. Seed 1 played Copycat right away. Seed 3 put Water on Lapras, then played Copycat. Both were km3's own moves.","trace_evidence":"File: /home/dacz8976/pgd/runs_kx3_trace/err_B-215203-t02.txt. Every decision was played out 16 times against the computer's exact list. Seed 2, first decision: Misty won 16 of 16 play-outs (1.000), Copycat 0.750. Misty led by +0.250 (SE 0.112, 2.2 SE), just past the 2 SE bar, so kx switched. Seed 1: Misty again 1.000 against Copycat 0.875. Misty led by +0.125 (SE 0.085, 1.5 SE), so Copycat was kept. Seed 3: km3's first move was Water on Lapras (0.813), and Misty scored 0.625 (-0.188, SE 0.136). After the Water, Misty trailed Copycat by -0.063 (SE 0.170). Misty's target on seed 2: Carvanha 0.813 against Lapras 0.750 (-0.063, SE 0.063, about 1 SE). That gap is noise, so kx kept km3's pick of Carvanha. km3: /home/dacz8976/pgd/runs_km3/out_B-215203-t02.jsonl.","why_it_matters":"kx plays Dustin's Supporter on 1 of 3 seeds. Misty can add Water at no Energy cost: each heads is a Water, but tails on the first flip gives none. Dustin's one heads on Lapras is what let him use Surf on turn 4, and he still played Copycat that turn. Copycat on turn 2 shuffles the other 3 cards (Misty, Lucky Ice Pop and the Ninetales ex) back and draws 4. kx put its Misty on the Carvanha, so in its line Lapras would not be ready to Surf on turn 4 the way Dustin's was. This is a weak example: one seed of three, 2.2 SE, a different Misty target, and play-outs that assume the computer plays like km3."}

<details><summary>What the check corrected</summary>

- Every number and fact checks out against the raw files. The board and hand match positions_kx.json. Dustin's play matches the game record (TURN_TABLE turn 2: Misty heads once, then tails, one Water to Lapras, then a normal Water to Lapras, no attack). km3's 12 seeds give Copycat 7, Water on Lapras then Copycat 3 (seeds 3, 5, 6), and Water on Carvanha then Copycat 2 (seeds 4, 10). The kx trace numbers are all exact. The card texts are confirmed: Lapras A3 044 has 110 HP and Surf [WWC] 70; Misty and Copycat are both Supporters; the rules allow one Supporter per turn. Marked not verified because of the wording problems below.
- human_choice is misleading. 'that turn's Water allowed Surf (70) on his very next turn' reads as if Surf came on turn 6. The record says it came on turn 4: Lapras started turn 4 with 2 Water, he attached a third and used Surf that same turn, knocking out Meowth for his first point. He also played Copycat on turn 4, so Misty first only delayed Copycat by one turn and did not give it up.
- kx_choice is imprecise. Seed 3 did not simply 'keep the Copycat line'. It attached Water to Lapras first and then played Copycat. Both were km3's moves.
- trace_evidence for seed 3 is imprecise. The -0.188 (SE 0.136) is measured against km3's first move on that seed, which was Water on Lapras (0.813), not against Copycat. After the Water, Misty trailed Copycat by -0.063 (SE 0.170). Also worth saying: Misty scored 1.000 (16 of 16 play-outs won) on seed 1 as well, against Copycat's 0.875.
- why_it_matters overstates slightly. 'Free Energy' should say it can be none: if the first flip is tails, Misty gives no Water. More important, kx aimed Misty at Carvanha. In kx's line, Lapras has only 2 Water on turn 4 and cannot Surf then, so kx does not reproduce the benefit that Dustin's one heads gave him. Copycat shuffles back Misty and Lucky Ice Pop as well as the Ninetales ex.
- Add the run's caveat: the play-outs used the computer's exact list but modelled the computer as km3.

</details>

### improved: LR-200654-t06 (decision maker Dustin (ladder game; APPROXIMATE list); exact list: False; milestone: none)

Position LR-200654-t06 (kx changed km3's move; descriptive only, no verdict).

Situation: APPROXIMATE LIST. His list was rebuilt from recordings. 18 of its 20 cards were seen in this game; the other 2 (two Galarian Linoone) were taken from his other recordings of the deck from Sept 26-27. The opponent's list is unknown, so this position is outside every verdict. It is a Ladder Log game from Sept 28 with his Hydreigon / Galarian Obstagoon deck, at game turn 6 with the score 0-0. His Active is a Galarian Zigzagoon with 1 Darkness and a Deceptive Needle. On his Bench are a second Zigzagoon (also 1 Darkness and a Needle) and a Zweilous (90 HP, no Energy). His hand is Galarian Obstagoon, Lillie and Hydreigon. The opponent has Arceus ex Active (140 HP, Rocky Helmet, no Energy), with Dialga ex (2 Metal) and Shaymin on the Bench.

His play: He evolved Zweilous into Hydreigon, put the Darkness on it, and used Tackle with Zigzagoon: 10 damage, plus 10 from the Needle at the end of the turn. Rocky Helmet did 20 back to Zigzagoon.

km3 (12 of 12 seeds): Evolve into Hydreigon, then use Roar in Unison (2 Darkness from the Energy Zone, 30 damage to itself). Retreat Zigzagoon into Hydreigon, heal Hydreigon with Lillie, and attach Darkness. Hydreigon now has 3 Darkness and Hyper Ray is ready, but km3 ends the turn without attacking.

kx (all 3 seeds): The same set-up, then Hyper Ray (130) on Arceus ex at the turn's last decision. Arceus ex goes from 140 to 10, and Rocky Helmet does 20 back, taking Hydreigon from 150 to 130.

Trace (err_LR-200654-t06.txt, last decision, step 6, Hyper Ray v ending the turn, 16 play-outs each):
- Seed 1: 0.813 v 0.500 (+0.313, SE 0.151, 2.1 SE).
- Seed 2: 0.813 v 0.500 (+0.313, SE 0.120, 2.6 SE).
- Seed 3: 0.938 v 0.438 (+0.500, SE 0.129, 3.9 SE).
No list in the pool fits the opponent's cards, so the play-outs drew its hidden cards from the closest one, t-hydreigon. That is a Darkness Hydreigon / Mega Absol ex list, nothing like the real Arceus ex / Dialga ex deck. km3 also played the opponent's side.

Why it matters: In kx's play-outs, attacking beat km3's pass in all three seeds, and the reason makes sense. Hyper Ray throws away its Energy, but Roar in Unison (2) plus the turn's attachment rebuild 3 Darkness every turn, so the Energy comes back. The cost is HP instead: Rocky Helmet's 20 now, and Roar in Unison's 30 each time it reloads. That HP can matter. In the real game, his turn 8 Roar left Hydreigon on 120. On turn 9, Ultimate Force (70 plus 20 for each of three Benched Pokemon, so 130) knocked it out. So this is kx catching a likely km3 'set up and then pass' mistake at the last decision of a turn, not proof of one. The list is approximate and the opponent model is the wrong deck, so it carries no verdict.

<details><summary>What the check corrected</summary>

- All the facts check against the raw files. The board, score, turn and hand match positions_kx.json, and so does his recorded line (Evolve Hydreigon, Darkness on it, Tackle). km3's plan is identical in all 12 seeds: Evolve, Roar in Unison, retreat into Hydreigon, Lillie, attach, end turn. At the last decision km3 scores ending the turn 1422.3 and Hyper Ray -572.7 in every seed. kx's plan is the same set-up plus Hyper Ray in all 3 seeds. The step 6 numbers are exact: seed 1 is 0.813 v 0.500 (+0.313, SE 0.151); seed 2 is 0.813 v 0.500 (+0.313, SE 0.120); seed 3 is 0.938 v 0.438 (+0.500, SE 0.129). Each ran 16 rounds with no failures, and the opponent list was 't-hydreigon (closest ... no list consistent)'. The card texts back the arithmetic: Roar in Unison takes 2 Darkness from the Energy Zone and does 30 to itself; Hyper Ray is 130 and discards all Energy; the Needle only fires from the Active Spot, so Arceus ex goes 140 to 10. The flaw is in the wording.
- Overstatement: 'so the 130 damage costs almost nothing'. The Energy does come back each turn, but the price is paid in HP. Rocky Helmet does 20 back to Hydreigon now, and every Roar in Unison reload costs 30. That HP mattered in this very game. After his turn 8 Roar, Hydreigon was on 120. On turn 9, Ultimate Force (70 plus 20 for each of three Benched Pokemon, so 130) knocked it out. Without the Roar it would have survived on 150.
- Overstatement: 'In plain terms this beats km3' and 'It shows kx fixing a km3 mistake'. These claim a result, which clashes with the closing 'carries no verdict'. The play-outs had km3 playing both sides, on an approximate list, against an opponent model that is the wrong deck. What the files support: kx's play-outs rated the attack above km3's pass in all three seeds, by 2.1 to 3.9 SE.
- Name the opponent model in plain words. 't-hydreigon' is a Darkness Hydreigon / Mega Absol ex tournament list (Deino, Hydreigon, Bombirdier, Mega Absol ex, Copycat, Cyrus, Sabrina). It is nothing like the real Arceus ex / Dialga ex / Shaymin Metal deck. It came out closest only because it shares Research, Poke Ball and Lucky Ice Pop.
- Minor completeness: the benched Zigzagoon also carries 1 Darkness and a Needle, and Zweilous and Arceus ex have no Energy. The 2 inferred cards (two Galarian Linoone) come from his other recordings of the deck (Sept 26-27), not from this recording. 'Dustin' as the player rests on the Ladder Log; the rebuilt-list file records the game mode as 'ladder_presumed'.

</details>

### failure: B-210952-t14 (decision maker Auto; exact list: True; milestone: preparing an attacker)

Game 210952, game turn 14, score 0-0. Auto played Dustin's side and lost 2-3. His Active is Lapras (110 HP, 3 Water). On his Bench: Mega Sharpedo ex (190 HP, 1 Water) and Alolan Ninetales ex (150 HP, 2 Water). His hand: Carvanha, two Misty, Elegant Cape, Irida, Copycat, Mega Sharpedo ex and Alolan Ninetales ex. The computer's Active is a Wailmer at 50 HP with 1 Water. Its Retreat Cost is 3, and the computer's only X Speed was used on turn 7. So the Wailmer can't leave this turn, and next turn it can leave only if the computer puts both of its Water (the Zone's and Ice Maker's) on it. The computer's Bench: Mega Blastoise ex (230 HP, 3 Water), Baxcalibur (20 HP left) and Wailmer (100 HP, 2 Water).

What Auto did: bench Carvanha, attach Water to it, and Surf (70) knocked out the Wailmer for the first point. The computer sent in the Mega Blastoise ex and gave it its 4th and 5th Water (Zone and Ice Maker). Then Triple Bombardment (130) knocked out Lapras.

km3, in 12 of 12 seeds: bench Carvanha, Elegant Cape on the Ninetales ex, Water on Carvanha, Surf knocks out the Wailmer.

kx, in 3 of 3 seeds: retreat Lapras into the Ninetales ex (discarding 2 Water), then end the turn. No attack, no Energy attached, Carvanha not benched.

Trace (err_B-210952-t14.txt, 16 play-outs per move; a win counts 1, a tie ½):
- First decision, retreat vs km3's 'bench Carvanha': 0.250 vs 0.000 (+0.250, SE 0.079), 0.250 vs 0.000 (+0.250, SE 0.065), 0.281 vs 0.000 (+0.281, SE 0.079). km3's own move won no play-out in any seed. In each seed, 8 or 9 of the 11 moves won none.
- Second decision, ending the turn vs 'bench Carvanha': 0.406 vs 0.250 (+0.156, SE 0.060), 0.438 vs 0.219 (+0.219, SE 0.064), 0.406 vs 0.250 (+0.156, SE 0.075).
- Binding Snow straight away scored 0.250, 0.219 and 0.250. Attaching Water to the Ninetales ex first, with km3 playing on, scored 0.281, 0.156 and 0.250. Both scored below ending the turn in every seed.

Why it matters: by the card texts there looks to be a better line. After the same retreat, attach the turn's Water and use Binding Snow (80; the Ninetales ex already has the 2 Water it costs). It knocks out the 50-HP Wailmer for a point. And during the computer's next turn, nothing can be attached from its Energy Zone to its Active Pokémon, Ice Maker included, whichever Pokémon it sends in. (In this game it sent in the Blastoise.) The block does not stop Triple Bombardment (130) with the Blastoise's 3 Water. But the Ninetales ex (150 HP) survives that hit, where Lapras (110) did not. The block worked on turn 17 of this game: the Blastoise got no Water, and its sixth Water, the one that adds the 50 Bench damage, came only on turn 19. Ending the turn gives up the point and the turn's Water (unattached Energy is discarded).

kx's play-outs rated this line lower, and nothing here tests who is right. kx's leads rest on scores of 4 to 7 out of 16, in a position where no move scored above 7. One possible cause: km3, which plays the computer in kx's play-outs, may misplay the Wailmer. That was not checked. Keeping the Wailmer in front does make the computer spend next turn's Water on it. 18 of kx's 24 switches on the computer-deck positions are in this one game, 6 of them in this position.

<details><summary>What the check corrected</summary>

- Checked and correct: the board, the hand, the score and the result (lost 2-3), from positions_kx.json. Auto, not Dustin, made the recorded choice: bench Carvanha, Water to Carvanha, Surf. km3 chose the line shown in 12 of 12 seeds (runs_km3/out). kx chose 'Retreat:2, EndTurn' in 3 of 3 seeds (runs_kx3_trace/out). Every trace number matches err_B-210952-t14.txt: 16 rounds, the scores, the leads, the SEs, and Binding Snow's 0.250, 0.219 and 0.250. 18 of the 24 kx switches on B- positions are in game 210952, 6 of them in this position. The turn record (Battle Logs TURN_TABLE.md) confirms turn 15: Ice Maker plus the Zone took the Blastoise from 3 to 5 Water, and Triple Bombardment 130 knocked out Lapras. It also confirms turn 17: the block was visible, and the Blastoise got no Water.
- 'Its retreat cost is 3, so it is stuck there' overstates. The computer's only X Speed was used on turn 7. But next turn the Zone and Ice Maker (Baxcalibur is on the Bench) can both put Water on the Active Wailmer. That makes 3 Water, enough to retreat. The computer paid a 3-Water retreat on turn 11. So it is stuck only this turn, or unless the computer spends both of next turn's Water on it.
- 'the Mega Blastoise ex that has to come in' overstates. After the knockout the computer picks the new Active: the Blastoise, the 20-HP Baxcalibur or the other Wailmer. In the game it picked the Blastoise. Also add: Binding Snow does not stop Triple Bombardment. It costs Water, Water, Colorless, and the Blastoise already has 3 Water, so it still hits for 130. The Ninetales ex (150 HP) survives that hit; Lapras (110) did not. That is what happened on turn 17.
- 'The leads rest on 2-7 wins out of 16' doesn't match the trace. The trace gives scores, not win counts: a win is 1, a tie is ½. kx's picks scored 4, 4 and 4.5 of 16 (the retreat) and 6.5, 7 and 6.5 of 16 (ending the turn). The win count can't be read from those numbers.
- 'At the first decision almost every candidate won 0 of 16': say it exactly instead. km3's own move scored 0 in all three seeds. In each seed 8 or 9 of the 11 moves won no play-out; some of them tied one.
- 'kx rated this line below passing' is accurate only with a qualifier. 'Attach Water, then Binding Snow' was not a candidate itself. Two nearby moves were, and both scored below ending the turn in all 3 seeds: Binding Snow without attaching first (0.250, 0.219, 0.250), and attaching Water to the Ninetales ex with km3 playing on from there (0.281, 0.156, 0.250).
- 'In plain terms there is a better line' states a judgement as fact. It is a reading of the card texts, kx's own play-outs disagree with it, and nothing in the files tests it. Say it 'looks like' the better line.
- 'looks like the opponent model (km3) mishandling the stuck Wailmer rather than a real plan' is an unchecked guess, and the Wailmer is not truly stuck. Leaving it in front does make the computer spend next turn's Water on it. Present this as one possible cause that was not checked.
- Small wording fix: on turn 15 the Blastoise got its 4th and 5th Water (one from the Zone, one from Ice Maker), not just 'its 5th'.

</details>

### failure: B-205731-t02 (decision maker Auto; exact list: True; milestone: none)

Failure, B-205731-t02, seed 2. This is draft A against the computer's Mega Blastoise/Wailord deck. Both lists are exact, and the game's Auto was playing. No milestone.

Situation: game turn 2. This is the second player's first turn, so nothing can evolve. A lone Carvanha (50 HP, no Energy) is in the Active Spot, nothing is on the Bench, and this turn's Energy is Water. Hand: Mega Sharpedo ex, Lucky Ice Pop, Irida, Alolan Ninetales ex, Copycat. The computer has Meowth (50 HP, Carefree Steps) in the Active Spot and Squirtle and Frigibax on the Bench, and it holds 3 cards. (The improved entry for this position is seed 3; this entry is seed 2.)

Auto's play: Water on Carvanha, then Sharp Fang (30).

km3 (12 seeds): Water then Copycat (6), Copycat (5), Water then Sharp Fang (1).

kx (3 seeds):
- Seed 1: Copycat. km3's move was kept because the difference was within the noise.
- Seed 2: ends the turn at once, with no Water on the only Pokémon and no attack.
- Seed 3: Water then Sharp Fang, the same as Auto.

Trace (err_B-205731-t02.txt, seed 2, first decision, 16 play-outs per move): ending the turn scored 0.938, Water 0.750, and Copycat (km3's move) 0.688. Ending the turn led Copycat by +0.250 with a standard error of 0.112. That is 2.2 standard errors, just over the 2-SE bar. Water led Copycat by only +0.063. In all three seeds ending the turn scored above Copycat (+0.063, +0.250, +0.125), but only seed 2 cleared the bar. Seed 3 shows what happens after the Water: km3's next move there was Copycat, and the play-outs rated Sharp Fang 0.875 against Copycat 0.563 (+0.313, 2.1 SE), so kx switched to Sharp Fang.

Why it matters: this is most likely a later km3 mistake leaking into the scores. Here Copycat shuffles the other 4 cards back into the deck and draws 3. One of those 4 is Mega Sharpedo ex, which could evolve Carvanha next turn.

When kx scores Water, km3 plays the rest of the play-out, and after Water km3 usually plays Copycat (6 of the 7 km3 seeds that attached Water did). So Water scores about the same as Copycat (-0.063, +0.063, 0.000 across the three seeds). Ending the turn is the only first move that stops Copycat being played this turn, so it scores best. kx scores one move at a time, so it cannot score 'Water, then Sharp Fang' as a single choice.

Ending turn 2 with a bare 50-HP Carvanha throws away this turn's Water (Energy left unattached is discarded at the end of the turn). It also skips a free 30-damage attack, which lands only if Meowth's Carefree Steps coin flip comes up tails. The Water had no cost: it would stay on Carvanha when it becomes Mega Sharpedo ex.

<details><summary>What the check corrected</summary>

- The facts check out against the raw files. The board, hand and 3-card computer hand are correct (positions_kx.json, out_B-205731-t02.jsonl). Auto's recorded plan is Water on Carvanha, then Sharp Fang (decision_maker Auto, exact_list true, no milestones). km3's 12 seeds give Water then Copycat 6, Copycat 5 and Water then Sharp Fang 1 (runs_km3/out). In seed 2 kx ends the turn at once (plan ['EndTurn']). The seed-2 trace has ending the turn at 0.938, Water at 0.750 and Copycat, km3's move, at 0.688: +0.250 with SE 0.112, 16 rounds. The three per-seed leads of ending the turn over Copycat are +0.063, +0.250 and +0.125.
- The 'situation' line is ambiguous. 'Same position as the improved entry for B-205731-t02, seed 2' reads as if the improved entry were seed 2. The improved entry is seed 3, where kx played Water then Sharp Fang (the report's '1/12' means 1 of 3). Seed 2 is this failure.
- 'Every play-out after Water continues with km3, which then plays Copycat' says more than the files show. The play-outs' own moves are not logged. km3's reference shows that after Water it plays Copycat in 6 of 7 seeds (seed 4 attacked instead), so the honest word is 'usually', not 'every'.
- 'Ending the turn is the only first move that stops km3 from playing Copycat later' is wrong as worded. Ending the turn keeps Copycat in hand, and km3 can still play it on a later turn in the play-outs. It only stops Copycat being played this turn.
- 'This shows how a later km3 mistake leaks into the scores' is too strong. It is the most likely explanation, not something the trace shows directly. The best direct evidence is missing from the example. In seed 3's second decision, after the Water, km3's move was Copycat, and the play-outs rated Sharp Fang 0.875 against Copycat 0.563 (+0.313, 2.1 SE), so kx switched to Sharp Fang. Add it.
- 'Wastes ... the 30 damage' overstates the attack's value. The computer's Active is Meowth B2 124, the only Meowth in its list, with Carefree Steps: when an attack damages it, flip a coin, and heads prevents the damage. Sharp Fang's 30 lands only on tails. 'Wastes the Energy' is right: RULES_FOR_AGENTS says unattached Energy is discarded at the end of the turn.
- The trace sentence should say that only seed 2 cleared the 2-standard-error bar. Seeds 1 and 3 had ending the turn ahead by about 0.4 and 0.8 standard errors, which is within the noise. The Water-versus-Copycat comparison is about even across seeds (-0.063, +0.063, 0.000), so 'no better than Copycat' is fair.
- Optional, for Dustin: say why Copycat is the likely mistake. Copycat shuffles the other 4 cards back into the deck, including the Mega Sharpedo ex that could evolve Carvanha next turn, and draws 3 (the computer holds 3 cards). Also say that nothing can evolve on this turn (the second player's first turn), and that the Water costs nothing: it stays on Carvanha when it becomes Mega Sharpedo ex (Turbo Shark costs one Water).

</details>

### failure: B-215203-t06 (decision maker Dustin; exact list: True; milestone: preparing an attacker)

Situation: Game 215203 (Dustin's decisions, won 3-0), game turn 6 (his third turn), he leads 1-0. His Active is a Lapras (110 HP, 3 Water). Bench: an Alolan Vulpix (60 HP, no Energy; benched on turn 4, so it can evolve now) and a Mega Sharpedo ex (220 HP with Elegant Cape, no Energy). Hand: Alolan Ninetales ex, Cyrus, Mega Sharpedo ex. The computer has Wailord ex Active (250 HP, no Energy), plus Wartortle (2 Water) and Frigibax.

Human choice: Evolve the Vulpix into Alolan Ninetales ex. Retreat Lapras into the Mega Sharpedo ex (Lapras discards 2 of its 3 Water) and attach Water to the Sharpedo. Turbo Shark does 70 to the Wailord ex (250 to 180), and its extra Water goes onto the new Ninetales ex. His recorded plan stops at the attack; the turn-8 board (Ninetales ex 1 Water, Lapras 1 Water) shows where the Water went. On turn 8 he retreated for free (Mega Sharpedo ex has no Retreat Cost) into the Ninetales ex, attached its second Water and used Binding Snow.

km3's choice: In 12 of 12 seeds: Water on the Benched Mega Sharpedo ex, then Surf with Lapras (70). The Vulpix stays a 60-HP Basic and the Ninetales ex stays in hand.

kx's choice: The same as km3 in 3 of 3 seeds.

Trace evidence: File /home/dacz8976/pgd/runs_kx3_trace/err_B-215203-t06.txt, 16 rounds per decision. kx made two decisions in each seed: the first action, then the action after the Water. At both decisions, in all three seeds, these all won 16 of 16 (score 1.000, lead 0.000, SE 0.000): evolving, Surf, each Water, ending the turn, and retreating into the Mega Sharpedo ex (the first step of his Turbo Shark line). The one exception was seed 2 after the Water: retreating Lapras into the Vulpix won 15 of 16 (0.938, lead -0.063, SE 0.063). No candidate beat km3's move, so kx kept it. Turn 8: positions_kx.json B-215203-t08.

Why it matters: The gain in his line comes from Turbo Shark. Its extra Water lets the Ninetales ex use Binding Snow on turn 8. After km3's Surf, turn 10 is the earliest, because Binding Snow needs 2 Water and the Ninetales ex would start turn 8 with none. Evolving on turn 6 is not what makes this possible, since Turbo Shark could have put the Water on the Vulpix. Evolving costs no Energy, though, and turns the 60-HP Benched Pokemon into a 150-HP one. His line did pay 2 Water to retreat Lapras. kx could not weigh any of this because every play-out was a win. In Dustin's three games (all won 3-0), km3's move won 16 of 16 in 96 of 176 kx decisions, and kx changed only one decision in those games. In games this one-sided, a planning edge like this can stay hidden from kx.

<details><summary>What the check corrected</summary>

- Trace numbers: the example says every candidate won 16 of 16 at both decisions in all three seeds. That is wrong for one candidate. In seed 2, at the second decision (after the Water), retreating Lapras into the Alolan Vulpix scored 0.938, which is 15 of 16 (lead -0.063, SE 0.063). The candidates it names (evolving, Surf, each Water, ending the turn) did all score 1.000 in all three seeds. So did retreating into the Mega Sharpedo ex, the first step of his Turbo Shark line.
- Why it matters: the turn-8 Binding Snow comes from Turbo Shark, not from evolving on turn 6. Turbo Shark puts its Water on a Benched Water Pokemon, and the Alolan Vulpix is one. So he could have evolved on turn 8 and still used Binding Snow that turn. Putting 'Evolving costs nothing' next to that claim suggests evolving is part of the gain. It isn't.
- Why it matters: it leaves out the cost of his line. Retreating Lapras (Retreat Cost 2) threw away 2 of its 3 Water. After his turn he had 3 Water in play (Lapras 1, Sharpedo 1, Ninetales ex 1). After km3's line he would have had 4 (Lapras 3, Sharpedo 1).
- 'Instead of turn 10' should say 'turn 10 at the earliest'. After km3's Surf line, the Ninetales ex enters turn 8 with no Energy and Binding Snow needs 2 Water, so turn 10 is the soonest, not a certainty.
- 'Any planning edge ... stays hidden' is too strong. In the other 80 of the 176 decisions, km3's move did not win every play-out, so kx could see differences there. Better: 'in games this one-sided, an edge like this can stay hidden from kx'.
- Turbo Shark's target is missing from his recorded plan, which stops at the attack. The turn-8 board shows where it went: Ninetales ex 1 Water, Lapras 1 Water (3 minus the 2 for the retreat), Wailord ex 250 to 180. So 'its extra Water goes onto the new Ninetales ex' holds, but only as an inference from that board.
- Checked and correct: the board, the hand, the 1-0 score, the Vulpix benched on turn 4 (t04 plan), the 3-0 win and Dustin as decision maker. km3 played 'Water on the Sharpedo, then Surf' in 12 of 12 seeds and kx did the same in 3 of 3. Each seed had 2 kx decisions of 16 rounds, all keeping km3's move as the tie. The turn-8 line (free retreat, second Water, Binding Snow) matches B-215203-t08. Across Dustin's three games there were 176 kx decisions: km3's move scored 1.000 in 96 and kx changed 1 (B-215203-t02, seed 2, Misty over Copycat). Card texts match lib/card.py: Turbo Shark [W] 70 plus a Water onto a Benched Water Pokemon; Binding Snow [WW] 80; Mega Sharpedo ex Retreat 0, 190 HP + Elegant Cape 30 = 220; Lapras A3 044 Surf [WWC] 70, Retreat 2.

</details>

### failure: B-215825-t06 (decision maker Dustin; exact list: True; milestone: preparing an attacker)

Situation: Game 215825 (Dustin's own decisions, won 3-0), game turn 6 (his third turn), score 0-0. His Active is an Alolan Ninetales ex (180 HP with Elegant Cape, 2 Water). Bench: Alolan Vulpix (60 HP, no Energy) and Mega Sharpedo ex (190 HP, no Energy; its Turbo Shark costs one Water). Hand: Lucky Ice Pop, Cyrus, Misty, Mega Sharpedo ex. The computer's Active is a Meowth (50 HP, 1 Water), with Frigibax, Arctibax (1 Water) and Squirtle on the Bench. None of them is damaged, so Cyrus has no target and Misty is the only Supporter he can use this turn.

Dustin: Water from the Energy Zone on the Alolan Vulpix, Misty on the Mega Sharpedo ex, then Binding Snow. The next turn's board shows one Water on each, so Misty gave one heads.

km3: in 12 of 12 seeds, Water on the Mega Sharpedo ex, then Binding Snow. It never plays Misty: its search scores Misty 1 point below ending the turn.

kx: the same as km3 in 3 of 3 seeds. It never switched.

Trace (err_B-215825-t06.txt; 16 play-outs per move, and every play-out drew the computer's real list): At the first decision, km3's Water on the Mega Sharpedo ex won 16, 16 and 14 of 16 (seeds 1, 2, 3). Playing Misty first won 16, 16 and 15. Dustin's Water on the Vulpix won 16, 16 and 14, the same as km3's move. In seed 3, Misty's lead is one play-out (+0.063, standard error 0.063), which is within the noise. Ending the turn without attacking and retreating into the Vulpix scored the same 15 of 16, and kx's own pick for the best move there was ending the turn. In seed 1, ending the turn with no attack at all won 16 of 16. At the second decision (after the Water on the Mega Sharpedo ex), Misty and Binding Snow tied in every seed (15, 16 and 16 of 16).

Why it matters: Misty had no competing use this turn, so km3's plan leaves a Supporter unused; the only cost of playing it is the card. Dustin used it. His line puts a sure Water on the Vulpix, and the Mega Sharpedo ex gets the one Water it needs only if the first flip is heads (half the time); in this game it was. km3's line makes the Mega Sharpedo ex ready for sure but leaves the Vulpix empty and Misty in hand. Doing both was also legal: Water on the Mega Sharpedo ex, then Misty. kx can't see any of this because from here nearly every move wins 14 to 16 of its 16 play-outs (km3 against km3), so an extra Water shows up as no gain. This shows kx missing a free resource. It does not prove Dustin's exact order was better.

<details><summary>What the check corrected</summary>

- Checked and correct: the board, hand, score (0-0), turn 6, 'won 3-0', decision maker Dustin and exact list all match positions_kx.json and blast_positions/bd_final.json. The card texts back it up: Alolan Ninetales ex is 150 HP plus 30 from Elegant Cape = 180, Mega Sharpedo ex is 190, Meowth B2 124 is 50, Frigibax is 60/60, Arctibax 90/90 and Squirtle B1a 70/70. Cyrus needs a damaged Benched Pokemon, so it has no target. Dustin's plan (Water on slot 1 = the Vulpix, Misty with target slot 2 = the Mega Sharpedo ex, then Binding Snow) matches the record. km3 played Water on the Mega Sharpedo ex then Binding Snow in all 12 seeds (runs_km3, AGREEMENT_TABLES row '215825 t6'). kx played the same in seeds 1-3. Every trace number quoted for seeds 1 and 2 and for the second decision is right, and there were 16 rounds.
- Wrong: 'Dustin's Water target (the Vulpix) also scored 1.000.' It scored 1.000 only in seeds 1 and 2. In seed 3 it scored 0.875, the same as km3's Water on the Mega Sharpedo ex.
- Misleading: in seed 3 the example sets Misty 0.938 against km3's 0.875 (+0.063, SE 0.063), which makes Misty look like the standout. Ending the turn with no attack and retreating into the Vulpix also scored 0.938. kx's own 'best move' in seed 3 was ending the turn (+0.062, SE 0.111, its reason line), not Misty. Misty's lead is one play-out out of 16 and within the noise.
- Overstated: 'every line wins all its play-outs.' In seed 3's first decision km3's move won 14 of 16 and Misty 15 of 16. In seed 1's second decision both won 15 of 16. Retreating into the Vulpix won 11 to 13 of 16. Better: 'nearly every move wins 14 to 16 of its 16 play-outs.' (The score is win 1, tie 1/2, loss 0, per playout_player.rs.) In seed 1, ending the turn with no attack at all won 16 of 16, which shows how saturated the scores are.
- Overstated: 'Dustin builds up two Pokemon this turn.' This depends on a coin. Misty gives nothing if the first flip is tails, which happens half the time. In that case only the Vulpix gets a Water and the Mega Sharpedo ex stays empty, which is worse for it than km3's line. In this game it worked: the turn-8 board shows one Water on the Vulpix and one on the Mega Sharpedo ex, so Misty gave one heads. That is read from the next board; the ledger's coin flips were not checked directly.
- Overstated: 'each heads is a Water on the empty Mega Sharpedo ex.' Turbo Shark costs one Water and Mega Sharpedo ex's retreat cost is 0, so only the first heads matters for it.
- Softened: 'Misty is free here.' It has no competing Supporter use this turn, which is correct. But it spends the card (Draft A has 2 Misty), so it costs only the card, not nothing.
- Worth adding: km3's search scores Misty 1 point below ending the turn (927 vs 928 before the attach, 1117 vs 1118 after), so km3 never plays it here. A line that does both was also legal: Water on the Mega Sharpedo ex, then Misty. After the Water, kx scored Misty the same as attacking at once in every seed. So kx's miss is the unused Misty, not where the turn's Water went. Dustin's exact order (Water on the Vulpix, gamble on the Sharpedo) is not shown to be better than km3's. No outcome here says who was right.

</details>

### failure: B-205731-t10 (decision maker Auto; exact list: True; milestone: preparing an attacker, managing a sacrifice)

Game 205731 (Auto, won 3-2), game turn 10, he leads 1-0. His Active is a Mega Sharpedo ex at 50 of 190 HP with 3 Water. If it is knocked out, the computer gets 3 points and the game. Bench: Alolan Ninetales ex (150 HP, 3 Water). Hand: Copycat, Alolan Ninetales ex, Misty, Alolan Vulpix. The computer has Mega Blastoise ex Active (230 HP, 3 Water) and holds 1 card.

Auto: bench the Vulpix, attach Water to it, retreat for free into the Ninetales ex, then Binding Snow. No Copycat. On turn 12 Auto used the Ninetales ex it kept to evolve that Vulpix.

km3 (12 seeds): retreat, bench the Vulpix, Water on it, then Binding Snow (7 seeds) or Copycat (5 seeds; the record stops at Copycat's draw).

kx (3 seeds):
- Seed 3 plays like km3, then Copycat. With the computer holding 1 card, that shuffles the Ninetales ex and Misty into the deck and draws 1.
- Seed 1 retreats, benches the Vulpix and uses Binding Snow without attaching any Energy, so the turn's Energy is discarded.
- Seed 2 puts the Water on the Mega Sharpedo ex just before retreating it and plays Misty on the Ninetales ex. Then it retreats, benches the Vulpix and uses Binding Snow.

Trace (/home/dacz8976/pgd/runs_kx3_trace/err_B-205731-t10.txt, 16 play-outs per move, with the computer's real list in all 16):
- Seed 3, at the Copycat decision: Binding Snow 0.625 v Copycat 0.313, a lead of +0.313 with SE 0.176, which is 1.8 SE. That is under the 2-SE bar, so km3's Copycat was kept.
- Seed 1, third decision: Binding Snow 0.813 v Water on the Vulpix 0.563, a lead of +0.250 with SE 0.112, which is 2.2 SE, so kx switched. Water on the Sharpedo or the Ninetales also scored 0.563.

Why it matters: Auto's line is better than both of these kx lines. Copycat here trades the Ninetales ex and Misty for one random card. Skipping the attachment throws away the turn's Energy.
- In seed 3 km3's Copycat mistake survives because the lead fell just short of the bar.
- In seed 1 kx avoided Copycat only by attacking before attaching. The likely reason: after any Water move, the play-out hands the rest of the turn to km3, and km3 sometimes goes on to play Copycat. It did in 5 of its own 12 seeds after the same Water. The trace does not record the play-outs, so this is the probable cause, not a recorded one.

kx only corrects km3 at the decision it is making, and only when the lead clears 2 SE. Mistakes km3 would make later in the same turn still pull down the scores of the moves before them.

<details><summary>What the check corrected</summary>

- Not verified as written because of the explanation in 'why it matters'. It says every Water line goes on into km3's Copycat, and that is not in the trace. The trace records only the score for each move, not what happened in the play-outs. It is also too strong. After the same Water on the Vulpix, km3's own 12-seed reference used Binding Snow in 7 seeds and Copycat in 5. In km3's seed 1 the two were almost tied (9904 v 9901). The defensible wording is that some of the Water play-outs probably go on into km3's Copycat, and that this is the likely cause, not a recorded one.
- 'Auto's line is clearly better here' needs narrowing and backing. kx's own numbers don't settle it. On Copycat the lead was 1.8 SE, under kx's bar. In seed 1 kx's play-outs actually scored Auto's next step (Water on the Vulpix, 0.563) below attacking at once (0.813). The case rests on the cards and the next turn. Copycat with the computer at 1 card swaps the Ninetales ex and Misty for one random card. On turn 12 Auto used the Ninetales ex it kept to evolve the Vulpix that got the Water. Skipping the attachment loses the turn's Energy, because Energy left unattached is discarded at the end of the turn. Nothing compares Auto's line with kx's seed 2 line, so the claim should cover only the Copycat line and the no-Energy line.
- km3_choice: in the 5 Copycat seeds the record stops at Copycat's draw. So 'Binding Snow (7) or Copycat (5)' should not read as if km3 never attacked after Copycat. That part isn't shown.
- kx seed 1: it attached no Energy at all that turn, not just 'no Water on the Vulpix'. Water on the Mega Sharpedo ex or on the Ninetales ex scored the same 0.563 as Water on the Vulpix.
- Minor: 'missed the bar with only 16 play-outs' implies more play-outs would have cleared it. Better: 'fell just short of the bar (1.8 SE against 2)'.
- Checked and correct: the board, hands, HP, Energy, points (1-0), the computer's 1 card, and Auto as decision maker with an exact list. Auto's recorded line: the Water target @2 is the Vulpix, and turn 12 shows the Vulpix with 1 Water and Auto evolving it with the kept Ninetales ex. km3's 7/5 split over 12 seeds, and all three kx seed plans. Trace numbers: seed 3 Copycat decision 0.625 v 0.313, +0.313, SE 0.176, kept. Seed 1 third decision 0.813 v 0.563, +0.250, SE 0.112, 2.2 SE, switched. Every decision used 16 rounds with the computer's real list in all 16. Card texts: Copycat; Mega Sharpedo ex retreat 0; Binding Snow; a Mega ex knockout is worth 3 points.

</details>

### failure: B-210952-t16 (decision maker Auto; exact list: True; milestone: preparing an attacker, adapting when the plan fails)

Failure. Position B-210952-t16: exact lists, and the decisions were made by Auto, not Dustin. Milestone: preparing an attacker, adapting when the plan fails.

Situation: Game 210952 (Auto played his side, lost 2-3), game turn 16, score 1-1. His Lapras's Surf knocked out a Wailmer on turn 14, then the Mega Blastoise ex knocked out Lapras. His Active is an Alolan Ninetales ex (150 HP, 2 Water). Bench: Carvanha (50 HP, 1 Water) and Mega Sharpedo ex (190 HP, 1 Water). Hand: Irida, Copycat, Alolan Ninetales ex, two Misty, Mega Sharpedo ex, Elegant Cape, Alolan Vulpix. The computer has Mega Blastoise ex Active (230 HP, 5 Water), with Baxcalibur (20 HP left) and Wailmer (100 HP, 2 Water) on the Bench.

What Auto did: benched the Vulpix, evolved the Carvanha into Mega Sharpedo ex, put the Water on the Vulpix, then used Binding Snow. That took the Blastoise from 230 to 150, and on the computer's next turn no Energy could go from its Energy Zone onto its Active Pokemon. Auto did not play Elegant Cape. On turn 18 Auto evolved that Vulpix into a fresh Alolan Ninetales ex.

km3: the same line in all 12 seeds, plus Elegant Cape on the Active Ninetales ex.

kx: in seeds 1 and 2 it used Binding Snow at once, so no Vulpix, no evolution and no Water this turn. Seed 3 kept the set-up, but put the Water on the Active Ninetales ex instead of the Vulpix, and the Cape on the Mega Sharpedo ex it had just evolved from Carvanha.

Trace: err_B-210952-t16.txt. Each move got 16 play-outs, and all 16 used the computer's real list.
- Seed 1, first decision: Binding Snow 0.188 v bench the Vulpix 0.000 (+0.188, SE 0.063, 3.0 SE).
- Seed 2, first decision: 0.125 v 0.000 (+0.125, SE 0.056, 2.2 SE). Every other first move scored 0.000 to 0.125.
- What those Binding Snow scores are made of: a win counts 1 and a tie counts half. Working back from the scores and SEs, Binding Snow won none of its play-outs. Its scores are 6 ties (seed 1) and 4 ties (seed 2) out of 16, most likely games that reached the 30-turn limit. Benching the Vulpix lost all 16.
- Seed 3, first decision: benching the Vulpix also lost all 16, but kx kept it because Water on the Active led with only 3 wins (1.9 SE, under the bar).
- Seed 3, second decision: Water on the Active (4 wins of 16) replaced km3's evolve (0 wins), +0.250, SE 0.112, 2.2 SE.
- Seed 3, fifth decision: Cape on the fresh Mega Sharpedo ex 0.688 v Cape on the Ninetales ex 0.125 (+0.563, SE 0.128, 4.4 SE).

Why it matters: benching the Vulpix now is what made a fresh Ninetales ex possible on turn 18, because a Pokemon can't evolve on the turn it is played. And a turn's Water that is not attached is gone. In seeds 1 and 2, kx gave up both for a move that won none of its 16 play-outs; its edge was a few more ties at the turn limit. The play-outs rate this position as nearly lost: km3's line lost all 16 in every seed, and no first move won more than 3. In that state, kx's switches here rest on a handful of ties or wins, not on a plan.

Seed 3's Cape choice is different. It was a strong signal, but the same Cape on the other Mega Sharpedo ex, which is identical, scored 0 of 16. So the gain comes from how km3 plays out the rest of the game, not from the Cape. It is not counted as part of this failure.

<details><summary>What the check corrected</summary>

- 'kx drops both because the play-outs win 2-3 more times out of 16' is wrong. A play-out scores 1 for a win, 1/2 for a tie and 0 for a loss (playout_player.rs). Benching the Vulpix lost all 16 play-outs in both seeds. Working back from the score and the SE, there is exactly one fit for Binding Snow at once: in seed 1 it scored 0.188 with SE 0.063, which is 0 wins and 6 ties. In seed 2 it scored 0.125 with SE 0.056, which is 0 wins and 4 ties. The ties are most likely games that reached the 30-turn limit. So kx switched to a move that won none of its 16 play-outs.
- 'the fresh Ninetales ex he evolved on turn 18' credits Dustin. positions_kx.json lists the decision maker as Auto at both turn 16 and turn 18, so Auto evolved it, not Dustin.
- 'Zone attachment blocked' overstates Binding Snow. The card text (lib/card.py) only stops the opponent attaching Energy from their Energy Zone to their Active Pokemon. Their Bench can still get Energy: the Wailmer went from 2 to 3 Water by turn 18, while the Blastoise stayed at 5.
- The trace evidence says 'first decision', which is true only for seeds 1 and 2. Seed 3 made six decisions that turn. First: it kept benching the Vulpix, which also lost all 16. Water on the Active led with 3 wins (+0.188, SE 0.101), but at 1.9 SE that is under the bar. Second: Water on the Active (4 wins) replaced km3's evolve (0 wins), +0.250, SE 0.112, 2.2 SE. This switch was missing from the example. The Cape numbers (0.688 v 0.125, +0.563, SE 0.128) come from the fifth decision, and that lead is 4.4 SE.
- Seed 3's Cape choice does not fit 'rests on a handful of wins'. It was the strongest signal in the file: about 7 to 11 wins of 16, against 0 to 2 for Cape on the Ninetales ex. But the same Cape on the other Mega Sharpedo ex, which is identical (190 HP, 1 Water), scored 0 of 16. So the gain reflects how km3 plays out the rest of the game, not the Cape itself. It should not count as part of the failure. 'In near-lost positions...' should be limited to this position and seeds 1 and 2.
- Minor: after the evolution there are two Mega Sharpedo ex on the Bench. kx put the Cape on the one it had just evolved from Carvanha. Seed 3 also leaves the Vulpix with no Water, so a turn-18 Ninetales ex would start empty.
- Checked and correct: the board, the hand and Auto's turn-16 line (bench Vulpix, evolve Carvanha, Water on the Vulpix, Binding Snow, no Cape). The score was 1-1: Surf knocked out a Wailmer on turn 14, then the Blastoise knocked out Lapras; Triple Bombardment does 130 and was the only attack that could knock out a 110-HP Lapras. The game was lost 2-3. km3 played the same line plus Cape on the Active in 12 of 12 seeds. kx's plans per seed and all the quoted scores, SEs and z values match the trace. Every decision used 16 rounds with no failed rounds, and all 16 play-outs used the computer's real list (extra:BL). Card texts: Binding Snow does 80, Blastoise goes 230 to 150, and Elegant Cape gives a Stage 1 Pokemon +30 HP. A Pokemon can't evolve on the turn it is played. In the engine, an unattached Zone Energy is replaced next turn.

</details>

### coordinated_plan: B-214254-t10 (decision maker Dustin; exact list: True; milestone: managing a sacrifice)

Position B-214254-t10. Exact lists; Dustin's own decision; milestone: managing a sacrifice.

Situation: Dustin v the fixed computer deck (Mega Blastoise ex / Wailord ex). His turn 5 (game turn 10); he leads 1-0. His Active is the Elegant Cape Mega Sharpedo ex at 120 of 220 HP with 1 Water. On the Bench: a fresh Mega Sharpedo ex (190 HP, 2 Water) and an Alolan Vulpix (60 HP) with 4 Water. Mega Sharpedo ex has no Retreat Cost. The computer's Active Wailord ex (250 HP, 4 Water) hits for 100 a turn with Wondrous Waves. Soothing Shore is in play: at the end of each player's own turn, it heals 20 from each of their Pokémon with Water attached. Hand: Irida, Lucky Ice Pop, Misty.

What he did: he kept the damaged Mega in front and healed it. He played Lucky Ice Pop (heads, back to hand), Lucky Ice Pop again (tails) and Irida (up to 200). He put the turn's Water on the Mega, used Turbo Shark (Wailord to 180) and sent Turbo Shark's Water to the Vulpix, its 5th. Next turn he played Professor's Research and Poké Ball and evolved that Vulpix into Alolan Ninetales ex. He retreated the Mega for free, brought the Ninetales ex in, and used Binding Snow. Binding Snow then kept Energy Zone attachments off the computer's Active every turn, and he won 3-0 without losing a Pokémon.

km3: the same line in all 12 seeds. It plays Irida first, then Lucky Ice Pop as often as the coin allows: twice in 9 seeds; in the other 3 the first flip was tails. Then Turbo Shark, with its Water to the Vulpix. It skips the turn's own Water. Its order (Irida, then the Pops) ends at the same 200 HP as his (the Pops, then Irida).

kx: km3's line in 3 of 3 seeds: one Pop in seed 1, where the first flip was tails, and two in seeds 2 and 3. It changed nothing at any of its 14 decisions.

Trace (err_B-214254-t10.txt; 16 play-outs per move; a move's score is its share of play-outs won, a tie counts half): sending Turbo Shark's Water to the Vulpix or to the other Mega Sharpedo ex scored exactly the same in all three seeds: 0.469 v 0.469, 0.813 v 0.813, 0.688 v 0.688. Every play-out ended the same way either way. Retreating (for free) into the fresh Mega instead of keeping the damaged one in front was offered at 11 decisions. It scored between -0.19 and +0.16 of km3's move and never passed 2 standard errors. Of the retreats, only the obvious blunder scored clearly below: retreating into the 60-HP Vulpix, at -0.50 to -0.84. Ending the turn early, without Turbo Shark, also scored more than 2 standard errors below km3's move at 5 of the 11 decisions where it was offered (as low as -0.56).

Why it matters: this is the kind of plan that item 4 of the play-out pilot's approval (Oct 2) asks for: charge a Benched attacker, keep the damaged Pokémon in front, promote at the right time. kx kept the plan only because km3 already chose it. The play-outs could not tell finishing the Vulpix from feeding the second Mega, or keeping the damaged Mega in front from retreating into the fresh one. Verdict: about equal. The play-outs saw no difference, but they play km3 on both sides, so a real difference could still be there unseen. km3's moves had win shares of 0.47-0.94 (about 0.70 on average), so the game was leaning his way, and part of the tie may be that it was largely decided.

<details><summary>What the check corrected</summary>

- km3_choice misreads a coin flip as a choice. km3 played the same line in all 12 seeds. In seeds 1, 4 and 9 the first Lucky Ice Pop came up tails: in runs_km3/err_B-214254-t10.txt, Lucky Ice Pop is missing from the next step's candidates. So there was no second Pop to play. The order also differs from his: km3 plays Irida first and then the Pops; he played the Pops first and then Irida. Both orders end at 200 HP.
- trace_evidence overstates 'Only the obvious blunder ... scored clearly below'. Ending the turn early (EndTurn) also scored more than 2 standard errors below km3's move at 5 of the 11 decisions where it was offered. At seed 1's first decision it scored -0.563 with a standard error of 0.157. The word 'only' is true only among the retreat choices.
- 'Switching into the fresh Mega' is a Retreat in the trace (Retreat(1)), and it costs nothing because Mega Sharpedo ex has no Retreat Cost (lib/card.py). Name it as the game does: retreating, for free.
- 'Verdict: about equal (hidden)': '(hidden)' is not defined in any report file. Spell it out in plain words.
- 'amendment 4' is ambiguous. In the repo, 'kph amendment 4' is the Sept 28 coverage-row ruling. The one meant here is item 4 of the Oct 2 approval in rl/results/planning_pilot_design_2026-10-02/DESIGN.md section 9: 'charge a Benched attacker, keep a sacrificial Active, promote at the right time'. Name it that way.
- Missing context (not an error): Soothing Shore is in play. At the end of each player's own turn it heals 20 from each of their Pokémon with Water attached. That is why the Mega went from 200 to 220 at the end of his turn, Wailord came back from 180 to 200, and a third Pop would have done nothing.
- Checked and correct: the board, hand, points and turn (positions_kx.json). The card texts: Mega Sharpedo ex has 190 HP, +30 from Elegant Cape = 220, and Retreat Cost 0. Wailord ex has 250 HP and Wondrous Waves for 4 Water does 100. Turbo Shark does 70 and attaches an Energy Zone Water to a Benched Water Pokémon. Lucky Ice Pop heals 20 and comes back to hand on heads. Irida heals 40. Binding Snow blocks Energy Zone attachments to the Active. The game ledger matches his turn: heads, then tails, 120 to 140 to 160, Irida to 200, Water on the Mega, Wailord 250 to 180, 5th Water to the Vulpix. His next turn matches too: Research, Poké Ball, evolve, a free retreat (paid 0), Binding Snow. On computer turns 13-21 every Energy Zone attachment went to the Bench. Final result 3-0. km3's 9 of 12 modal line matches. kx: 14 decisions, none changed. The Turbo Shark Water scores are identical in all three seeds: 0.469, 0.813, 0.688, each with a standard error of 0. Retreat(1) was offered 11 times, ranged -0.188 to +0.156, and was never more than 1.5 standard errors away. Retreat(2) ranged -0.50 to -0.84. km3's moves scored 0.47-0.94. Scoring is 1 for a win, 1/2 for a tie, 0 for a loss (playout_player.rs). All 16 play-outs used the computer's exact list.

</details>

### coordinated_plan: B-214254-t06 (decision maker Dustin; exact list: True; milestone: preparing an attacker)

Position B-214254-t06: the fixed computer deck, exact lists for both sides, Dustin's own decisions, milestone 'preparing an attacker'.

Situation: same game, his turn 3 (game turn 6), 0-0. Active: Mega Sharpedo ex with Elegant Cape (220 HP, 1 Water). Bench: Carvanha (1 Water) and Alolan Vulpix (1 Water). Hand: Irida, Lucky Ice Pop. The computer's Meowth is Active.

What Dustin did: he put the turn's Water on the Benched Vulpix, then used Turbo Shark, whose Water also went to the Vulpix (3 Water). On turn 8 he evolved the Carvanha into a second Mega Sharpedo ex and gave it the turn's Water. Turbo Shark knocked out Meowth, and its Water went to the Vulpix (4). Turbo Shark on turn 10 gave the Vulpix its 5th Water. On turn 12 he evolved it into Alolan Ninetales ex and moved it Active (Mega Sharpedo ex retreats for free). It used Binding Snow on turns 12 and 14, then retreated on turn 16 paying 2 Water and stayed on the Bench with 3 Water. The game was won by a second Alolan Ninetales ex, from a Vulpix he benched on turn 12. It did all the damage to Mega Blastoise ex and knocked it out on turn 22 after Cyrus.

km3: Turbo Shark at once in 12 of 12 seeds. The turn's Water is never attached, and unattached Energy is discarded at the end of the turn. Turn 8 was the same in 12 of 12: evolve, Turbo Shark, no Water. km3's own scores tie every Water option with Turbo Shark exactly, and it picks the attack.

kx: the same as km3 in 3 of 3 seeds on both turns, so the turn's Water is lost each time.

Trace, turn 6, Water on the Vulpix against attacking at once:
- 0.938 against 0.938, with the two moves giving the same result in each of the 16 paired play-outs
- 0.750 against 0.750
- 0.750 against 0.688 (+0.06, 1 standard error)

Turn 8, before the evolution: in seed 3, Water on the Vulpix led evolving first by +0.125 (about 1.5 standard errors), which is within the noise. After the evolution, the attack and all three Water targets scored 0.563, 0.375 and 0.531 in the three seeds, with the moves matching in every play-out.

Across the 57 computer-deck positions kx ran, km3 wanted to attack with the turn's Water still unused at 48 decisions:
- every Water option tied the attack exactly in 38
- one led within the noise in 3
- the Water options were level or behind in 7
- none ever passed 2 standard errors

Why it matters: the play-outs can't tell putting Water down first apart from attacking at once, and Dustin's own game agrees. Without the turn-6 Water, Turbo Shark on turns 6, 8 and 10 would still have given the Vulpix 4 Water by turn 12. That is enough for both Binding Snows and the turn-16 retreat, and that Ninetales ended the game with 3 Water it never used. His turn-8 and turn-10 Water went onto Mega Sharpedo ex that never needed a second Water. Verdict: hidden (equal). kx copies km3's habit of leaving the turn's Energy unused, but in this game the extra Water was never needed.

<details><summary>What the check corrected</summary>

- Wrong: 'By turn 10 the Vulpix had 5 Water and became the Alolan Ninetales ex that won the game.' The positions show the Vulpix had 4 Water at the start of turn 10. Its 5th Water came from that turn's Turbo Shark, and it evolved on turn 12, not by turn 10. It also did not win the game. This first Ninetales used Binding Snow on turns 12 and 14 against Wailord ex, which was never knocked out. On turn 16 it retreated, paying 2 Water (his discarded Energy went from 1 to 3), and it stayed on the Bench with 3 Water until the end. The game was won by a second Alolan Ninetales ex, evolved on turn 16 from a Vulpix he benched on turn 12. That Ninetales did all the damage to Mega Blastoise ex (230, 170, 110, 30 HP across turns 16 to 22) and knocked it out on turn 22 after Cyrus. Score: 1 point for Meowth plus 3 for the Mega ex.
- The 'why it matters' part leans on a use of the Water that his own game didn't need. Without the turn-6 Water, Turbo Shark on turns 6, 8 and 10 would still have given the Vulpix 4 Water by turn 12. That covers both Binding Snows (cost 2 Water) and the turn-16 retreat (cost 2), and the first Ninetales finished the game with 3 Water it never used. His turn-8 and turn-10 Water also went onto Mega Sharpedo ex that never needed a second Water (Turbo Shark costs 1 Water and retreating is free). So his game fits the first explanation, that the extra Water doesn't change the game. 'km3 never uses it the way Dustin did' is not shown. He himself also left the turn's Water unused on turns 20 and 22.
- 'The play-outs give it no value' says too much. There were small leads that sit within the noise: +0.06 on turn 6 seed 3, and on turn 8 seed 3 before the evolution, where Water on the Vulpix led evolving first by +0.125 (about 1.5 standard errors). The evidence only names the numbers after the evolution, which are correct, and leaves this one out. Better wording: no lead the play-outs can tell apart from noise.
- Wording: '(the same result in all 16 play-outs)' means the two moves gave the same result in each of the 16 paired play-outs, not that all 16 play-outs ended the same way. The score is 0.938, not 1.
- Checked and correct: the board, hand and score (positions_kx.json, B-214254-t06 and t08: Dustin, exact lists, preparing an attacker). Mega Sharpedo ex is 190 HP plus 30 from Elegant Cape, so 220. His turns 6 and 8 are as described, and Meowth was knocked out on turn 8 (points 0 to 1 by turn 10). km3 played Turbo Shark at once in 12 of 12 seeds on turn 6, and evolved then used Turbo Shark without Water in 12 of 12 on turn 8; its own scores tie the three Water options and Turbo Shark exactly. kx did the same in 3 of 3 seeds on both turns. All the trace numbers match. The rule that unattached Energy is discarded at the end of the turn is in RULES_FOR_AGENTS.md. The totals for the 57 computer-deck positions (48 decisions: 38 exact ties, 3 small leads within the noise, 7 level or behind, none past 2 standard errors) recount exactly.

</details>

### adapting: B-210952-t16 (decision maker Auto; exact list: True; milestone: adapting when the plan fails; preparing an attacker)

Adapting, B-210952-t16 (exact lists both sides, decision maker Auto; milestones: preparing an attacker, adapting when the plan fails).

Situation: Auto's game (the game's own bot; it lost this one 2-3), game turn 16, 1-1. Lapras, its attacker, was knocked out on the computer's last turn. Active: Alolan Ninetales ex (150 HP, 2 Water). Bench: Carvanha (50 HP, 1 Water) and Mega Sharpedo ex (190 HP, 1 Water). The computer's Mega Blastoise ex (230 HP, 5 Water) is Active. Hand: Alolan Ninetales ex, Alolan Vulpix, Copycat, Elegant Cape, Irida, Mega Sharpedo ex, Misty x2. 2 cards left in its deck.

What Auto did: rebuilt. It benched the Vulpix, evolved the Carvanha into a second Mega Sharpedo ex, put Water on the new Vulpix and used Binding Snow (Blastoise to 150). On turn 18 it evolved that Vulpix into Ninetales ex, played Cyrus, retreated the 20-HP Ninetales, and Turbo Shark knocked out Baxcalibur (2-1). On turn 19 Triple Bombardment, with 6 Water, also hit two Benched Pokémon and knocked out the old Ninetales ex (back to 40 HP after Turbo Shark's Water and Soothing Shore's heal). Auto lost 2-3.

km3: Auto's line in 12 of 12 seeds, plus Elegant Cape on the Active Ninetales ex.

kx: In seeds 1 and 2, Binding Snow at once, with nothing benched, nothing evolved and the turn's Water unused. In seed 3, the rebuild, but with the Water on the Active Ninetales ex and the Cape on the Mega Sharpedo ex it had just evolved from the Carvanha.

What the trace shows (err_B-210952-t16.txt): Benching the Vulpix (Auto's and km3's first move), with km3 playing on, lost all 16 play-outs in every seed (0.000). So did 8 of the 11 other first moves, evolving the Carvanha among them. Attacking at once scored 0.188, 0.125 and 0.094. It replaced the bench move in seeds 1 and 2 (3.0 and 2.2 standard errors). In seed 3 the best first move was the Water on the Active Ninetales ex (0.188, 1.9 standard errors), ahead of the attack (0.094). Both were within the noise, so kx kept the bench move. kx then changed km3's finish twice. First it put the Water on the Active Ninetales ex instead of evolving first (0.250 against 0.000, 2.2 standard errors). Four decisions after the bench, it put the Cape on the new Mega Sharpedo ex instead of the Active Ninetales ex (0.688 against 0.125, +0.56, 4.4 standard errors). The Cape on the other Mega Sharpedo ex scored 0.000 in those same play-outs, though it is the same card with the same 190 HP and 1 Water. So the 0.688 says more about how km3 plays on from there than about the Cape's 30 HP. At the last decision, the rebuild's Binding Snow scored 0.438.

Why it matters: This is a direct case, inside one turn, of km3's own follow-up making a good first move look bad. The play-outs judge 'bench the Vulpix' by how km3 finishes the turn: in km3's own run, the Cape on the Active Ninetales ex and the Water on the new Vulpix. That finish lost every play-out. In seed 3 kx changed both parts, and the rebuild scored 0.44 to 0.69. In seeds 1 and 2 kx never got that far and attacked at once, which scored 0.13 to 0.19. These numbers come from different seeds and different sampled worlds, so they are not a paired comparison. Verdict: below, because of km3's later moves rather than the bench move itself. The basis is seed 3's later play-outs; Auto's own finish (Water on the Vulpix, no Cape) was never played out.

<details><summary>What the check corrected</summary>

- Checked and correct: the board, hand, 2-card deck and 1-1 score (positions_kx.json and out_B-210952-t16.jsonl). Lapras was knocked out on turn 15. Auto's recorded plan was bench the Vulpix, evolve the Carvanha, Water to the Vulpix, Binding Snow. Turns 17 to 19 match the Codex TURN_TABLE: Blastoise 150 after Binding Snow, healed to 170. The old Ninetales ex was at 20 HP on turn 18, then 40 after Turbo Shark's Water and Soothing Shore's heal, and was knocked out by the Bench hit on turn 19. km3 played Auto's line plus Cape on the Active in 12 of 12 seeds, both in runs_km3 and in the repo's raw folder. kx's plans for seeds 1 to 3 match. A score of 0.000 means 16 losses (the code scores win 1, tie 1/2, loss 0; 16 rounds, 0 failed). The scores 0.188, 0.125 and 0.094, the 3.0 and 2.2 standard errors, Cape 0.688 against 0.125 (+0.563, 4.4 standard errors) and 'four decisions later' all match the KX_TRACE lines. Card texts checked: Elegant Cape (+30 HP to a Stage 1), Binding Snow, Triple Bombardment, Soothing Shore, Turbo Shark, Cyrus.
- Seed 3 reason is wrong. kx's best move at the first decision was not the attack. It was putting the turn's Water on the Active Ninetales ex: 0.188, +0.188 over the bench move, 1.9 standard errors. The attack led by only +0.094 (also 1.9 standard errors). kx only tests the best move against km3's, so the noise rule applied to the Water move, not the attack.
- 'The Cape on the Benched Mega Sharpedo ex' points to the wrong Pokémon. The situation lists one Benched Mega Sharpedo ex (the original, 190 HP). kx put the Cape on the other one, the Mega Sharpedo ex it had just evolved from the Carvanha (slot 1). The Cape on the original Mega Sharpedo ex scored 0.000 in the same 16 play-outs. Both are the same card with 190 HP and 1 Water, so the 0.688 reflects how km3 plays on from there, not the Cape's +30 HP itself.
- 'km3's later Cape placement made it lose every play-out' overstates. km3's finish of the turn had two parts kx later changed: the Water on the new Vulpix and the Cape on the Active. In seed 3 kx's first change was the Water, onto the Active Ninetales ex (0.250 against km3's 0.000, 2.2 standard errors). After that change, km3's Cape on the Active scored 0.125, not 0. Also, the play-outs are not traced, so km3's moves inside them are inferred from its own plan. And bench-first was not singled out: 8 of the 11 other first moves (evolve, end turn, Misty, Cape, both retreats, Water to either Benched Pokémon) also scored 0.000 in every seed.
- 'A line worth roughly a quarter of the rebuild' overstates. It sets seeds 1-2's first-decision attack (0.188, 0.125) against the best of four candidates at seed 3's fifth decision (0.688). Those come from different seeds, different decisions and different sampled worlds, so it is not a paired comparison. At seed 3's last decision the rebuild's own Binding Snow scored 0.438. Better: 0.13-0.19 against 0.44-0.69, not paired.
- 'The one direct case' is not checked. A scan of all kx traces found 3 other positions with the same split: first move kept in one seed and replaced in others, then changed later in the turn in the kept seed (B-205731-t02, B-205731-t10, D3-022135-t07). They are weaker, but they mean 'the only case' can't be claimed. 'Hiding' is also jargon for Dustin; say it plainly.
- The verdict 'below' needs its basis stated. Auto's own finish (Water on the Vulpix, no Cape) was never played out. Only km3's finish (with the Cape on the Active) was, and it scored 0. The case for 'below' rests on seed 3's later, unpaired play-outs.

</details>

### coordinated_plan: B-205731-t08 (decision maker Auto; exact list: True; milestone: preparing an attacker; managing a sacrifice)

Coordinated plan, B-205731-t08 (exact lists on both sides; decision maker: Auto; milestones: preparing an attacker, managing a sacrifice).

Situation: Auto's game (won 3-2), game turn 8, Auto leads 1-0. Auto's Active is Mega Sharpedo ex at 100 of 190 HP with 2 Water. On the Bench is Alolan Vulpix (60 HP, 2 Water). The computer's Active is Baxcalibur (90 of 140 HP, 3 Water), with Wartortle and Wailord ex on its Bench. The computer's Stadium, Soothing Shore, is in play: at the end of each turn, that player heals 20 from each of their Pokemon that has Water attached. Auto's hand: Alolan Ninetales ex x2, Copycat, Irida, Lucky Ice Pop, Misty.

What Auto did: kept the damaged Mega in front. It evolved the Benched Vulpix into Alolan Ninetales ex, then played Lucky Ice Pop and Irida (the Mega went from 100 to 160). It put Water on the Mega, and Turbo Shark took Baxcalibur to 20, with Turbo Shark's Water going onto the Ninetales (now 3 Water). Soothing Shore healed the Mega to 180 at the end of the turn. On turn 9 it took 130, down to 50. On turn 10 Auto benched a new Vulpix and gave it Water. It then retreated the Mega for free (its retreat cost is 0) into the 3-Water Ninetales ex and used Binding Snow.

km3's choice, in 12 of 12 seeds: retreat into the Vulpix now, play Irida, evolve the Vulpix in the Active Spot, then Binding Snow. It attaches no Energy that turn.

kx's choice: km3's line in 3 of 3 seeds. It never switched.

What the trace shows (err_B-205731-t08.txt, seeds 1-3, four decisions per seed):
- First decision: every move except Copycat won 16 of 16 play-outs in all three seeds, even ending the turn at once. Copycat won 13 or 14 of 16. Auto's first move (evolve on the Bench) and km3's retreat both won 16 of 16.
- The later decisions were not all ties. After the retreat, ending the turn or attacking with the Vulpix's Gnaw won 14 of 16, and Copycat won 4 to 7. After Irida, ending the turn or Gnaw won 11 to 13 of 16.
- Only at the attack did every choice win 16 of 16.
- km3's own move won 16 of 16 at all 12 decisions.
- All the play-outs used the computer's exact list.

Why it matters: this shows the third reason a plan can look equal. In the play-outs the game is already won: with km3 playing both sides, every sensible first move wins all 16, and only Copycat (which shuffles away both Ninetales ex) or stopping early loses any. So nothing can be read about which plan is better. Also, kx tests only the first move. After Auto's evolve-on-the-Bench, km3 played the rest of that turn, so Auto's full line (Mega stays in, Turbo Shark) was never played out as a whole. The real game was much closer, 3-2: the computer knocked out a Ninetales ex on turn 13. That fits the known caveat that kx's play-outs have km3 playing the computer's side. Across the computer-deck positions, km3's move won 16 of 16 at 197 of 411 kx decisions. At 108, every move scored exactly the same, 94 of those at 16 of 16.

<details><summary>What the check corrected</summary>

- The trace says 'every later decision was the same'. That is false. err_B-205731-t08.txt has 4 kx decisions per seed (12 in all). Only the first and the last (the attack choice) were full ties. At the 2nd decision (after the retreat), End Turn and the Vulpix's Gnaw won 14 of 16, and Copycat won 7 of 16 (seed 1) or 4 of 16 (seeds 2 and 3). At the 3rd decision (after Irida), End Turn and Gnaw won 11 to 13 of 16. What does hold: km3's own move won 16 of 16 at all 12 decisions, kx never switched (changed=false, reason "km's move has the best play-out score"), and all 16 play-outs used the computer's exact list (extra:BL, 1 of 1 consistent).
- 'km3 v km3 wins every play-out from here whatever kx does' overstates it. At the first decision Copycat won only 13 or 14 of 16, and at later decisions ending the turn early, Gnaw and Copycat lost play-outs. The accurate claim: every sensible move wins all 16, and only Copycat (which shuffles away both Ninetales ex) or stopping early loses any.
- The HP arithmetic doesn't add up as written: 160 minus 130 is 30, not 50. The missing step is the computer's Stadium, Soothing Shore (B4 154), which is in play: at the end of each turn, that player heals 20 from each of their Pokemon with Water attached. So the Mega went to 180 at the end of turn 8, then took 130 on turn 9, leaving 50 (it shows 50 HP with 3 Water at B-205731-t10). The situation should mention the Stadium.
- Baxcalibur's '90 HP' is what it has left. Its maximum is 140 (lib/card.py), so say 90 of 140, the same way the Mega's HP is given.
- Add that kx scores only the first move, with km3 playing out the rest. Auto's 'evolve on the Bench' scoring 16 of 16 means: that first move, followed by km3's own play for the rest of the turn. Auto's full line (Mega stays Active, Lucky Ice Pop, Irida, Water on the Mega, Turbo Shark) was never played out as a whole.
- Minor, accurate addition: km3's line (and kx's) attaches no Energy that turn. The plan ends with Binding Snow, and at the attack decision the Attach options also tied at 16 of 16. Auto did attach its Water (to the Mega).
- The 108 count is correct but needs a note: at 108 of 411 computer-deck decisions every move scored exactly the same, and 94 of those ties were at 16 of 16 (the other 14 were ties at a lower score). The 197 of 411 is correct.
- Checked and correct: the board, the hand and the 1-0 score (positions_kx.json, B-205731-t08). Auto's turn 8 plan matches his_plan: Evolve Ninetales ex on Bench slot 1, Lucky Ice Pop, Irida, Water to the Mega, Turbo Shark. 100+20+40=160, and 90-70=20 for Baxcalibur, per the card texts. The turn 10 plan matches: Place Vulpix, Water to slot 2, Retreat into Ninetales ex, Binding Snow. The retreat is free because Mega Sharpedo ex's retreat cost is 0. The Ninetales ex knockout between turns 12 and 14 matches (points 1-2 at t14), and the game was won 3-2. km3 picked Retreat:1 then Irida, Evolve at slot 0, Binding Snow in 12 of 12 seeds (runs_km3 and AGREEMENT_TABLES). kx's plan was identical in seeds 1-3. At the first decision, every move except Copycat won 16 of 16 in all three seeds, including End Turn.

</details>


## The readers' summaries (first drafts; where they differ from the checked examples above, the checked wording wins)

### Examples reader

kx changed km3's move on 45 of about 1,355 decisions it traced (about 3%). 24 of those were on the computer-deck positions (the B- positions), and 18 of the 24 came from one game: 210952, the only one Auto lost. Elsewhere the play-outs are nearly always wins. On Dustin's three 3-0 games, km3's move won 16 of 16 play-outs in 96 of 176 decisions, and kx changed only one. Seeds are 1-3; the report's "/12" means out of 3.

I found 4 improved decisions and 6 failures.

**Improved:**
- **B-210952-t18 (the best one, real):** kx plays Misty instead of Cyrus and keeps the Mega Blastoise ex Active under Binding Snow. That stops the 6th Water, and with it the Triple Bombardment Bench damage that knocked out the 20-HP Ninetales ex and lost the real game on the next turn. Lead 3.1 to 5.0 standard errors on all 3 seeds.
- **B-205731-t02, seed 3:** Water then Sharp Fang, exactly Auto's turn, instead of km3's Copycat (2.1 SE).
- **B-215203-t02, seed 2:** Misty, which is Dustin's Supporter, instead of Copycat (2.2 SE), but kx aimed it at the Carvanha.
- **LR-200654-t06 (APPROXIMATE, no verdict):** Hyper Ray where km3 sets up the attacker and then ends the turn.

**Failures (all exact-list B- positions):** three mechanisms, mostly the first two.
- **Saturation:** when every move wins all 16 play-outs, kx falls back to km3's move. B-215203-t06: Dustin evolves the Vulpix so his attacker hits a turn sooner. B-215825-t06: Dustin uses a free Misty.
- **km3's later mistakes leak into every play-out:** the play-outs run the rest of the turn with km3, so its later Copycat or Cyrus drags down every move except ones that end the turn or use up the Supporter. kx therefore picks "end the turn" (B-205731-t02 seed 2: a bare Carvanha, no Water, no attack). When the lead misses 2 SE it keeps km3's bad Copycat (B-205731-t10 seed 3: Copycat with the computer holding 1 card, lead 1.8 SE).
- **Nearly lost positions:** kx switches on 2-7 extra wins out of 16. B-210952-t14: retreat then pass, giving up a free knockout and the turn's Energy. B-210952-t16: attacks at once and drops the Vulpix that became turn 18's attacker.

**On your question: yes, something else is running.** WSL shows a kx3 strength run (`rl/strength/strength_prereg.py`, output folder `rl/results/strength_2026-10-04_kx3_v_k3`). It has been going about 14 minutes, is in its selfcheck step (`/home/dacz8976/kx2/strength selfcheck`, 12 games) and is using about 12 cores. This analysis only read files and did not touch it.

My scripts are in `C:\Users\dacz8\AppData\Local\Temp\claude\C--Users-dacz8-Projects\1b119d13-736d-4588-ba63-0e9ef1756970\scratchpad\` (`kx_scan.py`, `kx_detail.py`, `kx_human.py`, `kxo_changes.py`, `kxo_sat.py`).

### Coordinated-plan reader (DESIGN.md amendment 4)

On the question you asked: yes, something else is running. A strength run is going on the laptop: rl/results/strength_2026-10-04_kx3_v_k3, started by strength_prereg.py. When I checked, it had been going about 10 minutes and was in its kx3 self-check (Altaria v Suicune, 12 games), using about 12-13 cores. My job only read files and ran small Python scripts, so it started and stopped nothing and didn't get in that run's way.

Answer to amendment 4: there are signs of hiding, no sign of seeing, and too few usable cases to say how often hiding happens across turns.
- **Seeing.** In none of the computer-deck positions (exact lists, so they can carry a verdict) did the first move of Dustin's or Auto's multi-turn plan score clearly above km3's move.
- **Plan steps that differ from km3 score level.** Examples: putting the turn's Water on the Benched Vulpix that later becomes the attacker, sending Turbo Shark's Water to the Vulpix, keeping a damaged Mega in front. These usually score exactly level, often with the same result in all 16 play-outs. On the 57 computer-deck positions kx ran, there were 48 decisions where km3 attacked with the turn's Water still unattached (unattached Energy is discarded at the end of the turn). In 38 of them, every Water option gave exactly the same results as attacking; none led by 2 standard errors. kx never attached, so it inherits km3's habit of wasting the turn's Energy.
- **Hiding, seen directly once, inside a single turn (B-210952-t16).** km3's own later move in the play-outs (Elegant Cape on the Active Ninetales ex) made "bench the Vulpix" lose all 16 play-outs, so kx dropped the development in 2 of 3 seeds. In the third seed kx kept it and fixed the Cape itself, and that line scored about 0.69, against 0.09-0.19 for the move it picked. A smaller case of the same kind: in B-205731-t10 seed 1, km3's continuation after attaching played Copycat into a 1-card opposing hand, so kx attacked without attaching instead.
- **Across several turns, hiding can't be told apart from two other explanations.** Either the step truly matters little (Turbo Shark keeps feeding the Vulpix anyway), or the game is already decided.
- **Decided games swamp the positions.** Dustin's three computer-deck games are 3-0 wins. From most of these positions km3 v km3 wins every play-out whatever the move: of 411 kx decisions, km3's move won 16 of 16 in 197, and every move tied exactly in 108. That includes B-205731-t08 and B-215203-t06/t08, two of the plan positions, where nothing can be read.

Smaller points:
- The 2-standard-error switch rule picks the best of up to 12 noisy candidates, so some switches are probably noise.
- Where the game was really in doubt (Auto's 2-3 loss, 210952), kx switched more often and the same way in all 3 seeds. At t10 it retreated Lapras and went to Mega Sharpedo ex (+0.38 to +0.44, 2.4-3.4 SE). At t18 it played Misty instead of Cyrus; Auto's Cyrus line is the one that lost the game.
- The descriptive positions (approximate lists, no verdict) point the same way.
  - A-115323-t09: Dustin healed the Mega with both Lucky Ice Pops before retreating it. kx kept km3's order of retreating first, so the Ice Pops heal Lapras instead. Healing first versus retreating scored the same.
  - A-132311-t05: Dustin kept the damaged Mega in front; kx retreated it. His first move scored level or slightly below.
  - A-114458-t10 and D3-020315-t08 (adapting): every move won 16 of 16.
  - D3-022135-t09 (adapting): every move lost 16 of 16.

To settle it, it would need positions where the game is in doubt (close games, ladder games against stronger decks), and a check that plays the candidate move followed by the human's line, or kx, on the next turn instead of km3. The run's report prints "/12"; read it as out of 3 seeds, as I did.

Files: /home/dacz8976/pgd/runs_kx3_trace/err_B-214254-t06.txt, err_B-214254-t08.txt, err_B-214254-t10.txt, err_B-210952-t16.txt, err_B-205731-t08.txt and err_B-205731-t10.txt. Game reviews: C:\Users\dacz8\OneDrive\Desktop\Battle Logs\Recording_QA\BATCH_2026-10-02_DRAFT_A_V_BLASTOISE_WAILORD\20261002_214254000_iOS_shark_sol\REVIEW.md, 20261002_210952000_iOS_auto_sol\REVIEW.md and 20261002_205731000_iOS_auto_sol\TURN_TABLE.md. My scripts are in the session scratchpad (dump.py, overview.py, stats.py).

## Note added Oct 4 (Dustin): holding the turn's Energy back can be right

The coordinated-plan reader's draft above calls km3's habit of attacking with the turn's Water unattached "wasting the
turn's Energy". That is too strong. Some attacks do more damage for each Energy on the defending Pokemon, so an extra
Energy on your Active can cost you. The card texts (lib/deckgym-database.json) show 16 Pokemon with such an attack:
- "30 more damage for each Energy attached to your opponent's Active Pokemon": Indeedee ex (its Psychic), Alakazam,
  Alolan Raichu ex, Delphox, Quagsire and Slowking.
- 20 more: Bronzong, Espathra, Exeggutor, Gallade ex, Golduck, Hypno and Jynx. 40 more: Mewtwo.
- Smoochum: 20 for each such Energy. Tapu Lele: 20 to one Pokemon for each Energy attached to it.

The computer deck in these 8 games (decks/computer/blastoise-wailord-deluxe.txt) has none of them. So the 38 ties are
not explained by such an attack: there, attaching or not made no difference in the play-outs.

Among Dustin's decks this matters for deck 05 (Indeedee/Stoutland): it has Psychic Energy, its Indeedee ex attacks with
Psychic, and it runs 1 Psychic Supporter (B4 150). In decks 03 and 07, Indeedee ex can't attack, since they have Water or
Metal Energy; it is there for Watch Over (Dustin, Oct 4). Deck 14's Hypno is Team Rocket's Hypno, whose Entrap doesn't
scale.

The Supporter **Psychic** (B4 150) works with these attacks. You can use it only if your Active Pokemon has the Psychic
attack. It moves a random Energy from one of your opponent's Benched Pokemon to their Active Pokemon, which raises
Psychic's damage. The engine lists it as Complete.

Where an opponent has one of these attacks, the two pilots differ:
- km3 never sees the opponent's turn, so it can't price this.
- kx3's play-outs play the opponent's attacks, so they can, in principle.
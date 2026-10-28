# Score: G (Gemini) vs X (Codex), ScreenRecording_10-27-2026 14-11-19_1

41 frames opened (limit 120). Codex mm:ss times converted to seconds (for example 02:57 = 177 s). Frame numbers below are seconds into the video.

## Facts both reviews agree on (all confirmed by frames, not listed as disagreements)

- Dustin went first (turn-order line on the result screen, t=230). Opening Active is Deino 60 HP vs Mega Absol ex 170 HP. Both Energy Zones are Darkness.
- T1: Needle on Deino, Professor's Research (draws Rare Candy and a second Needle), end-of-turn Needle leaves Absol at 160 (t=80).
- T2: opponent attaches Darkness and Deceptive Needle to Absol, no attack, Needle leaves Deino at 50 (t=93, t=118).
- T3: Poke Ball finds Hoopa ex and it goes to the Bench, Rare Candy Deino to Hydreigon (140), Darkness attach, Roar in Unison (3 Darkness, 140 to 110), Lillie heals back to 150, Needle on Hoopa, Hyper Ray 130 (Absol 160 to 30, Energy discarded), end Needle leaves Absol at 20.
- T4: Darkness attach, three Lucky Ice Pop plays (Heads, Tails, Tails; Absol 20 to 80), Darkness Claw 80 (Hydreigon 150 to 70, no Supporter in hand to discard), Needle leaves Hydreigon at 60.
- T5: Dustin draws Professor's Research, opponent concedes (t=219 banner "Your opponent conceded"). 0-0, no Knock Outs. Damage done 150. Cards of the Game: Hydreigon (Dustin), Mega Absol ex (opponent). 5 turns.

## Disagreement table

| # | Turn | Item | G says | X says | Frames | Verdict |
|---|------|------|--------|--------|--------|---------|
| 1 | T4 | Opponent Trainer plays | Field Blower played about t=170, discards the Deceptive Needle from Dustin's Hydreigon (t=173-174), then three Lucky Ice Pops | "No other opponent Trainer play is established"; Field Blower and the Needle discard are absent (Hydreigon's Needle never removed) | t=172: Hydreigon has the Needle icon. t=174: icon gone, Absol still has its own. t=176/178/184/185: a card labelled Field Blower sits in the opponent's played-card spot. t=212: Hydreigon takes Absol's Needle damage and has no tool | **G right** |
| 2 | T3 | Poke Ball play time | t=113 | 01:58 = 118 | t=113: Poke Ball in play, Hoopa not yet in hand. t=118: Hoopa in hand, Poke Ball already finished | **G right** |
| 3 | T3 | Hoopa ex benched | t=121 | 02:06 = 126 | t=121: Hoopa landing on the Bench. t=126: settled (150 HP) | **G right** |
| 4 | T4 | 2nd Lucky Ice Pop play | play t=185, heal t=187 | about 03:10 = 190 | t=185: opponent playing a card. t=187: heal "20" animation, HP 40 to 60 | **G right** |
| 5 | T4 | 2nd coin (Tails) | t=192 | about 03:17 = 197 | t=192: "Tails!" screen | **G right** |
| 6 | T4 | 3rd Lucky Ice Pop play | play t=194, heal t=196 | about 03:19 = 199 | t=196: 3rd Ice Pop heal animation (60 to 80) | **G right** |
| 7 | T4 | 3rd coin (Tails) | t=200 | about 03:26 = 206 | t=200: coin showing "Ta...". t=204: Darkness Claw banner already on screen, so a coin at 206 is impossible | **G right** |
| 8 | T4 | Darkness Claw | t=204 | about 03:29 = 209 | t=204: Darkness Claw banner. t=206: Hydreigon 70, Absol 80 | **G right** |

All other times differ by 3 s or less (for example Rare Candy 127 vs 130-134, Roar 137, Lillie 144 vs 142-144, Hyper Ray 155, first Ice Pop 177, Needle end of T4 210-212 vs 212-213, concession 219).

## Claims only one review makes

- G only: Master Ball Rank 1,005 pts at t=2 and 1,014 at t=235 (frames t=2 and t=235 confirm; streak badge reads 2 before, 3 after). Opening hand Hydreigon, Deino, Lillie, Protective Poncho, Professor's Research (t=30 confirms). Deck screen at t=1 (Hoopa ex, Mega Sableye ex, Deino x2, Hydreigon x2, Poke Balls, Rare Candy; confirmed). No G-only claim is contradicted.
- X only: QR payload, file hashes and a mapped 20-card list (not visible in frames; not graded). "Three observed plays, not an assumption of three separate copies": consistent with the frames (the first copy was discarded on Tails at t=192, so the third play had to be a second copy, as G states). X does not list the opening hand and does not mention the Field Blower (graded under #1). No X-only claim is contradicted except through #1.

## Errors, graded

### G (Gemini): major 0, minor 0
None found. Every checked event, number, card name, HP, Energy type and target matched the frames. All G timestamps checked were within 3 s.

### X (Codex): major 1, minor 7
Major:
1. T4: misses the opponent's Field Blower and the discard of Dustin's Hydreigon Needle (a missing play and a missing tool removal), and states no other Trainer play happened. Also leaves Field Blower out of OPPONENT.json.

Minor (X's turn-3/4 timestamps run about 5 s late; each event off by more than 3 s is graded separately):
1. T3 Poke Ball play 118 vs 113.
2. T3 Hoopa benched 126 vs about 121.
3. T4 second Ice Pop play 190 vs about 185.
4. T4 second coin Tails 197 vs 192.
5. T4 third Ice Pop play 199 vs about 194.
6. T4 third coin Tails 206 vs 200.
7. T4 Darkness Claw 209 vs 204.

(Not counted: X does not list the owner's opening hand; this is a missing detail with nothing wrong, so it is left out under "differences in detail where neither is wrong". If the seven timestamp items are treated as one systematic drift, X would be major 1, minor 1.)

Verdict counts: G right 8, X right 0, both wrong 0, unsettled 0.

## Opponent sheet checks (12 fields)

Truth from the frames: went_first dustin; global_turns 5; final_score 0-0; end concede_opponent; Energy Zone Darkness; Pokemon Mega Absol ex only; attack Darkness Claw only; Trainers Deceptive Needle, Field Blower, Lucky Ice Pop; special_conditions none; healed true; bench_damage false; card of the game Mega Absol ex.

| Field | gemini | gemini_cheap | codex |
|-------|--------|--------------|-------|
| went_first | right | right | right |
| global_turns | right | right | right |
| final_score | right | right | right |
| end | right | right | right |
| opponent Energy Zone | right | right | right |
| opponent Pokemon names | right | right | right |
| opponent attack names | right | right | right |
| opponent Trainer names | right | right | **wrong** (no Field Blower) |
| special_conditions | right | right | right |
| healed | right | right | right |
| bench_damage | right | right | right |
| card of the game | right | right | right |
| **Total right / checked** | **12 / 12** | **12 / 12** | **11 / 12** |

Outside the 12 fields: both Gemini sheets say first_seen_turn 1, Codex says null (Absol is on the board from setup, before turn 1); not graded.

## Which record to rely on

For this game a player could rely on the Gemini record (G) more. It had every event, number, card and time right and matched the frames, including the opponent's Field Blower removing the Deceptive Needle from Hydreigon, the one real play Codex (X) missed. X was otherwise accurate on the facts (damage, HP, Energy, Lucky Ice Pop coin results, Darkness Claw, concession, score), but it states that no other Trainer was played, which would mislead a player studying how the opponent handled Hydreigon's tool. Its turn-3/4 timestamps also run about 5 s late, which matters little for the game record but makes it harder to find moments in the video. Both Gemini sheets were fully correct on the 12 fields; the Codex sheet missed the Field Blower.

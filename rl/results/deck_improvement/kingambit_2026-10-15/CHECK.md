## CHECKS

Each item gives the claim, the verdict, the evidence, and the corrected wording.

1. **Card text for every deck card, plus Red, Juliana, Bisharp, Pawniard P-B 067, Poncho and Cyrus.** Verdict: upheld. Evidence: `lib/card.py` output in `check/cards.out.txt`. Grimer A3 110 is 70 HP with [DC] 30, and B2 096 is 80 HP with [CC] 20. Kingambit is 140 HP, retreat 3, weak to Grass, and does 60 +40 per own knockout. Red reads: "+20 damage to your opponent's Active Pokémon ex". Corrected: none.
2. **Opponent HP and attacks used in the draft.** Verdict: upheld. Evidence: `check/opp.out.txt`. Rayquaza, Kangaskhan and Manectric are 180 HP. Lucario, Sharpedo and Altaria are 190. Absol is 170. Gardevoir is 210 and weak to Darkness. Mega Charizard X and Y are 220. Pichu is 30 and Drampa B4 is 100 with a 70 attack. Corrected: none.
3. **Lists A, B, C and B+ are legal 20-card lists.** Verdict: upheld. Evidence: each list counts 9 Pokémon plus 11 Trainers = 20, with no card above 2 copies. Each line evolves legally: Muk from Alolan Grimer, Glimmora from Glimmet, and Kingambit from Pawniard by Rare Candy. A matches `v2/decks/KW261013_010837000.txt`. The deck 01 file differs exactly as the draft states. Corrected: none.
4. **Card types.** Verdict: upheld. Evidence: in `deckgym-database.json`, Red, Juliana, Ilima, Copycat and Professor's Research are Supporters. Rare Candy, Poké Ball and Lucky Ice Pop are Items. Heavy Helmet and Protective Poncho are Tools. Mesagoza is a Stadium. Corrected: none.
5. **"Kingambit never in play in 6 of 11; those went 1-5, the others 4-1."** Verdict: upheld. Evidence: the ledgers. The games with Kingambit are 010706, 203719, 210823 and 010837 (wins) and 230258 (loss). The games without it are 210041, 225319, 014423, 015659 and 020824 (losses) and 010003 (win). Corrected: none.
6. **"You had it by own turn 4 in 4 of 11."** Verdict: upheld. Evidence: after converting game turns using seat order, the arrival turns are 010706 own 3, 210823 own 3 (he went second), 203719 own 4, 010837 own 4 and 230258 own 5. Corrected: none.
7. **"Missing piece: Rare Candy 4, Kingambit 1, Pawniard 1."** Verdict: upheld. Evidence: in 210041 the Candy arrived on own turn 6, and Kingambit had also been shuffled away on own turn 4. In 015659 and 020824 the Candy was never drawn. In 225319 Copycat shuffled the Candy away at game turn 4. In 014423 Kingambit was never drawn. In 010003 Pawniard was never found. Corrected: none.
8. **"Model: Kingambit by own turn 4 in at most 35.5%."** Verdict: weakened. Evidence: "at most" is wrong, because the model uses fixed play rules rather than the best play. My separately written model (`check/indep.py`, 100k deals) gives 34.9. Corrected: "about 35% (an optimistic figure: nothing knocks Pawniard out)".
9. **"Copycat shuffled pieces back in 5 of 11; 3 of those never got Kingambit."** Verdict: weakened. Evidence: the 5 shuffles were 203719 game turn 3 (Kingambit), 210041 game turn 8 (Kingambit), 010837 game turn 3 (Candy), 225319 game turn 4 (Candy) and 014423 game turn 5 (Candy). In 014423 Kingambit was never drawn anyway. Copycat also drew Kingambit in 010837, and both Kingambit and the Candy in 210823. Corrected: "In 2 games (210041, 225319) the lost piece never came back. Copycat also found the pieces in 2 games."
10. **"Never playing Copycat: 26.9% instead of 35.5%."** Verdict: upheld. Evidence: my model gives 26.4 against 34.9. Corrected: none.
11. **"In 3 losses your third knockout was the opponent's third point, every coin tails."** Verdict: upheld. Evidence: 230258 (Glimmora tails, then Regigigas, then Muk), 014423 (Grimer, Regigigas, Glimmora tails), 020824 (Glimmora tails, Glimmet, Regigigas). Corrected: none.
12. **"Count 3 with the opponent at 2 or fewer and Kingambit ready: 3 of 11, all won."** Verdict: upheld. Evidence: 010706 game turn 20, 203719 game turn 20, 010837 game turn 12. 210041 also reached count 3, but Kingambit was not in play. Corrected: none.
13. **"Bench damage reached Pawniard or Kingambit in 3 of 11; Chien-Pao knocked Pawniard out."** Verdict: upheld. Evidence: 225319 game turn 7, 015659 game turns 10 and 12, 230258 game turn 10. Corrected: none.
14. **"5 of 7 Pokémon weak to Fighting; 2 Lucario games conceded at 0-2."** Verdict: upheld. Evidence: card lookups, plus games 210041 and 015659. Corrected: none.
15. **"No support card fixes either Weakness."** Verdict: weakened. Evidence: I searched the database text only for cards that remove or change Weakness; I did not check every possible fix. Corrected: "No support card I found fixes either."
16. **"Regigigas gave up 7 of the 22 points."** Verdict: upheld. Evidence: points against him per game sum to 2+2+2+1+2+3+0+2+3+2+3 = 22. Regigigas was knocked out in 203719, 210041, 230258, 010837, 014423, 015659 and 020824. Corrected: none.
17. **"Deck ran out in 3 long games."** Verdict: upheld. Evidence: 210823 own turn 6, 230258 own turn 7, 203719 own turn 9. Corrected: none.
18. **"Passed up 3 free knockouts in 2 games, both wins."** Verdict: upheld. Evidence: 010837 game turns 3 and 11 (Pichu, 30 HP) and 203719 game turn 17 (Drampa at 100, count 1). Corrected: label these as game turns.
19. **"km3 counts the Blade as 60 whatever the count, so it Blades at count 0 and retreats in at count 2."** Verdict: weakened. Evidence: `KINGAMBIT_PASS_cloud.md:88-95` shows the 60 applies only to its look-ahead estimate. `POSITION_TABLE` rows 203719-t17 and 010837-t13 show km3 sees the real count within the turn. The "so" is not shown. Corrected: "km3 plans ahead as if the Blade were 60. It used the Blade at count 0 and retreated into Kingambit at count 2."
20. **"210041 turn 6: all three bots put Pawniard in front in 11 or 12 of 12."** Verdict: upheld. Evidence: PT:29 shows km3 12/12, `p2_F_TABLES.md:37` shows F 12/12, and `p2_C_TABLES.md:37` shows C 11/12. Corrected: "game turn 6".
21. **"km3 puts Energy on Regigigas instead of Pawniard."** Verdict: upheld. Evidence: PT:73, :82 and :88 (3 positions). Corrected: none.
22. **"A Pop rarely buys a whole extra hit; against 90-150 damage the wall takes the same number of hits; only Regigigas against 80 and Muk against 60."** Verdict: overturned. Evidence: the draft's calc assumed one 20-point heal. On heads a Pop returns to hand and can be played again, so one Pop heals 40 on average and two Pops heal 80 (`check/pops.py`). By card text, a 20 heal saves a Helmeted Regigigas from a 100 hit, and a 40 heal saves a plain Regigigas from a 90 hit. In his games, a Pop kept Glimmora alive through one more Drampa 70 hit in 010003 (game turn 3) and in 203719 (game turn 15, three heads). Both were wins. Corrected: see section 3, B.
23. **"Pops used: 2 at 010837 turn 9, 3 at 203719 turn 17."** Verdict: weakened. Evidence: those are game turns. Pops were played in 6 of 11 games (203719, 230258, 010003, 010837, 015659, 020824). Three plays in one turn happened at 203719 game turns 15 and 17 and at 230258 game turn 9. Corrected: "Pops played in 6 of 11 games."
24. **"Helmet is always on Kingambit."** Verdict: weakened. Evidence: the Helmet went on Kingambit in all 4 games where Kingambit was in play and the Helmet was drawn. It went on Regigigas in 230258, 014423 and 010003. It was put on Pawniard early in 225319, 210041 and 020824. Corrected: "On Kingambit in 4 of 4 games where both were in play."
25. **"Helmet keeps Kingambit alive against a 140 or 150 hit."** Verdict: upheld. Evidence: a 140 hit leaves Kingambit at 20 and a 150 hit leaves it at 10. Corrected: none.
26. **Model numbers for Kingambit by own turn 4: A 35.5, A -1 Pop +1 Candy 49.6, B 60.5, C 60.1, B+ 69.8, A -2 Pops +Candy +Juliana 62.0, file 46.1, C with a Copycat cut instead 49.6.** Verdict: upheld in direction. Evidence: my model gives 34.9, 48.5, 58.9, 58.8, 67.9, 61.0, 44.9 and 48.7. Corrected: give rounded figures or ranges.
27. **"Differences between lists are accurate to about ±0.5 points."** Verdict: overturned. Evidence: ±0.5 is only the random noise. The two models differ by up to 3.5 points on Kingambit by own turn 5 (B 75.4 against 71.9). For "all three by own turn 4" they differ by 8 points (B 42.8 against 34.8). Corrected: "noise ±0.5; play rules matter more; ranges shown".
28. **Table rows for Muk, "all three" and "Muk plus Regigigas".** Verdict: weakened. Evidence: my model gives A 42/17/47 and B 48/35/56, against the draft's 44/20/52 and 52/43/63. Corrected: show ranges.
29. **Gains under a no-Copycat policy.** Verdict: new. Evidence: if Copycat is never played, B reaches about 40% by own turn 4. B's extra gain depends on playing the Copycats. Corrected: add this line under B.
30. **"Copycat before Research came out best in the model."** Verdict: weakened. Evidence: the advantage is 0.4-0.6 points in my model and 1.4 in the original. Corrected: "makes almost no difference".
31. **"Faster Kingambit matters most against fast decks: Charizard/Entei, Rayquaza, Lucario, Lightning."** Verdict: weakened. Evidence: nothing shows which decks are fast. Corrected: "matters most when the opponent knocks out your Pokémon early; untested which decks".
32. **"Cut Pops matter most in long games against small attacks like Entei's 60."** Verdict: weakened. Evidence: both real saves came against Drampa's 70. Corrected: "attacks of about 70-100".
33. **Red arithmetic: count 2 = 160; 180-HP Megas need 20; 190-HP need 30; count 3 = 200 against 210; Gardevoir; count 1 = 120.** Verdict: upheld. Evidence: card text plus Weakness +20. Corrected: none.
34. **"Ex or Mega ex main attacker in about 60 of 80 log games."** Verdict: upheld. Evidence: the hand-coded tally has 36 Mega (4 of them probable) and 24 ex. The log copy totals 80 games (56 + 24). Corrected: none.
35. **"Red does nothing against non-ex attackers (about 14 of 80: Drampa walls, Hydreigon)."** Verdict: overturned on the examples. Evidence: the 14 non-ex games are Dustox, Butterfree, Dragonite, Garchomp, Salazzle, a plain Charizard and similar. Drampa walls appear in Rayquaza decks, which are coded Mega. 3 of the 4 Hydreigon games also had Mega Absol or Mega Sableye. Corrected: see section 3, C.
36. **"6 of the 11 Megas this season were over 190."** Verdict: upheld. Evidence: Swampert, Venusaur twice, Blaziken and Charizard twice (X/Y, both 220 HP). Corrected: "in 6 of the 11 games with a confirmed Mega".
37. **"Ilima used in 3 of 11; Kingambit attacked in 2 of 11."** Verdict: upheld. Evidence: Ilima in 203719, 210823 and 020824. Kingambit attacked in 010706 and 010837. Corrected: none.
38. **C's Red example ("Lucario at 150-160 after the Poison").** Verdict: weakened. Evidence: if both Poison ticks land, Lucario is at 140 and the count-2 Blade knocks it out without Red. Red matters when the opponent heals or cures in between; a Lucky Ice Pop did this in 210041. Corrected: see section 5.
39. **B's sacrifice example and the 203719 pass example.** Verdict: upheld. Evidence: Rayquaza held 1 Fire and 2 Lightning at game turn 17. Both Glimmoras fell afterwards, one tails and one heads. Corrected: "game turn 17 (own turn 9)".
40. **"Bench Pawniard on turn 1; each turn it waits costs a turn."** Verdict: weakened. Evidence: waiting only costs a turn once Kingambit and Rare Candy are in hand. He held Pawniard in 3 games (210823 was missing from the draft); in 015659 it cost nothing. The advice also pre-empts question 3. Corrected: see question 3 and section 5.
41. **"Every earlier bot number used the file."** Verdict: weakened. Evidence: the floor check used the file, but the v2 position reads used his real positions. Corrected: "the floor check used the file".
42. **"B keeps every card in your plan."** Verdict: weakened. Evidence: B cuts the Pops, which support the wall. Corrected: "keeps every Pokémon, the Helmet and Ilima".
43. **Opponent frequencies: Charizard/Entei 7, Rayquaza 5, Lucario 5/0, Suicune 3, Hydreigon 4, Lightning 9 (5 this season).** Verdict: upheld. Evidence: `check/ladder.py` over the log copy. Corrected: none.
44. **"Mega Sharpedo: 4 games."** Verdict: weakened. Evidence: a Mega Sharpedo was seen in only 2 of the 4. Corrected: add "(Mega seen in 2)".
45. **"Mega Manectric stands in for Lightning."** Verdict: weakened. Evidence: Mega Manectric appeared once in 80 games. The Lightning games were Magnezone/Miraidon, Rotom ex, Tapu Koko ex, Dedenne ex and Pachirisu ex, all 2-point ex decks. Corrected: "stands in poorly; optional".
46. **"Hydreigon's attacker isn't an ex, so Red does nothing there."** Verdict: overturned. Evidence: `t-hydreigon.txt` includes 1 Mega Absol ex. Corrected: "Red can matter against its Mega Absol".
47. **The Rayquaza opponent list.** Verdict: new caveat. Evidence: `g-dragonair_mega_rayquaza.txt` has Gouging Fire and no Drampa, while his 203719 opponent walled with Drampa. Corrected: note it in section 4.
48. **"km3 should play Red when it makes a knockout now."** Verdict: weakened. Evidence: this is an inference and was not checked. Corrected: "may".
49. **"Every list plays the same games."** Verdict: weakened. Evidence: the lists share seeds and seats, but different lists shuffle differently. Corrected: "same seeds and seats".
50. **"Setup numbers are best cases."** Verdict: weakened. Evidence: the play rules are fixed, not optimal. Corrected: "optimistic".
51. **"1,000 games detect about a 5-point setup difference."** Verdict: upheld. Evidence: the 95% half-width is about 4.4 points at 50%. Corrected: none.
52. **Timing and disk.** Verdict: upheld. Evidence: Wallace ran 1,000 games in 111 s (calls of 4-8 s, 16 cores). The deck 01 floor ran 1,920 games in 312 s, second slowest of 20. 21,000 games ≈ 57 min and 7,000 ≈ 19 min. C: has 4.5 GB free (about 99% full). Corrected: none.
53. **Engine and coverage references.** Verdict: upheld. Evidence: Red is at `apply_trainer_action.rs:135`, "Fully implemented", with the +20 applied only to an Active ex. Juliana is at :292. Copycat's effect is unpriced. Kingambit is estimated at printed damage. The KINGAMBIT_PASS lines match. Corrected: none.

## CORRECTED DELIVERABLE

# Kingambit (deck 01): what to change, why, and what you give up

DRAFT

## 1. Your plan and the core (please confirm)

**The plan, from your words and 12 pause games:**
- Glimmora poisons early, and Regigigas walls. Regigigas can attack only while Muk is in play.
- You let Glimmet, Glimmora and Regigigas be knocked out on purpose. Each of your knockouts adds 40 to Overlord's Blade. Each Glimmora knockout has a 50% chance of giving no point.
- Pawniard stays safe on the Bench. Rare Candy turns it into Kingambit there. Kingambit then gets 2 Energy and Heavy Helmet.
- After one of your Pokémon is knocked out, you promote Kingambit at count 3 (180 damage) and knock out an ex or a Mega ex.
- You take a knockout only if it wins or helps. The plan reached that moment in 3 of 11 games, and you won all 3.

**Proposed core:**
- Kingambit
- Pawniard (1 copy now; the printing and count can change)
- A way to evolve it (1 Rare Candy now)
- 2 Glimmet and 2 Glimmora

**Tied to the plan (core or flexible?):** Alolan Grimer/Muk, Regigigas, Heavy Helmet.

**Flexible:** 2 Poké Ball, 2 Professor's Research, Copycat, 2 Lucky Ice Pop, Mesagoza, Ilima.

**Questions for you:**
1. Is this core right? Are Muk and Regigigas core for you?
2. Which list is "the original"? I used the one you played Oct 11-12, checked by QR code: Alolan Grimer A3 110 (70 HP), 2 Ice Pop and 1 Copycat. Deck 01's file has Grimer B2 096 (80 HP), 1 Ice Pop and 2 Copycat. The floor check, the only bot win rate for this deck, used the file.
3. Did you keep Pawniard in your hand on purpose? This happened in 210823 (own turn 1), 015659 (own turns 1-2) and 230258 (own turns 2-3). Rare Candy can't be used on a Basic put down that turn. So once you hold Kingambit and Rare Candy, each turn Pawniard waits delays Kingambit by a turn:
   - In 230258, Kingambit came on own turn 5 instead of 3.
   - In 210823, it came on own turn 3 instead of 2.
   - In 015659 it cost nothing, because Rare Candy never came.
4. Is a Blade at count 2 ever part of your plan? List C depends on it.

## 2. Recurring problems

This covers 11 games. 015011 is left out because the opponent left after 1 turn. The counts describe what happened; 11 games support no conclusion about a matchup.

**Problems with the list:**
- **Kingambit doesn't arrive.** This is the main problem.
  - Kingambit never came into play in 6 of 11 games. Those 6 went 1-5, and the other 5 went 4-1. That is an association, not proof.
  - The missing piece was Rare Candy in 4 games, Kingambit in 1 and Pawniard in 1. In 225319, Copycat shuffled the Candy away and then Pawniard was knocked out.
  - The line is three single cards, and nothing in the list searches for Rare Candy.
  - A draw model of your list puts Kingambit in play by own turn 4 in about 35% of games. The model has no opponent and fixed play rules. That figure is optimistic, because nothing knocks Pawniard out. You had Kingambit by own turn 4 in 4 of 11 games.
- **Copycat shuffles pieces back.** It shuffled a piece away in 5 of 11 games: Kingambit twice and Rare Candy 3 times.
  - In 2 games (210041, 225319) the lost piece never came back and Kingambit never came. In 014423 Kingambit was never drawn anyway.
  - Copycat also found the pieces: Kingambit in 010837, and Kingambit plus Rare Candy in 210823.
  - This is part list, part play. Both models say playing Copycat during setup helps on average: never playing it gives about 26% instead of 35% by own turn 4.
- **Count 3 needs a Glimmora heads.**
  - No Pokémon in the list is an ex, so every knockout except a heads gives a point.
  - In 3 losses, your third knockout was the opponent's third point, and every Glimmora coin was tails.
  - When count 3 came with the opponent at 2 points or fewer and Kingambit ready (3 of 11 games), you won all 3.
- **Pawniard is 50 HP and alone.** Bench damage reached Pawniard or Kingambit in 3 of 11 games. In 225319, Chien-Pao ex knocked Pawniard out.
- **Weakness.** Five of the 7 Pokémon are weak to Fighting. Against Mega Lucario you played 2 games and conceded both at 0-2; Kingambit never came. Pawniard and Kingambit are weak to Grass. No support card I found fixes either.
- **Minor:**
  - The Energy is spread over 4 attackers.
  - Regigigas gave up 7 of the 22 points scored against you, and each of those knockouts also raised the count.
  - The deck ran out in 3 long games, on own turns 6, 7 and 9. No loss traced to it.
  - Sleep: 0 of 11 games, so no data.

**Your play:** you passed up 3 free knockouts in 2 games (010837 game turns 3 and 11; 203719 game turn 17). Both were wins and fit your rule. Nothing shows them to be mistakes.

**The bot's play (these are not list problems):**
- km3 doesn't value waiting for a higher count. When it plans ahead it counts the Blade as 60 whatever the count, though within the current turn it sees the real damage.
  - It used the Blade at count 0 (203719 game turn 7, 210823 game turn 8).
  - It retreated into Kingambit at count 2 (010837 game turns 9 and 11).
- It puts Pawniard in front to attack. At 210041 game turn 6, km3 and the frozen kx3 did so in 12 of 12 seeds, and candidate C in 11 of 12.
- It puts Energy on Regigigas where you fed Pawniard (3 positions).
- It doesn't value Copycat's effect.

## 3. Three lists

Each list is 20 cards with Darkness Energy. **None is shown to be better than A.** The setup numbers come from draw models: no opponent, no knockouts, and the same play rules for every list. They are optimistic.

**A, the original (as you played it Oct 11-12)**
1 Alolan Grimer A3 110, 1 Alolan Muk B2 097, 2 Glimmet B3a 044, 2 Glimmora B3a 045, 1 Pawniard B3a 041, 1 Kingambit B3a 043, 1 Regigigas B3 134, 2 Poké Ball, 1 Rare Candy, 2 Lucky Ice Pop, 1 Heavy Helmet, 2 Professor's Research, 1 Ilima, 1 Copycat, 1 Mesagoza.

**B, consistency: A with -2 Lucky Ice Pop, +1 Rare Candy, +1 Copycat**
1 Alolan Grimer A3 110, 1 Alolan Muk B2 097, 2 Glimmet B3a 044, 2 Glimmora B3a 045, 1 Pawniard B3a 041, 1 Kingambit B3a 043, 1 Regigigas B3 134, 2 Poké Ball, 2 Rare Candy, 1 Heavy Helmet, 2 Professor's Research, 1 Ilima, 2 Copycat, 1 Mesagoza.
- **+1 Rare Candy:** it was the most common missing piece in your games and in the model. With two copies, one Copycat shuffle doesn't cost the only one. On its own (A with -1 Ice Pop, +1 Candy) it raises Kingambit by own turn 4 from about 35% to about 49%.
- **+1 Copycat** (back to the file's 2): in the model it is the deck's main digging card.
  - Together with the Candy, Kingambit by own turn 4 rises to about 59-61%. It also finds Glimmora and Muk.
  - The extra gain needs you to play the Copycats. If you never play Copycat, B reaches only about 40%.
  - Without the extra Copycat (-2 Ice Pop, +Candy, +Juliana), Kingambit reaches about 61-62% by own turn 4, but Glimmora and Muk don't improve.
- **-2 Lucky Ice Pop:** the Pops never help setup, but they do more mid-game than one heal suggests.
  - On heads a Pop comes back and can be played again, so one Pop heals 40 on average and two heal 80.
  - In 2 of your 11 games a Pop kept Glimmora alive through one more 70-damage Drampa hit: 010003 (own turn 2) and 203719 (own turn 8, three heads in a row). Both were wins, and each time Glimmora got one more Venomous Hit.
  - You played Pops in 6 of 11 games.
  - By card text, a 40 heal lets a plain Regigigas survive one more 90 hit, and a 20 heal lets a Regigigas wearing the Helmet survive one more 100 hit.
- **Why the Pops and not something else:** the model gives the same setup numbers whether you cut Pops, Ilima or the Helmet. I cut the Pops because:
  - The Helmet went on Kingambit in all 4 games where both were in play.
  - Ilima is your Regigigas reset (used in 3 of 11 games).
  - If you'd rather keep the Pops, cut Ilima plus 1 Pop instead. The setup numbers don't change.
- **What B gives up:** both Pops, including the two saves above. Copycat also shuffles more often, and it shuffles the Helmet and Ilima back too.
- **Matchups by card text:**
  - No Pokémon changes, so no type matchup moves.
  - An earlier Kingambit matters most when the opponent knocks out your Pokémon quickly, because count 3 then comes early. Which decks do that is untested.
  - The cut Pops matter most where your wall takes hits of about 70-100, such as Drampa's 70. Both of your Pop saves were against Drampa.

**C, matchup: B with -1 Ilima, +1 Red (A2b 071)**
1 Alolan Grimer A3 110, 1 Alolan Muk B2 097, 2 Glimmet B3a 044, 2 Glimmora B3a 045, 1 Pawniard B3a 041, 1 Kingambit B3a 043, 1 Regigigas B3 134, 2 Poké Ball, 2 Rare Candy, 1 Heavy Helmet, 2 Professor's Research, 2 Copycat, 1 Red, 1 Mesagoza.
- **The problem it targets:**
  - At count 3 (180), the Blade knocks out 170- and 180-HP Megas from full HP. A 190-HP Mega needs 10 more.
  - Reaching count 3 without losing always needs a Glimmora heads, and it usually leaves the opponent at 2 points.
  - An ex or Mega ex was the main attacker in about 60 of the 80 ladder-log games, judged from the cards seen.
- **+1 Red** (Supporter: during this turn your attacks do +20 to the opponent's Active Pokémon ex):
  - At count 2 the Blade does 160 to an ex. A Mega knockout is 3 points, so it wins at any score.
  - 180-HP Megas (Rayquaza, Kangaskhan, Manectric) need 20 damage already on them.
  - 190-HP Megas (Lucario, Sharpedo, Altaria) need 30, which is one Venomous Hit.
  - At count 3 it does 200, so a 210-HP Mega needs only 10.
  - Red also adds 20 to Venomous Hit, Giga Turbo and Sludge Bomb against an ex.
- **-1 Ilima:** it never helps setup, and Regigigas is its only target. Cutting a Copycat instead would drop Kingambit by own turn 4 to about 49%.
- **Why C is built on B:** the Red turn only exists once Kingambit is in play, and Kingambit attacked in only 2 of 11 games with A. Building on B lets the test isolate Red.
- **What C gives up:**
  - Ilima's Regigigas reset, which you used in 3 of 11 games.
  - Red does nothing while a non-ex is in front or while the Mega waits on the Bench. About 14 of the 80 log games had a non-ex main attacker (Dustox, Butterfree, Dragonite, Garchomp, a plain Charizard and others). Mega Rayquaza decks often wall with Drampa, as in 203719.
  - On the Red turn, Red is your Supporter for that turn.
- **Matchups by card text:**
  - It might gain against ex and Mega ex up to 190 HP: Rayquaza, Kangaskhan, Manectric, Lucario, Sharpedo, Altaria, Absol, and Gardevoir thanks to its Darkness Weakness.
  - It might gain against 2-point ex with 120-150 HP, since count 1 plus Red does 120.
  - It helps less against Megas over 190 HP. In 6 of the 11 games this season with a confirmed Mega, the Mega was over 190.
  - It might lose a little against non-ex decks and in long Regigigas walls.
  - Fighting and Grass stay as bad as before.

**Setup odds** (model, both seats, % of games). The ranges come from two separately written models with slightly different play rules. Random noise is about ±0.5 points; the play rules matter more.

| | A | B | C |
|---|---|---|---|
| Kingambit in play by own turn 2 / 3 / 4 / 5 | 11 / 22 / 35 / 49-51 | 21 / 41 / 59-61 / 72-75 | 21 / 41 / 59-60 / 72-75 |
| Pawniard in play by own turn 2 | 70-71 | 74-75 | 74-75 |
| Glimmora in play by own turn 3 | 79 | 84-85 | 84-85 |
| Muk in play by own turn 3 | 42-44 | 48-52 | 49-52 |
| Kingambit, Glimmora and Muk all in play by own turn 4 | 17-20 | 35-43 | 35-43 |
| Muk in play and Regigigas found by own turn 4 | 47-52 | 56-63 | 57-63 |
| Pawniard forced to start Active | 13 | 13 | 13 |

For reference, deck 01's file reaches Kingambit by own turn 4 in about 45-46% of games.

**A larger package for the test, B+:** B with -Ilima, +Juliana (Juliana finds Kingambit). It reaches Kingambit by own turn 3 / 4 in about 49% / 68-70% of games, and it gives up Ilima.

## 4. Comparing them fairly, the Wallace way

**Setup of the test:**
- km3 plays both sides, on the current official engine.
- Every list plays the same seeds and seats.
- 1,000 games per list per opponent, 500 from each seat.
- The definitions are written down before the first game, as in the Wallace test.
- Lists tested: A, B, C, plus B+ if you want the bigger package.

**Skip kx3 for now.** On your Kingambit positions:
- The frozen kx3 kept km3's Blade line in 12 of 12 seeds at 010837 game turns 9 and 11.
- It put Pawniard in front in 12 of 12 at 210041 game turn 6.
- It is also slower.

**Opponents** (how often each appears in your 80-game ladder log, played with other decks):
- **Charizard Y/Entei:** 7 games. It was the Wallace opponent.
- **Mega Rayquaza:** 5 games. Two of your 12 Kingambit games were against Drampa/Dragonair, one of them with Mega Rayquaza. The saved list has Gouging Fire and no Drampa, unlike your 203719 opponent.
- **Mega Lucario:** 5 games last season, 0 this season; 2 of your 12 Kingambit games.
- **Mega Sharpedo:** 4 games, with the Mega seen in 2.
- **Lightning:** 9 games, 5 of them this season. Almost all were 2-point ex decks (Magnezone/Miraidon, Rotom ex, Tapu Koko ex, Dedenne ex); Mega Manectric appeared once. The only saved Lightning list is Mega Manectric, so it stands in poorly. Make it optional.
- **Suicune/Chien-Pao:** 3 games; it damages the Bench; 1 of your 12 Kingambit games.
- **Hydreigon:** 4 games. Hydreigon itself isn't an ex, but 3 of the 4 games also had Mega Absol or Mega Sableye, and the saved list holds a Mega Absol ex. So Red can matter there.
- **Optional:** Blaziken, Vespiquen, Altaria (Sleep).

**What gets measured, by weight:**
1. **Setup with an opponent hitting back** (depends little on the bot):
   - Pawniard in play by own turn 1-2, and Kingambit by own turn 2-5
   - Kingambit with 2 Energy by own turn N
   - Glimmora and Muk by own turn 3
   - Pawniard knocked out before it evolves
   - Rare Candy or Kingambit lost to Copycat
   - 1,000 games are enough to see a setup difference of about 5 points.
2. **The plan's line** (depends on the bot, so it is flagged):
   - The count when Kingambit first attacks
   - Games where a Blade knocks out an ex or Mega ex before the opponent has 3 points
   - For C, games where Red was played on a Blade knockout
   - Points denied by Glimmora
3. **Win rate:** the paired difference with its range, reported last and given little weight.

**What it can show:**
- Whether the extra Candy and Copycat get Kingambit down sooner with an opponent hitting back.
- Whether Pawniard lives long enough to evolve.
- Against which of these opponents the setup gains hold up.

**What it can't show:**
- Whether B or C carries out your plan better. km3 plans with the Blade at 60, so it attacks early and at low counts with every list. The count measures will mostly show that habit.
- Whether km3 uses Red the way you would. km3 sees the real damage of an attack it makes this turn: it took the exact 100-damage Blade on Drampa at 203719 game turn 17. So it may play Red when Red makes a knockout right now (not checked), but it won't build toward a count-2 Red turn.
- The real cost of cutting the Pops and Ilima. km3 doesn't value Glimmora's coin or Copycat, and it doesn't play the Regigigas wall your way, so that cost can look bigger or smaller than it is.
- Win rates and matchup reads. These wait for a bot that passes the Kingambit test; then the same seeds are run again with it.

**Rough cost:**
- The Wallace test played 1,000 games in about 2 minutes. Deck 01's floor check played 1,920 games in 312 seconds, and Kingambit games were among the slowest.
- So expect about 3 minutes per 1,000 games. A, B and C against 7 opponents is 21,000 games, about 1 hour of laptop time. B+ adds about 20 minutes.
- On top of that, a few hours of agent work to adapt the Wallace measurement script to the Kingambit line, plus a second reader.

## 5. How to play B and C

**B**
- **Opening:**
  - Start Glimmet or Regigigas. Start Pawniard only if it is your only Basic.
  - Depending on your answer to question 3: once you hold Kingambit and Rare Candy, bench Pawniard right away. Each turn it waits then costs a turn (230258: own turn 5 instead of 3).
  - If Pawniard has been down since last turn and you hold Kingambit and a Candy, evolve first, then play your Supporter. You already do this.
  - Copycat before or after Research makes almost no difference in the models (under 2 points).
  - With 2 Candies, a Copycat that shuffles one away leaves the other in the deck.
- **Sacrifice turn:**
  - The position: count 2, Kingambit benched with 2 Energy and the Helmet, Mega Rayquaza ex (180 HP) in front.
  - Attack with Glimmora's Venomous Hit (30 plus Poison, which does 10 at each checkup) and leave Glimmora in front.
  - If Glimmora is knocked out, the count is 3, and half the time they score nothing for it.
  - Promote Kingambit: the 180 Blade knocks out the Rayquaza for 3 points and the win.
  - If they already have 2 points, letting Glimmora go is a coin flip for the game. At 1 point or fewer it is safe.
- **Take or pass a knockout (your rule):**
  - Take the Blade knockout when it wins, or when Kingambit survives the reply. The Helmet takes 20 off each hit.
  - Pass when it would put Kingambit in front at a low count with a loaded Mega waiting.
  - Example: at 203719 game turn 17 (your own turn 9), you passed the exact-100 Blade on Drampa at count 1, with Mega Rayquaza ex benched on 3 Energy. Both Glimmoras then fell (one tails, one heads), the count reached 3, and they conceded.

**C (everything in B, plus Red)**
- **Opening:** Red is not a setup card, so hold it while Research and Copycat build your board. Spend it earlier only if it makes a knockout that turn, for example Giga Turbo 100 + 20 on an ex with 120 HP left.
- **The Red turn:**
  - The position: count 1, Glimmora in front of Mega Lucario ex (190 HP). Venomous Hit leaves it at 160.
  - Glimmora is knocked out, which makes count 2. Promote Kingambit.
  - If both Poison ticks landed (140 left), the Blade alone knocks it out.
  - If they healed or cured in between (a Lucky Ice Pop did this in 210041), play Red. The Blade then does 140 + 20 = 160: 3 points and the win, with no heads needed.
- **When to hold Red:**
  - Against a non-ex in front (Drampa, Hydreigon, Greninja), play C exactly like B.
  - If the Mega waits on the Bench behind a wall, Red waits too.
  - At count 1, Red plus the Blade does 120, enough to knock out a 120-HP ex for 2 points. Take it if that is your third point or if Kingambit survives the reply. Otherwise keep growing the count.

## 6. What stays uncertain

- **No test shows that B or C is better.** The setup gains are optimistic model numbers. Two models agree on Kingambit's arrival within about 3 points, but differ by up to 8 points on "all three in play".
- **Whether an earlier Kingambit turns into more winning Blade turns** against real players. They may hit the benched Kingambit, stop knocking out your Pokémon, or keep their Mega benched.
- **The real cost of cutting 2 Pops (B) and Ilima (C).** The Pops saved a Glimmora in 2 of 11 games, and the bot measures this poorly.
- **How often C's count-2 Red turn comes up.** It needs a Mega with 190 HP or less in front with some damage already on it.
- **Too few games for matchups.** 11 games, plus 80 log games played with other decks over two seasons, are too few for any matchup conclusion. The mix of opponents changes with each new set.
- **Which list is the original** (Grimer, Ice Pop and Copycat counts), until you confirm.
- **Fighting and Grass** stay bad for all three lists.

If you want to play one of these before any test: B changes 2 cards (-2 Ice Pop, +1 Rare Candy, +1 Copycat). It keeps every Pokémon, the Helmet and Ilima. Its gain is a model number, not a tested result, and it gives up the Pops.

## FOR THE LAPTOP (facts and paths)

**Lists**
- **List A (as played):** `rl/results/pause_games_new_2026-10-13/v2/decks/KW261013_010837000.txt`. The QR check is in `v2/deck_from_qr_check.txt` (010706 and 203719 AGREE).
- **Deck 01 file:** `decks/dustin/01-muk-glimmora-kingambit-regigigas.txt` differs: Grimer B2 096, 1 Lucky Ice Pop, 2 Copycat.
- **Other lists:**
  - B = A -2 Lucky Ice Pop B2 145, +1 Rare Candy A3 144, +1 Copycat B1 225.
  - C = B -1 Ilima A3 149, +1 Red A2b 071.
  - B+ = B -1 Ilima, +1 Juliana B3a 071.
  - All are 20 cards with at most 2 copies. No deck files have been written; there are no repo edits.

**Card types** (`lib/deckgym-database.json`)
- Supporter: Red, Juliana, Ilima, Copycat, Professor's Research
- Item: Rare Candy, Poké Ball, Lucky Ice Pop
- Tool: Heavy Helmet, Protective Poncho
- Stadium: Mesagoza

**Engine and coverage**
- Red: `engine/src/actions/apply_trainer_action.rs:135` (`red_effect` at :1826). The +20 applies only to an Active ex (`hooks/core.rs:1065`). Coverage says "Fully implemented" (`rl/results/floor_recheck_rules2_2026-10/07-skarmory-stall_coverage.json`).
- Juliana: `apply_trainer_action.rs:292`.
- Copycat: coverage `unpriced_text_rule` "its effect", and Kingambit "estimated at printed damage" (`floor_dustin_2026-09-30/01-..._coverage.json`).

**Setup models**
- The original model is the scratchpad's `kingambit/draft/run_draft.py`, which imports `../consistency/sim2.py` (SEED 20000000151, 100k per seat, "eager") and writes `draft_out.json`. Its numbers match the draft's table.
- The independent model is `kingambit/check/indep.py`, 100k deals, policies loose / eager / never. Outputs are `check/indep_{loose,eager,never}.json`.
- With every Trainer blank, `indep.py` agrees with the exact model: Kingambit by own turns 2-5 is 3.1/5.0/7.1/9.9, against the exact 3.0/4.7/7.0/10.0.
- Kingambit by own turn 4 (eager), indep against draft: A 34.9 v 35.5, B 58.9 v 60.5, C 58.8 v 60.1, B+ 67.9 v 69.8, A -2 Pops +Candy +Juliana 61.0 v 62.0, A -1 Pop +Candy 48.5 v 49.6, file 44.9 v 46.1.
- With Copycat never played: A 26.4, B 39.5.

**Pop arithmetic:** `kingambit/check/pops.py`. One Pop heals 40 on average and two heal 80. One Pop heals at least 40 in a turn 50% of the time; two Pops always do.

**Game facts used in the corrections** (all game turns; seat order from the ledgers)
- **Pops played:** 203719 game turns 15 (3 plays) and 17 (3); 230258 game turns 9 (3) and 11; 010003 game turns 3 and 11; 010837 game turn 9 (2); 015659 game turn 3; 020824 game turns 11 and 13 (2).
- **A Pop bought a hit** in 010003 game turn 3 (Glimmora 70 to 90, survived Drampa 70) and 203719 game turn 15 (Glimmora 20 to 80, survived Drampa 70).
- **Pawniard held in hand:** 210823 game turn 2; 015659 game turns 1 and 3; 230258 game turns 3 and 5.
- **Helmet:** on Kingambit in 010706, 203719, 210823 and 010837. On Regigigas in 230258, 010003 and 014423. On Pawniard in 225319, 210041 and 020824.
- **Copycat:**
  - Lost a piece: 203719 game turn 3 (Kingambit), 210041 game turn 8 (Kingambit), 010837 game turn 3 (Candy), 225319 game turn 4 (Candy), 014423 game turn 5 (Candy).
  - Found pieces: 010837 game turn 3 (Kingambit); 210823 game turn 4 (Kingambit and Candy).
- **Turn digests** (mechanical dumps of `TURN_LEDGER.json`): `kingambit/problems/tl/*.txt`.

**Ladder log (read-only copy)**
- 80 games: `kingambit/matchups/ladder/logs/*.json`. My check script is `kingambit/check/ladder.py`.
- Lightning (9 games): Miraidon/Magneton, Pachirisu ex, Rotom ex ×2, Magnezone ×2, Dedenne ex, Tapu Koko ex, Mega Manectric ×1.
- Hydreigon games: 3 of 4 with Mega Absol or Mega Sableye.
- The 14 non-ex main-attacker games come from the `matchups/tally.py` coding.

**Opponent lists** (all exist)
- `rl/results/b2e_card_check_2026-09-26/decks/h-charizardy_entei.txt` and `h-manectric.txt`. The Manectric list stands in poorly for the Lightning ex decks, and no Lightning ex list is saved.
- `decks/gauntlet_2026-09-26/g-dragonair_mega_rayquaza.txt`: Gouging Fire, no Drampa.
- `decks/screen/panel_ladder_2026-09-26/l-sharpedo.txt`
- `decks/screen/opponents/t-lucario.txt`, `t-suicune.txt`, `t-hydreigon.txt` (includes 1 Mega Absol ex B1 151).
- Optional: `t-blaziken`, `t-vespiquen`, `t-altaria`.

**Wallace timing and setup**
- `rl/results/draft_A_v_fire_2026-10-02/wallace/run.log`: 1,000 games from 19:06:12 to 19:08:03 UTC on Oct 2 (20 calls of 4-8 s, 110 s in total).
- `wallace/provenance.txt`: engine-2026-10-02 main-8626a35, 16 cores, `--players km3,km3`, seeds 23,200,000,000 + 500×seat + i.
- Deck 01 floor: 1,920 games in 312 s, second slowest of 20 decks (`floor_dustin_2026-09-30/timing.txt`, Sept 30 engine).

**Estimate**
- 21,000 games ≈ 57 minutes; B+ adds 7,000 ≈ 19 minutes.
- Use the official program, the one `python3 current_engine.py` prints (when this was written, Oct 15: `rl/engine-2026-10-12/deckgym`; Oct 21 to Oct 29: `rl/engine-2026-10-21/deckgym`; since Oct 29: `rl/engine-2026-10-29/deckgym`); no build is needed.
- Traces go to /tmp and are deleted after each 50-game call (`run_wallace.sh`). The 2.5 MB per game figure was not rechecked.
- C: has 4.5 GB free (about 99% full).
- Use a fresh seed block outside START_HERE's seed table.

**Scripts to adapt:** `rl/results/draft_A_v_fire_2026-10-02/analyze_wallace.py` and `run_wallace.sh`. `ADDENDUM_WALLACE.md` shows how the definitions were written down before the run.

**Sources for the bot's limits**
- `floor_dustin_2026-09-30/01-muk-glimmora-kingambit-regigigas.md:3-4, :24`
- `pause_positions_kx3_2026-10/KINGAMBIT_PASS_cloud.md:52-55` (F 12/12 at game turns 9 and 11) and `:88-95` (the 60 is the look-ahead estimate only).
- `v2/POSITION_TABLE.md`:
  - Rows 203719000-t17 and 010837000-t13: within its own turn, km3 sees the real count.
  - Rows 203719000-t07 and 210823000-t08: Blade at count 0.
  - Rows 010837000-t09 and t11: retreat into Kingambit at count 2.
  - Rows 010837000-t05, 014423000-t07 and 015659000-t05: Energy on Regigigas.
- Row 210041000-t06: km3 12/12; `p2_F_TABLES.md:37` F 12/12; `p2_C_TABLES.md:37` C 11/12.

**Not checked**
- Coverage flags of the opponent lists on the Oct 12 engine
- How fast Kingambit games run on the Oct 12 engine
- Whether km3 plays Red for a knockout this turn
- The hand coding of "main attacker" in `matchups/tally.py`, beyond the totals and the archetypes above

Win rates and matchup reads wait for a bot that passes the Kingambit test (`_blade` plus Glimmora's coin).
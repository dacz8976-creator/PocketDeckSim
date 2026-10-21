# Kingambit (deck 01): what to change, why, and what you give up

> **SUPERSEDED (Oct 15).**
> - Versions B, C and B+ below are withdrawn, after Dustin's plan correction the same day. They cut cards his plan uses: the
>   Lucky Ice Pops keep Glimmora alive for its turn, and Ilima pulls Regigigas back.
> - This page also measured speed ("Kingambit by own turn N"), which is not the deck's goal.
> - **The current comparison** is `rl/setup_tester/runs/2026-10-15_kingambit_A_A1_A2/`, from the reviewed setup tester under
>   his plan. It covers his list A, A1 and A2. The swap pool and the 2nd-Regigigas runs are beside it.
> - **The deck journal** `rl/deck_journal/journals/01-muk-glimmora-kingambit-regigigas.md` holds those results and his ladder
>   games.
> - This page is kept as history only.

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

##

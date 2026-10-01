# Grading: "Your Move, Blind 3" (Dustin's answers, Oct 1, 2026)

The quiz page is https://claude.ai/artifact/HCfxmzcTQFgHXAp8ABQAAK. It has 12 positions. Each is the first point where two bots chose differently on the same deal, on the official engine.
- **What's here** (committed after he finished, as quiz 2's were): his answers (`answers/Q01-Q12.json`, from the page's database), the 12 positions as the page showed them (`positions/`), the answer key (`answer_key.json`, kept private until now), and the build and verification notes (`BUILD_NOTES.md`, `VERIFY_NOTES.md`). In those notes, "quiz4-2026-09-30" is the private build folder's name.
- **How it was graded:** once, against the key's own rules. Only the part of the turn before any draw card counts. Where both bots make the same first tap, his written plan decides.
- **The three bots, once:**
  - **kog3** is the base bot.
  - **kta3** is kog3 with one change: it values Jasmine and Heavy Helmet differently. On your own decks that is the only difference these positions show.
  - **km3** is the newest bot: kta3 plus a Stadium change. It counts the damage a Stadium adds (Arena of Antiquity, Training Area), and the damage it takes away when it removes the opponent's. km3 has been the working bot since Sept 30 ("unconfirmed"). Its gain over kta3 on the tables was thin.
  - On the 8 table deals (Q01, Q02, Q04, Q05, Q07, Q08, Q10, Q11) the question is km3 against kta3. On your 4 decks (Q03, Q06, Q09, Q12) km3 plays exactly kta3's game, so the question is kta3 and km3 against kog3.

## In plain words

- **Table deals: km3 6, kta3 1, neither 1.**
- **Your decks: kta3/km3 1, kog3 2, decided after a draw 1.** In that last one (Q06), the Heavy Helmet he wrote down goes where kog3 put it.
- **Confidence:** sure 1 (Q08, km3), leaning 11, guess 0.
- **His Stadium rule:** play or clear a Stadium when it changes the damage now or sets up a knockout. Hold it when it does nothing this turn.
  - All six km3 answers are the first kind.
  - The one kta3 answer (Q07) is the second kind: the Arena does nothing against a Darkrai that isn't an ex. km3 plays it anyway.
- **Heavy Helmet:** both times he put it on the Active (Wailord in Q12, Muk in Q06), the Pokémon taking hits now. kta3 put it on the big Benched Pokémon both times.
- **His picks won 8 of the 10 single games that could be graded.** Single games are not evidence: one deal, one game, with draws and coin flips deciding most of it.

## 1. Outcome per position

| # | Deck v opponent, turn | What's tested | His first tap | Verdict | His deciding words | Confidence |
|---|---|---|---|---|---|---|
| Q01 | Lucario v Weezing, t2 | Your own Arena of Antiquity | Bench Hitmonlee (both bots do it) | **km3** | "play the stadium, put hitmonlee on the bench, attach energy to riolu ... Next I would probably attack with riolu" | leaning |
| Q02 | Suicune v Lucario, t2 | Field Blower's target | Field Blower | **km3** | "I would play the field blower on the stadium for sure" | leaning |
| Q03 | Your 07 Skarmory v Lucario, t5 | Jasmine or Red | Watch Over (both bots do it) | **kta3/km3** | "most likely use Jasmine" | leaning |
| Q04 | Altaria v Suicune, t4 | Training Area now or later | P on Swablu (neither bot's) | **neither** | "attach psychic energy to swablu and use sing" | leaning |
| Q05 | Suicune v Altaria, t7 | Field Blower on Training Area | Field Blower | **km3** | "Play the field blower to take away the stadium, then attack." | leaning |
| Q06 | Your 01 Muk deck v Vespiquen, t6 | Who holds Heavy Helmet | Mesagoza (neither bot's first tap) | **decided after a draw** | "use mesagoza ... I would probably go ahead and put my heavy helmet on muk" | leaning |
| Q07 | Lucario v Altaria, t8 | Your own Arena of Antiquity | Fighting Pulse | **kta3** | "Korrina and the stadium don't help your attack against darkrai so I would save them for later" | leaning |
| Q08 | Weezing v Lucario, t5 | Field Blower on the Arena | Field Blower | **km3** | "No downside to using field blower to get rid of the stadium." | sure |
| Q09 | Your 07 Skarmory v Altaria, t1 | Jasmine or Research | Bench Indeedee ex (both bots do it) | **kog3** | "Put indeedee ex on bench, use professor's research, depends on draw" | leaning |
| Q10 | Altaria v Hydreigon, t4 | Training Area before Copycat | Evolve Eevee (both bots do it) | **km3** | "Evolve eevee, play training area, use copycat, depends on draw." | leaning |
| Q11 | Suicune v Altaria, t9 | Soothing Shore over Training Area | Soothing Shore | **km3** | "The most important thing is playing soothing shore or altaria will kill suicune" | leaning |
| Q12 | Your 03 Wailord v Sceptile, t6 | Who holds Heavy Helmet | Soothing Shore (both bots play it) | **kog3** | "play the heavy helmet on the active wailord and the energy there and end my turn" | leaning |

How the close calls were settled:

- **Q01.** Arena and the Energy on Riolu are firm. The attack is "probably". His other idea ("retreat and protect riolu") would be the Arena without an attack, which matches neither bot. Neither branch is kta3's turn (Energy on Hitmonlee, no attack). His main line is km3's turn move for move. His note even has km3's number: "Riolu's attack would do 60 damage" (10, +30 against an ex, +20 from the Arena).
- **Q03.** His plan plays Poké Ball before the Supporter. Poké Ball normally counts as a draw, but here it can't draw anything. His deck has no Basic Pokémon left (the page shows Indeedee ex and both Skarmory ex at 0 left), and he says so: "no basics left in the deck". So it doesn't cut his plan short. Red only comes up if two Lucky Ice Pops flip heads and he reaches 130 HP, and even then it's "consider Red". Read strictly by the list of draw cards, this would be "decided after a draw" instead.
- **Q04.** Both bots evolve into Mega Altaria ex, put Small Balloon and the P on it, and end the turn without attacking. He doesn't evolve. He attacks with Sing instead, so his turn matches neither. He never mentions Training Area. By leaving it out he holds it, which is kta3's side of the Stadium question. That isn't counted, because he never says it.
- **Q06.** The deciding question is where the Helmet goes. His plan uses Mesagoza (a draw) before he gets to the Helmet. By the rule, that makes it "decided after a draw". What he wrote after it, Helmet on the Active Muk, is kog3's spot. It's reported here but not counted.
- **Q11.** He'd hold Inflatable Boat this turn ("I wouldn't on this turn"). Both bots play it, so it doesn't separate them. On the question being tested, Soothing Shore, he is with km3.

## 2. Totals

**Table deals (km3 against kta3):** km3 6 (Q01, Q02, Q05, Q08, Q10, Q11), kta3 1 (Q07), neither 1 (Q04).
- Seven graded answers is a small sample. If he were picking between the two at random, 6 or more of 7 going one bot's way would happen about 1 time in 8.

**Your decks (kta3 and km3 against kog3):** kta3/km3 1 (Q03), kog3 2 (Q09, Q12), decided after a draw 1 (Q06, written Helmet on kog3's spot).

**By confidence:**
- Sure (1): km3 1 (Q08).
- Leaning (11): km3 5, kta3 1, neither 1 on the table deals. On your decks: kta3/km3 1, kog3 2, after a draw 1.
- Guess: none.

**Each choice's single game, beside his pick** (result for the deck he was playing):

| # | His side | His side's game | The other side's game |
|---|---|---|---|
| Q01 | km3 | win 4-0 | kta3: loss 2-5 |
| Q02 | km3 | win 3-2 | kta3: loss 2-3 |
| Q04 | neither | n/a | km3: loss 0-3; kta3: loss 2-3 |
| Q05 | km3 | win 5-2 | kta3: loss 2-3 |
| Q07 | kta3 | win 5-2 | km3: loss 2-5 |
| Q08 | km3 | loss 1-4 | kta3: win 3-2 |
| Q10 | km3 | loss 2-3 | kta3: win 4-2 |
| Q11 | km3 | win 4-2 | kta3: loss 1-4 |
| Q03 | kta3/km3 | win 3-2 | kog3: loss 0-4 |
| Q06 | after a draw (wrote kog3's Helmet spot) | n/a | kta3/km3: win 2-2 (opponent ran out of Pokémon); kog3: loss 2-3 |
| Q09 | kog3 | win 3-2 | kta3/km3: loss 0-4 |
| Q12 | kog3 | win 4-2 | kta3/km3: loss 1-3 |

His side won 8 of 10: 5 of 7 on the table deals and 3 of 3 on his decks. **These are single games and are not evidence either way.** Each is one deal played once, and later draws and coin flips decide most of it. The key says the same.

## 3. What it says

**Does his play lean to km3's Stadium choices? Yes, where the Stadium matters this turn.** This is evidence only. It decides nothing about km's adoption.

- All six km3 answers are Stadiums that change the damage now or the next hit:
  - Q01: the Arena makes Riolu's attack 60 on Darkrai ex this turn.
  - Q02, Q08: the opponent's Arena powers up their Fighting attacks on you. In Q02: "The poncho isn't helping the opponent so get rid of the stadium."
  - Q05, Q11: the opponent's Training Area turns Mega Harmony's 130 into exactly 140, a knockout on Baxcalibur or Suicune ex. He saw it both times.
  - Q10: Training Area before Copycat. He gave no reason. Holding it would let Copycat shuffle it back into the deck.
- Where the Stadium does nothing this turn, he holds it, like kta3:
  - Q07 (the Darkrai isn't an ex). He wants it for next turn's Mega Altaria ex: "up to 190 (210 if you draw lucario) against altaria if you save korrina and the stadium for then".
  - Q04 (Mega Harmony needs two P, so no attack this turn). He doesn't play it either, though his turn differs in other ways.
  - km3 plays the Stadium in both spots.
- **So:** if km3's thin gain is real, his answers say it comes from Stadiums that matter now. Playing a Stadium that does nothing this turn is the part he wouldn't do. That would be worth a look if km3 is ever tuned. One game each way (Q07 km3 lost, Q04 both lost) proves nothing.

**On your decks (kta3's Jasmine and Heavy Helmet change, against kog3): a small lean toward kog3.** This doesn't touch km, because km3 plays exactly as kta3 here.
- **Jasmine:**
  - He plays it when the numbers say it keeps Skarmory ex alive (Q03): "They do 140 damage next turn. So unless they have Korrina, I'm safe another turn with Jasmine use and attacking."
  - On turn 1 he plays Research instead (Q09), because the worst case is only 80 damage: "You can heal multiple ways next turn."
- **Heavy Helmet:** both times on the Active, the Pokémon being hit now (Q12, and Q06 as written). kta3 put it on the full-HP Benched Wailord ex and on the Benched Regigigas.

## 4. Reasons in his notes the bots can't see, and rule points

1. **Opponent's hand, by name.**
   - Q03: "unless they have Korrina". The key lists Korrina as one of the hidden cards that decide whether Skarmory ex survives.
   - Q12: "hope they don't heal".
2. **The opponent's unseen deck, guessed from what's shown.**
   - Q09: from one Eevee, "Worst case scenario the[y] evolve eevee to espeon and play two darkrai on the bench. This would do 80 damage." Only Eevee was on the page.
   - Q09, on Starting Plains: "it is then at risk of being field blower'ed or a new stadium can kick it out".
   - Q02: "If this was a deck that likely had poison or sleep I would save the pokemon center lady".
3. **Hand size against Copycat.** This is the same habit as quiz 2.
   - Q03: he plays a Poké Ball that can't find anything, to "get it out of my hand and avoid an extra card draw from opponent copycat". One Copycat is already in the opponent's discard.
   - Q05: he'd play Team Rocket's Boss into a full Bench "to get rid of a card". He doesn't say why, but it is probably the same idea.
   - Neither bot thins its hand for this reason.
4. **Rule point, Q06:** "regigigas can't attack if muk dies". That's right. Alolan Muk's Power of Alchemy is what turns off Regigigas's Seal of Antiquity (the note the checker added to the page). It's his reason for the Helmet on Muk: "to try and keep him alive". The bots have the rule. Whether they value Muk's survival for Regigigas's sake is worth a look.
5. **No rule questions.** He asked none. He didn't pick the odd "Use the Stadium Fragrant Forest" option in Q06 or Q12.

## 5. Comments on the bots' earlier play (before each position)

- Q01: "I would have played hitmonlee into the active position to start."
- Q04: "I don't know why you retreated eevee and if you were going to you should have used small balloon on it first."
- Q06: "I would have attached the first 2 darkness energies on grimer, retreated and promoted regigigas, evolved grimer to muk on the bench."
- Q10: "This deck wants darkrai on the bench and loses when darkrai is active". That's the same point as his quiz 2 follow-up on Altaria's Darkrai.

## 6. Optional follow-ups (two would settle the open spots)

1. **Q06:** If Mesagoza's flip had found nothing, would the Heavy Helmet still go on Muk, not on the Benched Regigigas?
2. **Q04:** Leave aside Sing or evolving. If you did evolve into Mega Altaria ex this turn, would you play Training Area now or keep it?

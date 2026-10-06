# Quiz 4 ("Your Move, Blind 4"): results (Oct 6)

Dustin answered all 12 positions on Oct 6. Each position is the first decision where kx3 (claude/playout-pilot d513e37b)
and km3 chose differently on the same deal, with the two plans shown as Plan A and Plan B and nothing saying which bot
chose which. The key, private until now, is `answer_key_q4.json` in this folder.

## In short

| | km3's plan | kx3's plan | Neither | Both reasonable |
|---|---|---|---|---|
| All 12 | **6** | **2** | **4** | 0 |
| Setup decks (Q01-Q09) | 4 | 2 | 3 | 0 |
| Fast decks (Q10-Q12) | 2 | 0 | 1 | 0 |

- At the point where the two bots first part, Dustin preferred km3's plan three times as often as kx3's. In 4 of the 12
  he would play something else; his plans are below.
- This is despite kx3's game winning on 9 of these 12 deals (the positions were picked where the two games ended
  differently). One game's result after a split is weak evidence about the split itself: the rest of the game decides it.
- It doesn't contradict the strength results (kx3 +16.6 and +15.2 in development, +21.3 on the exam). Those are thousands
  of decisions; this is one decision per game. It does say kx3's *distinctive* first choices, at least these, mostly
  don't look like good play to a strong human.

## The positions

The "plan" columns name which bot's plan he chose; the games' results are for the deck in each arm.

| Q | deck, own turn | what differed | his answer | sure? | kx3's game | km3's game |
|---|---|---|---|---|---|---|
| Q01 | Muk, 2 | kx3: Darkness to the Bench + Fragrant Forest; km3: Darkness to Glimmora + Venomous Hit | **km3** | sure | win | loss |
| Q02 | Muk, 4 | kx3: Bench Energy, no attack; km3: attack | **km3** | sure | win | loss |
| Q03 | Muk, 5 | kx3: retreat, evolve on the Bench; km3: evolve the Active, attack | **km3** | sure | win | loss |
| Q04 | Wailord, 2 | kx3: Energy, Watch Over ×2, retreat, Poké Ball; km3: Poké Ball | **km3** | sure | win | loss |
| Q05 | Wailord, 3 | kx3: Bench Energy, Center Lady, evolve; km3: Center Lady, evolve, Active Energy | Neither (km3's "better") | leaning | loss | win |
| Q06 | Indeedee/Stoutland, 2 | kx3: Bench Energy, Watch Over, pass; km3: Watch Over, Energy, Psychic | Neither | leaning | win | loss |
| Q07 | Indeedee/Stoutland, 2 | kx3: attack with Psychic; km3: Bench Energy, pass | Neither | sure | win | loss |
| Q08 | Indeedee/Stoutland, 2 | kx3: retreat, Rare Candy...; km3: attack | **kx3** | sure | loss | win |
| Q09 | Skarmory, 5 | kx3: Poké Ball; km3: Watch Over, Bench Energy, Steel Wing | **kx3** | sure | win | loss |
| Q10 | Manectric, 2 | kx3: Bench Energy, retreat, Thunder Shock; km3: Active Energy, pass | **km3** | leaning | win | loss |
| Q11 | draft A, 3 | kx3: retreat, Gnaw; km3: bench Vulpix, Turbo Shark | Neither | leaning | win | loss |
| Q12 | Xatu, 2 | kx3: end the turn; km3: attack with Supernatural Feather | **km3** | sure | loss | win |

## His notes (verbatim) and what they say about the bots

- **Q01:** "You have no grass pokemon so using the stadium is a waste of time. Doesn’t harm anything to use stadium"
- **Q02:** "Attack when you can, poison. No rush to get kingambit ready with Regigas and glimmora to wall"
- **Q03:** "You didn’t say the result of glimmora’s ability after it was knocked out so I don’t know if the opponent has 1 or 2 points, but either way attacking with glimmora is the better option"
- **Q04:** "Plan B is pointless. Using the abilities are a waste of time since it won’t do anything, retreating before using the poke ball is a mistake because you can only retreat once per turn"
- **Q05:** "A is better, but the 30 healing isn’t that helpful. The opponent can do a max of 140 damage next turn so wailord will survive. Pokemon center lady may come in handy next turn if sleep attack is used. The rest of plan A is correct"
- **Q06:** "I would use the bench indeedee’s ability to heal the active one, retreat the active indeedee to lillipup, attach energy to lillipup and attack. Reasoning - indeedee 30 damage will do 0 to bonsly and since they won’t be attaching energy to bonsly, indeedee is useless as an attacker against it."
- **Q07:** "Retreat indeedee, promote stoutland, attach energy to stoutland, end turn. Stoutland causes opponent to need extra energy to attack and is worth 1 point versus indeedee 2 points and valuable for healing ability"
- **Q08:** "Well I wouldn’t use the ability or stadium because they won’t do anything, but the rest for sure"
- **Q09:** "Again indeedee’s ability does nothing here"
- **Q10:** "I wouldn’t have used the backpack with no Pokemon that it would help. Retreat is free, but heatmor hits bench and manectric is priority"
- **Q11:** "I would probably attack with sharpedo and attach its energy to lapras. Putting vulpix on the bench gives the opponent an extra 20 damage. If I retreated sharpedo I would promote lapras not vulpix"
- **Q12:** "Not sure why you wouldn’t attack"

Patterns:
1. **kx3 too often skips an attack it has** (Q02, Q03, Q12; Q01 and Q10 in part). "Attack when you can" is his rule
   here. This matches the position study: kx3 switches to "end the turn" or away from an attack on small leads (half its
   switches only just clear 2 standard errors).
2. **Both bots spend actions that do nothing**: Watch Over at full HP, Fragrant Forest without Grass Pokémon, Clemont's
   Backpack with no target (Q01, Q04, Q08, Q09, Q10). He calls them harmless but pointless. One costs something: a
   retreat before Poké Ball uses up the turn's only retreat (Q04).
3. **His "neither" plans are the planning the project wants**, all from setup decks or about the Bench:
   - Q06: switch attackers against a Bonsly that walls Indeedee. Psychic does 30 plus 30 for each Energy on the defender.
     A Bonsly with no Energy takes only the 30, and its own damage reduction (the −30 noted in the Oct 2 rules flags)
     takes that to 0.
   - Q07: promote Stoutland, worth 1 point and taxing the opponent's attacks, to keep the 2-point Indeedee healer safe.
   - Q11: don't bench the Vulpix, because the opponent's attack does more for each Benched Pokémon.

   Neither bot found any of these three.

## Follow-ups

- **For the pilot (next development round):**
  - a stricter bar for switching away from an available attack;
  - a tie-break against actions with no effect (the Tool tie-break's logic, applied to Abilities and Stadiums);
  - his three "neither" plans, as targets for the continuation experiment and future positions.
- **For the quiz pages:** show what an Ability did when its Pokémon was Knocked Out (Q03: Glimmora's), so points are
  never in doubt.
- **Card facts to keep:** Q11's "+20 for each Benched Pokémon" and Stoutland's attack tax. These are card text and are
  checked against the database before use, never asked again.

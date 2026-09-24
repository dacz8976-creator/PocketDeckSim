# Brew notes — 2026-09-10

Ideas, not results. Every list in this folder is a first draft built from card text in
`deckgym-database.json`; none has been played or simmed. Play 10–15 ladder games before
deciding anything. None of these pairings appears in the Limitless top 30 as of today
(`decks/classifier/limitless_2026-09-10.json`); the only Team Rocket's Weezing ex archetype
there is Weezing/Hoopa ex (4.2% share, 634–595).

Where things are: `decks/dustin/` holds the 15 decks decoded from in-game QR codes
(`lib/decode_qr.py`); `decks/classifier/` holds the classifier inputs and the full report;
`lib/deck_classifier.py` is the schema classifier. Run from the project root:

    python lib/deck_classifier.py deckgym-database.json deckgym-fork-s193/src decks/classifier/my_decks.json "query=B4a 043"

`deck_check.py pool decks/brews` and `deck_check.py pool decks/dustin` both pass (2026-09-10).

## brew-01 Arceus / Crobat / Xatu (Psychic)

Xatu's Life Drain sets their Active to 10 HP. On your next turn Crobat's Cunning Link does 30
as an ability before you attack, so the 10-HP Pokémon dies, they promote, and Arceus or Xatu
hits the replacement. Every Xatu heads is a knockout plus a full attack in one turn; Will makes
the flip heads when it matters. Arceus costs CCC so Psychic energy powers it; Crobat never needs
to attack. Fabled Luster still walls Altaria/Espeon sleep. Natu A4 081 (50 HP) and Zubat are
both Lisia targets. Cost: no Nihilego poison (needs Dark).

## brew-02 Arceus / Tandemaus / Persian (any energy — Dark chosen so Nihilego can slot in)

Arceus does 70 + 20 per benched Pokémon, so a full bench is 130. Tandemaus's Flock (one
Colorless) puts three random Tandemaus/Maushold from the deck onto the bench — one attack, bench
full. Maushold then hits for one energy: 60 per heads, one flip per mouse in play. Team Rocket's
Persian (from a 50-HP Meowth, another Lisia target) does 10 + 40 per Pokémon on *their* bench
for CC, so it's the attacker while Arceus sits on two energy. Team Rocket's Boss is the spice:
look at their hand and put every Basic onto their bench — fills Persian's count and strips the
Basics they were holding. Open rules point: whether Flock can put a Stage 1 Maushold directly
into play as the text reads — check in-game before building around it.

## brew-03a / 03b Arceus / Nihilego / Toxapex (Dark)

Toxapex B3b 047 Severe Poison: Poisoned, and the poison does 40 instead of 10. Nihilego's More
Poison should push that to 50 if the two stack — untested, verify in one game. Goo-zooka keeps
them from retreating out of it; Mareanie B3b 046 Venoshock is 80 for DC on a 60-HP Basic if
they're poisoned. 03a is the clean version (8 Pokémon, no Crobat). 03b keeps the Zubat/Crobat
line for the extra 30 ping and runs 9 trainers, which is thin — if it bricks, that's why. Pick
by which piece you'd miss more.

## brew-04 Xatu / Team Rocket's Slowking ex (Psychic)

Deck 10 with the Oricorio B4 slot replaced by TR Slowpoke/Slowking ex. Slowking does 20 per card
in your hand for PC and draws a card each turn while Active; a six-card hand is 120. Oricorio B4
discards from hand, so it worked against this. Copycat and Hiking Trail also came out: Copycat
shuffles your hand away (resets the size you're trying to grow) and Trail only draws up to 3.
Arcade is in as a gamble (all three heads → draw to 7), Lucky Egg refills after a knockout.
Retreat cost 3 is the real cost; X Speed is there for it. Koffing/Weezing stay as the on-evolve
Poison + Burn piece.

## brew-05 Meowstic / Hatterene confusion lock (Psychic)

Meowstic B3 066 confuses their Active every turn as an ability while it's in the Active Spot —
no attack needed, so in Pocket half their attacks fail outright. Behind it, Hattrem confuses
for P and Hatterene does 140 for PP if they're confused. Confusion stays until they retreat or
evolve, so Meowstic's one-cost retreat into Hatterene works. Team Rocket's Master Plan covers
the turns Meowstic isn't up front (tails confuses you too — use it when you don't need to
attack). Stage 2 line, hence two Rare Candy.

## Things to check on the existing lists

Deck 10 (Xatu/Oricorio/TR Weezing): Koffing's Reverse Thrust (D) and Weezing's Confusion Gas
(DD) can never be used — the deck is Psychic-only. Fine if Weezing is there purely for the
on-evolve Poison + Burn; a problem if you expected to attack with it.

Correction to what I said in chat: I flagged Hypno fighting Raticate's energy theft in deck 14.
Wrong — deck 14 runs Team Rocket's Hypno (Entrap: gust + 50), not Hypno B4 067. Entrap pulls
the same direction as Raticate. Nothing to fix there.

## Cards worth revisiting when the next set lands

Team Rocket's Muk (heals 60 if they're poisoned, 120 HP) for any poison shell; Swellow (forces
their Basic off the Active Spot, ability) with bench-damage decks; Polteageist (on-evolve hand
reset) for a denial shell with Red Card/Mars; Mimikyu ex as a free-turn wall in Psychic lists.

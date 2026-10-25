from v2_helpers import P, B
D = 'v2deck_995ac0891e'; G = '20261023_231312000_SR'
SQ = 'Squirtle P-A 033'; EI = 'Eiscue B1 080'; MB = 'Mega Blastoise ex B1a 020'; PB = 'Poké Ball P-A 005'; LI = 'Lillie A3 155'
SS = 'Soothing Shore B4 154'
GI = 'Gible B4a 052'; DR = 'Dratini A3b 051'; MW = 'Meowth B2 124'; OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[MB, SS, PB, PB, LI], disc=[], dene='', board=[B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[OPB, OPB, OCC], dene='', board=[B(GI, 60), B(DR, 60), B(MW, 50)], ko=0),
  ['Play:Poké Ball', 'Play:Poké Ball', 'Place:Eiscue@1', 'Place:Eiscue@2', 'Play:Soothing Shore', 'Attach:1Water@0 zone',
   'Attack:Water Gun'],
  D, None,
  approx=AP + "; the opponent's hand (4) counts its two global-1 Poke Balls as +1 each (Dratini and Meowth were benched) and its "
            "Copycat as drawing 4 (his hand then held 4); the opponent's Trainer printings (Poke Ball, Copycat) are not shown, the "
            "first listed are used; the opponent's Bench order (Dratini, Meowth) is the order benched",
  ambiguous=['Opponent Dratini printing chosen by HP (60) only (its attack was not shown); A3b 051, A4b 267, A4b 268, B2b 051, '
             'B2b 105 and B4 116 match',
             "Opponent Meowth printing chosen by HP (50) only; B2 124 and B2 204 match",
             'Opponent Trainer printings in the discard not shown: Poké Ball A2b 111 used (P-A 005 also matches), Copycat B1 225 '
             'used (B1 270 also matches)'],
  draws={0: [EI], 1: [EI]},
  notes="Global 2 = his 1st turn (he went second). Opening five at 24 s: Mega Blastoise ex, Soothing Shore, two Poke Ball, Squirtle; "
        "Squirtle Active, no Bench -> 4; draws Lillie -> 5. Opponent: Gible 60 Active; global 1 two Poke Balls, Dratini 60 and Meowth "
        "50 benched, Copycat ~64 s; hand 5 - 1 = 4, draw 5, Poke Balls 5, two benched 3, Copycat (-1, redraw 4 = his hand) 4. Move "
        "(global 2 section): both Poke Balls ~83/88 s (each finds an Eiscue), both Eiscue benched (the review gives the two plays, "
        "then the two benchings; the exact interleaving is not given), Soothing Shore ~102 s, Water to Squirtle, Water Gun ~109-111 s "
        "(Gible 60 -> 40)."),
]

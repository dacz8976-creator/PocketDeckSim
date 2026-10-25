from v2_helpers import P, B
D = 'v2deck_c4ac51db37'; G = '20261023_221617000_SR'
LP = 'Lillipup A3a 054'; ST = 'Stoutland A3a 056'; IN = 'Indeedee ex B1 121'; PR = "Professor's Research P-A 007"
RC = 'Rare Candy A3 144'; CH = 'Cheren B3 151'; LI = 'Lillie A3 155'; PS = 'Psychic B4 150'
EN = 'Entei ex A4a 010'; CM = 'Charmander B2b 007'; GC = 'Giant Cape A2 147'; RCV = 'Rainbow Cave B4 155'
OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 3, 2, [0, 0],
  dict(hand=[RC, PS, CH, LI, ST], disc=[PR], dene='', board=[B(LP, 60), B(IN, 130), B(LP, 60)], ko=0),
  dict(hand_count=4, disc=[OPB, OCC], dene='', board=[B(EN, 140, 'R'), B(CM, 90, tool=GC), B(EN, 140)], ko=0),
  ['Play:Rare Candy', 'Evolve:Stoutland@0', 'Attach:1Psychic@0 zone', 'EndTurn'],
  D, None, stadium={"card": RCV, "owner": 1},
  approx=AP + "; the opponent's hand (4) counts its global-2 Poke Ball as +1 (it found the benched Charmander), its Copycat as "
            "drawing 4 (his hand then held 4) and one Legendary Pulse draw at its turn end; the opponent's Trainer printings (Poke "
            "Ball, Copycat, Giant Cape) are not shown, the first listed are used; the opponent's next Energy after its Rainbow Cave use "
            "is not shown, so none is set; the Energy its Rainbow Cave use discarded on global 2 is not in its discarded Energy (the "
            "review does not name its type); the opponent's Bench order (Charmander, then Entei ex) is the order the review names them",
  ambiguous=['Opponent Entei ex printing chosen by HP (140) and Ability title (Legendary Pulse); A4a 010, A4a 079, A4a 087, B2a 126 '
             'and P-A 110 match',
             'Opponent Charmander printing chosen by HP (70 before Giant Cape) only (its attack was not shown); B2b 007 and B2b 091 match',
             'Opponent Giant Cape printing not shown; A2 147, A4b 320 and A4b 321 match',
             'Opponent Trainer printings in the discard not shown: Poké Ball A2b 111 used (P-A 005 also matches), Copycat B1 225 '
             'used (B1 270 also matches)'],
  notes="Global 3 = his 2nd turn (he went first). Setup: opening five Indeedee ex, Lillipup, Rare Candy, Professor's Research, Psychic; "
        "Lillipup Active, Indeedee ex on the left Bench -> hand Rare Candy, Research, Psychic. Global 1: draws the 2nd Lillipup, benches "
        "it beside Indeedee (@2), Professor's Research draws Cheren and Lillie -> hand Rare Candy, Psychic, Cheren, Lillie. Global 3: "
        "draws Stoutland -> 5. Opponent global 2: Fire to Entei ex, Poke Ball (Charmander), Charmander and 2nd Entei ex benched, Giant "
        "Cape on Charmander (70 -> 90), Copycat, Rainbow Cave played and used, Legendary Pulse draw. Hand 5 - 1 = 4, draw 5, Poke Ball "
        "5, two benched 3, Cape 2, Copycat (-1, redraw 4) 4, Rainbow Cave 3, Pulse 4. Move (global 3 section): Rare Candy evolves the "
        "Active Lillipup to Stoutland 140, Psychic to Stoutland, no Supporter, no attack."),
]

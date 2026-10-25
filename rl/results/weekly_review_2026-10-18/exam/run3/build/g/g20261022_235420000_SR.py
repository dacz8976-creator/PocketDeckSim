from v2_helpers import P, B
D = 'v2deck_ba2eca5816'; G = '20261022_235420000_SR'
GM = 'Goomy B1 177'; TR = 'Trapinch B3 076'; FX = 'Flygon ex B3 126'; DR = 'Dratini B4 116'; DA = 'Dragonair B4 117'; XS = 'X Speed P-A 002'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'; CC = 'Copycat B1 225'
HT = 'Hiking Trail B2b 069'
# opponent's cards (printing: the first cards.py lists among those matching the shown facts)
O_HA = 'Happiny B4a 063'; O_RI = 'Riolu A2b 042'; O_ML = 'Mega Lucario ex B3 081'; O_RE = 'Repel A3a 064'
O_PC = 'Pokémon Center Lady A2b 070'; O_KO = 'Korrina B3 149'; O_SB = 'Small Balloon B3b 064'
TRAIL = {"card": "Hiking Trail B2b 069", "owner": 0}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_HA = 'Opponent Happiny printing chosen by HP (30) and attack title (Chubby Cheer); B4a 063 and B4a 077 match'
AMB_RI = 'Opponent Riolu printing chosen by HP (70) only; its attack was not shown (70-HP Riolu printings have Punch)'
AP_RI = "the opponent's two Riolu are listed in the order benched (the review names the left one, which received the first Fighting)"
AP_CC = ("the opponent's Chubby Cheer (+20 to the opponent's attacks during its next turn) is not represented: the position format has "
         "no effect for it")

POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[PB, PB, PR, PR], disc=[], dene='', board=[B(DR, 50), B(TR, 60)], ko=0),
  dict(hand_count=3, disc=[O_RE], dene='', board=[B(O_HA, 30), B(O_RI, 70)], ko=0),
  ['Play:Poké Ball', 'Play:Poké Ball', "Play:Professor's Research", 'Attach:1Fighting@0 zone', 'Place:Goomy@2', 'Place:Trapinch@3',
   'Attack:Slam'],
  D, None, ez_now='F', ez_next='F',
  approx=AP + "; " + AP_CC + "; the opponent's Repel printing is not shown, the first listed printing is used; his next Energy "
            "(Fighting) is the one he attached on global 4",
  ambiguous=[AMB_HA, AMB_RI],
  draws={0: [TR], 1: [GM], 2: [RC, CY]},
  notes="Global 2 = his 1st turn (he went second). Setup: opening five Dratini, two Poke Ball, Professor's Research, Trapinch; Trapinch "
        "Active, Dratini Benched -> 3 in hand; draw Professor's Research -> 4. Global 1: Repel (he chose Dratini Active, Trapinch to the "
        "Bench), Chubby Cheer 10 -> Dratini 50. Opponent hand 5 - 2 = 3, draw 4, Repel 3. His move in the review's order (64-113): Poke "
        "Ball (Trapinch), Poke Ball (Goomy), Research (Rare Candy, Cyrus), Fighting to Dratini, Goomy and 2nd Trapinch benched (@2, @3), "
        "Slam (tails, heads: 20, Happiny 30 -> 10). Energy: Fighting now (attached), Fighting next (attached on global 4)."),
P(G, 4, 2, [0, 0],
  dict(hand=[PR, RC, CY, FX], disc=[PB, PB, PR], dene='', board=[B(DR, 20, 'F'), B(TR, 60), B(GM, 40), B(TR, 60)], ko=0),
  dict(hand_count=3, disc=[O_RE], dene='', board=[B(O_HA, 10), B(O_RI, 70, 'F'), B(O_RI, 70)], ko=0),
  ['Play:Rare Candy', 'Evolve:Flygon ex@1', "Play:Professor's Research", 'Play:Hiking Trail', 'Attach:1Fighting@1 zone', 'Attack:Slam'],
  D, None, ez_now='F', ez_next='G',
  approx=AP + "; " + AP_CC + "; " + AP_RI + "; the opponent's Repel printing is not shown, the first listed printing is used; his "
            "next Energy (Grass) is the one he attached on global 6",
  ambiguous=[AMB_HA, AMB_RI],
  draws={2: [HT, DR]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Professor's Research (the 2nd), Rare Candy, Cyrus; draw Flygon ex -> 4. Board: "
        "Dratini 50 - 30 (Chubby Cheer 10 + 20, global 3) = 20 with one Fighting; Bench left to right Trapinch (moved by Repel), Goomy, "
        "2nd Trapinch (the review's 'left Bench Trapinch' is taken as the first, @1). Opponent global 3: 3 + draw 4, 2nd Riolu benched 3, "
        "Fighting to the left Riolu; Happiny 10 (Slam). His move in the review's order (144-193): Rare Candy on the left Trapinch -> Flygon "
        "ex, Research (Hiking Trail, 2nd Dratini), Hiking Trail, the retreat menu opened and cancelled (not an action), Fighting to "
        "Flygon ex (@1), Slam (two tails, 0). Hiking Trail's end-of-turn draw (Dragonair) is after his move."),
P(G, 6, 3, [0, 1],
  dict(hand=[CY, DR, DA, DA], disc=[PB, PB, PR, RC, PR, DR], dene='F', board=[B(GM, 40), B(FX, 180, 'F', behind=[TR]), B(TR, 60)], ko=1),
  dict(hand_count=3, disc=[O_RE, O_PC], dene='', board=[B(O_HA, 30), B(O_RI, 70, 'F'), B(O_RI, 70, 'F')], ko=0),
  ['Place:Dratini@3', 'Attach:1Grass@1 zone', 'EndTurn'],
  D, None, stadium=TRAIL, ez_now='G', ez_next='F',
  approx=AP + "; " + AP_CC + " (Happiny's Chubby Cheer on global 5); " + AP_RI + "; the opponent's Trainer printings (Repel, Pokemon "
            "Center Lady) are not shown, the first listed printings are used; his next Energy (Fighting) is the one he attached on global 8",
  ambiguous=[AMB_HA, AMB_RI],
  notes="Global 6 = his 3rd turn. Hand after global 4: Cyrus, 2nd Dratini + Hiking Trail's draw Dragonair; draw 2nd Dragonair -> 4. "
        "Global 5: Fighting to the right Riolu, Pokemon Center Lady (Happiny 10 -> 30), Chubby Cheer 30 KOs Dratini 20 (its Fighting to "
        "the discard), he promoted Goomy 40. Opponent hand 3 + draw 4, Lady 3; Hiking Trail draws nothing at 3. Board (compacted): Goomy "
        "Active, Flygon ex 180 one Fighting (@1), 2nd Trapinch (@2). His move in the review's order (236-246): 2nd Dratini benched (lowest "
        "empty slot @3; the game showed it in Goomy's old middle spot), Grass to Flygon ex, no attack."),
P(G, 8, 4, [0, 1],
  dict(hand=[CY, DA, DA, XS], disc=[PB, PB, PR, RC, PR, DR], dene='F',
       board=[B(GM, 40), B(FX, 180, 'GF', behind=[TR]), B(TR, 60), B(DR, 60)], ko=1),
  dict(hand_count=3, disc=[O_RE, O_PC], dene='', board=[B(O_HA, 30), B(O_ML, 190, 'FF', behind=[O_RI]), B(O_RI, 70, 'F')], ko=0),
  ['Evolve:Dragonair@3', 'Play:X Speed', 'Retreat:1', 'Ability@3', 'Attach:1Fighting@2 zone', 'Attack:Dragon Pulse'],
  D, None, stadium=TRAIL, ez_now='F', ez_next='G',
  approx=AP + "; " + AP_RI + "; the opponent's Trainer printings (Repel, Pokemon Center Lady) are not shown, the first listed printings "
            "are used; his next Energy (Grass) is the one he attached on global 10",
  ambiguous=[AMB_HA, AMB_RI, 'Opponent Mega Lucario ex printing chosen by HP (190); B3 081, B3 184 and B3 204 match'],
  notes="Global 8 = his 4th turn. Hand after global 6: Cyrus, two Dragonair (Hiking Trail: 3 in hand, no draw); draw X Speed -> 4. "
        "Opponent global 7: 3 + draw 4, left Riolu -> Mega Lucario ex 190 (3), its 2nd Fighting attached; no attack; Trail no draw. His "
        "move in the review's order (279-341): Benched Dratini (@3) -> Dragonair, X Speed, Goomy retreats for 0 to Flygon ex (@1), "
        "Dragon's Blessing (Dragonair @3) moves the discarded Fighting to Flygon ex, Fighting from the zone to Trapinch (@2), Dragon "
        "Pulse 140 KOs Happiny (top card Copycat discarded). Hiking Trail's draw (Cyrus) and Sand Slammer come after his move."),
P(G, 10, 5, [1, 1],
  dict(hand=[CY, DA, CY, RC], disc=[PB, PB, PR, RC, PR, DR, XS, CC], dene='',
       board=[B(FX, 10, 'GFF', behind=[TR]), B(GM, 40), B(TR, 60, 'F'), B(DA, 80, behind=[DR])], ko=1),
  dict(hand_count=3, disc=[O_RE, O_PC, O_HA, O_KO], dene='', board=[B(O_ML, 170, 'FFF', tool=O_SB, behind=[O_RI]), B(O_RI, 50, 'F')], ko=1),
  ['Attach:1Grass@2 zone', 'Attack:Dragon Pulse'],
  D, None, stadium=TRAIL, ez_now='G', ez_next='G',
  approx=AP + "; Hiking Trail's end-of-turn draw for the opponent on global 9 counted as +1 (to 3 cards); the opponent's Trainer "
            "printings (Repel, Pokemon Center Lady, Korrina, Small Balloon) are not shown, the first listed printings are used; his next "
            "Energy is not shown (the game ended before his next turn): Grass is given, Grass and Fighting being equally likely",
  ambiguous=[AMB_HA, AMB_RI, 'Opponent Mega Lucario ex printing chosen by HP (190) and attack title (Fighting Pulse); B3 081, B3 184 '
             'and B3 204 match', 'Opponent Small Balloon printing not shown; B3b 064 and B3b 106 match'],
  notes="Global 10 = his 5th turn. Hand after global 8: Cyrus, Dragonair + Hiking Trail's draw Cyrus (2nd); draw Rare Candy -> 4. Board: "
        "Flygon ex 180 - 170 (Fighting Pulse 90 + 50 + Korrina 30) = 10 with Grass, Fighting, Fighting; Bench Goomy 40 (@1, retreated "
        "there), Trapinch 60 one Fighting (@2), Dragonair 80 (@3). Discard: two Poke Balls, two Research, Rare Candy, Dratini, X Speed, "
        "Copycat (milled); the discarded Fighting was moved by Dragon's Blessing. Opponent: Mega Lucario ex promoted after the Happiny "
        "KO; Sand Slammer twice (global 8 and 9 checkups): Mega 190 -> 170, Riolu 70 -> 50; global 9: 3 + draw 4, 3rd Fighting, Korrina 3, "
        "Small Balloon 2, Fighting Pulse, Hiking Trail draw -> 3. His move in the review's order (389-413): Grass to Trapinch (@2), the "
        "unused-Supporter warning accepted (not an action), Dragon Pulse 140 (Mega 170 -> 30, top card the 2nd Flygon ex discarded)."),
]

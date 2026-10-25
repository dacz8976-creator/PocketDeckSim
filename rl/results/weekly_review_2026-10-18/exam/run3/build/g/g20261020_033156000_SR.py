from v2_helpers import P, B
D = 'v2deck_d5e2757125'; G = '20261020_033156000_SR'
GT = 'Glimmet B3a 044'; GA = 'Glimmora B3a 045'; DN = 'Deceptive Needle B4 148'; PBR = 'Poison Barb A3 146'; PR = "Professor's Research P-A 007"
CC = 'Copycat B1 225'; WZ = "Team Rocket's Weezing ex B4a 043"; MKX = 'Alolan Muk ex A3 111'; MK = 'Alolan Muk B2 097'; PB = 'Poké Ball P-A 005'
GR70 = 'Alolan Grimer A3 110'; BA = 'Baltoy A3a 030'; KO = "Team Rocket's Koffing B4a 042"
WU = 'Wurmple B4 001'; SI_A = 'Silcoon B4 002'; SI_B = 'Silcoon B1 004'; CA = 'Cascoon B1 006'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_WU = 'Opponent Wurmple printing chosen by HP (60) only (no attack shown); B4 001 and B4 156 match'
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[DN, PBR, PR, CC], disc=[], dene='', board=[B(GT, 60), B(GT, 60)], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(WU, 60)], ko=0),
  ["Play:Professor's Research", 'Play:Deceptive Needle', 'Tool:Deceptive Needle@0', 'Attach:1Darkness@0 zone', 'Attack:Hang Down'],
  D, None,
  approx=AP + "; the opponent's Wurmple printing is chosen by HP (60) only",
  ambiguous=[AMB_WU],
  draws={0: [WZ, MKX]},
  notes="Global 2 = his 1st turn (he went second). '0-36s: Opening/setup': opening five two Glimmet, Deceptive Needle, Poison Barb, "
        "Professor's Research; Glimmet 60 Active, second Glimmet 60 Bench -> 3 in hand. '42-67s: Owner turn1 (global2)': draws Copycat -> "
        "4. Opponent: Wurmple 60 Active, empty Bench; '37-41s': draws and ends -> 5 - 1 + 1 = 5 cards. His move in the review's order: "
        "Professor's Research (Team Rocket's Weezing ex and Alolan Muk ex), Needle to the Active Glimmet, Darkness there, Hang Down 20."),
P(G, 4, 2, [0, 0],
  dict(hand=[PBR, CC, WZ, MKX, PB], disc=[PR], dene='', board=[B(GT, 60, 'D', tool=DN), B(GT, 60)], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(SI_A, 50, 'G', behind=[WU]), B(SI_B, 80), B(CA, 80), B(CA, 80)], ko=0),
  ['Play:Poké Ball', 'Place:Alolan Grimer@2', 'Play:Poison Barb', 'Tool:Poison Barb@2', 'Play:Copycat', 'Place:Baltoy@3',
   'Evolve:Glimmora@0', 'Attach:1Darkness@2 zone', 'Attack:Venomous Hit'],
  D, None,
  approx=AP + "; the opponent's Wurmple printing is chosen by HP (60) only; the Benched Silcoon and Cascoon printings are chosen by HP "
            "(80) only (their attacks were not shown); the opponent's Bench order (Silcoon, Cascoon, Cascoon) follows the review's "
            "wording, the arrangement is not given; Copycat's draw count (5) is the opponent's hand count from the visible plays, and "
            "equals the five cards the review names",
  ambiguous=[AMB_WU,
             'Opponent Active Silcoon printing chosen by HP (80) and attack (Cocoon Collector): B4 002',
             'Opponent Benched Silcoon printing chosen by HP (80) only; B1 004 and B4 002 match',
             'Opponent Benched Cascoon printings chosen by HP (80) only; B1 006 and B4 004 match'],
  draws={0: [GR70], 4: ['-' + WZ, '-' + MKX, GA, BA, KO, MK, PBR]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Poison Barb, Copycat, Weezing ex, Alolan Muk ex; '85-146s: Owner turn2': draws "
        "Poke Ball -> 5. Board: Glimmet 60 Active with Needle and one Darkness, Glimmet 60 Bench. Opponent '68-84s (global3)': draw (6), "
        "Grass to Wurmple, Wurmple 30 -> Silcoon 80 max with 30 damage = 50 (5), Cocoon Collector (an attack, 0 damage) puts Silcoon 80 and "
        "two Cascoon 80 from the deck onto the Bench (hand stays 5). His move in the review's order: Poke Ball (Alolan Grimer 70 = A3 110), "
        "bench Grimer, Poison Barb to Grimer, Copycat (Weezing ex and Muk ex shuffled away; opponent's hand 5 -> 5 cards: Glimmora, "
        "Baltoy, Team Rocket's Koffing, Alolan Muk, Poison Barb as the review names them; they match his later plays: Koffing benched "
        "and Barb attached global 6, Muk played global 12, Weezing ex and Muk ex drawn again globals 6 and 8), bench Baltoy, Active Glimmet "
        "-> Glimmora, Darkness to the benched Grimer, Venomous Hit. Place labels use the lowest empty slot (convention 1): Grimer @2, "
        "Baltoy @3; the review's resulting Bench reads Glimmet/Baltoy/Grimer, so the game showed Baltoy left of Grimer."),
]

from v2_helpers import P, B
D = 'v2deck_06ee642b71'; G = '20261020_000238000_SR'
DK = 'Darkrai ex A2 110'; HO = 'Hoopa ex B4 103'; BA = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'; MS = 'Mega Sableye ex B3b 041'
AM = 'Alolan Muk B2 097'
PR = "Professor's Research P-A 007"; PB = 'Poké Ball P-A 005'; DN = 'Deceptive Needle B4 148'; GZ = "Team Rocket's Goo-zooka B4a 068"
CY = 'Cyrus A2 150'; FB = 'Field Blower B3 147'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
SH = 'Shuckle ex A4 021'; LC = 'Leaf Cape A3 147'; CB = 'Combee A2 017'; FF = 'Fragrant Forest B3 153'; OFB = 'Field Blower B3 147'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
A_SH = 'Opponent Shuckle ex printing chosen by HP (120), Ability title (Solid Shell) and attack title (Triple Slap); A4 021, A4 186, A4 202 and A4b 023 match'
A_LC = "Opponent's Leaf Cape printing not shown; A3 147, A4b 324 and A4b 325 match"
A_CB = 'Opponent Combee: its attack was not shown; printing chosen by HP (50) only (the 50-HP Combee printings have Call for Family, Bug Bite or Reckless Charge)'
ZN = "; the opponent's next Energy read as Grass from the review's setup line ('opponent Grass' Energy Zone)"
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[DN, CL, PR, PB, PR], disc=[], dene='', board=[B(DK, 140)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(SH, 120)], ko=0, zone='G'),
  ["Play:Professor's Research", 'Play:Poké Ball', 'Place:Baltoy@1', 'Play:Poké Ball', 'Place:Hoopa ex@2', 'Play:Deceptive Needle',
   'Tool:Deceptive Needle@0', 'EndTurn'],
  D, None,
  approx=AP + ZN + "; the two cards Professor's Research drew are not named by the review: read as the 2nd Poke Ball (played right "
              "after) and Team Rocket's Goo-zooka (inspected in hand this turn, in neither the opening hand nor the draw)",
  ambiguous=[A_SH],
  draws={0: [PB, GZ], 1: [BA], 3: [HO]},
  notes="Global 1 = his 1st turn (he went first; no Energy). '0-50s, opening/setup': Darkrai ex 140 Active alone; remaining opening "
        "hand Deceptive Needle, Claydol, Professor's Research, Poke Ball. Opponent: Shuckle ex 120 alone; hand 5-1 = 4 (no draw yet); "
        "Energy Zones Darkness (his) and Grass (opponent). 'Global turn 1': draw Professor's Research -> 5 cards. His move in the "
        "review's order: Research (two cards; not named, inferred as the 2nd Poke Ball and Goo-zooka, see approx), Poke Ball (reveals "
        "Baltoy), Baltoy benched (@1), 2nd Poke Ball (Hoopa ex), Hoopa benched (@2), Needle to Active Darkrai (@0), no Energy, no "
        "attack, end (Goo-zooka kept)."),
P(G, 3, 2, [0, 0],
  dict(hand=[CL, PR, GZ, DN], disc=[PR, PB, PB, DN], dene='', board=[B(DK, 60), B(BA, 60), B(HO, 150)], ko=0),
  dict(hand_count=3, disc=[OFB], dene='', board=[B(SH, 140, 'G', tool=LC)], ko=0, zone='G'),
  ['Evolve:Claydol@1', "Play:Professor's Research", 'Attach:1Darkness@2 zone', 'Play:Deceptive Needle', 'Tool:Deceptive Needle@2',
   'EndTurn'],
  D, None,
  approx=AP + ZN,
  ambiguous=[A_SH, A_LC],
  draws={1: [MS, AM]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Claydol, Professor's Research, Goo-zooka; 'Global turn 3': draw the 2nd "
        "Deceptive Needle -> 4 cards. Discard: Research, Poke Ball x2, and the Needle the opponent's Field Blower removed. Board: "
        "Darkrai ex 60 (Triple Slap 60 + Weakness 20), no Energy, no Tool; Bench Baltoy 60, Hoopa ex 150. Opponent, 'Global turn 2': "
        "hand 4, draw 5, Grass to Shuckle, Field Blower (-1) 4, Leaf Cape (-1) 3; Shuckle 120 -10 (Needle, global 1) = 110, +30 Cape = "
        "140. His move in the review's order: Baltoy -> Claydol (@1), 2nd Research (draws Mega Sableye ex, Alolan Muk), Darkness to "
        "benched Hoopa (@2), 2nd Needle to Hoopa (@2), end without attacking."),
P(G, 5, 3, [0, 2],
  dict(hand=[GZ, MS, AM, CY], disc=[PR, PB, PB, DN, PR, DK], dene='', board=[B(HO, 150, 'D', tool=DN), B(CL, 100, behind=[BA])], ko=1),
  dict(hand_count=4, disc=[OFB], dene='', board=[B(SH, 140, 'GG', tool=LC)], ko=0, zone='G'),
  ['Place:Mega Sableye ex@2', 'Attach:1Darkness@0 zone', 'Attack:Shadow Bullet'],
  D, None,
  approx=AP + ZN,
  ambiguous=[A_SH, A_LC],
  notes="Global 5 = his 3rd turn. Hand after global 3: Goo-zooka, Mega Sableye ex, Alolan Muk; 'Global turn 5': draw Cyrus -> 4 cards "
        "(kept). 'Global turn 4': opponent hand 3, draw 4, 2nd Grass to Shuckle, Triple Slap 80 KOs Darkrai ex (no Energy) -> +2; he "
        "promoted Hoopa 150 (one Darkness, Needle); Claydol 100 on the Bench. His move in the review's order: Mega Sableye ex benched "
        "(@2), 2nd Darkness to Hoopa, Shadow Bullet (Solid Shell: 10; no opponent Bench)."),
P(G, 7, 4, [0, 2],
  dict(hand=[GZ, AM, CY, FB], disc=[PR, PB, PB, DN, PR, DK], dene='',
       board=[B(HO, 110, 'DD', tool=DN), B(CL, 100, behind=[BA]), B(MS, 170)], ko=1),
  dict(hand_count=3, disc=[OFB], dene='', board=[B(SH, 120, 'GG', tool=LC), B(CB, 80, 'G', tool=LC)], ko=0, zone='G'),
  ['Play:Field Blower', 'DiscardToolFromPokemon{player:1,in_play_idx:0,tool_idx:0}', 'Attach:1Darkness@0 zone', 'Attack:Dynamite Punch'],
  D, None, stadium={"card": FF, "owner": 1},
  approx=AP + ZN + "; the opponent's hand count assumes Fragrant Forest's use put one card in the hand (the review: a Basic Grass "
                   "card enters the hand)",
  ambiguous=[A_SH, A_LC, A_CB],
  notes="Global 7 = his 4th turn. Hand after global 5: Goo-zooka, Muk, Cyrus; 'Global turn 7': draw Field Blower -> 4 cards. Board: "
        "Hoopa 110 (Triple Slap 20 + Weakness 20 on global 6) with two Darkness and Needle; Bench Claydol 100, Mega Sableye ex 170. "
        "Opponent, 'Global turn 6' (v2 order): hand 4, draw 5, Fragrant Forest played (-1) 4 and used (+1 Basic Grass) 5, Combee benched "
        "(-1) 4, Leaf Cape on Combee (-1) 3 (50 -> 80), Grass to Combee; Shuckle 120 (140 -10 Shadow Bullet after Solid Shell -10 "
        "Needle) with two Grass and Cape. His move in the review's order: Field Blower on Shuckle's Leaf Cape (120 -> 90), 3rd Darkness "
        "to Hoopa, Dynamite Punch (80 after Solid Shell; Needle KO at the end of the turn)."),
]

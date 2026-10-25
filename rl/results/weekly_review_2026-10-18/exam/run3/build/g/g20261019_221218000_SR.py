from v2_helpers import P, B
D = 'v2deck_b1999cc10f'; G = '20261019_221218000_SR'
MS = 'Mega Sableye ex B3b 041'; HO = 'Hoopa ex B4 103'; AG = 'Alolan Grimer A3 110'; BA = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; LIP = 'Lucky Ice Pop B2 145'; DN = 'Deceptive Needle B4 148'
CC = 'Copycat B1 225'; PCL = 'Pokémon Center Lady A2b 070'; FB = 'Field Blower B3 147'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
GF = 'Gouging Fire B3a 054'; DT = 'Dratini B4 116'; DA = 'Dragonair B4 117'; MR = 'Mega Rayquaza ex B4 120'
CAP = 'Ancient Booster Energy Capsule B3a 069'; OPR = "Professor's Research A4b 373"; OPB = 'Poké Ball A2b 111'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_PR = "Opponent's Professor's Research printing not shown; A4b 373 and P-A 007 match"
AMB_PB = "Opponent's Poké Ball printing not shown; A2b 111 and P-A 005 match"
AMB_DT = 'Opponent Dratini printing chosen by HP (60) and attack title (Slam); B4 116 is the only match'
AMB_DA = "Opponent Dragonair printing chosen by HP (80) and Ability title (Dragon's Blessing); B4 117, B4 175 and B4 233 match"
AMB_MR = 'Opponent Mega Rayquaza ex printing chosen by HP (180) and attack title (Mega Burst); B4 120, B4 188 and B4 203 match'
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[CL, PR, PR, LIP, PB], disc=[], dene='', board=[B(MS, 170)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(GF, 110)], ko=0),
  ['Play:Poké Ball', 'Place:Hoopa ex@1', "Play:Professor's Research", 'Play:Deceptive Needle', 'Tool:Deceptive Needle@0',
   'Play:Deceptive Needle', 'Tool:Deceptive Needle@1', 'EndTurn'],
  D, None,
  approx=AP,
  draws={0: [HO], 2: [DN, DN]},
  notes="Global 1 = his 1st turn (he went first; no Energy on this turn). '36-46 Setup' row: opening hand Mega Sableye ex, Claydol, "
        "two Professor's Research, Lucky Ice Pop; Mega Sableye ex Active, no Bench -> hand Claydol, Research x2, Lucky Ice Pop. "
        "Opponent: Gouging Fire 110 Active, no Bench; hand 5-1 = 4 (no draw yet). '47-78 Global 1' row: draw Poke Ball -> 5 cards. His "
        "move in the review's order: Poke Ball ~51s (obtains Hoopa ex), Hoopa ex benched (@1), Professor's Research ~61s (draws two "
        "Deceptive Needles), one Needle to Active Mega Sableye ex (@0), the other to benched Hoopa (@1), no Energy, no attack, end."),
P(G, 3, 2, [0, 0],
  dict(hand=[CL, PR, LIP, AG], disc=[PB, PR], dene='', board=[B(MS, 170, tool=DN), B(HO, 150, tool=DN)], ko=0),
  dict(hand_count=4, disc=[OPR, OPB], dene='', board=[B(GF, 140, 'R', tool=CAP), B(DT, 60)], ko=0),
  ["Play:Professor's Research", 'Place:Alolan Grimer@2', 'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None,
  approx=AP,
  ambiguous=[AMB_DT, AMB_PR, AMB_PB],
  draws={0: [LIP, CC]},
  notes="Global 3 = his 2nd turn. Hand after global 1: Claydol, Professor's Research, Lucky Ice Pop; '110-128 Global 3' row: draw "
        "Alolan Grimer -> 4 cards. Board: Mega Sableye ex 170 + Needle Active, Hoopa ex 150 + Needle on the Bench; discard Poke Ball, "
        "Research. Opponent, '79-109 Global 2' row: hand 4, draw 5, Research (-1 +2) 6, Poke Ball (-1 +1) 6, Dratini benched (-1) 5, "
        "Capsule (-1) 4, Fire attached; Gouging Fire 110 -10 (Needle, global 1) = 100, +40 Capsule = 140. His move in the review's "
        "order: 2nd Professor's Research (draws Lucky Ice Pop and Copycat), Grimer benched (@2), Darkness to Mega Sableye ex ~123-124s, "
        "end without attacking."),
P(G, 5, 3, [0, 0],
  dict(hand=[CL, LIP, LIP, CC, PB], disc=[PB, PR, PR], dene='', board=[B(MS, 170, 'D', tool=DN), B(HO, 150, tool=DN), B(AG, 70)], ko=0),
  dict(hand_count=3, disc=[OPR, OPB], dene='', board=[B(GF, 130, 'R', tool=CAP), B(DA, 80, behind=[DT]), B(MR, 180, 'L')], ko=0),
  ['Play:Poké Ball', 'Place:Baltoy@3', 'Retreat:1', 'Play:Copycat', 'Play:Field Blower', 'DiscardToolFromPokemon{player:1,in_play_idx:0,tool_idx:0}','Attach:1Darkness@0 zone',
   'Attack:Shadow Bullet'],
  D, None,
  approx=AP + "; his Bench order (Hoopa ex, then Grimer) from the order benched and the review's end-of-turn listing",
  ambiguous=[AMB_DA, AMB_MR, AMB_PR, AMB_PB],
  draws={0: [BA], 3: ['-' + CL, '-' + LIP, '-' + LIP, PCL, FB, CL]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Claydol, Lucky Ice Pop x2, Copycat; '151-170' row: draws and plays the 2nd Poke "
        "Ball -> hand Claydol, Ice Pop x2, Copycat, Poke Ball. Board: Mega Sableye ex 170 + Needle + one Darkness Active; Bench Hoopa ex "
        "150 + Needle, Grimer 70. Opponent, '129-150 Global 4' row: hand 4, draw 5, Mega Rayquaza ex benched (-1) 4 with Lightning, "
        "Dratini -> Dragonair 80 (-1) 3 (matches Copycat's three draws); Gouging Fire 140 -10 (Needle, global 3) = 130, one Fire, Capsule. "
        "His move in the review's order: Poke Ball (obtains Baltoy), Baltoy benched (lowest empty slot @3; the end-of-turn listing "
        "'Baltoy, Mega Sableye ex and Alolan Grimer' suggests the left spot), Mega Sableye ex retreats for its one Darkness promoting "
        "Hoopa (Retreat:1), Copycat ~171-189s (hand Claydol, Ice Pop x2 shuffled in; draws Pokemon Center Lady, Field Blower, Claydol), "
        "Field Blower on Gouging Fire's Capsule (130 -> 90), Darkness to Hoopa ~189s, Shadow Bullet ~190-196s with the 20 to Dragonair "
        "(opponent Bench slot 1). The engine offers the Bench target only as ApplyQueuedAttackDamage labels, which convention 5 forbids "
        "writing, so the line ends at the attack; the review's target is Dragonair, not Mega Rayquaza ex."),
]

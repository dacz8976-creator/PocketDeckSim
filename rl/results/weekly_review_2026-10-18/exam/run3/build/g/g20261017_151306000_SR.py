from v2_helpers import P, B
D = 'v2deck_5c3566c961'; G = '20261017_151306000_SR'
PW = 'Pawniard B3a 041'; GM = 'Glimmet B3a 044'; GR = 'Glimmora B3a 045'; AG = 'Alolan Grimer A3 110'; AM = 'Alolan Muk B2 097'
PB = 'Poké Ball P-A 005'; PBR = 'Poison Barb A3 146'; HH = 'Heavy Helmet B1 219'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
KO = "Team Rocket's Koffing B4a 042"; MG = "Team Rocket's Magmar B4a 006"; WZ = "Team Rocket's Weezing ex B4a 043"
OMP = "Team Rocket's Master Plan B4a 070"; ORS = "Team Rocket's Researcher B4a 069"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_MP = "Opponent's Team Rocket's Master Plan printing not shown; B4a 070, B4a 086 and B4a 094 match"
AMB_RS = "Opponent's Team Rocket's Researcher printing not shown; B4a 069 and B4a 085 match"
AMB_WZ = "Opponent Team Rocket's Weezing ex printing chosen by HP (140) and Ability title (Boiler Smog); B4a 043, B4a 083 and B4a 092 match"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[PBR, PB, GR, HH, GM], disc=[], dene='', board=[B(PW, 50)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(KO, 60), B(MG, 70)], ko=0),
  ['Place:Glimmet@1', 'Play:Poké Ball', 'Place:Alolan Grimer@2', 'Play:Heavy Helmet', 'Tool:Heavy Helmet@0', 'Attach:1Darkness@0 zone',
   'Retreat:1', 'Play:Poison Barb', 'Tool:Poison Barb@0', 'EndTurn'],
  D, None,
  approx=AP,
  draws={1: [AG]},
  notes="Global 2 = his 1st turn (he went second). 'Pre-match and setup' row: opening five Pawniard, Poison Barb, Poke Ball, Glimmora, "
        "Heavy Helmet; Pawniard Active, no setup Bench -> hand Poison Barb, Poke Ball, Glimmora, Heavy Helmet. Opponent Active Team "
        "Rocket's Koffing 60. 'Global1' row: opponent 5-1 (Active) = 4, draw 5, benches Team Rocket's Magmar 70 -> 4; no attack, no "
        "Energy (first player). 'Global2' row: natural draw Glimmet -> 5 cards. His move in the review's order: bench Glimmet (@1), "
        "Poke Ball (visibly fetches Alolan Grimer), bench Grimer (@2), Heavy Helmet to Active Pawniard, Darkness to Pawniard, retreat to "
        "Glimmet paying the one Energy (Retreat:1), Poison Barb to Active Glimmet, end without attacking ('One Glimmora remains in "
        "hand')."),
P(G, 4, 2, [0, 0],
  dict(hand=[GR, GM], disc=[PB], dene='D', board=[B(GM, 50, tool=PBR, cond=['Confused']), B(AG, 70), B(PW, 50, tool=HH)], ko=0),
  dict(hand_count=4, disc=[OMP], dene='', board=[B(MG, 70), B(KO, 60, 'D')], ko=0),
  ['Place:Glimmet@3', 'Evolve:Glimmora@0', 'Attach:1Darkness@0 zone', 'Attack:Venomous Hit'],
  D, None,
  approx=AP + "; his Bench order (Grimer, then Pawniard) from the review's listing order; the review gives no left-right placement",
  ambiguous=[AMB_MP],
  notes="Global 4 = his 2nd turn. Hand after global 2: Glimmora only; 'Global4' row natural draw 2nd Glimmet -> Glimmora, Glimmet. Board "
        "after global 2 ('Global2' row): Glimmet Active with Poison Barb, Bench Grimer 70 and Pawniard 50 with Heavy Helmet, no Energy "
        "left (the Darkness paid the retreat -> discard Darkness). Global 3 ('Global3' row): Master Plan confuses Glimmet; Reverse Thrust "
        "10 -> Glimmet 50, Koffing (one Darkness) switches to the Bench, Magmar 70 Active (no Energy yet); Glimmet remains Confused. "
        "Opponent hand: 4 after global 1, draw 5, Master Plan -> 4. His Bench is listed Grimer, Pawniard (the review lists them in that "
        "order after global 2; at the end of global 4 it lists 'Glimmet60, Grimer70, Pawniard50/Helmet'). His move in the review's order: "
        "bench the 2nd Glimmet (lowest empty slot @3; the review's 'Glimmet60, Grimer70, Pawniard' listing suggests the left spot), "
        "evolve Active Glimmet to Glimmora (80 left), Darkness to Glimmora, Venomous Hit (30 into Magmar, Poison)."),
P(G, 6, 3, [0, 1],
  dict(hand=[AM], disc=[PB, GR, GM, PBR], dene='DD', board=[B(GM, 60), B(AG, 70), B(PW, 50, tool=HH)], ko=1),
  dict(hand_count=5, disc=[OMP, ORS], dene='', board=[B(MG, 60, 'D', cond=['Poisoned']), B(WZ, 140, 'D', behind=[KO])], ko=0),
  ['Evolve:Alolan Muk@1', 'Attach:1Darkness@2 zone', 'EndTurn'],
  D, None,
  approx=AP + "; his Bench order (Grimer, then Pawniard) as in global 4; the review gives no left-right placement; the opponent's "
              "hand count assumes Team Rocket's Researcher's two heads added two cards (the review: two Team Rocket Pokemon added to "
              "the hidden hand) and the Lucky Ice Pop, played twice, returned to the hand both times (heads twice)",
  ambiguous=[AMB_MP, AMB_RS, AMB_WZ],
  notes="Global 6 = his 3rd turn. Hand after global 4: empty (Glimmet benched, Glimmora evolved); 'Global6' row natural draw Alolan Muk "
        "-> hand of 1. Global 5 ('Global5' row): Magmar 110 KOs Glimmora (Poison Barb, one Darkness, Glimmet under it -> discard "
        "Glimmora, Glimmet, Poison Barb, D; with the retreat D: DD); Shattering Crystal tails, opponent 1 point; he promoted the fresh "
        "Glimmet 60 (from the left spot). Opponent: hand 4, draw 5, Researcher (-1, two heads +2) 6, Weezing ex evolution (-1) 5, Lucky "
        "Ice Pop played and returned twice (net 0) -> 5; Darkness to Magmar; Magmar 30 -> 70 by the Ice Pops, Poisoned by Poison Barb, "
        "checkup 70 -> 60 entering global 6; Weezing ex 140 keeps Koffing's Darkness. Discard: Master Plan, Researcher (both Ice Pops "
        "back in hand). His move: evolve benched Grimer (@1) to Alolan Muk, Darkness to benched Pawniard (@2; U5: 'Pawniard acquires one "
        "Darkness during owner global6', instant not pinpointed; written after the evolution, the review's order), end without attack "
        "or retreat."),
]

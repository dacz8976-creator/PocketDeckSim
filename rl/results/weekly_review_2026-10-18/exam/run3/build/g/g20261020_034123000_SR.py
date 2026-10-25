from v2_helpers import P, B
D = 'v2deck_0a80817331'; G = '20261020_034123000_SR'
GR70 = 'Alolan Grimer A3 110'; MKX = 'Alolan Muk ex A3 111'; MK = 'Alolan Muk B2 097'; PBR = 'Poison Barb A3 146'
WU = 'Wurmple B4 001'; CA = 'Cascoon B4 004'; DU = 'Dustox B4 005'; PR = "Professor's Research P-A 007"
RI = 'Riolu A2 091'; ML = 'Mega Lucario ex B3 081'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB = ['Opponent Riolu (under Mega Lucario ex) printing chosen by HP (60) only; A2 091, B3 079 and B3 169 have 60 HP',
       'Opponent Mega Lucario ex printing chosen by HP (190) and attack (Fighting Pulse); B3 081, B3 184 and B3 204 match']
POS = [
P(G, 4, 2, [0, 0],
  dict(hand=[CA, CA, DU, MKX, WU], disc=[], dene='', board=[B(GR70, 70, 'D', tool=PBR)], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(ML, 190, 'F', behind=[RI])], ko=0),
  ['Place:Wurmple@1', 'Evolve:Alolan Muk ex@0', 'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; the Riolu under the opponent's Mega Lucario ex is chosen by HP (60) only",
  ambiguous=AMB,
  notes="Global 4 = his 2nd turn (he went second). '26-47s': opening five Poison Barb, two Cascoon, Dustox, Alolan Grimer 70; Grimer "
        "Active, Bench empty -> 4 in hand. 'Global2 (owner1)': draws Alolan Muk ex (5), Poison Barb and one Darkness to Grimer -> 4 in "
        "hand. 'Global4 (owner2)': draws Wurmple -> 5. Opponent: Riolu 60 Active alone; opening 5 - 1 = 4, draws globals 1 and 3 (6), "
        "Riolu -> Mega Lucario ex 190 (5), one Fighting; no Trainer seen. His move in the review's order: Wurmple to the (left) Bench "
        "(slot 1), Grimer -> Alolan Muk ex, second Darkness to Muk ex, no attack."),
P(G, 6, 3, [0, 0],
  dict(hand=[CA, CA, DU, PR], disc=[], dene='', board=[B(MKX, 30, 'DD', tool=PBR, behind=[GR70]), B(WU, 60)], ko=0),
  dict(hand_count=5, disc=[], dene='', board=[B(ML, 180, 'FF', cond=['Poisoned'], behind=[RI])], ko=0),
  ['Attach:1Darkness@0 zone', 'Evolve:Cascoon@1', "Play:Professor's Research", 'Attack:Chemical Panic'],
  D, None,
  stadium={"card": "Arena of Antiquity B3 154", "owner": 1},
  approx=AP + "; the Riolu under the opponent's Mega Lucario ex is chosen by HP (60) only",
  ambiguous=AMB,
  draws={2: [DU, MK]},
  notes="Global 6 = his 3rd turn. Hand after global 4: two Cascoon, Dustox; 'Global6 (owner3)': draws Professor's Research -> 4. "
        "Opponent 'Global5': draw (6), second Fighting, Arena of Antiquity (5), Fighting Pulse 130 (Muk ex 160 -> 30), Poison Barb poisons "
        "Mega Lucario, checkup 190 -> 180. His move in the review's order: third Darkness to Muk ex, Wurmple -> Cascoon, Professor's "
        "Research (second Dustox and Alolan Muk), Chemical Panic (random condition: Paralysis)."),
]

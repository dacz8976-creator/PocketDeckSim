from v2_helpers import P, B
D = 'v2deck_06ee642b71'; G = '20261019_222211000_SR'
KO = "Team Rocket's Koffing B4a 042"; WZ = "Team Rocket's Weezing ex B4a 043"; MS = 'Mega Sableye ex B3b 041'
AG = 'Alolan Grimer A3 110'; AM = 'Alolan Muk B2 097'; BA = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'
PR = "Professor's Research P-A 007"; PB = 'Poké Ball P-A 005'; DN = 'Deceptive Needle B4 148'; SP = 'Starting Plains B2 154'
GZ = "Team Rocket's Goo-zooka B4a 068"; FB = 'Field Blower B3 147'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
OMS = 'Mega Sableye ex B3b 041'; OKO = "Team Rocket's Koffing B4a 042"; OWZ = "Team Rocket's Weezing ex B4a 043"
ORC = 'Red Card P-A 006'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_MS = 'Opponent Mega Sableye ex printing chosen by HP (170) and attack title (Cursed Jewel); B3b 041, B3b 081 and B3b 088 match'
AMB_WZ = "Opponent Team Rocket's Weezing ex printing chosen by HP (140) and Ability title (Boiler Smog); B4a 043, B4a 083 and B4a 092 match"
AMB_PR = "Opponent's Professor's Research printing not shown; A4b 373 and P-A 007 match"
STAD = {"card": SP, "owner": 0}
CJ = [{"effect": {"Counterattack": {"amount": 40}}, "turns": 1}]
POS = [
P(G, 1, 1, [0, 0],
  dict(hand=[PR, WZ, CL, SP, MS], disc=[], dene='', board=[B(KO, 60)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(OMS, 170), B(OKO, 60)], ko=0, zone='D'),
  ['Place:Mega Sableye ex@1', "Play:Professor's Research", 'Play:Deceptive Needle', 'Tool:Deceptive Needle@1', 'Play:Starting Plains',
   'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Energy Zone read as Darkness from the review's 'Darkness Energy Zones seen on both sides'",
  ambiguous=[AMB_MS],
  draws={1: [AM, DN]},
  notes="Global 1 = his 1st turn (he went first; no Energy). '0-56s' setup: he opens Team Rocket's Koffing 60 Active; the other four "
        "opening cards Professor's Research, Weezing ex, Claydol, Starting Plains. Opponent: Mega Sableye ex 170 Active, Koffing 60 "
        "Bench; hand 5-2 = 3 (no draw yet). 'Global turn1': draw Mega Sableye ex -> 5 cards. His move in the review's order: bench Mega "
        "(@1), Professor's Research (draws Alolan Muk, Deceptive Needle), Needle to benched Mega (@1), Starting Plains, end (no Energy, "
        "no attack)."),
P(G, 3, 2, [0, 0],
  dict(hand=[PR, AM, GZ, PB], disc=[PR], dene='', board=[B(KO, 80), B(MS, 190, tool=DN)], ko=0),
  dict(hand_count=2, disc=[ORC], dene='', board=[B(OMS, 190, 'D'), B(OKO, 80), B(OKO, 80)], ko=0, zone='D'),
  ['Play:Poké Ball', 'Place:Alolan Grimer@2', "Play:Professor's Research", 'Place:Baltoy@3', 'Attach:1Darkness@0 zone',
   'Attack:Reverse Thrust', 'Activate:0@1'],
  D, None, stadium=STAD,
  approx=AP + "; the opponent's Energy Zone read as Darkness from the review's 'Darkness Energy Zones seen on both sides'; the "
              "opponent's two Benched Koffing listed in the order benched (setup, then global 2)",
  ambiguous=[AMB_MS],
  draws={0: [AG], 2: [BA, FB]},
  notes="Global 3 = his 2nd turn. After global 1 his hand was Weezing ex, Claydol, Muk; 'Global turn2': Red Card shuffled them in and "
        "he drew Professor's Research, Alolan Muk, Goo-zooka. 'Global turn3': draw Poke Ball -> 4 cards. Discard: the global-1 "
        "Professor's Research. Starting Plains (his) in play: Koffing 80, Mega 190. Opponent, 'Global turn2': hand 3, draw 4, 2nd "
        "Koffing benched (-1) 3, Darkness to Active Mega, Red Card (-1) 2; Mega 190, two Koffing 80. His move in the review's order: "
        "Poke Ball (reveals Alolan Grimer), Grimer benched (@2), Professor's Research (draws Baltoy, Field Blower), Baltoy benched (@3), "
        "Darkness to Active Koffing, Reverse Thrust 10 (Mega 190 -> 180) switching Koffing with the benched Mega (slot 1)."),
P(G, 5, 3, [0, 0],
  dict(hand=[AM, GZ, FB, WZ], disc=[PR, PB, PR], dene='',
       board=[B(MS, 80, tool=DN, cond=['Poisoned', 'Burned']), B(AG, 90), B(BA, 80), B(KO, 80, 'D')], ko=0),
  dict(hand_count=3, disc=[ORC, OPR], dene='', board=[B(OMS, 170, 'DD', effects=CJ), B(OKO, 80), B(OWZ, 140, behind=[OKO])], ko=0,
       zone='D'),
  ["Evolve:Team Rocket's Weezing ex@3", 'Ability@3', 'Attach:1Darkness@0 zone', 'Retreat:1', 'Evolve:Alolan Muk@0',
   "Play:Team Rocket's Goo-zooka", 'EndTurn'],
  D, None, stadium=STAD,
  approx=AP + "; the opponent's Energy Zone read as Darkness from the review's 'Darkness Energy Zones seen on both sides'; his Bench "
              "order (Grimer, Baltoy, then Koffing, moved to the Bench by Reverse Thrust) is the order benched; the review gives no "
              "left-right placement",
  ambiguous=[AMB_MS, AMB_WZ, AMB_PR],
  notes="Global 5 = his 3rd turn. Hand after global 3: Alolan Muk, Goo-zooka, Field Blower; 'Global turn5': draw Weezing ex -> 4 cards. "
        "Discard: Professor's Research x2, Poke Ball. Board after global 3: Mega Sableye ex Active (Reverse Thrust switch) with Needle, "
        "Bench Grimer 90, Baltoy 80, Koffing 80 with one Darkness (no left-right placement in the review, so the order benched per "
        "convention 1: Grimer and Baltoy placed on global 3, then Koffing moved to the Bench by Reverse Thrust; the review lists them "
        "'Koffing80, Grimer90, Baltoy80'). 'Global turn4': Boiler Smog poisons and "
        "burns his Mega; Cursed Jewel 80 (190 -> 110); checkup poison 10 and burn 20 -> 80, burn coin tails, both conditions stay. "
        "Opponent: hand 2, draw 3, 'right Koffing' -> Weezing ex 140 (-1) 2, Professor's Research (-1 +2) 3; 2nd Darkness to Mega; Mega "
        "170 (190 -10 Reverse Thrust -10 Needle at the end of global 3); Cursed Jewel's 40-return effect lasts through his turn "
        "(Counterattack 40). Opponent Bench left to right: Koffing, Weezing ex (the review: the right Koffing evolved). His move in "
        "the review's order: evolve benched Koffing (@3) to Weezing ex, accept Boiler Smog (Ability@3; opposing Mega Poisoned and "
        "Burned), Darkness to Mega, retreat Mega paying it into Grimer (Retreat:1), evolve Active Grimer to Alolan Muk (@0), Goo-zooka, "
        "no attack."),
]

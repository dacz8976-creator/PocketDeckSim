from v2_helpers import P, B
D = 'v2deck_c4ac51db37'; G = '20261023_222318000_SR'
LP = 'Lillipup A3a 054'; ST = 'Stoutland A3a 056'; IN = 'Indeedee ex B1 121'; PR = "Professor's Research P-A 007"
PB = 'Poké Ball P-A 005'; CC = 'Copycat B1 225'; PO = 'Protective Poncho B2 147'; PS = 'Psychic B4 150'
TO = 'Torchic B1 033'; FR = 'Froakie A1 087'; HM = 'Heatmor B1 044'; HT = 'Hiking Trail B2b 069'
OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[PO, PB, CC, CC, PS], disc=[], dene='', board=[B(LP, 60)], ko=0),
  dict(hand_count=3, disc=[OPB, OCC], dene='', board=[B(TO, 60), B(FR, 60), B(TO, 60), B(HM, 80)], ko=0),
  ['Play:Poké Ball', 'Place:Indeedee ex@1', 'Play:Protective Poncho', 'Tool:Protective Poncho@1', 'Play:Copycat', 'Play:Poké Ball',
   'Place:Lillipup@2', 'Attach:1Psychic@0 zone', 'Attack:Tackle'],
  D, None, stadium={"card": HT, "owner": 1},
  approx=AP + "; the opponent's hand (3) counts its global-1 Poke Ball as +1 (the 2nd Torchic was benched from it), its Copycat as "
            "drawing 4 (his hand then held 4) and Hiking Trail's end-of-turn top-up to 3; the opponent's Trainer printings (Poke Ball, "
            "Copycat) are not shown, the first listed are used; the opponent's Bench order (Froakie, Torchic, Heatmor) is the order "
            "they were benched; the opponent's Heatmor is B1 044 (80 HP, Tongue Whip), the card in play, identified from its "
            "attack on global turn 3 (A1 048 also has 80 HP but Combustion)",
  ambiguous=['Opponent Torchic printing chosen by HP (60); B1 033, B3 206 and P-B 007 match',
             'Opponent Froakie printing chosen by HP (60) only (its attack was not shown); A1 087, A3a 091, A4b 110, A4b 111, B1 071, '
             'P-A 061 and P-B 003 match',
             'Opponent Trainer printings in the discard not shown: Poké Ball A2b 111 used (P-A 005 also matches), Copycat B1 225 '
             'used (B1 270 also matches)'],
  draws={0: [IN], 4: ['-' + CC, '-' + PS, PB, LP, PR], 5: [IN]},
  notes="Global 2 = his 1st turn (he went second). Opening five Lillipup, Protective Poncho, Poke Ball, two Copycat; Lillipup Active, no "
        "Bench -> 4; draws Psychic (the Supporter) -> 5. Opponent: Torchic 60 Active, Froakie 60 benched at setup; global 1 Poke Ball, "
        "2nd Torchic benched, Hiking Trail, Copycat, Heatmor benched; hand 5 - 2 = 3, draw 4, Poke Ball 4, Torchic 3, Trail 2, Copycat "
        "(-1, redraw 4 = his hand) 4, Heatmor 3, Trail top-up stays 3. His Copycat redraw is 3 cards: Poke Ball and Lillipup shown at "
        "101-102, Professor's Research inspected at 103 (the Copycat he plays on global 8 comes from Hiking Trail's end-of-turn top-up "
        "on global 2: after this turn he holds Research and the shiny Indeedee, 2 cards). Move (global 2 row, in order): Poke Ball ~80 "
        "(Indeedee ex), bench it 85-88 (@1), Poncho to it 90-94, Copycat 96-100 (2nd Copycat and Psychic shuffled away), Poke Ball "
        "105-108 (2nd Indeedee ex, kept in hand), bench the 2nd Lillipup 111-112 (@2), Psychic Energy to Active Lillipup, Tackle "
        "117-119 (Torchic 60 -> 40)."),
]

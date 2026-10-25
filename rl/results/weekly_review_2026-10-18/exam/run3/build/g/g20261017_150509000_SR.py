from v2_helpers import P, B
D = 'v2deck_9d2c3c7ccf'; G = '20261017_150509000_SR'
HO = 'Hoopa ex B4 103'; BA = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'; GM = 'Glimmet B3a 044'
PB = 'Poké Ball P-A 005'; PBR = 'Poison Barb A3 146'; CY = 'Cyrus A2 150'
# opponent's cards (printing: the first cards.py lists among those matching every shown fact)
ZU = 'Zorua B3 105'; ZX = 'Zoroark ex B3 106'; DE = 'Deino B1 155'; MA = 'Mega Absol ex B1 151'
OCC = 'Copycat B1 225'; OPR = "Professor's Research A4b 373"; OPB = 'Poké Ball A2b 111'; OFB = 'Field Blower B3 147'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_Z = 'Opponent Zorua printing chosen by HP (60) and attack title (Ascension); B3 105 and B3 174 match'
AMB_ZX = 'Opponent Zoroark ex printing chosen by HP (150) and attack title (Brutal Bash); B3 106, B3 186, B3 199 and B4 230 match'
AMB_MA = 'Opponent Mega Absol ex printing chosen by HP (170) and attack title (Darkness Claw); B1 151, B1 262, B1 280, B3 230 and P-B 009 match'
AMB_PR = "Opponent's Professor's Research printing not shown; A4b 373 and P-A 007 match"
AMB_PB = "Opponent's Poké Ball printing not shown; A2b 111 and P-A 005 match"
AMB_CC = "Opponent's Copycat printing not shown; B1 225 and B1 270 match"
POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CL, PBR, PB, CL], disc=[], dene='', board=[B(HO, 150), B(BA, 60)], ko=0),
  dict(hand_count=3, disc=[OCC], dene='', board=[B(ZU, 60)], ko=0, zone='D'),
  ['Play:Poké Ball', 'Play:Poison Barb', 'Tool:Poison Barb@0', 'Attach:1Darkness@0 zone', 'Attack:Shadow Bullet'],
  D, None,
  approx=AP + "; the opponent's Energy Zone read as Darkness from the review's statement that both visible Energy Zones are Darkness",
  ambiguous=[AMB_Z, AMB_CC],
  draws={0: [BA]},
  notes="Global 2 = his 1st turn (he went second). '0-39s: pre-match and setup': opening five Hoopa ex, Claydol, Poison Barb, Baltoy, "
        "Poke Ball; Hoopa ex Active 150, Baltoy on the right Bench (compacted: slot 1); hand Claydol, Poison Barb, Poke Ball. Opponent: "
        "lone Active Zorua 60, empty Bench. 'Global 1': opponent 5-1 (Active) = 4, draw 5, Copycat (-1, shuffle, draw 3 = his 3-card "
        "hand) = 3; no Energy, no bench, no attack. 'Global 2': natural draw 2nd Claydol -> hand of 4. His move in the review's order: "
        "Poke Ball ~66s (visibly returns the 2nd Baltoy ~68-70s, kept in hand all game), Poison Barb to Hoopa ~73-75s, Darkness to "
        "Hoopa ~76-79s, Shadow Bullet ~83-85s (no opponent Bench, no target). Zorua's printing: the review names its attack Ascension "
        "('revealed core is Zorua (Ascension)', used on global 3); the attack is printed on the face-up card, so B3 105 is used here too "
        "(by HP alone the first 60-HP Zorua would be A4a 049)."),
P(G, 4, 2, [0, 0],
  dict(hand=[CL, CL, BA, CY], disc=[PB, PBR], dene='', board=[B(HO, 150, 'D'), B(BA, 60)], ko=0),
  dict(hand_count=2, disc=[OCC, OPR, OPB, OFB], dene='', board=[B(ZX, 120, 'D', behind=[ZU]), B(DE, 60), B(DE, 60)], ko=0, zone='D'),
  ['Evolve:Claydol@1', 'Attach:1Darkness@0 zone', 'Attack:Shadow Bullet'],
  D, None,
  approx=AP + "; the opponent's Energy Zone read as Darkness from the review's statement that both visible Energy Zones are Darkness",
  ambiguous=[AMB_ZX, AMB_Z, AMB_CC, AMB_PR, AMB_PB],
  notes="Global 4 = his 2nd turn. Hand after global 2: Claydol, Claydol, Baltoy ('Owner retains two Claydol and Baltoy in hand'); "
        "'Global 4' natural draw Cyrus -> 4 cards. Discard: Poke Ball, and Poison Barb (Field Blower moved it to his discard, global 3). "
        "Hoopa 150 with one Darkness, no Tool; Baltoy 60 on the Bench. Opponent, 'Global 3': hand 3, draw 4, Professor's Research "
        "(-1 +2) 5, Poke Ball (-1 +1) 5, two Deino benched (-2) 3, Field Blower (-1) 2; Darkness to Zorua; Zorua Ascension -> Zoroark ex "
        "120/150 keeping the 30 damage and the one Darkness. Bench: two Deino 60 (left to right; the left one is the one he later "
        "targets, identical cards). His move in the review's order: Baltoy -> Claydol ~130-132s, Darkness to Hoopa ~134-136s, Shadow "
        "Bullet ~139-144s with the 20 to the left Deino (Bench slot 1 here). The engine offers the Bench target only as two "
        "ApplyQueuedAttackDamage labels (targets (20,true,1) / (20,true,2)), which convention 5 forbids writing, so the line ends at "
        "the attack; the two Deino are identical (60 HP, no Energy), and the review's choice is the left one, slot 1."),
P(G, 6, 3, [0, 0],
  dict(hand=[CL, BA, CY, GM], disc=[PB, PBR], dene='', board=[B(HO, 60, 'DD'), B(CL, 100, behind=[BA])], ko=0),
  dict(hand_count=2, disc=[OCC, OPR, OPB, OFB, OPB], dene='',
       board=[B(ZX, 90, 'D', behind=[ZU]), B(MA, 170, 'D'), B(DE, 40), B(DE, 60)], ko=0, zone='D'),
  ['Place:Glimmet@2', 'Attach:1Darkness@0 zone', 'Attack:Dynamite Punch'],
  D, None,
  approx=AP + "; the opponent's Energy Zone read as Darkness from the review's statement that both visible Energy Zones are Darkness; "
              "opponent's Bench order (Mega Absol ex left, damaged Deino middle, other Deino right) read from the review's note that "
              "the targeted Deino is the middle Bench slot when the Bench is full",
  ambiguous=[AMB_ZX, AMB_Z, AMB_MA, AMB_CC, AMB_PR, AMB_PB],
  notes="Global 6 = his 3rd turn. Hand after global 4: Claydol, Baltoy, Cyrus ('Cyrus and second Baltoy/Claydol stay in hand'); "
        "'Global 6' natural draw Glimmet -> 4 cards. Board: Hoopa 60 (Brutal Bash 90, global 5) with two Darkness; Claydol 100 on the "
        "Bench. Opponent, 'Global 5': hand 2, draw 3, Poke Ball (-1 +1) 3, Mega Absol ex benched (-1) 2; Darkness to Mega Absol; "
        "Zoroark 90 with one Darkness; Deino 40 and 60. Bench order: the review says the targeted Deino is 'middle Bench slot when "
        "later full', so Mega Absol is listed first (left). His move in the review's order: Glimmet benched on the LEFT ~181-184s "
        "(compacted Bench: lowest empty slot @2, after Claydol in slot 1), Darkness to Hoopa ~187-196s, Dynamite Punch ~202-205s "
        "(KO Zoroark ex, Hoopa 60 -> 40). The attack ends the turn; no EndTurn."),
P(G, 8, 4, [2, 2],
  dict(hand=[CL, BA, GM], disc=[PB, PBR, CY, HO], dene='DDD', board=[B(GM, 60), B(CL, 100, behind=[BA])], ko=1),
  dict(hand_count=4, disc=[OCC, OPR, OPB, OFB, OPB, OPR, ZX, ZU], dene='D',
       board=[B(MA, 170, 'DD'), B(DE, 40), B(DE, 60)], ko=1, zone='D'),
  ['Attach:1Darkness@0 zone', 'Retreat:1', 'Place:Glimmet@2', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Energy Zone read as Darkness from the review's statement that both visible Energy Zones are Darkness; "
              "opponent's Bench order (damaged Deino, then the other) as in the earlier turns",
  ambiguous=[AMB_ZX, AMB_Z, AMB_MA, AMB_CC, AMB_PR, AMB_PB],
  notes="Global 8 = his 4th turn. Hand after global 6: Claydol, Baltoy, Cyrus; global 7 Darkness Claw discarded Cyrus from his hand "
        "('remaining hand is Claydol and Baltoy'); 'Global 8' natural draw 2nd Glimmet -> Claydol, Baltoy, Glimmet. Hoopa ex KO'd "
        "(global 7) with three Darkness -> discard Hoopa ex, DDD; he promoted the gold Glimmet 60 (same list printing B3a 044). "
        "Claydol 100 on the Bench. Points 2-2. Opponent, 'Global 7': hand 2, draw 3, Darkness to Mega Absol (two now), Professor's "
        "Research (-1 +2) 4, Darkness Claw. Zoroark ex KO'd on global 6 -> opponent discard Zoroark ex, Zorua, one Darkness. His move "
        "in the review's order: Darkness to Active Glimmet ~254-255s, retreat into Claydol ~256-259s (the one Energy paid), 2nd "
        "Glimmet benched on the LEFT ~260-261s (compacted Bench: after the retreat the gold Glimmet sits in slot 1, so the new one is "
        "@2), Baltoy left in hand, end without attacking."),
]

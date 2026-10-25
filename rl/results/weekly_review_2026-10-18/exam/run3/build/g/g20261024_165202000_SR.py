from v2_helpers import P, B
D = 'v2deck_a75894a903'; G = '20261024_165202000_SR'
OR = 'Oricorio A3 066'; IE = 'Indeedee ex B1 121'; DE = 'Dedenne ex B3b 024'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; GC = 'Giant Cape A2 147'; CY = 'Cyrus A2 150'; CC = 'Copycat B1 225'
SP = 'Starting Plains B2 154'; SB = 'Small Balloon B3b 064'; CV = 'Clear Veil B4 149'
DN = 'Deino B1 155'; HY = 'Hydreigon B1 157'; BO = 'Bombirdier B3 115'; RH = 'Rocky Helmet A2 148'
OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'; ORC = 'Rare Candy A3 144'
STP = {"card": "Starting Plains B2 154", "owner": 0}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
T1CC = ("his Copycat on global 1 is taken to draw 4 (Copycat, Giant Cape, Poké Ball, Indeedee ex): the review lists five reveals "
        "including a Professor's Research, but the opponent then held 4 cards (5 dealt - Deino), the opponent's Copycat on global 2 drew "
        "3 (his hand count) and his own Copycat on global 3 drew 3, which fit only a 4-card draw; the Professor's Research is left out")
AMB_DN = 'Opponent Deino printing chosen by HP (60); only B1 155 matches'
AMB_BO = ('Opponent Bombirdier printing chosen by HP (70) and its Darkness retreat cost 1 less Ability; B3 115 and B3 234 match')
AMB_HY = ('Opponent Hydreigon printing chosen by HP (150), Ability title (Roar in Unison) and attack title (Hyper Ray); B1 157 and '
          'B1 245 match')
AMB_RH = 'Opponent Rocky Helmet printing not shown; A2 148 used (A2 148, A4b 322 and A4b 323 match)'
AMB_T = 'Opponent Trainer printings in the discard are not shown; the first listed printing is used (Poké Ball A2b 111 of A2b 111 / P-A 005; Copycat B1 225 of B1 225 / B1 270)'
AMB_T2 = AMB_T[:-1] + '; Rare Candy A3 144 of A3 144 / A4b 314 / A4b 315 / A4b 379)'


def no_energy_now(p):
    """The first player's first turn: the zone gives no Energy (RULES_FOR_AGENTS). P() sets the deck's one type as energy_now; with it
    pg_legal_v14 lists an attach from the zone as legal on global turn 1. energy_now None makes the engine read the zone as None."""
    p['me']['energy_now'] = None
    return p


POS = [
no_energy_now(P(G, 1, 1, [0, 0],
  dict(hand=[CY, CV, SB, CC], disc=[], dene='', board=[B(OR, 70), B(IE, 130)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(DN, 60)], ko=0),
  ['Play:Small Balloon', 'Tool:Small Balloon@0', 'Play:Clear Veil', 'Tool:Clear Veil@1', 'Play:Copycat', 'Play:Poké Ball',
   'Place:Indeedee ex@2', 'EndTurn'],
  D, None,
  approx=AP + "; he went first, so no Energy this turn; " + T1CC,
  ambiguous=[AMB_DN],
  draws={4: ['-' + CY, CC, GC, PB, IE], 5: [OR]},
  notes="Global 1 = his 1st turn (owner first, 18-21 s). Setup 22-37 s: opening five Indeedee ex, Oricorio, Cyrus, Clear Veil, Small "
        "Balloon; Oricorio Active, Indeedee ex Bench -> hand Cyrus, Clear Veil, Small Balloon. 'Copycat appears as normal draw41' -> 4. "
        "Opponent: Deino Active, no Bench; hand 5 - 1 = 4. His move in the review's order: Small Balloon to Active Oricorio 45-49 s, "
        "Clear Veil to benched Indeedee ex 50-54 s, Copycat 55-58 s (Cyrus shuffled; draws; see approx for the count), Poke Ball 66-70 s "
        "finds the second Oricorio (kept in hand), second Indeedee ex benched 72-75 s (slot 2), end turn 82 s, no Energy, no attack. "
        "Deck count check: with 4 drawn, his Research on global 7 draws only Cyrus and empties the deck, as the review shows (the "
        "5-card reading gives the same deck count, so the opponent's counts decide). energy_now set to None after P() (no Energy on "
        "the first player's first turn; with a letter the engine listed an attach as legal).")),
P(G, 3, 2, [0, 0],
  dict(hand=[CC, GC, OR, CV], disc=[CC, PB], dene='', board=[B(OR, 70, tool=SB), B(IE, 130, tool=CV), B(IE, 130)], ko=0),
  dict(hand_count=3, disc=[OPB, OCC], dene='', board=[B(DN, 60, 'D', tool=RH), B(DN, 60), B(BO, 70)], ko=0),
  ['Play:Clear Veil', 'Tool:Clear Veil@2', 'Place:Oricorio@3', 'Play:Giant Cape', 'Tool:Giant Cape@3', 'Play:Copycat',
   'Attach:1Lightning@3 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + T1CC + "; the opponent's Poké Ball on global 2 counted as +1 card (it found the benched Deino or Bombirdier, "
              "not shown which)",
  ambiguous=[AMB_DN, AMB_BO, AMB_RH, AMB_T],
  draws={5: [PR, SB, GC]},
  notes="Global 3 = his 2nd turn. Hand after global 1 (4-card Copycat reading): Copycat, Giant Cape, Oricorio; 'Draw second Clear "
        "Veil123-124' -> 4. Discard: Copycat, Poke Ball. Board: Oricorio 70 (Small Balloon) Active; Bench Indeedee ex (Clear Veil), "
        "Indeedee ex. Opponent global 2 (83-121 s): hand 4, draw 5, Poke Ball (-1 +1) 5, bench second Deino 4 and Bombirdier 3 (Ability "
        "announced), Darkness and Rocky Helmet to Active Deino 2, Copycat draws three (his hand count) -> 3. His move in the review's "
        "order: Clear Veil to the second Indeedee ex (slot 2) 126-131 s, bench second Oricorio 132-135 s (slot 3), Giant Cape to it "
        "137-142 s, Copycat 143-147 s (hand empty then; draws Professor's Research, Small Balloon, Giant Cape), Lightning to that "
        "benched Oricorio 155-157 s, end turn 158 s."),
P(G, 5, 3, [0, 1],
  dict(hand=[PR, SB, GC, DE], disc=[CC, PB, CC, OR, SB], dene='', board=[B(OR, 90, 'L', tool=GC), B(IE, 130, tool=CV), B(IE, 130, tool=CV)],
       ko=1),
  dict(hand_count=2, disc=[OPB, OCC, ORC], dene='DDD', board=[B(HY, 120, tool=RH, behind=[DN]), B(DN, 60, 'D'), B(BO, 70)], ko=0),
  ['Place:Dedenne ex@3', 'Play:Giant Cape', 'Tool:Giant Cape@3', "Play:Professor's Research", 'Play:Starting Plains',
   'Attach:1Lightning@3 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + T1CC,
  ambiguous=[AMB_HY, AMB_DN, AMB_BO, AMB_RH, AMB_T2],
  draws={3: [SP, PR]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Professor's Research, Small Balloon, Giant Cape; 'Normal draw Dedenne ex200-201' "
        "-> 4. Discard adds Copycat, the first Oricorio (KO global 4) and its Small Balloon (no Energy on it). Board: second Oricorio 90 "
        "(Giant Cape, one Lightning) promoted Active 193-196 s; Bench Indeedee ex x2 (Clear Veil each). Opponent global 4 (159-198 s): "
        "hand 3, draw 4, Rare Candy 3, Active Deino -> Hydreigon 2 (Rocky Helmet kept), Roar in Unison (two Darkness, 150 -> 120), "
        "manual Darkness to benched Deino, Hyper Ray 130 KOs Oricorio and discards Hydreigon's three Energy (+1). His move in the "
        "review's order: bench Dedenne ex 202-204 s (slot 3), Giant Cape to it 206-211 s, Research 212-218 s draws Starting Plains and "
        "Research, Starting Plains 219-223 s, Lightning to benched Dedenne 224 s, end turn, no attack."),
P(G, 7, 4, [0, 1],
  dict(hand=[SB, PR, PB], disc=[CC, PB, CC, OR, SB, PR], dene='',
       board=[B(OR, 110, 'L', tool=GC), B(IE, 150, tool=CV), B(IE, 150, tool=CV), B(DE, 160, 'L', tool=GC)], ko=1),
  dict(hand_count=2, disc=[OPB, OCC, ORC], dene='DDDD',
       board=[B(BO, 90, tool=RH), B(DN, 80, 'DD'), B(HY, 90, 'D', tool=RH, behind=[DN])], ko=0),
  ['Play:Poké Ball', "Play:Professor's Research", 'Retreat:3', 'Attach:1Lightning@0 zone', 'Attack:Dede-Circuit'],
  D, None, stadium=STP,
  approx=AP + "; " + T1CC,
  ambiguous=[AMB_BO, AMB_DN, AMB_HY, AMB_RH, AMB_T2],
  draws={0: [DE], 1: [CY]},
  notes="Global 7 = his 4th turn. Hand after global 5: Small Balloon, Professor's Research; 'Draw Poké Ball271-272' -> 3. Discard adds "
        "Research. Starting Plains (his) in play: Oricorio 70+20+20 = 110, Indeedee ex 150 each, Dedenne ex 120+20+20 = 160. Opponent "
        "global 6 (226-269 s): hand 2, draw 3, Roar in Unison (two Darkness, Hydreigon 120 -> 90), retreat Hydreigon (one Darkness "
        "discarded) for Bombirdier, manual Darkness to benched Deino (two), second Rocky Helmet on Active Bombirdier 2. Opponent Bench "
        "Deino 80 (slot 1), Hydreigon 90 with one Darkness and Rocky Helmet (slot 2, from the retreat). His move in the review's order: "
        "Poke Ball 273-277 s finds the second Dedenne ex (Bench full, kept), Research 279-282 s draws Cyrus only (deck 1 -> 0), retreat "
        "Oricorio 283-287 s discarding its Lightning, Dedenne ex (slot 3) Active, Lightning to it 289-291 s, Dede-Circuit 292-297 s "
        "(180, KOs Bombirdier; Rocky Helmet 20 back)."),
P(G, 9, 5, [1, 1],
  dict(hand=[SB, DE, CY], disc=[CC, PB, CC, OR, SB, PR, PB, PR], dene='L',
       board=[B(DE, 10, 'LL', tool=GC), B(IE, 150, tool=CV), B(IE, 150, tool=CV), B(OR, 110, tool=GC)], ko=1),
  dict(hand_count=3, disc=[OPB, OCC, ORC, BO, RH], dene='DDDDDDD', board=[B(HY, 60, tool=RH, behind=[DN]), B(DN, 80, 'DDD')], ko=1),
  ['Ability@1', 'Ability@2', 'Retreat:3', 'Attach:1Lightning@3 zone', 'EndTurn'],
  D, None, stadium=STP,
  approx=AP + "; " + T1CC,
  ambiguous=[AMB_HY, AMB_DN, AMB_RH, AMB_T2],
  notes="Global 9 = his 5th turn. Deck empty ('No cards left in deck announcement338-340'), no draw: hand Small Balloon, Dedenne ex, "
        "Cyrus. Discard adds Poke Ball, Research; Energy discard: Oricorio's Lightning (retreat global 7). Board: Dedenne ex 160 - 20 "
        "(Rocky Helmet) - 130 (Hyper Ray) = 10, two Lightning, Giant Cape, Active; Bench Indeedee ex x2, Oricorio 110 (Giant Cape, no "
        "Energy) in slot 3 from the global 7 retreat. Opponent: Bombirdier KO global 7 (+1 him; its Rocky Helmet discarded); Hydreigon "
        "promoted; global 8 (312-337 s): hand 2, draw 3, Roar in Unison (90 -> 60), manual Darkness to Deino (three), Hyper Ray 130 to "
        "Dedenne, all Hydreigon Energy discarded (three). His move in the review's order: both Indeedee ex Watch Over 340-350 s (10 -> 30 "
        "-> 50), retreat Dedenne 355-357 s discarding one Lightning, Oricorio (slot 3) Active, Lightning to benched Dedenne (now slot 3) "
        "363-364 s, end turn, no attack."),
]

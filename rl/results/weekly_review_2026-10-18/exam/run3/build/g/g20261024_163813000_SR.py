from v2_helpers import P, B
D = 'v2deck_2c68a379f5'; G = '20261024_163813000_SR'
GO = 'Goomy B1 177'; AX = 'Axew B2b 054'; HX = 'Haxorus B2b 056'; HA = 'Happiny B4a 063'; RM = 'Roaring Moon B3a 047'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'; IR = 'Iris B2b 067'
CC = 'Copycat B1 225'
MG = 'Magby A4 032'; CM = 'Charmander B2b 007'; MCX = 'Mega Charizard X ex B2b 009'
OPR = "Professor's Research A4b 373"; ORC = 'Rare Candy A3 144'; OPB = 'Poké Ball A2b 111'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_MG = 'Opponent Magby printing chosen by HP (30) and attack title (Toasty Toss); A4 032, A4 166 and B2 206 match'
AMB_CM = 'Opponent Charmander printing chosen by HP (70) and attack title (Flame Tail); B2b 007 and B2b 091 match'
AMB_MCX = ('Opponent Mega Charizard X ex printing chosen by HP (220) and attack title (Raging Blaze); B2b 009, B2b 076 and B2b 111 '
           'match')
AMB_PR = "Opponent Professor's Research printing not shown; A4b 373 used (A4b 373 and P-A 007 match)"
AMB_RC = 'Opponent Rare Candy printing not shown; A3 144 used (A3 144, A4b 314, A4b 315 and A4b 379 match)'
AMB_PB = 'Opponent Poké Ball printing not shown; A2b 111 used (A2b 111 and P-A 005 match)'


def no_energy_now(p):
    """The first player's first turn: the zone gives no Energy (RULES_FOR_AGENTS). P() needs a letter for ez_now; with one set,
    pg_legal_v14 lists an attach from the zone as legal on global turn 1. energy_now None makes the engine read the zone as None."""
    p['me']['energy_now'] = None
    return p


POS = [
no_energy_now(P(G, 1, 1, [0, 0],
  dict(hand=[CY, PR, IR, CC, AX], disc=[], dene='', board=[B(RM, 100)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(MG, 30)], ko=0),
  ['Place:Axew@1', "Play:Professor's Research", 'Place:Goomy@2', 'EndTurn'],
  D, None,
  approx=AP + "; he went first, so no Energy this turn; his next Energy (Fighting) is read from the Energy he attached on his next "
              "turn (global 3), the review does not show the zone preview",
  ambiguous=[AMB_MG],
  draws={1: [HX, GO]},
  ez_now='F', ez_next='F',
  notes="Global 1 = his 1st turn (owner goes first, 21 and 24 s). Setup: opening five Cyrus, Professor's Research, Iris, Roaring "
        "Moon, Copycat; Roaring Moon Active, no Bench -> hand Cyrus, Research, Iris, Copycat. 'Draw Axew (36)' -> 5. Opponent: Magby 30 "
        "Active, no Bench; hand 5 - 1 = 4. His move in the review's order: bench Axew 37-38 s (the review: on the right; engine's lowest "
        "empty slot @1), Professor's Research 41-42 s draws Haxorus and Goomy, bench Goomy 47-49 s (review: middle; engine @2), end "
        "turn, no Energy, no attack. Hand ends Cyrus, Iris, Copycat, Haxorus (review). ez_now given only because P() needs a letter; "
        "energy_now set to None after P() (with a letter the engine listed an attach as legal on global turn 1).")),
P(G, 3, 2, [0, 0],
  dict(hand=[CY, IR, CC, HX, PR], disc=[PR], dene='', board=[B(RM, 100), B(GO, 40), B(AX, 70)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(MG, 30), B(CM, 70, 'RR')], ko=0),
  ["Play:Professor's Research", 'Attach:1Fighting@2 zone', 'Place:Axew@3', 'EndTurn'],
  D, None,
  approx=AP + "; his next Energy (Fighting) is read from the Energy he attached on global 5, the review does not show the zone "
              "preview",
  ambiguous=[AMB_MG, AMB_CM],
  draws={0: [GO, AX]},
  ez_now='F', ez_next='F',
  notes="Global 3 = his 2nd turn. Hand after global 1: Cyrus, Iris, Copycat, Haxorus; draw Professor's Research (inspected 64 s) -> 5. "
        "Discard: Professor's Research. Board: Roaring Moon 100 Active; Bench left to right as the review shows it: Goomy (middle), "
        "Axew (right). Opponent global 2 (50-62 s): hand 4, draw 5, bench Charmander 70 4, Fire to Charmander, Magby's Toasty Toss "
        "moves a Fire from the zone to benched Charmander (two Fire), no damage. His move in the review's order: Research 67-68 s draws "
        "Goomy and Axew, Fighting to the right Axew 73-75 s (slot 2 in the compacted Bench), second Axew to the left slot 78-79 s "
        "(engine's lowest empty slot @3), second Goomy kept (Bench full), end turn, no attack."),
P(G, 5, 3, [0, 1],
  dict(hand=[CY, IR, CC, HX, GO, RC], disc=[PR, PR, RM], dene='', board=[B(GO, 40), B(AX, 70), B(AX, 70, 'F')], ko=1),
  dict(hand_count=4, disc=[OPR, ORC], dene='', board=[B(MCX, 220, 'RRR', behind=[CM]), B(MG, 30)], ko=0),
  ['Play:Rare Candy', 'Evolve:Haxorus@2', 'Place:Goomy@3', 'Play:Copycat', 'Attach:1Fighting@2 zone', 'EndTurn'],
  D, None,
  approx=AP + "; his next Energy (Metal) is read from the Energy he attached on global 7, the review does not show the zone preview",
  ambiguous=[AMB_MCX, AMB_CM, AMB_MG, AMB_PR, AMB_RC],
  draws={3: ['-' + CY, '-' + IR, RC, CY, IR, CC]},
  ez_now='F', ez_next='M',
  notes="Global 5 = his 3rd turn. Hand after global 3: Cyrus, Iris, Copycat, Haxorus, Goomy; 'Draw Rare Candy at 120-121' -> 6. "
        "Discard: two Research, Roaring Moon (KO global 4). Board: Goomy 40 promoted Active (114-116 s) from the middle slot; Bench "
        "left to right: left Axew (no Energy), right Axew (one Fighting). Opponent global 4 (80-119 s): hand 4, draw 5, Research 6, "
        "retreat Magby to Charmander, Rare Candy 5, Charmander -> Mega Charizard X ex 4, third Fire, Raging Blaze 100 KOs Roaring Moon "
        "(+1); Magby 30 on the Bench. 4 matches the review's 'visible four-card hand' at Copycat. His move in the review's order: Rare "
        "Candy 123-126 s right Axew (slot 2) -> Haxorus, second Goomy to the vacated middle slot 129-131 s (engine's lowest empty slot "
        "@3), Copycat 133-137 s (his hand then Cyrus, Iris shuffled; draws Rare Candy, Cyrus, Iris, Copycat), second Fighting to "
        "benched Haxorus 144-146 s, end turn, no attack."),
P(G, 7, 4, [0, 2],
  dict(hand=[RC, CY, IR, CC, HX], disc=[PR, PR, RM, RC, CC, GO], dene='', board=[B(HX, 150, 'FF', behind=[AX]), B(AX, 70), B(GO, 40)], ko=2),
  dict(hand_count=5, disc=[OPR, ORC, OPB], dene='', board=[B(MCX, 220, 'RRRR', behind=[CM]), B(MG, 30)], ko=0),
  ['Play:Rare Candy', 'Evolve:Haxorus@1', 'Play:Copycat', 'Play:Poké Ball', 'Play:Poké Ball', 'Place:Happiny@3',
   'Attach:1Metal@0 zone', 'Attack:Frenzied Blade'],
  D, None,
  approx=AP + "; the opponent's Poké Ball on global 6 counted as +1 card (its result is hidden); his next Energy is not shown (the "
              "game ended on the opponent's turn), Fighting is assumed",
  ambiguous=[AMB_MCX, AMB_CM, AMB_MG, AMB_PR, AMB_RC, AMB_PB],
  draws={2: ['-' + CY, '-' + IR, CY, PB, HA, PB, IR], 3: [], 4: []},
  ez_now='M', ez_next='F',
  notes="Global 7 = his 4th turn. Hand after global 5: Rare Candy, Cyrus, Iris, Copycat (Copycat's draws); 'Draw second Haxorus at "
        "175-176' -> 5. Discard adds Rare Candy, Copycat, Goomy (KO global 6). Board: right Haxorus 150 with two Fighting promoted "
        "Active (171-173 s); Bench left to right: left Axew 70, middle Goomy 40. Opponent global 6 (148-173 s): hand 4, draw 5, fourth "
        "Fire to Mega Charizard X ex, Poke Ball (-1 +1 hidden, no new Basic benched) 5, Raging Blaze KOs Goomy (+1, total 2); 5 matches "
        "the review's 'five-card hand' at Copycat. His move in the review's order: Rare Candy 177-181 s left Axew (slot 1) -> second "
        "Haxorus, Copycat 195-200 s (hand Cyrus, Iris shuffled; draws Cyrus, Poke Ball, Happiny, Poke Ball, Iris), Poke Ball 207-210 s "
        "and 211-214 s (both find nothing: no Basic left in the deck), bench Happiny 215-217 s (slot 3), Metal to Active Haxorus 220-221 "
        "s, Frenzied Blade 223-225 s (130 to Mega Charizard X ex 220 -> 90)."),
]

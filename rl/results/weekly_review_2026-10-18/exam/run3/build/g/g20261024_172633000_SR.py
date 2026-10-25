from v2_helpers import P, B
D = 'v2deck_bac3c8a158'; G = '20261024_172633000_SR'
DK = 'Darkrai ex A2 110'; BO = 'Bombirdier B3 115'; AB = 'Absol B4 100'; HO = 'Hoopa ex B4 103'; HA = 'Happiny B4a 063'
XS = 'X Speed P-A 002'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; RH = 'Rocky Helmet A2 148'; CY = 'Cyrus A2 150'
PBA = 'Poison Barb A3 146'; CC = 'Copycat B1 225'; SP = 'Starting Plains B2 154'; DN = 'Deceptive Needle B4 148'
ON = 'Onix B1a 038'; OBR = 'Brock A1 224'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_ON = 'Opponent Onix printing chosen by HP (100) and attack title (Dig); B1a 038 and B3 211 match'
AMB_BR = ('Opponent Brock printing not shown; A1 224 used (A1 224 and A1 271 match by name); the review shows its one play on global 1 '
          'putting two Fighting Energy on Onix, while the database text of both printings attaches one')
AMB_PR = "Opponent Professor's Research printing not shown; A4b 373 used (A4b 373 and P-A 007 match)"
DIG = [{"effect": "PreventAllDamageAndEffects", "turns": 1}]


def cheer(p):
    p['turn_effects'] = [{"turn": p['turn_count'], "effect": {"IncreasedDamage": {"amount": 20}}}]
    return p


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CY, CC, PR, PB], disc=[], dene='', board=[B(HA, 30), B(AB, 70)], ko=0),
  dict(hand_count=4, disc=[OBR], dene='', board=[B(ON, 100, 'FF')], ko=0),
  ['Play:Poké Ball', 'Place:Darkrai ex@2', "Play:Professor's Research", 'Place:Bombirdier@3', 'Attach:1Darkness@2 zone',
   'Attack:Chubby Cheer'],
  D, None,
  approx=AP + "; the opponent's Brock is shown attaching two Fighting to Onix (the database's Brock attaches one); Onix holds the two "
              "Fighting the review shows",
  ambiguous=[AMB_ON, AMB_BR],
  draws={0: [DK], 2: [BO, SP]},
  notes="Global 2 = his 1st turn (owner goes second). Setup 0-47 s: opening five Happiny, Absol, Cyrus, Copycat, Professor's "
        "Research; Happiny Active, Absol Bench -> hand Cyrus, Copycat, Research. 'Draws Poké Ball' -> 4. Opponent: Onix Active, empty "
        "Bench; hand 5 - 1 = 4; global 1 draw 5, Brock (53 s) 4, two Fighting on Onix, no attack. His move in the review's order: Poke "
        "Ball 62-64 s finds Darkrai ex, bench it (slot 2), Research 74 s draws Bombirdier and Starting Plains, bench Bombirdier 80 s "
        "(slot 3), Darkness to Darkrai ex 85-88 s (Nightmare Aura 20, Onix 100 -> 80), Happiny Chubby Cheer 90-94 s (10, Onix 80 -> "
        "70)."),
cheer(P(G, 4, 2, [0, 1],
  dict(hand=[CY, CC, SP, HO], disc=[PB, PR, HA], dene='', board=[B(AB, 70), B(DK, 140, 'D'), B(BO, 70)], ko=1),
  dict(hand_count=6, disc=[OBR, OPR], dene='', board=[B(ON, 70, 'FFM', effects=DIG)], ko=0),
  ['Place:Hoopa ex@3', 'Play:Starting Plains', 'Play:Copycat', 'Play:Deceptive Needle', 'Tool:Deceptive Needle@0',
   'Attach:1Darkness@1 zone', 'Play:Deceptive Needle', 'Tool:Deceptive Needle@3', 'EndTurn'],
  D, None,
  approx=AP + "; Chubby Cheer's +20 from global 2 is set as a turn effect (IncreasedDamage 20); Dig's heads on global 3 is set as "
              "PreventAllDamageAndEffects on Onix for this turn; the opponent's hand (6) is from the visible plays, but his later "
              "counts (his Copycat on global 6 drew 3, and his deck reached 0 after Research on global 8) imply the opponent held 3 "
              "or 4 cards on global 6, 1-2 fewer than the visible plays give, so the opponent made at least one play the review does "
              "not name, possibly before this turn; Copycat's draw here is taken as 6 (the opponent's count): the review names only the "
              "two Deceptive Needle and the second Copycat (played on global 6) among them, so 3 stand-ins from his list (Absol, Poké "
              "Ball, Professor's Research) fill the variant only",
  ambiguous=[AMB_ON, AMB_BR, AMB_PR],
  draws={2: ['-' + CY, DN, DN, CC, AB, PB, PR]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Cyrus, Copycat, Starting Plains; 'Draws and benches first Hoopa ex (130-134s)' "
        "-> 4 at the start. Discard: Poke Ball, Research, Happiny (KO global 3). Board: Absol 70 promoted Active (126 s); Bench Darkrai ex "
        "140 (Darkness), Bombirdier 70. Opponent global 3 (96-128 s): hand 4, draw 5, Metal to Onix (two Fighting, one Metal), Research "
        "(-1 +2) 6, Dig 30 KOs Happiny (+1), heads (116 s) grants the protection. Onix 100 - 20 - 10 = 70. His move in the review's "
        "order: bench Hoopa ex 130-134 s (slot 3), Starting Plains 136-144 s, Copycat 150 s (hand Cyrus shuffled; draws the opponent's "
        "hand count), Deceptive Needle to Absol 151-156 s, Darkness to Darkrai ex 159-163 s (Nightmare Aura 20), second Needle to Hoopa "
        "ex 164-167 s, end turn (Needle 10). The 3 Copycat stand-ins are not shown in the position; the real 3 are among Absol, Hoopa "
        "ex, X Speed, Poke Ball, Research, Cyrus, Poison Barb (all shuffled back by his global 6 Copycat).")),
]

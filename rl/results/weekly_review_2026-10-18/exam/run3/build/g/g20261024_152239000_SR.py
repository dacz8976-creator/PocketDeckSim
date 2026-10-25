from v2_helpers import P, B
D = 'v2deck_2c68a379f5'; G = '20261024_152239000_SR'
GO = 'Goomy B1 177'; AX = 'Axew B2b 054'; HX = 'Haxorus B2b 056'; HA = 'Happiny B4a 063'; RM = 'Roaring Moon B3a 047'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; RC = 'Rare Candy A3 144'; IR = 'Iris B2b 067'
PI = 'Pawmi B3a 014'; PO = 'Pawmo B3a 015'; EE = 'Eevee A4 134'; JO = 'Jolteon A1 102'; OR = 'Oricorio A3 066'
SB = 'Small Balloon B3b 064'; PBA = 'Poison Barb A3 146'; GC = 'Giant Cape A2 147'
OCC = 'Copycat B1 225'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_SB = ("Opponent Pawmi's Tool: its title is not displayed; it shows a retreat cost 1 less effect; Small Balloon B3b 064 used "
          "(B3b 064 and B3b 106 match)")
AMB_EE = "Opponent Eevee printing chosen by HP (60) and attack title (Find a Friend); A4 134 and A4 231 match"
AMB_OR = ("Opponent Oricorio printing chosen by HP (70) and Ability title (Safeguard); A3 066, A3 165, A4b 146, A4b 147 and B1 303 "
          "match")
AMB_JO = "Opponent Jolteon printing chosen by HP (90) and attack title (Pin Missile); only A1 102 matches"
AMB_GC = "Opponent Giant Cape printing not shown; A2 147 used (A2 147, A4b 320 and A4b 321 match)"
AMB_CC = "Opponent Copycat printing not shown; B1 225 used (B1 225 and B1 270 match)"
AMB_PR = "Opponent Professor's Research printing not shown; A4b 373 used (A4b 373 and P-A 007 match)"
CHEER = [{"turn": None, "effect": {"IncreasedDamage": {"amount": 20}}}]


def cheer(p):
    p['turn_effects'] = [dict(CHEER[0], turn=p['turn_count'])]
    return p


def no_energy_now(p):
    """The first player's first turn: the zone gives no Energy (RULES_FOR_AGENTS). P() needs a letter for ez_now; with one set,
    pg_legal_v14 lists 'Attach:1Metal@0 zone' as legal on global turn 1 (scratch/b9/t_te.py). energy_now None makes the engine read the
    zone as None and list no attach."""
    p['me']['energy_now'] = None
    return p


POS = [
no_energy_now(P(G, 1, 1, [0, 0],
  dict(hand=[PB, RC, CY, GO], disc=[], dene='', board=[B(HA, 30), B(GO, 40)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(PI, 50)], ko=0),
  ['Play:Poké Ball', 'Place:Axew@2', 'Place:Goomy@3', 'Attack:Chubby Cheer'],
  D, None,
  approx=AP + "; he went first, so no Energy this turn; his next Energy (Metal) is read from the Energy he attached on his next turn "
              "(global 3), the review does not show the zone preview",
  draws={0: [AX]},
  ez_now='M', ez_next='M',
  notes="Global 1 = his 1st turn (he went first). Setup 42-66s: opening five Happiny, Goomy, Poke Ball, Rare Candy, Cyrus; Happiny 30 "
        "Active, Goomy 40 Bench -> hand Poke Ball, Rare Candy, Cyrus. 'Draw Goomy around69s' -> 4 cards. Opponent: Pawmi 50 Active, no "
        "Bench; hand 5 - 1 = 4 (no draw yet). His move in the review's order: Poke Ball 72-75s finds Axew; Axew benched 77-79s (slot 2), "
        "second Goomy 80-84s (slot 3); Chubby Cheer 86-90s for 10 (no Energy on the first player's first turn). Zone: no Energy now; "
        "ez_now given as the next one (Metal, attached on global 3) only because P() needs a value; energy_now set to None after P() "
        "(with a letter the engine listed an attach as legal on global turn 1).")),
cheer(P(G, 3, 2, [0, 0],
  dict(hand=[RC, CY, PR], disc=[PB], dene='', board=[B(HA, 30), B(GO, 40), B(AX, 70), B(GO, 40)], ko=0),
  dict(hand_count=3, disc=[], dene='', board=[B(EE, 60, 'L', tool=PBA), B(PI, 40, tool=SB)], ko=0),
  ["Play:Professor's Research", 'Attach:1Metal@2 zone', 'Attack:Chubby Cheer'],
  D, None,
  approx=AP + "; Eevee's Find a Friend on global 2 counted as +1 card (its result is hidden); the opponent's Tool and Pokemon "
              "printings are chosen from the shown names, HP and titles; his next Energy (Metal) is read from the Energy he attached on "
              "global 5, the review does not show the zone preview; Chubby Cheer's +20 from global 1 is set as a turn effect "
              "(IncreasedDamage 20)",
  ambiguous=[AMB_EE, AMB_SB],
  draws={0: [IR, HX]},
  ez_now='M', ez_next='M',
  notes="Global 3 = his 2nd turn. Hand after global 1: Rare Candy, Cyrus; 'Draw Professor's Research161s' -> 3 cards. Discard: Poke "
        "Ball. Board: Happiny 30 Active, Bench Goomy 40 (setup), Axew 70, Goomy 40 in the order benched; no damage on his side (no "
        "opponent attack damage on global 2). Opponent global 2 (91-159s): hand 4, draw 5, bench Eevee 4, balloon Tool on Pawmi 3, "
        "retreat Pawmi (no Energy to discard) to Eevee, Poison Barb on Eevee 2, Lightning to Eevee, Eevee's Find a Friend (attack, "
        "random Pokemon from deck, hidden) 3. Pawmi 50-10 = 40 on the Bench. His move: Professor's Research 166-168s draws Iris and "
        "Haxorus, Metal to benched Axew (slot 2) 172-174s, Chubby Cheer 176-180s does 30 with the +20 (Eevee 60->30). Zone next: Metal "
        "(global 5 'second Metal').")),
cheer(P(G, 5, 3, [0, 1],
  dict(hand=[RC, CY, IR, HX, AX], disc=[PB, PR, HA], dene='', board=[B(GO, 40), B(AX, 70, 'M'), B(GO, 40)], ko=1),
  dict(hand_count=4, disc=[OCC], dene='', board=[B(JO, 60, 'LL', tool=PBA, behind=[EE]), B(PI, 40, tool=SB), B(OR, 90, tool=GC)], ko=0),
  ['Place:Axew@3', 'Play:Rare Candy', 'Evolve:Haxorus@1', 'Attach:1Metal@1 zone', 'Play:Cyrus', 'EndTurn'],
  D, None,
  approx=AP + "; Copycat on global 4 drew 4 (his hand count then); which Goomy was promoted after the Happiny KO is not stated: the "
              "setup Goomy is taken as promoted, so the Bench is Axew then the second Goomy; the opponent's printings are chosen from "
              "the shown names, HP and titles; his next Energy (Fighting) is read from the Energy he attached on global 7; Chubby "
              "Cheer's +20 from global 3 is set as a turn effect (IncreasedDamage 20)",
  ambiguous=[AMB_JO, AMB_EE, AMB_SB, AMB_OR, AMB_GC, AMB_CC],
  ez_now='M', ez_next='F',
  notes="Global 5 = his 3rd turn. Hand after global 3: Rare Candy, Cyrus, Iris, Haxorus; 'Draw second Axew283s' -> 5. Discard: Poke "
        "Ball, Professor's Research, Happiny (KO global 4). Board: Goomy 40 promoted Active (277-280s), Bench Axew 70 with Metal, other "
        "Goomy 40. Opponent global 4 (186-281s): hand 3, draw 4, bench Oricorio 3, Eevee -> Jolteon 60/90 (30 damage carried) 2, second "
        "Lightning to Jolteon, Giant Cape on Oricorio 70->90 1, Copycat -> draws his hand count 4; Pin Missile KOs Happiny (+1 Chico). "
        "Bench order Pawmi (retreated to Eevee's slot on global 2), Oricorio. His move in the review's order: bench second Axew 285-287s "
        "(lowest empty slot 3), Rare Candy 288-292s older Axew -> Haxorus (slot 1), second Metal 293-295s to that Haxorus, Cyrus 307-314s "
        "brings the damaged Pawmi 40 Active (the only damaged Benched Pokemon; the engine's single 'Activate:1@1' is applied by the "
        "tool), end turn, no attack. Turn effect: Happiny's Chubby Cheer on global 3 gives +20 during this turn (Happiny KO'd since; "
        "the effect is on his attacks).")),
P(G, 7, 4, [0, 2],
  dict(hand=[IR, PB], disc=[PB, PR, HA, RC, CY, GO], dene='', board=[B(HX, 150, 'MM', behind=[AX]), B(GO, 40), B(AX, 70)], ko=2),
  dict(hand_count=5, disc=[OCC, OPR], dene='',
       board=[B(JO, 60, 'LLL', tool=PBA, behind=[EE]), B(PO, 70, tool=SB, behind=[PI]), B(OR, 90, tool=GC)], ko=0),
  ['Attach:1Fighting@0 zone', 'Play:Poké Ball', 'Place:Roaring Moon@3', 'Ability@3', 'Play:Iris', 'Attack:Frenzied Blade'],
  D, None,
  approx=AP + "; the opponent's printings are chosen from the shown names, HP and titles; his next Energy is not shown (on global 9 "
              "he attacked without attaching), Fighting is assumed",
  ambiguous=[AMB_JO, AMB_EE, AMB_SB, AMB_OR, AMB_GC, AMB_CC, AMB_PR],
  draws={1: [RM]},
  ez_now='F', ez_next='F',
  notes="Global 7 = his 4th turn. Hand after global 5: Iris; 'Draw Poke Ball414s' -> Iris, Poke Ball. Discard adds Rare Candy, Cyrus, "
        "Goomy (KO global 6). Board: Haxorus 150 with Metal, Metal (Rare Candy from Axew) promoted Active 410-413s; Bench the second Goomy "
        "40 and the second Axew 70 (benched global 5). Opponent global 6 (316-413s): hand 4, draw 5, third Lightning to benched Jolteon, "
        "Professor's Research (-1 +2) 6, retreat Pawmi with its balloon, Jolteon 60 Active again, Pawmi -> Pawmo 70/80 5, Pin Missile "
        "KOs Goomy (+1, total 2). His move in the review's order: Fighting to Haxorus 416-418s, Poke Ball 419-422s finds Roaring Moon, "
        "bench it 425-428s (slot 3), accept Ancient Roar 431-434s (opponent chooses Oricorio), Iris 451-454s, Frenzied Blade 456-459s "
        "(150, KOs Oricorio, +2 with Iris). 'Ability@3' is the engine's yes to Ancient Roar after the Place. The after-chance variant "
        "stops at the opponent's choice of the new Active (two options, opponent's frame), so Iris and Frenzied Blade are not reached "
        "by check_game; scratch/b9/t_g2t7.py (Oricorio Active, Jolteon benched, Roaring Moon placed) applies both labels."),
]

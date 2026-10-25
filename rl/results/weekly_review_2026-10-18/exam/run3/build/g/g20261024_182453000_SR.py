from v2_helpers import P, B
D = 'v2deck_7907f1e146'; G = '20261024_182453000_SR'
MK = 'Magikarp P-B 014'; FE = 'Feebas B3b 014'; MGY = 'Mega Gyarados ex B1 052'; MIL = 'Milotic ex B3b 015'; MSH = 'Mega Sharpedo ex B4 035'
CAS = 'Carvanha B4 034'; CAJ = 'Carvanha P-B 081'; CAPE = 'Elegant Cape B3b 065'; WAL = 'Wallace B3b 068'; CC = 'Copycat B1 225'
CAB = 'Cabbie B3 150'; PB = 'Poké Ball P-A 005'; SS = 'Soothing Shore B4 154'; IRI = 'Irida A2a 072'; LIS = 'Lisia B1 226'
FUR = 'Furfrou B3b 061'; ORI = 'Oricorio A3 066'; EEV = 'Eevee A4 134'; SYL = 'Sylveon B3b 030'; SHX = 'Shinx A2 058'; LUX = 'Luxray A2 060'
PON = 'Protective Poncho B2 147'; GC = 'Giant Cape A2 147'
OPB = 'Poké Ball A2b 111'; OPR = "Professor's Research A4b 373"; OCC = 'Copycat B1 225'; RC = 'Rare Candy A3 144'
SSH = {"card": SS, "owner": 0}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_O = ('Opponent Oricorio printing chosen by HP (70), Ability title (Safeguard) and attack title (Zzzap); A3 066, A3 165, A4b 146, '
         'A4b 147 and B1 303 match')
AMB_E = 'Opponent Eevee printing chosen by HP (60) and attack title (Find a Friend); A4 134 and A4 231 match'
AMB_S = 'Opponent Sylveon printing chosen by HP (100), Ability title (Soothing Ribbon) and attack title (Magical Shot); B3b 030 and B3b 073 match'
AMB_SH = 'Opponent Shinx printing chosen by HP (60) only; its attack was not shown'
AMB_T = ("Opponent's Trainer printings not shown (Poké Ball, Professor's Research, Protective Poncho); A2b 111, A4b 373 and B2 147 used "
         "(P-A 005, P-A 007 and B2 234 also match)")
AMB_T2 = "Opponent's Copycat and Giant Cape printings not shown; B1 225 and A2 147 used (B1 270, A4b 320 and A4b 321 also match)"
HC = ("the opponent's hand count rests on his Copycat on global 4, which drew five; the visible plays of global 1 alone give one card "
      "fewer")
FUR_N = ("Furfrou's printing (B3b 061, the only 70-HP Fur Coat Furfrou with Double Headbutt) is the face-up Active card; the review "
         "names its attack when it is used on global 3")


def _wallace_sharpedo(v):
    v['me']['board'][1].update({'card': MSH, 'hp': 220, 'behind': [CAJ]})


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[CAB, CC, PB, MGY, MSH], disc=[], dene='', board=[B(MK, 30)], ko=0),
  dict(hand_count=4, disc=[OPB, OPR], dene='', board=[B(FUR, 70), B(EEV, 60, tool=PON), B(ORI, 70)], ko=0),
  ['Play:Poké Ball', 'Place:Feebas@1', 'Play:Cabbie', 'Play:Soothing Shore', 'Attach:1Water@0 zone', 'Attack:Expert Splasher'],
  D, None,
  approx=AP + "; " + HC + " (global 3 adds only its draw), so 4 is used here; the opponent's Trainer printings are not shown (the "
            "first listed printings are used); " + FUR_N + "; Eevee's 60 HP is its printing's (the review names only Find a Friend)",
  ambiguous=[AMB_O, AMB_E, AMB_T],
  draws={0: [FE], 2: [SS]},
  notes="Global 2 = his 1st turn (he went second). 'Opening and setup': opening five Magikarp, Cabbie, Copycat, Poké Ball, Mega Gyarados "
        "ex (native 24); Magikarp Active, no Bench. Opponent: Furfrou 70 Active. 'Global 1': Poké Ball, bench Eevee then Oricorio "
        "(Safeguard shown), Professor's Research, Protective Poncho onto Eevee; no Energy, no attack. Visible plays give 3 in hand; "
        "Copycat on global 4 drew five and global 3 adds only a draw, so 4 here. 'Global 2': draw Mega Sharpedo ex -> Cabbie, Copycat, "
        "Poké Ball, MGy, MSh. His move in order: Poké Ball 69-74 (Feebas), bench Feebas 75-76 (@1), Cabbie 97-101 (Soothing Shore), "
        "Soothing Shore 102-106, zone Water to Magikarp 107, Expert Splasher 108-114 (two tails, 0 damage). pg_legal_v14 stops at the "
        "Poké Ball; Cabbie is a hidden-draw stop that v2_helpers does not count as a chance step, so check_game's variant stops again "
        "there; scratch/b10/vcheck.py (Cabbie added) checks the rest."),
P(G, 4, 2, [0, 1],
  dict(hand=[CC, MGY, MSH, MSH], disc=[PB, CAB, MK], dene='W', board=[B(FE, 30)], ko=1),
  dict(hand_count=5, disc=[OPB, OPR], dene='', board=[B(FUR, 70, 'L'), B(EEV, 60, tool=PON), B(ORI, 70)], ko=0),
  ['Play:Copycat', 'Place:Carvanha@1', 'Play:Elegant Cape', 'Tool:Elegant Cape@1', 'Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium=SSH,
  approx=AP + "; the opponent's hand (5) is the number of cards his Copycat drew this turn; the opponent's Trainer printings are not "
            "shown (the first listed printings are used); Eevee's 60 HP is its printing's (the review names only Find a Friend)",
  ambiguous=[AMB_O, AMB_E, AMB_T],
  draws={0: ['-' + MGY, '-' + MSH, '-' + MSH, CAPE, IRI, CC, CAS, MSH]},
  notes="Global 4 = his 2nd turn. Hand after global 2: Copycat, MGy, MSh; 'Global 4' draw the 2nd Mega Sharpedo ex -> Copycat, MGy, MSh, "
        "MSh. 'Global 3': Lightning to Furfrou, Double Headbutt (one head) 30 KOs Magikarp (with its 1 Water), opponent +1; Feebas "
        "promoted. Discard: Poké Ball, Cabbie, Magikarp; Soothing Shore in play. His move in order: Copycat 165-174 (shuffles MGy, MSh, "
        "MSh; draws Elegant Cape, Irida, Copycat, Sharp Fang Carvanha, Mega Sharpedo ex), bench Carvanha 176-177 (@1), Cape on it 181-183, "
        "zone Water to the benched Carvanha 184-186, end (Feebas does not attack)."),
P(G, 6, 3, [0, 2],
  dict(hand=[IRI, CC, MSH, MGY], disc=[PB, CAB, MK, CC, FE], dene='W', board=[B(CAS, 50, 'W', tool=CAPE)], ko=2),
  dict(hand_count=6, disc=[OPB, OPR], dene='', board=[B(FUR, 70, 'L'), B(EEV, 60, tool=PON), B(ORI, 70, 'L')], ko=0),
  ['Evolve:Mega Sharpedo ex@0', 'Play:Copycat', 'Place:Carvanha@1', 'Attach:1Water@0 zone', 'Play:Elegant Cape', 'Tool:Elegant Cape@1',
   'Attack:Turbo Shark'],
  D, None, stadium=SSH,
  approx=AP + "; the opponent's hand (6) is global 4's (5) plus the global-5 draw, and matches his Copycat's six draws; the Benched "
            "Oricorio's 1 Lightning is a reconstruction: the review says the global-5 Energy stayed unattached, but Oricorio holds 2 "
            "Lightning after one attachment on global 7 (its Zzzap costs Lightning + Colorless; on global 13 it pays 1 and keeps 1), so "
            "the global-5 Lightning is taken as attached to it; the opponent's Trainer printings are not shown (the first listed are used)",
  ambiguous=[AMB_O, AMB_E, AMB_T,
             "Opponent Benched Oricorio's 1 Lightning is a reconstruction; the review's turn account does not show when it was attached"],
  draws={1: ['-' + IRI, '-' + MGY, WAL, WAL, MGY, SS, CAPE, CAJ]},
  notes="Global 6 = his 3rd turn. Hand after global 4: Irida, Copycat, MSh; 'Global 6' draw Mega Gyarados ex. 'Global 5': Double Headbutt "
        "(one head) 30 KOs Feebas (no Energy), opponent +1 = 2; Cape Carvanha (1 Water) promoted. Discard adds Copycat, Feebas. His move "
        "in order: evolve Active Carvanha to Mega Sharpedo ex 235-240 (220 with Cape, 1 Water), Copycat 241-247 (shuffles Irida, MGy; "
        "draws two Wallace, MGy, Soothing Shore, Elegant Cape, Aqua Jet Carvanha = six), bench Aqua Jet Carvanha 255-256 (@1), zone Water "
        "to the Active 258-259, Cape on the benched Carvanha 260-262, Turbo Shark 266-269 (50 after Fur Coat; its Water to the benched "
        "Carvanha, the only Benched Water Pokemon, so no target label)."),
P(G, 8, 4, [0, 2],
  dict(hand=[WAL, WAL, MGY, SS, LIS], disc=[PB, CAB, MK, CC, FE, CC], dene='W',
       board=[B(MSH, 150, 'WW', tool=CAPE, behind=[CAS]), B(CAJ, 50, 'W', tool=CAPE)], ko=2),
  dict(hand_count=3, disc=[OPB, OPR, OCC], dene='L',
       board=[B(ORI, 90, 'LL', tool=GC), B(SYL, 100, tool=PON, behind=[EEV]), B(FUR, 50), B(SHX, 60)], ko=0),
  ['Play:Wallace', 'ChooseRandomEvolutionTarget', 'Attach:1Water@1 zone', 'Retreat:1', 'EndTurn'],
  D, None, stadium=SSH,
  approx=AP + "; the opponent's hand (3) follows global 6's (6): +1 draw, -Sylveon, -Giant Cape, Copycat drawing his four, -Shinx; "
            "the opponent's Trainer and Tool printings are not shown (the first listed are used); Bench order is the order each "
            "Pokémon went to the Bench (Furfrou by its retreat)",
  ambiguous=[AMB_O, AMB_E, AMB_S, AMB_SH, AMB_T, AMB_T2],
  draws={0: []}, vpatch=_wallace_sharpedo,
  notes="Global 8 = his 4th turn. Hand after global 6: Wallace, Wallace, MGy, Soothing Shore; 'Global 8' draw Lisia (321). Board: Mega "
        "Sharpedo 220 -> 150 (Zzzap 50 + 20, global 7), 2 Water, Cape; Bench Aqua Jet Carvanha 50 with Cape and 1 Water (Turbo Shark). "
        "'Global 7': Eevee -> Sylveon (Poncho kept), Soothing Ribbon heals Furfrou 20 -> 50, Furfrou retreats to Oricorio discarding its "
        "Lightning, Lightning to Oricorio ('its second'), +20 HP cape (Giant Cape) -> 90, Copycat (draws his four), bench Shinx, Zzzap. "
        "His move in order: Wallace 328-334 on the benched Carvanha (2nd Mega Sharpedo ex, 220 with Cape, 1 Water; the variant sets it), "
        "zone Water to it ~338, free retreat of the damaged Active 339-344 (the new Mega comes in), End turn 345 (no attack). pg_legal_v14 "
        "stops at 'hidden random choice (ChooseRandomEvolutionTarget)' and leaves that step unmatched; scratch/b10/vcheck.py runs "
        "check_game's own variant."),
P(G, 10, 5, [0, 2],
  dict(hand=[WAL, MGY, SS, LIS, MIL], disc=[PB, CAB, MK, CC, FE, CC, WAL], dene='W',
       board=[B(MSH, 150, 'WW', tool=CAPE, behind=[CAJ]), B(MSH, 170, 'WW', tool=CAPE, behind=[CAS])], ko=2),
  dict(hand_count=4, disc=[OPB, OPR, OCC], dene='L',
       board=[B(ORI, 90, 'LL', tool=GC), B(SYL, 100, tool=PON, behind=[EEV]), B(FUR, 70), B(SHX, 60, 'L')], ko=0),
  ['Play:Lisia', 'Attach:1Water@0 zone', 'Retreat:1', 'EndTurn'],
  D, None, stadium=SSH,
  approx=AP + "; the opponent's hand (4) is global 8's (3) plus the global-9 draw; the opponent's Trainer and Tool printings are not "
            "shown (the first listed are used); Bench order is the order each Pokémon went to the Bench",
  ambiguous=[AMB_O, AMB_E, AMB_S, AMB_SH, AMB_T, AMB_T2],
  draws={0: []},
  notes="Global 10 = his 5th turn. Hand after global 8: Wallace, MGy, Soothing Shore, Lisia; 'Global 10' draw Milotic ex. Board: the new "
        "Mega Sharpedo (over Aqua Jet Carvanha) Active, 220 -> 150 (Zzzap, global 9), 2 Water, Cape; the original Mega on the Bench, 150 "
        "-> 170 (Shore at the end of global 8), 2 Water, Cape. Discard adds Wallace. His deck holds only Irida (drawn on global 12); no "
        "Basic is left in it. Opponent 'Global 9': Soothing Ribbon heals Furfrou 50 -> 70, Lightning to Shinx, Zzzap. His move in order: "
        "Lisia 376-380 ('no cards in the deck that can be the target'), zone Water to the Active (3 Water) 382, free retreat into the "
        "original Mega 385-389, End turn 390."),
P(G, 12, 6, [0, 2],
  dict(hand=[WAL, MGY, SS, MIL, IRI], disc=[PB, CAB, MK, CC, FE, CC, WAL, LIS], dene='W',
       board=[B(MSH, 120, 'WW', tool=CAPE, behind=[CAS]), B(MSH, 170, 'WWW', tool=CAPE, behind=[CAJ])], ko=2),
  dict(hand_count=5, disc=[OPB, OPR, OCC], dene='L',
       board=[B(ORI, 90, 'LL', tool=GC), B(SYL, 100, tool=PON, behind=[EEV]), B(FUR, 70), B(SHX, 60, 'LL')], ko=0),
  ['Play:Irida', 'Attach:1Water@0 zone', 'Retreat:1', 'EndTurn'],
  D, None, stadium=SSH,
  approx=AP + "; the opponent's hand (5) is global 10's (4) plus the global-11 draw; the opponent's Trainer and Tool printings are "
            "not shown (the first listed are used); Bench order is the order each Pokémon went to the Bench",
  ambiguous=[AMB_O, AMB_E, AMB_S, AMB_SH, AMB_T, AMB_T2],
  notes="Global 12 = his 6th turn. Hand after global 10: Wallace, MGy, Soothing Shore, Milotic ex; 'Global 12' draw Irida 414-416 (the "
        "last card of his deck). Board: the original Mega Active, 170 -> 190 (Shore) -> 120 (Zzzap, global 11), 2 Water, Cape; the new "
        "Mega on the Bench, 150 -> 170 (Shore), 3 Water, Cape. Discard adds Lisia. Opponent 'Global 11': Lightning to Shinx (2), Zzzap. "
        "His move in order: Irida 431-434 (both +40), zone Water to the Active ~436 (3 Water), free retreat to the new Mega 438-442, End "
        "turn 444."),
P(G, 14, 7, [0, 2],
  dict(hand=[WAL, MGY, SS, MIL], disc=[PB, CAB, MK, CC, FE, CC, WAL, LIS, IRI], dene='W',
       board=[B(MSH, 80, 'WWW', tool=CAPE, behind=[CAJ]), B(MSH, 180, 'WWW', tool=CAPE, behind=[CAS])], ko=2),
  dict(hand_count=4, disc=[OPB, OPR, OCC, RC], dene='LLLLL',
       board=[B(LUX, 130, behind=[SHX]), B(SYL, 100, tool=PON, behind=[EEV]), B(FUR, 70), B(ORI, 90, 'L', tool=GC)], ko=0),
  ['Attack:Turbo Shark'],
  D, None, stadium=SSH,
  approx=AP + "; the opponent's hand (4) is global 12's (5), +1 draw, -Rare Candy, -Luxray on global 13; the opponent's Trainer and "
            "Tool printings are not shown (the first listed are used); Bench order is the order each Pokémon went to the Bench "
            "(Oricorio by its retreat)",
  ambiguous=[AMB_O, AMB_E, AMB_S, AMB_SH, AMB_T, AMB_T2,
             "Opponent's Rare Candy printing not shown; A3 144 used (A4b 314, A4b 315 and A4b 379 also match)"],
  notes="Global 14 = his 7th turn; his deck is empty, no draw (476-477). Hand: Wallace, MGy, Soothing Shore, Milotic ex. Board: the new "
        "Mega Active, 210 -> 220 (Shore) -> 80 (Volt Bolt 120 + 20, global 13), 3 Water, Cape; the original Mega on the Bench, 160 -> 180 "
        "(Shore), 3 Water, Cape. Discard adds Irida. Opponent 'Global 13': Lightning to Shinx (3), Rare Candy Shinx -> Luxray 130 (Volt "
        "Bolt -> A2 060), Oricorio retreats paying 1 Lightning (keeps 1), Volt Bolt discards all 3 Lightning. Opponent's discarded "
        "Energy: Furfrou's (global 7), Oricorio's retreat (global 13), Luxray's 3. His move: Turbo Shark 481-483 (70 to Luxray; the zone "
        "Water is left unattached and goes to the benched Mega by the attack, 484.5-485; one Benched Water Pokemon, so no target label)."),
]

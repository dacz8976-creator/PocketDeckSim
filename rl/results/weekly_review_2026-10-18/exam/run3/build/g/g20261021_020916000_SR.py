from v2_helpers import P, B
D = 'v2deck_5309993874'; G = '20261021_020916000_SR'
AG = 'Alolan Grimer A3 110'; BT = 'Baltoy A3a 030'; CL = 'Claydol A3a 031'; AM = 'Alolan Muk B2 097'; MS = 'Mega Sableye ex B3b 041'
HO = 'Hoopa ex B4 103'; KO = "Team Rocket's Koffing B4a 042"; WZ = "Team Rocket's Weezing ex B4a 043"
XS = 'X Speed P-A 002'; PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CY = 'Cyrus A2 150'; PBB = 'Poison Barb A3 146'
CC = 'Copycat B1 225'; FB = 'Field Blower B3 147'; DN = 'Deceptive Needle B4 148'; GZ = "Team Rocket's Goo-zooka B4a 068"
CB = 'Carbink B3b 031'; MD = 'Mega Diancie ex B3b 032'; FM = 'Flutter Mane B3b 035'; FMX = 'Flutter Mane ex B3a 026'
OGC = 'Giant Cape A2 147'; OPR = "Professor's Research A4b 373"; OCC = 'Copycat B1 225'; OPB = 'Poké Ball A2b 111'
SP = {"card": "Starting Plains B2 154", "owner": 1}
AP = "opponent's list unknown; opponent's hand size from the visible plays"
OTR = ("the opponent's Trainer printings (Professor's Research, Giant Cape, Copycat, Poké Ball) are not shown; the printing cards.py "
       "lists first is used")
AMB_MD = 'Opponent Mega Diancie ex printings chosen by HP (170) and attack title (Brilliant Storm); B3b 032, B3b 080 and B3b 087 match'
AMB_FMX = 'Opponent Flutter Mane ex printing chosen by HP (130) and attack title (Spellbinding Start); B3a 026, B3a 083 and B3a 091 match'


def no_energy_now(p):
    """The first player's first turn: the zone gives no Energy. P() sets energy_now from the deck's type; with it set, pg_legal_v14
    lists 'Attach:1Darkness@0 zone' as legal on global turn 1 (see scratch/b3/t_t1energy.py). None makes the zone read
    ["None", "Some(Darkness)"]."""
    p['me']['energy_now'] = None
    return p


POS = [
no_energy_now(P(G, 1, 1, [0, 0],
  dict(hand=[FB, XS, DN, PB, DN], disc=[], dene='', board=[B(AG, 70)], ko=0),
  dict(hand_count=2, disc=[], dene='', board=[B(CB, 50), B(MD, 170), B(FM, 80)], ko=0, zone='P'),
  ['Play:Deceptive Needle', 'Tool:Deceptive Needle@0', 'Play:Poké Ball', 'Place:Baltoy@1', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's Carbink, Mega Diancie ex and Flutter Mane printings are chosen by name and HP (no attack used yet); "
            "no Energy on the first player's first turn (energy_now None); the opponent's next Energy (Psychic) is the zone the "
            "review shows at setup",
  ambiguous=['Opponent Carbink printing chosen by HP (50) and attack title (Glittering Gift); B3b 031 is the only match',
             'Opponent Mega Diancie ex printing chosen by name and HP (170); B3b 032, B3b 080 and B3b 087 match'],
  draws={2: [BT]},
  notes="Global 1 = his 1st turn (he went first). 'Actual deck QR and setup': opening five Alolan Grimer, Field Blower, X Speed, "
        "Deceptive Needle, Poke Ball; Grimer Active (70), empty Bench -> 4 in hand. 'Global turn 1': draw Deceptive Needle -> 5. "
        "Opponent setup: Carbink 50 Active, Mega Diancie ex 170 and Flutter Mane 80 on the Bench (in that order; 'left Mega Diancie "
        "ex' on global 2) -> opening 5 - 3 = 2 in hand, no draw yet. His move, in the review's order: Needle on Grimer, Poke Ball "
        "(Baltoy), Baltoy benched (@1), end; no first-turn Energy. Carbink's printing: the review identifies the 50-HP Glittering "
        "Gift Carbink (B3b 031), which attacks from global 2 on; the card in play shows its attack, so the printing is used from "
        "global 1 (the other 50-HP printing, B1 119, has Guard Press). energy_now set to None after P().")),
P(G, 3, 2, [0, 0],
  dict(hand=[FB, XS, DN, WZ], disc=[PB], dene='', board=[B(AG, 70, tool=DN), B(BT, 60)], ko=0),
  dict(hand_count=2, disc=[OPR], dene='', board=[B(CB, 40, 'P'), B(MD, 190, 'P', tool=OGC), B(FM, 80), B(MD, 170, 'P')], ko=0),
  ['Play:Field Blower', 'DiscardToolFromPokemon{player:1,in_play_idx:1,tool_idx:0}', 'Attach:1Darkness@0 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + OTR + "; the Flutter Mane printing is chosen by name and HP (80) (its attack not yet used)",
  ambiguous=['Opponent Carbink printing chosen by HP (50) and attack title (Glittering Gift)', AMB_MD],
  notes="Global 3 = his 2nd turn. Hand after global 1: Field Blower, X Speed, Deceptive Needle (Needle, Poke Ball played; Baltoy "
        "benched). 'Global turn 3': draw Team Rocket's Weezing ex -> 4. Board: Grimer 70 with Needle, no Energy; Baltoy 60. "
        "Opponent 'Global turn 2': Psychic to Carbink; Giant Cape on the left Mega Diancie ex (170 -> 190); Professor's Research; "
        "second Mega Diancie ex benched; Glittering Gift: one Psychic to each Diancie. Carbink 50 -> 40 by the Needle at the end of "
        "global 1. Opp hand: 2 + draw 3, Cape 2, Research 3, Diancie 2. Bench: setup Diancie (left, caped), Flutter Mane, second "
        "Diancie (benched global 2). His move, in the review's order: Field Blower on the Giant Cape (Diancie at in_play_idx 1), "
        "Darkness to Grimer, no attack (Sludge Toss needs two), end."),
P(G, 5, 3, [0, 0],
  dict(hand=[XS, DN, WZ, PB], disc=[PB, FB], dene='', board=[B(AG, 90, 'D', tool=DN), B(BT, 80)], ko=0),
  dict(hand_count=3, disc=[OPR, OGC, OCC, OPB], dene='', board=[B(CB, 50, 'P'), B(MD, 190, 'PP'), B(FM, 100, 'P'), B(MD, 190, 'PP')],
       ko=0),
  ['Play:Poké Ball', 'Place:Mega Sableye ex@2', 'Attach:1Darkness@2 zone', 'Play:Deceptive Needle', 'Tool:Deceptive Needle@2',
   'EndTurn'],
  D, None, stadium=SP,
  approx=AP + "; " + OTR + "; the opponent's Poké Ball on global turn 4 is counted +1 card (its result is hidden)",
  ambiguous=['Opponent Carbink printing chosen by HP (50) and attack title (Glittering Gift)', AMB_MD,
             'Opponent Flutter Mane printing chosen by name and HP (80); B3b 035 is the only 80-HP Flutter Mane'],
  draws={0: [MS]},
  notes="Global 5 = his 3rd turn. Hand after global 3: X Speed, Deceptive Needle, Team Rocket's Weezing ex (Field Blower played). "
        "'Global turn 5': draw Poke Ball -> 4. Board: Grimer with one Darkness and Needle, 90 under Starting Plains; Baltoy 80. "
        "Opponent 'Global turn 4': Starting Plains (every Basic +20: Diancie 190, Flutter Mane 100, Carbink 50 of 70); Copycat (drew "
        "3, his hand was X Speed, Needle, Weezing); Poke Ball (hidden, +1); Psychic to Flutter Mane; Glittering Gift -> each "
        "Diancie 2 Psychic. Opp hand: 2 + draw 3, Plains 2, Copycat 3, Poke Ball 3. His move, in the review's order: Poke Ball "
        "(Mega Sableye ex), Sableye benched (@2) at 190, Darkness to Sableye, 2nd Needle on Sableye, end (Grimer's Needle: Carbink "
        "50 -> 40)."),
P(G, 7, 4, [0, 1],
  dict(hand=[XS, WZ, GZ], disc=[PB, FB, PB, AG, DN], dene='D', board=[B(MS, 190, 'D', tool=DN), B(BT, 80)], ko=1),
  dict(hand_count=5, disc=[OPR, OGC, OCC, OPB, OPR], dene='P', board=[B(FM, 100, 'PP'), B(MD, 190, 'PP'), B(CB, 40), B(MD, 190, 'PP')],
       ko=0),
  ['Attach:1Darkness@0 zone', "Play:Team Rocket's Goo-zooka", 'Attack:Cursed Jewel'],
  D, None, stadium=SP,
  approx=AP + "; " + OTR + "; the opponent's Bench order follows the slots (Carbink retreated into Flutter Mane's slot)",
  ambiguous=['Opponent Carbink printing chosen by HP (50) and attack title (Glittering Gift)', AMB_MD,
             'Opponent Flutter Mane printing chosen by HP (80) and attack title (Hexing Flight); B3b 035 is the only match'],
  notes="Global 7 = his 4th turn. Hand after global 5: X Speed, Team Rocket's Weezing ex (Poke Ball, Needle played). 'Global turn 7': "
        "draw Team Rocket's Goo-zooka -> 3. 'Global turn 6': Hexing Flight 90 KOs Grimer 90 (Grimer, Needle, Darkness to discard; "
        "score 0-1, ko 1); he promotes Sableye (190, one Darkness, Needle); Baltoy 80 stays benched. Opponent global 6: 2nd Psychic "
        "to Flutter Mane; Carbink retreats (its Psychic discarded) for Flutter Mane; Professor's Research. Opp hand: 3 + draw 4, "
        "Research 5. His move, in the review's order: 2nd Darkness to Sableye, Goo-zooka, Cursed Jewel (80 to Flutter Mane 100)."),
P(G, 9, 5, [0, 1],
  dict(hand=[XS, WZ, CY], disc=[PB, FB, PB, AG, DN, GZ], dene='D', board=[B(MS, 190, 'DD', tool=DN), B(BT, 80)], ko=1),
  dict(hand_count=6, disc=[OPR, OGC, OCC, OPB, OPR], dene='PPP', board=[B(CB, 40, 'P'), B(MD, 190, 'PPP'), B(FM, 10), B(MD, 190, 'PPP')],
       ko=0),
  ['Play:Cyrus', 'Attach:1Darkness@1 zone', 'Attack:Cursed Jewel'],
  D, None, stadium=SP,
  approx=AP + "; " + OTR + "; the opponent's Bench order follows the slots (Flutter Mane retreated into Carbink's slot)",
  ambiguous=['Opponent Carbink printing chosen by HP (50) and attack title (Glittering Gift)', AMB_MD,
             'Opponent Flutter Mane printing chosen by HP (80) and attack title (Hexing Flight); B3b 035 is the only match'],
  notes="Global 9 = his 5th turn. Hand after global 7: X Speed, Team Rocket's Weezing ex (Goo-zooka played). 'Global turn 9': draw "
        "Cyrus -> 3. Board: Sableye 190 with two Darkness and Needle; Baltoy 80. Global 7: Cursed Jewel 80 and the Needle 10 leave "
        "Flutter Mane 10. Opponent 'Global turn 8': Flutter Mane retreats for Carbink (Goo-zooka: both Psychic discarded; native 324 s "
        "shows it empty); Psychic to Carbink; Glittering Gift -> each Diancie 3 Psychic; no damage. Opp hand: 5 + draw 6. Cursed "
        "Jewel's retaliation and Goo-zooka's effect both ended with global 8. Carbink 40 (no Needle hit it on global 7). His move, "
        "in the review's order: Cyrus (Flutter Mane, the only damaged Benched Pokemon), Darkness to Baltoy (@1), Cursed Jewel."),
P(G, 11, 6, [1, 1],
  dict(hand=[XS, WZ, CC], disc=[PB, FB, PB, AG, DN, GZ, CY], dene='D', board=[B(MS, 190, 'DD', tool=DN), B(BT, 80, 'D')], ko=1),
  dict(hand_count=6, disc=[OPR, OGC, OCC, OPB, OPR, FM], dene='PPP',
       board=[B(CB, 30, 'P'), B(MD, 190, 'PPPP'), B(FMX, 150, 'P'), B(MD, 190, 'PPPP')], ko=1),
  ['Play:X Speed', 'Play:Copycat', 'Attach:1Darkness@1 zone', 'Evolve:Claydol@1', "Place:Team Rocket's Koffing@2", 'Retreat:1',
   'Play:Poison Barb', 'Tool:Poison Barb@0', 'EndTurn'],
  D, None, stadium=SP,
  approx=AP + "; " + OTR + "; the Flutter Mane in the opponent's discard is the 80-HP Hexing Flight printing; the opponent's Bench "
            "order is not given: Flutter Mane ex is put between the two Diancie (the review names a left and a right Diancie on "
            "global turn 12)",
  ambiguous=['Opponent Carbink printing chosen by HP (50) and attack title (Glittering Gift)', AMB_MD, AMB_FMX],
  draws={1: ['-' + WZ, PBB, KO, CL, AM, WZ, PR]},
  notes="Global 11 = his 6th turn. Hand after global 9: X Speed, Team Rocket's Weezing ex (Cyrus played). 'Global turn 11': draw "
        "Copycat -> 3. Board: Sableye 190 two Darkness, Needle; Baltoy 80 one Darkness. Global 9: Cyrus, Cursed Jewel KOs Flutter "
        "Mane (score 1-1), Carbink promoted 40, Sableye's Needle -> 30. Opponent 'Global turn 10': Flutter Mane ex benched (150), "
        "Psychic to it, Glittering Gift -> each Diancie 4 Psychic; Carbink keeps its one Psychic. Opp hand: 6 + draw 7, Flutter "
        "Mane ex 6 (Copycat on global 11 draws 6). His move, in the review's order: X Speed, Copycat (his hand then only Weezing; "
        "draws Poison Barb, Team Rocket's Koffing, Claydol, Alolan Muk, Team Rocket's Weezing ex, Professor's Research), 2nd Darkness "
        "to Baltoy, Baltoy -> Claydol, Koffing benched (@2), free retreat Sableye -> Claydol (Retreat:1), Poison Barb on Claydol, no "
        "attack, end."),
P(G, 13, 7, [1, 1],
  dict(hand=[AM, WZ, PR, PR], disc=[PB, FB, PB, AG, DN, GZ, CY, XS, CC], dene='D',
       board=[B(CL, 100, 'DD', tool=PBB, behind=[BT]), B(MS, 190, 'DD', tool=DN), B(KO, 80)], ko=1),
  dict(hand_count=6, disc=[OPR, OGC, OCC, OPB, OPR, FM], dene='PPP',
       board=[B(CB, 30, 'P'), B(MD, 210, 'PPPPPP', tool=OGC), B(FMX, 150, 'P'), B(MD, 190, 'PPPPP')], ko=1),
  ["Play:Professor's Research", 'Place:Hoopa ex@3', 'Attach:1Darkness@0 zone', 'Attack:Power Beam'],
  D, None, stadium=SP,
  approx=AP + "; " + OTR + "; the opponent's Bench order is not given: Flutter Mane ex is put between the left (caped) and the right "
            "Diancie",
  ambiguous=['Opponent Carbink printing chosen by HP (50) and attack title (Glittering Gift)', AMB_MD, AMB_FMX],
  draws={0: [HO]},
  notes="Global 13 = his 7th turn. Hand after global 11: Alolan Muk, Team Rocket's Weezing ex, Professor's Research. 'Global turn 13': "
        "draw the 2nd Professor's Research -> 4; his deck then holds one card (Hoopa ex). Board: Claydol 100 (two Darkness, Poison "
        "Barb) Active; Bench Sableye 190 (two Darkness, Needle) in slot 1 after the retreat, Koffing 80 in slot 2. Opponent 'Global "
        "turn 12': 2nd Giant Cape on the left Diancie (190 -> 210), manual Psychic + Glittering Gift: left Diancie 6, right 5, "
        "Flutter Mane ex 1, Carbink 1; Carbink 30. Opp hand: 6 + draw 7, Cape 6. His move, in the review's order: Professor's "
        "Research (draws only Hoopa ex), Hoopa benched (@3) at 170, Darkness to Claydol, Power Beam (KOs Carbink)."),
P(G, 15, 8, [2, 2],
  dict(hand=[AM, WZ, PR], disc=[PB, FB, PB, AG, DN, GZ, CY, XS, CC, PR, BT, CL, PBB], dene='DDDD',
       board=[B(MS, 190, 'DD', tool=DN), B(KO, 80), B(HO, 170)], ko=2),
  dict(hand_count=6, disc=[OPR, OGC, OCC, OPB, OPR, FM, CB, OPB], dene='PPPP',
       board=[B(MD, 200, 'PPPPPPP', tool=OGC, cond=['Poisoned']), B(FMX, 150, 'P'), B(MD, 190, 'PPPPP')], ko=2),
  ["Evolve:Team Rocket's Weezing ex@1", 'Ability@1', 'Attach:1Darkness@2 zone', 'Attack:Cursed Jewel'],
  D, None, stadium=SP,
  approx=AP + "; " + OTR + "; the opponent's Bench order is not given: Flutter Mane ex is listed before the right Diancie",
  ambiguous=[AMB_MD, AMB_FMX],
  notes="Global 15 = his 8th turn. Hand after global 13: Alolan Muk, Team Rocket's Weezing ex, Professor's Research (one Research "
        "played). 'Global turn 15': no draw (deck empty). 'Global turn 14': Brilliant Storm 300 KOs Claydol (Baltoy, Claydol, Poison "
        "Barb, three Darkness to discard; score 2-2, ko 2); Poison Barb poisons the Diancie; he promotes Sableye; Koffing and Hoopa "
        "compacted to slots 1, 2. Opponent global 14: 7th Psychic to the Active (caped) Diancie; Poke Ball with no target (no +1); "
        "Poison checkup 210 -> 200. Global 13's Carbink KO (Carbink and its Psychic to discard; opp ko 2). Opp hand: 6 + draw 7, Poke "
        "Ball 6. His move, in the review's order: Koffing -> Team Rocket's Weezing ex (Boiler Smog: Poisoned and Burned), Darkness "
        "to Hoopa, Cursed Jewel."),
]

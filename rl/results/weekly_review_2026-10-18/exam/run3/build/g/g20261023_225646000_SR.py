from v2_helpers import P, B
D = 'v2deck_995ac0891e'; G = '20261023_225646000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; LI = 'Lillie A3 155'; CC = 'Copycat B1 225'; LP = 'Lucky Ice Pop B2 145'
SS = 'Soothing Shore B4 154'; CY = 'Cyrus A2 150'; PL = 'Parasol Lady B3 152'; MI = 'Misty A1 220'
MD = 'Mega Diancie ex B3b 032'; ME = 'Meloetta B2 070'; RA = 'Ralts A1 130'; GC = 'Giant Cape A2 147'; PP = 'Peculiar Plaza B2 155'
OCC = 'Copycat B1 225'; OPB = 'Poké Ball A2b 111'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
BASE = ['Opponent Mega Diancie ex printing chosen by HP (170 before Giant Cape); B3b 032, B3b 080 and B3b 087 match',
        'Opponent Ralts printing chosen by HP (60) only (its attack was not shown); A1 130, A2 068, A3b 097, A4b 164, A4b 165, B2 063, '
        'B4 071, B4 167 and P-B 028 match',
        'Opponent Giant Cape printing not shown; A2 147, A4b 320 and A4b 321 match']
ME3 = ['Opponent Meloetta printing chosen by HP (70) and type (Psychic); B2 070, B2 233 and P-B 050 match']
ME5 = ['Opponent Meloetta printing chosen by HP (70) and Ability title (Strange Singing); B2 070, B2 233 and P-B 050 match']
ME7 = ['Opponent Meloetta printing chosen by HP (70), Ability title (Strange Singing) and attack title (Psyshot); B2 070, B2 233 and '
       'P-B 050 match']
T_CC = 'Copycat B1 225 used (B1 270 also matches)'
T_PB = 'Poké Ball A2b 111 used (P-A 005 also matches)'
T_PR = "Professor's Research A4b 373 used (P-A 007 also matches)"


def tr(*names):
    return ['Opponent Trainer printings in the discard not shown: ' + ', '.join(names)]


AMB3 = BASE + ME3 + tr(T_CC)
AMB5 = BASE + ME5 + tr(T_CC)
AMB7 = BASE + ME7 + tr(T_CC, T_PB)
AMB9 = BASE + ME7 + tr(T_CC, T_PB, T_PR)
SHORE = {"card": SS, "owner": 0}
TPR = "; the opponent's Trainer printings (Copycat, Poke Ball, Professor's Research, Giant Cape) are not shown, the first listed are used"


def pop_tails(v):
    # Lucky Ice Pop: heals 20 on the Active Oricorio (20 -> 40); coin tails, the Pop goes to the discard
    v['me']['board'][0]['hp'] = 40
    v['me']['discard'] = list(v['me']['discard']) + [LP]


POS = [
P(G, 3, 2, [0, 0],
  dict(hand=[MB, LP, SQ, CY], disc=[PB], dene='', board=[B(OR, 70), B(EI, 80), B(SQ, 60)], ko=0),
  dict(hand_count=1, disc=[OCC], dene='', board=[B(ME, 70), B(MD, 190, tool=GC), B(RA, 60, 'P')], ko=0),
  ['Attach:1Water@1 zone', 'EndTurn'],
  D, None, stadium={"card": PP, "owner": 1},
  approx=AP + "; the opponent's hand (1) counts its global-2 Copycat as drawing 3 (his hand then held 3); his Bench is listed left to "
            "right (Eiscue on the left, Squirtle on the right, the centre spot empty, compacted); the opponent's Bench order (Mega "
            "Diancie ex where Meloetta was, then Ralts) assumes the retreating Diancie took Meloetta's Bench spot" + TPR,
  ambiguous=AMB3,
  notes="Global 3 = his 2nd turn (he went first). Opening five Mega Blastoise ex, Lucky Ice Pop, Squirtle, Oricorio, Poke Ball; "
        "Oricorio Active, Squirtle benched -> 3. Global 1: draws the 2nd Squirtle (kept), Poke Ball finds Eiscue, benched -> hand Mega "
        "Blastoise ex, Lucky Ice Pop, Squirtle. Global 3: draws Cyrus -> 4. The review has the first Eiscue on the left Bench (global "
        "3) and the 2nd Eiscue benched in the centre (global 5), so the setup Squirtle is on the right. Opponent: Mega Diancie ex "
        "Active; global 2 Giant Cape (170 -> 190), Peculiar Plaza, Copycat, Meloetta and Ralts benched, Psychic to Ralts, Diancie "
        "retreats free, Meloetta promoted. Hand 5 - 1 = 4, draw 5, Cape 4, Plaza 3, Copycat (-1, redraw 3) 3, two benched 1. Move: "
        "Water to the left-Bench Eiscue (@1), no attack."),
P(G, 5, 3, [0, 0],
  dict(hand=[MB, LP, SQ, CY, PB], disc=[PB], dene='', board=[B(OR, 70), B(EI, 80, 'W'), B(SQ, 60)], ko=0),
  dict(hand_count=3, disc=[OCC], dene='', board=[B(ME, 70, 'P'), B(MD, 190, tool=GC), B(RA, 60, 'P')], ko=0),
  ['Play:Poké Ball', 'Place:Eiscue@3', 'Attach:1Water@0 zone', 'EndTurn'],
  D, None, stadium={"card": PP, "owner": 1},
  approx=AP + "; the opponent's Strange Singing search on global 4 is counted +1 (hidden); his Bench is listed left to right, "
            "compacted (Eiscue, Squirtle); the opponent's Bench order as on the previous turn" + TPR,
  ambiguous=AMB5,
  draws={0: [EI]},
  notes="Global 5 = his 3rd turn. Hand after global 3: Mega Blastoise ex, Lucky Ice Pop, Squirtle, Cyrus; draws the 2nd Poke Ball -> 5. "
        "Global 4: Strange Singing (hidden search), Psychic to Meloetta, no attack; opponent hand 1 + 1 + 1 = 3. Move: Poke Ball (2nd "
        "Eiscue), bench it 141-144 (the review: centre spot; the compacted Bench gives the lowest empty slot @3), Water to Oricorio "
        "148.5, no attack."),
P(G, 7, 4, [0, 0],
  dict(hand=[MB, LP, SQ, CY, SS], disc=[PB, PB], dene='', board=[B(OR, 20, 'W'), B(EI, 80, 'W'), B(EI, 80), B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[OCC, OPB], dene='', board=[B(ME, 70, 'PP'), B(MD, 190, tool=GC), B(RA, 80, 'P', tool=GC)], ko=0),
  ['Play:Soothing Shore', 'Play:Lucky Ice Pop', 'Attach:1Water@3 zone', 'EndTurn'],
  D, None, stadium={"card": PP, "owner": 1},
  approx=AP + "; the opponent's global-6 Strange Singing and Poke Ball are each counted +1 (hidden); his Bench is listed left to "
            "right (Eiscue left, Eiscue centre, Squirtle right); the opponent's Bench order as before" + TPR,
  ambiguous=AMB7,
  draws={1: []}, vpatch=pop_tails,
  notes="Global 7 = his 4th turn. Hand after global 5: Mega Blastoise ex, Lucky Ice Pop, Squirtle, Cyrus; draws Soothing Shore -> 5. "
        "Global 6: Strange Singing, Poke Ball, 2nd Psychic to Meloetta, Giant Cape to Ralts (60 -> 80), Psyshot 50 -> Oricorio 20. "
        "Opponent hand 3 + 1 + 1 (Singing) + 0 (Poke Ball -1 +1) - Cape = 4. Move (global 7 section, in order): Soothing Shore "
        "(replaces Peculiar Plaza), Lucky Ice Pop heals Oricorio 20 -> 40, tails, discarded (coin patch), Water to the benched "
        "Squirtle (right spot = @3), no attack."),
P(G, 9, 5, [0, 0],
  dict(hand=[MB, SQ, CY, LI], disc=[PB, PB, LP], dene='', board=[B(OR, 10, 'W'), B(EI, 80, 'W'), B(EI, 80), B(SQ, 60, 'W')], ko=0),
  dict(hand_count=5, disc=[OCC, OPB, PP, OPR], dene='',
       board=[B(ME, 70, 'PP'), B(MD, 190, tool=GC), B(RA, 80, 'P', tool=GC), B(RA, 60, 'P')], ko=0),
  ['Retreat:1', 'Attach:1Water@0 zone', 'Attack:Ram'],
  D, None, stadium=SHORE,
  approx=AP + "; his Bench is listed left to right (Eiscue left, Eiscue centre, Squirtle right); the opponent's 2nd Ralts is listed "
            "after the first (benched last)" + TPR,
  ambiguous=AMB9,
  notes="Global 9 = his 5th turn. Hand after global 7: Mega Blastoise ex, Squirtle, Cyrus; draws Lillie -> 4. Oricorio: Shore end of "
        "global 7 40 -> 60; global 8 Psyshot 50 -> 10. Global 8: Strange Singing found nothing (explicit), Professor's Research, 2nd "
        "Ralts benched with a Psychic. Opponent hand 4 + 1 + 1 (Research -1 +2) - Ralts = 5. Move (global 9 section): Oricorio retreats "
        "(its Water discarded), the left Eiscue (@1) promoted, Water to it ~266.5, Ram 269.7 (Meloetta 70 -> 20)."),
P(G, 11, 6, [0, 0],
  dict(hand=[MB, SQ, CY, LI, PR], disc=[PB, PB, LP], dene='W',
       board=[B(EI, 70, 'WW'), B(OR, 10), B(EI, 80), B(SQ, 60, 'W')], ko=0),
  dict(hand_count=7, disc=[OCC, OPB, PP, OPR, OPR], dene='',
       board=[B(ME, 20, 'PP'), B(MD, 190, tool=GC), B(RA, 80, 'PP', tool=GC), B(RA, 60, 'P')], ko=0),
  ["Play:Professor's Research", 'Attach:1Water@1 zone', 'Attack:Ram'],
  D, None, stadium=SHORE,
  approx=AP + "; his Bench is listed left to right (Oricorio in the left spot the promoted Eiscue left, Eiscue centre, Squirtle "
            "right); the opponent's Bench order as before" + TPR,
  ambiguous=AMB9,
  draws={0: [SS, PL]},
  notes="Global 11 = his 6th turn. Hand after global 9: Mega Blastoise ex, Squirtle, Cyrus, Lillie; draws Professor's Research -> 5. "
        "Global 10: Strange Singing no target, 2nd Research, Psychic to the caped Ralts (2 now), Psyshot 50 - Ice Face 40 = 10 -> Eiscue "
        "70 (Shore heals only the turn player's Pokemon). Opponent hand 5 + 1 + 1 = 7. Oricorio 10 has no Energy (retreat), so no Shore "
        "heal. Move (global 11 section): Research (the review names Soothing Shore and Parasol Lady among the 2 cards), Water to benched "
        "Oricorio (@1), Ram KOs Meloetta 20."),
]

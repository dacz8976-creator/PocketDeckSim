from v2_helpers import P, B
D = 'v2deck_995ac0891e'; G = '20261024_003927000_SR'
SQ = 'Squirtle P-A 033'; OR = 'Oricorio A3 066'; EI = 'Eiscue B1 080'; WT = 'Wartortle B1a 018'; MB = 'Mega Blastoise ex B1a 020'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; CC = 'Copycat B1 225'; SS = 'Soothing Shore B4 154'
PL = 'Parasol Lady B3 152'; MI = 'Misty A1 220'
HE = 'Helioptile B4 060'; HL = 'Heliolisk B4 061'; EL = 'Electrike A2a 027'; EL2 = 'Electrike B2b 026'; MM = 'Mega Manectric ex B2b 027'
OPB = 'Poké Ball A2b 111'; OLP = 'Lucky Ice Pop B2 145'; CB = "Clemont's Backpack B1a 066"; OCC = 'Copycat B1 225'
OCY = 'Cyrus A2 150'; TA = 'Training Area B2 153'
AP = "opponent's list unknown; opponent's hand size from the visible plays"
AMB_EL = 'Opponent Electrike (the first, benched on global turn 1) printing chosen by HP (60) only (its attack was not shown); A2a 027, ' \
         'B2b 026, B2b 098 and P-B 043 match'
AMB_MM0 = 'Opponent Mega Manectric ex printing chosen by HP (180); B2b 027, B2b 078, B2b 084 and B2b 113 match'
AMB_MM = 'Opponent Mega Manectric ex printing chosen by HP (180) and attack title (Lightning Accelerator); B2b 027, B2b 078, B2b 084 ' \
         'and B2b 113 match'
TR_PB = 'Opponent Poké Ball printing in the discard not shown; A2b 111 used (P-A 005 also matches)'
TR_CC = 'Opponent Copycat printing in the discard not shown; B1 225 used (B1 270 also matches)'
TR_CY = 'Opponent Cyrus printing in the discard not shown; A2 150 used (A2 190, A4b 326 and A4b 327 also match)'
APX_HE = ("; the opponent's Helioptile is B4 060 (Jumping Kick) and its Heliolisk B4 061 (Electrispark), the cards in play, identified "
          "from their attacks on global turns 3 and 5 (other 60-HP Helioptile printings have other attacks)")


def misty_three_heads(v):
    # Misty on the Active Squirtle: three heads, then tails (+3 Water). The after-chance check plays Misty with no heads,
    # so the three Water are put on Squirtle up front.
    v['me']['board'][0]['energy'] = ['Water', 'Water', 'Water']


POS = [
P(G, 2, 1, [0, 0],
  dict(hand=[MB, SS, MI, PB, OR], disc=[], dene='', board=[B(SQ, 60)], ko=0),
  dict(hand_count=4, disc=[OPB], dene='', board=[B(HE, 60), B(EL, 60)], ko=0),
  ['Place:Oricorio@1', 'Play:Poké Ball', 'Place:Eiscue@2', 'Play:Misty', 'MistyTarget@0', 'Attach:1Water@2 zone', 'Retreat:2',
   'Play:Soothing Shore', 'EndTurn'],
  D, None,
  approx=AP + "; the opponent's global-1 Poke Ball is counted +1 (Electrike was benched from it)" + APX_HE + "; Misty's coins (three "
            "heads, then tails) are put in the after-chance check as three Water on Squirtle up front, because the engine plays Misty "
            "with no heads there",
  ambiguous=[AMB_EL, TR_PB],
  draws={1: [EI]}, vpatch=misty_three_heads,
  notes="Global 2 = his 1st turn (he went second). Setup: Squirtle 60 Active, Mega Blastoise ex, Soothing Shore, Misty, Poke Ball in "
        "hand; draws Oricorio -> 5. Opponent: Helioptile 60 Active; global 1 Poke Ball, Electrike 60 benched; hand 5 - 1 = 4, draw 5, "
        "Poke Ball 5, Electrike 4. Move (global 2 section, in order): bench Oricorio 53 s (@1), Poke Ball 58 s (Eiscue), bench Eiscue "
        "65 s (@2), Misty on Active Squirtle 68-77 s (three heads then tails: +3 Water; the engine asks the target, MistyTarget@0), "
        "Water to Eiscue 82-84 s, Squirtle retreats to Eiscue 85-87 s (one Water; Squirtle keeps two), Soothing Shore 89-90 s, no "
        "attack. Misty is not in v2_helpers' chance-step list and pg_legal does not stop at it (it plays it with no heads), so the "
        "coin patch puts the three Water on Squirtle in the after-chance variant."),
P(G, 4, 2, [0, 0],
  dict(hand=[MB, PL], disc=[PB, MI], dene='W', board=[B(EI, 80, 'W'), B(OR, 60), B(SQ, 60, 'WW')], ko=0),
  dict(hand_count=4, disc=[OPB], dene='', board=[B(HE, 60, 'L'), B(MM, 180, behind=[EL])], ko=0),
  ['Attach:1Water@0 zone', 'Attack:Ram'],
  D, None, stadium={"card": SS, "owner": 0},
  approx=AP + APX_HE + "; his Bench order (Oricorio, then Squirtle in the spot Eiscue left) follows the slots of global 2",
  ambiguous=[AMB_EL, AMB_MM0, TR_PB],
  notes="Global 4 = his 2nd turn. Hand after global 2: Mega Blastoise ex; draws Parasol Lady -> 2. Global 3: Electrike -> Mega "
        "Manectric ex (Bench), Lightning to Helioptile, Jumping Kick 10 to benched Oricorio (70 -> 60; no Water on it, so no Shore "
        "heal). Opponent hand 4 + 1 - Mega Manectric ex = 4. Move (global 4 section): 2nd Water to Active Eiscue 130-131 s, Parasol "
        "Lady not played, Ram 135-136 s (Helioptile 60 -> 10)."),
P(G, 6, 3, [0, 0],
  dict(hand=[MB, PL, CC], disc=[PB, MI, SS], dene='W', board=[B(EI, 30, 'WW'), B(OR, 10), B(SQ, 10, 'WW')], ko=0),
  dict(hand_count=1, disc=[OPB, OLP, CB, CB, OCC], dene='', board=[B(HL, 50, 'L', behind=[HE]), B(MM, 180, 'L', behind=[EL])], ko=0),
  ['Attach:1Water@2 zone', 'Play:Copycat', 'Evolve:Wartortle@2', 'Attack:Ram'],
  D, None, stadium={"card": TA, "owner": 1},
  approx=AP + APX_HE + "; the opponent's hand (1) counts its Copycat as drawing 2 (his hand then held 2), and his Copycat drew "
            "exactly 1 card",
  ambiguous=[AMB_EL, AMB_MM0, TR_PB, TR_CC],
  draws={1: ['-' + MB, '-' + PL, WT]},
  notes="Global 6 = his 3rd turn. Hand after global 4: Mega Blastoise ex, Parasol Lady; draws Copycat -> 3. Global 5: Lucky Ice Pop "
        "(Helioptile 10 -> 30, tails, discarded), Helioptile -> Heliolisk (80 max, 50 now), two Clemont's Backpack, Lightning to the "
        "benched Mega Manectric ex, Copycat (redraws 2 = his hand), Training Area replaces his Soothing Shore (to his discard), "
        "Electrispark: Eiscue 80 -> 30 (Ice Face), Oricorio 60 -> 10, Squirtle 60 -> 10. Opponent hand 4 + 1 - Pop - Heliolisk - two "
        "Backpacks - Copycat -> redraw 2, - Training Area = 1. Move (global 6 section, in order): 3rd Water to benched Squirtle 211-213 "
        "s, Copycat 218 s (Mega Blastoise ex and Parasol Lady shuffled away, draws Wartortle), Squirtle -> Wartortle 225-227 s (10 -> 40), "
        "Ram 231-233 s KOs Heliolisk 50."),
P(G, 10, 5, [1, 2],
  dict(hand=[PR], disc=[PB, MI, SS, CC, WT, SQ, OR], dene='WWWW', board=[B(EI, 30, 'WW'), B(SQ, 60, 'W')], ko=2),
  dict(hand_count=1, disc=[OPB, OLP, CB, CB, OCC, OCY, HL, HE], dene='L', board=[B(EL2, 60, 'L'), B(MM, 180, 'LL', behind=[EL])], ko=1),
  ["Play:Professor's Research", 'Attack:Ram'],
  D, None, stadium={"card": TA, "owner": 1},
  approx=AP + APX_HE + "; the opponent's 2nd Electrike is B2b 026 by its Quick Attack (global 9)",
  ambiguous=[AMB_EL, 'Opponent Active Electrike printing chosen by HP (60) and attack title (Quick Attack); B2b 026 and B2b 098 match',
             AMB_MM, TR_PB, TR_CC, TR_CY],
  draws={0: [PR, MB]},
  notes="Global 10 = his 5th turn. Hand: empty after global 6 (Copycat drew only Wartortle, evolved); global 8 draws Squirtle, "
        "benched, Water to it -> empty; global 10 draws Professor's Research -> 1. Global 7: 2nd Lightning to Mega Manectric ex, Cyrus "
        "pulls Wartortle 40 Active (Eiscue 30 to the Bench), Lightning Accelerator 110 KOs Wartortle (3 Water and Squirtle to the "
        "discard), Oricorio 10 promoted. Global 9: 2nd Electrike benched, Lightning to it, Mega Manectric ex (retreat 0, keeps two "
        "Lightning) switched to it, Quick Attack heads 40 KOs Oricorio, Eiscue 30 (two Water) promoted. Bench: Squirtle 60 with one "
        "Water. Opponent hand 1 + 1 - Cyrus = 1, + 1 - Electrike = 1. Score 1-2 (his Heliolisk KO; Wartortle, Oricorio). Discard "
        "Energy: one Water (global 2 retreat) + three on Wartortle. Move (global 10 section): Professor's Research 322 s (draws the "
        "2nd Research and Mega Blastoise ex), no attachment observed, Ram 332-334 s (Electrike 60 -> 10)."),
]

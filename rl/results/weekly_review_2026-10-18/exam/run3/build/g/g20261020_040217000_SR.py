from v2_helpers import P, B
D = 'v2deck_9633a01781'; G = '20261020_040217000_SR'
DT = 'Dratini B4 116'; DA = 'Dragonair B4 117'; DN = 'Dragonite B4 118'; GO = 'Goomy B1 177'; HG = 'Hisuian Goodra B3b 050'
PB = 'Poké Ball P-A 005'; PR = "Professor's Research P-A 007"; RC = 'Rare Candy A3 144'; LP = 'Lucky Ice Pop B2 145'
MO = 'Moltres ex A1 047'; CM = 'Charmander A1 033'; CE = 'Charmeleon B1a 012'; DW = 'Dewpider A3 052'
OPB = 'Poké Ball A2b 111'; OCC = 'Copycat B1 225'; OPR = "Professor's Research A4b 373"
AP = "opponent's list unknown; opponent's hand size from the visible plays"
OTR = "the opponent's Trainer printings (Poké Ball, Copycat, Professor's Research) are not shown; the printing cards.py lists first is used"


def no_energy_now(p):
    """The first player's first turn: the zone gives no Energy (RULES_FOR_AGENTS). P() needs a letter for ez_now; with one set,
    pg_legal_v14 lists 'Attach:1Metal@0 zone' as legal on global turn 1. energy_now None makes the engine read the zone as
    ["None", "Some(Metal)"] and list no attach (scratch/b3/t_t1energy.py)."""
    p['me']['energy_now'] = None
    return p


POS = [
no_energy_now(P(G, 1, 1, [0, 0],
  dict(hand=[DA, RC, DN, PB, LP], disc=[], dene='', board=[B(DT, 60)], ko=0),
  dict(hand_count=4, disc=[], dene='', board=[B(MO, 140)], ko=0),
  ['Play:Poké Ball', 'Place:Goomy@1', 'EndTurn'],
  D, None,
  approx=AP + "; Moltres ex printing chosen by name and HP (140) only (no attack used yet; every 140-HP Moltres ex printing has the "
            "same attacks); "
            "his Energy zone is not read on this turn (no Energy on the first player's first turn, so energy_now is None): "
            "the next Energy is the one he attached on his next turn (Metal), which the zone shows as next",
  ambiguous=['Opponent Moltres ex printing chosen by name and HP (140); A1 047, A1 255, A1 274, A3b 103, A4b 067 and P-A 025 match'],
  draws={0: [GO]}, ez_now='M', ez_next='M',
  notes="Global 1 = his 1st turn (he went first). 'Deck identity and opening': opening five Dratini, gold-art Dragonair, Rare Candy, "
        "Dragonite, Poke Ball; Dratini Active leaves four. 'Global1': draw Lucky Ice Pop -> hand of 5. Opponent lone Moltres ex 140 Active, "
        "opening 5 - 1 = 4 in hand, no draw yet (second player). His move, 'Global1' in time order: Poke Ball ~57s (Goomy 40, Sticky "
        "Membrane, retrieved ~59s), Goomy benched ~62-64s (@1), no Energy, end without attack. No zone reading on this turn; next "
        "zone Energy = Metal, from 'Global3' (Attach Metal ~146s). energy_now set to None after P() (no Energy on the first "
        "player's first turn; with a letter the engine listed an attach as legal).")),
P(G, 3, 2, [0, 0],
  dict(hand=[DA, RC, DN, LP, GO], disc=[PB], dene='', board=[B(DT, 60), B(GO, 40)], ko=0),
  dict(hand_count=4, disc=[OPB, OCC], dene='', board=[B(MO, 140, 'R'), B(CM, 60, 'RR')], ko=0),
  ['Place:Goomy@2', 'Attach:1Metal@0 zone', 'Retreat:1', 'Evolve:Dragonair@1', 'Ability@1', 'EndTurn'],
  D, None,
  approx=AP + "; " + OTR + "; the opponent's Poké Ball result on global turn 2 is hidden (counted +1 card; Copycat right after "
            "set the hand to 4 cards either way); the Benched Charmander's printing is chosen by HP (60) only (its attack was not "
            "shown); his next zone Energy is not read on this turn: ez_next is the Energy he attached on his next turn (Lightning)",
  ambiguous=['Opponent Moltres ex printing chosen by HP (140) and attack title (Inferno Dance); A1 047, A1 255, A1 274, '
             'A3b 103, A4b 067 and P-A 025 match',
             'Opponent Benched Charmander: its attack was not shown; printing chosen by HP (60) only (the 60-HP Charmander printings '
             'have Ember, Combustion or Bite)'],
  ez_now='M', ez_next='L',
  notes="Global 3 = his 2nd turn. Hand after global 1: Dragonair, Rare Candy, Dragonite, Lucky Ice Pop (Poke Ball played, Goomy "
        "benched); 'Global2' Copycat draws against his four-card hand (consistent). 'Global3': draw 2nd Goomy ~136s -> 5 cards. "
        "Opponent ('Global2'): Fire to Moltres ex; Poke Ball ~71s (hidden), Charmander 60 benched ~79s, Copycat ~81s (shuffle, draw 4), "
        "Inferno Dance 2 heads -> Charmander 2 Fire. Opp hand: 4 + draw 5, Poke Ball 5, Charmander 4, Copycat 4. His move, "
        "'Global3' in time order: bench Goomy ~138-140s (@2), Metal to Active Dratini ~146s, retreat for 1 (Metal discarded), "
        "'illustrated Goomy' promoted ~151-153s, Dratini evolved to Dragonair ~156-158s on the Bench, Dragon's Blessing ~159-162s "
        "puts the discarded Metal on Active Goomy. The review does not say which Bench Goomy came in (both are Goomy B1 177, 40 HP, "
        "no Energy, so the two choices give the same position up to slot order); Retreat:1 (the first Goomy) "
        "puts Dratini/Dragonair in slot 1 and leaves the other Goomy in slot 2, matching the end-of-turn order 'Bench Dragonair80HP "
        "and other Goomy40HP'."),
P(G, 5, 3, [0, 0],
  dict(hand=[RC, DN, LP, DA], disc=[PB], dene='', board=[B(GO, 40, 'M'), B(DA, 80, behind=[DT]), B(GO, 40)], ko=0),
  dict(hand_count=5, disc=[OPB, OCC, OPR], dene='', board=[B(MO, 140, 'RR'), B(CM, 60, 'RRRR'), B(DW, 60)], ko=0),
  ['Attach:1Lightning@1 zone', 'EndTurn'],
  D, None,
  approx=AP + "; " + OTR + "; the Benched Charmander's printing is chosen by HP (60) only (its attack was not shown); his next zone "
            "Energy is not read on this turn: ez_next is the Energy he attached on his next turn (Lightning)",
  ambiguous=['Opponent Moltres ex printing chosen by HP (140) and attack title (Inferno Dance); A1 047, A1 255, A1 274, '
             'A3b 103, A4b 067 and P-A 025 match',
             'Opponent Benched Charmander: its attack was not shown; printing chosen by HP (60) only (the 60-HP Charmander printings '
             'have Ember, Combustion or Bite)',
             'Opponent Dewpider printing chosen by HP (60) and attack title (Hook)'],
  ez_now='L', ez_next='L',
  notes="Global 5 = his 3rd turn. Hand after global 3: Rare Candy, Dragonite, Lucky Ice Pop (Goomy and Dragonair played). 'Global5': "
        "draw 2nd Dragonair ~210s -> 4 cards. Board ('Global3' end): Active Goomy 40 with Metal; Bench Dragonair 80 (on Dratini), other "
        "Goomy 40. Discard: Poke Ball; no discarded Energy (Metal recovered). Opponent ('Global4'): draw (5), Professor's Research ~185s "
        "(-1 +2 = 6), Dewpider 60 (Hook) benched ~190s (5), 2nd Fire to Moltres ex, Inferno Dance 2 heads -> Charmander 4 Fire. His move, "
        "'Global5': Lightning to Benched Dragonair ~229-231s, no attack (Ram needs Water/Psychic), end turn."),
P(G, 7, 4, [0, 1],
  dict(hand=[RC, DN, LP, DA, PR], disc=[PB, GO], dene='M', board=[B(GO, 40), B(DA, 80, 'L', behind=[DT])], ko=1),
  dict(hand_count=4, disc=[OPB, OCC, OPR], dene='',
       board=[B(MO, 140, 'RRRR'), B(CE, 80, 'RRRR', behind=[CM]), B(DW, 60), B(MO, 140)], ko=0),
  ["Play:Professor's Research", 'Play:Rare Candy', 'Evolve:Hisuian Goodra@0', 'Attach:1Lightning@0 zone', 'Ability@1', 'EndTurn'],
  D, None,
  approx=AP + "; " + OTR + "; the Charmander under Charmeleon: printing chosen by HP (60) only; his next zone Energy is not read on "
            "this turn: ez_next is the Energy he attached on his next turn (Metal)",
  ambiguous=['Opponent Moltres ex printings chosen by HP (140) and attack titles (Inferno Dance, Heat Blast); A1 047, A1 255, A1 274, '
             'A3b 103, A4b 067 and P-A 025 match',
             'Opponent Charmeleon printing chosen by HP (80) and Ability title (Ignition); B1a 012, B2b 008, B2b 092 and P-B 020 match',
             'Opponent Charmander under Charmeleon: its attack was not shown; printing chosen by HP (60) only',
             'Opponent Dewpider printing chosen by HP (60) and attack title (Hook)'],
  draws={0: [LP, HG]}, ez_now='L', ez_next='M',
  notes="Global 7 = his 4th turn. Hand after global 5: Rare Candy, Dragonite, Lucky Ice Pop, Dragonair. 'Global7': draw Professor's "
        "Research ~274s -> 5. Board: 'Global6' Heat Blast 70 KOs Active Goomy (Metal to discard), the remaining Goomy 40 promoted "
        "~269-270s; Bench Dragonair 80 with Lightning. Discard Poke Ball, Goomy; discarded Energy Metal. Score 0-1, ko 1. Opponent "
        "('Global6'): draw (6), Charmander -> Ignition Charmeleon 80 (5) keeping 4 Fire, Ignition Fire to Moltres (3), 2nd Moltres ex "
        "benched (4), Fire to Moltres (4 Fire), Heat Blast. Opp Bench order Charmeleon, Dewpider, Moltres ex (benched in that order; "
        "'Global8' retreat puts Moltres on the left Bench, 'Final boards' list Moltres, Dewpider, 2nd Moltres). His move, 'Global7' in "
        "time order: Professor's Research ~277s (Lucky Ice Pop ~279s, Hisuian Goodra ~280s), Rare Candy ~283-288s on Active Goomy -> "
        "Hisuian Goodra 150, Lightning to Goodra ~290s, Dragon's Blessing from Benched Dragonair ~291-295s puts the discarded Metal on "
        "Goodra, end without attack."),
]

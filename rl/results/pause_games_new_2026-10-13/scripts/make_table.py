#!/usr/bin/env python3
"""make_table.py: POSITION_TABLE.md, one row per position: his line, km3's free-run modal plan, km3 step by step along his line, and a short reading.
usage: make_table.py (run in the folder)"""
import json, os

pos = {p['id']: p for p in json.load(open('positions_all.json', encoding='utf-8'))}
summ = {s['id']: s for s in json.load(open('km3_summary.json', encoding='utf-8'))}
forced = {s['id']: s for s in json.load(open('runs_forced/forced_summary.json', encoding='utf-8'))}
meta = json.load(open('games_meta.json', encoding='utf-8'))
LISTROW = {r['position_id']: ('' if r['switch2_flag'] == 'no' else r['switch2_flag']) for r in json.load(open('position_list.json', encoding='utf-8'))}

# the reading of the positions where km3 and he part for a reason that is not a tie or an order (written by hand after reading the positions, the ledgers and the reviews)
READING = {
    '010837000-t03': "He evolves Glimmora, puts the Energy on Pawniard and retreats it (paying that Energy). Pawniard's Slash (30) would have knocked out the 30-HP Pichu on the opponent's Active: a point on turn 3. km3 attacks with Slash in 4 of 12 seeds and plays Copycat first in the other 8 (its plan is cut there); it scores his retreat 10,600 below its best. The cost of the knock-out would have been small: the opponent put its Mega Kangaskhan ex Active by retreating Pichu for free and knocked out Glimmora anyway. Looks like a miss.",
    '010837000-t05': "Muk before or after benching Glimmet is a tie. The Energy: he puts it on the benched Pawniard (it becomes Kingambit next turn), km3 on the Active Regigigas (150 HP, which can attack once Muk shuts off Seal of Antiquity, but needs three Energy).",
    '010837000-t07': "Both Rare Candy Kingambit. He puts the Energy on Glimmet (his next Active), km3 on Kingambit, which would then hold the 2 Energy Overlord's Blade needs. A bait-and-feed plan against a build-up plan; km3's score gap is small (658).",
    '010837000-t09': "He heals Glimmet with two Lucky Ice Pops and attacks for 20 (Hang Down); km3 retreats Glimmet and attacks with Kingambit's Overlord's Blade. The Blade does 60 + 40 per Pokémon of his already knocked out (2 so far): 140 on a 180-HP Mega Kangaskhan ex. The position runner does not carry that count (see the notes), so km3 saw 60 and still preferred it.",
    '010837000-t11': "The clearest disagreement. The Active is Pichu (30 HP, nothing reduces damage). He plays Heavy Helmet and attacks with Glimmet's Hang Down (20), leaving Pichu at 10. km3 retreats Glimmet and knocks Pichu out with Kingambit's Overlord's Blade (Kingambit already holds the 2 Energy): a point. km3 scores his line 9,200 below its own. His reason may be the next turns (Glimmet was knocked out on the opponent's turn, which raised the Blade to 180 for turn 13).",
    '010837000-t13': "Both attack with the Blade (180: it knocks out Raticate ex for 2). He puts the third Energy on the Active, km3 on the benched Muk.",
    '010837000-t15': "The opponent did not come back; no plan of his. km3: Energy, then the Blade (the Blade would be 180 against Mega Kangaskhan ex's 180 HP at 2-2: a winning knock-out).",
    '010003000-t01': "He uses Mesagoza (a free coin flip) before Professor's Research, km3 plays Research first; the flip does not depend on the order. Same turn.",
    '010003000-t03': "He evolves and attacks and keeps Heavy Helmet in hand; km3 puts it on Regigigas first. Same turn, an earlier Tool.",
    '010003000-t07': "Glimmora has 20 HP. km3 plays Lucky Ice Pops first (each heads returns the Pop; up to four in a row), he does not and attacks; Glimmora is then knocked out (the opponent got no point: Shattering Crystal, heads). To get above the 70 she needed three Pops, so two heads in a row (1 in 4).",
    '010003000-t11': "He was about to attack with Regigigas (the opponent conceded as the attack menu opened); km3 attacks at once with Giga Turbo. Same turn.",
    '014423000-t01': "Opening: Poké Ball, Copycat or Research first; km3's scores are 114, 180 and 467 (a weak preference for Copycat; Poké Ball in 5 of 12 seeds).",
    '014423000-t03': "He puts the Energy on the benched Pawniard; this is also km3's top choice in seed 1 (8 of 12 seeds go to the Active). The Active, Grimer, is knocked out next turn.",
    '014423000-t05': "Helmet on Regigigas and Copycat as he did. The Energy goes to the Active Regigigas (which cannot attack) in km3's plans, and to the new Glimmet in his.",
    '014423000-t07': "He evolves Glimmora and puts the Energy on the benched Pawniard; km3 puts it on the Active Regigigas (50 HP, no way to attack), which Dedenne ex's 100 damage knocks out on the next turn. He looks right.",
    '014423000-t09': "Both use Venomous Hit. He attaches first; km3 attacks without attaching (all its options tie in a lost position).",
    '015011000-t01': "Opening: Poké Ball first in 9 of 12 seeds.",
    '015011000-t03': "The opponent did not come back; no plan of his.",
    '015659000-t01': "Same opening.",
    '015659000-t03': "Evolution, Lucky Ice Pop, Energy: the same cards, km3 starts with the Pop (tie).",
    '015659000-t05': "He evolves Glimmora, benches Pawniard and puts the Energy on Pawniard; km3 puts it on the Active Regigigas (30 HP, a Fighting weakness against Mega Lucario ex's 90), which is knocked out next turn. He looks right.",
    '015659000-t07': "Same plan.",
    '015659000-t09': "Same first move (Poké Ball).",
    '015659000-t13': "He conceded this turn (0-2, 10-HP Pokémon, Mega Lucario ex benched); km3 starts with Research as he did.",
    '020824000-t01': "Same opening.",
    '020824000-t03': "He evolves Glimmora and Alolan Muk (Power of Alchemy switches off Shuckle ex's Solid Shell and Ogerpon ex's Soothing Wind, which stopped the Poison last turn) and attacks; km3 benches Pawniard first and plays the same turn.",
    '020824000-t05': "Same first move (Research).",
    '020824000-t07': "He benches Regigigas, uses Mesagoza (tails), attaches to Glimmet and retreats it into Regigigas without attacking. km3 attaches, uses Mesagoza, and, in 9 of 12 seeds, the flip brings a Glimmora: it evolves and attacks with Venomous Hit. His flip was tails.",
    '020824000-t09': "He only attaches. km3 attaches and uses the Stadium (Fragrant Forest), which finds a random Grass Basic: his deck has none, so it does nothing.",
    '020824000-t11': "He plays a Lucky Ice Pop (tails), then Ilima to put the damaged Regigigas back in his hand, benches it at full 150 HP and retreats into it. km3 does not use Ilima (it ranks it 270 points below its Lucky Ice Pop chain). Looks like a good idea of his that km3 misses.",
    # ---- the eight games added later (deck lists: 010706, 203719 and 030351 are ASSUMED from a game of the same named deck, so their positions are unverified)
    '010706000-t09': "He uses Mesagoza (tails) before attaching and attacking with Giga Turbo (100 on Mega Diancie ex); km3 attaches and attacks at once. Same turn.",
    '010706000-t11': "Heavy Helmet goes on the benched Kingambit in his line, on the Active Muk in km3's (small gap).",
    '010706000-t21': "He wins the game here: Overlord's Blade after three of his Pokémon were knocked out is 180 (+20 weakness) on a 130-HP Mega Gardevoir ex, 3 points, 3-2. km3 plays the same turn but the runner's count is 0: for km3 the Blade does 80 and cannot win.",
    '203719000-t07': "Rare Candy Kingambit, then Ilima puts his 10-HP Regigigas back in his hand to bench it at 150. km3 finds the same Ilima reset in 12 of 12 seeds; it then promotes Kingambit and uses the Blade, he promoted Glimmora (his plan's last step, Giga Turbo, is a converter slip: the converter does not follow Ilima's promotion; the review says Glimmora's Venomous Hit).",
    '203719000-t15': "Evolve, three Lucky Ice Pops, Energy on Kingambit, Venomous Hit; km3 starts with the Pops (up to four).",
    '203719000-t17': "Glimmora has 10 HP: he heals it with Pops (tails, heads, tails) and attacks with Venomous Hit; km3 attaches, plays Pops, retreats into Kingambit and uses the Blade (a different plan; the gap is small, 40).",
    '210041000-t06': "Mega Lucario ex (Fighting Pulse 90, Regigigas weak to Fighting) faces his 40-HP Regigigas. He puts the Energy on Pawniard and ends the turn (the game warns that a Supporter can still be played; he confirms). km3 plays Ilima in 12 of 12 seeds (Regigigas back in hand, fresh at 150 HP, Pawniard Active, Slash). Regigigas was knocked out next turn (0-1). The scores tie, so not clearly a mistake; a chance he left unused.",
    '210041000-t14': "He conceded here (0-2).",
    '210823000-t02': "His turn 1: Research first (draw 2); km3 plays Copycat first (the opponent holds 5 cards: draw 5; 877 higher). The only real gap of the added games that is not a missing condition.",
    '210823000-t08': "Ilima resets his 50-HP Regigigas (both). He then attacks with Glimmora's Venomous Hit (the plan's 'Giga Turbo' is the same converter slip); km3 promotes Kingambit and uses the Blade (60 with the runner's count at 0).",
    '210823000-t12': "The opponent conceded as he found his deck empty; no plan of his.",
    '225319000-t04': "He puts Heavy Helmet on Pawniard (Retreat Cost 1, below the Helmet's 3, so it does nothing until it becomes Kingambit) and uses Copycat. km3 starts with Mesagoza's coin flip in 8 of 12 seeds and with Copycat in 3.",
    '225319000-t06': "He attaches to Pawniard and retreats it, paying with that Energy (the zone Energy as a free retreat); km3 attaches and attacks with Slash. Same habit as 010837 t03.",
    '230258000-t09': "Mesagoza, Grimer, Rare Candy Kingambit, then Lucky Ice Pops; km3 plays the Pops first. Order.",
    '022530000-t09': "He uses Rainbow Cave (a fresh Fighting) and Dragonair's Dragon's Blessing (one more Energy for Haxorus from the discard) before Frenzied Blade; km3 attaches once and attacks, using neither.",
    '030351000-t05': "Unverified deck. His Dragonair is Asleep (it cannot attack); the runner has no Sleep, so km3 attacks with Draconic Whip and scores his line 8,600 lower. Not a real disagreement.",
    '030351000-t13': "Unverified deck. His Druddigon is Asleep (no retreat, no attack); km3 retreats and attacks (gap 10,100). Not a real disagreement. The deck-empty check of the next turn also fails by 4 cards (the assumed list or an untracked discard is off): turn 15 could not be run.",
    '020824000-t13': "Lucky Ice Pops and an Energy on Regigigas; km3 adds the useless Fragrant Forest use and plays up to seven Pops in a row.",
}

lines = ['# The 34 positions: his line, km3, and a short reading', '',
         '`first`: in how many of 12 seeds km3\'s first move is his. `line`: km3 step by step along his line (his plan cut at its first draw card): the first step where km3 would play something else in most seeds, with the gap between km3\'s best score and the score of his step (seed 1; scores are km3\'s own evaluation, a very negative number means km3 thinks the game is lost, ties at the top are common there). Switch 2: the position holds a card the rules switch changed.', '',
         '| position | game turn, points | his plan | km3 modal plan (12 seeds) | first | line | switch 2 | reading |', '|---|---|---|---|---|---|---|---|']
for pid, p in pos.items():
    s = summ.get(pid, {})
    f = forced.get(pid, {})
    dev = f.get('first_deviation')
    if not p['his_plan']:
        line = 'no plan of his'
    elif dev is None:
        line = 'km3 plays all of it'
    else:
        top = max(dev['km3_plays'].items(), key=lambda x: x[1])[0]
        gap = dev.get('gap_seed1')
        line = f"step {dev['step'] + 1} ({dev['his']}): km3 plays {top}" + (f", gap {gap:,.0f}" if gap is not None else '')
    short = pid.split('_', 1)[1]
    sw = LISTROW.get(pid, '')
    lines.append(f"| {short} | {p['turn_count']}, {p['points'][0]}-{p['points'][1]} | {' > '.join(p['his_plan']) or '-'} | {' > '.join(s.get('modal', [])) or '-'} | {s.get('same_first', '-')}/12 | {line} | {sw} | {READING.get(short, '')} |")
open('POSITION_TABLE.md', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(len(pos), 'rows;', sum(1 for pid in pos if pid.split('_', 1)[1] in READING), 'with a reading')

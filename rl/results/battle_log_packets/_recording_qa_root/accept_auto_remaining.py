"""Source-bound lead acceptance after independent reading and frame inspection."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
video = sys.argv[1]
packet = root / 'Recording_QA' / (Path(video).stem + '_auto_sol')
binding = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
if video == '20260930_160256000_iOS.MP4':
    review_path = packet / 'REVIEW.md'
    raw = review_path.read_text(encoding='utf-8-sig')
    (packet / 'FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md').write_text(raw, encoding='utf-8')
    revised = raw.replace('Dacz 8976', 'Dacz8976')
    revised = revised.replace('The revealed result is Typhlosion ex, and it evolves the damaged Quilava: 180 maximum HP,160 remaining.', 'The search resolves into the hidden AI hand; the identity of the searched copy is not independently exposed. Typhlosion ex is then played to evolve the damaged Quilava: 180 maximum HP, 160 remaining.')
    revised = revised.replace('The interface displays three filled point circles, rather than a fourth circle; do not report that cap as evidence that Typhlosion ex was worth only one point.', 'The final interface displays three filled owner point circles and one opponent circle. These visible circles do not establish an internal score above three, and do not change the printed two-point ex knockout rule.')
    review_path.write_text(revised, encoding='utf-8')
    summary_path = packet / 'SUMMARY.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8-sig'))
    summary['point_progression'][-1]['event'] = 'Typhlosion ex knockout; three owner circles and one opponent circle visible; printed two-point ex rule; no retained exact award caption or internal score above three established'
    summary_path.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    uncertainty_path = packet / 'UNCERTAINTIES.json'
    uncertainty = json.loads(uncertainty_path.read_text(encoding='utf-8-sig'))
    uncertainty['bounded_observation_limits'][0]['observation'] += ' Juliana resolves into a hidden hand before Typhlosion ex is played; the searched copy is not independently identified.'
    uncertainty['bounded_observation_limits'][2]['impact'] = 'Report the explicit win, final visible three owner circles and one opponent circle, and printed two-point ex entitlement. No retained +2 caption or internal score above three is asserted.'
    uncertainty_path.write_text(json.dumps(uncertainty, indent=2) + '\n', encoding='utf-8')
    (packet / 'LEAD_CORRECTION.md').write_text('''# Lead corrections

The unmodified worker report is preserved in `FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md`.

Independent inspection of `overview/sheet_08.jpg` shows Juliana resolving into face-down cards before the subsequent Typhlosion evolution. The visible evolution identifies the played Pokemon, but does not identify the searched copy. The revised account preserves that distinction.

`overview/sheet_12.jpg` shows the final three owner circles and one opponent circle. The visible Typhlosion ex card establishes its two-point rule. No exact award caption was retained, so the report does not assert an internal total above three or a score cap implementation.

Restored the exact visible owner handle Dacz8976 after the worker's spacing pass inserted a space. No outcome, turn coverage or source media changed.
''', encoding='utf-8')
    data = {
        'scope': 'Complete fifteen-turn 320.985215-second autopilot computer battle, setup through both Greninja lines, Typhlosion Energy disruption, Mega Slowbro final attack and explicit Victory',
        'first_pass': 'gpt-6.1-sol/high /root/sol_auto_160256',
        'lead_checks': 'Read full review, coverage, summary and uncertainties. Independently inspected opening AI/Auto sheet;123-second ordinary Combusken Fire attachment;203-second Juliana text and complete sheet08 hidden search/evolution sequence;207-second Typhlosion card;249-second five-head/one-tail panel;285-second Irida text and zero-Energy Greninja;288-second Slowbro130HP/twoWater and Greninja60HP;303-second final two-head/one-tail panel;309-second opponent Bench40/30 and owner150HP/threeWater;complete sheet12 final visible3-1 circles;320.60-second explicit Victory. Hidden search-copy attribution and internal score claims narrowed in LEAD_CORRECTION.md.',
        'outcome': 'owner_win',
        'final_points': {'owner': 3, 'opponent': 1},
        'result_display': 'Win; 3-1 circles shown, final ex knockout',
        'owner_visible_core': 'Greninja / Greninja ex / Mega Slowbro ex',
        'opponent': 'AI Mega Blaziken ex & Typhlosion ex Deck (Deluxe Pack: Mega)',
        'last_turn': 15,
        'useful_finding': 'Typhlosion flips five heads but removes only Greninja ex\'s two available Water. Shifting Stream then brings in the accumulating Mega Slowbro. Irida heals only the energized Slowbro, and its final two-head attack damages both opposing Bench Pokemon without knocking either out.',
        'limitations': 'Root verification is bounded. Juliana search-copy identity remains hidden. The printed two-point ex rule and final visible3-1 circles are recorded separately; no exact +2 caption or internal total above three is established.',
    }
elif video == '20260930_161055000_iOS.MP4':
    review_path = packet / 'REVIEW.md'
    raw = review_path.read_text(encoding='utf-8-sig')
    (packet / 'FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md').write_text(raw, encoding='utf-8')
    revised = raw.replace('The terminal UI caps its visible victory circles at three; the review records the observed +2 from the prior two-point state rather than claiming a displayed4-1 score.', 'The terminal animation displays three filled owner circles after an explicit +2 award from the prior two-point state. This establishes the visible award and win, without asserting an internal total above three or a score-cap implementation.')
    review_path.write_text(revised, encoding='utf-8')
    (packet / 'LEAD_CORRECTION.md').write_text('''# Lead clarification

The unmodified worker account is preserved in `FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md`. The final paragraph now records the visible three circles and explicit +2 award without inferring an internal score cap. No outcome, turn coverage or source changed.
''', encoding='utf-8')
    data = {
        'scope': 'Complete fourteen-turn 259.13-second computer practice battle, setup through both Generator flips, visible Auto pause/resume, Electrical Cord transfer, retreat, healing and explicit Victory',
        'first_pass': 'gpt-6.1-sol/high /root/sol_auto_161055',
        'lead_checks': 'Read full review, coverage, summary and uncertainties. Independently inspected opening sheet with checked Auto,61-second ordinary Wailmer40/Geodude70 state,129-second visibly unchecked Auto with no Electrike Energy,130-second checked Auto and pending zone attachment,155-second Blastoise230/fourWater and Electrike60/oneLightning,163-second Electrike60/twoLightning after Cord,185-second Mega Manectric own-points scaling text,203-second Blastoise70/oneWater on Bench and unready Wailord250,250-second explicit owner+2 with three visible circles/opponentone,258.8-second explicit Victory with named computer deck.',
        'outcome': 'owner_win',
        'final_points': {'owner': 3, 'opponent': 1},
        'result_display': 'Win; 3-1 circles shown, final +2 award',
        'owner_visible_core': 'Alolan Geodude / Graveler / Golem; Electrike / Mega Manectric ex; Electrical Cord',
        'opponent': 'AI Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)',
        'last_turn': 14,
        'useful_finding': 'Electrical Cord adds one Lightning to the lone Benched Electrike after Graveler is knocked out, taking it from one Energy to two. Both Generators flip tails. Auto is visibly unchecked during those plays, so they are not attributed to the automatic policy. Mega Manectric scales damage from its own earned points.',
        'limitations': 'Root verification is bounded. The cause and exact timing of the Auto toggle, hidden hand and card print identifiers remain unknown. Explicit final+2 and three visible circles do not establish an internal total above three.',
    }
elif video == '20260930_161633000_iOS.MP4':
    consult = root / 'Recording_QA' / 'BATCH_2026-09-30' / 'ASTRA_ARENA_CHECK.md'
    if not consult.is_file():
        raise SystemExit('Completed source-bound Astra consultation required')
    (packet / 'ASTRA_CHECK.md').write_text(consult.read_text(encoding='utf-8-sig'), encoding='utf-8')
    review_path = packet / 'REVIEW.md'
    raw = review_path.read_text(encoding='utf-8-sig')
    (packet / 'FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md').write_text(raw, encoding='utf-8')
    revised = raw.replace('its printed basic-Pokemon damage bonus', 'its printed Fighting-Pokemon damage bonus')
    revised = revised.replace('attacks by Basic Pokemon do20more', 'attacks by Fighting Pokemon do20more')
    revised = revised.replace('Drilbur B is Basic, Bellibolt ex has70 remaining', 'Drilbur B is Fighting, Bellibolt ex has70 remaining')
    revised = revised.replace('**Conditional alternative:** playing that Stadium first appears, from its printed text and shown state, to raise this attack to70 and KO Bellibolt for two points.', '**Conditional alternative:** if Arena could be played before this attack and its printed effect applied, Headbutt Bounce would reach70 and KO the70-HP Bellibolt ex for two points.')
    revised += '\n\n## Astra consultation and lead clarification\n\nAstra independently checked the Stadium eligibility and conditional immediate knockout against retained source frames. Arena applies to Fighting Pokemon, represented by the fist symbol. Drilbur satisfies that condition; the conditional 70-damage prediction remains valid as a printed-text inference. The alternative was not executed and does not establish an eventual win or engine behavior. See `ASTRA_CHECK.md` and `LEAD_CORRECTION.md`.\n'
    review_path.write_text(revised, encoding='utf-8')
    (packet / 'LEAD_CORRECTION.md').write_text('''# Lead correction after Astra consultation

The unmodified worker report is preserved in `FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md`. Astra and the lead inspected the retained native-resolution Arena card at `targets/t0144.00.jpg` and its small fist symbol. Arena's eligibility is Fighting Pokemon, not all Basic Pokemon. Drilbur is Fighting, so the conditional immediate knockout calculation remains 30 base +20 weakness +20 Arena =70 versus Bellibolt ex70HP. No actual Stadium play, alternate result, eventual win or engine test is claimed. See `ASTRA_CHECK.md` for independently bounded evidence.
''', encoding='utf-8')
    data = {
        'scope': 'Complete nine-turn 169.925-second autopilot computer battle, setup through separate Riolu and Drilbur attacks, Bellibolt tool/coin effects, three knockouts and explicit Defeat',
        'first_pass': 'gpt-6.1-sol/high /root/sol_auto_161633',
        'lead_checks': 'Read full review, coverage, summary and uncertainties. Independently inspected opening Auto at10.5,39-second Riolu/oneFighting and distinct Scratch/Headbutt Bounce Drilbur versions,66-second Stage1+30HP tool caption,77-second Riolu60damage,144-second held Arena/Fighting symbol and Bellibolt70/Drilbur60,147-second Drilbur twoEnergy before Headbutt Bounce,157.5-second finalDrilbur0/Bellibolt20,169-second explicit Defeat/named computer deck. Astra independently checked Arena eligibility and conditional immediate knockout; original worker prose corrected and preserved.',
        'outcome': 'owner_loss',
        'final_points': {'owner': 0, 'opponent': 3},
        'owner_visible_core': 'Riolu; Scratch Drilbur / Headbutt Bounce Drilbur; Garchomp ex and Mega Lucario ex held',
        'opponent': 'AI Mega Manectric ex & Bellibolt ex Deck (Deluxe Pack: Mega)',
        'last_turn': 9,
        'useful_finding': 'Two different Drilbur versions deal different damage. Arena of Antiquity is drawn and held. Its visible Fighting bonus supports a conditional final attack of70 instead of the observed50 against Bellibolt ex70HP, which would produce an immediate knockout if played first under the shown conditions. That alternative was not executed and does not establish an eventual win.',
        'limitations': 'Root and Astra checks are bounded. The cape title, opening coin face and hidden cards remain unknown. The Arena alternative is a source-text prediction, not a verified alternate engine result.',
        'astra_consulted': True,
        'astra_reason': 'Conflicting Stadium eligibility claims and conditional missed-knockout interpretation independently resolved in ASTRA_CHECK.md',
    }
elif video == '20260930_162102000_iOS.MP4':
    consult = root / 'Recording_QA' / 'BATCH_2026-09-30' / 'ASTRA_ARENA_CHECK.md'
    if not consult.is_file():
        raise SystemExit('Completed source-bound Astra consultation required')
    (packet / 'ASTRA_CHECK.md').write_text(consult.read_text(encoding='utf-8-sig'), encoding='utf-8')
    review_path = packet / 'REVIEW.md'
    raw = review_path.read_text(encoding='utf-8-sig')
    (packet / 'FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md').write_text(raw, encoding='utf-8')
    revised = raw.replace('t0129.00.jpg130 damage; t0132.00.jpg60HP', 't0129.00.jpg Korrina Fighting bonus caption; t0132.00.jpg 130-damage popup; t0135.00.jpg settled60HP')
    revised = revised.replace('Helmet still returns20 damage after the knockout', 'Helmet\'s20 damage still resolves after the lethal hit and before the result screen')
    revised += '\n\n## Astra consultation and lead clarification\n\nAstra independently checked Arena Fighting eligibility, Korrina, the 130-damage attack, Helmet retaliation and the empty-field loss with only two opponent points. The evidence anchors were corrected: 129s shows the Korrina bonus caption,132s the130-damage popup, and135s settled60HP. See `ASTRA_CHECK.md` and `LEAD_CORRECTION.md`.\n'
    review_path.write_text(revised, encoding='utf-8')
    summary_path = packet / 'SUMMARY.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8-sig'))
    summary['anchors']['decisive'] = {'path': 'targeted/t0132.00.jpg', 'seconds': 132, 'observed': '130-damage popup; prior HP still animating from190; settled60 at135s'}
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (packet / 'LEAD_CORRECTION.md').write_text('''# Lead anchor clarification after Astra consultation

The unmodified worker report is preserved in `FIRST_PASS_REVIEW_BEFORE_LEAD_CORRECTION.md`. `targeted/t0129.00.jpg` shows Korrina's Fighting +30 caption. The explicit 130-damage popup is at `targeted/t0132.00.jpg`, and settled Mega Manectric60HP is at `targeted/t0135.00.jpg`. The timeline evidence labels and decisive summary anchor now reflect those actual frames. The attack arithmetic and observed loss remain unchanged. Astra also confirmed Arena's Fighting symbol, which agrees with this worker's eligibility wording, and bounded the Helmet/empty-field conclusions. See `ASTRA_CHECK.md`.
''', encoding='utf-8')
    data = {
        'scope': 'Complete seven-turn 157.04-second autopilot computer battle, setup through Copycat draws, tools, healing, Stadium/Supporter damage, Helmet retaliation, empty-field loss and explicit Defeat',
        'first_pass': 'gpt-6.1-sol/high /root/sol_auto_162102',
        'lead_checks': 'Read full review, coverage, summary and uncertainties. Independently inspected complete opening AI/second/Auto sheet,65-second ordinary Heliolisk/Mega Manectric development and sole ownerPassimian,98-second Stage1+30HP/210 tool effect and Helmet text,123-second Arena in play,126-second Korrina use,129-second Fighting+30 caption,132-second explicit130-damage popup,144-second owner0HP with Helmet resolving,147-second owneremptyfield/Mega40,150-second opponent+2 and finalvisible1-2,152-second explicitDefeat. Astra independently checked Stadium/Supporter eligibility, damage and bounded post-KO Helmet/terminal conclusions; misleading time anchors corrected.',
        'outcome': 'owner_loss',
        'final_points': {'owner': 1, 'opponent': 2},
        'result_display': 'Loss 1-2; no Pokemon remaining',
        'owner_visible_core': 'Passimian ex / Rocky Helmet; Mega Lucario ex and Gabite held',
        'opponent': 'AI; visible Heliolisk / Mega Manectric ex / Bellibolt ex',
        'last_turn': 7,
        'useful_finding': 'Arena, Korrina and weakness raise Seismic Toss from60 to130, but the boosted Mega Manectric survives at60HP. Its next80damage knocks out the sole Passimian; Helmet still reduces the attacker to40. The owner loses with1-2 points because no Pokemon remains in play.',
        'limitations': 'Root and Astra verification is bounded. Exact cape title and terminal named deck/rewards page are absent or unreadable. The recorded Helmet retaliation and final empty field do not establish every engine queue detail or generalized rule priority.',
        'astra_consulted': True,
        'astra_reason': 'Conflicting Stadium eligibility, damage anchors and consequential terminal Helmet/empty-field interpretation independently checked in ASTRA_CHECK.md',
    }
else:
    raise SystemExit('Acceptance instructions must be added after packet and source checks')
data.update({
    'accepted': True,
    'decision': 'accepted_full_battle_review',
    'source_video': video,
    'source_sha256': binding['sha256'],
    'unreviewed_intervals': [],
    'material_unresolved': [],
    'ladder_eligible': False,
    'ladder_action': 'No Ladder Log entry; excluded by owner instruction',
})
data.setdefault('astra_consulted', False)
data.setdefault('astra_reason', 'Readable targeted card, coin and settled-state frames resolved consequential interactions; unexposed information remains explicitly unknown')
if data['astra_consulted']:
    summary_path = packet / 'SUMMARY.json'
    summary = json.loads(summary_path.read_text(encoding='utf-8-sig'))
    summary['lead_astra_consultation'] = {'consulted': True, 'model': 'gpt-6-astra/high', 'scope': 'Bounded Arena eligibility, damage/counterfactual and terminal Helmet interpretation', 'evidence': 'ASTRA_CHECK.md'}
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
(packet / 'LEAD_ACCEPTANCE.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
print('Lead accepted:', video)

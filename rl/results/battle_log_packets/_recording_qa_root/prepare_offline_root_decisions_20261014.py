"""Root's actual completed timeline reads and direct source observations."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BATCH = ROOT / 'Recording_QA/BATCH_2026-10-14_OFFLINE_LADDER_FOUR'
CONFIG = {
 '20261014_164328000_iOS': {
    'opponent': 'Roncaufeu', 'opponent_deck': 'Chien-Pao ex / Baxcalibur / Suicune ex', 'result': 'loss',
    'note_prefix': '2nd | Whimsicott ex T2 | opp 1 pt',
    'note': '2nd | Whimsicott ex T2 | opp 1 pt | vs Roncaufeu | recorded 2026-10-14 11:43:28 CDT | 20261014_164328000_iOS.MP4 | Defeat 2-3 at06:51.5; Diving Icicles KO benched Whimsicott ex.',
    'scope': 'Whole one-game ladder source, all7 turns and terminal defeat; visible core fits Deck12; independent source checks and root reconciliation of local Downloads copy.',
    'registration_notes': 'Owner authorized offline review. Visible Ariados/Whimsicott/Ogerpon core fits Deck12; selected label not directly shown. Loss2-3 versus Roncaufeu; second; Whimsicott ex first Grass Knot ownT2/global4, opponent1 before. Earlier Cottonee attack is supporting. OwnerT3 end tap versus timeout stays uncertain. Canonical cloud copy unverified and cloud work deferred.',
    'observations': [
       ('evidence/t0030.00.jpg', 'Opening explicitly shows going second.'),
       ('evidence/t0145.00.jpg', 'Your turn Current turn4, ownT2 for second player; Roncaufeu1point.'),
       ('evidence/t0184.00.jpg', 'Whimsicott ex first Grass Knot130 selection, opponent1point before, two Baxcalibur Bench and Chien-Pao ex130HP Active.'),
       ('evidence/t0186.00.jpg', 'Named Whimsicott ex Grass Knot attack, opponent1point.'),
       ('evidence/t0282.00.jpg', 'Owner Ariados, Cottonee and Ogerpon Bench with Whimsicott Active; visible core matches Deck12. Opponent Baxcalibur and Chien-Pao ex visible.'),
       ('evidence/t0411.50.jpg', 'Defeat versus Roncaufeu;went second;7turns;owner2/opponent3;150damage;Whimsicott ex Card of the Game.'),
    ]},
 '20261014_163325000_iOS': {
    'opponent': 'Shotgun', 'opponent_deck': 'Castform Sunny Form / Torchic / Mega Blaziken ex', 'result': 'loss',
    'note_prefix': '1st | Whimsicott ex no attack | opp pts N/A',
    'note': '1st | Whimsicott ex no attack | opp pts N/A | vs Shotgun | recorded 2026-10-14 11:33:25 CDT | 20261014_163325000_iOS.MP4 | Defeat 1-3 at09:37; Mega Blaziken ex terminal KO. Supporting Ogerpon T3, Ariados T6.',
    'scope': 'Whole one-game ladder source, all12 turns and terminal defeat; main attacker never attacks; local source, independent checking and root source-checked addendum.',
    'registration_notes': 'Owner authorized offline review. Deck12 loss1-3 versus Shotgun; first; Whimsicott ex stays benched after evolving ownT5 and never attacks, so timing/points are N/A. Supporting OgerponT3 and AriadosT6 remain separate. Root addendum corrects season label to B4b SP and Card of the Game to Ogerpon ex, without changing log facts; frozen primary retained. Canonical cloud copy unverified and cloud reconciliation deferred.',
    'clarifications': ['LEAD_CLARIFICATION.md supersedes B46 with B4b SP and Castform Card of the Game with Teal Mask Ogerpon ex; original frozen account stays intact.'],
    'observations': [
       ('native/t0002.50.jpg', 'Season B4b SP, Ultra Ball Rank4 700pts and Deck12; corrects primary season label.'),
       ('native/t0032.50.jpg', 'Opening explicitly shows owner going first.'),
       ('final_checks/t0356.00.jpg', 'Whimsicott ex evolves on Bench, with Ariados Active on ownerT5.'),
       ('native/t0554.00.jpg', 'Cyrus has brought Ogerpon40HP Active; Whimsicott ex140HP remains Bench; Shotgun2points before last attack.'),
       ('native/t0565.00.jpg', 'Terminal points owner1/Shotgun3 after +2 award.'),
       ('native/t0577.00.jpg', 'Defeat versus Shotgun; went first,12turns,1-3,90damage; Ogerpon ex Card of the Game.'),
    ]},
 '20261014_160506000_iOS': {
    'opponent': 'Odin', 'opponent_deck': 'Tapu Koko ex / Oricorio', 'result': 'loss',
    'note_prefix': '2nd | Whimsicott ex T4 | opp 2 pts',
    'note': '2nd | Whimsicott ex T4 | opp 2 pts | vs Odin | recorded 2026-10-14 11:05:06 CDT | 20261014_160506000_iOS.MP4 | Defeat 2-3 at07:16; Oricorio Zzzap terminal KO.',
    'scope': 'Whole one-game ladder source, all13 global turns and terminal defeat; local Downloads source accepted with separate source checks and root reconciliation.',
    'registration_notes': 'Owner authorized offline local review. Deck12 loss2-3 versus Odin; second; Whimsicott ex first Grass Knot ownT4/global8, opponent2 before. Early Ogerpon attacks remain supporting. Primary short prefix reformatted with explicit main attacker and points. Canonical cloud copy not verified; local staging archive and later cloud reconciliation remain separate.',
    'observations': [
       ('gaps/t0002.00.jpg', 'Ranked Season B4b SP, Ultra Ball Rank4 700pts and Deck12 selection visible.'),
       ('native/t0027.00.jpg', 'Opening explicitly shows owner going second.'),
       ('detail/t0278.00.jpg', 'Your turn Current turn8, ownT4 for second player; Odin2points.'),
       ('native/t0290.00.jpg', 'Whimsicott ex Active with two Grass, Odin2points and Tapu Koko ex10HP before first main attack.'),
       ('detail/t0291.00.jpg', 'Named Whimsicott ex Grass Knot attack, Odin2points visible.'),
       ('native/t0424.00.jpg', 'Terminal board shows owner2 and Odin3points.'),
       ('native/t0436.00.jpg', 'Defeat versus Odin; opponent Tapu Koko ex Card of the Game.'),
    ]},
 '20261014_161324000_iOS': {
    'opponent': 'ヤンチャ', 'opponent_deck': 'Charmander / Charmeleon / Charizard', 'result': 'loss',
    'note_prefix': '1st | Whimsicott ex T4 | opp 2 pts',
    'note': '1st | Whimsicott ex T4 | opp 2 pts | vs ヤンチャ | recorded 2026-10-14 11:13:24 CDT | 20261014_161324000_iOS.MP4 | Defeat 1-3 at05:25.5; Charizard terminal KO after Sabrina.',
    'scope': 'Whole one-game ladder source, all8 turns and terminal defeat; local Downloads source accepted with separate source checks and root reconciliation.',
    'registration_notes': 'Owner authorized offline local review. Visible Deck12, loss1-3 versus ヤンチャ; first; Whimsicott ex first Grass Knot ownT4/global7 with opponent2 before. Early Ariados Pierce ownT2 is supporting; Ogerpon only appears in deck setup. Exact queue-selection screen unrecorded, no Auto seen. Canonical cloud copy unverified; local archive and future cloud reconciliation separate.',
    'observations': [
       ('native/t0002.00.jpg', 'Deck12 directly named, visible Spinarak/Ariados/Cottonee/Whimsicott ex/Ogerpon ex core, Grass energy.'),
       ('native/t0022.00.jpg', 'Opening explicitly shows going first.'),
       ('native/t0266.00.jpg', 'First Grass Knot100 selection with Active Whimsicott ex, opponent ヤンチャ2points beforehand and80HP Charmeleon target.'),
       ('native/t0268.50.jpg', 'Named Whimsicott ex Grass Knot attack, opponent2points.'),
       ('native/t0325.50.jpg', 'Defeat versus ヤンチャ; went first;8combined turns;owner1/opponent3;130damage.'),
    ]},
}

for stem, config in CONFIG.items():
    packet = BATCH / stem
    output = packet / 'ROOT_DECISION.json'
    if output.exists():
        continue
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
    summary = json.loads((packet / 'SUMMARY.json').read_text(encoding='utf-8-sig'))
    decision = dict(config)
    decision.update({'source_filename': source['video_basename'], 'source_sha256': source['sha256'],
         'primary_note_prefix': summary['exact_three_item_note_prefix'], 'checked_utc': datetime.now(timezone.utc).isoformat(),
         'lead': '/root', 'battle_complete': True, 'root_read_full_timeline_and_coverage': True,
         'auto_option_seen': False, 'clarifications': config.get('clarifications', []), 'section': 'd12',
         'deck_name': 'Ariados / Whimsicott / Ogerpon', 'energy': 'Grass'})
    decision['observations'] = [{'path': path, 'finding': finding, 'directly_viewed_by_root': True} for path, finding in config['observations']]
    output.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output, flush=True)

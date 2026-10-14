#!/usr/bin/env python3
"""make_audited_games.py: writes audited_games.json, the list tools/battle_logs_cleanup.py reads as "a person has accepted that the positions of this game passed review".

  python3 make_audited_games.py [--ref origin/main]     (run from anywhere; reads the committed games_meta.json files at the ref)

This is PROPOSED by Sonnet (Oct 14) from the records on main; it decides nothing until the laptop (or Fable, or Dustin) records `confirmed` in the file and commits it. Two tiers:
  games   (deletable once confirmed): the 28 games of rl/results/pause_games_new_2026-10-12/games_meta.json (BATCH_2026-10-06, -09 and -11): the laptop's first panel read all three batches
          against Codex's ledgers (REVIEW_POSITIONS_laptop.md, e9a7d35e: not ready), Sonnet's converter fix was then verified by the laptop's two panels (2eff1be6, 43b7d71d: every first-panel
          error fixed, byte-for-byte regeneration) and the positions were checked again after the Special Condition / knock-out change (28df6315, REVIEW_PGFIX_laptop.md: the 125 positions
          regenerate identical). These are the positions the kx3 study ran on.
  pending (NOT deletable): the 14 games of rl/results/pause_games_new_2026-10-13/v2/games_meta.json (BATCH_2026-10-12 x2, BATCH_2026-10-13 x2): Sonnet's v2 read and the converter's checkup
          fix are integrated by the laptop (fb43ab9e, feddbce6, f6be4fd7), but no panel compared those 92 positions with their ledgers field by field. Move an entry to `games` when
          the laptop accepts it."""
import argparse, json, os, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audited_games.json')
TIER_A = 'rl/results/pause_games_new_2026-10-12/games_meta.json'
TIER_B = 'rl/results/pause_games_new_2026-10-13/v2/games_meta.json'


def show(ref, path):
    return json.loads(subprocess.run(['git', '-C', ROOT, 'show', f'{ref}:{path}'], capture_output=True, text=True, check=True).stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='origin/main')
    a = ap.parse_args()
    games = {k: {'folder': v['folder'], 'tier': 'A',
                 'evidence': ['e9a7d35e (laptop panel 1, Oct 12: errors found)', '43b7d71d + 2eff1be6 (laptop panel 2: every error fixed, byte-for-byte regeneration; integrated)',
                              '28df6315 (REVIEW_PGFIX_laptop.md, Oct 13: the 125 positions regenerate identical)']}
             for k, v in sorted(show(a.ref, TIER_A).items())}
    pending = {k: {'folder': v['folder'], 'tier': 'B',
                   'why': 'read and integrated by the laptop (fb43ab9e, feddbce6, f6be4fd7) but no panel compared these positions with the ledgers field by field'}
               for k, v in sorted(show(a.ref, TIER_B).items())}
    doc = {
        'schema': 'battle-logs-retention/audited-games-v1',
        'confirmed': None,
        'confirmed_help': 'A person writes here who accepted the list and when (for example "laptop, 2026-10-14") and commits it to main; tools/battle_logs_cleanup.py --apply refuses while this is empty.',
        'proposed_by': 'Sonnet (Opus agents progress), 2026-10-14, from the records on main; see make_audited_games.py for the evidence per tier',
        'games': games,
        'pending': pending,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'{len(games)} games (tier A), {len(pending)} pending (tier B) -> {OUT}')


if __name__ == '__main__':
    main()

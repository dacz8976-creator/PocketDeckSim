#!/usr/bin/env python3
"""make_audited_games.py: writes audited_games.json, the list tools/battle_logs_cleanup.py reads as "a person has accepted that the positions of this game passed review".

  python3 make_audited_games.py [--ref origin/main]     (run from anywhere; reads the committed games_meta.json and positions_all.json files at the ref)

This is PROPOSED by Sonnet (Oct 14) from the records on main; it decides nothing until a person writes an acceptance into it and commits it: "confirmed": {"by": ..., "date": "YYYY-MM-DD", "games_sha256": ...},
where games_sha256 is what `python3 tools/battle_logs_cleanup.py --audit-hash` prints for the games listed then (a later edit to `games` invalidates the acceptance). Two tiers:
  games   (deletable once accepted): the games of rl/results/pause_games_new_2026-10-12/games_meta.json (BATCH_2026-10-06, -09 and -11) THAT HAVE POSITIONS in the positions_all.json beside it: the laptop's first panel read
          all three batches against Codex's ledgers (REVIEW_POSITIONS_laptop.md, e9a7d35e: not ready), Sonnet's converter fix was then verified by the laptop's two panels (2eff1be6, 43b7d71d: every first-panel error
          fixed, byte-for-byte regeneration) and the positions were checked again after the Special Condition / knock-out change (28df6315, REVIEW_PGFIX_laptop.md: the 125 positions regenerate identical). Each entry
          names the games_meta file, the number of positions and the sha256 of those positions (the content that was reviewed); the tool holds the game back if any of them changes.
  pending (NOT deletable): (a) the games of the same games_meta WITHOUT positions (214518, 214731, 034229, 012140: Codex found no exact 20-card list), which that review cannot cover; (b) the 14 games of
          rl/results/pause_games_new_2026-10-13/v2/games_meta.json (BATCH_2026-10-12 x2, BATCH_2026-10-13 x2): integrated by the laptop (fb43ab9e, feddbce6, f6be4fd7), but no panel had compared those 92 positions
          with their ledgers field by field. Move an entry to `games` (with the reviewed games_meta, positions and positions_sha256: re-run this script) when a person accepts it."""
import argparse, collections, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import battle_logs_cleanup as bl            # the digest of a game's positions is the tool's own, so the list and the tool agree on it

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audited_games.json')
TIER_A = 'rl/results/pause_games_new_2026-10-12/games_meta.json'
TIER_B = 'rl/results/pause_games_new_2026-10-13/v2/games_meta.json'


def show(ref, path):
    return json.loads(subprocess.run(['git', '-C', ROOT, 'show', f'{ref}:{path}'], capture_output=True, text=True, check=True).stdout)


def counts(ref, meta_path):
    """-> ({game: number of positions}, {game: sha256 of its positions as they are in positions_all.json})"""
    by_game = collections.defaultdict(list)
    for p in show(ref, meta_path.rsplit('/', 1)[0] + '/positions_all.json'):
        by_game[p.get('game')].append(p)
    return {k: len(v) for k, v in by_game.items()}, {k: bl.positions_digest(v) for k, v in by_game.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='origin/main')
    a = ap.parse_args()
    meta_a, (pos_a, dig_a) = show(a.ref, TIER_A), counts(a.ref, TIER_A)
    meta_b, (pos_b, _) = show(a.ref, TIER_B), counts(a.ref, TIER_B)
    games, pending = {}, {}
    for k, v in sorted(meta_a.items()):
        if pos_a.get(k):
            games[k] = {'folder': v['folder'], 'games_meta': TIER_A, 'positions': pos_a[k], 'positions_sha256': dig_a[k], 'tier': 'A',
                        'evidence': ['e9a7d35e (laptop panel 1, Oct 12: errors found)', '43b7d71d + 2eff1be6 (laptop panel 2: every error fixed, byte-for-byte regeneration; integrated)',
                                     '28df6315 (REVIEW_PGFIX_laptop.md, Oct 13: the 125 positions regenerate identical)']}
        else:
            pending[k] = {'folder': v['folder'], 'games_meta': TIER_A, 'tier': 'A0',
                          'why': 'no positions to review: Codex found no exact 20-card list, so the converter produced none and the review of the 125 positions cannot cover this game'}
    for k, v in sorted(meta_b.items()):
        pending[k] = {'folder': v['folder'], 'games_meta': TIER_B, 'positions': pos_b.get(k, 0), 'tier': 'B',
                      'why': 'read and integrated by the laptop (fb43ab9e, feddbce6, f6be4fd7) but no panel compared these positions with the ledgers field by field'}
    doc = {
        'schema': 'battle-logs-retention/audited-games-v3',
        'confirmed': None,
        'confirmed_help': 'A person writes here {"by": "<a name>", "date": "YYYY-MM-DD", "games_sha256": "<what `wsl python3 tools/battle_logs_cleanup.py --audit-hash` prints>"} and commits it to main and pushes; tools/battle_logs_cleanup.py --apply refuses while it is missing, malformed, or no longer matches `games`.',
        'proposed_by': 'Sonnet (Opus agents progress), 2026-10-14, from the records on main; see make_audited_games.py for the evidence per tier',
        'games': games,
        'pending': pending,
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'{len(games)} games with positions (tier A), {len(pending)} pending ({sum(1 for p in pending.values() if p["tier"] == "A0")} without positions, {sum(1 for p in pending.values() if p["tier"] == "B")} of tier B) -> {OUT}')


if __name__ == '__main__':
    main()

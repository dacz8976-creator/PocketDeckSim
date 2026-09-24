#!/usr/bin/env python3
"""Validate sweep inputs and recorded game counts; never modify experiment evidence."""
import argparse
import json
import math
from pathlib import Path
import re
import sys


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def records(path):
    if not path or not Path(path).exists():
        return []
    result = []
    text = Path(path).read_text()
    if text and not text.endswith('\n'):
        raise ValueError('output has an unterminated last record; inspect before resuming')
    for line_no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line, object_pairs_hook=unique_object,
                             parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except ValueError as exc:
            raise ValueError(f"output line {line_no}: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"output line {line_no}: expected an object")
        result.append(row)
    return result


def job_rows(path):
    result = {}
    rows = []
    basenames = {}
    for line_no, line in enumerate(Path(path).read_text().splitlines(), 1):
        if not line.strip():
            continue
        fields = line.split('\t')
        if len(fields) != 3 or not all(fields):
            raise ValueError(f"jobs line {line_no}: expected exactly three nonempty fields")
        ident, a, b = fields
        if ident in result or ident == '__sentinel__':
            raise ValueError(f"jobs line {line_no}: duplicate or reserved id {ident}")
        for value in fields:
            if any(ord(c) < 32 or c in '\\"' for c in value):
                raise ValueError(f"jobs line {line_no}: unsupported control/JSON escape characters")
        for value in (a, b):
            deck = Path(value)
            if not deck.is_file():
                raise ValueError(f"jobs line {line_no}: missing deck {value}")
            resolved = deck.resolve()
            if deck.name in basenames and basenames[deck.name] != resolved:
                raise ValueError(f"jobs line {line_no}: deck basename collision {deck.name}")
            basenames[deck.name] = resolved
        result[ident] = (Path(a).name.removesuffix('.txt'), Path(b).name.removesuffix('.txt'))
        rows.append((ident, a, b))
    if not result:
        raise ValueError("jobs file is empty")
    return rows


def jobs(path):
    return {ident: (Path(a).name.removesuffix('.txt'), Path(b).name.removesuffix('.txt')) for ident, a, b in job_rows(path)}


def outcome_counts(row, games):
    values = [row.get(key) for key in ('w0', 'w1', 'draws')]
    if any(type(value) is not int or value < 0 for value in values):
        raise ValueError("outcomes must be nonnegative integers")
    if sum(values) != games:
        raise ValueError(f"outcomes sum to {sum(values)}, expected {games}")


def validate(rows, expected, games, players, seed_stream):
    if games < 1:
        raise ValueError("games must be positive")
    seen = set()
    for row in rows:
        ident = row.get('id')
        if not isinstance(ident, str) or ident not in expected:
            raise ValueError(f"unexpected output id: {ident!r}")
        if ident in seen:
            raise ValueError(f"duplicate output id: {ident}")
        seen.add(ident)
        if row.get('status') not in ('ok', 'error'):
            raise ValueError(f"{ident}: unrecognized record status")
        if row['status'] == 'error':
            continue
        if (row.get('a'), row.get('b')) != expected[ident]:
            raise ValueError(f"{ident}: deck pairing disagrees with jobs")
        if type(row.get('n')) is not int or row['n'] != games:
            raise ValueError(f"{ident}: game count disagrees with requested protocol")
        if row.get('players') != players or str(row.get('seed_stream', '')) != seed_stream:
            raise ValueError(f"{ident}: players/seed stream disagree with requested protocol")
        outcome_counts(row, games)
        for key in ('turns', 'plys', 'degrees', 'secs'):
            value = row.get(key)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{ident}: invalid {key}")


def parse_summary(text, games):
    if games < 1:
        raise ValueError("games must be positive")
    text = text.replace('\r\n', '\n')
    result = {}
    number = r"[-+]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?"
    # DeckGym uses English thousands separators for outcome counts. Match the
    # complete token so malformed counts cannot be silently truncated to a prefix.
    count = r"(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)"
    patterns = {
        'turns': rf'^(?:Average number of|avg) turns per game:\s*({number})\s*$',
        'plys': rf'^(?:Average number of|avg) plys per game:\s*({number})\s*$',
        'degrees': rf'^(?:Average number of|avg) degrees per ply:\s*({number})\s*$',
        'w0': rf'^Player 0 won:?\s+({count})(?:\s+.*)?$',
        'w1': rf'^Player 1 won:?\s+({count})(?:\s+.*)?$',
        'draws': rf'^Draws:\s+({count})(?:\s+.*)?$',
    }
    labels = {
        'turns': r'^(?:Average number of|avg) turns per game:',
        'plys': r'^(?:Average number of|avg) plys per game:',
        'degrees': r'^(?:Average number of|avg) degrees per ply:',
        'w0': r'^Player 0 won\b', 'w1': r'^Player 1 won\b', 'draws': r'^Draws:',
    }
    for key, pattern in patterns.items():
        if len(re.findall(labels[key], text, re.MULTILINE)) != 1:
            raise ValueError(f'expected exactly one summary field: {key}')
        matches = re.findall(pattern, text, re.MULTILINE)
        if len(matches) != 1:
            raise ValueError(f"expected exactly one summary field: {key}")
        result[key] = int(matches[0].replace(',', '')) if key in ('w0', 'w1', 'draws') else float(matches[0])
        if not math.isfinite(result[key]) or result[key] < 0:
            raise ValueError(f"invalid summary field: {key}")
    outcome_counts(result, games)
    reported_games = re.findall(rf'^Ran ({count}) simulations\b', text, re.MULTILINE)
    if len(reported_games) > 1 or (reported_games and int(reported_games[0].replace(',', '')) != games):
        raise ValueError("reported simulation total disagrees with requested games")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('jobs', 'rows', 'paths', 'check', 'ids', 'counts', 'ok-records', 'summary'))
    parser.add_argument('--jobs')
    parser.add_argument('--output')
    parser.add_argument('--games', type=int, default=200)
    parser.add_argument('--players', default='k3,k3')
    parser.add_argument('--seed-stream', default='')
    args = parser.parse_args()
    try:
        if args.mode == 'jobs':
            jobs(args.jobs)
        elif args.mode == 'rows':
            for row in job_rows(args.jobs):
                print('\t'.join(row))
        elif args.mode == 'paths':
            for path in sorted({p for _, a, b in job_rows(args.jobs) for p in (a, b)}):
                print(path)
        elif args.mode == 'ok-records':
            for row in records(args.output):
                if row['status'] == 'ok':
                    print(json.dumps(row, separators=(',', ':'), allow_nan=False))
        elif args.mode == 'check':
            validate(records(args.output), jobs(args.jobs), args.games, args.players, args.seed_stream)
        elif args.mode == 'summary':
            row = parse_summary(sys.stdin.read(), args.games)
            print('\t'.join(str(row[k]) for k in ('turns', 'plys', 'degrees', 'w0', 'w1', 'draws')))
        elif args.mode == 'ids':
            for row in records(args.output):
                print(row['id'])
        else:
            rows = records(args.output)
            print(sum(r['status'] == 'ok' for r in rows), sum(r['status'] == 'error' for r in rows))
    except (ValueError, OSError, TypeError, KeyError, OverflowError) as exc:
        print(f'REFUSED run evidence: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

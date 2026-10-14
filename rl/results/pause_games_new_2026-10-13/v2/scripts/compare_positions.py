#!/usr/bin/env python3
"""compare_positions.py OLD.json NEW.json [OUT.txt]: which positions changed between two regenerations of positions_all.json, and where.

One block per changed position: the path of every field that differs (`me.hand`, `opp.board[0].card`, `his_plan`, ...) with the old and the new value (long values cut), then a count by field.
The notes of a position are compared without the text that only says which ledger corrections were applied. Used for the v3 regeneration (the laptop's review of the 92 positions)."""
import collections, json, sys


def walk(a, b, path, out):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append((f'{path}.{k}' if path else k, '(absent)', b[k]))
            elif k not in b:
                out.append((f'{path}.{k}' if path else k, a[k], '(absent)'))
            else:
                walk(a[k], b[k], f'{path}.{k}' if path else k, out)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and any(isinstance(x, (dict, list)) for x in a):
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f'{path}[{i}]', out)
    elif a != b:
        out.append((path, a, b))


def short(v, n=140):
    s = json.dumps(v, ensure_ascii=False) if not isinstance(v, str) else v
    return s if len(s) <= n else s[:n] + '...'


def main(old_path, new_path, out_path=None):
    with open(old_path, encoding='utf-8') as f:
        old = {p['id']: p for p in json.load(f)}
    with open(new_path, encoding='utf-8') as f:
        new = {p['id']: p for p in json.load(f)}
    lines = []
    by_field = collections.Counter()
    changed = 0
    for pid in sorted(set(old) | set(new)):
        if pid not in old or pid not in new:
            lines.append(f'{pid}: {"only in the new set" if pid in new else "only in the old set"}')
            changed += 1
            continue
        diffs = []
        walk(old[pid], new[pid], '', diffs)
        diffs = [d for d in diffs if not (d[0] == 'notes' and 'ledger corrected from the frames' in str(d[2]))] + \
                [d for d in diffs if d[0] == 'notes' and 'ledger corrected from the frames' in str(d[2])]
        if not diffs:
            continue
        changed += 1
        lines.append(f'{pid}')
        for path, a, b in diffs:
            root = path.split('.')[0].split('[')[0]
            key = root if root not in ('me', 'opp') else '.'.join(path.replace('[', '.[').split('.')[:2]).split('[')[0] if '.' in path else root
            by_field[key] += 1
            lines.append(f'   {path}: {short(a)}  ->  {short(b)}')
    lines.append('')
    lines.append(f'{changed} of {len(old)} positions changed ({len(old) - changed} identical)')
    for k, n in by_field.most_common():
        lines.append(f'   {k}: {n}')
    text = '\n'.join(lines) + '\n'
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == '__main__':
    main(*sys.argv[1:4])

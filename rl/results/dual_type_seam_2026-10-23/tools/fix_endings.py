#!/usr/bin/env python3
"""Restore each edited file's original line endings, line by line, against a git base.

usage: fix_endings.py REPO BASE [--check] PATH...

For every PATH (relative to REPO) that exists at BASE, the working file is matched line by line against BASE's copy
(content compared with the ending stripped). Unchanged lines get BASE's exact ending back; new or changed lines take
the ending of the BASE line they replace, else of the nearest BASE line above, else the file's majority ending.
A file absent at BASE is left alone (reported as NEW). --check reports what would change and writes nothing.
The repo's .gitattributes is `* -text`, so endings are content: an edit tool must never flip them.
"""
import difflib, subprocess, sys
from collections import Counter


def split_keep(b):
    lines = b.split(b'\n')
    out = []
    for i, l in enumerate(lines):
        last = i == len(lines) - 1
        if last:
            if l:
                out.append((l[:-1], b'\r') if l.endswith(b'\r') else (l, b''))
            break
        if l.endswith(b'\r'):
            out.append((l[:-1], b'\r\n'))
        else:
            out.append((l, b'\n'))
    return out


def main():
    args = sys.argv[1:]
    check = '--check' in args
    args = [a for a in args if a != '--check']
    repo, base, paths = args[0], args[1], args[2:]
    for p in paths:
        r = subprocess.run(['git', '-C', repo, 'show', f'{base}:{p}'], capture_output=True)
        if r.returncode != 0:
            print(f'NEW  {p} (not at {base}; left as written)')
            continue
        old = split_keep(r.stdout)
        cur_bytes = open(f'{repo}/{p}', 'rb').read()
        new = split_keep(cur_bytes)
        maj = Counter(e for _, e in old if e).most_common(1)
        maj = maj[0][0] if maj else b'\n'
        sm = difflib.SequenceMatcher(None, [t for t, _ in old], [t for t, _ in new], autojunk=False)
        out = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    t, e_old = old[i1 + k]
                    _, e_new = new[j1 + k]
                    # keep the old ending, except a final line whose newline was added or removed on purpose
                    out.append((t, e_old if (e_old and e_new) or (not e_old and not e_new) else e_new or e_old))
            elif tag in ('replace', 'insert'):
                for k in range(j2 - j1):
                    t, e_new = new[j1 + k]
                    if not e_new:
                        out.append((t, b''))
                        continue
                    if tag == 'replace' and i1 + k < i2:
                        e = old[i1 + k][1] or maj
                    elif i1 > 0:
                        e = old[i1 - 1][1] or maj
                    else:
                        e = maj
                    out.append((t, e))
        fixed = b''.join(t + e for t, e in out)
        if fixed == cur_bytes:
            print(f'OK   {p}')
            continue
        flips = sum(1 for (t1, e1), (t2, e2) in zip(new, out) if e1 != e2)
        print(f'{"WOULD FIX" if check else "FIXED"} {p}: {flips} line endings restored')
        if not check:
            open(f'{repo}/{p}', 'wb').write(fixed)


if __name__ == '__main__':
    main()

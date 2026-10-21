#!/usr/bin/env python3
"""Weekly look at bcollazo/deckgym-core (upstream): what is new since the last look, and is any of it worth taking?  Read-only: it only fetches public git data.

  python3 tools/upstream_watch.py             report on everything new since rl/upstream_watch/LAST_CHECKED.txt (fetches upstream's main first)
  python3 tools/upstream_watch.py --mark      the same, then record upstream's tip in LAST_CHECKED.txt (do this after reading, so next week starts there)
  python3 tools/upstream_watch.py --since 9044ff6   look from another commit (nothing is recorded)

One line per upstream change (a merged pull request, or a direct commit on main), oldest first: number, date, author, title, the files it touches by kind, new cards, and the names of cards from OUR
decks (decks/dustin, the 8 panel lists in decks/screen/opponents, decks/brews) that the change mentions. The last column is a hint:
  LOOK      new cards in the data, or an engine change that mentions a card we play, or an engine change whose title says it fixes something
  maybe     an engine change that mentions none of our cards (rules code, abilities, move generation...)
  skip      only bots, replay viewer, Python bindings, docs, CI or dependencies
It never opens, comments on or pushes to upstream. The first run clones upstream into ~/upstream_watch/deckgym-core (a blobless clone, under 100 MB).
What makes a change worth taking is in rl/results/upstream_compare_2026-10-16/README.md ("Keeping up").
"""
import argparse, datetime, json, os, re, subprocess, sys, unicodedata

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
URL = 'https://github.com/bcollazo/deckgym-core.git'
DEFAULT_CLONE = os.path.expanduser('~/upstream_watch/deckgym-core')
STATE_REL = ('rl', 'upstream_watch', 'LAST_CHECKED.txt')
DECK_DIRS = ['decks/dustin', 'decks/screen/opponents', 'decks/brews', 'decks/brews/drafts_2026-10-01']
# paths that are not game rules: bots, replay viewer, bindings, terminal UI, optimiser, docs, build files
TOOLING = ('src/players/', 'src/replay/', 'src/tui/', 'src/python_bindings.rs', 'src/perf_watch.rs', 'src/simulate.rs', 'src/optimize.rs', 'src/temp_deck.rs', 'src/bin/', 'python/', 'docs/',
           'benches/', 'examples/', 'images/', '.github/', 'Cargo.toml', 'Cargo.lock', 'Makefile', 'README.md', 'CLAUDE.md', 'CONTRIBUTING.md', 'pyproject.toml')
GENERATED = ('src/database.rs', 'src/card_ids.rs')   # produced from database.json: not read for card names
MIN_NAME = 6   # shorter card names (Misty, Cyrus, Erika...) match too much by accident; the report says when a deck has such names


def git(clone, *args, check=True):
    r = subprocess.run(['git', '-C', clone, *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and r.returncode:
        raise SystemExit(f'git {" ".join(args)} failed: {r.stderr.strip()[:300]}')
    return r.stdout


def norm(s):
    """Letters and digits only, lower case, accents folded: 'PokÃ© Ball' and 'PokeBall' (as in CardId names) are alike."""
    return re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower())


def deck_card_names(repo):
    names = {}
    for d in DECK_DIRS:
        p = os.path.join(repo, *d.split('/'))
        if not os.path.isdir(p):
            continue
        for f in sorted(os.listdir(p)):
            if not f.endswith('.txt'):
                continue
            with open(os.path.join(p, f), encoding='utf-8-sig', errors='replace') as fh:
                for line in fh:
                    w = line.split()
                    if len(w) >= 4 and w[0].isdigit():
                        names.setdefault(' '.join(w[1:-2]), set()).add(f[:-4])
    return names


def classify_path(p):
    if p == 'database.json':
        return 'data'
    if p.startswith(GENERATED):
        return 'generated'
    if p.startswith('tests/'):
        return 'tests'
    if p.startswith('src/') and not p.startswith(TOOLING):
        return 'engine'
    return 'tooling'


def parse_message(subject, body):
    m = re.match(r'Merge pull request #(\d+) from (\S+?)/', subject)
    if m:
        title = next((l.strip() for l in body.splitlines() if l.strip()), subject)
        return int(m.group(1)), m.group(2), title
    return None, None, subject


def new_cards(clone, base, head):
    """(number of ids added, number of entries changed, names of added cards) between two commits' database.json."""
    def load(rev):
        try:
            return {next(iter(e.values()))['id']: e for e in json.loads(git(clone, 'show', f'{rev}:database.json'))}
        except (SystemExit, ValueError, KeyError):
            return {}
    a, b = load(base), load(head)
    added = [i for i in b if i not in a]
    changed = [i for i in b if i in a and b[i] != a[i]]
    return len(added), len(changed), sorted({next(iter(b[i].values()))['name'] for i in added})


def added_text(clone, base, head):
    out = git(clone, 'diff', '-U0', '--no-color', base, head, '--', 'src', 'tests', *[f':!{g}' for g in GENERATED])
    return '\n'.join(l[1:] for l in out.splitlines() if l.startswith('+') and not l.startswith('+++'))


def report(clone, since, tip, deck_names):
    revs = git(clone, 'log', '--first-parent', '--reverse', '--format=%H', f'{since}..{tip}').split()
    short = {n: norm(n) for n in deck_names if len(norm(n)) >= MIN_NAME}
    rows = []
    for h in revs:
        parents = git(clone, 'rev-list', '--parents', '-n1', h).split()
        base = parents[1]
        subject, body, author, date = (x.strip() for x in git(clone, 'log', '-1', '--format=%s%x00%b%x00%an%x00%as', h).split('\x00')[:4])
        number, user, title = parse_message(subject, body)
        kinds = {}
        for line in git(clone, 'diff', '--name-status', base, h).splitlines():
            kinds[classify_path(line.split('\t')[-1])] = kinds.get(classify_path(line.split('\t')[-1]), 0) + 1
        added = changed = 0
        added_names = []
        if kinds.get('data'):
            added, changed, added_names = new_cards(clone, base, h)
        text = norm(added_text(clone, base, h)) if (kinds.get('engine') or kinds.get('tests')) else ''
        hits = sorted(n for n, k in short.items() if k in text)
        reprints = sorted(n for n in added_names if n in deck_names)
        fixes = bool(re.search(r'\b(fix\w*|bug\w*|panic\w*|crash\w*|wrong|incorrect|stale|loop\w*)\b', title, re.I))
        if added or reprints:
            hint = 'LOOK'
        elif kinds.get('engine') and (hits or fixes):
            hint = 'LOOK'
        elif kinds.get('engine'):
            hint = 'maybe'
        else:
            hint = 'skip'
        rows.append(dict(commit=h[:8], number=number, date=date, who=user or author, title=title[:110], kinds=kinds, new_cards=added, changed_cards=changed, reprints=reprints, hits=hits, hint=hint))
    return rows


def few(names, n=8):
    return ', '.join(names[:n]) + (f' (+{len(names) - n} more)' if len(names) > n else '')


def print_rows(rows, deck_names, since, tip, out=None):
    out = out or sys.stdout
    print(f'upstream main {tip[:8]}; looking at the {len(rows)} change(s) since {since[:8]}', file=out)
    print('hint  | what | files (engine/tests/data/tooling) | new cards | our cards mentioned', file=out)
    for r in rows:
        k = r['kinds']
        files = '/'.join(str(k.get(x, 0)) for x in ('engine', 'tests', 'data', 'tooling'))
        what = (f"#{r['number']} " if r['number'] else '') + f"{r['date']} {r['who']}: {r['title']}"
        cards = (f"+{r['new_cards']} new" + (f", {r['changed_cards']} changed" if r['changed_cards'] else '') + (f" (we play reprints of: {few(r['reprints'])})" if r['reprints'] else '')) if r['new_cards'] or r['changed_cards'] else '-'
        print(f"{r['hint']:5} | {what} | {files} | {cards} | {few(r['hits']) or '-'}", file=out)
    short = sorted(n for n in deck_names if len(norm(n)) < MIN_NAME)
    print(f"({len(deck_names)} card names in our decks; names under {MIN_NAME} letters are not matched by name: {', '.join(short[:14]) or 'none'}{'...' if len(short) > 14 else ''})", file=out)


def state_path(repo):
    return os.path.join(repo, *STATE_REL)


def read_state(repo):
    try:
        with open(state_path(repo), encoding='utf-8') as fh:
            lines = fh.read().splitlines()
    except OSError:
        raise SystemExit(f'{state_path(repo)} is missing: give a commit with --since, or write one there') from None
    for line in lines:
        w = line.split()
        if w and re.fullmatch(r'[0-9a-f]{7,40}', w[0]):
            return w[0]
    raise SystemExit(f'{state_path(repo)} has no commit id')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--clone', default=DEFAULT_CLONE, help='where upstream is (cloned there on the first run)')
    ap.add_argument('--since', help='a commit to look from (default: the one in rl/upstream_watch/LAST_CHECKED.txt)')
    ap.add_argument('--mark', action='store_true', help="after the report, record upstream's tip as the new LAST_CHECKED")
    ap.add_argument('--no-fetch', action='store_true', help='do not touch the network (use the clone as it is)')
    ap.add_argument('--repo', default=REPO)
    a = ap.parse_args(argv)
    if not os.path.isdir(os.path.join(a.clone, '.git')):
        if a.no_fetch:
            raise SystemExit(f'{a.clone} is not a clone')
        os.makedirs(os.path.dirname(a.clone), exist_ok=True)
        subprocess.run(['git', 'clone', '--filter=blob:none', URL, a.clone], check=True)
    if not a.no_fetch:
        git(a.clone, 'fetch', '-q', 'origin', 'main')
    tip = git(a.clone, 'rev-parse', 'origin/main').strip()
    since = a.since or read_state(a.repo)
    since = git(a.clone, 'rev-parse', since).strip()
    names = deck_card_names(a.repo)
    rows = report(a.clone, since, tip, names)
    print_rows(rows, names, since, tip)
    if a.mark:
        date = datetime.date.today().isoformat()
        os.makedirs(os.path.dirname(state_path(a.repo)), exist_ok=True)
        with open(state_path(a.repo), 'w', encoding='utf-8', newline='\n') as f:
            f.write(f'{tip}  # upstream main, looked at on {date}; the next report starts after it\n')
        print(f'recorded {tip[:8]} in {os.path.relpath(state_path(a.repo), a.repo)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

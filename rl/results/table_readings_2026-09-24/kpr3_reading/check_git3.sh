#!/usr/bin/env bash
# Second reader, read-only: the registration's warning, and the card text behind the plain summary.
set -uo pipefail
cd "$(dirname "$0")/../../../.."
echo "== 9a35f54's message, lines mentioning 'discard decks' or 'moves more'"
git log -1 --format='%B' 9a35f54 | grep -n -i -E 'discard decks|moves more' | cut -c1-400
echo "== Hyper Ray card text"
python3 lib/card.py "Hydreigon" 2>&1 | grep -i -B2 -A3 'hyper ray' | head -20
echo "== discard-pile sources in 0adfeb7's message"
git log -1 --format='%B' 0adfeb7 | grep -n -i -E 'discard' | cut -c1-300

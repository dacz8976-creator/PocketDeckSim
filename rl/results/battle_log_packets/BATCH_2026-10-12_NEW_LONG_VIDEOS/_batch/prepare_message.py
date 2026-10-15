"""Prepare the exact unsent message only after local acceptance and archival."""
import json
from pathlib import Path

BATCH = Path(__file__).resolve().parent
completion = json.loads((BATCH / 'BATCH_COMPLETION_CHECK.json').read_text(encoding='utf-8-sig'))
assert completion['all_requested_local_reviews_complete'] is True
doc = json.loads((BATCH / 'PAUSE_GAMES_BATCH_IMPORT.json').read_text(encoding='utf-8-sig'))
assert doc['external_saved'] is False and doc['sent_to_claude'] is False
assert len(doc['deck_documents']) == 1 and len(doc['game_documents']) == 4
message = '''Update Dustin's existing Pause Games artifact only: https://claude.ai/artifact/Ruet4Bkb87ufEW4sYKUpyd.

The four new videos have finished full-source reviews, independent acceptance, registration and hash-preserving archival. Add the missing filmed Glimmora / Alolan Muk / Kingambit / Regigigas deck and these four games. Results are three wins and one loss, including two explicit opponent concessions.

Use the artifact's existing data collections and supported fields. Preserve the artifact HTML, layout, sharing, every existing deck and every existing game. Do not create a replacement artifact or touch the Ladder Log. Check current data before writing: reuse a deck with the identical QR code and skip any game already present by source filename plus game number/game identity. Create only missing entries, using the exact fields below. Leave ratings unassigned. The opponent field contains only visibly established deck cores; opponent names, outcome evidence and local packet references are in notes.

The verified earlier baseline is 25 decks and 39 games, 22 wins, 17 losses and 13 opponent-concession wins. If that baseline is unchanged and all four entries are absent, the result should be 26 decks and 43 games, 25 wins, 18 losses and 15 opponent-concession wins. Report the actual saved IDs and totals. Do not overwrite existing entries to force those totals.

The deck QR verifies 20 semantic card slots and Darkness Energy. Listed card references do not establish filmed artwork or rarity. Preserve the separate source limits recorded in the game packets. Hons and KCXPF explicitly conceded; the owner's concession is a loss. Last observed points in concession games are separate from unopened final numeric statistics.

The following JSON contains the reviewed deck and game fields:

'''
message += json.dumps({'deck_documents': doc['deck_documents'], 'game_documents': doc['game_documents']}, ensure_ascii=False, indent=2) + '\n'
(BATCH / 'CLAUDE_IMPORT_REQUEST.txt').write_text(message, encoding='utf-8')
print('Prepared unsent Claude import message; no external action performed.')

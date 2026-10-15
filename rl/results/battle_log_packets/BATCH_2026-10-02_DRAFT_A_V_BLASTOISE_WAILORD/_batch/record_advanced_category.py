import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
source = Path(r'C:\Users\dacz8\.codex\codex-remote-attachments\01a0fe49-4f9b-7111-8794-bd7e69c664c7\24CB7EDA-FAC4-42C3-A9C1-6B2676B3F5FF\1-Photo-1.jpg')
target = BATCH / 'opponent_deck' / 'OWNER_ADVANCED_CATEGORY.jpg'
sha = hashlib.sha256(source.read_bytes()).hexdigest()
if not target.exists():
    shutil.copy2(source, target)
assert hashlib.sha256(target.read_bytes()).hexdigest() == sha
receipt = {
    'category': 'Advanced',
    'battle_menu': 'Step-Up Battle',
    'owner_quote': 'I mean the computer decks are technically listed under advanced',
    'earlier_owner_confirmation': 'There aren’t difficulty settings',
    'separate_difficulty_selector': False,
    'received_utc': datetime.now(timezone.utc).isoformat(),
    'screenshot_original': str(source),
    'screenshot_copy': str(target),
    'screenshot_sha256': sha,
    'observed_text': ['Step-Up Battle', 'Advanced', 'Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)', 'AI'],
    'basis': 'Root visually inspected the owner-supplied category screenshot. The selected deck is visibly listed within Advanced. Owner confirms same opponent/setup for all eight games.',
    'scope': 'Menu category establishes Advanced; it is separate from a selectable difficulty option. Opening game screens need not show the menu category.'
}
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
save(BATCH / 'ADVANCED_CATEGORY_CONFIRMATION.json', receipt)
path = BATCH / 'OPPONENT_DECK.json'
deck = json.loads(path.read_text(encoding='utf-8-sig'))
backup = BATCH / 'OPPONENT_DECK.before_advanced_category.json'
if not backup.exists():
    shutil.copy2(path, backup)
deck.update({'difficulty': 'Advanced', 'difficulty_status': 'source_visible_step_up_category', 'difficulty_category': 'Advanced', 'separate_difficulty_selector': False, 'difficulty_basis': receipt})
save(path, deck)
context_path = BATCH / 'OWNER_CONTEXT.json'
context = json.loads(context_path.read_text(encoding='utf-8-sig'))
context.update({'computer_battle_category': 'Step-Up Battle: Advanced', 'category_evidence': str(BATCH / 'ADVANCED_CATEGORY_CONFIRMATION.json'), 'separate_difficulty_selector': False})
save(context_path, context)
note_path = BATCH / 'BATCH_NOTE.md'
note = note_path.read_text(encoding='utf-8')
note = note.replace('Difficulty: **not applicable; there are no difficulty settings in this setup**, per Dustin’s direct confirmation.', 'Category: **Step-Up Battle: Advanced**, confirmed by Dustin and the [category screenshot](opponent_deck/OWNER_ADVANCED_CATEGORY.jpg). There is no separate difficulty selector.')
note_path.write_text(note, encoding='utf-8')
print(json.dumps({'category': 'Advanced', 'screenshot_sha256': sha, 'receipt': str(BATCH / 'ADVANCED_CATEGORY_CONFIRMATION.json')}))

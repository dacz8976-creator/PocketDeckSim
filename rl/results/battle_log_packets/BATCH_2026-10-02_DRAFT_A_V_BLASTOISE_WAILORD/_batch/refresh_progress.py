"""Report the bounded eight-game batch without promoting unfinished reviews."""
import json
from datetime import datetime, timezone
from pathlib import Path

BATCH = Path(__file__).resolve().parent
AUTO = ['205230', '205731', '210612', '210952', '211613']
MANUAL = ['214254', '215203', '215825']

def read(path):
    try:
        return json.loads(path.read_text(encoding='utf-8-sig'))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

entries = []
for stamp in AUTO+MANUAL:
    automatic = stamp in AUTO
    name = f'20261002_{stamp}000_iOS.MP4'
    packet = BATCH/(Path(name).stem+('_auto_sol' if automatic else '_shark_sol'))
    source = read(packet/'SOURCE.json')
    submission = read(packet/'SUBMISSION.json')
    completion = read(packet/'COMPLETION_RECEIPT.json')
    guide_acceptance = read(packet/'GUIDE_UPDATE_ACCEPTANCE.json')
    guide_authored = all((packet/n).exists() for n in ['GUIDE_UPDATE_SUPPLEMENT.json','GUIDE_UPDATE_SUPPLEMENT.md','SEEN_CARD_INVENTORY.json','SEEN_CARD_INVENTORY.md'])
    external = read(packet/'EXTERNAL_LOG_RECEIPT.json')
    summary = read(packet/'SUMMARY.json') if submission else None
    lead = read(packet/'LEAD_ACCEPTANCE.json') if completion else None
    result = (lead or {}).get('outcome') or (summary or {}).get('outcome') or (summary or {}).get('result')
    details = result if isinstance(result,dict) else {}
    result_name = details.get('result',details.get('owner_result')) if details else result
    result_name = {'owner_win':'win','owner_loss':'loss','owner_victory':'win','owner_defeat':'loss'}.get(result_name,result_name)
    score = (summary or {}).get('score',{})
    if completion and guide_acceptance:
        status = 'accepted, indexed and archived locally'
    elif completion:
        status = 'core accepted and archived; latest guide supplement pending acceptance'
    elif submission:
        status = 'first pass complete; independent acceptance pending'
    elif source:
        status = 'source verified; full review in progress or queued'
    else:
        status = 'source delivery/access verification pending'
    entries.append({'source':name, 'group':'Auto' if automatic else 'Dustin manual',
                    'packet':packet.name, 'status':status, 'source_verified':bool(source),
                    'first_pass_complete':bool(submission), 'accepted_archived':bool(completion),
                    'guide_additions_authored':guide_authored,
                    'guide_additions_accepted':bool(guide_acceptance and guide_acceptance.get('accepted')),
                    'external_log_verified':bool(external and external.get('verified_after_reload')),
                    'outcome':result_name,
                    'outcome_acceptance':'accepted' if completion else 'unaccepted first pass' if summary else None,
                    'owner_points':details.get('owner_points',(summary or {}).get('owner_points',score.get('owner'))),
                    'opponent_points':details.get('opponent_points',(summary or {}).get('opponent_points',score.get('opponent'))),
                    'turns':details.get('turns',details.get('turns_displayed',(summary or {}).get('turns',(summary or {}).get('total_turns')))),
                    'capture_status':summary.get('capture_status') if summary else None})
state = {'updated_utc':datetime.now(timezone.utc).isoformat(), 'selected_games':8,
         'auto_games':5, 'manual_games':3, 'computer_category':'Step-Up Battle: Advanced',
         'separate_difficulty_selector':False, 'ranked_ladder_eligible_games':0,
         'source_verified':sum(e['source_verified'] for e in entries),
         'first_pass_complete':sum(e['first_pass_complete'] for e in entries),
         'accepted_archived':sum(e['accepted_archived'] for e in entries),
         'guide_additions_authored':sum(e['guide_additions_authored'] for e in entries),
         'guide_additions_accepted':sum(e['guide_additions_accepted'] for e in entries),
         'external_log_verified':sum(e['external_log_verified'] for e in entries),
         'online_game_entry_requested':False, 'human_pause_games_eligible_games':0,
         'entries':entries}
(BATCH/'BATCH_PROGRESS.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
completed = state['accepted_archived']==8 and state['guide_additions_accepted']==8
lines = ['# Draft A computer comparison', '',
         '**Status: '+('all eight reviews accepted, registered and archived locally.' if completed else 'review and verification in progress.')+'**', '',
         'Five Auto games and three games piloted by Dustin, against the same **Mega Blastoise ex & Wailord ex Deck (Deluxe Pack: Mega)**. The menu category is **Step-Up Battle: Advanced**; there is no separate difficulty selector. [Category evidence](ADVANCED_CATEGORY_CONFIRMATION.json) and [deck screenshots](opponent_deck/) are preserved.', '',
         'The owner confirms the original **Draft A: Shark Tempo with Misty**, using Water Energy. The [exact 20-card log snapshot](OWNER_DECK_SNAPSHOT.json) and [captured log text](OWNER_DECK_LOG_CAPTURE.txt) establish the version; each completed packet carries DECK_USED.json. A deck list does not reveal hidden hands.', '',
         'All eight are computer battles, saved in this local batch and BATTLE_REVIEW_INDEX. They are excluded from both the human Pause Games log and ladder totals. Any visible Auto option, even OFF, establishes computer classification under the owner\'s rule. [The local-only routing instruction](LOG_ROUTING.json) supersedes the tentative external destination in earlier intake files. Auto packets end in `_auto_sol`; owner-play packets end in `_shark_sol`. The full Pause Games capture protocol applies to this batch by the owner\'s explicit request.', '',
         '| Recording | Pilot | Current status | Reviewed result |',
         '|---|---|---|---|']
for e in entries:
    result = ''
    if e['outcome']:
        result = f"{e['outcome']} {e['owner_points']}-{e['opponent_points']}"
        if not e['accepted_archived']:
            result += ' (unaccepted draft)'
    else:
        result = 'Pending'
    lines.append(f"| [{e['source']}]({e['packet']}/REVIEW.md) | {e['group']} | {e['status']} | {result} |")
lines += ['', f"Source verified: {state['source_verified']}/8. First pass complete: {state['first_pass_complete']}/8. Accepted, indexed and archived: {state['accepted_archived']}/8. Latest guide supplements independently accepted: {state['guide_additions_accepted']}/8. Online game entries requested: zero.", '',
          '[The October 2 evening guide additions](GUIDE_UPDATE_REQUIREMENTS.md) apply only to these eight recordings. They include fresh owner-turn-start boards with evolution-stack provenance, owner choices during opponent turns, seen-card inventories with supported copy counts, and per-turn decision makers. Older recordings and packets remain untouched.', '',
          'Completed packets contain the full narrative, readable turn table, one structured row per game turn, draw-timed native hands and crops, named draws/searches, ordered plays, both boards and Energy Zones, opponent fan observations and explicit discard/hidden-information limits. Independent Sol acceptance follows the full Sol first pass; Astra handles consequential ambiguities as needed.', '',
          'Frozen producer files, independent findings, source identity and archive receipts remain separate. Complete battle coverage can coexist with unavailable discard views or concealed cards; the per-game capture status and limits state what the footage supports.', '',
          'No computer result is added to the online Pause Games or Ladder Log. Source-to-packet mappings are recorded in this report and the local review index. The Pause Games artifact was used only to capture the exact deck list.', '',
          'Original movies retain their filenames and bytes. Online-only storage is checked separately after archive verification and OneDrive sync; any remaining storage transition is reported in its metadata receipt. No movie reread is used to verify reclaimed space.', '',
          'Last updated: '+state['updated_utc']+'.']
(BATCH/'BATCH_REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in state.items() if k!='entries'},ensure_ascii=False))

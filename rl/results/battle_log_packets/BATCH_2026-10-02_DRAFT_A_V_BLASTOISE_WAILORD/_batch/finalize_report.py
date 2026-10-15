"""Add verified batch totals and effective packet paths to the reader report."""
import json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parent
v=json.loads((B/'FINAL_BATCH_VERIFICATION.json').read_text(encoding='utf-8-sig'));assert v['passed'] and v['accepted_games']==8
subprocess.run([sys.executable,str(B/'refresh_progress.py')],check=True)
report=(B/'BATCH_REPORT.md').read_text(encoding='utf-8')
auto=[r for r in v['results'] if r['pilot']=='Auto'];manual=[r for r in v['results'] if r['pilot']=='Dustin']
def score(rows):
 wins=sum(r['outcome']['result']=='win' for r in rows);losses=sum(r['outcome']['result']=='loss' for r in rows)
 return f"{wins} wins, {losses} "+('loss' if losses==1 else 'losses')
opening=f"\nObserved batch results: **Auto {score(auto)}; Dustin {score(manual)}**. These are eight games against one fixed computer deck. The results describe this batch only.\n\nAll **129 game turns** are recorded, including **65 owner turns** with fresh start-board checks, draw-timed hands, actor labels and ordered plays. There are **{v['native_frames']} retained native frames** and **{v['lossless_native_crops']} lossless hand/top crops**. Each game has separate, source-supported seen-card counts. The supplied20-card deck snapshot remains separate from what was visually exposed.\n"
anchor='**Status: all eight reviews accepted, registered and archived locally.**'
assert anchor in report;report=report.replace(anchor,anchor+'\n'+opening)
lines=['','## Accepted evidence paths','','Use these accepted manifests and current files for analysis. Original rejected submissions remain preserved as history; they are not the final accepted versions.','','| Source | Turn table | Fresh boards and choices | Seen inventory | Minimum owner copies seen | Accepted manifest |','|---|---|---|---|---:|---|']
for r in v['results']:
 stem=Path(r['source']).stem;folder=stem+('_auto_sol' if r['pilot']=='Auto' else '_shark_sol')
 lines.append(f"| {r['source']} | [Turns]({folder}/TURN_TABLE.md) | [Boards and actors]({folder}/GUIDE_UPDATE_SUPPLEMENT.json) | [Seen cards]({folder}/SEEN_CARD_INVENTORY.md) | {r['minimum_distinct_owner_cards_seen']} | [Core]({folder}/{r['accepted_core_manifest']}) / [Guide acceptance]({folder}/GUIDE_UPDATE_ACCEPTANCE.json) |")
lines+=['','The third Auto recording ends before a readable full result-statistics table, so its numerical damage total remains unknown. Its Victory and3-0 score are source-supported. Hidden opponent cards, unopened discard piles, covered lower card faces and exact touch timing remain qualified in each packet.','',f"Final verification passed: all8 independent acceptance bindings, exact20-card snapshots, retained capture hashes, source identities, before/after archive hashes, current filenames/size, media mapping, index rows and latest review events. The **129 unrelated index rows are unchanged**. [Verification receipt](FINAL_BATCH_VERIFICATION.json). No archived movie was reread for this final check.",'','## Local storage','','[Storage verification](STORAGE_FINAL.json) records allocated bytes and OneDrive online-only state separately. Movies keep their original filenames and bytes; review evidence remains pinned locally. A pending OneDrive sync or eviction is a storage transition, not a missing review.','']
storage=json.loads((B/'STORAGE_FINAL.json').read_text(encoding='utf-8-sig'))
lines.append(f"At the last metadata check, {storage['online_only']} of8 archived movies were verified online-only; {8-storage['online_only']} still awaited OneDrive sync or space release. All written reviews and extracted evidence remain available locally.")
text=report+'\n'.join(lines)
for old,new in [('supplied20-card','supplied 20-card'),('all8 independent','all 8 independent'),('all8','all 8'),('Victory and3-0','Victory and 3-0'),('of8 archived','of 8 archived')]:text=text.replace(old,new)
(B/'BATCH_REPORT.md').write_text(text+'\n',encoding='utf-8')
print('Final reader report saved')

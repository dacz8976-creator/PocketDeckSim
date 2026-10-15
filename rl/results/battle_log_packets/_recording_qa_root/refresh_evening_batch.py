"""Reconcile current status wording only for verified accepted batch packets."""
import json
from pathlib import Path
from refresh_accepted_packet import refresh_accepted_packet

root = Path(__file__).resolve().parent.parent
intake = json.loads((root / 'Recording_QA/BATCH_2026-09-30_EVENING/INTAKE.json').read_text(encoding='utf-8-sig'))
for item in intake['sources']:
    video = item['video']
    packet = root / 'Recording_QA' / (Path(video).stem + '_auto_sol')
    if (packet / f'MOVE_RECEIPT.{video}.json').is_file():
        changes = refresh_accepted_packet(packet)
        if changes:
            print(video + ': ' + ', '.join(changes))

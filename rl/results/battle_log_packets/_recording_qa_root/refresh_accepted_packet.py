"""Refresh current packet status from verified acceptance and archive receipts."""
import json
from pathlib import Path

CURRENT = 'full_battle_review_complete'
STAMP = '**Current status: completed full-battle review accepted by the lead; original archived unchanged in `Reviewed`. Excluded from Ladder Log.**'
PROSE = {
    'Independent lead acceptance remains pending.': 'Independent lead acceptance, registration and archival are complete.',
    'This worker has not registered completion, moved the source, or written Ladder Log.': 'The worker did not perform global registration or movement. The lead has since registered completion and archived the original; no Ladder Log entry was created.',
    'This worker has not accepted, registered completion, moved media, or written the Ladder Log.': 'The worker did not perform acceptance, registration or movement. The lead has since accepted, registered and archived the original; no Ladder Log entry was created.',
    'finished first pass awaiting independent lead acceptance': 'full review accepted by the lead, registered and archived',
    'Independent lead checks and acceptance remain required.': 'Independent lead checks, acceptance, registration and archival are complete.',
    'This worker has not registered completion, moved the video, or written to Ladder Log.': 'The worker did not perform global registration or movement. The lead has since registered completion and archived the original; no Ladder Log entry was created.',
    'This is the complete first pass. Independent lead source checks, acceptance, completion registration and archiving are pending outside worker scope.': 'The complete first pass and independent lead source checks are accepted. The coordinator registered completion and archived the unchanged original.',
    'No shared completion registration, media move, or Ladder Log action performed.': 'The worker performed no shared registration or media move. The lead has since registered completion and archived the unchanged source. No Ladder Log action was performed.',
    'No completion registration, archive move or Ladder Log mutation was performed.': 'At worker submission, no completion registration, archive move or Ladder Log mutation had been performed by that worker. The lead has since registered completion and archived the original; Ladder Log remains unchanged.',
    'No global log, Ladder Log, move or acceptance was performed.': 'At worker submission, no global log write, move or acceptance had been performed by that worker. The lead has since accepted, registered and archived the review; no Ladder Log entry was created.',
    'Status: finished first pass awaiting independent lead acceptance.': 'Status: full review accepted by the lead, registered and archived.',
    'Finished first pass awaiting independent lead acceptance.': 'Full review accepted by the lead, registered and archived.',
    'Independent lead acceptance remains required before registration and archival.': 'Independent lead acceptance, registration and archival are complete.',
    'Independent acceptance remains outstanding.': 'Independent acceptance, registration and archival are complete.',
    'Lead acceptance remains outstanding.': 'Lead acceptance, registration and archival are complete.',
    'Independent lead acceptance pending': 'Independent lead acceptance complete',
    'Status: first pass ready for independent lead checking; not lead accepted or registered complete.': 'Status: full review accepted by the lead, registered and archived.',
    'Independent checking and acceptance remain pending.': 'Independent checking and acceptance are complete.',
    'Independent acceptance is the next required workflow step.': 'Independent acceptance, registration and archival are complete.',
    'This report is a reviewed first-pass packet, not a claim that independent acceptance, global completion registration, archiving or storage release has happened.': 'Independent acceptance, global completion registration and matching-hash archival are complete; storage state is recorded separately in CLOUD_STORAGE.',
    'Status: complete first-pass account, awaiting independent lead acceptance.': 'Status: full review accepted by the lead; registration and archival are verified.',
    'First pass complete, awaiting independent lead acceptance.': 'Full review accepted by the lead; registration and archival are verified.',
    'Independent lead acceptance and finalization remain pending.': 'Independent lead acceptance, registration and verified archival are complete.',
    'Status: first-pass complete, awaiting lead acceptance. This is not a shared-log completion or archive authorization.': 'Status: full review accepted by the lead, registered and archived. The original worker submission did not itself register completion or authorize archival.',
    'Status: full visual first-pass coverage, awaiting lead acceptance.': 'Status: complete visual coverage accepted by the lead; registration and archival are verified.',
    'Lead acceptance and independent completion checks remain pending.': 'Lead acceptance and independent completion checks are complete.',
    'The original remains in its assigned location; this worker did not move media, write Ladder Log, or update shared logs/indexes.': 'At worker submission, the original remained in its assigned location; the worker did not move media, write Ladder Log, or update shared logs/indexes. The lead has since registered and archived the unchanged original.',
    'This is a finished first review awaiting lead reconciliation and registration.': 'This full review is lead-accepted, registered and archived.',
    'This is a finished first-pass packet for lead acceptance; only the lead registers completion and moves the source.': 'This full review is lead-accepted, registered and archived by the coordinator.',
    'Lead acceptance remains pending.': 'Lead acceptance, registration and archival are complete.',
    'Lead acceptance is pending.': 'Lead acceptance, registration and archival are complete.',
    'Lead acceptance: pending.': 'Lead acceptance: accepted; registration and archival complete.',
    'First-pass review is finished and awaits the lead\'s independent acceptance and registration.': 'The full review is lead-accepted, registered and archived.',
    'Complete first pass, awaiting independent lead acceptance.': 'Full review accepted by the lead, registered and archived.',
    'Status: first-pass full-battle account ready for lead reconciliation; this worker has not registered completion or moved the source.': 'Status: full battle accepted, registered and archived by the lead. The worker did not perform those global actions.',
    'Sol first pass is complete and ready for lead checks.': 'The Sol full review and lead checks are complete; registration and archival are verified.',
    'This is the source-bound Sol first pass for lead acceptance; the worker did not finalize shared records or move media.': 'This source-bound Sol full review is lead-accepted, registered and archived. The worker did not perform those global actions.',
    'Full first visual pass is complete, pending independent and lead acceptance. Source is bound in SOURCE.json and remains unmoved.': 'The full visual review and lead acceptance are complete. Source identity is bound in SOURCE.json; the unchanged original is archived in Reviewed.',
    'This report is ready for independent bounded verification and lead acceptance. It does not itself authorize or perform a move, global review-log write or Ladder Log entry.': 'Independent bounded verification and lead acceptance are complete. The lead registered completion and archived the unchanged original; no Ladder Log entry was created.',
    'This is the primary review, awaiting the lead\'s independent acceptance and registration.': 'This primary full review is lead-accepted, registered and archived.',
    'This is the complete first-pass account, ready for independent lead checking; the worker does not register completion or move media.': 'This complete full review is lead-accepted, registered and archived; the worker did not perform those global actions.',
    'full review draft ready for lead acceptance.': 'full review accepted by the lead, registered and archived.',
    'Independent lead verification, registration, index/location updates, source movement and postmove identity verification are outside this worker\'s write scope and are not claimed complete.': 'Independent lead verification, registration, index/location updates, source movement and matching postmove identity verification are complete. These global actions were performed by the coordinator.',
    'Independent checker anchors:': 'Retained independent-check anchors:',
    'Lead should independently verify the opening, an ordinary turn, the knockout sequence, and final results before accepting and archiving.': 'The lead independently checked the opening, an ordinary turn, the knockout sequence and final results before acceptance and archival; see LEAD_ACCEPTANCE.json.',
    'Root acceptance/registration/move remain coordinator work.': 'Root acceptance, registration and verified archival are complete.',
    'Lead acceptance and shared registration remain the root coordinator\'s responsibility.': 'The root coordinator completed lead acceptance, shared registration and verified archival.',
    'full review draft ready for lead acceptance': 'full review accepted by the lead, registered and archived',
    'root acceptance pending': 'root acceptance complete; registered and archived',
    'independent lead verification pending': 'independent lead verification complete; registered and archived',
}

def refresh_accepted_packet(packet):
    packet = Path(packet)
    read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
    source = read(packet / 'SOURCE.json')
    lead = read(packet / 'LEAD_ACCEPTANCE.json')
    receipt_name = f"MOVE_RECEIPT.{source['video_basename']}.json" if 'video_basename' in source else f"MOVE_RECEIPT.{lead['source_video']}.json"
    receipt = read(packet / receipt_name)
    assert lead['accepted'] is True and lead['ladder_eligible'] is False
    assert receipt['identity_match'] and source['sha256'] == lead['source_sha256'] == receipt['sha256_before'] == receipt['sha256_after']
    name = lead['source_video']
    archived = packet.parent.parent / 'Reviewed' / name
    assert archived.is_file() and archived.stat().st_size == source['bytes'] == receipt['bytes']
    changed = []
    for filename in ['REVIEW.md', 'COVERAGE.md', 'UNCERTAINTIES.json', 'SUMMARY.json']:
        path = packet / filename
        original = path.read_text(encoding='utf-8-sig')
        text = original
        for before, after in PROSE.items():
            text = text.replace(before, after)
        if filename.endswith('.json'):
            data = json.loads(text)
            if filename == 'SUMMARY.json':
                for key in ['status', 'review_status', 'review_state']:
                    if key in data:
                        data[key] = CURRENT
                if 'worker_status' in data:
                    data['worker_status'] = 'full_visual_review_complete'
                if 'primary_review_status' in data:
                    data['primary_review_status'] = 'complete_and_lead_accepted'
                historical = data.setdefault('worker_actions_at_submission', {})
                for key in ['source_moved', 'source_moved_or_modified', 'global_finalization_performed', 'global_log_or_index_written', 'shared_log_or_index_writes', 'global_registration_performed', 'global_complete_registered', 'global_log_written', 'global_records_written', 'global_mutations', 'global_mutations_performed', 'global_writes_or_source_changes']:
                    if key in data:
                        historical.setdefault(key, data.pop(key))
                data.update({'current_status': CURRENT, 'lead_acceptance': 'accepted', 'lead_acceptance_pending': False, 'source_archived': True, 'source_modified': False, 'archive_path': str(archived), 'archive_receipt': receipt_name, 'archive_completion_event_id': receipt['review_event_id'], 'global_registration_complete': True})
                if 'lead_accepted' in data:
                    data['lead_accepted'] = True
                if 'independent_lead_accepted' in data:
                    data['independent_lead_accepted'] = True
                if 'independently_accepted' in data:
                    data['independently_accepted'] = True
            elif 'lead_acceptance_pending' in data:
                data['lead_acceptance_pending'] = False
                data['lead_acceptance'] = 'accepted'
            if filename == 'UNCERTAINTIES.json':
                data['current_status'] = CURRENT
                data['lead_acceptance'] = 'accepted'
                if 'status' in data and data['status'] != CURRENT:
                    data['worker_status_at_submission'] = data['status']
                    data['status'] = CURRENT
            text = json.dumps(data, indent=2, ensure_ascii=False) + '\n'
        elif STAMP not in text:
            title, rest = text.split('\n', 1)
            text = title + '\n\n' + STAMP + '\n' + rest
        if text != original:
            path.write_text(text, encoding='utf-8')
            changed.append(filename)
    return changed

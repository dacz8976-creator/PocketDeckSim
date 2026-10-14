"""Record coordinator reconciliations after independent retained-source checks."""
import shutil
from datetime import datetime, timezone
from intake_competitive_20261002 import ROOT, BATCH, packet_for, read, save, DESTINATION

CHECKS = {
 '20261002_020920000_iOS.MP4': {
  'scope':'Entire 248.285-second battle: profiles, setup, all nine turns, concession and Victory statistics',
  'outcome':'Win by concession, 0-0 points, second, against おさるの上司',
  'evidence':['LEAD_CHECK.jpg','overview/sheet_03.jpg','native/t0206.00.jpg','native/t0214.00.jpg','native/t0238.00.jpg','native/t0247.40.jpg'],
  'checks':['Verified opponent, going second, visible Water core and actual first attack damage120 before explicit concession and Victory statistics.', 'Checked ordinary development with two Indeedee, Helmet and regular Water attachments; reconciled all nine turns, HP and point transitions in full reports.', 'Astra confirms deferred evolution can permit turn6 Wave Splash80 into Charmeleon80 under the same board continuation; evolution would wait until a later turn. Alternate outcome is unknown.'],
  'resolution':'Astra accepted the deferred-evolution line as a legal local opportunity. Keep Wailmer unevolved through the turn6 attack, then evolve on a later owner turn if it survives. The opponent could respond differently; no guaranteed win or unchanged continuation is claimed.',
  'field':'material_questions'
 },
 '20261002_021402000_iOS.MP4': {
  'scope':'Entire 430.026667-second battle: matchmaking, setup, all fourteen turns, both knockouts, Defeat statistics',
  'outcome':'Loss, 0-3 points, first, against ポジビン',
  'evidence':['LEAD_CHECK.jpg','overview/sheet_03.jpg','native/t0180.00.jpg','native/t0205.00.jpg','native/t0254.00.jpg','native/t0263.00.jpg','native/t0386.00.jpg','native/t0392.00.jpg','native/t0402.00.jpg','native/t0410.00.jpg','native/t0416.00.jpg','native/t0422.00.jpg','native/t0429.90.jpg'],
  'checks':['Verified opening Meloetta/Giratina, ordinary early evolutions/Water attachments, forced zero-Energy Wailord ex and Stadium/healing state.', 'Verified two displayed300 hits, +2 then +1 opponent points, owner sole110 attack, stable Diancie60HP, and explicit Defeat/first/14turn/0-3/110damage result.', 'Astra confirms Indeedee survives observed110 at20HP, may heal while Active, retreat free under Peculiar Plaza before replacement, and enable fourth-Water Wailord100 attack on turn9. Its Bench vulnerability and alternate opposing choices remain unknown.'],
  'resolution':'Astra accepted choosing Indeedee as a legal tempo alternative under the observed110-damage continuation: survive at20HP, optionally heal while Active, retreat free before replacing Peculiar Plaza, promote non-ex Wailord and attach fourth Water for100 damage on turn9. This leaves Mega Gardevoir110HP and exposes a damaged two-point Indeedee on Bench; it is not a guaranteed reversal of the loss.',
  'field':'material_clarifications'
 },
 '20261002_023418000_iOS.MP4': {
  'scope':'Entire 371.495-second battle: matchmaking, setup, all eleven turns, sacrifice point, concession and Victory',
  'outcome':'Win by concession, actual points0-1, first, against KO歐~YOU (wave separator transcription)',
  'evidence':['LEAD_CHECK.jpg','overview/sheet_01.jpg','overview/sheet_09.jpg','overview/sheet_11.jpg','overview/sheet_14.jpg','native/t0210.00.jpg','native/t0307.00.jpg','native/t0343.00.jpg','native/t0354.00.jpg','native/t0356.00.jpg','native/t0359.00.jpg','native/t0362.00.jpg'],
  'checks':['Verified named opponent, first-player setup, visible core, Sabrina sacrifice and actual opponent one-point progression.', 'Checked ordinary third-Water development and repeated Ice Pop healing; first Whale Pump100 and full healing against Mega Lucario supported by native and overview.', 'Verified turn11 minus30 banner, five Water, Cyrus moving only opponent, retained effect icon and explicit concession without attack; terminal Victory independently observed.', 'Astra confirms prospective Whale Pump80 would leave Mega110 at30HP. Concession motive remains unknown; no lethal or manufactured three-point win is claimed.'],
  'resolution':'Astra confirms Bonsly reduction stays on the affected Wailord because Cyrus switches only the opponent. Five-Water Whale Pump would do110-30=80 and leave Mega Lucario ex at30HP. No attack was executed; the actual result is concession at0-1, not a demonstrated lethal knockout.',
  'field':'items'
 }
}

def main():
    astra = BATCH/'ASTRA_TACTICAL_CHECKS.md'
    assert astra.is_file()
    for name, info in CHECKS.items():
        p=packet_for(name);s=read(p/'SOURCE.json');a=read(p/'ASSIGNMENT.json')
        history=p/'worker_submission';history.mkdir(exist_ok=True)
        for filename in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
            if not (history/filename).exists():shutil.copyfile(p/filename,history/filename)
        summary=read(p/'SUMMARY.json');u=read(p/'UNCERTAINTIES.json')
        for item in u[info['field']]:
            if item.get('id') in ['deferred_wailmer_evolution','sabrina_replacement_tempo','U1']:
                item.update(status='resolved_by_bounded_astra_and_lead_check',resolution=info['resolution'],addendum='../BATCH_2026-10-02_COMPETITIVE/ASTRA_TACTICAL_CHECKS.md')
        save(p/'UNCERTAINTIES.json',u)
        summary['astra_tactical_resolution']=info['resolution']
        summary['lead_reconciliation_notes']=['Raw first-pass files preserved in worker_submission. Astra clarifications appended; outcome unchanged.']
        summary['limitations']=[v for v in summary['limitations'] if 'pending' not in v.lower() and 'awaits' not in v.lower() and 'escalated' not in v.lower()]
        if name.endswith('020920000_iOS.MP4'):
            text=(p/'REVIEW.md').read_text(encoding='utf-8').replace('Voracious Waves','Wondrous Waves')
            (p/'REVIEW.md').write_text(text,encoding='utf-8')
            summary['owner_deck_core']=[v.replace('Voracious Waves','Wondrous Waves') for v in summary['owner_deck_core']]
            summary['lead_reconciliation_notes'].append('Attack name standardized to Wondrous Waves using clearer enlarged native021402t0180.00 and Astra check; mechanics unchanged.')
        save(p/'SUMMARY.json',summary)
        for filename in ['REVIEW.md','COVERAGE.md']:
            text=(p/filename).read_text(encoding='utf-8-sig')
            text=text.replace('first-pass draft awaiting independent lead acceptance','complete first pass independently lead-accepted')
            text=text.replace('first-pass review of all available footage; independent lead acceptance pending','first-pass review of all available footage; independently lead-accepted')
            text=text.replace('Independent lead acceptance remains required.','Independent lead acceptance is complete.')
            text=text.replace('Independent lead acceptance: pending.','Independent lead acceptance: complete.')
            text=text.replace('Lead acceptance pending.','Lead acceptance complete.')
            text=text.replace('Lead acceptance is pending.','Lead acceptance is complete.')
            text=text.replace('awaiting independent lead acceptance','independently lead-accepted')
            text += '\n\n## Lead and Astra reconciliation\n\n'+info['resolution']+' See [bounded Astra checks](../BATCH_2026-10-02_COMPETITIVE/ASTRA_TACTICAL_CHECKS.md). Earlier pending language in the first-pass account is superseded by this reconciliation. Raw reports remain in worker_submission.\n'
            (p/filename).write_text(text,encoding='utf-8')
        save(p/'LEAD_ACCEPTANCE.json',{'source_video':name,'source_sha256':s['sha256'],'source_bytes':s['bytes'],'accepted':True,'coverage_checked':True,'completion_status':'full_battle_review_complete','scope':info['scope'],'requested_log':DESTINATION,'ranked_ladder_eligible':False,'accepted_at_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'root independent lead','first_pass_reviewer':a['reviewer'],'lead_evidence':info['evidence'],'independent_checks':['Read all four first-pass reports and reconciled complete coverage, identity, deck, turn order, HP/Energy/point transitions and terminal evidence.']+info['checks'],'outcome_description':info['outcome'],'astra_addendum':'../BATCH_2026-10-02_COMPETITIVE/ASTRA_TACTICAL_CHECKS.md','remaining_coverage_gaps':[],'unverified_material_claims':[],'limitations':['Hidden full lists, exact selected queue, opponent automation and concession motive remain unknown. Owner competitive intent and local date basis are qualified. Conditional alternative decisions do not establish a different game outcome.']})
        print('Accepted '+name,flush=True)

if __name__=='__main__':main()

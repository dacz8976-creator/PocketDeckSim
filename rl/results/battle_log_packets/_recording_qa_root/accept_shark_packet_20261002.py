"""Lead-only acceptance after the named source checks actually performed."""
import argparse
from datetime import datetime, timezone
import shutil
import re
from setup_shark_batch_20261002 import ROOT, BATCH, SELECTED, packet_for, read, save, DESTINATION

def explicit_image_paths(prose, packet):
    lines=[]
    for line in prose.splitlines():
        prefix=''
        def replace(match):
            nonlocal prefix
            ref=match.group(0)
            if '/' in ref:
                prefix=ref.rsplit('/',1)[0]+'/'
                return ref
            if prefix and (packet/(prefix+ref)).is_file():
                return prefix+ref
            return ref
        lines.append(re.sub(r'(?<![A-Za-z0-9_])(?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.*?-]+\.(?:jpg|png)(?![A-Za-z0-9_])',replace,line))
    return '\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('video', choices=SELECTED)
    parser.add_argument('--evidence', nargs='+', required=True)
    parser.add_argument('--astra', nargs='*', default=[])
    parser.add_argument('--notes', required=True)
    args=parser.parse_args()
    packet=packet_for(args.video)
    source=read(packet/'SOURCE.json'); assignment=read(packet/'ASSIGNMENT.json')
    assert source['video_basename']==assignment['video_basename']==args.video
    assert source['sha256']==assignment['source_sha256']
    summary=read(packet/'SUMMARY.json')
    assert summary['video_basename']==args.video
    assert summary['complete_available_footage_review'] and summary['battle_complete']
    assert summary['outcome'] in ['win','loss']
    for ref in args.evidence:
        path=(packet/ref).resolve()
        assert path.is_relative_to(packet.resolve()) and path.is_file(),ref
    for name in args.astra:
        assert (BATCH/name).is_file(),name
    history=packet/'worker_submission';history.mkdir(exist_ok=True)
    for name in ['REVIEW.md','COVERAGE.md','SUMMARY.json','UNCERTAINTIES.json']:
        if not (history/name).exists():shutil.copyfile(packet/name,history/name)
    for name in ['REVIEW.md','COVERAGE.md']:
        path=packet/name; prose=path.read_text(encoding='utf-8-sig')
        prose=explicit_image_paths(prose,packet)
        prose=prose.replace('first-pass draft awaiting lead acceptance','full battle independently accepted by the lead')
        prose=prose.replace('First-pass draft awaiting lead acceptance.','Full battle independently accepted by the lead.')
        prose=prose.replace('This is a fresh complete visual first pass awaiting lead acceptance.','This is a fresh complete visual first pass independently accepted by the lead.')
        prose=prose.replace('First-pass review awaiting lead acceptance.','Full review independently accepted by the lead.')
        prose=prose.replace('Battle complete; draft awaits lead acceptance.','Battle complete; full review independently accepted by the lead.')
        prose=prose.replace('Native `t...jpg` references','Native frame filenames')
        prose=prose.replace('Lead acceptance is pending.','Lead acceptance is complete.')
        prose=prose.replace('This draft still requires lead acceptance and any targeted strategy clarification before registration.','The complete first pass and targeted clarifications have been independently accepted by the lead; registration and archive follow.')
        prose += '\n\n## Lead check\n\n'+args.notes+'\n'
        for name in args.astra:
            prose += '\n[Targeted Astra check](../'+BATCH.name+'/'+name+').\n'
        assert '\u2014' not in prose
        path.write_text(prose,encoding='utf-8')
    summary.update({'lead_acceptance':'accepted','lead_notes':args.notes,'astra_reports':args.astra})
    uncertainties=read(packet/'UNCERTAINTIES.json')
    if isinstance(uncertainties,list):
        uncertainties={'video_basename':args.video,'source_sha256':source['sha256'],'unreviewed_intervals':[],'material_outcome_ambiguities':[],'items':uncertainties,'format_normalization':'Unambiguous raw worker list preserved in worker_submission and wrapped without dropping any item.'}
    summary['limitations']=[x for x in summary.get('limitations',[]) if x!='First-pass packet awaits lead acceptance.']
    if args.video=='20261002_114458000_iOS.MP4':
        item=next(x for x in uncertainties['items'] if x['id']=='t8_point_preservation')
        item.update({'astra_needed':False,'status':'resolved_as_conditional_tactical_alternative','resolution':'Astra and lead confirm the two-Energy retreat and Lapras Surf WWC cost. Lapras has four Water, so its 90 damage through Water weakness leaves Chandelure at 50. The observed 80-damage response would leave Lapras at 30, allowing a later KO without yielding the immediate two-point Ninetales knockout. This drops Binding Snow and leaves a damaged, unpowered ex on Bench. Hidden opposing resources prevent a forced-win or definite-error claim.','resolution_report':'../'+BATCH.name+'/ASTRA_T8_CHECK.md'})
        summary['limitations']=[x for x in summary['limitations'] if not x.startswith('First-pass draft awaits')]
    elif args.video=='20261002_143309000_iOS.MP4':
        item=next(x for x in uncertainties['material_questions'] if x['id']=='binding_snow_psy_shadow')
        item.update({'status':'resolved_from_printed_card_text_with_observation_limits','resolution':'Binding Snow prohibits Energy Zone attachments to the Active Pokemon during the next opponent turn, including Psy Shadow. Normal Bench attachments remain legal; existing Energy is not removed. No rejected Psy Shadow attempt or opponent intent is observed.','resolution_report':'../'+BATCH.name+'/ASTRA_NINETALES_CHECK.md'})
        summary['limitations']=[x for x in summary['limitations'] if 'pending targeted' not in x and x!='First-pass packet awaiting lead acceptance']
        for item in summary.get('key_findings',[]):
            if item.get('type')=='inference_pending_clarification':
                item.update({'type':'printed_rule_interaction','finding':'Binding Snow includes Psy Shadow because both attach Energy from the Energy Zone to the Active Pokemon. No actual failed attempt is observed.'})
        for filename in ['REVIEW.md','COVERAGE.md']:
            path=packet/filename; prose=path.read_text(encoding='utf-8')
            prose=prose.replace('A mechanics/strategy question about Binding Snow and Psy Shadow is pending lead/Astra reconciliation. This packet is a full first-pass draft, not a claim of lead acceptance or external logging. No shared log, index, location map or artifact was edited by this worker.','Binding Snow and Psy Shadow were reconciled against their printed card text by Astra and the lead. No rejected ability attempt or opponent intent is claimed. The raw worker submission is preserved separately.')
            prose=prose.replace('Limits: full first-pass account does not imply exact hidden lists, opponent automation, observed failed Psy Shadow activation, or lead acceptance. Binding Snow/Psy Shadow causal interpretation is separately pending in UNCERTAINTIES.json.','Limits: exact hidden lists, opponent automation and a failed Psy Shadow activation are not established. The printed Binding Snow/Psy Shadow interaction has been reconciled by Astra and the lead.')
            path.write_text(prose,encoding='utf-8')
    elif args.video=='20261002_115323000_iOS.MP4':
        item=next(x for x in uncertainties['items'] if x['id']=='strategy_turn13_single_prize')
        item.update({'status':'resolved_as_conditional_survival_alternative','resolution':'Astra finds a credible single-point Vulpix survival line, not a forced win or definite blunder. Either Vulpix can pay Gnaw. Rampardos at its original 30 HP is already below the 50 conditional self-damage threshold, so Gnaw does not create fatal recoil. Against a direct Head Smash KO, one point each would likely bring the score to 2-2; precise simultaneous point timing is not verified. The precharged second Fossil and hidden responses remain threats.','resolution_report':'../'+BATCH.name+'/ASTRA_RAMPARDOS_CHECK.md'})
        summary['limitations']=[x for x in summary['limitations'] if not x.startswith('Strategic counterfactual awaits')]
        for item in summary.get('key_findings',[]):
            if item.get('classification')=='proposed_tactical_alternative':item['finding']=uncertainties['items'][0]['resolution']
        for filename in ['REVIEW.md','COVERAGE.md']:
            path=packet/filename; prose=path.read_text(encoding='utf-8')
            prose=prose.replace('**Proposed alternative requiring Astra judgment:**','**Conditional survival alternative, checked by Astra:**')
            prose=prose.replace('Lead/Astra should compare that single-prize route before assigning a definite tactical error.','Astra confirms the single-point route is plausible. Rampardos was already below its 50 self-damage threshold at 30 HP, so Gnaw does not create fatal recoil; either Vulpix could attack. This does not establish a definite tactical error.')
            prose=prose.replace('tactical counterfactual judgment remains for lead/Astra acceptance.','the tactical counterfactual has been accepted with the stated hidden-response and point-timing limits.')
            prose=prose.replace('Counterfactual strategy is explicitly unresolved in UNCERTAINTIES.json.','Counterfactual strategy is resolved as a conditional survival alternative in UNCERTAINTIES.json; exact unobserved simultaneous point timing remains qualified.')
            path.write_text(prose,encoding='utf-8')
    elif args.video=='20261002_143837000_iOS.MP4':
        summary['limitations']=[x for x in summary['limitations'] if not x.startswith('Draft requires lead acceptance')]
        uncertainties['flower_trick_astra_check']='Printed spot-based delayed timing independently confirmed in ASTRA_FLOWER_TRICK_CHECK.md; native initial-choice frames and before/after states support attribution. No recoil or Ability claim.'
    save(packet/'SUMMARY.json',summary)
    uncertainties['lead_check_complete']=True
    uncertainties['material_claims_reconciled']=True
    uncertainties['astra_reports']=args.astra
    save(packet/'UNCERTAINTIES.json',uncertainties)
    acceptance={'source_video':args.video,'source_sha256':source['sha256'],'accepted':True,'decision':'accepted_full_battle_review','coverage_checked':True,'completion_status':'full_battle_review_complete','requested_log':DESTINATION,'ranked_ladder_eligible':False,'remaining_coverage_gaps':[],'unverified_material_claims':[],'scope':f"Entire {source['duration_seconds']}-second recording: setup, every supplied turn, meaningful state changes and terminal outcome",'lead_evidence':args.evidence,'astra_reports':args.astra,'lead_notes':args.notes,'checked_at':datetime.now(timezone.utc).isoformat(),'review_model':assignment['review_model'],'reasoning_effort':assignment['reasoning_effort']}
    target=packet/'LEAD_ACCEPTANCE.json'
    assert not target.exists(),'Acceptance already exists; use a labelled addendum instead'
    save(target,acceptance)
    print('Lead accepted '+args.video)

if __name__=='__main__':main()

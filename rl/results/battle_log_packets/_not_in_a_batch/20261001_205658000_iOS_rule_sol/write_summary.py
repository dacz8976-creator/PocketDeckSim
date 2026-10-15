import json
from pathlib import Path
p=Path('Recording_QA/20261001_205658000_iOS_rule_sol')
s=json.loads((p/'SOURCE.json').read_text(encoding='utf-8-sig'))
summary={
 'video_basename':s['video_basename'],'sha256':s['sha256'],'reviewer':s['reviewer'],
 'review_model':'gpt-6.1-sol','reasoning_effort':'high',
 'status':'Finished first pass awaiting independent lead acceptance.',
 'recording_type':'one_complete_battle_rules_test','recording_intent':'rules_testing',
 'complete_available_footage_review':True,'battle_complete':True,'battle_count':1,
 'duration_seconds':s['duration_seconds'],'reviewed_intervals_seconds':[[0,s['duration_seconds']]],
 'proposed_completion_status':'full_battle_review_complete','independent_lead_acceptance':'pending',
 'mode':'Solo, Random Battle (Advanced), confirmed on results screen','ladder_eligible':False,
 'auto':{'observed_state':'off','visible_changes':[]},
 'outcomes':[{'battle':1,'owner_result':'defeat','turn_order':'went_first','turns_played':14,'owner_points':0,'opponent_displayed_score_circles':3,'opponent_awarded_points_total':4,'damage_done':120,'terminal_reason':'Second Team Rockets Moltres ex knocked out by Mega Gardevoir ex Fantasia Force','evidence':['native/t0173.00.jpg','native/t0393.00.jpg','native/t0395.00.jpg','native/t0400.50.jpg','native/t0404.00.jpg','native/t0409.50.jpg']}],
 'key_findings':[
  {'interaction':'Heat Charged plus Victory Star replacement','observation':'First original 1H/2T is replaced by 1H/2T; Active Fire settles 1 to 2, not accumulated batches.','evidence':['native/t0091.00.jpg','native/t0104.70.jpg','native/t0107.00.jpg','native/t0108.00.jpg','native/t0114.00.jpg','native/t0117.00.jpg']},
  {'interaction':'Heat Charged later turns','observation':'Victini prompts recur. Kept original batches 1H/2T, 2H/1T, 1H/2T produce Active Fire 2 to 3, 2 to 4, 3 to 4.','evidence':['native/t0138.00.jpg','native/t0155.50.jpg','native/t0156.00.jpg','native/t0164.00.jpg','native/t0193.00.jpg','native/t0204.00.jpg','native/t0206.00.jpg','native/t0208.00.jpg','native/t0358.00.jpg','native/t0370.00.jpg','native/t0374.00.jpg','native/t0376.00.jpg']},
  {'interaction':'Netherwing insufficient Energy','observation':'Cost 3 Fire plus 1 Colorless is visible; two Fire produces Not enough Energy. Netherwing is never successfully executed.','evidence':['native/t0193.00.jpg','native/t0194.00.jpg']},
  {'interaction':'Double Smash plus Victory Star','observation':'Kept HH produces 80; later original TT is replaced by TH and produces 40. Settled HP matches.','evidence':['native/t0230.00.jpg','native/t0241.00.jpg','native/t0243.00.jpg','native/t0246.00.jpg','native/t0283.00.jpg','native/t0285.00.jpg','native/t0287.00.jpg','native/t0292.00.jpg','native/t0293.00.jpg','native/t0298.00.jpg']},
  {'interaction':'Flame Patch and separate zone attachment','observation':'Flame Patch moves discarded Fire into ACTIVE Darmanitan, one to two. Separate zone attachment goes to BENCHED Moltres, two to three. No healing occurs.','evidence':['native/t0272.00.jpg','native/t0273.00.jpg','native/t0275.00.jpg','native/t0276.00.jpg','native/t0277.00.jpg','native/t0298.00.jpg']},
  {'interaction':'Bounded Field and card inspection boundaries','observation':'Stadium inspected on turn 11, played on turn 13. No matching-weakness attack follows. Will and Team Rockets Master Plan drawn or inspected, never played. Only one Victini in play.','evidence':['native/t0270.00.jpg','native/t0320.00.jpg','native/t0323.00.jpg','native/t0337.00.jpg','native/t0347.00.jpg','native/t0374.00.jpg']},
  {'interaction':'Terminal scoring and effects','observation':'Two Moltres ex KOs award +2 each; circles cap at three. Mega Gardevoir evolves from Kirlia and uses Fantasia Force 110 to KO 70 HP Moltres. Three-Energy allocation is printed but has no observed settled post-effect state before defeat.','evidence':['native/t0173.00.jpg','native/t0386.00.jpg','native/t0388.00.jpg','native/t0391.00.jpg','native/t0393.00.jpg','native/t0395.00.jpg','native/t0400.50.jpg','native/t0409.50.jpg']}
 ],
 'independent_check_times':[
  {'purpose':'Opening and ordinary turn','times_seconds':[0,23,34,40,50]},
  {'purpose':'First Heat Charged replacement and settled count','times_seconds':[91,104.7,107,108,114,117]},
  {'purpose':'Second Heat Charged, separate Bench attachment and decline','times_seconds':[138,155.5,156,164]},
  {'purpose':'First KO, promotion, insufficient Energy, third Heat Charged','times_seconds':[173,181,193,194,204,206,208]},
  {'purpose':'Retreat and Double Smash kept heads','times_seconds':[224,230,241,243,246]},
  {'purpose':'Flame Patch Active versus separate manual Bench attachment','times_seconds':[272,273,275,276,277,298]},
  {'purpose':'Double Smash replacement','times_seconds':[283,285,287,292,293,298]},
  {'purpose':'Ordinary opponent turn and actual Stadium play','times_seconds':[301,306,311,315,319,320,323]},
  {'purpose':'Copycat, evolution, fourth Heat Charged and Energy','times_seconds':[332,333,345,347,358,370,374,376]},
  {'purpose':'Final Mega evolution, attachment, attack, capped score and outcome','times_seconds':[383,386,388,390,391,393,395,400.5,404,409.5]}
 ],
 'remaining_coverage_gaps':[],
 'limitations':['Sampled visual reconstruction with targeted native frames; no frame-by-frame or audio transcript.','Hidden opponent hands and random ability-drawn card identity remain unknown.','Brief prompt declines inferred from immediate unchanged-batch resolution; exact finger tap instants are not claimed.','Printed but untested effects are explicitly separated in UNCERTAINTIES.json.'],
 'simulator_edits':False,'training_ingestion':False,'ladder_log_updated':False,'source_moved':False,'completion_registered_by_worker':False
}
u={
 'video_basename':s['video_basename'],'reviewer':s['reviewer'],
 'remaining_coverage_gaps':[],
 'honestly_unknown_hidden_information':[
  {'item':'Opponent unrevealed hand and complete deck order or lists','reason':'Face-down cards do not identify their contents.'},
  {'item':'Random Psychic Pokemon obtained by Strange Singing on turns 12 and 14','reason':'Ability animation reveals the effect but its deck-to-hand card remains hidden; a subsequent play does not independently prove which draw supplied it.'},
  {'item':'Exact recording clock and timezone basis','reason':'Filename date is known; capture clock basis is not independently verified.'}
 ],
 'untested_mechanics':[
  'Successful Netherwing damage and Fire discard.',
  'Multiple Victini in play and enforcement of the printed shared one-use-per-turn limit.',
  'Will forcing a first coin; Will is held or drawn and not played.',
  'Team Rockets Master Plan confusion and its coin; card is drawn or inspected and not played.',
  'Bounded Field damage multiplication on a matching weakness and its Mega-attacker exception.',
  'Mimikyu ex Disguise prevention; Mimikyu receives no attack damage.',
  'Brambleghast Accept Pain; ability not used.',
  'Mega Gardevoir ex three-Psychic Fantasia Force allocation in a settled surviving-battle state.',
  'Three-point award for knocking out a Mega Evolution Pokemon ex; the Mega is the attacker here.'
 ],
 'observation_precision_limits':[
  {'item':'Brief declined Victory Star choices','resolution':'Prompt and immediate attack or Energy resolution with no replacement batch establish kept originals; exact finger tap timestamps are not asserted. Dense quarter-second turn-5 frames retained.'},
  {'item':'Transient printed HP during animations','resolution':'Only settled board HP is used; enlarged card 120 HP is not counted as healing.'},
  {'item':'Notifications covering portions of upper screen','resolution':'Consequential states checked in adjacent native frames; notifications do not create an unresolved available-phase coverage gap.'}
 ],
 'material_ambiguities_requiring_clarification':[],
 'independent_acceptance_pending':True,
 'worker_status':'Finished first pass awaiting independent lead acceptance.'
}
(p/'SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(p/'UNCERTAINTIES.json').write_text(json.dumps(u,indent=2),encoding='utf-8')
print('Wrote SUMMARY.json and UNCERTAINTIES.json')

import json
from pathlib import Path
p=Path(r'C:/Users/dacz8/OneDrive/Desktop/Battle Logs/Recording_QA/20261001_210403000_iOS_rule_sol')
summary={
 'video_basename':'20261001_210403000_iOS.MP4',
 'reviewer':'sol_rules_20261001_210403000','review_model':'gpt-6.1-sol','reasoning_effort':'high',
 'recording_type':'one_complete_solo_battle_used_for_owner_rules_testing',
 'complete_available_footage_review':True,'battle_complete':True,
 'proposed_completion_status':'full_battle_review_complete',
 'status':'Finished first pass awaiting independent lead acceptance.',
 'lead_acceptance':False,'ladder_eligible':False,
 'mode':'Solo, AI Opponent; results identify Random Battle (Advanced)',
 'auto_state':{'initial':'off','on_by_seconds':403,'scope':'owner Auto indicator; does not establish opponent control mode'},
 'outcomes':[{'battle':1,'owner':'Dacz8976','opponent':'AI Opponent','result':'victory','owner_points':3,'opponent_points':2,'terminal_ko_seconds':447,'victory_result_seconds':463}],
 'key_findings':[
  {'claim':'Will does not force Confusion condition-check heads.','basis':'Will played and confirmed, then condition check tails and attack failed','times':[376,378,380,386,387,389]},
  {'claim':'Victory Star rerolls the complete three-coin attack batch once across two copies.','basis':'Heat Charged three tails, accepted reroll, three tails again, no second prompt; printed once-per-turn text','times':[99,102,104,107,110,111,112]},
  {'claim':'Failed Confusion checks are not offered Victory Star and do not deal self damage.','basis':'Both Victini visible, tails, attack did nothing, HP and Energy unchanged','times':[309,313,314,317,386,387,389]},
  {'claim':'Master Plan confuses opponent before its flip, with tails also confusing owner.','basis':'Printed card and separate public condition changes','times':[80,83,87,90,281,285,287,290]},
  {'claim':'Evolution and retreat cure Confusion in observed cases.','basis':'Explicit in-game recovery messages','times':[118,412,414]},
  {'claim':'Bounded Field doubling precedes Guard Press damage reduction in the observed Double Smash.','basis':'40 per heads, one heads, doubled Fire Weakness, minus20 protection gives observed60; arithmetic is inference from printed text and HP','times':[404,406,420,421,424,426]},
  {'claim':'Flame Patch restores discarded Fire to an Active Fire Pokemon ex.','basis':'Actual plays and settled Energy increases on Moltres','times':[250,253,299,305]},
  {'claim':'Deck exhaustion skips the draw without immediately ending this battle.','basis':'No cards left messages followed by continued turns and final knockout win','times':[410,411,439,447,454]},
  {'claim':'Final Netherwing applies doubled Fire Weakness for260.','basis':'Unshielded Bronzong60 knocked out, owner reaches third point','times':[442,447,450,454,457,463]}
 ],
 'independent_check_times':[
  {'purpose':'opening','seconds':[4,14,19]},
  {'purpose':'ordinary development and damage','seconds':[123,130,142,155]},
  {'purpose':'Master Plan and evolution recovery','seconds':[80,83,87,90,118,281,287,290]},
  {'purpose':'Victory Star complete reroll and once-per-turn limit','seconds':[99,102,104,107,110,111,112]},
  {'purpose':'Flame Patch real plays','seconds':[250,253,299,305]},
  {'purpose':'Confusion failed without Will','seconds':[309,313,314,317]},
  {'purpose':'Will exclusion from Confusion','seconds':[376,378,380,386,387,389]},
  {'purpose':'Auto, Guard Press, retreat recovery and damage ordering','seconds':[403,404,406,410,412,414,420,421,424,426]},
  {'purpose':'deck exhaustion and final victory','seconds':[439,442,447,450,454,457,463,465]}
 ],
 'coverage_method':'155 overview frames at3-second fps midpoint sampling across the whole465.875488 seconds; targeted native-resolution exact timestamp checks; all20 turns and end states reconciled',
 'remaining_coverage_gaps':[],
 'untested_questions':['Will with an accepted Victory Star reroll','Bounded Field Mega Evolution Pokemon ex exclusion','Flame Patch bench target or empty discard refusal'],
 'files':['SOURCE.json','REVIEW.md','COVERAGE.md','UNCERTAINTIES.json','overview/sheet_01.jpg through sheet_18.jpg','native/tNNNN.NN.jpg']
}
(p/'SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
uncertainties={
 'status':'Finished first pass awaiting independent lead acceptance.',
 'remaining_coverage_gaps':[],
 'honestly_unknown_hidden_information':[
  'Complete20-card deck lists and unrevealed opponent hand.',
  'Underlying coin random seed and choices not visibly revealed.',
  'Exact filename wall-clock/timezone basis beyond intake date.'
 ],
 'untested_rule_questions':[
  {'question':'Does Will alter the first coin on a Victory Star reroll after it has already applied to the initial attack batch?','reason':'The single accepted reroll occurs before Will is played. Later Will-supported Heat Charged rolls3heads and is retained.'},
  {'question':'How does Bounded Field handle Mega Evolution Pokemon ex?','reason':'No Mega Evolution Pokemon ex is used in this battle.'},
  {'question':'Will Flame Patch reject a Bench target or empty discard?','reason':'Both successful uses target Active Fire Moltres with discarded Fire available; early inspection is not an attempted play.'}
 ],
 'bounded_observation_limits':[
  'Full visual phase review is not a claim of separately viewing every encoded frame.',
  'Overview labels are fps midpoint samples; native filenames are exact requested timestamp frames.',
  'Top-screen notifications briefly obscure some public cards; later settled states and printed cards resolve consequential claims.',
  'Opponent resource actions are visible, but private policy reasoning is unknown.'
 ],
 'resolved_draft_corrections':[
  'Early supporter is Copycat; no Campfire is played.',
  'Confusion supporter is Team Rocket\'s Master Plan; Will inspected early remains in hand until later.',
  'Initial Bounded Field view around49s is inspection; actual Stadium play occurs around158-163s.',
  'Opponent face-up X Speed is discard, not an opposing Stadium replacement.',
  'Lopunny Jump Kick deals20 Active plus20 to one Bench Pokemon, not30.',
  'Bronzor, not Chatot, is benched on turn7.'
 ],
 'acceptance_work_remaining':'Independent lead coverage and source checks plus lead-only integration/registration/archive. Worker has not accepted the packet.'
}
(p/'UNCERTAINTIES.json').write_text(json.dumps(uncertainties,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
for name in ['SUMMARY.json','UNCERTAINTIES.json']:
 json.loads((p/name).read_text(encoding='utf-8'))
print('JSON validated')

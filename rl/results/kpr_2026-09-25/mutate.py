#!/usr/bin/env python3
"""Apply each kpr mutation to a scratch copy of engine/, run kpr's tests, record whether any fails, restore.
Usage: mutate_kpr.py <scratch engine copy> <results file> [mutation names...]"""
import subprocess, sys, os
ROOT, RESULTS = sys.argv[1], sys.argv[2]
VF = 'src/players/value_functions.rs'; PM = 'src/players/mod.rs'
KPR_ARM = """        PlayerCode::KPR { max_depth } => Box::new(PublicPricingPlayer {
            search: ExpectiMiniMaxPlayer {
                deck,
                max_depth: *max_depth,
                write_debug_trees: false,
                value_function: Box::new(value_functions::public_clock_effect_kpr_value_function),
                opponent_ply: 0,
                consistent_horizon: false,
                soft_opponent: false,
            },
        }),"""
BARE_ARM = """        PlayerCode::KPR { max_depth } => Box::new(ExpectiMiniMaxPlayer {
            deck,
            max_depth: *max_depth,
            write_debug_trees: false,
            value_function: Box::new(value_functions::public_clock_effect_kpr_value_function),
            opponent_ply: 0,
            consistent_horizon: false,
            soft_opponent: false,
        }),"""
MUTS = [
 ('KPR const switched off', VF, '        defender_modifiers: false,\n        projected_readiness: true,', '        defender_modifiers: false,\n        projected_readiness: false,'),
 ('KPR arm uses the kp value function', PM, 'value_function: Box::new(value_functions::public_clock_effect_kpr_value_function),', 'value_function: Box::new(value_functions::public_clock_effect_value_function),'),
 ('KPR arm without the pricing wrapper', PM, KPR_ARM, BARE_ARM),
 ('online score not projected', VF, '        reserve_aware,\n        projected_readiness,\n    );\n    let active_safety', '        reserve_aware,\n        false,\n    );\n    let active_safety'),
 ('clock not projected', VF, '            defender_modifiers,\n            projected_readiness,\n        )\n    } else {', '            defender_modifiers,\n            false,\n        )\n    } else {'),
 ("opponent's scores read hidden zones", VF, '        extract_features(\n            state,\n            opponent,\n            1.0,\n            public_eval,', '        extract_features(\n            state,\n            opponent,\n            1.0,\n            false,'),
 ('min of the clocks dropped', VF, '        clock(false).min(clock(true))', '        clock(true)'),
 ('Bench projected too', VF, '        let charged: &PlayedCard = if projected_readiness && slot == 0 {', '        let charged: &PlayedCard = if projected_readiness {'),
 ('clock damage not projected', VF, '            let damage = attack_damage(atk, charged);\n            if damage == 0 {', '            let damage = attack_damage(atk, pokemon);\n            if damage == 0 {'),
 ('forms not projected', VF, 'energy_missing(charged, &atk.energy_required, state, opponent).len() + steps;', 'energy_missing(pokemon, &atk.energy_required, state, opponent).len() + steps;'),
 ("forms' damage not projected", VF, '                        let damage = attack_damage(atk, charged);\n                        if damage > 0 {', '                        let damage = attack_damage(atk, pokemon);\n                        if damage > 0 {'),
 ('projected during setup', VF, '    if state.turn_count == 0 {\n        return Vec::new();\n    }\n    let owner_to_move', '    let owner_to_move'),
 ('turn-over check dropped', VF, '    if owner_to_move && !owner_turn_is_over(state, owner) {', '    if owner_to_move {'),
 ('this turn only (the registered rule)', VF, "    turns.push((state.turn_count + if owner_to_move { 2 } else { 1 }, false));", "    if turns.is_empty() {\n        turns.push((state.turn_count + if owner_to_move { 2 } else { 1 }, false));\n    }"),
 ('next turn is always turn + 1', VF, '    turns.push((state.turn_count + if owner_to_move { 2 } else { 1 }, false));', '    turns.push((state.turn_count + 1, false));'),
 ("this turn's block read on turn + 1", VF, '        turns.push((state.turn_count, true));', '        turns.push((state.turn_count + 1, true));'),
 ('pending end not a turn end', VF, '    state.end_turn_pending\n        || state.attack_name_used_this_turn[owner].is_some()', '    false\n        || state.attack_name_used_this_turn[owner].is_some()'),
 ('attack used not a turn end', VF, '        || state.attack_name_used_this_turn[owner].is_some()', '        || false'),
 ('forced EndTurn not a turn end', VF, '            matches!(choices.as_slice(), [SimpleAction::EndTurn])', '            false'),
 ('deferred Checkup not a turn end', VF, '                        SimpleAction::ResolvePokemonCheckup\n                            | SimpleAction::FinishPokemonCheckup', '                        SimpleAction::FinishPokemonCheckup\n                            | SimpleAction::FinishPokemonCheckup'),
 ('paused Checkup not a turn end', VF, '                        SimpleAction::ResolvePokemonCheckup\n                            | SimpleAction::FinishPokemonCheckup', '                        SimpleAction::ResolvePokemonCheckup\n                            | SimpleAction::ResolvePokemonCheckup'),
 ('end-of-turn evolution not a turn end', VF, '\n                            | SimpleAction::ResolveEndTurnEvolution { .. }', ''),
 ('Zone block ignored for the Zone', VF, '        if !zone_blocked {\n            charged.attached_energy.extend(zone);', '        if true {\n            charged.attached_energy.extend(zone);'),
 ('used Ability counted this turn', VF, '            if this_turn && holder.ability_used {', '            if false && holder.ability_used {'),
 ('used Ability not counted next turn', VF, '            if this_turn && holder.ability_used {', '            if holder.ability_used {'),
 ('Ice Maker ignores the block', VF, '                Some(AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon { energy_type })\n                    if !zone_blocked && state.pokemon_is_type(active, *energy_type) =>', '                Some(AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon { energy_type })\n                    if state.pokemon_is_type(active, *energy_type) =>'),
 ('Ice Maker ignores the type', VF, '                Some(AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon { energy_type })\n                    if !zone_blocked && state.pokemon_is_type(active, *energy_type) =>', '                Some(AbilityMechanic::AttachEnergyFromZoneToActiveTypedPokemon { energy_type })\n                    if !zone_blocked =>'),
 ('YourTyped from the Bench', VF, '                    if holds_it && !zone_blocked && state.pokemon_is_type(active, *energy_type) =>', '                    if !zone_blocked && state.pokemon_is_type(active, *energy_type) =>'),
 ('YourTyped arm dropped', VF, '                    if holds_it && !zone_blocked && state.pokemon_is_type(active, *energy_type) =>', '                    if false =>'),
 ('ZoneToSelf from the Bench', VF, 'Some(AbilityMechanic::AttachEnergyFromZoneToSelf { energy_type, amount }) if holds_it && !zone_blocked => {', 'Some(AbilityMechanic::AttachEnergyFromZoneToSelf { energy_type, amount }) if !zone_blocked => {'),
 ('ZoneToSelf arm dropped', VF, 'Some(AbilityMechanic::AttachEnergyFromZoneToSelf { energy_type, amount }) if holds_it && !zone_blocked => {', 'Some(AbilityMechanic::AttachEnergyFromZoneToSelf { energy_type, amount }) if false => {'),
 ('Roar ignores the block', VF, '                    if holds_it && !zone_blocked && self_damage + hit < remaining_hp =>', '                    if holds_it && self_damage + hit < remaining_hp =>'),
 ('Roar knock-out guard dropped', VF, '                    if holds_it && !zone_blocked && self_damage + hit < remaining_hp =>', '                    if holds_it && !zone_blocked =>'),
 ('Roar damage not cumulative', VF, '                    self_damage += hit;\n                    charged.attached_energy.extend(std::iter::repeat_n(*energy_type, *amount as usize));', '                    charged.attached_energy.extend(std::iter::repeat_n(*energy_type, *amount as usize));'),
 ('Combust knock-out guard dropped', VF, '                    if holds_it && self_damage + hit < remaining_hp =>', '                    if holds_it =>'),
 ('Combust from the Bench', VF, '                    if holds_it && self_damage + hit < remaining_hp =>', '                    if self_damage + hit < remaining_hp =>'),
 ('Combust keeps the discarded Energy', VF, '                        discard.remove(at);\n                        self_damage += hit;', '                        let _ = at;\n                        self_damage += hit;'),
 ('Blessing keeps the discarded Energy', VF, '            charged.attached_energy.push(discard.remove(at));', '            charged.attached_energy.push(discard[at]);'),
 ('Blessing takes the first discarded', VF, '    best.map(|(at, _)| at)', '    best.map(|_| 0)'),
 ('Blessing from the Active', VF, '                    if !holds_it && state.pokemon_is_type(active, *energy_type) =>\n                {\n                    blessings += 1;', '                    if state.pokemon_is_type(active, *energy_type) =>\n                {\n                    blessings += 1;'),
 ('Blessing ignores the type', VF, '                    if !holds_it && state.pokemon_is_type(active, *energy_type) =>\n                {\n                    blessings += 1;', '                    if !holds_it =>\n                {\n                    blessings += 1;'),
]
FILTERS = ['kpr_feature_tests', 'kpr3_from_get_player']
only = sys.argv[3:]
env = dict(os.environ, CARGO_TARGET_DIR=os.path.join(ROOT, 'target'))
out = open(RESULTS, 'a')
for name, path, old, new in MUTS:
    if only and name not in only:
        continue
    p = os.path.join(ROOT, path)
    orig = open(p, 'rb').read()
    norm = orig.decode().replace('\r\n', '\n')
    assert norm.count(old) == 1, (name, norm.count(old))
    open(p, 'wb').write(norm.replace(old, new).encode())
    try:
        r = subprocess.run(['cargo', 'test', '--release', '--features', 'test-utils', '--lib', '--', *FILTERS],
                           cwd=ROOT, env=env, capture_output=True, text=True)
        res = r.stdout + r.stderr
        failed = [l.split()[1] for l in res.splitlines() if l.startswith('test ') and l.rstrip().endswith('FAILED')]
        if 'could not compile' in res or 'error[' in res:
            status = 'COMPILE ERROR'
        elif failed:
            status = f'caught by {len(failed)}: ' + ', '.join(f.split('::')[-1] for f in failed)
        else:
            status = 'SURVIVED'
        line = f'{name}: {status}'
        print(line, flush=True); out.write(line + '\n'); out.flush()
        if status == 'COMPILE ERROR':
            print(res[-3000:])
    finally:
        open(p, 'wb').write(orig)

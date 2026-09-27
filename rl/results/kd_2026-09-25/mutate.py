#!/usr/bin/env python3
"""Apply each kd mutation to the scratch copy, run kd's tests, record whether any fails, restore."""
import subprocess, sys, os, shutil
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mut')
VF = 'src/players/value_functions.rs'; HC = 'src/hooks/core.rs'; PM = 'src/players/mod.rs'
MUTS = [
 ('weakness dropped', HC, '        let weakness = if weakness_applies {', '        let weakness = if false && weakness_applies {'),
 ('Solid Shell (ability reduction) dropped', HC, '            steel_apron_reduction(state, defender),\n            ability,', '            steel_apron_reduction(state, defender),\n            0 * ability,'),
 ('stored ReduceDamageFromAttacks read', HC, '            steel_apron_reduction(state, defender),\n            ability,', '            steel_apron_reduction(state, defender),\n            ability + defender.get_active_effects().iter().filter_map(|e| match e { CardEffect::ReduceDamageFromAttacks { amount } => Some(*amount), _ => None }).sum::<u32>(),'),
 ('Heavy Helmet dropped', HC, '            heavy_helmet_reduction(defender),\n            steel_apron_reduction', '            0 * heavy_helmet_reduction(defender),\n            steel_apron_reduction'),
 ('Steel Apron dropped', HC, '            steel_apron_reduction(state, defender),\n            ability,', '            0 * steel_apron_reduction(state, defender),\n            ability,'),
 ('NoWeakness honoured', HC, 'printed_weakness_application(state, defender, attacker)', 'weakness_application_against(state, defender, attacker)'),
 ('Ice Face on every hit', HC, '        let later = if first == 0 { 0 } else { after(reductions.saturating_sub(full_hp_only)) };', '        let later = first;'),
 ('Ice Face whole-hit absorption dropped', HC, '        let later = if first == 0 { 0 } else { after(reductions.saturating_sub(full_hp_only)) };', '        let later = after(reductions.saturating_sub(full_hp_only));'),
 ('Safeguard dropped', HC, 'if matches!(ability_effect, Some(CardEffect::PreventAllDamageFromEx)) && attacker.card.is_ex() {\n            return (0, 0);', 'if matches!(ability_effect, Some(CardEffect::PreventAllDamageFromEx)) && attacker.card.is_ex() && false {\n            return (0, 0);'),
 ('Intimidating Fang dropped', HC, '        let pre_weakness = base.saturating_sub(intimidating_fang);', '        let pre_weakness = base + 0 * intimidating_fang;'),
 ('conditional ability reductions dropped', HC, '            get_conditional_ability_damage_reduction(\n                state,\n                attacking_player,\n                attacker,', '            0 * get_conditional_ability_damage_reduction(\n                state,\n                attacking_player,\n                attacker,'),
 ('Coordinated Unit dropped', HC, '            get_coordinated_unit_reduction(state, attacking_player, defending_player, defender, true),', '            0 * get_coordinated_unit_reduction(state, attacking_player, defending_player, defender, true),'),
 ('Disguise dropped', HC, '        && !defender.prevent_first_attack_damage_used', '        && !defender.prevent_first_attack_damage_used && false'),
 ('coin prevention dropped', HC, '            (0.5 * first as f64, 0.5 * later as f64)', '            (first as f64, later as f64)'),
 ('coin reduction dropped', HC, '            let (heads_first, heads_later) = hit(base_damage.saturating_sub(amount));', '            let (heads_first, heads_later) = hit(base_damage + 0 * amount);'),
 ('coin cut after Weakness (the rules order)', HC, '            let (heads_first, heads_later) = hit(base_damage.saturating_sub(amount));', '            let (heads_first, heads_later) = { let (f, l) = hit(base_damage); (f.saturating_sub(amount), l.saturating_sub(amount)) };'),
 ('ignores-Weakness text dropped', HC, '    let weakness_applies = hit == DefenderHit::Active && !attack_effect_ignores_weakness(context);', '    let weakness_applies = hit == DefenderHit::Active;'),
 ('ignores-effects text dropped', HC, '    let skip_target_effects = hit == DefenderHit::Active && attack_ignores_opponent_active_effects(context);', '    let skip_target_effects = false;'),
 ('Poncho dropped', HC, '|| (attacking_player != defending_player && has_tool(defender, CardId::B2147ProtectivePoncho)))', '|| (false && has_tool(defender, CardId::B2147ProtectivePoncho)))'),
 ('Shell Shield dropped', HC, '        && (matches!(ability_effect, Some(CardEffect::PreventDamageWhileBenched))', '        && (false'),
 ('Fang from the victim on a Benched hit', HC, '    let fang_holder_effect = if hit == DefenderHit::Benched {', '    let fang_holder_effect = if false {'),
 ('KD arm uses k value function', PM, 'value_function: Box::new(value_functions::public_clock_effect_kd_value_function),', 'value_function: Box::new(value_functions::public_clock_effect_value_function),'),
 ('kd off on my side', VF, '            public_eval,\n            features.next_attack_reduction,\n            features.defender_modifiers,\n        ),\n        extract_features(', '            public_eval,\n            features.next_attack_reduction,\n            false,\n        ),\n        extract_features('),
 ('kd off on the opponent side', VF, '            public_eval,\n            features.next_attack_reduction,\n            features.defender_modifiers,\n        ),\n    );', '            public_eval,\n            features.next_attack_reduction,\n            false,\n        ),\n    );'),
 ('KD const switched off', VF, '        bench_attacker_weight: 0.0,\n        defender_modifiers: true,', '        bench_attacker_weight: 0.0,\n        defender_modifiers: false,'),
 ('board form instead of evolved form', VF, '            let targets = targets.get_or_insert_with(|| evolution_targets(state, owner, pokemon));\n            to_playable_card(&targets[form], false)', '            let _ = (targets, form);\n            pokemon.clone()'),
 ('Active immune counted as 1 turn', VF, '        let Some(price) = pricer.price(active, VictimPlace::Active) else {', '        let Some(price) = pricer.price(active, VictimPlace::Active).or(Some(KdPrice { ko_turns: 1.0, slot: threat.slot, extra: 0 })) else {'),
 ('immune benched victim skipped', VF, '        .collect::<Option<_>>()?;', '        .flatten()\n        .collect::<Vec<_>>();'),
 ('early return at 3 points dropped', VF, '    if points >= 3 {\n        return Some(turns);\n    }\n    let promoted', '    let promoted'),
 ('a sniper touches the Active', VF, '            (true, VictimPlace::Active) | (false, VictimPlace::BenchedOnly) => return (0.0, 0.0),', '            (false, VictimPlace::BenchedOnly) => return (0.0, 0.0),'),
 ('snipes-only branch takes Active attacks', VF, '            (true, VictimPlace::Active) | (false, VictimPlace::BenchedOnly) => return (0.0, 0.0),', '            (true, VictimPlace::Active) => return (0.0, 0.0),'),
 ('snipes in the slowest order', VF, '                .reduce(f64::min);', '                .reduce(f64::max);'),
 ('promotions in the quickest order', VF, '            turns\n        })\n        .fold(0.0, f64::max);', '            turns\n        })\n        .fold(f64::INFINITY, f64::min);'),
 ('Bench-only attack gets Weakness', VF, '            (true, _) => (DefenderHit::Benched, c.damage),', '            (true, _) => (DefenderHit::Active, c.damage),'),
 ('defender bonus dropped', VF, '                    + defender_identity_bonus(self.state, attack, victim),', '                    + 0 * defender_identity_bonus(self.state, attack, victim),'),
 ('sentinel on the first hit', VF, '        if later > 0.0 {\n            return Some(KdPrice {', '        if first > 0.0 {\n            return Some(KdPrice {'),
 ('0 HP victim counts a turn', VF, '            return Some(KdPrice { ko_turns: 0.0, slot: self.threat.slot, extra: 0 });', '            return Some(KdPrice { ko_turns: 1.0, slot: self.threat.slot, extra: 0 });'),
 ('cap at 30 dropped', VF, '            Some(turns) => (total_turns + turns).min(30.0),', '            Some(turns) => total_turns + turns,'),
 ('fallback dropped', VF, '                (later > 0.0).then_some((c, first, later))', '                (later > 0.0 && false).then_some((c, first, later))'),
 ('fallback Energy wait dropped', VF, '        let wait = self.extra.saturating_sub(paid[self.slot]);', '        let wait = 0 * self.extra.saturating_sub(paid[self.slot]);'),
 ('fallback Energy counted per victim', VF, '        paid[self.slot] = paid[self.slot].max(self.extra);', '        paid[self.slot] = paid[self.slot];'),
 ("fallback extra ignores the threat's missing", VF, '            extra: fallback.missing - self.threat.missing,', '            extra: fallback.missing,'),
 ('fallback ranked by damage only', VF, '            .min_by(|a, b| a.0.missing.cmp(&b.0.missing).then(b.2.total_cmp(&a.2)))?;', '            .min_by(|a, b| b.2.total_cmp(&a.2))?;'),
 ('attack text not passed', VF, '            attack_effect: attack.effect.as_deref(),', '            attack_effect: None,'),
 ('form sort dropped', VF, '    targets.sort_by_cached_key(|card| card.get_id());', ''),
 ('my clock reads the opponent zones', VF, '        calculate_turns_until_opponent_wins_damage_aware(\n            state,\n            player,\n            public_only,', '        calculate_turns_until_opponent_wins_damage_aware(\n            state,\n            player,\n            true,'),
 ('Bench spill kept on the Active', VF, '                c.damage.saturating_sub(estimated_bench_spill(attack, self.state, self.owner))', '                c.damage.saturating_sub(0 * estimated_bench_spill(attack, self.state, self.owner))'),
 ('Ability bonus dropped', VF, '        Mechanic::ExtraDamageIfOpponentActiveHasAbility { extra_damage } if has_any_in_play_ability(state, victim) => {', '        Mechanic::ExtraDamageIfOpponentActiveHasAbility { extra_damage } if false && has_any_in_play_ability(state, victim) => {'),
 ('coin flipped for direct damage', HC, '    let engine_flips_coin = !context', '    let engine_flips_coin = true || !context'),
]
FILTERS = ['persistent_defender_damage_tests', 'kd_feature_tests', 'kd3_from_get_player']
only = sys.argv[1:]
env = dict(os.environ, CARGO_TARGET_DIR=os.path.join(ROOT, 'target'))
out = open(os.path.join(os.path.dirname(ROOT), 'mutation_results.txt'), 'a')
for name, path, old, new in MUTS:
    if only and name not in only:
        continue
    p = os.path.join(ROOT, path)
    orig = open(p, 'rb').read()
    text = orig.decode()
    # match regardless of CRLF: normalise the file view for the search
    norm = text.replace('\r\n', '\n')
    assert norm.count(old) == 1, (name, norm.count(old))
    crlf = '\r\n' in text
    mutated = norm.replace(old, new)
    if crlf:
        # re-apply original line endings line by line where content is unchanged: simpler to keep the file LF-normalised
        pass
    open(p, 'wb').write(mutated.encode())
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

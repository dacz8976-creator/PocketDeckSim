
/// DRACO_METEOR_cloud.md (Oct 15): what km3's forecast reads for random-target damage, against what the engine deals.
/// Scratch test, appended to players/value_functions.rs in a copy of the engine; run with --nocapture.
#[cfg(test)]
mod draco_meteor_check {
    use super::*;
    use crate::actions::{Action, SimpleAction};
    use crate::card_ids::CardId;
    use crate::database::get_card_by_enum;
    use crate::test_support::get_initialized_game_with_board;
    use strum::IntoEnumIterator;

    fn dragonite() -> PlayedCard {
        PlayedCard::from_id(CardId::A1185Dragonite)
            .with_energy(vec![EnergyType::Water, EnergyType::Lightning, EnergyType::Colorless, EnergyType::Colorless])
    }

    /// Player 0: Hitmonlee (80) Active, Bulbasaur and Hitmonlee on the Bench. Player 1: Dragonite with Draco Meteor paid for.
    fn victims() -> Vec<PlayedCard> {
        vec![PlayedCard::from_id(CardId::A1154Hitmonlee), PlayedCard::from_id(CardId::A1001Bulbasaur), PlayedCard::from_id(CardId::A1154Hitmonlee)]
    }

    #[test]
    fn km3_forecast_v_the_engine() {
        let mut state = State::default();
        state.set_board(victims(), vec![dragonite()]);
        state.turn_count = 5;
        state.current_player = 0;
        let atk = get_card_by_enum(CardId::A1185Dragonite).get_attacks()[0].clone();
        let slot = state.get_active(1).clone();
        let est_km3 = estimated_attack_damage_ex(&atk, &slot, &state, 1, false);
        let est_spread = estimated_attack_damage_ex(&atk, &slot, &state, 1, true);
        println!("DRACO attack {} fixed {} est(spread_aware=false, km3) {} est(spread_aware=true) {}", atk.title, atk.fixed_damage, est_km3, est_spread);
        // km3's clocks: kt_clocks(state, myself, public_eval, effect_aware, reserve_aware, features), as km's value function calls them
        let (opp_wins, me_wins) = kt_clocks(&state, 0, true, true, false, EvalFeatures::KM);
        let (opp_wins_r, me_wins_r) = kt_clocks(&state, 0, true, true, true, EvalFeatures::KM);
        println!("DRACO km3 clock (reserve_aware=false): turns until the opponent wins {opp_wins}, until I win {me_wins}");
        println!("DRACO same clock with reserve_aware=true (spread-aware estimate): {opp_wins_r}, {me_wins_r}");
        let v = public_clock_effect_km_value_function(&state, 0);
        println!("DRACO km3 value of the position for player 0: {v}");
        // Without the Dragonite's Energy (no threat at all), for comparison.
        let mut bare = state.clone();
        bare.set_board(victims(), vec![PlayedCard::from_id(CardId::A1185Dragonite)]);
        println!("DRACO km3 clock with the Dragonite unpowered: {:?}; value {}", kt_clocks(&bare, 0, true, true, false, EvalFeatures::KM), public_clock_effect_km_value_function(&bare, 0));

        // The engine: Draco Meteor from this board, 2000 seeds.
        let (n, mut total, mut active, mut ko_active, mut kos) = (2000u64, 0.0, 0.0, 0u32, 0u32);
        for seed in 0..n {
            let mut game = get_initialized_game_with_board(20_000_015_000 + seed, 1, 6, vec![dragonite()], victims());
            // get_initialized_game_with_board puts `player_board` on side 0; mirror: Dragonite on side 0 attacks side 1.
            let before: Vec<u32> = game.get_state_clone().in_play_pokemon[1].iter().flatten().map(|p| p.get_remaining_hp()).collect();
            let mut st = game.get_state_clone();
            st.current_player = 0;
            game.set_state(st);
            game.apply_action(&Action { actor: 0, action: SimpleAction::Attack(atk.clone()), is_stack: false });
            let after = game.get_state_clone();
            let hp_after: Vec<u32> = (0..3).map(|i| after.in_play_pokemon[1][i].as_ref().map(|p| p.get_remaining_hp()).unwrap_or(0)).collect();
            let lost: Vec<f64> = before.iter().zip(&hp_after).map(|(b, a)| (*b as f64 - *a as f64).max(0.0)).collect();
            total += lost.iter().sum::<f64>();
            active += lost[0];
            ko_active += (hp_after[0] == 0) as u32;
            kos += hp_after.iter().filter(|h| **h == 0).count() as u32;
        }
        println!("DRACO engine over {n} seeds: mean HP lost by the defender's Pokemon {:.1} (Active {:.1}); Active knocked out {:.1}%; knockouts per attack {:.2}",
            total / n as f64, active / n as f64, 100.0 * ko_active as f64 / n as f64, kos as f64 / n as f64);
    }

    /// Every attack in the database whose text deals damage to a randomly chosen Pokemon, with its mechanic and what the
    /// estimate gives with spread_aware off (km3's clocks) and on.
    #[test]
    fn every_random_target_damage_attack() {
        for id in CardId::iter() {
            let card = get_card_by_enum(id);
            let Card::Pokemon(p) = &card else { continue };
            for atk in &p.attacks {
                let Some(text) = atk.effect.as_deref() else { continue };
                let t = text.to_lowercase();
                if !(t.contains("random") && t.contains("damage")) {
                    continue;
                }
                let mech = EFFECT_MECHANIC_MAP.get(text).map(|m| format!("{m:?}")).unwrap_or_else(|| "UNMAPPED".into());
                let slot = PlayedCard::from_id(id).with_energy(atk.energy_required.iter().map(|e| if *e == EnergyType::Colorless { EnergyType::Water } else { *e }).collect());
                let state = State::default();
                println!("RANDOM\t{}\t{}\t{}\t{:?}\t{}\t{}\t{}\t{}\t{}", card.get_id(), card.get_name(), atk.title, atk.energy_required, atk.fixed_damage,
                    estimated_attack_damage_ex(atk, &slot, &state, 0, false), estimated_attack_damage_ex(atk, &slot, &state, 0, true), mech.chars().take(110).collect::<String>(), text);
            }
        }
    }
}

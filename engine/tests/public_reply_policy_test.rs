use deckgym::{
    actions::{Action, SimpleAction},
    observation::{PlayerObservation, RevealedKnowledge},
    players::{ExpectiMiniMaxPlayer, Player, public_clock_effect_value_function},
    State,
};
use rand::{rngs::StdRng, SeedableRng};

fn saved_root() -> (State,u64) {
    let evidence:serde_json::Value=serde_json::from_str(include_str!("fixtures/public_reply_observed.json")).unwrap();
    let s:State=serde_json::from_value(evidence["row"]["state"].clone()).unwrap();
    (s,evidence["row"]["decision_randomness"]["search_seed"].as_u64().unwrap())
}
fn k3(s:&State)->ExpectiMiniMaxPlayer {
    ExpectiMiniMaxPlayer {deck:s.decks[s.current_player].clone(),max_depth:3,write_debug_trees:false,
        value_function:Box::new(public_clock_effect_value_function),opponent_ply:0,consistent_horizon:false,soft_opponent:false}
}
fn is_x_speed(a:&Action)->bool {
    matches!(&a.action,SimpleAction::Play{trainer_card} if trainer_card.name=="X Speed")
}

#[test]
fn recorded_k3_root_starts_a_defense_against_certified_immediate_loss() {
    let (s,seed)=saved_root(); let view=PlayerObservation::from_state(&s,0,&RevealedKnowledge::default());
    let (_,actions)=s.generate_possible_actions(); let chosen=k3(&s).decision_fn(&mut StdRng::seed_from_u64(seed),&view,&actions);
    assert!(actions.contains(&chosen));
    assert!(is_x_speed(&chosen),"expected X Speed to begin the demonstrated retreat defense, got {chosen:?}");
}

#[test]
fn hidden_card_and_own_deck_order_changes_do_not_change_the_defensive_root_choice() {
    let (s,seed)=saved_root();let mut alternate=s.clone();
    alternate.decks[0].cards.reverse();
    alternate.decks[1].cards.reverse();
    alternate.hands[1].reverse();
    let (_,actions)=s.generate_possible_actions();
    let views=[PlayerObservation::from_state(&s,0,&Default::default()),PlayerObservation::from_state(&alternate,0,&Default::default())];
    assert_eq!(views[0],views[1]);
    for view in views {
        for search_seed in [seed,seed^1,0,1,97] {
            let chosen=k3(&s).decision_fn(&mut StdRng::seed_from_u64(search_seed),&view,&actions);
            assert!(is_x_speed(&chosen),"defense cannot depend on sampled deck order: {chosen:?}");
        }
    }
}

#[test]
fn diagnostic_raw_state_entry_does_not_silently_claim_public_provenance() {
    let (s,seed)=saved_root();let (_,actions)=s.generate_possible_actions();
    let chosen=k3(&s).decide_omniscient(&mut StdRng::seed_from_u64(seed),&s,&actions);
    assert!(matches!(&chosen.action,SimpleAction::Attack(a) if a.title=="Thunderclaw"));
}

#[test]
fn immediate_winning_attack_is_kept_when_defender_is_no_longer_protected() {
    let (s,seed)=saved_root();let mut fixture=serde_json::to_value(&s).unwrap();
    fixture["in_play_pokemon"][1][0]["effects"]=serde_json::json!([]);
    let s:State=serde_json::from_value(fixture).unwrap();
    assert_eq!(s.get_active(1).get_remaining_hp(),90);
    let view=PlayerObservation::from_state(&s,0,&Default::default());let (_,actions)=s.generate_possible_actions();
    for depth in [2,3] {
        let mut bot=k3(&s);bot.max_depth=depth;
        let chosen=bot.decision_fn(&mut StdRng::seed_from_u64(seed),&view,&actions);
        assert!(matches!(&chosen.action,SimpleAction::Attack(a) if a.title=="Thunderclaw"),"immediate win must outrank retreat: {chosen:?}");
        let(p,m)=deckgym::actions::try_forecast_action(&s,&chosen).unwrap().into_branches();
        assert_eq!(p,vec![1.0]);
        for mutation in m {let mut result=s.clone();mutation(&mut StdRng::seed_from_u64(17),&mut result,&chosen);assert_eq!(result.winner,Some(deckgym::state::GameOutcome::Win(0)));}
    }
}

#[test]
fn consistent_horizon_search_also_uses_the_public_loss_witness() {
    let (s,seed)=saved_root();let view=PlayerObservation::from_state(&s,0,&Default::default());let (_,actions)=s.generate_possible_actions();
    for opponent_budget in [1,3] {
        let mut bot=k3(&s);bot.consistent_horizon=true;bot.opponent_ply=opponent_budget;
        let chosen=bot.decision_fn(&mut StdRng::seed_from_u64(seed),&view,&actions);
        assert!(is_x_speed(&chosen),"consistent horizon should retain the demonstrated defense: {chosen:?}");
    }
}

#[test]
fn defense_is_completed_across_fresh_observed_decisions() {
    let (mut s,seed)=saved_root();
    for step in 0..2 {
        let view=PlayerObservation::from_state(&s,0,&Default::default());let (_,actions)=s.generate_possible_actions();
        let chosen=k3(&s).decision_fn(&mut StdRng::seed_from_u64(seed+step),&view,&actions);
        assert!(actions.contains(&chosen));
        if step==0 {assert!(is_x_speed(&chosen),"defense starts with X Speed: {chosen:?}");}
        else {assert!(matches!(chosen.action,SimpleAction::Retreat(3)),"fresh decision must complete the retreat: {chosen:?}");}
        let(p,m)=deckgym::actions::try_forecast_action(&s,&chosen).unwrap().into_branches();assert_eq!(p,vec![1.0]);
        m.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(17),&mut s,&chosen);
    }
    assert_eq!(s.get_active(0).get_remaining_hp(),70);
}

#[test]
fn constructed_cursed_jewel_threat_is_defended_across_fresh_observations() {
    // Constructed extension of the saved root, not a replay of the Sableye video. Zapdos ex
    // at 30 HP concedes the winning two points to Cursed Jewel. The healthy benched Kecleon
    // concedes only one point, so X Speed -> Retreat(3) avoids that immediate winning reply.
    let (mut root, saved_seed) = saved_root();
    root.in_play_pokemon[1][0] = Some(
        deckgym::models::PlayedCard::from_id(deckgym::card_ids::CardId::B3b041MegaSableyeEx)
            .with_energy(vec![deckgym::models::EnergyType::Darkness; 2]),
    );
    assert_eq!(root.points, [2, 1]);
    assert_eq!(root.get_active(0).get_remaining_hp(), 30);
    assert_eq!(root.in_play_pokemon[0][3].as_ref().unwrap().get_remaining_hp(), 70);
    let mut hidden = root.clone();
    hidden.decks[0].cards.reverse();
    hidden.decks[1].cards.reverse();
    hidden.hands[1].reverse();
    assert_eq!(
        PlayerObservation::from_state(&root, 0, &Default::default()),
        PlayerObservation::from_state(&hidden, 0, &Default::default()),
    );

    for initial in [&root, &hidden] {
        for depth in [2, 3, 4] {
            for seed in [saved_seed, saved_seed ^ 1, 0, 1, 97] {
                let mut state = initial.clone();
                for step in 0..2 {
                    let view = PlayerObservation::from_state(&state, 0, &Default::default());
                    let (_, actions) = state.generate_possible_actions();
                    let mut bot = k3(&state);
                    bot.max_depth = depth;
                    let chosen = bot.decision_fn(&mut StdRng::seed_from_u64(seed), &view, &actions);
                    assert!(actions.contains(&chosen));
                    if step == 0 {
                        assert!(is_x_speed(&chosen), "depth {depth}, seed {seed}: {chosen:?}");
                    } else {
                        assert!(matches!(chosen.action, SimpleAction::Retreat(3)),
                            "fresh decision must complete the defense: {chosen:?}");
                    }
                    let (p, mut branches) = deckgym::actions::try_forecast_action(&state, &chosen)
                        .unwrap().into_branches();
                    assert_eq!(p, vec![1.0]);
                    assert_eq!(branches.len(), 1);
                    branches.pop().unwrap()(&mut StdRng::seed_from_u64(17), &mut state, &chosen);
                }
                assert_eq!(state.get_active(0).get_remaining_hp(), 70);
                assert_eq!(state.points, [2, 1]);
            }
        }
    }
}

use deckgym::{
    actions::{try_forecast_action, Action, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    effects::CardEffect,
    models::{Card, EnergyType, PlayedCard},
    observation::PlayerObservation,
    players::public_reply::{assess_observation, PublicReplyAssessment, UnsupportedReason},
    Deck, State,
};
use rand::{rngs::StdRng,SeedableRng};

fn observed(which:&str)->State {
    let v:serde_json::Value=serde_json::from_str(include_str!("fixtures/public_reply_observed.json")).unwrap();
    serde_json::from_value(if which=="root" {v["row"]["state"].clone()} else {v["opponent_turn_state"].clone()}).unwrap()
}
fn assess(s:&State,observer:usize)->PublicReplyAssessment {
    assess_observation(&PlayerObservation::from_state(s,observer,&Default::default()))
}
fn is_proven(a:&PublicReplyAssessment)->bool {matches!(a,PublicReplyAssessment::ProvenImmediateWin{..})}
fn one(s:&State,a:&Action)->State {
    assert!(s.generate_possible_actions().1.contains(a),"fixture action must be offered: {a:?}");
    let(p,m)=try_forecast_action(s,a).unwrap().into_branches();assert_eq!(p,vec![1.0]);assert_eq!(m.len(),1);
    let mut t=s.clone();m.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(53),&mut t,a);t
}
fn plain(actor:usize)->State {
    let mut s=State::new(&Deck::default(),&Deck::default());s.turn_count=13;s.current_player=actor;
    let attacker=vec![PlayedCard::from_id(CardId::A1129MewtwoEx).with_energy(vec![EnergyType::Psychic;4])];
    let target=vec![PlayedCard::from_id(CardId::A1001Bulbasaur)];
    if actor==0{s.set_board(attacker,target);}else{s.set_board(target,attacker);}
    s.points[actor]=2;s
}

#[test]
fn a_private_draw_frame_stays_concealed_until_a_fresh_free_turn_observation() {
    let mut s=observed("leaf");
    assert!(matches!(assess(&s,0),PublicReplyAssessment::NotApplicable{reason:UnsupportedReason::PrivateChoice}));
    let forced=s.generate_possible_actions().1;assert_eq!(forced.len(),1);s=one(&s,&forced[0]);
    let verdict=assess(&s,0);
    let PublicReplyAssessment::ProvenImmediateWin{action,..}=verdict else {panic!("expected recorded winning reply: {verdict:?}")};
    assert!(matches!(action.action,SimpleAction::Attack(a) if a.title=="Hit and Hide"));
}

#[test]
fn actual_x_speed_retreat_handoff_has_no_certified_winning_reply() {
    let mut s=observed("root");
    let xs=s.generate_possible_actions().1.into_iter().find(|a|matches!(&a.action,SimpleAction::Play{trainer_card} if trainer_card.name=="X Speed")).unwrap();
    s=one(&s,&xs);s=one(&s,&Action{actor:0,action:SimpleAction::Retreat(3),is_stack:false});
    assert_eq!(s.get_active(0).get_remaining_hp(),70);
    s=one(&s,&Action{actor:0,action:SimpleAction::EndTurn,is_stack:false});
    assert_eq!(s.current_player,1);
    let forced=s.generate_possible_actions().1;assert_eq!(forced.len(),1);s=one(&s,&forced[0]);
    let verdict=assess(&s,0);
    assert!(matches!(verdict,PublicReplyAssessment::NoCertifiedWitness{..}),"absence of a witness is not a safety proof: {verdict:?}");
}

#[test]
fn hidden_world_substitutions_and_full_or_empty_draw_counts_do_not_create_certificates() {
    let s=observed("leaf");
    for hand_count in [0,9,10] {
        for deck_count in [0,1,5] {
            let mut t=s.clone();t.hands[1]=vec![get_card_by_enum(CardId::PA001Potion);hand_count];
            t.decks[1].cards=vec![get_card_by_enum(CardId::A1129MewtwoEx);deck_count];
            t.decks[0].cards.reverse();
            let forced=t.generate_possible_actions().1;assert_eq!(forced.len(),1);t=one(&t,&forced[0]);
            assert!(is_proven(&assess(&t,0)),"fixed attached-Energy attack ignores hidden identities; hand={hand_count}, deck={deck_count}");
        }
    }
}

#[test]
fn paid_fixed_damage_replies_work_in_both_seats_without_future_energy() {
    for actor in [0,1] {
        let mut v=serde_json::to_value(plain(actor)).unwrap();v["decks"][actor]["energy_types"]=serde_json::json!([]);let mut s:State=serde_json::from_value(v).unwrap();
        assert!(is_proven(&assess(&s,1-actor)));
        s.in_play_pokemon[actor][0].as_mut().unwrap().attached_energy.clear();
        assert!(!is_proven(&assess(&s,1-actor)),"future Energy cannot pay a reply now");
    }
}

#[test]
fn full_protection_and_nonterminal_branches_do_not_become_winning_certificates() {
    let mut s=plain(1);s.in_play_pokemon[0][0].as_mut().unwrap().add_effect(CardEffect::PreventAllDamageAndEffects,1);
    assert!(!is_proven(&assess(&s,0)));
    let mut s=observed("leaf");s.in_play_pokemon[0][0]=Some(PlayedCard::from_id(CardId::PB024MegaLatiosEx));
    assert!(!is_proven(&assess(&s,0)));
}

#[test]
fn unclassified_tools_abilities_and_coin_statuses_force_abstention() {
    let s=plain(1);
    let mut tool=s.clone();tool.in_play_pokemon[0][0].as_mut().unwrap().attached_tools.push(get_card_by_enum(CardId::A2148RockyHelmet));
    assert!(!is_proven(&assess(&tool,0)));
    let mut ability=s.clone();ability.in_play_pokemon[0][1]=Some(PlayedCard::from_id(CardId::B3025Victini));
    assert!(!is_proven(&assess(&ability,0)));
    let mut v=serde_json::to_value(&s).unwrap();v["in_play_pokemon"][1][0]["confused"]=true.into();let confused:State=serde_json::from_value(v).unwrap();
    assert!(!is_proven(&assess(&confused,0)));
}

#[test]
fn random_energy_and_hidden_copy_families_are_not_silently_admitted() {
    for id in [CardId::A1a018GyaradosEx,CardId::B2b030Mew] {
        let mut s=plain(1);s.in_play_pokemon[1][0]=Some(PlayedCard::from_id(id).with_energy(vec![EnergyType::Water,EnergyType::Water,EnergyType::Water,EnergyType::Water,EnergyType::Psychic]));
        s.hands[0]=vec![get_card_by_enum(CardId::A1129MewtwoEx)];
        let verdict=assess(&s,0);assert!(!is_proven(&verdict),"unsupported exactness must remain unknown: {verdict:?}");
    }
}

#[test]
fn private_or_extra_pending_frames_and_setup_are_not_normalized_as_draws() {
    let s=observed("leaf");
    let mut extra=s.clone();extra.move_generation_stack.push((1,vec![SimpleAction::EndTurn]));
    assert!(!is_proven(&assess(&extra,0)));
    let mut private=s.clone();private.move_generation_stack=vec![(1,vec![])];
    assert!(!is_proven(&assess(&private,0)));
    let mut setup=s;setup.turn_count=0;
    assert!(!is_proven(&assess(&setup,0)));
}

#[test]
fn unmapped_printed_ability_is_unsupported_instead_of_treated_as_absent() {
    let s=plain(1);let mut fixture=serde_json::to_value(&s).unwrap();
    fixture["in_play_pokemon"][0][0]["card"]["Pokemon"]["ability"]=serde_json::json!({"title":"Future passive","effect":"Unclassified test-only passive effect."});
    let unclassified:State=serde_json::from_value(fixture).unwrap();
    assert!(!is_proven(&assess(&unclassified,0)));
}

#[test]
fn a_supported_winning_attack_is_not_discarded_because_another_attack_is_unsupported() {
    let mut s=plain(1);s.in_play_pokemon[1][0]=Some(PlayedCard::from_id(CardId::A1a032MewEx).with_energy(vec![EnergyType::Psychic;3]));
    s.in_play_pokemon[0][0]=Some(PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(60));
    let verdict=assess(&s,0);assert!(is_proven(&verdict),"Psychic Shot can win despite unqualified Genome Hacking: {verdict:?}");
}

#[test]
fn certified_witnesses_match_actual_attack_terminal_branches() {
    for actor in [0,1] {
        for shield in [false,true] {
            for energy_count in [0,1,2,3,4] {
                let mut s=plain(actor);s.in_play_pokemon[actor][0].as_mut().unwrap().attached_energy=vec![EnergyType::Psychic;energy_count];
                if shield {s.in_play_pokemon[1-actor][0].as_mut().unwrap().add_effect(CardEffect::PreventAllDamageAndEffects,1);}
                if let PublicReplyAssessment::ProvenImmediateWin{action,positive_branches,probability_sum}=assess(&s,1-actor) {
                    assert!(matches!(&action.action,SimpleAction::Attack(a) if a.title=="Psydrive"),"both-seat differential must exercise typed self discard: {action:?}");
                    let (p,m)=try_forecast_action(&s,&action).unwrap().into_branches();
                    assert_eq!(p.len(),positive_branches);assert!((p.iter().sum::<f64>()-probability_sum).abs()<1e-12);
                    for mutation in m {let mut result=s.clone();mutation(&mut StdRng::seed_from_u64(7),&mut result,&action);assert_eq!(result.winner,Some(deckgym::state::GameOutcome::Win(actor)));assert_eq!(result.get_active(actor).attached_energy.len(),2);}
                }
            }
        }
    }
    // Fixed damage also certifies the no-Pokemon terminal route before three points.
    for actor in [0,1] {
        let mut s=plain(actor);s.points[actor]=0;
        s.in_play_pokemon[actor][0]=Some(PlayedCard::from_id(CardId::A1a032MewEx).with_energy(vec![EnergyType::Psychic]));
        s.in_play_pokemon[1-actor][0]=Some(PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(60));
        let PublicReplyAssessment::ProvenImmediateWin{action,..}=assess(&s,1-actor) else {panic!("fixed damage must qualify against the last Pokemon")};
        assert!(matches!(&action.action,SimpleAction::Attack(a) if a.effect.is_none()));
        let (p,m)=try_forecast_action(&s,&action).unwrap().into_branches();assert_eq!(p,vec![1.0]);
        let mut result=s.clone();m.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(19),&mut result,&action);
        assert_eq!(result.winner,Some(deckgym::state::GameOutcome::Win(actor)));assert_eq!(result.points[actor],1);
    }
    let mut s=observed("leaf");let(_,forced)=s.generate_possible_actions();assert_eq!(forced.len(),1);s=one(&s,&forced[0]);
    let PublicReplyAssessment::ProvenImmediateWin{action,positive_branches,probability_sum}=assess(&s,0) else {panic!("natural public reply must qualify")};
    let (p,m)=try_forecast_action(&s,&action).unwrap().into_branches();assert_eq!(p,vec![0.5,0.5]);assert_eq!(positive_branches,2);assert_eq!(probability_sum,1.0);
    for mutation in m {let mut result=s.clone();mutation(&mut StdRng::seed_from_u64(9),&mut result,&action);assert_eq!(result.winner,Some(deckgym::state::GameOutcome::Win(1)));}
}

#[test]
fn unstable_or_unknown_boards_cannot_supply_attack_proofs() {
    let s=plain(1);
    let mut missing=s.clone();missing.in_play_pokemon[0][0]=None;
    assert!(!is_proven(&assess(&missing,0)));
    let mut knocked_out=s.clone();knocked_out.in_play_pokemon[0][0]=Some(PlayedCard::from_id(CardId::A1001Bulbasaur).with_damage(70));
    assert!(!is_proven(&assess(&knocked_out,0)));
    let mut terminal_points=s.clone();terminal_points.points[1]=3;
    assert!(!is_proven(&assess(&terminal_points,0)));
    let mut unknown=s.clone();unknown.in_play_pokemon[0][0].as_mut().unwrap().card=Card::Unknown;
    assert!(!is_proven(&assess(&unknown,0)));
    let mut unknown_under=s;unknown_under.in_play_pokemon[0][0].as_mut().unwrap().cards_behind.push(Card::Unknown);
    assert!(!is_proven(&assess(&unknown_under,0)));
}

#[test]
fn stale_hp_caches_are_rejected_without_their_public_source() {
    for field in ["stadium_hp_bonus","ability_hp_bonus"] {
        let mut v=serde_json::to_value(plain(1)).unwrap();v["in_play_pokemon"][0][0][field]=20.into();
        let state:State=serde_json::from_value(v).unwrap();
        assert!(!is_proven(&assess(&state,0)),"unsupported cached HP source: {field}");
    }
}

#[test]
fn raw_id_hooks_cannot_bypass_the_registry_with_missing_ability_metadata() {
    for id in [CardId::A1061Poliwrath,CardId::A1a056Druddigon,CardId::A2b028Pawmot,CardId::A3a052Ferrothorn,CardId::A4a065Zangoose,CardId::B1297Poliwrath,CardId::PA054Pawmot,CardId::B1160DragalgeEx,CardId::B1263DragalgeEx,CardId::B1281DragalgeEx,CardId::B3231DragalgeEx] {
        let mut state=plain(1);state.in_play_pokemon[0][0]=Some(PlayedCard::from_id(id));
        let mut v=serde_json::to_value(state).unwrap();v["in_play_pokemon"][0][0]["card"]["Pokemon"]["ability"]=serde_json::Value::Null;
        let state:State=serde_json::from_value(v).unwrap();
        assert!(!is_proven(&assess(&state,0)),"raw card-ID hook must be explicitly denied: {id:?}");
    }
}

#[test]
fn tool_identity_cannot_hide_a_different_effect_or_invalid_card_kind() {
    for id in [CardId::A2147GiantCape,CardId::A4b320GiantCape,CardId::A4b321GiantCape] {
        let mut state=plain(1);state.in_play_pokemon[0][0].as_mut().unwrap().attached_tools.push(get_card_by_enum(id));
        let valid=serde_json::to_value(state).unwrap();
        let mut effect=valid.clone();effect["in_play_pokemon"][0][0]["attached_tools"][0]["Trainer"]["effect"]=serde_json::json!("Unclassified future Tool effect.");
        assert!(!is_proven(&assess(&serde_json::from_value(effect).unwrap(),0)));
        let mut pokemon=valid.clone();pokemon["in_play_pokemon"][0][0]["attached_tools"][0]=serde_json::to_value(get_card_by_enum(CardId::A1001Bulbasaur)).unwrap();
        assert!(!is_proven(&assess(&serde_json::from_value(pokemon).unwrap(),0)));
        let mut subtype=valid;subtype["in_play_pokemon"][0][0]["attached_tools"][0]["Trainer"]["trainer_card_type"]=serde_json::json!("Item");
        assert!(!is_proven(&assess(&serde_json::from_value(subtype).unwrap(),0)));
    }
}

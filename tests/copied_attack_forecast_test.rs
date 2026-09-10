use deckgym::{
    actions::{try_forecast_action, Action, CoinPaths, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    observation::{hidden_continuation_reason, PlayerObservation, RevealedKnowledge},
    players::{ExpectiMiniMaxPlayer, Player},
    state::GameOutcome,
    test_support::{attack_action, get_initialized_game_with_board},
    Deck, State,
};
use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::{collections::BTreeMap, sync::{Arc, Mutex}};

fn card(id: CardId) -> Card { get_card_by_enum(id) }
fn attack(actor: usize, id: CardId, index: usize) -> Action {
    Action { actor, action: attack_action(id, index), is_stack: false }
}
fn mew(id: CardId) -> PlayedCard {
    PlayedCard::from_id(id).with_energy(vec![EnergyType::Psychic, EnergyType::Fire])
}
fn state(actor: usize, id: CardId) -> State {
    let mut s = State::new(&Deck::default(), &Deck::default());
    s.turn_count = 10; s.current_player = actor;
    let ours = vec![mew(id)];
    let theirs = vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_damage(130)];
    if actor == 0 { s.set_board(ours, theirs); } else { s.set_board(theirs, ours); }
    s.points[actor] = 2;
    s.hands[1-actor] = vec![card(CardId::A1001Bulbasaur)];
    s.decks[1-actor].cards = vec![card(CardId::A1002Ivysaur)];
    s
}
fn close(a: f64, b: f64) { assert!((a-b).abs() < 1e-12, "{a} != {b}"); }
fn branches(s: &State, a: &Action) -> Vec<(f64, State)> {
    let (p,m) = try_forecast_action(s,a).unwrap().into_branches();
    close(p.iter().sum(),1.0);
    p.into_iter().zip(m).map(|(p,m)| {
        let mut t=s.clone(); m(&mut StdRng::seed_from_u64(71), &mut t,a); (p,t)
    }).collect()
}
fn queued(s: &State, actor: usize) -> Action {
    let (chooser, actions) = s.generate_possible_actions();
    assert_eq!(chooser,actor); assert_eq!(actions.len(),1);
    assert!(actions[0].is_stack); assert!(matches!(actions[0].action, SimpleAction::Attack(_)));
    actions[0].clone()
}
fn title(a: &Action) -> String {
    let SimpleAction::Attack(a)=&a.action else {panic!("expected attack")}; a.title.clone()
}
fn play(actor: usize, id: CardId) -> Action {
    let Card::Trainer(trainer_card)=card(id) else {panic!("expected trainer")};
    Action {actor,action:SimpleAction::Play{trainer_card},is_stack:false}
}

#[test]
fn memory_exposes_half_win_mass_after_forced_copy_in_both_seats() {
    for actor in [0,1] {
        let s=state(actor,CardId::B2b030Mew); let a=attack(actor,CardId::B2b030Mew,0);
        assert!(s.generate_possible_actions().1.contains(&a));
        let first=branches(&s,&a); assert_eq!(first.len(),2);
        let mut win=0.0; let mut live=0.0;
        for (p,t) in first {
            close(p,0.5); assert!(t.winner.is_none());
            assert_eq!(t.get_active(1-actor).get_remaining_hp(),50);
            let forced=queued(&t,actor);
            for (q,u) in branches(&t,&forced) {
                match u.winner {
                    Some(GameOutcome::Win(w)) => {assert_eq!(w,actor); win+=p*q;},
                    None => {assert_eq!(u.get_active(1-actor).get_remaining_hp(),10); live+=p*q;},
                    other=>panic!("unexpected {other:?}"),
                }
            }
        }
        close(win,0.5); close(live,0.5);
    }
}

#[test]
fn selected_memory_branch_never_resamples_or_consumes_mutation_rng() {
    let s=state(0,CardId::B2b030Mew); let a=attack(0,CardId::B2b030Mew,0);
    let mut expected=None;
    for seed in [0,1,2,17,99] {
        let branches=try_forecast_action(&s,&a).unwrap().into_branches_with_coin_paths();
        let mut selected=Vec::new();
        for (p,m,coins) in branches {
            assert!(matches!(coins,CoinPaths::None));
            let mut t=s.clone(); let mut rng=StdRng::seed_from_u64(seed); let mut untouched=rng.clone();
            m(&mut rng,&mut t,&a); assert_eq!(rng.next_u64(),untouched.next_u64());
            close(p,0.5); selected.push(queued(&t,0));
        }
        assert_eq!(selected.len(),2);
        if let Some(ref old)=expected {assert_eq!(old,&selected);} else {expected=Some(selected);}
    }
}

#[test]
fn all_memory_prints_preserve_current_distinct_attack_pool_and_exclude_copy_sources() {
    // This binds the existing modeled deduplication law, not an independently verified Pocket rule.
    for id in [CardId::B2b030Mew,CardId::B2b085Mew,CardId::B2b086Mew] {
        let mut s=state(0,id);
        s.hands[1]=vec![card(CardId::A1001Bulbasaur),card(CardId::PA001Potion),card(id)];
        s.decks[1].cards=vec![card(CardId::A1001Bulbasaur),card(CardId::A1002Ivysaur)];
        let a=attack(0,id,0); let mut masses=BTreeMap::new();
        for (p,t) in branches(&s,&a) {*masses.entry(title(&queued(&t,0))).or_insert(0.0)+=p;}
        assert_eq!(masses.len(),2); close(masses["Vine Whip"],0.5); close(masses["Razor Leaf"],0.5);
    }
}

#[test]
fn no_eligible_source_is_one_deterministic_no_effect_branch() {
    let mut s=state(0,CardId::B2b030Mew);
    s.hands[1]=vec![card(CardId::PA001Potion)]; s.decks[1].cards=vec![card(CardId::B2b030Mew)];
    let a=attack(0,CardId::B2b030Mew,0); let result=branches(&s,&a);
    assert_eq!(result.len(),1); close(result[0].0,1.0);
    assert!(result[0].1.move_generation_stack.is_empty());
    assert_eq!(result[0].1.get_active(1).get_remaining_hp(),50);
}

#[test]
fn real_hand_scope_makes_exhausted_deck_memory_forecastable_without_hidden_cards() {
    let mut g=get_initialized_game_with_board(1,0,10,vec![mew(CardId::B2b030Mew)],vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx)]);
    let mut s=g.get_state_clone(); s.hands[0]=vec![card(CardId::PA003HandScope)];
    s.hands[1]=vec![card(CardId::A1001Bulbasaur),card(CardId::A1002Ivysaur)]; s.decks[1].cards.clear(); g.set_state(s);
    let a=attack(0,CardId::B2b030Mew,0);
    assert!(hidden_continuation_reason(g.observation(0).visible_state(),&a).is_some());
    let reveal=play(0,CardId::PA003HandScope); assert!(g.get_state_clone().generate_possible_actions().1.contains(&reveal));
    g.apply_action(&reveal);
    let view=g.observation(0); let known=view.search_state(&mut StdRng::seed_from_u64(21));
    assert_eq!(view.revealed.opponent_hand.len(),2);
    assert!(hidden_continuation_reason(&known,&a).is_none());
    assert_eq!(branches(&known,&a).len(),2);
}

#[test]
fn concealed_sources_have_identical_observations_and_search_stops_unpriced() {
    for actor in [0,1] {
        let s=state(actor,CardId::B2b030Mew); let mut alternate=s.clone();
        alternate.hands[1-actor]=vec![card(CardId::A1033Charmander)];
        alternate.decks[1-actor].cards=vec![card(CardId::A1036CharizardEx)];
        let a=attack(actor,CardId::B2b030Mew,0);
        let view=PlayerObservation::from_state(&s,actor,&RevealedKnowledge::default());
        assert_eq!(view,PlayerObservation::from_state(&alternate,actor,&RevealedKnowledge::default()));
        let leaves=Arc::new(Mutex::new(Vec::new())); let saved=Arc::clone(&leaves);
        let mut bot=ExpectiMiniMaxPlayer {deck:Deck::default(),max_depth:3,opponent_ply:0,consistent_horizon:false,soft_opponent:false,write_debug_trees:false,
            value_function:Box::new(move |s,_| {saved.lock().unwrap().push(s.clone());0.0})};
        assert!(hidden_continuation_reason(view.visible_state(),&a).is_some());
        assert_eq!(bot.decision_fn(&mut StdRng::seed_from_u64(91),&view,&[a.clone()]),a);
        let leaves=leaves.lock().unwrap(); assert!(!leaves.is_empty());
        for leaf in leaves.iter() {
            assert!(leaf.hands[1-actor].iter().all(|c| *c==Card::Unknown));
            assert!(leaf.decks[1-actor].cards.iter().all(|c| *c==Card::Unknown));
            assert!(leaf.move_generation_stack.is_empty()); assert_eq!(leaf.get_active(1-actor).get_remaining_hp(),50);
        }
    }
}

#[test]
fn partial_hand_reveal_does_not_authorize_unknown_deck_continuation() {
    let s=state(0,CardId::B2b030Mew); let a=attack(0,CardId::B2b030Mew,0);
    let known=RevealedKnowledge {opponent_hand:s.hands[1].clone(),..Default::default()};
    let view=PlayerObservation::from_state(&s,0,&known);
    assert!(!view.visible_state().hands[1].contains(&Card::Unknown));
    assert!(view.visible_state().decks[1].cards.contains(&Card::Unknown));
    assert!(hidden_continuation_reason(view.visible_state(),&a).is_some());
}

#[test]
fn genome_hacking_keeps_all_public_choices_in_one_nonrandom_branch() {
    for actor in [0,1] {
        let mut s=state(actor,CardId::A1a032MewEx);
        s.in_play_pokemon[1-actor][0]=Some(PlayedCard::from_id(CardId::A1036CharizardEx));
        s.in_play_pokemon[actor][0].as_mut().unwrap().attached_energy.push(EnergyType::Metal);
        let a=attack(actor,CardId::A1a032MewEx,1);
        assert!(s.generate_possible_actions().1.contains(&a));
        let result=branches(&s,&a); assert_eq!(result.len(),1);
        let (chooser,actions)=result[0].1.generate_possible_actions();assert_eq!(chooser,actor);assert_eq!(actions.len(),2);
        assert!(actions.iter().all(|a| a.is_stack && matches!(a.action,SimpleAction::Attack(_))));
    }
}

#[test]
fn memory_preserves_will_for_copied_binomial_attack_without_false_victini_prompt() {
    let mut g=get_initialized_game_with_board(13,0,10,vec![mew(CardId::B2b030Mew),PlayedCard::from_id(CardId::B3025Victini)],vec![PlayedCard::from_id(CardId::PB024MegaLatiosEx).with_energy(vec![EnergyType::Psychic,EnergyType::Psychic,EnergyType::Water])]);
    let mut s=g.get_state_clone();s.hands[0]=vec![card(CardId::A4156Will)];s.hands[1]=vec![card(CardId::B1182Pidgeot)];s.decks[1].cards.clear();g.set_state(s);
    g.apply_action(&play(0,CardId::A4156Will));
    g.apply_action(&attack(0,CardId::B2b030Mew,0));
    let s=g.get_state_clone();assert!(s.pending_attack_coin_choice.is_none());
    let copied=queued(&s,0);assert_eq!(title(&copied),"Twister");
    let mut counts=[0.0;3];
    for (p,t) in branches(&s,&copied) {
        assert!(t.pending_attack_coin_choice.is_none(),"Psychic Mew cannot use Fire-only Victory Star");
        assert_eq!(t.get_active(1).get_remaining_hp(),100);
        counts[t.discard_energies[1].len()]+=p;
    }
    close(counts[0],0.0);close(counts[1],0.5);close(counts[2],0.5);
    g.apply_action(&copied);
    let committed=g.get_state_clone();assert!(committed.pending_attack_coin_choice.is_none());
    assert_eq!(committed.get_active(1).get_remaining_hp(),100);
    assert!([1,2].contains(&committed.discard_energies[1].len()));
}

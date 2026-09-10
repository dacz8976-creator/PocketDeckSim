use deckgym::{
    actions::{try_forecast_action, Action, CoinPaths, CoinSeq, Outcomes, SimpleAction},
    card_ids::CardId,
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard},
    state::GameOutcome,
    test_support::{attack_action, get_initialized_game_with_board},
    Deck, State,
};
use rand::{rngs::StdRng, RngCore, SeedableRng};
use std::collections::BTreeMap;

fn board(actor: usize, ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> State {
    let mut s=State::new(&Deck::default(), &Deck::default());
    s.turn_count=10; s.current_player=actor;
    if actor==0 {s.set_board(ours,theirs);} else {s.set_board(theirs,ours);}
    s
}
fn attack(actor: usize, id: CardId) -> Action {Action{actor,action:attack_action(id,0),is_stack:false}}
fn close(a:f64,b:f64) {assert!((a-b).abs()<1e-12,"{a} != {b}");}
fn total(s:&State,owner:usize)->usize {s.enumerate_in_play_pokemon(owner).map(|(_,p)|p.attached_energy.len()).sum::<usize>()+s.discard_energies[owner].len()}
fn forecast(s:&State,a:&Action)->Outcomes {try_forecast_action(s,a).unwrap()}
fn outcomes(s:&State,a:&Action)->Vec<(f64,State)> {
    let (p,m)=forecast(s,a).into_branches();close(p.iter().sum(),1.0);
    p.into_iter().zip(m).map(|(p,m)|{let mut t=s.clone();m(&mut StdRng::seed_from_u64(0),&mut t,a);(p,t)}).collect()
}
fn energy_key(s:&State,owner:usize)->Vec<EnergyType> {let mut e=s.discard_energies[owner].clone();e.sort();e}
fn sponge()->PlayedCard {PlayedCard::from_id(CardId::PB024MegaLatiosEx)}
fn entei()->PlayedCard {PlayedCard::from_id(CardId::A4033Entei).with_energy(vec![EnergyType::Fire,EnergyType::Fire,EnergyType::Water,EnergyType::Psychic])}

#[test]
fn mawile_coin_and_energy_choice_have_exact_terminal_mass_in_both_seats() {
    for actor in [0,1] {
        let mut s=board(actor,vec![PlayedCard::from_id(CardId::A1178Mawile).with_energy(vec![EnergyType::Metal])],vec![PlayedCard::from_id(CardId::B1a034Reuniclus).with_energy(vec![EnergyType::Psychic,EnergyType::Water]).with_damage(80)]);
        s.points[actor]=2;assert_eq!(s.get_active(1-actor).get_remaining_hp(),40);
        let a=attack(actor,CardId::A1178Mawile);assert!(s.generate_possible_actions().1.contains(&a));
        let mut win=0.0;let mut live=0.0;
        for (p,t) in outcomes(&s,&a) {
            for owner in [0,1] {assert_eq!(total(&s,owner),total(&t,owner));}
            match t.winner {Some(GameOutcome::Win(w))=>{assert_eq!(w,actor);win+=p;},None=>{assert_eq!(t.get_active(1-actor).get_remaining_hp(),20);live+=p;},x=>panic!("unexpected {x:?}")}
        }
        close(win,0.25);close(live,0.75);
    }
}

#[test]
fn mawile_conditioned_heads_preserves_physical_weighting_and_discard_ledger() {
    let s=board(0,vec![PlayedCard::from_id(CardId::A1178Mawile).with_energy(vec![EnergyType::Metal])],vec![sponge().with_energy(vec![EnergyType::Psychic,EnergyType::Psychic,EnergyType::Water])]);
    let a=attack(0,CardId::A1178Mawile);
    let conditional=forecast(&s,&a).condition_on_coin_sequence(&CoinSeq(vec![true])).unwrap();
    let (p,m)=conditional.into_branches();close(p.iter().sum(),1.0);let mut mass=BTreeMap::new();
    for (p,m) in p.into_iter().zip(m) {let mut t=s.clone();m(&mut StdRng::seed_from_u64(6),&mut t,&a);assert_eq!(total(&s,1),total(&t,1));*mass.entry(energy_key(&t,1)).or_insert(0.0)+=p;}
    assert_eq!(mass.len(),2);close(mass[&vec![EnergyType::Psychic]],2.0/3.0);close(mass[&vec![EnergyType::Water]],1.0/3.0);
}

#[test]
fn entei_tails_refinements_preserve_coin_identity_and_hypergeometric_weights() {
    let s=board(0,vec![entei()],vec![sponge()]);let a=attack(0,CardId::A4033Entei);
    let branches=forecast(&s,&a).into_branches_with_coin_paths();let mut heads=0.0;let mut tails=0.0;
    for (p,m,c) in branches {
        let mut t=s.clone();let mut rng=StdRng::seed_from_u64(55);let mut untouched=rng.clone();m(&mut rng,&mut t,&a);
        assert_eq!(rng.next_u64(),untouched.next_u64(),"a refined branch cannot resample Energy");
        assert_eq!(t.get_active(1).get_remaining_hp(),70);assert_eq!(total(&s,0),total(&t,0));
        match c {CoinPaths::Exact(paths) if paths==vec![CoinSeq(vec![true])]=>{heads+=p;assert!(t.discard_energies[0].is_empty());},CoinPaths::Exact(paths) if paths==vec![CoinSeq(vec![false])]=>{tails+=p;assert_eq!(t.discard_energies[0].len(),2);},c=>panic!("lost coin provenance {c:?}")}
    }
    close(heads,0.5);close(tails,0.5);
    let conditioned=forecast(&s,&a).condition_on_coin_sequence(&CoinSeq(vec![false])).unwrap();let (p,m)=conditioned.into_branches();let mut mass=BTreeMap::new();
    for(p,m)in p.into_iter().zip(m){let mut t=s.clone();m(&mut StdRng::seed_from_u64(0),&mut t,&a);*mass.entry(energy_key(&t,0)).or_insert(0.0)+=p;}
    let mut expected=BTreeMap::new();for (mut k,v) in [(vec![EnergyType::Fire,EnergyType::Fire],1.0/6.0),(vec![EnergyType::Fire,EnergyType::Water],1.0/3.0),(vec![EnergyType::Fire,EnergyType::Psychic],1.0/3.0),(vec![EnergyType::Water,EnergyType::Psychic],1.0/6.0)] {k.sort();expected.insert(k,v);}
    assert_eq!(mass.len(),expected.len());for(k,v)in expected{close(mass[&k],v);}
}

#[test]
fn victini_keep_conditions_only_the_coin_and_reroll_retains_both_coin_outcomes() {
    let mut found=false;
    for seed in 0..32 {
        let mut g=get_initialized_game_with_board(seed,0,10,vec![entei(),PlayedCard::from_id(CardId::B3025Victini)],vec![sponge()]);let a=attack(0,CardId::A4033Entei);g.apply_action(&a);let s=g.get_state_clone();
        let pending=s.pending_attack_coin_choice.as_ref().expect("Entei must offer Victory Star");
        assert_eq!(s.get_active(1).get_remaining_hp(),180);assert!(s.discard_energies[0].is_empty());assert_eq!(s.get_active(0).attached_energy.len(),4);
        if pending.flips!=vec![false]{continue;}
        found=true;let keep=Action{actor:0,action:SimpleAction::KeepAttackCoinResults,is_stack:true};assert!(s.generate_possible_actions().1.contains(&keep));let paths=outcomes(&s,&keep);assert_eq!(paths.len(),4,"Keep tails must retain all four Energy multisets");
        for(_,t)in paths{assert_eq!(t.discard_energies[0].len(),2);assert_eq!(t.get_active(1).get_remaining_hp(),70);assert!(t.pending_attack_coin_choice.is_none());assert_eq!(total(&s,0),total(&t,0));}
        let reroll=Action{actor:0,action:SimpleAction::RerollAttackCoins{victory_star_in_play_idx:1},is_stack:true};let mut kept_energy=0.0;let mut lost_energy=0.0;
        for(p,t)in outcomes(&s,&reroll){assert!(t.victory_star_used_this_turn[0]);assert!(t.pending_attack_coin_choice.is_none());match t.discard_energies[0].len(){0=>kept_energy+=p,2=>lost_energy+=p,n=>panic!("discarded {n}")};}
        close(kept_energy,0.5);close(lost_energy,0.5);break;
    }
    assert!(found,"test seeds must contain a tails batch");
}

#[test]
fn will_forces_entei_heads_once_without_forcing_victini_replacement() {
    let mut g=get_initialized_game_with_board(7,0,10,vec![entei(),PlayedCard::from_id(CardId::B3025Victini)],vec![sponge()]);let mut s=g.get_state_clone();let card=get_card_by_enum(CardId::A4156Will);s.hands[0]=vec![card.clone()];g.set_state(s);
    let Card::Trainer(trainer)=card else {panic!("Will must be trainer")};let play=Action{actor:0,action:SimpleAction::Play{trainer_card:trainer},is_stack:false};assert!(g.get_state_clone().generate_possible_actions().1.contains(&play));g.apply_action(&play);g.apply_action(&attack(0,CardId::A4033Entei));let s=g.get_state_clone();assert_eq!(s.pending_attack_coin_choice.as_ref().unwrap().flips,vec![true]);
    let reroll=Action{actor:0,action:SimpleAction::RerollAttackCoins{victory_star_in_play_idx:1},is_stack:true};let mut tails=0.0;for(p,t)in outcomes(&s,&reroll){if t.discard_energies[0].len()==2{tails+=p;}}close(tails,0.5);
}

#[test]
fn regice_random_movement_exposes_energy_choice_before_bench_choice_without_discard() {
    let s=board(0,vec![PlayedCard::from_id(CardId::B3045Regice).with_energy(vec![EnergyType::Water,EnergyType::Water,EnergyType::Psychic]),PlayedCard::from_id(CardId::A1001Bulbasaur),PlayedCard::from_id(CardId::A1033Charmander)],vec![sponge()]);let a=attack(0,CardId::B3045Regice);assert!(s.generate_possible_actions().1.contains(&a));let mut mass=BTreeMap::new();
    for(p,t)in outcomes(&s,&a){assert_eq!(total(&s,0),total(&t,0));assert!(t.discard_energies[0].is_empty());let(_,choices)=t.generate_possible_actions();assert_eq!(choices.len(),2);let mut sampled=None;
        for choice in choices {let SimpleAction::MoveEnergies{from_in_play_idx,to_in_play_idx,ref energies}=choice.action else {panic!("expected movement")};assert_eq!(from_in_play_idx,0);assert!([1,2].contains(&to_in_play_idx));assert_eq!(energies.len(),2);if let Some(ref e)=sampled {assert_eq!(e,energies);}else{sampled=Some(energies.clone());}
            for(_,after)in outcomes(&t,&choice){assert_eq!(after.get_active(0).attached_energy.len(),1);assert_eq!(after.in_play_pokemon[0][to_in_play_idx].as_ref().unwrap().attached_energy,*energies);assert_eq!(total(&after,0),total(&s,0));assert!(after.discard_energies[0].is_empty());}
        }
        *mass.entry(sampled.unwrap()).or_insert(0.0)+=p;
    }
    assert_eq!(mass.len(),2);let mut mixed=vec![EnergyType::Water,EnergyType::Psychic];mixed.sort();close(mass[&vec![EnergyType::Water,EnergyType::Water]],1.0/3.0);close(mass[&mixed],2.0/3.0);
}

#[test]
fn both_active_discards_are_independent_per_pokemon_and_preserve_owner_resources() {
    for actor in [0,1] {
        let s=board(actor,vec![PlayedCard::from_id(CardId::A3034Oricorio).with_energy(vec![EnergyType::Fire,EnergyType::Fire,EnergyType::Water])],vec![sponge().with_energy(vec![EnergyType::Psychic,EnergyType::Psychic,EnergyType::Psychic,EnergyType::Metal])]);let a=attack(actor,CardId::A3034Oricorio);assert!(s.generate_possible_actions().1.contains(&a));let mut mass=BTreeMap::new();
        for(p,t)in outcomes(&s,&a){for owner in [0,1]{assert_eq!(total(&s,owner),total(&t,owner));assert_eq!(t.discard_energies[owner].len(),1);}assert_eq!(t.get_active(1-actor).get_remaining_hp(),140);*mass.entry((t.discard_energies[actor][0],t.discard_energies[1-actor][0])).or_insert(0.0)+=p;}
        assert_eq!(mass.len(),4);close(mass[&(EnergyType::Fire,EnergyType::Psychic)],0.5);close(mass[&(EnergyType::Fire,EnergyType::Metal)],1.0/6.0);close(mass[&(EnergyType::Water,EnergyType::Psychic)],0.25);close(mass[&(EnergyType::Water,EnergyType::Metal)],1.0/12.0);
    }
}

#[test]
fn three_coin_discard_preserves_head_count_mass_and_conditioned_energy_weights() {
    let s=board(0,vec![PlayedCard::from_id(CardId::B2a082Maushold).with_energy(vec![EnergyType::Fire,EnergyType::Water])],vec![sponge().with_energy(vec![EnergyType::Psychic,EnergyType::Psychic,EnergyType::Water])]);let a=attack(0,CardId::B2a082Maushold);assert!(s.generate_possible_actions().1.contains(&a));let mut counts=[0.0;4];
    for(p,t)in outcomes(&s,&a){counts[t.discard_energies[1].len()]+=p;assert_eq!(t.get_active(1).get_remaining_hp(),120);assert_eq!(total(&s,1),total(&t,1));}for(a,b)in counts.into_iter().zip([0.125,0.375,0.375,0.125]){close(a,b);}
    let c=forecast(&s,&a).condition_on_coin_sequence(&CoinSeq(vec![true,false,true])).unwrap();let(p,m)=c.into_branches();let mut mass=BTreeMap::new();for(p,m)in p.into_iter().zip(m){let mut t=s.clone();m(&mut StdRng::seed_from_u64(3),&mut t,&a);*mass.entry(energy_key(&t,1)).or_insert(0.0)+=p;}
    let mut mixed=vec![EnergyType::Psychic,EnergyType::Water];mixed.sort();assert_eq!(mass.len(),2);close(mass[&vec![EnergyType::Psychic,EnergyType::Psychic]],1.0/3.0);close(mass[&mixed],2.0/3.0);
}

#[test]
fn evolved_discard_gate_retains_damage_and_refines_only_evolved_branch() {
    for evolved in [false,true] {
        let mut dud=PlayedCard::from_id(CardId::B3a060Dudunsparce).with_energy(vec![EnergyType::Water;2]);dud.played_this_turn=evolved;
        let s=board(0,vec![dud],vec![sponge().with_energy(vec![EnergyType::Psychic,EnergyType::Psychic,EnergyType::Water])]);let a=attack(0,CardId::B3a060Dudunsparce);let mut mass=BTreeMap::new();
        for(p,t)in outcomes(&s,&a){assert_eq!(t.get_active(1).get_remaining_hp(),120);assert_eq!(total(&s,1),total(&t,1));*mass.entry(energy_key(&t,1)).or_insert(0.0)+=p;}
        if !evolved{assert_eq!(mass.len(),1);close(mass[&vec![]],1.0);}else{assert_eq!(mass.len(),2);let mut mixed=vec![EnergyType::Psychic,EnergyType::Water];mixed.sort();close(mass[&vec![EnergyType::Psychic,EnergyType::Psychic]],1.0/3.0);close(mass[&mixed],2.0/3.0);}
    }
}

#[test]
fn walking_wake_refinements_keep_all_damage_and_bench_knockout_effects() {
    let s=board(0,vec![PlayedCard::from_id(CardId::B3a053WalkingWake).with_energy(vec![EnergyType::Fire,EnergyType::Water,EnergyType::Water])],vec![sponge(),PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(10),PlayedCard::from_id(CardId::A1033Charmander)]);let a=attack(0,CardId::B3a053WalkingWake);assert!(s.generate_possible_actions().1.contains(&a));let mut mass=BTreeMap::new();
    for(p,t)in outcomes(&s,&a){assert_eq!(t.get_active(1).get_remaining_hp(),120);assert!(t.in_play_pokemon[1][1].is_none());assert_eq!(t.in_play_pokemon[1][2].as_ref().unwrap().get_remaining_hp(),40);assert_eq!(t.points[0],1);assert_eq!(total(&s,0),total(&t,0));*mass.entry(energy_key(&t,0)).or_insert(0.0)+=p;}
    assert_eq!(mass.len(),2);close(mass[&vec![EnergyType::Fire]],1.0/3.0);close(mass[&vec![EnergyType::Water]],2.0/3.0);
}

#[test]
fn gyarados_opponent_discard_has_exact_terminal_uncertainty_without_a_coin() {
    let mut s=board(0,vec![PlayedCard::from_id(CardId::A1078Gyarados).with_energy(vec![EnergyType::Water;4])],vec![PlayedCard::from_id(CardId::B1a034Reuniclus).with_energy(vec![EnergyType::Psychic,EnergyType::Psychic,EnergyType::Water]).with_damage(30)]);s.points[0]=2;assert_eq!(s.get_active(1).get_remaining_hp(),120);let a=attack(0,CardId::A1078Gyarados);assert!(s.generate_possible_actions().1.contains(&a));let mut win=0.0;let mut live=0.0;
    for(p,t)in outcomes(&s,&a){for owner in [0,1]{assert_eq!(total(&s,owner),total(&t,owner));}if t.winner==Some(GameOutcome::Win(0)){win+=p;}else{assert!(t.winner.is_none());assert_eq!(t.get_active(1).get_remaining_hp(),20);live+=p;}}
    close(win,2.0/3.0);close(live,1.0/3.0);
}

#[test]
fn every_shared_coin_discard_print_uses_its_own_damage_on_both_coin_faces() {
    let cases=[(CardId::A1178Mawile,20),(CardId::A1192Fearow,50),(CardId::A1a023Drednaw,70),(CardId::A2021MowRotom,30),(CardId::A3100Lycanroc,80),(CardId::A3a012Sharpedo,50),(CardId::B1a050Garbodor,70),(CardId::B2094AlolanMeowth,0),(CardId::B4028Houndoom,60),(CardId::PA068Lycanroc,80)];
    for(id,expected)in cases {
        let Card::Pokemon(card)=get_card_by_enum(id) else{panic!("pokemon expected")};let(index,atk)=card.attacks.iter().enumerate().find(|(_,a)|a.effect.as_deref()==Some("Flip a coin. If heads, discard a random Energy from your opponent's Active Pokémon.")).unwrap();assert_eq!(atk.fixed_damage,expected);let energy=atk.energy_required.iter().map(|e|if *e==EnergyType::Colorless{EnergyType::Water}else{*e}).collect();
        let s=board(0,vec![PlayedCard::from_id(id).with_energy(energy)],vec![sponge()]);let a=Action{actor:0,action:attack_action(id,index),is_stack:false};assert!(s.generate_possible_actions().1.contains(&a));
        for face in [false,true]{let c=forecast(&s,&a).condition_on_coin_sequence(&CoinSeq(vec![face])).unwrap();let(p,m)=c.into_branches();close(p.iter().sum(),1.0);for m in m{let mut t=s.clone();m(&mut StdRng::seed_from_u64(1),&mut t,&a);assert_eq!(t.get_active(1).get_remaining_hp(),180-expected,"{id:?} face={face} must use printed damage");assert!(t.discard_energies[1].is_empty());}}
    }
}

#[test]
fn protected_opponent_keeps_energy_but_both_active_attacker_still_pays_own_discard() {
    for id in [CardId::A1078Gyarados,CardId::A1178Mawile,CardId::B1182Pidgeot,CardId::B3a060Dudunsparce,CardId::A3034Oricorio] {
        let Card::Pokemon(card)=get_card_by_enum(id)else{panic!("pokemon")};let atk=&card.attacks[0];let e=atk.energy_required.iter().map(|e|if *e==EnergyType::Colorless{EnergyType::Water}else{*e}).collect();let mut ours=PlayedCard::from_id(id).with_energy(e);ours.played_this_turn=true;
        let mut defender=sponge().with_energy(vec![EnergyType::Water,EnergyType::Psychic,EnergyType::Psychic]);defender.add_effect(deckgym::effects::CardEffect::PreventAllDamageAndEffects,1);let s=board(0,vec![ours],vec![defender]);let a=attack(0,id);
        for(_,t)in outcomes(&s,&a){assert_eq!(t.get_active(1).get_remaining_hp(),180,"{id:?} damage blocked");assert_eq!(t.get_active(1).attached_energy,s.get_active(1).attached_energy,"{id:?} discard blocked");assert!(t.discard_energies[1].is_empty());if id==CardId::A3034Oricorio{assert_eq!(t.discard_energies[0].len(),1);}else{assert!(t.discard_energies[0].is_empty());}}
        if matches!(id,CardId::A1178Mawile|CardId::B1182Pidgeot){assert!(forecast(&s,&a).has_any_coin_paths(),"protected defender does not erase printed coin evidence");}
    }
}

#[test]
fn pidgeot_two_tails_nullifies_damage_but_one_head_has_weighted_discard() {
    let s=board(0,vec![PlayedCard::from_id(CardId::B1182Pidgeot).with_energy(vec![EnergyType::Water;3])],vec![sponge().with_energy(vec![EnergyType::Psychic,EnergyType::Psychic,EnergyType::Water])]);let a=attack(0,CardId::B1182Pidgeot);assert!(s.generate_possible_actions().1.contains(&a));
    for faces in [vec![false,false],vec![true,false]] {let c=forecast(&s,&a).condition_on_coin_sequence(&CoinSeq(faces.clone())).unwrap();let(p,m)=c.into_branches();let mut mass=BTreeMap::new();for(p,m)in p.into_iter().zip(m){let mut t=s.clone();m(&mut StdRng::seed_from_u64(0),&mut t,&a);if !faces[0]{assert_eq!(t.get_active(1).get_remaining_hp(),180);assert!(t.discard_energies[1].is_empty());}else{assert_eq!(t.get_active(1).get_remaining_hp(),100);*mass.entry(energy_key(&t,1)).or_insert(0.0)+=p;}}
        if faces[0]{assert_eq!(mass.len(),2);close(mass[&vec![EnergyType::Psychic]],2.0/3.0);close(mass[&vec![EnergyType::Water]],1.0/3.0);}
    }
}

#[test]
fn gouging_fire_keeps_next_turn_damage_reduction_for_every_discard_multiset() {
    let s=board(0,vec![PlayedCard::from_id(CardId::B3a054GougingFire).with_energy(vec![EnergyType::Fire,EnergyType::Lightning,EnergyType::Water]),PlayedCard::from_id(CardId::A1001Bulbasaur)],vec![PlayedCard::from_id(CardId::A4a020SuicuneEx).with_energy(vec![EnergyType::Water;2]),PlayedCard::from_id(CardId::A1033Charmander)]);let a=attack(0,CardId::B3a054GougingFire);assert!(s.generate_possible_actions().1.contains(&a));let paths=outcomes(&s,&a);assert_eq!(paths.len(),3);
    for(p,mut t)in paths{close(p,1.0/3.0);assert_eq!(t.discard_energies[0].len(),2);assert_eq!(total(&s,0),total(&t,0));assert_eq!(t.get_active(1).get_remaining_hp(),40);
        for _ in 0..8 {if t.current_player==1 && t.move_generation_stack.is_empty(){break;}let(_,offered)=t.generate_possible_actions();assert_eq!(offered.len(),1);let paths=outcomes(&t,&offered[0]);assert_eq!(paths.len(),1);t=paths.into_iter().next().unwrap().1;}
        assert_eq!(t.current_player,1);let reply=attack(1,CardId::A4a020SuicuneEx);assert!(t.generate_possible_actions().1.contains(&reply));for(_,after)in outcomes(&t,&reply){assert_eq!(after.get_active(0).get_remaining_hp(),100,"40 printed board damage minus30 reduction must deal10 in every refined branch");}
    }
}

#[test]
fn swanna_move_all_and_no_bench_boundary_remain_deterministic() {
    for bench in [false,true]{let mut ours=vec![PlayedCard::from_id(CardId::A4063Swanna).with_energy(vec![EnergyType::Water,EnergyType::Fire,EnergyType::Psychic])];if bench{ours.push(PlayedCard::from_id(CardId::A1001Bulbasaur));}let s=board(0,ours,vec![sponge()]);let a=attack(0,CardId::A4063Swanna);assert!(s.generate_possible_actions().1.contains(&a));let paths=outcomes(&s,&a);assert_eq!(paths.len(),1);let t=&paths[0].1;assert_eq!(t.get_active(1).get_remaining_hp(),120);assert!(t.discard_energies[0].is_empty());let(_,offered)=t.generate_possible_actions();let moves:Vec<_>=offered.iter().filter(|a|matches!(a.action,SimpleAction::MoveEnergies{..})).collect();
        if bench{assert_eq!(moves.len(),1);for(_,after)in outcomes(t,moves[0]){assert!(after.get_active(0).attached_energy.is_empty());assert_eq!(after.in_play_pokemon[0][1].as_ref().unwrap().attached_energy.len(),3);assert_eq!(total(&s,0),total(&after,0));}}else{assert!(moves.is_empty());assert_eq!(t.get_active(0).attached_energy.len(),3);}
    }
}

#[test]
fn earned_kecleon_shield_blocks_opponent_attack_energy_effect_on_next_turn() {
    let s=board(0,vec![PlayedCard::from_id(CardId::B4a062TeamRocketsKecleon).with_energy(vec![EnergyType::Water;2])],vec![PlayedCard::from_id(CardId::A1178Mawile).with_energy(vec![EnergyType::Metal])]);let a=attack(0,CardId::B4a062TeamRocketsKecleon);assert!(s.generate_possible_actions().1.contains(&a));let c=forecast(&s,&a).condition_on_coin_sequence(&CoinSeq(vec![true])).unwrap();let(p,m)=c.into_branches();assert_eq!(p,vec![1.0]);let mut t=s.clone();m.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(0),&mut t,&a);
    for _ in 0..8{if t.current_player==1 && t.move_generation_stack.is_empty(){break;}let(_,offered)=t.generate_possible_actions();assert_eq!(offered.len(),1);let paths=outcomes(&t,&offered[0]);assert_eq!(paths.len(),1);t=paths.into_iter().next().unwrap().1;}
    assert_eq!(t.current_player,1);let reply=attack(1,CardId::A1178Mawile);assert!(t.generate_possible_actions().1.contains(&reply));let c=forecast(&t,&reply).condition_on_coin_sequence(&CoinSeq(vec![true])).unwrap();let(_,m)=c.into_branches();for m in m{let mut after=t.clone();m(&mut StdRng::seed_from_u64(0),&mut after,&reply);assert_eq!(after.get_active(0).get_remaining_hp(),70);assert_eq!(after.get_active(0).attached_energy,vec![EnergyType::Water;2]);assert!(after.discard_energies[0].is_empty());}
}

#[test]
fn global_discard_selects_from_full_pool_before_protected_target_prevents_effect() {
    let mut defender=PlayedCard::from_id(CardId::B4a062TeamRocketsKecleon).with_energy(vec![EnergyType::Water;2]);defender.add_effect(deckgym::effects::CardEffect::PreventAllDamageAndEffects,1);let s=board(0,vec![PlayedCard::from_id(CardId::A1a018GyaradosEx).with_energy(vec![EnergyType::Water;4])],vec![defender]);let a=attack(0,CardId::A1a018GyaradosEx);let mut own_discard=0.0;let mut prevented=0.0;
    for(p,t)in outcomes(&s,&a){assert_eq!(t.get_active(1).get_remaining_hp(),70);assert_eq!(t.get_active(1).attached_energy.len(),2);assert!(t.discard_energies[1].is_empty());for owner in [0,1]{assert_eq!(total(&s,owner),total(&t,owner));}match t.discard_energies[0].len(){1=>own_discard+=p,0=>prevented+=p,n=>panic!("discarded{n}")}}
    close(own_discard,4.0/6.0);close(prevented,2.0/6.0);
}

#[test]
fn safeguard_blocks_ex_damage_but_does_not_block_energy_effects() {
    let s=board(0,vec![PlayedCard::from_id(CardId::A1a018GyaradosEx).with_energy(vec![EnergyType::Water;4])],vec![PlayedCard::from_id(CardId::A3165Oricorio).with_energy(vec![EnergyType::Psychic])]);let a=attack(0,CardId::A1a018GyaradosEx);let mut effect_mass=0.0;
    for(p,t)in outcomes(&s,&a){assert_eq!(t.get_active(1).get_remaining_hp(),70);assert_eq!(t.discard_energies[0].len()+t.discard_energies[1].len(),1);if t.get_active(1).attached_energy.is_empty(){effect_mass+=p;}for owner in [0,1]{assert_eq!(total(&s,owner),total(&t,owner));}}
    close(effect_mass,1.0/5.0);
}

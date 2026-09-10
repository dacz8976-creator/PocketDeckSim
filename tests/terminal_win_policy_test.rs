//! Outcome utility and action-efficiency regressions. The Arceus hand comes from
//! the owner Auto recording20260907_025604000_iOS.MP4; hidden zones remain synthetic.
use deckgym::{actions::{try_forecast_action,Action,SimpleAction},card_ids::CardId,
 database::get_card_by_enum,effects::CardEffect,models::{Attack,Card,EnergyType,PlayedCard},
 observation::{canonical_actions,PlayerObservation,RevealedKnowledge},
 players::{public_baseline_value_function,public_effect_value_function,public_clock_effect_value_function,
 ExpectiMiniMaxPlayer,Player,ValueFunctionParams},state::GameOutcome,test_support::attack_action,Deck,State};
use rand::{rngs::StdRng,SeedableRng};

fn board(own:Vec<PlayedCard>,opp:Vec<PlayedCard>)->State {
 let mut s=State::default();s.current_player=0;s.turn_count=15;s.set_board(own,opp);
 s.hands=[vec![],vec![get_card_by_enum(CardId::A1001Bulbasaur);4]];
 s.decks[0].cards.clear();s.decks[1].cards=vec![get_card_by_enum(CardId::A1001Bulbasaur);8];
 s.energy_zone[0].current=None;s
}
fn apply(s:&mut State,a:&Action) {
 assert!(s.generate_possible_actions().1.contains(a));
 let(p,m)=try_forecast_action(s,a).unwrap().into_branches();assert_eq!(p,vec![1.0]);
 m.into_iter().next().unwrap()(&mut StdRng::seed_from_u64(47),s,a);
}
fn choose(s:&State,depth:usize,seed:u64)->Action {
 let mut actions=s.generate_possible_actions().1;canonical_actions(&mut actions);
 let obs=PlayerObservation::from_state(s,0,&RevealedKnowledge::default());
 assert!(obs.visible_state().hands[1].iter().all(|c|*c==Card::Unknown));
 let mut p=ExpectiMiniMaxPlayer{deck:Deck::default(),max_depth:depth,write_debug_trees:false,
 value_function:Box::new(public_clock_effect_value_function),opponent_ply:0,
 consistent_horizon:false,soft_opponent:false};
 p.decision_fn(&mut StdRng::seed_from_u64(seed),&obs,&actions)
}
fn arceus(n:usize)->PlayedCard{PlayedCard::from_id(CardId::A2a071ArceusEx).with_energy(vec![EnergyType::Water;n])}
fn final_board(nonempty_deck:bool)->State {
 let mut m=PlayedCard::from_id(CardId::B2113MegaMawileEx).with_damage(50).with_energy(vec![EnergyType::Metal;2]);
 m.add_effect(CardEffect::IncreasedDamageForAttack{attack_name:"Heat-Up Crunch".into(),amount:30},255);
 let mut s=board(vec![],vec![]);s.active_stadium=Some(get_card_by_enum(CardId::B2154StartingPlains));
 s.set_board(vec![arceus(2),arceus(0),PlayedCard::from_id(CardId::A4120Absol),PlayedCard::from_id(CardId::A2a050Crobat)],
 vec![m,PlayedCard::from_id(CardId::B2113MegaMawileEx).with_energy(vec![EnergyType::Metal])]);
 s.hands[0]=vec![get_card_by_enum(CardId::A3151Guzma),get_card_by_enum(CardId::A2147GiantCape),get_card_by_enum(CardId::PA005PokeBall)];
 if nonempty_deck{s.decks[0].cards=vec![get_card_by_enum(CardId::A1001Bulbasaur),get_card_by_enum(CardId::A1033Charmander)];}
 s.points=[2,2];s.energy_zone[0].current=Some(EnergyType::Water);s
}

#[test]
fn public_terminal_utility_ignores_resources_and_raw_points() {
 let mut plain=final_board(false);plain.points=[3,2];
 let mut rich=plain.clone();rich.points=[5,0];rich.hands[0].extend(vec![get_card_by_enum(CardId::PA001Potion);5]);
 rich.in_play_pokemon[0][0]=Some(arceus(5).with_tool(get_card_by_enum(CardId::A2147GiantCape)));
 let evaluators:[fn(&State,usize)->f64;3]=[public_baseline_value_function,public_effect_value_function,public_clock_effect_value_function];
 for (outcome,expected) in [(GameOutcome::Win(0),ValueFunctionParams::baseline().is_winner),(GameOutcome::Win(1),-ValueFunctionParams::baseline().is_winner),(GameOutcome::Tie,0.0)] {
  plain.winner=Some(outcome);rich.winner=Some(outcome);
  for eval in evaluators {assert_eq!(eval(&plain,0),expected);assert_eq!(eval(&rich,0),expected);assert_eq!(eval(&plain,1),-expected);}
 }
 plain.winner=None;rich.winner=None;
 assert_ne!(public_clock_effect_value_function(&plain,0),public_clock_effect_value_function(&rich,0),"nonterminal resources still matter");
}

#[test]
fn current_k3_finishes_visible_hand_combination_in_three_actions() {
 for nonempty_deck in [false,true] {for seed in [91,92] {
  let mut s=final_board(nonempty_deck);let hand=s.hands[0].clone();let mut line=vec![];
  for _ in 0..3 {let a=choose(&s,3,seed);line.push(format!("{:?}",a.action));apply(&mut s,&a);if s.winner.is_some(){break;}}
  println!("nonempty_deck={nonempty_deck} seed={seed} line={line:?}");
  assert_eq!(s.winner,Some(GameOutcome::Win(0)),"take the three-action win");
  assert_eq!(s.hands[0],hand,"no Cape, draw, or other hand action is needed");
  assert_eq!(s.points,[5,2]);
 }}
}

#[test]
fn immediate_win_precedes_spare_energy_and_tool_placement() {
 let mut s=final_board(false);
 s.in_play_pokemon[0][0].as_mut().unwrap().attached_energy.push(EnergyType::Water);
 s.in_play_pokemon[1][0]=Some(s.in_play_pokemon[1][0].as_ref().unwrap().clone().with_remaining_hp(110));
 for depth in [1,2,3] {
  let a=choose(&s,depth,91);assert!(matches!(a.action,SimpleAction::Attack(_)),"depth{depth}: {a:?}");
  let mut after=s.clone();apply(&mut after,&a);assert_eq!(after.winner,Some(GameOutcome::Win(0)));
 }
}

#[test]
fn possible_coin_win_does_not_displace_certain_attack_win() {
 let mut attacker=PlayedCard::from_id(CardId::A1198Farfetchd).with_energy(vec![EnergyType::Water]);
 // Synthetic two-attack card isolates choice quality without claiming a real printing.
 let safe=Attack{energy_required:vec![EnergyType::Colorless],title:"Certain knockout".into(),fixed_damage:40,effect:None};
 let risky=Attack{energy_required:vec![EnergyType::Colorless],title:"Coin knockout".into(),fixed_damage:80,effect:Some("Flip a coin. If tails, this attack does nothing.".into())};
 if let Card::Pokemon(ref mut p)=attacker.card {p.attacks=vec![safe.clone(),risky.clone()];}
 let mut s=board(vec![attacker],vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(30),PlayedCard::from_id(CardId::A1001Bulbasaur)]);s.points=[2,2];
 let risk=Action{actor:0,action:SimpleAction::Attack(risky),is_stack:false};
 let(p,m)=try_forecast_action(&s,&risk).unwrap().into_branches();assert_eq!(p,vec![0.5,0.5]);
 let outcomes:Vec<_>=m.into_iter().map(|m|{let mut n=s.clone();m(&mut StdRng::seed_from_u64(47),&mut n,&risk);n.winner}).collect();
 assert!(outcomes.contains(&None)&&outcomes.contains(&Some(GameOutcome::Win(0))));
 for depth in [1,2,3] {let a=choose(&s,depth,91);assert_eq!(a.action,SimpleAction::Attack(safe.clone()));}
}

#[test]
fn necessary_preparation_avoids_a_simultaneous_knockout_tie() {
 let mut s=board(vec![PlayedCard::from_id(CardId::B4a014TeamRocketsArticunoEx).with_energy(vec![EnergyType::Water;3]),PlayedCard::from_id(CardId::B4034Carvanha).with_remaining_hp(10)],
 vec![PlayedCard::from_id(CardId::A1001Bulbasaur).with_remaining_hp(30),PlayedCard::from_id(CardId::A1001Bulbasaur)]);
 s.points=[2,2];s.hands[0]=vec![get_card_by_enum(CardId::A2147GiantCape)];
 let hailstorm=Action{actor:0,action:attack_action(CardId::B4a014TeamRocketsArticunoEx,1),is_stack:false};
 let mut direct=s.clone();apply(&mut direct,&hailstorm);assert_eq!(direct.winner,Some(GameOutcome::Tie));
 assert_eq!(public_clock_effect_value_function(&direct,0),0.0);
 let mut line=vec![];
 for _ in 0..3 {let a=choose(&s,3,91);line.push(format!("{:?}",a.action));apply(&mut s,&a);if s.winner.is_some(){break;}}
 println!("necessary preparation={line:?}");assert_eq!(s.winner,Some(GameOutcome::Win(0)));
 assert_eq!(s.in_play_pokemon[0][1].as_ref().unwrap().get_remaining_hp(),10,"Cape protects the injured friendly Bench from Hailstorm");
}

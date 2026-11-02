// Ported from upstream deckgym-core #438 (20d1857): the tests of tests/pokemon/c1_attacks/{alakazam,eevee,electrode,espeon,malamar,pidgeot,pidgey,porygon_z,pupitar,umbreon,whiscash}.rs and tests/pokemon/c1_abilities/pawmot.rs, all as upstream wrote them (R8-08a), in one file with the helpers of upstream's two mod.rs files: damage is read with `Taken` (upstream's `public_details().damage` is not in this fork; as in dual_fusion_ex/mod.rs), and `end_turn` also plays the Pokémon Checkup and the next player's draw, as c1_grass_fire_test's does. Deoxys, Jigglypuff and Lunala, the rest of c1_attacks, are not ported here. Fork tests are added at the end (Electrode's exact 90 on itself; Electrocreation on each printing from the Active Spot and the Bench, once per Pawmot, not to an Active of another type; Mind Jack counting only the opponent's Bench; Brainwave counting only [P]; Amass leaving the turn's Energy; Power Press with 4 [F] in all; Moonlit Raid and Clean Hit against a Stage 2 and a Fossil; Find a Friend and Signs of Evolution over seeds, past a Fossil and at a 10-card hand; Overdrive Smash's +50 staying with the Porygon-Z that used it; Pester the Dizzy against the other Special Conditions and before Weakness; the printings' status).
use deckgym::{
    actions::{Action, SimpleAction},
    card_ids::CardId,
    card_validation::{get_implementation_status, implementation_limitations, ImplementationStatus},
    database::get_card_by_enum,
    models::{Card, EnergyType, PlayedCard, StatusCondition},
    test_support::{attack_action, get_initialized_game_with_board, get_test_game_with_board},
    Game,
};
use std::collections::BTreeSet;

/// Damage on a Pokémon, in place of upstream's `public_details().damage`: its full HP (the remaining HP after
/// setting it above the maximum, which clamps to the full HP) less its remaining HP.
trait Taken {
    fn taken(&self) -> u32;
}
impl Taken for PlayedCard {
    fn taken(&self) -> u32 {
        self.clone().with_remaining_hp(u32::MAX).get_remaining_hp() - self.get_remaining_hp()
    }
}

// Upstream's tests/pokemon/c1_attacks/mod.rs.

// Extra HP isolates the attack's damage from knockouts and promotion choices.
fn durable_of(id: CardId) -> PlayedCard {
    PlayedCard::new(get_card_by_enum(id), 0, 1000, vec![], false, vec![])
}
// Snorlax is weak to [F]; Charmander is not weak to anything these tests attack with.
fn durable() -> PlayedCard {
    durable_of(CardId::A1211Snorlax)
}
fn ready(id: CardId, index: usize) -> PlayedCard {
    let Card::Pokemon(p) = get_card_by_enum(id) else {
        panic!("Pokémon required")
    };
    PlayedCard::from_id(id).with_energy(p.attacks[index].energy_required.clone())
}
fn board(ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> Game<'static> {
    get_initialized_game_with_board(0, 0, 3, ours, theirs)
}
fn attack(game: &mut Game<'static>, id: CardId, index: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(id, index),
        is_stack: false,
    });
}
fn end_turn(game: &mut Game<'static>, actor: usize) {
    game.apply_action(&Action {
        actor,
        action: SimpleAction::EndTurn,
        is_stack: false,
    });
    // The Pokémon Checkup and the next player's draw.
    game.play_until_stable();
}
fn defender_damage(game: &Game<'static>) -> u32 {
    game.get_state_clone().get_active(1).taken()
}

// Upstream's tests/pokemon/c1_abilities/mod.rs.

fn use_ability(game: &mut Game<'static>, in_play_idx: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::UseAbility { in_play_idx },
        is_stack: false,
    });
}

fn offers_ability(game: &Game<'static>, in_play_idx: usize) -> bool {
    let (_, actions) = game.get_state_clone().generate_possible_actions();
    actions.iter().any(|action| {
        matches!(action.action, SimpleAction::UseAbility { in_play_idx: i } if i == in_play_idx)
    })
}

// c1_attacks/alakazam.rs

#[test]
fn mind_jack_adds_thirty_per_opponent_benched_pokemon_on_both_printings() {
    for id in [CardId::C1055Alakazam, CardId::C1197Alakazam] {
        let mut game = board(
            vec![ready(id, 0)],
            vec![durable(), durable(), durable(), durable()],
        );
        attack(&mut game, id, 0);
        assert_eq!(defender_damage(&game), 50 + 30 * 3, "{id:?}");
    }
}

#[test]
fn mind_jack_does_only_base_damage_with_an_empty_opponent_bench() {
    let id = CardId::C1055Alakazam;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 50);
}

// c1_attacks/eevee.rs

#[test]
fn signs_of_evolution_puts_only_an_eevee_evolution_into_hand() {
    let id = CardId::C1107Eevee;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    let mut state = game.get_state_clone();
    state.hands[0].clear();
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::A1206Eevee),
        get_card_by_enum(CardId::A1080Vaporeon),
    ];
    game.set_state(state);
    attack(&mut game, id, 0);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0].len(), 1);
    assert_eq!(state.hands[0][0].get_name(), "Vaporeon");
    assert_eq!(state.decks[0].cards.len(), 2);
}

// c1_attacks/electrode.rs

#[test]
fn self_destruct_hits_the_defender_and_electrode_for_ninety() {
    let id = CardId::C1045Electrode;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 90);
    let state = game.get_state_clone();
    // Electrode has 90 HP, so it knocks itself out and the opponent scores the point.
    assert_eq!(state.points[1], 1);
}

// c1_attacks/espeon.rs

#[test]
fn brainwave_adds_twenty_per_psychic_energy_attached() {
    let id = CardId::C1060Espeon;
    let mut game = board(
        vec![ready(id, 0).with_energy(vec![
            EnergyType::Psychic,
            EnergyType::Psychic,
            EnergyType::Water,
        ])],
        vec![durable()],
    );
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 10 + 20 * 2);
}

// c1_attacks/malamar.rs

#[test]
fn pester_the_dizzy_adds_ninety_against_a_confused_active() {
    let id = CardId::PC005Malamar;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    let mut state = game.get_state_clone();
    state.apply_status_condition(1, 0, StatusCondition::Confused);
    game.set_state(state);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 10 + 90);
}

#[test]
fn pester_the_dizzy_does_only_base_damage_otherwise() {
    let id = CardId::PC005Malamar;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 10);
}

// c1_attacks/pidgeot.rs

#[test]
fn clean_hit_adds_eighty_against_an_evolution_active() {
    let id = CardId::C1104Pidgeot;
    let mut game = board(vec![ready(id, 0)], vec![durable_of(CardId::A1002Ivysaur)]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 40 + 80);
}

#[test]
fn clean_hit_adds_nothing_against_a_basic_active() {
    let id = CardId::C1104Pidgeot;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 40);
}

// c1_attacks/pidgey.rs

#[test]
fn find_a_friend_puts_a_colorless_pokemon_from_the_deck_into_hand() {
    let id = CardId::C1102Pidgey;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    let mut state = game.get_state_clone();
    state.hands[0].clear();
    state.decks[0].cards = vec![
        get_card_by_enum(CardId::A1001Bulbasaur),
        get_card_by_enum(CardId::A1211Snorlax),
        get_card_by_enum(CardId::A1080Vaporeon),
    ];
    game.set_state(state);
    attack(&mut game, id, 0);
    let state = game.get_state_clone();
    assert_eq!(state.hands[0].len(), 1);
    assert_eq!(state.hands[0][0].get_name(), "Snorlax");
    assert_eq!(state.decks[0].cards.len(), 2);
}

#[test]
fn find_a_friend_does_nothing_without_a_colorless_pokemon_in_the_deck() {
    let id = CardId::C1102Pidgey;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    let mut state = game.get_state_clone();
    state.hands[0].clear();
    state.decks[0].cards = vec![get_card_by_enum(CardId::A1001Bulbasaur)];
    game.set_state(state);
    attack(&mut game, id, 0);
    let state = game.get_state_clone();
    assert!(state.hands[0].is_empty());
    assert_eq!(state.decks[0].cards.len(), 1);
}

// c1_attacks/porygon_z.rs

#[test]
fn overdrive_smash_adds_fifty_on_the_next_turn_only() {
    let id = CardId::C1110PorygonZ;
    let mut game = board(vec![ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 50);
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 50 + 100);
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    attack(&mut game, id, 0);
    // The bonus is re-armed by each use, so it applies again the turn after.
    assert_eq!(defender_damage(&game), 50 + 100 + 100);
}

// c1_attacks/pupitar.rs

#[test]
fn amass_attaches_two_fighting_energy_to_itself_on_both_printings() {
    for id in [CardId::C1076Pupitar, CardId::C1146Pupitar] {
        let mut game = board(vec![ready(id, 0)], vec![durable()]);
        attack(&mut game, id, 0);
        let state = game.get_state_clone();
        let energy = &state.get_active(0).attached_energy;
        assert_eq!(
            energy
                .iter()
                .filter(|e| **e == EnergyType::Fighting)
                .count(),
            2,
            "{id:?}"
        );
        assert_eq!(defender_damage(&game), 0);
    }
}

// c1_attacks/umbreon.rs

#[test]
fn moonlit_raid_adds_fifty_against_a_basic_active_on_both_printings() {
    for id in [CardId::C1084Umbreon, CardId::C1186Umbreon] {
        let mut game = board(vec![ready(id, 0)], vec![durable()]);
        attack(&mut game, id, 0);
        assert_eq!(defender_damage(&game), 30 + 50, "{id:?}");
    }
}

#[test]
fn moonlit_raid_adds_nothing_against_an_evolved_active() {
    let id = CardId::C1084Umbreon;
    let mut game = board(vec![ready(id, 0)], vec![durable_of(CardId::A1002Ivysaur)]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 30);
}

// c1_attacks/whiscash.rs

fn fighting(extra: usize) -> Vec<EnergyType> {
    vec![EnergyType::Fighting; 1 + extra]
}

#[test]
fn power_press_adds_sixty_with_three_extra_fighting_energy() {
    let id = CardId::C1078Whiscash;
    let mut game = board(
        vec![PlayedCard::from_id(id).with_energy(fighting(3))],
        vec![durable_of(CardId::A1033Charmander)],
    );
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 40 + 60);
}

#[test]
fn power_press_needs_all_three_extra_energy() {
    let id = CardId::C1078Whiscash;
    let mut game = board(
        vec![PlayedCard::from_id(id).with_energy(fighting(2))],
        vec![durable_of(CardId::A1033Charmander)],
    );
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 40);
}

// c1_abilities/pawmot.rs

const PAWMOTS: [CardId; 3] = [
    CardId::C1050Pawmot,
    CardId::C1142Pawmot,
    CardId::C1216Pawmot,
];

#[test]
fn electrocreation_attaches_lightning_to_the_active_lightning_pokemon() {
    for id in PAWMOTS {
        // Pawmot may be benched: the Ability targets the Active Spot.
        let mut game = get_test_game_with_board(
            vec![
                PlayedCard::from_id(CardId::A1094Pikachu),
                PlayedCard::from_id(id),
            ],
            vec![PlayedCard::from_id(CardId::A1055Blastoise)],
        );
        assert!(offers_ability(&game, 1), "{id:?}");
        use_ability(&mut game, 1);
        let state = game.get_state_clone();
        assert_eq!(
            state.get_active(0).attached_energy,
            vec![EnergyType::Lightning],
            "{id:?}"
        );
        assert!(!offers_ability(&game, 1), "{id:?}: once per turn");
    }
}

#[test]
fn electrocreation_is_not_offered_when_the_active_pokemon_is_not_lightning() {
    let game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1033Charmander),
            PlayedCard::from_id(CardId::C1050Pawmot),
        ],
        vec![PlayedCard::from_id(CardId::A1055Blastoise)],
    );
    assert!(!offers_ability(&game, 1));
}

// ---------------------------------------------------------------------------------------------
// Fork additions.
// ---------------------------------------------------------------------------------------------

/// Electrode - Self-Destruct: "This Pokémon also does 90 damage to itself." An Electrode with 1000 HP
/// survives it, so the self-damage shows as exactly 90 (and 90 on the defender), and no point is scored.
#[test]
fn test_electrode_self_destruct_does_exactly_90_to_itself() {
    let electrode = PlayedCard::new(
        get_card_by_enum(CardId::C1045Electrode),
        0,
        1000,
        vec![EnergyType::Colorless, EnergyType::Colorless],
        false,
        vec![],
    );
    let mut game = board(vec![electrode], vec![durable()]);
    attack(&mut game, CardId::C1045Electrode, 0);
    let state = game.get_state_clone();
    assert_eq!(state.get_active(0).taken(), 90);
    assert_eq!(defender_damage(&game), 90);
    assert_eq!(state.points, [0, 0]);
}

/// Pawmot - Electrocreation: "Once during your turn, you may take a [L] Energy from your Energy Zone and
/// attach it to the [L] Pokémon in the Active Spot." On each printing, an Active Pawmot (itself an [L]
/// Pokémon) charges itself; a Benched Pawmot charges the Active Pikachu and not itself. The Energy comes
/// from the Zone without using the turn's Energy, and each Pawmot uses it once a turn: two Benched Pawmot
/// give the Active two [L].
#[test]
fn test_pawmot_electrocreation_charges_the_lightning_active_from_either_spot() {
    for id in PAWMOTS {
        let mut game = get_test_game_with_board(vec![PlayedCard::from_id(id)], vec![durable()]);
        let zone = game.get_state_clone().energy_zone[0];
        assert!(offers_ability(&game, 0), "{id:?} in the Active Spot");
        use_ability(&mut game, 0);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Lightning], "{id:?}");
        assert_eq!(state.energy_zone[0], zone, "{id:?}: the turn's Energy is not used");
        assert!(!offers_ability(&game, 0), "{id:?}: once per turn");

        let mut game = get_test_game_with_board(
            vec![PlayedCard::from_id(CardId::A1094Pikachu), PlayedCard::from_id(id)],
            vec![durable()],
        );
        use_ability(&mut game, 1);
        let state = game.get_state_clone();
        assert_eq!(state.get_active(0).attached_energy, vec![EnergyType::Lightning], "{id:?}");
        assert!(state.in_play_pokemon[0][1].as_ref().unwrap().attached_energy.is_empty(), "{id:?}");
    }

    let mut game = get_test_game_with_board(
        vec![
            PlayedCard::from_id(CardId::A1094Pikachu),
            PlayedCard::from_id(CardId::C1050Pawmot),
            PlayedCard::from_id(CardId::C1216Pawmot),
        ],
        vec![durable()],
    );
    use_ability(&mut game, 1);
    assert!(offers_ability(&game, 2), "the second Pawmot still has its use");
    use_ability(&mut game, 2);
    assert_eq!(
        game.get_state_clone().get_active(0).attached_energy,
        vec![EnergyType::Lightning, EnergyType::Lightning]
    );
    assert!(!offers_ability(&game, 1) && !offers_ability(&game, 2));
}

/// Electrocreation is not offered by any printing while the Active is a [C], [P] or [G] Pokémon.
#[test]
fn test_pawmot_electrocreation_is_not_offered_to_an_active_of_another_type() {
    for id in PAWMOTS {
        for active in [CardId::A1211Snorlax, CardId::A1129MewtwoEx, CardId::A1001Bulbasaur] {
            let game = get_test_game_with_board(
                vec![PlayedCard::from_id(active), PlayedCard::from_id(id)],
                vec![durable()],
            );
            assert!(!offers_ability(&game, 1), "{id:?} with {active:?} Active");
        }
    }
}

/// Alakazam - Mind Jack: "This attack does 30 more damage for each of your opponent's Benched Pokémon."
/// Only the opponent's Bench counts: with three of its own Benched, 50 against no Benched Pokémon, 80
/// against one and 110 against two, on both printings.
#[test]
fn test_alakazam_mind_jack_counts_only_the_opponents_bench() {
    for id in [CardId::C1055Alakazam, CardId::C1197Alakazam] {
        for (benched, expected) in [(0, 50), (1, 80), (2, 110)] {
            let mut game = board(
                vec![ready(id, 0), durable(), durable(), durable()],
                std::iter::repeat_with(durable).take(1 + benched).collect(),
            );
            attack(&mut game, id, 0);
            assert_eq!(defender_damage(&game), expected, "{id:?} against {benched} Benched");
        }
    }
}

/// Espeon - Brainwave: "This attack does 20 more damage for each [P] Energy attached to this Pokémon."
/// Only [P] counts: 10 with [C] and [W], 30 with [P], [L] and [G], 90 with four [P].
#[test]
fn test_espeon_brainwave_counts_only_psychic_energy() {
    let id = CardId::C1060Espeon;
    for (energy, expected) in [
        (vec![EnergyType::Colorless, EnergyType::Water], 10),
        (vec![EnergyType::Psychic, EnergyType::Lightning, EnergyType::Grass], 30),
        (vec![EnergyType::Psychic; 4], 90),
    ] {
        let mut game = board(vec![PlayedCard::from_id(id).with_energy(energy.clone())], vec![durable()]);
        attack(&mut game, id, 0);
        assert_eq!(defender_damage(&game), expected, "{energy:?}");
    }
}

/// Pupitar - Amass: "Take 2 [F] Energy from your Energy Zone and attach it to this Pokémon." On both
/// printings two [F] join the [W] it had, the defender takes nothing, and the turn's Energy in the Zone
/// is left as it was.
#[test]
fn test_pupitar_amass_adds_two_fighting_without_the_turns_energy() {
    for id in [CardId::C1076Pupitar, CardId::C1146Pupitar] {
        let mut game = board(
            vec![PlayedCard::from_id(id).with_energy(vec![EnergyType::Water])],
            vec![durable()],
        );
        let zone = game.get_state_clone().energy_zone[0];
        attack(&mut game, id, 0);
        let state = game.get_state_clone();
        assert_eq!(
            state.get_active(0).attached_energy,
            vec![EnergyType::Water, EnergyType::Fighting, EnergyType::Fighting],
            "{id:?}"
        );
        assert_eq!(state.energy_zone[0], zone, "{id:?}");
        assert_eq!(defender_damage(&game), 0, "{id:?}");
    }
}

/// Whiscash - Power Press: "If this Pokémon has at least 3 extra [F] Energy attached, this attack does 60
/// more damage." Its cost is [F], so the +60 needs 4 [F] in all: 100 with 4 or 5 [F], 40 with 3 [F] and
/// a [W], or 1 [F] and 3 [W] (the extra Energy must be [F]).
#[test]
fn test_whiscash_power_press_needs_four_fighting_in_all() {
    let id = CardId::C1078Whiscash;
    let fighting_and_water = |f: usize, w: usize| {
        let mut energy = vec![EnergyType::Fighting; f];
        energy.extend(vec![EnergyType::Water; w]);
        energy
    };
    for (energy, expected) in [
        (fighting_and_water(4, 0), 100),
        (fighting_and_water(5, 0), 100),
        (fighting_and_water(3, 1), 40),
        (fighting_and_water(1, 3), 40),
    ] {
        let mut game = board(
            vec![PlayedCard::from_id(id).with_energy(energy.clone())],
            vec![durable_of(CardId::A1033Charmander)],
        );
        attack(&mut game, id, 0);
        assert_eq!(defender_damage(&game), expected, "{energy:?}");
    }
}

/// Moonlit Raid ("If your opponent's Active Pokémon is a Basic Pokémon, this attack does 50 more damage.")
/// and Clean Hit ("If your opponent's Active Pokémon is an Evolution Pokémon, this attack does 80 more
/// damage.") read the defender's stage as the fork's other Basic and Evolution bonuses do (`get_stage`).
/// A Stage 2 Venusaur is an Evolution Pokémon: Moonlit Raid 30 on both printings, Clean Hit 40 + 80. A
/// Fossil is played "as if it were a 40-HP Basic [C] Pokémon" (Helix Fossil, A1 216): Moonlit Raid 30 +
/// 50, Clean Hit 40.
#[test]
fn test_moonlit_raid_and_clean_hit_against_a_stage_2_and_a_fossil() {
    let cases = [
        (CardId::C1084Umbreon, CardId::A1003Venusaur, 30),
        (CardId::C1186Umbreon, CardId::A1003Venusaur, 30),
        (CardId::C1104Pidgeot, CardId::A1003Venusaur, 40 + 80),
        (CardId::C1084Umbreon, CardId::A1216HelixFossil, 30 + 50),
        (CardId::C1186Umbreon, CardId::A1216HelixFossil, 30 + 50),
        (CardId::C1104Pidgeot, CardId::A1216HelixFossil, 40),
    ];
    for (id, defender, expected) in cases {
        let mut game = board(vec![ready(id, 0)], vec![durable_of(defender)]);
        attack(&mut game, id, 0);
        assert_eq!(defender_damage(&game), expected, "{id:?} against {defender:?}");
    }
}

/// The deck-search attacks, from `seed`: player 0's Active `id` (ready) with an empty hand and `deck`
/// (or, with `full_hand`, 10 Potions in hand) uses its attack; returns the hand and the deck after it.
fn search(seed: u64, id: CardId, deck: &[CardId], full_hand: bool) -> (Vec<Card>, Vec<Card>) {
    let mut game = get_initialized_game_with_board(seed, 0, 3, vec![ready(id, 0)], vec![durable()]);
    let mut state = game.get_state_clone();
    state.hands[0] = if full_hand {
        vec![get_card_by_enum(CardId::PA001Potion); 10]
    } else {
        vec![]
    };
    state.decks[0].cards = deck.iter().map(|card| get_card_by_enum(*card)).collect();
    game.set_state(state);
    attack(&mut game, id, 0);
    let state = game.get_state_clone();
    (state.hands[0].clone(), state.decks[0].cards.clone())
}

/// Pidgey - Find a Friend: "Put 1 random [C] Pokémon from your deck into your hand." Over 30 seeds with
/// Snorlax, Eevee, Bulbasaur, Vaporeon and Helix Fossil in the deck, the card is always Snorlax or Eevee,
/// and both come up: a Fossil in the deck is a Trainer card, not a [C] Pokémon. With a 10-card hand
/// nothing is added and the deck keeps all 5 (a deck search stops at 10 cards, rules/09).
#[test]
fn test_pidgey_find_a_friend_takes_only_a_colorless_pokemon() {
    let deck = [
        CardId::A1211Snorlax,
        CardId::A1206Eevee,
        CardId::A1001Bulbasaur,
        CardId::A1080Vaporeon,
        CardId::A1216HelixFossil,
    ];
    let mut found = BTreeSet::new();
    for seed in 0..30 {
        let (hand, rest) = search(seed, CardId::C1102Pidgey, &deck, false);
        assert_eq!((hand.len(), rest.len()), (1, 4), "seed {seed}");
        found.insert(hand[0].get_name());
    }
    assert_eq!(found, ["Eevee", "Snorlax"].map(String::from).into_iter().collect::<BTreeSet<_>>());

    let (hand, rest) = search(0, CardId::C1102Pidgey, &deck, true);
    assert_eq!((hand.len(), rest.len()), (10, 5));
}

/// Eevee - Signs of Evolution: "Put a random card that evolves from Eevee from your deck into your hand."
/// Over 30 seeds with Eevee, Snorlax, Vaporeon, Espeon (C1 060) and Umbreon (C1 084) in the deck, the card
/// is always one of the three evolutions, and each comes up. With none of them in the deck nothing is
/// added.
#[test]
fn test_eevee_signs_of_evolution_finds_any_eevee_evolution() {
    let deck = [
        CardId::A1206Eevee,
        CardId::A1211Snorlax,
        CardId::A1080Vaporeon,
        CardId::C1060Espeon,
        CardId::C1084Umbreon,
    ];
    let mut found = BTreeSet::new();
    for seed in 0..30 {
        let (hand, rest) = search(seed, CardId::C1107Eevee, &deck, false);
        assert_eq!((hand.len(), rest.len()), (1, 4), "seed {seed}");
        found.insert(hand[0].get_name());
    }
    let evolutions = ["Espeon", "Umbreon", "Vaporeon"].map(String::from);
    assert_eq!(found, evolutions.into_iter().collect::<BTreeSet<_>>());

    let (hand, rest) = search(0, CardId::C1107Eevee, &deck[..2], false);
    assert_eq!((hand.len(), rest.len()), (0, 2));
}

/// Overdrive Smash's +50 is "this Pokémon's": the Porygon-Z that used it retreats to a second Porygon-Z on
/// the next turn, whose Overdrive Smash does its printed 50 (50 + 50 on the defender in all).
#[test]
fn test_porygon_z_overdrive_smash_bonus_stays_with_the_porygon_z_that_used_it() {
    let id = CardId::C1110PorygonZ;
    let mut game = board(vec![ready(id, 0), ready(id, 0)], vec![durable()]);
    attack(&mut game, id, 0);
    end_turn(&mut game, 0);
    end_turn(&mut game, 1);
    game.apply_action(&Action {
        actor: 0,
        action: SimpleAction::Retreat(1),
        is_stack: false,
    });
    game.play_until_stable();
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 50 + 50);
}

/// Malamar - Pester the Dizzy: "If your opponent's Active Pokémon is Confused, this attack does 90 more
/// damage." Only Confusion counts: 10 against an Asleep, Paralyzed, Poisoned or Burned Active. The +90
/// comes before Weakness: 10 + 90 + 20 = 120 on a Confused Machop (A1 143, weak to [P]).
#[test]
fn test_malamar_pester_the_dizzy_needs_confusion_and_comes_before_weakness() {
    let id = CardId::PC005Malamar;
    for status in [
        StatusCondition::Asleep,
        StatusCondition::Paralyzed,
        StatusCondition::Poisoned,
        StatusCondition::Burned,
    ] {
        let mut game = board(vec![ready(id, 0)], vec![durable().with_status_condition(status)]);
        attack(&mut game, id, 0);
        assert_eq!(defender_damage(&game), 10, "{status:?}");
    }
    let machop = durable_of(CardId::A1143Machop).with_status_condition(StatusCondition::Confused);
    let mut game = board(vec![ready(id, 0)], vec![machop]);
    attack(&mut game, id, 0);
    assert_eq!(defender_damage(&game), 10 + 90 + 20);
}

/// The printings R8-08a maps: each is Complete, with no known limitation.
#[test]
fn test_mapped_438_printings_report_complete() {
    for id in [
        CardId::C1045Electrode,
        CardId::C1050Pawmot,
        CardId::C1142Pawmot,
        CardId::C1216Pawmot,
        CardId::C1055Alakazam,
        CardId::C1197Alakazam,
        CardId::C1060Espeon,
        CardId::C1076Pupitar,
        CardId::C1146Pupitar,
        CardId::C1078Whiscash,
        CardId::C1084Umbreon,
        CardId::C1186Umbreon,
        CardId::C1102Pidgey,
        CardId::C1104Pidgeot,
        CardId::C1107Eevee,
        CardId::C1110PorygonZ,
        CardId::PC005Malamar,
    ] {
        assert_eq!(
            get_implementation_status(id),
            ImplementationStatus::Complete,
            "{id:?}"
        );
        assert!(implementation_limitations(id).is_empty(), "{id:?}");
    }
}

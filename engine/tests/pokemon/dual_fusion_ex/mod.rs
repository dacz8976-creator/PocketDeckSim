// Upstream #431's tests (6ee270b), adapted to this fork: damage is read with `Taken` below (upstream's
// `public_details().damage` is not in this fork), and supported_designs.rs has its own Trainer helpers.
use deckgym::{
    actions::Action,
    card_ids::CardId,
    database::get_card_by_enum,
    models::PlayedCard,
    test_support::{attack_action, get_initialized_game_with_board},
    Game,
};
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
// Extra HP isolates random damage branches from knockout and promotion choices.
fn durable() -> PlayedCard {
    PlayedCard::new(
        get_card_by_enum(CardId::A1211Snorlax),
        0,
        1000,
        vec![],
        false,
        vec![],
    )
}
fn ready(id: CardId, index: usize) -> PlayedCard {
    let deckgym::models::Card::Pokemon(p) = get_card_by_enum(id) else {
        panic!("Pokémon required")
    };
    PlayedCard::from_id(id).with_energy(p.attacks[index].energy_required.clone())
}
fn board(seed: u64, ours: Vec<PlayedCard>, theirs: Vec<PlayedCard>) -> Game<'static> {
    get_initialized_game_with_board(seed, 0, 3, ours, theirs)
}
fn attack(game: &mut Game<'static>, id: CardId, index: usize) {
    game.apply_action(&Action {
        actor: 0,
        action: attack_action(id, index),
        is_stack: false,
    });
}

mod alolan_exeggutor;

mod fuecoco;

mod lycanroc;

mod mega_dragonite;

mod mega_mewtwo_y;

mod mega_skarmory;

mod mega_tyranitar;

mod mew;

mod supported_designs;

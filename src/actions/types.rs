use crate::actions::abilities::DiscardSearchKind;
use crate::models::{Attack, Card, EnergyType, StatusCondition, TrainerCard};
use serde::{Deserialize, Serialize};
use std::fmt;

/// Main structure for following Game Tree design. Using "nesting" with a
/// SimpleAction to share common fields here.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Action {
    pub actor: usize,
    pub action: SimpleAction,
    pub is_stack: bool,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum SimpleAction {
    DrawCard {
        amount: u8,
    },
    Play {
        trainer_card: TrainerCard,
    },

    // Card because of the fossil Trainer Cards...
    // usize is bench 1-based index, with 0 meaning Active pokemon, 1..4 meaning Bench
    Place(Card, usize),
    Evolve {
        evolution: Card,
        in_play_idx: usize,
        from_deck: bool,
    },
    UseAbility {
        in_play_idx: usize,
    },

    // Use the carried Attack definition as the current attack of the active Pokemon.
    // Carrying the whole Attack (instead of an index) lets a single codepath serve the
    // active's own attacks, copied attacks (e.g. Mew ex's Genome Hacking), and attacks
    // granted from previous evolutions (e.g. Celebi's Time Recall).
    Attack(Attack),
    // usize is in_play_pokemon index to retreat to. Can't Retreat(0)
    Retreat(usize),
    EndTurn,

    // Atomic actions as part of different effects.
    Attach {
        attachments: Vec<(u32, EnergyType, usize)>, // (amount, energy_type, in_play_idx)
        is_turn_energy: bool, // true if this is the energy from the zone that can be once per turn
    },
    MoveEnergy {
        from_in_play_idx: usize,
        to_in_play_idx: usize,
        energy_type: EnergyType,
        amount: u32,
    },
    /// Move a specific (possibly mixed-type) set of Energy between two of the actor's
    /// in-play Pokémon (e.g. Swanna's Feathery Cyclone, Regice's Reflect Energy).
    MoveEnergies {
        from_in_play_idx: usize,
        to_in_play_idx: usize,
        energies: Vec<EnergyType>,
    },
    AttachTool {
        in_play_idx: usize,
        tool_card: Card,
    },
    Heal {
        in_play_idx: usize,
        amount: u32,
        cure_status: bool,
    },
    HealAndDiscardEnergy {
        in_play_idx: usize,
        heal_amount: u32,
        discard_energies: Vec<EnergyType>,
    },
    /// Heal and cure a *specific subset* of Special Conditions (e.g. Whitney, which recovers from
    /// being Asleep, Paralyzed and Confused but leaves Poisoned and Burned alone). `Heal`'s
    /// `cure_status` flag is all-or-nothing, so it cannot express this.
    HealAndCureConditions {
        in_play_idx: usize,
        amount: u32,
        conditions: Vec<StatusCondition>,
    },
    MoveAllDamage {
        from: usize,
        to: usize,
    },
    /// Acerola: move up to `amount` damage off one of your Pokémon and onto the opponent's Active
    /// Pokémon. Only as much damage as the source actually carries is moved.
    MoveDamageToOpponentActive {
        from_in_play_idx: usize,
        amount: u32,
    },
    ApplyDamage {
        attacking_ref: (usize, usize), // (attacking_player, attacking_pokemon_idx)
        targets: Vec<(u32, usize, usize)>, // Vec of (damage, target_player, in_play_idx)
        is_from_active_attack: bool,
    },
    /// Resolve a target choice that belongs to an attack whose attacker-side gates have already
    /// run. The original Attack is carried so defender prevention, damage modification, knockout
    /// coins and attribution use its title/effect without recording or gating the attack twice.
    ApplyQueuedAttackDamage {
        attack: Attack,
        /// `(raw damage, is opponent target, in-play index)`, relative to `Action::actor`.
        targets: Vec<(u32, bool, usize)>,
    },
    ScheduleDelayedSpotDamage {
        target_player: usize,
        target_in_play_idx: usize,
        amount: u32,
        /// Armaldo's Abyssal Drop: the spot is KNOCKED OUT rather than dealt `amount` damage.
        /// Resolved at trigger time against whatever occupies the spot then.
        knock_out: bool,
    },
    /// §47 — Move a specific multiset of Energy from one or more of your Pokémon onto one
    /// destination, in a single action.
    ///
    /// Exists so that Vaporeon's Wash Out and Delcatty's Energy Blender can present a *complete*
    /// redistribution as one decision instead of a repeated one-Energy-at-a-time choice, which is
    /// what made them a branching-factor bomb (§43-D). See `actions::energy_moves`.
    ConsolidateEnergyToPokemon {
        to_in_play_idx: usize,
        /// `(from_in_play_idx, energies to move off it)`, in ascending source order.
        transfers: Vec<(usize, Vec<EnergyType>)>,
    },
    /// Switch the in_play_idx pokemon with the active pokemon.
    Activate {
        player: usize,
        in_play_idx: usize,
    },
    /// Compulsory replacement after the Active Spot becomes empty.
    ///
    /// Only `State::trigger_promotion_or_declare_winner` constructs this variant. Keeping it
    /// distinct from `Activate` lets search resolve the mandatory continuation without treating
    /// effect-driven switches as free promotion.
    Promote {
        player: usize,
        in_play_idx: usize,
    },
    // Custom Mechanics:
    /// Pokemon Communication: swap a specific Pokemon from hand with a random Pokemon from deck
    CommunicatePokemon {
        hand_pokemon: Card,
    },
    /// May: shuffle specific Pokemon from hand into your deck (no replacement)
    ShufflePokemonIntoDeck {
        hand_pokemon: Vec<Card>,
    },
    /// Maintenance: shuffle specific cards from hand into your deck, then draw a card
    ShuffleOwnCardsIntoDeck {
        cards: Vec<Card>,
    },
    /// Kid's Room: switch a specific card from hand with a random Pokemon Tool card from deck
    SwitchHandCardForRandomTool {
        hand_card: Card,
    },
    /// Shuffle a specific card from the opponent's hand into their deck. Silver restricts the
    /// choice to Supporters, Purugly's Interrupt allows any card; the restriction lives at the
    /// site that builds the choices, not here.
    ShuffleOpponentHandCard {
        card: Card,
    },
    /// Mega Absol Ex: discard a specific Supporter from opponent's hand
    DiscardOpponentSupporter {
        supporter_card: Card,
    },
    /// Discard multiple specific cards from own hand
    DiscardOwnCards {
        cards: Vec<Card>,
    },
    /// Slowking's Litter: discard the chosen cards from your own hand, then have the attacking
    /// Pokémon deal `damage_per_card` × (number of cards discarded) to the opponent's Active
    /// Pokémon. The damage depends on a choice the player makes *after* the attack resolves, so
    /// it cannot be carried in the attack's own `AttackOutcome`.
    DiscardOwnCardsForAttackDamage {
        cards: Vec<Card>,
        damage_per_card: u32,
    },
    /// Lusamine: attach energies from discard to a Pokemon
    AttachFromDiscard {
        in_play_idx: usize,
        num_random_energies: usize,
    },
    /// Volkner: attach a fixed number of a specific energy type from discard to a Pokemon
    AttachTypedFromDiscard {
        in_play_idx: usize,
        energy_type: EnergyType,
        count: usize,
    },
    /// Professor Sada: attach 3 specific different-typed energies from discard to Ancient Pokémon
    SadaAttach {
        assignments: Vec<(EnergyType, usize)>, // (energy_type, in_play_idx) × 3
    },
    /// Eevee Bag Option 1: Apply damage boost for Eevee evolutions this turn
    ApplyEeveeBagDamageBoost,
    /// Eevee Bag Option 2: Heal all Eevee evolutions
    HealAllEeveeEvolutions,
    /// Discard a Fossil from play (Fossils can be discarded at any time during your turn)
    DiscardFossil {
        in_play_idx: usize,
    },
    /// Use an activated stadium effect (once per turn per player)
    UseStadium,
    /// Return a Pokemon in play to your hand (e.g., Ilima).
    ReturnPokemonToHand {
        in_play_idx: usize,
    },
    /// Shuffle a Pokemon from play into its owner's deck (e.g., Professor Turo).
    ShuffleInPlayPokemonIntoDeck {
        in_play_idx: usize,
    },
    /// Field Blower: discard one selected Tool from a specific Pokémon (any player).
    DiscardToolFromPokemon {
        player: usize,
        in_play_idx: usize,
        #[serde(default)]
        tool_idx: usize,
    },
    /// Field Blower: discard the active stadium.
    DiscardActiveStadium,
    /// Pokémon Flute: put a Basic Pokémon from the opponent's discard pile onto their Bench.
    BenchOpponentFromDiscard {
        card: Card,
        bench_idx: usize,
    },
    /// Team Rocket's Boss: put this chosen multiset of Basic Pokémon from the opponent's hand
    /// into the first available opponent Bench slots. An empty vector is the printed choose-zero.
    BenchOpponentHandBasics {
        cards: Vec<Card>,
    },
    /// Delcatty's Search for Friends: put a specific, player-chosen card from your own discard
    /// pile into your hand.
    PutCardFromDiscardToHand {
        card: Card,
    },
    /// Galarian Perrserker's Dig Up: put `amount` *random* cards of `card_kind` from your own
    /// discard pile into your hand. Which cards is decided at forecast time, so the search bots
    /// see the real distribution instead of a pre-picked answer.
    PutRandomCardsFromDiscardToHand {
        card_kind: DiscardSearchKind,
        amount: u8,
    },
    /// Crawdaunt's Unruly Claw: discard a random Energy from the opponent's Active Pokémon
    DiscardRandomOpponentActiveEnergy,
    /// Dark Pendant: your opponent reveals a random card from their hand and shuffles it into
    /// their deck. Which card is picked is decided when the action is applied, exactly like the
    /// attacks that print the same sentence (Liepard's Snatch and Flee & co.).
    ShuffleRandomOpponentHandCard,
    /// Polteageist's Refreshing Tea: your opponent shuffles their hand into their deck and draws
    /// one card for each remaining point they need to win. Identical to Mars' effect, which is
    /// where the shared implementation lives.
    OpponentShuffleHandAndDrawRemainingPoints,
    /// Psychic (Supporter): move a random Energy from one of the opponent's Benched Pokémon to
    /// the opponent's Active Pokémon.
    MoveRandomOpponentEnergyToActive {
        from_in_play_idx: usize,
    },
    /// Apply a chosen Special Condition to the opponent's Active Pokémon (e.g. Dustox's Select Powder).
    ApplyStatusToOpponentActive {
        condition: StatusCondition,
    },
    /// Gyarados' Wild Swing: discard the chosen Benched Pokémon of your own (and everything
    /// attached to them), then deal `damage` to the opponent's Active Pokémon. The two halves have
    /// to travel together because the damage is a function of how many Pokémon were discarded, so
    /// the player's choice decides both at once. Applying it queues the damage as a follow-up
    /// `ApplyDamage` so the ordinary damage pipeline (modifiers, counterattacks, Guts) still runs.
    DiscardOwnBenchedThenDamage {
        in_play_idxs: Vec<usize>,
        damage: u32,
    },
    /// Accept the sampled attack-effect coin batch stored in State.
    KeepAttackCoinResults,
    /// Ignore the sampled batch and commit one fresh replacement batch.
    RerollAttackCoins {
        victory_star_in_play_idx: usize,
    },
    /// Accept the sampled Trainer-effect coin batch stored in State.
    KeepTrainerCoinResults,
    /// Ignore the sampled Trainer batch and commit one fresh replacement batch.
    RerollTrainerCoins {
        luxury_coin_in_play_idx: usize,
    },
    /// Fix Misty's printed Water-Pokemon target before its first coin is sampled.
    ChooseMistyTarget {
        in_play_idx: usize,
    },
    Noop, // No operation, used to have the user say "no" to a question
}

impl fmt::Display for SimpleAction {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SimpleAction::DrawCard { amount } => write!(f, "DrawCard({amount})"),
            SimpleAction::Play { trainer_card } => write!(f, "Play({trainer_card:?})"),
            SimpleAction::Place(card, index) => write!(f, "Place({card}, {index})"),
            SimpleAction::Evolve {
                evolution,
                in_play_idx,
                from_deck,
            } => {
                write!(
                    f,
                    "Evolve({evolution}, {in_play_idx}, from_deck: {from_deck})"
                )
            }
            SimpleAction::UseAbility { in_play_idx } => write!(f, "UseAbility({in_play_idx})"),
            SimpleAction::Attack(attack) => write!(f, "Attack({})", attack.title),
            SimpleAction::Retreat(index) => write!(f, "Retreat({index})"),
            SimpleAction::EndTurn => write!(f, "EndTurn"),
            SimpleAction::Attach {
                attachments,
                is_turn_energy,
            } => {
                let attachments_str = attachments
                    .iter()
                    .map(|(amount, energy_type, in_play_idx)| {
                        format!("({amount}, {energy_type:?}, {in_play_idx})")
                    })
                    .collect::<Vec<_>>()
                    .join(", ");
                write!(f, "Attach({attachments_str:?}, {is_turn_energy})")
            }
            SimpleAction::MoveEnergy {
                from_in_play_idx,
                to_in_play_idx,
                energy_type,
                amount,
            } => {
                write!(
                    f,
                    "MoveEnergy(from:{from_in_play_idx}, to:{to_in_play_idx}, {amount}x {energy_type:?})"
                )
            }
            SimpleAction::MoveEnergies {
                from_in_play_idx,
                to_in_play_idx,
                energies,
            } => {
                write!(
                    f,
                    "MoveEnergies(from:{from_in_play_idx}, to:{to_in_play_idx}, {energies:?})"
                )
            }
            SimpleAction::AttachTool {
                in_play_idx,
                tool_card,
            } => {
                write!(f, "AttachTool({in_play_idx}, {})", tool_card.get_name())
            }
            SimpleAction::Heal {
                in_play_idx,
                amount,
                cure_status,
            } => write!(f, "Heal({in_play_idx}, {amount}, cure:{cure_status})"),
            SimpleAction::HealAndDiscardEnergy {
                in_play_idx,
                heal_amount,
                discard_energies,
            } => write!(
                f,
                "HealAndDiscardEnergy({in_play_idx}, {heal_amount}, {discard_energies:?})"
            ),
            SimpleAction::HealAndCureConditions {
                in_play_idx,
                amount,
                conditions,
            } => write!(
                f,
                "HealAndCureConditions({in_play_idx}, {amount}, {conditions:?})"
            ),
            SimpleAction::MoveAllDamage { from, to } => {
                write!(f, "MoveAllDamage(from:{from}, to:{to})")
            }
            SimpleAction::MoveDamageToOpponentActive {
                from_in_play_idx,
                amount,
            } => write!(f, "MoveDamageToOpponentActive({from_in_play_idx}, {amount})"),
            SimpleAction::ApplyDamage {
                attacking_ref,
                targets,
                is_from_active_attack,
            } => {
                let targets_str = targets
                    .iter()
                    .map(|(damage, target_player, in_play_idx)| {
                        format!("({damage}, {target_player}, {in_play_idx})")
                    })
                    .collect::<Vec<_>>()
                    .join(", ");
                write!(
                    f,
                    "ApplyDamage(attacker:{:?}, targets:[{}], from_active:{})",
                    attacking_ref, targets_str, is_from_active_attack
                )
            }
            SimpleAction::ApplyQueuedAttackDamage { attack, targets } => {
                let targets_str = targets
                    .iter()
                    .map(|(damage, is_opponent, in_play_idx)| {
                        format!("({damage}, opponent:{is_opponent}, {in_play_idx})")
                    })
                    .collect::<Vec<_>>()
                    .join(", ");
                write!(
                    f,
                    "ApplyQueuedAttackDamage({}, targets:[{}])",
                    attack.title, targets_str
                )
            }
            SimpleAction::ScheduleDelayedSpotDamage {
                target_player,
                target_in_play_idx,
                amount,
                knock_out,
            } => write!(
                f,
                "ScheduleDelayedSpotDamage(target:{target_player}:{target_in_play_idx}, amount:{amount}, ko:{knock_out})"
            ),
            SimpleAction::Activate {
                player,
                in_play_idx,
            } => write!(f, "Activate({player}, {in_play_idx})"),
            SimpleAction::Promote {
                player,
                in_play_idx,
            } => write!(f, "Promote({player}, {in_play_idx})"),
            SimpleAction::CommunicatePokemon { hand_pokemon } => {
                write!(f, "CommunicatePokemon({hand_pokemon})")
            }
            SimpleAction::ShufflePokemonIntoDeck { hand_pokemon } => {
                write!(f, "ShufflePokemonIntoDeck({:?})", hand_pokemon)
            }
            SimpleAction::ShuffleOwnCardsIntoDeck { cards } => {
                write!(f, "ShuffleOwnCardsIntoDeck({:?})", cards)
            }
            SimpleAction::SwitchHandCardForRandomTool { hand_card } => {
                write!(f, "SwitchHandCardForRandomTool({hand_card})")
            }
            SimpleAction::ShuffleOpponentHandCard { card } => {
                write!(f, "ShuffleOpponentHandCard({card})")
            }
            SimpleAction::DiscardOpponentSupporter { supporter_card } => {
                write!(f, "DiscardOpponentSupporter({supporter_card})")
            }
            SimpleAction::DiscardOwnCards { cards } => {
                write!(f, "DiscardOwnCards({:?})", cards)
            }
            SimpleAction::DiscardOwnCardsForAttackDamage {
                cards,
                damage_per_card,
            } => {
                write!(
                    f,
                    "DiscardOwnCardsForAttackDamage({cards:?}, {damage_per_card})"
                )
            }
            SimpleAction::AttachFromDiscard {
                in_play_idx,
                num_random_energies,
            } => {
                write!(f, "AttachFromDiscard({in_play_idx}, {num_random_energies})")
            }
            SimpleAction::AttachTypedFromDiscard {
                in_play_idx,
                energy_type,
                count,
            } => {
                write!(f, "AttachTypedFromDiscard({in_play_idx}, {energy_type:?}, {count})")
            }
            SimpleAction::SadaAttach { assignments } => {
                let s = assignments
                    .iter()
                    .map(|(e, idx)| format!("{e:?}→{idx}"))
                    .collect::<Vec<_>>()
                    .join(", ");
                write!(f, "SadaAttach([{s}])")
            }
            SimpleAction::ApplyEeveeBagDamageBoost => {
                write!(f, "ApplyEeveeBagDamageBoost")
            }
            SimpleAction::HealAllEeveeEvolutions => {
                write!(f, "HealAllEeveeEvolutions")
            }
            SimpleAction::DiscardFossil { in_play_idx } => {
                write!(f, "DiscardFossil({in_play_idx})")
            }
            SimpleAction::ReturnPokemonToHand { in_play_idx } => {
                write!(f, "ReturnPokemonToHand({in_play_idx})")
            }
            SimpleAction::ShuffleInPlayPokemonIntoDeck { in_play_idx } => {
                write!(f, "ShuffleInPlayPokemonIntoDeck({in_play_idx})")
            }
            SimpleAction::DiscardToolFromPokemon { player, in_play_idx, tool_idx } => {
                write!(f, "DiscardToolFromPokemon({player}, {in_play_idx}, {tool_idx})")
            }
            SimpleAction::DiscardActiveStadium => write!(f, "DiscardActiveStadium"),
            SimpleAction::BenchOpponentFromDiscard { card, bench_idx } => {
                write!(f, "BenchOpponentFromDiscard({card}, {bench_idx})")
            }
            SimpleAction::BenchOpponentHandBasics { cards } => {
                write!(f, "BenchOpponentHandBasics({cards:?})")
            }
            SimpleAction::PutCardFromDiscardToHand { card } => {
                write!(f, "PutCardFromDiscardToHand({card})")
            }
            SimpleAction::PutRandomCardsFromDiscardToHand { card_kind, amount } => {
                write!(f, "PutRandomCardsFromDiscardToHand({card_kind:?}, {amount})")
            }
            SimpleAction::DiscardRandomOpponentActiveEnergy => {
                write!(f, "DiscardRandomOpponentActiveEnergy")
            }
            SimpleAction::OpponentShuffleHandAndDrawRemainingPoints => {
                write!(f, "OpponentShuffleHandAndDrawRemainingPoints")
            }
            SimpleAction::ShuffleRandomOpponentHandCard => {
                write!(f, "ShuffleRandomOpponentHandCard")
            }
            SimpleAction::MoveRandomOpponentEnergyToActive { from_in_play_idx } => {
                write!(f, "MoveRandomOpponentEnergyToActive({from_in_play_idx})")
            }
            SimpleAction::ConsolidateEnergyToPokemon {
                to_in_play_idx,
                transfers,
            } => write!(
                f,
                "ConsolidateEnergyToPokemon(to:{to_in_play_idx}, {transfers:?})"
            ),
            SimpleAction::UseStadium => write!(f, "UseStadium"),
            SimpleAction::ApplyStatusToOpponentActive { condition } => {
                write!(f, "ApplyStatusToOpponentActive({condition:?})")
            }
            SimpleAction::DiscardOwnBenchedThenDamage {
                in_play_idxs,
                damage,
            } => write!(f, "DiscardOwnBenchedThenDamage({in_play_idxs:?}, {damage})"),
            SimpleAction::KeepAttackCoinResults => write!(f, "KeepAttackCoinResults"),
            SimpleAction::RerollAttackCoins {
                victory_star_in_play_idx,
            } => write!(f, "RerollAttackCoins(VictoryStar:{victory_star_in_play_idx})"),
            SimpleAction::KeepTrainerCoinResults => write!(f, "KeepTrainerCoinResults"),
            SimpleAction::RerollTrainerCoins {
                luxury_coin_in_play_idx,
            } => write!(f, "RerollTrainerCoins(LuxuryCoin:{luxury_coin_in_play_idx})"),
            SimpleAction::ChooseMistyTarget { in_play_idx } => {
                write!(f, "ChooseMistyTarget({in_play_idx})")
            }
            SimpleAction::Noop => write!(f, "Noop"),
        }
    }
}

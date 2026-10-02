# Wallace: a second read of the stale-note flag (Sonnet, Oct 1, 2026)

For the coordinator and the laptop Opus, before the rules switch's step 13 edits the rules notes. Read-only: nothing in the engine or the
rules files was changed. Everything below is read at 24ef210 (main when the readout was written; the engine, test and rules files named are
unchanged at 1ba07d9, today's main; line numbers are approximate to a line or two). The tests were read, not run.

## 1. The answer

**Yes, both notes are stale, and so is a third that the readout did not list.** The engine does what the plain card text says. The notes
describe the engine before the rules1 repair (Sept 22).

| Note | What it says | What is true |
|---|---|---|
| `rules/02_damage_knockouts_points.md:153` | the engine's Wallace check reads printed HP (`card_logic/wallace.rs`), so it would allow a Giant Cape Staryu | Wrong now. Both the playability check and the effect read the current maximum HP. |
| `rules/04_actions_cards_effects.md:91` (the Wallace clause) | "Probably also wrong by the same rule: Wallace (blocked unless a matching Water evolution is in the deck, `card_logic/wallace.rs`)" | Wrong now. Wallace is blocked only when the deck is empty or no eligible Water Pokémon is in play. What the deck holds does not matter. |
| `rules/05_open_questions.md:85` (not in the readout) | "Engine: timing ✓; reads printed HP ✗ (on Astra's list)" | The printed-HP half is fixed; the same fix as the first note. |

`rules/04:175`, `rules/09:38-39`, `rules/10:38` and `rules/README.md:107` already say the repair was made ("Wallace uses maximum HP after
bonuses"); they are right. The two flagged notes and the one in `05` are older text that nobody revisited.

## 2. The card

`python3 lib/card.py "B3b 068"` (and `B3b 085`, the same text): **Wallace, Supporter.** "Choose 1 of your [W] Pokémon in play with a
maximum HP of 50 or less. Put a random [W] Pokémon from your deck that evolves from that Pokémon onto that Pokémon to evolve it."

By Dustin's Oct 1 rule (the plain reading of the text is the default unless something contradicts it), the text says four things:
1. **The player chooses the target**, a Water Pokémon in play. The deck's randomness comes only after the choice.
2. **"Maximum HP of 50 or less" is the current maximum**, bonuses included. The official Detailed Battle FAQ says so in terms: "If your
   Pokémon's maximum HP increases to more than 50, such as with a card effect, you can no longer choose it" (article 59513864093209;
   `rules/_research_notes/detailed_battle_faq.md:29-31`: a 50-HP Staryu with Giant Cape is 70 and not selectable). Damage does not
   change the maximum.
3. **No timing limit is printed.** Quick-Grow Extract prints "You can't use this card during your first turn or on a Pokémon that was put
   into play this turn". Wallace prints neither, so neither applies (as `rules/04:42` already says).
4. **The deck's contents are hidden**, so they cannot stop the card from being played. Dustin's rule (`rules/04:82`) blocks a card only
   when what is visible shows it cannot work. The visible conditions here are a nonempty deck and an eligible Water Pokémon in play.

## 3. What the engine does at 24ef210

- **Playable?** `can_play_wallace` (`move_generation/move_generation_trainer.rs:988-1004`): a nonempty deck and a Water Pokémon in
  play whose `get_effective_total_hp()` is 50 or less. Nothing about the deck's contents and nothing about the turn.
- **Effect.** `wallace_effect` (`actions/apply_trainer_action.rs:2436-2458`): offers each in-play Water Pokémon with
  `get_effective_total_hp() <= 50` as a `ChooseRandomEvolutionTarget`. After the choice,
  `random_typed_evolution_outcomes` (`:2460-2510`) samples uniformly among the Water cards in the deck that evolve from that target,
  evolves it, and shuffles the deck, and with no such card in the deck it only shuffles. So the player picks the target and the deck picks
  the evolution, as the text reads.
- **"Effective" maximum HP** (`state/played_card.rs:290-311`): printed HP plus Giant Cape, Leaf Cape (Grass), Elegant Cape (Stage 1),
  the Ancient capsule, the Stadium bonus (Starting Plains) and Ability bonuses. Damage taken is not in it.
- **Pinned by tests.** `rules_repair_trainers.rs:276` `wallace_uses_effective_max_hp_and_randomizes_only_after_target_choice`
  (Staryu with Giant Cape is not offered; the Magikarp is; both Magikarp evolutions are sampled and Starmie never).
  `trainers/wallace_test.rs`: evolves a low-HP Water Pokémon from the deck; can evolve a Pokémon played this turn; no valid target means
  the card is not playable. No test covers Starting Plains, Leaf Cape or Elegant Cape on a Wallace target, or an empty-deck refusal.
- **Dead code behind the old notes.** `card_logic/wallace.rs::wallace_candidates` still reads printed HP (`pokemon_card.hp > 50`) and
  still requires an evolution in the deck, which is exactly what the notes describe. It is exported (`card_logic/mod.rs:18`) and **has no
  caller anywhere in `engine/`**. The notes cite a file the engine no longer runs. Deleting it, or a note on it, belongs to a later switch;
  it changes no game.

## 4. The evidence, and whether anything contradicts the plain reading

- **Giant Cape and the maximum:** the official FAQ above, plus Dustin's confirmation already in `rules/02:153` ("the game blocks it"). Not
  filmed. Nothing contradicts it.
- **First turn:** seen in 150630 turn 1: Wallace asks "Please choose a Pokémon to evolve" with the Active Magikarp and the Benched Carvanha
  both highlighted, Carvanha into Mega Sharpedo ex (`rules/_research_notes/main_session_findings.md:72`).
- **The Oct 1 recording 213822 (68-78 s):** Wallace evolved a 50-HP Carvanha into Mega Sharpedo ex from the deck: a Water Pokémon of
  maximum HP 50, a random compatible evolution, a chosen target. That is the plain reading. The lead's acceptance note says it "supplies no
  evidence of a same-turn exception", and the review's own list marks "Wallace evolution on the same turn a Basic enters play" untested.
  So the footage neither supports nor contradicts the same-turn use. The plain text, Dustin ("almost positive", `rules/05:85`) and the
  engine agree.
- **What the game offers when no evolution is in the deck:** unknown. `rules/10` R5 notes that in 150630 both highlighted Pokémon had
  evolutions, so we do not know whether the game would also highlight one with none. The plain text names no such condition, and the deck
  is hidden, so the plain reading is "any eligible Water Pokémon, and a miss shuffles". The engine does that.

Nothing contradicts the plain reading, so the plain reading stands.

## 5. What the notes should say

**`rules/02:153`**, replace the whole bullet with:

> Cards that care about maximum HP read the boosted value: Wallace can't choose a 50-HP Staryu wearing Giant Cape (maximum HP 70), and
> damage doesn't change maximum HP. [OFFICIAL] Detailed Battle FAQ (article 59513864093209) + Dustin. Engine ✓ since rules1: Wallace's
> playability check and its effect both read the current maximum HP (`can_play_wallace`, `wallace_effect`; test
> `wallace_uses_effective_max_hp_and_randomizes_only_after_target_choice`). `card_logic/wallace.rs` is old code with no caller.

**`rules/04:91`**: take Wallace out of the "probably also wrong" sentence, and see section 6, because the whole ⚠ paragraph is stale.

**`rules/05:85`** (Wallace): change the last sentence to "Engine ✓ (timing; maximum HP after bonuses, rules1; `09`)", and add: "Seen again in
213822 (68-78 s): a 50-HP Water Pokémon chosen, a random compatible evolution from the deck; the same-turn case is still not filmed, and
the plain text (no timing limit printed) decides it."

**Wallace in the playability rule** (suggested line for `rules/04` §6, next to the Cabbie and Gladion examples): "Wallace: playable with a
nonempty deck and a visible Water Pokémon in play with a current maximum HP of 50 or less; whether the deck holds an evolution is hidden
and does not matter. [Plain text + Dustin's rule]. Engine ✓."

## 6. Beyond Wallace: the whole ⚠ paragraph in `rules/04:91` is stale

It is a snapshot of `deckgym-fork-s193` before rules1 (the path it cites). At 24ef210:
- **Gladion, Team Galactic Grunt, Clemont, Serena, Juliana, Cabbie, Arven, Traveling Merchant** are all `can_search_nonempty_deck`
  (`move_generation_trainer.rs:28-41`, dispatch at `:148-312`): blocked only on an empty deck. The text on the helper says why: "Its
  hidden contents cannot suppress the action before it resolves." So "Gladion still has the old block", "Team Galactic Grunt is blocked
  unless a Glameow/Stunky/Croagunk is in the deck" and "Cabbie (blocked unless a Stadium is in the deck)" are all fixed.
- **Pokémon Communication** (`:685-699`): needs a Pokémon in hand and a nonempty deck; the deck's contents are not read. Fixed.
- **Quick-Grow Extract** (`:963-983`): a nonempty deck, not the first turn, a visible Grass Pokémon not put into play this turn. Right.
- **The Tool-searching Ability check** (`move_generation_abilities.rs` around `:415`): I read only that it tests deck emptiness; I did
  not trace which card it serves, so I would not mark that one fixed without a second look.
- Dustin's "clean spec" (a card that takes from the deck is blocked only when the deck is empty) is now what the engine implements, so the
  paragraph can become one line: "Engine ✓ since rules1 (`09`): every 'from your deck' card is blocked only by an empty deck, never by what
  the deck holds."

## 7. Section 4's list: what else I read, and where I disagree

I read the whole of section 4 against the rules files, the engine and the review's evidence. **I agree with the list and with the open
cases at its end.** The disagreements are small, and the first one is a real addition:

1. **Add `rules/05:85` to step 13's edit list** (above). The readout names `rules/02:153` and `rules/04:91` only.
2. **The step 13 line for 203626 T12** ("Will's forced heads is used up on the first batch, and a Victory Star replacement is a fresh flip
   [OBSERVED 203626 T12, 336.3-347; DUSTIN]") is stronger than section 2.2 says. The readout itself notes that "Will forced the original
   first heads" is only inferred (a natural heads looks the same). What is seen is the replacement's first coin coming up tails. Suggest:
   "[OBSERVED 203626 T12: the replacement's first coin was tails; the original first heads is consistent with Will but not shown to be
   forced; DUSTIN: Will does not apply on a re-roll]".
3. **"The six helpers"** (the "Mark these fixed" line and the open case 4): my source reading of repair B counts seven helper functions
   (`direct_damage`, `direct_damage_and_self_card_effect`, `direct_damage_if_damaged`, the discard-all-energy-of-a-type attack, the
   self-discard-then-snipe attack, damage per target energy, switch-in-then-damage) plus Chase Order's no-discard choice and its
   discard branch (`EQUIVALENCE_sonnet.md` section 2, rows 12 to 20). If the plan counts six, check which one it leaves out before the
   number goes into `rules/09`.
4. **Trap Territory.** I agree with the plain reading. The card is `Ability: Trap Territory: Your opponent's Active Pokémon's Retreat Cost
   is 1 more.` on each Ariados, and `rules/04:61` already has "Passive same-name Abilities stack" (two Lucario). Label the new line as
   arithmetic, as proposed: 40 + 30 x (printed 2 + 1 + 1) = 160 is the only reading that fits. I have no other disagreement with it.
5. **The Water Shuriken line for `rules/02:57`** rests on two card lookups the readout says the finding made: Typhlosion ex is Fire with
   Weakness Water (confirmed here: B4 026/181/195 `wk Water`), and Greninja is Water. Fine; keep the "plain 20, no Weakness" wording as
   an observation about Ability damage, which `rules/02:80` already states as a rule.

Not disagreements, but things the next reader should know: the F4 test comment and `card_validation.rs:97` stay as they are in R
(correct: they are R's files, and R is pinned); and `card_logic/wallace.rs` has no caller, as in section 3, so a later cleanup can drop
it with no behaviour change.

# B — In-game text findings (Pokémon TCG Pocket)

Scope: official in-app Help/Rules text, tutorial, glossary, UI messages. Grading: INGAME-QUOTED / DATAMINE / COMMUNITY / MEMORY-UNVERIFIED.

---

## Official Pokémon Support pages (highest authority — these ARE the "in-app rules" surface, published by Creatures/Pokémon Co. as the canonical FAQ referenced from in-game help)

### Source: Pokémon TCG Pocket Battle Rules FAQ
URL: https://support.pokemon.com/hc/en-us/articles/38906248102292-Pok%C3%A9mon-TCG-Pocket-Battle-Rules-FAQ
Grade: INGAME-QUOTED (official Pokémon Support rules clarifications, the canonical rulings source; not literally the in-app screen text but Pokémon Co.'s own battle-rules FAQ)

- **Q16 (damage calc / energy-cost display):** "If no Energy symbol is displayed to the left of the attack name on a card, then it is an attack that can be used without any Energy attached to the Pokémon." — confirms 0-cost attacks are usable with no Energy.
- **Q20 (KO points vs discard):** Players only earn points when opponent Pokémon are **knocked out**, not when discarded through card effects. Direct rule: discard ≠ KO, no points for discard-effect removal.
- **Prank Spinner ruling:** shuffles only ONE card (from either player's hand, chosen by the card's user) into its owner's deck — clarifies a specific card's targeting (tangential to Q41/Q42 targeting questions, shows official ruling process exists for ambiguous card text).
- **Jolteon ex's Electromagnetic Wall ruling (relevant to Q46):** the ability "activates only when Energy is attached from the Energy Zone to a Pokémon. It doesn't trigger when Energy moves from the discard pile or transfers between Pokémon." — Confirms game engine distinguishes "attach from Energy Zone" as a distinct event type from other energy-movement effects. Relevant to Q46 (effects that attach from the Energy Zone outside the manual attachment) — shows the manual/Zone-sourced attachment is a specific trackable event.
- **Buzzwole ex's Big Beat ruling (relevant to Q29/Q33):** the attack CAN be used on consecutive turns despite "can't use next turn"-style attack text, because **"all effects applied to a Pokémon are removed when that Pokémon returns to the Bench,"** resetting the restriction. — Directly answers Q33 (effects attached to the Active from attacks end when it moves to Bench) with an official quote: bench-return clears attached attack-effects.
- **Scizor's Gale Thrust ruling (relevant to Q29 evolution/promotion distinctions):** the attack's extra damage applies **only if Scizor moves from Bench to Active during the turn it uses the attack** — NOT if it becomes Active because the opponent KO'd the prior Active (forced promotion) or through evolution. Shows the game distinguishes "self-retreated/switched into Active this turn" from "promoted after KO" and from "evolved while already Active" as different game-state triggers.

### Source: Pokémon TCG Pocket Gameplay FAQ
URL: https://support.pokemon.com/hc/en-us/articles/30330309361172-Pok%C3%A9mon-TCG-Pocket-Gameplay-FAQ
Grade: INGAME-QUOTED for the one rules line quoted; rest is COMMUNITY/non-rules (app/UI support content)

- Explicit statement: **"The rules of Pokémon TCG Pocket are different from the Pokémon Trading Card Game."** Page does NOT itself contain detailed gameplay rules — it refers players to the official website and in-game tips instead. So this FAQ is NOT a rules source for our questions, just confirms Pocket has its own distinct ruleset (supports the instruction to never assume a physical-TCG rule applies).
- **Q14 (tie/draw handling in Ranked):** "If your game ends in a tie, your ranked match points will not increase or decrease. However, your win streak points will be reset." — Confirms ties ARE a possible outcome tracked distinctly from win/loss in Ranked (supports Q14's premise that draws exist as a real outcome), though this is about ranking-point consequences, not the in-battle tiebreak mechanism itself.
- **Q15 (disconnect handling):** "If you experience a crash or disconnection during a versus match, you may attempt to rejoin the match within the reconnection window of around 120 seconds. If you cannot reconnect within that timeframe, you lose the match." — Direct answer: disconnect >120s = automatic LOSS for the disconnecting player (not a draw, not free win voided).
- **Q49 (Ranked eligibility, not a rules difference per se):** Ranked matches require player level 3 to unlock; win-streak bonus caps at 5 consecutive wins (bonus does not keep growing beyond that). Rank points can decrease even after a win "due to changes in other players' rank points" (relative/pooled ranking system) — administrative/meta detail, not a battle-rule difference.
- No page content found on turn timers, deck size, hand limits, coin flips, Energy Zone, special conditions, or evolution mechanics — this FAQ does not cover those.

### Source: "Is there a difference in battle rules between the Pokémon Trading Card Game?"
URL: https://app-ptcgp.pokemon-support.com/hc/en-us/articles/39076901803801-Is-there-a-difference-in-battle-rules-between-the-Pok%C3%A9mon-Trading-Card-Game
Grade: INGAME-QUOTED (short) 

- Quote: **"The rules of the Pokémon Trading Card Game Pocket is different from the Pokémon Trading Card Game."** Directs to tcgpocket.pokemon.com and in-game documentation for specifics. No further detail extracted yet — confirms scope instruction (don't assume physical rules apply) is officially stated, but gives no specifics itself.

---

## GitHub repositories (datamine / localization strings)

### TCGP-Corpus-Lite
URL: https://github.com/superpikapool13/TCGP-Corpus-Lite
Live tool: https://superpikapool13.github.io/TCGP-Corpus-Lite/
Grade: DATAMINE (if confirmed to contain actual extracted game strings)

- Contains translation strings extracted by "SombrAbsol", organized by language (DE/EN/FR/ES/IT/JA/KO/PT-BR/ZH-TW), in a `locales/` directory, queryable via a web tool. Not yet confirmed whether it includes rules/glossary/tutorial strings specifically vs. only card text. **Investigating by cloning to scratch_B.**

---

## GitHub datamine — TCGP-Corpus-Lite (en_US locale strings) — MAJOR SOURCE
Repo: https://github.com/superpikapool13/TCGP-Corpus-Lite (cloned to /home/claude/rr/scratch_B/TCGP-Corpus-Lite)
Files used: `locales/en_US/UI.json` (actual in-game tutorial script + all battle UI messages/errors), `locales/en_US/Master.json` (card/ability/attack description templates)
Grade: **DATAMINE** — these are the literal extracted client localization strings, i.e. the exact in-game text (tutorial dialogue, UI toasts, error/blocking messages). Highest-confidence non-official source found; effectively equivalent to screenshotting the game since it's the actual string table. Credited to extractor "SombrAbsol" in the repo.

### Deck construction (Q1)
Exact in-game deck-legality check text (`deck_dialog_001_body` etc.):
> "This deck cannot be used because it does not meet one or more of the following conditions: • Consists of exactly 20 cards • Includes one or more Basic Pokémon • Has no more than two cards of the same name • Has Energy selected that allows one or more Pokémon to use their attacks • Built using owned cards only"

- `deck_toast_002`: **"You may only select up to three Energy types"** — confirms max 3 Energy types per deck.
- `deck_toast_006`: "Decks must have exactly 20 cards. Decks with more cards (up to 30) can be saved but not used" — a deck CAN be saved in an illegal (21–30 card) state but can't be used to battle.
- `deck_recommend_setting_body`: "Please select up to two types" — this is for a "recommend"/auto-suggest feature, not the hard cap (which is 3 per deck_toast_002).
- Energy-type generation rule (`deck_supply_energy_select_body`): **"Energy of the selected types will generate during battle. When multiple types are selected, a different type will generate at random on each of your turns."** — direct confirmation for Q6: each turn's generated type is randomly chosen among the deck's declared types, independently per turn.

### Setup (Q3)
- `battle_ui_message_body_txt_01`: "Please put a Basic Pokémon in the Active Spot."
- `battle_ui_message_body_txt_02`: "Only Basic Pokémon can be chosen."
- `battle_ui_message_body_txt_04`: "Please put up to 3 Basic Pokémon onto your Bench, then tap Start Battle." — confirms Bench setup is simultaneous (up to 3, chosen together before tapping Start), and optional/flexible count ("up to 3").
- `battle_ui_message_body_txt_05`: "Waiting for opponent to set up..." — confirms setup is done by both players in parallel (not sequential/visible to each other while placing).
- Tutorial: "During a real battle, you have the option to set up your Bench" (bench placement is optional, unlike Active which is mandatory).

### Who goes first (Q4)
- Coin flip UI strings confirm a coin-flip screen: `battle_ui_coin_flip_result_head_txt` "Heads!" / `_tail_txt` "Tails!", then `battle_ui_first_turn_heads_txt` "You are going first" / `battle_ui_first_turn_tails_txt` "You are going second"; also `battle_ui_start_coin_flip_heads_turn_txt`/`_tails_turn_txt` = "Going first"/"Going second"; `battle_ui_game_start_telop_start_txt` = "Ready? Go!". Post-game log shows `battle_result_info_detail_01/02` = "Went first"/"Went second". Confirms a coin flip determines turn order and the result is shown to the player, but the exact ordering (coin flip before or after Bench setup) is NOT unambiguously stated by these strings alone — inferred only.

### Turn structure / energy / hand limit (Q6, Q8, Q9)
- `battle_tutorial_introduction_message_01600`: **"You can have up to 10 cards in your hand, and you use these cards during the battle."** — confirms hand limit = 10.
- `battle_ui_message_body_txt_33`: **"Hand full; unable to draw cards"** — direct confirmation: when hand is full, the draw is simply skipped (not "discard down to limit"), for Q8.
- `battle_ui_message_body_txt_34`: **"No cards left in deck; unable to draw cards"** — deck-out just skips the draw (consistent with Q15's premise that deck-out isn't a loss — no separate loss message tied to this).
- `battle_ui_message_body_txt_46`: "Hand full; unable to return card" — same skip-logic applies to card-return effects.
- `battle_tutorial_bench_message_00100`: "Start your turn by drawing a card from your deck."
- `battle_tutorial_energy_active_message_00300/00400`: "When it is your turn, an Energy is generated in the Energy Zone." / "You can also see the Energy that will be generated during your next turn." — confirms Energy is generated on your own turn (implies P2 gets one turn-1 energy; doesn't explicitly answer whether P1 gets a turn-1 energy — the widely-known rule that P1 does NOT get a first-turn Energy is not directly contradicted or confirmed by this string alone).
- `battle_ui_next_energy_next_txt`: "Next Energy generated" — UI label confirming the "next energy" preview exists in-battle.
- `battle_ui_base_canvas_turn_end_btn_txt`: "End Turn" button exists; tutorial: "When you can't use an attack, tap the End Turn button to end your turn."

### Retreat (Q31)
Exact blocking messages:
- `battle_ui_message_body_txt_24`: **"The Pokémon can't retreat because you already retreated a Pokémon this turn"** — confirms once-per-turn.
- `battle_ui_message_body_txt_25`: "The Pokémon can't retreat because there are no Pokémon on the Bench"
- `battle_ui_message_body_txt_26`: "[CardName] can't retreat due to the effects of [AttackName]" — attack-effect-based retreat lock (distinct trigger from Special Conditions).
- `battle_ui_message_body_txt_28`: "Not enough Energy to retreat"
- `battle_ui_message_body_txt_38`: **"[CardName] can't attack or retreat because it's [SpecialCondition]"** — ONE shared message for both attack-block and retreat-block tied to a Special Condition (answers Q24: at least some Special Conditions block both attacking and retreating via the same game-state flag).
- Tutorial: "If you retreat, the Energy cost will be discarded from that Pokémon." / "You can retreat once per turn." / "You can still use an attack even if you retreated during that turn." — confirms retreat does NOT end the turn and can be followed by an attack (Q9).

### Special Conditions (Q22, Q23, Q24, Q25, Q26)
- `battle_tutorial_special_condition_message_00700`: **"Poisoned Pokémon take 10 damage during Pokémon Checkup."** — exact value confirmed.
- `battle_tutorial_special_condition_message_00800`: **"Pokémon will recover from Special Conditions, such as Poisoned, when they move to the Bench."** — direct confirmation Special Conditions are cured by moving to Bench (retreat or being replaced after KO).
- `battle_ui_coin_flip_dialog_body_txt_01/02/03`: "Pokémon Checkup — Asleep", "Pokémon Checkup — Burned", **"Coin flip — Confused"** — confirms Asleep and Burned flips happen AT Pokémon Checkup, while the Confused flip is labeled just "Coin flip" (not "Pokémon Checkup"), consistent with Confused being checked at time-of-attack rather than at Checkup (answers part of Q22).
- Message templates `battle_ui_message_body_logic_txt_84/85/86` show the game has UI text for a Pokémon becoming **1, 2, or 3 Special Conditions simultaneously** ("[CardName] is now [Cond1]", "...now [Cond1] and [Cond2]", "...now [Cond1], [Cond2], and [Cond3]") and symmetric "recovered from being [Cond1]/[Cond1] and [Cond2]/[Cond1], [Cond2], and [Cond3]" (txt_90/91/92). **This is strong evidence multiple Special Conditions CAN coexist on one Pokémon simultaneously** (up to 3 at once per the UI templates) — directly relevant to Q23.
- Healing does NOT automatically cure Special Conditions as a blanket rule — specific Trainer/Tool card text separately states "...and it recovers from all Special Conditions" (e.g. `TRAINER_DESC_36`, `TRAINER_DESC_64`) as an EXPLICIT additional clause distinct from the heal/HP-boost effect, implying plain healing alone does not cure conditions unless the card text says so (Q25 nuance).
- Card ability text confirms multiple ways Special Conditions are inflicted/cured, e.g. `ABILITY_DESC_45`: "Each of your Pokémon that has any [Energy] attached recovers from all Special Conditions and can't be affected by any Special Conditions" and `ABILITY_DESC_132`: "you may remove a random Special Condition from your Active Pokémon" (implying multiple could be present to choose from at random).
- `ATTACK_DESC_111`: an attack that randomly inflicts "1 Special Condition from among Asleep, Burned, Confused, Paralyzed, and Poisoned" and explicitly excludes ones "already affecting" — again implies conditions stack (otherwise no need to exclude already-present ones from the random pool while still allowing others).

### Damage / prevention effects (Q16, Q18, Q19)
Distinct, separately-worded prevention effect tiers found in the UI string table — precise answer to Q18:
- `battle_ui_status_effect_logic_description_txt_32` / `battle_ui_message_body_txt_56`: **"Prevent all damage done by attacks"** (damage-only block)
- `battle_ui_status_effect_logic_description_txt_28` / `battle_ui_message_body_txt_52`: **"Prevent all effects of attacks used by the opponent's Pokémon"** (effects-only block, e.g. blocks Special Conditions/other attack effects but not the damage itself)
- `battle_ui_status_effect_logic_description_txt_03` / `_79`, `battle_ui_message_body_logic_txt_76`/`_234`: **"Prevent all damage from—and effects of—attacks [used by the opponent's Pokémon]"** (blocks BOTH damage and effects)
- These three are separate, independently-used templates, confirming the game engine truly distinguishes "damage only" vs "effects only" vs "damage AND effects" as three different effect types — a precise, unambiguous answer to Q18.
- `battle_ui_message_body_txt_42`: "Effects done to [CardName] were prevented" — UI feedback when an effect-prevention triggers.
- Weakness default vs. exception (relevant Q16): `battle_ui_message_body_logic_txt_210` / `_status_effect_logic_description_txt_106`: **"Apply the opponent's Active Pokémon's Weakness to damage as ×2 for attacks from Pokémon that aren't Mega Evolution Pokémon ex"** — this is a specific EXCEPTION effect (implying the game's DEFAULT Weakness math is NOT simple ×2; the well-known Pocket default is flat **+20**, and this string exists specifically because some card/ability overrides that default to ×2 for certain attackers). This indirectly supports (but doesn't literally state) the commonly-cited flat +20 default — flag as DATAMINE-inferred, not DATAMINE-confirmed for the +20 figure itself.
- `battle_ui_status_effect_logic_description_txt_70/71`, `battle_ui_message_body_logic_txt_156/157`: "No Weakness" / "Take −X damage from attacks; no Weakness" — confirms Weakness-negation exists as a distinct effect (some Pokémon/effects remove Weakness entirely).

### Knock Out / points (Q12, Q20)
- `ex_pokemon_down_description`: **"When your Pokémon ex is Knocked Out, your opponent gets 2 points."**
- `megaex_pokemon_down_description`: **"When your Mega Evolution Pokémon ex is Knocked Out, your opponent gets 3 points."**
- (Regular non-ex Pokémon KO = 1 point, by clear implication/elimination; not found as its own explicit string but is the baseline all other UI text assumes, e.g. `battle_ui_point_acquire_txt` "+N points!" is generic.)
- `battle_ui_message_body_logic_txt_180`: "Get 1 more point if the opponent's Active Pokémon is Knocked Out by damage from an attack used by [CardName]" — bonus-point card effects exist on top of the base KO points.
- `battle_ui_message_body_logic_txt_158/196`: "Unable to get any points" / "Opponent was unable to get any points" — confirms a KO can happen while a coin-flip/effect denies the resulting points (matches `ABILITY_DESC_94`: "When this Pokémon is Knocked Out, flip a coin. If heads, your opponent can't get any points for it.") — direct evidence a KO and its point-award are handled as separable events (relevant to Q20).
- Pokémon Support Battle Rules FAQ (see above): discard via card effect ≠ Knocked Out, no points for discard.

### Evolution (Q28, Q29)
- `battle_tutorial_evolve_message_00800`: **"Even if a Pokémon evolves, it keeps all attached Energy and any damage."**
- `battle_tutorial_evolve_message_00900`: "You can evolve as many Pokémon as you want on your turn, except on your first turn."
- `battle_tutorial_evolve_message_01000`: **"You can't evolve a Pokémon on its first turn in play or if it already evolved during this turn."** — confirms BOTH restrictions precisely (that specific Pokémon's first turn in play AND already-evolved-this-turn), for Q28.
- `battle_ui_status_effect_logic_description_txt_77` / `battle_ui_message_body_logic_txt_164`: "Can evolve during the first turn or the turn it's played" — an explicit override/exception effect confirming the above is indeed the enforced default rule.
- Buzzwole ex official ruling (Pokémon Support, see above) confirms attack-attached effects (e.g. "can't attack next turn") are cleared when a Pokémon returns to the Bench — separate from evolution's carry-over of Energy/damage.

### Pokémon Tools (Q38)
- `battle_tutorial_pokemon_tool_message_00600`: "You can use as many Pokémon Tools during your turn as you'd like, but each Pokémon can have only one attached at a time." (default = 1)
- `battle_ui_message_body_logic_txt_225` / `_status_effect_logic_description_txt_112`: "Can have up to [N] Pokémon Tool cards attached" — confirms an exception effect can raise a Pokémon's Tool cap above 1.
- `battle_tutorial_pokemon_tool_message_00500`: "Once a Pokémon Tool has been attached to a Pokémon, it remains attached until the Pokémon leaves play."
- `battle_ui_message_body_txt_69`: "The conditions for attaching this Pokémon Tool have not been met" — generic block message.
- Tutorial example: HP-boosting Tool (+20 HP) is illustrated raising 50→70 HP, i.e., HP bonus applies immediately as a straightforward max-HP increase (not literally testing the "Tool removed → retroactive KO" edge case from Q38, which remains unconfirmed by this source).

### Stadiums (Q39)
- `battle_tutorial_stadium_message_00500`: "You can play only 1 Stadium card from your hand during your turn, and it stays in play."
- `battle_tutorial_stadium_message_00600`: "Only 1 Stadium card can be in play at a time."
- `battle_tutorial_stadium_message_00700`: **"When a Stadium with a different name is put in play, discard the Stadium that was previously in play and replace it."** — confirms you CAN replace the opponent's Stadium (no ownership restriction stated) as long as the name differs.
- `battle_tutorial_stadium_message_00800` / `battle_ui_message_body_txt_70`: **"You can't play a Stadium card with the same name as the Stadium already in play."**
- `battle_ui_message_body_txt_71`: **"You can't use any more Stadium cards this turn"** — confirms a strict one-Stadium-PLAY-per-turn limit (separate from the "only 1 in play" limit).
- `battle_tutorial_stadium_message_00400`: "When a Stadium card is in play, it has an effect on both you and your opponent." — confirms Stadium effects are symmetric by design (Q39's symmetry question), though individual card text can still target asymmetrically (e.g. Training Area in the tutorial affects "both players' Stage 1 Pokémon" symmetrically by design).

### Supporters / Items (Q37)
- `battle_tutorial_support_message_00400`: **"Unlike Item cards, you can only use one Supporter card on your turn."**
- `battle_tutorial_goods_message_00900`: "You may play as many Item cards as you like during your turn."
- `battle_ui_message_body_txt_29`: "You can't use any more Supporter cards this turn" — UI enforcement of the once-per-turn cap.
- `battle_ui_message_body_txt_30/31/40`: **"The conditions for using this Supporter card have not been met" / "...this Item card have not been met" / "...this Ability have not been met"** — direct confirmation the UI actively blocks playing/using cards or Abilities whose effect condition can't be satisfied (e.g., Potion on an undamaged Pokémon would be blocked) — answers Q37's UI-blocking question.

### Abilities (Q34, Q36)
- `battle_tutorial_ability_message_00300`: "Unlike attacks, using an Ability does not end your turn."
- `battle_tutorial_ability_message_00400`: "There are Abilities that work all the time." (passive vs. activated distinction)
- `battle_ui_message_body_logic_txt_129`: "Use the effect of [AbilityName]?" confirmation prompt for activated Abilities.
- `battle_ui_message_body_logic_txt_223` / `battle_ui_message_body_txt_21`: "[CardName] can't use attacks due to the effects of [AbilityName]" — Ability-caused attack lock (separate template from Special-Condition-caused lock).

### Timers (Q10) — partial
- `battle_ui_countdown_command_txt`: "Time limit" (per-turn timer UI label).
- `battle_ui_message_body_txt_07`: **"The battle is over because the turn limit has been reached."**
- `battle_ui_message_body_txt_08`: **"The battle is over because the time limit has been reached."**
- `battle_ui_message_body_txt_39`: **"The battle is over because your opponent's time limit has been reached."**
- These confirm THREE distinct end-of-battle-by-timer conditions exist: (1) a turn-count cap, (2) an overall battle time limit, (3) a per-player time-bank exhaustion ("opponent's time limit reached" — implies each player has an individual time allotment, and running it out ends the battle, likely as a loss for whoever ran out, analogous to chess). **None of these three strings state the resulting outcome (draw vs. win/loss) explicitly** — unresolved by this source; only the crash/disconnect case is explicitly a loss (see Pokémon Support FAQ above: reconnection window ~120s, failure = loss).
- `pve_battle_rule_description_01/02/03/04`: "Maximum of [N] turns" / "[N] points to win" / "Time limit of [N] seconds per turn" / "No time limit per turn" — these are configurable **PvE/solo-battle** rule-slot templates (`pve_battle_rule_ttl` = "Battle Rules", shown via `pve_battle_detail_special_rule_btn`). Confirms PvE/event battles can have DIFFERENT turn caps, point targets, and per-turn timers than standard Ranked/casual PvP — direct evidence for Q49 that rules vary by battle type, though the standard PvP numbers themselves aren't given by this string (they're data-driven per event/stage, not fixed text).

### Win / loss / draw (Q13, Q14, Q15)
- `battle_tutorial_bench_message_00400`: **"If you have no Pokémon left in play, you lose the battle."**
- `battle_result_top_win`/`_lose`/`_draw`: "Victory!" / "Defeat..." / "Tie" — confirms three possible match outcomes exist.
- `battle_ui_error_dialog_body_txt_04`: **"Battle ended. You were not able to connect within the allowed time. The battle will be counted as a loss."** — disconnect timeout = loss (matches Pokémon Support Gameplay FAQ's ~120s reconnection window finding).
- `battle_ui_message_body_txt_35`: "Your opponent conceded" — concede is instant, presumably a win for the other player (not explicitly stated as such here, but strongly implied).
- No datamined string was found that resolves the exact simultaneous-win-conditions/tiebreak mechanism (Q14) beyond confirming "Tie" is a real, distinct outcome from Win/Loss.

### Coin flips (Q44)
- `battle_ui_coin_flip_unitil_get_tails_txt`: **"Until tails comes up"** — confirms the "flip until tails" UI/mechanic exists exactly as described in Q44 (e.g. `TRAINER_DESC_2`: "flip a coin until you get tails. For each heads, take a [type] Energy...").
- `battle_ui_coin_flip_coin_count_txt`: "Flips: " (counter shown during multi-flip sequences).
- Card-text-driven exception: `battle_ui_status_effect_logic_description_txt_60` / `battle_ui_message_body_logic_txt_145`: "The first coin of the next coin flip for the effect of an attack, Ability, or Trainer card will definitely be heads" — this is a SPECIFIC card/ability effect (not a universal rule) that forces a guaranteed-heads first flip; the earlier-seen toast "First coin flip will definitely be heads" is this effect firing, NOT a general property of all coin flips. Confirms normal coin flips are genuinely 50/50 except when such a specific effect is active.
- `battle_ui_status_effect_logic_description_txt_110`/`_113`, `battle_ui_message_body_logic_txt_220`/`_226`: "If any coins are flipped for an attack/effect of [Pokémon/Trainer card], they may begin flipping those coins again" — a "re-flip" mechanic exists as a distinct effect type too.

### Energy Zone manual attachment vs. card-driven attachment (Q46)
- Distinct UI text for the manual once-per-turn attachment (drag/tray UI: `battle_ui_energy_select_tray_to_tray_title_txt_03` = "Attach") vs. card/ability-driven bulk attachment prompts: `battle_ui_message_body_logic_txt_97`/`_135`/`_217`/`_219`: **"Attach N Energy to your [Pokémon] in any way you like"** — worded as a distinct, separate action from the standard once-per-turn attach, supporting that these effects do NOT consume/replace the manual attachment for the turn (though not 100% explicitly stated as "in addition to").
- Official Pokémon Support ruling (Jolteon ex, above) confirms the engine tracks "Energy attached from the Energy Zone" as a specific triggerable event distinct from energy moved from discard or between Pokémon — directly relevant scaffolding for Q46.
- `battle_ui_status_effect_logic_description_txt_46` / `battle_ui_message_body_logic_txt_112`: "Can't attach any Energy from the Energy Zone to Active Pokémon" — confirms lock effects can specifically target Energy-Zone-sourced attachment (further evidence it's a distinct, trackable action type).
- `battle_ui_message_body_txt_45`: "Changed the type of the next Energy generated" — confirms cards CAN alter the "next energy" preview's type (relevant to Q6 mechanics around the preview).

### Special Conditions vs. Abilities/effects at Checkup — order (Q11) — NOT resolved by this source
No datamined string enumerates a strict Checkup processing order (Poison → Burn → Sleep-flip → Paralysis-end, or whose Pokémon first). `battle_ui_log_check_txt` = "Pokémon Checkup" is just the log label. This remains **unresolved**.

---

## Community secondary sources (cross-check / contradiction-check against datamine)

### Dexerto — tie rules (Q14) — IMPORTANT, community-sourced, not official
URL: https://www.dexerto.com/pokemon/pokemon-tcg-pocket-players-discover-unfair-rules-for-tying-games-3015305/
Grade: COMMUNITY (article explicitly credits discovery to the PTCGP subreddit, not an official source; no in-game text quoted)

- Claimed mechanism: A tie is declared when **both Active Pokémon are Knocked Out simultaneously AND both Benches are empty**.
- Claimed tiebreak: if both Actives are KO'd simultaneously but **one player still has a Benched Pokémon and the other does not**, the player with a Bench Pokémon **wins**, "regardless of who inflicted the final blow."
- Claimed edge case: "A tie also happens even if one player scores four Points... so long as both Actives are knocked out at the same time and the Benches are clear" — i.e., points reached at the moment of simultaneous double-KO doesn't override the empty-bench-vs-not tiebreak/tie rule.
- This is the most specific answer found anywhere (including the datamine) for Q14, but it is **uncorroborated by any official or in-game text** — flag as unresolved/needs verification, though independently corroborated in substance by Game8 (see below): "If only one player still has pokemon they could move to the Active Spot, they are considered the winner."

### GameWith — win/draw conditions (Q10, Q14)
URL: https://gamewith.net/pokemon-tcg-pocket/48611
Grade: COMMUNITY

- Claims draw scenarios: simultaneous 3-point reach; simultaneous double-KO via self-damaging attacks leaving no Pokémon; and **turn-limit expiry** — states **"After 30 turns have passed for both players, the battle will be forced to a draw" in Versus mode (50 turns in Solo mode)**. Gives concrete numbers for Q10's "turn cap" question, but uncorroborated by any INGAME-QUOTED/DATAMINE source found — the datamine confirms a turn-limit-ends-battle MESSAGE exists (`battle_ui_message_body_txt_07`) but not the number of turns or that the outcome is a draw specifically.

### Game8 — Battle System Explained (Q9, Q10, Q14, Q15, Q22, Q49)
URL: https://game8.co/games/Pokemon-TCG-Pocket/archives/474412
Grade: COMMUNITY (paraphrase, no in-game text quoted)

- **Turn order presented as a fixed sequence**: Draw → Attach Energy → Evolve → Play Basic to Bench → Use Abilities → Play Trainer cards (Supporter max 1) → Retreat → Attack. This conflicts with the general assumption in Q9 that the main-phase action order is free — Game8 presents it as a recommended/typical sequence rather than a strict rule, but does not clearly say whether the order is enforced or just conventional. **Not confirmed as an enforced order by any INGAME-QUOTED source; the tutorial strings found in the datamine show these actions being taught in a similar demonstrative order but never state the order is mandatory.**
- **Timer claim**: "twenty-minute timer per player; if time expires, whoever has more points wins" — if true, this resolves Q10's "what happens when the per-player time-bank runs out" question (favors the player with more points, not an automatic loss for the timed-out player) — but this **directly needs verification**; it is not corroborated by the datamine strings (which only show a "time limit reached" message with no stated winner-selection rule) nor the official Pokémon Support FAQ (which only documents the *disconnect* reconnection window, a different timer).
- **CONTRADICTS the datamine on deck-out (Q15):** Game8 states **"You lose a match when you have no cards in your deck as you draw your card at the beginning of your turn."** This directly contradicts the DATAMINE finding (`battle_ui_message_body_txt_34`: "No cards left in deck; unable to draw cards" — a benign skip message with no loss indicated) and contradicts the project's own instruction that "deck-out is not a loss." **This looks like Game8 incorrectly carrying over the physical-TCG deck-out-loss rule into Pocket — exactly the kind of error this research is meant to catch.** Flag as a contradiction; the datamine's skip-only message plus lack of any loss-on-empty-deck string is stronger evidence than this uncited paraphrase.
- Confirms (independently, weakly) the Dexerto tiebreak rule: "If only one player still has pokemon they could move to the Active Spot, they are considered the winner" — matches Dexerto's Bench-count tiebreak for Q14.
- Special condition summary given (Poison 10/turn, Burn 20/turn+coin-flip-to-heal, Sleep blocks attack/retreat+coin-flip-wake, Paralysis blocks actions/cures after one turn, Confusion tails=attack fails) is consistent with the datamine's confirmed Poison-10 figure and the project's Q22 assumptions, but stated without in-game citation (COMMUNITY grade) for the Burn/Sleep/Paralysis/Confusion specifics.
- States Solo/AI battles are untimed, unlike Ranked — consistent with the datamine's `pve_battle_rule_description_04` = "No time limit per turn" being one of the configurable PvE rule slots (Q49).

### Bulbapedia "Pokémon Checkup (TCG)" — CAUTION: likely NOT Pocket-specific (Q11)
URL: https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Checkup_(TCG)
Grade: **UNRELIABLE for this scope** — this Bulbapedia page is the generic "(TCG)" article covering the physical card game's rules terminology; a fetch summary reported it describing a Poison→Burn→Asleep→Paralyzed Checkup order "in the same order as the TCG," which is language describing the PHYSICAL game, not confirmed Pocket-specific text. Per the task's explicit warning not to assume physical-TCG rules apply to Pocket, **this finding is NOT trusted** and Q11's Checkup order remains functionally unresolved from an in-game-text perspective — no Pocket-specific INGAME-QUOTED or DATAMINE source was found stating the Checkup processing order or whose Pokémon (current player vs. opponent) is processed first. This is a genuine gap.

### Pokémon Zone — "How to play Pokémon TCG Pocket?" (extensive, multiple questions)
URL: https://www.pokemon-zone.com/articles/how-to-play-pokemon-tcg-pocket/
Grade: COMMUNITY (thorough guide, no in-game text directly quoted, but internally consistent and detailed)

- **Q6 — P1 first-turn Energy, CORROBORATES a widely-assumed rule not directly stated by the datamine**: "The starting player does not receive a larger Energy on their Energy Zone, meaning they cannot manually attach an Energy to their Pokémon until their second turn." First clear statement found (any grade) that P1 gets NO turn-1 Energy.
- **Q1 — ex naming clarification**: "Pokémon ex have different names from regular versions, so you can play 2 Pikachu + 2 Pikachu ex" (i.e., the "max 2 per name" cap treats "X" and "X ex" as different names) — plausible, but not datamine-confirmed.
- **Q1 — confirms 3-type Energy Zone cap**, matching the datamine's `deck_toast_002`.
- **Q9 — turn structure claim**: draw → Energy Zone cycles → free actions → attack → turn ends immediately after attack. Actions unlimited per turn: Bench a Basic (up to 3), Evolve, play Item cards. Actions limited to once/turn: attach Energy, retreat, play Supporter, use an Ability (**this "once per turn" cap on Ability use contradicts nothing found elsewhere but is stated as a blanket rule here — the datamine only confirms "once during your turn" phrasing appears on individual ability card text, not as a hard universal engine rule for ALL abilities**; flag as possibly overstated).
- **Q10 — per-turn timer of 90 seconds and overall match timer of 20 minutes** claimed — first concrete numbers found for Q10's specific limits (uncorroborated elsewhere; datamine only confirms the UI labels/messages exist, not the numeric values, since those may be data-driven not string-embedded).
- **Q15 — deck-out, CONTRADICTS Game8's battle-system page, CORROBORATES datamine**: **"running out of cards in deck and being unable to draw doesn't result in a loss."** This matches the datamine's benign skip message and directly contradicts the other Game8 article's claim of an automatic loss — see contradiction noted above; this is now a 2-(datamine + this source) vs 1 (other Game8 page) split, strengthening confidence that deck-out is NOT a loss in Pocket.
- **Q22/Q23 — Special Conditions, resolves the apparent tension**: States Poison "can stack with other Special Conditions," while **"Asleep, Paralyzed, and Confused cannot stack with each other."** This reconciles neatly with the datamine's UI templates for up to 3 simultaneous conditions (`battle_ui_message_body_logic_txt_84-92`): a Pokémon can be Poisoned + Burned + (at most one of Asleep/Paralyzed/Confused) = up to 3 conditions total, but never two from the {Asleep, Paralyzed, Confused} mutually-exclusive group at once. This is the clearest resolution of Q23 found, though still COMMUNITY-grade for the mutual-exclusivity claim specifically.
- **Q25 — recovery**: "Recovery occurs if Pokémon moves to Bench, evolves, or card effect heals it" — adds "evolves" as a cure trigger not explicitly seen in the datamine tutorial text (which only mentioned moving to Bench).
- **Q16 — damage granularity**: "Damage is dealt in multiples of ten, using damage counters" and "a damaging move that hits on the Defending Pokémon's Weakness deals 20 more damage" (flat +20, NOT ×2) and "Non-damaging attacks don't trigger weakness" — this is the clearest statement found anywhere that Weakness is flat +20 (not multiplicative) as the DEFAULT, consistent with the datamine's ×2-Weakness string being an explicit override/exception rather than the base rule.
- **Q14 — tie condition, phrased differently from Dexerto/Game8 (possible contradiction or garbled summary)**: "If both players have a Pokémon on their bench that they can promote, the game ends in a tie" — this reads as the OPPOSITE of Dexerto's claim (Dexerto: tie only when BOTH benches are empty; if one has a bench Pokémon and the other doesn't, the one with a Pokémon wins). Given this came through an automated single-pass fetch summarizer, it may be a garbled/mis-paraphrased rendering of the same underlying rule rather than a true contradiction — **flagging as UNRESOLVED / needs a direct re-read of the source page** rather than treating as a confirmed contradiction.

### Game8 — "All Pokemon TCG Pocket Rule Differences" (vs. physical TCG)
URL: https://game8.co/games/Pokemon-TCG-Pocket/archives/474638
Grade: COMMUNITY

- Corroborates: 20-card decks, 5-card opening hand, 10-card hand max, max 2 copies per card, 3-Pokémon Bench (vs. 5 in physical), 3 points to win (vs. 6 Prize cards), flat +20 Weakness (not ×2), no Resistances in Pocket, no deck-out loss.
- **Direct claim for Q5**: "Pocket: Player going first does NOT draw a card" (physical TCG: first player must draw) — i.e., confirms P1 skips the turn-1 draw, not just the turn-1 Energy. This is a distinct, specific claim worth flagging since it wasn't independently seen in the datamine strings (which only show a generic "Start your turn by drawing a card" tutorial line, not a P1-specific exception).
- **Direct claim for Q5**: "Pocket allows Supporter card use on first turn; physical TCG forbids it" — confirms Supporters are usable turn 1 by both players in Pocket, unlike the physical game.
- **Direct claim for Q5**: "Energy attachment restricted on first turn in Pocket" — vague wording, likely refers to P1 not receiving a first-turn Energy (per Pokémon Zone above) rather than a blanket restriction on both players.

### Community ruling claim — Mew ex "Genome Hacking" copy-attack (Q45)
URL: https://www.threads.com/@jaysen_trinity/post/DDfBEw1y-VJ/ (social media post, unverifiable authorship/authority)
Grade: COMMUNITY (low confidence — an uncited social post, not a forum-verified compendium entry; the "Pokémon Rulings Compendium" link found in search results is for the PHYSICAL TCG's much older Dragons Exalted Mew EX card and must NOT be conflated with Pocket's Mew ex)

- Claimed ruling: "You do not have to meet the energy requirements for the attack. However, if the attack says you must do something or the attack does nothing, that part still has to be done." — i.e., copy-attack effects (Genome Hacking-style) bypass the copied attack's Energy cost entirely, but any conditional/mandatory sub-effects of the copied attack still apply normally. Plausible and consistent with how Ditto/Mew-style "copy attack" cards are known to work in the physical game too, but **not found in any INGAME-QUOTED or DATAMINE source** — remains unresolved at higher confidence.

### Bulbapedia — main "Pokémon Trading Card Game Pocket" article (Q2, Q5, Q6, Q10, Q12, Q15, Q16, Q22)
URL: https://bulbapedia.bulbagarden.net/wiki/Pok%C3%A9mon_Trading_Card_Game_Pocket
Grade: COMMUNITY (wiki, but well-established/collaboratively maintained; several claims triple-corroborate the datamine and other sources)

- **Q2 — resolves the mulligan question directly**: **"Each players' starting hand will always contain at least one Basic Pokémon, meaning mulligans will never be taken."** Clear, explicit answer: no mulligan mechanic exists because the deal itself guarantees a Basic (mechanism of the guarantee, e.g. forced first card vs. reshuffle-and-redeal, still not spelled out).
- **Q6 — adds nuance**: "First player cannot manually attach Energy but may use Supporter cards that attach Energy" — confirms P1's turn-1 manual-attach block is specific to the manual action; Supporter-sourced energy attachment is NOT blocked for P1 turn 1.
- **Q5 — attack restriction framed generally, not as a flat "0-cost only" rule**: "The player who goes first may use an attack, only if they are able to attach enough Energy" — i.e., the real constraint is simply "has enough Energy," which in practice usually means a 0-Energy-cost attack (since P1 has no manual attachment) but is not a hardcoded 0-cost-only restriction; a Supporter-granted Energy could enable a paid attack turn 1.
- **Q10 — turn caps, triple-corroborates GameWith**: "Versus battles: maximum 30 turns. Solo battles: maximum 50 turns."
- **Q12 — confirms point values**: 1 point regular KO / 2 points ex KO / 3 points Mega Evolution ex KO — matches datamine exactly.
- **Q15 — explicit, direct contradiction-flag against the Game8 battle-system article**: **"Players unable to draw a card at the start of their turn do not lose the battle, as they would in the physical game."** This explicitly calls out the physical-TCG rule (deck-out = loss) and states Pocket does NOT follow it — the clearest and most explicit statement found for Q15, and it directly matches this task's own instruction not to assume physical rules carry over. Combined with the datamine's benign skip-message and Pokémon Zone's explicit denial, **Game8's "All Pokemon TCG Pocket Rule Differences"-adjacent claim of a deck-out loss (from the separate "Battle System Explained" article) is very likely simply WRONG** — flagged as a confirmed contradiction, 3 sources against 1.
- **Q16 — triple-corroborates flat +20 Weakness**: "Pokémon cards have no Resistance and have a Weakness modifier of +20 instead of ×2."
- **Q22 — resolves the Confusion self-damage question**: **"Confused Pokémon do not take damage when flipping tails for the Special Condition."** Explicitly contrasts with the physical TCG (where a tails flip on Confused causes 30 self-damage) — Pocket's Confused Pokémon simply fails the attack with no self-harm.

---

## Summary of contradictions found (flagged for the simulator check)
1. **Deck-out / empty deck on required draw (Q15):** DATAMINE (benign "unable to draw cards" skip message) + Pokémon Zone ("doesn't result in a loss") + Bulbapedia ("do not lose the battle, as they would in the physical game") **all agree: NOT a loss** — versus Game8's "Battle System Explained" article, which claims it IS an automatic loss (apparently incorrectly importing the physical-TCG rule). Treat the loss claim as wrong.
2. **Tie/draw trigger mechanics (Q14):** Dexerto and Game8 agree on a "whoever still has a promotable Bench Pokémon wins; tie only if both benches are empty at simultaneous double-KO" rule, but Pokémon Zone's page (via an automated summary) rendered the opposite framing ("if both players have a promotable bench Pokémon, it's a tie"). This is very likely a summarization artifact rather than a true third position, but it was not independently re-verified by direct reading — flagged as needing a direct check of the Pokémon Zone source text. No in-game or official text confirms either version; Q14 remains formally **unresolved at INGAME-QUOTED/DATAMINE grade.**
3. **Weakness math (Q16):** the datamine contains a specific card/ability string applying Weakness as "×2 ... for attacks from Pokémon that aren't Mega Evolution Pokémon ex," which could be misread as the default — but three independent COMMUNITY sources (Pokémon Zone, Game8, Bulbapedia) all state the DEFAULT is flat +20, and the ×2 string is clearly an exception effect's description, not the base rule. No true contradiction, but worth flagging so the simulator doesn't misread that one string as universal.

## Unresolved after this research pass (no INGAME-QUOTED/DATAMINE/reliable COMMUNITY source found)
- Q11: Exact Pokémon Checkup processing order (Poison/Burn/Sleep-flip/Paralysis-end) and whose Pokémon (current player vs. opponent) is processed first — the one Bulbapedia sub-page found for "Pokémon Checkup" reads as physical-TCG-general content, not confirmed Pocket-specific, and was explicitly NOT trusted per this task's scope rules.
- Q14: The precise simultaneous-win/tie resolution algorithm at DATAMINE/official grade (only community-sourced, and even those show a possible internal inconsistency — see contradiction #2 above).
- Q17, Q19, Q21, Q26, Q27, Q30 (Rare Candy/Mega ex specifics), Q32, Q33 (partial — Buzzwole ruling covers attack-effects only), Q35, Q40 (Fossil specifics), Q41 (reveal-to-opponent details), Q42 (individual Supporter targeting details beyond what's in the Battle Rules FAQ), Q43 (exact public/hidden info list), Q45 (Genome Hacking ruling only found as an uncited social post), Q47, Q48 (partial — only inferred from generic "no valid target" messages), Q49 (partial — PvE rule-slot strings confirm variability exists but not the standard PvP numeric values), Q50 (no errata/changelog list found in this pass) — none of these had a dedicated, clearly-worded in-game or datamine string found; would need further targeted searches (web search budget was exhausted this session before these could be pursued).

## Pending / not yet investigated (budget exhausted)
- Bulbapedia Pokémon TCG Pocket rules subpages (community wiki, cross-check/contradiction-check against datamine).
- Serebii TCG Pocket section.
- Game8 beginner guides quoting in-game help.
- pokemon-zone.com how-to-play.
- ptcgpocket.gg
</content>

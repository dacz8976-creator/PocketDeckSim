# 08 — In-game tests and recordings that would settle what's still open

Written 2026-09-22. Each test says what it settles, how to set it up, and what to look for. Tests you can run alone in
a **Solo** battle (you control your side; the AI deck is fixed) are marked *Solo*. Tests that need the opponent to do
something specific need a **friend battle** with someone willing to follow a script, or a lucky ladder moment (*Friend*).
Tests that need only a screenshot of a menu or the damage preview are marked *One look*. Record the screen for
anything that resolves quickly (Checkup, promotions). The move itself is usually 1–2 seconds.

The attack preview ("Expected damage") shows damage without attacking, so damage questions don't need a real attack.

---

## 1. Tests, highest value first

| # | Settles | Type | Setup | Look for |
|---|---|---|---|---|
| **T1 ✅ DONE 2026-09-22** | Opening-hand rule on today's app (engine bug H1; the only study is from v1.2.5) | Solo, ~40–60 starts | A legal deck with **exactly 2 Basics** (e.g. 2 Riolu + 18 Trainers/evolutions). Start a Solo battle, screenshot the opening hand, concede. Repeat | Count hands holding **both** Basics. Real rule (swap-in): ~5%. Engine (Basic-first): ~21%. With 50 hands, 0–5 hits = swap-in rule, 8+ = Basic-first |
| **T2 ✅ VIDEO OBSERVED; RULES4 CASE IMPLEMENTED** | Observed one-seat setup: player at 2 points receives 3rd point while last Pokémon is Knocked Out in same attack; opponent still has Pokémon and fewer than 3 (`05` #2) | Friend | One video seat; see T2 evidence | Result overlay: Tie. Opponent final 2 points inferred from ex KO, not shown on overlay. Both-seat engine fixtures are regression coverage, not video evidence. Broader simultaneous finishes remain open |
| **T3 - OPTIONAL lethal-boundary confirmation** | Checkup healing can rescue a status-damaged Pokémon at 0 HP (`05` #4; order is already settled by 010316) | Friend (or Solo vs a poison AI deck) | Your Poisoned Active on exactly 10 HP, Garganacl in play | Survival at 10 HP is expected under the official end-of-Checkup KO rule and rules1/rules2 deferred KO handling. This confirms the app's lethal-boundary behavior; it does not test Poison-versus-heal order. |
| **T4** | Who promotes first when both Actives are Knocked Out in the same Checkup (`05` #21) | Friend / lucky ladder | Both Actives Poisoned or Burned and on lethal HP at the same Checkup | Which player is asked to promote first. One source says the player whose turn is **next** |
| **T5** | Hand full when an effect returns cards (`05` #9) | Solo | Hold 10 cards including Ilima. Play Ilima (9 left) on a **damaged, evolved** Colorless Stage 1 (2 cards come back = 11) | Where the 11th card goes: stays in play, discard, or deck. Also whether Ilima can be played at all in that spot |
| **T6 ✅ ANSWERED 2026-09-22** | Who picks discarded Energy (engine M7) | One look | (a) Retreat a Pokémon with two **different** Energy types attached and Retreat Cost 1. (b) Gouging Fire's Scorching Interruption or Walking Wake's Sweeping Billow with mixed Energy | Does a "choose Energy to discard" picker appear? Yes → the engine should let the player choose |
| **T7** | Weakness when an attacker-side debuff takes the attack to 0 (`05` #11) | One look (preview) | Your attacker under "attacks do −20 damage", 20-damage attack, defender weak to it | Preview shows 0 or 20 |
| **T8** | Heavy Helmet with a changed Retreat Cost (`05` #19) | One look (preview) | Heavy Helmet on a Retreat-3 Psychic Pokémon with Peculiar Plaza in play (Retreat becomes 1); get attacked, or check the opponent's preview | Is the −20 still applied? |
| **T9 ✅ ANSWERED** | Heal targets (engine low item) | One look | Two eligible Pokémon, only one damaged. Play Potion, Erika or Lillie | Can the undamaged one be selected, or is it greyed out? |
| **T10 ✅ DONE 2026-09-22** | A second, different Stadium in the same turn (engine M6) | One look | Two different Stadiums in hand | Expect "You can't use any more Stadium cards this turn" |
| **T11** | Glimmora/Dusknoir coin on a Poison KO (engine M3) | Whenever it happens | Your Glimmora Knocked Out by Poison/Burn | A coin flip appears (card text says it should) |
| **T12** | Turn limit timing (`05` #22) | Only if a game gets there | A stall game reaching turn 30 | Does the final Checkup still happen, and can a KO in it still win? |

**Results so far:** T1 — both Basics in 3 of 50 hands (6%): the swap-in rule holds on the current app; the `unified1`
engine's Basic-first dealing is wrong. T10 — "You can't use any more Stadium cards this turn" shown when Arcade was
played after Mesagoza; the one-play limit is also printed on every Stadium. Evidence:
`_research_notes/audit_2026-09-22/T1_T10_results.md`.
T6 — the player chooses which Energy to discard, both for retreat and for attacks that say "discard X Energy" (Dustin;
confirmed in his video `EnergyRetreatAttackChoice`). T3 — Poison resolves before Blessed Salt: Passimian ex with two
Garganacl went from 130→120→130 on T16 and 120→110→130 on T18 (recording 010316). Only the lethal case is unrecorded. T9 — healing cards can't target a full-HP Pokémon; only Pokémon Center Lady can, and only
if it has a Special Condition (Dustin).
T2 — the single observed video seat shows a tie in the narrow setup described in `05` #2. The opponent's final 2 points are inferred from the ex KO, not shown on the overlay. Rules4 returns a tie for this narrow case; engine regression fixtures cover both seats. The broader community model remains unverified.

Already settled, no test needed: Rough Skin vs Prickly Powder (official JP FAQ), Clemont's Backpack on the Bench
(two recordings), one Stadium per turn (in-game text; T10 only confirms the message).

## 2. Ordinary ladder recordings: what makes them useful

Astra's review campaign (Gemini + Sol) is working through the 5 new recordings from Sept 21–22. Most reviewed games
confirm rules we already have. What would make a normal recording count for more:

- **Damage numbers on screen.** Every "X damage" banner is a free check of the damage order (weakness, Tools,
  Stadiums, reductions). Games with walls (Metal Core Barrier, Heavy Helmet, Shuckle ex), Bounded Field, or bench
  damage are the most useful.
- **Status-heavy matchups** (Altaria sleep, Weezing poison/burn/confusion, Blaziken burn), especially the Checkup
  moments.
- **Endings.** Keep recording through the result screen. Double KOs, Rocky Helmet endings and Checkup endings are
  what `05` #21 needs.
- **Opening hands.** A quick look at your opening hand in every recording, over many games, adds to T1 for free.

## 3. An idea with more payoff than more videos: replay reviewed games through the engine

Each accepted review already has a turn-by-turn ledger (setup, cards played, Energy, damage, KOs, score). Turning a
ledger into a script the engine replays (same boards, same choices, coin results forced to what happened) and
checking each displayed damage number and each legal/illegal move against the engine would turn 40+ reviewed games
into hundreds of automatic rule checks. It would also catch mismatches nobody thought to look for. This is a build
job for Astra and only worth it if Dustin wants it. It's listed here because it's the cheapest way to get *systematic*
evidence out of recordings that already exist.

# 06 — Sources, grades, and how the "read the app's code" question came out

Checked 2026-09-20/21. Raw research notes (per source, with longer quotes) are in `_research_notes/`.

## Official (grade [OFFICIAL])

| Source | What it settled |
|---|---|
| **In-app Tips › About Battle Rules** — 10 screenshots Dustin sent 2026-09-21 (transcript: `_research_notes/in_app_tips_about_battle_rules.md`). Covers Energy attachment through Communication errors; the opening part (setup, first turn, Energy Zone) is not yet captured. | Every Special Condition (incl. Paralysis timing, Confusion, stacking, cures, Active-only); Checkup order and "not part of either player's turn"; turn limit → tie; battle clock out = loss; turn and input timers; disconnects (both disconnected = both lose); evolution and retreat end attack effects and Special Conditions; retreat cost/choice rules; Weakness never on the Bench; one Supporter per turn; points per Knock Out and Rule Box; win = set points "before the other player"; no Pokémon left = loss regardless of points; concede = loss; deck-out not a loss; Checkup definition, player order, Knock Outs at the end of Checkup. pokemon-zone's guide copies this text word for word in places. |
| **Detailed Battle FAQ** — the in-app Tips FAQ, hosted at https://app-ptcgpt.pokemon-support.com/hc/en-us/sections/53604902813209 (Japanese has one extra article: /hc/ja/sections/53604902813209). Linked from https://app-ptcgp.pokemon-support.com/hc/en-us/articles/61745874022553 ("I want to know more about the battle rules" → Menu › Tips › About Battle Rules / Detailed Battle FAQ). | Damage order (57286049312665); end-of-turn order (57285887108377); effects removed on going to the Bench (53604957483289, 57281623683481); non-attack damage vs Disguise (55980981811097); Disguise vs Swift/Ability lock (57285274843545); Jolteon ex (57284110688921); Prank Spinner (57283495239193); points for discards (57282177269273); Scizor (57281428279193); Wallace (59513864093209); Thieving Machine (61529839106073); Budew Itchy Pollen (ja 57286218211225). |
| Pokémon Support **Battle Rules FAQ** https://support.pokemon.com/hc/en-us/articles/38906248102292 (updated 2026-05-12) | Zero-cost attacks usable on the first player's first turn; same card rulings as above. |
| Pokémon Support **Gameplay FAQ** https://support.pokemon.com/hc/en-us/articles/30330309361172 | Disconnect → ~120 s to rejoin, else loss; ties don't change rank points, reset win streak; rules live in-app. |
| Printed card text (local `deckgym-database.json`, 3,879 cards, A1–B4a, file date 2026-09-06) | Rare Candy / Quick-Grow limits, Fossil text, Stadium/Tool texts, all card wording quoted. |

## In-game text (grade [IN-GAME TEXT])

- **TCGP-Corpus-Lite** https://github.com/superpikapool13/TCGP-Corpus-Lite — the game's own localization strings (UI, tutorial, battle messages, battle log labels) for v1.7.1, extracted by SombrAbsol. Licence CC BY-NC-SA 4.0; the maintainer asks that it not be used to train AI models (so don't feed it to the RL bot). I used it only to read the rules text and quote short strings; I did not copy the string tables into the project. To look something up: `locales/en_US/UI.json`, keys starting `battle_`, `deck_`, `rank_match_`.
- Strings that answered questions directly (English): hand limit ("You can have up to 10 cards in your hand"; "Hand full; unable to draw cards"; "No cards left in deck; unable to draw cards"); deck rules and "You may only select up to three Energy types"; evolution ("You can't evolve a Pokémon on its first turn in play or if it already evolved during this turn"; "…except on your first turn"; "keeps all attached Energy and any damage"); retreat (once per turn; can still attack after; five block messages); "[X] can't attack or retreat because it's [condition]"; Supporter once per turn; Items unlimited; Tools one per Pokémon and stay until the Pokémon leaves play; Stadium rules (one play per turn, one in play, same name blocked, different name replaces and discards, affects both players); ex = 2 and Mega ex = 3 points; "If you have no Pokémon left in play, you lose"; turn-limit / time-limit / opponent's-time-limit end messages; prevention wording in three kinds; Checkup coin labels ("Pokémon Checkup — Asleep/Burned", "Coin flip — Confused").

## Observed in Dustin's recordings (grade [OBSERVED])

Text reviews of 28 recordings written 2026-09-07/09 (Codex video workers), read in full by two Sonnet agents; notes in
`_research_notes/R1_battle_observations.md` and `R2_battle_observations.md`. Files (under `Boss Folder/`):
`video-review-coordinator-2026-09-09/battle-20260907-*/REVIEW.md`, `…/previously-finished-audit/*/REVIEW.md`,
`…/trial-manectric`, `…/trial-revavroom`, `…/log-scroll`, `competitive-deck-study-2026-09-08/…/recordings/*`,
`…/native-*`, `…/video-intake/*`, `video-mechanics-flygon-sableye-2026-09-07`, `split-battle-review-2026-09-07`,
`owner-auto-battle-031901-2026-09-06`, `luckycad-video-2026-09-06`. Caveats: machine-written from video; about half the
games were against the in-game AI; files that describe simulator runs rather than real games were excluded.

### OCR scan of the unreviewed videos

The 10 unreviewed recordings in `OneDrive\Desktop\Battle Logs` (plus one reviewed) were scanned on the laptop with ffmpeg keyframes + tesseract; only the game's own on-screen messages were used ("You are going first", "…is now Poisoned and Burned", "Coin flip — Confused", "The attack did nothing", "…recovered from being Confused", "…didn't become…", both players' clocks, "Current turn: 16", "No cards left in deck"). Hits: `_research_notes/ocr_video_scan_hits.md`.

## Community (grade [COMMUNITY] / [SINGLE])

| Source | Used for |
|---|---|
| pokemon-zone "How to play" https://www.pokemon-zone.com/articles/how-to-play-pokemon-tcg-pocket/ (updated 2025-05-04) | Checkup order and player order, KO at end of Checkup, conditions text, tie counting, Energy Zone mechanics, timers |
| pokemon-zone rulings: …/mythical-island-rulings-interactions/, …/space-time-smackdown-rulings-interactions/, …/triumphant-light-rulings-interactions/ | Card interaction rulings (below) |
| Bulbapedia: main Pocket article (Differences, Version history), Battle (TCG Pocket), Pokémon ex (TCG Pocket), Fossil Item card, Stadium card, Pokémon Tool card, set pages | No mulligan, turn caps, timers, Confusion no self-damage, Fossil setup rule, history dates |
| Dexerto 2024-12-24 https://www.dexerto.com/pokemon/pokemon-tcg-pocket-players-discover-unfair-rules-for-tying-games-3015305/ | Tie/win-condition counting (from a Reddit report) |
| Game8 EN (474572 timers, 483132 conditions, 522247 bench Weakness, 575671 Stadiums, 501550 Mega, 476278 Sabrina) | Timers, conditions, bench Weakness. **Two Game8 EN claims are wrong**: "first player doesn't draw" (474638) and "deck-out is a loss" (474412). |
| Game8 JP (650664 timers/turn cap, 650710 hand limit, 651087 deck-out, 650844 conditions, 710998 Mega, 758158 Stadium) | Cross-checks; JP timer rule differs (see file 05 #8) |
| GameWith JP 462758 (setup/turn flow), 466440 (Weakness: "10+20−20", five no-Weakness cases) | Setup order, Weakness exceptions |
| did2memo.net 2024-12-23 (Giovanni +10 scope) | Attacker boosts: Active only, attacks only, not on 0 damage |
| Sportskeeda status guide; hp-no-game-no-life, Altema (JP) | Conditions, coexistence |
| hakase-seikatsu blog (JP), Threads @bobabr0 | Mew ex Genome Hacking details |
| gameland.gg | Fossils not Pokémon in deck; Poké Ball can't find them |

pokemon-zone card rulings worth encoding (community-grade): Rough Skin doesn't trigger on Rough Skin/Gas Leak damage;
Marshadow Revenge needs a KO by attack damage; Cramorant Dive blocks only attack damage/effects; Mew ex ignores copied
Energy types but needs the copied attack's other conditions; Gyarados ex Rampaging Whirlpool also hits the KO'd Defending
Pokémon's Energy; Serperior Jungle Totem doubles Grass Energy for attacks and retreat; Primeval Law = opponent's Active
only; Exeggcute Growth Spurt attaches even without that type selected; Pokémon Flute blocked by a full opposing Bench;
Pluck removes Tools before damage; Giant Cape removal takes the HP away at once; Manaphy "does as much as you can";
Fighting Coach stacks and boosts Lucario itself; Regice "damage is not an effect"; Pokémon Communication fetches a
different card than the one returned; Swirling Disaster applies Weakness to the Active only; Group Beatdown counts
itself; Glaceon ex Snowy Terrain twice per round; Toxicroak's 20-Poison replaces an existing Poison; Donphan Rolling Spin
resets on leaving the Active Spot; Manectric Flash stops the Bench damage too; Snorlax Collapse Sleep can be cured by
Lum Berry at end of turn.

## Simulators (not evidence of the real game)

- `bcollazo/deckgym-core` (upstream, cloned at commit f01e695, 2026-09-17; 88.8% of cards; B4a present) and the
  project fork `deckgym-fork-s193` (unified1 source, commit 237b0f8). Useful as a model, never as proof — no rule in
  the repo cites real-game evidence. Where it disagrees with an official/observed rule, that's listed in `README.md`.

## Reading the actual app's code — what I found

- **No public code dump exists** for Pokémon TCG Pocket: no IL2CPP `dump.cs`, no protobuf/gRPC definitions (unlike
  Pokémon GO). One group (RaenonX-PokemonTCGP) has a public APK-dumper tool but keeps its extracted data private.
  Public card-data repos (flibustier, PocketDecks, etc.) have card text/stats only — no effect timing or rule code.
- The public **text extraction** (TCGP-Corpus-Lite, above) is the closest thing to "the app's own words" and was used.
- **Battles are very likely server-run** in versus mode (you can rejoin a battle within ~120 s after a disconnect), so
  the rule-ordering code may not be in the phone app at all. A decompile of the app would probably show UI and
  message code, not the damage/Checkup logic.
- I did **not** download the APK or decompile anything: it needs the app file from an unofficial mirror, breaks the
  game's terms of use, and likely wouldn't contain the battle logic. The one hands-on route with real yield would be
  capturing a battle's network traffic (needs a rooted phone and certificate-pinning bypass) — not attempted, and only
  worth considering with your sign-off.
- The cheapest remaining "source code" is the app's own rules screens: **Menu › Tips › About Battle Rules**.
  Screenshots of those pages would be the most authoritative thing left to add.

## Added 2026-09-22 (second session)

| Source | Grade | Used for |
|---|---|---|
| machapin, Qiita "初期手札の「たねポケが1枚以上含まれる」ロジックを「統計的仮説検定」で徹底検証" https://qiita.com/machapin/items/a4d3b09d1b369c123e85 (posted 2025-06-02, updated 2025-11-22; app v1.2.5; 2,000 automated games) | [COMMUNITY-TESTED] | Opening hand = deal 5, swap one for a Basic if none (`01` §2, `05` #6, `07` H1). Fetched and read by Claude |
| Davoi, Qiita "初手たねポケ1枚確定ってどういうロジック？" https://qiita.com/Davoi/items/8e6393f6833c9492da4e (120 games) | [COMMUNITY-TESTED] | Same question; rules out "Basic first" |
| Detailed Battle FAQ, JA article 57281556361113 | [OFFICIAL] | Near-duplicate of the Cursed Prose ruling ("effects on a Pokémon disappear once it returns to the Bench"); nothing new |
| Full re-sweep of the Detailed Battle FAQ (EN, JA, zh-tw, ko, fr, de, it, es) | [OFFICIAL] | No new rulings; European sites have only 7 of 12–13 articles |
| Gameplay FAQ https://support.pokemon.com/hc/en-us/articles/30330309361172 (updated 2026-07-30) | [OFFICIAL] | Disconnect ~120 s then loss; tie leaves rank points unchanged, resets win streak (already in `01` §8) |
| App version history: perfectly-nintendo.com changelog; pokemonblog.com 2026-09-03 | [COMMUNITY] | 1.7.1 (Aug 5–6) and 1.7.2 (Sep 3–4) = unspecified bug fixes |
| pokemon-zone.com schedule; ptcgpocket.gg/b4b | [COMMUNITY] | B4b Sep 29–30, C1 Oct 28, 2026 |
| torecataru.com ?p=447; poke-memo.com/pokepoke-hikiwake; Game8 JP 650664 | [COMMUNITY] | Simultaneous-finish readings (`05` #2) |
| gamepedia.jp/pokemon-tcgp/archives/4981 | [SINGLE] | Checkup double-KO promotion order (`05` #21) |
| X @TrustYourPilot1 (Oct 2024) quoting the in-app rules; Yahoo!知恵袋 q14308499649 | [COMMUNITY]/[SINGLE] | 30-turn limit; Solo 50 disputed |
| Game8 JP 650710 (hand limit) | [COMMUNITY] | Research at 10 cards draws what fits |
| Coin-flip tally (JP community, several hundred flips, ~48.4% heads) | [COMMUNITY-TESTED] | Coins look fair |
| Engine source, unified1 working tree, built and probed in the cloud | — (not evidence of the real game) | `07` engine audit; probe tests in `_research_notes/audit_2026-09-22/probes/` |
| Astra's review campaign (`Boss Folder/wsl-review-campaign-2026-09-22/`): 022627 and 000905 accepted | [OBSERVED] | Nothing new; deck-out without loss seen again |

Raw agent reports for this session, with every quote and URL: `_research_notes/audit_2026-09-22/web_official.md` and
`web_grey.md`.

### "Reading the app's code", re-checked 2026-09-22

Nothing new is public. TCGP-Corpus-Lite is still only the text strings (no effect parameters, no rules or FAQ text).
No full corpus, IL2CPP dump, protocol dump or effect-definition dump has been published. RaenonX-PokemonTCGP still keeps
its extracted data private. The answer from 2026-09-21 stands: not decompiled (terms of use; APK from an unofficial
mirror; the battle logic very likely runs on the server). The practical substitutes are the official FAQ (fully
captured), the in-app Tips (captured) and in-game tests (`08`).

### Dustin's in-game tests, 2026-09-22 [OBSERVED]

- **T1**: 50 opening-hand screenshots + deck QR in `OneDrive\Desktop\Battle Logs\StartingBasicReview\`: swap-in opening-hand rule confirmed on the current app.
- **T10**: `OneDrive\Desktop\Battle Logs\T10-stadiums.MP4`: "You can't use any more Stadium cards this turn", plus the printed Stadium rules box.
- **T2 video [OBSERVED]**: Dustin reported, "After 20 tries, it is a tie"; this is his reported count, not 20 independently reviewed video observations. One recorded seat shows Dustin at 2 points, with one Pokémon left, receiving the 3rd point while that Pokémon is Knocked Out in the same attack; the result overlay is Tie and the opponent still has Pokémon. The opponent's final 2 points are inferred from the ex Knock Out, not read from the overlay. Both-seat engine regression fixtures are separate from the single-seat video observation. See [`T2-evidence.md`](../Boss%20Folder/rules4-t2-repair-2026-09-22/T2-evidence.md).

Counts, statistics and frame times: `_research_notes/audit_2026-09-22/T1_T10_results.md`.

### Added later on 2026-09-22

- **JP Pokémon Support, Gameplay section, article 41083304332057** (Grapploct's Knock Back and Battle Trials), found by
  Astra: a Pokémon moved to the Bench by the attack is Knocked Out on the Bench [OFFICIAL]. This is a different section
  from the Detailed Battle FAQ we swept (`app-ptcgp.pokemon-support.com/hc/ja/…`, breadcrumb ゲームプレイについて). The
  Japanese Gameplay section hasn't been swept for other battle rulings yet.
- Dustin's statements, 2026-09-22: the player chooses discarded Energy (retreat; "discard X Energy" without "random");
  heal cards can't target a full-HP Pokémon, except Pokémon Center Lady on one with a Special Condition. His T6 video
  (`EnergyRetreatAttackChoice`) was later reviewed and confirms the Energy choice.
- **All remaining recordings reviewed, 2026-09-22** [OBSERVED]: 20 accepted reviews (`Battle Logs/Recording_QA/*/final_packet/`
  and `Boss Folder/wsl-review-campaign-2026-09-22/battle-*/`, with their verification files) read in full by a Sonnet
  agent against this folder; key passages re-checked by Claude. No contradictions of these docs. New: 010316 settles
  Poison-before-Blessed-Salt (`05` #4); `EnergyRetreatAttackChoice` confirms the Energy choice (`05` #23); 224540 and
  235356 show Bonsly's Teary Attack debuff cleared by evolving the Defending Pokémon (`10` R1). Only the Luckycad Xatu
  video (someone else's, partial review) is still pending.

### Support-site sweep, 2026-09-22 (Haiku agent, checked by Claude)

Every article on both Pocket help centers was listed through their public Help Center API, in Japanese and English.
- `app-ptcgp.pokemon-support.com` (147 JA / 143 EN articles): the only battle ruling is the Grapploct Knock Back
  article (41083304332057, already in `02` §5). Also rules-adjacent: disconnect window "around 60 seconds"
  (44994624550809, 2026-01-29; conflicts with the ~120 s in the newer support.pokemon.com FAQ); a tie leaves Ranked
  points unchanged and resets the win streak (44976870283417); results apply even if the result screen wasn't seen
  (44978680957465). The "Battle Rules" section (47926110503193) holds one article that points to the in-app Tips and
  Detailed Battle FAQ.
- `app-ptcgpt.pokemon-support.com`: only the Detailed Battle FAQ (14 articles, all already captured) plus Zendesk
  template pages.
- So the official written rulings are now fully collected. Full list: `_research_notes/audit_2026-09-22/support_gameplay_sweep.md`.


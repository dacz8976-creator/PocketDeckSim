# web_official research report — Pokémon TCG Pocket
Research date: 2026-09-22. Budget used: ~35 WebSearch calls + ~25 WebFetch calls.

## Headline: what's actually NEW vs. the baseline we already had
1. **One new Detailed Battle FAQ article found (Japanese-only), not in the known list**: article ID `57281556361113`, a near-duplicate of the known Mismagius/bench article `57281623683481`. Full text captured below (Task 1).
2. **Two app updates since 1.7.0 exist, but both are undocumented "bug fixes" with zero public detail**: v1.7.1 (Aug 5–6, 2026) and v1.7.2 (Sept 3–4, 2026). No patch notes beyond the word "Bug fixes" have been published anywhere I could find (Task 2).
3. **No new set has been released after B4a.** B4a ("Team Rocket's Ambition") is still the newest live set. **B4b releases Sept 29/30, 2026** (7 days from today) and **C1 (first set of a new "C" series) releases Oct 28, 2026.** Neither has official mechanic details published yet since they haven't shipped (Task 3).
4. **No public "full" TCGP-Corpus, IL2CPP dump, or protocol dump found.** Only the already-known TCGP-Corpus-Lite exists publicly, and it is translation-strings-only (no effect defs/params, no rules/FAQ text) (Task 4).
5. **New verbatim official text on disconnects and ties**, from the Gameplay FAQ (updated 2026-07-30), not in the previously captured set — see Task 5.

---

## Task 1 — Detailed Battle FAQ: full article enumeration + language check

**Correct domain**: the section actually lives at `https://app-ptcgpt.pokemon-support.com/hc/en-us/sections/53604902813209-Detailed-battle-FAQ` (note: domain is `app-ptcgpt` with an extra "t" — this is a *separate* Zendesk instance from the general account-support site `app-ptcgp.pokemon-support.com`, which only has billing/account sections and a one-article "Battle Rules" section containing the in-app Tips text, unrelated to this FAQ). The Detailed Battle FAQ sits under a "Tips" category on the `ptcgpt` site.

### English (en-us) — 12 articles (all already in the known list; no new English articles)
1. 61529839106073 — Team Rocket's Thieving Machine
2. 59513864093209 — Wallace's effect
3. 57286049312665 — Damage calculation (Weakness/effects)
4. 57285887108377 — End-of-turn effect order
5. 57285274843545 — Mimikyu ex Disguise (attack damage)
6. 57284110688921 — Jolteon ex Electromagnetic Wall
7. 57283495239193 — Prank Spinner
8. 57282177269273 — Points for discards
9. 57281623683481 — Mismagius Cursed Prose / bench
10. 57281428279193 — Scizor Gale Thrust
11. 55980981811097 — Mimikyu ex Disguise (duplicate/second instance)
12. 53604957483289 — Buzzwole ex Big Beat

No "updated" dates are exposed on any of these article pages (checked several; the summarization tool found no visible update-date metadata on individual FAQ articles).

### Japanese (ja) — 14 entries: 12 known + Budew (known) + **1 genuinely new**
Same 12 as English, **plus**:
- `57286218211225` — Budew "Itchy Pollen" (already flagged in our baseline as JA-only — confirmed still JA/Asian-locale-only, see below)
- **NEW: `57281556361113`** — "ムウマージのワザ「のろいのことだま」を受けたポケモンが、ベンチでダメージを受けなかった" (title identical to the known article 57281623683481, but a **different article ID**). Full text, verbatim (Japanese) and translation:

> **JA (verbatim):** "ムウマージのワザ「のろいのことだま」を使うと、ワザを受けたポケモンに「次の相手の番の終わりにこのワザを受けたポケモンに90ダメージ」という効果が適用されます。ポケモンにかかる効果は、一度ベンチに戻るとなくなるというルールがあり、これを利用すると、「のろいのことだま」の効果を受けなくなります。"
>
> **EN translation:** "When using Mismagius's attack 'Curse Orb,' the targeted Pokémon receives an effect that deals 90 damage at the end of your opponent's next turn. However, there is a game rule where effects on Pokémon are removed once they return to the Bench. By utilizing this rule, the 'Curse Orb' effect can be avoided, preventing damage from being dealt."

This restates the same "effects removed on going to the Bench" rule as the already-known article 57281623683481, just as a second, separately-numbered FAQ entry that exists only on the Japanese locale. No confirmable creation/update date was exposed on the page (checked specifically for 作成日/更新日 metadata — none visible).

### Other locales checked
- **zh-tw**: 13 articles = the 12 English ones + Budew (57286218211225). No extra duplicate.
- **ko**: 13 articles = the 12 + Budew. No extra duplicate. (Korean localized card names, e.g. "Followchu ex" for Mimikyu ex, "Jupithunder ex" for Jolteon ex — MT artifacts of the fetch tool, not official English names.)
- **fr**: only **7 of the 12/13** articles are translated (missing: Jolteon ex Electromagnetic Wall, Prank Spinner, Mismagius/bench, Scizor Gale Thrust, Buzzwole ex Big Beat, and Budew). French coverage is notably incomplete.
- **de, it, es**: only **7 articles** each (same subset pattern as French: items 1–6 plus the "Mimikyu ex damage" duplicate — missing Jolteon ex, Prank Spinner, bench/Curse, Scizor, Buzzwole ex, Budew).
- **pt-br**: fetch returned a partial list (5 items shown, including Budew as #3); could not confirm a full count in the budget available.

**Conclusion for Task 1**: The only substantive new find is the Japanese-only duplicate article `57281556361113`, which conveys no new rule — it reinforces the existing "effects clear when a Pokémon returns to the Bench" ruling already captured via 57281623683481. English/JP/zh-tw/ko article sets are otherwise unchanged from the known baseline. Western European locales (fr/de/it/es) carry a materially smaller subset of the FAQ than English/Japanese/Chinese/Korean.

---

## Task 2 — App update / rule-change notices since 2026-07-29

Source: perfectly-nintendo.com's cumulative Pokémon TCG Pocket update-history page (cross-checked against APKMirror version listings and the official Nintendo & Pokémon Blog / pokemonblog.com).

- **Ver. 1.7.0 (Jul 28/29, 2026)** — already known baseline (named-card Supporter search change). Full listed changes for completeness: "New Ruler of the Skies booster packs are now available," "Revisions to the Missions screen," "Added '♦♦♦♦ or higher guaranteed' booster pack category," "Deck order adjustment feature added," "Added feature to share decks using 2D pattern codes," **"Rule changes for some cards,"** "Revisions made to some features." (The "Rule changes for some cards" line is generic marketing copy; the only specific, named change found anywhere is the Gladion/named-search Supporter fix already in the baseline.)
- **Ver. 1.7.1 (Aug 5/6, 2026)** — patch notes text in full: **"Bug fixes."** No itemized list found anywhere (checked game8, pokemonblog, APKMirror, Reddit, Dexerto/Dot Esports — none have specifics).
- **Ver. 1.7.2 (Sept 3/4, 2026)** — patch notes text in full: **"Bug fixes and other behind-the-scenes improvements... focused on addressing issues affecting the player experience rather than introducing major new gameplay features"** (pokemonblog.com, Sept 3, 2026). Again, no itemized/card-specific list found.
- **No 1.8.x has shipped** as of 2026-09-22.
- Checked support.pokemon.com's TCG Pocket support category for "Known Issue" articles: the only one currently listed is **"Pokémon TCG Pocket Issue Affecting Certain Devices (July 2026)"** (article 51825646356756) — a device-compatibility notice, not a rules/card-behavior notice. No September 2026 "known issue" or card-behavior bug notice was found.
- **Battle Rules FAQ** (support.pokemon.com, article 38906248102292): confirmed still shows **"Updated May 12, 2026"** — unchanged, no post-2026-09-15 update.
- **Gameplay FAQ** (support.pokemon.com, article 30330309361172): shows **"Updated July 30, 2026 02:00"** — this is a real update after 2026-07-29 cutoff, though still before 2026-09-15. Verbatim new content pulled from it (not in prior baseline), under Task 5 below.

**Conclusion for Task 2**: No official, itemized rule or card-behavior change has been published since 2026-07-29 beyond the already-known 1.7.0 Gladion fix. 1.7.1/1.7.2 are opaque "bug fixes" releases with no public detail anywhere.

---

## Task 3 — Sets released after B4a

**None.** B4a ("Team Rocket's Ambition," released ~Aug 26, 2026 per pokemon.com/ptcgpocket.gg) remains the newest live set as of 2026-09-22.

Upcoming (per pokemon-zone.com schedule and ptcgpocket.gg, checked 2026-09-22):
- **B4b** — releases **Sept 29–30, 2026** (~1 week away). No card list or mechanic details are public yet; ptcgpocket.gg's B4b page is still a placeholder/stub with no populated content.
- **C1** — releases **Oct 28, 2026**. This is the first set coded "C1," i.e., the start of a new expansion series after the "A" and "B" series. No name or mechanic details found yet — too far out for spoilers at time of writing.

Since neither has shipped, there is no official wording yet on any new mechanics/keywords/rules they might introduce. [INFERRED: the "C1" code change itself may signal a new set-series naming convention, but nothing official states this explicitly yet.]

---

## Task 4 — Public data-mining / corpus status

- Searched GitHub broadly for successors to TCGP-Corpus-Lite, IL2CPP dumps, protocol dumps, and effect-definition dumps for Pokémon TCG Pocket. Found nothing new and public.
- **TCGP-Corpus-Lite** (github.com/superpikapool13/TCGP-Corpus-Lite, already known): confirmed via README that it is **translation-strings only** — "a small tool for comparing translation strings from Pokémon Trading Card Game Pocket, side by side across languages" (9 locales: de/en/fr/es/it/ja/ko/pt-br/zh-tw). Strings were "extracted by SombrAbsol for use by Encyclopædiæ Pokémonis." **It does not contain effect definitions/parameters, and does not contain the in-app rules/Tips/FAQ text.** No "full" (non-Lite) version is referenced anywhere in its README or elsewhere I could find.
- **RaenonX-PokemonTCGP** GitHub org (runs ptcgp.raenonx.cc, a datamining-backed wiki): public repos are limited to an APK asset extractor (pokemon-tcgp-apk-dumper), a CI/index repo, and a UI-discussion repo. The org states most of its actual data repos are **private**; nothing new and public was found here either.
- No public IL2CPP dump, protocol schema dump, or master-data effect-parameter dump for the current game version was located. (Per instructions, did not attempt to download any APK or bypass protections — this is a pure public-search result: nothing found.)

---

## Task 5 — Official statements on ties / disconnects / timers / tournament rules

### New verbatim text (Gameplay FAQ, support.pokemon.com, article 30330309361172, **updated 2026-07-30**):

> **"What happens if I experience a crash or disconnection during a versus match?"**
> "If you experience a crash or disconnection during a versus match, you may attempt to rejoin the match within the reconnection window of around 120 seconds. If you cannot reconnect within that timeframe, you lose the match."

> **"What happens to my ranked match points if there's a tie?"**
> "If your game ends in a tie, your ranked match points will not increase or decrease. However, your win streak points will be reset."

(A near-duplicate FAQ entry "What happens if I disconnect during a versus match?" gives the same ~120-second reconnection window / loss-on-timeout rule in slightly different wording.)

### Turn-limit draw rule (unofficial source only — flagging, not new/official)
GameWith's guide (gamewith.net/pokemon-tcg-pocket/48611, not an official Pokémon Company source) states: "In a 'Versus' battle, after 30 turns have passed for both players, the battle will be forced to a draw. In 'Solo' mode, the limit is extended to 50 turns instead of 30," plus simultaneous-KO-at-3-points and simultaneous-field-wipe draw conditions. This is **not independently confirmed on an official page** in this pass — [INFERRED likely already covered by the in-app Tips "About Battle Rules" text per the baseline, since that omission was specifically flagged as already-captured].

### Official Pokémon TCG Pocket tournaments / Worlds
- Confirmed Pocket has had an official "Pocket Championship" presence at Worlds since 2025 (PokeBeach, June 2025: "Worlds 2025 Activities and Side Events Announced, Including First-Ever 'Pocket' Championship!"). Could not locate a **2026-specific published Pocket rulebook** (tiebreakers, best-of-X, sudden death, deck-format specifics) on pokemon.com, championships.pokemon.com, or Limitless within the search budget — championships.pokemon.com's Worlds 2026 event-results page could not be read (returned only a bot-protection/Incapsula placeholder to the fetch tool). play.limitlesstcg.com does track Pokémon TCG Pocket tournaments/decks but I did not find a published official Pocket-specific rulebook there (Limitless's own docs page is for the general Limitless platform, not Pocket-specific ruling).
- No official statement found on: simultaneous-win resolution beyond the "tie ⇒ no rank change, win-streak reset" text above, or an official (non-GameWith) turn-limit citation.

---

## Sources (primary, official)
- https://app-ptcgpt.pokemon-support.com/hc/en-us/sections/53604902813209-Detailed-battle-FAQ (and /ja/, /zh-tw/, /ko/, /fr/, /de/, /it/, /es/, /pt-br/ locale variants)
- https://app-ptcgpt.pokemon-support.com/hc/ja/articles/57281556361113 (new article, no date shown)
- https://support.pokemon.com/hc/en-us/articles/30330309361172-Pok%C3%A9mon-TCG-Pocket-Gameplay-FAQ (updated 2026-07-30)
- https://support.pokemon.com/hc/en-us/articles/38906248102292-Pok%C3%A9mon-TCG-Pocket-Battle-Rules-FAQ (updated 2026-05-12, unchanged)
- https://support.pokemon.com/hc/en-us/categories/19331422065172-Pok%C3%A9mon-Trading-Card-Game-Pocket (support category listing, checked for Sept 2026 known-issue articles — none found)
- https://ptcgpocket.gg/b4b and https://www.pokemon-zone.com/schedule/upcoming/ (B4b Sept 29/30, C1 Oct 28, 2026)
- https://www.perfectly-nintendo.com/pokemon-trading-card-game-pocket-mobile-all-the-updates/ (1.7.0/1.7.1/1.7.2 changelog)
- https://pokemonblog.com/2026/09/03/pokemon-tcg-pocket-version-1-7-2-update-goes-live-with-bug-fixes/ (Sept 3, 2026)
- https://github.com/superpikapool13/TCGP-Corpus-Lite and https://github.com/RaenonX-PokemonTCGP (data-mine public-repo check)
- https://gamewith.net/pokemon-tcg-pocket/48611 (unofficial, turn-limit draw rule — flagged as non-official)

## Notes on blocked/inaccessible pages
- `championships.pokemon.com/.../catch-all-the-pokemonxp-and-2026-pokemon-world-championships-action` — returned an Incapsula bot-protection placeholder to the fetch tool; not bypassed, skipped per instructions.
- `gamerant.com` "Double Deck may be championship format" article — blocked by robots.txt for the fetch tool; not bypassed, skipped.
- Direct `curl` to `app-ptcgp(t).pokemon-support.com` from the sandbox is blocked by the outbound proxy's organization policy; all support-site content was retrieved via the WebFetch tool instead, which worked.
- Several bare-ID article URLs (no slug) on app-ptcgpt.pokemon-support.com intermittently 404'd; using the search-discovered full slugged URL, or the section-page discovery, worked reliably instead.

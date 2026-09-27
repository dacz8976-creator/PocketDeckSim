# REGISTERED (Sept 27): kpg, the discard-Energy credit on its own, as a pilot candidate

Dustin, Sept 27: "kpg: yes, register it as a candidate. F alone takes real error from 15.5 to 14.0 with a clean interval and no veto — by the rule it reads 'adopt' and only the held-out run is missing. … Run the held-out, confirm on post-Sept-24 events, and if it holds kpg becomes the pilot. That also sharpens the second question: once F is the baseline, kpf is 'R on top of kpg,' and everything that remains to explain is R."

## 1. In plain words

- **What kpg is:** kp3, the adopted pilot, plus one thing. Energy in the discard pile counts for something when the deck can pull it back:
  - Dragon's Blessing, Combust, Flame Patch, Professor Sada, Lusamine and Volkner;
  - on the opponent's side, only when such a source is visible on their board.
- **What it does:** Rayquaza's pilot uses Rainbow Cave about half the time, against a third under kp3. Over the 45 scoreboard cells, real error goes from 15.5 to 14.0, and no veto fires.
- **What is still needed before it becomes the pilot:**
  1. the held-out archetypes (B2e), where no deck may move more than 2 points further from its real results;
  2. confirmation on Limitless events after Sept 24.

## 2. What kpg is, exactly

- **Code:** `kpg<N>` as built by the cloud from kpf's registration (section 4 there; `../kpf_2026-09-26/BUILD.md`), at 9bffbda. It is in the official engine (main-83e17ae, `rl/engine-2026-09-27/`).
- **Nothing changes in it.**
  - The credit is K × min(E, CAP), with K = 15 and CAP = 4, §117's pre-set constants.
  - Without R there is no projection, so E is the side's whole discard-pile Energy that its available recovery sources can move back, under their play conditions.
  - The own side may use its own list. The opponent's side counts only a source visible in play that can act as its text allows.
- **The recovery class** is the six cards in the build note, re-checked from every card text.

## 3. Evidence so far, and what kind it is

- **The 45-cell reading on Sept 27** (`../kpf_2026-09-26/reading/score45_kpg3_vs_kp3.txt`; official engine, against scoreboard v3's kp3):
  - real error 15.5 → 14.0;
  - ΔMSE −43.2, 95% interval −62.2 to −26.5;
  - τ̂ margin +1.47, 90% interval +0.87 to +1.70;
  - no cell or deck veto;
  - rule v2 reads "adopt (held-out-deck veto checked separately)".
- **Disclosed:** that reading was registered as a diagnostic of kpf (F's own share), not as an adoption test, and it came before this registration.
  - The 17 new cells were also used to design kpf (RUN5 "Development data").
  - So the 45-cell result is development evidence. The decision rests on sections 4 and 5, which come after this registration.
- **Where the gain comes from:** F acts only where a recovery source exists. Among the scoreboard decks, that is Rayquaza (Dragon's Blessing, Sada, Rainbow Cave feeding them) and Blaziken (Flame Patch).
  - kpf's identity runs showed F changes 2.1% of choices on the 28 table cells, all in Blaziken's.
  - Rayquaza v Lucario, same deals, kpg3 against kp3: 59 wins of 200, against kp3's 43 (`../kpf_2026-09-26/reading/READING.md`).

## 4. The held-out check (before confirmation)

- **Run:** kpg3 on both sides of B2e's 96 pairings, on B2e's deals (21,106,000,000 + pairing × 10,000 + i, i < 500), at the official engine. It is compared with kp3's rows at the same engine (`../kpf_2026-09-26/reading/b2e_kp3.jsonl`).
- **The rule:** a held-out archetype (pairings 0-47) moving more than 2 points further from its Limitless pooled equal-weight average is a veto. Under rule v2 it counts only through mixed rows, which would then be run. Dustin's files (48-95) are reported, never counted.
- **Also reported, not gated (the coverage decks):**
  - the Scizor coverage row, run with kpg3 on its deals;
  - the variation check's second lists, once they are built into the gauntlet.

## 5. Confirmation (RUN5 "Rules")

- **Where:** Limitless events starting after the development window's last event on Sept 24, 2026, never the spent Sept 25 holdout.
- **What it needs:** size as well as direction. On the post-freeze events alone, kpg's τ̂ margin over kp3 must be at least half its development margin (+1.47, so at least +0.74), with its own 90% interval above zero. The pooled figure and the sign are reported beside it.
- **Data:** a pull of post-freeze Limitless events by the same method and parsing as scoreboard v2's development half, over the 45 cells. There are few events so far, so confirmation waits until they are enough to fill the cells. When to pull is Dustin's call.
- **If it confirms:** kpg becomes the pilot for the table and the screen together (the reserve route's (e): one pilot). kpf is then read as "R on top of kpg".
- **Dustin's ruling, Sept 27: combine with koa.** The target is one pilot, kp3 + koa's opening (switch A) + kpg's discard credit. It is reached by a composition check of the two components, once kpg's held-out check is in (RUN5 "Composing candidates into one pilot"). Each component keeps its own verdict and evidence.

## 6. What would refute it

- A held-out archetype moves more than 2 further, and its mixed rows show kpg's own side worse.
- Or the post-freeze margin falls short of +0.74, or its 90% interval reaches zero.
- F makes the bot hoard: the kpf traces showed no sign, and the check is repeated for kpg3 alone (`../kpf_2026-09-26/reading/trace_rayquaza_v_lucario_kpg3.txt`: retreats 0.79 a game against kp3's 0.85, recoveries 2.40 against 2.08).

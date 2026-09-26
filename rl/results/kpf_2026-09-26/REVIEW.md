# kpf registration: its one review (Sept 26 evening)

An independent reviewer read the draft against kpr's code at e09fb46, the §117 prereg file, the card database and RUN5's Rules.
- It found nothing tuned to a cell and no false number.
- Every fix below was applied to the draft before registration.

1. **R's conditions: OK.**
   - `projected_active_energy` (e09fb46 `value_functions.rs` 2159-2205) checks, for each Ability: used this turn, switched off, holder position, Active type, Zone block, discard-pile Energy (each taken once) and a self-damage knockout.
   - Dragon's Blessing's conditions match the move generator (`move_generation_abilities.rs` 265-272), and any type may be taken.
   - Applied: the Ice Maker bullet reworded (no holder condition), and "switched off" added.
2. **Constants.**
   - `s117_prereg.txt` is in Pocket Deck Lab, not the repo. Its text shows K = 15 and CAP = 4 were written before any g-tier game; its timestamp is a bulk-copy time.
   - Applied: the path, the lines, what shows the order, and the disclosure that §117 aimed them at a Rayquaza-Dragonair deck.
3. **List-free wording.**
   - A Dragonair in the Active Spot can't use Dragon's Blessing.
   - No Tool, Stadium or attack recovers discard Energy today.
   - Applied: "can use such an Ability as its text allows (holder position included)", and the note that the Tool/Stadium clause covers future cards.
4. **The recovery class is 6 cards:** Dragonair B4 117, Flareon ex A3b 009, Flame Patch B1 217, Professor Sada B3a 072, Lusamine A3a 069 and Volkner A2 153.
   - Applied: the list, and "counts only Energy the effect can move, to a Pokémon it can target, under its play conditions".
5. **RUN5 consistency.**
   - Applied: B2e's 48 held-out pairings are in the reading itself.
   - Applied: the held-out veto is under the mixed-row condition like the others.
   - Applied: the freeze date is stated (after the window's last event on Sept 24).
   - Applied: post-freeze confirmation for all 45 is shown to follow from the two existing rules.
   - Applied: the Scizor row doesn't hold the verdict open if the repair isn't in the build.
6. **Wording.** Rainbow Cave under kpr3 said "barely changes", but the numbers are 28% and 40%. Applied.

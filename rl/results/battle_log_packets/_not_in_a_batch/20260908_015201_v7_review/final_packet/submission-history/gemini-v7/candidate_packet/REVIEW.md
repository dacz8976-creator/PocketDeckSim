# Battle Review: Dacz8976 vs. Opponent (AI)

- **Date**: Unknown (source filename suggests 2026-09-08, not verified in video).
- **Match Mode**: Solo (explicit `AI` badge displayed above Opponent name).
- **Auto State**: Off.
- **Players**: Player (`Dacz8976`) vs. Opponent (`AI`).
- **Starting Board**:
  - Player Active: Duraludon (HP 100, Dragon/Metal, 0 Energy).
  - Player Opening Hand: Rainbow Cave, Iris, Copycat, Professor's Research, Duraludon (placed Active).
  - Opponent Active: Team Rocket's Rattata (HP 40, 0 Energy).
  - Opponent Bench: Corphish (HP 60, 0 Energy), Team Rocket's Rattata (HP 40, 0 Energy).

---

## Timeline & Evidence Ledger

### Setup (00:00.000 - 00:22.800)
- Coin flip: Black coin / Going second.
- Both sides draw starting hands. Player places Duraludon as Active.
- Opponent reveals Active Team Rocket's Rattata, Bench Corphish and Team Rocket's Rattata.

### Turn 1: Opponent (00:23.400 - 00:29.200)
- **Observed actions**: Opponent plays Chien-Pao ex (HP 130) onto the Bench. No Energy attached (first-turn rule). Opponent passes.
- **State delta**: Opponent Bench has Corphish, Team Rocket's Rattata, and Chien-Pao ex.
- **Evidence anchors**:
  - `00:23.400`: Opponent turn banner.
  - `00:27.000`: Chien-Pao ex card played to Bench.
  - `00:29.000`: Turn transitions to player.

### Turn 2: Player (00:29.400 - 01:06.400)
- **Observed actions**:
  - Player draws Dratini (HP 60) for turn. Fighting Energy generated in Energy Zone.
  - Player plays Dratini onto the Bench.
  - Player plays Supporter Professor's Research, drawing Poké Ball and Axew (HP 70).
  - Player plays Item Poké Ball, searching and drawing an Axew.
  - Player plays Axew onto the Bench.
  - Player plays Stadium Rainbow Cave.
  - Prompt: "Use the effect of Rainbow Cave?". Player selects "Yes". The generated Fighting Energy is discarded and replaced with Metal Energy.
  - Player manually attaches Metal Energy to Active Duraludon.
  - Player ends turn without attacking.
- **State delta**:
  - Player Active: Duraludon (HP 100, 1 Metal Energy attached).
  - Player Bench: Dratini (HP 60, 0 Energy), Axew (HP 70, 0 Energy).
  - Stadium: Rainbow Cave active.
  - Player Hand: Iris, Copycat, Axew.
- **Evidence anchors**:
  - `00:31.200`: Dratini drawn.
  - `00:33.800`: Dratini placed on Bench.
  - `00:39.400`: Professor's Research played.
  - `00:41.800`: Poké Ball and Axew drawn.
  - `00:46.400`: Poké Ball played.
  - `00:48.000`: Axew revealed from deck into hand.
  - `00:51.400`: Axew benched.
  - `00:56.200`: Rainbow Cave played.
  - `01:00.000`: Rainbow Cave activated (Fighting Energy discarded -> Metal Energy produced).
  - `01:04.000` - `01:05.000`: Metal Energy attached to Duraludon.
  - `01:06.200`: Turn ended.

### Turn 3: Opponent (01:06.600 - 01:08.000)
- **Observed actions**: Opponent's turn starts. Video truncates at 01:08.000.
- **State delta**: None observed.
- **Evidence anchors**:
  - `01:06.600`: Turn 3 banner displayed.
  - `01:08.000`: Video ends.

---

## HP, Energy, Bench, Hand, and Score Reconciliation
- **Score**: 0 - 0 (no knockouts occurred).
- **Player Active Duraludon**: 100/100 HP, 1 Metal Energy attached.
- **Player Bench**: Dratini (60/60 HP, 0 Energy), Axew (70/70 HP, 0 Energy).
- **Opponent Active Team Rocket's Rattata**: 40/40 HP, 0 Energy.
- **Opponent Bench**: Corphish (60/60 HP, 0 Energy), Team Rocket's Rattata (40/40 HP, 0 Energy), Chien-Pao ex (130/130 HP, 0 Energy).

## Mechanics & Tactical Observations
- Player utilized Rainbow Cave's effect on Turn 2 to convert unusable Fighting Energy into Metal Energy, enabling the first Energy attachment required for Duraludon's Power Beam (which requires Metal + Fighting).

## Outcome
- Unknown. Recording is incomplete and terminates at 01:08.000.

## Explicit Uncertainties
- See UNCERTAINTIES.json entry U1 regarding the truncated recording and unresolved match outcome.

---
*Status: Partial pending independent Sol verification*

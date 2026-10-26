# Uncertainties (recording g1sub)

Everything not listed here is read directly from the frames. Each item gives its turn, the timestamps, and what would settle it.

## U1. Dustin's deck list and the QR code (before turn 1)
- Frames: t=0-1 ("Share With 2D Pattern Code" QR over a blurred deck screen), t=2 (deck tile "New deck 17" with a badge "25").
- What is uncertain: the QR content was not decoded, so the 20-card list is only known from the cards that appeared in play (see Notes for use in REVIEW.md). The meaning of the "25" badge on the deck tile is not established.
- What would settle it: decode the QR from the full-resolution frame t=0000, or ask Dustin for the deck code or list.

## U2. Name of the Item the opponent played on turn 7
- Frames: t=214-217 (Item played, banner "Retreat Cost is 1 less" at t=217), t=217 and t=220 (item card face-up in the opponent's discard, upside-down at the left edge).
- What is uncertain: the card name is read from upside-down small text in the discard ("X Speed") and from the effect banner. The wording of the card itself was not seen at readable size.
- What would settle it: the Battle Log, or a full-resolution zoom on the opponent's discard at t=217-222.

## U3. Dustin's hand after his Copycat on turn 6
- Frames: t=164-170 (Copycat played, hand tray lowered), t=172 (hand shows Poke Ball, Mega Gyarados ex and a third card hidden), t=178-182 (second Poke Ball played, then hand is Mega Gyarados ex only).
- What is uncertain: the exact three cards drawn are not all visible at once. They are inferred as Poke Ball, Poke Ball, Mega Gyarados ex from the later plays. Cabbie and the original Mega Gyarados ex went back into the deck (shuffled by Copycat), so the Mega Gyarados ex in hand afterwards was redrawn.
- What would settle it: the half-resolution frames t=166.5-170.0 with the hand tray open, or the Battle Log.

## U4. Dustin's hand at the start of turn 10 (and the source of the second Soothing Shore)
- Frames: t=298-306. The hand tray is partly hidden behind a toast and the large drawn card at t=300-302.
- What is uncertain: the Soothing Shore played at t=303-305 is believed to be the copy drawn on turn 8 (t=242, kept in hand through turn 9, visible at t=260.5). A direct frame of the full hand at the start of turn 10 was not found.
- What would settle it: a full-resolution frame of the hand at t=296-299.

## U5. No manual Energy attachment on turn 12
- Frames: t=336-346. The Energy Zone icon is still shown (a Water Energy available) at t=342-346 and the only Energy attach seen this turn is Turbo Shark's effect (to Mega Gyarados ex, t=344-346).
- What is uncertain: whether Dustin chose not to attach, or whether it was not captured. The game ended on the Knock Out at t=344.
- What would settle it: nothing further is needed for the result; the Battle Log would confirm.

## U6. Mega Gyarados ex attack text and cost (turn 8)
- Frames: t=246 (full card), t=303-312 (small card).
- What is uncertain: Mega Blaster is read as 140 damage with four Energy symbols (three Water, one Colorless) and the effect text "Discard the top 3 cards of your opponent's deck". The effect text was read at low size. The attack was never used.
- What would settle it: a full-resolution zoom of the card at t=246 or t=303.

## U7. Opponent's hand counts
- Frames: all opponent turns. Counts are taken from the number of card backs in the opponent's fan.
- What is uncertain: the fan is partly hidden by banners and the Energy Zone, so counts can be off by one at some seconds (for example t=260-280). The opponent's draws on turns 1, 3, 5, 7, 9, 11 are inferred from the fan growing, not seen as a draw.
- What would settle it: the Battle Log, or a closer look at the half-resolution frames during each opponent draw.

## U8. Mega Sharpedo ex retreat cost
- Frames: t=187-191, t=215-226, t=300-306.
- What is uncertain: the card shows no Energy symbol in its retreat box, and no Energy was lost when Dustin retreated it on turn 6 (Water x1 stays on the Benched Mega Sharpedo ex, t=191-215). The retreat cost was not read as a number in the card text.
- What would settle it: a full-resolution zoom of the Retreat box on Mega Sharpedo ex at t=300.

## U9. Opponent's set numbers
- Set numbers on the opponent's cards (Buneary, Mega Lopunny ex, Hitmonchan ex) are not readable at any frame size. OPPONENT.json uses null for them.
- What would settle it: the Battle Log or the card detail screen.

## U11. Meaning of "points_taken" in OPPONENT.json
- Not a video uncertainty. The field is filled as points the opponent scored with that Pokemon (Hitmonchan ex 2, others 0). If it was meant as points Dustin took by Knocking that Pokemon Out, the values are Buneary full-art 1 (t=78), Hitmonchan ex 2 (t=347-350), others 0. Both readings are recorded in the "notes" field of OPPONENT.json.

## U10. Meaning of the "opponent_effects" field
- Not a video uncertainty. OPPONENT.json fills the field as effects caused by the opponent's cards on Dustin (Confusion on turn 5; no healing by the opponent, no Bench damage). If the field was meant to describe effects on the opponent's own Pokemon, then the entries are: special conditions on the opponent none, healed none, bench damage taken none (Aqua Jet's bench damage was never used; Dustin's Turbo Shark never hit the Bench). The answer is the same for healing and Bench damage under either reading.

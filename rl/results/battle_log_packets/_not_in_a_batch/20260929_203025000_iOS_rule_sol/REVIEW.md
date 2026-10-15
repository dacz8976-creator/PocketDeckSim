# Rule test review: Victory Star after a Confusion Heads flip

Reviewer: `sol_confusion_203025` (Sol); review date: 2026-09-29 America/Chicago. Scope: entire supplied 2:55.99 recording, with dense inspection of the Confusion and Victory Star sequence. This is an explicitly labeled **RULE TEST**. There is no terminal result or ladder entry. Source identity and recording relationship are in [SOURCE.json](SOURCE.json); coverage and frame references are in [COVERAGE.md](COVERAGE.md).

## Finding

The on-screen sequence shows a Confused Team Rocket's Moltres ex **pass** its separate Confusion attack gate on Heads. Its Heat Charged attack then flips three coins, yielding one heads and two tails. The game offers benched Victini's Victory Star; the owner chooses Yes; and Heat Charged's **three attack coins** are rolled again, again yielding one heads and two tails. One Fire Energy is attached to Moltres ex (the displayed count rises from six to seven). The recording shows **no Victory Star offer for the single Confusion coin**, and no second Confusion gate after the attack-coin reroll. This contradicts a blanket claim that Victory Star is unavailable whenever the attacker is Confused, for this observed case. It does not independently establish the simulator's internal rule implementation or the result when the Confusion gate is tails.

| Elapsed time | Direct observation | Retained source frames |
|---|---|---|
| 00:19-00:21 | Victini is on the owner's Bench. Its visible Victory Star text says that once during the owner's turn, after flipping coins for an attack of one of the owner's Fire Pokemon, the owner may ignore all those results and begin flipping those coins again. | `evidence/contact_01.jpg` |
| 02:08-02:20 | Owner plays Team Rocket's Master Plan. The visible card says it Confuses the opponent's Active Pokemon and flips a coin; tails also Confuses the owner's Active. Stufful becomes Confused, the card's coin is tails, and owner Active Moltres ex is explicitly announced Confused. | `evidence/key_001.jpg`, `evidence/key_007.jpg`, `evidence/key_021.jpg` |
| 02:26-02:30 | Owner selects Moltres ex's Heat Charged. The next prompt is `Coin flip — Confused`, a **single gate coin**, which displays `Heads!`. No Victory Star prompt appears here. | `evidence/key_035.jpg`, `evidence/key_041.jpg` |
| 02:32-02:40 | Heat Charged's own text calls for three coins, with one Fire Energy produced per heads. The attack's first three-coin result is **1 heads, 2 tails**. Moltres ex shows six Fire Energy before resolution. | `evidence/key_059.jpg` |
| 02:41-02:45 | A distinct prompt asks `Use the effect of Victory Star?` and displays Victini's ability text; Yes is selected, followed by a Victory Star activation animation. | `evidence/key_063.jpg`, `evidence/key_071.jpg` |
| 02:47-02:53 | The Heat Charged three-coin display resets to zero and rolls again, ending **1 heads, 2 tails**. Moltres ex's displayed Fire Energy count rises from six to seven. | `evidence/key_083.jpg`, `evidence/key_087.jpg` |
| 02:54-02:55.99 | Turn 7 starts for the opponent. Both Actives still show Confusion. Recording ends before the battle ends. | `evidence/key_contact_04.jpg` |

## Whole supplied clip

| Elapsed time | Observed phase |
|---|---|
| 00:00-00:29 | Battle loads. Owner goes second, with Team Rocket's Moltres ex Active and Victini Benched. The Victini card and Victory Star text are shown. |
| 00:30-00:59 | Opponent develops a Stufful Active and three Benched Pokemon, then plays Professor's Research. Owner puts Rainbow Cave in play and attaches Fire Energy to Moltres ex. |
| 01:00-01:31 | An earlier Heat Charged coin sequence increases Moltres ex's Fire Energy. The opponent later develops its Bench, including an evolution; the owner draws cards and begins building its own Bench. This is before either Active is Confused. |
| 01:32-02:07 | Owner establishes two Darumaka on the Bench. Another pre-Confusion Heat Charged at about 01:45 flips 1 heads and 2 tails and shows a Victory Star prompt. Moltres ex then has six Fire Energy. On the next opponent turn Rainbow Cave and Rotom Dex are played; owner turn 6 begins. |
| 02:08-02:25 | Owner plays Team Rocket's Master Plan. Stufful becomes Confused, the card's coin is tails, and Moltres ex becomes Confused too. Owner evolves both Benched Darumaka into Darmanitan and continues developing Energy. |
| 02:26-02:55.99 | Confusion gate, attack coins, Victory Star offer/selection, and rerolled attack coins occur as detailed above. The clip cuts off just after opponent turn 7 begins, with no point gained by either side in the visible segment. |

## Limits

- This packet records what the app displayed in one attempt. No source code or official game ruling was checked here. The attack's final one-head result produced the same Energy gain as its discarded first result, so the **separate prompt and reset three-coin display** are the evidence that Victory Star was used; the net Energy count alone would not prove a reroll.
- The one-coin Heads result is explicitly labeled `Confused`, and the later three-coin screen uses Heat Charged's exact effect text. They are different flip groups in the visible sequence. Victini's printed wording alone would not establish how the app routes every possible flip.
- The recording ends mid-battle. Opponent hidden cards, final outcome, and the unobserved tail outcome for the Confusion gate remain unknown. The Auto button appears off during the consequential sequence; neither player mode nor opponent identity is established from that alone.

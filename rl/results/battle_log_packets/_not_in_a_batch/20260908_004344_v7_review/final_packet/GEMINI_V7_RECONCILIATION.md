# Gemini v7 reconciliation

Gemini v7 produced the primary full-battle outline and covered all eight turns, major actions, knockouts, scoring, and the terminal result. Its source binding was correct. The two-pass run used approximately $0.4007-$0.4302 of reported usage.

The parser correctly blocked automatic acceptance. The raw packet lacked the required battle-identity version and omitted named causes on the two Thieving Incisors Energy-effect records. More importantly, the blind preflight disagreed with the main pass on the opening Pokémon and exact terminal frame. Those blocks forced selective review instead of silently accepting the draft.

## Accepted after correction

- Gemini's eight-turn structure, action sequence, damage, knockout, scoring, and 3-1 opponent win are retained.
- The opening hand's third card is Team Rocket's Raticate ex, not Team Rocket's Rattata.
- The first Magmar's attached Energy and the Energy moved by Thieving Incisors are Darkness, not Fire. Raticate ex later holds Darkness plus Psychic.
- A second Drowzee benched during Turn 5 was added to the record.
- The result banner timestamp is approximately 04:18.950, not 04:18.800.
- Unsupported Solo/AI classification was removed. It is minor metadata and remains unknown.
- The two Energy-effect records now name Thieving Incisors as their visible cause, and battle identity is versioned.

The untouched Gemini response and candidate packet remain in `submission-history/gemini-v7/`. REVIEW.md, COVERAGE.md, SOURCE.json, and UNCERTAINTIES.json are the accepted corrected record.

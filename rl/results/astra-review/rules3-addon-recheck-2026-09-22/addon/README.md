# Rules3 RL add-on rebuild and forecast check

September 22, 2026. This folder preserves the original 0.6.0 source, the forecast-code unchanged 0.7.0 rules3 baseline, and the corrected 0.7.1 candidate. No earlier wheel, virtual environment, checkpoint, training result, or engine source was changed. No Run 5 training was started.

## Identity

The project manifest named rules3 as the current engine release. The release executable SHA-256 was 66acb493724ec189300ddaae6bd61de9a175d07677ad3df23da36414a3a922f2. Its source manifest SHA-256 was 77280596fb5a8a9442cb0086c4fae8239c4519a3a0eb268423ad621883f89906. The versioned 0.7.0 and 0.7.1 builds used the canonical rules3 source tree as a path dependency. The engine and source manifest identities were checked before the canonical add-on update.

The corrected 0.7.0 wheel SHA-256 is 9bad48553d1f55e09f97106674b31426a8cc8685c96dd1fca5f0394770f964a5. Its v2.rs content is unchanged from the original 0.6.0 add-on (SHA-256 9e19558fb727d265e60549a595fb16817e560fa64a90c03e027b4c1c40431c4e). The corrected 0.7.1 wheel SHA-256 is b4fddfa482f98c1269855c643686d8cd4f994010d508fd70690292a277d4f3c7. These wheels use the platform tag cp38-abi3-linux_x86_64. See wheel-sha256.txt and source-sha256.txt for current inventories. The original wheels incorrectly advertised manylinux_2_34 and are preserved under wheels/superseded-manylinux-label; their hashes are in superseded-wheel-sha256.txt. readelf-baseline-070.txt and readelf-final-071.txt show a GLIBC_2.39 requirement, which the original tag could not promise. The generic Linux wheels make no manylinux portability claim.

The original baseline Python executable is /home/dacz8976/.cache/pocket-deck-lab/rules3-addon-070/venv/bin/python. The original final Python executable used for the full benchmark is /home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071/venv/bin/python. Both remain unchanged. The corrected final wheel was installed and smoke-tested in a distinct environment at /home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071-linux/venv/bin/python. Its installed extension has the same SHA-256, 46e7b29fcb188326dcd0b6a2c99113c91bb0ebc70e9ab2dc78df7b933ad1df9a, as the tested original environment.

## Forecast result

A constructed Team Rocket Koffing Reverse Thrust at two points hit a 10-HP opposing Active. On the 0.7.0 baseline, both one-bench and two-bench attack rows claimed to be priced but reported zero points and no win. The engine awarded the third point and win only after a switch choice and its pending forced rule step.

Version 0.7.1 plays through public single-option continuations while a new rules3 rule frame remains. With one bench, the attack row now reports one point divided by three and win probability one. With two benches, the attack row is unpriced because the player has a genuine choice; each subsequent Activate choice row reports the point and win correctly. Hidden continuations, too many branches, and budget exhaustion remain visibly unpriced. The add-on does not select a real choice for the learner.

The focused EndTurn fixture with Glimmora point denial prices the two exact coin outcomes within the configured branch cap: expected point feature one sixth and win probability one half. Hidden opponent-deck Caterpie evolution is refused with an explicit unknown-deck reason; a known own-deck evolution frame is priced. Focused tests are in the final source snapshot and focused-tests.log. Two direct add-on unit tests also passed: ChooseRetreatEnergy, ChooseAttackEnergyDiscard, and ChooseRandomEvolutionTarget appear as visible, distinct encoded legal alternatives. The random-evolution target is priced when the acting player has a known own deck; an unknown evolution card is explicitly refused. Their output is in choice-encoding-tests.log. The decision-wide lookahead trace and per-action forecast_diagnostics analysis method identify affected decisions and refusal reasons without adding these fields to learner features. The diagnostic returns one JSON string per legal action, in legal-action order, with status, reason, new_rule_frame_seen, forced_steps, and lookahead_new_rule_frame_seen.

Twenty final-wheel decisions also passed the hidden opponent hand/deck and own deck-order invariance checks, legal move-list checks, and twenty visible-own-hand positive controls. The parent recheck packet contains the broader replay, hidden-information, and same-seed feature comparisons.

The existing capped forecast beam remains an approximation when a continuation has more branches than its cap. The one-coin point-denial fixture fits inside the cap. This evidence does not claim exact probabilities for arbitrary multi-flip continuations.

## Rebuild and install

The canonical add-on source is at Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env. Historical source and both versioned copies are preserved here. The baseline-0.6-to-rules3-0.7.0.patch and rules3-0.7.0-to-0.7.1.patch files show each source change. The final source snapshot matches the canonical add-on source.

The Rust build originally used two Cargo jobs, no debug data, no incremental output, and an offline dependency cache. A future build from the current canonical 0.7.1 source can use a distinct target directory:

    CARGO_TARGET_DIR=/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071-linux/rebuild-target CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 cargo build --locked --offline --release --manifest-path "/mnt/c/Users/dacz8/Projects/Pocket Deck Lab/Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env/Cargo.toml"

Check the resulting extension SHA-256 and the rules3 engine identity before packaging a rebuild. The packaging correction itself did not rebuild Rust: build_wheel.py packages a verified existing extension and checks its expected SHA-256 before writing a wheel. For example, the final wheel can be reproduced with:

    python3 build_wheel.py --module /home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071/venv/lib/python3.14/site-packages/pdl_rl_env.abi3.so --version 0.7.1 --output-dir wheels --expect-sha256 46e7b29fcb188326dcd0b6a2c99113c91bb0ebc70e9ab2dc78df7b933ad1df9a

The corrected final wheel was installed offline with:

    /home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071-linux/venv/bin/python -m pip install --no-index wheels/pdl_rl_env-0.7.1-cp38-abi3-linux_x86_64.whl

The wheel contains package metadata and hashed RECORD entries. Its installed module SHA-256 matches the original tested binary, so earlier benchmark results apply to this corrected package. A one-game engine_play smoke test with frozen Altaria and Lucario decks returned winner 1, points [0, 5], turns 10. RawEnv.forecast_diagnostics is present.

## Focused test commands

The isolated source copy under /home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071/Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env was tested with two integration targets and a separate unit target. The unit test binary needs the local Python shared library because this package is normally built as a Python extension:

    CARGO_TARGET_DIR=/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-070/target CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 cargo test --release --offline --manifest-path "/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071/Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env/Cargo.toml" --test deferred_reverse_thrust

    CARGO_TARGET_DIR=/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-070/target CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 cargo test --release --offline --manifest-path "/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071/Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env/Cargo.toml" --test rules3_continuations

    RUSTFLAGS="-C link-arg=/usr/lib/x86_64-linux-gnu/libpython3.14.so.1.0" CARGO_TARGET_DIR=/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071/unit-target CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 cargo test --release --offline --manifest-path "/home/dacz8976/.cache/pocket-deck-lab/rules3-addon-071/Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env/Cargo.toml" --lib

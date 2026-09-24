# Rules4 add-on 0.7.2

This folder preserves the rules3 add-on 0.7.1 source, the rules4 add-on 0.7.2 source, their patch and hashes, focused tests, and the new Linux wheel. The canonical add-on source matches rules4-0.7.2-source. No prior wheel, virtual environment, training checkpoint, or historical result was modified. No training was started.

The engine dependency came from the rules4 source archive in the parent folder, SHA-256 69a7ce40c1fec70493367ba79f55ea4dcee677a597c2c965d2e146351a21bbc6. Its source manifest SHA-256 is ddb6bc9b8add3ffdf5fe84db39a5fbbb0ff0fa66955cc39df25c1de9958c839c. The candidate engine executable SHA-256 is e6593ed816d0d5dbaf24fc8bc81a8317ed8069cda6ae7162c3d53e1fa7a12415.

The 0.7.2 add-on changes only version metadata, the version in one help message, and a new T2 forecast regression test. The forecast implementation src/v2.rs is byte-identical to 0.7.1 (SHA-256 a8e83636379ccbb2da92e5029d76c7bdbba669cd71180dabf6992044837cd796). The new test shows that the observed last-Pokemon simultaneous finish is priced in both seats: own point feature increases by one third, opponent point feature by two thirds, and both win and loss probabilities remain zero because the result is a tie. All five focused integration tests passed, including Reverse Thrust, point denial, and end-turn evolution checks. See focused-integration-tests.log.

The corrected wheel is wheels/pdl_rl_env-0.7.2-cp38-abi3-linux_x86_64.whl, SHA-256 56ca0bad21a569b852da3c82c321f6ab3f08b162e8019d0cf5871c82636c925b. The installed shared library SHA-256 is 0fee43ceaf9cf6bc15ed2319bb08c100397621a60703880cf26ace8f044a9101. It resides in /home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/venv/lib/python3.14/site-packages/pdl_rl_env.abi3.so. The Python executable is /home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/venv/bin/python. Its import reports version 0.7.2 and provides RawEnv.forecast_diagnostics. A frozen Altaria versus Lucario engine_play smoke test succeeded. See packaging-checks.txt.

readelf-072.txt shows a GLIBC_2.39 requirement, so the wheel uses the generic linux_x86_64 tag and makes no manylinux portability claim. The wheel ZIP, tag, metadata, embedded module hash, and every RECORD entry were checked. The earlier mislabeled 0.7.0 and 0.7.1 wheels remain preserved in the rules3 add-on packet; they were not reused.

The two choice-encoding unit tests also passed on 0.7.2 and rules4 (2 passed, 0 failed, 0 ignored). They verify that retreat and attack Energy choices appear as distinct public legal options and that random-evolution targets are encoded while hidden-deck refusals stay scoped. This unit-test executable needs an explicit local Python link argument. The exact passing command, with a separate target directory, was:

    RUSTFLAGS="-C link-arg=/usr/lib/x86_64-linux-gnu/libpython3.14.so.1.0" CARGO_TARGET_DIR=/home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/unit-target CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 cargo test --locked --offline --release --manifest-path "/home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env/Cargo.toml" --lib

The shared library at that path was verified before testing. The run finished in 7m 41s; full output is in choice-encoding-tests.log. The earlier broad linker failure remains preserved for transparency and does not apply to this corrected unit command.

## Reproduce from the verified local sources

The staged source directory is /home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072. Its deckgym-fork-s193 tree was extracted from the exact rules4 source archive above. The add-on source is the copy under Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env inside that directory. Build with two jobs, no incremental output, no debug data, and the offline dependency cache:

    CARGO_TARGET_DIR=/home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/target CARGO_BUILD_JOBS=2 CARGO_PROFILE_RELEASE_DEBUG=0 CARGO_INCREMENTAL=0 cargo build --locked --offline --release --manifest-path "/home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/Boss Folder/rl-feasibility-2026-09-18/pdl_rl_env/Cargo.toml"

After verifying the shared-library hash, package without a manylinux claim:

    python3 build_wheel.py --module /home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/target/release/libpdl_rl_env.so --version 0.7.2 --output-dir wheels --expect-sha256 0fee43ceaf9cf6bc15ed2319bb08c100397621a60703880cf26ace8f044a9101

Install offline into a separate Python environment:

    python3.14 -m venv /home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/venv
    /home/dacz8976/.cache/pocket-deck-lab/rules4-addon-072/venv/bin/python -m pip install --no-index wheels/pdl_rl_env-0.7.2-cp38-abi3-linux_x86_64.whl

Run the focused tests from the staged source with the same Cargo settings and three explicit targets: deferred_reverse_thrust, rules3_continuations, and rules4_t2_forecast. A broad cargo test --tests attempt linked the Python extension library test without libpython and failed at linkage; its output is preserved in lib-test-python-link-failure.log. The three integration targets compiled and passed without that linkage requirement. The engine itself passed the full 1,826-test suite in the parent folder.

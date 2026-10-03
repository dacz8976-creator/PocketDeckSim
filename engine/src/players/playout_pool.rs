//! The REALISTIC knowledge mode's candidate opponent lists (the play-out chooser, playout_player.rs; Oct 2): the lists
//! under decks/screen/opponents and decks/research, copied here at build time of this file (each with its sha256), so the
//! player needs no file at run time. The pool never holds a brew or one of Dustin's lists: the meta side is never handed
//! the brew's list (DESIGN.md section 9). Regenerate `POOL` by hand if those lists change: the sha256 lines show which
//! version. Each research/X list holds the same cards as t-X; the player removes such duplicates when it loads the pool.
//!
//! Below `POOL` (not generated): lists added at run time through `KX_EXTRA_LISTS` (fixes round 1, Oct 3), such as the
//! fixed computer deck of Dustin's positions. Read once per process. Refused (round 2): a path under decks/brews or
//! decks/dustin, and any list holding the same cards as a list there, wherever the copy lives.

/// (name, source path, sha256 of the source file, the list text).
pub const POOL: [(&str, &str, &str, &str); 16] = [
    ("t-altaria", "decks/screen/opponents/t-altaria.txt", "c3a57b9c835be77ba864514e2636645885c4f22d75028c5f29e2686edcbe171f", r#"Energy: Psychic
2 Swablu B1 196
1 Mega Altaria ex B1 102
2 Eevee B1 184
2 Espeon B3a 020
2 Darkrai B2b 040
1 Igglybuff A4a 059
2 Professor's Research P-A 007
2 Copycat B1 225
1 Sabrina A1 225
2 Poké Ball P-A 005
1 Field Blower B3 147
1 Small Balloon B3b 064
1 Training Area B2 153
"#),
    ("t-blaziken", "decks/screen/opponents/t-blaziken.txt", "d88a70e56dae8f8500d539348223b5fee5eaba705667578a8fcbca95963fd7ed", r#"Energy: Fire
2 Torchic B1 033
2 Mega Blaziken ex B1 036
1 Heatmor B1 044
1 Castform Sunny Form B3 024
2 Professor's Research P-A 007
2 Copycat B1 225
1 Cyrus A2 150
2 Flame Patch B1 217
2 Rare Candy A3 144
2 Poké Ball P-A 005
1 Field Blower B3 147
1 Rocky Helmet A2 148
1 Hiking Trail B2b 069
"#),
    ("t-hydreigon", "decks/screen/opponents/t-hydreigon.txt", "18688bd9ab09f2638538006590767a5750abe763572c0fb636c47eec93155f3b", r#"Energy: Darkness
2 Deino B1 155
2 Hydreigon B1 157
1 Bombirdier B3 115
1 Mega Absol ex B1 151
2 Professor's Research P-A 007
2 Copycat B1 225
1 Cyrus A2 150
1 Sabrina A1 225
2 Poké Ball P-A 005
2 Rare Candy A3 144
2 Lucky Ice Pop B2 145
2 Deceptive Needle B4 148
"#),
    ("t-lucario", "decks/screen/opponents/t-lucario.txt", "76ad71c4d932da51fddc8c3082f184f8012c86e1f1e15c5858e055190560f634", r#"Energy: Fighting
2 Riolu B3 079
2 Mega Lucario ex B3 081
1 Lucario A2 092
1 Bonsly B3 078
1 Hitmonlee A1 154
2 Professor's Research P-A 007
2 Copycat B1 225
1 Korrina B3 149
1 Pokémon Center Lady A2b 070
1 Cyrus A2 150
2 Poké Ball P-A 005
1 Field Blower B3 147
1 X Speed P-A 002
1 Protective Poncho B2 147
1 Arena of Antiquity B3 154
"#),
    ("t-sceptile", "decks/screen/opponents/t-sceptile.txt", "fe0b7fc4de2f9dff0268a65d30dd39bfd5b73e7e5115b48e59f3975777018cd2", r#"Energy: Grass
2 Caterpie B3b 001
2 Metapod B3b 002
2 Butterfree B3b 003
1 Treecko B3 005
1 Grovyle B3 006
1 Mega Sceptile ex B3 008
2 Professor's Research P-A 007
1 Erika A1 219
1 Copycat B1 225
1 Sabrina A1 225
1 Cyrus A2 150
2 Quick-Grow Extract B1a 067
1 Leaf Cape A3 147
2 Fragrant Forest B3 153
"#),
    ("t-suicune", "decks/screen/opponents/t-suicune.txt", "639778c3cdc056130278fa13984b1bb1c508226032334d54b7a01a25d3187783", r#"Energy: Water
1 Frigibax B2a 034
1 Frigibax P-B 037
2 Baxcalibur B2a 036
2 Suicune ex A4a 020
1 Chien-Pao ex B2a 037
2 Professor's Research P-A 007
1 Team Rocket's Boss B4a 071
1 Pokémon Center Lady A2b 070
1 Copycat B1 225
2 Rare Candy A3 144
2 Poké Ball P-A 005
1 Field Blower B3 147
1 Inflatable Boat A4a 067
1 Giant Cape A2 147
1 Soothing Shore B4 154
"#),
    ("t-vespiquen", "decks/screen/opponents/t-vespiquen.txt", "8356844fd2d143a44c547356ff5a32b74977478fbb1f9fc2a716a7f2233f8255", r#"Energy: Grass
2 Combee B4 010
2 Vespiquen ex B4 011
2 Shuckle ex A4 021
1 Teal Mask Ogerpon ex B2 017
2 Professor's Research P-A 007
2 Copycat B1 225
1 Cyrus A2 150
1 Sabrina A1 225
2 X Speed P-A 002
1 Field Blower B3 147
2 Leaf Cape A3 147
2 Fragrant Forest B3 153
"#),
    ("t-weezing", "decks/screen/opponents/t-weezing.txt", "26cb869fe5f2c7cd79f8b974bf7667f802837bdb6ec9442db5360aef490ce5a1", r#"Energy: Darkness
2 Hoopa ex B4 103
2 Team Rocket's Koffing B4a 042
2 Team Rocket's Weezing ex B4a 043
1 Darkrai ex A2 110
2 Professor's Research P-A 007
2 Cyrus A2 150
2 Copycat B1 225
1 Mars A2 155
2 Poké Ball P-A 005
1 X Speed P-A 002
1 Field Blower B3 147
2 Deceptive Needle B4 148
"#),
    ("research/altaria", "decks/research/altaria.txt", "435a2bebc567ca8357696e400643fdc821cc36ae4765a7a16663fd4413a3bd7f", r#"Energy: Psychic
2 B1 196
1 B1 102
2 B1 184
2 B3a 020
2 B2b 040
1 A4a 059
2 P-A 007
2 B1 225
1 A1 225
2 P-A 005
1 B3 147
1 B3b 064
1 B2 153
"#),
    ("research/blaziken", "decks/research/blaziken.txt", "fb08470e8801e93ca4f459dcff42fd04d8bc63ff76aa984dbbc25ac1c527dd58", r#"Energy: Fire
2 B1 033
2 B1 036
1 B1 044
1 B3 024
2 P-A 007
2 B1 225
1 A2 150
2 B1 217
2 A3 144
2 P-A 005
1 B3 147
1 A2 148
1 B2b 069
"#),
    ("research/hydreigon", "decks/research/hydreigon.txt", "6ea0042236b4844458a1b2d0f0e6cefb4c50ce0148a38aded1162f4d27e935e9", r#"Energy: Darkness
2 B1 155
2 B1 157
1 B3 115
1 B1 151
2 P-A 007
2 B1 225
1 A2 150
1 A1 225
2 P-A 005
2 A3 144
2 B2 145
2 B4 148
"#),
    ("research/lucario", "decks/research/lucario.txt", "46a4820bc788b4fd9ac1d9491e62bf7123c467441e7e30012e42e8a70c91e3f3", r#"Energy: Fighting
2 B3 079
2 B3 081
1 A2 092
1 B3 078
1 A1 154
2 P-A 007
2 B1 225
1 B3 149
1 A2b 070
1 A2 150
2 P-A 005
1 B3 147
1 P-A 002
1 B2 147
1 B3 154
"#),
    ("research/sceptile", "decks/research/sceptile.txt", "7404c99e49161e68e7e2fe19025f63da9dd294c20dfa9fc608c742af97b25471", r#"Energy: Grass
2 B3b 001
2 B3b 002
2 B3b 003
1 B3 005
1 B3 006
1 B3 008
2 P-A 007
1 A1 219
1 B1 225
1 A1 225
1 A2 150
2 B1a 067
1 A3 147
2 B3 153
"#),
    ("research/suicune", "decks/research/suicune.txt", "7affe6530b8d096b2d81425380bbb92c303de84458bc2fd1ee0936c40f922633", r#"Energy: Water
1 B2a 034
1 P-B 037
2 B2a 036
2 A4a 020
1 B2a 037
2 P-A 007
1 B4a 071
1 A2b 070
1 B1 225
2 A3 144
2 P-A 005
1 B3 147
1 A4a 067
1 A2 147
1 B4 154
"#),
    ("research/vespiquen", "decks/research/vespiquen.txt", "fc3a0ffd1997f202ebe255390ae72ccb621369c6ac17ac72397471ca6be9c1ac", r#"Energy: Grass
2 B4 010
2 B4 011
2 A4 021
1 B2 017
2 P-A 007
2 B1 225
1 A2 150
1 A1 225
2 P-A 002
1 B3 147
2 A3 147
2 B3 153
"#),
    ("research/weezing", "decks/research/weezing.txt", "c322fe64d6052bf9c55875ecf8bebcf9460e819df19d21fc8a20a04ff7a79e9b", r#"Energy: Darkness
2 B4 103
2 B4a 042
2 B4a 043
1 A2 110
2 P-A 007
2 A2 150
2 B1 225
1 A2 155
2 P-A 005
1 P-A 002
1 B3 147
2 B4 148
"#),
];

/// A list added at run time through `KX_EXTRA_LISTS`: its name, the path as given, a 64-bit FNV-1a hash of the file's
/// bytes (hex; the laptop records the sha256 itself), the list, and what it was checked against (the repository and how
/// many protected lists it holds).
#[derive(Debug, Clone)]
pub struct ExtraList {
    pub name: String,
    pub path: String,
    pub fnv1a64: String,
    pub deck: crate::Deck,
    pub checked_against: String,
}

/// The 64-bit FNV-1a hash of `bytes` (stable across builds and machines; no crate needed).
pub fn fnv1a64(bytes: &[u8]) -> u64 {
    bytes.iter().fold(0xcbf2_9ce4_8422_2325u64, |h, b| (h ^ *b as u64).wrapping_mul(0x0000_0100_0000_01b3))
}

/// The protected folders under decks/: Dustin's brews and drafts (with their subfolders) and Dustin's own lists. A pilot is
/// never handed one of these lists (DESIGN.md section 9; the pool above holds none).
pub const PROTECTED: [&str; 2] = ["brews", "dustin"];

/// True if `path` lies under decks/brews or decks/dustin, as given or once resolved. Backslashes count as separators, and
/// the match ignores case, so a Windows path is caught too.
pub fn under_protected(path: &str) -> bool {
    let under = |p: &std::path::Path| {
        let parts: Vec<String> = p.components().map(|c| c.as_os_str().to_string_lossy().to_lowercase()).collect();
        parts.windows(2).any(|w| w[0] == "decks" && PROTECTED.contains(&w[1].as_str()))
    };
    let given = path.replace('\\', "/");
    under(std::path::Path::new(&given)) || std::fs::canonicalize(&given).map(|p| under(&p)).unwrap_or(false)
}

/// A list's cards as a sorted multiset of card ids.
fn card_ids(deck: &crate::Deck) -> Vec<String> {
    let mut ids: Vec<String> = deck.cards.iter().map(|c| c.get_id()).collect();
    ids.sort();
    ids
}

fn is_repository(root: &std::path::Path) -> bool {
    PROTECTED.iter().all(|f| root.join("decks").join(f).is_dir())
}

/// The repository whose decks/brews and decks/dustin the extra lists are checked against: `KX_REPO` if set (it must hold
/// both folders), else the first folder holding both above the build's engine directory, the working directory, or one of
/// the lists. (The harnesses' builds copy engine/ out of the repository, so the build's directory alone may not find it.)
pub fn find_repository(list_paths: &[&str]) -> Result<std::path::PathBuf, String> {
    if let Some(root) = std::env::var_os("KX_REPO") {
        let root = std::path::PathBuf::from(root);
        return if is_repository(&root) {
            Ok(root)
        } else {
            Err(format!("KX_EXTRA_LISTS: KX_REPO={} holds no decks/brews and decks/dustin to check the lists against", root.display()))
        };
    }
    let mut starts = vec![std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))];
    starts.extend(std::env::current_dir().ok());
    starts.extend(list_paths.iter().filter_map(|p| std::fs::canonicalize(p.replace('\\', "/")).ok()));
    for start in &starts {
        if let Some(root) = start.ancestors().find(|a| is_repository(a)) {
            return Ok(root.to_path_buf());
        }
    }
    Err(format!(
        "KX_EXTRA_LISTS: can't find the repository's decks/brews and decks/dustin to check the lists against (looked above {}, \
         the working directory and each list); set KX_REPO to the repository root",
        env!("CARGO_MANIFEST_DIR")
    ))
}

/// Every list under `repo`'s decks/brews (subfolders included) and decks/dustin: its path and cards. Refused if either
/// folder can't be read or holds no list. A .txt that doesn't read as a list (a note) is skipped: a copy of it couldn't be
/// loaded as an extra list either.
pub fn protected_lists(repo: &std::path::Path) -> Result<Vec<(String, Vec<String>)>, String> {
    fn walk(dir: &std::path::Path, files: &mut Vec<std::path::PathBuf>) -> Result<(), String> {
        let entries = std::fs::read_dir(dir).map_err(|e| format!("KX_EXTRA_LISTS: can't read {} to check the lists against: {e}", dir.display()))?;
        for entry in entries {
            let path = entry.map_err(|e| format!("KX_EXTRA_LISTS: can't read {}: {e}", dir.display()))?.path();
            if path.is_dir() {
                walk(&path, files)?;
            } else if path.extension().is_some_and(|x| x == "txt") {
                files.push(path);
            }
        }
        Ok(())
    }
    let mut lists = Vec::new();
    for folder in PROTECTED {
        let dir = repo.join("decks").join(folder);
        let mut files = Vec::new();
        walk(&dir, &mut files)?;
        files.sort();
        let before = lists.len();
        for file in files {
            let text = std::fs::read_to_string(&file).map_err(|e| format!("KX_EXTRA_LISTS: can't read {}: {e}", file.display()))?;
            // The deck parser panics on an unknown Energy type rather than erring: such a file is skipped too.
            if let Ok(Ok(deck)) = std::panic::catch_unwind(|| crate::Deck::from_string(&text)) {
                lists.push((file.display().to_string(), card_ids(&deck)));
            }
        }
        if lists.len() == before {
            return Err(format!("KX_EXTRA_LISTS: {} holds no list to check against; is {} the repository?", dir.display(), repo.display()));
        }
    }
    Ok(lists)
}

/// Parses `name=path;name=path` and reads each list, checking it against `repo`'s protected lists. Refused: a path under
/// decks/brews or decks/dustin, a list holding the same cards as one there (a copy anywhere else), an unreadable or
/// invalid list, a missing or repeated name. The variable reaches both seats, so the meta side must never get such a list.
pub fn parse_extra_lists_against(spec: &str, repo: &std::path::Path) -> Result<Vec<ExtraList>, String> {
    let entries: Vec<&str> = spec.split(';').map(str::trim).filter(|e| !e.is_empty()).collect();
    if entries.is_empty() {
        return Ok(Vec::new());
    }
    let mut lists: Vec<ExtraList> = Vec::new();
    let mut parsed = Vec::new();
    for entry in entries {
        let (name, path) = entry
            .split_once('=')
            .map(|(n, p)| (n.trim(), p.trim()))
            .filter(|(n, p)| !n.is_empty() && !p.is_empty())
            .ok_or_else(|| format!("KX_EXTRA_LISTS: '{entry}' is not name=path"))?;
        if under_protected(path) {
            return Err(format!(
                "KX_EXTRA_LISTS: {path} is under decks/brews or decks/dustin; a brew's list or one of Dustin's is never handed to a pilot"
            ));
        }
        if parsed.iter().any(|(n, _)| *n == name) {
            return Err(format!("KX_EXTRA_LISTS: the name '{name}' is given twice"));
        }
        parsed.push((name, path));
    }
    let protected = protected_lists(repo)?;
    let checked_against = format!("{}: {} lists under decks/brews and decks/dustin", repo.display(), protected.len());
    for (name, path) in parsed {
        let bytes = std::fs::read(path.replace('\\', "/")).map_err(|e| format!("KX_EXTRA_LISTS: {path}: {e}"))?;
        let text = String::from_utf8_lossy(&bytes);
        let deck = crate::Deck::from_string(&text).map_err(|e| format!("KX_EXTRA_LISTS: {path}: {e}"))?;
        if let Some((copy_of, _)) = protected.iter().find(|(_, ids)| *ids == card_ids(&deck)) {
            return Err(format!(
                "KX_EXTRA_LISTS: {path} holds the same cards as {copy_of} (under decks/brews or decks/dustin); a brew's list or one of Dustin's is never handed to a pilot"
            ));
        }
        lists.push(ExtraList {
            name: name.to_string(),
            path: path.to_string(),
            fnv1a64: format!("{:016x}", fnv1a64(&bytes)),
            deck,
            checked_against: checked_against.clone(),
        });
    }
    Ok(lists)
}

/// `parse_extra_lists_against` the repository `find_repository` finds (none is needed for an empty spec).
pub fn parse_extra_lists(spec: &str) -> Result<Vec<ExtraList>, String> {
    let paths: Vec<&str> = spec.split(';').filter_map(|e| e.split_once('=').map(|(_, p)| p.trim())).collect();
    if paths.is_empty() {
        return parse_extra_lists_against(spec, std::path::Path::new(""));
    }
    parse_extra_lists_against(spec, &find_repository(&paths)?)
}

/// The lists in `KX_EXTRA_LISTS`, read once per process (none if it is unset).
pub fn extra_lists() -> &'static Result<Vec<ExtraList>, String> {
    static LISTS: std::sync::OnceLock<Result<Vec<ExtraList>, String>> = std::sync::OnceLock::new();
    LISTS.get_or_init(|| match std::env::var("KX_EXTRA_LISTS") {
        Ok(spec) => parse_extra_lists(&spec),
        Err(_) => Ok(Vec::new()),
    })
}

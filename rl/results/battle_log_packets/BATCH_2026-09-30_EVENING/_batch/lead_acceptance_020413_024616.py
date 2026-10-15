"""Record independent lead checks after reading the complete assigned packets."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
checks = {
    '020413000': {
        'scope': 'Complete seventeen-turn 326.96-second Auto AI battle, setup through terminal Fantasia Force knockout and named Defeat',
        'lead_checks': 'Read the complete narrative, all-turn coverage, source, summary and uncertainties. Independently inspected native25s setup;140s ordinary Grindcore30 and coin text;113.60s zero-heads/one-tail result;230.50s Diantha90-heal/two-Energy-discard text;242s post-Diantha settled190HP and five Psychic;309/312s final pre-attack board (Mega5, Bramblin2, Mimikyu4) and110 damage;315/316s settled post-attack board (6/4/4) and Crobat removal;316.50s terminal point-circle transition;326.50s named Defeat,17turns,2-3 and440 damage. The separate normal turn17 attachment was not established; narrowed that wording and preserved original worker documents. See LEAD_CLARIFICATION.md. Bounded lead checks supplement the worker complete visual review.',
        'lead_evidence': ['native/t0025.00.jpg','native/t0113.60.jpg','native/t0140.00.jpg','native/t0230.50.jpg','native/t0242.00.jpg','native/t0309.00.jpg','native/t0312.00.jpg','native/t0315.00.jpg','native/t0316.00.jpg','native/t0316.50.jpg','native/t0326.50.jpg','LEAD_CLARIFICATION.md'],
        'outcome': 'owner_loss', 'final_points': {'owner':2,'opponent':3},
        'result_display': 'Loss 2-3 circles; opponent received 4 awarded points',
        'owner_visible_core': 'Guzzlord ex / Crobat ex / Mega Gengar ex',
        'opponent': 'AI Mega Gardevoir ex & Mimikyu ex Deck (Deluxe Pack: Mega)',
        'last_turn':17,
        'useful_finding':'Wynaut delays Guzzlord through its attack tax. Mimikyu blocks the first Grindcore damage while a tails flip is still shown. Diantha heals without clearing Poison; free Psychic retreats under Peculiar Plaza clear it. The final exposed100-HP Crobat falls to110 while Mega Gengar remains two Energy short. Settled final Energy gain is three; no extra normal attachment or rule defect is established.',
        'limitations':'Hidden decks/draws, cosmetic IDs, clock basis and separate normal turn17 attachment remain unknown. The Mega Gengar survival alternative is conditional, not a proven win.'
    },
    '024616000': {
        'scope':'Complete ten-turn 192.775-second Auto AI battle, setup through zero-Energy Wynaut knockout and named Defeat',
        'lead_checks':'Read full narrative, source, all-turn coverage, summary and uncertainties. Independently inspected exact-time retained frames in LEAD_CONTACT.jpg/LEAD_CONTACT_2.jpg:13s opening Victini and Auto checked;87s ordinary Numel bench placement;93s Victini two Fire and Gholdengo90HP;128s unchecked Auto with End Turn and Mega170HP;133s Auto checked again with Bounded Field in play;141s two recovered Fire settled before normal attachment;152s Spending Rush160;162.50s Mega Kaboom Weakness180 while owner has10HP;176s Wynaut zero-Energy Stompy Jammer printed10;178s Mega0;184s explicit+3 award;192.74s named Defeat and Card of Game with no numeric statistics. Bounded independent checks supplement the worker complete visual review.',
        'lead_evidence':['LEAD_CONTACT.jpg','LEAD_CONTACT_2.jpg','native/t0013.00.jpg','native/t0087.00.jpg','native/t0093.00.jpg','native/t0128.00.jpg','native/t0133.00.jpg','native/t0141.00.jpg','native/t0152.00.jpg','native/t0162.50.jpg','native/t0176.00.jpg','native/t0178.00.jpg','native/t0184.00.jpg','native/t0192.74.jpg'],
        'outcome':'owner_loss','final_points':{'owner':2,'opponent':3},
        'result_display':'Loss 2-3 circles; opponent received 5 awarded points',
        'owner_visible_core':'Victini / Pansear / Mega Camerupt ex',
        'opponent':'AI Mega Scizor ex & Gholdengo ex Deck (Deluxe Pack: Mega)',
        'last_turn':10,
        'useful_finding':'Spending Rush knocks out Pansear, then Victini, and leaves Mega at10HP. Two Flame Patch recover Victini Fire. Bounded Field is played during Auto off and excludes Mega attackers; Kaboom displays180 with ordinary weakness. Wynaut then uses its zero-Energy10 attack for the three-point Mega knockout.',
        'limitations':'Hidden decks, exact toggle instants, input intent, cosmetic IDs and filename clock basis remain unknown. No numerical results statistics are shown. Manual Stadium play is not attributed to Auto policy.'
    }
}
for stamp, data in checks.items():
    video = f'20261001_{stamp}_iOS.MP4'
    packet = root / 'Recording_QA' / (Path(video).stem + '_auto_sol')
    source = json.loads((packet / 'SOURCE.json').read_text(encoding='utf-8-sig'))
    assert source['ladder_eligible'] is False
    for ref in data['lead_evidence']:
        assert (packet / ref).is_file(), ref
    data.update(accepted=True, decision='accepted_full_battle_review', source_video=video, source_sha256=source['sha256'], first_pass=f'gpt-6.1-sol/high /root/auto_{stamp[:6]}', unreviewed_intervals=[], material_unresolved=[], ladder_eligible=False, ladder_action='No Ladder Log entry; owner-declared Auto AI game', astra_consulted=False, astra_reason='Source checks resolved consequential questions; no additional consultation required')
    target = packet / 'LEAD_ACCEPTANCE.json'
    assert not target.exists(), 'Do not overwrite acceptance'
    target.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(video)

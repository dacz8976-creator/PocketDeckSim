"""Constants of the Gemini finished-game test (frozen-8). No other file defines them."""
SEED_BASE = 25_103_000_000
def seed(cell, k): assert 0 <= cell < 16 and 0 <= k < 100; return SEED_BASE + 100 * cell + k
def cell_of(deck, lst, policy, seat): return 8 * deck + 4 * lst + 2 * policy + seat
def cell_bits(cell): return {'deck': (cell >> 3) & 1, 'list': (cell >> 2) & 1, 'policy': (cell >> 1) & 1, 'seat': cell & 1}
DECKS = {0: 'decks/dustin/09-mega-manectric-heliolisk.txt', 1: 'decks/dustin/11-archaludon-haxorus-dragonair.txt'}  # A fast (0), B setup (1)
LISTS = {0: 'decks/screen/opponents/t-lucario.txt', 1: 'decks/screen/opponents/t-suicune.txt'}  # list 1 (0), list 2 (1)
POLICIES = {0: 'km3', 1: 'kx3'}
STAGE1_K = 80; RESTART_K = tuple(range(81, 90)); DEV_K = tuple(range(90, 100))
STAGE1_ORDER = (0, 15, 6, 9, 3, 12, 1, 2, 4, 5, 7, 8, 10, 11, 13, 14)
BOT_TIMEOUT_MS = 2_700_000; DECIDE_MARGIN_S = 120; SHADOW_RESERVE_S = 600; VERTEX_TIMEOUT_S = 1260
GAME_WALL_S = 14_400                    # a game past 4 h is killed, classed infra, and replayed
PAUSE_GAP_S = 60                        # a gap over this inside an arm (heartbeat or pause marker) classes the arm infra; replayed
STOP_AT_UTC = '2026-11-28T05:59:00Z'    # no new deal starts after this; stop_reason 'stop_date'
MAX_TRIES = 3; RETRY_WAITS_S = (150, 300); RETRY_WINDOW_S = 600   # only HTTP 429 and transport errors are retried
CALL_CAP = 75                           # stage 1: judge DECISIONS per game, not tries; fallback (d) fires at the first intervention point after the 75th judge decision; earlier fallbacks do not count toward the 75
LISTER_LIMITS = {'max_plans': 2000, 'max_nodes': 200000, 'max_steps': 30}; LISTER_HANG_S = 600
def lister_mem_rule(max_vmhwm_kb): return min(3 * 2**30, max(2**30, 3 * 1024 * max_vmhwm_kb))
LISTER_MEM_BYTES = None                 # A2 sets it once: lister_mem_rule(largest VmHWM kB on the 92 and the LS dumps)
SEARCH_SEED = 0x5EED_0001
SHADOW_FEED = 'fallback'                # fixed: the shadow is asked only at setup and fallback points
POOL_SHA256 = {'t-lucario': '76ad71c4d932da51fddc8c3082f184f8012c86e1f1e15c5858e055190560f634',
               't-suicune': '639778c3cdc056130278fa13984b1bb1c508226032334d54b7a01a25d3187783'}
KX3_CODE = 'kx3'; KX3_CANONICAL = 'kx3_r16_c12_z2_real_t0'
RAYON_THREADS_BUILD = 2; RAYON_THREADS_LAPTOP = 8   # this job; the laptop's gates and stage 1
LEDGER_LABEL = 'gemini-vertex:gemini-4-argon'
BOOT_DRAWS = 10_000; BOOT_SEED = 20261030; FLIP_DRAWS = 100_000; SIGNFLIP_SEED = 20261031
MIN_PAIRS = 64; FALLBACK_LIMIT = 0.10; DROP_LIMIT = 0.05; GO_MIN_N = 80; N_MAX = 128
SHADOW_ENV_KEEP = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR', 'RAYON_NUM_THREADS')
FORBIDDEN_ENV = ('KX_EXTRA_LISTS', 'PDL_DB', 'PG_DUMP')   # plus every name starting VERTEX_ for anything but the judge bot
def pid_prefix(seed_, cell, arm): return f'{seed_}-c{cell:02d}-{arm}'   # judge pid = f'{prefix}-p{ply}'

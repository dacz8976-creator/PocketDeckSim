"""Counter-based random streams for the setup tester.

Each random choice (shuffle, search pick, coin, clock) comes from its own stream, keyed by the deal's seed, a purpose
name and a running count, so two versions of a deck that play the same way draw the same numbers
(SPEC.md "Pairing"). Standard library only; the generator is splitmix64.
"""
M64 = (1 << 64) - 1
GOLD = 0x9E3779B97F4A7C15

PURPOSES = {'shuffle': 1, 'swap': 2, 'reshuffle': 3, 'search': 4, 'coin': 5, 'return': 6, 'clock': 7,
            'glimmora': 8, 'mesagoza': 9, 'bootstrap': 10, 'sightseer': 11, 'comm': 12, 'lisia': 13, 'copycat': 14}


def mix(x):
    x = (x + GOLD) & M64
    x = ((x ^ (x >> 30)) * 0xBF58476D1CE4E5B9) & M64
    x = ((x ^ (x >> 27)) * 0x94D049BB133111EB) & M64
    return x ^ (x >> 31)


def stream_key(seed, purpose):
    return mix(mix(seed) ^ (PURPOSES[purpose] * GOLD & M64))


class Stream:
    """below(k) is uniform on 0..k-1 (bias under 2^-50 for k under 2^14); unit() is uniform on [0, 1)."""
    __slots__ = ('key', 'n')

    def __init__(self, seed, purpose):
        self.key = stream_key(seed, purpose)
        self.n = 0

    def raw(self):
        self.n += 1
        return mix(self.key + self.n * GOLD)

    def below(self, k):
        return (self.raw() * k) >> 64

    def unit(self):
        return self.raw() / 18446744073709551616.0

    def shuffle(self, items):
        for i in range(len(items) - 1, 0, -1):
            j = self.below(i + 1)
            items[i], items[j] = items[j], items[i]

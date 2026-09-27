from math import comb, lgamma, exp, log


def binom_two_sided(k, n, p=0.5):
    """exact two-sided binomial test (sum of probabilities <= observed)"""
    if n == 0:
        return 1.0
    pk = [comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(n + 1)]
    obs = pk[k]
    return min(1.0, sum(x for x in pk if x <= obs * (1 + 1e-9)))


def fisher_two_sided(a, b, c, d):
    """2x2 table [[a,b],[c,d]] exact two-sided Fisher test"""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    def p(x):
        return comb(r1, x) * comb(r2, c1 - x) / comb(n, c1)
    obs = p(a)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= obs * (1 + 1e-9)))


def test(w, b, W=140, B=140):
    """worse count w of W, better count b of B: exact test on the 2x2 table (equal sampling)."""
    return fisher_two_sided(w, W - w, b, B - b)

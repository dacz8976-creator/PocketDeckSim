from vsk_stats import binom_two_sided, fisher_two_sided, test
print("analyst P2 15/7 binom", round(binom_two_sided(15, 22), 3), "fisher vs 140s", round(test(15, 7), 3))
print("analyst P2 vs P3 fisher [[15,7],[18,25]]", round(fisher_two_sided(15, 7, 18, 25), 3))
print("analyst P5 13/4 binom", round(binom_two_sided(13, 17), 3), "fisher", round(test(13, 4), 3))
print("analyst P6 27/10 binom", round(binom_two_sided(27, 37), 3), "fisher", round(test(27, 10), 3))
print("analyst 1c->1c 38/15 binom", round(binom_two_sided(38, 53), 4), "fisher", round(test(38, 15), 4))
print("mine 1c->1c 37/14 binom", round(binom_two_sided(37, 51), 4), "fisher", round(test(37, 14), 4))
print("Bonferroni threshold for 40 tests:", 0.05 / 40)

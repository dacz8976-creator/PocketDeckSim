import re
s = "Evolves 120 HP; uses Thieving Incisors moving 1 Darkness from owner active Glimmet to Raticate"
rx = r'moves?\s+(?:one|1|an?|\d+)\s+(\w+)\s+(?:Energy\s+)?from\s+(?:the\s+|owner\s+|your\s+|Active\s+|Benched?\s+)*(.+?)\s+to\s'
print("match:", re.search(rx, s, re.I))
s2 = s.replace("moving", "moves")
m = re.search(rx, s2, re.I)
print("with 'moves':", m and m.groups())

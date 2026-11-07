"""Dvar name -> 64-bit hash for the full-game cod.exe (Steam 'Call of Duty HQ', build dumped 2026-11-07).
Lowercase FNV-1a-64 variant, prime 0x10000000233, initial state chosen by the FIRST character of the name.
Seeds are known for the letters in letter_seeds.json only (empirically recovered)."""
import json, os
M = (1 << 64) - 1; P = 0x10000000233
SEEDS = {k: int(v, 16) for k, v in json.load(open(os.path.join(os.path.dirname(__file__), 'letter_seeds.json'))).items()}
def dvar_hash(name):
    b = name.lower().encode()
    h = SEEDS[chr(b[0])]
    for c in b: h = ((h ^ c) * P) & M
    return h
if __name__ == '__main__':
    import sys
    for n in sys.argv[1:]: print(n, '0x%016X' % dvar_hash(n))

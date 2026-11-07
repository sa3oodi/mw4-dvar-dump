# COD (full game) DVAR dump

Dvar (console variable) dump of the full-release Call of Duty PC build (Steam "Call of Duty HQ", `cod.exe`),
modeled on [bradselph/COD-MW4-Beta-DVAR-Dump](https://github.com/bradselph/COD-MW4-Beta-DVAR-Dump) but taken from the
full game instead of the beta.

Dumped 2026-11-07 from the live process: once at the main menu and once in an online match.

## Status

| | |
|---|---|
| Dvars in the runtime hash table | **17,830** |
| Names recovered | **3,116** (17.5%) |
| Hash-only (name unknown) | 14,714 |

Names are stored in the game only as 64-bit hashes, so each name had to be recovered by hashing candidate names and
matching them against the live table. Anything not matched stays hash-only. Coverage is limited by available wordlists,
not by missing data: every dvar's type, flags, values and limits are present.

| type | total | named |
|---|---|---|
| bool | 7572 | 928 |
| float | 5437 | 979 |
| int | 3254 | 869 |
| string | 627 | 120 |
| enum | 266 | 72 |
| vec2 / vec3 / vec4 | 96 / 114 / 74 | 42 / 20 / 32 |
| color | 29 | 25 |
| type6 / 7 / 8 / 12 / 13 / 14 (undecoded) | 262 / 1 / 69 / 16 / 6 / 7 | 0 / 0 / 11 / 16 / 1 / 1 |

## Files

| File | Contents |
|---|---|
| `dvars.json` | Every dvar: hash, name (or `null`), `seen`, type, flags, current/default value, min/max, enum options, raw bytes |
| `dvars.csv` | Same data, flat |
| `dvars.txt` | Named dvars only, sorted: `name \| type \| flags \| default \| range/options` |
| `dvar_hashes.txt` | `hash => name` for recovered names |
| `unresolved_hashes.txt` | Hash, type, flags, default for dvars without a name |
| `dvar_hash.py`, `letter_seeds.json` | Name → hash function and the per-letter seeds it needs |
| `report.md` | Counts |

`seen` is `both` (16,815), `menu_only` (1,011) or `match_only` (4). The menu table is nearly a superset of the match
table. Menu-only dvars are mostly AI, vehicle and `g_*` dvars.

## Hash function

Dvar names are hashed with a lowercase FNV-1a-64 variant:

```python
M = (1 << 64) - 1; P = 0x10000000233
def dvar_hash(name):
    b = name.lower().encode()
    h = SEEDS[chr(b[0])]          # initial state depends on the FIRST character
    for c in b:
        h = ((h ^ c) * P) & M
    return h
```

The per-letter seeds were recovered empirically (not derived from a formula) and exist for **19 letters**:
`a b c d f g h i l m o p r s t u v w x`. Seeds for `e j k n q y z`, digits and `_` are unknown, so names starting
with those cannot be recovered yet. See `letter_seeds.json`.

Check: `dvar_hash("cg_fov") == 0xDF1DC712C4A91588`, which matches its entry in the live table.

## Record layout (runtime node)

Reverse-engineered from the live hash table (20,702 buckets, chained nodes). Offsets are from the node start:

| Offset | Meaning |
|---|---|
| `+0x00` | 64-bit name hash |
| `+0x08` | next node in bucket chain |
| `+0x10` | flags (u32). Raw values only. Bit names are not verified |
| `+0x15` | type byte |
| `+0x18` | domain (16 bytes): float/int `min,max`; enum: `count` + pointer to string table |
| `+0x28` | current value (16 bytes) |
| `+0x38` | default value (16 bytes) |

Type byte: `0` bool, `1` float, `2/3/4` vec2/3/4, `5` int, `9` enum, `10` string, `11` color.
Types `6, 7, 8, 12, 13, 14` are not decoded and appear as `typeN`.

## Method

1. Memory dump of the running game (Windows Task Manager, "Create memory dump file"). `cod.exe` on disk is packed
   (entropy 7.43), so a static analysis of the file is not enough. No debugger was attached.
2. Locate the dvar lookup (found through the game's automation RPC `dvar_get` handler), which gave the table address and
   bucket function.
3. Read the whole table out of the dump.
4. Identify the hash function by inverting FNV-1a: for known names, compute the seed each (name, hash) pair implies and
   look for seeds shared by many names.
5. Recover names with wordlists (strings from the game, other CoD dvar lists, script dumps) plus a meet-in-the-middle
   search over word combinations.

## Limitations

- **Names:** 82.5% are hash-only. More names need more wordlists; a dvar list from the same build would help most.
- **Flags:** raw numbers only.
- **Types:** six type codes are undecoded.
- **Coverage:** tables from two moments (menu and one match). Dvars registered at other times may be missing.
- **Case:** generated names are lowercase because hashing is case-insensitive. Original capitalization is unknown for
  those.
- Names that came from wordlists can in principle be wrong if two names collide on a 64-bit hash. This is very unlikely.

## Notes

- This repo contains only dvar metadata (names, hashes, types, values), no game code, assets or the dumps themselves.
- Taking the dump touches the game process memory. Attaching a debugger to this game closes it (anti-cheat), and
  memory reads can carry ban risk, so do this at your own risk and not on an account you can't afford to lose.
- For research and modding reference only.

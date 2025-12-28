from constants import RANKS

def rank_from_xp(xp: int) -> str:
    r = RANKS[0][0]
    for name, need in RANKS:
        if xp >= need:
            r = name
    return r

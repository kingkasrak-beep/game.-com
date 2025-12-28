RANKS = [
    ("سرباز تازه کار", 0),
    ("سرباز خبره", 10),
    ("گروهبان تازه کار", 30),
    ("گروهبان خبره", 80),
    ("ستوان دوم", 150),
    ("ستوان اول", 300),
    ("سرگرد", 600),
    ("سرهنگ", 1200),
    ("سپهبد", 5000),
    ("ارتشبد", 15000)
]

def calculate_rank(xp: int):
    current = RANKS[0][0]
    for rank, need in RANKS:
        if xp >= need:
            current = rank
    return current

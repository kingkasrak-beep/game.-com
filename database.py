import sqlite3

conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    faction TEXT,
    city TEXT,
    money INTEGER,
    xp INTEGER,
    rank TEXT,
    title TEXT,
    position TEXT,
    honors INTEGER,
    registered INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    user_id INTEGER,
    item TEXT,
    count INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS income_log (
    user_id INTEGER,
    count INTEGER
)
""")

conn.commit()


def is_registered(user_id: int) -> bool:
    cursor.execute("SELECT registered FROM users WHERE user_id=?", (user_id,))
    r = cursor.fetchone()
    return bool(r and r[0] == 1)

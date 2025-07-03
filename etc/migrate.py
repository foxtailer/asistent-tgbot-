import sqlite3


old = '/home/nami/git/asistent-tgbot-/bot_db.db'
new = '/home/nami/git/asistent-tgbot-/new_db.db'

source_conn = sqlite3.connect(old)
target_conn = sqlite3.connect(new)

source_conn.execute("PRAGMA foreign_keys = ON;")
target_conn.execute("PRAGMA foreign_keys = ON;")

source_cur = source_conn.cursor()
target_cur = target_conn.cursor()

source_cur.execute("SELECT * FROM Yaroslav")

# id, eng, rus, example, day,, lvl
for row in source_cur:
    target_cur.execute("INSERT INTO EN_WORD (word) VALUES (?)", (row[1],))
    en_id = target_cur.lastrowid
    target_cur.execute("INSERT INTO RU_WORD (word) VALUES (?)", (row[2],))
    ru_id = target_cur.lastrowid
    target_cur.execute("INSERT INTO EN_EX (word, text) VALUES (?, ?)", (en_id, row[3]))
    ex = target_cur.lastrowid
    target_cur.execute("INSERT INTO dict (user, date, ru, en) VALUES (?, ?, ?, ?)", (1, row[4], ru_id, en_id))
    target_cur.execute("INSERT INTO examples (user, ex, en) VALUES (?, ?, ?)", (1, ex, en_id))
    target_cur.execute("INSERT INTO progress (user, lvl, en) VALUES (?, ?, ?)", (1, 0, en_id))

target_conn.commit()

source_conn.close()
target_conn.close()
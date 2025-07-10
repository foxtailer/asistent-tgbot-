import sqlite3


old = '/home/zoy/git/asistent-tgbot-/bot_db.db'
new = '/home/zoy/git/asistent-tgbot-/new_db.db'

source_conn = sqlite3.connect(old)
target_conn = sqlite3.connect(new)

source_conn.execute("PRAGMA foreign_keys = ON;")
target_conn.execute("PRAGMA foreign_keys = ON;")

source_cur = source_conn.cursor()
target_cur = target_conn.cursor()

source_cur.execute("SELECT * FROM Yaroslav")

target_cur.execute("insert OR IGNORE into users (tg_id, name) values (?, ?)", (123, "Yaroslav3"))
user_id = target_cur.lastrowid
target_cur.execute("insert OR IGNORE into users (tg_id, name) values (?, ?)", (124, "Yaroslav4"))
target_cur.execute("insert OR IGNORE into users (tg_id, name) values (?, ?)", (125, "Yaroslav5"))

# id, eng, rus, example, day, lvl
i = 0
for row in source_cur:
    i += 1
    target_cur.execute("INSERT INTO EN_WORD (word) VALUES (?)", (row[1],))
    en_id = target_cur.lastrowid

    target_cur.execute("UPDATE users SET words = ? WHERE id = ?", (i, user_id))

    target_cur.execute("INSERT or ignore INTO RU_WORD (word) VALUES (?)", (row[2],))
    ru_id = target_cur.lastrowid
    if target_cur.rowcount != 1:
        target_cur.execute("SELECT id FROM RU_WORD WHERE word = ?", (row[2],))
        ru_id = target_cur.lastrowid

    target_cur.execute("INSERT or ignore INTO EN_EX (word, text) VALUES (?, ?)", (en_id, row[3]))
    ex_id = target_cur.lastrowid
    if target_cur.rowcount != 1:
        target_cur.execute("SELECT id FROM EN_EX WHERE text = ?", (row[3],))
        ex_id = target_cur.lastrowid

    # dont add native language in dict
    target_cur.execute("INSERT INTO dict (user, date, en) VALUES (?, ?, ?)", (1, row[4], en_id))
    target_cur.execute("INSERT INTO examples (user, ex, en) VALUES (?, ?, ?)", (1, ex_id, en_id))
    target_cur.execute("INSERT INTO progress (user, lvl, en) VALUES (?, ?, ?)", (1, 0, en_id))
    target_cur.execute("INSERT INTO links (user, ru, en) VALUES (?, ?, ?)", (1, ru_id, en_id))

target_conn.commit()

source_conn.close()
target_conn.close()
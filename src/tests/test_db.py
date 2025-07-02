def test_insert_and_query(in_memory_db):
    cur = in_memory_db.cursor()
    cur.execute("INSERT INTO example (name) VALUES (?)", ("Alice",))
    in_memory_db.commit()

    cur.execute("SELECT id, name FROM example WHERE name = ?", ("Alice",))
    row = cur.fetchone()
    assert row[1] == "Alice"
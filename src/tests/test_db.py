def test_insert_and_query(in_memory_db):
    in_memory_db.execute("INSERT INTO example (name) VALUES (?)", ("Alice",))
    in_memory_db.commit()

    assert row[1] == "Alice"
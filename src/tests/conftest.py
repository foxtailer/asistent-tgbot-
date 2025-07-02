import pytest
import sqlite3

@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(":memory:")
    # You can create tables here if you want

    yield conn
    conn.close()
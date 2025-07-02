import sqlite3

import pytest

from src.services.db_functions import init_db


@pytest.fixture
def in_memory_db():
    conn = sqlite3.connect(":memory:")
    init_db(conn, language=['EN', 'JA'])
    yield conn
    conn.close()

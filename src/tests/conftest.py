import aiosqlite

import pytest

from src.services.db_functions import init_db


@pytest.fixture
async def in_memory_db_conn():
    conn = await aiosqlite.connect(":memory:")
    await init_db(conn, language=['EN', 'RU'])
    yield conn
    await conn.close()

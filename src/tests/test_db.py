from datetime import date

import pytest
import aiosqlite

from src.services.db_functions import add_to_db, init_db
from src.services.types import WordRow


@pytest.mark.asyncio
async def test_add_to_db():
    conn = await aiosqlite.connect(":memory:")
    await init_db(conn, language=['EN', 'RU'])

    data = [WordRow(
        language=('EN', 'RU'),
        word='test',
        trans='тест',
        date=date.today().strftime('%Y-%m-%d'),
        example='Test there.'
    )]

    await conn.execute("INSERT INTO user (tg_id, name) VALUES (?, ?)",
                        (111, 'Name'))
    await conn.commit()
    await add_to_db(111, data, conn)

    async with conn.execute("SELECT * FROM EN_WORD") as cursor:
        en_word_row = await cursor.fetchall()
        assert len(en_word_row) == 1
        assert en_word_row[0] == (1, 'test', None, None)

    await conn.close()
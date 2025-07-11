from datetime import date, timedelta

import pytest
import aiosqlite

from src.services import db_functions
from src.services.types_ import WordRow, Word


@pytest.mark.asyncio
async def test_add_to_db():
    conn = await aiosqlite.connect(":memory:")
    #conn = await aiosqlite.connect("/home/zoy/git/asistent-tgbot-/new_db.db")
    await db_functions.init_db(conn, language=['EN', 'RU'])

    data = WordRow(**{
        "languages": ('EN', 'RU'),
        "words": ((Word(**{"text": "cat", "language": 'EN', "examples":( "Nice little cat.",)}),),
                  (Word(**{"text": 'кот', "language": 'RU'}),)
        ),
        "date": date.today().strftime('%Y-%m-%d'),
    })

    await db_functions.check_user(123, 'Name', conn)
    await conn.commit()
    await db_functions.add_to_db(123, data, conn)

    async with conn.execute("SELECT * FROM EN_WORD") as cursor:
        en_word_row = await cursor.fetchall()
        assert len(en_word_row) == 1
        assert en_word_row[0] == (1, 'cat', None, None)

    async with conn.execute("SELECT * FROM RU_WORD") as cursor:
        en_word_row = await cursor.fetchall()
        assert len(en_word_row) == 1
        assert en_word_row[0] == (1, 'кот', None, None)

    async with conn.execute("SELECT en FROM dict WHERE user=1") as cursor:
        words = await cursor.fetchone()
        assert words[0] == 1

    async with conn.execute("SELECT en, ru FROM links WHERE user=1") as cursor:
        words = await cursor.fetchone()
        assert words == (1, 1)

    # Add one more time
    next_day = date.today() + timedelta(days=1)
    next_day_str = next_day.strftime('%Y-%m-%d')
    data.date = next_day_str
    await db_functions.add_to_db(123, data, conn)

    async with conn.execute("SELECT * FROM EN_WORD") as cursor:
        en_word_row = await cursor.fetchall()
        assert len(en_word_row) == 1
        assert en_word_row[0] == (1, 'cat', None, None)

    async with conn.execute("SELECT en FROM dict WHERE user=1") as cursor:
        words = await cursor.fetchone()
        assert words[0] == 1

    async with conn.execute("SELECT date FROM dict WHERE user=1 and en=1") as cursor:
        words = await cursor.fetchone()
        assert words[0] == date.today().strftime('%Y-%m-%d')

    async with conn.execute("SELECT * FROM links WHERE user=1") as cursor:
        words = await cursor.fetchall()
        assert len(words) == 1

    await conn.close()

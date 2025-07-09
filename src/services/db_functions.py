import random
from collections import defaultdict

from src.services.variables import ALLOWED_LANGUAGES
from src.services.types_ import WordRow, Word


async def init_db(conn, language: list[str]):
    print(f"Connecting to database at ..")

    try:
        await conn.execute("PRAGMA foreign_keys = ON")
        print("Creating tables if not exist...")

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL,
                name TEXT,
                args_ INTEGER DEFAULT 0
            )
        """)

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS dict (
                user INTEGER REFERENCES user(id),
                date TEXT NOT NULL DEFAULT (DATETIME('now'))
            )
        """)

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS examples (
                user INTEGER REFERENCES user(id),
                ex INTEGER
            )
        """)

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS progress (
                user INTEGER REFERENCES user(id),
                lvl INTEGER DEFAULT 0
            )
        """)

        for lang in language:

            if lang not in ALLOWED_LANGUAGES:
                raise ValueError(f"Invalid language: {lang}")
            
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_WORD (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    cefr TEXT,
                    freq INTEGER
                )
            """)

            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_SYN (
                    word INTEGER,
                    syn INTEGER,
                    FOREIGN KEY (word) REFERENCES {lang}_WORD(id),
                    FOREIGN KEY (syn) REFERENCES {lang}_WORD(id),
                    PRIMARY KEY (word, syn)
                )
            """)

            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_ANT (
                    word INTEGER,
                    ant INTEGER,
                    FOREIGN KEY (word) REFERENCES {lang}_WORD(id),
                    FOREIGN KEY (ant) REFERENCES {lang}_WORD(id),
                    PRIMARY KEY (word, ant)
                )
            """)

            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_EX (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word INTEGER NOT NULL,
                    text TEXT,
                    FOREIGN KEY (word) REFERENCES {lang}_WORD(id)
                )
            """)

            await conn.execute(f"""
                ALTER TABLE progress ADD COLUMN {lang.lower()} INTEGER;
            """)
            await conn.execute(f"""
                ALTER TABLE dict ADD COLUMN {lang.lower()} INTEGER;
            """)
            await conn.execute(f"""
                ALTER TABLE examples ADD COLUMN {lang.lower()} INTEGER;
            """)

        await conn.commit()
        print("Tables created or already exist.")

    except aiosqlite.Error as e:
        print(f"SQLite error: {e}")


async def add_to_db(tg_id: int, args_: list[WordRow], conn) -> bool:
    try:    
        async with conn.execute("SELECT id FROM user WHERE tg_id = ?", (tg_id,)) as cursor:
            row = await cursor.fetchone()
            if not row:
                print("User not found")
                return False
            user_id = row[0]

        for w in args_:
            cursor = await conn.execute(
                f"INSERT INTO {w.language[0]}_WORD (word) VALUES (?)", 
                (w.word.text,))
            w_id = cursor.lastrowid

            cursor = await conn.execute(
                f"INSERT INTO {w.language[1]}_WORD (word) VALUES (?)",
                (w.trans[0].text,))
            t_id = cursor.lastrowid

            if w.example:
                cursor = await conn.execute(
                    f"INSERT INTO {w.language[0]}_EX (word, text) VALUES (?, ?)",
                    (w_id, w.example[0][0]))
                ex = cursor.lastrowid
            else:
                ex = None

            l1, l2 = w.language[0].lower(), w.language[1].lower()

            await conn.execute(
                f"INSERT INTO dict (user, date, {l1}, {l2}) VALUES (?, ?, ?, ?)",
                (user_id, w.date, w_id, t_id))

            if ex is not None:
                await conn.execute(
                    f"INSERT INTO examples (user, ex, {l1}) VALUES (?, ?, ?)",
                    (user_id, ex, w_id))

            await conn.execute(
                f"INSERT INTO progress (user, lvl, {l1}) VALUES (?, ?, ?)",
                (user_id, 0, w_id))
            
            async with conn.execute("SELECT args_ FROM user WHERE tg_id = ?",
                                    (tg_id,)) as cursor:
                args_ = await cursor.fetchone()

            w_amount = args_[0] + 1

            await conn.execute("UPDATE user SET args_ = ? WHERE tg_id = ?",
                (w_amount, tg_id)
)
        await conn.commit()  
        return True
    
    except Exception as e:
        print(f"add_to_db error: {e}")
        return False


async def del_from_db(tg_id, args_: tuple[str, tuple[int]], conn) -> bool:
    try:
        async with conn.conn() as conn:
            if args_[0] == 'w': 
                # Delete by IDs
                placeholders = ','.join('?' for _ in args_[1])
                query = f'DELETE FROM {tg_id} WHERE id IN ({placeholders})'
                await conn.execute(query, args_[1])

            else:
                # Delete by day numbers
                day_numbers = args_[1]
                
                # Validate day_numbers
                query = f"SELECT COUNT(DISTINCT day) FROM {tg_id}"
                await conn.execute(query)
                total_days = (await conn.fetchone())[0] 
                
                valid_day_numbers = [day for day in day_numbers if 1 <= day <= total_days]

                query = f"SELECT DISTINCT day FROM {tg_id}"
                await conn.execute(query)
                unique_days = tuple(day[0] for day in await conn.fetchall())

                days_for_del = [unique_days[day-1] for day in valid_day_numbers] 
                
                placeholders = ','.join('?' for _ in days_for_del)
                query = f'DELETE FROM {tg_id} WHERE day IN ({placeholders})'
                await conn.execute(query, days_for_del)

            await conn.commit()
            return True

    except Exception as e:
        print(f"del_from_db error: {e}") 
        return False


async def check_user(tg_id:str, username, conn) -> bool:
    async with conn.conn() as conn:
        await conn.execute("SELECT 1 FROM user WHERE tg_id = ?", (tg_id,))
        exists = await conn.fetchone() is not None

        if not exists:
            await conn.execute("INSERT INTO user (tg_id, username) VALUES (?, ?)", (tg_id, username))
            await conn.commit()
            return False
        else:
            return True


async def get_word(tg_id: int, conn, n: int = 1) -> list[WordRow,]:
    async with conn.conn() as conn:
        await conn.execute(f"SELECT COUNT(*) FROM {tg_id}")
        row_count = (await conn.fetchone())[0]
        
        if row_count == 0:
            return None  # No rows in the table
        
        # Generate unique random offsets
        num_rows = min(n, row_count)
        offsets = set()
        while len(offsets) < num_rows:
            offsets.add(random.randint(0, row_count - 1))
        
        rows_as_tuples = []
        for offset in offsets:
            # Fetch a single random row with OFFSET
            query = f"SELECT * FROM {tg_id} LIMIT 1 OFFSET {offset}"
            await conn.execute(query)
            row = await conn.fetchone()
            
            if row:
                rows_as_tuples.append(row)
            
        return rows_as_tuples


async def get_day(tg_id: int, days: tuple[int], conn) -> dict[int:list[WordRow,]]:
    """
    Return day or days {day_number: [WordRow,...],}
    """
    result = {}

    async with conn.conn() as conn:
        # Fetch all unique days in the database
        async with conn.execute(f"""
            SELECT DISTINCT day
            FROM {tg_id}
            ORDER BY day
        """) as conn:
            unique_days = await conn.fetchall()
            unique_days = [day[0] for day in unique_days]  # Flatten to a list of days

        # Map the specified day index to actual days
        day_mapping = {idx + 1: day for idx, day in enumerate(unique_days)}

        for day_index in days:
            # Skip invalid index
            if day_index < 1 or day_index > len(unique_days):
                continue

            # Get the corresponding day value
            target_day = day_mapping[day_index]

            # Fetch rows for the specified day
            async with conn.execute(f"""
                SELECT id, eng, rus, example, day, lvl
                FROM {tg_id}
                WHERE day = ?
                ORDER BY id
            """, (target_day,)) as conn:
                rows = await conn.fetchall()

            # Convert rows to named tuples and store in the result dictionary
            result[day_index] = [WordRow(*row) for row in rows]

    return result
        

async def get_all(tg_id: int, conn) -> dict[int:list[WordRow]]:
    """
    Return all user days {day_number: [WordRow,...],}
    """
    
    result = defaultdict(list)

    async with conn.conn() as conn:
        async with conn.execute(f'SELECT * FROM {tg_id}') as conn:
            rows = await conn.fetchall()

        # Extract unique day numbers and map them to sequential indices
        unique_days = sorted(set(row[4] for row in rows))  # Assuming day is the 5th column
        day_to_index = {day: idx + 1 for idx, day in enumerate(unique_days)}

        # Group rows by sequential day indices using the named tuple
        for row in rows:
            day_number = row[4]  # Assuming day is the 5th column
            day_index = day_to_index[day_number]
            result[day_index].append(WordRow(*row))  # Convert the tuple to a named tuple

    return dict(result)


async def get_info(tg_id: int, conn) -> tuple:
    """
    ruturn info about amount of days and args_ of user: (args_, days)
    """

    async with conn.conn() as conn:
        async with conn.execute(
            f'''
                SELECT MAX(id), COUNT(DISTINCT day) 
                FROM {tg_id}
            '''
            ) as conn:
            return await conn.fetchall()


async def search(tg_id: int, word: str, conn):
    """
    ruturn info about amount of days and args_ of user: (args_, days)
    """

    async with conn.conn() as conn:
        async with conn.execute(
            f'''
                SELECT * 
                FROM {tg_id}
                WHERE eng = '{word}'
            '''
            ) as conn:

            row = await conn.fetchall()
            
            if row:
                return WordRow(*row[0])


# #import pudb; pudb.set_trace()

async def main():
    from datetime import date
    import aiosqlite

    conn = await aiosqlite.connect("/home/zoy/git/asistent-tgbot-/new_db2.db")
    args_ = [WordRow(**{
             "language": ('EN', 'RU'), 
             "word": Word(**{"text": 'test', "tg_id": 123}), 
             "trans": (Word(**{"text": 'тест', "tg_id": 123}),),
             "date": date.today().strftime('%Y-%m-%d'),
             "example": (('Test there.',),)}
    )]
    await add_to_db(123, args_, conn)


if __name__ == "__main__":
     import asyncio
     asyncio.run(main())

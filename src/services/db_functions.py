import random
from collections import defaultdict, namedtuple

from src.services.variables import ALLOWED_LANGUAGES
from src.services.types_ import WordRow, Word, DelArgs


LangOrder = namedtuple('LangOrder', ['number', 'name'])


async def init_db(conn, language: list[str]):
    print(f"Connecting to database at ..")
    
    try:
        await conn.execute("PRAGMA foreign_keys = ON")
        print("Creating tables if not exist...")

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL UNIQUE,
                name TEXT
            )
        """)

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS dict (
                user INTEGER REFERENCES users(id),
                date TEXT NOT NULL DEFAULT (DATETIME('now')),
                archive BOOLEAN NOT NULL DEFAULT 0,
                lvl INTEGER DEFAULT 0
            )
        """)

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS links (
                user INTEGER REFERENCES users(id)
            )
        """)

        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS examples (
                user INTEGER REFERENCES users(id),
                ex INTEGER
            )
        """)

        for lang in language:

            if lang not in ALLOWED_LANGUAGES:
                raise ValueError(f"Invalid language: {lang}")
            
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_WORD (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE,
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
                    text TEXT NOT NULL UNIQUE,
                    FOREIGN KEY (word) REFERENCES {lang}_WORD(id)
                )
            """)

            await conn.execute(f"""
                ALTER TABLE dict ADD COLUMN {lang.lower()} INTEGER;
            """)
            await conn.execute(f"""
                ALTER TABLE examples ADD COLUMN {lang.lower()} INTEGER;
            """)
            await conn.execute(f"""
                ALTER TABLE links ADD COLUMN {lang.lower()} INTEGER;
            """)

        await conn.commit()
        print("Tables created or already exist.")

    except Exception as e:
        print(f"SQLite error: {e}")


async def add_to_db(tg_id: int, args_: WordRow, conn) -> bool:
    try:
        user_id = await get_user_id(tg_id, conn)

        for word_number in range(len(args_.words[0])):
            column_languages = []
            column_words_ids = []

            for __ in enumerate(args_.languages):
                l = LangOrder(*__)
                column_languages.append(l.name.lower())

                cursor = await conn.execute(
                    f"INSERT OR IGNORE INTO {l.name}_WORD (word) VALUES (?)", 
                    ((word := args_.words[l.number][word_number]).text,))
                word.id_ = cursor.lastrowid
                
                if cursor.rowcount != 1:
                    cursor = await conn.execute(
                        f"SELECT id FROM {l.name}_WORD WHERE word = ?", 
                        (word.text,))
                    row = await cursor.fetchone()
                    word.id_ = row[0]

                column_words_ids.append(word.id_)

                cursor = await conn.execute(
                    f"INSERT OR IGNORE INTO dict (user, date, {l.name.lower()}) VALUES (?, ?, ?)",
                    (user_id, args_.date, word.id_)
                )

                if word.examples:
                    for example in word.examples:
                        cursor = await conn.execute(
                            f"INSERT OR IGNORE INTO {l.name}_EX (word, text) VALUES (?, ?)",
                            (word.id_, example))
                        ex_id = cursor.lastrowid

                        if cursor.rowcount != 1:
                            cursor = await conn.execute(
                                f"SELECT id FROM {l.name}_EX WHERE text = ?", 
                                (example,))
                            row = await cursor.fetchone()
                            ex_id = row[0]

                        await conn.execute(
                            f"INSERT INTO examples (user, ex, {l.name.lower()}) VALUES (?, ?, ?)",
                            (user_id, ex_id, word.id_))
                        
            # cursor = await conn.execute(
            #         f"INSERT OR IGNORE INTO links (user, {','.join(column_languages)})\
            #             VALUES (?, {','.join(['?' for _ in column_languages])})",
            #         (user_id, *column_words_ids)
            #     )
            column_list = ', '.join(column_languages)
            placeholders = ', '.join(['?' for _ in column_languages])

            query = f"""
                INSERT INTO links (user, {column_list})
                SELECT ?, {placeholders}
                WHERE NOT EXISTS (
                    SELECT 1 FROM links
                    WHERE user = ?
                    AND {" AND ".join([f"{col} = ?" for col in column_languages])}
                )
            """
            params = (user_id, *column_words_ids, user_id, *column_words_ids)
            await conn.execute(query, params)
            
        await conn.commit()  
        return True
    
    except Exception as e:
        print(f"add_to_db error: {e}")
        return False


async def del_from_db(tg_id: int, args_: DelArgs, conn) -> bool:
    try:
        user_id = get_user_id(tg_id, conn)

        async with conn.conn() as conn:
            if 'w' in args_.flag: 
                # Delete by IDs
                placeholders = ','.join('?' for _ in args_.range)
                await conn.execute(f'''
                                    UPDATE dict SET archive = 1 
                                    WHERE {args_.language[0].lower()} IN ({placeholders})
                                    AND user = ?
                ''', (user_id,))

            elif 'd' in args_.flag:
                # Delete by day numbers
                id_range = days_to_id(tg_id, args_.range)
                
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


async def check_user(tg_id: int, username, conn) -> bool:
    cursor = await conn.execute("SELECT 1 FROM users WHERE tg_id = ?", (tg_id,))
    exist = (await cursor.fetchone()) is not None

    if not exist:
        await conn.execute("INSERT INTO users (tg_id, name) VALUES (?, ?)", (tg_id, username))
        await conn.commit()
        return False
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
    ruturn info about amount of days and words of user: (words, days)
    """

    async with conn.conn() as conn:
        async with conn.execute(
            f'''
                SELECT MAX(id), COUNT(DISTINCT day) 
                FROM {tg_id}
            '''
            ) as conn:
            return await conn.fetchall()


# #import pudb; pudb.set_trace()


async def get_user_id(tg_id, conn):
    async with conn.execute("SELECT id FROM users WHERE tg_id = ?", (tg_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            print("User not found")
            return False
        user_id = row[0]
    
    return user_id

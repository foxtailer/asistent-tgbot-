import random
from datetime import datetime
from typing import List, Tuple
from collections import defaultdict, namedtuple
import aiosqlite

from src.services.variables import ALLOWED_LANGUAGES
from src.services.types import Word
WordRow =1

def init_db(connection, language: list[str]):
    print(f"Connecting to database at ..")

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        print("Creating tables if not exist...")

        connection.execute(f"""
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tg_id INTEGER NOT NULL,
                name TEXT,
                words INTEGER DEFAULT 0
            )
        """)

        connection.execute(f"""
            CREATE TABLE IF NOT EXISTS dict (
                user INTEGER REFERENCES user(id),
                date TEXT NOT NULL DEFAULT (DATETIME('now'))
            )
        """)

        connection.execute(f"""
            CREATE TABLE IF NOT EXISTS examples (
                user INTEGER REFERENCES user(id),
                ex INTEGER
            )
        """)

        connection.execute(f"""
            CREATE TABLE IF NOT EXISTS progress (
                user INTEGER REFERENCES user(id),
                lvl INTEGER DEFAULT 0
            )
        """)

        for i in language:
            lang = i.upper()

            if lang not in ALLOWED_LANGUAGES:
                raise ValueError(f"Invalid language: {lang}")
            
            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_WORD (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL,
                    cefr TEXT,
                    freq INTEGER
                )
            """)

            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_SYN (
                    word INTEGER,
                    syn INTEGER,
                    FOREIGN KEY (word) REFERENCES {lang}_WORD(id),
                    FOREIGN KEY (syn) REFERENCES {lang}_WORD(id),
                    PRIMARY KEY (word, syn)
                )
            """)

            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_ANT (
                    word INTEGER,
                    ant INTEGER,
                    FOREIGN KEY (word) REFERENCES {lang}_WORD(id),
                    FOREIGN KEY (ant) REFERENCES {lang}_WORD(id),
                    PRIMARY KEY (word, ant)
                )
            """)

            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS {lang}_EX (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word INTEGER NOT NULL,
                    text TEXT,
                    FOREIGN KEY (word) REFERENCES {lang}_WORD(id)
                )
            """)

            connection.execute(f"""
                ALTER TABLE progress ADD COLUMN {lang.lower()} INTEGER;
            """)
            connection.execute(f"""
                ALTER TABLE dict ADD COLUMN {lang.lower()} INTEGER;
            """)
            connection.execute(f"""
                ALTER TABLE examples ADD COLUMN {lang.lower()} INTEGER;
            """)

        connection.commit()
        print("Tables created or already exist.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")


async def add_to_db(user_id: int, words: List[Tuple[str, str, str]], connection) -> bool:
    try:    
        async with connection.cursor() as cursor:
            today_date = datetime.today().isoformat()[:10]

            for data_set in words:
                insert_data = (*data_set, today_date)
                await cursor.execute(
                    f'INSERT OR REPLACE INTO {user_id} (eng, rus, example, day) VALUES (?, ?, ?, ?)',
                    insert_data
                )
            
            await connection.commit()  

        return True
    except Exception as e:
        return False


async def del_from_db(user_id, command_args: Tuple[str, Tuple[int]], connection) -> bool:
    try:
        async with aiosqlite.connect(db_path) as connection:
            cursor = await connection.cursor()

            if command_args[0] == 'w': 
                # Delete by IDs
                placeholders = ','.join('?' for _ in command_args[1])
                query = f'DELETE FROM {user_id} WHERE id IN ({placeholders})'
                await cursor.execute(query, command_args[1])

            else:
                # Delete by day numbers
                day_numbers = command_args[1]
                
                # Validate day_numbers
                query = f"SELECT COUNT(DISTINCT day) FROM {user_id}"
                await cursor.execute(query)
                total_days = (await cursor.fetchone())[0] 
                
                valid_day_numbers = [day for day in day_numbers if 1 <= day <= total_days]

                query = f"SELECT DISTINCT day FROM {user_id}"
                await cursor.execute(query)
                unique_days = tuple(day[0] for day in await cursor.fetchall())

                days_for_del = [unique_days[day-1] for day in valid_day_numbers] 
                
                placeholders = ','.join('?' for _ in days_for_del)
                query = f'DELETE FROM {user_id} WHERE day IN ({placeholders})'
                await cursor.execute(query, days_for_del)

            await connection.commit()
            return True

    except Exception as e:
        print(f"Error during database deletion: {e}") 
        return False


async def check_user(user_id:str, username, connection)->bool:
     db_path = '/home/nami/git/asistent-tgbot-/new_db.db'
     async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM user WHERE tg_id = ?", (user_id,))
            exists = await cursor.fetchone() is not None

            if not exists:
                await cursor.execute("INSERT INTO user (tg_id, username) VALUES (?, ?)", (user_id, username))
                await conn.commit()
                return False
            else:
                return True


async def get_word(user_id: int, connection, n: int = 1) -> list[WordRow,]:
    async with aiosqlite.connect(db_path) as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT COUNT(*) FROM {user_id}")
            row_count = (await cursor.fetchone())[0]
            
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
                query = f"SELECT * FROM {user_id} LIMIT 1 OFFSET {offset}"
                await cursor.execute(query)
                row = await cursor.fetchone()
                
                if row:
                    rows_as_tuples.append(row)
                
            return rows_as_tuples


async def get_day(user_id: int, days: Tuple[int], connection) -> dict[int:list[WordRow,]]:
    """
    Return day or days {day_number: [WordRow,...],}
    """
    result = {}

    async with aiosqlite.connect(db_path) as connection:
        # Fetch all unique days in the database
        async with connection.execute(f"""
            SELECT DISTINCT day
            FROM {user_id}
            ORDER BY day
        """) as cursor:
            unique_days = await cursor.fetchall()
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
            async with connection.execute(f"""
                SELECT id, eng, rus, example, day, lvl
                FROM {user_id}
                WHERE day = ?
                ORDER BY id
            """, (target_day,)) as cursor:
                rows = await cursor.fetchall()

            # Convert rows to named tuples and store in the result dictionary
            result[day_index] = [WordRow(*row) for row in rows]

    return result
        

async def get_all(user_id: int, connection) -> dict[int:list[WordRow]]:
    """
    Return all user days {day_number: [WordRow,...],}
    """
    
    result = defaultdict(list)

    async with aiosqlite.connect(db_path) as connection:
        async with connection.execute(f'SELECT * FROM {user_id}') as cursor:
            rows = await cursor.fetchall()

        # Extract unique day numbers and map them to sequential indices
        unique_days = sorted(set(row[4] for row in rows))  # Assuming day is the 5th column
        day_to_index = {day: idx + 1 for idx, day in enumerate(unique_days)}

        # Group rows by sequential day indices using the named tuple
        for row in rows:
            day_number = row[4]  # Assuming day is the 5th column
            day_index = day_to_index[day_number]
            result[day_index].append(WordRow(*row))  # Convert the tuple to a named tuple

    return dict(result)


async def get_info(user_id: int, connection) -> tuple:
    """
    ruturn info about amount of days and words of user: (words, days)
    """

    async with aiosqlite.connect(db_path) as connection:
        async with connection.execute(
            f'''
                SELECT MAX(id), COUNT(DISTINCT day) 
                FROM {user_id}
            '''
            ) as cursor:
            return await cursor.fetchall()


async def search(user_id: int, word: str, connection):
    """
    ruturn info about amount of days and words of user: (words, days)
    """

    async with aiosqlite.connect(db_path) as connection:
        async with connection.execute(
            f'''
                SELECT * 
                FROM {user_id}
                WHERE eng = '{word}'
            '''
            ) as cursor:

            row = await cursor.fetchall()
            
            if row:
                return WordRow(*row[0])

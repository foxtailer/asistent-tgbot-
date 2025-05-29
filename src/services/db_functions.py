import os
import random
import aiosqlite
from datetime import datetime
from typing import List, Tuple
from collections import defaultdict, namedtuple


DB_PATH = ''

WordRow = namedtuple("WordRow", ["id", "eng", "rus", "example", "day", "lvl"])


async def init_db():
    print(f"Connecting to database at {DB_PATH}")

    try:
        async with aiosqlite.connect(DB_PATH) as connection:
            print("Creating table if not exists...")
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    bot TEXT DEFAULT 'ENG' CHECK (LENGTH(bot) = 3) 
                )
            """)
            await connection.commit()
            print("Table created or already exists.")
    except aiosqlite.Error as e:
        print(f"SQLite error: {e}")
        

# Future db
def init_user_db():
    print(f"Connecting to database at ..")

    try:
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            print("Creating tables if not exist...")
                
            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER NOT NULL,
                    name TEXT,
                    lvl INTEGER,
                    words INTEGER
                )
            """)
            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS dict (
                    user INTEGER,
                    eng INTEGER,
                    ru INTEGER,
                    jp INTEGER,
                    date TEXT DEFAULT (DATETIME('now')),
                    FOREIGN KEY (user) REFERENCES user(id),
                    FOREIGN KEY (eng) REFERENCES ENG(id),
                    FOREIGN KEY (ru) REFERENCES RU(id),
                    FOREIGN KEY (jp) REFERENCES JP(id),
                    UNIQUE (user, eng),
                    UNIQUE (user, ru),
                    UNIQUE (user, jp)
                )
            """)
            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS examples (
                    user INTEGER,
                    eng INTEGER,
                    ru INTEGER,
                    jp INTEGER,
                    ex INTEGER,
                    FOREIGN KEY (user) REFERENCES user(id),
                    FOREIGN KEY (eng) REFERENCES ENG(id),
                    FOREIGN KEY (ru) REFERENCES RU(id),
                    FOREIGN KEY (jp) REFERENCES JP(id),
                    CHECK (
                        (eng IS NOT NULL) + (ru IS NOT NULL) + (jp IS NOT NULL) = 1
                    )
                )
            """)
            connection.execute(f"""
                CREATE TABLE IF NOT EXISTS progress (
                    user INTEGER,
                    eng INTEGER,
                    ru INTEGER,
                    jp INTEGER,
                    lvl INTEGER,
                    FOREIGN KEY (user) REFERENCES user(id),
                    FOREIGN KEY (eng) REFERENCES ENG(id),
                    FOREIGN KEY (ru) REFERENCES RU(id),
                    FOREIGN KEY (jp) REFERENCES JP(id),
                    CHECK (
                        (eng IS NOT NULL) + (ru IS NOT NULL) + (jp IS NOT NULL) = 1
                    )
                )
            """)

            connection.commit()
            print("Tables created or already exist.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")


# Future db
def init_lang_db(language: list[str]):
    print(f"Connecting to database at ..")

    try:
        with sqlite3.connect(DB_PATH) as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            print("Creating tables if not exist...")

            for i in language:
                lang = i.upper()
                
                connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS {lang} (
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
                        FOREIGN KEY (word) REFERENCES {lang}(id),
                        FOREIGN KEY (syn) REFERENCES {lang}(id),
                        PRIMARY KEY (word, syn)
                    )
                """)
                connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS {lang}_ANT (
                        word INTEGER,
                        ant INTEGER,
                        FOREIGN KEY (word) REFERENCES {lang}(id),
                        FOREIGN KEY (ant) REFERENCES {lang}(id),
                        PRIMARY KEY (word, ant)
                    )
                """)
                connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS {lang}_POS (
                        word INTEGER,
                        pos TEXT,
                        FOREIGN KEY (word) REFERENCES {lang}(id),
                        PRIMARY KEY (word, pos)
                    )
                """)
                connection.execute(f"""
                    CREATE TABLE IF NOT EXISTS {lang}_EX (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        word INTEGER NOT NULL,
                        text TEXT,
                        FOREIGN KEY (word) REFERENCES {lang}(id)
                    )
                """)

            connection.commit()
            print("Tables created or already exist.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")


async def add_to_db(user_name: str, words: List[Tuple[str, str, str]], db_path: str='') -> bool:
    try:    
        async with aiosqlite.connect(db_path) as connection:
            async with connection.cursor() as cursor:
                today_date = datetime.today().isoformat()[:10]

                for data_set in words:
                    insert_data = (*data_set, today_date)
                    await cursor.execute(
                        f'INSERT OR REPLACE INTO {user_name} (eng, rus, example, day) VALUES (?, ?, ?, ?)',
                        insert_data
                    )
                
                await connection.commit()  

        return True
    except Exception as e:
        return False


async def del_from_db(user_name, command_args: Tuple[str, Tuple[int]], db_path='') -> bool:
    try:
        async with aiosqlite.connect(db_path) as connection:
            cursor = await connection.cursor()

            if command_args[0] == 'w': 
                # Delete by IDs
                placeholders = ','.join('?' for _ in command_args[1])
                query = f'DELETE FROM {user_name} WHERE id IN ({placeholders})'
                await cursor.execute(query, command_args[1])

            else:
                # Delete by day numbers
                day_numbers = command_args[1]
                
                # Validate day_numbers
                query = f"SELECT COUNT(DISTINCT day) FROM {user_name}"
                await cursor.execute(query)
                total_days = (await cursor.fetchone())[0] 
                
                valid_day_numbers = [day for day in day_numbers if 1 <= day <= total_days]

                query = f"SELECT DISTINCT day FROM {user_name}"
                await cursor.execute(query)
                unique_days = tuple(day[0] for day in await cursor.fetchall())

                days_for_del = [unique_days[day-1] for day in valid_day_numbers] 
                
                placeholders = ','.join('?' for _ in days_for_del)
                query = f'DELETE FROM {user_name} WHERE day IN ({placeholders})'
                await cursor.execute(query, days_for_del)

            await connection.commit()
            return True

    except Exception as e:
        print(f"Error during database deletion: {e}") 
        return False


async def create_user(user_name: str, db_path='') -> None:
    
    async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {user_name} (
                    id INTEGER PRIMARY KEY,
                    eng TEXT NOT NULL UNIQUE,
                    rus TEXT NOT NULL,
                    example TEXT,
                    day TEXT,
                    lvl INTEGER DEFAULT 0
                )
            """)
            await conn.commit()


async def check_user(user_name:str, db_path='')->bool:
     
     async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM users WHERE name = ?", (user_name,))
            user_exists = (await cursor.fetchone())[0] > 0

            if not user_exists:
                await cursor.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
                await conn.commit()
                await create_user(user_name, db_path)
                return False
            else:
                return True


async def get_word(user_name: str, n: int = 1, db_path='') -> list[WordRow,]:
    async with aiosqlite.connect(db_path) as db:
        async with db.cursor() as cursor:
            await cursor.execute(f"SELECT COUNT(*) FROM {user_name}")
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
                query = f"SELECT * FROM {user_name} LIMIT 1 OFFSET {offset}"
                await cursor.execute(query)
                row = await cursor.fetchone()
                
                if row:
                    rows_as_tuples.append(row)
                
            return rows_as_tuples


async def get_day(user_name: str, days: Tuple[int], db_path='') -> dict[int:list[WordRow,]]:
    """
    Return day or days {day_number: [WordRow,...],}
    """
    result = {}

    async with aiosqlite.connect(db_path) as connection:
        # Fetch all unique days in the database
        async with connection.execute(f"""
            SELECT DISTINCT day
            FROM {user_name}
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
                FROM {user_name}
                WHERE day = ?
                ORDER BY id
            """, (target_day,)) as cursor:
                rows = await cursor.fetchall()

            # Convert rows to named tuples and store in the result dictionary
            result[day_index] = [WordRow(*row) for row in rows]

    return result
        

async def get_all(user_name: str, db_path='') -> dict[int:list[WordRow]]:
    """
    Return all user days {day_number: [WordRow,...],}
    """
    
    result = defaultdict(list)

    async with aiosqlite.connect(db_path) as connection:
        async with connection.execute(f'SELECT * FROM {user_name}') as cursor:
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


async def get_info(user_name: str, db_path='') -> tuple:
    """
    ruturn info about amount of days and words of user: (words, days)
    """

    async with aiosqlite.connect(db_path) as connection:
        async with connection.execute(
            f'''
                SELECT MAX(id), COUNT(DISTINCT day) 
                FROM {user_name}
            '''
            ) as cursor:
            return await cursor.fetchall()


def find_dir_path():
    script_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(script_path)
    return dir_path


if __name__ == '__main__':
    import sqlite3
    init_lang_db(["eng", "ru"])
    init_lang_db(["jp"])
    init_user_db()
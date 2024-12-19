import os
import random
import sqlite3
import aiosqlite
from datetime import datetime
from typing import List, Tuple

from ..config import DB_PATH


async def add_to_db(user_name: str, words: List[Tuple[str, str, str]], db_path: str = DB_PATH) -> bool:
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


async def del_from_db(user_name, command_args: Tuple[str, Tuple[int]], db_path=DB_PATH) -> bool:
    try:
        if not command_args[0]:

            async with aiosqlite.connect(db_path) as connection:
                cursor = await connection.cursor()

                placeholders = ','.join('?' for _ in command_args[1])
                query = f'DELETE FROM {user_name} WHERE id IN ({placeholders})'
                await cursor.execute(query, command_args[1])

                await connection.commit()
        else:

            day_numbers = command_args[1]

            async with aiosqlite.connect(db_path) as connection:
                cursor = await connection.cursor()

                query = f"SELECT DISTINCT day FROM {user_name}"
                await cursor.execute(query)
                unique_days = await cursor.fetchall()
                unique_days = tuple(day[0] for day in unique_days)
                
                day_numbers = [day for day in day_numbers if day > 1 and day <= len(unique_days)]

                days_for_del = [unique_days[day-1] for day in day_numbers]
                
                placeholders = ','.join('?' for _ in days_for_del)
                query = f'DELETE FROM {user_name} WHERE day IN ({placeholders})'
                await cursor.execute(query, days_for_del)

                await connection.commit()

        return True
    except Exception as e:
        return False


async def create_user(user_name: str, db_path=DB_PATH) -> None:
    
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


async def check_user(user_name:str, db_path=DB_PATH)->bool:
     
     async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM users WHERE name = ?", (user_name,))
            user_exists = (await cursor.fetchone())[0] > 0

            if not user_exists:
                await cursor.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
                await conn.commit()
                await create_user(user_name, DB_PATH)
                return False
            else:
                return True


async def get_word(user_name, n=1, db_path=DB_PATH):
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


async def get_day(user_name: str, day: Tuple[int], db_path: str = DB_PATH):
    async with aiosqlite.connect(db_path) as db:
        async with db.execute(f"""
            SELECT DISTINCT day
            FROM {user_name}
            ORDER BY day
        """) as cursor:
            days = await cursor.fetchall()
            
            if day < 0 or day >= len(days):
                return
            
            # Extract the day value at the specified index
            target_day = days[day][0]
        
        # Fetch rows with the selected day
        async with db.execute(f"""
            SELECT id, eng, rus, example, day, lvl
            FROM {user_name}
            WHERE day = ?
            ORDER BY id
        """, (target_day,)) as cursor:
            rows = await cursor.fetchall()
            random.shuffle(rows)

            return rows
        

async def get_all(user_name: str, db_path: str = DB_PATH):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(f'SELECT * FROM {user_name}')
    # [(371, ' Stain', ' пятно', ' The red wine left a stain on the carpet.', '2024-08-26', 0),]
    curent_dict = cursor.fetchall()  
    connection.close()

    return curent_dict


def transfer(a, b, name):
    connection = sqlite3.connect(a)
    cursor = connection.cursor()

    cursor.execute(f'SELECT * FROM {name}')
    user_dict = cursor.fetchall()
    user_dict = [tuple(list(x)[1:]) for x in user_dict]

    connection.commit()
    connection.close()

    connection = sqlite3.connect(b)
    cursor = connection.cursor()

    for i in user_dict:
        cursor.execute(f'INSERT INTO {name} (eng, rus, example, day) VALUES (?, ?, ?, ?)', i)

    connection.commit()
    connection.close()


def find_dir_path():
    script_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(script_path)
    return dir_path


# Initiate db
if __name__ == '__main__':

    print(f"Connecting to database at {DB_PATH}")

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        print("Creating table if not exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                bot TEXT DEFAULT 'ENG' CHECK (LENGTH(bot) = 3) 
            )
        """)
        
        connection.commit()
        print("Table created or already exists.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        connection.close()

import os
import random
import sqlite3
import aiosqlite

from datetime import datetime


DB_NAME = 'bot_db.db'

async def add_to_db(user_name, command_args, script_dir) -> bool:
    db_path = f"{script_dir}/{DB_NAME}"

    try:    
        async with aiosqlite.connect(db_path) as connection:
            async with connection.cursor() as cursor:
                today_date = datetime.today().isoformat()[:10]
                data = [element.lower().strip() for element in command_args.split(',')]

                if (len(data) % 3) != 0:
                    return False

                data_sets = [tuple(data[i:i + 3]) for i in range(0, len(data), 3)]

                for data_set in data_sets:
                    insert_data = (*data_set, today_date)
                    await cursor.execute(
                        f'INSERT OR REPLACE INTO {user_name} (eng, rus, example, day) VALUES (?, ?, ?, ?)',
                        insert_data
                    )
                
                await connection.commit()  

        return True
    except Exception as e:
        return False


async def del_from_db(user_name, command_args: tuple, script_dir):
    try:
        if not command_args[0]:
            id_list = tuple(map(int, command_args[1].strip().split(",")))

            async with aiosqlite.connect(f"{script_dir}/{DB_NAME}") as connection:
                cursor = await connection.cursor()

                placeholders = ','.join('?' for _ in id_list)
                query = f'DELETE FROM {user_name} WHERE id IN ({placeholders})'
                await cursor.execute(query, id_list)

                await connection.commit()
        else:
            day_numbers = tuple(map(int, command_args[1].strip().split(",")))

            async with aiosqlite.connect(f"{script_dir}/{DB_NAME}") as connection:
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


async def create_user(user_name: str, script_dir: str) -> None:
    
    async with aiosqlite.connect(f"{script_dir}/{DB_NAME}") as conn:
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


async def check_user(user_name:str, script_dir)->bool:
     
     async with aiosqlite.connect(f"{script_dir}/{DB_NAME}") as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) FROM users WHERE name = ?", (user_name,))
            user_exists = (await cursor.fetchone())[0] > 0

            if not user_exists:
                await cursor.execute("INSERT INTO users (name) VALUES (?)", (user_name,))
                await conn.commit()
                await create_user(user_name, script_dir)
                return False
            else:
                return True


async def get_word(script_dir, user_name, n=1):
    async with aiosqlite.connect(f"{script_dir}/{DB_NAME}") as db:
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


async def get_day(script_dir, user_name, day):
    async with aiosqlite.connect(f"{script_dir}/{DB_NAME}") as db:
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


def find_path():
    script_path = os.path.realpath(__file__)
    script_dir = os.path.dirname(script_path)

    return script_dir


# from datetime import datetime

# def iso_to_unix(date_str):
#     dt = datetime.fromisoformat(date_str)
#     return int(dt.timestamp())

# # Example conversion
# date_str = '2023-08-12'
# unix_timestamp = iso_to_unix(date_str)

if __name__ == '__main__':

    db_path = f"{find_path()}/{DB_NAME}"
    print(f"Connecting to database at {db_path}")

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        print("Creating table if not exists...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        
        connection.commit()
        print("Table created or already exists.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        connection.close()

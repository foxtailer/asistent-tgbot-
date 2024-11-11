import sqlite3
import os
from datetime import datetime, timedelta


DB_NAME = 'bot_db.db'

def find_path():
    script_path = os.path.realpath(__file__)
    script_dir = os.path.dirname(script_path)

    return script_dir


db_path = f"{find_path()}/{DB_NAME}"

connection = sqlite3.connect(db_path)
cursor = connection.cursor()

today_date = datetime.today().date()
yesterday_date2 = today_date - timedelta(days=2)
yesterday_date_str = yesterday_date2.isoformat()[:10]

yesterday_date1 = today_date - timedelta(days=1)
yesterday_date_str = yesterday_date1.isoformat()[:10]

# update_query = '''
#     UPDATE Victoria
#     SET day = ?
#     WHERE id < 30
# '''

# update_query2 = '''
#     UPDATE Victoria
#     SET day = ?
#     WHERE id > 50
# '''

# cursor.execute(update_query, (yesterday_date2,))
# cursor.execute(update_query2, (yesterday_date1,))

delete_query = '''
    DELETE FROM Victoria
    WHERE id = ?
'''

cursor.execute(delete_query, (8,))

connection.commit()
connection.close()
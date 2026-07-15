import sqlite3
from datetime import datetime, timedelta


DB = "users.db"


def connect():
    return sqlite3.connect(DB)



def create_tables():

    conn = connect()
    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id INTEGER UNIQUE,

        username TEXT,

        first_name TEXT,

        devices INTEGER DEFAULT 0,

        months INTEGER DEFAULT 0,

        expire_date TEXT

    )
    """)


    conn.commit()
    conn.close()




def add_user(user):

    conn = connect()
    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (
        telegram_id,
        username,
        first_name
        )

        VALUES (?, ?, ?)
        """,

        (
            user.id,
            user.username,
            user.first_name
        )
    )


    conn.commit()
    conn.close()




def get_user(telegram_id):

    conn = connect()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE telegram_id=?
        """,
        (telegram_id,)
    )


    result = cursor.fetchone()

    conn.close()

    return result





def activate_subscription(
        telegram_id,
        devices,
        months
):

    conn = connect()
    cursor = conn.cursor()


    expire = datetime.now() + timedelta(
        days=30 * months
    )


    cursor.execute(
        """
        UPDATE users

        SET
        devices=?,
        months=?,
        expire_date=?

        WHERE telegram_id=?
        """,

        (
            devices,
            months,
            expire.strftime("%d.%m.%Y"),
            telegram_id
        )
    )


    conn.commit()
    conn.close()
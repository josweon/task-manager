"""
task-manager.database
~~~~~~~~~~~~~~~~~~~~~

This module contains the data handlers for task-manager.
"""

import sqlite3 as sqweel
import re


DB_PATH = "task_manager.db"

def connect_db() -> sqweel.Connection:
    """Helper function that opens the database connection."""
    conn = sqweel.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db() -> None:
    """Initializes schema for Tasks and User tables."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        # Create tasks table        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR (50),
                completed BIT,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
                )
        """)

        # Creates index for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id)")

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR NOT NULL UNIQUE,
                password_hash VARCHAR NOT NULL
            )
        """)
        conn.commit()
        
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
        #            IMPORTING DATA INTO TABLES TO ADD PERSISTANCE            #
        # for task in tasks:                                                  #
        #     cursor.execute(                                                 #
        #         "INSERT INTO tasks (id, title, completed) VALUES(?, ?, ?)", #
        #         (task["id"], task["title"], int(task["completed"]))         #
        #     )                                                               #
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    except sqweel.Error as error:
        print(f"An error occured: {error}")

    finally:
        conn.close()


def get_single_task(title: str, user_id: int) -> list:
    """Gets a single task stored under a user.
    
    :param title: str, name of the task.
    :param user_id: int, id associated with user.
    :return: list, dictionary containing row for scoped task.
    """
    conn = connect_db()
    conn.row_factory = sqweel.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE title = ? AND user_id = ?",
        (title, user_id)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_user_tasks(user_id: int) -> list:
    """Retrieves tasks by user_id from Tasks.

    :param user_id: int, id associated with user.
    :return: List, dictionaries containing contents of tasks by id.
    """
    conn = connect_db()
    conn.row_factory = sqweel.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE user_id = ?",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_tasks(new_task: dict) -> int | None:
    """Inserts a new row(task) in Tasks.

    :param new_task: Dictonary, contains attibutes to be inserted.
    :return: int, task_id associated with the newly created task.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (user_id, title, completed) VALUES (?,?,?)",
        (new_task["user_id"], new_task["title"], new_task["completed"])
    )
    conn.commit()
    conn.close()

    return cursor.lastrowid


def update_completion(task: dict) -> int | None:
    """Updates the status of existing task.

    :param task: Dictionary, contains attributes of task.
    :return: rowcount(int), confirmation that status was changed.
    """
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
            ((1 if task["completed"] else 0), task["id"], task["user_id"])
        )
        conn.commit()
        return cursor.rowcount > 0

    except sqweel.Error as error:
        print(f"An error occured: {error}")
    
    finally:    
        conn.close()


def remove_tasks(task_id: int, user_id: int) -> int | None:
    """Removes a task associated with a user from Tasks table.

    :param task_id: int, id associated with task.
    :param user_id: int, id associated with user.
    :return: rowcount(int), confirmation that task was removed.
    """
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
        
    except sqweel.Error as error:
        print(f"An error occured: {error}" )
    
    finally:
        conn.close()


def create_user(email: str, password_hash) -> None:
    """Creates a new user.
    
    :param email: str, email address of the new user.
    :param password_hash: str, hashed passowrd of new user.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users(email, password_hash) VALUES(?,?)",
        (email, password_hash)
    )
    conn.commit()
    conn.close()


def get_user_by_email(email: str) -> dict | None:
    """Checks if a user already exists by email.

    :param email: str, email address of the user.
    :return: dict, user information if user exists else none.
    """
    conn = connect_db()
    conn.row_factory = sqweel.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None

def is_valid_email(email: str) -> bool:
    """Helper function to determine if string is formatted as an email."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

if __name__ == "__main__":
    initialize_db()

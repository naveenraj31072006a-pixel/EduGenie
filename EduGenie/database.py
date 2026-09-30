import os
import sqlite3

from datetime import datetime
from pathlib import Path

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)


BASE_DIR = Path(__file__).resolve().parent

DB_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        BASE_DIR / "edugenie.db"
    )
)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_connection():

    connection = sqlite3.connect(
        DB_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


# --------------------------------------------------
# CREATE TABLES
# --------------------------------------------------

def init_db():

    with get_connection() as conn:

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                email TEXT NOT NULL UNIQUE,

                password_hash TEXT NOT NULL,

                created_at TEXT NOT NULL
            );


            CREATE TABLE IF NOT EXISTS progress (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                activity TEXT NOT NULL,

                score INTEGER NOT NULL DEFAULT 0,

                total INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL,

                FOREIGN KEY(user_id)
                REFERENCES users(id)
            );
            """
        )


# --------------------------------------------------
# CREATE USER
# --------------------------------------------------

def create_user(
    name,
    email,
    password
):

    password_hash = generate_password_hash(
        password
    )

    try:

        with get_connection() as conn:

            cursor = conn.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password_hash,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    password_hash,
                    datetime.utcnow().isoformat()
                )
            )

            return cursor.lastrowid

    except sqlite3.IntegrityError:

        raise ValueError(
            "An account with this email already exists."
        )


# --------------------------------------------------
# GET USER
# --------------------------------------------------

def get_user_by_email(email):

    with get_connection() as conn:

        row = conn.execute(
            """
            SELECT
                id,
                name,
                email,
                password_hash
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        return dict(row) if row else None


# --------------------------------------------------
# VERIFY PASSWORD
# --------------------------------------------------

def verify_password(
    password,
    password_hash
):

    return check_password_hash(
        password_hash,
        password
    )


# --------------------------------------------------
# SAVE PROGRESS
# --------------------------------------------------

def add_progress(
    user_id,
    activity,
    score,
    total
):

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO progress
            (
                user_id,
                activity,
                score,
                total,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                activity,
                score,
                total,
                datetime.utcnow().isoformat()
            )
        )


# --------------------------------------------------
# GET PROGRESS
# --------------------------------------------------

def get_progress(user_id):

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT
                activity,
                score,
                total,
                created_at
            FROM progress
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()

    rows = [
        dict(row)
        for row in rows
    ]

    completed = len(rows)

    earned = sum(
        row["score"]
        for row in rows
    )

    possible = sum(
        row["total"]
        for row in rows
    )

    percentage = (
        round(
            (earned / possible) * 100,
            1
        )
        if possible
        else 0
    )

    return {
        "activities": rows,
        "completed": completed,
        "earned": earned,
        "possible": possible,
        "percentage": percentage
    }
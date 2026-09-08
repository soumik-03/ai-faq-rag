import sqlite3

from pathlib import Path
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "tickets.db"


# ============================================================
# CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(
        DB_PATH
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_ticket_database():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id TEXT UNIQUE NOT NULL,

            customer_name TEXT,

            customer_email TEXT NOT NULL,

            question TEXT NOT NULL,

            status TEXT NOT NULL DEFAULT 'Open',

            priority TEXT NOT NULL DEFAULT 'Normal',

            created_at TEXT NOT NULL

        )
        """
    )


    conn.commit()

    conn.close()


# ============================================================
# CREATE TICKET
# ============================================================

def create_ticket(
    customer_name,
    customer_email,
    question,
    priority="Normal"
):

    initialize_ticket_database()


    conn = get_connection()

    cursor = conn.cursor()


    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


    # Temporary ID first

    cursor.execute(
        """
        INSERT INTO tickets (
            ticket_id,
            customer_name,
            customer_email,
            question,
            status,
            priority,
            created_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "TEMP",
            customer_name,
            customer_email,
            question,
            "Open",
            priority,
            created_at
        )
    )


    database_id = cursor.lastrowid


    # Generate public ticket ID

    ticket_id = (
        f"TKT-"
        f"{datetime.now().strftime('%Y%m%d')}-"
        f"{database_id:04d}"
    )


    cursor.execute(
        """
        UPDATE tickets

        SET ticket_id = ?

        WHERE id = ?
        """,
        (
            ticket_id,
            database_id
        )
    )


    conn.commit()

    conn.close()


    return ticket_id


# ============================================================
# GET ALL TICKETS
# ============================================================

def get_all_tickets():

    initialize_ticket_database()


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            ticket_id,
            customer_name,
            customer_email,
            question,
            status,
            priority,
            created_at

        FROM tickets

        ORDER BY id DESC
        """
    )


    tickets = cursor.fetchall()

    conn.close()


    return tickets
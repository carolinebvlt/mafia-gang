import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "mafia.db"


def init_database():

    connexion = sqlite3.connect(DATABASE)
    curseur = connexion.cursor()

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            money INTEGER NOT NULL,
            country TEXT NOT NULL,
            ammo INTEGER NOT NULL
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS alcohols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            alcohol_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            UNIQUE(player_id, alcohol_id)
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS market (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT NOT NULL,
            alcohol_id INTEGER NOT NULL,
            current_price INTEGER NOT NULL,
            previous_price INTEGER,
            UNIQUE(country, alcohol_id)
        )
    """)

    curseur.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY,
            last_market_update DATETIME NOT NULL
        )
    """)

    connexion.commit()
    connexion.close()

    print("Database initialized !")


init_database()
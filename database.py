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
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER NOT NULL,
        item TEXT NOT NULL,
        amount INTEGER NOT NULL
    )
    """)

    curseur.execute("""
    CREATE TABLE IF NOT EXISTS market (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country TEXT NOT NULL,
        item TEXT NOT NULL,
        current_price INTEGER,
        previous_price INTEGER,
        UNIQUE(country, item)
    )
    """)

    curseur.execute("""
    CREATE TABLE IF NOT EXISTS game_state(
        id INTEGER PRIMARY KEY,
        last_market_update DATETIME NOT NULL
    )
    """)

    connexion.commit()
    connexion.close()

    print("Database initialized !")


init_database()
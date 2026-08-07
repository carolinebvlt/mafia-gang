import sqlite3
import data
from datetime import date
from random import randint

def buy_one_ammo(player_id):

    if check_enough_money(player_id, data.AMMO_PRICE) :

        connexion = sqlite3.connect("mafia.db")
        connexion.row_factory = sqlite3.Row
        curseur = connexion.cursor()

        curseur.execute(
            "UPDATE players SET money = money-?, ammo = ammo+1 WHERE id = ?",
            (data.AMMO_PRICE, player_id)
        )
        connexion.commit()
        connexion.close()

def check_enough_money(player_id, amount) :
    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT money from players WHERE id = ?",
        (player_id,)
    )
    money = curseur.fetchone()['money']
    connexion.close()

    if money >= amount :
        return True
    else :
        return False

def get_player(player_id):

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()
    curseur.execute(
        "SELECT * FROM players WHERE id = ?",
        (player_id,)
    )
    player = curseur.fetchone()
    connexion.close()
    return player

def get_current_market(player_id):
    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT last_market_update FROM game_state"
    )
    last_market_update = curseur.fetchone()
    if last_market_update == None :
        init_market()
    else :
        date_last_market_update = last_market_update[0]


    if date_last_market_update == str(date.today()): 
        # load market for country of the player
        curseur.execute(
            "SELECT country FROM players WHERE id = ?",
            (player_id,)
        )
        country = curseur.fetchone()['country']
        curseur.execute(
            "SELECT item, current_price FROM market WHERE country = ?",
            (country,)
        )
        market = curseur.fetchall()

        return market

    #else update market
        


    connexion.close()

def init_market():

    connexion = sqlite3.connect("mafia.db")
    curseur = connexion.cursor()

    for alcohol in data.ALCOHOLS :
        for country in data.COUNTRIES :

            curseur.execute("""
                INSERT INTO market (country, item, current_price)
                VALUES (?, ?, ?)
            """, (country, alcohol, randint(50, 150)))

    curseur.execute("""
        INSERT INTO game_state (id, last_market_update)
        VALUES (?, ?)
    """, (1, date.today()))

    connexion.commit()
    connexion.close()
    print("market initialized")
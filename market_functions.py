import game
import data
import players
from datetime import date, datetime
from random import randint, choice

def init_market():

    connexion = game.get_connection()
    curseur = connexion.cursor()

    # Make sure all alcohols exist
    for alcohol in data.ALCOHOLS:

        curseur.execute(
            "INSERT OR IGNORE INTO alcohols (name) VALUES (?)",
            (alcohol,)
        )

    # Create market for every alcohol in every country
    for alcohol in data.ALCOHOLS:

        curseur.execute(
            "SELECT id FROM alcohols WHERE name = ?",
            (alcohol,)
        )

        alcohol_id = curseur.fetchone()[0]

        for country in data.COUNTRIES:

            curseur.execute("""
                INSERT OR IGNORE INTO market
                (country, alcohol_id, current_price)
                VALUES (?, ?, ?)
            """, (
                country,
                alcohol_id,
                randint(50, 150)
            ))

    # Create/update game state
    curseur.execute("""
        INSERT OR REPLACE INTO game_state
        (id, last_market_update)
        VALUES (?, ?)
    """, (1, date.today()))

    connexion.commit()
    connexion.close()

    print("market initialized")

def get_market(player_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT country FROM players WHERE id = ?",
        (player_id,)
    )

    player = curseur.fetchone()

    if player is None:
        connexion.close()
        return []

    country = player["country"]

    curseur.execute("""
        SELECT
            market.id,
            market.alcohol_id,
            alcohols.name,
            market.current_price,
            market.previous_price
        FROM market
        JOIN alcohols ON market.alcohol_id = alcohols.id
        WHERE market.country = ?
    """, (country,))

    market = curseur.fetchall()

    connexion.close()

    return market

def get_current_market(player_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT last_market_update FROM game_state"
    )

    last_market_update = curseur.fetchone()

    connexion.close()

    if last_market_update is None:

        return get_market(player_id)

    date_last_market_update = last_market_update[0]

    if date_last_market_update == str(date.today()):

        return get_market(player_id)

    else:

        update_market()

        return get_market(player_id)

def update_market():

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT id, current_price FROM market"
    )

    market = curseur.fetchall()

    for element in market:

        progression = choice(["lower", "higher"])
        rate = randint(1, 10)

        previous_price = element["current_price"]

        if progression == "lower":

            new_price = previous_price - previous_price * rate // 100

        else:

            new_price = previous_price + previous_price * rate // 100

        curseur.execute("""
            UPDATE market
            SET current_price = ?, previous_price = ?
            WHERE id = ?
        """, (new_price, previous_price, element["id"]))

    curseur.execute(
        "UPDATE game_state SET last_market_update = ?",
        (date.today(),)
    )

    connexion.commit()
    connexion.close()

def buy_one_alcohol(player_id, alcohol_id):

    item = players.get_market_item(player_id, alcohol_id)

    if item is None:
        return

    if players.check_enough_money(player_id, item["current_price"]):

        connexion = game.get_connection()
        curseur = connexion.cursor()

        curseur.execute(
            "UPDATE players SET money = money-? WHERE id = ?",
            (item["current_price"], player_id)
        )

        inventory_item = players.get_inventory_item(player_id, alcohol_id)

        if inventory_item is None:

            curseur.execute("""
                INSERT INTO inventory (player_id, alcohol_id, amount)
                VALUES (?, ?, ?)
            """, (player_id, alcohol_id, 1))

        else:

            curseur.execute("""
                UPDATE inventory
                SET amount = amount + 1
                WHERE player_id = ? AND alcohol_id = ?
            """, (player_id, alcohol_id))

        connexion.commit()
        connexion.close()

def sell_one_alcohol(player_id, alcohol_id):

    if not check_enough_stock(player_id, alcohol_id, 1):
        return

    item = players.get_market_item(player_id, alcohol_id)

    if item is None:
        return

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "UPDATE players SET money = money + ? WHERE id = ?",
        (item["current_price"], player_id)
    )

    curseur.execute("""
        UPDATE inventory
        SET amount = amount - 1
        WHERE player_id = ? AND alcohol_id = ?
    """, (player_id, alcohol_id))

    connexion.commit()
    connexion.close()

def check_enough_stock(player_id, alcohol_id, amount):

    inventory_item = players.get_inventory_item(player_id, alcohol_id)

    if inventory_item is None:
        return False

    return inventory_item["amount"] >= amount

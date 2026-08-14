import game
import data


def get_player(player_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT * FROM players WHERE id = ?",
        (player_id,)
    )

    player = curseur.fetchone()

    connexion.close()

    return player

def get_all_players() :
    connexion = game.get_connection()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM players")
    players = curseur.fetchall()
    connexion.close()
    return players

def reset_player(player_id) :
    connexion = game.get_connection()
    curseur = connexion.cursor()

    # set money and ammo to initial amount
    curseur.execute("UPDATE players SET money = ?, ammo = ?, wounds = 0 WHERE id = ?", 
                    (data.INITIAL_MONEY, data.INITIAL_AMMO, player_id,))

    # delete stock 
    curseur.execute("DELETE FROM inventory WHERE player_id = ?", 
                    (player_id,))

    connexion.commit()
    connexion.close()

def check_enough_money(player_id, amount):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT money FROM players WHERE id = ?",
        (player_id,)
    )

    player = curseur.fetchone()

    connexion.close()

    if player is None:
        return False

    return player["money"] >= amount

def add_money(player_id, amount):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "UPDATE players SET money = money + ? WHERE id = ?",
        (amount, player_id)
    )

    connexion.commit()
    connexion.close()

def travelTo(player_id, country):

    if check_enough_money(player_id, data.FLY_COST):

        connexion = game.get_connection()
        curseur = connexion.cursor()

        curseur.execute(
            "UPDATE players SET country = ? WHERE id = ?",
            (country, player_id)
        )

        curseur.execute(
            "UPDATE players SET money = money-? WHERE id = ?",
            (data.FLY_COST, player_id)
        )

        connexion.commit()
        connexion.close()

def get_inventory_player(player_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute("""
        SELECT
            alcohols.id AS alcohol_id,
            alcohols.name,
            COALESCE(inventory.amount, 0) AS amount
        FROM alcohols
        LEFT JOIN inventory
            ON alcohols.id = inventory.alcohol_id
            AND inventory.player_id = ?
    """, (player_id,))

    inventory_player = curseur.fetchall()

    connexion.close()

    return inventory_player

def get_inventory_item(player_id, alcohol_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute("""
        SELECT *
        FROM inventory
        WHERE player_id = ? AND alcohol_id = ?
    """, (player_id, alcohol_id))

    inventory_item = curseur.fetchone()

    connexion.close()

    return inventory_item

def get_market_item(player_id, alcohol_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT country FROM players WHERE id = ?",
        (player_id,)
    )

    player = curseur.fetchone()

    if player is None:
        connexion.close()
        return None

    country = player["country"]

    curseur.execute("""
        SELECT *
        FROM market
        WHERE country = ? AND alcohol_id = ?
    """, (country, alcohol_id))

    item = curseur.fetchone()

    connexion.close()

    return item


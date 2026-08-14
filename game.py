import sqlite3
import data
from datetime import date, datetime
from random import randint, choice


def get_connection():
    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    return connexion

def buy_one_ammo(player_id):

    if check_enough_money(player_id, data.AMMO_PRICE):

        connexion = get_connection()
        curseur = connexion.cursor()

        curseur.execute(
            "UPDATE players SET money = money-?, ammo = ammo+1 WHERE id = ?",
            (data.AMMO_PRICE, player_id)
        )

        connexion.commit()
        connexion.close()

def buy_one_alcohol(player_id, alcohol_id):

    item = get_market_item(player_id, alcohol_id)

    if item is None:
        return

    if check_enough_money(player_id, item["current_price"]):

        connexion = get_connection()
        curseur = connexion.cursor()

        curseur.execute(
            "UPDATE players SET money = money-? WHERE id = ?",
            (item["current_price"], player_id)
        )

        inventory_item = get_inventory_item(player_id, alcohol_id)

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

def check_enough_money(player_id, amount):

    connexion = get_connection()
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

def get_player(player_id):

    connexion = get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT * FROM players WHERE id = ?",
        (player_id,)
    )

    player = curseur.fetchone()

    connexion.close()

    return player

def get_npc(npc_id):

    connexion = get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT * FROM npcs WHERE id = ?",
        (npc_id,)
    )

    npc = curseur.fetchone()

    connexion.close()

    return npc

def get_current_market(player_id):

    connexion = get_connection()
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

def get_market(player_id):

    connexion = get_connection()
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

def update_market():

    connexion = get_connection()
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

def init_market():

    connexion = get_connection()
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

def get_market_item(player_id, alcohol_id):

    connexion = get_connection()
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

def get_inventory_item(player_id, alcohol_id):

    connexion = get_connection()
    curseur = connexion.cursor()

    curseur.execute("""
        SELECT *
        FROM inventory
        WHERE player_id = ? AND alcohol_id = ?
    """, (player_id, alcohol_id))

    inventory_item = curseur.fetchone()

    connexion.close()

    return inventory_item

def get_inventory_player(player_id):

    connexion = get_connection()
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

def travelTo(player_id, country):

    if check_enough_money(player_id, data.FLY_COST):

        connexion = get_connection()
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

def sell_one_alcohol(player_id, alcohol_id):

    if not check_enough_stock(player_id, alcohol_id, 1):
        return

    item = get_market_item(player_id, alcohol_id)

    if item is None:
        return

    connexion = get_connection()
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

    inventory_item = get_inventory_item(player_id, alcohol_id)

    if inventory_item is None:
        return False

    return inventory_item["amount"] >= amount

def check_enough_ammo(shooter_id, amount):

    shooter = get_player(shooter_id)

    if shooter is None:
        return False

    return shooter["ammo"] >= amount

def remove_one_ammo(shooter_id):

    connexion = get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "UPDATE players SET ammo = ammo-1 WHERE id = ?",
        (shooter_id,)
    )

    connexion.commit()
    connexion.close()

def get_target(target_id, npc_or_player):

    connexion = get_connection()
    curseur = connexion.cursor()

    if npc_or_player == "player":

        curseur.execute(
            "SELECT * FROM players WHERE id = ?",
            (target_id,)
        )

        target = curseur.fetchone()

    elif npc_or_player == "npc":

        curseur.execute(
            "SELECT * FROM npcs WHERE id = ?",
            (target_id,)
        )

        target = curseur.fetchone()

    else:

        target = None

    connexion.close()

    return target

def add_wound(target_id, npc_or_player):

    connexion = get_connection()
    curseur = connexion.cursor()

    if npc_or_player == "player":

        curseur.execute(
            "UPDATE players SET wounds = wounds+1 WHERE id = ?",
            (target_id,)
        )

    elif npc_or_player == "npc":

        curseur.execute(
            "UPDATE npcs SET wounds = wounds+1 WHERE id = ?",
            (target_id,)
        )

    connexion.commit()
    connexion.close()

def shoot(shooter_id, target_id, npc_or_player):

    result = {}

    # Check if the shooter has enough ammo
    if not check_enough_ammo(shooter_id, 1):

        result = {
            "message": "Not enough ammo"
        }

        return result

    # Get target
    target = get_target(target_id, npc_or_player)

    if target is None:

        result = {
            "message": "Target not found."
        }

        return result

    # Check if target is already dead
    if target["wounds"] == 3:

        result = {
            "message": "The target is already dead..."
        }

        return result

    # Shoot: remove one ammo
    remove_one_ammo(shooter_id)

    # Get shooter
    shooter = get_player(shooter_id)

    # Check if target is in the same country
    if target["country"] != shooter["country"]:

        result = {
            "message": "Your target is not in this country..."
        }

        return result

    # Add wound
    add_wound(target_id, npc_or_player)

    # Check if this was the third wound
    if target["wounds"] + 1 == 3:

        death(shooter_id, target_id, npc_or_player)

        result = {
            "message": "The target is dead ! GG !"
        }

    else:

        result = {
            "message": "The target has been touched ! But still alive..."
        }

    return result

def death(shooter_id, target_id, npc_or_player):

    # Reset the target if it's a player,
    # delete it if it's a NPC

    if npc_or_player == "player":

        target = get_player(target_id)

        # Player death logic goes here

    elif npc_or_player == "npc":

        target = get_npc(target_id)

        if target is None:
            return

        delete_npc(target_id)

    else:

        return

    if target is None:
        return

    bounty = target["bounty"]

    add_money(shooter_id, bounty)

def add_money(player_id, amount):

    connexion = get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "UPDATE players SET money = money + ? WHERE id = ?",
        (amount, player_id)
    )

    connexion.commit()
    connexion.close()

def delete_npc(npc_id):

    connexion = get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "DELETE FROM npcs WHERE id = ?",
        (npc_id,)
    )

    connexion.commit()
    connexion.close()

def init_npcs(amount_npcs_to_create):

    connexion = get_connection()
    curseur = connexion.cursor()

    npcs = 0

    while npcs < amount_npcs_to_create:

        # Create a random name for the NPC
        first_name = choice(data.RANDOM_NAMES)
        last_name = choice(data.RANDOM_NAMES)
        npc_name = first_name + " " + last_name

        # Give him a random country where to start
        npc_country = choice(data.COUNTRIES)

        # Give him a random bounty between 100 and 1000 $
        npc_bounty = randint(100, 1000)

        # Init wounds = 0
        npc_wounds = 0

        # Init last move
        npc_last_move = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        curseur.execute("""
            INSERT INTO npcs
            (name, country, bounty, wounds, last_move)
            VALUES (?, ?, ?, ?, ?)
        """, (
            npc_name,
            npc_country,
            npc_bounty,
            npc_wounds,
            npc_last_move
        ))

        npcs += 1

    connexion.commit()
    connexion.close()

def get_all_npcs() :
    connexion = get_connection()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM npcs")
    npcs = curseur.fetchall()
    connexion.close()
    return npcs

def get_all_players() :
    connexion = get_connection()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM players")
    players = curseur.fetchall()
    connexion.close()
    return players
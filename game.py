import sqlite3
import data
from datetime import date, datetime
from random import randint, choice

def buy_one_ammo(player_id):

    if check_enough_money(player_id, data.AMMO_PRICE):

        connexion = sqlite3.connect("mafia.db")
        connexion.row_factory = sqlite3.Row
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

        connexion = sqlite3.connect("mafia.db")
        connexion.row_factory = sqlite3.Row
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

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
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

# Get the current market for the country where the player is. 
# Update the market if necessary
def get_current_market(player_id):

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT last_market_update FROM game_state"
    )

    last_market_update = curseur.fetchone()

    connexion.close()

    # Le marché doit normalement déjà être initialisé
    if last_market_update is None:
        return []

    date_last_market_update = last_market_update[0]

    # Market already updated today
    if date_last_market_update == str(date.today()):

        return get_market(player_id)

    # New day -> update prices
    update_market()

    return get_market(player_id)

# Used by get_current_market() 
def get_market(player_id):

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
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

# used by get_current_market() to update the prices everyday
def update_market():

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
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

    connexion = sqlite3.connect("mafia.db")
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

    # Create game state
    curseur.execute("""
        INSERT OR REPLACE INTO game_state
        (id, last_market_update)
        VALUES (?, ?)
    """, (1, date.today()))

    connexion.commit()
    connexion.close()

    print("market initialized")


def get_market_item(player_id, alcohol_id):

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
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

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
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

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
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

        connexion = sqlite3.connect("mafia.db")
        connexion.row_factory = sqlite3.Row
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

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
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

def init_npcs(nbr) :

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    amount_npcs_to_create = (nbr)
    npcs = 0
    while npcs < amount_npcs_to_create :

        # Create a random name for the npc's by combining 2 names from RANDOM_NAMES
        first_name = choice(data.RANDOM_NAMES)
        last_name = choice(data.RANDOM_NAMES)
        npc_name = first_name+" "+last_name

        # Give him a random country where to start
        npc_country = choice(data.COUNTRIES)

        # Give him a random bounty between 100 and 1000 $
        npc_bounty = randint(100, 1000)

        # Init wounds = 0
        npc_wounds = 0

        #Init last move = now
        npc_last_move = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # add it in database
        curseur.execute("INSERT INTO npcs (name, country, bounty, wounds, last_move) VALUES (?, ?, ?, ?, ?)", 
                        (npc_name, npc_country, npc_bounty, npc_wounds, npc_last_move ))

        npcs += 1

    connexion.commit()
    connexion.close()

def get_all_npcs() :
    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    curseur.execute("SELECT * FROM npcs")

    npcs = curseur.fetchall()
    connexion.close()

    return npcs


def get_all_players() :
    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    curseur.execute("SELECT * FROM players")

    players = curseur.fetchall()
    connexion.close()


    return players

def shoot(shooter_id, target_id, npc_or_player) :

    result = {}

    #check if the shooter has enough ammo (at least 1)

    # if he has no ammo : return a message 
    if check_enough_ammo(shooter_id, 1) == False :
        result = {
            "message" : "Not enough ammo"
        }
        return result

    else : 
        # check if the target is alive (different tables : players or npcs)
        target = get_target(target_id, npc_or_player)

        if target is None:
            result = {
                "message": "Target not found."
            }
            return result

        # if not alive : return a message
        if target['wounds'] == 3 :
            result = {
                "message" : "The target is already dead..."
            }
            return result
        else :
            # shoot : -1 ammo for the shooter
            remove_one_ammo(shooter_id)

            #check if the target is in the same country than the shooter
            shooter = get_player(shooter_id)
            
            # if not in the same country : return a messsage
            if target['country'] != shooter['country'] :
                result = {
                    "message" : "Your target is not in this country..."
                }
            else :
            
                # add a wound to the target
                add_wound(target_id, npc_or_player)

                # if 3 wounds = death
                if target['wounds']+1 == 3 :
                    death(target_id, npc_or_player)
                    result = {
                        "message" : "The target is dead ! GG !"
                    }
                else :
                    result = {
                        "message" : "The target has been touched ! But still alive..."
                    }
    
    return result

def check_enough_ammo(shooter_id, amount) :
    shooter = get_player(shooter_id)

    if shooter is None:
        return False

    if shooter['ammo'] >= amount :
        return True
    else : 
        return False

def get_target(target_id, npc_or_player):
    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    if npc_or_player == "player" :
        curseur.execute("SELECT * FROM players WHERE id = ?", 
                        (target_id,))
        target = curseur.fetchone()
    elif npc_or_player == "npc" :
        curseur.execute("SELECT * FROM npcs WHERE id = ?", 
                        (target_id,))
        target = curseur.fetchone()
    else:
        target = None

    connexion.close()
    return target

def add_wound(target_id, npc_or_player) :

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    if npc_or_player == "player" :
        curseur.execute("UPDATE players SET wounds = wounds+1 WHERE id = ?",
                        (target_id,))
    elif npc_or_player == "npc" :
        curseur.execute("UPDATE npcs SET wounds = wounds+1 WHERE id = ?", 
                        (target_id,))

    connexion.commit()
    connexion.close()

def remove_one_ammo(shooter_id) :
    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row
    curseur = connexion.cursor()

    curseur.execute("UPDATE players SET ammo = ammo-1 WHERE id = ?", 
                                (shooter_id,))

    connexion.commit()
    connexion.close()


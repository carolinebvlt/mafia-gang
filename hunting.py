import game
import data
import players
import npcs

def buy_one_ammo(player_id):

    if players.check_enough_money(player_id, data.AMMO_PRICE):

        connexion = game.get_connection()
        curseur = connexion.cursor()

        curseur.execute(
            "UPDATE players SET money = money-?, ammo = ammo+1 WHERE id = ?",
            (data.AMMO_PRICE, player_id)
        )

        connexion.commit()
        connexion.close()

def remove_one_ammo(shooter_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "UPDATE players SET ammo = ammo-1 WHERE id = ?",
        (shooter_id,)
    )

    connexion.commit()
    connexion.close()

def check_enough_ammo(shooter_id, amount):

    shooter = players.get_player(shooter_id)

    if shooter is None:
        return False

    return shooter["ammo"] >= amount

def death(shooter_id, target_id, npc_or_player):

    # Reset the target if it's a player,
    # delete it if it's a NPC

    if npc_or_player == "player":

        target = players.get_player(target_id)

        if target is None:
            return
        
        players.reset_player(target_id)


    elif npc_or_player == "npc":

        target = npcs.get_npc(target_id)

        if target is None:
            return

        npcs.delete_npc(target_id)

    else:

        return

    if target is None:
        return

    bounty = target["bounty"]

    players.add_money(shooter_id, bounty)

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
    shooter = players.get_player(shooter_id)

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

def add_wound(target_id, npc_or_player):

    connexion = game.get_connection()
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

def get_target(target_id, npc_or_player):

    connexion = game.get_connection()
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

def bounty_on_player(player_id, target_id, bounty) :
    # check if the player has enough money
    if not players.check_enough_money(player_id, bounty) :
        result = {
            "message":"You don't have enough money..."
        }
        return result
    else :
        # Put the bounty on the target and if it works, substract money
        modify_bounty(target_id, bounty)
        players.substract_money(player_id, bounty)
        result = {
            "message":"Bounty on the target's head !"
        }
        return result

def modify_bounty(target_id, amount) :
    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "UPDATE players SET bounty = bounty + ? WHERE id = ?",
        (amount, target_id)
    )

    connexion.commit()
    connexion.close()

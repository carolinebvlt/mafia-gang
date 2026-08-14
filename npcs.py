import game
import data
from datetime import date, datetime
from random import randint, choice

def init_npcs(amount_npcs_to_create):

    connexion = game.get_connection()
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

def get_npc(npc_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "SELECT * FROM npcs WHERE id = ?",
        (npc_id,)
    )

    npc = curseur.fetchone()

    connexion.close()

    return npc

def get_all_npcs() :
    connexion = game.get_connection()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM npcs")
    npcs = curseur.fetchall()
    connexion.close()
    return npcs

def delete_npc(npc_id):

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        "DELETE FROM npcs WHERE id = ?",
        (npc_id,)
    )

    connexion.commit()
    connexion.close()

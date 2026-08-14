from flask import Flask, render_template, request, session, redirect, flash
import sqlite3
from data import COUNTRIES, REWARD_30_MIN_WORK, INITIAL_MONEY, INITIAL_AMMO
import game
import players
import market_functions
import hunting
import npcs
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "mafia-secret-key"


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        if "player_id" in request.form:

            session["player_id"] = request.form["player_id"]

            # Le nouveau joueur n'hérite pas du travail de l'ancien
            session.pop("work_end", None)
            session.pop("work_duration", None)

            return redirect("/player")

        name = request.form["name"]
        country = request.form["country"]
        money = INITIAL_MONEY
        ammo = INITIAL_AMMO

        connexion = sqlite3.connect("mafia.db")
        curseur = connexion.cursor()

        curseur.execute("""
            INSERT INTO players (name, money, country, ammo)
            VALUES (?, ?, ?, ?)
        """, (name, money, country, ammo))

        connexion.commit()

        player_id = curseur.lastrowid
        session["player_id"] = player_id

        connexion.close()

    connexion = sqlite3.connect("mafia.db")
    connexion.row_factory = sqlite3.Row

    curseur = connexion.cursor()

    curseur.execute("SELECT * FROM players")

    players = curseur.fetchall()

    connexion.close()

    return render_template(
        "index.html",
        players=players,
        countries=COUNTRIES
    )


@app.route("/player")
def player():

    player_id = session.get("player_id")

    player = players.get_player(player_id)

    return render_template(
        "player.html",
        player=player,
        countries=COUNTRIES
    )


@app.route("/buy_ammo", methods=["POST"])
def buy_ammo():

    player_id = session.get("player_id")

    hunting.buy_one_ammo(player_id)

    return redirect("/hunt")


@app.route("/market")
def market():

    player_id = session.get("player_id")

    player = players.get_player(player_id)
    market = market_functions.get_current_market(player_id)
    inventory_player = players.get_inventory_player(player_id)

    return render_template(
        "market.html",
        player=player,
        market=market,
        inventory_player=inventory_player,
        countries=COUNTRIES
    )


@app.route("/buy_alcohol", methods=["POST"])
def buy_alcohol():

    player_id = session.get("player_id")
    alcohol_id = request.form["alcohol_id"]

    market_functions.buy_one_alcohol(player_id, alcohol_id)

    return redirect("/market")


@app.route("/travel", methods=["POST"])
def travel():

    player_id = session.get("player_id")
    country = request.form["travel"]

    
    players.travelTo(player_id, country)

    return redirect("/player")

@app.route("/sell_alcohol", methods=["POST"])
def sell_alcohol():

    player_id = session.get("player_id")
    alcohol_id = request.form["alcohol_id"]

    print(alcohol_id)
    market_functions.sell_one_alcohol(player_id, alcohol_id)

    return redirect("/market")

@app.route("/hunt")
def hunt():

    player_id = session.get("player_id")
    player = players.get_player(player_id)
    npcs_list = npcs.get_all_npcs()
    all_players = players.get_all_players()

    return render_template(
        "hunt.html",
        player=player,
        countries=COUNTRIES,
        npcs = npcs_list,
        players = all_players
    )

@app.route("/shoot_npc", methods=["POST"])
def shoot_npc():
    npc_target_id = request.form["npc_id"]
    shooter = session.get("player_id")
    result = hunting.shoot(shooter, npc_target_id, "npc")
    flash(result['message'])
    return redirect("/hunt")

@app.route("/shoot_player", methods=["POST"])
def shoot_player():
    player_target_id = request.form["player_id"]
    shooter = session.get("player_id")
    result = hunting.shoot(shooter, player_target_id, "player")
    flash(result['message'])
    return redirect("/hunt")


@app.route("/work", methods=["POST"])
def work():
    player_id = session.get("player_id")

    working_duration = int(request.form["work_duration"])

    # Calcul de l'heure à laquelle le travail sera terminé
    end_time = datetime.now() + timedelta(minutes=working_duration)

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        """
        UPDATE players
        SET work_end = ?, work_duration = ?
        WHERE id = ?
        """,
        (end_time.timestamp(), working_duration, player_id)
    )

    connexion.commit()
    connexion.close()

    flash(f"You started working for {working_duration} min.")

    return redirect("/player")

@app.route("/work/finish", methods=["POST"])
def finish_work():

    player_id = session.get("player_id")

    player = players.get_player(player_id)

    working_duration = player["work_duration"]

    reward = working_duration // 30 * 250

    players.add_money(player_id, reward)

    connexion = game.get_connection()
    curseur = connexion.cursor()

    curseur.execute(
        """
        UPDATE players
        SET work_end = NULL, work_duration = NULL
        WHERE id = ?
        """,
        (player_id,)
    )

    connexion.commit()
    connexion.close()

    flash(f"You finished working! You earned ${reward}.")

    return redirect("/player")


app.run(debug=True)
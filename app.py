from flask import Flask, render_template, request, session, redirect, flash
import sqlite3
from data import COUNTRIES
import game

app = Flask(__name__)
app.secret_key = "mafia-secret-key"


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        if "player_id" in request.form:

            session["player_id"] = request.form["player_id"]

            return redirect("/player")

        name = request.form["name"]
        country = request.form["country"]
        money = 1000
        ammo = 3

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

    player = game.get_player(player_id)

    return render_template(
        "player.html",
        player=player,
        countries=COUNTRIES
    )


@app.route("/buy_ammo", methods=["POST"])
def buy_ammo():

    player_id = session.get("player_id")

    game.buy_one_ammo(player_id)

    return redirect("/player")


@app.route("/market")
def market():

    player_id = session.get("player_id")

    player = game.get_player(player_id)
    market = game.get_current_market(player_id)
    inventory_player = game.get_inventory_player(player_id)

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

    game.buy_one_alcohol(player_id, alcohol_id)

    return redirect("/market")


@app.route("/travel", methods=["POST"])
def travel():

    player_id = session.get("player_id")
    country = request.form["travel"]

    
    game.travelTo(player_id, country)

    return redirect("/player")

@app.route("/sell_alcohol", methods=["POST"])
def sell_alcohol():

    player_id = session.get("player_id")
    alcohol_id = request.form["alcohol_id"]

    print(alcohol_id)
    game.sell_one_alcohol(player_id, alcohol_id)

    return redirect("/market")

@app.route("/hunt")
def hunt():

    player_id = session.get("player_id")
    player = game.get_player(player_id)
    npcs = game.get_all_npcs()
    players = game.get_all_players()

    return render_template(
        "hunt.html",
        player=player,
        countries=COUNTRIES,
        npcs = npcs,
        players = players
    )

@app.route("/shoot_npc", methods=["POST"])
def shoot_npc():
    npc_target_id = request.form["npc_id"]
    shooter = session.get("player_id")
    result = game.shoot(shooter, npc_target_id, "npc")
    flash(result['message'])
    return redirect("/hunt")

@app.route("/shoot_player", methods=["POST"])
def shoot_player():
    player_target_id = request.form["player_id"]
    shooter = session.get("player_id")
    result = game.shoot(shooter, player_target_id, "player")
    flash(result['message'])
    return redirect("/hunt")

app.run(debug=True)
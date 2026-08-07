from flask import Flask, render_template, request, session, redirect
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
        player=player
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

    return render_template(
        "market.html",
        player = player,
        current_market=market
    )


app.run(debug=True)
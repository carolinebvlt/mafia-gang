import database
import game
import data

database.init_database()
game.init_market()
game.init_npcs(data.INITIAL_NPCS_NUMBER)
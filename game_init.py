import database
import game
import market_functions
import npcs
import data

database.init_database()
market_functions.init_market()
npcs.init_npcs(data.INITIAL_NPCS_NUMBER)
import game
import players
import data
from random import randint


def decide_to_control(player_id):
    player = players.get_player(player_id)
    points = player["crime_points"]

    number = randint(1, 50)

    match points:
        case points if points >= data.crime_levels[5]:
            return number <= 40

        case points if points >= data.crime_levels[4]:
            return number <= 25

        case points if points >= data.crime_levels[3]:
            return number <= 10

        case points if points >= data.crime_levels[2]:
            return number <= 5

        case points if points >= data.crime_levels[1]:
            return number <= 1

    return False
    
def control(player_id):
    player = players.get_player(player_id)
    points = player["crime_points"]
    match points:
        case points if points >= data.crime_levels[5]:
            penalty = 1000
            return penalty 

        case points if points >= data.crime_levels[4]:
            penalty = 500
            return penalty 

        case points if points >= data.crime_levels[3]:
            penalty = 100
            return penalty 

        case points if points >= data.crime_levels[2]:
            penalty = 50
            return penalty 

        case points if points >= data.crime_levels[1]:
            penalty = 10
            return penalty 

    return 1
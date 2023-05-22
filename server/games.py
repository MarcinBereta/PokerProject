# from SocketServer import *
from PokerGame import PokerGame
import random

games = {}
games_lobbies = {}

def pass_data(data):
    print(f"games.data_request()")
    for i in games.keys():
        if games[i] is not None:
            for j in games[i].list_of_players:
                if j.player_id == data['user_id']:
                    game_data = games[i].get_data()
                    game_data['cards'] = j.get_cards()
                    game_data['valid_moves'] = j.potential_moves()
                    game_data['max_size'] = games_lobbies[i]
                    
                    # sio.enter_room(sid, i)
                    print(game_data)
                    return {'data': game_data, 'game_id': i, 'game_sid': i}

def create_new_game(data):
    hash = random.getrandbits(128)
    games[hash] = PokerGame()
    return hash

def update_data(data):
    print('game_move_played()')

    if games[data['gameId']].get_actual_id() != data['playerId']:
        return

    games[data['gameId']].calculate_move(data['move_id'])
    game_data = games[data['gameId']].get_data()
    game_data['max_size'] = games_lobbies[data['gameId']]

    print("games.update_data()")

    if games[data['gameId']].winner is not None:
        print('finish_game')
        games[data['gameId']] = None
        return True, game_data

    game_data['valid_moves'] = games[data['gameId']].list_of_players[games[data['gameId']].player_index].potential_moves()
    return False, game_data
    
def start_game(room_id, players, max_players, game_id, data):
    print(f"games.start_game()")
    games[game_id].config(data)
    games[game_id].parse_players(players)
    games[game_id].start()
    games_lobbies[game_id] = max_players

# @sio.on('change_tour')
def join_lobby(sid):
    print("Changing tour")


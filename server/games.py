from SocketServer import *
from PokerGame import PokerGame
import random

games = {}

@sio.on('create_live_game')
def create_new_game(sid, data):
    hash = random.getrandbits(128)
    games[hash] = PokerGame()
    sio.emit('game_created', {'game_id': hash})


@sio.on('game_move_played')
def update_data(sid, data):
    games[data['gameId']].calculate_move(data['move_id'])

    if games[data['gameId']].winner is not None:
        sio.emit('game_update', game_data, room=i.player_id)

    game_data = games[data['gameId']].get_data()
    for i in games[data['gameId']].list_of_active_players:
        game_data['valid_moves'] = i.potential_moves()
        sio.emit('game_update', game_data, room=i.player_id)

@sio.on('change_tour')
def join_lobby(sid):
    print("Changing tour")


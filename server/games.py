from SocketServer import *
from PokerGame import PokerGame
import random

games = {}
games_lobbies = {}

@sio.on('data_request')
def pass_data(sid, data):
    print(games)
    print(f"{sid} requested data [{data}]")
    for i in games.keys():
        for j in games[i].list_of_players:
            if j.player_id == data['user_id']:
                game_data = games[i].get_data()
                game_data['cards'] = j.get_cards()
                game_data['valid_moves'] = j.potential_moves()
                game_data['max_size'] = games_lobbies[i]
                
                sio.enter_room(sid, i)
                return {'data': game_data, 'game_id': i}

@sio.on('create_live_game')
def create_new_game(sid, data):
    print(f"games.on('create_live_game')")
    hash = random.getrandbits(128)
    games[hash] = PokerGame()
    sio.emit('game_created', {'game_id': hash}, room=data['room_id'])
    return {'game_id': hash}

@sio.on('leave_game')
def leave_game(sid, data):
    print(f"leave_game()")
    sio.leave_room(sid, data['game_id'])


@sio.on('game_move_played')
def update_data(sid, data):
    print('game_move_played()')
    print(f"act: {games[data['gameId']].get_actual_id()} data: {data}" )

    if games[data['gameId']].get_actual_id() != data['playerId']:
        return

    games[data['gameId']].calculate_move(data['move_id'])
    game_data = games[data['gameId']].get_data()
    game_data['max_size'] = games_lobbies[data['gameId']]

    print("games.update_data()")

    if games[data['gameId']].winner is not None:
        print('finish_game')
        sio.emit('finish_game', game_data, room=data['gameId'])
        return

    game_data['valid_moves'] = games[data['gameId']].list_of_players[games[data['gameId']].player_index].potential_moves()
    sio.emit('game_update', game_data, room= data['gameId'])



@sio.on('change_tour')
def join_lobby(sid):
    print("Changing tour")


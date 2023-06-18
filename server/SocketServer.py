import random
import socketio
from waitress import serve
import eventlet
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)
import Lobbies
import Games

@sio.event
def connect(sid, environ):
   print(sid, 'connected    ')

@sio.event
def disconnect(sid):
   print(sid, 'disconnected')

# Lobby Management 
@sio.on('join_lobby')
def join_lobby(sid):
    print(f"SocketServer.on('join_lobby')")
    sio.enter_room(sid, 'lobby')
    return {'lobbies': Lobbies.lobbies}

@sio.on('leave_game')
def leave_game(sid, data):
    print("server.leave_game")
    # Games.player_left_game(data)
    sio.enter_room(sid, 'lobby')
    is_actual, game_data = Games.player_left_game(data)

    print(game_data)

    if is_actual:
        sio.emit('finish_game', game_data, room=data['game_id'])

    sio.emit('game_update', game_data, room= data['game_id'])
    sio.emit('lobby_update', {'lobbies':Lobbies.lobbies}, room='lobby')


@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("Leaving lobby")
    sio.leave_room(sid, 'lobby')
    sio.emit('lobby_update', {'lobbies':Lobbies.lobbies}, room='lobby')

# Room Management 
@sio.on('create_room')
def create_room(sid, data):
    print("socketServer.on('create_room')")
    sio.leave_room(sid, 'lobby')

    lobbyId = Lobbies.create_room(data)

    leave_lobby(sid, None)
    sio.enter_room(sid, lobbyId)
    sio.enter_room(sid, data['playerId'])

    sio.emit('lobby_update', { 'lobbies':Lobbies.lobbies}, room='lobby')
    return {'status': 'success', 'roomId': lobbyId, 'room': Lobbies.lobbies[lobbyId]}

@sio.on('leave_room')
def leave_room(sid, data):
    sio.leave_room(sid, data['roomId'])
    sio.leave_room(sid, (data['playerId'] + '_' +data['roomId']))

    Lobbies.leave_room(data)

    sio.enter_room(sid, 'lobby')
    sio.emit('lobby_update', { 'lobbies':Lobbies.lobbies}, room='lobby')

@sio.on('room_change_ready')
def room_change_ready(sid, data):
    print(f"SocketServer.on('room_change_ready')")
    Lobbies.change_ready(data)

    # sio.emit('room_player_ready', {'content': 'A player has changed their ready status!'}, room=data['roomId'])
    sio.emit('room_update', {'room': Lobbies.lobbies[data['roomId']]}, room=data['roomId'])
    sio.emit('lobby_update', { 'lobbies':Lobbies.lobbies}, room='lobby')

    # print(lobbies[data['roomId']])
    return { 'room': Lobbies.lobbies[data['roomId']]}

@sio.on('join_room')
def join_room(sid, data):
    print(f"SocketServer.on('join_room')")
    sio.enter_room(sid, data['roomId'])
    sio.enter_room(sid, data['playerId'] + '_' + data['roomId'])
    sio.leave_room(sid, 'lobby')
    # lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False, 'playerId': data['playerId']})

    Lobbies.join_room(data)

    sio.emit('lobby_update', {'lobbies':Lobbies.lobbies}, room='lobby')
    sio.emit('room_update', {'room':Lobbies.lobbies[data['roomId']]}, room=data['roomId'])

    sio.enter_room(sid, (data['playerId'] + '_'+ data['roomId']))
    return {'status': 'success', 'roomId': data['roomId'], 'room': Lobbies.lobbies[data['roomId']]}

# Game Management
@sio.on('create_live_game')
def create_live_game(sid, data):
    hash = Games.create_new_game(data)
    sio.emit('game_created', {'game_id': hash}, room=data['room_id'])
    return {'game_id': hash}

@sio.on('game_move_played')
def update_data(sid, data):
    is_actual, game_data = Games.update_data(data)

    if is_actual:
        sio.emit('finish_game', game_data, room=data['gameId'])

    sio.emit('game_update', game_data, room= data['gameId'])
    return game_data 

@sio.on('room_start_game')
def room_start_game(sid, data):
    print(f"SocketServer.on('room_start_game')")
    if True:
        Games.start_game(data['gameId'], Lobbies.lobbies[data['roomId']])

        sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['roomId'])
        sio.emit('lobby_update', { 'lobbies':Lobbies.lobbies}, room='lobby')

# Info
@sio.on('set_data')
def get_connection(sid, data):
    sio.enter_room(sid, str(data['player_id']))
    sio.emit('room_update', {'room': Lobbies.lobbies[data['roomId']]}, room=data['roomId'])


@sio.on('data_request')
def data_request(sid, data):
    print(f"SocketServer.on('data_request')")
    games_config = Games.pass_data(data)
    print(f"[DATA] {games_config} \n")
    
    if games_config is None:
        return None
    
    sio.enter_room(sid, data['game_id'])
    return games_config

@sio.on('start_round')
def start_next_round(sid, data):
    Games.play_next_round(data)
    sio.emit('next_round', room=data['game_id'])

eventlet.wsgi.server(eventlet.listen(('', 5500)), app)

import random
import socketio
from waitress import serve
import eventlet
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)
import lobbies
import games

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
    return {'lobbies': lobbies.lobbies}

@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("Leaving lobby")
    sio.leave_room(sid, 'lobby')
    sio.emit('lobby_update', {'lobbies':lobbies.lobbies}, room='lobby')

# Room Management 
@sio.on('create_room')
def create_room(sid, data):
    print("socketServer.on('create_room')")
    sio.leave_room(sid, 'lobby')

    lobbyId = lobbies.create_room(data)

    leave_lobby(sid, None)
    sio.enter_room(sid, lobbyId)
    sio.enter_room(sid, data['playerId'])

    sio.emit('lobby_update', { 'lobbies':lobbies.lobbies}, room='lobby')
    return {'status': 'success', 'roomId': lobbyId, 'room': lobbies.lobbies[lobbyId]}

@sio.on('leave_room')
def leave_room(sid, data):
    sio.leave_room(sid, data['roomId'])
    sio.leave_room(sid, (data['playerId'] + '_' +data['roomId']))

    lobbies.leave_room(data)

    sio.enter_room(sid, 'lobby')
    sio.emit('lobby_update', { 'lobbies':lobbies.lobbies}, room='lobby')

@sio.on('room_change_ready')
def room_change_ready(sid, data):
    print(f"SocketServer.on('room_change_ready')")
    lobbies.change_ready(data)

    # sio.emit('room_player_ready', {'content': 'A player has changed their ready status!'}, room=data['roomId'])
    sio.emit('room_update', {'room': lobbies.lobbies[data['roomId']]}, room=data['roomId'])
    sio.emit('lobby_update', { 'lobbies':lobbies.lobbies}, room='lobby')

    # print(lobbies[data['roomId']])
    return { 'room': lobbies.lobbies[data['roomId']]}

@sio.on('join_room')
def join_room(sid, data):
    print(f"SocketServer.on('join_room')")
    sio.enter_room(sid, data['roomId'])
    sio.enter_room(sid, data['playerId'] + '_' + data['roomId'])
    sio.leave_room(sid, 'lobby')
    # lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False, 'playerId': data['playerId']})

    lobbies.join_room(data)

    sio.emit('lobby_update', {'lobbies':lobbies.lobbies}, room='lobby')
    sio.emit('room_update', {'room':lobbies.lobbies[data['roomId']]}, room=data['roomId'])

    sio.enter_room(sid, (data['playerId'] + '_'+ data['roomId']))
    return {'status': 'success', 'roomId': data['roomId'], 'room': lobbies.lobbies[data['roomId']]}

# Game Management
@sio.on('create_live_game')
def create_live_game(sid, data):
    hash = games.create_new_game(data)
    sio.emit('game_created', {'game_id': hash}, room=data['room_id'])
    return {'game_id': hash}

@sio.on('game_move_played')
def update_data(sid, data):
    is_actual, game_data = games.update_data(data)

    if is_actual:
        sio.emit('finish_game', game_data, room=data['gameId'])

    sio.emit('game_update', game_data, room= data['gameId'])

@sio.on('room_start_game')
def room_start_game(sid, data):
    print(f"SocketServer.on('room_start_game')")
    if True:

        games.start_game(
            data['roomId'],
            lobbies.lobbies[data['roomId']]['players'],
            lobbies.lobbies[data['roomId']]['maxPlayers'],
            data['gameId'], 
            lobbies.lobbies[data['roomId']]
        )

        sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['roomId'])
        sio.emit('lobby_update', { 'lobbies':lobbies.lobbies}, room='lobby')

# Info
@sio.on('set_data')
def get_connection(sid, data):
    sio.enter_room(sid, str(data['player_id']))
    sio.emit('room_update', {'room': lobbies.lobbies[data['roomId']]}, room=data['roomId'])


@sio.on('data_request')
def data_request(sid, data):
    games_config = games.pass_data(data)
    sio.enter_room(sid, games_config['game_sid'])

    return {
        'data': games_config['data'],
        'game_id': games_config['game_id']
    }


eventlet.wsgi.server(eventlet.listen(('', 5500)), app)

import socketio
import eventlet
import Lobbies
import Games

sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)


@sio.event
def connect(sid, environ):
    print(sid, 'connected    ')


@sio.event
def disconnect(sid):
    print(sid, 'disconnected')


# Lobby Management
@sio.on('join_lobby')
def join_lobby(sid):
    print(f"SocketServer.join_lobby()")
    sio.enter_room(sid, 'lobby')
    return {'lobbies': Lobbies.lobbies}


@sio.on('leave_game')
def leave_game(sid, data):
    print("SocketServer.leave_game()")
    game_data = Games.player_left_game(data)

    Lobbies.leave_room(data)
    sio.leave_room(sid, data['game_id'])

    if game_data['winner'] is not None:
        sio.emit('finish_game', game_data, room=data['game_id'])

    sio.emit('game_update', game_data, room= data['game_id'])
    sio.emit('lobby_update', {'lobbies':Lobbies.lobbies}, room='lobby')


@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("SocketServer.leave_lobby()")
    sio.leave_room(sid, 'lobby')
    sio.emit('lobby_update', {'lobbies': Lobbies.lobbies}, room='lobby')


# Room Management
@sio.on('create_room')
def create_room(sid, data):
    print("socketServer.create_room()")
    sio.leave_room(sid, 'lobby')

    lobbyId = Lobbies.create_room(data)

    leave_lobby(sid, None)
    sio.enter_room(sid, lobbyId)
    sio.enter_room(sid, data['playerId'])

    sio.emit('lobby_update', {'lobbies': Lobbies.lobbies}, room='lobby')
    return {'status': 'success', 'roomId': lobbyId, 'room': Lobbies.lobbies[lobbyId]}


@sio.on('leave_room')
def leave_room(sid, data):
    print("socketServer.leave_room()")
    sio.leave_room(sid, data['roomId'])
    sio.leave_room(sid, data['playerId'])

    Lobbies.leave_room(data)

    sio.enter_room(sid, 'lobby')
    sio.emit('lobby_update', {'lobbies': Lobbies.lobbies}, room='lobby')


@sio.on('room_change_ready')
def room_change_ready(sid, data):
    print(f"SocketServer.room_change_ready()")
    Lobbies.change_ready(data)

    sio.emit('room_update', {'room': Lobbies.lobbies[data['roomId']]}, room=data['roomId'])
    sio.emit('lobby_update', {'lobbies': Lobbies.lobbies}, room='lobby')

    return { 'room': Lobbies.lobbies[data['roomId']]}

@sio.on('join_room')
def join_room(sid, data):
    print(f"SocketServer.join_room()")
    sio.enter_room(sid, data['roomId'])
    sio.leave_room(sid, 'lobby')

    Lobbies.join_room(data)

    sio.emit('lobby_update', {'lobbies': Lobbies.lobbies}, room='lobby')
    sio.emit('room_update', {'room': Lobbies.lobbies[data['roomId']]}, room=data['roomId'])

    return {'status': 'success', 'roomId': data['roomId'], 'room': Lobbies.lobbies[data['roomId']]}


# Game Management
@sio.on('create_live_game')
def create_live_game(sid, data):
    print("socketServer.create_live_game()")

    for player in Lobbies.lobbies[data['room_id']]['players']:
        if player['ready'] is False:
            return {'content': 'Players not ready!'}

    hash = Games.create_new_game(data)
    sio.emit('game_created', {'game_id': hash}, room=data['room_id'])
    return {'game_id': hash}


@sio.on('game_move_played')
def update_data(sid, data):
    print("socketServer.game_move_played()")
    game_data = Games.update_data(data)

    if game_data['winner'] is not None:
        sio.emit('finish_game', game_data, room = data['gameId'])

    sio.emit('game_update', game_data, room=data['gameId'])
    return game_data


@sio.on('room_start_game')
def room_start_game(sid, data):
    print(f"SocketServer.room_start_game()")
    if True:
        Games.games_lobbies[data['roomId']] = data['gameId']
        Games.start_game(data['gameId'], Lobbies.lobbies[data['roomId']], data['roomId'])

        sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['roomId'])
        sio.emit('next_round', room=data['gameId'])
        sio.emit('lobby_update', { 'lobbies':Lobbies.lobbies}, room='lobby')

# Info
@sio.on('set_data')
def get_connection(sid, data):
    print(f"SocketServer.set_data()")

    if data['player_id'] not in sio.rooms(sid):
        sio.enter_room(sid, str(data['player_id']))

    sio.emit('room_update', {'room': Lobbies.lobbies[data['roomId']]}, room=data['roomId'])

@sio.on('data_request')
def data_request(sid, data):
    print(f"SocketServer.data_request()")
    games_config = Games.pass_data(data)    
    if games_config is None:
        return None
    
    sio.enter_room(sid, games_config['game_id'])

    return games_config


@sio.on('start_round')
def start_next_round(sid, data):
    print(f"SocketServer.start_round()")
    Games.play_next_round(data, Lobbies.lobbies[data['room_id']])
    sio.emit('next_round', room=data['game_id'])
    sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['room_id'])


eventlet.wsgi.server(eventlet.listen(('', 5500)), app)

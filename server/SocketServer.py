import random
import socketio
from waitress import serve
import eventlet
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)
import lobbies
import games

lobbies = {}

@sio.event
def connect(sid, environ):
   print(sid, 'connected    ')

@sio.event
def disconnect(sid):
   print(sid, 'disconnected')

@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("Leaving lobby")
    sio.leave_room(sid, 'lobby')

@sio.on('set_data')
def get_connection(sid, data):
    sio.enter_room(sid, str(data['player_id']))

@sio.on('create_room')
def create_room(sid, data):
    print("socketServer.on('create_room')")

    lobbyId = random.randint(0, 1000000)
    while lobbyId in lobbies:
        lobbyId = random.randint(0, 1000000)
    lobbyId = str(lobbyId)
    lobbies[lobbyId] = {
        'players': [{'username': data['playerName'], 'ready': False, 'playerId': data['playerId']}],
        'maxPlayers': data['maxPlayers'],
        'startingMoney': data['startingMoney'],
        'lobbyName': data['lobbyName'],
        'owner': data['playerId'],
        'roomId': lobbyId
    }
    sio.enter_room(sid, lobbyId)
    sio.leave_room(sid, 'lobby')
    sio.enter_room(sid, data['playerId'])
    sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')

    return {'status': 'success', 'roomId': lobbyId, 'room': lobbies[lobbyId]}

@sio.on('leave_room')
def leave_room(sid, data):
    sio.leave_room(sid, data['roomId'])
    sio.leave_room(sid, (data['playerId'] + '_'+data['roomId']))

    lobbies[data['roomId']]['players'] = [player for player in lobbies[data['roomId']]['players'] if not player['playerId'] == data['playerId']]
    if len(lobbies[data['roomId']]['players']) == 0:
        del lobbies[data['roomId']]
    else:
        if data['playerId'] == lobbies[data['roomId']]['owner']:
            if len(lobbies[data['roomId']]['players']) > 0:
                lobbies[data['roomId']]['owner'] = lobbies[data['roomId']]['players'][0]['playerId']
    sio.enter_room(sid, 'lobby')
    sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')
    sio.emit('room_update', {'room': lobbies[data['roomId']]}, room=data['roomId'])

@sio.on('room_change_ready')
def room_change_ready(sid, data):
    print(f"SocketServer.on('room_change_ready')")
    for player in lobbies[data['roomId']]['players']:
        if player['playerId'] == data['playerId']:
            player['ready'] = not player['ready']
    # sio.emit('room_player_ready', {'content': 'A player has changed their ready status!'}, room=data['roomId'])
    sio.emit('room_update', {'room': lobbies[data['roomId']]}, room=data['roomId'])
    sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')

    # print(lobbies[data['roomId']])
    return { 'room': lobbies[data['roomId']]}


def shufflePlayers(players):
    random.shuffle(players)
    return players

@sio.on('join_room')
def join_room(sid, data):
    print(f"SocketServer.on('join_room')")
    sio.enter_room(sid, data['roomId'])
    sio.enter_room(sid, data['playerId'])
    sio.leave_room(sid, 'lobby')
    lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False, 'playerId': data['playerId']})

    sio.emit('lobby_update', {'lobbies':lobbies}, room='lobby')
    sio.emit('room_update', {'room':lobbies[data['roomId']]}, room=data['roomId'])

    sio.enter_room(sid, (data['playerId'] + '_'+ data['roomId']))
    return {'status': 'success', 'roomId': data['roomId'], 'room': lobbies[data['roomId']]}

@sio.on('join_lobby')
def join_lobby(sid):
    print(f"SocketServer.on('join_lobby')")
    sio.enter_room(sid, 'lobby')
    return {'lobbies': lobbies}

@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("Leaving lobby")
    sio.leave_room(sid, 'lobby')
    sio.emit('lobby_update', {'lobbies':lobbies}, room='lobby')

@sio.on('room_start_game')
def room_start_game(sid, data):
    print(f"SocketServer.on('room_start_game')")
    # Check if all players all ready! 
    if True:
        print(lobbies[data['roomId']]['players'])
        games.games[data['gameId']].parse_players(lobbies[data['roomId']]['players'])
        games.games[data['gameId']].start()
        games.games_lobbies[data['gameId']] = lobbies[data['roomId']]['maxPlayers']

        sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['roomId'])
        sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')

eventlet.wsgi.server(eventlet.listen(('', 5500)), app)

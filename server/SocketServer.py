import random
import socketio
from waitress import serve
import eventlet
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)
import lobbies
import games

lobbies = {
    '1':{
        'players':[{
            'username':'test',
            'userId':0,
            'ready':False
        }],
        'maxPlayers':4,
        'startingMoney':1000,
        'lobbyName':'Tes123t',
        'owner':0
    }
}
games = {}

@sio.event
def connect(sid, environ):
   print(sid, 'connected')


@sio.event
def disconnect(sid):
   print(sid, 'disconnected')


@sio.on('join_lobby')
def join_lobby(sid):
    print("Joining lobby")
    sio.enter_room(sid, 'lobby')
    return {'lobbies': lobbies}

@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("Leaving lobby")
    sio.leave_room(sid, 'lobby')

@sio.on('create_room')
def create_room(sid, data):
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
    sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')
    return { 'room': lobbies[lobbyId]}

@sio.on('leave_room')
def leave_room(sid, data):
    # print(data)
    sio.leave_room(sid, data['roomId'])
    print(lobbies[data['roomId']]['players'])
    lobbies[data['roomId']]['players'] = [player for player in lobbies[data['roomId']]['players'] if not player['playerId'] == data['playerId']]
    print(lobbies[data['roomId']]['players'])
    if len(lobbies[data['roomId']]['players']) == 0:
        del lobbies[data['roomId']]
    else:
        if data['playerId'] == lobbies[data['roomId']]['owner']:
            if len(lobbies[data['roomId']]['players']) > 0:
                lobbies[data['roomId']]['owner'] = lobbies[data['roomId']]['players'][0]['playerId']
    sio.enter_room(sid, 'lobby')
    sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')
    sio.emit('room_update', {'room': lobbies[data['roomId']]}, room=data['roomId'])


@sio.on('join_room')
def join_room(sid, data):
    if len(lobbies[data['roomId']]['players']) >= lobbies[data['roomId']]['maxPlayers']:
        return
    sio.enter_room(sid, data['roomId'])
    sio.leave_room(sid, 'lobby')
    lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False, 'playerId': data['playerId']})
    sio.emit('room_update', {'room': lobbies[data['roomId']]}, room=data['roomId'])
    sio.emit('lobby_update', { 'lobbies':lobbies }, room='lobby')


@sio.on('room_change_ready')
def room_change_ready(sid, data):
    for player in lobbies[data['roomId']]['players']:
        if player['playerId'] == data['playerId']:
            player['ready'] = not player['ready']
    sio.emit('room_player_ready', {'content': 'A player has changed their ready status!'}, room=data['roomId'])



@sio.on('room_start_game')
def room_start_game(sid, data):
    if data['playerId'] == lobbies[data['roomId']]['owner']:
        games[data['roomId']] = {'players': shufflePlayers(lobbies[data['roomId']]['players']) , 'startingMoney': lobbies[data['roomId']]['startingMoney']}
        del lobbies[data['roomId']]
        sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['roomId'])
        sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')

def shufflePlayers(players):
    random.shuffle(players)
    return players


eventlet.wsgi.server(eventlet.listen(('', 5500)), app)

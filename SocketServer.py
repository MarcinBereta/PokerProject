import random
import socketio
from waitress import serve
import eventlet
sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)

lobbies = {}
games = {}

def shufflePlayers(players):
    random.shuffle(players)
    return players

@sio.event
def connect(sid, environ):
   print(sid, 'connected')


@sio.event
def disconnect(sid):
   print(sid, 'disconnected')


@sio.on('join_lobby')
def join_lobby(sid, data):
    print("Joining lobby")
    sio.enter_room(sid, 'lobby')
    return {'content': 'A new player has joined the lobby!', 'lobbies': lobbies}
    sio.emit('lobby_message', {'content': 'A new player has joined the lobby!', 'lobbies': lobbies}, )

@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("Leaving lobby")
    sio.leave_room(sid, 'lobby')

@sio.on('create_room')
def create_room(sid, data):
    print("Creating lobby")
    lobbyId = random.randint(0, 1000000)
    while lobbyId in lobbies:
        lobbyId = random.randint(0, 1000000)
    lobbies[lobbyId] = {'players': [{'username': data['playerName'], 'ready': False}], 'maxPlayers': data['maxPlayers'], 'startingMoney': data['startingMoney'], 'owner': data['playerName']}
    sio.enter_room(sid, lobbyId)
    sio.leave_room(sid, 'lobby')
    sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')
    return {'content': 'A new lobby has been created!', 'room': lobbies[lobbyId]}

@sio.on('leave_room')
def leave_room(sid, data):
    print("Leaving room")
    sio.leave_room(sid, data['roomId'])
    lobbies[data['roomId']]['players'] = [player for player in lobbies[data['roomId']]['players'] if player['username'] != data['playerName']]
    if(len(lobbies[data['roomId']]['players']) == 0):
        del lobbies[data['roomId']]
    if data['playerName'] == lobbies[data['roomId']]['owner']:
        if(len(lobbies[data['roomId']]['players']) > 0):
            lobbies[data['roomId']]['owner'] = lobbies[data['roomId']]['players'][0]['username']

    sio.enter_room(sid, 'lobby')
    sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')
    sio.emit('room_player_join', {'content': 'A player has joined the room!', 'room': lobbies[data['roomId']]}, room=data['roomId'])


@sio.on('join_room')
def join_room(sid, data):
    print("Joining room")
    sio.enter_room(sid, data['roomId'])
    sio.leave_room(sid, 'lobby')
    lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False})
    sio.emit('room_player_join', {'content': 'A player has joined the room!'}, room=data['roomId'])
    sio.emit('lobby_update', { 'lobbies':lobbies,  'room': lobbies[data['roomId']]}, room='lobby')


@sio.on('room_change_ready')
def room_change_ready(sid, data):
    lobbies[data['roomId']]['players'][data['playerIndex']]['ready'] = not lobbies[data['roomId']]['players'][data['playerIndex']]['ready'];
    sio.emit('room_player_ready', {'content': 'A player has changed their ready status!'}, room=data['roomId'])



@sio.on('room_start_game')
def room_start_game(sid, data):
    if data['playerName'] == lobbies[data['roomId']]['owner']:
        games[data['roomId']] = {'players': shufflePlayers(lobbies[data['roomId']]['players']) , 'startingMoney': lobbies[data['roomId']]['startingMoney']}
        del lobbies[data['roomId']]
        sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['roomId'])
        sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

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
        'players':[
        {
            'playerId':'test',
            'userId':1,
            'ready':True,
            'username': 'TestPlayer01'
        }, 
        {
            'playerId':'test2',
            'userId':2,
            'ready':True, 
            'username': 'TestPlayer02'
        },
        {
            'playerId':'test3',
            'userId':3,
            'ready':True, 
            'username': 'TestPlayer03'
        }
        ],
        'maxPlayers':4,
        'startingMoney':1000,
        'lobbyName':'Tes123t',
        'owner':0
    }
}

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
    return { 'room': lobbies[lobbyId]}

@sio.on('leave_room')
def leave_room(sid, data):
    sio.leave_room(sid, data['roomId'])
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
    for player in lobbies[data['roomId']]['players']:
        if player['playerId'] == data['playerId']:
            player['ready'] = not player['ready']
    sio.emit('room_player_ready', {'content': 'A player has changed their ready status!'}, room=data['roomId'])

def shufflePlayers(players):
    random.shuffle(players)
    return players

@sio.on('join_room')
def join_room(sid, data):
    sio.enter_room(sid, data['roomId'])
    sio.enter_room(sid, data['playerId'])
    sio.leave_room(sid, 'lobby')
    lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False, 'playerId': data['playerId']})
    sio.emit('lobby_update', { 'lobbies':lobbies })
    return {'lobbies': lobbies}

@sio.on('join_lobby')
def join_lobby(sid):
    print("Joining lobby")
    sio.enter_room(sid, 'lobby')
    return {'lobbies': lobbies}

@sio.on('leave_lobby')
def leave_lobby(sid, data):
    print("Leaving lobby")
    sio.leave_room(sid, 'lobby')

@sio.on('room_start_game')
def room_start_game(sid, data):
    if True:
        games.games[data['gameId']].parse_players(lobbies['1']['players'])
        games.games[data['gameId']].start()

        game_data = games.games[data['gameId']].get_data()

        for i in games.games[data['gameId']].list_of_active_players:
            game_data['cards'] = i.get_cards()
            game_data['valid_moves'] = i.potential_moves()
            sio.emit('game_update', game_data, room=i.player_id)

        
        sio.emit('room_game_start', {'content': 'The game has started!'}, room=data['roomId'])
        sio.emit('lobby_update', { 'lobbies':lobbies}, room='lobby')

eventlet.wsgi.server(eventlet.listen(('', 5500)), app)

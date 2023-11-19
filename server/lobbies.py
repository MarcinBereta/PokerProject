# from SocketServer import *

import random

lobbies = {
    '1': {
        'players': [
            {
                'username': 'test',
                'playerId': '1',
                'ready': True
            },
            {
                'username': 'test2',
                'playerId': '2',
                'ready': True
            }
        ],
        'maxPlayers': 4,
        'startingMoney': 1000,
        'bigBlind': 10,
        'lobbyName': 'LobbyWith2Players',
        'owner': 0
    },
    '2': {
        'players': [
            {
                'username': 'test',
                'playerId': '3',
                'ready': True
            },
            {
                'username': 'test2',
                'playerId': '4',
                'ready': True
            },
            {
                'username': 'test3',
                'playerId': '5',
                'ready': True
            }
        ],
        'maxPlayers': 4,
        'startingMoney': 1000,
        'bigBlind': 10,
        'lobbyName': 'LobbyWith3Players',
        'owner': 0
    },
    '3': {
        'players': [
            {
                'username': 'test',
                'playerId': '6',
                'ready': True
            }
        ],
        'maxPlayers': '6',
        'startingMoney': 1000,
        'bigBlind': 10,
        'lobbyName': 'LobbyWith1Player',
        'owner': 0
    }
}


def create_room(data):
    print("Lobbies.create_room()")
    lobbyId = random.randint(0, 1000000)
    while lobbyId in lobbies:
        lobbyId = random.randint(0, 1000000)
    lobbyId = str(lobbyId)

    lobbies[lobbyId] = {
        'players'           :[{'username': data['playerName'], 'ready': True, 'playerId': data['playerId']}],
        'maxPlayers'        : data['maxPlayers'],
        'startingMoney'     : data['startingMoney'],
        'lobbyName'         : data['lobbyName'],
        'owner'             : data['playerId'],
        'roomId'            : lobbyId,
        'bigBlind'          : data['bigBlind']

    }

    # print(lobbies)

    return lobbyId


def join_room(data):

    print("Lobbies.join_room()")
    lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False, 'playerId': data['playerId']})

    # print(lobbies)
    return True


def leave_room(data):
    print(f"Lobbies.leave_room()")
    lobbies[data['roomId']]['players'] = [player for player in lobbies[data['roomId']]['players'] if not player['playerId'] == data['playerId']]
    if len(lobbies[data['roomId']]['players']) == 0:
        del lobbies[data['roomId']]
    else:
        if data['playerId'] == lobbies[data['roomId']]['owner']:
            if len(lobbies[data['roomId']]['players']) > 0:
                lobbies[data['roomId']]['owner'] = lobbies[data['roomId']]['players'][0]['playerId']

def change_ready(data):
    print(f"Lobbies.change_ready()")
    for player in lobbies[data['roomId']]['players']:
        if player['playerId'] == data['playerId']:
            player['ready'] = not player['ready']

# @sio.on('join_lobby')
# def join_lobby(sid):
#     print("Joining lobby")
#     sio.enter_room(sid, 'lobby')
#     return {'lobbies': lobbies}

# @sio.on('leave_lobby')
# def leave_lobby(sid, data):
#     print("Leaving lobby")
#     sio.leave_room(sid, 'lobby')

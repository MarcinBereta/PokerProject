# from SocketServer import *

import random

# lobbies = {
#     '1':{
#         'players':[
#         {
#             'playerId':'test',
#             'userId':1,
#             'ready':True
#         }, 
#         {
#             'playerId':'test2',
#             'userId':2,
#             'ready':True
#         }
#         ],
#         'maxPlayers':4,
#         'startingMoney':1000,
#         'lobbyName':'Tes123t',
#         'owner':0
#     }
# }

lobbies = {}

def create_room(data):
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

    print(lobbies)

    return lobbyId

def join_room(data):
    print("lobbies.join_room()")
    lobbies[data['roomId']]['players'].append({'username': data['playerName'], 'ready': False, 'playerId': data['playerId']})
    print(lobbies)
    return True

def leave_room(data):
    lobbies[data['roomId']]['players'] = [player for player in lobbies[data['roomId']]['players'] if not player['playerId'] == data['playerId']]
    if len(lobbies[data['roomId']]['players']) == 0:
        del lobbies[data['roomId']]
    else:
        if data['playerId'] == lobbies[data['roomId']]['owner']:
            if len(lobbies[data['roomId']]['players']) > 0:
                lobbies[data['roomId']]['owner'] = lobbies[data['roomId']]['players'][0]['playerId']

def change_ready(data):
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


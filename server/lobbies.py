from SocketServer import *

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

# @sio.on('join_lobby')
# def join_lobby(sid):
#     print("Joining lobby")
#     sio.enter_room(sid, 'lobby')
#     return {'lobbies': lobbies}

# @sio.on('leave_lobby')
# def leave_lobby(sid, data):
#     print("Leaving lobby")
#     sio.leave_room(sid, 'lobby')


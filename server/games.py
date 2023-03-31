from SocketServer import *

@sio.on('change_tour')
def join_lobby(sid):
    print("Changing tour")


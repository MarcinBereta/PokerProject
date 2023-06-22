#Socket test file
import socketio

sio = socketio.Client()
roomId = 0
lobbies={}
@sio.event
def connect():
    print('connection established')

@sio.event
def my_message(data):
    print('message received with ', data)
    sio.emit('my response', {'response': 'my response'})

@sio.event
def disconnect():
    print('disconnected from server')
#LOBBY MANAGEMENT
@sio.on('lobby_update')
def lobby_update(data):
    lobbies = data['lobbies']

def setLobbies(data):
    lobbies = data['lobbies']

@sio.event
def join_lobby():
    sio.emit('join_lobby', {'playerName': 'test'}, callback=setLobbies)

@sio.event
def leave_lobby():
    sio.emit('leave_lobby', {'playerName': 'test'}, callback=(lambda data: print(data)))

# ROOM MANAGEMENT
def setRoomId(data):
    roomId = data['roomId']

@sio.event
def create_room():
    sio.emit('create_room', {'playerName': 'test', 'maxPlayers': 4, 'startingMoney': 1500}, callback=setRoomId)

@sio.event
def leave_room():
    sio.emit('leave_room', {'playerName': 'test', 'roomId': roomId}, callback=setLobbies)



sio.connect('http://127.0.0.1:5000')
while True:
    messsageContent = input("Enter message: ")
    message = input("Enter message: ")

    if messsageContent == 'join_lobby':
        join_lobby()
    elif messsageContent == 'create_lobby':
        create_room()
    elif messsageContent == 'leave_lobby':
        leave_lobby()
    elif messsageContent == 'leave_room':
        leave_room()
    else:
        sio.emit(messsageContent, {'content': message})
    print("MESSAGE SENT")
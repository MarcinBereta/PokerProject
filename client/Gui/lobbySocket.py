import socketio
import json

class LobbySocketWrapper():
    sio = socketio.Client()

    def __init__(self, set_lobbies_data, set_room_data):
        self.lobbies = {}
        self.games = {}
        self.room = {}
        self.roomId = None
        self.set_lobbies = set_lobbies_data
        self.set_room = set_room_data
        pass

    def setup(self):
        self.sio.connect('http://127.0.0.1:5500')
        self.call_backs()

    def loop(self):
        self.sio.wait()

    def set_room_data(self, data):
        self.roomId = data['room']['roomId']
        self.room = data['room']
        self.set_room(data['room'])

    def set_lobbies_callback(self, data):
        self.lobbies = data['lobbies']
        self.set_lobbies(data['lobbies'])

    def set_start_game(self):
        print("STARTING GAME")

        @self.sio.event
        def connect():
            print('connection established')

        @self.sio.event
        def my_message(data):
            print('message received with ', data)
            self.sio.emit('my response', {'response': 'my response'})

        @self.sio.event
        def disconnect():
            print('disconnected from server')

        # LOBBY MANAGEMENT
        @self.sio.on('lobby_update')
        def lobby_update(data):
            print("LOBBY UPDATE")
            # self.set_lobbies_callback(data)

        @self.sio.on('room_update')
        def set_room_data(data):
            print("Room update!")
            self.set_room_data(data)

    def join_room_callback(self, data):
        if data['status'] == 'success':
            self.roomId = data['roomId']
            self.room = data['room']
            self.set_lobbies(data['lobbies']['lobbies'])

    def join_room(self, data):
        @self.sio.event
        def join_room_socket():
            self.sio.emit('join_room', {
                        'playerId': data['playerId'],
                        'roomId': data['roomId'], 
                        'playerName':data['playerName']
                        })
        join_room_socket()
            
    def leave_lobby(self, data):
        @self.sio.event
        def leave_lobby_socket():
            self.sio.emit('leave_lobby', {
                        'playerId': data['playerId'],
                        'lobbyId': data['lobbyId']}
                        , callback=self.set_lobbies_callback)
        self.roomId = None
        leave_lobby_socket()

    def create_room(self, data):
        @self.sio.event
        def create_room_socket():
            self.sio.emit('create_room', data,
                          callback=self.set_room_data)
        create_room_socket()

    def send_lobbies_request(self):
        @self.sio.event
        def send_lobbies_request_socket():
            self.sio.emit('join_lobby', callback=self.set_lobbies_callback)
        send_lobbies_request_socket()

    def leave_room(self, data):
        @self.sio.event
        def leave_room_socket():
            self.sio.emit('leave_room', {'playerId': data['playerId'], 'roomId': self.roomId})
        leave_room_socket()
        self.roomId = None
# 
    # def start_game(self, data):
        # @self.sio.event
        # def room_start_game():
            # self.sio.emit('room_start_game',
                        #   {'playerId': data['playerId'], 'roomId': self.roomId},
                        #   callback=self.set_start_game)
        # room_start_game()
    # def change_ready_state(self, data):
        # @self.sio.event
        # def change_ready_state_socket():
            # self.sio.emit('room_change_ready',
                        #   {'playerId': data['playerId'], 'roomId': self.roomId},
                        #   callback=self.set_room_data)
        # change_ready_state_socket()

    def run(self):
        self.setup()
        # self.loop()

import socketio
import json


class LobbySocketWrapper():
    sio = socketio.Client()

    def __init__(self, user_id, username):
        self.lobbies = {}
        self.games = {}
        self.room = {}
        self.roomId = None
        pass

        # Lista wszystkich lobby
        self.lobbies = {}

        # Dane aktualnego Pokoju 
        self.room = {}

        # Id Pokoju 
        self.roomId = None

        self.is_game = False
        self.game_id = None
        self.user_id = user_id
        self.username = username
        self.returning = False

        self.new_data = True
        self.call_backs()

    # Setup Connection
    def setup(self):
        try:
            self.sio.connect('http://127.0.0.1:5500')
        except:
            print("Still connected")
        self.call_backs()

    def run(self):
        self.setup()

    def loop(self):
        self.sio.wait()

    def set_room_data(self, data):
        self.room = data['room']
        print(self.room)
        self.new_data = True

    def set_room_callback(self, data):
        # print(data)
        # self.roomId =   data['room']['roomId']
        self.room = data['room']
        self.new_data = True

    def set_lobbies_callback(self, data=None):
        if data is None:
            return
        self.lobbies = data['lobbies']
        # self.set_lobbies(data['lobbies'])
        self.new_data = True
        for i in self.lobbies:
            for j in self.lobbies[i]['players']:
                if self.user_id == j['playerId']:
                    self.room = self.lobbies[i]
                    self.roomId = self.lobbies[i]['roomId']
                    self.returning = True

    def call_backs(self, data=None):
        @self.sio.on('lobby_update')
        def lobby_update(data):
            print("lobbySocket.on('lobby_update')")
            self.lobbies = data['lobbies']
            self.new_data = True
            # self.set_lobbies_callback(data)

        @self.sio.on('room_update')
        def room_update(data):
            print("lobbySocket.on('room_update')")
            self.room = data['room']
            self.new_data = True
            pass

        @self.sio.on('game_created')
        def room_update(data):
            print("lobbySocket.on('game_created')")
            self.game_id = data['game_id']
            self.is_game = True

    # ROOM MANAGEMENT 
    def join_room_callback(self, data):
        if data['status'] == 'success':
            self.roomId = data['roomId']
            self.room = data['room']
        else:
            print(f"[ERROR] JOIN ROOM FAILED!")
        self.new_data = True

    def join_room(self, data):
        print(f"join_room()")

        @self.sio.event
        def join_room_socket():
            self.sio.emit('join_room', {
                'playerId': data['playerId'],
                'roomId': data['roomId'],
                'playerName': data['playerName']
            }, callback=self.join_room_callback)

        join_room_socket()

    def create_room(self, data):
        print(f"create_room() + join_room()")

        @self.sio.event
        def create_room_socket():
            self.sio.emit('create_room', data,
                          callback=self.join_room_callback)

        create_room_socket()

    def leave_room(self):
        @self.sio.event
        def leave_room_socket():
            self.sio.emit('leave_room', {'playerId': self.user_id, 'roomId': self.roomId})

        leave_room_socket()

        self.new_data = True
        self.roomId = None
        self.room = None

    # LOBBY MANAGEMENT        
    def leave_lobby(self):
        print(f"lobbySocket.leave_lobby()")

        @self.sio.event
        def leave_lobby_socket():
            self.sio.emit('leave_lobby', {
                'playerId': self.user_id,
                'lobbyId': self.roomId}
                          , callback=self.set_lobbies_callback)

        self.roomId = None
        leave_lobby_socket()

    def send_lobbies_request(self):
        print(f"lobbySocket.send_lobbies_request()")

        @self.sio.event
        def send_lobbies_request_socket():
            self.sio.emit('join_lobby', callback=self.set_lobbies_callback)

        send_lobbies_request_socket()

    def start_game(self):
        print(f"lobbySocket.start_game()")
        self.is_game = True

        @self.sio.event
        def room_start_game():
            self.sio.emit('room_start_game',
                          {'playerId': self.user_id, 'roomId': self.roomId, 'gameId': self.game_id})

        room_start_game()

    def set_game_data(self, data):
        print("lobbySocket.on('set_game_data')")
        self.game_id = data['game_id']
        self.start_game()

    def create_live_game(self):
        print(f"lobbySocket.create_live_game()")

        @self.sio.event
        def new_game():
            self.sio.emit('create_live_game',
                          {'room_id': self.roomId}, callback=self.set_game_data)
            self.is_game = True

        new_game()

    def change_ready_state(self):
        @self.sio.event
        def change_ready_state_socket():
            self.sio.emit('room_change_ready',
                          {'playerId': self.user_id, 'roomId': self.roomId}, callback=self.set_room_callback)

        change_ready_state_socket()
        # self.loop()

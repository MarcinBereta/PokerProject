import socketio
import json

class LobbySocketWrapper():
    sio = socketio.Client()

    def __init__(self,  set_game_data):
        self.lobbies = {}
        self.games = {}
        self.room = {}
        self.roomId = None
        self.set_game = set_game_data
        pass

    def setup(self):
        self.sio.connect('http://192.168.0.77:5500')
        # self.call_backs()

    def loop(self):
        self.sio.wait()

    def set_game_data(self, data):
        self.roomId = data['game']['roomId']
        self.room = data['game']
        self.set_room(data['room'])


    def call_backs(self):
        # GAME MANAGEMENT
        @self.sio.on('lobby_update')
        def lobby_update(data):
            self.set_lobbies_callback(data)

    def join_room_callback(self, data):
        if data['status'] == 'success':
            self.roomId = data['roomId']
            self.room = data['room']
            self.set_lobbies(data['lobbies']['lobbies'])
    def move_played(self, data):
        @self.sio.event
        def game_move_played():
            self.sio.emit('game_move_played',
                          {'playerId': data['playerId'], 'gameId': self.roomId},
                          callback=self.join_room_callback)
        game_move_played()

    def run(self):
        self.setup()
        # self.loop()

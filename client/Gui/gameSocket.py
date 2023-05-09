import socketio
import json

class GameSocketWrapper():
    sio = socketio.Client()

    def __init__(self, set_game_data, user_id):
        self.user_id = user_id
        # self.lobbies = {}
        # self.games = {}
        # self.room = {}
        self.set_game = set_game_data
        self.game_id = None
        self.roomId = 1
        self.newUpdate = False
        self.game_data = None 
        self.cards = None
        self.moves = {}

    def setup(self):
        self.sio.connect('http://127.0.0.1:5500')
        self.call_backs()

        @self.sio.event
        def send_data():
            self.sio.emit('set_data', {'player_id' : self.user_id})
        send_data()

    def create_live_game(self, data):
        @self.sio.event
        def new_game():
            self.sio.emit('create_live_game',
                {'room_id' : self.roomId}, callback=self.call_backs)
        new_game()

    # def loop(self):
    #     self.sio.wait()

    def set_game_data(self, data):
        self.roomId = data['game']['roomId']
        self.room = data['game']
        self.set_room(data['room'])

    def call_backs(self):
        @self.sio.on('room_update')
        def game_update(data):
            print("Game")
            self.join_room_callback(data)
    
        @self.sio.on('room_game_start')
        def game_status(data):
            print(data['content'])

        @self.sio.on('game_update')
        def game_update(data):
            self.newUpdate = True
            self.game_data = data

            if self.cards == None:
                self.cards = self.game_data['cards']

            print(self.cards)

        @self.sio.on('game_created')
        def game_created(data):
            self.game_id = data['game_id']
            
            @self.sio.event
            def start_game():
                self.sio.emit('room_start_game', { 
                       'roomId': self.roomId,
                       'gameId': self.game_id
                   }),
            start_game()

    def move_played(self, data):
        @self.sio.event
        def game_move_played():
            self.sio.emit('game_move_played',
                {'playerId': self.user_id, 'gameId': self.game_id, 'move_id': data['move_id']},
                callback=self.call_backs),
        game_move_played()

    def run(self):
        self.setup()
        # self.loop()

    def join_room(self, data):
        # player has joined new room
        @self.sio.event
        def join_room_socket():
            self.sio.emit('join_room', {
                        'playerId': self.user_id,
                        'roomId': data['roomId'], 
                        'playerName':data['playerName']
                        })
            
        self.roomId = data['roomId']
        join_room_socket()

    def start_game(self, data):
        @self.sio.event
        def room_start_game():
            self.sio.emit('room_start_game',
                          {'playerId': self.user_id, 'roomId': self.roomId})
        room_start_game()

    def change_ready_state(self, data):
        @self.sio.event
        def change_ready_state_socket():
            self.sio.emit('room_change_ready',
                          {'playerId': self.user_id, 'roomId': self.roomId},
                          callback=self.set_room_data)
        change_ready_state_socket()
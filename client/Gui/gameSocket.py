import socketio
import json


class GameSocketWrapper():
    sio = socketio.Client()

    def __init__(self, set_game_data, user_id):
        self.user_id = user_id
        self.set_game = set_game_data
        self.game_id = None
        self.roomId = None
        self.newUpdate = False
        self.game_data = None
        self.cards = None
        self.moves = {}
        self.winner = False

        self.max_size = None

    def setup(self):
        print("gameSocket.setup()")
        self.sio.connect('http://127.0.0.1:5500')
        self.call_backs()

    def leave_game(self):
        @self.sio.event
        def leave_lobby_socket():
            self.sio.emit('leave_game', {
                'playerId': self.user_id,
                'game_id': self.game_id}
                          )

        leave_lobby_socket()

    def send_room_request(self):
        print("send_room_request()")

        @self.sio.event
        def send_room_request_socket():
            self.sio.emit('data_request', {"user_id": self.user_id}, callback=self.set_data)

        send_room_request_socket()

    # def loop(self):
    #     self.sio.wait()
    def set_data(self, data):
        print(data)
        self.max_size = data['data']['max_size']
        self.game_data = data['data']
        self.newUpdate = True
        self.game_id = data['game_id']
        self.call_backs()

        if self.cards == None:
            self.cards = self.game_data['cards']

    def set_game_data(self, data):
        print('set_game_data()')
        self.roomId = data['game']['roomId']
        self.room = data['game']
        self.set_room(data['room'])

    def call_backs(self):
        @self.sio.on('room_update')
        def game_update(data):
            print("gameSocket.on('room_update')")
            self.join_room_callback(data)

        @self.sio.on('finish_game')
        def game_update(data):
            print("gameSocket.on('finish_game')")
            self.winner = True
            self.game_data = data

        @self.sio.on('start_game')
        def game_status(data):
            print("gameSocket.on('start_game')")

        @self.sio.on('game_update')
        def game_update(data):
            print("gameSocket.on('game_update')")
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
        print("gameSocket.run()")
        self.setup()
        # self.loop()

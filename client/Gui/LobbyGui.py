from random import random
from tkinter import *
from tkinter import ttk
import ScreensEnum
from client.sockets.lobbySocket import LobbySocketWrapper


def randomInt(min, max):
    return int(random() * (max - min + 1)) + min


class LobbyGui:
    def __init__(self, root, change_screen, clear_canvas, user_id, username):
        self.leaveGameButton = None
        self.startGameButton = None
        self.maxPlayers = None
        self.lobbyNameInput = None
        self.moneyInput = None
        self.createRoomButton = None
        self.searchText = None
        self.searchInput = None
        self.lobbyList = None
        self.parseError = None
        self.room = None
        self.userId = user_id
        self.playerName = username
        self.lobbies = {
            '1': {
                'lobbyId': 1,
                'lobbyName': 'kurwa',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '2': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '3': {
                'lobbyId': 1,
                'lobbyName': 'chuj',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '4': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '5': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '6': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '7': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '8': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '9': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '10': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '11': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '12': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            },
            '13': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            }
            , '14': {
                'lobbyId': 1,
                'lobbyName': 'Test',
                'players': ['test', 'test2'],
                'maxPlayers': 4
            }
        }
        self.change_screen = change_screen
        self.root = root
        self.clear_canvas = clear_canvas
        self.socketHandler = LobbySocketWrapper(self.set_lobbies, self.set_room)
        self.socketHandler.run()
        self.socketHandler.send_lobbies_request()

    def create_lobby(self):
        self.clear_canvas()
        text = Label(self.root, text="Lobby name", font=("Arial", 15), fg="black")
        text.pack()
        self.lobbyNameInput = Entry(self.root, width=40, font=("Arial", 15))
        self.lobbyNameInput.pack()
        text = Label(self.root, text="Starting money", font=("Arial", 15), fg="black")
        text.pack()
        self.moneyInput = Entry(self.root, width=40, font=("Arial", 15))
        self.moneyInput.pack()
        text = Label(self.root, text="Max players", font=("Arial", 15), fg="black")
        text.pack()
        self.maxPlayers = Entry(self.root, width=40, font=("Arial", 15))
        self.maxPlayers.pack()
        self.createRoomButton = Button(self.root, text="Create Lobby", command=self.create_room, height=1, width=50)
        self.createRoomButton.pack()

    def set_room(self, room):
        self.room = room
        self.generate_room()

    def generate_parse_error(self):
        if self.parseError is not None:
            self.parseError.destroy()
        self.parseError = Label(self.root, text="Max players and Starting money has to be numbers",
                                font=("Arial", 15),
                                fg="red")
        self.parseError.pack()

    def create_room(self):
        lobby_name = self.lobbyNameInput.get()
        try:
            max_players = int(self.maxPlayers.get())
        except ValueError:
            self.maxPlayers.delete(0, END)
            self.maxPlayers.bg = "red"
            self.generate_parse_error()
            return
        try:
            money = int(self.moneyInput.get())
        except ValueError:
            self.moneyInput.delete(0, END)
            self.moneyInput.bg = "red"
            self.generate_parse_error()
            return
        self.socketHandler.create_room({
            'lobbyName': lobby_name,
            'maxPlayers': max_players,
            'startingMoney': money,
            "playerName": self.playerName,
            "playerId": self.userId
        })

    def callback(self):
        self.generateLobbies()

    def set_lobbies(self, lobbies):
        print("LOADING LOBBIES")
        self.lobbies = lobbies
        self.generate_lobbies()

    def joinLobby(self, event):
        item = self.lobbyList.selection()[0]
        lobbyIndex = self.lobbyList.item(item, "tags")[0]
        if len(self.lobbies[lobbyIndex]['players']) >= self.lobbies[lobbyIndex]['maxPlayers']:
            return
        self.socketHandler.join_room({
            "roomId": lobbyIndex,
            "playerId": self.userId,
            "playerName": self.playerName

        })

    def generate_lobbies(self):
        if self.lobbyList is not None:
            self.lobbyList.delete(*self.lobbyList.get_children())
        if self.searchText is None or self.lobbyList is None:
            print("LAUNCHING GUI")
            self.clear_canvas()
            self.launch_gui();
            return
        for i, lobbyKey in enumerate(self.lobbies):
            lobby = self.lobbies[lobbyKey]
            if self.searchText is None or self.searchText.get() == "":
                self.lobbyList.insert("", "end", text=i + 1, tags=lobbyKey,
                                      values=(lobby['lobbyName'], len(lobby['players']), lobby['maxPlayers']))
            else:
                if (self.searchText.get() in lobbyKey or self.searchText.get() in lobby['lobbyName']):
                    self.lobbyList.insert("", "end", text=i + 1, tags=lobbyKey,
                                          values=(lobby['lobbyName'], len(lobby['players']), lobby['maxPlayers']))
        self.lobbyList.bind("<Double-1>", self.joinLobby)

    def launch_gui(self):
        self.createRoomButton = Button(self.root, text="Create Lobby", command=self.create_lobby, height=1, width=50)
        self.createRoomButton.pack()
        text = Label(self.root, text="Search for a lobby", font=("Arial", 15), fg="black")
        text.pack()
        self.searchText = StringVar()
        self.searchText.trace("w", lambda name, index, mode, sv=self.searchText: self.callback())
        self.searchInput = Entry(self.root, width=40, font=("Arial", 15), textvariable=self.searchText)
        self.searchInput.pack()
        self.lobbyList = ttk.Treeview(self.root, columns=("lobbyName", "players", "maxPlayers"))
        self.lobbyList.heading("#0", text="Lobby ID")
        self.lobbyList.heading("lobbyName", text="Lobby Name")
        self.lobbyList.heading("players", text="Players")
        self.lobbyList.heading("maxPlayers", text="Max Players")
        self.lobbyList.column("#0", width=100)
        self.lobbyList.column("lobbyName", width=200)
        self.lobbyList.column("players", width=100)
        self.lobbyList.column("maxPlayers", width=100)
        self.generate_lobbies()
        self.lobbyList.pack()

    def start_game(self):
        self.socketHandler.start_game({'roomId': self.roomId, 'playerId': self.userId})

    def ready(self):
        self.socketHandler.change_ready_state({'roomId': self.roomId, 'playerId': self.userId})

    def leave_room(self):
        self.socketHandler.leave_room({'playerId': self.userId})
        self.searchText = None
        self.searchInput = None

    def generate_room(self):
        self.clear_canvas()
        text = Label(self.root, text="Lobby name: " + self.room['lobbyName'], font=("Arial", 15), fg="black")
        text.pack()
        text = Label(self.root, text="Starting money: " + str(self.room['startingMoney']), font=("Arial", 15),
                     fg="black")
        text.pack()
        text = Label(self.root, text="Max players: " + str(self.room['maxPlayers']), font=("Arial", 15), fg="black")
        text.pack()
        self.lobbyList = ttk.Treeview(self.root, columns=("Username", "Is ready"))
        self.lobbyList.heading("#0", text="Player ID")
        self.lobbyList.heading("Username", text="Username")
        self.lobbyList.heading("Is ready", text="Is ready")

        for i, player in enumerate(self.room['players']):
            self.lobbyList.insert("", "end", text=i + 1,
                                  values=(player['username'], 'ready' if player['ready'] else 'Not ready'))
        self.lobbyList.pack()
        if self.room['owner'] == self.userId:
            self.startGameButton = Button(self.root, text="Start Game", command=self.start_game, height=1, width=50)
            self.startGameButton.pack()
        else:
            self.startGameButton = Button(self.root, text="Change ready state", command=self.ready, height=1, width=50)
            self.startGameButton.pack()
        self.leaveGameButton = Button(self.root, text="Leave room", command=self.leave_room, height=1, width=50)
        self.leaveGameButton.pack()

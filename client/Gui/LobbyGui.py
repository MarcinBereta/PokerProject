import sys
from random import random
from tkinter import *
from tkinter import ttk
import ScreensEnum
from client.sockets.LobbySocket import LobbySocketWrapper

sys.path.append("./..")


def random_int(min_val, max_val):
    return int(random() * (max_val - min_val + 1)) + min_val


class LobbyGui:
    def __init__(self, root, change_screen, clear_canvas, user_id, username, save_game_data):
        self.roomId = None
        self.leave_game_button = None
        self.start_game_button = None
        self.create_room_button = None
        self.save_game_data = save_game_data
        self.socketHandler = LobbySocketWrapper(user_id, username)
        self.socketHandler.run()
        self.socketHandler.send_lobbies_request()
        self.max_players = None
        self.lobby_name_input = None
        self.money_input = None
        self.search_text = None
        self.search_input = None
        self.lobby_list = None
        self.parseError = None
        self.big_blind_input = None
        self.error_label = None

        # Dane GuiManagera
        self.userId = user_id
        self.playerName = username
        self.change_screen = change_screen
        self.root = root
        self.clear_canvas = clear_canvas
        self.reload_window = self.generate_lobbies
        self.root.after(100, self.update)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.socketHandler.leave_room()
        self.socketHandler.leave_lobby()
        self.root.destroy()

    def update(self):
        if self.socketHandler.is_game is True:
            self.save_game_data(self.socketHandler.game_id, self.socketHandler.roomId)
            self.change_screen(ScreensEnum.ScreensEnum.GAME)
            return

        if self.socketHandler.new_data is True:
            self.reload_window()
            self.socketHandler.new_data = False

        self.root.after(100, self.update)

    def create_lobby(self):
        self.clear_canvas()
        self.lobby_list = None

        text = Label(self.root, text="Lobby name", font=("Arial", 15), fg="black")
        text.pack()

        self.lobby_name_input = Entry(self.root, width=40, font=("Arial", 15))
        self.lobby_name_input.pack()
        text = Label(self.root, text="Starting money", font=("Arial", 15), fg="black")
        text.pack()

        self.big_blind_input = Entry(self.root, width=40, font=("Arial", 15))
        self.big_blind_input.pack()
        text = Label(self.root, text="Big Blind", font=("Arial", 15), fg="black")
        text.pack()

        self.money_input = Entry(self.root, width=40, font=("Arial", 15))
        self.money_input.pack()
        text = Label(self.root, text="Max players", font=("Arial", 15), fg="black")
        text.pack()

        self.max_players = Entry(self.root, width=40, font=("Arial", 15))
        self.max_players.pack()

        self.create_room_button = Button(self.root, text="Create Lobby", command=self.create_room, height=1, width=50)
        self.create_room_button.pack()

    def generate_parse_error(self):
        if self.parseError is not None:
            self.parseError.destroy()
        self.parseError = Label(self.root, text="Max players and Starting money has to be numbers",
                                font=("Arial", 15),
                                fg="red")
        self.parseError.pack()

    def create_room(self):
        lobby_name = self.lobby_name_input.get()
        try:
            max_players = int(self.max_players.get())
            if max_players > 6 or max_players <= 1:
                raise ValueError
        except ValueError:
            self.max_players.delete(0, END)
            self.max_players.bg = "red"
            self.generate_parse_error()
            return
        try:
            money = int(self.money_input.get())
            bigBlind = int(self.big_blind_input.get())
            if money < 5:
                raise ValueError
        except ValueError:
            self.money_input.delete(0, END)
            self.money_input.bg = "red"
            self.generate_parse_error()
            return

        self.socketHandler.create_room({
            'lobbyName': lobby_name,
            'maxPlayers': max_players,
            'startingMoney': bigBlind,
            "playerName": self.playerName,
            "playerId": self.userId,
            'bigBlind': money
        })
        self.reload_window = self.generate_room
        self.socketHandler.new_data = False

    def join_lobby(self):
        item = self.lobby_list.selection()[0]
        lobbyIndex = self.lobby_list.item(item, "tags")[0]

        lobbies = self.socketHandler.lobbies
        print(lobbyIndex)
        if len(lobbies[lobbyIndex]['players']) >= int(lobbies[lobbyIndex]['maxPlayers']):
            return

        self.socketHandler.join_room({
            "roomId": lobbyIndex,
            "playerId": self.userId,
            "playerName": self.playerName
        })

        self.reload_window = self.generate_room

    def generate_lobbies(self):
        if self.lobby_list is not None:
            self.lobby_list.delete(*self.lobby_list.get_children())

        if self.search_text is None or self.lobby_list is None:
            self.clear_canvas()
            self.launch_gui()
            return

        for i, lobbyKey in enumerate(self.socketHandler.lobbies):
            lobby = self.socketHandler.lobbies[lobbyKey]
            if self.search_text is None or self.search_text.get() == "":
                self.lobby_list.insert("", "end", text=i + 1, tags=lobbyKey,
                                       values=(lobby['lobbyName'], len(lobby['players']), lobby['maxPlayers']))
            else:
                if self.search_text.get() in lobbyKey or self.search_text.get() in lobby['lobbyName']:
                    self.lobby_list.insert("", "end", text=i + 1, tags=lobbyKey,
                                           values=(lobby['lobbyName'], len(lobby['players']), lobby['maxPlayers']))
        self.lobby_list.bind("<Double-1>", self.join_lobby)

    def go_to_user_profile(self):
        self.change_screen(ScreensEnum.ScreensEnum.USER_PROFILE)

    def launch_gui(self):
        self.clear_canvas()
        frame = Frame(self.root)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        header = Label(frame, text="Lobby", font=("Arial", 30), fg="black")
        header.grid(row=0, column=0)
        user_profile = Button(frame, text="Go to user profile", font=("Arial", 30), fg="black",
                              command=self.go_to_user_profile)
        user_profile.grid(row=1, column=0)
        header.grid(row=0, column=0)
        buttons = Frame(self.root)
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=3)
        buttons.columnconfigure(2, weight=4)
        buttons.rowconfigure(0, weight=1)
        buttons.rowconfigure(1, weight=1)
        buttons.rowconfigure(2, weight=1)
        text = Label(buttons, text="Search for a lobby", font=("Arial", 15), fg="black")
        text.grid(row=0, column=0)
        self.search_text = StringVar()
        self.search_text.trace("w", lambda name, index, mode, sv=self.search_text: self.callback())
        self.search_input = Entry(buttons, font=("Arial", 15), textvariable=self.search_text)
        self.search_input.grid(row=1, column=0, columnspan=2)
        self.create_room_button = Button(buttons, text="Create Lobby", command=self.create_lobby, height=1, width=50)
        self.create_room_button.grid(row=1, column=2)
        self.lobby_list = ttk.Treeview(self.root, columns=("lobbyName", "players", "maxPlayers"))
        self.lobby_list.heading("#0", text="Lobby ID")
        self.lobby_list.heading("lobbyName", text="Lobby Name")
        self.lobby_list.heading("players", text="Players")
        self.lobby_list.heading("maxPlayers", text="Max Players")
        self.lobby_list.column("#0", width=100)
        self.lobby_list.column("lobbyName", width=200)
        self.lobby_list.column("players", width=100)
        self.lobby_list.column("maxPlayers", width=100)
        self.generate_lobbies()
        frame.pack()
        buttons.pack()
        self.lobby_list.pack()

    def start_game(self):
        self.roomId = self.socketHandler.roomId
        self.socketHandler.create_live_game()
        while self.socketHandler.game_id is None:
            self.reload_window()
            return  
        self.save_game_data(self.socketHandler.game_id, self.socketHandler.roomId)


    def ready(self):
        self.socketHandler.change_ready_state()
        self.generate_room()

    def leave_room(self):
        self.socketHandler.leave_room()
        self.reload_window = self.generate_lobbies
        self.search_text = None
        self.search_input = None

    def generate_room(self):
        self.clear_canvas()
        room = self.socketHandler.room
        text = Label(self.root, text="Lobby name: " + self.socketHandler.room['lobbyName'], font=("Arial", 15),
                     fg="black")
        text.pack()
        text = Label(self.root, text="Starting money: " + str(room['startingMoney']), font=("Arial", 15),
                     fg="black")
        text.pack()
        text = Label(self.root, text="Max players: " + str(room['maxPlayers']), font=("Arial", 15), fg="black")
        text.pack()
        self.lobby_list = ttk.Treeview(self.root, columns=("Username", "Is ready"))
        self.lobby_list.heading("#0", text="Player ID")
        self.lobby_list.heading("Username", text="Username")
        self.lobby_list.heading("Is ready", text="Is ready")
        for i, player in enumerate(room['players']):
            self.lobby_list.insert("", "end", text=str(i + 1),
                                   values=(player['username'], 'ready' if player['ready'] else 'Not ready'))
        self.lobby_list.pack()
        if room['owner'] == self.userId:
            self.start_game_button = Button(self.root, text="Start Game", command=self.start_game, height=1, width=50)
            self.start_game_button.pack()
        else:
            self.start_game_button = Button(self.root, text="Change ready state", command=lambda: self.ready(),
                                            height=1,
                                            width=50)
            self.start_game_button.pack()

        self.error_label = Label(self.root, text=self.socketHandler.message_from_server, font=("Arial", 15), fg="red", )
        self.error_label.pack()

        self.leave_game_button = Button(self.root, text="Leave room", command=self.leave_room, height=1, width=50)
        self.leave_game_button.pack()

    def callback(self):
        pass

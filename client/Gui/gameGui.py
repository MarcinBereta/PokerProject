#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
import os
from PIL import Image, ImageTk

from client.sockets.gameSocket import GameSocketWrapper
from screensEnum import ScreensEnum

URL = "http://127.0.0.1:5000"

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI_6 = os.path.join(PROJECT_PATH, "userInterfaces/game_window_6.ui")
PROJECT_UI_4 = os.path.join(PROJECT_PATH, "userInterfaces/game_window_4.ui")
CARDS_SOURCE = os.path.join(PROJECT_PATH, "cards")
IMAGES_SOURCE = os.path.join(PROJECT_PATH, "images")


class GameGui:
    def __init__(self, root, switch_screen, clear_canvas, user_id, username, game_id, room_id):
        self.shifted_players = None
        self.main_window = None
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.root = root
        self.user_id = user_id
        self.username = username
        self.game_id = game_id
        self.room_id = room_id

        self.main_window = None
        self.seats = None

        self.game_socket_handler = GameSocketWrapper(user_id, game_id, room_id)
        self.game_socket_handler.run()

        self.actual_player_id = None
        self.community_cards = []
        self.stakes_data = None
        self.pot_value = 0
        self.nick = {}
        self.shift = None
        self.raise_value = None
        self.all_cards = None
        self.shifted_players = {}

        self.player_nick = {}
        self.stakes_labels = {}
        self.players_labels = {}
        self.board_labels = {}
        self.buttons = {}
        self.stakes = {}
        self.notes = {}
        self.act = {}
        self.pot = None
        self.raise_bet_slider = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit_button_click)

        self.generate_gui()

    def clear_data(self):
        self.shift = None
        self.actual_player_id = None
        self.community_cards = []
        self.stakes_data = None
        self.pot_value = 0
        self.raise_value = None

        for i in range(6):
            self.display_card("table0" + str(i) + "card01", False, True)
            self.display_card("table0" + str(i) + "card02", False, True)

    def on_quit_button_click(self):
        self.game_socket_handler.leave_game()
        self.switch_screen(ScreensEnum.LOBBIES)

    def generate_gui(self, master=None):
        self.root = pygubu.Builder()
        self.root.add_resource_path(PROJECT_PATH)
        self.root.add_from_file(PROJECT_UI_6)

        self.main_window = self.root.get_object('game_window', master)
        self.root.connect_callbacks(self)

        for i in range(6):
            self.players_labels["table0" + str(i) + "card01"] = self.root.get_object("table0" + str(i) + "card01",
                                                                                     master)
            self.players_labels["table0" + str(i) + "card02"] = self.root.get_object("table0" + str(i) + "card02",
                                                                                     master)
            self.stakes[i] = self.root.get_object("table0" + str(i) + "stake", master)
            self.notes[i] = self.root.get_object("table0" + str(i) + "note", master)
            self.act[i] = self.root.get_object("table0" + str(i) + "act", master)

        for i in range(5):
            self.board_labels["table07card0" + str(i)] = self.root.get_object("table07card0" + str(i + 1), master)
            self.player_nick["table0" + str(i + 1)] = self.root.get_object("table0" + str(i + 1) + "nick", master)

        self.buttons['move_01'] = self.root.get_object("move_01", master)
        self.buttons['move_02'] = self.root.get_object("move_02", master)
        self.buttons['move_03'] = self.root.get_object("move_03", master)

        self.buttons['move_01'].configure(text="CALL/CHECK")
        self.buttons['move_02'].configure(text="RAISE")
        self.buttons['move_03'].configure(text="FOLD")

        self.buttons['move_01'].bind('<Button-1>', lambda _: self.make_move(1))
        self.buttons['move_02'].bind('<Button-1>', lambda _: self.make_move(2))
        self.buttons['move_03'].bind('<Button-1>', lambda _: self.make_move(3))

        self.pot = self.root.get_object("game_pot", master)
        self.raise_bet_slider = self.root.get_object("raise_bet", master)

        self.update()

    def make_move(self, move_id):
        self.raise_value = self.raise_bet_slider.get()

        self.game_socket_handler.move_played(
            {'playerId': self.user_id,
             'move_id': move_id,
             'raise_bet': self.raise_value},
        )

    def handle_winner(self):
        self.all_cards = self.game_socket_handler.game_status['all_cards']
        self.seats = self.game_socket_handler.game_status['players_at_table']
        self.stakes_data = self.game_socket_handler.game_status['stakes']

        for uuid, seat_no in self.shifted_players.items():
            if uuid not in self.seats:
                self.display_card("table0" + str(self.shifted_players[uuid]) + "card01", False, True)
                self.display_card("table0" + str(self.shifted_players[uuid]) + "card02", False, True)
            else:
                self.display_card('table0' + str(seat_no) + "card01", False, False, self.all_cards[uuid][0])
                self.display_card('table0' + str(seat_no) + "card02", False, False, self.all_cards[uuid][1])

            self.stakes[seat_no].configure(text="$" + str(self.stakes_data[uuid]))

        self.open_popup()
        self.game_socket_handler.game_status = None

    def set_up_table_seats(self):
        self.seats = self.game_socket_handler.game_status['players_at_table']
        self.shift = self.seats[self.user_id]
        self.nick = self.game_socket_handler.game_status['players_info']

        self.shifted_players = {}

        print(self.seats, self.player_nick, self.user_id, self.nick)

        for player in self.seats.keys():
            self.shifted_players[player] = (self.seats[player] - self.shift + len(self.seats)) % len(self.seats)
            if player != self.user_id and self.shifted_players[player] != 0:
                self.player_nick["table0" + str(self.shifted_players[player])].configure(text=str(self.nick[player]))

    def update_game_data(self):
        self.actual_player_id = self.game_socket_handler.game_status['actual_id']
        self.pot_value = self.game_socket_handler.game_status['pot']
        self.community_cards = self.game_socket_handler.game_status['board_cards']
        self.seats = self.game_socket_handler.game_status['players_at_table']
        self.stakes_data = self.game_socket_handler.game_status['stakes']

        # self.game_socket_handler.game_status = None
        self.game_socket_handler.new_update = False

    def update(self):
        if self.shift is None and self.game_socket_handler.game_status is not None:
            self.set_up_table_seats()

        if self.game_socket_handler.game_status is not None and self.game_socket_handler.new_update is True and \
                self.game_socket_handler.game_status['winner'] is not None:
            self.handle_winner()

        if self.game_socket_handler.game_status is not None and self.game_socket_handler.new_update is True and \
                self.game_socket_handler.game_status['winner'] is None:
            self.update_game_data()

            actual_player = self.seats[str(self.actual_player_id)]

            for note, stake, actual_player_token in zip(self.notes.values(), self.stakes.values(), self.act.values()):
                note.configure(text="")
                stake.configure(text="")
                actual_player_token.configure(text="")

            self.act[(actual_player - self.shift + len(self.shifted_players)) % len(self.shifted_players)].configure(
                text="AC")
            self.pot.config(text="POT: $" + str(self.pot_value))
            self.raise_bet_slider.configure(to=self.stakes_data[self.user_id])

            for uuid, seat_no in self.shifted_players.items():
                if uuid not in self.seats:
                    self.display_card("table0" + str(self.shifted_players[uuid]) + "card01", False, True)
                    self.display_card("table0" + str(self.shifted_players[uuid]) + "card02", False, True)
                elif seat_no != 0:
                    self.display_card('table0' + str(seat_no) + "card01", False, False)
                    self.display_card('table0' + str(seat_no) + "card02", False, False)
                else:
                    self.display_card('table00card01', False, False, self.game_socket_handler.cards[0], )
                    self.display_card('table00card02', False, False, self.game_socket_handler.cards[1])

                self.stakes[seat_no].configure(text="$" + str(self.stakes_data[uuid]))

            for i in range(len(self.community_cards)):
                self.display_card('table07card0' + str(i), True, False, self.community_cards[i])

            for i in range(len(self.community_cards), 5, 1):
                self.display_card('table07card0' + str(i), True, True)

        self.main_window.after(200, self.update)

    def generate_waiting_room(self, master=None):
        pass

    def open_popup(self):
        self.shift = None
        top = tk.Toplevel(self.main_window)

        def on_submit():
            top.destroy()
            self.start_game()

        top.geometry("600x150")
        top.title("Poker Game")
        text = tk.Label(top, text="Winner is " + str(self.game_socket_handler.game_status['winner']),
                        font=('Mistral 15 bold'))
        text.pack()

        if self.game_socket_handler.owner == self.user_id:
            confirm = tk.Button(top, text="Next round!", font=("Arial", 15), command=on_submit)
            confirm.pack()

    @staticmethod
    def generate_path(card_name):
        return os.path.join(CARDS_SOURCE, card_name)

    def display_card(self, label, board=False, delete_card=True, card_path="card_back.png"):

        if delete_card is True:
            fpath = os.path.join(IMAGES_SOURCE, "p_b.png")
        else:
            fpath = self.generate_path(card_path)

        WIDTH = 115
        HEIGHT = 155

        aux = Image.open(fpath).resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(aux)

        if board:
            self.board_labels[label].configure(image=img, height=HEIGHT, width=WIDTH)
            self.board_labels[label].image = img
        else:
            self.players_labels[label].configure(image=img, height=HEIGHT, width=WIDTH)
            self.players_labels[label].image = img

    def start_game(self):
        self.clear_data()
        self.game_socket_handler.room_start_game()

#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
import os
from PIL import Image, ImageTk

URL = "http://127.0.0.1:5000"
from lobbySocket import LobbySocketWrapper
from gameSocket import GameSocketWrapper
from ScreensEnum import ScreensEnum

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI_6 = os.path.join(PROJECT_PATH, "UserInterface/game_window_6.ui")
PROJECT_UI_4 = os.path.join(PROJECT_PATH, "UserInterface/game_window_4.ui")
CARDS_SOURCE = os.path.join(PROJECT_PATH, "cards")

class GameGui:
    def __init__(self, root, switch_screen, clear_canvas, user_id, username):
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.root = root
        self.user_id = user_id

        self.game_socket_handler = GameSocketWrapper(None, user_id)
        self.game_socket_handler.run()
        self.game_socket_handler.send_room_request()

        self.username = username
        self.pass_cards = True
        self.game_data = None
        self.actual_id = None

        self.players_labels     = {}
        self.board_labels       = {}
        self.buttons            = {}
        self.stakes             = {}
        self.notes              = {}
        self.player_nick        = {}
        self.act                = {}
        self.pot                = None

        self.shift = None
        self.starting_players = None

        self.move = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.generate_gui()
        pass

    def on_closing(self):
        if self.game_socket_handler.winner == True:
            self.game_socket_handler.leave_game()
            self.game_socket_handler.disconnect()
            self.switch_screen(ScreensEnum.LOBBIES)

        self.game_socket_handler.disconnect()
        self.switch_screen(ScreensEnum.LOBBIES)

    def generate_gui(self, master = None):
        self.root = pygubu.Builder()
        self.root.add_resource_path(PROJECT_PATH)
        self.root.add_from_file(PROJECT_UI_6)

        self.mainwindow = self.root.get_object('game_window', master)

        for i in range(6):
            self.players_labels["table0"+ str(i) + "card01"] = self.root.get_object("table0"+ str(i) + "card01", master)
            self.players_labels["table0"+ str(i) + "card02"] = self.root.get_object("table0"+ str(i) + "card02", master)

        for i in range(5):
            self.board_labels["table07card0" + str(i)] = self.root.get_object("table07card0" + str(i+1), master)
            self.player_nick["table0"+str(i+1)]        = self.root.get_object("table0" + str(i+1) +"nick", master)

        self.buttons['move_01'] = self.root.get_object("move_01", master)
        self.buttons['move_02'] = self.root.get_object("move_02", master)
        self.buttons['move_03'] = self.root.get_object("move_03", master)

        self.buttons['move_01'].bind('<Button-1>', self.make_move1)
        self.buttons['move_02'].bind('<Button-1>', self.make_move2)
        self.buttons['move_03'].bind('<Button-1>', self.make_move3)

        self.pot = self.root.get_object("game_pot", master)

        for i in range(6):
            self.stakes[i]  = self.root.get_object("table0"+str(i)+"stake", master)
            self.notes[i]   = self.root.get_object("table0"+str(i)+"note", master)
            self.act[i]     = self.root.get_object("table0"+str(i)+"act", master)

        self.make_move = None
        self.update()
    
    def make_move1(self, event):
        self.move = 1

    def make_move2(self, event):
        self.move = 2
    
    def make_move3(self, event):
        self.move = 3

    def update(self):
        if self.game_socket_handler.game_data != None:
            self.actual_id = self.game_socket_handler.game_data['actual_id']

        if self.game_socket_handler.winner == True:
            all_cards           = self.game_socket_handler.game_data['all_cards']
            players_at_table    = self.game_socket_handler.game_data['players_at_table']
            stakes              = self.game_socket_handler.game_data['stakes']
            
            for player in players_at_table.keys():
                players_at_table[player] = (players_at_table[player] - self.shift + self.starting_players)%self.starting_players

            for i in players_at_table:
                if players_at_table[i] != self.user_id:
                    self.stakes[players_at_table[i]].configure(text="$"+str(stakes[i]))

            for i in players_at_table:
                self.display_card('table0'+str(players_at_table[i])+"card01", all_cards[i][0])
                self.display_card('table0'+str(players_at_table[i])+"card02", all_cards[i][1])

            self.game_data = self.game_socket_handler.game_data
            self.open_popup()
            return

        if self.game_socket_handler.newUpdate == True:
            game_pot            = self.game_socket_handler.game_data['pot']
            board_cards         = self.game_socket_handler.game_data['board_cards']
            players_at_table    = self.game_socket_handler.game_data['players_at_table']
            stakes              = self.game_socket_handler.game_data['stakes']
            all_cards           = self.game_socket_handler.game_data['all_cards']
            nick                = self.game_socket_handler.game_data['players_info']

            if self.shift is None:
                self.shift = players_at_table[self.user_id]

            if self.starting_players is None:
                self.starting_players = len(players_at_table)

            self.game_data = self.game_socket_handler.game_data
            self.game_socket_handler.newUpdate = False

            actual_player = (players_at_table[self.actual_id] - self.shift + self.starting_players)%self.starting_players

            for i in self.notes.values():
                i.configure(text="")

            for i in self.stakes.values():
                i.configure(text="")
            
            for i in self.act.values():
                i.configure(text="")

            self.act[actual_player].configure(text="AC")

            for player in players_at_table.keys():
                players_at_table[player] = ( players_at_table[player] - self.shift + self.starting_players)%self.starting_players

            for i in self.players_labels:
                self.delete_card(i)

            print(nick, players_at_table)

            for i in players_at_table:
                self.display_card('table0'+str(players_at_table[i])+"card01")
                self.display_card('table0'+str(players_at_table[i])+"card02")

                self.stakes[players_at_table[i]].configure(text="$"+str(stakes[i]))
                if i != self.user_id:
                    self.player_nick["table0"+str(players_at_table[i])].configure(text=str(nick[i]))
            
            if board_cards != '':
                for i in range(len(board_cards)):
                    self.display_board_card('table07card0'+str(i),board_cards[i])

            self.pot.config(text="POT: $" + str(game_pot))

            self.buttons['move_01'].configure(text=self.game_data['valid_moves']['1'])
            self.buttons['move_02'].configure(text=self.game_data['valid_moves']['2'])
            self.buttons['move_03'].configure(text=self.game_data['valid_moves']['3'])

            if self.user_id in players_at_table.keys():
                self.display_card('table00card01', self.game_socket_handler.cards[0])
                self.display_card('table00card02', self.game_socket_handler.cards[1])

        if self.move != None and self.actual_id == self.user_id:
            self.game_socket_handler.move_played(
                 {'playerId': self.user_id, 
                  'move_id': self.move},
            )
            self.move = None

        # self.mainwindow.pack()
        self.mainwindow.after(1000, self.update)

    def generate_waiting_room(self, master = None):
        pass

    def open_popup(self):
        top = tk.Toplevel(self.mainwindow)
        top.geometry("600x150")
        top.title("Poker Game")
        tk.Label(top, text= "Winner is " + str(self.game_data['winner']), font=('Mistral 18 bold')).place(x=75,y=75)

    def delete_card(self, label):
        self.players_labels[label].configure(image = None)
        self.players_labels[label].image = None   

    def display_card(self, label, card_path = "card_back.png"):
        fpath = os.path.join(CARDS_SOURCE, card_path)

        WIDTH = 128
        HEIGHT = 169
        print(WIDTH, HEIGHT)

        aux = Image.open(fpath).resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(aux)
        self.players_labels[label].configure(image = img, height=HEIGHT, width=WIDTH)
        self.players_labels[label].image = img      

    def display_board_card(self, label, card_path):
        fpath = os.path.join(CARDS_SOURCE, card_path)
        WIDTH = 128
        HEIGHT = 169

        aux = Image.open(fpath).resize((WIDTH, HEIGHT), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(aux)
        self.board_labels[label].configure(image = img, height=HEIGHT, width=WIDTH)
        self.board_labels[label].image = img     

    def start_game(self):
        pass
        # self.game_socket_handler.run()
        # self.game_socket_handler.create_live_game()
        # self.mainwindow.mainloop()
    
        # self.mainwindow.mainloop()
#!/usr/bin/python3
import pathlib
import tkinter as tk
import pygubu
import os
from PIL import Image, ImageTk

URL = "http://127.0.0.1:5000"
from lobbySocket import LobbySocketWrapper
from gameSocket import GameSocketWrapper

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = os.path.join(PROJECT_PATH, "game_window.ui")
CARDS_SOURCE = os.path.join(PROJECT_PATH, "cards")

class GameGui:
    def __init__(self, root, switch_screen, clear_canvas, userId, username):
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.root = root
        self.userId = userId
        self.game_socket_handler = GameSocketWrapper(None, self.userId)
        self.username = username
        self.pass_cards = True
        self.game_data = None

        self.players_labels = {}
        self.board_labels = {}
        self.buttons = {}

        self.move = None

        self.game_socket_handler.run()
        self.generate_gui()
        self.game_socket_handler.create_live_game({'game_Id': 1234})
        pass

    def generate_gui(self, master = None):
        self.root = builder = pygubu.Builder()
        self.root.add_resource_path(PROJECT_PATH)
        self.root.add_from_file(PROJECT_UI)

        self.mainwindow = self.root.get_object('game_window', master)

        for i in range(4):
            self.players_labels["table0"+ str(i) + "card01"] = self.root.get_object("table0"+ str(i) + "card01", master)
            self.players_labels["table0"+ str(i) + "card02"] = self.root.get_object("table0"+ str(i) + "card02", master)

        for i in range(5):
            self.board_labels["table05card0" + str(i)] = self.root.get_object("table05card0" + str(i+1), master)

        self.buttons['move_01'] = self.root.get_object("move_01", master)
        self.buttons['move_02'] = self.root.get_object("move_02", master)
        self.buttons['move_03'] = self.root.get_object("move_03", master)

        self.buttons['move_01'].bind('<Button-1>', self.make_move1)
        self.buttons['move_02'].bind('<Button-1>', self.make_move2)
        self.buttons['move_03'].bind('<Button-1>', self.make_move3)

        # self.root.get_object("move_01", master).bind('<Button-1>', self.make_move(2))
        # self.root.get_object("move_02", master).bind('<Button-1>', self.make_move(2))
        # self.root.get_object("move_03", master).bind('<Button-1>', self.make_move(3))
        self.make_move = None
        self.update()
    
    def make_move1(self, event):
        self.move = 1

    def make_move2(self, event):
        self.move = 2
    
    def make_move3(self, event):
        self.move = 3

    def update(self):        
        if self.game_socket_handler.newUpdate == True:
            self.game_data = self.game_socket_handler.game_data
            self.game_socket_handler.newUpdate = False

            for i in self.players_labels:
                self.delete_card(i)

            for i in self.game_data['players_at_table']:
                if i != self.userId:
                    self.display_card('table0'+str(self.game_data['players_at_table'][i]+1)+"card01")
                    self.display_card('table0'+str(self.game_data['players_at_table'][i]+1)+"card02")

            if self.game_data['board_cards'] != '':
                for i in range(len(self.game_data['board_cards'])):
                    self.display_board_card('table05card0'+str(i),self.game_data['board_cards'][i])

            self.buttons['move_01'].configure(text=self.game_data['valid_moves']['1'])
            self.buttons['move_02'].configure(text=self.game_data['valid_moves']['2'])
            self.buttons['move_03'].configure(text=self.game_data['valid_moves']['3'])


            self.display_card('table00card01', self.game_socket_handler.cards[0])
            self.display_card('table00card02', self.game_socket_handler.cards[1])

        if self.move != None:
            self.game_socket_handler.move_played(
                 {'playerId': self.userId, 
                  'move_id': self.move},
            )
            self.move = None

        # self.mainwindow.pack()
        self.mainwindow.after(50, self.update)

    def generate_waiting_room(self, master = None):
        pass

    def delete_card(self, label):
        self.players_labels[label].configure(image = None)
        self.players_labels[label].image = None   

    def display_card(self, label, card_path = "card_back.png"):
        fpath = os.path.join(CARDS_SOURCE, card_path)
        aux = Image.open(fpath).resize((130, 190), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(aux)
        self.players_labels[label].configure(image = img, height=190, width=140)
        self.players_labels[label].image = img      

    def display_board_card(self, label, card_path):
        fpath = os.path.join(CARDS_SOURCE, card_path)
        aux = Image.open(fpath).resize((130, 190), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(aux)
        self.board_labels[label].configure(image = img, height=190, width=140)
        self.board_labels[label].image = img     

    def start_game(self):
        pass
        # self.game_socket_handler.run()
        # self.game_socket_handler.create_live_game()
        # self.mainwindow.mainloop()
    
        # self.mainwindow.mainloop()
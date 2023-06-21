import base64
import os
from tkinter import filedialog, ttk
from urllib.request import urlopen

from PIL import Image, ImageTk
from requests import post, get

import ScreensEnum
from tkinter import *

URL = "http://127.0.0.1:5000"


class LeaderBoardGui:
    def __init__(self, root, switch_screen, clear_canvas):
        self.search_button = None
        self.lobby_list = None
        self.create_room_button = None
        self.search_input = None
        self.search_text = None
        self.myFrame = None
        self.root = root
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.user = None
        self.search_text = StringVar()
        self.search_input = None
        self.scores = None
        self.get_leaderboard_data()

    def get_leaderboard_data(self):
        if self.search_input is None or self.search_input.get() == "":
            if self.search_input is not None:
                print(self.search_input.get())
            r = get(URL + "/get_leaderboard/ ")
        else:
            print(self.search_input.get())
            r = get(URL + "/get_leaderboard/" + self.search_input.get())
        data = r.json()

        if data["status"] == "success":
            # self.scores = []
            # self.user = data["user"]
            self.scores = data["scores"]
            self.launch_gui()
        else:
            return None

    def switch_to_lobby(self):
        self.switch_screen(ScreensEnum.ScreensEnum.USER_PROFILE)

    def generate_lobbies(self):
        if self.lobby_list is not None:
            self.lobby_list.delete(*self.lobby_list.get_children())
        for i, score in enumerate(self.scores):
            self.lobby_list.insert("", "end", text=i + 1, tags=score,
                                   values=(score['username'], score['score'], score['timestamp']))

    def launch_gui(self):
        self.clear_canvas()
        frame = Frame(self.root)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        header = Label(frame, text="Lobby", font=("Arial", 30), fg="black")
        header.grid(row=0, column=0)

        user_profile = Button(frame, text="Go to user profile", font=("Arial", 30), fg="black",
                              command=self.switch_to_lobby)
        user_profile.grid(row=1, column=0)
        header.grid(row=0, column=0)

        buttons = Frame(self.root)

        # buttons.rowconfigure(12, weight=1)
        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=3)
        buttons.columnconfigure(2, weight=4)
        buttons.rowconfigure(0, weight=1)
        buttons.rowconfigure(1, weight=1)
        buttons.rowconfigure(2, weight=1)
        text = Label(buttons, text="Search for user", font=("Arial", 15), fg="black")
        text.grid(row=0, column=0)
        # text.pack()

        self.search_input = Entry(buttons, font=("Arial", 15), textvariable=self.search_text)
        self.search_input.grid(row=1, column=0, columnspan=2)
        self.search_button = Button(buttons, text="Search", font=("Arial", 15), fg="black",
                                    command=self.get_leaderboard_data)
        self.search_button.grid(row=1, column=2)
        self.lobby_list = ttk.Treeview(self.root, columns=("username", "score", "time"))
        self.lobby_list.heading("#0", text="Rank")
        self.lobby_list.heading("username", text="Username")
        self.lobby_list.heading("score", text="User score")
        self.lobby_list.heading("time", text="Time")

        self.lobby_list.column("username", width=200)
        self.lobby_list.column("score", width=100)
        self.lobby_list.column("time", width=100)
        self.generate_lobbies()
        frame.pack()
        buttons.pack()
        self.lobby_list.pack()

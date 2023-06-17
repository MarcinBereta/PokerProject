import base64
import os
from tkinter import filedialog
from urllib.request import urlopen

from PIL import Image, ImageTk
from requests import post, get

import ScreensEnum
from tkinter import *

URL = "http://127.0.0.1:5000"


def parse_user_date(date):
    return date.split(" ")[0] + " " + date.split(" ")[1] + " " + date.split(" ")[2] + " " + date.split(" ")[3] \
        + " " + date.split(" ")[4]


class UserProfileGui:
    def __init__(self, root, switch_screen, clear_canvas, user_id, save_user_data):
        self.remove_image = None
        self.selected_image = None
        self.files = None
        self.image_input = None
        self.password_input2 = None
        self.password_input = None
        self.display_name_input = None
        self.email_input = None
        self.myFrame = None
        self.root = root
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.user_id = user_id
        self.user = None
        self.scores = None
        self.save_user_data = save_user_data
        self.get_user_data()

    def get_user_data(self):
        r = get(URL + "/get_profile/" + str(self.user_id))
        data = r.json()

        if data["status"] == "success":
            self.user = data["user"]
            self.scores = data["scores"]
            self.generate_gui()
        else:
            return None

    def switch_to_lobby(self):
        self.switch_screen(ScreensEnum.ScreensEnum.LOBBIES)

    def switch_to_leader_board(self):
        self.switch_screen(ScreensEnum.ScreensEnum.LEADERBOARD)

    def generate_main_box(self):
        self.clear_canvas()
        self.myFrame = Frame(self.root)
        self.myFrame.configure(width=800, height=800)
        self.myFrame.grid_configure(padx=10, pady=10)
        self.myFrame.rowconfigure(0, weight=1)
        self.myFrame.rowconfigure(1, weight=2)
        self.myFrame.rowconfigure(2, weight=3)
        self.myFrame.columnconfigure(0, weight=1)
        self.myFrame.columnconfigure(1, weight=1)
        self.myFrame.columnconfigure(2, weight=1)
        text = Label(self.myFrame, text="UserPage", font=("Arial", 20))
        text.grid(row=0, column=0)
        lobbyButton = Button(self.myFrame, text="Lobby", font=("Arial", 15), command=self.switch_to_lobby)
        lobbyButton.grid(row=0, column=1)
        lobbyButton = Button(self.myFrame, text="LeaderBoard", font=("Arial", 15), command=self.switch_to_leader_board)
        lobbyButton.grid(row=0, column=2)
        customUrl = URL + "/images/" + self.user['avatar']
        u = urlopen(customUrl)
        rwa_data = u.read()
        u.close()
        image = PhotoImage(data=rwa_data)
        userImageLabel = Label(self.myFrame, image=image)
        userImageLabel.image = image
        userImageLabel.configure(width=100, height=100)
        userImageLabel.grid(row=1, column=0)
        text = Label(self.myFrame, text="UserName: " + self.user['username'], font=("Arial", 20))
        text.grid(row=1, column=1)
        self.myFrame.pack()

    def generate_gui(self):
        self.generate_main_box()
        edit_button = Button(self.myFrame, text="Edit user", font=("Arial", 15), command=self.generate_edit)
        edit_button.grid(row=1, column=2)
        scoreFrame = Frame(self.myFrame)
        if self.scores is not None:
            scoreLabel = Label(scoreFrame, text="Scores: ", font=("Arial", 20))
            scoreLabel.pack()
            scoreFrame.grid(row=2, column=1, rowspan=2)
            for score in self.scores:
                scoreLabel = Label(scoreFrame, text=("Score: " + score['score'] + ", time:  "
                                                     + parse_user_date(score['timestamp'])), font=("Arial", 20))
                scoreLabel.pack()

    def generate_edit(self):
        self.generate_main_box()
        editFrame = Frame(self.myFrame)
        editFrame.grid(row=2, column=1, rowspan=2)
        text = Label(editFrame, text="Email", font=("Arial", 20))
        text.pack()
        self.email_input = Entry(editFrame, font=("Arial", 15))
        self.email_input.insert(0, self.user['email'])
        self.email_input.pack()
        text = Label(editFrame, text="Username", font=("Arial", 20))
        text.pack()
        self.display_name_input = Entry(editFrame, font=("Arial", 15))
        self.display_name_input.insert(0, self.user['username'])
        self.display_name_input.pack()
        text = Label(editFrame, text="Password", font=("Arial", 20))
        text.pack()
        self.password_input = Entry(editFrame, font=("Arial", 15))
        self.password_input.pack()
        text = Label(editFrame, text="Confirm Password", font=("Arial", 20))
        text.pack()
        self.password_input2 = Entry(editFrame, font=("Arial", 15))
        self.password_input2.pack()
        self.image_input = Button(editFrame, text="Select image", font=("Arial", 15), command=self.select_image)
        self.image_input.pack()
        self.remove_image = Button(editFrame, text="Remove image", font=("Arial", 15), command=self.delete_image)
        self.remove_image.pack()
        self.selected_image = Label(editFrame, text=self.user['avatar'], font=("Arial", 15))
        self.selected_image.pack()
        if self.user['avatar'] is None:
            self.remove_image.configure(state=DISABLED)
            self.selected_image.configure(text="No images selected")
        update_button = Button(editFrame, text="Update", font=("Arial", 15), command=self.update_user)
        update_button.pack()
        cancel_button = Button(editFrame, text="Cancel", font=("Arial", 15), command=self.generate_gui)
        cancel_button.pack()

    def delete_image(self):
        self.files = None
        self.selected_image.configure(text="No images selected")
        if self.user['avatar'] is None:
            self.remove_image.configure(state=DISABLED)

    def update_user(self):
        self.validate_form()
        if self.files is None:
            print(self.display_name_input.get())
            r = post(URL + "/update_user_data", data={
                'username': self.display_name_input.get(),
                "email": self.email_input.get(),
                "password": self.password_input.get(),
                "_id": self.user['_id'],
                'avatar': self.selected_image.cget("text")
            })
        else:
            r = post(URL + "/update_user_data", data={
                'username': self.display_name_input.get(),
                "email": self.email_input.get(),
                "password": self.password_input.get(),
                "_id": self.user['_id'],

            }, files={'file': open(self.files, 'rb')})
        data = r.json()
        if data["status"] == "success":
            self.save_user_data(data["user"])
            self.user = data["user"]
            self.generate_gui()
        else:
            print("Failed to update user data")

    def validate_form(self):
        if self.display_name_input.get() == "":
            self.display_name_input.set(self.user['username'])
        if self.email_input.get() == "":
            self.email_input.set(self.user['email'])
        if self.password_input.get() != self.password_input2.get():
            self.password_input.set("")
            self.password_input2.set("")
        if "@" not in self.email_input.get():
            self.email_input.set("")

    def select_image(self):
        files = filedialog.askopenfilenames(filetypes=(("Image files", "*.png"), ("all files", "*.*")))
        self.files = files[0]
        self.selected_image["text"] = os.path.basename(str(files[0]))

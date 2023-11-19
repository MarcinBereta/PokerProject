from requests import post

import screensEnum
from tkinter import *
from tkinter import filedialog
import os

from screensEnum import ScreensEnum

URL = "http://127.0.0.1:5000"


class RegisterGui:
    def __init__(self, root, switch_screen, clear_canvas, save_user_data):
        self.selected_image = None
        self.email_input = None
        self.root = root
        self.display_name_input = None
        self.password_input = None
        self.password_input2 = None
        self.image_input = None
        self.login_button = None
        self.register_button = None
        self.forgot_password_button = None
        self.files = None
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.save_user_data = save_user_data
        self.generate_gui()

    def generate_gui(self):
        self.clear_canvas()
        text = Label(self.root, text="Email", font=("Arial", 20))
        text.pack()
        self.email_input = Entry(self.root, font=("Arial", 15))
        self.email_input.pack()
        text = Label(self.root, text="Username", font=("Arial", 20))
        text.pack()
        self.display_name_input = Entry(self.root, font=("Arial", 15))
        self.display_name_input.pack()
        text = Label(self.root, text="Password", font=("Arial", 20))
        text.pack()
        self.password_input = Entry(self.root, font=("Arial", 15), show="*")
        self.password_input.pack()
        text = Label(self.root, text="Confirm Password", font=("Arial", 20))
        text.pack()
        self.password_input2 = Entry(self.root, font=("Arial", 15), show="*")
        self.password_input2.pack()
        self.image_input = Button(self.root, text="Select image", font=("Arial", 15), command=self.select_image)
        self.image_input.pack()
        self.selected_image = Label(self.root, text="No image selected", font=("Arial", 15))
        self.selected_image.pack()
        self.register_button = Button(self.root, text="Register", font=("Arial", 15), command=self.register)
        self.register_button.pack()
        self.login_button = Button(self.root, text="Login", font=("Arial", 15), command=self.switch_to_login)
        self.login_button.pack()

    def select_image(self):
        files = filedialog.askopenfilenames(filetypes=(("Image files", "*.png"), ("all files", "*.*")))
        self.files = files[0]
        self.selected_image["text"] = os.path.basename(str(files[0]))

    def register(self):
        if self.validate_form():
            print("Please fill all fields")
            return
        else:
            if self.files is None:
                r = post(URL + "/register", data={
                    'userName': self.display_name_input.get(),
                    "email": self.email_input.get(),
                    "password": self.password_input.get(),
                })
            else:
                r = post(URL + "/register", data={
                    'userName': self.display_name_input.get(),
                    "email": self.email_input.get(),
                    "password": self.password_input.get(),
                }, files={'file': open(self.files, 'rb')})
            print(r)
            data = r.json()
            if data["status"] == "success":
                self.save_user_data(data["user"])
                self.switch_screen(ScreensEnum.LOBBIES)
            else:
                print("Failed to log in")

    def validate_form(self):
        if self.password_input.get() == "" or self.password_input2.get() == "" \
                or self.display_name_input.get() == "" or self.email_input.get() == "":
            return True
        if self.password_input.get() != self.password_input2.get():
            return True
        if "@" not in self.email_input.get():
            return True
        return False

    def switch_to_login(self):
        self.switch_screen(ScreensEnum.LOGIN)

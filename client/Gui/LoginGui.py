from requests import post, get
import json
import ScreensEnum

URL = "http://127.0.0.1:5000"
import ScreensEnum
from tkinter import *
from tkinter import ttk


class LoginGui:
    def __init__(self, root, switch_screen, clear_canvas, save_user_data):
        self.root = root
        self.login_input = None
        self.password_input = None
        self.login_button = None
        self.register_button = None
        self.forgot_password_button = None
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.generate_gui()
        self.save_user_data = save_user_data

    def generate_gui(self):
        self.clear_canvas()
        text = Label(self.root, text="UserName", font=("Arial", 20))
        text.pack()
        self.login_input = Entry(self.root, font=("Arial", 15))
        self.login_input.pack()
        text = Label(self.root, text="Password", font=("Arial", 20), show="*")
        text.pack()
        self.password_input = Entry(self.root, font=("Arial", 15))
        self.password_input.pack()
        self.login_button = Button(self.root, text="Login", font=("Arial", 15), command=self.login)
        self.login_button.pack()
        self.register_button = Button(self.root, text="Register", font=("Arial", 15), command=self.switch_to_register)
        self.register_button.pack()
        self.forgot_password_button = Button(self.root, text="Forgot password", font=("Arial", 15),
                                             command=self.switch_to_forgot_password)
        self.forgot_password_button.pack()

    def login(self):
        if self.login_input.get() == "" or self.password_input.get() == "":
            print("Please fill all fields")
            return
        else:
            r = post(URL + "/login", data={"userName": self.login_input.get(), "password": self.password_input.get()})
            data = r.json()
            if data["status"] == "success":
                self.save_user_data(data["user"])
                self.switch_screen(ScreensEnum.ScreensEnum.LOBBIES)
            else:
                print("Failed to log in")

    def switch_to_register(self):
        self.switch_screen(ScreensEnum.ScreensEnum.REGISTER)

    def switch_to_forgot_password(self):
        self.switch_screen(ScreensEnum.ScreensEnum.FORGOT_PASSWORD)

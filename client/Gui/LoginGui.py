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
        self.loginInput = None
        self.passwordInput = None
        self.loginButton = None
        self.registerButton = None
        self.forgotPasswordButton = None
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.generateGui()
        self.save_user_data = save_user_data

    def generateGui(self):
        self.clear_canvas()
        text = Label(self.root, text="UserName", font=("Arial", 20))
        text.pack()
        self.loginInput = Entry(self.root, font=("Arial", 15))
        self.loginInput.pack()
        text = Label(self.root, text="Password", font=("Arial", 20))
        text.pack()
        self.passwordInput = Entry(self.root, font=("Arial", 15))
        self.passwordInput.pack()
        self.loginButton = Button(self.root, text="Login", font=("Arial", 15), command=self.login)
        self.loginButton.pack()
        self.registerButton = Button(self.root, text="Register", font=("Arial", 15), command=self.switch_to_register)
        self.registerButton.pack()
        self.forgotPasswordButton = Button(self.root, text="Forgot password", font=("Arial", 15),
                                           command=self.switch_to_forgot_password)
        self.forgotPasswordButton.pack()

    def login(self):
        if self.loginInput.get() == "" or self.passwordInput.get() == "":
            print("Please fill all fields")
            return
        else:
            r = post(URL + "/login", data={"userName": self.loginInput.get(), "password": self.passwordInput.get()})
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

from requests import post, get
import json
import ScreensEnum

URL = "http://127.0.0.1:5000"
import ScreensEnum
from tkinter import *
from tkinter import ttk


class ForgotPasswordGui:
    def __init__(self, root, switch_screen, clear_canvas):
        self.root = root
        self.email = None
        self.code = None
        self.confirmButton = None
        self.password = None
        self.confirmPassword = None
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.generateEmailSection()

    def generateEmailSection(self):
        self.clear_canvas()
        text = Label(self.root, text="Email", font=("Arial", 20))
        text.pack()
        self.email = Entry(self.root, font=("Arial", 15))
        self.email.pack()
        self.confirmButton = Button(self.root, text="Send password", font=("Arial", 15),
                                           command=self.generate_email_code)
        self.confirmButton.pack()
    def generateCodeSection(self):
        self.clear_canvas()
        text = Label(self.root, text="Code", font=("Arial", 20))
        text.pack()
        self.code = Entry(self.root, font=("Arial", 15))
        self.code.pack()
        self.confirmButton = Button(self.root, text="Confirm", font=("Arial", 15),
                                           command=self.verify_code)
        self.confirmButton.pack()

    def generatePasswordSection(self):
        self.clear_canvas()
        text = Label(self.root, text="Password", font=("Arial", 20))
        text.pack()
        self.password = Entry(self.root, font=("Arial", 15))
        self.password.pack()
        text = Label(self.root, text="Confirm password", font=("Arial", 20))
        text.pack()
        self.confirmPassword = Entry(self.root, font=("Arial", 15))
        self.confirmPassword.pack()
        self.confirmButton = Button(self.root, text="Confirm", font=("Arial", 15),
                                           command=self.change_password)
        self.confirmButton.pack()


    def generate_email_code(self):
        if self.email.get() == "":
            print("Please fill all fields")
            return
        if "@" not in self.email.get():
            print("Please enter a valid email")
            return
        r = post(URL + "/forgot_password", data={"email": self.email.get()})
        data = r.json()
        if data["status"] == "success":
            self.generateCodeSection()
        else:
            print("Failed to send email")

    def verify_code(self):
        if self.code.get() == "":
            print("Please fill all fields")
            return
        r = post(URL + "/verify_code", data={"code": self.code.get(), "email": self.email.get()})
        data = r.json()
        if data["status"] == "success":
            self.switch_screen(ScreensEnum.ScreensEnum.LOGIN)
        else:
            print("Failed to verify code")

    def change_password(self):
        if self.password.get() == "" or self.confirmPassword.get() == "":
            print("Please fill all fields")
            return
        if self.password.get() != self.confirmPassword.get():
            print("Passwords don't match")
            return
        r = post(URL + "/change_password", data={"password": self.password.get(), "email": self.email.get()})
        data = r.json()
        if data["status"] == "success":
            self.switch_screen(ScreensEnum.ScreensEnum.LOGIN)
        else:
            print("Failed to change password")
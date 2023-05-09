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
        self.own_email = ''
        self.email = None
        self.code = None
        self.confirm_button = None
        self.password = None
        self.confirm_password = None
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.generate_email_section()

    def generate_email_section(self):
        self.clear_canvas()
        text = Label(self.root, text="Email", font=("Arial", 20))
        text.pack()
        self.email = Entry(self.root, font=("Arial", 15))
        self.email.pack()
        self.confirm_button = Button(self.root, text="Send password", font=("Arial", 15),
                                     command=self.generate_email_code)
        self.confirm_button.pack()

    def generate_code_section(self):
        self.clear_canvas()
        text = Label(self.root, text="Code", font=("Arial", 20))
        text.pack()
        self.code = Entry(self.root, font=("Arial", 15))
        self.code.pack()
        self.confirm_button = Button(self.root, text="Confirm", font=("Arial", 15),
                                     command=self.verify_code)
        self.confirm_button.pack()

    def generate_password_section(self):
        self.clear_canvas()
        text = Label(self.root, text="Password", font=("Arial", 20))
        text.pack()
        self.password = Entry(self.root, font=("Arial", 15), show="*")
        self.password.pack()
        text = Label(self.root, text="Confirm password", font=("Arial", 20))
        text.pack()
        self.confirm_password = Entry(self.root, font=("Arial", 15), show="*")
        self.confirm_password.pack()
        self.confirm_button = Button(self.root, text="Confirm", font=("Arial", 15),
                                     command=self.change_password)
        self.confirm_button.pack()

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
            self.own_email = self.email.get()
            self.generate_code_section()
        else:
            print("Failed to find user")

    def verify_code(self):
        if self.code.get() == "":
            print("Please fill all fields")
            return
        r = post(URL + "/verify_code", data={"code": self.code.get(), "email": self.own_email})
        data = r.json()
        print(data)
        if data["status"] == "success":
            self.generate_password_section()
        else:
            print(data)
            print("Failed to verify code")

    def change_password(self):
        if self.password.get() == "" or self.confirm_password.get() == "":
            print("Please fill all fields")
            return
        if self.password.get() != self.confirm_password.get():
            print("Passwords don't match")
            return
        r = post(URL + "/change_password", data={"password": self.password.get(), "email": self.own_email})
        data = r.json()
        if data["status"] == "success":
            self.switch_screen(ScreensEnum.ScreensEnum.LOGIN)
        else:
            print("Failed to change password")

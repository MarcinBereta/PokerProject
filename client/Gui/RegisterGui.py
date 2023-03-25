from requests import post, get
import json
import ScreensEnum

URL = "http://127.0.0.1:5000"
import ScreensEnum
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


class RegisterGui:
    def __init__(self, root, switch_screen, clear_canvas, save_user_data):
        self.emailInput = None
        self.root = root
        self.nameInput = None
        self.displayNameInput = None
        self.passwordInput = None
        self.passwordInput2 = None
        self.imageInput = None
        self.loginButton = None
        self.registerButton = None
        self.forgotPasswordButton = None
        self.files = None
        self.switch_screen = switch_screen
        self.clear_canvas = clear_canvas
        self.generateGui()
        self.save_user_data = save_user_data


    def generateGui(self):
        self.clear_canvas()
        text = Label(self.root, text="Email", font=("Arial", 20))
        text.pack()
        self.emailInput = Entry(self.root, font=("Arial", 15))
        self.emailInput.pack()
        text = Label(self.root, text="Name", font=("Arial", 20))
        text.pack()
        self.nameInput = Entry(self.root, font=("Arial", 15))
        self.nameInput.pack()
        text = Label(self.root, text="Username", font=("Arial", 20))
        text.pack()
        self.displayNameInput = Entry(self.root, font=("Arial", 15))
        self.displayNameInput.pack()
        text = Label(self.root, text="Password", font=("Arial", 20))
        text.pack()
        self.passwordInput = Entry(self.root, font=("Arial", 15))
        self.passwordInput.pack()
        text = Label(self.root, text="Confirm Password", font=("Arial", 20))
        text.pack()
        self.passwordInput2 = Entry(self.root, font=("Arial", 15))
        self.passwordInput2.pack()
        self.imageInput = Button(self.root, text="Select files", font=("Arial", 15), command=self.select_image)
        self.imageInput.pack()
        self.registerButton = Button(self.root, text="Register", font=("Arial", 15), command=self.register)
        self.registerButton.pack()
        self.loginButton = Button(self.root, text="Login", font=("Arial", 15), command=self.switch_to_login)
        self.loginButton.pack()

    def select_image(self):
        files = filedialog.askopenfilenames(filetypes=(("Image files", "*.jpg *.png"), ("all files", "*.*")))
        self.files = files[0]

    def register(self):
        if self.validateForm():
            print("Please fill all fields")
            return
        else:
            r = post(URL + "/register", data={
                "name": self.nameInput.get(),
                'displayName': self.displayNameInput.get(),
                "email": self.emailInput.get(),
                "password": self.passwordInput.get(),
                 }, files={'file': open(self.files, 'rb')})
            data = r.json()
            if data["status"] == "success":
                print("You have been registered")
            else:
                print("Failed to log in")

    def validateForm(self):
        if self.nameInput.get() == "" or self.passwordInput.get() == "" or self.passwordInput2.get() == ""\
                or self.displayNameInput.get() == "" or self.emailInput.get() == "":
            return True
        if self.passwordInput.get() != self.passwordInput2.get():
            return True
        if "@" not in self.emailInput.get():
            return True
        return False

    def switch_to_login(self):
        self.switch_screen(ScreensEnum.ScreensEnum.LOGIN)

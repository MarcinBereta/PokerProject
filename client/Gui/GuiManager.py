import time
from tkinter import *
from tkinter import ttk
import ScreensEnum
from client.Gui.ForgotPasswordGui import ForgotPasswordGui
from client.Gui.LobbyGui import LobbyGui
from client.Gui.LoginGui import LoginGui
from client.Gui.RegisterGui import RegisterGui


class GuiManager:
    def __init__(self):
        self.mainScreen = None
        self._gui = None
        self.username = None
        self.userId = None
        self.currentScreen = ScreensEnum.ScreensEnum.REGISTER
        self._root = Tk()
        self._root.title("Poker online")
        self._root.geometry("800x600")
        self._root.resizable(False, False)
        self.load_screen()
        self._root.mainloop()

    def load_screen(self):
        if self.currentScreen == ScreensEnum.ScreensEnum.LOBBIES:
            self.mainScreen = LobbyGui(self._root, self.change_screen, self.clear_canvas, self.userId, self.username)
            # self.mainScreen.launch_gui()
        elif self.currentScreen == ScreensEnum.ScreensEnum.LOGIN:
            self.mainScreen = LoginGui(self._root, self.change_screen, self.clear_canvas, self.save_user_data)
        elif self.currentScreen == ScreensEnum.ScreensEnum.REGISTER:
            self.mainScreen = RegisterGui(self._root, self.change_screen, self.clear_canvas, self.save_user_data)
        elif self.currentScreen == ScreensEnum.ScreensEnum.FORGOT_PASSWORD:
            self.mainScreen = ForgotPasswordGui(self._root, self.change_screen, self.clear_canvas)
    def change_screen(self, screen):
        self.currentScreen = screen
        self.load_screen()

    def clear_canvas(self):
        for item in self._root.winfo_children():
            item.destroy()

    def save_user_data(self, username, userId):
        self.username = username
        self.userId = userId
myGui = GuiManager()

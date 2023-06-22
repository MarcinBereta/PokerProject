from tkinter import *
import ScreensEnum
from ForgotPasswordGui import ForgotPasswordGui
from LobbyGui import LobbyGui
from LoginGui import LoginGui
from RegisterGui import RegisterGui
from GameGui import GameGui
from LeaderBoard import LeaderBoardGui
from UserProfileGui import UserProfileGui


class GuiManager:
    def __init__(self):
        self.mainScreen = None
        self._gui = None
        self.username = ""
        self.userId = ""
        self.game_id = None
        self.current_screen = ScreensEnum.ScreensEnum.LOGIN
        self._root = Tk()
        self._root.title("Poker online")
        # self._root.geometry("800x600")
        self._root.resizable(False, False)
        self.save = None
        self.root_to_destroy = False
        self.load_screen()

        self.game_data = None

    def load_screen(self):
        if self.current_screen == ScreensEnum.ScreensEnum.LOBBIES:
            self.mainScreen = LobbyGui(self._root, self.change_screen, self.clear_canvas, self.userId, self.username,
                                       self.save_game_data)
        elif self.current_screen == ScreensEnum.ScreensEnum.LOGIN:
            self.mainScreen = LoginGui(self._root, self.change_screen, self.clear_canvas, self.save_user_data)
            self._root.mainloop()
        elif self.current_screen == ScreensEnum.ScreensEnum.REGISTER:
            self.mainScreen = RegisterGui(self._root, self.change_screen, self.clear_canvas, self.save_user_data)
            self._root.mainloop()
        elif self.current_screen == ScreensEnum.ScreensEnum.FORGOT_PASSWORD:
            self.mainScreen = ForgotPasswordGui(self._root, self.change_screen, self.clear_canvas)
            self._root.mainloop()
        elif self.current_screen == ScreensEnum.ScreensEnum.GAME:
            self.mainScreen = GameGui(self._root, self.change_screen, self.clear_canvas, self.userId, self.username,
                                      self.game_id)
        elif self.current_screen == ScreensEnum.ScreensEnum.USER_PROFILE:
            self.current_screen = UserProfileGui(self._root, self.change_screen, self.clear_canvas, self.userId,
                                                 self.save_user_data)
        elif self.current_screen == ScreensEnum.ScreensEnum.LEADERBOARD:
            self.mainScreen = LeaderBoardGui(self._root, self.change_screen, self.clear_canvas)

    def change_screen(self, screen):
        self.current_screen = screen
        self.clear_canvas()
        self.load_screen()

    def clear_canvas(self):
        for item in self._root.winfo_children():
            item.destroy()

    def save_user_data(self, data):
        self.username = data['username']
        self.userId = data['_id']

    def save_game_data(self, game_id):
        self.game_id = game_id


myGui = GuiManager()

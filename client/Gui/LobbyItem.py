class LobbyItem:
    def __init__(self, root, lobbyId, lobbyName, players, maxPlayers):
        self.tk = root
        self.lobbyId = lobbyId
        self.lobbyName = lobbyName
        self.players = players
        self.maxPlayers = maxPlayers
    def generateGui(self, frame):
        self.frame = frame
        self.lobbyNameLabel = self.tk.Label(self.frame, text=self.lobbyName, font=("Arial", 15))
        self.lobbyNameLabel.grid(row=0, column=0, sticky="W")
        self.playersLabel = self.tk.Label(self.frame, text="Players: " + str(len(self.players)) + "/" + str(self.maxPlayers), font=("Arial", 15))
        self.playersLabel.grid(row=1, column=0, sticky="W")
        self.joinButton = self.tk.Button(self.frame, text="Join", font=("Arial", 15), command=self.join)
        self.joinButton.grid(row=2, column=0, sticky="W")
    def join(self):
        print("Joining lobby")

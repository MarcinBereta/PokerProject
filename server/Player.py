from CardUtility import Hand


class Player:
    ACTION_FOLD = "FOLD"
    ACTION_CALL = "CALL"
    ACTION_RAISE = "RAISE"

    def __init__(self, name, uuid, initial_stack) -> None:
        self.uuid = uuid
        self.name = name
        self.stack = initial_stack
        self.hand = Hand()
        self.is_active = True
        self.is_playing = True

        self.stake = 0

    def pop_cards(self):
        return self.hand.pop_all()

    def add_cards(self, cards):
        for card in cards:
            self.hand.add_card(card)

    def potential_moves(self) -> object:
        if self.stake_gap == 0:
            return {1: "check", 2: "raise", 3: "fold"}

        if self.chips > self.stake_gap:
            return {1: "call", 2: "raise", 3: "fold"}

        if self.chips <= self.stake_gap:
            return {1: "all_in", 2: "all_in", 3: "fold"}

    def add_chips(self, amount):
        self.stack += amount

    def bet_chips(self, bet):
        if self.stack <= bet:
            bet = self.stack
        self.stack -= bet
        self.stake += bet

        return bet

    def get_cards(self):
        return self.hand.get_cards_path_name()

    def reset_stake(self):
        self.stake = 0

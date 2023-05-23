from CardUtility import Hand

class Player: 
    def __init__(self, name=None, id=0, table_no = None, starting_money = 100) -> None:
        self.player_id = id
        self.name = name
        self.hand = Hand()
        self.all_in = False
        self.stake_gap = 0
        self.stake = 0
        self.table_no = table_no
        self.chips = starting_money

    def potential_moves(self) -> object:
        moves = {}
        if self.stake_gap == 0:
            moves = {1:"check", 2:"raise", 3:"fold"}
        else:
            if self.chips > self.stake_gap:
                moves = {1:"call", 2:"raise", 3:"fold"}
            if self.chips <= self.stake_gap:
                moves = {1:"all_in", 2:"all_in", 3:"fold"}
        return moves
    
    def set_chips(self, chips):
        self.chips = chips

    def bet_chips(self, bet):
        self.stake += bet
        self.chips -= bet
        self.stake_gap = 0
    
    def get_cards(self):
        return self.hand.get_cards_path_name()
    
    def reset_stake(self):
        self.stake_gap = 0
        self.stake = 0
        self.all_in = False
            
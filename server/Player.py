from CardUtility import Hand

class Player: 
    def __init__(self, name=None, id=0, table_no = None) -> None:
        self.player_id = id
        self.name = name
        self.chips = 100
        self.hand = Hand()
        self.all_in = False
        self.stake_gap = 0
        self.stake = 0
        self.table_no = table_no

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
    
    def get_cards(self):
        return self.hand.get_cards_path_name()
    
    def reset_stake(self):
        self.stake_gap = 0
        self.stake = 0
        self.all_in = False
            
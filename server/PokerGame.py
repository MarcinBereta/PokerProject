from pymongo import MongoClient
from CardUtility import Deck
from Player import Player
from PokerHand import PokerHand
from Tables import Table

cluster = "mongodb+srv://Mardorus:PokerAGH@poker.gmn3mgg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cluster)


class PokerGame(object):
    def __init__(self) -> None:
        self.deck                   = Deck()
        self.game_pot               = 0
        self.big_blind              = None
        self.small_blind            = None 
        self.last_player            = None
        self.raise_stage            = False
        self.player_index           = 0
        self.tables                 = None
        self.owner                  = None
        
        self.highest_stake          = self.big_blind
        self.winner                 = None
        self.round_no               = 0 
        
        self.turn_no                = 0
        self.db                     = client['poker']
        
    def config(self, settings):
        self.starting_money         = settings['startingMoney']
        self.big_blind              = settings['bigBlind']
        self.small_blind            = int(self.big_blind*0.5)
        self.owner                  = settings['owner']
        
        if self.tables is None:
            self.tables = Table()
        
        for player in settings['players']:
            if player['playerId'] not in self.tables.players:
                self.tables.sitdown(Player(player['username'], player['playerId'], self.starting_money))        
    
    def _player_left_game(self, uuid):
        self.tables.player_left(uuid)
        
    def transfer_chips(self, uuid, amout, player=False):
        if player is False:
            chips = self.tables.players[uuid].bet_chips(amout)
            self.game_pot += chips
        else:
            self.tables.players[uuid].add_chips(self.game_pot)
            self.game_pot = 0
        
    def clear_table(self):
        self.game_pot = 0
        self.tables.reset_state()

        for player in self.tables.players.values():
            self.deck.add_card(player.pop_cards())

        self.deck.add_card(self.tables.pop_cards())
        self.deck.shuffle()

        self.highest_stake = 0
        self.winner = None
        self.round_no += 1 
        self.highest_stake = self.big_blind
        self.tables.set_blind(self.round_no, self.round_no+1)

        self.transfer_chips(self.tables.get_big_blind().uuid, self.big_blind)
        self.transfer_chips(self.tables.get_small_blind().uuid, self.small_blind)

        self.player_index = self.tables.set_player_turn(self.round_no + 2)
        self.last_player  = self.tables.set_last_player(self.round_no + 1)
        self.turn_no = 0

    def calculate_move(self, uuid, move, amount):
        if move == 1:
            self.check_action(uuid)
        if move == 2:
            self.raise_action(uuid, amount)
        if move == 3:
            self.fold_action(uuid)

    def player_left_table(self, uuid):
        self.tables.player_stop_playing(uuid)

        if self.tables.count_active() == 1:
            self.handle_end_game()
            return 
        
        if uuid == self.player_index:
            self.player_index = self.tables.get_next_player()
        
        if uuid == self.last_player:
            self.last_player = self.tables.get_prev_player()
            self.tables.set_last_player()

    
    def check_action(self, uuid):  
        if uuid != self.player_index:
            return
        
        gap = self.highest_stake - self.tables.get_player(uuid).stake

        if gap != 0:
            self.call_action(uuid)
            return

        if uuid == self.last_player:
            self.handle_end_of_turn()
        else:
            self.player_index = self.tables.get_next_player()

    def call_action(self, uuid):
        if uuid != self.player_index:
            return

        gap = self.highest_stake - self.tables.get_player(uuid).stake

        if gap == 0:
            self.check_action(uuid)
            return  
        
        self.transfer_chips(uuid, gap)
                    
        if uuid == self.last_player:
            self.handle_end_of_turn()
        else:
            self.player_index = self.tables.get_next_player()

    def raise_action(self, uuid, amount):
        if uuid != self.player_index:
           return
  
        gap = self.highest_stake - self.tables.get_player(uuid).stake
        self.transfer_chips(uuid, gap + amount)
        self.highest_stake = self.highest_stake + amount

        self.last_player = self.tables.get_prev_player()
        self.player_index = self.tables.get_next_player()

    def fold_action(self, uuid):
        if uuid != self.player_index:
            return
        

        self.tables.player_left(uuid)

        if self.tables.count_active() == 1:
            self.handle_end_game()
            return

        if uuid == self.last_player:
            self.handle_end_of_turn()
        else:
            self.player_index = self.tables.get_next_player()

    def handle_end_of_turn(self):
        if self.turn_no == 0:
            self.deck.give_cards(self.tables.community_cards, 3)
        elif self.turn_no <= 2:
            self.deck.give_cards(self.tables.community_cards, 1)
        else:
            self.handle_end_game()

        self.player_index = self.tables.set_player_turn(self.round_no - 1)
        self.last_player = self.tables.set_last_player(self.round_no - 2)

        self.highest_stake = 0

        for player in self.tables.ordered_players:
            player.reset_stake()

        self.turn_no += 1

    def handle_end_game(self):
        user_score = 0
        winner_score = math.inf

        for i in self.tables.ordered_players:
            if i.is_active == False or i.is_playing == False:
                user_score = math.inf
            else:
                user_score = PokerHand(i.hand, self.tables.community_cards).evaluateHand()
                                
            if user_score < winner_score:
                winner_score = user_score
                self.winner = i.uuid

            i.reset_stake()
        
        self.transfer_chips(self.winner, self.game_pot, True)

        self.db['scores'].insert_one({
            "userId": i.uuid,
            "score": user_score,
            "username": i.name,
            'timestamp': datetime.utcnow()
        })
                
        self.tables.reset_state()

    def get_data(self):
        board = self.tables.community_cards.get_cards_path_name()

        tables = {}
        stakes = {}
        cards = {}
        player_info = {}

        for i, player in enumerate(self.tables.ordered_players):
            if player.is_active is True and player.is_playing is True:
                tables[player.uuid] = i

            stakes[player.uuid] = player.stack
            player_info[player.uuid] = player.name

        if self.winner is not None:
            cards = self.get_all_player_cards()

        return {
            'pot': self.game_pot,
            'highest_stake': self.highest_stake,
            'board_cards': board,
            'players_at_table': tables,
            'big_blind': self.tables.get_big_blind().uuid,
            'small_blind': self.tables.get_small_blind().uuid,
            'actual_id': self.player_index,
            'stakes': stakes,
            'all_cards': cards,
            'winner': self.winner,
            'players_info': player_info
        }

    def get_all_player_cards(self):
        cards = {}

        for player in self.tables.ordered_players:
            if player.is_active is True and player.is_playing is True:
                cards[player.uuid] = [player.hand.get_cards_path_name()]

        return cards

    def start(self):
        self.clear_table()

        for player in self.tables.players.values():
            self.deck.give_cards(player.hand, 2)            
    

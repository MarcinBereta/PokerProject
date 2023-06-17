from datetime import datetime
from pymongo import MongoClient

from CardUtility import Hand, Deck, Card
from Player import Player
from PokerHand import PokerHand
from Tables import Table
import math
from copy import copy

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
        
        self.highest_stake          = self.big_blind
        self.winner                 = None
        self.round_no               = 0 
        
        self.turn_no                = 0
        
    def config(self, settings):
        self.starting_money         = settings['startingMoney']
        self.big_blind              = settings['bigBlind']
        self.small_blind            = int(self.big_blind*0.5)
        self.tables                 = Table()
        
        for player in settings['players']:
            self.tables.sitdown(Player(player['username'], player['playerId'], self.starting_money))        
    
    def _player_left_game(self, uuid):
        self.tables.player_left(uuid)
        
    def transfer_chips(self, uuid, amout):
        self.game_log.write(f"{uuid} transfered chips to pot\n")
        self.table.players[uuid].bet_chips(amout)
        self.game_pot += amout
        
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
        
        self.tables.get_big_blind().bet_chips(self.big_blind)
        self.tables.get_small_blind().bet_chips(self.small_blind)
        
        self.game_pot += (self.big_blind + self.small_blind)
        
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
        
        if uuid == self.last_player:
            self.handle_end_of_turn()
        else:
            self.player_index = self.tables.get_next_player()
    
    def check_action(self, uuid):  
        if uuid != self.player_index:
            uuid = self.player_index
        
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
            # return
            uuid = self.player_index
        
        gap = self.highest_stake - self.tables.get_player(uuid).stake
        
        if gap == 0:
            self.check_action(uuid)
            # return
            return  
        
        chips = self.tables.players[uuid].bet_chips(gap)
        self.game_pot += chips
                    
        if uuid == self.last_player:
            self.handle_end_of_turn()
        else:
            self.player_index = self.tables.get_next_player()
        
    def raise_action(self, uuid, amount):
        if uuid != self.player_index:
            # return
            uuid = self.player_index
  
        gap = self.highest_stake - self.tables.get_player(uuid).stake
        chips = self.tables.players[uuid].bet_chips(gap + amount)
        self.highest_stake = self.highest_stake + amount
        
        self.last_player = self.tables.get_prev_player()
        self.game_pot += chips
        self.player_index = self.tables.get_next_player()
        
    def fold_action(self, uuid):
        if uuid != self.player_index:
            uuid = self.player_index
        
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
            
        self.player_index   = self.tables.set_player_turn(self.round_no - 1)
        self.last_player    = self.tables.set_last_player(self.round_no - 2)
    
        self.highest_stake = 0

        for player in self.tables.ordered_players:
            player.reset_stake()

        self.turn_no += 1
        
    def handle_end_game(self):
        if self.tables.count_active() == 1:
            for player in self.tables.ordered_players:
                if player.is_playing == True:
                    user_score = 1
                    self.winner = player.uuid
                    self.tables.players[self.winner].add_chips(self.game_pot)
                    return 

        for i in self.tables.ordered_players:
            if i.is_active == False or i.is_playing == False:
                user_score = 0 
            else:
                user_score = PokerHand(i.hand, self.tables.community_cards).evaluateHand()
                
            winner_score = 0
                
            if user_score > winner_score:
                winner_score = user_score
                self.winner = i.uuid

                # self.db['scores'].insert_one({
                #     "userId": i.uuid,
                #     "score": user_score,
                #     "username": i.name,
                #     'timestamp': datetime.datetime.utcnow()
                # })
                
        self.tables.players[self.winner].add_chips(self.game_pot)
        self.tables.reset_state()
                
    def get_data(self):
        board = self.tables.community_cards.get_cards_path_name()

        tables = {}
        stakes = {}
        cards = {}
        player_info = {}

        for i, player in enumerate(self.tables.ordered_players):
            # print(i, player)
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
            
    
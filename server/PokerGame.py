from datetime import datetime

from pymongo import MongoClient

from CardUtility import Hand, Deck, Card
from Player import Player
from PokerHand import PokerHand
import math
from copy import copy

cluster = "mongodb+srv://Mardorus:PokerAGH@poker.gmn3mgg.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cluster)

class PokerGame(object):
    def __init__(self, game_settings=None) -> None:

        self.cards = Hand()
        self.deck = Deck()
        self.pot = 0
        self.db = client['poker']
        self.list_of_players = []
        self.list_of_active_players = []

        self.big_blind = 8
        self.small_blind = int(self.big_blind * 0.5)
        self.flop = True

        self.last = 0
        self.last_after_rise = 0

        self.raise_stage = False

        self.round_no = 0
        self.player_index = 0
        self.tables = {}

        self.highest_stake = self.big_blind

        self.big_blind_player = None
        self.small_blind_player = None
        self.winner = None

        self.players_info = {}

    def config(self, data):
        self.starting_money = data['startingMoney']

    def get_moves(self, index):
        return self.list_of_active_players[index].potential_moves()

    def set_stake(self, index):
        self.list_of_active_players[index].stake_gap = self.highest_stake - self.list_of_active_players[index].stake

    # get actual game data
    def get_data(self):
        board = self.cards.get_cards_path_name()

        tables = {}
        stakes = {}
        cards = {}

        for i in self.list_of_active_players:
            tables[i.player_id] = i.table_no
            stakes[i.player_id] = i.chips

        if self.winner is not None:
            for i in self.list_of_active_players:
                cards[i.player_id] = i.get_cards()

        return {
            'pot': self.pot,
            'highest_stake': self.highest_stake,
            'board_cards': board,
            'players_at_table': tables,
            'big_blind': self.list_of_players[self.big_blind_player].player_id,
            'small_blind': self.list_of_players[self.small_blind_player].player_id,
            'actual_id': self.list_of_active_players[self.player_index].player_id,
            'stakes': stakes,
            'all_cards': cards,
            'winner': self.winner,
            'players_info': self.players_info
        }

    def get_actual_id(self):
        return self.list_of_active_players[self.player_index].player_id

    def parse_players(self, data):
        for i in data:
            self.list_of_players.append(
                Player(i['username'], i['playerId'], len(self.list_of_players), self.starting_money))
            self.players_info[i['playerId']] = i['username']

    def raise_bet(self, id: int, bet) -> None:
        self.raise_stage = True

        bet += self.list_of_active_players[id].stake_gap

        self.list_of_active_players[id].bet_chips(bet)
        self.highest_stake = self.list_of_active_players[id].stake

        self.pot += bet
        self.last_after_rise = id

    def calculate_move(self, response):
        # print(f"LAST: {self.last}")
        # print(f"ACTUAL: {self.player_index}\n\n")

        self.set_stake(self.player_index)
        potential_moves = self.get_moves(self.player_index)

        if potential_moves[response] == "raise":
            self.raise_bet(self.player_index, 5)

        if potential_moves[response] == "fold":
            self.fold(self.player_index)
            self.player_index %= len(self.list_of_active_players)
            return

        if potential_moves[response] == "call" or potential_moves[response] == "all_in":
            self.call(self.player_index)

        if potential_moves[response] == "check":
            if self.raise_stage == True or self.flop == True or self.player_index == self.last:
                self.end_of_turn()
                return

        self.player_index = (self.player_index + 1) % len(self.list_of_active_players)

    def get_player_id(self, index):
        return self.list_of_active_players[index].player_id

    def fold(self, index: int):
        # set fold variable to true
        actual_player_id = self.get_player_id(index)

        # end turn if it was the last player and mark previous player as the last one 

        if actual_player_id == self.small_blind_player:
            self.small_blind_player = self.get_player_id(
                (index - 1 + len(self.list_of_active_players)) % len(self.list_of_active_players))

        if self.raise_stage:
            self.list_of_active_players.remove(self.list_of_active_players[index])

            if len(self.list_of_active_players) == 1:
                self.find_winner()

            return

        if self.last == index or self.last == actual_player_id:
            # self.last = self.get_player_id((index-1+len(self.list_of_active_players))%len(self.list_of_active_players))
            self.list_of_active_players.remove(self.list_of_active_players[index])
            self.end_of_turn()
            return

        self.list_of_active_players.remove(self.list_of_active_players[index])

        if len(self.list_of_active_players) == 1:
            self.find_winner()

        # remove player from active players

    def call(self, id: int) -> None:
        # all in! 
        if self.list_of_active_players[id].chips <= self.list_of_active_players[id].stake_gap:
            self.list_of_active_players[id].stake += self.list_of_active_players[id].chips
            self.pot += self.list_of_active_players[id].chips
            self.list_of_active_players[id].all_in = True
            return

        # transfer chips from player to pot
        self.list_of_active_players[id].stake += self.list_of_active_players[id].stake_gap
        self.pot += self.list_of_active_players[id].stake_gap
        self.list_of_active_players[id].chips -= self.list_of_active_players[id].stake_gap
        self.list_of_active_players[id].stake_gap = 0

    def find_winner(self):
        winner_id = 0
        winner_score = math.inf

        if len(self.list_of_active_players) == 1:
            self.winner_id = self.list_of_active_players[0].player_id
            self.winner = self.list_of_active_players[0].player_id
            self.list_of_active_players[0].chips += self.pot
            return

        for i in range(len(self.list_of_active_players)):
            user_score = PokerHand(self.list_of_active_players[i].hand, self.cards).evaluateHand()
            if user_score > winner_score:
                winner_score = user_score
                winner_id = i

                self.db['scores'].insert_one({
                    "userId": self.list_of_players[i].player_id,
                    "score": user_score,
                    "username": self.list_of_players[i].name,
                    'timestamp': datetime.datetime.utcnow()
                })

        print(f"PLAYER {self.list_of_active_players[winner_id].player_id} WINS\n")
        self.winner = self.list_of_active_players[winner_id].player_id
        self.list_of_active_players[winner_id].chips += self.pot

    def clear_table(self):
        self.deck = Deck()
        self.pot += self.big_blind + self.small_blind
        self.cards = Hand()
        self.highest_stake = 0
        self.list_of_active_players = copy(self.list_of_players)
        self.flop = True
        self.round_no += 1
        self.winner = None

        map(lambda x: x.reset_stake(), self.list_of_players)

        self.highest_stake = self.big_blind

        self.big_blind_player = (self.round_no + 1) % len(self.list_of_active_players)
        self.small_blind_player = self.big_blind_player - 1

        if self.small_blind_player < 0:
            self.small_blind_player += len(self.list_of_active_players)

        self.list_of_active_players[self.big_blind_player].chips -= self.big_blind
        self.list_of_active_players[self.big_blind_player].stake = self.big_blind

        self.list_of_active_players[self.small_blind_player].chips -= self.small_blind
        self.list_of_active_players[self.small_blind_player].stake = self.small_blind

        for i in range(len(self.list_of_active_players)):
            if i != self.small_blind_player and i != self.big_blind_player:
                self.list_of_active_players[i].stake_gap = 0

        self.last = self.big_blind_player
        self.player_index = (self.big_blind_player + 1) % len(self.list_of_active_players)

    def end_of_turn(self):
        map(lambda x: x.reset_stake(), self.list_of_players)

        self.raise_stage = False

        if self.flop:
            self.last = self.small_blind_player - 1
            if self.last < 0:
                self.last += len(self.list_of_active_players)

            self.player_index = self.small_blind_player

            self.deck.give_cards(self.cards, 3)
            self.flop = False
            return

        # self.last = self.list_of_active_players[(self.round_no-1+len(self.list_of_active_players))%len(self.list_of_active_players)].player_id

        if len(self.list_of_active_players) <= 1:
            self.find_winner()
            return

        self.last = self.small_blind_player - 1
        self.player_index = self.small_blind_player

        if len(self.cards.cards) < 5:
            self.deck.give_cards(self.cards, 1)
            print(f"\n Cards at desk:\n {self.cards}")
            return

        if len(self.cards.cards) == 5:
            self.find_winner()
            return

    def start(self) -> None:
        if len(self.list_of_players) < 2:
            print(f"Not enough players...\n")
            return

        self.clear_table()
        self.player_index = (self.round_no + 2) % len(self.list_of_active_players)

        for i in range(len(self.list_of_active_players)):
            self.deck.give_cards(self.list_of_active_players[i].hand, 2)

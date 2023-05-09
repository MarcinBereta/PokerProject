from CardUtility import Hand, Deck, Card
from Player import Player
from PokerHand import PokerHand
import math
from copy import copy

class PokerGame(object):
    def __init__(self) -> None:
        self.cards = Hand()
        self.pot = 0
        self.deck = Deck()
        self.list_of_players = []
        self.list_of_active_players = []
        self.big_blind = 8
        self.small_blind = int(self.big_blind * 0.5)
        self.flop = True
        self.last = 0
        self.round_no = 0
        # self.flop_rise = False
        self.player_index = 0
        self.tables = {}
        self.highest_stake = self.big_blind
        self.player_raised = False

        self.big_blind_player = None
        self.small_blind_player = None

        self.winner = None


    def calculate_move(self, response):
        self.list_of_active_players[self.player_index].stake_gap = self.highest_stake - self.list_of_active_players[self.player_index].stake

        # print("\n-----------------GAME_INFO-------------------------")
        # print("FLOP:", self.flop)
        # print(f"POT: {self.pot}")
        # print(f"NO. PLAYERS:", len(self.list_of_active_players))
        # print(f"BIG BLIND {self.big_blind} AT PLAYER {self.big_blind_player}")
        # print(f"SMALL BLIND {self.small_blind} AT PLAYER {self.small_blind_player}")
        # print(f"ACTUAL PLAYER INDEX {self.player_index}")
        # print(f"LAST PLAYER {self.last}")
        # print(f"STAKE {self.list_of_active_players[self.player_index].chips}")
        # print("-----------------PLAYER_INFO-------------------------\n")

        potential_moves = self.list_of_active_players[self.player_index].potential_moves()

        if potential_moves[response] == "raise":
            self.raise_bet(self.player_index, 5)
            
        if potential_moves[response] == "fold":
            self.fold(self.player_index)
            self.player_index =self.player_index%len(self.list_of_active_players)
                
        if potential_moves[response] == "call" or potential_moves[response] == "all_in":
            self.call(self.player_index)

        if potential_moves[response] == "check":
            if self.flop == True:
                self.end_of_turn()

            elif self.player_index == self.last:
                self.end_of_turn()

        if self.last == self.list_of_active_players[self.player_index].player_id and self.flop == False:
            result = self.end_of_turn()

            if result == 3:
                print("GAME OVER!")
        
            self.player_index = (self.round_no + 1)%len(self.list_of_active_players) 
            self.player_index =self.player_index - 1
            return

        self.player_index = (self.player_index+1)%len(self.list_of_active_players)
        print("Calculating move")

    def get_data(self):
        board = []
        for i in self.cards.cards:
            board.append(i.get_path())

        tables = {}
        for i in self.list_of_active_players:
            tables[i.player_id] = i.table_no

        return {
            'no_round': self.round_no,
            'player_index': self.player_index,
            'pot': self.pot, 
            'highest_stake': self.highest_stake,
            'board_cards': board,
            'players_at_table': tables,
            'actual_player_move': self.list_of_active_players[self.player_index].table_no
        }
    
    def parse_players(self, data):
        for i in data:
            self.list_of_players.append(Player(i['username'], i['playerId'], len(self.list_of_players)))
            # self.tables[i['playerId']] = len(self.tables)

    def raise_bet(self, id:int, bet) -> None:
        self.list_of_active_players[id].stake += bet
        self.list_of_active_players[id].chips -= bet
        self.list_of_active_players[id].stake_gap = 0
        self.highest_stake = self.list_of_active_players[id].stake
        self.pot += bet 
        self.last = self.list_of_active_players[(id-1+len(self.list_of_active_players))%len(self.list_of_active_players)].player_id
            

    def fold(self, id:int):
        self.list_of_active_players[id].fold = True

        if self.last == self.list_of_active_players[id].player_id:
            self.end_of_turn()
            self.last = self.list_of_active_players[(id-1+len(self.list_of_active_players))%len(self.list_of_active_players)].player_id

        self.list_of_active_players.remove(self.list_of_active_players[id])

    
    def call(self, id:int) -> None:
        if self.list_of_active_players[id].chips <= self.list_of_active_players[id].stake_gap:
            self.list_of_active_players[id].stake += self.list_of_active_players[id].chips
            self.pot +=  self.list_of_active_players[id].chips
            self.list_of_active_players[id].all_in = True
            return

        self.list_of_active_players[id].stake += self.list_of_active_players[id].stake_gap
        self.pot += self.list_of_active_players[id].stake_gap
        self.list_of_active_players[id].chips -= self.list_of_active_players[id].stake_gap
        self.list_of_active_players[id].stake_gap = 0


    def find_winner(self):
        winner_id = 0
        winner_score = math.inf

        if len(self.list_of_active_players) == 1:
            self.winner =self.list_of_active_players[0].player_id
            self.list_of_active_players[0].chips += self.pot
            return

        for i in range(len(self.list_of_active_players)):
            if PokerHand(self.list_of_active_players[i].hand, self.cards).evaluateHand() < winner_score:
                winner_score = PokerHand(self.list_of_active_players[i].hand, self.cards).evaluateHand()
                winner_id = i

        print(f"PLAYER {self.list_of_active_players[winner_id].player_id} WINS\n")
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

        map(lambda x:x.reset_stake(), self.list_of_players)

        self.highest_stake = self.big_blind       

        self.big_blind_player = (self.round_no+1)%len(self.list_of_active_players)
        self.small_blind_player = self.big_blind_player - 1

        if self.small_blind_player < 0:
            self.small_blind_player += len(self.list_of_active_players)

        self.list_of_active_players[self.big_blind_player].chips -= self.big_blind
        self.list_of_active_players[self.big_blind_player].stake = self.big_blind

        self.list_of_active_players[self.small_blind_player].chips -= self.small_blind
        self.list_of_active_players[self.small_blind_player].stake = self.small_blind

        for i in range(len(self.list_of_active_players)):
            if i != self.small_blind_player and i != self.big_blind_player:
                self.list_of_active_players[i].stake_gap = 1

        self.player_index = (self.big_blind_player + 1)%len(self.list_of_active_players)


    def end_of_turn(self): 
        map(lambda x:x.reset_stake(), self.list_of_players)

        if self.flop == True:
            self.last = self.small_blind_player - 1
            if self.last < 0:
                self.last += len(self.list_of_active_players)

            self.player_index =  self.small_blind_player

            self.deck.give_cards(self.cards, 3)
            self.flop = False
            return
    
        # self.last = self.list_of_active_players[(self.round_no-1+len(self.list_of_active_players))%len(self.list_of_active_players)].player_id
        self.last = self.small_blind_player - 1
        if self.last < 0:
                self.last += len(self.list_of_active_players)
        
        self.player_index =  self.small_blind_player

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
        self.player_index = (self.round_no + 2)%len(self.list_of_active_players)

        for i in range(len(self.list_of_active_players)):
            self.deck.give_cards(self.list_of_active_players[i].hand, 2)

       

        # print(f"Starting game: round {self.round_no}\n")
        # self.clear_table()

        # for i in range(len(self.list_of_active_players)):
        #     self.deck.give_cards(self.list_of_active_players[i].hand, 2)

        # self.self.player_index = (self.round_no + 2)%len(self.list_of_active_players) 

        # while(True):
        #     if len(self.list_of_active_players) == 1:
        #         self.find_winner()

        #         ask = input("continue?[y/n]: ")
        #         if ask != "y":
        #             exit(0)

        #         self.clear_table()
        #         self.self.player_index = (self.round_no + 2)%len(self.list_of_active_players) 
        #         continue

        #     print(f"\nPlayer {self.list_of_active_players[self.self.player_index].name}\n")
        #     self.list_of_active_players[self.self.player_index].stake_gap = self.highest_stake - self.list_of_active_players[self.self.player_index].stake

        #     print(f"Players cards:\n{self.list_of_active_players[self.self.player_index].hand}")
        #     print(f"POT: {self.pot}")
        #     # print(f"Highest stake: {self.highest_stake}")
        #     print(f"Put in at least {self.list_of_active_players[self.self.player_index].stake_gap} chips.\n")
        #     print(f"Chips available: {self.list_of_active_players[self.self.player_index].chips}")

        #     potential_moves = self.list_of_active_players[self.self.player_index].potential_moves()
        #     response = 0

        #     for j in range(len(potential_moves)):
        #         print(f"{j+1}. {potential_moves[j+1]}")
            
        #     while(True):
        #         if self.list_of_active_players[self.player_index].all_in == True:
        #             break

        #         response = int(input(":"))
        #         if response >= 1 and response < len(potential_moves) + 1:
        #             break 
        #         else:
        #             print("enter valid move: ")

        #     if potential_moves[response] == "raise":
        #         self.raise_bet(self.player_index)
            
        #     if potential_moves[response] == "fold":
        #         self.fold(self.player_index)
        #         self.player_index =self.player_index%len(self.list_of_active_players)
        #         continue
                
        #     if potential_moves[response] == "call":
        #         self.call(self.player_index)

        #     if potential_moves[response] == "all_in":
        #         self.call(self.player_index)

        #     if potential_moves[response] == "check":   

        #         result = self.end_of_turn() if (self.flop and self.flop_rise == False) == True else 0

        #         if result == 2:
        #             self.player_index = (self.player_index-1+len(self.list_of_active_players))%len(self.list_of_active_players)
        #             self.last = self.list_of_active_players[(self.player_index-1+len(self.list_of_active_players))%len(self.list_of_active_players)].player_id             
        #             continue

        #     if self.last == self.list_of_active_players[self.player_index].player_id and self.flop == False:
        #         result = self.end_of_turn()

        #         if result == 3:
        #             ask = input("continue?[y/n]: ")
        #             if ask == "y":
        #                 self.clear_table()
        #                 self.self.player_index = (self.round_no + 2)%len(self.list_of_active_players) 
        #                 continue
        #             else:
        #                 exit(0)


        #         self.player_index = (self.round_no + 1)%len(self.list_of_active_players) 
        #         self.player_index =self.self.player_index - 1
        #         continue

        #     self.player_index = (self.player_index+1)%len(self.list_of_active_players)

            
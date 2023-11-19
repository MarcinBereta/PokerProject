from player import Player
from cardUtility import Hand


class Table:
    def __init__(self) -> None:
        self.players = {}
        self.small_blind = None
        self.big_blind = None
        self.community_cards = Hand()

        self.player_turn = None
        self.last_player = None

        self.ordered_players = []

    def sitdown(self, player: Player):
        self.players[player.uuid] = player
        self.ordered_players.append(player)

    def player_stop_playing(self, uuid):
        self.players[uuid].is_active = False

        for player in self.ordered_players:
            if player.uuid == uuid:
                player.is_active = False

    def player_left(self, uuid):
        self.players[uuid].is_playing = False

        for player in self.ordered_players:
            if player.uuid == uuid:
                player.is_playing = False

    def size(self):
        return len(self.ordered_players)

    def count_active(self):
        return len([p for p in self.players.values() if p.is_active and p.is_playing])

    def set_blind(self, small_blind, big_blind):
        self.small_blind, self.big_blind = small_blind % self.size(), big_blind % self.size()

    def set_player_turn(self, player_index):
        self.player_turn = (player_index + self.size()) % self.size()

        while not self.ordered_players[self.player_turn % self.size()].is_playing or \
                not self.ordered_players[self.player_turn % self.size()].is_active:
            self.player_turn = (self.player_turn + 1) % self.size()

        return self.ordered_players[self.player_turn % self.size()].uuid
    
    def set_last_player(self, player_index = None):
        if player_index is not None:
            self.last_player = (player_index + self.size()) % self.size()

        while self.ordered_players[self.last_player].is_playing == False or self.ordered_players[self.last_player].is_active == False:
            self.last_player = (self.last_player - 1 + self.size())% self.size()
        
        return self.ordered_players[self.last_player].uuid

    def get_big_blind(self):
        if self.big_blind is None:
            raise ValueError("Big blind is not set yet")

        # if self.big_blind >= self.count_active():
        #     raise IndexError("List out of range")

        return self.ordered_players[self.big_blind]

    def get_small_blind(self):
        if self.small_blind is None:
            raise ValueError("Small blind is not set yet")

        # if self.small_blind >= self.count_active():
        #     raise IndexError("List out of range")

        return self.ordered_players[self.small_blind]

    def add_cards(self, cards):
        for card in cards:
            self.community_cards.add_card(card)

    def get_community_cards(self):
        return self.community_cards

    def pop_cards(self):
        return self.community_cards.pop_all()

    def get_next_player(self):
        if self.count_active() <= 1:
            raise ValueError("Not enought players!")

        self.player_turn += 1

        while not self.ordered_players[self.player_turn % self.size()].is_playing or \
                not self.ordered_players[self.player_turn % self.size()].is_active:
            self.player_turn += 1

        return self.ordered_players[self.player_turn % self.size()].uuid

    def get_prev_player(self):
        if self.count_active() <= 1:
            raise ValueError("Not enough players!")

        prev_index = (self.player_turn - 1 + self.size()) % self.size()

        while not self.ordered_players[prev_index].is_playing or \
                not self.ordered_players[
                    prev_index].is_active:
            prev_index = (prev_index - 1 + self.size()) % self.size()

        return self.ordered_players[prev_index].uuid

    def get_player(self, uuid):
        return self.players[uuid]

    def reset_state(self):
        for player in self.ordered_players:
            player.is_playing = True

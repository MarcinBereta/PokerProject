# from SocketServer import *
from PokerGame import PokerGame
import random

games = {}
games_lobbies = {}
history = {}


def pass_data(data):
    print(f"games.data_request()")

    user_id = data['user_id']
    game_id = data['game_id']
    game_data = {}

    try:
        game_data = games[game_id].get_data()
        game_data['cards'] = games[game_id].tables.players[user_id].get_cards()

    except KeyError:
        print(f"[ERROR] no such key")

    return game_data


def player_left_game(data):
    games[data['gameId']].player_left_table(data['playerId'])


def create_new_game():
    hash = random.getrandbits(128)
    games[hash] = PokerGame()

    return hash


def update_data(data):
    # print('game_move_played()', data)

    if games[data['gameId']].player_index != data['playerId']:
        return

    games[data['gameId']].calculate_move(data['playerId'], data['move_id'], data['raise_bet'])
    game_data = games[data['gameId']].get_data()

    print(f"[UPDATE DATA] {game_data}\n")

    if games[data['gameId']].winner is not None:
        players_cards = {}

        for uuid, player in games[data['gameId']].tables.players.items():
            if uuid in game_data['players_at_table']:
                players_cards[uuid] = player.get_cards()

        game_data['all_cards'] = players_cards
        end_game(data['gameId'])

        return True, game_data

    return False, game_data


def end_game(game_id):
    history[game_id] = games[game_id]
    # games[game_id] = None


def start_game(game_id, data):
    # print(f"games.start_game()")
    games[game_id].config(data)
    games[game_id].start()


def play_next_round(data):
    games[data['game_id']].start()


# @sio.on('change_tour')
def join_lobby():
    print("Changing tour")

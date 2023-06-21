# from SocketServer import *
from PokerGame import PokerGame
import random

games = {}
games_lobbies = {}
history = {}

def pass_data(data):
    print(f"games.data_request(){data}")
    
    user_id = data['user_id']
    game_id = data['game_id']
    game_data = {}

    if game_id is None:
        game_id = games_lobbies[data['room_id']]

    try:
        game_data = games[game_id].get_data()
        game_data['cards'] = games[game_id].tables.players[user_id].get_cards()
    except KeyError:
        print(f"[ERROR] no such key")

    game_data['game_id'] = game_id
        
    
        
    return game_id, game_data
    
    # print(games)
    # for game_id, game in games.items():
    #     if game is not None:
    #         game_data = game.get_game_status()
    #         # print(game_data, data['user_id'] in game_data['seats'])
            
    #         if data['user_id'] in game_data['seats']:
    #             # print(game.tables.players, game.tables.players[data['user_id']])
    #             game_data['cards'] = game.tables.players[data['user_id']].get_cards()
    #             game_data['game_id'] = game_id
            
    #             return game_data
            
    return None 

def player_left_game(data):
    games[data['game_id']].player_left_table(data['playerId'])
    game_data = games[data['game_id']].get_data()
    
    print(f"[UPDATE DATA] {game_data}\n")

    if games[data['game_id']].winner is not None:
        players_cards = {}
        
        for uuid, player in games[data['game_id']].tables.players.items():
            if uuid in game_data['players_at_table']:
                players_cards[uuid] = player.get_cards()
        
        game_data['all_cards'] = players_cards
        game_data['owner']     =  games[data['game_id']].owner
        end_game(data['game_id'])
        
        return True, game_data

    return False, game_data


def create_new_game(data):
    hash = random.getrandbits(128)
    games[hash] = PokerGame()

    return hash

def update_data(data):
    # print('game_move_played()', data)

    if games[data['gameId']].player_index != data['playerId']:
        pass
    
    games[data['gameId']].calculate_move(data['playerId'], data['move_id'], data['raise_bet'])
    game_data = games[data['gameId']].get_data()
    

    print(f"[UPDATE DATA] {game_data}\n")

    if games[data['gameId']].winner is not None:
        players_cards = {}
        
        for uuid, player in games[data['gameId']].tables.players.items():
            if uuid in game_data['players_at_table']:
                players_cards[uuid] = player.get_cards()
        
        game_data['all_cards'] = players_cards
        game_data['owner']     =  games[data['gameId']].owner
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
    
    
def play_next_round(data, config):
    games[data['game_id']].config(config)
    games[data['game_id']].start()


# @sio.on('change_tour')
def join_lobby(sid):
    print("Changing tour")

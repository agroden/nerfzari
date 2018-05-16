from typing import List, Any

games = []

def add_game(object: 'Game') -> int:
	games.append(object)
	return len(games)-1

def get_game(game_id: int) -> 'Game':
	return games[game_id]
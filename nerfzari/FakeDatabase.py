from typing import List, Any

games = []
users = []

def start_unittest_mode():
	"""
	This function resets the database for testing
	"""
	games = []
	users = []

def add_game(object: 'Game') -> int:
	"""
	:param object: Game object representing the game to add to the db
	:return: Returns unique id for the user on success; otherwise -1 is returned
	"""
	games.append(object)
	object.id = len(games)-1
	return object.id

def get_game(game_id: int) -> 'Game':
	return games[game_id]

def update_game(object: 'Game') -> bool:
	"""
	:param object: Game object representing the game to update
	:return: Returns True if the object was successfully updated; otherwise False is returned
	"""
	games[object.id] = object;

def complete_game(object: 'Game') -> bool:

	update_game(object)
	# Loop through each participant and update kills/deaths.

def add_user(object: 'User') -> int:
	"""
	:param object: User object representing the new user
	:return: Returns unique id for the user on success; otherwise -1 is returned
	"""
	users.append(object)
	return len(users)-1

def get_user(user_id: int) -> 'User':
	return users[user_id]



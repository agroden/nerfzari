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
	:param object: User object representing the new user
	:return: Returns unique id for the user on success; otherwise -1 is returned
	"""
	games.append(object)
	return len(games)-1

def get_game(game_id: int) -> 'Game':
	return games[game_id]

def add_user(object: 'User') -> int:
	"""
	:param object: User object representing the new user
	:return: Returns unique id for the user on success; otherwise -1 is returned
	"""
	users.append(object)
	return len(users)-1

def get_user(user_id: int) -> 'User':
	return users[user_id]

def register_kill(user_id: int) -> bool:
	user = get_user(user_id)
	if user is None:
		print("ERROR FakeDatabase.register_kill: user with id " + str(user_id) + " does not exist")
	user.kills += 1
	return True

def register_death(user_id: int) -> bool:
	user = get_user(user_id)
	if user is None:
		print("ERROR FakeDatabase.register_kill: user with id " + str(user_id) + " does not exist")
	user.deaths += 1
	return True

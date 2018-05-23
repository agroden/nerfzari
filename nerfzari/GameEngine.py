from datetime import datetime
from enum import Enum
import FakeDatabase as database
from User import User


#################
### Game Type ###
#################

class GameType(Enum):
	def __str__(self):
		return self.name

	NERF_ASSASSIN = 1
	TEAM_ASSASSIN = 2
	NERF_ZOMBIE = 3

#################
### Game Type ###
#################

class Game:
	"""Base Class for all games. """

	type: GameType
	name: str
	start_date: datetime
	id: int

	def __init__(self,game_type: GameType):
		self.type = game_type
		self.name = "Unnamed"
		self.start_date = 0
		self.is_started = False
		self.id = 0
	# -------------------------------------------------------------------------

	def __str__(self):
		return self.name + " - " + str(self.type) + " start date: " + str(self.start_date)

	# -------------------------------------------------------------------------

###################
### Game Engine ###
###################

def new_user(first_name: str, last_name:str):
	"""
	:param first_name: The first name of the new user
	:param last_name: The last name of the new user
	:return: The unique user id of the new user; if an error occurred -1 is returned
	"""
	user = User(first_name,last_name)
	user_id = database.add_user(user)
	return user_id
# -----------------------------------------------------------------------------

def new_game(game_type: GameType, name: str, start_date: datetime) -> Game:
	"""
	:param game_type: Enum value defining the type of game to create
	:param name: Name of the Game
	:param start_date: Date and Time for the game to begin
	:param game_type: Identifier for the type of game to be created
	:returns: Game Id if game has been created successfully; otherwise 0 is returned.
	"""

	if game_type == GameType.NERF_ASSASSIN:
		from NerfAssassin import NerfAssassin
		game = NerfAssassin(name,start_date)
	elif game_type == GameType.TEAM_ASSASSIN:
		raise NotImplementedError()
	elif game_type == GameType.NERF_ZOMBIE:
		raise NotImplementedError()
	else:
		print("ERROR: Unknown GameType " + str(game_type))
		return None

	game.id = database.add_game(game)  # TODO: This needs to be replaced with a real database call

	return game
# -------------------------------------------------------------------------

def get_game(game_id: int):
	"""
	:param game_id: Unique id of the game to retrieve the object of
	:returns: The game object matching the id; otherwise None is returned
	"""

	return database.get_game(game_id)  # TODO: This needs to be replaced with a real database call
# -------------------------------------------------------------------------

def leaderboard():
	"""
	:returns: True if leaderboard is successfully printed; otherwise False is returned.
	"""

	# Fetch all users
	# Sort by K/D ratio where kills are greater than some magic number or calculated number
	# print them

	raise NotImplementedError()

# -------------------------------------------------------------------------

def register_kill(game_id: int, assassin_handle: str, assassinated_handle: str):
	"""
	:param assassin_handle: Handle of the assassin that performed the kill
	:param assassinated_handle: Handle of the participant that was assassinated
	:param game_id: Unique id of the game the assassination was performed under
	:return: True if the kill was successfully registered; otherwise False is returned.
	"""
	game = database.get_game(game_id)      # TODO: This needs to be replaced with a real database call
	return game.register_kill(assassin_handle,assassinated_handle)
# -------------------------------------------------------------------------

def add_participant(game_id: int, user_id: int, handle: str):
	"""
	:param game_id: Unique id of the game to add the user to
	:param user_id: Unique id of the user to add to the specified game
	:param handle: Unique printable name or identifier for the user during the game
	:returns: True if user has been successfully added to the game; otherwise False is returned.
	"""

	game = database.get_game(game_id)      # TODO: This needs to be replaced with a real database call
	return game.add_participant(user_id,handle)
# -------------------------------------------------------------------------

def remove_participant(game_id: int, user: str):
	"""
	:param user: Name of the user to remove
	:param game_id: Unique id of the game to remove the user from
	:returns: True if user has been successfully removed from the game; otherwise False is returned.
	"""

	game = database.get_game(game_id)      # TODO: This needs to be replaced with a real database call
	return game.remove_participant(user)
# -------------------------------------------------------------------------

def status(game_id: int, user: str):
	"""
	:param user: Name of the user to print the status of
	:param game_id: Unique id of the game the user is a participant in
	:returns: True if status has been successfully retrieved and printed; otherwise False is returned.
	"""

	raise NotImplementedError()
# --------------------------------------------------------------------------

def history():
	"""
	:returns: True if history has been successfully printed; otherwise False is returned.
	"""

	raise NotImplementedError()
# -------------------------------------------------------------------------
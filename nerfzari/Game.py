from typing import List, Any
from datetime import datetime
from enum import Enum

from User import User

import FakeDatabase as database

class GameType(Enum):
	def __str__(self):
		return self.name

	NERF_ASSASSIN = 1
	TEAM_ASSASSIN = 2
	NERF_ZOMBIE = 3

class Game():
	"""Base Class for all games. """

	type: GameType
	name: str
	start_date: datetime
	id: int

	def __init__(self,game_type: GameType):
		self.type = game_type
		self.name = "Unnamed"
		self.start_date = 0
		self.id = 0
	# -------------------------------------------------------------------------

	def __str__(self):
		return self.name + " - " + str(self.type) + " start date: " + str(self.start_date)

	# -------------------------------------------------------------------------

	def create_game(self, name: str, start_date: datetime) -> int:
		"""
		:param name: Name of the Game
		:param start_date: Date and Time for the game to begin
		:param game_type: Identifier for the type of game to be created
		:returns: Game Id if game has been created successfully; otherwise 0 is returned.
		"""

		if self.type == GameType.NERF_ASSASSIN:
			from NerfAssassin import NerfAssassin
			new_game = NerfAssassin(name,start_date)
			return database.add_game(new_game)     # TODO: This needs to be replaced with a real database call
		elif self.type == GameType.TEAM_ASSASSIN:
			from TeamAssassin import TeamAssassin
			new_game = TeamAssassin(name,start_date)
			return database.add_game(new_game)     # TODO: This needs to be replaced with a real database call
		elif self.type == GameType.NERF_ZOMBIE:
			from NerfZombie import NerfZombie
			new_game = NerfZombie(name,start_date)
			return database.add_game(new_game)     # TODO: This needs to be replaced with a real database call
		else:
			print("ERROR: Unknown GameType " + str(self.type))

		return 0
	# -------------------------------------------------------------------------

	def leaderboard(self, game_id: int):
		"""
		:param game_id: Unique id of the game to print the leaderboard of
		:returns: True if leaderboard is successfully printed; otherwise False is returned.
		"""

		game = database.get_game(game_id)      # TODO: This needs to be replaced with a real database call
		game.leaderboard()

	# -------------------------------------------------------------------------

	def status(self, user: str, game_id: int):
		"""
		:param user: Name of the user to print the status of
		:param game_id: Unique id of the game the user is a participant in
		:returns: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""

		raise NotImplementedError()

	# --------------------------------------------------------------------------

	def register_kill(self, assassin_handle: str, assassinated_handle: str, game_id: int):
		"""
		:param assassin_handle: Handle of the assassin that performed the kill
		:param assassinated_handle: Handle of the participant that was assassinated
		:param game_id: Unique id of the game the assassination was performed under
		:return: True if the kill was successfully registered; otherwise False is returned.
		"""
		game = database.get_game(game_id)      # TODO: This needs to be replaced with a real database call
		return game.register_kill(assassin_handle,assassinated_handle)

	def add_participant(self, user: User, game_id: int):
		"""
		:param user: Name of the user to add
		:param game_id: Unique id of the game to add the user to
		:returns: True if user has been successfully added to the game; otherwise False is returned.
		"""

		game = database.get_game(game_id)      # TODO: This needs to be replaced with a real database call
		game.add_participant(user)
		return True

	# -------------------------------------------------------------------------

	def remove_participant(self, user: str, game_id: int):
		"""
		:param user: Name of the user to remove
		:param game_id: Unique id of the game to remove the user from
		:returns: True if user has been successfully removed from the game; otherwise False is returned.
		"""

		raise NotImplementedError()
	# -------------------------------------------------------------------------

	def history(self):
		"""
		:returns: True if history has been successfully printed; otherwise False is returned.
		"""

		raise NotImplementedError()
	# -------------------------------------------------------------------------



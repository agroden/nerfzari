from datetime import datetime
from typing import List,Any
import User
from Game import Game,GameType

class NerfAssassin(Game):

	GAME_TYPE = GameType.NERF_ASSASSIN
	TYPE_NAME = "Nerf Assassin"
	participants: List['User']

	def __init__(self, name, start_date):
		super().__init__(self.GAME_TYPE)
		self.name = name
		self.start_date = start_date
		self.id = 0
		self.participants = []
	# -------------------------------------------------------------------------

	def __str__(self):
		return self.TYPE_NAME + " - " + self.name + " - " + str(self.start_date)

	# -------------------------------------------------------------------------

	def leaderboard(self):
		"""
		:returns: True if leaderboard is successfully printed; otherwise False is returned.
		"""
		print("--- " + str(self) + " ---")
		for index,participant in enumerate(self.participants):
			print(str(index+1) + " - " + str(participant))
		return True
	# -------------------------------------------------------------------------

	def status(self, user: User):
		"""
		:param user: User object to print the status of (is_alive, current target, # kills... etc)
		:return: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""

		raise NotImplementedError()

	# -------------------------------------------------------------------------

	def add_participant(self, user: User):
		"""
		:param user: Name of the user to add
		:param game_id: Unique id of the game to add the user to
		:return: True if user has been successfully added to the game; otherwise False is returned.
		"""
		self.participants.append(user)

		return True

	# -------------------------------------------------------------------------

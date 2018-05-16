from datetime import datetime
from typing import List,Any
import User
from Game import Game,GameType

class NerfZombie(Game):

	GAME_TYPE = GameType.NERF_ZOMBIE
	TYPE_NAME = "Nerf Zombie"
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
		print("1 - fred - 3 Kills")
		print("2 - bob     - 1 Kill")
		print("3 - infected guy  - 0 Kills")
		return True
	# -------------------------------------------------------------------------

	def status(self, user: User):
		"""
		:param user: User object to print the status of (is_alive, current target, # kills... etc)
		:return: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""

		raise NotImplementedError()

	# -------------------------------------------------------------------------

from datetime import datetime
from typing import List,Any
import User
from Game import Game,GameType

class NerfZombie(Game):

	GAME_TYPE = GameType.NERF_ZOMBIE
	TYPE_NAME = "Nerf Zombie"
	participants: List['User']

	def __init__(self, name: str, start_date: datetime):
		super().__init__(self.GAME_TYPE)
		self.name = name
		self.start_date = start_date
		self.id = 0
		self.participants = []
	# -------------------------------------------------------------------------

	def __str__(self):
		return str(self.id) + " - " + self.TYPE_NAME + " - " + self.name + " - " + str(self.start_date)

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

	def status(self, handle: str):
		"""
		:param handle: handle of the participant to print the status of (is_alive, current target, # kills... etc)
		:return: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""

		raise NotImplementedError()

	# -------------------------------------------------------------------------

	def distribute_targets(self):
		"""
		:return: True if all participants were assigned a target; otherwise False is returned.
		"""

		raise NotImplementedError()
	# -------------------------------------------------------------------------

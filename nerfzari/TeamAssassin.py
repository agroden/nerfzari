from datetime import datetime
from typing import List
from Game import Game,GameType

class TeamAssassin(Game):

	GAME_TYPE = GameType.TEAM_ASSASSIN
	TYPE_NAME = "Team Nerf Assassin"
	teams: List['Team']

	def __init__(self, name: str, start_date: datetime):
		super().__init__(self.GAME_TYPE)
		self.name = name
		self.start_date = start_date
		self.id = 0
		self.teams = []
	# -------------------------------------------------------------------------

	def __str__(self):
		return str(self.id) + " - " + self.TYPE_NAME + " - " + self.name + " - " + str(self.start_date)

	# -------------------------------------------------------------------------

	def leaderboard(self):
		"""
		:returns: True if leaderboard is successfully printed; otherwise False is returned.
		"""
		print("--- " + str(self) + " ---")
		print("1 - Team 1 - 3 Kills")
		print("2 - Team 2 - 1 Kill")
		print("3 - Team 3 - 0 Kills")
		print("4 - Team 4 - (-1) Kills")
		return True
	# -------------------------------------------------------------------------

	def status(self, team_id: int):
		"""
		:param team_id: name of the the team to print the status of (kills, deaths, stock, members & member stats, etc)
		:returns: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""

		raise NotImplementedError()

	# -------------------------------------------------------------------------

	def distribute_targets(self):
		"""
		:return: True if all participants were assigned a target; otherwise False is returned.
		"""

		raise NotImplementedError()
	# -------------------------------------------------------------------------
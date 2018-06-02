from typing import List

class User:

	first_name: str
	last_name: str
	kills: int
	deaths: int
	games_participated_in: List[int]
	games_won: List[int]

	def __init__(self, first_name, last_name):
		self.first_name = first_name
		self.last_name = last_name
		self.kills = 0
		self.deaths = 0
	# -------------------------------------------------------------------------

	def __str__(self):

		string = self.first_name
		string += " "
		string += self.last_name
		return string
	# -------------------------------------------------------------------------

	def status(self):
		"""
		:returns: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""

		status = self.first_name
		status += " "
		status += self.last_name
		status += " - "
		status += str(self.kills)
		status += " Kills - "
		status += str(self.deaths)
		status += " Deaths - "
		status += str(self.kill_death_ratio)
		status += " K/D"
		return status
	# -------------------------------------------------------------------------

	@property
	def kill_death_ratio(self):
		"""
		:return: number of kills divided by the num.
		"""
		return self.kills / self.deaths
	# -----------------------------------------------------------------------

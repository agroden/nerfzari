from typing import List

class User():

	first_name: str
	last_name: str
	handle: str
	kills: List['User']
	deaths: int
	is_alive: bool
	assassinator: str

	def __init__(self, first_name, last_name, handle):
		self.first_name = first_name
		self.last_name = last_name
		self.handle = handle
		self.kills = []
		self.deaths = 0
		self.is_alive = True
		self.assassinator = ""

	def __str__(self):

		string = self.handle + " - " + str(len(self.kills)) + " Kills - "

		if(self.is_alive):
			string += "Alive"
		else:
			string += "Assassinated by " + self.assassinator
		return string

	# -------------------------------------------------------------------------

	def status(self, user: 'User'):
		"""
		:param user: User object of the user to print the status of (name, handle, kills, deaths, etc)
		:returns: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""

		raise NotImplementedError()

	# -------------------------------------------------------------------------

	@property
	def kill_death_ratio(self):
		"""
		:return: number of kills divided by the num.
		"""
		return len(self.kills) / self.deaths

	# -----------------------------------------------------------------------

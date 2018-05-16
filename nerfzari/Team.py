from typing import List, Any

class Team():

	MAX_TEAM_SIZE = 5

	name: str
	kills: List['TeamMember']
	is_alive: bool
	members: List['TeamMember']

	def __init__(self, name):
		self.name = name
		self.kills = []
		self.is_alive = True
		self.members = []

	def add_team_member(self, team_member: 'TeamMember'):
		"""
		:returns: True if user has been successfully added to the team; otherwise False is returned.
		"""

		raise NotImplementedError()

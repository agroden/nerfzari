import User
from Team import Team

class TeamMember(User):

	team: Team

	def __init__(self, first_name, last_name, handle, team):
		super().__init__(first_name,last_name,handle)
		self.team = team


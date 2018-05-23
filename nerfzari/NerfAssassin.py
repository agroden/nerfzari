from datetime import datetime
from typing import List
from GameEngine import Game,GameType
import FakeDatabase as database


###################
### Participant ###
###################

class Participant:
	user_id: int
	handle: str
	target_handle: str
	hunter_handle: str
	is_alive: bool
	assassinator: str

	def __init__(self, user_id: int, handle: str):
		self.user_id = user_id
		self.handle = handle
		self.target_handle = ""
		self.hunter_handle = ""
		self.is_alive = True
		self.assassinator = ""

	def __str__(self):
		string = str(self.user_id)
		string += " - "
		string += self.handle
		string += " - "
		if self.is_alive:
			string += "Alive"
			string += " - Target: "
			string += self.target_handle
		else:
			string += "Dead. Killed by "
			string += self.assassinator
		return string

#####################
### Nerf Assassin ###
#####################

class NerfAssassin(Game):

	GAME_TYPE = GameType.NERF_ASSASSIN
	TYPE_NAME = "Nerf Assassin"
	participants: List[Participant]

	def __init__(self, name: str, start_date: datetime):
		super().__init__(self.GAME_TYPE)
		self.name = name
		self.start_date = start_date
		self.id = 0
		self.participants = []
	# -------------------------------------------------------------------------

	def __str__(self):
		return str(self.id) + " - " + self.name + " - " + self.TYPE_NAME
	# -------------------------------------------------------------------------

	def status(self, handle: str):
		"""
		:param handle: handle of the participant to print the status of (is_alive, current target, # kills... etc)
		:return: True if status has been successfully retrieved and printed; otherwise False is returned.
		"""
		participant = self.get_participant(handle)
		if participant is None:
			print("ERROR: Assassin " + handle + " is not a participant in " + self.name)
			return False
		print(str(participant))

		return True
	# -------------------------------------------------------------------------

	def register_kill(self, assassin_handle: str, assassinated_handle: str):
		"""
		:param assassin_handle: Handle of the assassin that performed the kill
		:param assassinated_handle: Handle of the participant that was assassinated
		:return: True if the kill was successfully registered; otherwise False is returned.
		"""

		if assassin_handle == assassinated_handle:
			print("Suicide is not a valid escape path...")
			return False

		assassin = self.get_participant(assassin_handle)
		if assassin is None:
			print("ERROR: Assassin " + assassin_handle + " is not a participant in " + self.name)
			return False
		assassinated = self.get_participant(assassinated_handle)
		if assassinated is None:
			print("ERROR: Assassin " + assassinated_handle + " is not a participant in " + self.name)
			return False

		if not assassin.is_alive:
			print("ERROR: assassin " + assassin.handle + " is not alive and thus cannot assassinate " + assassinated.handle)
			return False

		if not assassinated.is_alive:
			print("ERROR: participant " + assassinated.handle + " is not alive and thus cannot be assassinated by " + assassin.handle)
			return False

		database.register_kill(assassin.user_id)
		assassinated.is_alive = False
		database.register_death(assassinated.user_id)
		assassinated.assassinator = assassin_handle

		if assassin.handle != assassinated.hunter_handle:
			hunter_of_assassinated = self.get_participant(assassinated.hunter_handle)
			if hunter_of_assassinated is None:
				print("ERROR: " + assassinated_handle + "'s hunter " + assassinated.hunter_handle + " is not a participant in " + self.name)
				return False
			target_of_assassinated = self.get_participant(assassinated.target_handle)
			if target_of_assassinated is None:
				print("ERROR: " + assassinated_handle + "'s target " + assassinated.target_handle + " is not a participant in " + self.name)
				return False
			hunter_of_assassinated.target_handle = assassinated.target_handle
			target_of_assassinated.hunter_handle = hunter_of_assassinated.handle

		else:
			new_target = self.get_participant(assassinated.target_handle)
			if new_target is None:
				print("ERROR: " +assassinated.target_handle+ " is not a participant in " + self.name)
			assassin.target_handle = new_target.handle
			new_target.hunter_handle = assassin.handle

		return True
	# -------------------------------------------------------------------------

	def add_participant(self, user_id: int, handle: str) -> bool:
		"""
		:param user_id: Unique id of the user to add
		:param handle: Unique printable name or identifier for the user during the game
		:return: True if user has been successfully added to the game; otherwise False is returned.
		"""

		participant_exists = False
		for participant in self.participants[:]:
			if participant.handle == handle:
				participant_exists = True
				break

		if participant_exists:
			print("ERROR: " + handle + " is already a participant in " + self.name)
			return False

		self.participants.append(Participant(user_id,handle))

		return True
	# -------------------------------------------------------------------------

	def get_participant(self, handle) -> Participant:
		"""
		:param handle: The handle of the participant to retrieve
		:return: object of the participant matching the given handle; otherwise None is returned
		"""

		for participant in self.participants[:]:
			if participant.handle == handle:
				return participant

		print("ERROR get_participant: participant with handle " + handle + " not found.")
		return None
	# -------------------------------------------------------------------------

	def distribute_targets(self):
		"""
		This function should only be called once to start the game, all other target reassignments are performed on a
		per kill basis
		:return: True if all participants were assigned a target; otherwise False is returned.
		"""
		import random

		random.shuffle(self.participants)

		num_participants = len(self.participants)
		for i,participant in enumerate(self.participants):

			if i != (num_participants-1):
				participant.target_handle = self.participants[i+1].handle
			else:
				participant.target_handle = self.participants[0].handle

			if i != 0:
				participant.hunter_handle = self.participants[i-1].handle
			else:
				participant.hunter_handle = self.participants[-1].handle
	# -------------------------------------------------------------------------
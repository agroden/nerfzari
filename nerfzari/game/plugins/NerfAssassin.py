from datetime import datetime
from typing import List
from GameEngine import Game,GameType
from GameEngine import UserCommunicationException
from DatabaseInterface import DatabaseInterface

database = DatabaseInterface()


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
	# --------------------------------------------------------------------------

	def __str__(self):
		return str(self.id) + " - " + self.name + " - " + self.TYPE_NAME
	# --------------------------------------------------------------------------

	@property
	def num_participants(self):
		return len(self.participants)
	# --------------------------------------------------------------------------

	@property
	def num_living_participants(self) -> int:
		num_alive = 0
		for participant in self.participants[:]:
			if participant.is_alive:
				num_alive += 1
		return num_alive
	# --------------------------------------------------------------------------

	@property
	def is_game_complete(self):
		"""

		:return: True if the game has completed (has a winner); otherwise False is returned. If an error occurs a UserCommunicationException is raised.
		"""
		return self.num_living_participants == 1
	# -----------------------------------------------------------------------------

	def start_game(self):
		"""
		This function starts the game. A game can only be started once and only on or after the start_date
		:return: void. If an error occurs (such as game has already been started) a UserCommunicationException is raised.
		"""

		if self.is_started:
			raise UserCommunicationException("Game " + self.name + " has started.")

		if self.start_date > datetime.now():
			raise UserCommunicationException("Game " + self.name + " cannot be started before " + str(self.start_date) + ".")

		self.distribute_targets()
		self.is_started = True
	# -----------------------------------------------------------------------------

	def status(self, handle: str):
		"""
		:param handle: handle of the participant to print the status of (is_alive, current target, # kills... etc)
		:return: True if status has been successfully retrieved and printed; otherwise UserCommunicationException is raised
		"""
		participant = self.get_participant(handle)
		if participant is None:
			raise UserCommunicationException("ERROR: Assassin " + handle + " is not a participant in " + self.name)
		print(str(participant))
	# --------------------------------------------------------------------------

	def register_kill(self, assassin_handle: str, assassinated_handle: str):
		"""
		:param assassin_handle: Handle of the assassin that performed the kill
		:param assassinated_handle: Handle of the participant that was assassinated
		:return: True if the kill was successfully registered; otherwise False is returned.
		"""

		if not self.is_started:
			raise UserCommunicationException("Cannot register a kill before the game has started.")

		if assassin_handle == assassinated_handle:
			raise UserCommunicationException("Suicide is not a valid escape path...")

		assassin = self.get_participant(assassin_handle)
		assassinated = self.get_participant(assassinated_handle)

		if not assassin.is_alive:
			raise UserCommunicationException("Assassin " + assassin.handle + " is not alive and thus cannot assassinate " + assassinated.handle+".")

		if not assassinated.is_alive:
			raise UserCommunicationException("Participant " + assassinated.handle + " is not alive and thus cannot be assassinated by " + assassin.handle+".")

		database.register_kill(assassin.user_id)
		assassinated.is_alive = False
		database.register_death(assassinated.user_id)
		assassinated.assassinator = assassin_handle

		if assassin.handle != assassinated.hunter_handle:
			hunter_of_assassinated = self.get_participant(assassinated.hunter_handle)
			target_of_assassinated = self.get_participant(assassinated.target_handle)

			hunter_of_assassinated.target_handle = assassinated.target_handle
			target_of_assassinated.hunter_handle = hunter_of_assassinated.handle

		else:
			new_target = self.get_participant(assassinated.target_handle)
			assassin.target_handle = new_target.handle
			new_target.hunter_handle = assassin.handle
	# --------------------------------------------------------------------------

	def add_participant(self, user_id: int, handle: str):
		"""
		:param user_id: Unique id of the user to add
		:param handle: Unique printable name or identifier for the user during the game
		"""

		if self.is_started:
			raise UserCommunicationException("Cannot add participants to an active game.")

		participant_exists = False
		for participant in self.participants[:]:
			if participant.handle == handle:
				participant_exists = True
				break

		if participant_exists:
			raise UserCommunicationException(handle + " is already a participant in " + self.name)

		self.participants.append(Participant(user_id,handle))

	# --------------------------------------------------------------------------

	def remove_participant(self, handle: str):
		"""
		:param handle: Handle of the participant to remove from the game
		:returns: void if user has been successfully removed from the game; otherwise UserCommunicationException is raised.
		"""

		participant = self.get_participant(handle)

		if self.is_started:
			if participant.is_alive:
				hunter_of_participant = self.get_participant(participant.hunter_handle)
				target_of_participant = self.get_participant(participant.target_handle)
				hunter_of_participant.target_handle = participant.target_handle
				target_of_participant.hunter_handle = hunter_of_participant.handle

		self.participants.remove(participant)
	# -------------------------------------------------------------------------

	def get_participant(self, handle: str) -> Participant:
		"""
		:param handle: The handle of the participant to retrieve
		:return: object of the participant matching the given handle; otherwise UserCommunicationException is raised
		"""

		for participant in self.participants[:]:
			if participant.handle == handle:
				return participant

		raise UserCommunicationException(handle + " is not a participant in " + self.name)
	# --------------------------------------------------------------------------

	def distribute_targets(self):
		"""
		This function must only be called before start of the game, all other target reassignments are performed on a
		per kill basis
		:return: True if all participants were assigned a target; otherwise UserCommunicationException is raised
		"""
		if self.is_started:
			raise UserCommunicationException("Cannot distribute targets once the game has already started.")

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
	# --------------------------------------------------------------------------

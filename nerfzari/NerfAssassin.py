from datetime import datetime
from typing import List
import User
from Game import Game,GameType

class NerfAssassin(Game):

	GAME_TYPE = GameType.NERF_ASSASSIN
	TYPE_NAME = "Nerf Assassin"
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
		for index,participant in enumerate(self.participants):
			print(str(index+1) + " - " + str(participant))
		return True
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

		msg = "Name: "
		msg += participant.first_name
		msg += " "
		msg += participant.last_name
		msg += " Handle: "
		msg += participant.handle
		msg += " Kills "
		msg += str(len(participant.kills))
		msg += " Target: "
		msg += participant.target

		print(msg)
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

		assassin.kills.append(assassinated_handle)
		assassinated.is_alive = False
		assassinated.deaths += 1
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

	def add_participant(self, user: User):
		"""
		:param user: Object of the user to add
		:return: True if user has been successfully added to the game; otherwise False is returned.
		"""

		if self.get_participant(user.handle) is not None:
			print("ERROR: " + user.handle + " is already a participant in " + self.name)
			return False
		self.participants.append(user)

		return True
	# -------------------------------------------------------------------------

	def get_participant(self, handle) -> User:
		"""
		:param handle: The handle of the participant to retrieve
		:return: User object of the participant; otherwise None is returned
		"""

		for user in self.participants[:]:
			if user.handle == handle:
				return user

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

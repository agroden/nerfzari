import unittest
from datetime import datetime
from Game import Game,GameType
from User import User
import Game


def print_participants(game: Game):

	print("##### " + game.name + " Participants" + " #####")
	for participant in game.participants[:]:
		if participant.is_alive:
			print(participant.handle + " Target: " + participant.target_handle)
		else:
			print(participant.handle + " DEAD")
#------------------------------------------------------------------------------

def kill_target(game: Game, handle: str):
	killer = game.get_participant(handle)
	game.register_kill(handle,killer.target_handle)
#------------------------------------------------------------------------------

if __name__ == '__main__':

	# Create a nerf assassin game
	nerf_assassin = Game.new_game(GameType.NERF_ASSASSIN,"Assassin's Feed",datetime.now())

	nerf_assassin.add_participant(User("Desmond","Miles","an00bis"))
	nerf_assassin.add_participant(User("Altair", "IbnLaAhad", "NoName"))
	nerf_assassin.add_participant(User("Dr", "Vidic", "LookOut"))
	nerf_assassin.add_participant(User("Assassin4","Assassin4","Assassin4"))
	nerf_assassin.add_participant(User("Assassin5", "Assassin5", "Assassin5"))
	nerf_assassin.distribute_targets()
	print_participants(nerf_assassin)
	#nerf_assassin.leaderboard()


	kill_target(nerf_assassin,"an00bis")

	print_participants(nerf_assassin)

	nerf_assassin.register_kill("an00bis", "Assassin4")

	print_participants(nerf_assassin)

	#Game.leaderboard(nerf_assassin.id)

	# Create a team assassin game
	team_assassin = Game.new_game(GameType.TEAM_ASSASSIN,"Brotherhood Civil War",datetime.now())
	team_assassin.leaderboard()

	# Create a nerf zombie gamel
	nerf_zombie = Game.new_game(GameType.NERF_ZOMBIE,"Flight of the Living Dead",datetime.now())
	nerf_zombie.leaderboard()

	#Create 2nd nerf assassin game
	nerf_assassins2 = Game.new_game(GameType.NERF_ASSASSIN, "Assassin's Feed 2: The job", datetime.now())
	nerf_assassins2.leaderboard()
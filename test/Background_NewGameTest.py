from datetime import datetime
from Game import Game,GameType
from User import User
import Game

if __name__ == '__main__':

	# Create a nerf assassin game
	nerf_assassin = Game.new_game(GameType.NERF_ASSASSIN,"Assassin's Feed",datetime.now())

	nerf_assassin.add_participant(User("Desmond","Miles","an00bis"))
	nerf_assassin.add_participant(User("Altair", "IbnLaAhad", "NoName"))
	nerf_assassin.add_participant(User("Dr", "Vidic", "LookOut"))

	nerf_assassin.leaderboard()

	nerf_assassin.register_kill("an00bis", "NoName")

	Game.leaderboard(nerf_assassin.id)

	# Create a team assassin game
	team_assassin = Game.new_game(GameType.TEAM_ASSASSIN,"Brotherhood Civil War",datetime.now())
	team_assassin.leaderboard()

	# Create a nerf zombie game
	nerf_zombie = Game.new_game(GameType.NERF_ZOMBIE,"Flight of the Living Dead",datetime.now())
	nerf_zombie.leaderboard()

	#Create 2nd nerf assassin game
	nerf_assassins2 = Game.new_game(GameType.NERF_ASSASSIN, "Assassin's Feed 2: The job", datetime.now())
	nerf_assassins2.leaderboard()
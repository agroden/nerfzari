from datetime import datetime
from Game import Game,GameType
from User import User

if __name__ == '__main__':

	# Create a nerf assassin game
	nerf_assassin = Game(GameType.NERF_ASSASSIN)
	nerf_assassin_id = nerf_assassin.create_game("Assassin's Feed",datetime.now())

	nerf_assassin.add_participant(User("Desmond","Miles","an00bis"),nerf_assassin_id)
	nerf_assassin.add_participant(User("Altair", "IbnLaAhad", "NoName"), nerf_assassin_id)
	nerf_assassin.add_participant(User("Dr", "Vidic", "LookOut"), nerf_assassin_id)

	nerf_assassin.leaderboard(nerf_assassin_id)

	# Create a team assassin game
	team_assassin = Game(GameType.TEAM_ASSASSIN)
	team_assassin_id = team_assassin.create_game("Brotherhood Civil War",datetime.now())
	team_assassin.leaderboard(team_assassin_id)

	# Create a nerf zombie game
	nerf_zombie = Game(GameType.NERF_ZOMBIE)
	nerf_zombie_id = nerf_zombie.create_game("Flight of the Living Dead",datetime.now())
	nerf_zombie.leaderboard(nerf_zombie_id)
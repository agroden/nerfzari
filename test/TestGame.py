import unittest
from datetime import datetime
from Game import Game,GameType
import Game

#############################
### TEST CASE: Game Setup ###
#############################

class TestGameSetup(unittest.TestCase):

	def test_game_creation(self):

		game_type = GameType.NERF_ASSASSIN
		game_name = "Test Game 1"
		game_start = datetime.now()

		game = Game.new_game(game_type, game_name , game_start)
		self.assertEqual(game_type,game.type)
	# --------------------------------------------------------------------------

	def test_multigame_support(self):
		game_type = GameType.NERF_ASSASSIN
		game_name = "Test Game 1"
		game_start = datetime.now()

		game1 = Game.new_game(game_type, game_name , game_start)
		game2 = Game.new_game(game_type, game_name , game_start)
		self.assertNotEqual(game1.id,game2.id)
	# --------------------------------------------------------------------------

	def test_game_types(self):

		from NerfAssassin import NerfAssassin
		from NerfZombie import NerfZombie
		from TeamAssassin import TeamAssassin

		nerf_assassin = Game.new_game(GameType.NERF_ASSASSIN, "Nerf Assasin Test Game 0" , datetime.now())
		self.assertIsNotNone(nerf_assassin)
		self.assertIsInstance(nerf_assassin, NerfAssassin)

		team_assassin = Game.new_game(GameType.TEAM_ASSASSIN, "Team Assassin Test Game 0" , datetime.now())
		self.assertIsNotNone(team_assassin)
		self.assertIsInstance(team_assassin, TeamAssassin)

		nerf_zombie = Game.new_game(GameType.NERF_ZOMBIE, "Nerf Zombie Test Game 0" , datetime.now())
		self.assertIsNotNone(nerf_zombie)
		self.assertIsInstance(nerf_zombie, NerfZombie)


############
### MAIN ###
############

if __name__ == '__main__':
	unittest.main(verbosity=2)
import unittest
import random
from datetime import datetime
from User import User
from NerfAssassin import NerfAssassin
import Game


#############################
### TEST CASE: Game Setup ###
#############################

class Test01GameSetup(unittest.TestCase):

	game: Game

	def setUp(self):
		self.game = NerfAssassin("Test Game", datetime.now())
		self.assertIsNotNone(self.game)
	# --------------------------------------------------------------------------

	def tearDown(self):
		self.game = None
	# --------------------------------------------------------------------------

	def test01_adding_participants(self):

		self.assertEqual(0, len(self.game.participants))
		self.assertTrue(self.game.add_participant(User("Ass", "Assin1", "Assassin1")))
		self.assertEqual(1, len(self.game.participants))
		self.assertTrue(self.game.add_participant(User("Ass", "Assin2", "Assassin2")))
		self.assertEqual(2, len(self.game.participants))
		self.assertTrue(self.game.add_participant(User("Ass", "Assin3", "Assassin3")))
		self.assertEqual(3, len(self.game.participants))
	# --------------------------------------------------------------------------

	def test02_adding_duplicate_participant(self):

		user = User("Ass", "Assin2", "Assassin2")
		self.assertTrue(self.game.add_participant(user))
		self.assertFalse(self.game.add_participant(user))
		self.assertEqual(1, len(self.game.participants))
	# --------------------------------------------------------------------------

######################################
### TEST CASE: Target Distribution ###
######################################

class Test02TargetDistribution(unittest.TestCase):

	MIN_NUM_PARTICIPANTS = 3
	MAX_NUM_PARTICIPANTS = 100
	game: Game

	def setUp(self):
		self.game = NerfAssassin("Test Game", datetime.now())
		self.assertIsNotNone(self.game)

		for i in range(random.randint(self.MIN_NUM_PARTICIPANTS,self.MAX_NUM_PARTICIPANTS)):
			self.assertTrue(self.game.add_participant(User("Ass", "Assin" + str(i), "Assassin" + str(i))))

		self.game.distribute_targets()
	# --------------------------------------------------------------------------

	def tearDown(self):
		self.game = None
	# --------------------------------------------------------------------------

	def test01_no_empty_assignments(self):

		for participant in self.game.participants[:]:
			self.assertIsNotNone(participant.target_handle)
			self.assertNotEqual(participant.target_handle, "")
	# --------------------------------------------------------------------------

	def test02_no_self_assignments(self):

		for participant in self.game.participants[:]:
			self.assertNotEqual(participant.handle,participant.target_handle)
	# --------------------------------------------------------------------------

	def test03_no_duplicates(self):

		for participant in self.game.participants[:]:
			num_hunters = 0
			for hunter in self.game.participants[:]:
				if hunter.target_handle == participant.handle:
					num_hunters += 1
			self.assertEqual(num_hunters,1)
	# --------------------------------------------------------------------------

	def test04_no_non_participating(self):

		for participant in self.game.participants[:]:
			target = self.game.get_participant(participant.target_handle)
			self.assertIsNotNone(target)
	# --------------------------------------------------------------------------

	def test05_no_closed_loops(self):

		for participant in self.game.participants[:]:
			target = self.game.get_participant(participant.target_handle)
			self.assertIsNotNone(target)
			self.assertNotEqual(participant.target_handle,participant.hunter_handle)
	# --------------------------------------------------------------------------


############################
### TEST CASE: Game Play ###
############################

class Test03GamePlay(unittest.TestCase):

	MIN_NUM_PARTICIPANTS = 3
	MAX_NUM_PARTICIPANTS = 10
	game: Game

	def setUp(self):
		self.game = NerfAssassin("Test Game", datetime.now())
		self.assertIsNotNone(self.game)

		for i in range(random.randint(self.MIN_NUM_PARTICIPANTS,self.MAX_NUM_PARTICIPANTS)):
			self.assertTrue(self.game.add_participant(User("Ass", "Assin" + str(i), "Assassin" + str(i))))

		self.game.distribute_targets()
	# --------------------------------------------------------------------------

	def tearDown(self):
		self.game = None
	# --------------------------------------------------------------------------

	def test01_target_kill(self):

		participant = random.choice(self.game.participants)
		target = self.game.get_participant(participant.target_handle)
		prev_num_kills = len(participant.kills)
		prev_targets_target = target.target_handle

		self.game.register_kill(participant.handle, target.handle)
		self.assertFalse(target.is_alive)
		self.assertEqual(target.assassinator, participant.handle)
		self.assertEqual(len(participant.kills),prev_num_kills+1)
		self.assertEqual(participant.target_handle,prev_targets_target)
	# --------------------------------------------------------------------------

	def test02_kill_own_hunter(self):

		participant = random.choice(self.game.participants)
		self.assertIsNotNone(participant)
		hunter = self.game.get_participant(participant.hunter_handle)
		self.assertIsNotNone(hunter)

		prev_num_kills = len(participant.kills)
		prev_target = participant.target_handle

		self.game.register_kill(participant.handle, participant.hunter_handle)
		self.assertFalse(hunter.is_alive)
		self.assertEqual(hunter.assassinator, participant.handle)
		self.assertEqual(len(participant.kills), prev_num_kills + 1)
		self.assertEqual(participant.target_handle, prev_target) # Ensure target of participant didn't change

		#Ensure hunter's hunter is assigned to the killer
		hunters_hunter = self.game.get_participant(hunter.hunter_handle)
		self.assertIsNotNone(hunters_hunter)
		self.assertEqual(hunters_hunter.target_handle, participant.handle)
	# --------------------------------------------------------------------------

	def test03_non_target_kill(self):

		participant = random.choice(self.game.participants)
		killed = random.choice(self.game.participants)
		attempts = 0
		while participant.target_handle == killed.handle or killed.target_handle == participant.handle or participant.handle == killed.handle:
			participant = random.choice(self.game.participants)
			attempts += 1
			if attempts >= 100:
				break
		self.assertLess(attempts,100,"Failed to locate two unrelated targets")

		prev_num_kills = len(participant.kills)
		prev_target = participant.target_handle

		self.game.register_kill(participant.handle,killed.handle)
		self.assertFalse(killed.is_alive)
		self.assertEqual(killed.assassinator, participant.handle)
		self.assertEqual(len(participant.kills), prev_num_kills + 1)
		self.assertEqual(participant.target_handle, prev_target) # Ensure target of participant didn't change

		#Ensure killed assassin's hunter is assigned to the killer
		killeds_hunter = self.game.get_participant(killed.hunter_handle)
		self.assertIsNotNone(killeds_hunter)
		self.assertEqual(killeds_hunter.target_handle, killed.target_handle)
	# --------------------------------------------------------------------------


	def test04_full_game_simulation(self):

		num_participants = len(self.game.participants)
		kill_order = random.sample(range(num_participants),num_participants-1)

		for killer_index in kill_order[:]:
			killer = self.game.participants[killer_index]
			self.game.register_kill(killer.handle,killer.target_handle)

		num_alive = 0
		for participant in self.game.participants[:]:
			if participant.is_alive:
				num_alive += 1
		self.assertEqual(num_alive,1)
	# --------------------------------------------------------------------------

	def test05_full_game_simulation_chaos(self):

		def get_living_pariticipant():
			living_participant = random.choice(self.game.participants)
			while not living_participant.is_alive:
				living_participant = random.choice(self.game.participants)
			return living_participant

		def kill_target(killer):
			print("DEBUG kill_target: " + killer.handle + " killed " + killer.target_handle)
			self.game.register_kill(killer.handle, killer.target_handle)

		def kill_own_hunter(killer):
			print("DEBUG kill_own_hunter: " + killer.handle + " killed " + killer.hunter_handle)
			self.game.register_kill(killer.handle, killer.hunter_handle)

		def kill_non_target(killer):
			killed = random.choice(self.game.participants)
			attempts = 0
			while killer.target_handle == killed.handle or killed.target_handle == killer.handle or killer.handle == killed.handle:
				killed = get_living_pariticipant()
				attempts += 1
				if attempts >= 100:
					break
			#self.assertLess(attempts, 100, "Failed to locate two unrelated targets")
			print("DEBUG kill_non_targetl: " + killer.handle + " killed " + killed.handle)
			self.game.register_kill(killer.handle,killed.handle)

		print_participants(self.game)

		num_participants = len(self.game.participants)
		for i in range(num_participants-1):
			participant = get_living_pariticipant()
			action = random.randint(1,3)
			print("--------------")
			if(action == 1):
				kill_target(participant)
				print_participants(self.game)
			elif(action == 2):
				kill_own_hunter(participant)
				print_participants(self.game)
			elif(action == 3):
				kill_non_target(participant)
				print_participants(self.game)
			else:
				self.assertLessEqual(action,3,"Unknown action number " + str(action))

		num_alive = 0
		for participant in self.game.participants[:]:
			if participant.is_alive:
				num_alive += 1



		self.assertEqual(num_alive,1)

	# --------------------------------------------------------------------------


############
### MAIN ###
############


def print_participants(game: Game):

	print("##### " + game.name + " Participants" + " #####")
	for participant in game.participants[:]:
		if participant.is_alive:
			print(participant.handle + " Target: " + participant.target_handle)
		else:
			print(participant.handle + " DEAD")
# --------------------------------------------------------------------------


if __name__ == '__main__':
	#unittest.main(verbosity=2)

	suite = unittest.TestSuite()
	suite.addTest(Test03GamePlay("test05_full_game_simulation_chaos"))
	runner = unittest.TextTestRunner()
	runner.run(suite)


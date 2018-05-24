import unittest
import random
from datetime import datetime
from NerfAssassin import NerfAssassin,Participant
from GameEngine import UserCommunicationException
import GameEngine
import FakeDatabase as database

#############################
### TEST CASE: Game Setup ###
#############################

class Test01GameSetup(unittest.TestCase):

	game: NerfAssassin

	def setUp(self):
		self.game = NerfAssassin("Test Game", datetime.now())
		self.assertIsNotNone(self.game)
		database.start_unittest_mode()
	# --------------------------------------------------------------------------

	def tearDown(self):
		self.game = None
	# --------------------------------------------------------------------------

	def test01_adding_participants(self):
		assassin1_id = GameEngine.new_user("Ass", "Assin1")
		self.assertGreaterEqual(assassin1_id,0)
		assassin2_id = GameEngine.new_user("Ass", "Assin2")
		self.assertGreaterEqual(assassin2_id,0)
		assassin3_id = GameEngine.new_user("Ass", "Assin3")
		self.assertGreaterEqual(assassin3_id,0)


		self.assertEqual(self.game.num_participants, 0)
		self.game.add_participant(assassin1_id, "Assassin1")
		self.assertEqual(self.game.num_participants, 1)
		self.game.add_participant(assassin2_id, "Assassin2")
		self.assertEqual(self.game.num_participants, 2)
		self.game.add_participant(assassin3_id, "Assassin3")
		self.assertEqual(self.game.num_participants, 3)
	# --------------------------------------------------------------------------

	def test02_adding_duplicate_participant(self):

		assassin2_id = GameEngine.new_user("Ass", "Assin2")
		self.assertGreaterEqual(assassin2_id, 0)

		self.game.add_participant(assassin2_id, "Assassin2")
		self.assertRaises(UserCommunicationException,self.game.add_participant,assassin2_id, "Assassin2")
		self.assertEqual(self.game.num_participants, 1)
	# --------------------------------------------------------------------------

######################################
### TEST CASE: Target Distribution ###
######################################

class Test02TargetDistribution(unittest.TestCase):

	MIN_NUM_PARTICIPANTS = 100
	MAX_NUM_PARTICIPANTS = 1000
	game: NerfAssassin

	def setUp(self):

		database.start_unittest_mode()

		self.game = NerfAssassin("Test Game", datetime.now())
		self.assertIsNotNone(self.game)

		for i in range(random.randint(self.MIN_NUM_PARTICIPANTS,self.MAX_NUM_PARTICIPANTS)):
			user_id = GameEngine.new_user("Ass", "Assin" + str(i))
			self.assertGreaterEqual(user_id,0)
			self.game.add_participant(user_id, "Assassin" + str(i))

		self.game.start_game()
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

	MIN_NUM_PARTICIPANTS = 100
	MAX_NUM_PARTICIPANTS = 1000
	game: NerfAssassin

	def setUp(self):
		database.start_unittest_mode()

		self.game = NerfAssassin("Test Game", datetime.now())
		self.assertIsNotNone(self.game)

		for i in range(random.randint(self.MIN_NUM_PARTICIPANTS,self.MAX_NUM_PARTICIPANTS)):
			user_id = GameEngine.new_user("Ass", "Assin" + str(i))
			self.assertGreaterEqual(user_id,0)
			self.game.add_participant(user_id, "Assassin" + str(i))

		self.game.start_game()
	# --------------------------------------------------------------------------

	def tearDown(self):
		self.game = None
	# --------------------------------------------------------------------------

	@property
	def num_living_participants(self) -> int:
		num_alive = 0
		for participant in self.game.participants[:]:
			if participant.is_alive:
				num_alive += 1
		return num_alive
	# --------------------------------------------------------------------------

	def get_living_pariticipant(self) -> Participant:
		living_participants = [x for x in self.game.participants if x.is_alive]
		num_living_participants = len(living_participants)
		if num_living_participants < 1:
			print("ERROR: No living participants!")
			return None
		return random.choice(living_participants)

	# --------------------------------------------------------------------------

	def get_num_kills(self,user_id) -> int:
		user = database.get_user(user_id)
		self.assertIsNotNone(user)
		return user.kills
	# --------------------------------------------------------------------------

	def get_num_deaths(self,user_id) -> int:
		user = database.get_user(user_id)
		self.assertIsNotNone(user)
		return user.deaths
	# --------------------------------------------------------------------------

	def test01_target_kill(self):

		participant = random.choice(self.game.participants)
		self.assertIsNotNone(participant)
		target = self.game.get_participant(participant.target_handle)
		self.assertIsNotNone(target)

		prev_num_kills = self.get_num_kills(participant.user_id)
		prev_targets_target = target.target_handle
		prev_num_deaths = self.get_num_deaths(target.user_id)

		self.game.register_kill(participant.handle, target.handle)
		self.assertFalse(target.is_alive)
		self.assertEqual(target.assassinator, participant.handle)
		self.assertEqual(self.get_num_deaths(target.user_id),prev_num_deaths+1)
		self.assertEqual(self.get_num_kills(participant.user_id),prev_num_kills+1)

		# Ensure participant's target was changed to the target of the killed
		self.assertEqual(participant.target_handle, prev_targets_target)

		# Ensure new target's hunter was updated to be the participant
		new_target = self.game.get_participant(participant.target_handle)
		self.assertIsNotNone(new_target)
		self.assertEqual(new_target.hunter_handle, participant.handle)
	# --------------------------------------------------------------------------

	def test02_kill_own_hunter(self):

		participant = random.choice(self.game.participants)
		self.assertIsNotNone(participant)
		hunter = self.game.get_participant(participant.hunter_handle)
		self.assertIsNotNone(hunter)

		prev_num_kills = self.get_num_kills(participant.user_id)
		prev_target = participant.target_handle
		prev_num_deaths = self.get_num_deaths(hunter.user_id)

		self.game.register_kill(participant.handle, participant.hunter_handle)
		self.assertFalse(hunter.is_alive)
		self.assertEqual(hunter.assassinator, participant.handle)
		self.assertEqual(self.get_num_deaths(hunter.user_id), prev_num_deaths + 1)
		self.assertEqual(self.get_num_kills(participant.user_id), prev_num_kills + 1)
		self.assertEqual(participant.target_handle, prev_target) # Ensure target of participant didn't change

		#Ensure hunter's hunter is assigned to the killer
		hunters_hunter = self.game.get_participant(hunter.hunter_handle)
		self.assertIsNotNone(hunters_hunter)
		self.assertEqual(hunters_hunter.target_handle, participant.handle)

		#Ensure participant was updated with its new hunter
		self.assertEqual(participant.hunter_handle, hunters_hunter.handle)
	# --------------------------------------------------------------------------

	def test03_non_target_kill(self):

		max_num_attempts = self.game.num_participants * 10
		attempts = 0
		while True:
			killer = self.get_living_pariticipant()
			killed = self.get_living_pariticipant()
			attempts += 1
			if (killer.target_handle != killed.handle
	      and killed.target_handle != killer.handle
			and killer.handle != killed.handle) \
			or attempts >= max_num_attempts:
				break
		self.assertLess(attempts,max_num_attempts,"Failed to locate two unrelated targets")

		prev_num_kills = self.get_num_kills(killer.user_id)
		prev_target = killer.target_handle
		prev_num_deaths = self.get_num_deaths(killed.user_id)

		self.game.register_kill(killer.handle,killed.handle)
		self.assertFalse(killed.is_alive)
		self.assertEqual(killed.assassinator, killer.handle)
		self.assertEqual(self.get_num_deaths(killed.user_id), prev_num_deaths + 1)
		self.assertEqual(self.get_num_kills(killer.user_id), prev_num_kills + 1)
		self.assertEqual(killer.target_handle, prev_target) # Ensure target of killer didn't change

		#Ensure killed assassin's hunter is assigned to the killer
		killeds_hunter = self.game.get_participant(killed.hunter_handle)
		self.assertIsNotNone(killeds_hunter)
		self.assertEqual(killeds_hunter.target_handle, killed.target_handle)

		#Ensure killed assassin's target is updated with its new hunter
		killeds_target = self.game.get_participant(killed.target_handle)
		self.assertIsNotNone(killeds_target)
		self.assertEqual(killeds_target.hunter_handle, killeds_hunter.handle)
	# --------------------------------------------------------------------------

	def test04_kill_already_dead(self):

		max_num_attempts = self.game.num_participants * 10
		attempts = 0
		while True:
			killer = self.get_living_pariticipant()
			target = random.choice(self.game.participants)
			attempts += 1
			if not target.is_alive or attempts >= max_num_attempts:
				break
			elif killer.handle != target.handle:
				self.game.register_kill(killer.handle, target.handle)
		self.assertLess(attempts, max_num_attempts, "Failed to locate a living killer and a dead target")
		self.assertTrue(killer.is_alive)
		self.assertFalse(target.is_alive)
		self.assertRaises(UserCommunicationException,self.game.register_kill,killer.handle,target.handle)
	# --------------------------------------------------------------------------

	def test05_dead_killer(self):

		max_num_attempts = self.game.num_participants * 10
		attempts = 0
		while True:
			killer = random.choice(self.game.participants)
			target = self.get_living_pariticipant()
			attempts += 1
			if not killer.is_alive or attempts >= max_num_attempts:
				break
			elif killer.handle != target.handle:
				self.game.register_kill(killer.handle, target.handle)
		self.assertLess(attempts, max_num_attempts, "Failed to locate a living target and a dead killer")
		self.assertFalse(killer.is_alive)
		self.assertTrue(target.is_alive)
		self.assertRaises(UserCommunicationException, self.game.register_kill, killer.handle, target.handle)
	# --------------------------------------------------------------------------

	def test06_full_game_simulation(self):

		max_num_kill_attempts = self.game.num_participants * 10
		kill_attempts = 0
		while self.num_living_participants > 1:
			killer = self.get_living_pariticipant()
			kill_attempts += 1
			if killer.is_alive:
				self.game.register_kill(killer.handle, killer.target_handle)

			if kill_attempts >= max_num_kill_attempts:
				break

		self.assertEqual(self.num_living_participants, 1)
	# --------------------------------------------------------------------------

	def test07_full_game_simulation_chaos(self):

		def kill_target(killer):
			self.game.register_kill(killer.handle, killer.target_handle)

		def kill_own_hunter(killer):
			self.game.register_kill(killer.handle, killer.hunter_handle)

		def kill_non_target(killer):
			max_num_attempts = self.game.num_participants*10
			attempts = 0
			while True:
				killed = self.get_living_pariticipant()
				attempts += 1
				if killer.handle != killed.handle \
				and ((killer.target_handle != killed.handle and killed.target_handle != killer.handle)
				     or attempts >= max_num_attempts):
					break
			self.assertTrue(killer.is_alive)
			self.assertTrue(killed.is_alive)
			self.game.register_kill(killer.handle,killed.handle)

		num_participants = self.game.num_participants
		for i in range(num_participants-1):
			participant = self.get_living_pariticipant()
			action = random.randint(1,3)
			if action == 1:
				kill_target(participant)
			elif action == 2:
				kill_own_hunter(participant)
			elif action == 3:
				kill_non_target(participant)
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


def print_participants(game: NerfAssassin):
	print("##### " + game.name + " Participants" + " #####")
	for participant in game.participants[:]:
		if participant.is_alive:
			print(participant.handle + " Target: " + participant.target_handle + " Hunter: " + participant.hunter_handle)
		else:
			print(participant.handle + " DEAD")
# --------------------------------------------------------------------------

def run_specific_test(test):
	suite = unittest.TestSuite()
	suite.addTest(test)
	runner = unittest.TextTestRunner()
	runner.run(suite)
# -------------------------------------------------------------------------

if __name__ == '__main__':

	unittest.main(verbosity=2)

	#run_specific_test(Test01GameSetup("test02_adding_duplicate_participant"))


	#for i in range(0,100):
	#	run_specific_test(Test03GamePlay("test05_full_game_simulation_chaos"))
	#	run_specific_test(Test03GamePlay("test04_kill_already_dead"))



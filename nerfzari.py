"""
"""

import socket
import logging
import sys
import paramiko
import tableprint
import io
import os
import inspect
import time
import random
import peewee
from datetime import datetime
from nerfzari import ConfigStore, Authenticator, SSHServer, SSHCmd, Game, User, username


logging.basicConfig(filename='nerfzari.log', level=logging.DEBUG)
log = logging.getLogger(__name__)


NERFZARI_CFG_PATH = 'nerfzari.json'
NERFZARI_CFG_SCHEMA = {
	'$schema': 'http://json-schema.org/draft-06/schema#',
	'description': 'Data needed by the Nerfzari server',
	'type': 'object',
	'default': {},
	'required': ['rsa_key'],
	'properties': {
		'listen_port': {
			'type': 'integer',
			'default': 4040
		},
		'rsa_key': { 'type': 'string' },
		'auth_cls': {
			'type': 'string',
			'default': 'AcceptAll'
		},
		'module_dir': {
			'type': 'string',
			'default':	'modules'
		}
	}
}
ConfigStore.register(
	NERFZARI_CFG_PATH,
	NERFZARI_CFG_SCHEMA
)


QUOTE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'quotes.txt'))
_quotes = None
def random_quote():
	global _quotes
	if _quotes is None:
		_quotes = []
		with open(QUOTE_FILE, 'r') as f:
			while True:
				line = f.readline()
				if not line:
					break
				line = line.strip()
				if len(line) > 0:
					_quotes.append(line)
	return random.choice(_quotes)


class NerfzariCmd(SSHCmd):
	# actions:
	# personal status (games, IDs, overall K/D ratio, ranking)
	# game status - game ID or current (who has been killed, K/D ratio)
	# leaderboard
	# game history
	# kill - ID of participant
	# suicide - remove yourself from game
	prompt = '>'
	'''
	def __init__(self, chan, username, completekey='tab'):
		super().__init__(chan, username, completekey)
		methods = inspect.getmembers(self, predicate=inspect.ismethod)
		self._game_subcommands = [x[0].split('_')[0] for x in methods if x[0].endswith('game')]
	'''

	def preloop(self):
		# check if this is the first time the user has logged in
		self._user = User.get_by_username(self._username)
		if self._user is None:
			self.poutput('processing login, retrieving user data', end='')
			for _ in range(3):
				time.sleep(0.5)
				self.poutput('.', end='')
			time.sleep(0.75)
			self.poutput('')
			self.poutput('error: user not found - please enter your information to access the server')
			name = self.terminput('full name>', False)
			email = self.terminput('email>', False)
			self._user = User.new_user(self._username, name, email)
			self.poutput('user registration complete; welcome to game, {}'.format(name))
		# get a random quote
		#self.poutput(random_quote())
		# display game info
		curr_games = Game.active_games()
		if len(curr_games) > 1:
			self.poutput('current game is {}'.format(curr_games[0].name)) # TODO: show all current games
		else:
			next_game = Game.next_game()
			if next_game is not None:
				self.poutput('next scheduled game is {} on {}'.format(next_game.name, next_game.start_date))

	def new_game(self):
		# TODO: finish type completer from discovered game types
		def type_completer(text):
			pass
		gtype = self.terminput('game type>', False)
		name = self.terminput('game name>', False)
		date_str = self.terminput('start date (month/day/year)>', False)
		month, day, year = date_str.split('/')
		date = datetime(int(year), int(month), int(day), 12, 0, 0, 0)
		try:
			Game.new_game(date, gtype, name, self._user)
		except peewee.IntegrityError:
			self.poutput('a game with that name or date already exists.')

	def list_game(self):
		games = Game.list_games()
		self.draw_gamelist(games)

	def delete_game(self):
		games = Game.list_games()
		print('games: {}'.format(games))
		if len(games) > 0:
			self.draw_gamelist(games)
			name = self.terminput('game name>', False)
			game = Game.get(name=name, creator=self._user)
			if game.start_date < datetime.now:
				self.poutput('cannot delete games that are in progress')
				return
			players = [x for x in game.players]
			if len(players) > 0:
				self.poutput('players have joined this game, please confirm you wish to delete this game')
				confirm = self.terminput('confirm>', False)
			else:
				confirm = 'yes'
			if confirm.lower() in ['y', 'yes']:
				game.safe_delete()
		else:
			self.poutput('you may only delete games you have created')

	def join_game(self):
		self.draw_gamelist(Game.list_games())
		name = self.terminput('game name>', False)
		if not self._user.has_joined(name):
			game = Game.get(name=name)
			if game.start_date < datetime.now:
				self.poutput('cannot join a game currently in session')
		player = game.join(self._user)
		self.poutput('your game tag is {}'.format(player.tag))
		self.poutput('your game tag represents you - remember it')
		self.poutput('when you are eliminated, you give your tag to the player that eliminated you')
		self.poutput('if a player discovers your tag, they can use it to eliminate you, so keep it secret!')

	def leave_game(self):
		# TODO: only allow leave if game hasn't started yet
		self.draw_gamelist(Game.list_games())
		name = self.terminput('game name>', False)
		game = Game.get(name=name)
		if not game.started():
			Game.leave_game(self._user, Game.get(name=name))
		else:
			self.poutput('cannot leave a game that has started')

	def show_tag(self):
		game = Game.next_game()
		if game:
			self.poutput('your current tag is: {}'.format(game.tag(self._user)))

	def reset_tag(self):
		self.show_tag()
		game = Game.next_game()
		new_tag = game.tag
		resp = self.terminput('keep?>')
		while resp.lower() not in ['y', 'yes']:
			new_tag = username.generate_username(8, 8)
			self.poutput('new tag: {}'.format(new_tag))
			resp = self.terminput('keep?>')
		game.tag = new_tag
		game.save()

	_game_subcommands = ['new', 'list', 'delete', 'join', 'joined', 'leave', 'tag', 'reset_tag']
	def do_game(self, line):
		"""
		interact with games. Has the following sub commands:
		new - create a new game
		delete - delete a game you created before it has started
		list - list upcoming games
		join - join a game
		leave - leave a game
		tag - show your current / next tag
		"""
		if line == '':
			line = 'list'
		if line not in self._game_subcommands:
			self.poutput('unrecognized subcommand: {}'.format(line))
			return
		func = getattr(self, '{}_game'.format(line))
		return func()

	def complete_game(self, text, line, bidx, eidx):
		if text is None:
			ret = self._game_subcommands[:]
		else:
			ret = [x for x in self._game_subcommands if x.startswith(text)]
		return ret

	def do_target(self, line):
		"""show your current target"""
		game = Game.next_game(self, line)
		pass

	def do_eliminate(self, line):
		"""Eliminate a target"""
		# TODO: process line for game tag
		pass

	def do_stats(self, line):
		"""show your stats"""
		pass

	def do_exit(self, args):
		"""exit nerfzari"""
		return True

	def draw_gamelist(self, games):
		if len(games) > 0:
			joined = [x for x in self._user.games_joined()]
			print('joined: {}'.format(joined))
			header = ['start date', 'name', 'game type', 'creator', 'joined', 'winner']
			data = []
			for game in games:
				data.append((
					game.start_date.strftime('%M/%d/%Y'),
					game.name,
					game.game_type,
					game.creator.user_name,
					'joined' if game.primary_key in joined else '',
					game.winner
				))
			self.draw_table(header, data)

	def draw_table(self, header, data):
		strio = io.StringIO()
		tableprint.table(data, header, out=strio)
		rows = strio.getvalue().split('\n')
		for row in rows:
			if len(row) > 0:
				self.poutput(row)

if __name__ == '__main__':
	# TODO: make the game management thread
	ConfigStore.load_all()
	cfg = ConfigStore.get(NERFZARI_CFG_PATH)
	addr = ('', cfg['listen_port'])
	key_path = cfg['rsa_key']
	auth_cls = Authenticator.get(cfg['auth_cls'])
	try:
		with SSHServer(addr, key_path, NerfzariCmd, auth_cls) as server:
			server.serve_forever()
	except KeyboardInterrupt:
		server.shutdown()

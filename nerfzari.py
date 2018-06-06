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
from nerfzari import ConfigStore, Authenticator, SSHServer, SSHCmd, Game, User


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
	# unregister from game (before game start)
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
			self._user = User.create(
				user_name = self._username,
				real_name = name,
				email = email
			)
			self._user.save()
			self.poutput('user registration complete; welcome to game, {}'.format(name))
		# get a random quote
		self.poutput(random_quote())
		# display game info
		curr_games = Game.active_games()
		if len(curr_games) > 1:
			self.poutput('current game is {}'.format(curr_games[0].name)) # TODO: show all current games
		else:
			next_game = Game.next_game()
			if next_game is not None:
				self.poutput('next scheduled game is {} on {}'.format(next_game.name, next_game.start_date))

	def new_game(self):
		gtype = self.terminput('game type>', False)
		nickname = self.terminput('game name>', False)
		date_str = self.terminput('start date (month/day/year)>', False)
		month, day, year = date_str.split('/')
		date = datetime(int(year), int(month), int(day), 12, 0, 0, 0)
		# create game
		Game.create(
			state_date = date,
			game_type = gtype,
			name = nickname,
			creator = self._user.primary_key
		).save()

	def list_game(self):
		# TODO: show games joined
		games = Game.list_games()
		self.draw_gamelist(games)

	def delete_game(self):
		games = Game.list_games()
		print('games: {}'.format(games))
		if len(games) > 0:
			self.draw_gamelist(games)
			name = self.terminput('game name>', False)
			confirm = self.terminput('are you sure>', False)
			if confirm.lower() in ['y', 'yes']:
				Game.delete_game(name, self._user)
		else:
			self.poutput('you may only delete games you have created')

	def join_game(self):
		# TODO: don't allow join if already joined
		# TODO: only allow joining of upcoming games (start date == now)
		self.draw_gamelist(Game.list_games())
		name = self.terminput('game name>', False)
		Game.join_game(self._user, Game.get(name=name))

	def leave_game(self):
		self.draw_gamelist(Game.list_games())
		name = self.terminput('game name>', False)
		Game.leave_game(self._user, Game.get(name=name))

	_game_subcommands = ['new', 'list', 'delete', 'join', 'joined', 'leave']
	def do_game(self, line):
		"""
		interact with games. Has the following sub commands:
		new - create a new game
		delete - delete a game you created before it has started
		list - list upcoming games
		join - join a game
		leave - leave a game
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
		# TODO: only show target if there is a current game
		pass

	def do_tag(self, line):
		"""Show your current tag"""
		# TODO: show current or next tag
		pass

	def do_stats(self, line):
		"""show your stats"""
		pass

	def do_exit(self, args):
		"""exit nerfzari"""
		return True

	def draw_gamelist(self, games):
		if len(games) > 0:
			joined = [x for x in User.games_joined(self._user)]
			print('joined: {}'.format(joined))
			header = ['start date', 'name', 'game type', 'creator', 'joined']
			data = []
			for game in games:
				data.append((
					game.start_date.strftime('%M/%d/%Y'),
					game.name,
					game.game_type,
					game.creator.user_name,
					'joined' if game.primary_key in joined else ''
				))
			self.draw_table(header, data)

	def draw_table(self, header, data):
		strio = io.StringIO()
		tableprint.table(data, header, out=strio)
		rows = strio.getvalue().split('\n')
		for row in rows:
			if len(row) > 0:
				self.poutput(row)

	'''
	def do_hello(self, args):
		"""say hello"""
		out = 'world'
		if args:
			out = args
		self.poutput('Hello {}'.format(out))

	greetings = ['Alice', 'Adam', 'Bob', 'Barbara']
	def complete_hello(self, text, line, begidx, endidx):
		if not text:
			ret = self.greetings[:]
		else:
			ret = [x for x in self.greetings if x.startswith(text)]
		return ret
	
	def do_input(self, args):
		recv = self.terminput('input>', False)
		self.poutput('You entered: {}'.format(recv))

	def do_box(self, args):
		#for x in [0x6a, 0x6b, 0x6c, 0x6d, 0x6e, 0x71, 0x74, 0x75, 0x76, 0x77, 0x78]:
		#	self.poutput('0x{0:x} {0:c} \x1b(0{0:c}\x1b(B'.format(x))
		strio = io.StringIO()
		tableprint.table([[1,2,3],[4,5,6],[7,8,9]], ['A', 'B', 'C'], out=strio)
		rows = strio.getvalue().split('\n')
		for row in rows:
			if len(row) > 0:
				self.poutput(row)

	def do_exit(self, args):
		"""exit the terminal"""
		self.poutput('exiting...')
		return True
		
	def postloop(self):
		self.poutput('goodbye')
	'''


if __name__ == '__main__':
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

	'''
	# TODO: make this safer for a daemon
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind(('', cfg['listen_port']))
	except socket.error as err:
		log.error('Bind failed: {}'.format(str(err)))
		sys.exit(1)
	print('0')

	try:
		sock.listen()
		conn, addr = sock.accept()
	except socket.error as err:
		log.error('Listen / accpet failed: {}'.format(str(err)))
		sys.exit(1)
	print('1')

	try:
		trans = paramiko.Transport(conn)
		trans.set_gss_host(socket.getfqdn(''))
		trans.add_server_key(host_key)
		auth = Authenticator.make(cfg['auth_cls'])
		server = SSHServer(auth)
		try:
			trans.start_server(server=server)
			print('server started')
		except paramiko.SSHException:
			log.error('SSH negotiation failed')
			sys.exit(1)
		chan = trans.accept(20)
		if chan is None:
			log.error('No channel')
			sys.exit(1)
		server.event.wait(10)
		if not server.event.is_set():
			log.error('Client did not ask for shell')
			sys.exit(1)
		print('2')
		term = NerfzariCmd(chan)
		term.cmdloop('nerfing is true; everything is permitted')

	except Exception as ex:
		log.error('Unexpected exception occurred: {}'.format(str(ex)))
		sys.exit(1)
	finally:
		trans.close()
'''
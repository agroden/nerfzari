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
from nerfzari import ConfigStore, Authenticator, SSHServer, SSHCmd, GameEngine, GameMeta, User, username


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

	def preloop(self):
		# check if this is the first time the user has logged in
		self._user = User.get_by_username(self._username)
		if self._user is None:
			self.poutput('processing login, retrieving user data', end='')
			'''
			for _ in range(3):
				time.sleep(0.5)
				self.poutput('.', end='')
			time.sleep(0.75)
			self.poutput('')
			'''
			self.poutput('error: user not found - please enter your information to access the server')
			name = self.terminput('full name>', False)
			email = self.terminput('email>', False)
			self._user = User.new_user(self._username, name, email)
			self.poutput('user registration complete; welcome to game, {}'.format(name))
		# get a random quote
		#self.poutput(random_quote())
		# display game info
		curr_games = GameMeta.active_games()
		if len(curr_games) > 1:
			self.poutput('current game is {}'.format(curr_games[0].name)) # TODO: show all current games
		else:
			next_game = GameMeta.next_game()
			if next_game is not None:
				self.poutput('next scheduled game is {} on {}'.format(next_game.name, next_game.start_date))

	def new_game(self, line=None):
		def type_completer(text, line, bidx, eidx):
			# TODO: finish type completer from discovered game types
			if text is None:
				ret = GameMeta.game_types()[:]
			else:
				ret = [x for x in GameMeta.game_types() if x.startswith(text)]
			return ret
		gtype = self.terminput('game type>', tab_completer=type_completer)
		name = self.terminput('game name>', False)
		date_str = self.terminput('start date (month/day/year)>', False)
		month, day, year = date_str.split('/')
		date = datetime(int(year), int(month), int(day), 12, 0, 0, 0)
		try:
			GameMeta.new_game(date, gtype, name, self._user)
		except peewee.IntegrityError:
			self.poutput('a game with that name or date already exists.')

	def list_game(self, line=None):
		self.draw_gamelist(GameMeta.list_games())

	def select_game(self, line=None):
		if line is not None:
			name = line
		else:
			self.draw_gamelist(GameMeta.list_games())
			name = self.terminput('game name>', False)
		return name

	def join_game(self, line=None):
		name = self.select_game(line)
		if not self._user.has_joined(name):
			try:
				return GameMeta.get(name=name)
			except peewee.DoesNotExist:
				self.poutput('game {} does not exist'.format(name))
				return None
			if meta.active():
				self.poutput('cannot join an active game')
				return
			player = meta.game.join(self._user)
			self.poutput('your game tag is {}'.format(player.tag))
			self.poutput('your game tag represents you - remember it')
			self.poutput('when you are eliminated, you give your tag to the player that eliminated you')
			self.poutput('if a player discovers your tag, they can use it to eliminate you, so keep it secret!')
		else:
			self.poutput('you have already joined this game')

	def leave_game(self, line=None):
		name = self.select_game(line)
		if self._user.has_joined(name):
			try:
				meta = GameMeta.get(name=name)
			except peewee.DoesNotExist:
				self.poutput('game {} does not exist'.format(name))
				return
			if meta.active():
				self.poutput('cannot leave an active game')
				return
			meta.game.leave(self._user)

	def delete_game(self, line=None):
		name = self.select_game(line)
		try:
			meta = GameMeta.get(name=name)
		except peewee.DoesNotExist:
			self.poutput('game {} does not exist'.format(name))
			return
		if meta.creator != self._user:
			self.poutput('you may only delete games you have created')
			return
		if meta.active():
			self.poutput('cannot delete an active game')
			return
		players = [x for x in meta.players]
		if len(players) > 0:
			self.poutput('game has players, please confirm deletion')
			confirm = self.terminput('confirm>', False)
		else:
			confirm = 'yes'
		if confirm.lower() in ['y', 'yes']:
			meta.safe_delete()

	def tag_game(self, line=None):
		meta = GameMeta.next_game()
		if meta:
			self.poutput('your tag for the game {} is: {}'.format(
				meta.name, meta.game.tag(self._user)))

	def reset_tag_game(self, line=None):
		if line is not None:
			name = line
			try:
				meta = GameMeta.get(name=name)
			except peewee.DoesNotExist:
				self.poutput('game {} does not exist'.format(name))
				return
		else:
			meta = GameMeta.next_game()
		if meta:
			tag = meta.game.tag(self._user)
			self.poutput('your tag for the game {} is: {}'.format(meta.name, tag))
			new_tag = tag
			resp = self.terminput('keep?>')
			while resp.lower() not in ['y', 'yes']:
				new_tag = username.generate_username(8, 8)
				self.poutput('new tag: {}'.format(new_tag))
				resp = self.terminput('keep?>')
			meta.game.reset_tag(self._user, new_tag)

	def start_game(self, line=None):
		name = self.select_game(line)
		meta = GameMeta.get(name=name)
		if meta is not None:
			meta.game.start()

	_game_subcommands = ['new', 'list', 'delete', 'join', 'joined', 'leave', 'tag', 'reset_tag', 'start']
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
		parts = line.split()
		sub_cmd = parts[0]
		if sub_cmd == '':
			sub_cmd = 'list'
		if sub_cmd not in self._game_subcommands:
			self.poutput('unrecognized subcommand: {}'.format(sub_cmd))
			return
		func = getattr(self, '{}_game'.format(sub_cmd))
		return func(' '.join(parts[1:]) if len(parts) > 1 else None)

	def complete_game(self, text, line, bidx, eidx):
		if text is None:
			ret = self._game_subcommands[:]
		else:
			ret = [x for x in self._game_subcommands if x.startswith(text)]
		return ret

	def get_game(self, line=None):
		if line is not None:
			name = line
			try:
				return GameMeta.get(name=name)
			except peewee.DoesNotExist:
				self.poutput('game {} does not exist'.format(name))
				return
		else:
			return GameMeta.next_game()

	def do_target(self, line):
		"""show your current target"""
		meta = self.get_game(line)
		if meta is not None:
			target = meta.game.target(self._user)
			self.poutput('your target is: {}'.format(target.real_name))
		
	def do_eliminate(self, line):
		"""eliminate a target by their game tag"""
		meta = self.get_game(line)
		if meta is not None:
			meta.eliminate_by_tag(self._user, line)

	def do_stats(self, line):
		"""show your stats"""
		pass

	def do_exit(self, args):
		"""exit nerfzari"""
		return True

	def draw_gamelist(self, games):
		if len(games) > 0:
			joined = [x for x in self._user.games_joined()]
			header = ['start date', 'name', 'game type', 'creator', 'joined', 'status']
			data = []
			for game in games:
				status = 'pending'
				if game.over:
					status = 'over'
				if game.start_date >= datetime.now():
					status = 'active'
				data.append((
					game.start_date.strftime('%M/%d/%Y'),
					game.name,
					game.type,
					game.creator.user_name,
					'joined' if game.primary_key in joined else '',
					status
				))
			self.draw_table(header, data)

	def draw_table(self, header, data):
		strio = io.StringIO()
		tableprint.table(data, header, out=strio)
		rows = strio.getvalue().split('\n')
		for row in rows:
			if len(row) > 0:
				self.poutput(row)

	def emptyline(self):
		pass

if __name__ == '__main__':
	# TODO: make the game management thread
	ConfigStore.load_all()
	cfg = ConfigStore.get(NERFZARI_CFG_PATH)
	addr = ('', cfg['listen_port'])
	key_path = cfg['rsa_key']
	auth_cls = Authenticator.get(cfg['auth_cls'])
	engine = GameEngine()
	engine.start()
	try:
		with SSHServer(addr, key_path, NerfzariCmd, auth_cls) as server:
			server.serve_forever()
	except KeyboardInterrupt:
		engine.stop()
		server.shutdown()

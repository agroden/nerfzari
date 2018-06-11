"""
"""


__license__ = 'MIT'
__all__ = []

import abc
import datetime
import uuid
import threading
import importlib
import pkgutil
import peewee

from .username import generate_username
import plugins


def _iter_plugins(nspkg=plugins):
	return pkgutil.iter_modules(nspkg.__path__, nspkg.__name__ + '.')

plugins = {
	name: importlib.import_module(name) for _, name, _ in _iter_plugins()
}

importlib.invalidate_caches()

def all_subclasses(cls):
	def recurse(cls):
		return set(cls.__subclasses__()).union(
			[s for c in cls.__subclasses__() for s in all_subclasses(c)])
	return { scls.__name__: scls for scls in recurse(cls) }

class GameBase(abc.ABC):
	MAX_ADJ = 8
	MAX_NOUN = 8
	
	def __init__(self, game):
		self.game = game

	def started(self):
		return self.game.start_date > datetime.datetime.now

	def join(self, user):
		if self.game not in user.games:
			tag = generate_username(GameBase.MAX_ADJ, GameBase.MAX_NOUN)
			player = Player.create(
				user = user,
				game = self.game,
				tag = tag
			)
			player.save()
			return player
		return player.get(user=user, game=self.game)

	def leave(self, user):
		try:
			player = Player.get((Player.user == user) & (Player.game == self.game))
			player.delete_instance()
		except peewee.DoesNotExist:
			pass

	def tag(self, user):
		player = Player.get((Player.user == user) & (Player.game == self.game))
		return player.tag

	def reset_tag(self, user, tag):
		player = Player.get((Player.user == user) & (Player.game == self.game))
		player.tag = tag
		player.save()

	def safe_delete(self):
		for player in self.game.players:
			player.delete_instance()
		self.game.delete_instance()

	@staticmethod
	def get_by_id(guid):
		game = Game.get(primary_key=guid)
		ret = all_subclasses(GameBase)[game.game_type]
		return ret(game)

	@staticmethod
	def get_by_name(name):
		game = Game.get(name=name)
		ret = all_subclasses(GameBase)[game.game_type]
		return ret(game)

	@staticmethod
	def new_game(start_date, game_type, name, creator):
		"""Factory for creating a new game"""
		subs = all_subclasses(GameBase)
		ret = subs[game_type]
		game = Game.create(
			state_date = start_date,
			game_type = game_type,
			name = name,
			creator = creator
		)
		game.save()
		return ret(game)

	@staticmethod
	def active_games():
		try:
			return (Game
				.select()
				.where((Game.start_date <= datetime.datetime.now()) & (Game.complete == False))
				.order_by(Game.start_date.desc())
			)
		except peewee.DoesNotExist:
			return []

	@staticmethod
	def next_game():
		try:
			return (Game
				.select()
				.where(Game.over == False)
				.order_by(Game.start_date.desc())
				.get()
			)
		except peewee.DoesNotExist:
			return None

	@staticmethod
	def list_games(creator=None, start_date=None, end_date=None):
		try:
			ret = (Game
				.select()
				.order_by(Game.start_date.desc())
			)
			if start_date is not None:
				ret = ret.where(Game.start_date >= start_date)
			if end_date is not None:
				ret = ret.where(Game.start_date <= end_date)
			if creator is not None:
				ret = ret.where(Game.creator == creator)
			return ret
		except peewee.DoesNotExist:
			return []

	@abc.abstractmethod
	def start(self):
		pass

	@abc.abstractmethod
	def eliminate(self, user, target):
		pass

	@abc.abstractmethod
	def winner(self):
		pass


class GameEngine(threading.Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
		super().__init__(group, target, name, args, kwargs)
		self.stopped= threading.Event()

	def stop(self):
		self.stopped.set()

	def run(self):
		while not self.stopped.is_set():
			# TODO: check to see if any games need to be started
			games = Game.active_games()
			now = datetime.datetime.now
			for game in games:
				if game.start_date > now:
					game.start()
			self.stopped.wait(10)

'''
class GameFactory(object):
	def get_game(name, type):
		if name not in GameFactory.game_plugins.keys():
			raise KeyError('{} not found'.format(name))
'''


_db = peewee.SqliteDatabase('nerfzari.sqlite')


class BaseModel(peewee.Model):
	class Meta:
		database = _db


class UUIDModel(BaseModel):
	primary_key = peewee.UUIDField(
		primary_key=True,
		default=uuid.uuid4()
	)


class User(UUIDModel):
	"""
	"""
	user_name = peewee.TextField(unique=True)
	real_name = peewee.TextField()
	email = peewee.TextField()
	image_path = peewee.TextField(null=True)

	@staticmethod
	def get_by_username(uname):
		try:
			return User.get(user_name=uname)
		except peewee.DoesNotExist:
			return None

	@staticmethod
	def new_user(user_name, real_name, email):
		user = User.create(
				user_name = user_name,
				real_name = real_name,
				email = email
			)
		user.save()
		return user

	def games_joined(self):
		return [x.game_id for x in self.games]

	def has_joined(self, game_name):
		for x in self.games:
			if x.name == game_name:
				return True
		return False

User.create_table()

class Game(UUIDModel):
	"""
	"""
	start_date = peewee.DateTimeField(default=datetime.datetime.now)
	game_type = peewee.TextField() # TODO set choices= game types gathered by plugin engine
	name = peewee.TextField(unique=True)
	creator = peewee.ForeignKeyField(User, backref='created_games')
	over = peewee.BooleanField(default=False)
Game.create_table()


class Player(BaseModel):
	"""
	"""
	class Meta:
		primary_key = peewee.CompositeKey('user', 'game')
	user = peewee.ForeignKeyField(User, backref='games')
	game = peewee.ForeignKeyField(Game, backref='players')
	tag = peewee.TextField(default=generate_username(8, 8))
	eliminated_by = peewee.ForeignKeyField(Player, null=True)
	eliminated_on = peewee.DateTimeField(null=True)

Player.create_table()


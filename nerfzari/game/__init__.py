"""
"""


__license__ = 'MIT'
__all__ = []


import datetime
import peewee
import uuid
from .username import generate_username


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
	winner = peewee.ForeignKeyField(User, null=True)

	def started(self):
		return self.start_date > datetime.datetime.now

	def finished(self):
		return self.start_date > datetime.datetime.now and self.winner is not None

	def join(self, user):
		if self not in user.games:
			tag = generate_username(8, 8)
			player = Player.create(
				user = user,
				game = self,
				tag = tag
			)
			player.save()
			return player

	def leave(self, user):
		try:
			player = Player.get((Player.user == user) & (Player.game == self))
			player.delete_instance()
		except peewee.DoesNotExist:
			pass

	def tag(self, user):
		player = Player.get((Player.user == user) & (Player.game == self))
		return player.tag

	def reset_tag(self, user, tag):
		player = Player.get((Player.user == user) & (Player.game == self))
		player.tag = tag
		player.save()

	def safe_delete(self):
		for player in self.players:
			player.delete_instance()
		self.delete_instance()

	@staticmethod
	def new_game(start_date, game_type, name, creator):
		game = Game.create(
			state_date = start_date,
			game_type = game_type,
			name = name,
			creator = creator
		)
		game.save()
		return game

	@staticmethod
	def active_games():
		try:
			return (Game
				.select()
				.where((Game.start_date <= datetime.datetime.now()) & (Game.winner.is_null(True)))
				.order_by(Game.start_date.desc())
			)
		except peewee.DoesNotExist:
			return []

	@staticmethod
	def next_game():
		try:
			return (Game
				.select()
				.where(Game.winner.is_null(True))
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

Game.create_table()


class Player(BaseModel):
	"""
	"""
	class Meta:
		primary_key = peewee.CompositeKey('user', 'game')
	user = peewee.ForeignKeyField(User, backref='games')
	game = peewee.ForeignKeyField(Game, backref='players')
	tag = peewee.TextField(default=generate_username(8, 8))
	eliminated_by = peewee.ForeignKeyField(User, null=True)
	eliminated_on = peewee.DateTimeField(null=True)

Player.create_table()


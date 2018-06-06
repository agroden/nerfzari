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
	def games_joined(user):
		return [x.game_id for x in user.games]
		'''
		return (Player
			.select(Player.game_key)
			.where(Player.user_key == user.primary_key)
		)
		'''

User.create_table()


class Game(UUIDModel):
	"""
	"""
	start_date = peewee.DateTimeField(
		default=datetime.datetime.now
	)
	game_type = peewee.TextField() # TODO set choices= game types gathered by plugin engine
	name = peewee.TextField(unique=True)
	creator = peewee.ForeignKeyField(User, backref='created_games')
	winner = peewee.ForeignKeyField(User, null=True)

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
	
	@staticmethod
	def delete_game(name, creator):
		game = Game.get((Game.creator == creator) & (Game.name == name))
		game.delete_instance()

	@staticmethod
	def join_game(user, game):
		if game not in user.games:
			tag = generate_username(8, 8)
			player = Player.create(
				user = user,
				game = game,
				tag = tag
			)
			print('Creating player: {}'.format(player))
			player.save()
	
	@staticmethod
	def leave_game(user, game):
		player = Player.get(
			(Player.user == user) & (Player.game == game)
		)
		print('removing player: {}'.format(player))
		player.delete_instance()

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


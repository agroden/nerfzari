"""
"""


import peewee
import uuid
from datetime import datetime
from .username import generate_username


MAX_ADJ = 8
MAX_NOUN = 8
_db = peewee.SqliteDatabase('nerfzari.sqlite')


def all_subclasses(cls, name_func=None):
	def recurse(cls):
		return set(cls.__subclasses__()).union(
			[s for c in cls.__subclasses__() for s in all_subclasses(c)])
	if name_func is not None:
		return { name_func(scls): scls for scls in recurse(cls) }
	return { scls.__name__: scls for scls in recurse(cls) }



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
			if x.game.name == game_name:
				return True
		return False

	def kills(self):
		count = 0
		for meta in self.games:
			count += meta.kills()
		return count

	def deaths(self):
		count = 0
		for meta in self.games:
			count += meta.deaths()
		return count


class GameMeta(UUIDModel):
	"""
	"""
	start_date = peewee.DateTimeField(default=datetime.now)
	type = peewee.TextField()
	name = peewee.TextField(unique=True)
	creator = peewee.ForeignKeyField(User, backref='created_games')
	over = peewee.BooleanField(default=False)

	@property
	def game(self):
		"""
		Acts as a backref to the specific game entry based on the game type.
		peewee's backrefs are cool but fragile; for instance, specific game 
		types inherit the "meta" foreign key from :class:`GameBase`, which 
		can break the backref functionality since the base class doesn't 
		know which table to search.
		"""
		subs = all_subclasses(GameBase)
		sub = subs.get(self.type)
		if sub is not None:
			return sub.get(sub.meta == self.primary_key)
		return None

	def active(self):
		return self.start_date >= datetime.now()

	def safe_delete(self):
		players = PlayerMeta.select().where(PlayerMeta.game == self.primary_key)
		for player in players:
			player.safe_delete()
		self.game.delete_instance()
		self.delete_instance()

	@staticmethod
	def game_types():
		return all_subclasses(GameBase).keys()

	@staticmethod
	def new_game(start_date, game_type, name, creator):
		"""Factory for creating a new game"""
		game_type = game_type.capitalize()
		subs = all_subclasses(GameBase)
		if game_type not in subs.keys():
			raise RuntimeError('Unknown game type: {}'.format(game_type))
		# create meta
		meta = GameMeta.create(
			state_date = start_date,
			type = game_type,
			name = name,
			creator = creator
		)
		meta.save()
		# create game
		sub = subs[game_type]
		game = sub.create(
			meta = meta
		)
		game.save()
		return meta

	@staticmethod
	def active_games():
		return (GameMeta
			.select()
			.where((GameMeta.start_date <= datetime.now()) & (GameMeta.over == False))
			.order_by(GameMeta.start_date.desc())
		)

	@staticmethod
	def next_game():
		res = (GameMeta
			.select()
			.where(GameMeta.over == False)
			.order_by(GameMeta.start_date.desc())
		)
		if len(res) > 0:
			return res[0]
		return None

	@staticmethod
	def list_games(game_type=None, creator=None, start_date=None, end_date=None):
		res = GameMeta.select().order_by(GameMeta.start_date.desc())
		if game_type is not None:
			res = res.where(GameMeta.type == game_type)
		if creator is not None:
			res = res.where(GameMeta.creator == creator)
		if start_date is not None:
			res = res.where(GameMeta.start_date >= start_date)
		if end_date is not None:
			res = res.where(GameMeta.start_date <= end_date)
		return res


class GameBase(UUIDModel):
	meta = peewee.ForeignKeyField(GameMeta)
	
	def start(self):
		raise NotImplementedError('Subclasses must implement the start method')

	def target(self, user):
		raise NotImplementedError('Subclasses must implement the target method')

	def eliminate_by_tag(self, user, tag):
		player = PlayerMeta.get((PlayerMeta.user == user) & (PlayerMeta.game == self.meta))
		target = PlayerMeta.get(PlayerMeta.tag == tag)
		self.eliminate(player, target)

	def eliminate(self, player, target):
		if player.eliminated_by is None:
			raise RuntimeError('an eliminated player can no longer participate in the game')
		target.eliminated_by = player
		target.eliminated_on = datetime.now
		target.save()
	
	def started(self):
		return self.meta.start_date > datetime.now

	def join(self, user):
		if self.meta not in user.games:
			return PlayerMeta.new_player(user, self.meta)
		else:
			return PlayerMeta.get(
				(PlayerMeta.user == user) & (PlayerMeta.game == self.meta)
			)

	def leave(self, user):
		try:
			player = PlayerMeta.get(
				(PlayerMeta.user == user) & (PlayerMeta.game == self.meta)
			)
			player.safe_delete()
		except peewee.DoesNotExist:
			pass

	def tag(self, user):
		player = PlayerMeta.get((PlayerMeta.user == user) & (PlayerMeta.game == self.meta))
		return player.tag

	def reset_tag(self, user, tag):
		player = PlayerMeta.get((PlayerMeta.user == user) & (PlayerMeta.game == self.meta))
		player.tag = tag
		player.save()


class PlayerMeta(UUIDModel):
	"""
	"""
	user = peewee.ForeignKeyField(User, backref='games')
	game = peewee.ForeignKeyField(GameMeta, backref='players')
	tag = peewee.TextField(unique=True, default=generate_username(MAX_ADJ, MAX_NOUN))
	eliminated_on = peewee.DateTimeField(null=True)
	eliminated_by = peewee.ForeignKeyField('self', null=True)

	@property
	def player(self):
		"""
		See GameMeta.game for an explanation of what is going on here.
		"""
		subs = all_subclasses(PlayerBase, lambda x: x.FOR_GAMETYPE)
		sub = subs.get(self.game.type)
		if sub is not None:
			return sub.get(sub.meta == self.primary_key)
		return None

	def safe_delete(self):
		self.player.delete_instance()
		self.delete_instance()

	def kills(self):
		return (PlayerMeta
			.select()
			.where((PlayerMeta.game == self.game) & (PlayerMeta.eliminated_by == self))
			.count()
		)

	def deaths(self):
		if self.eliminated_by.is_null():
			return 1
		return 0

	@staticmethod
	def new_player(user, game, tag=None):
		if tag is None:
			tag = generate_username(MAX_ADJ, MAX_NOUN)
		# create meta
		meta = PlayerMeta.create(
			user = user,
			game = game,
			tag = tag
		)
		meta.save()
		# create player
		subs = all_subclasses(PlayerBase, lambda x: x.FOR_GAMETYPE)
		sub = subs[game.type]
		player = sub.create(
			meta = meta
		)
		player.save()
		return meta


class PlayerBase(UUIDModel):
	FOR_GAMETYPE=None
	meta = peewee.ForeignKeyField(PlayerMeta)
"""
"""



__license__ = 'MIT'
__all__ = []

import datetime
import peewee
import uuid


_db = peewee.SqliteDatabase("")


class BaseModel(peewee.Model):
	class Meta:
		database = _db

class UUIDModel(BaseModel):
	primary_key = peewee.UUIDField(
		primary_key=True,
		default=uuid.uuid4()
	)

class User(UUIDModel):
	first_name = peewee.TextField()
	last_name = peewee.TextField()


class Game(UUIDModel):
	start_date = peewee.DateTimeField(
		default=datetime.datetime.now
	)

class Player(UUIDModel):
	"""
	primary_key | user_key | game_key | positive | negative
	"""
	username = peewee.TextField(default=gen_uname())
	user_key = peewee.ForeignKeyField(User, backref='games')
	game_key = peewee.ForeignKeyField(Game, backref='players')
	positive = peewee.IntegerField()
	negative = peewee.IntegerField()
	eliminated_by = peewee.ForeignKeyField(User, backref='')
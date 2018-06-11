"""
"""


import datetime
import peewee
import random
from .. import *


class StandardAssassinGame(UUIDModel):
	game = peewee.ForeignKeyField(Game, backref='extension')
	winner = peewee.ForeignKeyField(User)


class StandardAssassinPlayer(UUIDModel):
	player = peewee.ForeignKeyField(Player, backref='extension')
	target = peewee.ForeignKeyField(Player)


class StandardAssassin(GameBase):
	def __init__(self, game):
		super().__init__(game)
		self.ext = StandardAssassinGame.get(self.game.primary_key)

	def start(self):
		players = [x for x in self.game.players]
		random.shuffle(players)
		for idx in range(len(players)-1):
			players[idx].extension.target = players[idx+1]
			players[idx].save()
		players[-1].extension.target = players[0]
		players[-1].save()

	def eliminate(self, player, target):
		if player.eliminated_by is None:
			raise RuntimeError('an eliminated player can no longer participate in the game')
		target.eliminated_by = player
		target.eliminated_on = datetime.datetime.now
		target.save()
		remaining = [x for x in Player.select().where(Player.eliminated_by.is_null())]
		if len(remaining) == 1:
			self.game.extension.winner = remaining[0]
			self.game.extension.save()
			self.game.over = True
			self.game.save()


	def winner(self):
		return self.game.extension.winner

"""
"""


import random
import peewee
from datetime import datetime
from .models import GameBase, PlayerBase, PlayerMeta


class AssassinPlayer(PlayerBase):
	FOR_GAMETYPE='Assassin'
	target = peewee.ForeignKeyField(PlayerMeta, null=True)


class Assassin(GameBase):
	winner = peewee.ForeignKeyField(PlayerMeta, null=True)

	def start(self):
		players = [x for x in self.meta.players]
		random.shuffle(players)
		for idx in range(len(players)-1):
			players[idx].extension.target = players[idx+1]
			players[idx].save()
		players[-1].extension.target = players[0]
		players[-1].save()

	def eliminate(self, player, target):
		super().eliminate(player, target)
		remaining = [x for x in PlayerMeta.select().where(PlayerMeta.eliminated_by.is_null())]
		if len(remaining) == 1:
			self.winner = remaining[0]
			self.meta.over = True
			self.meta.save()
			self.save()

	def target(self, user):
		pmeta = self.meta.players.where(PlayerMeta.user == user)
		return pmeta.player.target.user
		


"""
"""


import threading
from datetime import datetime
from .models import GameMeta


class GameEngine(threading.Thread):
	def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
		super().__init__(group, target, name, args, kwargs)
		self.stopped= threading.Event()

	def stop(self):
		self.stopped.set()

	def run(self):
		while not self.stopped.is_set():
			# TODO: check to see if any games need to be started
			metas = GameMeta.active_games()
			now = datetime.now
			for meta in metas:
				if meta.start_date > now:
					meta.game.start()
			self.stopped.wait(10)
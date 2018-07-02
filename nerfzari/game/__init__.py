"""
"""


from .models import User, GameMeta, GameBase, PlayerMeta, PlayerBase
from .engine import GameEngine
from .assassin import Assassin, AssassinPlayer


__license__ = 'MIT'
__all__ = ['models', 'engine', 'assassin']


# create tables
User.create_table()
GameMeta.create_table()
# GameBase is a base class for specific game types and should not be created
PlayerMeta.create_table()
# PlayerBase is a base class for specific game types and should not be created
Assassin.create_table()
AssassinPlayer.create_table()
# more tables can be created here
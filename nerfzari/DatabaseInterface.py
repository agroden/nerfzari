from typing import List, Any
from User import User
import sqlite3
import os

# Master Database
############################################################
# Table: Games
# GameID | filename
Gtable = "Games (game_id INTEGER PRIMARY KEY, database_name TEXT UNIQUE)"
############################################################

############################################################
# Table: Users
# UID, First, Last, kills, death, games played, games won
UTable = "Users (UID INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, kills INTEGER, death INTEGER, games_played INTEGER, games_won INTEGER)"
############################################################

# Game Database
############################################################
# Table: Assassins
# UID | Assassin ID | Target ID
ATable = "Users (UID INTEGER PRIMARY KEY, assassin_id TEXT UNIQUE, target_id TEXT)"
############################################################

# databases are stored where DatabaseInterface.py is located
dir_path = os.path.dirname(os.path.realpath(__file__))
masterdb = None
currGdbName = "currGame.db"
currGdb = None

class gameDb:
    db = None
    gid : int

    def __init__(self, game_id):
        filename = 

def get_master():
    if masterdb == None:
        try:
            masterdb = sqlite3.connect(dir_path+"/master.db")
        except Error as e:
            print e
    return masterdb

def get_curr_game():
    if currGdb == None:
        try:
            currGdb = sqlite3.connect(dir_path+"/"+currGdbName)
        except Error as e:
            print e
    return currGdb


def close():
    if masterdb != None:
        masterdb.close()
    if currGdb != None:
        currGdb.close()

def start_unittest_mode():
	"""
	This function resets the database for testing
	"""
    try:
        masterdb = sqlite3.connect(":memory:")
    except Error as e:
        print e

    try:
        currGdb = sqlite3.connect(":memory:")
    except Error as e:
        print e

def add_game(object: 'Game') -> int:
	"""
	:param object: User object representing the new user
	:return: Returns unique id for the user on success; otherwise -1 is returned
	"""
	games.append(object)
	return len(games)-1

def get_game(game_id: int) -> 'Game':
	return games[game_id]

def add_user(object: 'User') -> int:
	"""
	:param object: User object representing the new user
	:return: Returns unique id for the user on success; otherwise -1 is returned
	"""
	users.append(object)
	return len(users)-1

def get_user(user_id: int) -> 'User':
	return users[user_id]

def register_kill(user_id: int) -> bool:
	user = get_user(user_id)
	if user is None:
		print("ERROR FakeDatabase.register_kill: user with id " + str(user_id) + " does not exist")
	user.kills += 1
	return True

def register_death(user_id: int) -> bool:
	user = get_user(user_id)
	if user is None:
		print("ERROR FakeDatabase.register_kill: user with id " + str(user_id) + " does not exist")
	user.deaths += 1
	return True

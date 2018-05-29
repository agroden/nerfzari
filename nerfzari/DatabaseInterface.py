from hashlib import sha256
from typing import List, Any
from User import User

import sqlite3
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

# Master Database
############################################################
# Table: Games
# GameID | filename | start date  NOTE: format %Y%m%d-%H:%M:%S ie 109004280-23:45:13
GTable = "Games (game_id INTEGER PRIMARY KEY, database_name TEXT UNIQUE, start_date TEXT)"
############################################################

############################################################
# Table: Users
# UID | First | Last | kills | death | games played | games won
UTable = "Users (UID INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, kills INTEGER, death INTEGER, games_played INTEGER, games_won INTEGER)"
############################################################

# Game Database
############################################################
# Table: Assassins
# UID | Assassin ID | Target ID | 
ATable = "Users (UID INTEGER PRIMARY KEY, assassin_id TEXT UNIQUE, target_id TEXT)"
############################################################

class DatabaseInterface:
    # databases are stored where DatabaseInterface.py is located
    masterdb = None
    gamedb = None

    def __init__(self, unittest=False):
        mdbFileName = dir_path+"/master.db"
        self.unittest = unittest

        if self.unittest:
            try:
                self.masterdb = sqlite3.connect(":memory:")
                self.masterdb.execute("CREATE TABLE " + UTable)
                self.masterdb.execute("CREATE TABLE " + GTable)
                self.masterdb.commit()
            except Error as e:
                print(e)

        if self.masterdb == None:
            try:
                if not os.path.isfile(mdbFileName):
                    self.masterdb = sqlite3.connect(dir_path+"/master.db")
                    self.masterdb.execute("CREATE TABLE " + UTable)
                    self.masterdb.execute("CREATE TABLE " + GTable)
                    self.masterdb.commit()
                else:
                    self.masterdb = sqlite3.connect(dir_path+"/master.db")
            except Error as e:
                print(e)

    def __del__(self):
        if self.masterdb != None:
            self.masterdb.commit()
            self.masterdb.close()
        if self.gamedb != None:
            self.gamedb.commit()
            self.gamedb.close()

    #@property
    #def masterdb(self):
    #    return self.masterdb

    def get_game(self, game_id: int) -> "Game":
        if self.game.id == game_id:
            return self.currGdb

        cursor = self.masterdb.cursor()
        cursor.execute("SELECT * FROM Games WHERE game_id={}".format(game_id))
        ret = cursor.fetchone()
        if not ret:
            return -1

        print(ret)

        # GameID | filename | start date  NOTE: format %Y%m%d-%H:%M:%S ie 109004280-23:45:13
        # TODO: Handle game type
        self.game = NerfAssassin(ret[1], datetime.strptime(ret[2], "%Y%m%d-%H:%M:%S"))
        if self.unittest:
            self.gamedb = sqlite3.connect(dir_path+"/"+ret[1])
        else:
            self.gamedb = sqlite3.connect(":memory:")

        return self.game # TODO consider not returning ref 

    def add_game(self, game: 'Game') -> int:
        """
        :param object: Game object representing the new game
        :return: Returns unique id for the game on success; otherwise -1 is returned
        """
        cursor = masterdb.cursor()
        try:
            cursor.execute("INSERT INTO Games (game_id, database_name, start_data) VALUES ({}, '{}', '{}')".\
            format(game.id, game.name, game.start_date.strftime("%Y%m%d-%H:%M:%S")))
        except sqlite3.IntegrityError:
            print('ERROR: ID already exists in PRIMARY KEY column game_id')
            return -1

        return game.id

    def add_user(self, user: 'User') -> int:
        """
        :param object: User object representing the new user
        :return: Returns unique id for the user on success; otherwise -1 is returned
        """

        # create "hopefully" random id
        hs = sha256()
        hs.update(str(user.first_name + user.last_name).encode("utf-8"))
        hs.update(os.urandom(16))
        uid = int(hs.hexdigest()[:8], 16)

        cursor = self.masterdb.cursor()
        try:
            cursor.execute("INSERT INTO Users (UID, first_name, last_name) VALUES ({}, '{}', '{}')".\
            format(uid, user.first_name, user.last_name))
        except sqlite3.IntegrityError:
            print('ERROR: ID already exists in PRIMARY KEY column UID')
            return -1

        return uid

    def get_user(self, user_id: int) -> 'User':
        cursor = self.masterdb.cursor()
        cursor.execute("SELECT * FROM Users WHERE UID={}".format(user_id))
        ret = cursor.fetchone()
        if not ret:
            return None

        print(ret)
   
        return User(ret[1], ret[2])

    def register_kill(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user is None:
            print("ERROR FakeDatabase.register_kill: user with id " + str(user_id) + " does not exist")
            return False
        user.kills += 1

        cursor = masterdb.cursor()
        cursor.execute("UPDATE Games SET {cn}=('Hi World') WHERE {idf}=(123456)".\
        format(tn=table_name, cn=column_name, idf=id_column))

        return True

    def register_death(self, user_id: int) -> bool:
        user = self.get_user(user_id)

        if user is None:
            print("ERROR FakeDatabase.register_kill: user with id " + str(user_id) + " does not exist")
            return False

        user.deaths += 1
        return True

    def start_unittest_mode(self):
        """
        This function resets the database for testing
        """
        if self.masterdb != None:
            self.masterdb.close()

        try:
            self.masterdb = sqlite3.connect(":memory:")
            self.masterdb.execute("CREATE TABLE " + UTable)
            self.masterdb.execute("CREATE TABLE " + GTable)
            self.masterdb.commit()
        except Error as e:
            print(e)

        if self.gamedb != None:
            self.masterdb.close()

        try:
            gamedb = sqlite3.connect(":memory:")
        except Error as e:
            print(e)


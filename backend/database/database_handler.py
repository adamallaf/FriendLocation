from database import Database
import random

class DatabaseHandler:
    __instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not DatabaseHandler.__instance:
            DatabaseHandler.__instance = object.__new__(cls)
        return DatabaseHandler.__instance

    __USERS = "users"
    __LOCATION_HISTORY = "location_history"
    __LOCATION = "location"

    db_name = "my.db"

    def __init__(self):
        self.db = None

    def connect(self):
        self.db = Database(self.db_name)
        self._createUsersTab()
        self._createLocationHistoryTab()
        self._createLocationTab()

    def _createUsersTab(self):
        if not self.db.isTableExist(self.__USERS):
            self.db.createTable(self.__USERS, "uniqueID INTEGER UNIQUE")
            self.db.addColumn(self.__USERS, "username", 'CHAR(16)')
            self.db.addColumn(self.__USERS, "password")

    def _createLocationHistoryTab(self):
        if not self.db.isTableExist(self.__LOCATION_HISTORY):
            self.db.createTable(self.__LOCATION_HISTORY, "uniqueID INTEGER")
            self.db.addColumn(self.__LOCATION_HISTORY, "username", 'CHAR(16)')
            self.db.addColumn(self.__LOCATION_HISTORY, "latitude", 'FLOAT')
            self.db.addColumn(self.__LOCATION_HISTORY, "longitude", 'FLOAT')

    def _createLocationTab(self):
        if not self.db.isTableExist(self.__LOCATION):
            self.db.createTable(self.__LOCATION, "uniqueID INTEGER UNIQUE")
            self.db.addColumn(self.__LOCATION, "username", 'CHAR(16)')
            self.db.addColumn(self.__LOCATION, "latitude", 'FLOAT')
            self.db.addColumn(self.__LOCATION, "longitude", 'FLOAT')

    def push(self, location_object):
        username = location_object.username
        longitude = location_object.longitude
        latitude = location_object.latitude
        uID = self.db.get(self.__USERS, uniqueID=None, condition="username='{}'".format(username))
        if uID:
            uID = uID[0][0]
        else:
            raise UserWarning("USER NOT FOUND!")
        self.db.insert(self.__LOCATION_HISTORY, uniqueID=uID, username=username, latitude=latitude, longitude=longitude)
        self.db.insertReplace(self.__LOCATION, uniqueID=uID, username=username, latitude=latitude, longitude=longitude)
    
    def pull(self, usernames):
        location_objects = []

        for username in usernames:
            uID = self.db.get(self.__USERS, uniqueID=None, condition="username='{}'".format(username))
            if uID:
                uID = uID[0][0]
            else:
                raise UserWarning("USER NOT FOUND!")
            result = self.db.get(self.__LOCATION, username=None, latitude=None, longitude=None, condition="username='{}' and uniqueID={}".format(username, uID))
            if result:
                location_objects.append({"username": result[0][0], "latitude": result[0][1], "longitude": result[0][2]})

        return location_objects

    def close(self):
        del self.db

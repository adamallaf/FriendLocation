import json


class LocationPoint:
    #def __init__(self, userName, userId, timeStamp, longitude, latitude):
    def __init__(self, username, longitude, latitude):
        self._username = username
        self._latitude = latitude
        self._longitude = longitude
        #self.userId = userId
        #self.timeStamp = timeStamp

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        self._longitude = value

    def moveToNewLocation(self, longitude, latitude):
        self._longitude = longitude
        self._latitude = latitude

    def convertToJSON(self):
        return json.dumps({'username': self.username, 'latitude': self.latitude, 'longitude': self.longitude})

import MySQLdb

class Database:
    def __init__(self):
        self.db = None
        self.cur = None

    def connect(self):
        self.db = MySQLdb.connect(db="friend_location_db", user="friend_location_user")
        self.cur = self.db.cursor()

    def push(self, location_object):
        username = location_object.get_username()
        longitude = location_object.get_longitude()
        latitude = location_object.get_latitude()
        self.cur.execute("""INSERT INTO locations (username, longitude, latitude)
            values (\"%s\", %s, %s) ON DUPLICATE KEY UPDATE longitude=%s, latitude=%s;""",
            (username, longitude, latitude, longitude, latitude))
        self.db.commit()
    
    def pull(self, usernames):
        location_objects = []

        for username in usernames:
            self.cur.execute("SELECT username, longitude, latitude FROM locations WHERE username=\"%s\";", (username,))
            result = self.cur.fetchone()
            if result is not None:
                location_objects.append({"username": result[0], "longitude": result[1], "latitude": result[2]})

        return location_objects

    def close(self):
        self.cur.close()
        self.db.close()

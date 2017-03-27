import json
#Class that defines an area delimited by 4 points
class LocationArea:
    def __init__(self, pointList):
        self.pointList = pointList
        # create a "maximal frame" that surrounds all the points in the list
        # Done by making a rectangle composed of the maximum values in pointList
        self.maxLong = max([obj.longitude for obj in pointList])
        self.minLong = min([obj.longitude for obj in pointList])
        self.maxLat = max([obj.latitude  for obj in pointList])
        self.minLat = min([obj.latitude  for obj in pointList])
        # with this max frame we can calculate a point that lies outside of
        # the location area
        self.point_out = LocationPoint(self.maxLong + 1, self.maxLat)
        self.vectors = []
        # Create the vectors that connect all the points
        # Note: it is important that the points are in the correct order
        for i in range(len(self.pointList) - 1):
            self.vectors.append(Vector(self.pointList[i], self.pointList[i+1]))
        self.vectors.append(Vector(self.pointList[-1], self.pointList[1]))
        

    #Checks if a location Point is inside the area
    def isInside(self, locPoint):
        longitude = locPoint.longitude
        latitude = locPoint.latitude
        # create a ray that connects the outside point to the current point
        ray = Vector(locPoint, self.point_out)
        # check if the current point lies outside of the max frame
        if (longitude >= self.minLong and longitude <= self.maxLong 
                and latitude >= self.minLat and latitude <= self.maxLat and 
            # if the number of intersections is odd, it is inside, else it ain't
            list(map(lambda x: ray.intersects(x), self.vectors)).count(True) % 2
            == 1
            ):
            return True
        else:
            return False

# class for vectors, used inside the others
class Vector:
    # a vector consists of two points
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2

    # checks if two numbers have different signs
    @staticmethod
    def _diff_sign(a,b): 
        return ((a > 0) and (b < 0) or ((a <0) and (b >0)))

    
    # equation in general form a*x + b*y +c = 0 of an infinite line that goes
    # through vector self
    # evaluates the generated equation with the longitude and latitude of point
    # returns a number 
    def _to_eq(self, point):
        # Delta Y
        a = self.p2.get_latitude() - self.p1.get_latitude()
        # - Delta X
        b = self.p1.get_longitude() - self.p2.get_longitude()
        c = self.p2.get_longitude() * self.p1.get_latitude() - self.p1.get_longitude() * self.p2.get_latitude()
        return a * point.get_longitude() + b * point.get_latitude() + c


    # checks if self intersects with vector self
    def intersects(self, vec):
        # if the d1 and d2 have different signs, they are on different sides of the
        # vector self
        d1 = self._to_eq(vec.p1)
        d2 = self._to_eq(vec.p2)

        # we must check again, but otherwise
        d3 = vec._to_eq(self.p1)
        d4 = vec._to_eq(self.p2)
        
        # will return true if the vectors do intersect, false if they don't
        return (self._diff_sign(d1,d2) and self._diff_sign(d3,d4)) 
        

class Database:
    def __init__(self):
        self.db = {}
    def insert(self, locPoint):
        self.db[locPoint.get_username()] = locPoint
    def query_username(self, u_name):
        return self.db.get(u_name)




#Class to define a locationPoint object
class LocationPoint:
    #def __init__(self, userName, userId, timeStamp, longitude, latitude):
    def __init__(self, username, longitude, latitude):
        self.username = username
        #self.userId = userId
        #self.timeStamp = timeStamp
        self.longitude = longitude
        self.latitude = latitude

    # move a point to a new location
    def moveTo(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude
    def get_latitude(self):
        return self.latitude
    def get_longitude(self):
        return self.longitude
    def get_username(self):
        return self.username
    def to_json(self):
        return json.dumps({'username': self.username, 'latitude' :
            self.latitude, 'longitude' : self.longitude})


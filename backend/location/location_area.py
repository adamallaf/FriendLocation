#Class that defines an area delimited by 4 points
from location.location_point import LocationPoint
from location.vector import Vector


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
        self.point_out = LocationPoint("", self.maxLong + 1, self.maxLat)
        self.vectors = []
        # Create the vectors that connect all the points
        # Note: it is important that the points are in the correct order
        for i in range(len(self.pointList) - 1):
            self.vectors.append(Vector(self.pointList[i], self.pointList[i + 1]))
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


class Database:
    def __init__(self):
        self.db = {}
    def insert(self, locPoint):
        self.db[locPoint.username] = locPoint
    def query_username(self, u_name):
        return self.db.get(u_name)

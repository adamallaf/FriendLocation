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
        a = self.p2.latitude - self.p1.latitude
        # - Delta X
        b = self.p1.longitude - self.p2.longitude
        c = self.p2.longitude * self.p1.latitude - self.p1.longitude * self.p2.latitude
        return a * point.longitude + b * point.latitude + c


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
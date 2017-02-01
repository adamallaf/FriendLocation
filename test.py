from backend import Vector, LocationPoint, LocationArea

x = LocationPoint(0,0)
y = LocationPoint(0,2)
v1 = Vector(x,y)

w = LocationPoint(2,1)
z = LocationPoint(-2,1)
v2 = Vector(w,z)

v3 = Vector(LocationPoint(-1,3),LocationPoint(1,-2))
rect1 = LocationPoint(0,0)
rect2 = LocationPoint(0,-2) 
rect3 = LocationPoint(-2, -2)
rect4 = LocationPoint(-2, 0)

def areaTest():
    rect = LocationArea((rect1,rect2,rect3,rect4))
    print("///////////////////////////////")
    print("TESTING AREA OBJECT")
    print("--------------------------------")
    print("TEST WITH SQUARE AREA BEGIN")
    print("Max Long " + str(rect.maxLong))
    print("Min Long " + str(rect.minLong))
    print("Max Lat  " + str(rect.maxLat))
    print("Min Lat  " + str(rect.minLat))
    print("Point out " )
    printPoint(rect.point_out)
    if(rect.isInside(rect.point_out)):
        print("Point out is Inside FAILURE!")
    else:
        print("Point out is effectively Outside SUCCESS!")
    print("Trying with Point (1,1)");
    if(rect.isInside(LocationPoint(1,1))):
        print("Point is Inside FAILURE!")
    else:
        print("Point is effectively Outside SUCCESS!")
    print("Trying with Point (1,1)");
    if(rect.isInside(LocationPoint(1,1))):
        print("Point is Inside FAILURE!")
    else:
        print("Point is effectively Outside SUCCESS!")
    print("Trying with Point (-1,-1)");
    if(rect.isInside(LocationPoint(-1,-1))):
        print("Point is Inside SUCCESS!")
    else:
        print("Point is effectively Outside FAILURE!")
    print("Trying with Point (-1.5,-1.5)");
    if(rect.isInside(LocationPoint(-1.1,-1.1))):
        print("Point is Inside SUCCESS!")
    else:
        print("Point is effectively Outside FAILURE!")
    print("Trying with Point (2.01 , 2.01)");
    if(rect.isInside(LocationPoint(2.01,2.01))):
        print("Point is Inside FAILURE!")
    else:
        print("Point is effectively Outside SUCCESS!")



def printPoint(x):
    print("longitude: " + str(x.get_longitude()), end=" ")
    print("latitude: " + str(x.get_latitude()))
def printVec(v):
    print("point 1:", end=" ")
    printPoint(v.p1)
    print("point 2:", end=" ")
    printPoint(v.p2)

def interTest():
    print("Testing function intersects")
    print ("  Testing with v1 v2 ")
    if(v1.intersects(v2)):
        print("    TRUE Success")
    else:
        print("    FALSE Failure")
    print ("  Testing with v2 v1 ")
    if(v2.intersects(v1)):
        print("    TRUE Success")
    else:
        print("    FALSE Failure")
    print ("  Testing with v1 v3 ")
    if(v1.intersects(v3)):
        print("    TRUE Failure")
    else:
        print("    FALSE Success")
    print ("  Testing with v3 v1 ")
    if(v3.intersects(v1)):
        print("    TRUE Failure")
    else:
        print("    FALSE Success")
    if(v3.intersects(v2)):
        print("    TRUE Success")
    else:
        print("    FALSE Failure")

def diffSignTest():
    print("Testing function _dif_sign")
    print("  Testing with -1, 2 ")
    if (v1._diff_sign(-1,2)):
        print("    TRUE Success")
    else:
        print("    FALSE Failure")
    print("  Testing with 1, -2 ")
    if (v2._diff_sign(-1,2)):
        print("    TRUE Success")
    else:
        print("    FALSE Failure")
    print("  Testing with 1, 2 ")
    if (v3._diff_sign(1,2)):
        print("    TRUE Failure")
    else:
        print("    FALSE Success")
    print("  Testing with -1, -2 ")
    if (v1._diff_sign(1,2)):
        print("    TRUE Failure")
    else:
        print("    FALSE Success")

diffSignTest()
interTest()
areaTest()

from backend import Vector, LocationPoint

x = LocationPoint(0,0)
y = LocationPoint(0,2)
v1 = Vector(x,y)

w = LocationPoint(2,1)
z = LocationPoint(-2,1)
v2 = Vector(w,z)

v3 = Vector(LocationPoint(2,1),LocationPoint(1,1))

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

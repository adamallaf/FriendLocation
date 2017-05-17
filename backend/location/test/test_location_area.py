import pytest
from location import LocationArea
from location import LocationPoint


@pytest.fixture(scope="function")
def locationArea():
    user = "user"
    p1 = LocationPoint(user, 0, 0)
    p2 = LocationPoint(user, 0, -2) 
    p3 = LocationPoint(user, -2, -2)
    p4 = LocationPoint(user, -2, 0)
    rect = (p1, p2, p3, p4)
    return LocationArea(rect)


def test_locationArea_isInside_pointsOutsideLocationArea_ut(locationArea):
    assert locationArea.isInside(LocationPoint("user", 1, 1)) is False
    assert locationArea.isInside(LocationPoint("user", -0.1, 0.1)) is False
    assert locationArea.isInside(LocationPoint("user", 0, 0)) is False


def test_locationArea_isInside_pointInsideLocationArea_ut(locationArea):
    assert locationArea.isInside(LocationPoint("user", -1, -1))
    assert locationArea.isInside(LocationPoint("user", -0.01, -0.01))


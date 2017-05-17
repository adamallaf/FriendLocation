import pytest
from location import LocationPoint
from location import Vector


@pytest.fixture(scope="function")
def vector1():
    v1 = Vector(LocationPoint("", 0, 0), LocationPoint("", 0, 2))
    return v1


@pytest.fixture(scope="function")
def vector2():
    v2 = Vector(LocationPoint("", 2, 1), LocationPoint("", -2, 1))
    return v2


@pytest.fixture(scope="function")
def vector3():
    v3 = Vector(LocationPoint("", 0, -1), LocationPoint("", 1, 2))
    return v3


def test_vector_intersects_vectorsIntersections_ut(vector1, vector2, vector3):
    assert vector1.intersects(vector2) and vector2.intersects(vector1)
    assert vector2.intersects(vector3) and vector3.intersects(vector2)
    assert vector1.intersects(vector3) is False and vector3.intersects(vector1) is False


def test_vector_diff_sign_differentSignVectors_ut(vector1, vector2, vector3):
    assert vector1._diff_sign(-1, 2)
    assert vector2._diff_sign(1, -2)
    assert vector3._diff_sign(1, -2)
    assert vector1._diff_sign(1, -2)

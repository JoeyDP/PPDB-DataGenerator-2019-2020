import pycristoforo as pyc

from geopy.distance import distance
import itertools


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

BE = pyc.get_shape("Belgium")


def convertPoint(point):
    return tuple(reversed(point['geometry']['coordinates']))


def distancePoints(point1, point2):
    p1 = convertPoint(point1)
    p2 = convertPoint(point2)
    return distance(p1, p2).km


def generatePoints(maxDistance, amount):
    result = list()

    while len(result) < amount:
        points = pyc.geoloc_generation(BE, min(20, amount), "Belgium")
        # TODO: finish




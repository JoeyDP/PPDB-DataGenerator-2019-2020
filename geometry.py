import pycristoforo as pyc

from geopy.distance import distance

from scipy.stats import gamma
import random
import math
import logging

from shapely.geometry import Point

from settings import MAX_ATTEMPTS

BE = pyc.get_shape("Belgium")


def convertPoint(point):
    return tuple(reversed(point['geometry']['coordinates']))


def sampleRandomLocation():
    points = pyc.geoloc_generation(BE, 1, "Belgium")
    return convertPoint(points[0])


def sampleLocationNear(origin, distanceScale=1):
    for _ in range(MAX_ATTEMPTS):
        angle = random.uniform(0, 2 * math.pi)
        distance = gamma.rvs(a=2, loc=0.01, scale=0.1 * distanceScale)
        point = (origin[0] + math.cos(angle) * distance, origin[1] + math.sin(angle) * distance)

        # Check if on land
        if BE.contains(Point(*reversed(point))):
            return point

    logging.error(f"Couldn't sample random point near {origin} with scale {distanceScale} in {MAX_ATTEMPTS} tries")
    raise RuntimeError(f"Couldn't sample random point near {origin} with scale {distanceScale} in {MAX_ATTEMPTS} tries")

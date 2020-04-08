import random
import logging
from datetime import date, time, timedelta

from distribution import BernoulliDistribution, NormalDurationDistribution, NormalTimeDistribution
from settings import WORK_DISTANCE_SCALE, HOBBY_DISTANCE_SCALE, MAX_ATTEMPTS
from person import WorkerPerson, Activity
import geometry


class WorkerPersonGenerator(object):
    """ Generates a random WorkerPerson with random distributions for their activities. """
    def __init__(self):
        pass

    def sampleWorkStartTime(self):
        return NormalTimeDistribution(randomTime(time(9), timedelta(hours=1)), randomTimedelta(0.5, 0.3))

    def sampleWorkDuration(self):
        return NormalDurationDistribution(random.normalvariate(7, 1), random.normalvariate(1, 0.5))

    def sampleWorkChance(self):
        return BernoulliDistribution(randomChance(0.9, 0.1))

    def sampleWorkBridgeChance(self):
        return BernoulliDistribution(randomChance(0.2, 0.2))

    def sampleHobbyStartTime(self):
        return NormalTimeDistribution(randomTime(time(19), timedelta(hours=1)), randomTimedelta(2, 0.5))

    def sampleHobbyDuration(self):
        return NormalDurationDistribution(random.normalvariate(2, 0.2), random.normalvariate(1, 0.2))

    def sampleHobbyChance(self):
        return BernoulliDistribution(randomChance(0.4, 0.3))

    def sampleHobbyBridgeChance(self):
        return BernoulliDistribution(randomChance(0.2, 0.2))

    def generate(self, firstname, lastname, username, gender, password, home):
        work = geometry.sampleLocationNear(home, WORK_DISTANCE_SCALE)
        workActivity = Activity(self.sampleWorkStartTime(), self.sampleWorkDuration(), self.sampleWorkChance(), self.sampleWorkBridgeChance(), [work])

        hobbyLocations = [geometry.sampleLocationNear(home, HOBBY_DISTANCE_SCALE) for _ in range(random.randint(1, 8))]
        hobbyActivity = Activity(self.sampleHobbyStartTime(), self.sampleHobbyDuration(), self.sampleHobbyChance(), self.sampleHobbyBridgeChance(), hobbyLocations)

        return WorkerPerson(firstname, lastname, username, gender, password, home, workActivity, hobbyActivity)


def randomTime(mean, stddev):
    """ Sample a random timestamp from a normal distribution. """
    d = date.today()
    dist = NormalTimeDistribution(mean, stddev)
    for _ in range(MAX_ATTEMPTS):
        t = dist.sample(d)
        if t.date() == d:
            return t.time()

    logging.error(f"Couldn't sample random time in {MAX_ATTEMPTS} tries with mean {mean} and stddev {stddev}")
    raise RuntimeError(f"Couldn't sample random time in {MAX_ATTEMPTS} tries with mean {mean} and stddev {stddev}")


def randomTimedelta(mean, stddev):
    """ Sample random duration. Mean and stddev in hours. """
    return NormalDurationDistribution(mean, stddev).sample()


def randomChance(mean, stddev):
    """ Sample a value between 0 and 1 from a normal distribution with mean and stddev. """
    return min(1, max(0, random.normalvariate(mean, stddev)))

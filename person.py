import pickle
import os
from os.path import isfile
import random
import logging
from datetime import date, time, timedelta

from distribution import BernoulliDistribution, NormalDurationDistribution, NormalTimeDistribution
from settings import WORK_DISTANCE_SCALE, HOBBY_DISTANCE_SCALE, MAX_ATTEMPTS

import geometry


class Person(object):
    def __init__(self, firstname, lastname, username, password, home):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username

        self.password = password

        self.home = home
        self.activities = list()

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def __repr__(self):
        return self.username

    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.username})"

    @staticmethod
    def loadFrom(path):
        person = pickle.load(open(path, "rb"))
        return person

    def saveTo(self, directory):
        pickle.dump(self, open(os.path.join(directory, str(self.username) + ".pickle"), "wb"))

    @staticmethod
    def loadAllFrom(directory):
        files = [os.path.join(directory, f) for f in os.listdir(directory) if isfile(os.path.join(directory, f))]
        people = [Person.loadFrom(file) for file in files]
        return people

    def generateRidesForDay(self, day):
        for activity in self.activities:
            pass

    def addNotificationTime(self, ride, minTimeNotification):
        pass


class Activity(object):
    def __init__(self, startDistribution, durationDistribution, chanceDistribution, locations):
        self.startDistribution = startDistribution
        self.durationDistribution = durationDistribution
        self.chance = chanceDistribution
        self.locations = locations


class WorkerPerson(Person):
    def __init__(self, firstname, lastname, username, password, home, workActivity, hobbyActivity):
        super().__init__(firstname, lastname, username, password, home)

        self.workActivity = workActivity
        self.hobbyActivity = hobbyActivity

        self.activities.append(workActivity)
        self.activities.append(hobbyActivity)

    @property
    def work(self):
        return self.workActivity.locations[0]


class WorkerPersonGenerator(object):
    def __init__(self):
        pass

    def sampleWorkStartTime(self):
        return NormalTimeDistribution(randomTime(time(9), timedelta(hours=1)), randomTimedelta(0.5, 0.3))

    def sampleWorkDuration(self):
        return NormalDurationDistribution(randomTimedelta(7, 1), randomTimedelta(1, 0.5))

    def sampleWorkChance(self):
        return BernoulliDistribution(randomChance(0.9, 0.1))

    def sampleHobbyStartTime(self):
        return NormalTimeDistribution(randomTime(time(20), timedelta(hours=1)), randomTimedelta(2, 0.5))

    def sampleHobbyDuration(self):
        return NormalDurationDistribution(randomTimedelta(2, 0.2), randomTimedelta(1, 0.2))

    def sampleHobbyChance(self):
        return BernoulliDistribution(randomChance(0.4, 0.3))

    def generate(self, firstname, lastname, username, password, home):
        work = geometry.sampleLocationNear(home, WORK_DISTANCE_SCALE)
        workActivity = Activity(self.sampleWorkStartTime(), self.sampleWorkDuration(), self.sampleWorkChance(), [work])

        hobbyLocations = [geometry.sampleLocationNear(home, HOBBY_DISTANCE_SCALE) for _ in range(random.randint(1, 8))]
        hobbyActivity = Activity(self.sampleHobbyStartTime, self.sampleHobbyDuration(), self.sampleHobbyChance(), hobbyLocations)

        return WorkerPerson(firstname, lastname, username, password, home, workActivity, hobbyActivity)



def randomTime(mean, stddev):
    d = date.today()
    dist = NormalTimeDistribution(mean, stddev)
    for _ in range(MAX_ATTEMPTS):
        t = dist.sample(d)
        if t.date() == d:
            return t.time()

    logging.error(f"Couldn't sample random time in {MAX_ATTEMPTS} tries with mean {mean} and stddev {stddev}")
    raise RuntimeError(f"Couldn't sample random time in {MAX_ATTEMPTS} tries with mean {mean} and stddev {stddev}")


def randomTimedelta(mean, stddev):
    """ Mean and stddev in hours """
    return NormalDurationDistribution(mean, stddev).sample()


def randomChance(mean, stddev):
    return min(1, max(0, random.normalvariate(mean, stddev)))




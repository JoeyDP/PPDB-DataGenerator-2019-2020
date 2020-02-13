import pickle
import os
from os.path import isfile
import random
from datetime import datetime, time, timedelta

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


WORK_DISTANCE_SCALE = 1
HOBBY_DISTANCE_SCALE = 0.8


class WorkerPerson(Person):
    def __init__(self, firstname, lastname, username, password, home, workActivity, hobbyActivity):
        super().__init__(firstname, lastname, username, password, home)

        self.work = geometry.sampleLocationNear(self.home, WORK_DISTANCE_SCALE)

        self.activities.append(workActivity)
        self.activities.append(hobbyActivity)


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

    def generate(self, firstname, lastname, username, password, home, amountHobbies):
        work = geometry.sampleLocationNear(home, WORK_DISTANCE_SCALE)
        workActivity = Activity(self.sampleWorkStartTime(), self.sampleWorkDuration(), self.sampleWorkChance(), [work])

        hobbyLocations = [geometry.sampleLocationNear(home, HOBBY_DISTANCE_SCALE) for _ in range(amountHobbies)]
        hobbyActivity = Activity(self.sampleHobbyStartTime, self.sampleHobbyDuration(), self.sampleHobbyChance(), hobbyLocations)

        return WorkerPerson(firstname, lastname, username, password, home, workActivity, hobbyActivity)


def randomTime(mean, stddev):
    d = datetime.today()
    dist = NormalTimeDistribution(mean, stddev)
    while True:
        t = dist.sampleTime(d)
        if t.date() == d:
            return t.time()


def randomTimedelta(mean, stddev):
    """ Mean and stddev in hours """
    return NormalDurationDistribution(mean, stddev).sample()


def randomChance(mean, stddev):
    return min(1, max(0, random.normalvariate(mean, stddev)))


class Distribution(object):
    def __init__(self):
        pass

    def sample(self):
        raise NotImplementedError()


class BernoulliDistribution(Distribution):
    def __init__(self, chance):
        super().__init__()
        self.chance = chance

    def sample(self):
        return random.random() <= self.chance


class NormalDurationDistribution(Distribution):
    def __init__(self, mean, stddev):
        super().__init__()
        self.mean = mean
        self.stddev = stddev

    def sampleTime(self, date):
        return timedelta(hours=max(0, random.normalvariate(self.mean, self.stddev)))


class TimeDistribution(object):
    def __init__(self):
        pass

    def sampleTime(self, date):
        raise NotImplementedError()


class NormalTimeDistribution(TimeDistribution):
    def __init__(self, mean, stddev):
        super().__init__()
        self.mean = mean
        self.stddev = stddev

    def sampleTime(self, date):
        return random.normalvariate(datetime.combine(date, self.mean), self.stddev)


class Activity(object):
    def __init__(self, startDistribution, durationDistribution, chanceDistribution, locations):
        self.startDistribution = startDistribution
        self.durationDistribution = durationDistribution
        self.chance = chanceDistribution
        self.locations = locations



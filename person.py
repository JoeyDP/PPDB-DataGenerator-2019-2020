import pickle
import os
from os.path import isfile

from datetime import timedelta
from util import daterange

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
    def __init__(self, firstname, lastname, username, password, home, amountHobbies):
        super().__init__(firstname, lastname, username, password, home)

        self.work = geometry.sampleLocationNear(self.home, WORK_DISTANCE_SCALE)

        # self.activities.append(Activity(startTime, duration, [self.work]))
        #
        # hobbyLocations = [geometry.sampleLocationNear(self.home, HOBBY_DISTANCE_SCALE) for _ in range(amountHobbies)]
        # self.activities.append(Activity(startTime, duration, hobbyLocations))

    @staticmethod
    def generate(self):
        pass


class PersonRides(object):
    def __init__(self, person):
        self.person = person
        self.rides = list()
        self.lastGeneratedDay = None

    def generateUntil(self, endDay, minStartTime=None):
        """ Generate rides for all days from max(minStartDay, lastGeneratedDay) until endDay. """
        assert not (self.lastGeneratedDay is None and minStartTime is None), "Need some starting point."
        if self.lastGeneratedDay is None:
            startDay = minStartTime.date()
        else:
            startDay = max(minStartTime.date(), self.lastGeneratedDay + timedelta(1))

        for day in daterange(startDay, endDay):
            self.generateDay(day, minStartTime)
            self.lastGeneratedDay = day

    def generateDay(self, day, minTimeNotification):
        # print(f"Generating day: {day}")
        pass


class Activity(object):
    def __init__(self, startTime, duration, locations):
        self.startTime = startTime
        self.duration = duration
        self.locations = locations



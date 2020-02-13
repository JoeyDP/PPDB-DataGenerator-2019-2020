import pickle
import os
from os.path import isfile

from datetime import timedelta
from util import daterange


class Person(object):
    def __init__(self, firstname, lastname, password, wakeTime=7.5, sleepTime=20.0, tripTime=8.0):
        self.firstname = firstname
        self.lastname = lastname
        self.username = firstname + "_" + lastname

        self.password = password

        self.locations = list()

        self.wakeTime = wakeTime
        self.sleepTime = sleepTime
        self.tripTime = tripTime

    def __eq__(self, other):
        return self.username == other.username

    def __hash__(self):
        return hash(self.username)

    def __repr__(self):
        return self.username

    def __str__(self):
        return self.username

    @staticmethod
    def loadFrom(path):
        person = pickle.load(open(path, "rb"))
        return person

    def saveTo(self, directory):
        pickle.dump(self, open(os.path.join(directory, self.username), "wb"))

    @staticmethod
    def loadAllFrom(directory):
        files = [os.path.join(directory, f) for f in os.listdir(directory) if isfile(os.path.join(directory, f))]
        people = [Person.loadFrom(file) for file in files]
        return people


class PersonRides(object):
    def __init__(self, person):
        self.person = person
        self.rides = list()
        self.lastGeneratedDay = None

    def generateUntil(self, endDay, minStartDay=None):
        """ Generate rides for all days from max(minStartDay, lastGeneratedDay) until endDay. """
        assert not (self.lastGeneratedDay is None and minStartDay is None), "Need some starting point."
        if self.lastGeneratedDay is None:
            startDay = minStartDay
        else:
            startDay = max(minStartDay, self.lastGeneratedDay)

        for day in daterange(startDay + timedelta(1), endDay + timedelta(1)):
            self.generateDay(day)
            self.lastGeneratedDay = day

    def generateDay(self, day):
        print(f"Generating day: {day}")

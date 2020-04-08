import pickle
import random
import logging
import os
from os.path import isfile
from datetime import timedelta

from ride import Ride


class Person(object):
    """
    Base class for a person with behaviour. Contains minimal personal info and
    is able to generate rides based on activities.
    """
    def __init__(self, firstname, lastname, username, gender, password, home):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.gender = gender

        self.password = password

        # Note: could make a car generator if needed
        self.passengers = random.choice([3, 3, 3, 4, 4, 6])

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
        """ Load person from file. """
        person = pickle.load(open(path, "rb"))
        return person

    def saveTo(self, directory):
        """ Save person to file. Rides are not stored with the person itself. """
        pickle.dump(self, open(os.path.join(directory, str(self.username) + ".pickle"), "wb"))

    @staticmethod
    def loadAllFrom(directory):
        """ Loads all people from a directory. """
        files = [os.path.join(directory, f) for f in os.listdir(directory) if isfile(os.path.join(directory, f))]
        people = [Person.loadFrom(file) for file in files]
        return people

    def labelLocation(self, location):
        """ Utility function to have the person label coordinates (for pretty printing of rides). """
        return "Home" if location == self.home else location

    def getAdditionalData(self):
        """ Return a dictionary with extra information that should be added when registering. """
        return {
            "home": self.home,
            "gender": self.gender
        }

    def generateRidesForDay(self, day):
        """ Have a person iterate over their activities to generate potential rides for one day. """

        rides = list()

        # current location (starts from home every day)
        origin = self.home

        # ride back, if any
        returnRide = None
        for activity in self.activities:
            # for every activiy, check whether it occurs
            if not activity.sampleOccurence():
                continue

            arrive = activity.sampleStartTime(day)
            destination = activity.sampleLocation()

            # check if possible, given return ride
            if returnRide is not None:
                ride = Ride(self, returnRide.destination, destination, arrive, self.passengers)
                if ride.departBy < returnRide.arriveBy:
                    pass    # cancel return ride, leave from previous location
                else:
                    # return ride valid, add it
                    rides.append(returnRide)
                    origin = returnRide.destination
                    returnRide = None

            # create the actual ride
            ride = Ride(self, origin, destination, arrive, self.passengers)
            rides.append(ride)
            origin = destination

            # Check if return ride needs to be made. If not, person will not go home in between activities for example.
            if not activity.sampleBridge():
                duration = activity.sampleDuration()
                returnRide = Ride(self, origin, self.home, arrive + duration, self.passengers)

        if returnRide is not None:
            rides.append(returnRide)

        return rides

    def addNotificationTime(self, ride, minTimeNotification):
        """ Sample a random notification time for a ride uniform within the possible window. """
        # Note: could add behaviour to this as well
        ride.notificationTime = random.uniform(minTimeNotification, ride.lastPossibleNotificationTime - timedelta(minutes=5))


class WorkerPerson(Person):
    """ Specialized person with a job and hobbies. Person class handles generation of rides through activity system. """
    def __init__(self, firstname, lastname, username, gender, password, home, workActivity, hobbyActivity):
        super().__init__(firstname, lastname, username, gender, password, home)

        self.workActivity = workActivity
        self.hobbyActivity = hobbyActivity

        self.activities.append(workActivity)
        self.activities.append(hobbyActivity)

    @property
    def work(self):
        return self.workActivity.locations[0]

    @property
    def hobbies(self):
        return self.hobbyActivity.locations

    def labelLocation(self, location):
        if location == self.work:
            return "Work"
        elif location in self.hobbies:
            return "Hobby" + str(self.hobbies.index(location) + 1)
        else:
            return super().labelLocation(location)

    def getAdditionalData(self):
        data = super().getAdditionalData()
        data.update({
            "work": self.work
        })
        return data


class Activity(object):
    """
    Activities represent locations the person needs to be.
    Occurence, start and duration are represented by distributions. Bridge chance means the user will not go home after.
    """
    def __init__(self, startDistribution, durationDistribution, chanceDistribution, bridgeChanceDistribution, locations):
        self.startDistribution = startDistribution
        self.durationDistribution = durationDistribution
        self.chanceDistribution = chanceDistribution
        self.bridgeChanceDistribution = bridgeChanceDistribution    # chance to connect to next activity (or not return home if no next activity)
        self.locations = locations

    def sampleOccurence(self):
        return self.chanceDistribution.sample()

    def sampleBridge(self):
        return self.bridgeChanceDistribution.sample()

    def sampleStartTime(self, day):
        return self.startDistribution.sample(day)

    def sampleDuration(self):
        return self.durationDistribution.sample()

    def sampleLocation(self):
        return random.choice(self.locations)



from util import daterange
from datetime import timedelta

from cached_property import cached_property
from geopy.distance import distance

from settings import SPEED


class Ride(object):
    def __init__(self, person, origin, destination, arriveBy, passengers, notificationTime):
        self.person = person
        self.notificationTime = notificationTime
        self.origin = origin
        self.destination = destination
        self.arriveBy = arriveBy
        self.passengers = passengers

    def __lt__(self, other):
        return self.arriveBy < other.arriveBy

    @cached_property
    def distance(self):
        return distance(self.origin, self.destination).km

    @cached_property
    def travelTime(self):
        return timedelta(seconds=self.distance / SPEED)

    def rescheduleNotificationTime(self, minTime):
        self.person.addNotificationTime(self, minTime)


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
        rides = self.person.generateRidesForDay(day)
        for ride in rides:
            self.person.addNotificationTime(ride, minTimeNotification)

        self.rides.extend(rides)

from util import daterange
from datetime import timedelta


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

    def rescheduleNotificationTime(self, minTime):
        pass
        # self.person


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
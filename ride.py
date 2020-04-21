from datetime import timedelta
from collections import defaultdict
from cached_property import cached_property

from geopy.distance import distance

from util import daterange
from settings import SPEED, MINIMUM_TRAVEL_MARGIN
import sender


class BaseRide(object):
    """ The base for any Ride. Contains only common information and utilities. """
    def __init__(self, origin, destination, arriveBy):
        self.origin = origin
        self.destination = destination
        self.arriveBy = arriveBy

    def __lt__(self, other):
        return self.arriveBy < other.arriveBy

    def __str__(self):
        return f"{self.origin} -> {self.destination} by {self.arriveBy.isoformat(' ', 'minutes')}"

    @cached_property
    def distance(self):
        return distance(self.origin, self.destination).km

    @cached_property
    def travelTime(self):
        return timedelta(seconds=self.distance / SPEED)

    @cached_property
    def departBy(self):
        return self.arriveBy - self.travelTime

    @cached_property
    def lastPossibleNotificationTime(self):
        return self.arriveBy - self.travelTime * MINIMUM_TRAVEL_MARGIN


class QuerryRide(BaseRide):
    """ Ride from the webapp. """
    pass


class Simulatable(object):
    def __init__(self, person):
        self.person = person
        self.notificationTime = None

    def notify(self, simulator):
        return True

    def rescheduleNotificationTime(self, minTime):
        raise NotImplementedError()

    @cached_property
    def lastPossibleNotificationTime(self):
        raise NotImplementedError()


class Ride(BaseRide, Simulatable):
    """ A ride of some person. """
    def __init__(self, person, origin, destination, arriveBy, passengerPlaces):
        BaseRide.__init__(self, origin, destination, arriveBy)
        Simulatable.__init__(self, person)
        self.passengerPlaces = passengerPlaces

    def __str__(self):
        origin = self.person.labelLocation(self.origin)
        destination = self.person.labelLocation(self.destination)

        return f"[{self.person.username}]: {origin} -> {destination} by {self.arriveBy.isoformat(' ', 'minutes')}, notify at {self.notificationTime.isoformat(' ', 'minutes')}"

    def notify(self, simulator):
        """
        Sends ride to webservice. Returns True if successful, False otherwise.
        First tries to join an existing ride, if none found, creates new ride.
        """
        return sender.notifyRide(self, simulator.url)

    def rescheduleNotificationTime(self, minTime):
        self.person.addNotificationTime(self, minTime)


class RideRequest(Simulatable):
    """ A ride join request to another ride. """

    def __init__(self, person, ride, rideToJoin):
        super().__init__(person)
        self.ride = ride                # the ride the person desires (BaseRide)
        self.rideToJoin = rideToJoin    # the ride to join (Ride)

    def notify(self, simulator):
        pass
        # TODO

    def rescheduleNotificationTime(self, minTime):
        pass        # TODO

    @cached_property
    def lastPossibleNotificationTime(self):
        return self.ride.lastPossibleNotificationTime


class PersonRides(object):
    """
    Collection of rides of a person with some utility functions.
    Rides are separated from people because they are persisted for simulation.
    """
    def __init__(self, person):
        self.person = person
        self.rides = list()
        self.lastGeneratedDay = None

    def removeRide(self, ride):
        self.rides.remove(ride)

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

    def ridesToStr(self):
        ret = ""
        days = defaultdict(list)
        for ride in self.rides:
            days[ride.arriveBy.date()].append(ride)

        for day, rides in days.items():
            ret += f"{day}\n"
            for ride in rides:
                ret += f"\t{str(ride)}\n"
            ret += "\n"

        return ret


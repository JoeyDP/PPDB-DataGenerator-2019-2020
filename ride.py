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
    def __init__(self):
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
    def __init__(self, person, origin, destination, arriveBy, passengerPlaces, rideId=None):
        BaseRide.__init__(self, origin, destination, arriveBy)
        Simulatable.__init__(self)
        self.person = person
        self.passengerPlaces = passengerPlaces
        self.rideId = rideId

    def __str__(self):
        origin, destination = self.origin, self.destination
        if hasattr(self.person, "labelLocation"):
            origin = self.person.labelLocation(origin)
            destination = self.person.labelLocation(destination)

        return f"[{self.person}]: {origin} -> {destination} by {self.arriveBy.isoformat(' ', 'minutes')}, notify at {self.notificationTime.isoformat(' ', 'minutes')}"

    def notify(self, simulator):
        """
        Sends ride to webservice. Returns True if successful, False otherwise.
        First tries to join an existing ride, if none found, creates new ride.
        """
        # join ride
        candidates = sender.searchRide(self, simulator)

        # select candidate
        for candidate in candidates:
            rideRequest = RideRequest(self, candidate)
            # check if passenger wants to join and whether notification time would still be possible given current time of simulator)
            if rideRequest.passengerOk and rideRequest.lastPossibleNotificationTime > simulator.time:
                # a good candidate is found, try to join
                status = sender.sendRideRequest(rideRequest, simulator)
                if status:
                    # If it's one of our rides, schedule a rideRequest, so it can be accepted or declined by the driver
                    driver = simulator.findPerson(rideRequest.rideToJoin.person)
                    if driver:
                        rideRequest.rideToJoin.person = driver
                        simulator.scheduleRide(rideRequest)
                    return True

                # if join did not work, stop trying and make own ride
                break

        return sender.sendRide(self, simulator)

    def rescheduleNotificationTime(self, minTime):
        self.person.addNotificationTime(self, minTime)


class RideRequest(BaseRide, Simulatable):
    """ A ride join request to another ride. """

    def __init__(self, ride, rideToJoin):
        BaseRide.__init__(self, rideToJoin.origin, rideToJoin.destination, rideToJoin.arriveBy)
        Simulatable.__init__(self)
        self.ride = ride                # the ride the person desires (BaseRide)
        self.rideToJoin = rideToJoin    # the ride to join (Ride)

    @cached_property
    def distance(self):
        return distance(self.rideToJoin.origin, self.ride.origin).km \
               + self.ride.distance\
               + distance(self.ride.destination, self.rideToJoin.destination).km

    @cached_property
    def detourFactor(self):
        return self.distance / self.rideToJoin.distance

    @cached_property
    def passengerOk(self):
        """ Does the passenger want to do this """
        return self.detourFactor <= self.ride.person.detourTolerance

    @cached_property
    def driverOk(self):
        """ Does the driver want to do this """
        return self.detourFactor <= self.rideToJoin.person.detourTolerance

    def notify(self, simulator):
        status = self.driverOk
        return sender.notifyRideRequest(self, status, simulator)

    def rescheduleNotificationTime(self, minTime):
        self.rideToJoin.person.addNotificationTime(self, minTime)

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


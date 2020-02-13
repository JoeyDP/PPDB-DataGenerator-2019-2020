



class Ride(object):
    def __init__(self, origin, destination, arriveBy, passengers, notificationTime):
        self.notificationTime = notificationTime
        self.origin = origin
        self.destination = destination
        self.arriveBy = arriveBy
        self.passengers = passengers

    def __lt__(self, other):
        return self.notificationTime < other.notificationTime

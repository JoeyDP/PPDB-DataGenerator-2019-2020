


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
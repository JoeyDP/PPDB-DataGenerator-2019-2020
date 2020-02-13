

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
        pass

    def __hash__(self):
        pass

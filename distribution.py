import random
from datetime import datetime, timedelta


class Distribution(object):
    def __init__(self):
        pass

    def sample(self):
        raise NotImplementedError()


class BernoulliDistribution(Distribution):
    def __init__(self, chance):
        super().__init__()
        self.chance = chance

    def sample(self):
        return random.random() <= self.chance


class NormalDurationDistribution(Distribution):
    def __init__(self, mean, stddev):
        """ mean and stddev in hours """
        super().__init__()
        self.mean = mean
        self.stddev = stddev

    def sample(self):
        return timedelta(hours=max(0, random.normalvariate(self.mean, self.stddev)))


class TimeDistribution(object):
    def __init__(self):
        pass

    def sample(self, date):
        raise NotImplementedError()


class NormalTimeDistribution(TimeDistribution):
    def __init__(self, mean, stddev):
        super().__init__()
        self.mean = mean
        self.stddev = stddev

    def sample(self, date):
        return random.normalvariate(datetime.combine(date, self.mean), self.stddev)

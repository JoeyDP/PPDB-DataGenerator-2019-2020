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
    def __init__(self, mean, stddev, trimSeconds=True):
        """ mean and stddev in hours """
        super().__init__()
        self.mean = mean
        self.stddev = stddev
        self.trimSeconds = trimSeconds

    def sample(self):
        t = timedelta(hours=max(0, random.normalvariate(self.mean, self.stddev)))
        if self.trimSeconds:
            return t - timedelta(seconds=t.seconds, microseconds=t.microseconds)
        return t


class TimeDistribution(object):
    def __init__(self):
        pass

    def sample(self, date):
        raise NotImplementedError()


class NormalTimeDistribution(TimeDistribution):
    def __init__(self, mean, stddev, trimSeconds=True):
        super().__init__()
        self.mean = mean
        self.stddev = stddev
        self.trimSeconds = trimSeconds

    def sample(self, date):
        t = random.normalvariate(datetime.combine(date, self.mean), self.stddev)
        if self.trimSeconds:
            return t.replace(second=0, microsecond=0)
        return t

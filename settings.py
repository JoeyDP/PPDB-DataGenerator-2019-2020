import datetime


DATA_FILE = "state"
PEOPLE_DIR = "users"
EPSILON_NOTIFICATION = datetime.timedelta(minutes=1)
MINIMUM_TRAVEL_MARGIN = 1.2                             # factor to multiply travel time with
SPEED = 50.0/3600                                       # speed in km/s


GENERATE_DAYS = datetime.timedelta(days=7)

MAX_SLEEP_TIME = datetime.timedelta(hours=1)
RETRY_DELAY = datetime.timedelta(minutes=5)


WORK_DISTANCE_SCALE = 1
HOBBY_DISTANCE_SCALE = 0.8
MAX_ATTEMPTS = 50

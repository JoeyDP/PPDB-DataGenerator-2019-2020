import datetime

# simulation settings
DATA_FILE = "state"
PEOPLE_DIR = "users"
EPSILON_NOTIFICATION = datetime.timedelta(minutes=1)    # margin for notification (later than this time -> reschedule
MAX_SLEEP_TIME = datetime.timedelta(hours=1)            # don't sleep for longer stretches than this
RETRY_DELAY = datetime.timedelta(minutes=5)             # if missed notification or error, reschedule after this delay
GENERATE_DAYS = datetime.timedelta(days=7)              # generate this many days into the future


# generation settings
MINIMUM_TRAVEL_MARGIN = 1.2                             # factor to multiply travel time with
SPEED = 50.0/3600                                       # speed in km/s
WORK_DISTANCE_SCALE = 1                                 # modifier for how far work can be from home
HOBBY_DISTANCE_SCALE = 0.8                              # modifier for how far hobbies can be from home
MAX_ATTEMPTS = 50                                       # max retries to prevent infinite while loop


# webservice settings
LOGIN_PATH = "users/auth"
REGISTER_PATH = "users/register"
DRIVES_PATH = "drives"



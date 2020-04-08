import shelve
import time
import logging
from os import path
from queue import PriorityQueue
from logging.handlers import RotatingFileHandler
from datetime import date, datetime, timedelta

import bacli

from person import Person
from ride import PersonRides
import sender

from settings import MAX_SLEEP_TIME, PEOPLE_DIR, EPSILON_NOTIFICATION, RETRY_DELAY, DATA_FILE, GENERATE_DAYS


def generateRides(people, endDay):
    """
     Have a set of people generate their rides until a certain date.
    :param people: list of people
    :param endDay: typically determined by current day + GENERATE_DAYS
    """
    minStartTime = datetime.now()
    for person in people:
        person.generateUntil(endDay, minStartTime=minStartTime)


def sleep(sleeptime: timedelta):
    """
    Wrapper for time.sleep with debug log.
    :param sleeptime: timedelta to indicate amount of time to sleep for. Microseconds are stripped.
    """
    if sleeptime.seconds > 0:
        sleeptime -= timedelta(microseconds=sleeptime.microseconds)
        logging.debug(f"Sleeping for: {sleeptime}")
        time.sleep(sleeptime.seconds)


def notify(ride, url):
    """ Sends ride to webservice. Returns True if successful, False otherwise. """
    return sender.notifyRide(ride, url)


def getPersonRides(person, ridesMap):
    """ Get or create PersonRides in persistent state (ridesMap). """
    personRides = ridesMap.get(person, PersonRides(person))
    ridesMap[person] = personRides
    return personRides


def scheduleRide(ride, schedule):
    """ Add a ride to the schedule. Schedule is a priority queue based on notification time. """
    schedule.put((ride.notificationTime, ride))


def removeRide(ride, state):
    """ Remove a ride from the persistent state. """
    #logging.debug(f"Removing ride: {ride}")
    ridesMap = state["ridesMap"]
    personRides = ridesMap[ride.person]
    personRides.removeRide(ride)


def debugPrintPeopleRides(peopleRides):
    for personRides in peopleRides:
        logging.debug(personRides.ridesToStr())


def updateAll(directory, generateUntil, state):
    """ Reload people, generate rides and update schedule """
    # Load people from files in folder
    people = Person.loadAllFrom(path.join(directory, PEOPLE_DIR))

    # Find associated PersonRides info or create if it doesn't exist yet
    ridesMap = state["ridesMap"]
    peopleRides = [getPersonRides(person, ridesMap) for person in people]

    # Update all rides
    generateRides(peopleRides, generateUntil)
    state["lastGeneratedDay"] = generateUntil

    # debugPrintPeopleRides(peopleRides)

    # Schedule them
    schedule = PriorityQueue()
    for personRides in peopleRides:
        for ride in personRides.rides:
            scheduleRide(ride, schedule)

    return schedule


def checkNextRide(schedule, url, state):
    """
    Handle the next ride that needs to be notified.
    Depending on the time to be notified and the time of the ride, decide to either send, reschedule, wait or discard.
    """
    notificationTime, nextRide = schedule.get()

    logging.info(f"Next ride: {nextRide}")

    if notificationTime <= datetime.now() + EPSILON_NOTIFICATION:
        # notification time passed and too late to reschedule
        if nextRide.lastPossibleNotificationTime < datetime.now():
            # Too late to notify still -> discard
            logging.info(f"Discarded, too late")
            removeRide(nextRide, state)
        elif datetime.now() - notificationTime < EPSILON_NOTIFICATION:
            # Need to notify
            # If failed, reschedule notification
            logging.info(f"Notifying")
            status = notify(nextRide, url)
            if status:
                logging.info("Succes!")
                removeRide(nextRide, state)
            else:
                logging.info("Notify failed")
                logging.info(f"Retrying in {RETRY_DELAY}")
                nextRide.notificationTime += RETRY_DELAY
                scheduleRide(nextRide, schedule)
        else:
            # Notification somewhere in past
            # Resample notification time and reschedule
            logging.warning(f"Missed notification for ride")
            logging.warning("Rescheduling notification")
            nextRide.rescheduleNotificationTime(datetime.now())
            scheduleRide(nextRide, schedule)
            logging.warning(f"Notification rescheduled to {notificationTime}")
    else:
        logging.info("Notification in future, skipping")
        scheduleRide(nextRide, schedule)

    logging.info("")


def simulate(directory: str, url: str):
    """
    Main loop of the simulation. Loads the persistent state of rides from file and creates a priority queue based on
    the notifications times. People generate rides up to GENERATE_DAYS in the future, which are send to the webservice
    on their notification time.
    :param directory: data directory for the simulation. Should contain a users/ dir with users and a state file will be created
    :param url: base url of the webservice
    """
    with shelve.open(path.join(directory, DATA_FILE), writeback=True) as state:
        # Maps Person to PersonRides
        ridesMap = state.get("ridesMap", dict())
        state["ridesMap"] = ridesMap

        # The last generated day
        lastGeneratedDay = state.get("lastGeneratedDay", None)

        update = True
        while True:
            # Check if update is required
            generateUntil = date.today() + GENERATE_DAYS
            # print("Generate until: ", generateUntil)
            if lastGeneratedDay is None or lastGeneratedDay < generateUntil:
                update = True

            # Generate rides and update users
            if update:
                logging.info("Performing update")
                state.sync()
                schedule = updateAll(directory, generateUntil, state)
                lastGeneratedDay = state["lastGeneratedDay"]
                update = False

            # Simulate rides by taking next ride to be notified, if any
            if not schedule.empty():
                checkNextRide(schedule, url, state)

            # Check if there is a next ride
            if schedule.empty():
                sleep(MAX_SLEEP_TIME)
                continue

            # Sleep until next ride needs to be notified
            notificationTime, nextRide = schedule.queue[0]
            sleeptime = max(timedelta(seconds=0), min(MAX_SLEEP_TIME, (notificationTime - datetime.now())))
            sleep(sleeptime)


# utility module for turning functions into command line interface (cli) commands
with bacli.cli() as cli:

    @cli.command
    def run(directory: str, url: str):
        """ Run the simulator for the specified directory and webservice. """
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)  # this must be DEBUG to allow debug messages through

        # console = logging.StreamHandler()
        # console.setLevel(logging.INFO)
        # formatter = logging.Formatter(f'[{path.basename(directory)}] [%(levelname)s]: %(message)s')
        # console.setFormatter(formatter)
        # log.addHandler(console)

        fileHandler = RotatingFileHandler(
            path.join(directory, "simulator.log"),
            mode='a',
            maxBytes=5*1024*1024,
            backupCount=1
        )
        formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        fileHandler.setFormatter(formatter)
        fileHandler.setLevel(logging.DEBUG)
        log.addHandler(fileHandler)

        try:
            simulate(directory, url)
        except KeyboardInterrupt:
            logging.info("Shutting down")

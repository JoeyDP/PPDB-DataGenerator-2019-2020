from queue import PriorityQueue
import shelve
from os import path
import time

import bacli

from person import Person, PersonRides

from datetime import date, datetime, timedelta


DATA_FILE = "state"
PEOPLE_DIR = "users"
EPSILON_NOTIFICATION = timedelta(minutes=1)
MINIMUM_ARRIVEBY_MARGIN = timedelta(hours=1)

GENERATE_DAYS = timedelta(days=7)

MAX_SLEEP_TIME = timedelta(hours=1)
RETRY_DELAY = timedelta(minutes=5)


def generateRides(people, endDay):
    minStartTime = datetime.now()
    for person in people:
        person.generateUntil(endDay, minStartTime=minStartTime)


def sleep(sleeptime):
    print(f"Sleeping for: {sleeptime}")
    time.sleep(sleeptime.seconds)


def notify(ride):
    """ Sends ride to webservice. Returns True if successful, False otherwise. """
    # TODO: implement


def getPersonRides(person, ridesMap):
    """ Get or create PersonRides in persistent state. """
    personRides = ridesMap.get(person, PersonRides(person))
    ridesMap[person] = personRides
    return personRides


def scheduleRide(ride, schedule):
    schedule.put((ride.notificationTime, ride))


def updateAll(directory, generateUntil, state, ridesMap):
    """ Reload people, generate rides and update schedule """
    # Load people from files in folder
    people = Person.loadAllFrom(path.join(directory, PEOPLE_DIR))

    # Find associated PersonRides info or create if it doesn't exist yet
    peopleRides = [getPersonRides(person, ridesMap) for person in people]

    # Update all rides
    generateRides(peopleRides, generateUntil)
    state["lastGeneratedDay"] = generateUntil

    # Schedule them
    schedule = PriorityQueue()
    for personRides in peopleRides:
        for ride in personRides.rides:
            scheduleRide(ride, schedule)

    return schedule


def checkNextRide(schedule):
    notificationTime, nextRide = schedule.get()

    if notificationTime <= datetime.now():
        # notification time passed
        if nextRide.arriveBy < datetime.now() + MINIMUM_ARRIVEBY_MARGIN:
            # Too late to notify still -> discard
            print(f"Discarded: {nextRide}, too late")
            pass
        elif datetime.now() - notificationTime < EPSILON_NOTIFICATION:
            # Need to notify
            # If failed, reschedule notification
            print(f"Notifying ride: {nextRide}")
            status = notify(nextRide)
            if not status:
                print(f"Notify failed")
                print(f"Retrying in {RETRY_DELAY}")
                nextRide.notificationTime += RETRY_DELAY
                scheduleRide(nextRide, schedule)
            else:
                print("Succes!")
        else:
            # Notification somewhere in past
            # Resample notification time and reschedule
            print(f"Missed notification for ride: {nextRide}")
            print("Rescheduling notification")
            nextRide.rescheduleNotificationTime(datetime.now())
            scheduleRide(nextRide, schedule)


with bacli.cli() as cli:

    @cli.command
    def run(directory: str):
        with shelve.open(path.join(directory, DATA_FILE), writeback=True) as state:
            # Maps Person to PersonRides
            ridesMap = state.get("ridesMap", dict())
            state["ridesMap"] = ridesMap

            # The last generated day
            lastGeneratedDay = state.get("lastGeneratedDay", None)
            state["lastGeneratedDay"] = lastGeneratedDay

            update = True
            while True:
                # Check if update is required
                generateUntil = date.today() + GENERATE_DAYS
                # print("Generate until: ", generateUntil)
                if lastGeneratedDay is None or lastGeneratedDay < generateUntil:
                    update = True

                # Generate rides and update users
                if update:
                    print("Performing update")
                    schedule = updateAll(directory, generateUntil, state, ridesMap)
                    update = False

                # Check if ride to be simulated
                if schedule.empty():
                    sleep(MAX_SLEEP_TIME)
                    continue

                # Simulate rides
                checkNextRide(schedule)

                # Optional: sync state (happens on close as well)
                state.sync()

                # Check if there is a next ride
                if schedule.empty():
                    sleep(MAX_SLEEP_TIME)
                    continue

                # Sleep until next ride needs to be notified
                notificationTime, nextRide = schedule.queue[0]
                sleeptime = max(timedelta(seconds=0), min(MAX_SLEEP_TIME, (notificationTime - datetime.now())))
                sleep(sleeptime)

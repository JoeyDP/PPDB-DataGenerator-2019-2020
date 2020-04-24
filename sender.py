import logging
from urllib.parse import urljoin
from datetime import datetime

import requests

from settings import LOGIN_PATH, REGISTER_PATH, DRIVES_PATH, SEARCH_PATH, PASSENGER_REQUEST_PATH, REQUEST_STATUS_PATH
import ride


def sendGETRequest(url, data=None, token=None):
    """ Wrapper for sending a GET request. """
    if data is None:
        data = dict()
    logging.debug(f"Sending GET request to: {url}")
    logging.debug(f"with data: {data}")

    headers = dict()
    if token:
        headers["Authorization"] = f"Bearer {token}"
        logging.debug(f"and headers: {headers}")

    try:
        response = requests.get(url, data, headers=headers)
        if response:
            logging.debug(f"Response: {response.json()}")
        return response
    except requests.exceptions.RequestException:
        logging.exception("Failed request")


def sendPOSTRequest(url, data=None, token=None):
    """ Wrapper for sending a POST request. """
    if data is None:
        data = dict()
    logging.debug(f"Sending POST request to: {url}")
    logging.debug(f"with data: {data}")

    headers = dict()
    if token:
        headers["Authorization"] = f"Bearer {token}"
        logging.debug(f"and headers: {headers}")

    try:
        response = requests.post(url, json=data, headers=headers)
        if response:
            logging.debug(f"Response: {response.json()}")
        return response
    except requests.exceptions.RequestException:
        logging.exception("Failed request")


def register(person, simulator):
    """ Tries to register the person on webservice at baseUrl. Returns True or False depending on success. """
    registerUrl = urljoin(simulator.url, REGISTER_PATH)
    data = {
        "firstname": person.firstname,
        "lastname": person.lastname,
        "username": person.username,
        "password": person.password,
        **person.getAdditionalData()
    }
    response = sendPOSTRequest(registerUrl, data)
    if response:
        try:
            id = response.json().get('id')
            simulator.registerPerson(person, id)
        except ValueError:
            logging.exception("Failed to extract id after register")
        return True

    logging.debug(f"Failed to register. Response: {response}")
    return False


def login(person, simulator):
    """ Authenticates the user with a webservice. If valid, a token is returned. """
    loginUrl = urljoin(simulator.url, LOGIN_PATH)
    data = {
        "username": person.username,
        "password": person.password
    }
    response = sendPOSTRequest(loginUrl, data)
    if response:
        try:
            return response.json().get("token")
        except ValueError:
            logging.exception("Failed to extract token after login")

    logging.debug(f"Failed to login. Response: {response}")
    return None


def getToken(person, simulator):
    """ Tries to get a login token for a person. If login fails, tries register with login. """
    token = login(person, simulator)
    if token is None:
        status = register(person, simulator)
        if not status:
            return None
        token = login(person, simulator)
    return token


def sendRide(ride, simulator):
    """ Sends a user ride to the webservice. """
    token = getToken(ride.person, simulator)

    if not token:
        logging.warning(f"No valid token for person: {ride.person}")
        return False

    driveUrl = urljoin(simulator.url, DRIVES_PATH)
    data = {
        "from": ride.origin,
        "to": ride.destination,
        "passenger-places": ride.passengerPlaces,
        "arrive-by": ride.arriveBy.isoformat()
    }

    response = sendPOSTRequest(driveUrl, data, token)
    if response:
        return True

    logging.debug(f"Failed to create ride. Response: {response}")
    return False


def searchRide(queryRide, simulator):
    """ Search for a similar ride that can be joined instead of creating a new one. """
    searchUrl = urljoin(simulator.url, SEARCH_PATH)

    data = {
        'from': queryRide.origin,
        'to': queryRide.destination,
        'arrive_by': queryRide.arriveBy.isoformat(),
        'limit': 5,
    }

    response = sendGETRequest(searchUrl, data)
    if not response:
        return []

    candidates = list()
    try:
        rides = response.json()
        for rideData in rides:
            candidate = ride.Ride(
                rideData['driver-id'],
                rideData['from'],
                rideData['to'],
                datetime.fromisoformat(rideData['arrive-by']),
                rideData.get("passenger-places", 3) - len(rideData['passenger-ids']),         # I forgot to mention this in apiary, my bad.
                rideId=rideData['id']
            )
            candidates.append(candidate)

    except ValueError:
        logging.exception("Failed parsing ride from search")
        return []

    return candidates


def sendRideRequest(rideRequest, simulator):
    """ Try to join an existing ride. """
    rideId = rideRequest.rideToJoin.rideId
    url = urljoin(simulator.url, REQUEST_STATUS_PATH.format(rideId))
    response = sendPOSTRequest(url)

    if response:
        # could check response status as well
        return True

    return False


def notifyRideRequest(rideRequest, accept: bool, simulator):
    """ Respond to ride request with given status. """
    rideId = rideRequest.rideToJoin.rideId
    userId = simulator.findPersonId(rideRequest.ride.person)
    url = urljoin(simulator.url, REQUEST_STATUS_PATH.format(rideId, userId))

    data = {
        'action': "accept" if accept else "reject"
    }

    response = sendPOSTRequest(url, data)
    if response:
        # could check response status as well
        return True

    return False


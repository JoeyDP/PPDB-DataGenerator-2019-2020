import logging
from urllib.parse import urljoin

import requests

from settings import LOGIN_PATH, REGISTER_PATH, DRIVES_PATH


def sendGETRequest(url, data, token=None):
    """ Wrapper for sending a GET request. """
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


def sendPOSTRequest(url, data, token=None):
    """ Wrapper for sending a POST request. """
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


def register(person, baseUrl):
    """ Tries to register the person on webservice at baseUrl. Returns True or False depending on success. """
    registerUrl = urljoin(baseUrl, REGISTER_PATH)
    data = {
        "firstname": person.firstname,
        "lastname": person.lastname,
        "username": person.username,
        "password": person.password,
        **person.getAdditionalData()
    }
    response = sendPOSTRequest(registerUrl, data)
    if response:
        return True

    logging.debug(f"Failed to register. Response: {response}")
    return False


def login(person, baseUrl):
    """ Authenticates the user with a webservice. If valid, a token is returned. """
    loginUrl = urljoin(baseUrl, LOGIN_PATH)
    data = {
        "username": person.username,
        "password": person.password
    }
    response = sendPOSTRequest(loginUrl, data)
    if response:
        return response.json().get("token")

    logging.debug(f"Failed to login. Response: {response}")
    return None


def getToken(person, baseUrl):
    """ Tries to get a login token for a person. If login fails, tries register with login. """
    token = login(person, baseUrl)
    if token is None:
        status = register(person, baseUrl)
        if not status:
            return None
        token = login(person, baseUrl)
    return token


def notifyRide(ride, baseUrl):
    """ Sends a user ride to the webservice. """
    token = getToken(ride.person, baseUrl)

    if not token:
        logging.warning(f"No valid token for person: {ride.person}")
        return False

    driveUrl = urljoin(baseUrl, DRIVES_PATH)
    data = {
        "from": ride.origin,
        "to": ride.destination,
        "passenger-places": ride.passengers,
        "arrive-by": ride.arriveBy.isoformat()
    }

    response = sendPOSTRequest(driveUrl, data, token)
    if response:
        return True

    logging.debug(f"Failed to create ride. Response: {response}")
    return False


def searchRide(ride, baseUrl):
    """ Search for a similar ride that can be joined instead of creating a new one. """
    pass


def joinRide(rideId, person):
    """ Try to join an existing ride. """
    pass


def notifyJoinRequest(driver, rideId, passengerId, accept: bool):
    """ Respond to ride request with given status. """
    pass


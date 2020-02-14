import logging
from urllib.parse import urljoin

import requests

from settings import LOGIN_PATH, REGISTER_PATH, DRIVES_PATH


def sendGETRequest(url, data, token=None):
    logging.debug(f"Sending GET request to: {url}")
    logging.debug(f"with data: {data}")

    headers = dict()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # return requests.post(url, data, headers=headers)


def sendPOSTRequest(url, data, token=None):
    logging.debug(f"Sending POST request to: {url}")
    logging.debug(f"with data: {data}")

    headers = dict()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # return requests.post(url, data, headers=headers)


def register(person, baseUrl):
    registerUrl = urljoin(baseUrl, REGISTER_PATH)
    data = {
        "firstname": person.firstname,
        "lastname": person.lastname,
        "username": person.username,
        "password": person.password
    }
    response = sendPOSTRequest(registerUrl, data)
    if response:
        return True

    logging.debug(f"Failed to register. Response: {response}")
    return False


def login(person, baseUrl):
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
    token = login(person, baseUrl)
    if token is None:
        status = register(person, baseUrl)
        if not status:
            return None
        token = login(person, baseUrl)
    return token


def notifyRide(ride, baseUrl):
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


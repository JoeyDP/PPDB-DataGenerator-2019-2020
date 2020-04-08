import logging

import bacli
import names
import username_generator
import random

import geometry
from personGenerator import WorkerPersonGenerator


logging.basicConfig(format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s', level=logging.DEBUG)


def generatePerson():
	""" Generates a random WorkerPerson and returns it. """
	gender = random.choice(('male', 'female'))
	firstname = names.get_first_name(gender)
	lastname = names.get_last_name()
	password = "password"
	username = username_generator.get_uname(0, 255, False)
	home = geometry.sampleRandomLocation()

	person = WorkerPersonGenerator().generate(firstname, lastname, username, gender, password, home)

	# logging.debug(person.home)
	# logging.debug(person.work)
	# logging.debug(geometry.distance(person.home, person.work).km)

	return person


# utility module for turning functions into command line interface (cli) commands
with bacli.cli() as cli:

	@cli.command
	def generatePeople(directory: str, amount: int = 1):
		""" generates people in the specified directory. """
		logging.info(f"Generating {amount} people.")
		for i in range(amount):
			person = generatePerson()
			person.saveTo(directory)




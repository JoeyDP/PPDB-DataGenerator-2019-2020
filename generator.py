import bacli
from person import Person, WorkerPersonGenerator
import names
import username_generator
import random

import geometry

import logging

logging.basicConfig(format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())


def generatePerson():
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


with bacli.cli() as cli:

	@cli.command
	def generatePeople(directory: str, amount: int = 1):
		logging.info(f"Generating {amount} people.")
		for i in range(amount):
			person = generatePerson()
			person.saveTo(directory)

	@cli.command
	def loadPeople(directory: str):
		people = Person.loadAllFrom(directory)
		#for person in people:
			#serialized = jsonpickle.encode(person)
			#print(json.dumps(json.loads(serialized), indent=4))

		# print(people)
		# for person in people:
		# 	print(person.home[1], ",", person.home[0])
		# 	print(person.work[1], ",", person.work[0])



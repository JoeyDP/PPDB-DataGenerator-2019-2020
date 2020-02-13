import bacli
from person import Person, WorkerPerson
import names
import username_generator

import geometry


def generatePerson():
	firstname = names.get_first_name()
	lastname = names.get_last_name()
	password = "password"
	username = username_generator.get_uname(0, 255, False)
	home = geometry.sampleRandomLocation()

	person = WorkerPerson(firstname, lastname, username, password, home, 1)

	print(person.home)
	print(person.work)
	print(geometry.distance(person.home, person.work).km)

	return person


with bacli.cli() as cli:

	@cli.command
	def generatePeople(directory: str, amount: int = 1):
		print(f"Generating {amount} people.")
		for i in range(amount):
			person = generatePerson()
			person.saveTo(directory)

	@cli.command
	def loadPeople(directory: str):
		people = Person.loadAllFrom(directory)
		print(people)
		for person in people:
			print(person.home[1], ",", person.home[0])
			print(person.work[1], ",", person.work[0])



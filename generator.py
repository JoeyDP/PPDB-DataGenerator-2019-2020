import bacli
from person import Person


def generatePerson():
	person = Person("Test", "123", "password")
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


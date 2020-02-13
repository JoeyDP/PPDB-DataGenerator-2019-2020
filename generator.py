import bacli



def generatePerson(path: str):
	pass


with bacli.cli() as cli:

	@cli.command
	def generatePeople(path: str, amount: int = 1):
		print(f"Generating {amount} people.")

	


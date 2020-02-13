from queue import PriorityQueue
import shelve
from os import path
import time

import bacli


DATA_FILE = "state"


with bacli.cli() as cli:

    @cli.command
    def run(directory: str):
        queue = PriorityQueue()

        with shelve.open(path.join(directory, DATA_FILE), writeback=True) as data:

            if "counter" not in data:
                data["counter"] = 0

            while True:
                print(data["counter"])
                time.sleep(1)
                data["counter"] += 1

                # queue.put(element)
                # el = queue.get()

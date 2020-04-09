# PPDB-DataGenerator-2019-2020

This repository contains the data generation script for the 2019-2020 course Programming Project Databases. Students implement a carpool webapp and this script provides them with simulated live data.

## How To Use

There are two scripts to configure and run the simulator:  
 - `runGenerator.sh [team] [amount]`  
   - Generates random users in the folder `data/[team]/users/`. These users have unique behavior and can be simulated to produce rides.
 -  `runSimulator.sh [team]`
   - Simulates all users in the folder `data/[team]/users/` by generating their rides and sending them to the webservice `[team].ppdb.me` at the scheduled time. The state of this script is kept in the team directory as well as the logs. You can safely stop and restart this script without losing data/causing conflicts.

Additionally there is a service file included:
 - `service/generator@.service`
   - The '@' indicates that this service takes a parameter, namely the team name in this case. Start the service by placing the file in `/etc/systemd/system/` (no symlink) and running `systemctl start generator@[team]`. Enable it to run on startup with `systemctl enable generator@[team]`. Replace the `[team]` parameter with the appropriate value.
   - If you generate more users (or remove users) you can restart the script (to force an update) with `systemctl restart generator@[team]`. Otherwise the change will be picked up on the next automatic update (once per day).


## How To Contribute

The most interesting files to look at if you want to add new types of users or change the way the script calls the API are:
 - `person.py` - encodes information about person and their behaviour.
 - `personGenerator.py` - contains types of persons that can be generated. Currently only a WorkerPerson, but you could add a TaxiPerson for example that does rides more randomly and uniformly spread over the day.
 - `generator.py` - main script for generating people.
 - `sender.py` - utility functions to communicate with API.
 - `simulator.py` - main simulation script.

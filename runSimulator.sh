#!/bin/bash

TEAM=$1

echo "Running simulator for team: $TEAM"

URL="$1.ppdb.me"
DIR="data/$1"


. env/bin/activate

mkdir -p $DIR
mkdir -p $DIR/users

python3 simulator.py run "$DIR"




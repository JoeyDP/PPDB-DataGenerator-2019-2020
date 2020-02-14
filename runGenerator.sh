#!/bin/bash

if [ $# -lt 2 ]
  then
    echo "Supply team name (e.g.: team1) and amount of people to generate"
    exit 1
fi

TEAM=$1
AMOUNT_USERS=$2

echo "Running generator for team: $TEAM"

URL="$1.ppdb.me"
DIR="data/$1"
USER_DIR="$DIR/users"

mkdir -p "$DIR"
mkdir -p "$USER_DIR"

. env/bin/activate

python3 generator.py generatePeople "$USER_DIR" --amount "$AMOUNT_USERS"




#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Supply team name (e.g.: team1)"
    exit 1
fi

TEAM=$1

echo "Running simulator for team: $TEAM"

URL="http://$1.ppdb.me/api/"
DIR="data/$1"
USER_DIR="$DIR/users"

mkdir -p "$DIR"
mkdir -p "$USER_DIR"

. env/bin/activate

python3 simulator.py run "$DIR" "$URL"

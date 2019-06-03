#!/usr/bin/bash

BASEDIR=$(dirname "$0")

rm $BASEDIR/db.sqlite3
python $BASEDIR/manage.py makemigrations
python $BASEDIR/manage.py migrate
python $BASEDIR/manage.py loaddata user.yaml
python $BASEDIR/manage.py loaddata billapp.yaml

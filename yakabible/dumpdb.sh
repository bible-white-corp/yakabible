#!/usr/bin/bash

BASEDIR=$(dirname "$0")

python $BASEDIR/manage.py dumpdata billapp --format yaml > billapp/fixtures/billapp.yaml
python $BASEDIR/manage.py dumpdata auth.group auth.permission auth.user social_django.usersocialauth --format yaml > billapp/fixtures/user.yaml

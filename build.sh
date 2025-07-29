#!/usr/bin/env bash

set -o errexit

pip install -r requirements

python manage.py collectstatic --noinput
python manage.py migrate
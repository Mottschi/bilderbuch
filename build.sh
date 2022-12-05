#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

pip install --upgrade pippip install --force-reinstall -U setuptools

python manage.py collectstatic --no-input
python manage.py migrate
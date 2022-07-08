#!/bin/bash

# python -m pip install pip-tools && \
# pip-compile ./requirements.in && \
# pip-sync ./requirements.txt && \
# python manage.py collectstatic --clear --no-input && \
# python manage.py compress --force && \
# python manage.py collectstatic --no-post-process --no-input && \

echo 'in release file';
echo 'migrate';
python makemigrations --merge;
python manage.py migrate;
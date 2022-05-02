#!/bin/bash

echo 'in release file';
echo 'migrate';
python makemigrations --merge;
python manage.py migrate;
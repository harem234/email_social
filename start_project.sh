# create user django
sudo adduser django
# add django (the user) to sudo group for development only
sudo usermod -aG sudo django
# log in to django user
su - django
# change owner ship of project files
sudo chown -R django:django /mnt/d/Projects/django/DJ_EmailUser_Social;
# go to project folder
cd /mnt/d/Projects/django/DJ_EmailUser_Social || exit;

sudo apt-get update;
#for psycopg in requirements.txt
sudo apt-get install libpq-dev gcc;

source /home/mahdi/.virtualenvs/DJ_EmailUser_Social/bin/activate;
pip install -U pip;
pip install -U pip-tools;
pip-compile --generate-hashes --rebuild --upgrade --verbose --output-file requirements.txt requirements.local.in;
pip-sync requirements.txt;
pip-audit;

# env

## for google api scopes error: 'scopes changed from "some scope" to "some other scope"'
export OAUTHLIB_RELAX_TOKEN_SCOPE=True
# django
export DJANGO_SETTINGS_MODULE=DJ_EmailUser_Social.settings.local
export PYTHONPATH=/mnt/d/Projects/django/DJ_EmailUser_Social
export SECRET_KEY='ja^!!d945ez9341cpf^vwmth$*p2v6p*!z9(q#8^%3#iwzl8q0^ud_9hh7igc5$)7n6sta8^omp9%nt881%n+l)1u+lha+6uk&dg'

# SENDGRID
export SENDGRID_USERNAME=mahdi123123123
export SENDGRID_PASSWORD=october19101994
export SENDGRID_API_KEY=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

python manage.py collectstatic -v 3 --clear;

python manage.py runserver wsl.localhost:8000

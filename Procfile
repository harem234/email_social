release: chmod u+x release.sh && ./release.sh

# web: gunicorn DJ_EmailUser_Social.wsgi:application --log-file -
web: bin/start-pgbouncer daphne DJ_EmailUser_Social8
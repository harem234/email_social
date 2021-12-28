release: chmod u+x release.sh && bin/start-pgbouncer && ./release.sh

# web: gunicorn DJ_EmailUser_Social.wsgi:application --log-file -
web: daphne DJ_EmailUser_Social.asgi:application --port $PORT --bind 0.0.0.0 -v2
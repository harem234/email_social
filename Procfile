release: bash ./release.bash

# web: gunicorn DJ_EmailUser_Social.wsgi:application --log-file -
web: daphne DJ_EmailUser_Social.asgi:application --bind 0.0.0.0 -v2
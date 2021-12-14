release: bash ./release.bash

# web: gunicorn DJ_EmailUser_Social.wsgi:application --log-file -
web: daphne <my-web-app>.asgi:application --port $PORT --bind 0.0.0.0 -v2
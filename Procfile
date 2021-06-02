release: python -m pip install pip-tools
release: pip-compile ./requirements.in
release: pip-sync ./requirements.txt

web: gunicorn DJ_EmailUser_Social.wsgi --log-file -
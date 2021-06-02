python -m pip install pip-tools && \
pip-compile ./requirements.in && \
pip-sync ./requirements.txt && \
python manage.py migrate
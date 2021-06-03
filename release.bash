python -m pip install pip-tools && \
pip-compile ./requirements.in && \
pip-sync ./requirements.txt && \
python manage.py collectstatic --clear && \
python manage.py compress --force && \
python manage.py collectstatic --no-post-process && \

python manage.py migrate
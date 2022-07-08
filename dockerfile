FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN mkdir /opt/email_user_prj
COPY . /opt/email_user_prj

RUN pip install --upgrade pip pip-tools; \
    python3 -m venv ~/envs/prj_env; \
    source ~/envs/prj_env/bin/activate; \
    pip-tools requirements.all.in; \
    pip install -r requirements.all.in;
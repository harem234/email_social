FROM python:3.10.7-bullseye

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# for google api scopes error: 'scopes changed from "some scope" to "some other scope"'
ENV OAUTHLIB_RELAX_TOKEN_SCOPE=True

# django
ENV DJANGO_SETTINGS_MODULE=DJ_EmailUser_Social.settings.local
ENV SECRET_KEY='ja^!!d945ez9341cpf^vwmth$*p2v6p*!z9(q#8^%3#iwzl8q0^ud_9hh7igc5$)7n6sta8^omp9%nt881%n+l)1u+lha+6uk&dg'

# SENDGRID
ENV SENDGRID_USERNAME=mahdi123123123
ENV SENDGRID_PASSWORD=october19101994
ENV SENDGRID_API_KEY=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

# RUN mkdir /opt/email_user_prj
COPY . /opt/email_user_prj

RUN pip install --upgrade pip pip-tools; \
    python3.10 -m venv ~/envs/prj_env; \
    source ~/envs/prj_env/bin/activate; \
    pip-compile /opt/email_user_prj/requirements.all.in --output-file /opt/email_user_prj/requirements.all.debian.txt --pip-args "--retries 10 --timeout 60" ; \
#    --generate-hashes requirements.all.in \
#    for production \
#
    pip-sync /opt/email_user_prj/requirements.all.debian.txt;
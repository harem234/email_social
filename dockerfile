FROM python:3.10

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# RUN mkdir /opt/email_user_prj
COPY . /opt/email_user_prj

RUN pip install --upgrade pip; \
    pip install -r ;
RUN pip install -r requirements.txt 
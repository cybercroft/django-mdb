# pull official base image
FROM python:3.9.13-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies (just listing some...)
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev gettext libmagic 

# install python packages
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

# run entrypoint.sh
RUN ["chmod", "+x", "/usr/src/app/entrypoint.sh"]

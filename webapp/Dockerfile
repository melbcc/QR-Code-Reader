# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
# ref: https://github.com/psycopg/psycopg2/issues/684#issuecomment-392015532
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
